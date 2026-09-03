# 国際医療福祉大学 基礎試験セット第2回（iuhw-set-2）追加記録

## 登録名と対象

- アプリ登録名: `iuhw-set-2` / 「国際医療福祉大学 総合型選抜 基礎試験 第2回」
- shortLabel: `医療福祉`（第1回と同じ。ホームの「医療福祉・基礎試験」グループに並ぶ）
- 対象: 基礎試験 英語（選択肢文の語彙）15問 / 60語句（単語48・熟語12）
- 正答位置（1始まり）: `2, 3, 1, 4, 2, 3, 1, 4, 2, 3, 1, 4, 2, 3, 1`（各位置3〜4件）
- 正本: `scripts/build_q1_iuhw_set_2_data.py`。`data/questions_iuhw_set-2.json` /
  `data/vocab_iuhw_set-2.json` は生成物。

## 出典

**原本を持たない完全自作。** `meta.source` に
「AI生成（英検過去問の引用なし）・人手校閲。第1回の題材傾向に沿った学習用自作文」と明記した。
第1回（`iuhw-set-1`）の選択肢文由来の語彙傾向を踏まえ、題材と難易度をそろえた自作文で構成する。

## 語彙選定（第1回の傾向を踏襲）

第1回の60語句を4つの題材の柱に分けて分析し、同じ柱・同じ品詞バランスで、第1回と
1語も重複しない「隣接語」を選んだ。

| 柱 | 第1回の例 | 第2回で採った隣接語 |
| --- | --- | --- |
| 医療人材のグローバル調達 | immigration, resources, professionals, skilled, visas, preferential | shortage, surplus, recruit, sponsor, dismiss, educate, qualified, retired, temporary, junior, overseas, private |
| 医師の働き方・地域偏在 | doctors, promote, positions, treatment, male/female | distribution, retention, admission, shift, burden, allowance, leave, quota, concentration, expansion, decline, turnover, rural, urban |
| 社会保障財政・格差・高齢化 | security, benefits, expenditure, expenses, fiscal, disparities, income, growth | aging, shrinking, neighboring, leading, elderly, chronic, mental, dental, contributions, wages, refunds, fines, recipients, taxpayers, employers, volunteers, coverage, eligibility, enrollment, premium |
| 図表・統計・談話標識 | ratio, percentage, proportion, average, according to, in place | in terms of, regardless of, prior to, in favor of, as a result, for instance, in particular, by contrast, account for, lead to, refer to, cope with |

- 品詞構成: 名詞34 / 形容詞16 / 動詞8 / 熟語12（第1回は名詞32 / 形容詞17 / 動詞7 / 副詞1 /
  前置詞1 / 熟語2）。
- 熟語は第1回の2件から12件へ増やした（ユーザー依頼）。passage形式で問われやすい
  観点・談話標識・数量因果の熟語に絞り、Q13〜Q15の3問を熟語問題にした。
- 難易度は第1回と同等（共通テスト＋社会科学アカデミック語）。易しい語（`private` `leave`
  `leading` `dental` など）は正答にせずダミー専用にした。

## 重複制約の確認（`references/CHECKS.md` の選定プレチェック）

60語句すべてが次のいずれとも衝突しないことを、`check_q1_data.surface_variants` を使って
選定時に確認した。

| 対象 | 結果 |
| --- | --- |
| iuhw既存60語（`data/vocab_iuhw_set-1.json`、語形の揺れ含む） | 衝突なし |
| 全配信セットの熟語 `phrase`（`data/vocab_*.json` 全件） | 衝突なし。`due to` `on the whole` `carry out` `consist of` `according to` `in place` は既存にあり除外 |
| `data/lemmas.json` の canonical `lemmas` と `flashcardLemmas` の全キー・全原形値 | 衝突なし。`relocate` `deploy` `enroll` `dispatch` `transfer` は衝突のため不採用 |
| セット内部の surface variant 重複・各設問の意味重複 | なし |

canonical `lemmas` に触れないため、`build_lemma_entries.py` の
`REVIEWED_MEANING_DIGEST` は不変（`npm test` の `check-lemma-headword.cjs` で確認）。

## 独立レビュー（正答の一意性）

生成に使っていない別モデル（`codex exec`、GPT-5系）に、正答を伏せた設問文と4択だけを渡し、
各設問で成立する選択肢を挙げさせた。3周実施。

