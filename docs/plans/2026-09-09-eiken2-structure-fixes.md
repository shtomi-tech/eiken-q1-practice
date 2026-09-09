# 実装計画: 英検2級 eiken2-* 形式・構造修正 (2026-09-09)

## 計画状態
- `READY`（セルフレビュー済み・実装へ引き渡し可）
- ユーザーは `mal → kira → yuna` の一連実行を明示済み。本計画内は実装承認済み。

## 目標
自作 `eiken2-mock-1`〜`mock-4` を各20問・80語句、単語設問14問の後に熟語設問6問が連続する構成へ揃える。4択の種別・POS、核心イメージ、句動詞比率を監査契約へ適合させ、正本builder、生成JSON、専用検査、全体検査を整合させる。

## 入力・証拠
- 監査: `docs/EIKEN2_STRUCTURE_AUDIT_2026-09-09.md`（形式・構造監査）
- 実測: `py -3 scripts/audit_question_set.py --grade eiken2` は終了1、ERROR 14 / WARN 15 / 7セット。`check_q1_data.py` と `npm test` は終了0。
- 確認済み: 4builderは `" " in choice` でword/idiomを分類し、各 `data/questions_2_mock-N.json` / `vocab_2_mock-N.json` を生成する。専用checkerは現行件数を固定検査する。
- 未確認: 語義・和訳・難易度・正答一意性・出典。監査は対象外と明記。
- 開始時: `main`、worktreeは大幅にdirty。4builder、8生成JSON、4checkerには差分なし。`package.json` / lockは既に変更済み、監査CLIは未追跡。既存差分を戻さない。

## 対象 / 対象外
- 対象: F-06〜F-29（自作mockのERROR 14 / WARN 10）。
- 対象外: F-01〜F-05（公式由来WARN 5）。公式出題順・語彙構成を保持する。
- UI、manifest、進捗、音声、語源、依存、公式データ、公開は変更しない。

## 前提・受入目標
- T1で変更対象と句動詞候補を独立レビューし、セット別の最終Q順、stem、4択、answerIndex、訳、DETAILS、CORE_IMAGES、particle/Senseを値まで確定する。安全な値を確定できないセットは `NEEDS_CONTEXT`。他セットは続行可。
- After目標（未観測）: 各mock 20問、words 56、idioms 24、熟語Q15〜Q20、設問内同一種別、POS 2種類以下、particle付き6件以上、全idiom chain 3段以上、stem 13〜45語。
- 監査CLIが消失・変更されたら監査Gateは `UNVERIFIED`。対象write_setへ他者差分が入ったら該当タスクを `PAUSED`。推測で代替・上書きしない。

## 変更方針・ファイルマップ
空白ではなく設問単位の明示契約（熟語Q番号集合15〜20）でbucketを決める。`QUESTIONS` を14単語+6熟語へ並べ、T1承認内容だけで4択・正答・訳・DETAILS・CORE_IMAGESを一体更新する。JSONは直接編集せずbuilderで再生成する。

| ファイル | 扱い / 責務 |
|---|---|
| `scripts/build_q1_eiken2_mock_{1,2,3,4}_data.py` | 変更・正本。問題、メタデータ、種別、生成 |
| `scripts/check_eiken2_mock_{1,2,3,4}_data.py` | 変更。内容契約と56/24件数 |
| `data/questions_2_mock-{1,2,3,4}.json` | builderによる再生成物 |
| `data/vocab_2_mock-{1,2,3,4}.json` | builderによる再生成物 |
| `scripts/audit_question_set.py`, `check_q1_data.py`, `data/manifest.json`, package files | 読取専用 |

## 実行設計
- execution_mode: `SERIAL_ONLY`; Worker: `YUNA-A`; YUNA-B: なし。
- 依存: `T1 → T2 → T3 → T4 → T5 → T6`。T1はセット別判定で、未達セットを飛ばし独立セットを直列続行可。
- 理由: T1が共有内容契約を確定し、builder・生成物・checkerを一体更新する。全体監査、Q1検査、npm testは同じcheckout/生成物を読む。dirty環境で並行再生成すると帰属が曖昧になる。
- checkout: 現在の同一checkout。別worktree、merge、cherry-pickなし。
- integration_owner: 親Agent。YUNA-AのT6結果と対象限定diffまで待つ。
- 競合: write_setへの第三者差分、監査CLI変更、同じ生成先を別プロセスが更新した場合は `PAUSED`。

