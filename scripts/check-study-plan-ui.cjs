const assert = require("node:assert/strict");
const { appCss, appJs, extractFunctionBody } = require("./lib/app-source.cjs");

const js = appJs();
const css = appCss();


const home = extractFunctionBody(js, "renderHomeContent");
const studyPanel = extractFunctionBody(js, "studyPlanPanel");
const vocabGoal = extractFunctionBody(js, "vocabGoalCard");
const cloudMeta = extractFunctionBody(js, "cloudMeta");

assert.match(home, /currentGrade\(\) === "eiken1"/);
assert.ok(home.includes("studyPlanPanel"), "1級の今日の学習カードに学習目標パネルを置く");
assert.ok(home.includes("home.appendChild(goalCard)"), "語彙目標カードはホーム直下に置く");
assert.match(studyPanel, /studyPlanSummary\(/);
assert.match(home, /vocabGoalCard\(/);

for (const text of ["学習目標", "回答済み", "今週", "新規", "総目標達成", "今日の目標達成", "今週の目標達成"]) {
  assert.ok(studyPanel.includes(text), `ホームに ${text} の表示契約が必要`);
}

// 常時表示は「今日」1つ。総目標・今週・再配分の目安は折りたたみ（studyPlanMore）へ。
{
  const moreIdx = studyPanel.indexOf('"studyPlanMore"');
  const todayIdx = studyPanel.indexOf('"今日"');
  const overallIdx = studyPanel.indexOf('"総目標"');
  assert.ok(moreIdx !== -1, "総目標・今週は折りたたみ（studyPlanMore）に入れる必要がある");
  assert.ok(todayIdx !== -1 && overallIdx !== -1, "今日/総目標の studyPlanProgress ラベルが特定できない");
  assert.ok(todayIdx < moreIdx, "「今日」は折りたたみの外（常時表示）に置く必要がある");
  assert.ok(overallIdx > moreIdx, "「総目標」は折りたたみ（studyPlanMore）の中に置く必要がある");
}
assert.ok(css.includes(".studyPlanMore"), "CSSに .studyPlanMore の規則が必要");

for (const text of ["studyPlanSettings", "総問題目標", "1日の問題目標", "週の開始曜日", "保存", "キャンセル", "aria-expanded", "aria-controls"]) {
  assert.ok(studyPanel.includes(text), `設定UIに ${text} が必要`);
}
assert.match(studyPanel, /type: "number"/);
assert.match(studyPanel, /type: "submit"/);
assert.match(studyPanel, /weekStartsOn/);
assert.match(studyPanel, /function restoreSettingsForm\(\)/, "キャンセル時に設定フォームを復元する");
assert.match(studyPanel, /goalInput\.value = String\(plan\.questionGoal\)/, "総問題目標を保存済み値へ戻す");
assert.match(studyPanel, /dailyInput\.value = String\(plan\.dailyQuestionGoal\)/, "日別目標を保存済み値へ戻す");
assert.match(studyPanel, /weekSelect\.value = String\(plan\.weekStartsOn\)/, "週開始曜日を保存済み値へ戻す");
assert.match(studyPanel, /settingsToggle\.focus\(\)/, "キャンセル後に設定トグルへフォーカスを戻す");

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
  ".vocabForecast",
  ".vocabForecastGrid",
]) {
  assert.ok(css.includes(cls), `CSSに ${cls} の規則が必要`);
}
assert.match(css, /@media \(max-width: 320px\)/);
assert.match(css, /prefers-reduced-motion: reduce/);

console.log("study plan UI contract: OK");
