# 医療福祉セットの1級基準整合 実装計画（計画A）

状態: 完了（2026-09-04）。結果は `docs/IUHW_ALIGNMENT.md` に記録。

## 1. 目的

`eiken1-mock-6` を参照実装とする共通整合検査の対象から、現在唯一外れている
国際医療福祉大学セット（`iuhw-set-1` / `iuhw-set-2`）を、収録内容と進捗キーを変えずに
同じ完成条件へ揃える。

英検26セットは `py -3 scripts/check_eiken1_alignment.py --all` を0件で通過済み。
医療福祉2セットだけが `VOCAB_AUDIO_GRADE` に未登録で、検査対象になっていない。

## 2. 固定する互換性

- `iuhw-set-1` / `iuhw-set-2` の設問数・選択肢・正答位置・語句表層・`itemKey` を変更しない。
- 進捗キー `eiken_q1_progress_iuhw-set-1` / `-2`、保存キー、公開URLを変更しない。
- 1級の25問 / 100語句形式を適用しない。現在の15問 / 60語句（set-1: 58語+熟語2、
  set-2: 48語+熟語12）を保つ。
- `questions_iuhw_*.json` / `vocab_iuhw_*.json` は生成物として扱い、正本
  （`scripts/build_q1_iuhw_set_{1,2}_data.py`）または補完スクリプトから更新する。
- 語源データは既存方式どおり **出題形キー**（`lemmas.json` 適用後の原形。今回の45語は
  すべて出題形＝原形）で登録し、`lemmas.json` へ新しい原形化を足さない。

## 3. 現状と不足（監査実測値）

`VOCAB_AUDIO_GRADE` に `"iuhw": "iuhw"` を仮追加して `--all --audit` を実行した結果。

| 項目 | iuhw-set-1 | iuhw-set-2 |
| --- | ---: | ---: |
| IPA不足 | 58件（全words） | 48件（全words） |
| 語源またはC型理由の不足 | 0件 | 45件 |
| 表層MP3不足 | 0件（60/60あり） | 60件（ディレクトリ自体が無い） |
| 熟語の核心イメージ | 2/2あり | 12/12あり |
| 例文8語以上・骨格重複・語形重複・4択対応・訳 | すべて合格 | すべて合格 |
| **不整合の合計** | **58件** | **153件** |

原形音声（`flashcardLemmas`）の対象語は両セットとも0件。**原形MP3の追加生成は不要**。

set-2で語源が不足する45語:

```
surplus shortage outbreak closure dismiss educate recruit sponsor qualified retired
junior urban overseas rural retention distribution admission shift allowance burden
quota concentration expansion decline turnover leading shrinking neighboring aging dental
elderly mental chronic wages refunds contributions fines recipients taxpayers employers
volunteers premium enrollment eligibility coverage
```

## 4. 実装方針

### 段階A0: ベースラインを固定する

1. `git status --short` で既存変更がないことを確認する。
2. 開始時点の結果を記録する。

```powershell
py -3 scripts/check_eiken1_alignment.py --all
npm test
```

3. `data/manifest.json` の `iuhw-set-1` / `iuhw-set-2` の件数を実データと突き合わせる
   （固定値を手で転記しない）。

### 段階A1: IPAを補完する

対象: `scripts/enrich_flashcard_fields.py` / `data/vocab_iuhw_set-{1,2}.json`

1. `TARGET_PATTERN` に `iuhw_set-\d+` を追加する。

```python
TARGET_PATTERN = re.compile(
    r"^vocab_(?:1_(?:20\d{2}-\d+|mock-\d+)|5_20\d{2}-\d+|pre1_20\d{2}-\d+|p2_mock-\d+|iuhw_set-\d+)\.json$"
)
```

2. 件数を先に確認してから実行する（Datamuseへのネットワーク取得）。

```powershell
py -3 scripts/enrich_flashcard_fields.py --file data/vocab_iuhw_set-1.json --dry-run
py -3 scripts/enrich_flashcard_fields.py --file data/vocab_iuhw_set-1.json
py -3 scripts/enrich_flashcard_fields.py --file data/vocab_iuhw_set-2.json --dry-run
py -3 scripts/enrich_flashcard_fields.py --file data/vocab_iuhw_set-2.json
```

3. Datamuseが返さなかった語は、辞書（Merriam-Webster等）を確認して手で補い、
   `/…/` 形式（`IPA_RE`）を満たすことを確認する。推測でIPAを書かない。
4. `pos` は既に全件あるため触らない（`pos` の自動補完は `vocab_1_` のみが対象）。

受入条件:

- 106語すべてに `ipa` があり、`/…/` 形式である。
- `word` / `phrase` / `meaning` / `example` / `q` / `is_answer` に差分がない
  （`git diff` で `ipa` 行だけが増えていること）。

