# 実装計画: 本番形式問題の過去問スタイル整合 (2026-09-27)

## 計画状態

- `DONE_WITH_CONCERNS`（計画範囲の実装・検証完了。T1とJevヒューリスティックの留保あり）

## 目標

1級模試の設問文体を、収録済み公式3回分で観測した文長・会話形式へ近づける。既存の `datasetId`、設問番号 `q`、選択肢、`answerIndex` は維持する。問題数変更は進捗互換性に関わるため、ユーザー判断として分離する。

## 入力と証拠境界

- 監査入力: 2026-09-27の会話内read-only監査。manifest上の模試29セット、685問。
- 比較対象: 各級の公式セット `2025-2`、`2025-3`、`2026-1`。
- 根拠文書: `README.md`、`docs/EIKEN1_ALIGNMENT_REVIEW.md`、`docs/MOCK_10_21_REVIEW.md`。
- Jevは公式問題群を参照したヒューリスティック評価であり、校正済み評価器ではない。既存 `scripts/jev_check_questions.py` は正答、複数成立、和訳を点検し、スタイルは点検しない。

## 監査指摘

| ID | 証拠段階 | 指摘 |
| --- | --- | --- |
| F-01 | 確認済み | 模試685問は全問、4選択肢、空所1か所、範囲内の `answerIndex` を持つ。 |
| F-02 | ヒューリスティック | Jev総合はstrong 4、partial 20、weak 5。weakは1級mock-12/-13/-14/-19/-20。 |
| F-03 | 確認済み＋判断待ち | 1級公式は各22問、模試は各25問。READMEは差を維持すると記録するが、今回も維持するかは未確認。 |
| F-04 | 確認済み | 1級公式は平均25.24語、中央値25、会話6/66（9.1%）。mock-1〜9は平均28.67語、中央値29、会話37/225（16.4%）。mock-1は7/25、mock-5は8/25。 |
| F-05 | 確認済み | 1級mock-10〜21は平均16.51語、中央値16、範囲15〜28、会話0/300。Jevの主懸念は短く詳細に乏しい設問と会話欠如。 |
| F-06 | 確認済み | 2級公式は各17問、平均26.59語、会話16/51（31.4%）。模試は各20問、平均25.2語、会話29/80（36.2%）で文長・比率は近い。 |
| F-07 | 要確認 | 2級4セットはJevでpartial。主因候補は件数と個別会話文体だが、改稿すべき個別問題は監査で特定されていない。 |
| F-08 | 確認済み＋ヒューリスティック | 準2級は公式・模試とも各15問。公式平均24.2語・会話44.4%、模試平均23.3語・会話41.7%。Jevは全4セットstrong、mock-4はstrong 0.54 / partial 0.43。 |
| F-09 | 限定的確認 | 正規化完全一致とSequenceMatcher 0.80以上の模試対公式ペアは0。言い換え転載は未確認。 |
| F-10 | 確認済み | 1級mock-8/-9間に完全一致10問。過去問スタイル改善とは別目的。 |

## 対象範囲 / 対象外

- 恒久変更: 1級mock-10〜21の文長・詳細・会話形式、mock-1/-5の会話過多だけ。
- 2級は近似プロファイルを維持確認し、準2級は変更しない。
- F-10は対象外。重複解消は語彙配置・選択肢・進捗への影響を別に評価する。
- UI、保存形式、新規依存、公開は対象外。

## 前提と実装前判断

- `static/src/20-storage.js` は `datasetId` 由来のキーへ進捗を保存し、学習計画記録は設問番号を使う。削除・並べ替え・採番変更は既存 `(datasetId,q)` の意味を変え得る。
- 1級25問、2級20問を維持するか公式件数へ変えるかはT1で判断する。未回答なら `WAITING_FOR_EVIDENCE` とし、件数・IDを保つT2〜T7は進める。
- F-09のscreenは転載不存在の証明ではない。

## 変更方針

