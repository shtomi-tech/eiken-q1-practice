# 日次・週次学習目標 実装レビュー指摘の修正計画

> 対象: `static/mode-q1.js` / `scripts/check-study-plan.cjs` / `scripts/check-study-plan-ui.cjs` / `README.md`
> 状態: 計画（未着手）
> 作成日: 2026-08-25
> 前提: `docs/DAILY_WEEKLY_STUDY_GOAL_PLAN.md` に基づく実装へのレビュー指摘3件だけを修正する。

## 1. 目的

実装レビューで再現した次の不整合を、既存の学習進捗・クラウド同期・UI構造を変えずに修正する。

1. 総問題目標より日別目標が大きいと、週間集計だけ日別目標が縮められる
2. 設定フォームで「キャンセル」しても未保存の入力値が残る
3. READMEの語句換算説明が「1日4語句」になっている

対象外のリファクタリング、保存形式変更、データ変更、デプロイは混ぜない。

## 2. 現状と再現条件

### 2.1 日別目標と週間目標の不一致

`studyPlanSummary()` は次のように、`questionGoal` を `normalizeStudyPlan()` の上限へ渡している。

```js
const safe = normalizeStudyPlan(plan, Math.max(1, Number(plan?.questionGoal) || 1));
```

設定フォーム自体は総問題目標と日別目標を、それぞれ1〜収録問題数で独立して許可する。このため、次の有効な設定で表示が矛盾する。

```text
questionGoal = 5
dailyQuestionGoal = 8

日別表示: 8問
週間集計内部: 5問 × 7 = 35問
7日後の語句予測: 8問 × 4語句 × 7日 = 224語句
```

総目標、日別目標、語句予測は独立した利用者設定であり、総問題目標を日別目標の上限として扱わない。

### 2.2 キャンセル後に入力値が残る

`studyPlanPanel()` のキャンセル処理はフォームを隠し、エラー文を消すだけである。入力値を8から10へ変えてキャンセルした後、再度開くと10のまま残る。保存済み設定は8のため、画面内に未保存値だけが残る状態になる。

また、フォームを隠した後にフォーカスが設定トグルへ戻らず、実ブラウザでは `body` へ移った。キーボード利用者が操作位置を見失う。

### 2.3 READMEの換算単位

実装は `1問 = 4語句` で予測するが、READMEは「日別目標を1日4語句として」と説明している。「1問4語句として」が正しい。

## 3. 修正方針

### 3.1 集計時に2つの目標を独立して保持する

`studyPlanSummary()` 内で正規化に使う上限を、`questionGoal` だけから決めない。少なくとも両設定値を保持できる上限にする。

```js
const planLimit = Math.max(
  1,
  Number(plan?.questionGoal) || 1,
  Number(plan?.dailyQuestionGoal) || 1,
);
const safe = normalizeStudyPlan(plan, planLimit);
```

- 保存時の正規化は従来どおり、実際の収録問題数 `studyPlanQuestionLimit()` を上限にする。
- 集計関数は保存済みの正規化済み設定を再解釈するだけとし、日別目標を総目標へ合わせて縮めない。
- `weeklyGoal = dailyQuestionGoal × 7` と語句予測が、常に同じ日別目標を使うことをテストする。

### 3.2 キャンセル時に保存済み値へ戻す

`studyPlanPanel()` 内に、フォーム値とエラーを現在の保存済み `plan` へ戻す小さい関数を置く。

```js
function restoreSettingsForm() {
  goalInput.value = String(plan.questionGoal);
  dailyInput.value = String(plan.dailyQuestionGoal);
  weekSelect.value = String(plan.weekStartsOn);
  error.textContent = "";
}
```

キャンセル時の順序は次とする。

1. 入力値とエラーを復元
2. フォームを閉じる
3. `aria-expanded="false"` を設定
4. `settingsToggle.focus()` で操作位置を戻す

設定トグルで開いたフォームを再び閉じる場合も、未保存値を破棄して同じ状態へ戻す。保存時のクラウド同期と再描画は変更しない。

### 3.3 READMEの文言だけを直す

```diff
- 日別目標を1日4語句として
+ 1問4語句として
```

他のREADME変更は混ぜない。

## 4. 回帰テスト

### 4.1 `scripts/check-study-plan.cjs`

次のケースを追加する。

```js
const plan = { version: 1, questionGoal: 5, dailyQuestionGoal: 8, weekStartsOn: 1 };
```

- `studyPlanSummary(...).dailyQuestionGoal === 8`
- `studyPlanSummary(...).weeklyGoal === 56`
- `vocabularyForecast(plan)[0].vocabulary === 224`
- 総問題残数は従来どおり5問を基準にする

これにより、総問題目標と日別目標を別々に変更できる契約を固定する。

### 4.2 `scripts/check-study-plan-ui.cjs`

最低限、キャンセル処理が次を含むことを契約として追加する。

- 総問題目標の復元
- 日別目標の復元
- 週開始曜日の復元
- 設定トグルへのフォーカス復帰

文字列契約だけで完了せず、実ブラウザでも確認する。

## 5. 検証

### 5.1 自動検証

```powershell
node scripts/check-study-plan.cjs
node scripts/check-study-plan-ui.cjs
npm test
py -3 scripts/check_q1_data.py
git diff --check
graft build
graft check
```

### 5.2 実ブラウザ

`?g=1` で英検1級ホームを開き、次を確認する。

1. 総目標5問・日別8問を保存すると、今日8問・今週56問・1週間後224語句になる
2. 入力値を変更してキャンセルすると、再表示時に保存済み値へ戻る
3. キャンセル後のフォーカスが「学習目標を設定」へ戻る
4. 保存した設定がリロード後も残る
5. 320 / 375 / 720 / 1280pxで横あふれがない
6. コンソールエラーがない

クラウド同期を確認する場合は、生徒別URLで別端末相当の再読込を行う。トークンや進捗JSON全体はログへ出さない。

## 6. 変更対象

| ファイル | 変更内容 |
| --- | --- |
| `static/mode-q1.js` | 集計上限の修正、キャンセル時の値・フォーカス復元 |
| `scripts/check-study-plan.cjs` | 総目標5・日別8の回帰テスト |
| `scripts/check-study-plan-ui.cjs` | キャンセル復元とフォーカス契約 |
| `README.md` | 「1問4語句」へ訂正 |

`DESIGN.md`、保存キー、`_meta.studyPlanV1`、Supabase RPC、問題・語彙データ、生成済みharnessは変更しない。

## 7. 実装順

1. 2つの回帰テストを追加し、現状で失敗することを確認する
2. `studyPlanSummary()` の独立した目標処理を修正する
3. キャンセル時の復元とフォーカス移動を実装する
4. READMEの換算単位を訂正する
5. 集中テスト、全テスト、データ検証を実行する
6. 実ブラウザで設定・キャンセル・主要幅を確認する
7. `graft build/check` でコードグラフを更新する

## 8. 完了条件

- 総目標より大きい日別目標でも、日別・週間・語句予測が矛盾しない
- キャンセルで未保存の3設定値が残らない
- キャンセル後にキーボードフォーカスが設定トグルへ戻る
- READMEが「1問4語句」と正しく説明する
- 既存の保存・クラウド同期・他級・復習動作に変更がない
- 全自動検証と実ブラウザ確認が通る

## 9. デプロイ境界

この計画作成では実装・コミット・push・デプロイを行わない。実装後にデプロイを依頼された場合は、今回の学習計画関連ファイルだけを選択してコミットし、GitHub Actions完了後に公開HTML・`static/mode-q1.js`・`static/styles.css`と公開ブラウザ表示を確認する。