### 段階A2: set-2の45語へ語源を追加する

対象: `data/word_origin_research.json`（authoring正本） / `data/word_origins.json` /
`data/word_origin_excluded.json`

複数形・分詞形の語（`wages` `recipients` `qualified` など14語）は、`lemmas.json` へ新しい原形化を
足さず**出題形をキー**にして登録する。`lemmas.json` の `lemmas` に写像を足すと、原形辞書エントリ・
`meaningReviewDigest`・`build_lemma_entries.py` の承認済みハッシュ・原形MP3まで連鎖して
必要になるため、今回の目的に対して変更が大きすぎる。

`docs/WORD_ORIGIN_AUTHORING.md` の基準に従う。既存バッチと同じ25語単位で2回に分ける。

1. 追加方法は**バッチスクリプトではなく台帳への直接追記**にする。
   `apply-word-origin-research-batch.cjs` は `researchTarget`（既存B型1,255語の再調査スコープ）に
   含まれる既存エントリの更新専用で、新規語を追加できない
   （`assert.ok(target.has(lemma))` と `assert.ok(entry)` があるため）。
   新規語は `data/word_origin_research.json` の `entries` へ直接足す
   （`researchTarget` 外の既存エントリが278件あり、これが前例）。
2. 25語・20語の2回に分けて追記する。1語ごとに:
   - 2ホスト以上の独立した出典URLと `sourceNotes` を付ける。
   - A型（接辞＋語根で中心義を導ける）／B型（由来一行）／C型（分解がこじつけ）を判定する。
   - 迷った語は件数合わせでA/Bにせず、C型として `word_origin_excluded.json` へ理由を残す。
   - `display.derivation` の矢印の後ろを、`vocab_iuhw_set-2.json` の `meaning` の中心義に揃える。
   - 複合語（`outbreak` `turnover` `taxpayers`）と分詞形（`qualified` `retired` `leading`
     `shrinking` `neighboring` `aging`）は、綴りの類似だけでA型にしない。
3. 追記後に表示用辞書を再生成する。

```powershell
node scripts/rebuild-word-origin-dictionaries.cjs --write
node scripts/rebuild-word-origin-dictionaries.cjs --check
node scripts/check-word-origin-research.cjs
node scripts/check-word-origin-data.cjs
```

注: `check-word-origin-research.cjs` は entries のキーが語彙データに存在することを要求する。
`researchTarget`（既存B型1,255語の再調査スコープ）には新規語を足さない。

受入条件:

- set-2の48語すべてが `word_origins.json` または `word_origin_excluded.json` で解決する。
- `rebuild-word-origin-dictionaries.cjs --check` と `check-word-origin-research.cjs` が通る。
- 既存1,533件の語源エントリに差分がない。

### 段階A3: set-2の表層MP3を生成する

対象: `assets/audio/vocab/iuhw/set-2/`

`generate_tts_1.py` は既に `--grade iuhw` に対応済み（`GRADE_CONFIG["iuhw"]`）。

1. Azureキーはログ・ファイル・チャットへ出さず、環境変数だけで設定する。
2. 件数と出力先を先に確認する。

```powershell
py -3 scripts/generate_tts_1.py --grade iuhw --round set-2 --dry-run
py -3 scripts/generate_tts_1.py --grade iuhw --round set-2
```

3. 生成後に0バイト・欠番・熟語ディレクトリの誤りを検査する
   （words → `set-2/*.mp3`、idioms → `set-2/idiom/*.mp3`）。

受入条件:

- `assets/audio/vocab/iuhw/set-2/` に単語48件、`idiom/` に熟語12件、計60件が存在し、
  すべて0バイトより大きい。
- set-1の60件に差分がない。

### 段階A4: 共通整合検査へ組み込む

対象: `scripts/check_eiken1_alignment.py` / `README.md`

1. `VOCAB_AUDIO_GRADE` へ `"iuhw": "iuhw"` を追加する。これだけで
   `manifest_dataset_ids()` が28セットを返し、`--all` と `default_audio_required()` が
   医療福祉セットを含むようになる。
2. `--dataset-id` のヘルプ文と `parser.error()` の文言へ `iuhw-` を追加する。
3. スクリプトのdocstringと `README.md` の記述（「5級・準2級・2級・準1級・1級全セット」）を
   医療福祉を含む28セットへ更新する。
4. 5級だけに掛かっている語形重複の除外（`if prefix != "eiken5"`）は医療福祉へ広げない。

受入条件:

- `py -3 scripts/check_eiken1_alignment.py --all` が28セットすべてで「整合OK」。
- 英検26セットの結果に変化がない。