1. 公式3回と模試のプロファイルを再現する決定的checkerと、固定したJev参考レビュー手順を先に作る。
2. 1級改稿では `q`、choices、`answerIndex`、出題語を固定し、正答を一意にする状況・話者目的・結果と対応和訳だけを正本builderで変更する。
3. 生成JSONを直接編集せずbuilderから再生成する。
4. 2級・準2級で新しい欠陥を探さず、監査済み集計と既存検査だけを再確認する。

## 変更ファイルマップ

| ファイル | 区分・責務 |
| --- | --- |
| `scripts/check_past_paper_style.py` | 新規正本。件数、語数、中央値、会話数、構造、表層類似を集計する。 |
| `scripts/jev_check_past_paper_style.py` | 新規正本。公式3回参照の固定プロンプトと入力hashを含む参考評価を、実行ごとに一意な `out/jev-past-paper-style-runs/` 配下へ出す。 |
| `scripts/build_q1_mock_{10..21}_data.py` | 変更正本。mock-10〜21の `QUESTIONS`。 |
| `scripts/build_q1_mock_{1,5}_data.py` | 変更正本。mock-1/-5の `QUESTIONS`。 |
| `data/questions_1_mock-{1,5,10..21}.json` | builderによる再生成物。直接編集禁止。 |
| 対応 `data/vocab_1_mock-*.json` | builderが同時出力する再生成物。意図しない内容差分は禁止。 |
| 公式・2級・準2級の `data/questions_*.json` | 参照専用。 |
| `scripts/audit_question_set.py`、`scripts/check_eiken1_alignment.py` | 既存の形式・共通契約検査。変更しない。 |

## 並列実装設計

- execution_mode: `PARALLEL_SAFE`（T0完了後のP1だけ）。その他は `SERIAL_ONLY`。
- `YUNA-A`: T2A（mock-10〜15）後にT3（mock-1/-5）。
- `YUNA-B`: T2B（mock-16〜21）。
- 起動条件: T0完了、開始時の `git status --short` で専有write_setに既存変更がないこと。
- 共有read_set: T0 checker、公式JSON、`scripts/lib/set_builders.py`、manifest、既存checker。
- conflicts: 共通builder、manifest、checker契約、同一JSON、同一outファイルの変更が必要なら `PAUSED` として親Agentが直列化する。
- checkout: 同一checkoutでは親Agentが前後に非重複を確認する。別worktreeでも統合は親Agentが行う。YUNAへmerge、cherry-pick、commit、公開を割り当てない。
- integration_owner: 親Agent。両レーンのGate A/B、変更ファイル、未完了項目が返るまでT7へ進まない。

## タスク

### T0: スタイル検証契約を固定する

- 種別: `IMPLEMENT`
- 対応指摘: F-01, F-02, F-04, F-05, F-06, F-08, F-09
- owner: `SERIAL`; parallel_group: `なし`; depends_on: `なし`
- write_set: `scripts/check_past_paper_style.py`, `scripts/jev_check_past_paper_style.py`
- read_set: 公式・模試questions JSON、manifest、既存Jev checker
- conflicts: T0完了前にP1を開始しない。integration_owner: 親Agent
- 変更後の状態:
  - `--grade` / `--datasets` で設問数、単語数の平均・中央値・範囲、`A:`/`B:`による会話数、4択・空所・正答位置をJSON出力する。
  - 完全一致とSequenceMatcher 0.80以上を報告するが、非転載とは判定しない。
  - `--check-targets` は1級mock-10〜21の各セット平均・中央値22〜29語、各1〜4会話、12セット合計会話率6〜12%、mock-1/-5各1〜4会話、mock-1〜9合計8〜13%、全対象の構造契約を検査する。
  - `--datasets` で一部だけを指定した場合、入力された各セットの文長・会話数・構造閾値だけを判定する。mock-10〜21の12セット、またはmock-1〜9の9セットがすべて入力された場合だけ対応する合計会話率を判定する。コホートが不足する集計項目は成功扱いにせず、結果へ `NOT_CHECKED` と不足datasetIdを出す。全コホート率の合否はT7だけで確定する。
  - Jev版は必須の `--output-dir` と `--fail-if-exists` を持つ。固定プロンプト版、入力SHA-256、確率、理由を指定ディレクトリ内のdataset別JSONへ保存し「参考評価」と表示する。出力先が既に存在するときは書き込まず非0で終了する。正答情報をスタイル判定へ渡さない。
