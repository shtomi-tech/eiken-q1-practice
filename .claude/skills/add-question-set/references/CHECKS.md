# 機械チェックの中身と、選定時の下調べコマンド

## どの検査が何を見ているか

### `py -3 scripts/check_q1_data.py`（全セット共通・データ契約）

- `data/manifest.json` のキーが `defaultDatasetId` と `q1` だけであること
- `manifest.q1` のIDの集合が `EXPECTED_IDS` と**完全一致**すること
  → **新セットを追加したら必ず両方を直す**
- `manifest` の `totalQuestions` / `totalVocabulary` が実データと一致すること
  （`--update-manifest` で実データから書き戻せる）
- 設問番号が 1..N で連続、語彙の `q` と設問番号が一致
- 各設問の `choices` が4件・`answerIndex` が 0..3
- 各設問の語彙4件と `choices` が語形の揺れを含めて1対1対応（`surface_variants()`）
- 同一設問内で `meaning` が重複しない
- `eikentopic-*` はテーマ別専用の追加規則（axis・設問文語数・例文骨格の一意性）

### `py -3 scripts/check_p2_mock_data.py`（準2級の自作模試のみ・内容）

`check_q1_data.check_dataset()` を呼んだうえで、さらに:

| 検査 | 条件 |
| --- | --- |
| 件数 | 15問 / 語40 / 熟語20、正答項目15件 |
| 会話文 | `A:` を含む設問が6〜8問 |
| 設問文 | 15〜35語、`(   )` がちょうど1か所、訳に空所記号なし |
| 正答・ダミー | どちらも stem に出ていない（語形変化も判定） |
| 4択の品詞 | 設問内で一致 |
| 正答位置 | 各位置3〜5件 |
| 例文 | 8語以上、見出し語句がちょうど1回、骨格がセット内で重複しない |
| 語句の重複 | 同一セット内・**準2級の全 `vocab_p2_*.json`** と重複しない |
| 原形辞書 | 新語が `lemmas.json` のキー・原形値と一致しない |
| 熟語 phrase | **全 `vocab_*.json`** の熟語 phrase と重複しない |
| 熟語の pos | `熟語` 不可。既存データにある熟語ラベルの集合内 |
| 句動詞 | `coreImage.particle` を持つ熟語が4件以上 |

単一セットだけ検査: `py -3 scripts/check_p2_mock_data.py --dataset mock-5`

### `npm test`（Node の契約チェック群）

問題セット追加で落ちやすいのは次の2つ。**どちらも全級・全 `vocab_*.json` が対象**。

- `check-lemma-headword.cjs` — `data/vocab_*.json` 全件から原形ごとの出題形・意味を集計し、
  `build_lemma_entries.py` の `REVIEWED_MEANING_DIGEST` と照合する。
  新語が `lemmas.json` のキーまたは原形値に一致すると集計が変わって落ちる。
- `check-core-image-data.cjs` — manifest が配信する全セットの熟語に、
  `coreImage` があるか、`cReasons`（このスクリプト内）に理由が書いてあるかを要求する。
  `chain` は2〜5要素・最終要素に `term` を置かない・`term` は小文字原形で phrase と対応・
  `particleSense` は `data/particle_images.json` にある id（`general` 不可）・
  仲間例に自分自身を含めない。同じ `particle` × `particleSense` を1セット内で使い回すほど
  辞書側に必要な仲間例が増える（`3 + (使用回数 - 1)`、上限6）ので**同じ sense に偏らせない**。

### 自作セット専用の内容チェック

`check_p2_mock_data.py` は準2級専用である。1級・2級・準1級・iuhwなどの自作セットでは、追加したセット専用の `scripts/check_<set>_data.py` を作るか、既存検査を一般化してからセットを完成扱いにする。少なくとも次を検査する。

- manifest件数と、設問・語彙の件数および `q` の対応
- 4択、正答位置、同一設問の品詞・意味、正答とダミーの本文露出
- 例文の語句出現回数・語数・骨格重複、和訳の空所記号
- 同級既存語句・原形辞書・全配信熟語との重複
- 熟語の `pos` と `coreImage` の型

例: 1級模試第6回では `py -3 scripts/check_mock_6_data.py` が25問 / 100語句、84語 / 16熟語、正答位置、例文、重複を検査した。

### 模試第6回を基準にした整合監査

「模試第6回を正」として既存セットを整える場合は、まず基準自身を固定し、対象セットを1件ずつ比較する。

```bash
py -3 scripts/check_mock_6_data.py
py -3 scripts/check_<set>_data.py
npm test
```

同型の1級模試（`eiken1-mock-*`）では、少なくとも次を比較する。

| 監査軸 | 模試第6回の基準 | 判定・扱い |
| --- | --- | --- |
| 構造・件数 | 25問 / 100語句、84語 / 16熟語、設問と4択・語彙の対応 | 同型なら合わせる。別形式には強制しない |
| 内容品質 | 全語句の意味・品詞・例文・例文訳・語源、4択1正答 | 欠落を補う。正答や原本固有の内容は保持する |
| 語源・核心イメージ | 84語の語源チェーン、熟語は意味に基づく個別判断 | 説明の完成度を合わせる。chainをコピーしない |
| 原形・音声 | 出題形音声、必要な動詞の原形表示・原形MP3 | `flashcardLemmas` とMP3を照合する。出題形を上書きしない |
| 出典・ID・進捗 | 第6回固有の出典記録と `eiken1-mock-6` | 対象セット固有の出典・ID・進捗キーは保持する |

