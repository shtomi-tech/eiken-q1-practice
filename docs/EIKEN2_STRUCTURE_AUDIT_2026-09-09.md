# 英検2級 問題セット形式・構造監査

実施日: 2026-09-09
Worker: `mal`
使用 Skill: `audit-question-set`（監査のみ。データ・生成スクリプト・manifest は変更していない）

## 結論

**ERROR 14 / WARN 15、対象7セット。** `py -3 scripts/audit_question_set.py --grade eiken2` の終了コードは `1`。

manifest の `q1` にある `eiken2-*` は、公式3回（2026-1、2025-3、2025-2）と模試4回（mock-1〜4）の計7セットだった。`eiken2-2026-1` は指摘なし。ERROR は自作模試4セットにのみ発生し、公式セットのWARNは正答位置・品詞・句動詞比率に関するものなので、公式の出題順を保つ限り機械的な修正対象ではない。

監査の実行時点で worktree は既に dirty だった。既存差分は保持し、今回の書き込みはこのレポート1ファイルだけに限定した。

## 対象と基準

`--baseline` の実測基準は `eiken1-*` **24セット**（skill の説明にある12セットとは現行manifestの実数が異なる）で、次の値だった。

| 基準 | 実測値 |
| --- | ---: |
| 設問数 | 25 |
| 熟語設問数 | 4 |
| 空所表記 | `(   )` |
| 設問文の語数 | 13〜45語 |
| 例文の語数 | 8〜15語 |

対象セットの実データ形状は次のとおり。mock系のS04標準は、同じ `eiken2-mock-*` の多数派である「熟語設問6問」。

| datasetId | 設問 | 語彙 | 単語 / 熟語 | 熟語設問 | 正答位置（選択肢1〜4） |
| --- | ---: | ---: | ---: | ---: | --- |
| `eiken2-2026-1` | 17 | 68 | 40 / 28 | 7 | 5 / 4 / 4 / 4 |
| `eiken2-2025-3` | 17 | 68 | 40 / 28 | 7 | 3 / 7 / 6 / 1 |
| `eiken2-2025-2` | 17 | 68 | 40 / 28 | 7 | 0 / 5 / 6 / 6 |
| `eiken2-mock-1` | 20 | 80 | 54 / 26 | 7 | 5 / 6 / 4 / 5 |
| `eiken2-mock-2` | 20 | 80 | 57 / 23 | 6 | 3 / 7 / 5 / 5 |
| `eiken2-mock-3` | 20 | 80 | 63 / 17 | 6 | 6 / 8 / 2 / 4 |
| `eiken2-mock-4` | 20 | 80 | 57 / 23 | 6 | 4 / 4 / 6 / 6 |

## Findings

行番号は、修正時に参照する正本スクリプトの現行位置。JSON生成物の直接編集は行わない。

### `eiken2-2025-2`

| ID / 位置 | 深刻度 | 根拠 | 正本スクリプト |
| --- | --- | --- | --- |
| Q14 / `set` | WARN | 正答位置が選択肢1の `0/17`。公式解答の位置を保持した結果であり、他の契約違反はない。 | `scripts/build_q1_official_data.py:94-108,125-134`、`scripts/q1_eiken2_metadata.py:420-439` |

### `eiken2-2025-3`

| ID / 位置 | 深刻度 | 根拠 | 正本スクリプト |
| --- | --- | --- | --- |
| Q13 / `Q13` | WARN | 4択のPOSが3種類（`副詞句`、`形容詞句`、`形容詞句・名詞句`）。 | `scripts/build_q1_official_data.py:94-108`、`scripts/q1_eiken2_metadata.py:451-474` |
| Q14 / `set` | WARN | 正答位置が選択肢2の `7/17`。公式解答の位置を保持した結果。 | `scripts/build_q1_official_data.py:94-108,125-134`、`scripts/q1_eiken2_metadata.py:420-439` |
| Q14 / `set` | WARN | 正答位置が選択肢4の `1/17`。公式解答の位置を保持した結果。 | `scripts/build_q1_official_data.py:94-108,125-134`、`scripts/q1_eiken2_metadata.py:420-439` |
| V10 / `set` | WARN | 句動詞が `3/28`（下限25%）。公式語彙の構成による。 | `scripts/q1_eiken2_metadata.py:424-435`、`scripts/build_core_image_stub.py:97-119` |

### `eiken2-mock-1`