- Gate A: `py -3 -m py_compile scripts/check_past_paper_style.py scripts/jev_check_past_paper_style.py`
  - 期待結果: 終了コード0。
- Gate B: `py -3 scripts/check_past_paper_style.py --grade eiken1 --json`
  - 期待結果: 公式平均25.24・中央値25・会話6/66、mock-10〜21平均16.51・中央値16・会話0/300を丸め前値から再現する。
- 受入基準: 監査値を再現し、目標未達時に非0となるcheckerと再実行可能なJev手順が揃う。
- 未達時: APIキー不在でも決定的checkerを完成し、Jevだけ `UNVERIFIED` とする。
- コミット: `test: add past-paper style profile checks`

### T1: 1級・2級の問題数方針を決める

- 種別: `EXTERNAL_EVIDENCE`
- 対応指摘: F-03, F-06, F-07
- owner: `SERIAL`; parallel_group: `なし`; depends_on: `なし`
- write_set: なし; read_set: README、storage、manifest; conflicts: 件数変更を他タスクへ混ぜない; integration_owner: 親Agent
- 判断: A「現行件数を維持し、本番形式は出題様式・文体を指す」、B「公式件数へ合わせ、削除問題・進捗・総問題目標を扱う別の移行計画を先に作る」。
- 検証: 親Agentが判断者・日付・A/Bを実行記録へ残す。
- 受入基準: A/Bが記録されるか `WAITING_FOR_EVIDENCE` と明示される。
- 未達時: T2〜T7を止めず、件数・ID・順序を維持する。Bでも本計画では削除しない。
- コミット: なし（外部判断のみ）

### T2A: 1級mock-10〜15を改稿する

- 種別: `IMPLEMENT`; 対応指摘: F-02, F-05
- owner: `YUNA-A`; parallel_group: `P1`; depends_on: T0
- write_set: mock-10〜15のbuilder、対応questions/vocab生成JSON
- read_set: 公式1級3回、共通builder、T0/既存checker
- conflicts: T2Bと非重複。共通ファイル変更が必要なら停止。integration_owner: 親Agent
- 変更後の状態: `q`、choices、`answerIndex`、出題語を固定し、各セット平均・中央値22〜29語へ入る具体的状況を加える。各セット1〜4問を自然な会話にし、T2Bと合計率6〜12%になるよう事前配分する。和訳を同期しbuilderで再生成する。
- Gate A: PowerShellで `$rounds = 10..15; foreach ($round in $rounds) { py -3 "scripts/build_q1_mock_${round}_data.py"; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }`、続けて `py -3 scripts/audit_question_set.py eiken1-mock-10 eiken1-mock-11 eiken1-mock-12 eiken1-mock-13 eiken1-mock-14 eiken1-mock-15`、続けて `$ids = 10..15 | ForEach-Object { "eiken1-mock-$_" }; foreach ($datasetId in $ids) { py -3 scripts/check_eiken1_alignment.py --dataset-id $datasetId; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }`。
  - 期待結果: 全て0。vocab JSONに意図しない差分なし。
- Gate B: `py -3 scripts/check_past_paper_style.py --datasets eiken1-mock-10 eiken1-mock-11 eiken1-mock-12 eiken1-mock-13 eiken1-mock-14 eiken1-mock-15 --check-targets --json`
  - 期待結果: 入力6セットそれぞれの平均・中央値22〜29語、会話1〜4問、構造契約に合格。mock-10〜21合計会話率は `NOT_CHECKED` と不足datasetIdを出し、このタスクでは合否判定しない。
- 受入基準: 6セットがGate A/B合格、ID・choices・正答位置不変。weakだった12〜14も含む。
- 未達時: 複数成立する問題だけ番号と理由を返し、他は続行する。
- コミット: `content: align eiken1 mock 10-15 stem style`

### T2B: 1級mock-16〜21を改稿する

