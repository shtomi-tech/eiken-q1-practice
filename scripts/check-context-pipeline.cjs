"use strict";

const assert = require("node:assert/strict");
const childProcess = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { validateContextItem } = require("./lib/context-validator.cjs");
const { publish } = require("./publish-context-drafts.cjs");

const ROOT = path.resolve(__dirname, "..");
const BASE_COMMIT = "64d25f54375490519856d787b5be67bff45d5fe3";
const RUNTIME_PATH = path.join(ROOT, "data", "context_2026-1.json");
const VOCAB_PATH = path.join(ROOT, "data", "vocab_2026-1.json");
const DRAFT_PATH = path.join(ROOT, "data", "context-drafts", "eiken2-2026-1-q3.json");
const REVIEW_PATH = path.join(ROOT, "data", "context-drafts", "eiken2-2026-1-q3-review.json");
const APPROVED_PATH = path.join(ROOT, "data", "context-approved", "eiken2-2026-1-q3.json");
const REQUIRED_REVIEW_CHECKS = [
  "senseAppropriate", "senseUniquelySupported", "otherKnownSensesExcluded", "targetMainUnknown",
  "clueQuality", "clueIndependence", "noAnswerLeakage", "noSynonymLeakage", "contextCoherent",
  "difficultyAppropriate", "naturalEnglish", "supportNecessary", "distractorQuality", "answerUnique",
];

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function vocabItems() {
  const data = readJson(VOCAB_PATH);
  return [...(data.words || []), ...(data.idioms || [])];
}

function byTarget(items) {
  return new Map(items.map((item) => [item.word || item.phrase || item.target || item.source?.target, item]));
}

function runCheck(script) {
  childProcess.execFileSync(process.execPath, [path.join(ROOT, "scripts", script), "--check"], { stdio: "pipe" });
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

function expectRejected(approvedPath, mutate, label, tempDir) {
  const bad = readJson(APPROVED_PATH);
  mutate(bad);
  const badPath = path.join(tempDir, `${label}.json`);
  fs.writeFileSync(badPath, `${JSON.stringify(bad, null, 2)}\n`, "utf8");
  assert.throws(() => publish({ dryRun: true, approvedPath: badPath }), label);
}

function main() {
  runCheck("generate-context-q3-draft.cjs");
  runCheck("validate-context-drafts.cjs");
  runCheck("approve-context-drafts.cjs");
  runCheck("publish-context-drafts.cjs");

  const vocab = byTarget(vocabItems());
  const q3Sources = vocabItems().filter((item) => item.q === 3);
  assert.equal(q3Sources.length, 4, "Vocabulary Data must define exactly four q=3 items");
  const runtime = readJson(RUNTIME_PATH);
  const draft = readJson(DRAFT_PATH);
  const review = readJson(REVIEW_PATH);
  const approved = readJson(APPROVED_PATH);
  assert.equal(runtime.meta.count, 68, "runtime meta.count must remain 68");
  assert.equal(runtime.contexts.length, 68, "runtime item count must remain 68");
  assert.equal(draft.manualReview, undefined, "draft root must not self-approve review");
  assert.equal(review.reviewStatus, "complete", "manual review artifact must be complete");

  const runtimeByTarget = byTarget(runtime.contexts);
  const draftByTarget = byTarget(draft.items);
  const approvedByTarget = byTarget(approved.items);
  for (const source of q3Sources) {
    const target = source.word || source.phrase;
    const draftItem = draftByTarget.get(target);
    const approvedItem = approvedByTarget.get(target);
    const runtimeItem = runtimeByTarget.get(target);
    assert.ok(draftItem && approvedItem && runtimeItem, `${target}: pipeline item is missing`);
    const draftResult = validateContextItem({ ...draftItem.source, ...draftItem }, source, { requireTargetSense: true });
    assert.equal(draftResult.status, "pass", `${target}: draft structural validation failed`);
    assert.equal(draftItem.structuralValidation.status, "pass", `${target}: draft stage is not structurally approved`);
    assert.equal(draftItem.manualReview.status, "pending", `${target}: draft must remain manual-review pending`);
    assert.equal(draftItem.approval.status, "pending", `${target}: draft must remain approval pending`);
    assert.equal(review.items[target].status, "pass", `${target}: manual review must pass`);
    for (const key of REQUIRED_REVIEW_CHECKS) assert.equal(review.items[target].checks[key], "pass", `${target}: review check ${key}`);
    assert.deepEqual(runtimeProjection(runtimeItem), runtimeProjection(approvedItem), `${target}: runtime differs from approved item`);
    assert.equal(approvedItem.manualReview.status, "pass", `${target}: approved item lacks manual review pass`);
    assert.equal(approvedItem.approval.status, "approved", `${target}: approved item lacks approval`);
  }

  const baseline = JSON.parse(childProcess.execFileSync("git", ["show", `${BASE_COMMIT}:data/context_2026-1.json`], { cwd: ROOT, encoding: "utf8" }));
  assert.deepEqual(runtime.contexts.filter((item) => item.q <= 2 || item.q >= 8),
    baseline.contexts.filter((item) => item.q <= 2 || item.q >= 8),
    "q=1, q=2, and q=8+ runtime items must remain unchanged during q=3 proof");
  assert.equal(JSON.stringify(runtime.contexts.filter((item) => item.q === 3).map((item) => item.target)),
    JSON.stringify(q3Sources.map((item) => item.word || item.phrase)), "q=3 order must follow Vocabulary Data");

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "context-pipeline-"));
  try {
    const tempRuntime = path.join(tempDir, "context.json");
    fs.copyFileSync(RUNTIME_PATH, tempRuntime);
    const first = publish({ dryRun: false, runtimePath: tempRuntime });
    const firstRaw = fs.readFileSync(tempRuntime, "utf8");
    const second = publish({ dryRun: false, runtimePath: tempRuntime });
    const secondRaw = fs.readFileSync(tempRuntime, "utf8");
    assert.equal(first.changed, false, "publishing an already published approved draft should be idempotent");
    assert.equal(second.changed, false, "second publish must not change runtime data");
    assert.equal(firstRaw, secondRaw, "repeated publish must produce identical output");
    expectRejected(APPROVED_PATH, (bad) => { bad.items[0].approval.status = "pending"; }, "pending-approval", tempDir);
    expectRejected(APPROVED_PATH, (bad) => { bad.items[0].answerIndex = 1; }, "wrong-answer", tempDir);
    expectRejected(APPROVED_PATH, (bad) => { bad.items[0].segments[0].find((segment) => segment.role === "target").useJapanese = true; }, "target-japanese", tempDir);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
  console.log("context pipeline proof: OK (q=3 draft, review, approval, publish guard, idempotency)");
}

main();
