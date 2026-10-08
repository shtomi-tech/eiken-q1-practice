# 既存の音声・IPA不足45件の補完

2026-10-08。前の問題修正後に残っていた2級模試の不足45件をすべて補完した。

| 対象 | 音声 | IPA |
|---|---:|---:|
| 2級 mock-1 | 5 | 0 |
| 2級 mock-2 | 9 | 0 |
| 2級 mock-3 | 15 | 0 |
| 2級 mock-4 | 13 | 3 |
| 合計 | 42 | 3 |

音声4件は既存の同一表現を再利用。having spent / has spent / had spent は既存の idiom フォルダーから、put out は既存の原形音声からコピーした。既存ファイルは保持した。
残る38件は、前の暗記カード原形音声と同じ Microsoft Zira Desktop（en-US、Rate=-1）で合成し、libmp3lame 64kbpsでMP3化した。人間による辞書音声ではない。
生成先は共通検査とアプリが参照する `assets/audio/vocab/2/mock-N/` と `idiom/`。

IPAは mock-4 Q13 の3表現に追加した。

| 表現 | IPA |
|---|---|
| having spent | /ˈhævɪŋ spɛnt/ |
| has spent | /hæz spɛnt/ |
| had spent | /hæd spɛnt/ |

[Cambridge have](https://dictionary.cambridge.org/dictionary/english/have)、[Cambridge spent](https://dictionary.cambridge.org/us/dictionary/english/spent)、[Merriam-Webster have](https://www.merriam-webster.com/dictionary/have) を参照。
構成語の発音から作成した米語の広い表記で、has/had は強形を採用した。句全体を辞書から引用したものではなく、自然な文中では弱形も使われる。

## 検証と再実行

- `python scripts/check_eiken1_alignment.py --all`: 全44セット合格、不足0件。
- `npm test`: 54 checks passed。
- `python scripts/check_q1_data.py`: 全44セット合格。
- 42MP3すべてをデコードし、再生時間・音声信号の存在を検査。再利用4件はコピー元とSHA-256一致。
- 再インベントリ: 音声0件、IPA0件。既存の非空音声・IPAは上書きしない。
- 問題文、選択肢、正答、ID、進捗スキーマには変更なし。前の20問の修正を保持。
- 全件の人間による聴取確認は未実施。デコード検査は発音の独立した聴取検査とは区別する。

対象表現、コピー元、音声のハッシュ・再生時間、IPAの出典は `data/audit/mock-audio-ipa-completion-20261008.json`。
生成記録と検証ログは `out/mock-audio-ipa-20261008/`。

```powershell
python scripts/complete_mock_audio_ipa.py --apply
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/complete_mock_audio.ps1
python scripts/check_eiken1_alignment.py --all
npm test
```

FFmpegの場所は PowerShell スクリプトの `-Ffmpeg` で指定できる。合成には Windows の Microsoft Zira Desktop を使う。
再実行のインベントリはその時点の不足一覧になる。初回の42件の記録は上記audit JSONに保持する。

この補完記録の作成時点では未公開。公開状態は後続のGit履歴・リリース記録を参照。
