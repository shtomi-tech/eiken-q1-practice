const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const source = fs.readFileSync("static/mode-q1.js", "utf8").replace(
  "return { mount, handleKey };",
  "return { mount, handleKey, __test: { medianMs, rtGrade, meaningResultState, nextAverageMs } };",
);
const sandbox = {};
vm.runInNewContext(`${source}\nglobalThis.app = EikenQ1App;`, sandbox);

const { medianMs, rtGrade, meaningResultState, nextAverageMs } = sandbox.app.__test;

assert.equal(rtGrade(7999, 8000), "good");
assert.equal(rtGrade(8000, 8000), "good");
assert.equal(rtGrade(20000, 8000), "hard");
assert.equal(rtGrade(16001, 10000), "hard");
assert.equal(rtGrade(undefined, 8000), "good");
assert.equal(medianMs([1000, 2000, 3000, 4000]), 8000);
assert.equal(medianMs([5000, 1000, 3000, 2000, 4000]), 3000);
assert.equal(medianMs([60000, 1000, 2000, 3000, 4000]), 8000);
function assertState(actual, intervalDays, nextStage) {
  assert.equal(actual.intervalDays, intervalDays);
  assert.equal(actual.nextStage, nextStage);
}
assertState(meaningResultState(0, 0, true, "good"), 1, 1);
assertState(meaningResultState(1, 0, true, "hard"), 3, 1);
assertState(meaningResultState(2, 5, true, "good"), 3, 1);
assertState(meaningResultState(1, 0, false, "good"), null, 0);
assert.equal(nextAverageMs(undefined, 4100), 4100);
assert.equal(nextAverageMs(7000, 4000), 6100);

// 誤答で lastMs を更新すると、weightedOrder で wrongCount と二重に重み付けされる。
const record = source.slice(source.indexOf("function recordMeaningResult("));
const correctBranch = record.slice(record.indexOf("if (isCorrect) {"), record.indexOf("} else {"));
assert.ok(/s\.lastMs = ms;/.test(correctBranch), "lastMs は正答ブランチで更新すること");
assert.equal((record.match(/s\.lastMs = ms;/g) || []).length, 1, "lastMs の更新は正答時の1箇所だけ");

// avgMs は結果表示の読み手があって初めて意味を持つ。書き込み専用にしない。
assert.ok(source.includes("前回までの平均"), "解答直後に前回までの平均を表示すること");

console.log("response-time SRS contract: OK");
