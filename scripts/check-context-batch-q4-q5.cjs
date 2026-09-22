"use strict";

const assert = require("node:assert/strict");
const childProcess = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { validateContextItem } = require("./lib/context-validator.cjs");
const {
  ROOT,
  pipelinePaths,
  readJson,
  sourceItems,
  vocabItems,
  vocabularyByTarget,
} = require("./lib/context-pipeline.cjs");
const { publish } = require("./publish-context-drafts.cjs");

const QS = [4, 5];
const BASE_COMMIT = "64d25f54375490519856d787b5be67bff45d5fe3";
const PATHS = pipelinePaths(QS);
const RUNTIME_PATH = path.join(ROOT, "data", "context_2026-1.json");
const REQUIRED_CATEGORIES = [
  "SENSE", "CONTEXT", "CLUE", "DIFFICULTY", "LEAKAGE", "JAPANESE_SUPPORT",
  "DISTRACTOR", "NATURALNESS", "OTHER",
];

function runCheck(script, args = []) {
  childProcess.execFileSync(process.execPath, [path.join(ROOT, "scripts", script), ...args, "--check"], { stdio: "pipe" });
}

function byTarget(items) {
  return new Map(items.map((item) => [item.target || item.source?.target, item]));
}

function projection(item) {
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

function expectRejected(approvedPath, mutate, label, tempDir) {
  const bad = readJson(PATHS.approved);
  mutate(bad);
  const badPath = path.join(tempDir, `${label}.json`);
  fs.writeFileSync(badPath, `${JSON.stringify(bad, null, 2)}\n`, "utf8");
  assert.throws(() => publish({ qs: QS, dryRun: true, approvedPath: badPath }), label);
}

function main() {
  runCheck("generate-context-draft.cjs", ["--q", "4,5"]);
  runCheck("validate-context-drafts.cjs", ["--q", "4,5"]);
  runCheck("approve-context-drafts.cjs", ["--q", "4,5"]);
  runCheck("publish-context-drafts.cjs", ["--q", "4,5"]);

  const sources = sourceItems(QS);
  assert.equal(sources.length, 8, "q=4 and q=5 must contain exactly eight Vocabulary items");
  assert.deepEqual(sources.map((item) => item.target), [
    "tendency", "discrimination", "shelter", "content",
    "foster", "hate", "divide", "pronounce",
  ], "q=4/q=5 source order must come from Vocabulary Data");

  const draft = readJson(PATHS.draft);
  const review = readJson(PATHS.review);
  const approved = readJson(PATHS.approved);
  const metrics = readJson(PATHS.metrics);
  const runtime = readJson(RUNTIME_PATH);
  const vocabulary = vocabularyByTarget();
  assert.deepEqual(draft.qs, QS, "draft must identify q=4 and q=5");
  assert.equal(draft.sourceCount, 8, "draft sourceCount must be eight");
  assert.equal(draft.initialItems?.length, 8, "initial draft must be retained for every item");
  assert.equal(draft.items.length, 8, "final draft must contain eight items");
  assert.equal(review.reviewStatus, "complete", "review artifact must be complete");
  assert.deepEqual(approved.qs, QS, "approved artifact must identify q=4 and q=5");
  assert.equal(approved.items.length, 8, "all eight final PASS items should be approved");

  const draftByTarget = byTarget(draft.items);
  const approvedByTarget = byTarget(approved.items);
  const runtimeByTarget = byTarget(runtime.contexts);
  for (const source of sources) {
    const target = source.target;
    const item = draftByTarget.get(target);
    const approvedItem = approvedByTarget.get(target);
    const runtimeItem = runtimeByTarget.get(target);
    const reviewItem = review.items[target];
    assert.ok(item && approvedItem && runtimeItem && reviewItem, `${target}: batch artifact is incomplete`);
    assert.equal(item.structuralValidation.status, "pass", `${target}: structural validation must pass`);
    assert.equal(item.manualReview.status, "pending", `${target}: draft manual review must remain pending`);
    assert.equal(item.approval.status, "pending", `${target}: draft approval must remain pending`);
    assert.equal(reviewItem.status, "pass", `${target}: final review must pass`);
    assert.ok(["pass", "revise", "reject"].includes(reviewItem.initialStatus), `${target}: invalid initial review status`);
    for (const key of Object.keys(reviewItem.checks)) assert.equal(reviewItem.checks[key], "pass", `${target}: final review ${key}`);
    assert.deepEqual(projection(runtimeItem), projection(approvedItem), `${target}: runtime differs from approved artifact`);
    assert.equal(approvedItem.manualReview.status, "pass", `${target}: approved manual review is missing`);
    assert.equal(approvedItem.approval.status, "approved", `${target}: approved status is missing`);
    const result = validateContextItem({ ...item.source, ...item }, vocabulary.get(target), { requireTargetSense: true });
    assert.equal(result.status, "pass", `${target}: final draft structural validation failed`);
  }

  const initialStatuses = Object.values(review.items).map((item) => item.initialStatus);
  const finalStatuses = Object.values(review.items).map((item) => item.status);
  const revised = initialStatuses.filter((status) => status === "revise").length;
  const initialPass = initialStatuses.filter((status) => status === "pass").length;
  const rejected = initialStatuses.filter((status) => status === "reject").length;
  assert.equal(initialPass, metrics.initialPass, "metrics.initialPass must match initial review artifact");
  assert.equal(revised, metrics.revised, "metrics.revised must match initial review artifact");
  assert.equal(rejected, metrics.rejected, "metrics.rejected must match initial review artifact");
  assert.equal(finalStatuses.filter((status) => status === "pass").length, metrics.finalPass, "metrics.finalPass must match final review artifact");
  assert.equal(metrics.generated, 8, "metrics.generated must be eight");
  assert.equal(metrics.initialPassRate, metrics.initialPass / metrics.generated, "initialPassRate is stale");
  assert.equal(metrics.revisionRate, metrics.revised / metrics.generated, "revisionRate is stale");
  const reasonCounts = Object.fromEntries(REQUIRED_CATEGORIES.map((category) => [category, 0]));
  for (const item of Object.values(review.items)) {
    for (const entry of item.revisionLog || []) {
      assert.ok(REQUIRED_CATEGORIES.includes(entry.category), `${entry.category}: unknown revision category`);
      reasonCounts[entry.category] += 1;
    }
  }
  assert.deepEqual(metrics.revisionReasons, reasonCounts, "revision reason metrics are stale");
  const japaneseSupportUsed = draft.items.filter((item) => item.segments.flat().some((segment) => segment.useJapanese)).length;
  assert.equal(metrics.japaneseSupportUsed, japaneseSupportUsed, "Japanese Support metric is stale");

  assert.equal(runtime.meta.count, 68, "runtime meta.count must remain 68");
  assert.equal(runtime.contexts.length, 68, "runtime item count must remain 68");
  assert.deepEqual(runtime.contexts.map((item) => item.target), vocabItems().map((item) => item.word || item.phrase),
    "runtime target order must remain Vocabulary order");

  assert.deepEqual(runtime.contexts.filter((item) => item.q === 4 || item.q === 5).map((item) => item.target), sources.map((item) => item.target),
    "q=4/q=5 runtime target order must follow Vocabulary Data");

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "context-batch-"));
  try {
    const tempRuntime = path.join(tempDir, "context.json");
    fs.copyFileSync(RUNTIME_PATH, tempRuntime);
    const first = publish({ qs: QS, dryRun: false, runtimePath: tempRuntime });
    const firstRaw = fs.readFileSync(tempRuntime, "utf8");
    const second = publish({ qs: QS, dryRun: false, runtimePath: tempRuntime });
    const secondRaw = fs.readFileSync(tempRuntime, "utf8");
    assert.equal(first.changed, false, "publishing an already published batch should be idempotent");
    assert.equal(second.changed, false, "second batch publish must not change runtime data");
    assert.equal(firstRaw, secondRaw, "repeated batch publish must produce identical output");
    expectRejected(PATHS.approved, (bad) => { bad.items[0].manualReview.status = "pending"; }, "manual-review-pending", tempDir);
    expectRejected(PATHS.approved, (bad) => { bad.items[0].manualReview.status = "revise"; }, "manual-review-revise", tempDir);
    expectRejected(PATHS.approved, (bad) => { bad.items[0].approval.status = "pending"; }, "approval-pending", tempDir);
    expectRejected(PATHS.approved, (bad) => { bad.items[0].answerIndex = 1; }, "wrong-answer-index", tempDir);
    expectRejected(PATHS.approved, (bad) => { bad.items[0].choices[0] = "別の意味"; }, "target-sense-missing", tempDir);
    expectRejected(PATHS.approved, (bad) => { bad.items.find((item) => item.target === "content").choices[1] = "満足して"; }, "other-sense-distractor", tempDir);
    expectRejected(PATHS.approved, (bad) => { bad.items[0].segments[0].find((segment) => segment.role === "target").useJapanese = true; }, "target-japanese", tempDir);
    expectRejected(PATHS.approved, (bad) => { bad.items[0].segments.flat().find((segment) => segment.role === "clue").useJapanese = true; }, "clue-japanese", tempDir);
    expectRejected(PATHS.approved, (bad) => {
      const segment = bad.items[0].segments[0].find((candidate) => candidate.role === "core");
      segment.useJapanese = true;
      segment.ja = "補助";
      delete segment.supportReason;
    }, "support-reason-missing", tempDir);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }

  console.log(`context q4-q5 batch: OK (generated ${metrics.generated}, initial PASS ${metrics.initialPass}, REVISE ${metrics.revised}, final PASS ${metrics.finalPass}, Japanese Support ${metrics.japaneseSupportUsed})`);
}

main();
