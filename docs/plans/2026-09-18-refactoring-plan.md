# eiken-q1-practice リファクタリング計画（2026-09-18）

種別: 計画のみ。実装・commit・deploy は別依頼。
原則: **挙動・データ出力・保存キーを一切変えない**（振る舞い不変リファクタ）。各タスクは単独でコミット可能な大きさにする。

## 0. 現状（調査結果）

| 領域 | 事実 | 問題 |
| --- | --- | --- |
| アプリ本体 | `static/src/*.js` 12断片を連結 → `static/mode-q1.js`（4180行・1つのIIFE）。`90-learn-flow.js` 1180行/45関数、`80-home.js` 953行、`20-storage.js` 536行 | 学習フロー・フラッシュカードのジェスチャー・確認問題・完了画面が1断片に同居。断片が単体で構文完結しない |
| データ生成 (Python) | `build_q1_mock_{10..21}_data.py` 等 **約31本**が各600行前後。差分は `ROUND_ID` と `QUESTIONS/DETAILS/CORE_IMAGES` のデータ部のみ | 後半の関数群（`write_json`/`surface_variants`/`build`/`main`, 約130行）がコピペ。しかも mock-10 と mock-21 で **既に内容が食い違っている**（ハッシュ不一致）＝修正の横展開漏れリスク |
| データ検証 (Python) | `check_eiken2_mock_{1..4}_data.py` 等がほぼ同一（差分28行）。`load_json` 系ヘルパーが26ファイルに重複 | 同上 |
| 検証 (Node) | `npm test` は26個の `check-*.cjs` を `&&` で直列連結した1行 | 追加・並べ替えが読みにくい。`app-source.cjs` 集約後も一部チェックが独自に `readFileSync`+`JSON.parse` |
| 文書 | `docs/` 直下に `*_PLAN.md` / `*_REVIEW.md` が約75本フラット | 完了済み計画と現行の正本が区別できない |
| 作業ツリー | 未コミット変更16件（skill群、AGENTS.md、新規 audit スクリプト等） | リファクタ着手前に取り扱いを決める必要あり |

## 1. 守る契約（変更禁止）

- `localStorage` のキー名・`scopedStorageKey` の規則、Supabase の appId・cloud 同期 v2 の形式（共通 `portal/shared/cloud.js` が正本。`40-cloud.js` は配布物なので手で整理しない）。
- `data/*.json` の内容（語源データは出題形キー、`lemmas.json` のレビューダイジェスト）。**生成スクリプト整理後も出力はバイト一致**させる。
- `static/mode-q1.js` 生成物方式と `index.html` の `?v=` 運用。
- 公開 URL / `pages.yml` の配信ブランチ。

## 2. フェーズとタスク

### Phase 0 — 準備（必須・最初）

- **T0-1** 未コミット変更16件をユーザーがコミットするか退避するか決める（`EXTERNAL_EVIDENCE`: ユーザー判断）。リファクタは clean な作業ツリーから `refactor/*` ブランチで開始。
- **T0-2** ベースライン採取: `npm test` 成功ログ、全 Python build を一時ディレクトリへ出力したときの `data/` との一致確認手順を `scripts/verify-data-reproducible.*` として用意（`IMPLEMENT`）。
  - 受入: 現状で全 build スクリプトの出力が `data/` と一致するか一覧化。**一致しないスクリプトは記録するだけで直さない**（それ自体が別課題）。

#### Phase 0 結果（2026-09-18, ブランチ `refactor/phase0`）

- T0-1: 未コミット変更を `9164f9f` でコミット。生徒名入りの配布物（`docs/memory-sheets/`、`docs/plans/eiken2-14day-plan-qr_*.html`、`/eiken2-14day-plan.html`）は `.gitignore` に登録。
- ベースライン `npm test`: **Windows 作業ツリーでは `check-study-plan-ui.cjs:45` で失敗**。`core.autocrlf=true` で CRLF になったソースに対して、LF 前提の複数行文字列 `'studyPlanProgress(\n      "今日"'` を検索しているため。リファクタとは無関係の既存事象（CI の LF 環境では通る想定）。後続の3チェックは個別実行で成功。各フェーズの回帰判定はこの状態を基準にする。
- T0-2: **生成スクリプト単体では `data/` を再現しない**ことが判明。語彙JSONの `ipa` 等は生成後に別工程で追記されているため（31本中30本で差分）。よって Phase 1 の受入は「`data/` と一致」ではなく **「基準コミットの scripts/ と作業ツリーの scripts/ の出力がバイト一致」** に変更。検証は `python scripts/verify-builder-output.py [--base <commit>] [名前の一部...]`。現状 31/31 一致、1本を改変すると DIFF を検出することを確認済み。

### Phase 1 — データ生成スクリプトの共通化（効果最大・リスク中）

