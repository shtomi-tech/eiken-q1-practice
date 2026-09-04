# 学習目標・語彙目標の全級展開 実装計画（計画B）

状態: 完了（2026-09-04）

## 1. 目的

1級だけに出している「日次・週次の学習目標カード」を英検5級〜1級の全5区分へ広げ、
語彙目標カードが出ていない5級にも目標を用意する。データは変更せず、
`static/src/*.js` の級ハードコードを外す作業だけで完結させる。

方針決定（2026-09-04・ユーザー確認済み）:

- 学習目標カードの対象は **英検5級・準2級・2級・準1級・1級の5区分**。
  医療福祉（`iuhw`）は英検の級ではないため対象外にする。
- 語彙目標は **5級に `0 → 600語` を追加**する。医療福祉には語彙目標カードを出さない（現状維持）。

## 2. 固定する互換性

- localStorageキー `eiken_q1_study_plan_v1`（および生徒別スコープ版）の**名前と中身を変えない**。
  これは今後も1級の目標レコードとして使い、既存の1級ユーザーの設定・実績をそのまま維持する。
- クラウド同期フィールド `_meta.studyPlanV1` の意味を変えない（1級の目標）。
- 進捗キー `eiken_q1_progress_<datasetId>`、`itemKey`、`migrations.studyPlanFirstAnsweredAtV1`、
  アプリIDを変更しない。
- 語彙目標の既存4級（準2級3,000／2級5,000／準1級9,000／1級14,000）の値と、
  「前級のtarget＝次級のprev」という連鎖を崩さない。
- `data/` 配下と `static/mode-q1.js`（生成物）を直接編集しない。

## 3. 現状の級ハードコード（実測）

| 箇所 | 内容 |
| --- | --- |
| `static/src/80-home.js:180` | `const isStudyPlanGrade = currentGrade() === "eiken1";` |
| `static/src/80-home.js:181,300-303` | 学習目標カードと学習済み語彙数の算出を1級だけ別経路にしている |
| `static/src/80-home.js:535` | 予測パネルの表示条件が `currentGrade() === "eiken1"` |
| `static/src/80-home.js:171,393` | `loadStudyPlan()` の呼び出しが `"eiken1"` / `"1"` 条件付き |
| `static/src/99-boot.js:71-73` | 起動時のプール読み込みと `loadStudyPlan()` が1級のみ |
| `static/src/20-storage.js:85` | `studyPlanQuestionLimit()` が `gradeQuestionEntries("eiken1")` 固定 |
| `static/src/20-storage.js:196` | `migrateStudyPlanFirstAnswers()` が `studyPlanDatasetIds("eiken1")` 固定 |
| `static/src/20-storage.js:170,181` | 目標レコードの保存先が単一キー |
| `static/src/10-config.js:36-37` | `STUDY_PLAN_TARGET_VOCABULARY = 14000` / `BASE_VOCABULARY = 9000` が1級固定 |
| `static/src/10-config.js:45-50` | `VOCAB_GOALS` に `eiken5` が無い |
| `static/src/80-home.js:546` | 予測文の「14,000語」が直書き |
| `static/src/80-home.js:541` | 読み込み中の文言が「英検1級通常問題の語句を読み込み中…」 |

## 4. 実装方針

### 段階B0: ベースラインを固定する

1. `git status --short` で既存変更がないことを確認する。
2. `npm test` の成功と `npm run build --check` 相当（`node scripts/build-mode-q1.cjs --check`）を確認する。
3. 1級の既存 `eiken_q1_study_plan_v1` を持つブラウザプロファイルで、現在の
   日次実績・目標値・週開始曜日を控える（段階B4の回帰確認に使う）。

### 段階B1: 級ごとの目標レコードに分ける

対象: `static/src/10-config.js` / `static/src/20-storage.js`

1. 対象級の定数を1か所に置く。

