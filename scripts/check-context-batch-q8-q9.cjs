"use strict";

const assert = require("node:assert/strict");
const childProcess = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { validateContextItem } = require("./lib/context-validator.cjs");
const { validateTargetSense } = require("./lib/context-sense-validator.cjs");
const {
  ROOT,
  pipelinePaths,
  readJson,
  sourceItems,
  vocabItems,
  vocabularyByTarget,
} = require("./lib/context-pipeline.cjs");
const { publish } = require("./publish-context-drafts.cjs");

const QS = [8, 9];
const BASE_COMMIT = "a2c21f700ba193afa0b5a930ff0f352912281cea";
const PATHS = pipelinePaths(QS);
const RUNTIME_PATH = path.join(ROOT, "data", "context_2026-1.json");
const REVISION_CATEGORIES = [
  "SENSE", "SENSE_POS", "SENSE_SEMANTIC", "CONTEXT", "CLUE", "DIFFICULTY", "LEAKAGE",
  "JAPANESE_SUPPORT", "DISTRACTOR", "NATURALNESS", "OTHER",
];

function runCheck(script, args = []) {
  childProcess.execFileSync(process.execPath, [path.join(ROOT, "scripts", script), ...args, "--check"], { stdio: "pipe" });
}

function byTarget(items) {
  return new Map(items.map((item) => [item.target || item.source?.target, item]));
}

function runtimeProjection(item) {
  return {
    q: item.q, type: item.type, target: item.target, meaning: item.meaning, targetSense: item.targetSense,
    pos: item.pos, level: item.level, fullEnglish: item.fullEnglish, mixedEnglish: item.mixedEnglish,
    contextClues: item.contextClues, inferencePath: item.inferencePath, segments: item.segments,
    choices: item.choices, answerIndex: item.answerIndex, inferenceExplanation: item.inferenceExplanation,
    quality: item.quality, manualReview: item.manualReview, approval: item.approval,
  };
}

function expectRejected(mutate, label, tempDir) {
  const bad = readJson(PATHS.approved);
  mutate(bad);
  const badPath = path.join(tempDir, `${label}.json`);
  fs.writeFileSync(badPath, `${JSON.stringify(bad, null, 2)}\n`, "utf8");
  assert.throws(() => publish({ qs: QS, dryRun: true, approvedPath: badPath }), label);
}