| ID / 位置 | 深刻度 | 根拠 | 正本スクリプト |
| --- | --- | --- | --- |
| Q12 / `Q18` | ERROR | Q18の選択肢 `have / had / will have / would have` が、空白を含む後2件だけ熟語として生成され、単語と熟語が混在。 | `scripts/build_q1_eiken2_mock_1_data.py:118-121,282-299` |
| S05 / `set` | ERROR | 熟語設問列が `Q12,Q13,Q15,Q16,Q17,Q18,Q20` で、末尾連続でない。 | `scripts/build_q1_eiken2_mock_1_data.py:14-135,282-299` |
| Q13 / `Q19` | WARN | POSが3種類（`前置詞`、`副詞`、`接続詞`）。 | `scripts/build_q1_eiken2_mock_1_data.py:124-125,211-214` |
| Q13 / `Q20` | WARN | POSが3種類（`形容詞句`、`数量表現`、`表現`）。 | `scripts/build_q1_eiken2_mock_1_data.py:130-131,215-218` |
| S04 / `set` | WARN | 熟語設問が7問で、mock系多数派の標準6問と異なる。 | `scripts/build_q1_eiken2_mock_1_data.py:282-299` |
| V10 / `set` | WARN | 句動詞が `1/26`。`kept up`（`particle: up`）以外の熟語にparticleがない。 | `scripts/build_q1_eiken2_mock_1_data.py:222-248,293-297` |

### `eiken2-mock-2`

| ID / 位置 | 深刻度 | 根拠 | 正本スクリプト |
| --- | --- | --- | --- |
| Q12 / `Q15` | ERROR | Q15の選択肢 `in return for / with respect to / as a consequence of / despite` は、最後の `despite` だけ単語として生成され、単語と熟語が混在。 | `scripts/build_q1_eiken2_mock_2_data.py:100-103,279-296` |
| S05 / `set` | ERROR | 熟語設問列が `Q11,Q12,Q13,Q15,Q18,Q19` で、末尾連続でない。 | `scripts/build_q1_eiken2_mock_2_data.py:14-135,279-296` |
| V10 / `set` | WARN | 句動詞が `1/23`。`turning off`（`particle: off`）だけにparticleがある。 | `scripts/build_q1_eiken2_mock_2_data.py:222-245,290-294` |

### `eiken2-mock-3`

| ID / 位置 | 深刻度 | 根拠 | 正本スクリプト |
| --- | --- | --- | --- |
| Q12 / `Q17` | ERROR | Q17の `from / near / under / in memory of` は、最後の1件だけ熟語として生成され、単語と熟語が混在。 | `scripts/build_q1_eiken2_mock_3_data.py:112-115,273-291` |
| Q12 / `Q18` | ERROR | Q18の `had become / to become / became / become` は、空白を含む前2件だけ熟語として生成され、単語と熟語が混在。 | `scripts/build_q1_eiken2_mock_3_data.py:118-121,273-291` |
| Q12 / `Q20` | ERROR | Q20の `the time / once / ahead / the next` は、空白を含む前後2件だけ熟語として生成され、単語と熟語が混在。 | `scripts/build_q1_eiken2_mock_3_data.py:130-133,273-291` |
| S05 / `set` | ERROR | 熟語設問列が `Q13,Q14,Q15,Q17,Q18,Q20` で、末尾連続でない。 | `scripts/build_q1_eiken2_mock_3_data.py:14-135,273-291` |
| V08 / `Q20/the time` | ERROR | `coreImage.chain` が2段で、3段以上の基準を満たさない。 | `scripts/build_q1_eiken2_mock_3_data.py:238,273-288` |
| V08 / `Q20/the next` | ERROR | `coreImage.chain` が2段で、3段以上の基準を満たさない。 | `scripts/build_q1_eiken2_mock_3_data.py:239,273-288` |
| V10 / `set` | ERROR | 句動詞（`coreImage.particle`付き）が `0/17`。 | `scripts/build_q1_eiken2_mock_3_data.py:222-239,284-288` |
| Q13 / `Q18` | WARN | POSが3種類（`不定詞句`、`助動詞句`、`動詞`）。 | `scripts/build_q1_eiken2_mock_3_data.py:118-119,207-210` |
| Q13 / `Q20` | WARN | POSが4種類（`副詞`、`名詞句`、`形容詞句`、`接続詞`）。 | `scripts/build_q1_eiken2_mock_3_data.py:130-131,215-218` |

### `eiken2-mock-4`