| 周 | 対象 | 曖昧と判定された設問 |
| --- | --- | --- |
| 1 | 全15問 | Q2, Q5, Q8, Q9, Q13, Q14（各2択以上が成立） |
| 2 | 上記6問（文脈を追加して修正） | Q8, Q9, Q14（弱い競合が残存） |
| 3 | 上記3問（さらに文脈を限定） | なし |

修正は語の差し替えではなく、設問文に文脈を足して正答を一意にした（語彙・正答・選択肢は不変）。

| 設問 | 競合 | 追加した文脈 |
| --- | --- | --- |
| Q2 | recruit / sponsor | 「面接してその場で（interview and … on the spot）」で採用行為に限定 |
| Q5 | distribution / retention / shift | 「医師がどこで働くことを選ぶか（where doctors choose to work）」で地理的分布に限定 |
| Q8 | aging / shrinking | 「住民の総数が減っていない地域でも（even where the total number of residents is not falling）」で人口減少と分離 |
| Q9 | elderly / chronic / dental | 見出し名詞を patients → people にし、非年齢の形容詞（dental/mental/chronic + people）を非文にした |
| Q13 | In terms of / Regardless of | 「この一つの指標では（on this one measure）」で比較軸を空所に固定 |
| Q14 | as a result / for instance | 「その谷で最後の産科病棟が来春閉鎖される」という単一の帰結にし、例示の読みを排除 |

## 機械チェック

```powershell
py -3 scripts/build_q1_iuhw_set_2_data.py
py -3 scripts/check_q1_data.py
npm test
```

- `build`: 品詞混在 0/15、正答位置分散 [4, 4, 4, 3]、15問 / 60語句（単語48・熟語12）。
- `check_q1_data.py`: `iuhw-set-2: 15 questions / 60 words OK` / `Q1 data: OK`（WARN なし）。
  `EXPECTED_IDS` に `iuhw-set-2` を追加。
- `npm test`: 全チェック通過。`core image progress: vocab_iuhw_set-2.json: 12 idioms / 12 coreImage`、
  `lemma headword contract: OK`、`grade scope contract: OK`。

## メタデータ・音声・語源

- 全60語句に意味・品詞・8語以上のオリジナル例文・和訳を付与。
- 熟語12件に核心イメージ（`chain`）を付与。第1回と同じく particle 機構は使わず、
  term ステップ2件＋導出結果1件の3段チェーンに統一（Q15の account for / lead to /
  refer to / cope with も同形式）。
- 語源（`data/word_origins.json`）は第1回同様に未登録。IPA も第1回同様に未付与
  （`enrich_flashcard_fields.py` の `TARGET_PATTERN` は `vocab_iuhw_*` を対象外にしており、
  第1回にも IPA はない）。暗記カードは見出し語・品詞・意味・例文・例文訳を表示する。
- 表層MP3は未生成。生成する場合は Azure Speech キーを環境変数に設定して
  `py -3 scripts/generate_tts_1.py --grade iuhw --round set-2`。MP3 が無い間はブラウザ内蔵音声で
  再生される。キーはリポジトリ・ログ・チャットへ出さない。

## 組み込み

- `data/manifest.json` の `q1` に `iuhw-set-2` を追加（`iuhw-set-1` の直後）。
- `scripts/check_q1_data.py` の `EXPECTED_IDS` に `iuhw-set-2` を追加。
- `README.md`: 冒頭のセット数（27→28）、間隔復習の表（医療福祉 30問 / 120語句）、
  対象データ節、スクリプト節を更新。
- `static/mode-q1.js` と `index.html` は変更不要（`iuhw` 級は第1回で対応済み。データJSONは新規URL、
  manifest は `no-store`）。`check-grade-scope.cjs` も固定 fixture で `iuhw-set-1` のみを使うため変更不要。

## 未確定・想定

- 出題年度が不明なため ID は `set-2`。年度が判明したら `iuhw-2026-2` 等へ変える必要があり、
  その時点の進捗（`eiken_q1_progress_iuhw-set-2`）は引き継がれない。**変えるなら早いほうがよい。**
- ブラウザ確認は、ホームに第2回カードが並ぶこと・データJSONが HTTP 200 で配信され設問数と
  語句数が一致することまで確認した。スキーマは第1回と同一。
