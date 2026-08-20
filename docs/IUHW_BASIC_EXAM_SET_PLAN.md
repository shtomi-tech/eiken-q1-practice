# 国際医療福祉大学 総合型選抜 基礎試験セット（iuhw-set-1）を追加する実装計画

対象: 新規 `scripts/build_q1_iuhw_set_1_data.py` / `data/questions_iuhw_set-1.json` /
`data/vocab_iuhw_set-1.json` / `data/manifest.json` / `static/mode-q1.js` /
`scripts/check_q1_data.py` / `scripts/check-grade-scope.cjs` / `scripts/generate_tts_1.py` /
`assets/audio/vocab/iuhw/set-1/` / `README.md`
状態: 実装済み（2026-08-20、未コミット）。9節に実装との差分を記載。

## 0. 目的

国際医療福祉大学 総合型選抜 入試の基礎試験を1セット追加する。
**本文（passage）は日本語で、英語は正誤判定の選択肢文だけ**という出題形式のため、
英語部分に出る語彙60語を学習対象にする。英検以外の初のセットになる。

出典の扱い: 設問文は実際の選択肢文をもとにするが、空所化のため最小限の書き換えを行う。
日本語本文は収録しない。著作権上の懸念が出た場合は、設問文を全面的に自作文へ差し替える
（語彙60語とダミー配置はそのまま使える）。

## 1. IDと命名

`DATASET_ID_RE` が許すIDは `\d{4}-\d+` / `mock-\d+` / `set-\d+` の3種のみ
（[mode-q1.js:34](../static/mode-q1.js)）。年度が特定できないため `set-1` を使う。

| 項目 | 値 |
| --- | --- |
| datasetId | `iuhw-set-1` |
| label | `国際医療福祉大学 総合型選抜 基礎試験` |
| shortLabel | `医療福祉` |
| questionsUrl | `data/questions_iuhw_set-1.json` |
| vocabUrl | `data/vocab_iuhw_set-1.json` |
| 音声フォルダ | `assets/audio/vocab/iuhw/set-1/` |

## 2. 出題設計

既存契約（[check_q1_data.py:91](../scripts/check_q1_data.py)）は
**1設問 = 4選択肢 = 語彙4件（うち `is_answer` 1件）**。
60語 = **15問 × 4択**でちょうど収まる。易しい語（`male` / `figure` / `table` など）は
正答にせずダミー専用として収録し、60語すべてを意味チェック・間隔復習の対象にする。

| Q | 空所（正答） | 元になる選択肢文の題材 |
| --- | --- | --- |
| 1 | immigration | 移民と高度知識の創出 |
| 2 | uniform | 高度人材の定義 |
| 3 | ratio | 博士課程の留学生比率 |
| 4 | preferential | 外国人材への優遇措置 |
| 5 | reveal(s) | 英国のビザ発給数 |
| 6 | doctor(s) | 日本の医師の長時間労働 |
| 7 | promoted | 女性医師の昇進 |
| 8 | average | OECD平均との比較 |
| 9 | percentage | 女性医師の割合 |
| 10 | position(s) | 医師の勤務・役職（要文の調整、3.2参照） |
| 11 | strengthened | 血縁・地縁の相互扶助 |
| 12 | disparities | 所得格差の縮小 |
| 13 | growth | 経済成長の下支え |
| 14 | expenses | 社会保障給付費に占める医療費 |
| 15 | proportion | 歳出に占める社会保障費 |

残り45語は同一設問内のダミーとして配置する。

### 2.1 ダミー選択肢の規則

- 正答と**同じ品詞**を選ぶ（名詞の空所に動詞を並べない）。
- 同一設問内で `meaning` が重複すると `check_q1_data.py` が落ちる。
  「割合」系は訳語を書き分け、かつ別設問へ分散する：
  `ratio`=比率 / `percentage`=百分率、〜% / `proportion`=割合。
- 文脈的に成立してしまう語をダミーにしない（正答が一意に決まること）。

### 2.2 設問文の調整

