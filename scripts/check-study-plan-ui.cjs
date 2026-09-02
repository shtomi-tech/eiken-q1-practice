const assert = require("node:assert/strict");
const { appCss, appJs, extractFunctionBody } = require("./lib/app-source.cjs");

const js = appJs();
const css = appCss();


const home = extractFunctionBody(js, "renderHomeContent");
const studyPanel = extractFunctionBody(js, "studyPlanPanel");
const vocabGoal = extractFunctionBody(js, "vocabGoalCard");
const cloudMeta = extractFunctionBody(js, "cloudMeta");

assert.match(home, /currentGrade\(\) === "eiken1"/);
assert.ok(home.includes("const studyPlanNode = isStudyPlanGrade ? studyPlanPanel(studyPlanEntries) : null;"), "1級の統合目標カードへ学習目標パネルを渡す");
assert.ok(!home.includes("summary.appendChild(studyPlanPanel"), "学習目標パネルを今日の学習カードへ重複配置しない");
assert.ok(home.includes("home.appendChild(goalCard)"), "語彙目標カードはホーム直下に置く");
assert.match(studyPanel, /studyPlanSummary\(/);
assert.match(home, /vocabGoalCard\(/);
assert.ok(vocabGoal.includes("studyPlanNode"), "統合目標カードへ学習目標パネルを含める");

for (const text of ["学習目標", "今日", "今日の目標達成"]) {
  assert.ok(studyPanel.includes(text), `ホームに ${text} の表示契約が必要`);
}
assert.ok(!studyPanel.includes("総問題目標"), "総問題目標は設定UIから外す");
assert.ok(!studyPanel.includes("総目標"), "総目標の表示を学習目標パネルから外す");
assert.ok(!studyPanel.includes("goalInput"), "総問題目標の入力欄を学習目標パネルから外す");
assert.ok(!studyPanel.includes("studyPlanMore"), "週次進捗の折りたたみ表示を学習目標パネルから外す");
assert.ok(!studyPanel.includes("今週の進捗"), "週次進捗の表示を学習目標パネルから外す");

// 常時表示は「今日」1つ。週開始曜日は設定フォームに残すが、週次進捗は表示しない。
{
  const todayIdx = studyPanel.indexOf('studyPlanProgress(\n      "今日"');
  assert.ok(todayIdx !== -1, "「今日」の studyPlanProgress ラベルが特定できない");
}

for (const text of ["studyPlanSettings", "1日の問題目標", "週の開始曜日", "保存", "キャンセル", "aria-expanded", "aria-controls"]) {
  assert.ok(studyPanel.includes(text), `設定UIに ${text} が必要`);
}
assert.ok(!studyPanel.includes("総問題目標"), "設定UIに総問題目標を残さない");
assert.match(studyPanel, /type: "number"/);
assert.match(studyPanel, /type: "submit"/);
assert.match(studyPanel, /weekStartsOn/);
assert.match(studyPanel, /function restoreSettingsForm\(\)/, "キャンセル時に設定フォームを復元する");
assert.match(studyPanel, /dailyInput\.value = String\(plan\.dailyQuestionGoal\)/, "日別目標を保存済み値へ戻す");
assert.match(studyPanel, /weekSelect\.value = String\(plan\.weekStartsOn\)/, "週開始曜日を保存済み値へ戻す");
assert.match(studyPanel, /settingsToggle\.focus\(\)/, "キャンセル後に設定トグルへフォーカスを戻す");
assert.match(studyPanel, /dailyInput\.focus\(\)/, "設定を開いたときに日別目標へフォーカスを置く");

for (const text of ["vocabularyForecast", "vocabularyGoalForecast", "理論上の学習量", "現在、このアプリの英検1級通常問題には", "14,000語まであと"]) {
  assert.ok(vocabGoal.includes(text) || js.includes(text), `語彙予測に ${text} が必要`);
}
assert.match(vocabGoal, /7日|1週間後/);
assert.match(vocabGoal, /30日|1か月後/);
assert.match(vocabGoal, /estimatedDate/);

assert.ok(cloudMeta.includes("studyPlanV1"), "cloudMetaへ学習計画を含める");
assert.match(js, /scopedStorageKey\(STUDY_PLAN_KEY\)/, "学習計画は生徒スコープ付きlocalStorageへ保存する");
assert.match(js, /cloud\.queueSave\(\{[\s\S]*cloudMeta\(\)/, "設定変更時に現在セットとcloudMetaを同期する");

for (const cls of [
  ".studyPlanPanel",
  ".studyPlanMetrics",
  ".studyPlanMetric",
  ".studyPlanSettings",
  ".studyPlanFields",
  ".vocabGoalCard > .studyPlanPanel",
  ".vocabForecast",
  ".vocabForecastGrid",
]) {
  assert.ok(css.includes(cls), `CSSに ${cls} の規則が必要`);
}
assert.ok(!css.includes(".studyPlanMore"), "CSSに削除済みの週次進捗ブロックを残さない");
assert.match(css, /@media \(max-width: 320px\)/);
assert.match(css, /prefers-reduced-motion: reduce/);

console.log("study plan UI contract: OK");
