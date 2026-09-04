# 英検2級全セット整合レビュー

更新日: 2026-09-04

英検1級模試第6回の完成条件を、英検2級の公式過去問3回分へ互換性のある範囲で適用した。英検2級の公式形式、設問数、語句、`datasetId`、進捗キーは保持している。

## 差分と判断

| 監査軸 | 2級の現状 | 対応 |
| --- | --- | --- |
| 構造・件数 | 各回17問、40語・28熟語、計68語句 | 形式と件数を保持 |
| 設問文 | 4択、正答位置、設問番号を保持 | 変更なし |
| 設問文訳 | 3回分51問に既存訳あり | 空所記号を含まないことを確認し保持 |
| 語句カード | 意味・品詞・例文・例文訳・語源・IPAを保持。熟語には核心イメージあり | 変更なし |
| 正答フラグ | 各回68語句中17件 | 選択肢の活用形も照合し、`is_answer`を再適用 |
| 例文 | 短い例文、または見出し語句が表層どおり現れないものがあった | 3回分78件を8語以上・見出し語句1回へ補正 |
| メタデータ | 回・級・設問区分・公式問題PDF・解答PDF・件数が不足 | 両JSONへ共通項目を追加 |
| 音声 | 各回68件の表層MP3が存在 | 既存音声を保持。新規生成は不要 |
| 語源辞書 | 単語120件は共有`word_origins`へ収録済み | 現行の共有辞書を使用 |

複数語句を`idioms`へ移すなどの型変更は行っていない。既存利用者の進捗キーを別項目へ変えないためである。

## 正本と適用

- `scripts/q1_eiken2_metadata.py`: 2級3回分の例文補正、設問・語句の整合確認、出典メタデータ、正答フラグの正本。
- `scripts/curate_eiken2_data.py`: 既存の2級生成JSONへ整合情報を再適用する入口。
- `scripts/check_eiken1_alignment.py`: 2級を含む共通整合検査。2級と1級は表層MP3を必須とする。
- `scripts/build_q1_official_data.py`: 非公開の公式PDFと、設問文・選択肢・正答位置を照合する。

## 独立レビュー（2026-09-04）

正答キーを渡さず、設問文と4択だけをローカルの別モデルへ渡した。

- `qwen3:8b`: 2026-1、2025-3は全34問、2025-2はQ1を除く16問で公式解答と一致。
- 2025-2 Q1は`deepseek-r1:8b`と`qwen2.5vl:7b`が公式解答の第2選択肢を一意と判定した。
- `deepseek-r1:8b`が2025-2 Q12で一度異なる判定を出したが、`qwen3:8b`と
  `qwen2.5vl:7b`は公式解答の第2選択肢を一意と判定した。

最終的に51問すべてで、公式解答を支持する正答非表示レビュー結果を確認した。

```powershell
py -3 scripts/curate_eiken2_data.py
py -3 scripts/build_q1_official_data.py --grade 2
py -3 scripts/review_official_questions.py --dataset-id eiken2-2026-1
py -3 scripts/check_eiken1_alignment.py --dataset-id eiken2-2025-2
py -3 scripts/check_eiken1_alignment.py --dataset-id eiken2-2025-3
py -3 scripts/check_eiken1_alignment.py --dataset-id eiken2-2026-1
```

例文とその和訳は学習用作例であり、公式問題・解答PDF本文をリポジトリへ追加していない。出典URLは英検公式の[2級過去問ページ](https://www.eiken.or.jp/eiken/exam/grade_2/index.html)で確認した。
