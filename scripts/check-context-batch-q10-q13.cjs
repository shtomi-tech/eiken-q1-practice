"use strict";

const assert = require("node:assert/strict");
const childProcess = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { validateContextItem } = require("./lib/context-validator.cjs");
const { validateTargetSense } = require("./lib/context-sense-validator.cjs");
const {
  ROOT, assertExactTargetOrder, pipelinePaths, readJson, sourceItems, vocabItems, vocabularyByTarget,
} = require("./lib/context-pipeline.cjs");
const { publish } = require("./publish-context-drafts.cjs");

const QS = [10, 11, 12, 13];
const BASE_COMMIT = "a18ee9959f806f3d7915d275f4e9118ffe233248";
const PATHS = pipelinePaths(QS);
const RUNTIME_PATH = path.join(ROOT, "data", "context_2026-1.json");
const CATEGORIES = ["SENSE", "SENSE_POS", "SENSE_SEMANTIC", "CONTEXT", "CLUE", "DIFFICULTY", "LEAKAGE", "JAPANESE_SUPPORT", "DISTRACTOR", "NATURALNESS", "OTHER"];

function runCheck(script, args = []) {
  childProcess.execFileSync(process.execPath, [path.join(ROOT, "scripts", script), ...args, "--check"], { stdio: "pipe" });
}
function byTarget(items) { return new Map(items.map((item) => [item.target || item.source?.target, item])); }
function projection(item) {
  return { q: item.q, type: item.type, target: item.target, meaning: item.meaning, targetSense: item.targetSense, pos: item.pos, level: item.level,
    fullEnglish: item.fullEnglish, mixedEnglish: item.mixedEnglish, contextClues: item.contextClues, inferencePath: item.inferencePath,
    segments: item.segments, choices: item.choices, answerIndex: item.answerIndex, inferenceExplanation: item.inferenceExplanation,
    quality: item.quality, manualReview: item.manualReview, approval: item.approval };
}
function expectRejected(mutate, label, tempDir) {
  const bad = readJson(PATHS.approved);
  mutate(bad);
  const file = path.join(tempDir, `${label}.json`);
  fs.writeFileSync(file, `${JSON.stringify(bad, null, 2)}\n`, "utf8");
  assert.throws(() => publish({ qs: QS, dryRun: true, approvedPath: file }), label);
}

