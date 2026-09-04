# 英検準1級全セット整合レビュー

更新日: 2026-09-04

英検1級模試第6回の完成条件を、準1級の公式過去問3回分へ互換性のある範囲で適用した。準1級の公式形式、設問数、語句、datasetId、進捗キーは保持している。

## 差分と判断

| 監査軸 | 1級側の基準 | 準1級の現状 | 判定 |
| --- | --- | --- | --- |
| 構造・件数 | 公式過去問は回ごとの公式形式を保持 | 18問 / 72語、各回の形式を保持 | 保持 |
| 設問文 | 4択・空所1か所・正答位置を維持 | 54問の設問文・選択肢・正答位置は変更なし | 保持 |
| 設問文訳 | 全問に自然な和訳を持つ | 3回分54問へ追加 | 合わせる |
| 語句メタデータ | `is_answer`、出典、件数、sectionを持つ | 216語へ正答フラグ、両JSONへ共通メタデータを追加 | 合わせる |
| 語句カード | 意味・品詞・例文・例文訳・語源・IPA | 既存216語を保持し、例文56件を8語以上・見出し語句1回へ補正 | 合わせる |
| 語源辞書 | 単語は共有`word_origins`を参照 | 準1級の単語168件を共有辞書へ収録済み | 合わせる |
| 熟語 | `idioms`に核心イメージを付ける | 48句動詞は`words`のまま、互換`coreImage`を付与 | 合わせる |
| 原形・音声 | 1級は表層MP3と必要な原形音声を配信 | 3回分216件の表層MP3を配信済み | 合わせる |
| 出典 | 公式PDF・解答PDFのURLを記録 | 2025-2、2025-3、2026-1の公式URLを両JSONへ記録 | 合わせる |

> **追記（2026-09-01）**: 上表の語源辞書の行は、当時の判断の記録である。その後、単語の語源表示は
> `data/word_origins.json` へ一本化し、語句データの `etymology` フィールドは全級で削除した。
> 準1級固有語も共有辞書に収録済みで、上表にある「不確かな9件の印」（`etymologyUncertain`）も
> 削除した。語源の確度は `data/word_origin_research.json` の `research.confidence` で管理する。

複数語句を`idioms`へ移さなかったのは、現在の実装で進捗キーが`type:surface`形式になっており、既存利用者の`word:`キーを`idiom:`へ変えると学習履歴が別項目になるためである。48件は`words`のまま`coreImage`を持ち、暗記カードでは語源より核心イメージを優先表示する。

## 正本と適用

- `scripts/q1_pre1_metadata.py`: 準1級3回分の設問文訳、例文補正、出典メタデータ、正答フラグの正本。
- `scripts/curate_pre1_data.py`: 既存の生成JSONへ再適用する入口。
- `scripts/build_q1_pre1_data.py`: 抽出後に上記メタデータを自動適用する。
- `scripts/check_eiken1_alignment.py`: `eiken1-*` と `eikenp1-*` の共通整合検査。準1級はMP3を省略時に許容し、`--require-audio`で必須化できる。
- `scripts/build_q1_official_data.py`: 非公開の公式PDFと、設問文・選択肢・正答位置を照合する。
- `scripts/check-pre1-core-image-compat.cjs`: 48句動詞が`word:`互換のまま核心イメージを持つことを検査する。

## 独立レビュー（2026-09-04）

正答キーを渡さず、設問文と4択だけをローカルの別モデルへ渡した。

- `qwen3:8b`: 2026-1、2025-3は全36問、2025-2はQ13を除く17問で公式解答と一致。
- 2025-2は`deepseek-r1:8b`で再確認し、Q13を含む18問すべてが公式解答と一致した。

最終的に54問すべてで、公式解答を支持する正答非表示レビュー結果を確認した。

## 検証

```powershell
py -3 scripts/check_eiken1_alignment.py --dataset-id eikenp1-2025-2
py -3 scripts/check_eiken1_alignment.py --dataset-id eikenp1-2025-3
py -3 scripts/check_eiken1_alignment.py --dataset-id eikenp1-2026-1
py -3 scripts/build_q1_official_data.py --grade pre1
py -3 scripts/review_official_questions.py --dataset-id eikenp1-2026-1
```

公式問題・解答PDFの所在は、英検公式の[準1級過去問ページ](https://www.eiken.or.jp/eiken/exam/grade_p1/)で確認した。設問文の和訳は学習用作例であり、PDF本文・PDF自体はリポジトリへ追加していない。