- **T1-1** 31本の build スクリプトの関数部を相互 diff し、食い違いを分類（バグ修正の横展開漏れ / 級ごとの意図的差分）。結果を本計画に追記（`VERIFY_ONLY`）。
- **T1-2** `scripts/lib/set_builder.py` を作り、`write_json`・`surface_variants`・`build`・`main` を移す。級差分は引数（grade, dataset prefix, particles 等）で表現。
- **T1-3** 各 `build_*_data.py` をデータ定義（`ROUND_ID`, `QUESTIONS`, `DETAILS`, `CORE_IMAGES`）＋ `set_builder.run(...)` 呼び出しだけに縮める。**1本ずつ置換し、毎回出力がバイト一致することを確認**。T1-1 で「意図的差分」とされたものはオプション化、「横展開漏れ」はこのタスクでは挙動を保ち、別タスクとして報告。
- **T1-4** 同様に `check_*_data.py` 系と `load_json`/`read_json` 重複を `scripts/lib/common.py` に集約。
- **T1-5** `add-question-set` skill の `AUTHORING.md`/`CHECKS.md` のテンプレートを新形式に更新（新セット追加時に再びコピペが増えないように）。
- 受入: `python scripts/verify-builder-output.py --base <Phase1着手前のコミット>` が全件一致、`python scripts/audit_question_set.py` と既存 check_*.py が成功。

### Phase 2 — 学習フロー断片の分割（リスク中）

`build-mode-q1.cjs` の `PARTS` に断片を追加するだけで、連結後のコードの**並び以外は変えない**。

- **T2-1** `90-learn-flow.js` を分割:
  - `90-session.js`（`startLearn`〜`questionProgressBar`、セッション/進捗バー）
  - `91-flashcard.js`（`buildFlashCard`〜`flashExampleRow`、ジェスチャー・語源・コアイメージ表示）
  - `92-check-practice.js`（`renderCheck`〜`onPracticeAnswer`）
  - `93-done.js`（`renderDone` 以降）
- **T2-2** `80-home.js` を「ホーム描画」と「セット/問題一覧」「学習計画・目標表示」に分割（関数の移動のみ）。
- **T2-3** `20-storage.js` を「保存キー・読み書き」と「FSRS/SRS状態計算」に分割。
- 受入: 分割前後で `static/mode-q1.js` の**関数集合が同一**（`graft skeleton` 比較）で、差分は関数の出現順のみ。`npm test` 成功。`?v=` を1つ上げる。
- 注意: `check-*.cjs` の `extractFunctionBody` は生成物全体を対象にするので影響なし。ただし断片ファイル名を直接参照するチェックがないか `graft grep "static/src"` で事前確認。

### Phase 3 — 検証ハーネス整理（リスク低）

- **T3-1** `npm test` の長い `&&` 連鎖を `scripts/run-checks.cjs`（チェック一覧の配列を順に実行し、最初の失敗で終了コード≠0）へ置換。実行順と対象は現状と同一。
- **T3-2** `check-*.cjs` 内の独自 `readFileSync`+`JSON.parse`（`check-lemma-headword`, `check-core-image-data`, `check-word-origin-data`, `check-meaning-example-ui`, `check-pre1-core-image-compat`, `check-fsrs-vendor`）を `scripts/lib/app-source.cjs` に `readJson(rel)` を足して寄せる。
- 受入: `npm test` 成功、わざと1チェックを失敗させたとき非ゼロ終了すること。

### Phase 4 — docs 整理（リスク低、ファイル移動を伴うため事前に一覧提示して確認）

- **T4-1** 完了済みの `*_PLAN.md`/`*_FIX_PLAN.md`/`*_REVIEW.md` を `docs/archive/` へ移動、現行正本（`STATE_TRANSITIONS.md`, `*_AUTHORING.md`, `*_ALIGNMENT.md`）は残す。移動対象一覧はユーザー承認後に実施し、リンク切れを検索。
- **T4-2** 直下の `eiken2-14day-plan.html` 等の生成物置き場を決める（未追跡のため T0-1 と合わせて判断）。

## 3. 順序と並列性

```
T0-1 → T0-2 → Phase1 ─┐
              Phase3 ─┼→ (各フェーズ独立にマージ可)
              Phase2 ─┘
Phase4 は任意のタイミング（承認後）
```
Phase1（`scripts/*.py`）と Phase2（`static/src`）は write_set が重ならないため並列可。Phase3 の T3-1 は `package.json` を触るので Phase2 の `PARTS` 変更とは別コミットにする。

## 4. 対象外（今回やらない）

- 挙動変更・UI改善・新機能、TypeScript化やバンドラ導入（新規依存になるため別途承認が必要）。
- `static/vendor/fsrs`・`40-cloud.js`（外部正本）。
- T1-1 で見つかった横展開漏れの**修正**（報告のみ、別タスク化）。

## 5. 未確認事項

- 全 build スクリプトの出力が現状 `data/` と一致しているか（T0-2 で確認）。
- 31本の関数部の食い違いが意図的かどうか（T1-1）。
- `docs/` のどの計画が完了済みか（T4-1 で git log と照合）。