```js
// 日次・週次の学習目標を出す級。医療福祉は英検の級ではないため含めない。
const STUDY_PLAN_GRADES = ["eiken5", "eikenp2", "eiken2", "eikenp1", "eiken1"];
```

2. 保存キーは1級だけ従来のまま、他級は接尾辞を足す。

```js
function studyPlanStorageKey(grade) {
  return scopedStorageKey(grade === "eiken1" ? STUDY_PLAN_KEY : `${STUDY_PLAN_KEY}_${grade}`);
}
```

`const STUDY_PLAN_KEY = "eiken_q1_study_plan_v1";` の定義行は
`scripts/check-study-plan.cjs` が正規表現で検査しているため、文字列も行の形も変えない。

3. `let studyPlan = null;` を級→計画のマップへ変え、参照箇所は現在級の計画を返す
   アクセサ経由にする。

```js
let studyPlans = {};                       // { [grade]: plan }
function currentStudyPlan() {
  const grade = currentGrade();
  return studyPlans[grade] || (isStudyPlanGrade(grade) ? defaultStudyPlan(grade) : null);
}
```

4. 級引数を通す。既定値は現在級にし、`"eiken1"` の直書きを消す。

- `studyPlanQuestionLimit(grade = currentGrade())`
- `defaultStudyPlan(grade = currentGrade())`
- `loadStudyPlan(grade = currentGrade())` / `saveStudyPlan(grade = currentGrade())`
- `migrateStudyPlanFirstAnswers()` は `STUDY_PLAN_GRADES` すべてを走査する

5. 変更後の参照箇所（既存6か所）:
   `20-storage.js:180,181,190,192` / `50-vocab-pool.js:185,187` /
   `80-home.js:34,101,106,544,545`。

受入条件:

- 1級の既存レコードが `eiken_q1_study_plan_v1` から読み書きされ続ける。
- 他級で目標を変更しても1級のレコードが書き換わらない（キーが別）。
- `questionGoal` の上限が級ごとの問題数（5級15／準2級105／2級51／準1級54／1級291）で
  クランプされる。

### 段階B2: クラウド同期を級別に拡張する

対象: `static/src/40-cloud.js` / `static/src/50-vocab-pool.js`

1. `cloudMeta()` は `studyPlanV1`（1級）をそのまま送り続け、他級を別フィールドで足す。

```js
function cloudMeta() {
  const byGrade = { ...studyPlans };
  delete byGrade.eiken1;
  return {
    lastDatasetId: state.datasetId,
    ...(studyPlans.eiken1 ? { studyPlanV1: studyPlans.eiken1 } : {}),
    ...(Object.keys(byGrade).length ? { studyPlanByGradeV1: byGrade } : {}),
  };
}
```

2. 受信側（`50-vocab-pool.js:180-187`）は `studyPlanV1` を1級として、
   `studyPlanByGradeV1` を他級として取り込む。既存の `_meta` マージ方式は変えない。

受入条件:

- 既存のクラウド進捗（`studyPlanV1` のみを持つレコード）を読み込んでも例外が出ず、
  1級の目標が復元される。
- `scripts/check-cloud-progress-namespace.cjs` と `check-student-storage-scope.cjs` が通る。

### 段階B3: 5級の語彙目標と予測の級対応

対象: `static/src/10-config.js` / `static/src/80-home.js`

1. `VOCAB_GOALS` へ5級を追加する。

```js
const VOCAB_GOALS = {
  // 5級は前級を持たない起点。連鎖（前級target＝次級prev）には含めない。
  eiken5: { prev: 0, target: 600, prevLabel: "" },
  eikenp2: { prev: 1500, target: 3000, prevLabel: "3級" },
  ...
};
```

2. `prev === 0` のとき、目盛り（`vgTick`）と `aria-valuetext` の「前級までのn語」を出さない
   分岐を入れる（5級で「0語 / ラベル空」の目盛りが出るのを防ぐ）。