15文のうち、`male` / `female` / `most` など空所化しても語彙学習にならない文がある。
その場合は**対象語が自然な空所になるよう最小限に書き換える**（Q10）。
書き換えた設問には `meta.note` にその旨を残す。

## 3. 成果物

1. `scripts/build_q1_iuhw_set_1_data.py` — `QUESTIONS` と `DETAILS` をベタ書きし、
   JSON 2本を出力する。[build_q1_p2_mock_1_data.py](../scripts/build_q1_p2_mock_1_data.py)
   と同型。正本がこの1ファイルに集約され、再生成できる。
2. `data/questions_iuhw_set-1.json` / `data/vocab_iuhw_set-1.json` — 生成物（コミットする）。
3. `assets/audio/vocab/iuhw/set-1/*.mp3` — 60語のTTS（6節）。
4. `data/manifest.json` / `static/mode-q1.js` / 各チェックスクリプト / `README.md` の追記。

### 3.1 データ形式

`vocab_iuhw_set-1.json`

```json
{ "meta": { "grade": "国際医療福祉大学", "round": "set-1", "section": "基礎試験 英語（選択肢文の語彙）",
            "source": "...", "counts": { "words": 60, "idioms": 0, "total": 60 } },
  "words": [ { "q": 1, "word": "immigration", "is_answer": true, "pos": "名詞",
               "meaning": "移民（の流入）", "example": "...", "exampleTranslation": "..." } ],
  "idioms": [] }
```

`questions_iuhw_set-1.json`

```json
{ "meta": { ... },
  "questions": [ { "q": 1, "stem": "According to the passage, ( ) is an important factor in the creation of advanced knowledge.",
                   "choices": ["immigration", "definition", "expenditure", "disparity"],
                   "answerIndex": 0, "translation": "..." } ] }
```

`example` / `exampleTranslation` / `pos` は必須チェック対象ではないが、
暗記カードUIが使うため60語すべてに入れる。

## 4. コード変更（[static/mode-q1.js](../static/mode-q1.js)）

英検前提のハードコードが4箇所ある。いずれも1行〜数行。

| 箇所 | 変更 | 変更しないと起きること |
| --- | --- | --- |
| `GRADE_BY_PREFIX`（L33） | `iuhw: "iuhw"` を追加 | 「級不明」となり意味だけ復習のプールから丸ごと外れる／音声パスが空になる |
| `GRADE_PREFIXES` / `GRADE_CHOICE_ORDER` / `GRADE_LABELS`（L36-43） | `iuhw` を追加（ラベル「医療福祉」、順序は末尾） | 級絞り込みが保存済み（例: 1級）の端末で新セットが表示されない |
| `datasetHeadline`（L164） | 接頭辞「英検」を英検プレフィックス限定にする | 見出しが「英検医療福祉 大問1」になる |
| `datasetSetLabel`（L1632）/ `datasetSetKind`（L1627） | 同上。種別は「基礎試験」を返す | セット名から接頭辞が剥がれず、「過去問」に分類される |

`VOCAB_GOALS` には追加しない → `vocabGoal` が null を返し、語彙目標カードが自動的に非表示になる
（英検の級別語彙目標は他大学入試に当てはまらないため）。

## 5. 検証

- `scripts/check_q1_data.py` の `EXPECTED_IDS` に `iuhw-set-1` を追加（manifestキーの完全一致
  チェックがあるため必須）→ `py -3 scripts/check_q1_data.py`
- `scripts/check-grade-scope.cjs` の
  `assert.match(js, /const GRADE_CHOICE_ORDER = \["pre2", "2", "pre1", "1"\]/)` を更新し、
  `iuhw` スコープの絞り込みケースを1つ追加 → `npm test`
- ローカル確認（`py -3 -m http.server 8061 --bind 127.0.0.1`）:
  ホームに新セットが出る／1問通しで解ける／意味チェックが動く／音声ボタンが鳴る／
  級を「医療福祉」に絞ると他級が消える／コンソールエラーなし。

## 6. 音声（MP3）

[generate_tts_1.py](../scripts/generate_tts_1.py) の `GRADE_CONFIG` に1行追加する。

