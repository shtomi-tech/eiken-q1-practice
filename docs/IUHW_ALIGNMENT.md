# 国際医療福祉大学セット整合レビュー

更新日: 2026-09-04

英検1級模試第6回の完成条件を、国際医療福祉大学 総合型選抜 基礎試験セット2回分
（`iuhw-set-1` / `iuhw-set-2`）へ適用した。出題内容、設問数、語句、`datasetId`、
進捗キーは変更していない。これで `check_eiken1_alignment.py --all` の対象は
manifest上の全28セットになった。

## 差分と対応

| 監査軸 | 整合前の状態 | 対応 |
| --- | --- | --- |
| 共通整合検査 | `VOCAB_AUDIO_GRADE` に未登録で対象外 | `iuhw` を追加し、`--all` を28セットへ拡大 |
| 構造・件数 | set-1: 15問／58語＋熟語2、set-2: 15問／48語＋熟語12 | 形式と件数を保持 |
| 設問文・4択・正答位置 | 空所1件、4択、正答1件を満たす | 変更なし |
| 設問文訳 | 30問すべてに既存訳あり | 空所記号を含まないことを確認し保持 |
| 例文・例文訳 | 8語以上、見出し語句1回、骨格の重複なし | 変更なし |
| IPA | 106語すべてに欠落（両セット） | Datamuse経由で106件を付与（set-1: 58、set-2: 48） |
| 語源 | set-1は共有辞書で充足。set-2は48語中45語が未収録 | 45語を研究台帳へ追記（A型10・B型35） |
| 熟語の核心イメージ | 14件すべてにあり | 変更なし |
| 表層MP3 | set-1は60件あり。set-2は0件 | set-2に60件（単語48・熟語12）を生成 |
| 原形音声 | `flashcardLemmas` の対象語が両セットとも0件 | 追加生成は不要 |

## 語源の登録方針

複数形・分詞形の14語（`wages` `refunds` `contributions` `fines` `recipients`
`taxpayers` `employers` `volunteers` `qualified` `retired` `leading` `shrinking`
`aging` `neighboring`）は、`lemmas.json` へ新しい原形化を足さず**出題形をキー**として
登録した。`lemmas` に写像を足すと、原形辞書エントリ・`meaningReviewDigest`・
`build_lemma_entries.py` の承認済みハッシュ・原形MP3まで連鎖して必要になるためである。

語根・接辞の新規登録は行っていない。A型10語（dismiss, educate, retention,
distribution, admission, concentration, dental, contributions, recipients,
eligibility）は既存の語根 mit / duc / ten / trib / centr / dent / cap / lect だけを使う。
語根の表面形が綴りに現れない語（`expansion` の pans、`closure` の clos、
`refunds` の fund、`employers` の plic）は無理に分解せず、B型の由来一行にした。

出典は1語につき独立2ホスト。merriam-webster.com と collinsdictionary.com は
自動取得に対して403を返すため、etymonline.com と dictionary.com（一部
en.wiktionary.org）の組み合わせで確認した。`eligibility` のみ2つ目の出典に語源欄が
なく、`confidence` を `medium` として記録している。

## 独立レビュー（正答の一意性）

`iuhw-set-2` は `docs/IUHW_BASIC_EXAM_SET_2_REVIEW.md` に実施済みの記録がある。
今回は `iuhw-set-1` の15問について、正答キーを渡さず設問文と4択だけを
ローカルの別モデルへ渡した（2026-09-04）。

- `qwen3:8b`: 15問中13問で公式想定の選択肢を一意と判定。Q11とQ12で異なる判定。
- `deepseek-r1:8b`: Q11で異なる判定。Q2・Q5・Q7はAMBIGUOUS判定だが、
  挙げた候補にいずれも想定正答を含む。
- `qwen2.5vl:7b`: 出力形式を守らずテンプレートを反復したため、判定として採用しない。

不一致2件は、いずれもモデル側の誤りと判断した。教材データは変更していない。

- Q11「Mutual help ... ( ) family life in the past」: モデルは `functioned` を選ぶが、
  `function` は自動詞で `functioned family life` は成立しない。想定正答
  `strengthened` が唯一の他動詞用法として成り立つ。
- Q12「reduce income ( ) between rich and poor households」: モデルは `economic` を
  選ぶが、形容詞のため `income economic` は名詞句にならない。想定正答
  `disparities` のみが成立する。

