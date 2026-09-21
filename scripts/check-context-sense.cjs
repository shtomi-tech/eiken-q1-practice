"use strict";

const assert = require("node:assert/strict");
const path = require("node:path");
const {
  ROOT,
  pipelinePaths,
  readJson,
  sourceItems,
  vocabularyByTarget,
} = require("./lib/context-pipeline.cjs");
const {
  candidateSensesFromMeaning,
  validateTargetSense,
} = require("./lib/context-sense-validator.cjs");

const VOCAB_PATH = path.join(ROOT, "data", "vocab_2026-1.json");
const vocab = readJson(VOCAB_PATH);
const vocabulary = vocabularyByTarget();
const q67Candidates = readJson(pipelinePaths([6, 7]).candidate).items;

function source(target) {
  return sourceItems([6, 7]).find((item) => item.target === target) || {
    ...vocabulary.get(target),
    target,
    pos: ({ "名詞": "noun", "動詞": "verb", "形容詞": "adjective", "副詞": "adverb" })[vocabulary.get(target)?.pos] || vocabulary.get(target)?.pos,
    level: "EIKEN Grade 2",
  };
}

function senseItem(target, selection) {
  const sourceItem = source(target);
  return { ...sourceItem, ...selection };
}

function assertFinal(target) {
  const entry = q67Candidates[target];
  assert.ok(entry?.final, `${target}: final selection is missing`);
  const result = validateTargetSense(senseItem(target, entry.final), vocabulary.get(target));
  assert.equal(result.status, "pass", `${target}: final selection failed: ${result.errors.join(" / ")}`);
}

for (const item of sourceItems([6, 7])) assertFinal(item.target);

const expectedGroups = {
  chemical: ["化学の", "化学物質"],
  tap: ["（指などで）軽くたたく", "蛇口"],
};
for (const [target, expected] of Object.entries(expectedGroups)) {
  const parsed = candidateSensesFromMeaning(vocabulary.get(target).meaning, source(target).pos).map((item) => item.sense);
  assert.deepEqual(parsed, expected, `${target}: parsed candidate senses changed`);
}

const q45Review = readJson(pipelinePaths([4, 5]).review).items;
const senseRegression = {
  tendency: ["癖", "傾向"],
  discrimination: ["識別、区別", "差別"],
  shelter: ["保護", "避難所、シェルター"],
  content: ["満足して", "中身、内容"],
};
for (const [target, [incorrect, approved]] of Object.entries(senseRegression)) {
  assert.equal(q45Review[target].revisionLog[0].before, incorrect, `${target}: incorrect regression fixture changed`);
  assert.equal(q45Review[target].revisionLog[0].after, approved, `${target}: approved regression fixture changed`);
}

const positives = {
  branch: "枝",
  scale: "はかり",
  balance: "均衡、バランス",
  foster: "育む、促進する",
  hate: "ひどく嫌う",
  divide: "分ける、分割する",
  pronounce: "発音する",
};
const context = readJson(path.join(ROOT, "data", "context_2026-1.json"));
for (const [target, expected] of Object.entries(positives)) {
  const item = context.contexts.find((candidate) => candidate.target === target);
  assert.equal(item.targetSense, expected, `${target}: positive sense fixture changed`);
}

const q67VocabTargets = [...(vocab.words || []), ...(vocab.idioms || [])]
  .filter((item) => item.q === 6 || item.q === 7)
  .map((item) => item.word || item.phrase);
assert.deepEqual(Object.keys(q67Candidates), q67VocabTargets, "q=6/q=7 candidates must follow Vocabulary Data order");
console.log("target sense parser and regression fixtures: OK");
