"use strict";

const assert = require("node:assert/strict");
const { compatibleSense } = require("./lib/context-validator.cjs");
const { sourceItems, pipelinePaths, readJson, vocabularyByTarget } = require("./lib/context-pipeline.cjs");
const {
  candidateSensesFromMeaning,
  filterEligibleSenses,
  validateTargetSense,
} = require("./lib/context-sense-validator.cjs");

const vocabulary = vocabularyByTarget();
const q67Candidates = readJson(pipelinePaths([6, 7]).candidate).items;

function source(target) {
  return sourceItems([6, 7]).find((item) => item.target === target) || (() => {
    const item = vocabulary.get(target);
    return { q: item.q, target, meaning: item.meaning, pos: ({ "名詞": "noun", "動詞": "verb", "形容詞": "adjective", "副詞": "adverb" })[item.pos] || item.pos, level: "EIKEN Grade 2" };
  })();
}

function senses(items) {
  return items.map((item) => `${item.sense}|${item.pos}`);
}

function assertFilter(target, candidate, expectedEligible, expectedFiltered) {
  const result = filterEligibleSenses(candidate, source(target).pos);
  assert.deepEqual(senses(result.eligibleSenses), senses(expectedEligible), `${target}: eligible senses changed`);
  assert.deepEqual(result.filteredOutSenses.map((item) => ({ sense: item.sense, pos: item.pos, reason: item.reason })), expectedFiltered,
    `${target}: filtered senses changed`);
}

assertFilter("chemical", candidateSensesFromMeaning(vocabulary.get("chemical").meaning, "adjective"),
  [{ sense: "化学の", pos: "adjective" }],
  [{ sense: "化学物質", pos: "noun", reason: "source-pos-mismatch" }]);
assertFilter("tap", candidateSensesFromMeaning(vocabulary.get("tap").meaning, "verb"),
  [{ sense: "（指などで）軽くたたく", pos: "verb" }],
  [{ sense: "蛇口", pos: "noun", reason: "source-pos-mismatch" }]);
assertFilter("occur", candidateSensesFromMeaning(vocabulary.get("occur").meaning, "verb"),
  [{ sense: "起こる、生じる", pos: "verb" }, { sense: "（心に）浮かぶ", pos: "verb" }], []);

const content = vocabulary.get("content");
const contentFilter = filterEligibleSenses(candidateSensesFromMeaning(content.meaning, "noun"), "noun");
assert.deepEqual(senses(contentFilter.eligibleSenses), ["中身、内容|noun"]);
assert.deepEqual(contentFilter.filteredOutSenses.map((item) => item.sense), ["満足して"]);

for (const target of ["chemical", "tap", "occur"]) {
  const item = { ...source(target), ...q67Candidates[target].final };
  const filtered = filterEligibleSenses(item.candidateSenses, item.pos);
  item.eligibleSenses = filtered.eligibleSenses;
  item.filteredOutSenses = filtered.filteredOutSenses;
  assert.equal(validateTargetSense(item, vocabulary.get(target), { requireEligibleSenses: true }).status, "pass", `${target}: valid pre-filter item failed`);
}

function expectFail(label, mutate) {
  const target = "chemical";
  const item = { ...source(target), ...q67Candidates[target].final };
  const filtered = filterEligibleSenses(item.candidateSenses, item.pos);
  item.eligibleSenses = filtered.eligibleSenses;
  item.filteredOutSenses = filtered.filteredOutSenses;
  mutate(item);
  const result = validateTargetSense(item, vocabulary.get(target), { requireEligibleSenses: true });
  assert.equal(result.status, "fail", `${label}: invalid pre-filter item was accepted`);
}

expectFail("eligible-missing", (item) => { delete item.eligibleSenses; });
expectFail("eligible-empty", (item) => { item.eligibleSenses = []; });
expectFail("eligible-outside-candidate", (item) => { item.eligibleSenses = [{ sense: "別の意味", pos: "adjective" }]; });
expectFail("eligible-pos-incompatible", (item) => { item.eligibleSenses = [{ sense: "化学物質", pos: "noun" }]; });
expectFail("filtered-remains-eligible", (item) => { item.eligibleSenses.push({ sense: "化学物質", pos: "noun" }); });
expectFail("filtered-target", (item) => { item.targetSense = "化学物質"; });
expectFail("target-outside-eligible", (item) => { item.targetSense = "化学物質"; });
expectFail("wrong-filtered-reason", (item) => { item.filteredOutSenses[0].reason = "manual-choice"; });
expectFail("all-candidates-filtered", (item) => { item.eligibleSenses = []; });

for (const [target, expected] of Object.entries({
  branch: "枝",
  scale: "はかり",
  balance: "均衡、バランス",
  foster: "育む、促進する",
  hate: "ひどく嫌う",
  divide: "分ける、分割する",
  pronounce: "発音する",
})) {
  const item = vocabulary.get(target);
  const sourcePos = ({ "名詞": "noun", "動詞": "verb", "形容詞": "adjective", "副詞": "adverb" })[item.pos] || item.pos;
  const result = filterEligibleSenses(candidateSensesFromMeaning(item.meaning, sourcePos), sourcePos);
  assert.ok(result.eligibleSenses.some((candidate) => compatibleSense(candidate.sense, expected)), `${target}: positive sense was filtered out`);
}

console.log("POS-aware sense pre-filter: OK (chemical/tap/occur, Phase 6 fixtures, negative guards)");
