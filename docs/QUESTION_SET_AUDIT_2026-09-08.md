# 問題セット 形式・構造監査（全28セット）

実施日: 2026-09-08 ／ skill: `audit-question-set`

> **2026-09-08 追記**: 監査後にユーザー指示で A・B と一括整理を修正済み。結果は末尾
> 「対応結果」を参照。以下の本文は監査時点の記録。

## 結論

- **ERROR 4 / WARN 70 ／ 対象 28セット**（`py -3 scripts/audit_question_set.py`）。
- 前提チェックは通過: `py -3 scripts/check_q1_data.py` → `Q1 data: OK`、`npm test` → 全契約 OK。
- ERROR 4件のうち **新規に対応が要るのは 1件**（`iuhw-set-1` Q15 の単語／熟語混在）。
  残り 3件（`eiken1-mock-8` / `iuhw-set-1` / `iuhw-set-2` の句動詞0件）は文書化済みの意図的逸脱。
- WARN 70件のうち **判断が要るのは 4件**（下記「B」）。他は SKILL §4 の既知逸脱、
  級差（下位級の設問文が短い等）、公式過去問の内容そのものに由来し、形式監査としては対応不要。

## A. 対応が要る（未文書化）

| 検査ID 位置 | 内容 | 直す対象 |
| --- | --- | --- |
| **Q12 `iuhw-set-1` Q15**（ERROR） | 4択が `benefits / proportion`（名詞）＋ `according to / in place`（熟語）の混在。統語クラスが割れ、熟語2択を読まずに消去できる。 | [`scripts/build_q1_iuhw_set_1_data.py:223`](scripts/build_q1_iuhw_set_1_data.py) の Q15 `choices`／`items`。set-1 は熟語が全2件でこの1問に集約されている。名詞ダミー2件へ差し替えるか、熟語のみの設問を1問立てる（set-2 は Q13〜15 を熟語問題化して回避済み）。いずれも作例・正答一意性の再確認を伴う。 |

## B. 判断が要る WARN

| 検査ID 位置 | 内容 | 直す対象 / 判断材料 |
| --- | --- | --- |
| **X02 `eiken1-mock-1` Q5/clemency** | 例文「The prisoner appealed to the governor for clemency.」が公式セット `eiken1-2026-1` Q17（正答 `clemency`）と完全一致。自作模試が公式の作例を流用している。 | [`scripts/build_q1_mock_1_data.py`](scripts/build_q1_mock_1_data.py) の `clemency` 例文を書き直す。 |
| **Q14 `eiken1-mock-5`**（正答位置の偏り） | 選択肢2が 2/25問（下限 10%＝2.5問を下回る）。自作セットなので調整可能。 | [`scripts/build_q1_mock_5_data.py`](scripts/build_q1_mock_5_data.py) の `choices` 並びと `answerIndex` を同時に直し、語彙JSONを追随。 |
| **X03 `eikenp2-2025-3` Q13/make a start** | 例文訳の骨格が `eikenp2-2026-1` Q15（`make a start on`）と同一。 | 軽微。`scripts/build_pre1_data.py` 系（eikenp2 ビルダー）の該当例文訳を差し替え。表示上の実害は小さい。 |
| **V02 collocation フィールド ×7** | `eiken2-2025-2/3` `eiken2-2026-1` `eikenp2-2025-2/3` `eikenp2-2026-1`（各60〜68件）と `eikenp1-2026-1`（3件）に、アプリが参照しない `collocation` が残る。基準セットには無い。 | 一括除去候補（低優先）。各級のビルドスクリプト（`curate_eiken2_data.py` / `curate_eikenp2_data.py` / `build_pre1_data.py` 系）で出力しないようにして再生成。 |
| **S09 meta 不一致 ×6** | `eiken2` `eikenp2` の公式3セットずつで `questions.meta` と `vocab.meta` の `note` 文言・`source_pdf` キーの有無が食い違う。`grade/round/source/counts` は一致。 | 整形のみ。各ビルドスクリプトの `META` を片側へそろえて再生成。 |