差分は `docs/<SET>_ALIGNMENT.md` に、次の分類で残す。

```text
| 監査軸 | 基準 | 対象セットの現状 | 判定（合わせる / 内容判断 / 保持） | 根拠・変更元 |
```

`mock-6` の14件の核心イメージと2件のC型（`come clean` / `rooted for`）は判断例であり、他セットへそのまま移植しない。公式過去問・別級・iuhwは、件数・出典・問題形式の差を保持したまま、互換性のある品質項目だけを合わせる。

### 原形・音声の確認

新しい語彙JSONで、`pos` が動詞かつ `-ed` / `-ing` で終わる出題形を一覧にする。

```powershell
$vocab = Get-Content data/vocab_1_mock-N.json -Raw | ConvertFrom-Json
$vocab.words | Where-Object { $_.pos -match '動詞' -and $_.word -match '(?:ed|ing)$' } |
  Select-Object word, pos, meaning
```

各語を `data/lemmas.json` の canonical `lemmas` と表示専用 `flashcardLemmas` に照合する。原形はPOS・意味・綴りを人が確認した明示的な対応表にし、語尾切り落としだけで決めない。`data/vocab_*.json` の出題形は変更しない。

ユーザーが暗記カードの音声も原形にするよう求めた場合は、音声ボタンへ原形を渡す。原形MP3がないときはブラウザ標準音声へフォールバックし、出題形MP3を原形音声として再利用しない。MP3を生成する場合はAzureキーを環境変数だけから読み、生成後に対象MP3の存在・公開先コピー・再生経路を確認する。

## 語彙選定の下調べ

同じ級の既存語句と、熟語 phrase と、原形辞書を一度に確認する。

```bash
py -3 - <<'PY'
import json, glob, sys
sys.path.insert(0, "scripts")
from check_q1_data import surface_variants

candidates = ["candidate1", "candidate2", "hold off"]   # ここに候補を並べる
grade_glob = "data/vocab_p2_*.json"                     # 追加する級に合わせる

existing = {}
for path in glob.glob(grade_glob):
    d = json.load(open(path, encoding="utf-8"))
    for bucket in ("words", "idioms"):
        for it in d.get(bucket, []):
            s = it.get("phrase") or it.get("word", "")
            for v in surface_variants(s):
                existing[v] = f"{path}:{s}"

phrases = {}
for path in glob.glob("data/vocab_*.json"):
    d = json.load(open(path, encoding="utf-8"))
    for it in d.get("idioms", []):
        phrases.setdefault(" ".join(str(it.get("phrase","")).lower().split()), path)

lemma_data = json.load(open("data/lemmas.json", encoding="utf-8"))
lem = lemma_data["lemmas"]
display_lemmas = lemma_data.get("flashcardLemmas", {})
forms = (
    {str(k).lower() for k in lem} | {str(v).lower() for v in lem.values()}
    | {str(k).lower() for k in display_lemmas} | {str(v).lower() for v in display_lemmas.values()}
)

for c in candidates:
    hits = []
    owners = [existing[v] for v in surface_variants(c) if v in existing]
    if owners:
        hits.append(f"同級既存: {owners[0]}")
    p = " ".join(c.lower().split())
    if p in phrases:
        hits.append(f"熟語phrase: {phrases[p]}")
    if c.lower() in forms:
        hits.append("lemmas.json（canonical/display）と衝突")
    print(f"{c}: {' / '.join(hits) if hits else 'OK'}")
PY
```

熟語の型（A/B/C）と particle の候補出しは読み取り専用スクリプトがある:

```bash
py -3 scripts/build_core_image_stub.py
```

## Pages公開確認（デプロイを依頼された場合のみ）

pushやActionsの成功だけでは完了にしない。該当commitのActionsを特定して完了まで待ち、公開URLから次を直接確認する。

```powershell
gh run list --workflow pages.yml --branch main --limit 5 --json databaseId,status,conclusion,headSha,url
gh run watch <run-id> --interval 5 --exit-status

$revision = (git rev-parse HEAD).Trim()
$publishRoot = 'https://shtomi-tech.github.io/eiken-q1-practice'
Invoke-WebRequest "$publishRoot/" -UseBasicParsing
Invoke-WebRequest "$publishRoot/data/manifest.json?rev=$revision" -UseBasicParsing
Invoke-WebRequest "$publishRoot/data/questions_1_mock-N.json?rev=$revision" -UseBasicParsing
Invoke-WebRequest "$publishRoot/data/vocab_1_mock-N.json?rev=$revision" -UseBasicParsing
Invoke-WebRequest "$publishRoot/static/mode-q1.js?rev=$revision" -UseBasicParsing
```

`manifest` の新ID・件数と、問題JSON・語彙JSONの実件数を読み取って一致を確認する。JS/CSSを変更した場合は、indexのキャッシュバスターも公開版で確認する。

## 出力の見方

`check_q1_data.py` は正常時に各セット1行と `Q1 data: OK` を出す。
`WARN:` 行（設問文訳に正答meaningを含まない／複数トピック）は失敗ではないが、
新セットで出たら内容を見直す。
