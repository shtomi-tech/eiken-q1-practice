<!-- graft:start -->
## Graft — repo context graph

This repo is indexed in `graft/`: small linked markdown nodes that explain each
system and carry exact file:line spans, kept in sync with the code through git.

For ANY task here — understanding how something works, finding where code lives,
or scoping a change — get context from the graph before grepping or opening
source files. Re-ask freely (it's cheap) and reuse literal identifiers you
already have (symbol, error string, file name) as the query. New to this repo?
Run `graft map` first — a token-budgeted orientation (dir clusters, hubs,
hotspots), no LLM, no key.

- Run `graft ask "<your question>" --source` → ranked nodes with the relevant
  code spans inlined (each hit's ≤8-line crux by default; `--full` for whole
  definitions when the crux isn't enough). Match the tool to the task shape:
  for understanding or editing, the top node IS the answer — cite its
  `covers:` file:line spans and edit straight from `--source`. For
  exhaustive tasks ("every occurrence / every caller of this pattern"), ranked
  results are top-N, not complete — run `graft grep "<literal>"` instead
  (exhaustive over indexed files, grouped by enclosing symbol), falling back
  to raw `grep -rn` only for unindexed files.
- `graft skeleton <file>` → every definition's signature + span, ~10× cheaper
  than reading the file; use it to skim an API surface.
- `graft callers <symbol>` gives precomputed, exact edges — who calls this.
  Add `--direction out` for what it calls, or `--depth N` to walk
  transitively for the full blast radius. For structural questions, skip
  ranking and use this directly.
- Or browse: `graft/INDEX.md` lists every node; follow the links.
- Monorepos and folders of multiple repos rank fairly across sub-projects —
  hits carry `[scope/]` labels naming which one they're from. Narrow with
  `graft ask "<task>" --in <scope>/` once you know where you're working.

If a returned span is truncated ("+N more lines"), open the file at that exact
range before finalizing. Only open source files when a node genuinely lacks a
needed detail, and then at the exact file:line the node points to — never
re-read whole files.

After big code changes, refresh the graph with `graft build` (deterministic,
no API key, $0).
<!-- graft:end -->

## アプリ本体（static/mode-q1.js）の編集

`static/mode-q1.js` は **生成物**。正本は `static/src/*.js` で、ファイル名の数値接頭辞順に
そのまま連結すると `static/mode-q1.js` になる（全体で1つのIIFEなので、各断片は単体では
完結しない＝`node --check` は通らない）。

- 編集は `static/src/` 側で行い、`npm run build` で再生成する。
- `npm test` の先頭で生成物の鮮度を検証する。ズレていればエラーになる。
- `static/mode-q1.js` を直接編集しない。次のビルドで失われる。
- 区間の追加・分割順の変更は `scripts/build-mode-q1.cjs` の `PARTS` を直す。

`static/mode-q1.js` か `static/styles.css` を変更したら、`index.html` の該当する
`?v=` を上げる（配信済みキャッシュ対策）。

`scripts/check-*.cjs` はアプリのソースをテキストとして読む。読み込みと
`extractFunctionBody` は `scripts/lib/app-source.cjs` に集約してあるので、そちらを使う。

## 文脈推測（Context Discovery）データの追加

2級セットは `scripts/build-context-datasets.mjs`（Gemini生成）→ レビュー →
`scripts/publish-expanded-context-datasets.mjs` の流れで `data/context_*.json` を作る。

1級セットは人が書いた原稿から組み立てる。

- 原稿: `data/context-src/eiken1-<round>.json`
  - 各項目は `q` / `target` / `sense` / `sentences` / `clues` / `distractors` / `reason`。
  - `sentences[0]` は語彙データの `example` をそのまま置く（2文または3文）。
  - `target` は全体でちょうど1回。`clues` は1文の中に収まり、targetや他のclueと重ならない。
  - `sense` は語彙データの `meaning` を「、；／,」で分けた要素のいずれか。
  - `distractors` は3つ。その語の別の語義は使わない。
  - `reason` は「〜と述べられています」のような理由の本文だけを書く。手がかりの引用と
    「そのため、TARGETは「SENSE」だと推測できます。」は組み立て側が付ける。
- 組み立て: `node scripts/build-q1-context-datasets.mjs [round ...]`
  （引数なしで原稿のある全roundを再生成する）。`data/context_1_<round>.json` を書き出し、
  `data/manifest.json` の `contextUrl` / `contextTotal` も更新する。
- 検証: `scripts/check-context-eiken1-datasets.cjs`（`npm test` に含む）。
  2級と同じ `context-validator` / `context-leakage-validator` を通す。
  解説に想定外の文字体系（キリル文字など）が混ざっていないかも確認する。
- 1文目は語彙データの example をそのまま使うため、そこだけを根拠に
  `DIRECT_DEFINITION`（"that is" が関係詞として現れる等）と判定された場合に限り、
  原稿へ `"leakageReview": {"status": "accepted", "reason": "…"}` を書いて通す。
  それ以外の leakage FAIL は本文を書き直す。

アプリ側は級を問わず manifest の `contextUrl` があるセットで文脈推測を有効にするため、
コードの変更は不要。

### Jev による内容点検

語義・手がかり・解説の内容面は機械チェックでは判定できないため、
`scripts/jev_check_contexts.py`（TypeSafe System One）で点検する。
`TYPESAFE_API_KEY` が必要。1件につき6つの判定（正解選択・複数成立・語義・
手がかりの十分性・答えの露出・解説の一致）を投げ、基準に触れた項目だけを報告する。

```bash
python scripts/jev_check_contexts.py data/context_1_mock-1.json --sample 5   # 傾向を見る
python scripts/jev_check_contexts.py data/context_1_*.json --concurrency 12  # 全件
```

結果は `out/jev-context-<datasetId>.json`（`out/` は .gitignore 済み）。
語句空所補充の側は `scripts/jev_check_questions.py` が担当する。

## 問題セットの追加

大問1の問題セット（自作模試・新しい回）を追加するときは、
`.claude/skills/add-question-set/SKILL.md` の手順に従う（Claude Code / Codex 共通の正本）。
語彙の重複制約・機械チェック・manifest と README の組み込みまでを含む。

既存セットの**形式・構造**を英検1級セット基準で監査するときは
`.claude/skills/audit-question-set/SKILL.md` に従う（`scripts/audit_question_set.py`）。
内容面（語義・和訳・難易度・正答一意性）は対象外。
