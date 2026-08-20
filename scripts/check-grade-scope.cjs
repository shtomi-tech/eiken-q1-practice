const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const js = fs.readFileSync("static/mode-q1.js", "utf8");
assert.match(js, /const GRADE_PREFIXES = \{/);
assert.match(js, /const GRADE_CHOICE_ORDER = \["pre2", "2", "pre1", "1"\]/);
assert.match(js, /function applyGradeScope\(/);
assert.match(js, /function resolveGradeCode\(/);
assert.match(js, /function renderGradeChoice\(/);

const source = js.replace(
  "return { mount, handleKey };",
  "return { mount, handleKey, __test: { applyGradeScope, resolveGradeCode, availableDatasets, defaultDatasetId, datasetGrades, otherGradeDueCounts, setManifest: (datasets, defaultId) => { ALL_DATASETS = datasets; DATASETS = datasets; DEFAULT_DATASET_ID = defaultId; }, setDataset: (id) => { state.datasetId = id; }, gradeStorageKey: () => scopedStorageKey(GRADE_KEY) } };",
);
const values = new Map();
const localStorage = {
  getItem: (key) => values.has(key) ? values.get(key) : null,
  setItem: (key, value) => values.set(key, String(value)),
  removeItem: (key) => values.delete(key),
};
const location = { search: "" };
const sandbox = {
  URLSearchParams,
  encodeURIComponent,
  localStorage,
  window: { location },
};
vm.runInNewContext(`${source}\nglobalThis.app = EikenQ1App;`, sandbox);
const scope = sandbox.app.__test;

const datasets = {
  "eiken2-2026-1": {},
  "eikenp2-2026-1": {},
  "eikenp1-2026-1": {},
  "eiken1-2026-1": {},
  "eikentopic-set-1": {},
};
scope.setManifest(datasets, "eiken2-2026-1");
const datasetIds = () => Array.from(scope.availableDatasets(), ([id]) => id);

values.set("grade", "1");
location.search = "?g=pre1";
assert.equal(scope.resolveGradeCode(), "pre1", "URLの級指定を優先する");
assert.equal(values.get(scope.gradeStorageKey()), "pre1", "URLの級指定を保存する");

location.search = "?g=unknown";
assert.equal(scope.resolveGradeCode(), "pre1", "未知のURL指定は保存済みの級へ戻る");
values.set("grade", "unknown");
location.search = "";
assert.equal(scope.resolveGradeCode(), "", "未知の保存値は無視する");

assert.equal(scope.applyGradeScope("pre1"), true);
assert.deepEqual(datasetIds(), ["eikenp1-2026-1"]);
assert.equal(scope.defaultDatasetId(), "eikenp1-2026-1");
assert.deepEqual(Array.from(scope.datasetGrades()), ["eikenp1"]);
scope.setDataset("eikenp1-2026-1");
assert.deepEqual(Array.from(scope.otherGradeDueCounts()), []);

assert.equal(scope.applyGradeScope("2"), true, "級変更時に元の全データから再絞り込みできる");
assert.deepEqual(datasetIds(), ["eiken2-2026-1"]);
const beforeInvalidScope = datasetIds();
assert.equal(scope.applyGradeScope("missing"), false);
assert.deepEqual(datasetIds(), beforeInvalidScope, "未知の級で現在の範囲を壊さない");

// 級を絞ってもクラウドへ送る進捗は manifest 全件から集める。
assert.match(
  js.slice(js.indexOf("function collectAllProgress("), js.indexOf("function collectAllProgress(") + 400),
  /Object\.keys\(ALL_DATASETS\)/,
  "collectAllProgress は絞り込み前の全セットを走査する",
);

const home = js.slice(js.indexOf("function renderHomeContent("), js.indexOf("/* ---- 問題一覧", js.indexOf("function renderHomeContent(")));
assert.match(home, /if \(needsGradeChoice\) \{[\s\S]*renderGradeChoice\(\);/);
assert.match(home, /setChromeTitle\("英検 大問1 単語アプリ"\)/);
assert.match(home, /級を変更/);
const picker = js.slice(js.indexOf("function datasetPicker("), js.indexOf("function answerActions", js.indexOf("function datasetPicker(")));
assert.match(picker, /grades\.length > 1/);

console.log("grade scope contract: OK");