set-1は原文を収録しない学習用自作文であり（`meta.source`）、set-2は原本を持たない
完全自作である。いずれも英検過去問を引用していない。

## 正本と適用

- `scripts/build_q1_iuhw_set_1_data.py` / `scripts/build_q1_iuhw_set_2_data.py`:
  問題・語彙データの正本。IPAは持たないため、生成後に発音補完を実行する。
- `scripts/enrich_flashcard_fields.py`: 発音（IPA）の補完。`TARGET_PATTERN` に
  `iuhw_set-\d+` を含む。
- `data/word_origin_research.json`: 語源のauthoring正本。表示用辞書は
  `rebuild-word-origin-dictionaries.cjs --write` で再生成する。
- `scripts/generate_tts_1.py`: `--grade iuhw` で表層MP3を生成する。
- `scripts/check_eiken1_alignment.py`: 医療福祉を含む共通整合検査。

```powershell
py -3 scripts/enrich_flashcard_fields.py --file data/vocab_iuhw_set-2.json
node scripts/rebuild-word-origin-dictionaries.cjs --check
py -3 scripts/generate_tts_1.py --grade iuhw --round set-2 --dry-run
py -3 scripts/check_eiken1_alignment.py --dataset-id iuhw-set-1
py -3 scripts/check_eiken1_alignment.py --dataset-id iuhw-set-2
py -3 scripts/check_eiken1_alignment.py --all
py -3 scripts/review_official_questions.py --dataset-id iuhw-set-1
```

## 検査結果（2026-09-04）

- `check_eiken1_alignment.py --all`: 28セットすべて「第6回基準の整合OK」。
- `check-word-origin-research.cjs` / `check-word-origin-data.cjs`: 台帳1,578件、
  origins 1,578件で成功。
- `npm test`: 成功。
- `assets/audio/vocab/iuhw/set-2/`: 単語48件・熟語12件、0バイトなし。

## Q15 を熟語のみの4択へ変更（2026-09-08、監査 Q12 対応）

`audit-question-set` の Q12（同一設問に単語と熟語が混在）指摘に対応し、`iuhw-set-1` Q15 を
語彙2＋熟語2の混在から、熟語のみの4択へ作り替えた。設問数・`datasetId`・進捗キーは不変。

- **Q15 新設問文**: 「A nationwide system for sending rural patients to city hospitals was
  finally ( ) by 2020, after years of delay.」正答 `in place`（位置2、正答位置分散 [4,4,4,3] は不変）。
- **語句構成**: 単語58＋熟語2 → 単語56＋熟語4。
  - 削除: `benefits` `proportion`（Q15 でしか使っていなかった単語）、`according to`（前置詞句のため
    述語補語の空所に他の熟語と同居できない）。
  - 追加: `at risk` `on hold` `in demand`（`in place` と同じ述語補語クラスの熟語）。核心イメージは
    term ステップ2件＋導出1件の3段チェーン（set-2 と同形式、particle 不使用）。
- **語源台帳**: `data/word_origin_research.json` の `entries` から `benefits` `proportion` を削除、
  `researchTarget.lemmas` から `benefits` を外し `count` 1255→1254。
  `node scripts/rebuild-word-origin-dictionaries.cjs --write` で `word_origins.json`（1578→1576）を再生成。
- **暗記カード表示原形**: `data/lemmas.json` の `flashcardDisplayLemmas` から `benefits: benefit` を削除
  （出題形が語彙データから消えたため）。
- **ビルド**: `scripts/build_q1_iuhw_set_1_data.py` に既存 IPA の引き継ぎを追加（IPA は
  `enrich_flashcard_fields.py` がネット経由で付けるため、再生成でオフラインでも 56 語の IPA を保持）。
- **未了**: `at risk` / `on hold` / `in demand` の表層MP3が未生成
  （`assets/audio/vocab/iuhw/set-1/idiom/`）。`AZURE_SPEECH_KEY` を設定して
  `py -3 scripts/generate_tts_1.py --grade iuhw --round set-1` を実行する。MP3 が無い間は
  ブラウザ内蔵音声で再生される。`check_eiken1_alignment.py --all` はこの3件で終了コード1。
- 検証: `check_q1_data.py` OK / `npm test` 成功 / `audit_question_set.py iuhw-set-1` は Q12 が消え、
  残りは V10（句動詞0件・IUHW の設計）と Q04（級相応）のみ。