### 段階A5: 整合文書を残す

対象: `docs/IUHW_ALIGNMENT.md`（新規） / `README.md`

1. `docs/EIKEN2_ALIGNMENT.md` と同じ構成で、対象セット・件数・音声・語源・IPAの
   整合結果と実施日を記録する。
2. set-2は原本を持たない完全自作である旨（`build_q1_iuhw_set_2_data.py` のdocstring）を
   引き継いで明記する。既存の `docs/IUHW_BASIC_EXAM_SET_2_REVIEW.md` の独立レビュー結果へ
   相互リンクする。
3. set-1に独立レビュー記録が無い場合は、`review_official_questions.py` と同じ手順
   （正答を伏せて別モデルへ渡す）で15問分を実施し、結果を記録する。

受入条件:

- 文書の件数・音声状態・語源件数が実データと一致する。
- READMEの対象データ一覧とコマンド例が実態と一致する。

## 5. 検証

### 機械検査

```powershell
py -3 scripts/check_eiken1_alignment.py --all
py -3 scripts/check_q1_data.py
npm test
```

### 実ブラウザ（最小限）

`py -3 -m http.server 8061 --bind 127.0.0.1` で起動し、`?g=iuhw` の set-2 だけ確認する。

- 暗記カードでIPAと語源が表示される
- MP3が404を経由せず再生される
- 既存進捗が復元される
- コンソールエラーなし

### 差分検査

- `git diff -- data/questions_iuhw_*.json` が空である。
- `git diff -- data/vocab_iuhw_*.json` が `ipa` の追加行だけである。

## 6. コミット境界

1. IPA補完（`enrich_flashcard_fields.py` の対象拡張 + 2セットのJSON）
2. 語源バッチ1（25語）
3. 語源バッチ2（20語）
4. set-2の表層MP3
5. 共通検査への組み込みとREADME
6. 整合文書

push・デプロイは別途依頼された場合だけ行う。

## 7. 実施記録

### 段階A1（2026-09-04・完了）

- `enrich_flashcard_fields.py` の `TARGET_PATTERN` へ `iuhw_set-\d+` を追加。
- set-1に58件、set-2に48件のIPAを付与（Datamuse経由、未取得0件）。
- `ipa` 以外のフィールドに差分がないことをJSON比較で確認済み。

### 段階A2（2026-09-04・完了）

- 45語を `word_origin_research.json` へ追記。A型10語 / B型35語、C型なし。
  - A型: dismiss, educate, retention, distribution, admission, concentration,
    dental, contributions, recipients, eligibility（語根 mit / duc / ten / trib /
    centr / dent / cap / lect はすべて既存辞書のものを使い、語根・接辞の新規登録はゼロ）
  - B型35語は由来一行のみ。語根の表面形が綴りに現れない語（expansion の pans、
    closure の clos、refunds の fund、employers など）は無理に分解せずB型にした。
- 出典は1語につき2ホスト。**merriam-webster.com と collinsdictionary.com は
  WebFetchに対して403を返す**ため、etymonline.com と dictionary.com（一部
  en.wiktionary.org）の組み合わせで確認した。
- `eligibility` のみ dictionary.com 側に語源欄がなく（eligible の名詞形としての
  定義のみ）、`confidence` を `medium` にしている。
- 検査結果: `rebuild-word-origin-dictionaries.cjs --check`、
  `check-word-origin-research.cjs`、`check-word-origin-data.cjs`、`npm test` すべて成功。
  台帳1,578件 / origins 1,578件。
- 監査結果: iuhw-set-1 は不整合0件。iuhw-set-2 は表層音声60件のみ残る。

### 段階A3〜A5（2026-09-04・完了）

- set-2の表層MP3を60件生成（単語48・熟語12、0バイトなし、set-1に差分なし）。
- `check_eiken1_alignment.py` の `VOCAB_AUDIO_GRADE` へ `iuhw` を追加し、`--all` が28セットを検査。
- `iuhw-set-1` の独立レビューを実施（qwen3:8b / deepseek-r1:8b）。不一致2件はモデル側の
  文法的な誤りと判断し、教材データは変更していない。詳細は `docs/IUHW_ALIGNMENT.md`。
- README と新規 `docs/IUHW_ALIGNMENT.md` を実データに合わせて更新。

## 8. 完了条件

- `check_eiken1_alignment.py --all` が医療福祉2セットを含む28セットで0件。
- 106語すべてにIPA、set-2の48語すべてに語源またはC型理由がある。
- `assets/audio/vocab/iuhw/set-2/` に60件のMP3がある。
- 設問・選択肢・正答位置・語句表層・進捗キーに差分がない。
- `npm test` が成功する。
