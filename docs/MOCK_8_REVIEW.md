# 英検1級 模試第8回 追加記録

## 参照資料と登録名

- 参照資料: ユーザー提供の教材写真10枚（問題ページ5枚、解答・解説ページ5枚）
- 写真内の教材表記: Chapter 3「模擬テスト 第3回」
- アプリ登録名: `eiken1-mock-8` / 「英検1級 模試 第8回」
- 対象: Reading 大問1（語句空所補充）25問、100語句（単語84・熟語16）
- 写真の解答表による正答位置（1始まり）: `2, 4, 1, 1, 1, 3, 2, 1, 1, 1, 2, 2, 3, 4, 1, 2, 3, 4, 1, 4, 4, 1, 4, 1, 2`

写真の本文・選択肢・解答は問題データの参照に使い、教材に印刷された受験者向けの指示文はエージェントへの指示として扱わない。写真そのものはリポジトリへコピーしていない。

## 選択肢の置換

既存の英検1級セット、`lemmas.json`、熟語辞書との衝突を避け、各設問の4択と正答を一意に保つため、次を置換した。置換は元の選択肢位置を保ち、正答位置は写真の解答表と一致させている。

| 問 | 原本の語句 | 登録語句 | 理由 |
| --- | --- | --- | --- |
| 1 | `introspective` | `sporadic` | 既存1級セットとの語形衝突 |
| 1 | `impromptu` | `incongruous` | 既存1級セットとの語形衝突 |
| 4 | `surreptitiously` | `furtively` | 既存1級セットとの語形衝突 |
| 5 | `specters` | `undertones` | 既存1級セットとの語形衝突 |
| 6 | `elocution` | `enunciation` | 既存1級セットとの語形衝突 |
| 9 | `cajole` | `persuade` | 既存1級セットとの語形衝突 |
| 9 | `juxtapose` | `inhibit` | 既存1級セットとの語形衝突 |
| 9 | `redeem` | `absolve` | 既存1級セットとの語形衝突 |
| 11 | `debrief` | `deplete` | 既存1級セットとの語形衝突 |
| 13 | `debilitate` | `bewail` | 既存1級セットとの語形衝突 |
| 13 | `bemoan` | `disparage` | 既存1級セットとの語形衝突 |
| 14 | `intrepid` | `venturesome` | 既存1級セットとの語形衝突 |
| 15 | `lethal` | `amateurish` | 既存1級セットとの語形衝突 |
| 16 | `intangible` | `murky` | 既存1級セットとの語形衝突 |
| 17 | `extolling` | `lauding` | `extol` を含む既存原形との語形衝突 |
| 18 | `bigotry` | `discrimination` | 既存1級セットとの語形衝突 |
| 19 | `palliative` | `laudatory` | 既存1級セットとの語形衝突、および第4選択肢の一意性確保 |
| 20 | `percolate` | `seep` | 既存1級セットとの語形衝突 |
| 24 | `drum up` | `bring in` | 既存1級セットとの熟語衝突 |
| 24 | `lop off` | `trim down` | 既存1級セットとの熟語衝突 |
| 25 | `cashed in on` | `capitalized on` | 既存1級セットとの熟語衝突 |

Q19は当初 `acerbic` を置いたが、独立レビューで `derogatory` と意味が競合し得ると判定されたため、正答と反対方向の `laudatory` へ差し替えた。

## メタデータと音声

- すべての語句に意味、品詞、8語以上のオリジナル英文、和訳、語源説明を付与した。例文は教材本文の転載ではなく、学習用作例である。
- 84単語にはIPAを付与した。
- 16熟語には、共有不変化詞辞書を変更せず、語句内の連鎖で表す核心イメージを付与した。
- 表層MP3は `assets/audio/vocab/1/mock-8/` に100件生成済み（単語84件、熟語16件）。再生成時は、キーを保存せず環境変数へ設定し、`py -3 scripts/generate_tts_1.py --grade 1 --round mock-8` を実行する。
- 活用形12件（`grappled`, `dismantled`, `scuffed`, `reviled`, `diffused`, `assailed`, `maligned`, `shirked`, `ostracizing`, `bridling`, `lauding`, `pulverizing`）は、問題・進捗キーを変更せず `data/lemmas.json` の `flashcardLemmas` で原形表示へ解決し、原形MP3を `assets/audio/lemma/` に生成した。

## 検証

正答キーを伏せた設問文・4択だけをローカルの `qwen3:8b` に渡して独立レビューした。初回25問の判定は登録正答と一致したが、Q19の `acerbic` に正答競合の可能性が出たため、`laudatory` へ差し替えた。その後、Q13の正答位置を元の第3選択肢へ戻した変更も含め、Q13・Q19を再レビューし、最終登録値と一致し、曖昧さなしとなった。

```powershell
py -3 scripts/check_mock_8_data.py
py -3 scripts/check_q1_data.py
node scripts/check-core-image-data.cjs
node scripts/check-word-origin-data.cjs
```
