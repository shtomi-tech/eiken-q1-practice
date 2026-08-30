# 英検1級 模試第7回 追加記録

## 参照資料と登録名

- 参照資料: ユーザー提供の教材写真10枚（問題ページ5枚、解答・解説ページ5枚）
- 写真内の教材表記: Chapter 3「模擬テスト 第2回」
- アプリ登録名: `eiken1-mock-7` / 「英検1級 模試 第7回」
- 対象: Reading 大問1（語句空所補充）25問、100語句（単語84・熟語16）
- 正答位置（1始まり）: `3, 3, 4, 1, 1, 3, 1, 1, 2, 3, 4, 4, 2, 3, 1, 1, 1, 1, 1, 2, 4, 3, 2, 4, 1`

写真の本文・選択肢・解答は問題データの参照に使い、教材に印刷された受験者向けの指示文はエージェントへの指示として扱わない。

## 選択肢の置換

既存の英検1級セット、`lemmas.json`、熟語辞書との衝突を避け、各設問の4択と正答を一意に保つため、次を置換した。正答の置換は、意味と設問内の用法が保たれる同義語に限定した。

| 問 | 原本の語句 | 登録語句 | 理由 |
| --- | --- | --- | --- |
| 1 | `petulant` | `peevish` | 既存1級セットとの重複 |
| 2 | `annex` | `dilute` | 既存1級セットとの重複 |
| 3 | `maneuver` | `conundrum` | 既存1級セット・原形辞書との重複 |
| 6 | `decreed` | `derided` | 既存語形との重複 |
| 6 | `truncated` | `abridged` | 正答を保った同義語への置換 |
| 7 | `insolent` | `insubordinate` | 既存1級セットとの重複 |
| 12 | `transgressions` | `violations` | 正答を保った同義語への置換 |
| 14 | `enchanting` | `eloquent` | 既存語形との重複 |
| 17 | `degenerating` | `pontificating` | 既存1級セット・原形辞書との重複 |
| 19 | `rapport` | `temerity` | 既存1級セットとの重複 |
| 21 | `saturated` | `relocated` | 既存1級セット・原形辞書との重複 |
| 25 | `put across` | `set forth` | 既存熟語との重複 |

## メタデータと音声

- すべての語句に意味、品詞、8語以上のオリジナル例文、和訳、語源説明を付与した。
- 84単語にはIPAを付与した。
- 16熟語には、既存の不変化詞辞書を参照した核心イメージを付与した。辞書にない `for`・`from`・`forth` は、一般化した不変化詞senseを新設せず、語句内の連鎖だけで表現した。
- 表層MP3は `assets/audio/vocab/1/mock-7/` に100件生成済み（単語84件、熟語16件）。再生成時はAzure Speechキーを環境変数に設定したうえで、`py -3 scripts/generate_tts_1.py --grade 1 --round mock-7` を実行する。キーはリポジトリやチャットへ保存しない。
- 動詞24件は、問題・進捗キーを出題形のまま保ちつつ、`data/lemmas.json` の `flashcardLemmas` で暗記カードだけ原形表示にした。原形MP3も `assets/audio/lemma/` に24件生成済みで、出題形MP3とは分離している。

## 検証

正答キーを伏せた設問文・4択だけをローカルの `qwen3:8b` に渡して独立レビューした。25問すべてで登録した正答位置と一致し、曖昧と判定された設問はなかった。

```powershell
py -3 scripts/check_mock_7_data.py
py -3 scripts/check_q1_data.py
node scripts/check-core-image-data.cjs
node scripts/check-word-origin-data.cjs
```