3. `STUDY_PLAN_TARGET_VOCABULARY` / `STUDY_PLAN_BASE_VOCABULARY` の直参照をやめ、
   `vocabularyGoalForecast(now, plan, learned, goal)` へ級の `VOCAB_GOALS` を渡す。
   引数省略時は従来値（9,000→14,000）を既定にし、`scripts/check-study-plan.cjs` の
   既存アサーションを壊さない。
4. 予測パネルの表示条件を `currentGrade() === "eiken1"` から
   「`VOCAB_GOALS` と学習目標を持つ級」へ変える。文中の「14,000語」を `goal.target`、
   「英検1級通常問題の語句を読み込み中…」を級ラベル由来の文言にする。

受入条件:

- 5級で語彙目標カードが「0 → 600語」で表示され、目盛りが破綻しない。
- 準2級〜1級の表示数値・文言が変わらない。
- 医療福祉では従来どおり語彙目標カードも学習目標カードも出ない。

### 段階B4: ホームと起動の級判定を差し替える

対象: `static/src/80-home.js` / `static/src/99-boot.js`

1. `isStudyPlanGrade` を `STUDY_PLAN_GRADES.includes(currentGrade())` に変える。
2. `studyPlanEntries` / `learnedVocabulary` / `studyPlanNode` の算出を現在級で行う。
3. `loadStudyPlan()` の呼び出し条件（`80-home.js:171,393`、`99-boot.js:71-73`）を
   対象級すべてへ広げる。プール読み込み（`loadPooledItems`）も同様に現在級で行う。

**要確認事項**: 他級の語彙目標カードの分子が `meaningSummary.learned` から
`learnedVocabularyCount(grade)` に変わる。コード上は同じ母集団（`80-home.js:492` のコメント）
だが、実データで一致することを1級以外の1級区分（準2級など）で確認してから確定する。
一致しない場合は、学習目標カードの有無にかかわらず従来の `meaningSummary.learned` を使う。

受入条件:

- 5級・準2級・2級・準1級で学習目標カードが表示され、日次「今日 n / m問」が動く。
- 1級の表示・数値が変更前と一致する。
- 級を切り替えても、直前の級の目標値が新しい級のレコードへ書き込まれない。

### 段階B5: 検査と文書を更新する

対象: `scripts/check-study-plan-ui.cjs` / `scripts/check-vocab-goal-ui.cjs` /
`scripts/check-study-plan.cjs` / `README.md` / `DESIGN.md`

1. `check-study-plan-ui.cjs:13` の `assert.match(home, /currentGrade\(\) === "eiken1"/)` を、
   新しい級判定（`STUDY_PLAN_GRADES`）を検査する形へ置き換える。
2. `check-vocab-goal-ui.cjs` は連鎖検査の `order` を現状のまま
   （`eikenp2 → eiken2 → eikenp1 → eiken1`）に保ち、**5級は連鎖の外**として
   `prev < target` と `prevLabel` の扱いだけを個別に検査する。
3. `check-study-plan.cjs` へ、級別キーとクラウド `studyPlanByGradeV1` のアサーションを足す。
   `STUDY_PLAN_KEY` の定義行アサーションは残す。
4. `README.md` の「1級の日次・週次学習目標」節を全級向けに書き直し、対象級・保存キー・
   クラウドフィールドを実装と一致させる。`DESIGN.md` のホーム構成の記述も更新する。
5. `static/src/*.js` を変更したので `npm run build` で `static/mode-q1.js` を再生成し、
   `index.html` のキャッシュバスターを更新する。

受入条件:

- `npm test` の全チェックが成功する。
- READMEとDESIGNの記述が実装と一致する。

## 5. 検証

### 機械検査

```powershell
npm run build
npm test
```

### 実ブラウザ（最小限）

`py -3 -m http.server 8061 --bind 127.0.0.1` で起動し、`?g=5` と `?g=1` の2つを確認する。