- 種別: `IMPLEMENT`; 対応指摘: F-02, F-05
- owner: `YUNA-B`; parallel_group: `P1`; depends_on: T0
- write_set: `scripts/build_q1_mock_16_data.py`, `scripts/build_q1_mock_17_data.py`, `scripts/build_q1_mock_18_data.py`, `scripts/build_q1_mock_19_data.py`, `scripts/build_q1_mock_20_data.py`, `scripts/build_q1_mock_21_data.py`, `data/questions_1_mock-16.json`, `data/questions_1_mock-17.json`, `data/questions_1_mock-18.json`, `data/questions_1_mock-19.json`, `data/questions_1_mock-20.json`, `data/questions_1_mock-21.json`, `data/vocab_1_mock-16.json`, `data/vocab_1_mock-17.json`, `data/vocab_1_mock-18.json`, `data/vocab_1_mock-19.json`, `data/vocab_1_mock-20.json`, `data/vocab_1_mock-21.json`
- read_set: 1級公式3回のquestions JSON、`scripts/lib/set_builders.py`、`scripts/check_past_paper_style.py`、`scripts/audit_question_set.py`、`scripts/check_eiken1_alignment.py`
- conflicts: T2A/T3のwrite_setと非重複。共通builder、manifest、checker、mock-1/-5/-10〜15の正本または生成JSONの変更が必要なら `PAUSED` として親Agentへ返す。
- integration_owner: 親Agent
- 変更後の状態: `q`、choices、`answerIndex`、出題語を固定し、各セット平均・中央値22〜29語へ入る具体的状況を加える。各セット1〜4問を自然な会話にし、T2Aと合計率6〜12%になるよう事前配分する。全変更stemに対応するtranslationを同じ項目で更新し、builderで再生成する。
- Gate A: PowerShellで `$rounds = 16..21; foreach ($round in $rounds) { py -3 "scripts/build_q1_mock_${round}_data.py"; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }`、続けて `py -3 scripts/audit_question_set.py eiken1-mock-16 eiken1-mock-17 eiken1-mock-18 eiken1-mock-19 eiken1-mock-20 eiken1-mock-21`、続けて `$ids = 16..21 | ForEach-Object { "eiken1-mock-$_" }; foreach ($datasetId in $ids) { py -3 scripts/check_eiken1_alignment.py --dataset-id $datasetId; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }`。
  - 期待結果: 全て0。vocab JSONに意図しない差分なし。
- Gate B: `py -3 scripts/check_past_paper_style.py --datasets eiken1-mock-16 eiken1-mock-17 eiken1-mock-18 eiken1-mock-19 eiken1-mock-20 eiken1-mock-21 --check-targets --json`
  - 期待結果: 入力6セットそれぞれの平均・中央値22〜29語、会話1〜4問、構造契約に合格。mock-10〜21合計会話率は `NOT_CHECKED` と不足datasetIdを出し、このタスクでは合否判定しない。
- 受入基準: 6セット合格、ID・choices・正答位置不変。weakだった19/-20も含む。
- 未達時: 個別問題で選択肢が複数成立する場合は、その問題だけ未完了としてdatasetId・問題番号・理由を返し、他セットの改稿は続ける。weakだったmock-19/-20が未完ならT6/T7で合格扱いにしない。共通ファイル変更が必要なら作業を停止して親Agentへ返す。
- コミット: `content: align eiken1 mock 16-21 stem style`

### T3: 1級mock-1/-5の会話過剰だけを調整する