function main() {
  runCheck("validate-context-senses.cjs", ["--q", "8,9"]);
  runCheck("generate-context-draft.cjs", ["--q", "8,9"]);
  runCheck("validate-context-drafts.cjs", ["--q", "8,9"]);
  runCheck("approve-context-drafts.cjs", ["--q", "8,9"]);
  runCheck("publish-context-drafts.cjs", ["--q", "8,9"]);

  const sources = sourceItems(QS);
  assert.deepEqual(sources.map((item) => item.target), [
    "illustrate", "occupy", "polish", "congratulate", "barely", "secretly", "gently", "repeatedly",
  ], "q=8/q=9 source order must come from Vocabulary Data");
  const draft = readJson(PATHS.draft);
  const review = readJson(PATHS.review);
  const approved = readJson(PATHS.approved);
  const metrics = readJson(PATHS.metrics);
  const runtime = readJson(RUNTIME_PATH);
  const vocabulary = vocabularyByTarget();
  assert.equal(draft.initialItems?.length, 8, "initial draft must be retained");
  assert.equal(draft.items.length, 8);
  assert.equal(review.reviewStatus, "complete");
  assert.equal(approved.items.length, 8);

  const draftByTarget = byTarget(draft.items);
  const approvedByTarget = byTarget(approved.items);
  const runtimeByTarget = byTarget(runtime.contexts);
  for (const source of sources) {
    const target = source.target;
    const item = draftByTarget.get(target);
    const approvedItem = approvedByTarget.get(target);
    const runtimeItem = runtimeByTarget.get(target);
    const reviewItem = review.items[target];
    assert.ok(item && approvedItem && runtimeItem && reviewItem, `${target}: q8/q9 artifact is incomplete`);
    assert.ok(Array.isArray(item.candidateSenses), `${target}: candidateSenses missing`);
    assert.ok(Array.isArray(item.eligibleSenses), `${target}: eligibleSenses missing`);
    assert.ok(Array.isArray(item.filteredOutSenses), `${target}: filteredOutSenses missing`);
    assert.equal(item.structuralValidation.status, "pass");
    assert.equal(item.senseValidation.status, "pass");
    assert.equal(item.manualReview.status, "pending");
    assert.equal(item.approval.status, "pending");
    assert.equal(reviewItem.senseReview.status, "pass");
    assert.equal(reviewItem.status, "pass");
    assert.equal(approvedItem.senseValidation.status, "pass");
    assert.notEqual(approvedItem.senseConfidence, "low");
    assert.deepEqual(runtimeProjection(runtimeItem), runtimeProjection(approvedItem));
    for (const key of ["candidateSenses", "eligibleSenses", "filteredOutSenses", "senseConfidence", "senseSelectionReason", "senseValidation"]) {
      assert.equal(runtimeItem[key], undefined, `${target}: ${key} must not enter runtime data`);
    }
    assert.equal(validateTargetSense({ ...item.source, ...item }, vocabulary.get(target), { requireEligibleSenses: true }).status, "pass");
    assert.equal(validateContextItem({ ...item.source, ...item }, vocabulary.get(target), { requireTargetSense: true }).status, "pass");
  }

  const initialStatuses = Object.values(review.items).map((item) => item.initialStatus);
  const senseStatuses = Object.values(review.items).map((item) => item.initialSenseStatus);
  assert.equal(initialStatuses.filter((value) => value === "pass").length, metrics.initialPass);
  assert.equal(initialStatuses.filter((value) => value === "revise").length, metrics.revised);
  assert.equal(initialStatuses.filter((value) => value === "reject").length, metrics.rejected);
  assert.equal(senseStatuses.filter((value) => value === "pass").length, metrics.senseInitialPass);
  assert.equal(senseStatuses.filter((value) => value === "revise").length, metrics.senseRevised);
  assert.equal(senseStatuses.filter((value) => value === "reject").length, metrics.senseRejected);
  const allDraftItems = [...draft.items];
  const filteredCounts = allDraftItems.map((item) => item.filteredOutSenses.length);
  assert.equal(metrics.generated, allDraftItems.length);
  assert.equal(metrics.multiSenseItems, allDraftItems.filter((item) => item.eligibleSenses.length > 1).length);
  assert.equal(metrics.posFilteredItems, allDraftItems.filter((item) => item.filteredOutSenses.length > 0).length);
  assert.equal(metrics.posFilteredSenseCount, filteredCounts.reduce((sum, count) => sum + count, 0));
  assert.equal(metrics.singleEligibleAfterFilter, allDraftItems.filter((item) => item.eligibleSenses.length === 1).length);
  assert.equal(metrics.multipleEligibleAfterFilter, allDraftItems.filter((item) => item.eligibleSenses.length > 1).length);
  assert.equal(metrics.posPreventedRevisionCount, metrics.posFilteredItems);
  assert.equal(metrics.senseInitialPassRate, metrics.senseInitialPass / metrics.generated);
  assert.equal(metrics.senseRevisionRate, metrics.senseRevised / metrics.generated);
  assert.equal(metrics.initialPassRate, metrics.initialPass / metrics.generated);
  assert.equal(metrics.revisionRate, metrics.revised / metrics.generated);
  assert.equal(metrics.finalPass, 8);
  const reasonCounts = Object.fromEntries(REVISION_CATEGORIES.map((category) => [category, 0]));
  for (const item of Object.values(review.items)) {
    for (const entry of item.revisionLog || []) reasonCounts[entry.category] += 1;
  }
  assert.deepEqual(metrics.revisionReasons, reasonCounts);

  assert.equal(runtime.meta.count, 68);
  assert.equal(runtime.contexts.length, 68);
  assert.deepEqual(runtime.contexts.map((item) => item.target), vocabItems().map((item) => item.word || item.phrase));

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "context-pos-batch-"));
  try {
    const tempRuntime = path.join(tempDir, "context.json");
    fs.copyFileSync(RUNTIME_PATH, tempRuntime);
    const first = publish({ qs: QS, dryRun: false, runtimePath: tempRuntime });
    const firstRaw = fs.readFileSync(tempRuntime, "utf8");
    const second = publish({ qs: QS, dryRun: false, runtimePath: tempRuntime });
    const secondRaw = fs.readFileSync(tempRuntime, "utf8");
    assert.equal(first.changed, false);
    assert.equal(second.changed, false);
    assert.deepEqual(second.changedTargets, []);
    assert.equal(firstRaw, secondRaw);
    expectRejected((bad) => { delete bad.items[0].eligibleSenses; }, "eligible-missing", tempDir);
    expectRejected((bad) => { bad.items[0].eligibleSenses = []; }, "eligible-empty", tempDir);
    expectRejected((bad) => { bad.items[0].eligibleSenses = [{ sense: "別の意味", pos: "verb" }]; }, "eligible-outside", tempDir);
    expectRejected((bad) => { bad.items[0].eligibleSenses = [{ sense: "挿絵を入れる", pos: "noun" }]; }, "eligible-pos", tempDir);
    expectRejected((bad) => { bad.items[0].filteredOutSenses = [{ sense: "挿絵を入れる", pos: "verb", reason: "source-pos-mismatch" }]; }, "filtered-remains", tempDir);
    expectRejected((bad) => { bad.items[0].filteredOutSenses = [{ sense: "（例などで）説明する、明らかにする", pos: "verb", reason: "source-pos-mismatch" }]; }, "filtered-target", tempDir);
    expectRejected((bad) => { bad.items[0].targetSense = "存在しない意味"; }, "target-outside-eligible", tempDir);
    expectRejected((bad) => { bad.items[0].filteredOutSenses = [{ sense: "挿絵を入れる", pos: "verb", reason: "manual-choice" }]; }, "wrong-filtered-reason", tempDir);
    expectRejected((bad) => { bad.items[0].senseConfidence = "low"; }, "low-confidence", tempDir);
    expectRejected((bad) => { bad.items[0].senseValidation.status = "pending"; }, "sense-validation-pending", tempDir);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }

  console.log(`context q8-q9 batch: OK (POS-filtered ${metrics.posFilteredItems}, sense initial PASS ${metrics.senseInitialPass}, final PASS ${metrics.finalPass})`);
}

main();
