const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const js = fs.readFileSync("static/mode-q1.js", "utf8");
const exposed = [
  "normalizeStudyPlan",
  "isValidIsoDate",
  "startOfLocalDay",
  "startOfWeek",
  "nextWeekStart",
  "answeredQuestionEntries",
  "studyPlanSummary",
  "vocabularyForecast",
  "vocabularyGoalForecast",
  "migrateFirstAnsweredAt",
];

assert.match(js, /const STUDY_PLAN_KEY = "eiken_q1_study_plan_v1";/);
assert.match(js, /function cloudMeta\(\)/);
assert.match(js, /studyPlanV1/);

const source = js.replace(
  "return { mount, handleKey };",
  `return { mount, handleKey, __test: { ${exposed.join(", ")} } };`,
);
const sandbox = {};
vm.runInNewContext(`${source}\nglobalThis.app = EikenQ1App;`, sandbox);
const plan = sandbox.app.__test;

const limit = 191;
const validPlan = { version: 1, questionGoal: 191, dailyQuestionGoal: 8, weekStartsOn: 1 };
const localDate = (year, month, day, hour = 12, minute = 0) => new Date(year, month - 1, day, hour, minute);
const iso = (date) => date.toISOString();

const normalizedInvalid = plan.normalizeStudyPlan(
  { questionGoal: 0, dailyQuestionGoal: 999, weekStartsOn: 8, futureFlag: true },
  limit,
);
assert.equal(normalizedInvalid.version, 1, "無効な設定値は既定値へ戻す");
assert.equal(normalizedInvalid.questionGoal, 191, "総問題目標の既定値");
assert.equal(normalizedInvalid.dailyQuestionGoal, 8, "日別問題目標の既定値");
assert.equal(normalizedInvalid.weekStartsOn, 1, "週開始曜日の既定値");
assert.equal(normalizedInvalid.futureFlag, true, "未知の項目は保持する");

const now = localDate(2026, 8, 25, 10);
const sameQuestion = { datasetId: "eiken1-2026-1", q: 1, unit: { learned: true, attempts: 1, firstAnsweredAt: iso(localDate(2026, 8, 25, 9)) } };
const duplicateQuestion = { datasetId: "eiken1-2026-1", q: 1, unit: { learned: true, attempts: 2, firstAnsweredAt: iso(localDate(2026, 8, 25, 9)) } };
const anotherRoundSameQ = { datasetId: "eiken1-2025-3", q: 1, unit: { learned: true, attempts: 1, firstAnsweredAt: iso(localDate(2026, 8, 24, 23, 30)) } };
const wrongAnswer = { datasetId: "eiken1-2026-1", q: 2, unit: { learned: true, attempts: 1, firstAnsweredAt: iso(localDate(2026, 8, 25, 23, 30)), answerResult: "incorrect" } };
const oldAnswer = { datasetId: "eiken1-2026-1", q: 3, unit: { learned: true, attempts: 1, firstAnsweredAt: iso(localDate(2026, 8, 18, 12)) } };

const answered = plan.answeredQuestionEntries([
  sameQuestion,
  duplicateQuestion,
  anotherRoundSameQ,
  wrongAnswer,
  oldAnswer,
  { datasetId: "eiken1-2026-1", q: 4, unit: { learned: false, attempts: 0 } },
]);
assert.equal(answered.length, 4, "同じセット・同じ設問だけを重複排除し、別セットの同じqは残す");

const summary = plan.studyPlanSummary(now, validPlan, answered);
assert.equal(summary.answeredToday, 2, "正誤を問わず初回答日で今日の件数へ入れる");
assert.equal(summary.answeredThisWeek, 3, "週の集計は初回答のローカル日付で行う");
assert.equal(summary.answeredOverall, 4);
assert.equal(summary.dailyRemaining, 6);
assert.equal(summary.weeklyGoal, 56);
assert.equal(summary.weeklyRemaining, 53);
assert.equal(summary.daysRemainingIncludingToday, 6);
assert.equal(summary.adjustedDailyTarget, 9);
assert.equal(summary.overallRemaining, 187);

const reallocationEntries = Array.from({ length: 18 }, (_, index) => ({
  datasetId: "eiken1-2026-1",
  q: index + 10,
  unit: { learned: true, attempts: 1, firstAnsweredAt: iso(localDate(2026, 8, 24, 9, index)) },
}));
const reallocation = plan.studyPlanSummary(localDate(2026, 8, 27, 10), validPlan, reallocationEntries);
assert.equal(reallocation.weeklyRemaining, 38);
assert.equal(reallocation.daysRemainingIncludingToday, 4);
assert.equal(reallocation.adjustedDailyTarget, 10, "残り38問・4日なら1日10問へ調整する");