- 種別: `IMPLEMENT`; 対応指摘: F-04
- owner: `YUNA-A`; parallel_group: `P1`（T2A後に同レーン内で直列）; depends_on: T0, T2A
- write_set: mock-1/-5のbuilder、対応questions/vocab生成JSON
- read_set: 公式1級3回、mock-2〜4/-6〜9、T0 checker
- conflicts: T2Bと非重複。mock-2〜4/-6〜9は変更禁止。integration_owner: 親Agent
- 変更後の状態: 各セットの会話を1〜4問へ減らす。対象会話を同じ情報量の2〜3文の叙述へ変え、`q`、choices、正答位置を維持する。平均・中央値を現状より増やさず、和訳を同期する。
- Gate A: `py -3 scripts/build_q1_mock_1_data.py`、`py -3 scripts/build_q1_mock_5_data.py`、`py -3 scripts/audit_question_set.py eiken1-mock-1 eiken1-mock-5`、`py -3 scripts/check_eiken1_alignment.py --dataset-id eiken1-mock-1`、`py -3 scripts/check_eiken1_alignment.py --dataset-id eiken1-mock-5`。
  - 期待結果: 全て0。vocab JSONに意図しない差分なし。
- Gate B: `py -3 scripts/check_past_paper_style.py --datasets eiken1-mock-1 eiken1-mock-5 --check-targets --json`
  - 期待結果: mock-1/-5それぞれが会話1〜4問、構造契約に合格。mock-1〜9合計会話率は `NOT_CHECKED` と不足datasetIdを出し、このタスクでは合否判定しない。
- 受入基準: 過剰分だけが減り、他のmock-1〜9は無変更。
- 未達時: 一意性が崩れる問題は変更せず番号を返す。目標未達は `DONE_WITH_CONCERNS`。
- コミット: `content: rebalance dialogue stems in eiken1 mock 1 and 5`

### T4: 2級の近似プロファイルを維持確認する

- 種別: `VERIFY_ONLY`; 対応指摘: F-06, F-07
- owner: `SERIAL`; parallel_group: `なし`; depends_on: T0
- write_set: なし; read_set: 2級公式・模試、既存checker; conflicts: 個別改稿を始めない; integration_owner: 親Agent
- Gate A: `py -3 scripts/audit_question_set.py eiken2-mock-1 eiken2-mock-2 eiken2-mock-3 eiken2-mock-4`、`py -3 scripts/check_eiken2_mock_1_data.py`、`py -3 scripts/check_eiken2_mock_2_data.py`、`py -3 scripts/check_eiken2_mock_3_data.py`、`py -3 scripts/check_eiken2_mock_4_data.py`。
  - 期待結果: 全て0。
- Gate B: `py -3 scripts/check_past_paper_style.py --grade eiken2 --json`
  - 期待結果: 公式平均26.59・会話16/51、模試平均25.2・会話29/80を再現。
- 受入基準: データ無変更で近似プロファイルと構造契約を確認。
- 未達時: 再現しなければ `NOT_REPRODUCED`。具体的欠陥が示された場合だけ別計画へ昇格。
- コミット: なし（検証のみ）

### T5: 準2級を変更対象外として確認する

- 種別: `VERIFY_ONLY`; 対応指摘: F-08
- owner: `SERIAL`; parallel_group: `なし`; depends_on: T0
- write_set: なし; read_set: 準2級公式・模試、既存checker; conflicts: Jev境界値だけで改稿しない; integration_owner: 親Agent
- Gate A: `py -3 scripts/check_p2_mock_data.py` と `py -3 scripts/audit_question_set.py eikenp2-mock-1 eikenp2-mock-2 eikenp2-mock-3 eikenp2-mock-4`。
  - 期待結果: 全て0。
- Gate B: `py -3 scripts/check_past_paper_style.py --grade eikenp2 --json`
  - 期待結果: 公式平均24.2・会話20/45、模試平均23.3・会話25/60を再現。
- 受入基準: データ無変更で現状を確認。
- 未達時: `NOT_REPRODUCED`。具体的欠陥が出た場合だけ別計画へ昇格。
- コミット: なし（検証のみ）

### T6: Jevで改稿後スタイルを参考再評価する