- 5級: 学習目標カードと語彙目標カード（0→600語）が表示され、設定変更が保存される
- 1級: 既存の目標値・日次実績・予測が変更前と一致する（段階B0で控えた値と照合）
- 級を切り替えたときに互いの目標値が混ざらない
- コンソールエラーなし

級の切り替え・数値の細かい確認はユーザー側で実施する前提とし、こちらでは上記のみ行う。

### 差分検査

- `git diff -- data/` が空である（Bはデータを変更しない）。
- `static/mode-q1.js` の差分が `static/src/*.js` の結合結果と一致する
  （`node scripts/build-mode-q1.cjs --check`）。

## 6. コミット境界

1. 級別の目標レコード（`10-config.js` / `20-storage.js`）
2. クラウド同期の級別拡張（`40-cloud.js` / `50-vocab-pool.js`）
3. 5級の語彙目標と予測の級対応
4. ホーム・起動の級判定差し替え
5. 検査・README・DESIGN・ビルド生成物

push・デプロイは別途依頼された場合だけ行う。

## 7. 完了条件

- 英検5級〜1級の5区分で学習目標カードが表示され、級ごとに独立した目標値を保存できる。
- 5級に語彙目標カード（0→600語）が表示され、既存4級の表示が変わらない。
- 1級の既存ローカル・クラウド目標レコードが失われず、表示も変更前と一致する。
- 医療福祉の表示が変わらない。
- `npm test` と実ブラウザ2画面の確認が成功する。

## 8. 実施記録（2026-09-04）

### 要確認事項の結論

計画で保留していた「他級の語彙目標カードの分子が `meaningSummary.learned` から
`learnedVocabularyCount(grade)` に変わる」点は、**実データで完全に一致する**ことを確認した。
そのため級ごとの分岐を残さず、対象5級すべてを `learnedVocabularyCount(grade)` に統一した。

- `learned` / `attempts` / `firstAnsweredAt` は `90-learn-flow.js:1026-1028` の1か所でのみ
  同時に設定される。したがって `answeredQuestionEntries()` の判定（firstAnsweredAt or
  attempts>0 or learned）と `learned === true` は、このアプリが作るデータでは一致する。
- `learnedVocabularyCount` は `datasetId:itemKey` で重複排除し、`learnedPooledItems` は
  重複排除しない。全 `data/vocab_*.json` を走査して、1セット内の `itemKey` 重複が
  **0件**であることを確認した（5級60件も全ユニーク）。

### 追加した保護

`loadStudyPlan()` の上限計算に、保存済みの `questionGoal` / `dailyQuestionGoal` を下限として
加えた。語彙プールの読み込みに失敗すると問題数を1件しか数えられず、利用者の保存済み目標を
1問へ切り下げて上書きする経路が既存コードにもあったため、対象級が5つに増える前に塞いだ。

### 実ブラウザ確認

- 5級: 学習目標カード（今日 0/8問）と語彙目標カード（0語/600語）が表示され、
  前級を持たないため中間目盛りが出ない。予測は「600語まであと600語」。
- 1級: 9,000語/14,000語、目盛り 0／9,000（準1級）／14,000（1級）、
  「14,000語まであと5,000語」で変更前と一致。
- 級別キーの分離: 5級で1日3問・週開始日曜へ変更すると
  `eiken_q1_study_plan_v1_eiken5`（questionGoal 15）だけが書かれ、1級で1日12問へ変更すると
  `eiken_q1_study_plan_v1`（questionGoal 291）だけが書かれた。5級へ戻ると「今日 0 / 3問」で
  復元され、互いの設定が混ざらないことを確認した。
- 医療福祉: 学習目標カード・語彙目標カードとも非表示のまま。
- コンソールエラーなし。確認用に作成したlocalStorageは削除済み。

## 9. 計画Aとの関係

AとBは対象が独立している（Aはデータと検査、Bは `static/src` のみ）。並行して進められるが、
Bは `static/mode-q1.js` を再生成するため、コミットは混ぜない。