function main() {
  runCheck("seed-context-candidates.cjs", ["--q", "10,11,12,13"]);
  runCheck("validate-context-senses.cjs", ["--q", "10,11,12,13"]);
  runCheck("generate-context-draft.cjs", ["--q", "10,11,12,13"]);
  runCheck("validate-context-drafts.cjs", ["--q", "10,11,12,13"]);
  runCheck("approve-context-drafts.cjs", ["--q", "10,11,12,13"]);
  runCheck("publish-context-drafts.cjs", ["--q", "10,11,12,13"]);
  runCheck("check-json-duplicate-keys.cjs");

  const sources = sourceItems(QS);
  assert.equal(sources.length, 16, "q=10..13 must contain sixteen Vocabulary items");
  for (const q of QS) assert.equal(sources.filter((item) => item.q === q).length, 4, `q=${q} must contain four source items`);
  const targets = sources.map((item) => item.target);
  const candidates = readJson(PATHS.candidate);
  const draft = readJson(PATHS.draft);
  const review = readJson(PATHS.review);
  const approved = readJson(PATHS.approved);
  const metrics = readJson(PATHS.metrics);
  const runtime = readJson(RUNTIME_PATH);
  const vocabulary = vocabularyByTarget();
  assertExactTargetOrder(Object.keys(candidates.items), targets, "candidate");
  assertExactTargetOrder(draft.initialItems.map((item) => item.source.target), targets, "initial draft");
  assertExactTargetOrder(draft.items.map((item) => item.source.target), targets, "final draft");
  assertExactTargetOrder(Object.keys(review.items), targets, "review");
  assertExactTargetOrder(approved.items.map((item) => item.target), targets, "approved");
  assert.equal(review.batchDiversity.status, "pass");
  for (const value of Object.values(review.batchDiversity.checks)) assert.equal(value, "pass");

  const draftByTarget = byTarget(draft.items);
  const approvedByTarget = byTarget(approved.items);
  const runtimeByTarget = byTarget(runtime.contexts);
  for (const source of sources) {
    const item = draftByTarget.get(source.target);
    const approvedItem = approvedByTarget.get(source.target);
    const runtimeItem = runtimeByTarget.get(source.target);
    const reviewItem = review.items[source.target];
    assert.ok(item && approvedItem && runtimeItem && reviewItem, `${source.target}: incomplete pipeline artifacts`);
    assert.equal(item.structuralValidation.status, "pass");
    assert.equal(item.senseValidation.status, "pass");
    assert.equal(item.manualReview.status, "pending");
    assert.equal(item.approval.status, "pending");
    assert.equal(reviewItem.senseReview.status, "pass");
    assert.equal(reviewItem.status, "pass");
    assert.equal(approvedItem.manualReview.status, "pass");
    assert.equal(approvedItem.approval.status, "approved");
    assert.deepEqual(projection(runtimeItem), projection(approvedItem));
    for (const key of ["candidateSenses", "eligibleSenses", "filteredOutSenses", "senseConfidence", "senseSelectionReason", "senseValidation", "revisionLog"]) {
      assert.equal(runtimeItem[key], undefined, `${source.target}: ${key} entered runtime`);
    }
    assert.equal(validateTargetSense({ ...item.source, ...item }, vocabulary.get(source.target), { requireEligibleSenses: true }).status, "pass");
    assert.equal(validateContextItem({ ...item.source, ...item }, vocabulary.get(source.target), { requireTargetSense: true }).status, "pass");
  }

  const reviews = Object.values(review.items);
  const revisionEvents = reviews.flatMap((item) => item.revisionLog || []);
  assert.equal(metrics.generated, 16);
  assert.equal(metrics.initialPass, reviews.filter((item) => item.initialStatus === "pass").length);
  assert.equal(metrics.revised, reviews.filter((item) => item.initialStatus === "revise").length);
  assert.equal(metrics.rejected, reviews.filter((item) => item.initialStatus === "reject").length);
  assert.equal(metrics.finalPass, reviews.filter((item) => item.status === "pass").length);
  assert.equal(metrics.senseInitialPass, reviews.filter((item) => item.initialSenseStatus === "pass").length);
  assert.equal(metrics.senseRevised, reviews.filter((item) => item.initialSenseStatus === "revise").length);
  assert.equal(metrics.initialPassRate, metrics.initialPass / metrics.generated);
  assert.equal(metrics.revisionRate, metrics.revised / metrics.generated);
  assert.equal(metrics.revisionDensity, revisionEvents.length / metrics.generated);
  assert.equal(metrics.criticalRevisionItems, reviews.filter((item) => (item.revisionLog || []).some((entry) => entry.critical)).length);
  assert.equal(metrics.criticalRevisionRate, metrics.criticalRevisionItems / metrics.generated);
  assert.equal(metrics.manualReviewCount, reviews.length);
  assert.equal(metrics.manualRevisionCount, metrics.revised);
  assert.equal(metrics.approvalCount, approved.items.length);
  assert.equal(metrics.blockedCount, metrics.generated - metrics.approvalCount);
  const reasonCounts = Object.fromEntries(CATEGORIES.map((category) => [category, 0]));
  for (const entry of revisionEvents) reasonCounts[entry.category] += 1;
  assert.deepEqual(metrics.revisionReasons, reasonCounts);
  assert.equal(metrics.contextRevised, reviews.filter((item) => item.initialStatus === "revise").length);
  assert.equal(metrics.clueRevised, reasonCounts.CLUE);
  assert.equal(metrics.distractorRevised, reasonCounts.DISTRACTOR);
  const draftItems = draft.items;
  assert.equal(metrics.multiSenseItems, draftItems.filter((item) => item.eligibleSenses.length > 1).length);
  assert.equal(metrics.posFilteredItems, draftItems.filter((item) => item.filteredOutSenses.length > 0).length);
  assert.equal(metrics.posFilteredSenseCount, draftItems.reduce((sum, item) => sum + item.filteredOutSenses.length, 0));
  assert.equal(metrics.singleEligibleAfterFilter, draftItems.filter((item) => item.eligibleSenses.length === 1).length);
  assert.equal(metrics.multipleEligibleAfterFilter, draftItems.filter((item) => item.eligibleSenses.length > 1).length);
  assert.equal(metrics.japaneseSupportUsed, draftItems.filter((item) => item.segments.flat().some((segment) => segment.useJapanese)).length);

  assert.equal(runtime.meta.datasetId, "eiken2-2026-1");
  assert.equal(runtime.meta.count, 68);
  assert.equal(runtime.contexts.length, 68);
  assert.deepEqual(runtime.contexts.map((item) => item.target), vocabItems().map((item) => item.word || item.phrase));

  assert.throws(() => assertExactTargetOrder(targets.slice(1), targets, "missing-target"));
  assert.throws(() => assertExactTargetOrder([...targets, targets[0]], targets, "duplicate-target"));
  assert.throws(() => assertExactTargetOrder([...targets.slice(0, -1), sourceItems([14])[0].target], targets, "unexpected-target"));
  assert.throws(() => assertExactTargetOrder([targets[1], targets[0], ...targets.slice(2)], targets, "wrong-order"));

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "context-q10-q13-"));
  try {
    const tempRuntime = path.join(tempDir, "context.json");
    fs.copyFileSync(RUNTIME_PATH, tempRuntime);
    const first = publish({ qs: QS, dryRun: false, runtimePath: tempRuntime });
    const second = publish({ qs: QS, dryRun: false, runtimePath: tempRuntime });
    assert.equal(first.changed, false);
    assert.equal(second.changed, false);
    assert.deepEqual(second.changedTargets, []);
    expectRejected((bad) => { bad.items[0].q = 14; }, "outside-scope", tempDir);
    expectRejected((bad) => { bad.items.push(structuredClone(bad.items[0])); }, "duplicate-target", tempDir);
    expectRejected((bad) => { [bad.items[0], bad.items[1]] = [bad.items[1], bad.items[0]]; }, "wrong-order", tempDir);
    expectRejected((bad) => { bad.items[0].manualReview.status = "pending"; }, "manual-pending", tempDir);
    expectRejected((bad) => { bad.items[0].manualReview.status = "revise"; }, "manual-revise", tempDir);
    expectRejected((bad) => { bad.items[0].approval.status = "pending"; }, "approval-pending", tempDir);
    expectRejected((bad) => { bad.items[0].senseConfidence = "low"; }, "low-confidence", tempDir);
    expectRejected((bad) => { bad.items[0].answerIndex = 1; }, "wrong-answer", tempDir);
    expectRejected((bad) => { bad.items[0].choices[0] = "別の意味"; }, "target-absent", tempDir);
    expectRejected((bad) => { bad.items.find((item) => item.target === "slip").choices[1] = "そっと動く・抜け出す"; }, "other-sense-choice", tempDir);
    expectRejected((bad) => { delete bad.items[0].candidateSenses; }, "missing-candidates", tempDir);
    expectRejected((bad) => { bad.items[0].eligibleSenses = []; }, "empty-eligible", tempDir);
    expectRejected((bad) => { bad.items[0].eligibleSenses = [{ sense: "別の意味", pos: "verb" }]; }, "eligible-outside", tempDir);
    expectRejected((bad) => { bad.items[0].segments[0].find((segment) => segment.role === "target").useJapanese = true; }, "target-japanese", tempDir);
    expectRejected((bad) => { bad.items[0].segments.flat().find((segment) => segment.role === "clue").useJapanese = true; }, "clue-japanese", tempDir);
    expectRejected((bad) => { const segment = bad.items[0].segments.flat().find((item) => item.role === "core"); segment.useJapanese = true; segment.ja = "補助"; delete segment.supportReason; }, "support-reason", tempDir);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
  console.log(`context q10-q13 controlled batch: OK (${metrics.initialPass}/16 initial PASS, ${metrics.finalPass}/16 final PASS)`);
}

main();
