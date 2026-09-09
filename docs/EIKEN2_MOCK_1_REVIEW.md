# 英検2級 模試第1回 独立レビュー

## 出典と編集範囲

- ユーザー提供の「Chapter 3 模擬テスト 第1回」原稿を入力素材にした。
- 書誌情報と原本URLは確認していないため、出典を推測していない。
- 設問文・選択肢の構造を基に、設問訳・語句の意味・例文・例文訳・核心イメージを学習用に作成した。
- 2級既存データ、全配信熟語、原形辞書との衝突を避けるため、下表の選択肢を置き換えた。

| 問 | 原稿の語句 | 採用語句 | 理由 |
| --- | --- | --- | --- |
| 1 | frown | flee | `vocab_2026-1.json` の2級語彙と重複 |
| 6 | surgery | scenery | `vocab_2025-2.json` の2級語彙と重複 |
| 7 | suppose | estimate | `lemmas.json` の原形辞書と衝突 |
| 12 | in place | out of place | `vocab_iuhw_set-1.json` の熟語phraseと重複 |
| 13 | except for | in accordance with | `vocab_p2_2026-1.json` の熟語phraseと重複 |
| 13 | due to | owing to | `vocab_p2_mock-4.json` の熟語phraseと重複 |
| 15 | as a result | in fact | `vocab_iuhw_set-2.json` の熟語phraseと重複 |

## 独立レビュー

- 使用モデル: `qwen3:8b`（Ollama、生成用モデルとは別のローカルレビューセッション）
- 入力: `data/questions_2_mock-1.json` から `q`・`stem`・`choices` だけを抽出。`answerIndex`、訳、語彙メタデータは入力から除外した。
- 判定基準: 各設問で自然かつ文法的に成立する選択肢が1つだけかを確認。ファイル変更は禁止した。

| 問 | 判定 | レビュー上の成立選択肢 | 採用正答 |
| ---: | --- | ---: | ---: |
| 1 | UNIQUE | 3 | 3 |
| 2 | UNIQUE | 1 | 1 |
| 3 | UNIQUE | 2 | 2 |
| 4 | UNIQUE | 2 | 2 |
| 5 | UNIQUE | 4 | 4 |
| 6 | UNIQUE | 1 | 1 |
| 7 | UNIQUE | 1 | 1 |
| 8 | UNIQUE | 2 | 2 |
| 9 | UNIQUE | 4 | 4 |
| 10 | UNIQUE | 1 | 1 |
| 11 | UNIQUE | 3 | 3 |
| 12 | UNIQUE | 3 | 3 |
| 13 | UNIQUE | 2 | 2 |
| 14 | UNIQUE | 4 | 4 |
| 15 | UNIQUE | 1 | 1 |
| 16 | UNIQUE | 3 | 3 |
| 17 | UNIQUE | 2 | 2 |
| 18 | UNIQUE | 4 | 4 |
| 19 | UNIQUE | 4 | 4 |
| 20 | UNIQUE | 1 | 1 |

判定結果: 20問すべて `UNIQUE`、採用正答との不一致なし。

## 機械検証

- `py -3 scripts/check_eiken2_mock_1_data.py`
- `py -3 scripts/check_q1_data.py`
- `py -3 scripts/enrich_flashcard_fields.py --file data/vocab_2_mock-1.json`