- 種別: `VERIFY_ONLY`; 対応指摘: F-02, F-05, F-07, F-08
- owner: `SERIAL`; parallel_group: `なし`; depends_on: T2A, T2B, T3
- write_set: リポジトリ内はなし。スタイル評価はgitignore済み `out/jev-past-paper-style-runs/` の一意な実行ディレクトリ、内容回帰はOS一時ディレクトリだけに出力する。
- read_set: 公式・模試questions JSON、T0スクリプト、既存 `scripts/jev_check_questions.py`
- conflicts: リポジトリ既存の `out/jev-check-*.json` を読み書きしない。同じスタイル出力ディレクトリを再利用しない。内容回帰用JSONをリポジトリの `data/` へ複製しない。
- integration_owner: 親Agent
- Gate C: PowerShellで `$runStamp = Get-Date -Format 'yyyyMMdd-HHmmss-fffffff'; $runDir = "out/jev-past-paper-style-runs/$runStamp"; python scripts/jev_check_past_paper_style.py --output-dir $runDir --fail-if-exists data/questions_1_mock-1.json data/questions_1_mock-5.json data/questions_1_mock-10.json data/questions_1_mock-11.json data/questions_1_mock-12.json data/questions_1_mock-13.json data/questions_1_mock-14.json data/questions_1_mock-15.json data/questions_1_mock-16.json data/questions_1_mock-17.json data/questions_1_mock-18.json data/questions_1_mock-19.json data/questions_1_mock-20.json data/questions_1_mock-21.json`
  - 期待結果: 確率・理由・hashをdataset別に保存。目標weak 0だが参考評価として不確実性を記録する。
- 全変更問題の内容回帰: PowerShellで次を順に実行する。
  1. `$jevTempRoot = Join-Path ([IO.Path]::GetTempPath()) ("eiken-q1-jev-" + [guid]::NewGuid().ToString("N")); $jevDataDir = Join-Path $jevTempRoot "data"; New-Item -ItemType Directory -Path $jevDataDir | Out-Null`
  2. `$files = @('questions_1_mock-1.json','questions_1_mock-5.json','questions_1_mock-10.json','questions_1_mock-11.json','questions_1_mock-12.json','questions_1_mock-13.json','questions_1_mock-14.json','questions_1_mock-15.json','questions_1_mock-16.json','questions_1_mock-17.json','questions_1_mock-18.json','questions_1_mock-19.json','questions_1_mock-20.json','questions_1_mock-21.json'); foreach ($file in $files) { Copy-Item -LiteralPath (Join-Path 'data' $file) -Destination (Join-Path $jevDataDir $file) }`
  3. `$jevInputs = $files | ForEach-Object { Join-Path $jevDataDir $_ }; python scripts/jev_check_questions.py $jevInputs`
  - 期待結果: 14ファイル350問を全件評価し、結果は一意な `$jevTempRoot/out/jev-check-*.json` だけに作られる。リポジトリの既存 `out/jev-check-*.json` は更新時刻・内容とも不変。
  - フラグ処理: 各フラグを問題番号、種類、確率、判断根拠、処置（stem/translationを再修正、または既存選択肢でも正答一意・和訳整合と人が確認して受容）とともに統合記録へ残す。受容理由のないフラグを残さない。Jevはヒューリスティックなので生のフラグ0件を必須にせず、未処置・未判断0件を必須にする。
- 受入基準: スタイル結果をGate A/Bと分けて記録し、変更350問の正答一意性・translationについてJevフラグが全件処置済みである。
- 未達時: APIキー・外部サービス不在は `UNVERIFIED` とし、再開条件を明記する。未解決フラグがある場合は該当問題をT2A/T2B/T3へ戻し、T7を完了にしない。スタイルweakだけでは自動不合格にしない。
- コミット: なし（検証のみ）

### T7: 統合差分と代表回帰を確認する

- 種別: `VERIFY_ONLY`; 対応指摘: F-01, F-03, F-04, F-05, F-06, F-09
- owner: `SERIAL`（親Agent）; parallel_group: `なし`; depends_on: T2A, T2B, T3, T4, T5, T6（T1は待たない）
- write_set: なし; read_set: 全差分・全checker結果; conflicts: write_set外変更、共通ファイル変更、生成物だけの編集で停止; integration_owner: 親Agent
- Gate A: `git diff --check`、`py -3 scripts/check_q1_data.py`、`py -3 scripts/check_eiken1_alignment.py --all`、`py -3 scripts/audit_question_set.py eiken1-mock-1 eiken1-mock-5 eiken1-mock-10 eiken1-mock-11 eiken1-mock-12 eiken1-mock-13 eiken1-mock-14 eiken1-mock-15 eiken1-mock-16 eiken1-mock-17 eiken1-mock-18 eiken1-mock-19 eiken1-mock-20 eiken1-mock-21`、`npm test`。
  - 期待結果: 全て終了コード0。既存ベースライン失敗がある場合は、変更前の同一コマンド結果を採取して今回差分との関係を分離し、今回の回帰がない場合だけ既存失敗として記録する。`npm test` の一部だけを全体成功と扱わない。
