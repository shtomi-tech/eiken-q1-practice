# 英検2級 模擬テスト第4回 レビュー記録

## 対象

- 入力: ユーザー提供の「Chapter 3 模擬テスト 第4回」
- 収録: 20問、80語句（単語57、熟語23）
- 出典表記: ユーザー提供資料。出典情報は追加推定していない。

## 収録時の調整

既存の2級データとの表層重複、熟語共有辞書との重複、または独立レビューでの曖昧さを避けるため、次を調整した。正答の意味は維持している。

| 問題 | 調整 |
| --- | --- |
| 2 | `suspects` を `strangers` に変更（同級データの `suspect` 重複回避） |
| 3 | `attempted` を `folded` に変更（同級データの `attempt` 重複回避） |
| 4 | `democracy` を `geometry` に変更（既存語・同級データとの重複回避） |
| 5 | `reserved` を `destroyed` に変更（同級データの `reserve` 重複回避） |
| 7 | 正答語を `qualify` から `compete` に変更し、語法に合わせて `qualify for` を `compete in` に調整 |
| 9 | `supplied` を `tracked` に変更（同級データの `supply` 重複回避） |
| 10 | `details` を `souvenirs` に変更（第3回の `detail` 表層重複回避） |
| 11 | `identical to` を `similar to` に変更（既存熟語との重複回避） |
| 12 | `for good` を `in writing` に変更（既存熟語との重複回避） |
| 13 | `even if` を `as if` に変更（既存熟語との重複回避） |
| 14 | `public` を `money` に変更（既存語との重複回避） |
| 15 | `make` を `manage`、`share` を `own` に変更し、文中も `manage it` に調整 |
| 17 | `using tape` を追加し、標識を貼り付ける `stuck` が一意になるよう調整 |
| 20 | 目覚ましが未設定だった事実を追加し、過去の根拠に基づく推量 `must not have` が一意になるよう調整 |

## 独立レビュー

`qwen3:8b`（ローカル Ollama）に、正答・訳・メタデータを伏せた問題文と選択肢だけを渡した。第20問の文脈調整前に全20問をレビューし、20問すべてについて一意判定を得た。その後、第20問だけは最終文面で追加確認した。

| 問題 | 採用正答 | 判定 |
| ---: | ---: | --- |
| 1 | 1 | UNIQUE |
| 2 | 4 | UNIQUE |
| 3 | 2 | UNIQUE |
| 4 | 4 | UNIQUE |
| 5 | 1 | UNIQUE |
| 6 | 3 | UNIQUE |
| 7 | 4 | UNIQUE |
| 8 | 1 | UNIQUE |
| 9 | 4 | UNIQUE |
| 10 | 2 | UNIQUE |
| 11 | 3 | UNIQUE |
| 12 | 1 | UNIQUE |
| 13 | 3 | UNIQUE |
| 14 | 3 | UNIQUE |
| 15 | 3 | UNIQUE |
| 16 | 4 | UNIQUE |
| 17 | 2 | UNIQUE |
| 18 | 2 | UNIQUE |
| 19 | 3 | UNIQUE |
| 20 | 4 | UNIQUE |

第20問は全体レビュー時にモデルが `should not have` と誤読したため、最終文面に目覚ましが未設定だった事実を加え、文法に絞った再確認を実施した。`must not have` は事実からの強い推量、`should not have` は「すべきではなかった」という評価・後悔を表す。最終文脈は前者であり、採用正答は4とした。

## 検証

- `py -3 scripts/build_q1_eiken2_mock_4_data.py`
- `py -3 scripts/enrich_flashcard_fields.py --file data/vocab_2_mock-4.json`
- `py -3 scripts/check_eiken2_mock_4_data.py`
- `py -3 scripts/check_q1_data.py`
- `npm test`