| ID / 位置 | 深刻度 | 根拠 | 正本スクリプト |
| --- | --- | --- | --- |
| Q12 / `Q18` | ERROR | Q18の `spent / having spent / has spent / had spent` は、先頭1件だけ単語として生成され、単語と熟語が混在。 | `scripts/build_q1_eiken2_mock_4_data.py:118-121,279-297` |
| S05 / `set` | ERROR | 熟語設問列が `Q11,Q12,Q13,Q16,Q18,Q20` で、末尾連続でない。 | `scripts/build_q1_eiken2_mock_4_data.py:14-135,279-297` |
| V10 / `set` | ERROR | 句動詞（`coreImage.particle`付き）が `0/23`。 | `scripts/build_q1_eiken2_mock_4_data.py:222-245,290-294` |
| Q04 / `Q13` | WARN | 設問文が12語で、eiken1基準13〜45語を1語下回る。 | `scripts/build_q1_eiken2_mock_4_data.py:88-91`（基準定数: `scripts/audit_question_set.py:30-38`） |
| Q13 / `Q18` | WARN | POSが3種類（`助動詞句`、`動詞`、`動詞句`）。 | `scripts/build_q1_eiken2_mock_4_data.py:118-119,207-210` |
| Q13 / `Q19` | WARN | POSが3種類（`代名詞`、`副詞`、`接続詞`）。 | `scripts/build_q1_eiken2_mock_4_data.py:124-125,211-214` |

## 目視確認（読み取り専用）

- 対象7セットの全131設問を一覧確認した。空所は全件 `(   )` で、各設問1か所。公式3セットの熟語設問は `Q11〜Q17` に連続している。
- mock系の熟語設問列は、mock-1 `12,13,15,16,17,18,20`、mock-2 `11,12,13,15,18,19`、mock-3 `13,14,15,17,18,20`、mock-4 `11,12,13,16,18,20`。生成スクリプトが `" " in choice` で語句種別を決めるため、時制・不定詞などの複数語表現も熟語側へ入り、Q12/S05が体系的に発生している。
- 会話文（`A:`を含む設問）は、公式2026-1/2025-3/2025-2が各 `2/17`、`10/17`、`4/17`、mock-1〜4が各 `4/20`、`9/20`、`8/20`、`8/20`。既存2級公式の範囲内で、会話文比率だけからの追加指摘はなかった。
- 全体の場面は学校・仕事・家庭・健康・環境・旅行などに分散しており、同一場面の設問が連続する明白な構造上の偏りは目視では確認できなかった。
- 誤答が文脈上成立するか、語義・和訳が自然か、級相当の難易度か、正答が一意か、出典が妥当かは、このSkillの対象外なので判定していない。正答一意性の独立レビューも実施していない。
- ブラウザ確認は未実施。今回の依頼は読み取り専用の形式・構造監査で、UI・生成物の変更を行っていないため、ブラウザ回帰確認の対象変更がない。

## 機械検証の実結果

| コマンド | 結果 |
| --- | --- |
| `graft check` | 成功。`graph check: OK`。deep layerは未構築という注記のみ。 |
| `graft ask "..." --source` | 成功。監査CLI、manifest、2級生成正本、公式照合、共有coreImage処理の該当ソースを確認した。 |
| `py -3 scripts/check_q1_data.py` | 終了コード0、manifest上44セットすべて `OK`、`Q1 data: OK`。 |
| `npm test` | 終了コード0。build freshness、core image、語源、状態遷移、学習UI等の既存契約がすべて成功。 |
| `py -3 scripts/audit_question_set.py --baseline` | 終了コード0。基準24セット、25問、熟語4問、空所`(   )`、設問13〜45語、例文8〜15語。 |
| `py -3 scripts/audit_question_set.py --grade eiken2` | 終了コード1。ERROR 14 / WARN 15、対象7セット。 |
| `py -3 scripts/audit_question_set.py --grade eiken2 --json` | 上記と同じ対象・件数・findingsを機械可読形式で再確認。 |

## 判定と次工程への引き渡し

- 公式WARN（eiken2-2025-2/3のQ14、eiken2-2025-3のQ13/V10）は公式出題順・語彙構成を保持した結果として扱い、模試修正計画と混ぜない。
- mock-1〜4は、まず語句種別の定義（空白を含む表現をすべて熟語にするか、時制・不定詞等を単語側へ扱うか）を決めてから、設問単位の単語／熟語統一と熟語設問末尾化を計画する。mock-3はそれに加えて `the time` / `the next` のchainを3段以上へ直すか、語句を差し替える判断が必要。句動詞比率とPOSのWARNは自作セットの設計判断として計画に含める。
- 次担当はこのレポートを入力に、内容面（語義・和訳・難易度・正答一意性・出典）を別途確認したうえで実装計画を作成する。監査時点では修正・再生成・再監査は未実施。

**First unfinished task:** kiraが本レポートのfindingsを実装計画へ落とし込むこと。
**Integration handoff:** yunaは承認済み計画に従い、`data/*.json`を直接編集せず、各 `scripts/build_q1_eiken2_mock_*.py`（および必要な公式正本）を修正して再生成し、`check_q1_data.py`、`npm test`、対象監査、内容面レビューを再実行すること。
