# 英検準2級公式セット整合レビュー

更新日: 2026-09-04

英検1級模試第6回の完成条件を、英検準2級の公式過去問3回分へ互換性のある範囲で適用した。準2級の公式形式、設問数、語句、`datasetId`、進捗キーは保持している。

## 差分と判断

| 監査軸 | 準2級公式3回分の現状 | 対応 |
| --- | --- | --- |
| 構造・件数 | 各回15問、40語・20熟語、計60語句 | 形式と件数を保持 |
| 設問文 | 4択、正答位置、設問番号を保持 | 変更なし |
| 設問文訳 | 3回分45問に既存訳あり | 空所記号を含まないことを確認し保持 |
| 語句カード | 意味・品詞・例文・例文訳・語源・IPAを保持。熟語には核心イメージあり | 既存項目を保持 |
| 正答フラグ | 各回60語句中15件 | 選択肢の語形も照合し、`is_answer`を再適用 |
| 例文 | 短い例文、または見出し語句の表層が現れないものがあった | 3回分145件を8語以上・見出し語句1回へ補正 |
| メタデータ | 回・級・設問区分・公式問題PDF・解答PDF・共通件数が不足 | 両JSONへ共通項目を追加 |
| 音声 | 各回60件の表層MP3が存在 | 既存音声を保持。新規生成は不要 |
| 語源辞書 | 公式3回の単語120件は共有`word_origins`へ収録済み | 現行の共有辞書を使用 |

複数語句を`idioms`へ移すなどの型変更は行っていない。既存利用者の進捗キーを別項目へ変えないためである。

準2級の自作模試第1回〜第4回は公式過去問の内容補正対象には含めず、既存の専用内容検査で確認した。2026-09-04に各回60件、計240件の表層MP3を生成し、共通検査でも音声を必須化した。

## 正本と適用

- `scripts/q1_eikenp2_metadata.py`: 準2級公式3回分の例文補正、設問・語句の整合確認、出典メタデータ、正答フラグの正本。
- `scripts/curate_eikenp2_data.py`: 既存の準2級公式生成JSONへ整合情報を再適用する入口。
- `scripts/check_eiken1_alignment.py`: 準2級公式過去問と自作模試を含む共通整合検査。全7セットで表層MP3を必須とする。
- `scripts/build_q1_official_data.py`: 非公開の公式PDFと、設問文・選択肢・正答位置を照合する。

## 独立レビュー（2026-09-04）

正答キーを渡さず、設問文と4択だけをローカルの`qwen3:8b`へ渡した。
2025-2、2025-3、2026-1の全45問で、モデルが一意とした選択肢と公式解答が一致した。

```powershell
py -3 scripts/curate_eikenp2_data.py
py -3 scripts/build_q1_official_data.py --grade pre2
py -3 scripts/review_official_questions.py --dataset-id eikenp2-2026-1
py -3 scripts/check_eiken1_alignment.py --dataset-id eikenp2-2025-2
py -3 scripts/check_eiken1_alignment.py --dataset-id eikenp2-2025-3
py -3 scripts/check_eiken1_alignment.py --dataset-id eikenp2-2026-1
py -3 scripts/check_p2_mock_data.py
```

例文とその和訳は学習用作例であり、公式問題・解答PDF本文をリポジトリへ追加していない。出典URLは英検公式の[準2級過去問ページ](https://www.eiken.or.jp/eiken/exam/grade_p2/)で確認した。
