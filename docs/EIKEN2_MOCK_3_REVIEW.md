# 英検2級 模試第3回 独立レビュー

## 出典と編集範囲

- ユーザー提供の「Chapter 3 模擬テスト 第3回」原稿を入力素材にした。
- 書誌情報と原本URLは確認していないため、出典を推測していない。
- 設問文・選択肢の構造を基に、設問訳・語句の意味・例文・例文訳・核心イメージを学習用に作成した。
- 2級既存データ、全配信熟語、原形辞書との衝突を避けるため、下表の選択肢を置き換えた。

| 問 | 原稿の語句 | 採用語句 | 理由 |
| --- | --- | --- | --- |
| 2 | whispers | visions | 準2級既存語彙の `whisper` と語形が重複 |
| 3 | means | method | 第2回の語彙と語形が重複 |
| 3 | charge | expense | 第1回の語彙と語形が重複 |
| 11 | fault | problems | 第2回の語彙と語形が重複 |
| 11 | trouble | approval | 独立レビューで `finding trouble with me` も成立したため差し替え |
| 13 | in other words | in that case | 2026年度第1回の熟語phraseと重複 |
| 14 | put up with | deal with | 準2級模試第3回の熟語phraseと重複 |
| 14 | come up with | get along with | 準2級模試第3回の熟語phraseと重複 |
| 17 | within | near | 第2回の語彙と語形が重複 |
| 17 | on | under | 5級の語彙と語形が重複 |
| 17 | after | in memory of | 5級の語彙と語形が重複 |
| 19 | help | waiting | `helping` と surface variant が重複 |
| 19 | will help | sitting | `helping` と surface variant が重複 |
| 19 | having helped | visiting | `helping` と surface variant が重複 |

## 独立レビュー

- 使用モデル: `qwen3:8b`（Ollama、生成用モデルとは別のローカルレビューセッション）
- 入力: `data/questions_2_mock-3.json` から `q`・`stem`・`choices` だけを抽出。`answerIndex`、訳、語彙メタデータは入力から除外した。
- 判定基準: 各設問で自然かつ文法的に成立する選択肢が1つだけかを確認。ファイル変更は禁止した。

| 問 | レビュー判定 | 成立する選択肢 | 採用正答 |
| --- | --- | --- | --- |
| 1 | UNIQUE | 1 | 1 |
| 2 | UNIQUE | 4 | 4 |
| 3 | UNIQUE | 1 | 1 |
| 4 | UNIQUE | 3 | 3 |
| 5 | UNIQUE | 2 | 2 |
| 6 | UNIQUE | 4 | 4 |
| 7 | UNIQUE | 3 | 3 |
| 8 | UNIQUE | 2 | 2 |
| 9 | UNIQUE | 2 | 2 |
| 10 | UNIQUE | 1 | 1 |
| 11 | UNIQUE | 2 | 2 |
| 12 | UNIQUE | 4 | 4 |
| 13 | UNIQUE | 1 | 1 |
| 14 | UNIQUE | 2 | 2 |
| 15 | UNIQUE | 2 | 2 |
| 16 | UNIQUE | 1 | 1 |
| 17 | UNIQUE | 4 | 4 |
| 18 | UNIQUE | 2 | 2 |
| 19 | UNIQUE | 1 | 1 |
| 20 | UNIQUE | 2 | 2 |

判定結果: 20問すべて `UNIQUE`。レビュー上、採用正答と成立する選択肢は全問一致した。

## 機械検証

- `py -3 scripts/check_eiken2_mock_3_data.py`
- `py -3 scripts/check_q1_data.py`
- `py -3 scripts/enrich_flashcard_fields.py --file data/vocab_2_mock-3.json`
