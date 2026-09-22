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

const QS = [6, 7];
const BASE_COMMIT = "0b539fbe33fc776d9b2fe11e7be79748edfa6657";
const PATHS = pipelinePaths(QS);
const RUNTIME_PATH = path.join(ROOT, "data", "context_2026-1.json");
const REVISION_CATEGORIES = [
  "SENSE", "CONTEXT", "CLUE", "DIFFICULTY", "LEAKAGE", "JAPANESE_SUPPORT",
  "DISTRACTOR", "NATURALNESS", "OTHER",
];

function runCheck(script, args = []) {
  childProcess.execFileSync(process.execPath, [path.join(ROOT, "scripts", script), ...args, "--check"], { stdio: "pipe" });
}

function byTarget(items) {
  return new Map(items.map((item) => [item.target || item.source?.target, item]));
}

function runtimeProjection(item) {
  return {
    q: item.q,
    type: item.type,
    target: item.target,
    meaning: item.meaning,
    targetSense: item.targetSense,
    pos: item.pos,
    level: item.level,
    fullEnglish: item.fullEnglish,
    mixedEnglish: item.mixedEnglish,
    contextClues: item.contextClues,
    inferencePath: item.inferencePath,
    segments: item.segments,
    choices: item.choices,
    answerIndex: item.answerIndex,
    inferenceExplanation: item.inferenceExplanation,
    quality: item.quality,
    manualReview: item.manualReview,
    approval: item.approval,
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
  runCheck("validate-context-senses.cjs", ["--q", "6,7"]);
  runCheck("generate-context-draft.cjs", ["--q", "6,7"]);
  runCheck("validate-context-drafts.cjs", ["--q", "6,7"]);
  runCheck("approve-context-drafts.cjs", ["--q", "6,7"]);
  runCheck("publish-context-drafts.cjs", ["--q", "6,7"]);

  const sources = sourceItems(QS);
  assert.deepEqual(sources.map((item) => item.target), [
    "typical", "gradual", "chemical", "false", "weep", "occur", "swell", "tap",
  ], "q=6/q=7 source order must come from Vocabulary Data");
  const draft = readJson(PATHS.draft);
  const review = readJson(PATHS.review);
  const approved = readJson(PATHS.approved);
  const metrics = readJson(PATHS.metrics);
  const runtime = readJson(RUNTIME_PATH);
  const vocabulary = vocabularyByTarget();
  assert.deepEqual(draft.qs, QS);
  assert.equal(draft.initialItems?.length, 8, "initial Sense/Context draft must be retained");
  assert.equal(draft.items.length, 8);
  assert.equal(review.reviewStatus, "complete");
  assert.deepEqual(approved.qs, QS);
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
    assert.ok(item && approvedItem && runtimeItem && reviewItem, `${target}: q6/q7 artifact is incomplete`);
    assert.equal(item.structuralValidation.status, "pass", `${target}: context structural validation must pass`);
    assert.equal(item.senseValidation.status, "pass", `${target}: sense validation must pass`);
    assert.ok(Array.isArray(item.candidateSenses), `${target}: candidateSenses must be present`);
    assert.ok(Array.isArray(item.eligibleSenses), `${target}: eligibleSenses must be present`);
    assert.ok(Array.isArray(item.filteredOutSenses), `${target}: filteredOutSenses must be present`);
    assert.equal(item.manualReview.status, "pending");
    assert.equal(item.approval.status, "pending");
    assert.equal(reviewItem.senseReview.status, "pass", `${target}: sense review must pass`);
    assert.equal(reviewItem.status, "pass", `${target}: context review must pass`);
    for (const value of Object.values(reviewItem.senseReview.checks)) assert.equal(value, "pass", `${target}: sense review check`);
    for (const value of Object.values(reviewItem.checks)) assert.equal(value, "pass", `${target}: context review check`);
    assert.equal(approvedItem.senseValidation.status, "pass");
    assert.notEqual(approvedItem.senseConfidence, "low");
    assert.deepEqual(runtimeProjection(runtimeItem), runtimeProjection(approvedItem), `${target}: runtime differs from approved artifact`);
    assert.equal(runtimeItem.candidateSenses, undefined, `${target}: candidateSenses must not enter runtime data`);
    assert.equal(runtimeItem.eligibleSenses, undefined, `${target}: eligibleSenses must not enter runtime data`);
    assert.equal(runtimeItem.filteredOutSenses, undefined, `${target}: filteredOutSenses must not enter runtime data`);
    assert.equal(runtimeItem.senseSelectionReason, undefined, `${target}: review metadata must not enter runtime data`);
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
  assert.equal(metrics.senseInitialPassRate, metrics.senseInitialPass / metrics.generated);
  assert.equal(metrics.senseRevisionRate, metrics.senseRevised / metrics.generated);
  assert.equal(metrics.initialPassRate, metrics.initialPass / metrics.generated);
  assert.equal(metrics.revisionRate, metrics.revised / metrics.generated);
  assert.equal(metrics.finalPass, 8);
  assert.equal(metrics.initialLowConfidence, 2);
  assert.equal(metrics.finalLowConfidence, 0);
  const reasonCounts = Object.fromEntries(REVISION_CATEGORIES.map((category) => [category, 0]));
  for (const item of Object.values(review.items)) {
    for (const entry of item.revisionLog || []) reasonCounts[entry.category] += 1;
  }
  assert.deepEqual(metrics.revisionReasons, reasonCounts);

  assert.equal(runtime.meta.count, 68);
  assert.equal(runtime.contexts.length, 68);
  assert.deepEqual(runtime.contexts.map((item) => item.target), vocabItems().map((item) => item.word || item.phrase));
  assert.deepEqual(runtime.contexts.filter((item) => item.q === 6 || item.q === 7).map((item) => item.target), sources.map((item) => item.target));

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "context-sense-batch-"));
  try {
    const tempRuntime = path.join(tempDir, "context.json");
    fs.copyFileSync(RUNTIME_PATH, tempRuntime);
    const first = publish({ qs: QS, dryRun: false, runtimePath: tempRuntime });
    const firstRaw = fs.readFileSync(tempRuntime, "utf8");
    const second = publish({ qs: QS, dryRun: false, runtimePath: tempRuntime });
    const secondRaw = fs.readFileSync(tempRuntime, "utf8");
    assert.equal(first.changed, false);
    assert.equal(second.changed, false);
    assert.equal(firstRaw, secondRaw);
    expectRejected((bad) => { bad.items[0].senseValidation.status = "pending"; }, "sense-validation-pending", tempDir);
    expectRejected((bad) => { bad.items[0].senseConfidence = "low"; }, "low-confidence", tempDir);
    expectRejected((bad) => { bad.items[0].candidateSenses = []; }, "candidate-senses-missing", tempDir);
    expectRejected((bad) => { delete bad.items[0].eligibleSenses; }, "eligible-senses-missing", tempDir);
    expectRejected((bad) => { bad.items[0].eligibleSenses = []; }, "eligible-senses-empty", tempDir);
    expectRejected((bad) => { bad.items[0].targetSense = "存在しない意味"; }, "target-sense-outside", tempDir);
    expectRejected((bad) => { bad.items.find((item) => item.target === "chemical").targetSense = "化学物質"; }, "pos-incompatible-sense", tempDir);
    expectRejected((bad) => { delete bad.items[0].senseSelectionReason; }, "sense-reason-missing", tempDir);
    expectRejected((bad) => { bad.items[0].senseConfidence = "unknown"; }, "invalid-confidence", tempDir);
    expectRejected((bad) => { bad.items[0].answerIndex = 1; }, "wrong-answer-index", tempDir);
    expectRejected((bad) => { bad.items[0].segments[0].find((segment) => segment.role === "target").useJapanese = true; }, "target-japanese", tempDir);
    expectRejected((bad) => { bad.items[0].segments.flat().find((segment) => segment.role === "clue").useJapanese = true; }, "clue-japanese", tempDir);
    expectRejected((bad) => {
      const segment = bad.items[0].segments[0].find((candidate) => candidate.role === "core");
      segment.useJapanese = true;
      segment.ja = "補助";
      delete segment.supportReason;
    }, "support-reason-missing", tempDir);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }

  console.log(`context q6-q7 batch: OK (sense initial PASS ${metrics.senseInitialPass}, sense REVISE ${metrics.senseRevised}, final PASS ${metrics.finalPass})`);
}

main();