## C. 文書化済みの意図的逸脱 — SKILL §4 への追記を推奨

`audit-question-set` の SKILL.md §4「既知の逸脱」に以下が未収載。次回監査でノイズになるため追記したい。

- **`iuhw-set-1` / `iuhw-set-2`: 句動詞0件（V10 ERROR）** — IUHW セットは particle 機構を使わず、
  熟語は term ステップ2件＋導出1件の3段チェーンで統一する設計。
  根拠: [`docs/IUHW_ALIGNMENT.md`](docs/IUHW_ALIGNMENT.md)、[`docs/IUHW_BASIC_EXAM_SET_2_REVIEW.md`](docs/IUHW_BASIC_EXAM_SET_2_REVIEW.md)。
- **`iuhw-set-2`: 熟語設問数3（S04、標準1）** — ユーザー依頼で熟語を2→12件へ増やし Q13〜15 を熟語問題化。
  根拠: [`docs/IUHW_BASIC_EXAM_SET_2_REVIEW.md`](docs/IUHW_BASIC_EXAM_SET_2_REVIEW.md)。

（既収載で今回も再現: `eiken1-mock-8` 句動詞0件、`eiken1-mock-6/7/8/9` の `(   )` 表記、
`eiken1-mock-9` の設問文10問が `mock-8` と同一、5級・iuhw の設問文が基準レンジより短い。）

## D. 対応不要（級差・公式過去問の内容由来）

- **Q13 選択肢の品詞3種類以上 ×16** — 内訳 `eiken1-2025-2`×4 / `eiken1-2025-3`×4 / `eiken1-2026-1`×5 は
  基準セット自身（＝実際の英検過去問）。`eiken2-2025-3`×1 / `eikenp2-2025-3`×1 / `iuhw-set-1` Q14×1 も
  公式または級相応。公式過去問は選択肢を改変できないため対応不可。自作分のみ誤答の品詞をそろえれば軽減。
- **Q04 設問文が基準レンジ（13〜45語）より短い ×14** — `eiken5-2026-1`×8（公式・5級）、`iuhw-set-1`×4 / `iuhw-set-2`×2。
  SKILL §4 の通り級相応。
- **Q14 正答位置の偏り（公式分）** — `eiken1-2025-3`（選択肢4が10/22）、`eiken2-2025-2`（選択肢1が0/17）、
  `eiken2-2025-3`（選択肢2が7/17・選択肢4が1/17）、`eiken5-2026-1`（選択肢4が7/15）。本番の解答表に一致させており改変不可。
- **V10 句動詞比率 < 25%（WARN、下位級公式）** — `eiken2-2025-3`（3/28）、`eikenp2-2025-2`（1/20）、
  `eikenp2-2025-3`（4/20）。語彙が級相応で、句動詞を無理に増やすと難易度が崩れる。
- **X01 `eiken1-mock-9` ×10** — SKILL §4 既知（`mock-8` の設問文を流用し選択肢だけ差し替えたセット）。

## 指摘なしのセット（9件）

`eiken1-mock-2` `eiken1-mock-3` `eiken1-mock-4` `eikenp1-2025-2` `eikenp1-2025-3`
`eikenp2-mock-1` `eikenp2-mock-2` `eikenp2-mock-3` `eikenp2-mock-4`

## 再現コマンド

```powershell
py -3 scripts/check_q1_data.py
npm test
py -3 scripts/audit_question_set.py --baseline
py -3 scripts/audit_question_set.py            # 全28セット
py -3 scripts/audit_question_set.py iuhw-set-1 # 個別
```

出力が文字化けする場合は `$env:PYTHONUTF8=1`（bash なら `PYTHONUTF8=1`）を付ける。

---

## 対応結果（2026-09-08）

監査後、ユーザー指示で A・B と一括整理を実施。**監査は ERROR 4 / WARN 70 → ERROR 3 / WARN 53**。
残る ERROR 3 と WARN 53 はすべて「文書化済みの意図的逸脱」「級差」「公式過去問の改変不可な内容」で、
形式監査としての対応は完了。`check_q1_data.py` OK / `npm test` 成功。