## Gate
- Gate A: 対象builder/checkerを `py -3 -m py_compile`、builder実行、専用checker、`py -3 scripts/check_q1_data.py`。
- Gate B: 各mockの監査finding 0、20/56/24、熟語Q15〜Q20を記録。変更設問1件とQ15のstem/4択/正答/訳/例文/coreImageを実装者が読み合わせる。
- Gate C: 4専用checker、全Q1検査、英検2級監査、`npm test`、対象diff。UI/公開変更なしのためブラウザ・公開確認は省略。UI/公開変更が別途入った場合のみ再開。

## タスク

### T1: 内容・正答一意性の独立レビュー
- 種別: `VERIFY_ONLY`; 対応: F-06〜F-29; owner: `YUNA-A`; parallel_group: `なし`; depends_on: `なし`
- write_set: `なし`
- read_set: 4builder、8生成JSON、lemmas、同級語彙、全配信熟語、particle辞書
- conflicts: 恒久書込で中止。レビュー中にbuilderが変われば該当セットを再読込。
- integration_owner: 親Agent
- 対象: mock-1 Q18/19/20+particle候補、mock-2 Q15+particle候補、mock-3 Q17/18/20+particle候補、mock-4 Q13/18/19+particle候補。並べ替え後の全20問もanswerIndex/訳を照合。
- 変更後: 変更なし。結果へセット別の最終Q1〜20順と、変更する全値（stem/choices/answerIndex/translation/DETAILS/CORE_IMAGES/particleSense）を記録する。
- 検証: 各選択肢の文法・意味・コロケーション・一意性・2級相当性、同級語句/原形/全熟語重複、particleSenseを確認。
- 期待/受入: 各設問の正答が一意、POS≤2、14+6、particle≥6/24を満たす値付き表。複数正解、正解なし、誤文、重複は不採用。
- 未達: 該当セットのみ `NEEDS_CONTEXT` / 外部出典待ちは `WAITING_FOR_EVIDENCE`。他セットは続行。
- コミット: なし（検証のみ）

### T2: mock-1修正
- 種別: `IMPLEMENT`; 対応: F-06〜F-11; owner: `YUNA-A`; parallel_group: `なし`; depends_on: T1 mock-1承認
- write_set: mock-1 builder/checker/questions JSON/vocab JSON; read_set: T1結果、共通検査・辞書; conflicts: 対象外差分で `PAUSED`; integration_owner: 親Agent
- 変更内容: `have/had/will have/would have` を全てword扱いにする。空白判定を廃止しQ15〜20のみidiomへ生成。T1表で並べ替え・置換しQ19/20 POS≤2、particle≥6/24。meta、自己検査、checkerを56/24へ更新し再生成。
- 検証: Gate A。Gate BでQ15と変更設問1件を読み合わせ、監査のmock-1 findingを確認。
- 期待/受入: 20/56/24、熟語Q15〜20、F-06〜11が0、T1表とJSON一致。
- 未達: T1未達は `NEEDS_CONTEXT`。検査失敗はmock-1内だけで修正。
- コミット: `fix(data): align eiken2 mock 1 structure`

### T3: mock-2修正
- 種別: `IMPLEMENT`; 対応: F-12〜F-14; owner: `YUNA-A`; parallel_group: `なし`; depends_on: T2完了またはskip、T1 mock-2承認
- write_set: mock-2 builder/checker/questions JSON/vocab JSON; read_set: T1結果と共通読取; conflicts: 対象外差分で `PAUSED`; integration_owner: 親Agent
- 変更内容: Q15をT1承認の同一種別4択へ修正。Q15〜20を熟語として連続配置。設問単位分類、particle≥6/24、meta/自己検査/checker=56/24、再生成。
- 検証: mock-2対象のGate A/B。
- 期待/受入: 20/56/24、熟語Q15〜20、F-12〜14が0、T1表とJSON一致。
- 未達: T1未達はmock-2 `NEEDS_CONTEXT`、T4へ続行。
- コミット: `fix(data): align eiken2 mock 2 structure`

