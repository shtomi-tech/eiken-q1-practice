# 準2級 自作模試第1回 独立レビュー

## 方法

2026-08-20、設問文と4択だけを別Agentへ渡し、正答情報と語彙データは伏せて確認した。各問で文脈上成立する選択肢、不自然な英文、語彙レベルを確認した。

## 初回レビューと修正

| 問 | 指摘 | 修正 |
| --- | --- | --- |
| 3 | `vehicle` と `route` の両方が成立し得た | `with enough seats for all six travelers` を追加し、`vehicle` に限定した |
| 13 | `left ... early to set off` が重複し、出発と到着の関係が曖昧だった | `We will set off for ... so that we can arrive before dark.` に変更した |
| 14 | `carry out rules` が不自然で、`pick up` も解釈できた | `carry out the new safety procedures correctly` に変更した |

## 修正後の判定

再レビューでは15問すべてについて成立する選択肢が1つに絞られ、不自然な表現もないと判定された。正答候補は Q1〜Q15 の順に次のとおり。

`assignment` / `affordable` / `vehicle` / `completed` / `prize` / `event` / `relieved` / `label` / `touch` / `postpone` / `go over` / `take it back` / `set off for` / `carry out` / `set up`

## 2回目のレビュー（2026-08-20、実装後チェック）

| 問 | 指摘 | 対応 |
| --- | --- | --- |
| 14 | `pick up`（習得する）でも「指示が複雑で正しく身につけるのが難しい」と読め、二重解釈が残っていた | 設問文を `Each morning the workers must (   ) a short safety check ...` に差し替え、`carry out` 以外が成立しないようにした |
| 全問 | 空所が `( )` で、既存の準2級3セットの `(   )` と表記が違っていた | 全15問を `(   )` にそろえた |
| 全語句 | `etymology` が無く、既存の準2級3セット（60/60）と差があった。フラッシュカードの「語源・なりたち」行は `item.etymology` があるときだけ表示される | 60語句すべてに `etymology` を追記し、ビルド時に欠落を検出する検査を追加した |

`collocation` は既存の準2級データには入っているが、アプリ側で参照していないため今回は付けていない。

## 会話文の比率を本番に合わせる（2026-08-20）

既存の準2級3セットは15問中の会話文が6問・6問・8問だったのに対し、自作セットは2問しかなかった。
Q2・Q7・Q11・Q15 を A: / B: の対話形式に書き換え、**6問**にそろえた。
`check_p2_mock_data.py` の判定も「ちょうど2問」から「6〜8問」に変更した。

| 問 | 書き換え後の話者設定 | 正答 |
| --- | --- | --- |
| 2 | 買い物（デパートのセール） | affordable |
| 7 | 学校（校長の発表への反応） | relieved |
| 11 | 学校（試験前の教室） | go over |
| 15 | 地域（公民館の回収箱） | set up |

4択と正答位置は変更していない。書き換え後も各問で成立する選択肢は1つだけであることを確認した。
