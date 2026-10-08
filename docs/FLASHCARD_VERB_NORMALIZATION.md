# 暗記カードの動詞原形化（2026-10-08）

Jev分類で「原形以外」に残った105カードについて、英語の形を確認し、
`data/lemmas.json` の `flashcardDisplayLemmas` に105件の対応を追加した。
要確認に分けた610カードは今回の対象外。

対応の正本は `scripts/normalize_flashcard_verbs.py` の `MAPPING`。
`python scripts/normalize_flashcard_verbs.py` は差分確認、`--apply` は適用。
同じ対応を再適用しても変更は発生しない。既存の異なる対応は上書きせず停止する。

- 単語・動詞句の活用を原形へ戻す（例: `committing → commit`、`brought up → bring up`）。
- `made by → be made by` は受動の意味を保つ。
- `has spent` / `had spent → spend` は見出しから完了時制を除く。
- `you required → require` は主語と過去時制を除く。
- 出題形、問題・選択肢、意味、例文、既存辞書エントリ、進捗キーは保持する。
- 表示見出しと辞書見出しが異なる場合、表示見出しの辞書IPAだけを使う。
  IPAがない場合は発音記号を省略し、出題形のIPAを原形に流用しない。

## 音声

表示原形に必要な101件のMP3を追加。9件は同じ原形の既存語彙MP3をコピーし、
92件はWindowsの `Microsoft Zira Desktop`（en-US、Rate=-1）でローカル生成した。
WAVを既存FFmpegのlibmp3lameで64kbps MP3へ変換した。
既存MP3は上書きしていない。Azure音声とは話者・音質が異なる。

今回のローカル生成対象と再利用元の記録は
`out/jev-verb-form-20261008/local-audio-generated.json` と `audio-reuse.json` にある。
この作業記録は公開対象外。

## 検証

- 105件の対応、語彙データのハッシュ、既存辞書の保持、適用の再実行を確認。
- 追加MP3をFFmpegでデコードして確認。
- `npm test` の51チェックを実行。
- ローカルHTTPの実ブラウザで原形見出し、出題形、音声、再開、
  キーボード移動、320px表示、コンソールを確認。

commit / push / deploy はこの変更に含めない。
