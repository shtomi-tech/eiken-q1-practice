"use strict";

const assert = require("node:assert/strict");
const childProcess = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { ROOT, assertExactTargetOrder, pipelinePaths, readJson, sourceItems, vocabItems } = require("./lib/context-pipeline.cjs");
const { publish } = require("./publish-context-drafts.cjs");

const QS = [14, 15, 16, 17];
const BASE_COMMIT = "3a173e3a070a9df0f2b1eab3cc454959f51c60e4";
const PATHS = pipelinePaths(QS);
const RUNTIME_PATH = path.join(ROOT, "data", "context_2026-1.json");
const CATEGORIES = ["SENSE", "SENSE_POS", "SENSE_SEMANTIC", "CONTEXT", "CLUE", "DIFFICULTY", "LEAKAGE", "JAPANESE_SUPPORT", "DISTRACTOR", "NATURALNESS", "OTHER"];

function runCheck(script, args = []) {
  childProcess.execFileSync(process.execPath, [path.join(ROOT, "scripts", script), ...args, "--check"], { stdio: "pipe" });
}
function targetOf(item) { return item.target || item.source?.target; }
function expectRejected(mutate, label, tempDir) {
  const bad = readJson(PATHS.approved);
  mutate(bad);
  const file = path.join(tempDir, `${label}.json`);
  fs.writeFileSync(file, `${JSON.stringify(bad, null, 2)}\n`, "utf8");
  assert.throws(() => publish({ qs: QS, dryRun: true, approvedPath: file }), label);
}

