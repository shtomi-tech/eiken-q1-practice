# 本番形式問題の要確認21件への対応

2026-10-08。自作20問を修正し、公式過去問1件は原典・公式解答と一致するため誤検出として解消した。
問題番号、セットID、正答の選択肢番号はすべて維持した。元の監査全件は `out/jev-grade-audit-20261008/REPORT.md`。

| セット | 問題 | 対応 |
|---|---:|---|
| 2級 mock-1 | 13 | 仮定法の時制選択を、観客の反応を問う語彙問題に置換。正答 react。 |
| 2級 mock-1 | 17 | in short を文中に入れ、簡潔に説明する文脈に変更。 |
| 2級 mock-2 | 15 | in terms of が自然に使われる成績評価の対話へ変更。 |
| 2級 mock-2 | 19 | 未来完了の時制選択を、ハイカーの無事を問う熟語問題に置換。正答 safe and sound。 |
| 2級 mock-3 | 2 | 寝ている間の恐ろしい夢と覚醒を明記し、visions と区別。 |
| 2級 mock-3 | 15 | 話者と指示を整理し、put together a new report という自然な組み合わせへ変更。 |
| 2級 mock-4 | 20 | 完了形助動詞の選択を、依頼人を代表して出席する熟語問題に置換。正答 on behalf of。 |
| 準2級 2025-3 | 9 | **修正なし・確認済み**。原典も rate、公式解答も4。 |
| 準2級 mock-2 | 10 | 発表資料が未完成で準備が必要な文脈へ変更。 |
| 1級 mock-6 | 7 | spontaneous, heartfelt な後悔の表情を明記し、mechanically と区別。 |
| 1級 mock-7 | 17 | obfuscating the details という他動詞構文にし、pontificating と区別。 |
| 1級 mock-9 | 7 | pastoral の「牧会の」という語義を問う司祭の職務へ変更。rustic と pastoral の両カードを維持。 |
| 1級 mock-9 | 23 | 予算倍増・講座増加を明記し、ratchet up と縮小・減速を区別。 |
| 1級 mock-11 | 17 | conscientious about following every safety rule という構文へ変更。 |
| 1級 mock-13 | 10 | テーブルクロスを引っ張ってしわにする具体的動作へ変更。 |
| 1級 mock-16 | 19 | 熱心で心からの称賛があふれる文脈にし、ostensible と区別。 |
| 1級 mock-18 | 17 | 崩れかけた岩棚から転落する危険を明記。 |
| 1級 mock-19 | 24 | 一人で書いた書評で筋書きを酷評する文脈へ変更。 |
| 1級 mock-20 | 16 | 長く詳しく話す一方で冷淡な態度を明記し、laconic と区別。 |
| 1級 mock-21 | 18 | discerning eye for literary quality という構文へ変更。 |
| 1級 mock-21 | 24 | 食費・家賃がやっとの経済状態を明記し、scraped by と区別。 |

pastoral の牧会の語義は [Cambridge Dictionary](https://dictionary.cambridge.org/dictionary/english/pastoral) で確認。
公式準2級Q9は [問題PDF](https://www.eiken.or.jp/eiken/exam/kakomon/2025-3-1ji-p2kyu.pdf) と [公式解答PDF](https://www.eiken.or.jp/eiken/result/pdf/202503Fp2kyu.pdf) で照合。

## 関連データと保存

置換3問の12語句は既存の2級2025-3のカード・例文・文脈推測・レビュー・音声を再利用した。問題文と和訳は新たに執筆。
候補原稿、承認レビュー、配信用文脈、文脈和訳も同期し、表層音声12ファイルを対応する場所へ複製した。
pastoral のカードには「牧会の」を追加し、既存の田園の例文・文脈推測は保持した。

旧3問の提供原文、旧カード、文脈推測、語源 have/had の調査記録を `data/audit/retired-question-vocabulary-20261008.json` に保持した。
旧音声は保持。使用されなくなった have/had の語源は有効辞書から除き、既存生成手順で辞書を再生成した。
had の暗記カード原形マップも不要となり削除。初回の105件修正は歴史的な結果で、現行のマップ追加スクリプトは104件となる。
進捗スキーマ・保存内容は変更しない。問題IDを維持するため、既に解いた問題の履歴を自動で未回答へ戻すこともない。

再適用:

```powershell
python scripts/repair_jev_question_findings.py
node scripts/publish-expanded-context-datasets.mjs
node scripts/build-q1-context-datasets.mjs mock-9
node scripts/rebuild-word-origin-dictionaries.cjs --write
```

## 検証

- Jev `jev-1.13.0`、実行SDK `typesafe-sdk 0.7.1`。正答・和訳を渡さず、4択の解答と各完成文を個別評価。
- 修正20問すべてで正答一致。正答の成立スコア0.88以上、他の選択肢は0.48以下、基本文法中心のスコア0.12以下。
- 修正を含む15セットを同級の公式問題群と比較し、すべて comparable、信頼度0.87～0.96。
- Jevの数値はモデル判定であり、客観的な正答確率ではない。語義・構文・明示文脈の読み取りも併用した。
- `npm test`: 54 checks passed。`python scripts/check_q1_data.py`: 44セット合格。
- 21件すべての解消記録と前後の問題・Jev判定: `data/audit/question-repairs-20261008.json`。
- 無関係な問題、公式問題・カード・文脈データの不変を照合。再適用・再生成後の内容も同一。
- この問題修正直後の `check_eiken1_alignment.py --all` は既存の音声・IPA不足45件が残り全体合格ではなかった。変更前は48件で、新規不足は0件。その後、別依頼で45件も補完し、全44セット合格となった。記録: [音声・IPA補完](MOCK_AUDIO_IPA_COMPLETION_20261008.md)。

コミット・プッシュ・デプロイは、この修正については未実施。