### A（ERROR）

| 指摘 | 対応 | 変更ファイル |
| --- | --- | --- |
| Q12 `iuhw-set-1` Q15 | Q15 を熟語のみの4択へ作り替え（正答 `in place`）。`benefits`/`proportion`/`according to` を外し `at risk`/`on hold`/`in demand` を追加。核心イメージ3件を新規作成。 | `scripts/build_q1_iuhw_set_1_data.py`、`data/word_origin_research.json`（`benefits`/`proportion` entry 削除、`researchTarget` 1255→1254）、`data/word_origins.json` ほか（`rebuild-word-origin-dictionaries.cjs --write` で再生成）、`data/lemmas.json`（`flashcardDisplayLemmas` から `benefits` 削除）。詳細は `docs/IUHW_ALIGNMENT.md`。 |

### B（WARN）

| 指摘 | 対応 | 変更ファイル |
| --- | --- | --- |
| X02 `eiken1-mock-1` Q5/clemency | 例文を公式 `eiken1-2026-1` と重複しない文へ差し替え。 | `scripts/build_q1_mock_1_data.py`（+ 再生成でオフラインでも IPA を保持する引き継ぎを追加） |
| Q14 `eiken1-mock-5` | 正答位置を [8,2,8,7] → [6,5,7,7] へ再配分（Q6/Q12/Q18 の選択肢並びと `answerIndex` を入れ替え）。 | `scripts/build_q1_mock_5_data.py`（同上の IPA 引き継ぎ追加） |
| X03 `eikenp2-2025-3` Q13/make a start | 例文・訳を差し替え、`eikenp2-2026-1` と骨格が一致しないようにした。 | `scripts/q1_eikenp2_metadata.py`（`EXAMPLE_OVERRIDES`） |
| V02 collocation ×7 | `eiken2`×3・`eikenp2`×3・`eikenp1-2026-1` から `collocation` フィールドを除去。 | `scripts/q1_eiken2_metadata.py` / `scripts/q1_eikenp2_metadata.py` / `scripts/q1_pre1_metadata.py`（`apply_round` で `pop`）、`scripts/build_q1_pre1_data.py`（`VOCAB_FIELDS` から削除） |
| S09 meta 不一致 ×6 | `metadata()` を正準化し `questions.meta` と `vocab.meta` を同一に（`exam` は落とし `note` は正準の1本に統一）。 | `scripts/q1_eiken2_metadata.py` / `scripts/q1_eikenp2_metadata.py` |

### C（SKILL §4 追記）

`.claude/skills/audit-question-set/SKILL.md` §4 に `iuhw-set-1/2` の V10（句動詞0件・IUHW の設計）と
`iuhw-set-2` の S04（熟語設問3・依頼で増やした）を既知逸脱として追記。

### 未了

`iuhw-set-1` の新熟語3件（`at risk` / `on hold` / `in demand`）の表層MP3が未生成。
`AZURE_SPEECH_KEY` を設定して `py -3 scripts/generate_tts_1.py --grade iuhw --round set-1` を実行する。
MP3 が無い間はブラウザ内蔵音声で再生される。`check_eiken1_alignment.py --all` はこの3件で終了コード1。

### D（対応不要のまま残る主なもの）

- Q13 品詞3種類（`eiken1` 公式・`eiken2-2025-3`・`eikenp2-2025-3`・`iuhw-set-1` Q14）＝実過去問／級相応、選択肢改変不可。
- Q14 偏り（`eiken1-2025-3`・`eiken2-2025-2/3`・`eiken5-2026-1`）＝本番の解答表に一致。
- S07 `(   )`（`eiken1-mock-6/7/8/9`）・X01（`eiken1-mock-9`）＝SKILL §4 既知。
- Q04 短い設問文（`eiken5-2026-1`・`iuhw`）＝級相応。
- V10 句動詞比率<25%（`eiken2-2025-3`・`eikenp2-2025-2/3`）＝下位級で語彙が級相応。
