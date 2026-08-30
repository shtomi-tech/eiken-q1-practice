const assert = require("node:assert/strict");
const { appJs } = require("./lib/app-source.cjs");

const source = appJs();

const matches = source.match(/const APP_ID = "([^"]*)";/g) || [];
assert.equal(matches.length, 1, `expected exactly 1 APP_ID declaration, found ${matches.length}`);
assert.equal(matches[0], 'const APP_ID = "eiken2-q1";', `unexpected APP_ID declaration: ${matches[0]}`);
assert.ok(
  !source.includes('const APP_ID = "eiken-q1-practice";'),
  "APP_ID must not point at the old eiken-q1-practice namespace",
);
assert.ok(
  source.includes("eiken_q1_student_"),
  "student-scoped localStorage prefix eiken_q1_student_ must remain",
);
assert.match(source, /function cloudMeta\(\)/, "cloudMeta() を一箇所へまとめる必要があります");
assert.match(source, /studyPlanV1/, "cloudMetaへstudyPlanV1を含める必要があります");
assert.match(source, /map\._meta = cloudMeta\(\)/, "フル保存payloadにもcloudMetaを含める必要があります");
assert.match(source, /meta: cloudMeta\(\)/, "パッチ保存にもcloudMetaを含める必要があります");
assert.match(source, /pendingCloudStudyPlan/, "クラウドから来た学習計画を検証前に捨てない必要があります");
console.log("cloud progress namespace: OK");