### T4: mock-3修正
- 種別: `IMPLEMENT`; 対応: F-15〜F-23; owner: `YUNA-A`; parallel_group: `なし`; depends_on: T3完了またはskip、T1 mock-3承認
- write_set: mock-3 builder/checker/questions JSON/vocab JSON; read_set: T1結果と共通読取; conflicts: 対象外差分で `PAUSED`; integration_owner: 親Agent
- 変更内容: Q17/18/20を各同一種別4択、Q15〜20を熟語へ配置。Q18/20 POS≤2、particle≥6/24。`the time/the next` をidiomに残すならchain≥3、wordならCORE_IMAGESから除く。設問単位分類、meta/自己検査/checker=56/24、再生成。
- 検証: mock-3対象のGate A/B。Q20残存idiomのchain長も記録。
- 期待/受入: 20/56/24、熟語Q15〜20、F-15〜23が0、T1表とJSON一致。
- 未達: T1未達はmock-3 `NEEDS_CONTEXT`、T5へ続行。
- コミット: `fix(data): align eiken2 mock 3 structure`

### T5: mock-4修正
- 種別: `IMPLEMENT`; 対応: F-24〜F-29; owner: `YUNA-A`; parallel_group: `なし`; depends_on: T4完了またはskip、T1 mock-4承認
- write_set: mock-4 builder/checker/questions JSON/vocab JSON; read_set: T1結果と共通読取; conflicts: 対象外差分で `PAUSED`; integration_owner: 親Agent
- 変更内容: Q13 stemへ意味を変えない語を加え13語以上。Q18を同一種別、Q18/19 POS≤2。Q15〜20を熟語へ配置、設問単位分類、particle≥6/24、meta/自己検査/checker=56/24、再生成。
- 検証: mock-4対象のGate A/B。Q13監査語数も記録。
- 期待/受入: 20/56/24、熟語Q15〜20、F-24〜29が0、T1表とJSON一致。
- 未達: T1未達はmock-4 `NEEDS_CONTEXT`。
- コミット: `fix(data): align eiken2 mock 4 structure`

### T6: 統合回帰・差分境界
- 種別: `VERIFY_ONLY`; 対応: F-06〜F-29; owner: `YUNA-A`; parallel_group: `なし`; depends_on: 実行可能なT2〜T5完了
- write_set: `なし`; read_set: 全write_set、監査、package、worktree; conflicts: 検証による予期しない書込で `PAUSED`; integration_owner: 親Agent
- 検証: Gate Aを4セット一括。Gate B `py -3 scripts/audit_question_set.py --grade eiken2 --json`。Gate C `npm test`; `git diff --check -- scripts/build_q1_eiken2_mock_*_data.py scripts/check_eiken2_mock_*_data.py data/questions_2_mock-*.json data/vocab_2_mock-*.json`; 同じpathspecの対象限定diff; `git status --short`。
- 期待/受入: Gate A/C終了0、自作finding 0、残存は公式F-01〜05のみ。差分はT2〜5 write_set内で、package/manifest/UI/公式に新規差分なし。
- 未達: 未実装セットは `DONE_WITH_CONCERNS` としF-ID/再開条件を返す。npm失敗は今回差分との関連を分け、既存dirtyを成功扱いしない。
- コミット: なし（検証のみ）