```python
"iuhw": {"pattern": "vocab_iuhw_*.json", "filename": r"vocab_iuhw_(set-\d+)\.json", "folder": "iuhw"},
```

`vocab_iuhw_set-1.json` は既存の `"2"` 用パターン `vocab_(\d{4}-\d+)\.json` には一致しないため、
他級の生成対象を汚さない。

```powershell
$env:AZURE_SPEECH_KEY = "AzureポータルのKEY 1"
$env:AZURE_SPEECH_REGION = "japaneast"
py -3 scripts/generate_tts_1.py --grade iuhw --round set-1 --dry-run
py -3 scripts/generate_tts_1.py --grade iuhw --round set-1
```

出力先は `assets/audio/vocab/iuhw/set-1/<slug>.mp3`（60ファイル、熟語なし）。
MP3が無い間はブラウザ内蔵音声にフォールバックする（[mode-q1.js:1005](../static/mode-q1.js)）ため、
音声生成はデータ投入後に独立して実施できる。

## 7. 作業順

1. `build_q1_iuhw_set_1_data.py` を書き、JSON 2本を生成
2. `manifest.json` 追記 → `check_q1_data.py` の `EXPECTED_IDS` 追記 → データ検証を通す
3. `mode-q1.js` 4箇所 + `check-grade-scope.cjs` → `npm test`
4. ローカルブラウザ確認
5. TTS生成（Azureキーはユーザー実行）
6. `README.md` 更新（セット数 23→24、対象データ一覧）

## 8. 想定外・未確定

- 出題年度が不明。判明したら `iuhw-2026-1` 等へIDを変える必要があり、その時点の進捗
  （`eiken_q1_progress_iuhw-set-1`）は引き継がれない。**IDを後から変えるなら早いほうがよい。**
- `shortLabel` 「医療福祉」は級ラベルの位置に出る。他大学セットが増えたら
  「大学入試」等の上位カテゴリへの再設計を検討する（今回はしない）。
- 語彙60語は選択肢文由来のため、`work` / `show` などの超基礎語は除外済み。

## 9. 実装メモ（2026-08-20）

初回実装では60語のうち40語が一覧外のフィラー語（musical / wooden / festivals など）に置き換わり、
`fiscal` `doctoral` `mutual` `benefits` `security` などが未収録になっていた。原因は
ビルドスクリプトが「同一設問内は全4件同一品詞」を必須にしていたことで、
品詞が偏った60語では満たせず、同品詞の別語で埋める方向に流れたため。次のとおり作り直した。

### 9.1 choices と見出し語の二層化

60語の品詞は名詞32・形容詞17・動詞7・その他4で、15問すべてを同一品詞の4択にはできない。
そこで `QUESTIONS` に `choices`（空所に入る語形）と `items`（`WORD_LIST` の見出し語）を並べ、
学習見出し語は60語の原形のまま、選択肢は活用形を許すようにした。
対応の検証は `check_q1_data.py` の `surfaces_match` をそのまま import して使う。
例: Q11 は choices `functioned / strengthened / numbered / figured`、items は
`function / strengthen / number / figure`。

### 9.2 ビルド時の検証を入れ替え

- 追加: **`items` の集合が `WORD_LIST` の60語と完全一致**（今回の欠陥を検出できる唯一の条件）
- 追加: 選択肢が設問文に出ていないこと、例文の見出し語一致を語境界付きで判定（`per` が `person` に誤マッチしていた）
- 変更: 「全4件同一品詞」→「**正答と同品詞が2件以上、または選択肢の語形が揃っている**」
- 削除: 品詞混在の設問数の上限（語彙側の偏りで決まる値のため。件数は生成時に表示する。現状 9/15）

### 9.3 音声

見出し語が入れ替わったため、`assets/audio/vocab/iuhw/set-1/` の43件が不要になり、43件が不足する。
再生成は次で行う（MP3が無い語はブラウザ内蔵音声で再生される）。

```powershell
py -3 scripts/generate_tts_1.py --grade iuhw --round set-1
```