const utcBoundary = { datasetId: "eiken1-2026-1", q: 5, unit: { learned: true, attempts: 1, firstAnsweredAt: iso(localDate(2026, 8, 25, 23, 59)) } };
assert.equal(
  plan.studyPlanSummary(localDate(2026, 8, 25, 23, 59), validPlan, [utcBoundary]).answeredToday,
  1,
  "ISO文字列をUTC日付として切り出さず、利用者のローカル日付で集計する",
);

const sundayPlan = { ...validPlan, weekStartsOn: 0 };
const sundaySummary = plan.studyPlanSummary(localDate(2026, 8, 29, 12), sundayPlan, [
  { datasetId: "eiken1-2026-1", q: 1, unit: { learned: true, attempts: 1, firstAnsweredAt: iso(localDate(2026, 8, 29, 8)) } },
]);
assert.equal(sundaySummary.daysRemainingIncludingToday, 1, "週開始曜日が日曜でも週最終日は残り1日とする");
assert.equal(plan.startOfWeek(localDate(2026, 8, 26), 2).getDay(), 2, "任意の週開始曜日を扱う");
assert.equal(plan.nextWeekStart(localDate(2026, 8, 26), 2).getDay(), 2);

assert.equal(
  JSON.stringify(plan.vocabularyForecast(validPlan)),
  JSON.stringify([
    { days: 7, vocabulary: 224 },
    { days: 30, vocabulary: 960 },
    { days: 90, vocabulary: 2880 },
    { days: 180, vocabulary: 5760 },
    { days: 365, vocabulary: 11680 },
  ]),
  "固定期間の理論上の語句数を日別目標と連動させる",
);

const goalForecast = plan.vocabularyGoalForecast(now, validPlan, 0);
assert.equal(goalForecast.currentVocabulary, 9000);
assert.equal(goalForecast.remainingVocabulary, 5000);
assert.equal(goalForecast.dailyVocabulary, 32);
assert.equal(goalForecast.daysToGoal, 157);
const expectedDate = new Date(now);
expectedDate.setHours(0, 0, 0, 0);
expectedDate.setDate(expectedDate.getDate() + 157);
assert.equal(goalForecast.estimatedDate.getTime(), expectedDate.getTime(), "到達日はローカル日付へ日数を加算する");

const changedPlan = { ...validPlan, dailyQuestionGoal: 5 };
assert.equal(plan.studyPlanSummary(now, changedPlan, []).weeklyGoal, 35);
assert.equal(plan.vocabularyForecast(changedPlan)[0].vocabulary, 140);
assert.equal(plan.vocabularyGoalForecast(now, changedPlan, 0).daysToGoal, 250);
assert.equal(plan.studyPlanSummary(now, { ...validPlan, questionGoal: 1 }, answered).overallRemaining, 0);

const independentGoalsPlan = { version: 1, questionGoal: 5, dailyQuestionGoal: 8, weekStartsOn: 1 };
const independentGoalsSummary = plan.studyPlanSummary(now, independentGoalsPlan, []);
assert.equal(independentGoalsSummary.dailyQuestionGoal, 8, "日別目標を総問題目標で縮めない");
assert.equal(independentGoalsSummary.weeklyGoal, 56, "週間目標は日別目標の7倍を使う");
assert.equal(independentGoalsSummary.overallRemaining, 5, "総問題残数は総問題目標を基準にする");
assert.equal(plan.vocabularyForecast(independentGoalsPlan)[0].vocabulary, 224, "語句予測は日別目標8問と連動する");

const legacy = {
  units: {
    1: { learned: true, attempts: 2 },
    2: { learned: true, attempts: 1, firstAnsweredAt: iso(localDate(2026, 8, 20)) },
    3: { learned: true, attempts: 1 },
  },
  history: [
    { kind: "meaning", q: 1, at: iso(localDate(2026, 8, 1)) },
    { kind: "question", q: 1, result: "wrong", at: iso(localDate(2026, 8, 3)) },
    { kind: "question", q: 1, result: "correct", at: iso(localDate(2026, 8, 4)) },
  ],
};
assert.equal(plan.migrateFirstAnsweredAt(legacy), true, "履歴から初回答時刻を補完する");
assert.equal(legacy.units[1].firstAnsweredAt, iso(localDate(2026, 8, 3)));
assert.equal(legacy.units[2].firstAnsweredAt, iso(localDate(2026, 8, 20)), "既存の初回答時刻を上書きしない");
assert.equal(legacy.units[3].firstAnsweredAt, undefined, "日時不明の旧回答へ推測日時を作らない");
assert.equal(legacy.migrations.studyPlanFirstAnsweredAtV1, 1);
assert.equal(plan.migrateFirstAnsweredAt(legacy), false, "移行は冪等にする");

console.log("study plan logic contract: OK");