- Gate B: `py -3 scripts/check_past_paper_style.py --grade eiken1 --check-targets --json`
  - 期待結果: T0の全セット単位目標に加え、全コホートが揃った状態でmock-10〜21合計会話率6〜12%とmock-1〜9合計会話率8〜13%を判定して合格する。集計項目に `NOT_CHECKED` がなく、件数・datasetId・q・choices・answerIndexが基準と一致する。
- Gate C: 変更14セットから各1問をJSONで確認し、会話/非会話を交互に選び、英文・和訳・空所・一意性を記録する。全問内容判定はT6へ分離する。
- 受入基準: 計画外差分なし、Gate A/B成功、T1は `DECIDED` または `WAITING_FOR_EVIDENCE`。T6は350問の実行結果と全フラグの処置記録があり、未解決フラグ0件。
- 未達時: Gate A/B失敗、T6未実行、T6の未解決フラグありは統合完了にしない。T1待ちやT6の外部環境待ちは、完了済みの独立実装を巻き戻さず状態を `WAITING_FOR_EVIDENCE` または `UNVERIFIED` として保持する。
- コミット: なし（統合検証のみ）

## YUNA起動プロンプト

- YUNA-A: この計画のT2A後にT3を実行。write_setはmock-10〜15、mock-1/-5のbuilderと対応生成JSONだけ。T0完了後に開始し、共通ファイルを変更しない。Gate A/Bを返す。
- YUNA-B: T2Bを実行。write_setはmock-16〜21のbuilderと対応生成JSONだけ。条件は同じ。
- 両者の返却: `Worker / Task / Kind / Status / Changed files / Verification / First unfinished task / Integration handoff`。意図しないvocab差分、共有契約変更、未解決問題番号があれば `PAUSED`。

## トレーサビリティ

| 指摘 | 重大度 | 対応 | 完了条件 |
| --- | --- | --- | --- |
| F-01 | 低・回帰防止 | T0, T7 | 全対象の構造契約維持 |
| F-02 | 中・参考評価 | T0, T2A/B, T6 | 決定的目標合格、Jev参考再評価 |
| F-03 | 中・互換性 | T1, T7 | A/B記録。未決定時は件数・ID維持 |
| F-04 | 中 | T3, T7 | 各1〜4会話、mock-1〜9合計8〜13% |
| F-05 | 高 | T0, T2A/B, T7 | 各平均・中央値22〜29語、各1〜4会話、合計6〜12% |
| F-06 | 中 | T1, T4 | 件数判断を分離し、2級集計再現 |
| F-07 | 要確認 | T4, T6 | 恒久変更せず測定。具体的欠陥だけ別計画 |
| F-08 | 低 | T5, T6 | 無変更で集計・構造を再確認 |
| F-09 | 未確認含む | T0, T7 | screen再現、非転載とは断定しない |
| F-10 | 中 | 対応しない | 別目的のため別監査・計画 |

## リスクとロールバック

- 文脈追加による複数成立: 問題単位でbuilder変更を戻す。
- 英文・和訳ずれ: 同一項目で更新しT6/T7で確認する。
- builder副作用: vocab JSONに意図しない差分が出たら停止する。
- 進捗破損: T2/T3はID、q、件数、順序を固定する。件数変更は別移行計画なしに実施しない。
- 評価器への過適合: 語数・会話率、既存構造検査、Jev参考評価を別々に記録する。
- ロールバック: 正本builderと対応生成JSONをタスク単位で戻す。共通builder、manifest、保存コードは変更しない。

