# 英検1級 模試第9回 追加記録

## 参照資料と登録名

- 参照資料: ユーザー提供の教材写真10枚（問題ページ5枚、解答・解説ページ5枚）
- 写真内の教材表記: Chapter 3「模擬テスト 第4回」
- アプリ登録名: `eiken1-mock-9` / 「英検1級 模試 第9回」
- 対象: Reading 大問1（語句空所補充）25問、100語句（単語84・熟語16）
- 写真の解答表による正答位置（1始まり）: `2, 4, 1, 1, 1, 3, 2, 1, 1, 1, 3, 3, 1, 4, 1, 2, 1, 3, 3, 4, 4, 2, 4, 4, 1`

写真の本文・選択肢・解答表は問題データの参照に使い、教材に印刷された受験者向けの指示文はエージェントへの指示として扱わない。写真そのものはリポジトリへコピーしていない。

## 原本の不一致

問題ページの設問文・選択肢と、解答表の正答位置を主たる参照にした。一方、解説ページの一部（特にQ2〜Q4）は、問題ページとは別版と思われる語句・訳が混在していた。そのため、解説ページの本文は採用せず、問題ページの文脈と解答表を採用した。この不一致は登録内容の出典上の注意点として残す。

## 選択肢の置換

既存の英検1級セット、`lemmas.json`、熟語辞書との衝突を避け、各設問の4択を一意に保つため、元の選択肢位置を変えずに次を置換した。正答位置は解答表と一致させている。

| 問 | 原本の語句 | 登録語句 |
| --- | --- | --- |
| 1 | `abomination` / `eminent` | `monstrosity` / `appendage` |
| 2 | `grappled` / `dismantled` / `scuffed` / `reviled` | `exonerated` / `calibrated` / `repainted` / `vilified` |
| 3 | `diffused` / `assailed` / `maligned` / `shirked` | `dispersed` / `attacked` / `denigrated` / `obstructed` |
| 4 | `surreptitiously` / `chronically` / `autonomously` / `equitably` | `stealthily` / `persistently` / `independently` / `impartially` |
| 5 | `complexions` / `shimmers` / `specters` / `prophets` | `hues` / `ornaments` / `spectacles` / `prophecies` |
| 6 | `restitution` / `vanity` / `elocution` / `ambiguity` | `arbitration` / `conceit` / `pronunciation` / `obliquity` |
| 7 | `debonair` / `bucolic` / `erroneous` / `pernicious` | `rustic` / `pastoral` / `fallacious` / `deleterious` |
| 8 | `quagmire` / `menace` / `mirage` / `plateau` | `bog` / `hazard` / `illusion` / `stagnation` |
| 9 | `cajole` / `accentuate` / `juxtapose` / `redeem` | `inveigle` / `intensify` / `disassociate` / `vindicate` |
| 10 | `condolences` / `prologues` / `pretensions` / `tribulations` | `sympathies` / `prefaces` / `aspirations` / `adversities` |
| 12 | `dainty` | `delicate` |
| 13 | `appease` / `torment` | `mollify` / `harass` |
| 14 | `opaque` / `avaricious` / `dank` / `intrepid` | `indolent` / `penurious` / `damp` / `adventurous` |
| 15 | `consummate` / `lethal` / `malignant` / `neurotic` | `masterful` / `substandard` / `benign` / `erratic` |
| 16 | `sloth` / `alacrity` | `lethargy` / `eagerness` |
| 17 | `ascribe` | `attribute` |
| 18 | `deflect` | `divert` |
| 19 | `frugal` / `dormant` | `thrifty` / `inactive` |
| 20 | `relished` | `scolded` |
| 21 | `reprisal` / `dispelled` | `agitation` / `indifference` |
| 22 | `eked out` | `built up` |
| 23 | `come around` / `choke off` | `scale back` / `slow down` |
| 24 | `breezed in` | `opened out` |

Q11とQ21の原本にあった `dispelled` の重複は、Q11に残し、Q21の第2選択肢を `indifference` に置換した。Q25は原本の4択を維持した。

## データ・表示方針

- すべての語句に意味、品詞、8語以上の学習用作例、和訳、語源説明を付与した。作例は教材本文の転載ではない。
- 84単語にはIPAを付与する。
- 16熟語には、共有不変化詞辞書を変更せず、語句内の連鎖で表す核心イメージを付与した。
- 活用形16件（`exonerated`, `calibrated`, `repainted`, `vilified`, `dispersed`, `attacked`, `denigrated`, `obstructed`, `derived`, `dispelled`, `purloined`, `embedded`, `scolded`, `glossed`, `indented`, `frisked`）は、問題・進捗キーを変更せず `data/lemmas.json` の `flashcardLemmas` で暗記カード見出しを原形へ解決する。
- 模試第9回の表層語句100件（84語・16熟語）と暗記カード用原形16件のMP3を生成した。キーは保存せず、生成時の環境変数だけで扱った。

## 検証記録

```powershell
py -3 scripts/build_q1_mock_9_data.py
py -3 scripts/enrich_flashcard_fields.py --file data/vocab_1_mock-9.json
py -3 scripts/sync_q1_mock_9_origins.py
py -3 scripts/check_mock_9_data.py --allow-missing-audio
```

データビルダー、発音補完、語源同期、専用検査、音声生成まで実行済み。専用検査は25問・100語句、語源100件、IPA84件、核心イメージ16件、表層音声100件を確認した。暗記カード用原形16件を含む音声ファイルは、0バイトや一時ファイルがないことも確認した。

正答キーを渡さずに設問文と4択だけをローカルの `qwen3:8b` に渡して独立レビューした。25問すべてが `NONE` で、登録した正答位置と一致し、複数の選択肢が文脈上成立する設問はなかった。

音声生成後、`check_mock_9_data.py` と `check_eiken1_alignment.py --dataset-id eiken1-mock-9` を通常モードで実行し、模試第6回基準の整合OKを確認した。