function main() {
  for (const [script, args] of [
    ["seed-context-candidates.cjs", ["--q", "14,15,16,17"]],
    ["validate-context-senses.cjs", ["--q", "14,15,16,17"]],
    ["generate-context-draft.cjs", ["--q", "14,15,16,17"]],
    ["build-context-review.cjs", ["--q", "14,15,16,17"]],
    ["validate-context-drafts.cjs", ["--q", "14,15,16,17"]],
    ["approve-context-drafts.cjs", ["--q", "14,15,16,17"]],
    ["publish-context-drafts.cjs", ["--q", "14,15,16,17"]],
    ["check-json-duplicate-keys.cjs", []],
  ]) runCheck(script, args);

  const sources = sourceItems(QS);
  assert.equal(sources.length, 16);
  const targets = sources.map((item) => item.target);
  const candidates = readJson(PATHS.candidate);
  const draft = readJson(PATHS.draft);
  const review = readJson(PATHS.review);
  const approved = readJson(PATHS.approved);
  const metrics = readJson(PATHS.metrics);
  const runtime = readJson(RUNTIME_PATH);
  assertExactTargetOrder(Object.keys(candidates.items), targets, "candidates");
  assertExactTargetOrder(draft.initialItems.map(targetOf), targets, "initial draft");
  assertExactTargetOrder(draft.items.map(targetOf), targets, "final draft");
  assertExactTargetOrder(Object.keys(review.items), targets, "review");
  assertExactTargetOrder(approved.items.map(targetOf), targets, "approved");
  assert.equal(review.batchDiversity.status, "pass");

  const initialByTarget = new Map(draft.initialItems.map((item) => [targetOf(item), item]));
  const finalByTarget = new Map(draft.items.map((item) => [targetOf(item), item]));
  const approvedByTarget = new Map(approved.items.map((item) => [targetOf(item), item]));
  const runtimeByTarget = new Map(runtime.contexts.map((item) => [item.target, item]));
  for (const target of targets) {
    const initial = initialByTarget.get(target);
    const final = finalByTarget.get(target);
    const accepted = approvedByTarget.get(target);
    const runtimeItem = runtimeByTarget.get(target);
    assert.ok(initial && final && accepted && runtimeItem);
    assert.equal(final.structuralValidation.status, "pass");
    assert.notEqual(final.leakageValidation.status, "fail");
    if (final.leakageValidation.status === "warn") assert.equal(accepted.leakageReview.status, "accepted");
    for (const key of ["candidateSenses", "eligibleSenses", "filteredOutSenses", "senseConfidence", "senseValidation", "leakageValidation", "leakageFindings", "leakageReview", "revisionLog"]) {
      assert.equal(runtimeItem[key], undefined, `${target}: ${key} entered runtime`);
    }
  }

  const reviews = Object.values(review.items);
  const revisions = reviews.flatMap((item) => item.revisionLog || []);
  const initialLeakage = reviews.map((item) => item.initialLeakageValidation);
  const finalLeakage = reviews.map((item) => item.finalLeakageValidation);
  for (const status of ["pass", "warn", "fail"]) {
    const key = `leakageInitial${status[0].toUpperCase()}${status.slice(1)}`;
    assert.equal(metrics[key], initialLeakage.filter((item) => item.status === status).length);
    const finalKey = `leakageFinal${status[0].toUpperCase()}${status.slice(1)}`;
    assert.equal(metrics[finalKey], finalLeakage.filter((item) => item.status === status).length);
  }
  assert.equal(metrics.generated, 16);
  assert.equal(metrics.initialPass, reviews.filter((item) => item.initialStatus === "pass").length);
  assert.equal(metrics.revised, reviews.filter((item) => item.initialStatus === "revise").length);
  assert.equal(metrics.finalPass, reviews.filter((item) => item.status === "pass").length);
  assert.equal(metrics.initialPassRate, metrics.initialPass / metrics.generated);
  assert.equal(metrics.revisionRate, metrics.revised / metrics.generated);
  assert.equal(metrics.revisionDensity, revisions.length / 16);
  assert.equal(metrics.leakagePreReviewRevised, revisions.filter((entry) => entry.stage === "pre-review" && entry.category === "LEAKAGE").length);
  assert.equal(metrics.manualLeakageRevisions, revisions.filter((entry) => entry.stage === "manual-review" && entry.category === "LEAKAGE").length);
  assert.equal(metrics.leakagePreventedBeforeManualReview, reviews.filter((item) => item.initialLeakageValidation.status === "fail" && item.finalLeakageValidation.status !== "fail").length);
  const typeCounts = { DIRECT_DEFINITION: 0, SYNONYM_LEAKAGE: 0, PARAPHRASE_LEAKAGE: 0, TRANSLATION_LEAKAGE: 0, OTHER_LEAKAGE: 0 };
  for (const result of initialLeakage) for (const finding of result.findings) typeCounts[finding.type] += 1;
  assert.deepEqual(metrics.leakageTypeFindings, typeCounts);
  const reasonCounts = Object.fromEntries(CATEGORIES.map((category) => [category, 0]));
  for (const entry of revisions) reasonCounts[entry.category] += 1;
  assert.deepEqual(metrics.revisionReasons, reasonCounts);

  assert.equal(runtime.meta.datasetId, "eiken2-2026-1");
  assert.equal(runtime.meta.count, 68);
  assert.equal(runtime.contexts.length, 68);
  assert.deepEqual(runtime.contexts.map((item) => item.target), vocabItems().map((item) => item.word || item.phrase));

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "context-q14-q17-"));
  try {
    const tempRuntime = path.join(tempDir, "context.json");
    fs.copyFileSync(RUNTIME_PATH, tempRuntime);
    assert.equal(publish({ qs: QS, dryRun: false, runtimePath: tempRuntime }).changed, false);
    assert.deepEqual(publish({ qs: QS, dryRun: false, runtimePath: tempRuntime }).changedTargets, []);
    expectRejected((bad) => { bad.items[0].leakageValidation = { status: "fail", findings: [] }; }, "leakage-fail", tempDir);
    expectRejected((bad) => { bad.items[0].leakageValidation = { status: "warn", findings: [] }; delete bad.items[0].leakageReview; }, "warn-unreviewed", tempDir);
    expectRejected((bad) => { bad.items[0].manualReview.status = "pending"; }, "manual-pending", tempDir);
    expectRejected((bad) => { bad.items[0].approval.status = "pending"; }, "approval-pending", tempDir);
    expectRejected((bad) => { bad.items[0].q = 18; }, "outside-scope", tempDir);
    expectRejected((bad) => { bad.items.push(structuredClone(bad.items[0])); }, "duplicate-target", tempDir);
    expectRejected((bad) => { [bad.items[0], bad.items[1]] = [bad.items[1], bad.items[0]]; }, "wrong-order", tempDir);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
  console.log(`context q14-q17 leakage batch: OK (${metrics.initialPass}/16 initial PASS, ${metrics.finalPass}/16 final PASS)`);
}

main();