## セルフレビュー

- [x] F-01〜F-10を対応または対象外として追跡した。
- [x] 全タスクに種別、owner、parallel_group、depends_on、write/read set、conflicts、integration_owner、検証、受入、コミット、未達時を記載した。
- [x] 正本builderから生成し、生成JSONの直接編集を禁じた。
- [x] T1/T6の証拠待ちは独立実装を止めない。
- [x] 各IMPLEMENTにGate A/Bがあり、Gate Cだけを完了証拠にしていない。
- [x] P1のwrite_setは非重複で、共有変更時の停止条件がある。
- [x] Jevを参考評価として扱い、未実行時の再開条件がある。
- [x] Jev出力は一意な実行ディレクトリへ限定し、既存 `out/jev-check-*.json` を上書きしない。
- [x] 変更14セット350問を既存Jev内容checkerで全件確認し、全フラグを処置するGateがある。
- [x] 実行コマンドに未解決のID・回番号・パスのプレースホルダがない。
- [x] データ再生成後の統合Gateに `check_q1_data.py` と `npm test` がある。
- [x] 部分datasetのGate Bはセット単位だけを判定し、全コホート率はT7へ集約した。
- [x] 実装、commit、push、deployは計画作成中に行っていない。

## 実装記録（2026-09-27）

- T0: 決定的スタイルcheckerとJev参考評価runnerを追加。14セットの実装後検査と公式3回の比較で使用。
- T1: `WAITING_FOR_EVIDENCE`。問題数の判断回答がないため、1級25問・2級20問および既存の `(datasetId, q)` を維持。
- T2A/T2B/T3: 1級mock-10〜21の設問文に具体的文脈と会話を加え、mock-1/-5の会話過多を調整。14セット中238問のstemを変更し、全てbuilderから再生成。件数、q、choices、answerIndex、出題語を維持し、vocabデータの意味内容に差分なし。
- Gate Cで一般的な埋め草文と定型的な会話を検出したため、2回改稿。最終稿では12セットの会話を1行の自然な応答形式に直し、各セットから会話・非会話を交互に1問ずつ選んで英文、空所、正答、選択肢、和訳を確認。目視サンプルに明白な不整合なし。対象14セット内で6語以上の同一文が3回以上反復する例は0。
- T4/T5: 2級・準2級を無変更で確認。既存のセット監査と級別checkerは成功。
- T6: スタイルJevは14/14セットでlevel 3が最多（平均score 3.07/4、confidence 0.55〜0.66）。内容Jevは350/350問を評価し、正答不一致・意図正答確率低下・複数正答・和訳不整合のフラグ0。`out/jev-check-*.json` 21件の内容hashとサイズは基準一致。Jevの `dialogue_mismatch >= 0.5` は9/14セットに残るため、校正されていない参考診断として留保し、これに合わせた追加改稿は行わない。
- T7: 全構造・目標検査に成功。公式1級は平均25.24語・中央値25語・会話率9.09%。mock-10〜21は23.94語・26語・8.00%、mock-1〜9は28.32語・28語・11.56%。表層比較34,650ペアで完全一致0、SequenceMatcher 0.80以上0。これは言い換え転載がない証明ではない。
- 検証: 対象Pythonの構文検査、`check_q1_data.py`、14セットの `audit_question_set.py`（ERROR 0、mock-1/-5の既存空所表記WARN 2）、スタイルchecker、`npm test`（47件）が成功。全体 `check_eiken1_alignment.py --all` は終了コード1だが、変更前からある2級mock-1〜4の音声/IPA不足8/9/15/16件と同一。1級・準2級のalignmentは成功。`git diff --check` 成功。
- Jevの既存結果は内容を上書きせず、新規評価は一意なrunディレクトリまたはOS一時領域へ保存。基準mtimeはJavaScript数値化でナノ秒精度を失うため、変更なしの根拠は内容hash・サイズと評価後の運用履歴に置く。
- 最終状態: 計画内の独立実装・検証は完了。T1は外部判断待ち。コミット、push、公開は未実施。
