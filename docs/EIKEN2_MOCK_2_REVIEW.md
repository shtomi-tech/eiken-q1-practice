# 英検2級 模試第2回 独立レビュー

## 出典と編集範囲

- ユーザー提供の「Chapter 3 模擬テスト 第2回」原稿を入力素材にした。
- 書誌情報と原本URLは確認していないため、出典を推測していない。
- 設問文・選択肢の構造を基に、設問訳・語句の意味・例文・例文訳・核心イメージを学習用に作成した。
- 2級既存データ、第1回、全配信熟語、原形辞書との衝突を避けるため、下表の選択肢を置き換えた。

| 問 | 原稿の語句 | 採用語句 | 理由 |
| --- | --- | --- | --- |
| 1 | occupations | careers | `vocab_2025-2.json` の `occupation` と語形が重複 |
| 9 | greet | praise | 第1回の語彙と重複 |
| 11 | in place | in advance of | 全配信データの熟語phraseと重複 |
| 11 | for need | in need of | 学習用の自然な熟語へ置換 |
| 12 | confident of | proud of | `vocab_2025-2.json` の熟語phraseと重複 |
| 15 | in addition to | with respect to | `vocab_p2_2025-2.json` の熟語phraseと重複 |
| 15 | on account of | as a consequence of | `vocab_p2_2025-2.json` の熟語phraseと重複 |
| 15 | instead of | despite | `vocab_p2_mock-2.json` の熟語phraseと重複 |
| 17 | sight | fashion | 第1回の語彙と重複 |
| 20 | doing | making | `surface_variants` で `do` と衝突 |

## 独立レビュー

- 使用モデル: `qwen3:8b`（Ollama、生成用モデルとは別のローカルレビューセッション）
- 入力: `data/questions_2_mock-2.json` から `q`・`stem`・`choices` だけを抽出。`answerIndex`、訳、語彙メタデータは入力から除外した。
- 判定基準: 各設問で自然かつ文法的に成立する選択肢が1つだけかを確認。ファイル変更は禁止した。

| 問 | レビュー判定 | 成立する選択肢 | 採用正答 |
| --- | --- | --- | --- |
| 1 | UNIQUE | 3 | 3 |
| 2 | UNIQUE | 4 | 4 |
| 3 | UNIQUE | 3 | 3 |
| 4 | UNIQUE | 3 | 3 |
| 5 | UNIQUE | 2 | 2 |
| 6 | UNIQUE | 1 | 1 |
| 7 | UNIQUE | 1 | 1 |
| 8 | UNIQUE | 4 | 4 |
| 9 | UNIQUE | 2 | 2 |
| 10 | UNIQUE | 4 | 4 |
| 11 | UNIQUE | 2 | 2 |
| 12 | UNIQUE | 2 | 2 |
| 13 | UNIQUE | 4 | 4 |
| 14 | UNIQUE | 2 | 2 |
| 15 | UNIQUE | 3 | 3 |
| 16 | UNIQUE | 1 | 1 |
| 17 | UNIQUE | 3 | 3 |
| 18 | UNIQUE | 4 | 4 |
| 19 | UNIQUE | 2 | 2 |
| 20 | UNIQUE | 2 | 2 |

判定結果: 20問すべて `UNIQUE`。レビュー上、採用正答と成立する選択肢は全問一致した。

## 機械検証

- `py -3 scripts/check_eiken2_mock_2_data.py`
- `py -3 scripts/check_q1_data.py`
- `py -3 scripts/enrich_flashcard_fields.py --file data/vocab_2_mock-2.json`