## トレーサビリティ
| F | dataset / 監査ID | 重大度 | 概要 | タスク / 受入 |
|---|---|---|---|---|
| F-01 | 2025-2 Q14 set | WARN | 正答1が0/17、公式順 | 対象外・公式無変更 |
| F-02 | 2025-3 Q13 Q13 | WARN | POS 3種、公式構成 | 対象外・公式無変更 |
| F-03 | 2025-3 Q14 set | WARN | 正答2が7/17 | 対象外・公式無変更 |
| F-04 | 2025-3 Q14 set | WARN | 正答4が1/17 | 対象外・公式無変更 |
| F-05 | 2025-3 V10 set | WARN | particle 3/28 | 対象外・公式無変更 |
| F-06 | m1 Q12 Q18 | ERROR | 時制4択が混在 | T1,T2・全word |
| F-07 | m1 S05 | ERROR | 熟語末尾非連続 | T2・Q15〜20 |
| F-08 | m1 Q13 Q19 | WARN | POS 3種 | T1,T2・≤2 |
| F-09 | m1 Q13 Q20 | WARN | POS 3種 | T1,T2・≤2 |
| F-10 | m1 S04 | WARN | 熟語設問7 | T2・6 |
| F-11 | m1 V10 | WARN | particle 1/26 | T1,T2・≥6/24 |
| F-12 | m2 Q12 Q15 | ERROR | despiteだけword | T1,T3・同一種別 |
| F-13 | m2 S05 | ERROR | 熟語末尾非連続 | T3・Q15〜20 |
| F-14 | m2 V10 | WARN | particle 1/23 | T1,T3・≥6/24 |
| F-15 | m3 Q12 Q17 | ERROR | 1件だけidiom | T1,T4・同一種別 |
| F-16 | m3 Q12 Q18 | ERROR | 時制4択が混在 | T1,T4・同一種別 |
| F-17 | m3 Q12 Q20 | ERROR | 2件だけidiom | T1,T4・同一種別 |
| F-18 | m3 S05 | ERROR | 熟語末尾非連続 | T4・Q15〜20 |
| F-19 | m3 V08 the time | ERROR | chain 2 | T1,T4・idiomなら≥3 |
| F-20 | m3 V08 the next | ERROR | chain 2 | T1,T4・idiomなら≥3 |
| F-21 | m3 V10 | ERROR | particle 0/17 | T1,T4・≥6/24 |
| F-22 | m3 Q13 Q18 | WARN | POS 3種 | T1,T4・≤2 |
| F-23 | m3 Q13 Q20 | WARN | POS 4種 | T1,T4・≤2 |
| F-24 | m4 Q12 Q18 | ERROR | spentだけword | T1,T5・同一種別 |
| F-25 | m4 S05 | ERROR | 熟語末尾非連続 | T5・Q15〜20 |
| F-26 | m4 V10 | ERROR | particle 0/23 | T1,T5・≥6/24 |
| F-27 | m4 Q04 Q13 | WARN | stem 12語 | T1,T5・13〜45 |
| F-28 | m4 Q13 Q18 | WARN | POS 3種 | T1,T5・≤2 |
| F-29 | m4 Q13 Q19 | WARN | POS 3種 | T1,T5・≤2 |

## 停止・続行・ロールバック
- 停止: 第三者差分、T1で一意性未確定、監査CLI不能、共通契約/manifest/package変更が必要。再現しなければ `NOT_REPRODUCED` とし変更しない。
- 続行: 1セットが `NEEDS_CONTEXT` / `WAITING_FOR_EVIDENCE` でも承認済み独立セットは直列続行。
- 問題順変更は既存進捗のq対応へ影響しうる。datasetIdは維持し、親Agentが互換性を確認。保てなければversion仕様判断まで停止。
- ロールバックはタスクのbuilder/checker/生成JSONだけをタスク開始時へ戻す。他のdirty差分を戻さない。commit/push/deployなし。

## yuna起動プロンプト（親Agent用）
`docs/plans/2026-09-09-eiken2-structure-fixes.md` を唯一の計画として `SERIAL_ONLY` / `YUNA-A` でT1から実行する。開始時にstatusと全write_setのdiffを確認し、既存差分をrevertしない。T1は書込なしでセット別に内容と一意性を確定し、承認できたセットだけ実装する。JSONはbuilderから再生成し各Gate A/B後にT6を行う。共有契約・対象外差分・監査CLI変更はPAUSED。返却: Worker / Task / Kind / Status / Changed files / Verification / First unfinished task / Integration handoff。commit/push/deploy禁止。

## セルフレビュー
- [x] 29件全てをF-ID化し、公式5件は理由付き対象外、自作24件はタスクへ対応。
- [x] 全タスクに種別、owner、parallel_group、depends_on、write/read set、conflicts、integration_owner、変更後、Gate、期待、受入、コミット、未達時を記載。
- [x] T1を先行VERIFY_ONLYとし、生成物直接編集、依存追加、UI/公式/公開変更を禁止。
- [x] Gate A/B/Cと各IMPLEMENTの最小Gate Bを分離。
- [x] dirty/共有検証を考慮し `SERIAL_ONLY`。状態は `READY`。
