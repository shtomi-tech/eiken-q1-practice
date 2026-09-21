"use strict";

const assert = require("node:assert/strict");
const childProcess = require("node:child_process");
const path = require("node:path");
const { AUDIT_PATH, CATEGORIES, MANUAL_CHECKS, main: buildAudit } = require("./build-context-full-audit.cjs");
const { ROOT, readJson, sourceItems, vocabItems, vocabularyByTarget } = require("./lib/context-pipeline.cjs");
const { compatibleSense, validateContextItem } = require("./lib/context-validator.cjs");
const { validateContextLeakage } = require("./lib/context-leakage-validator.cjs");

const BASE_COMMIT = "5ce31e1007e50e41a92dd78ce9d4cd0e19060b56";
const RUNTIME_PATH = path.join(ROOT, "data", "context_2026-1.json");
const VALID_STATUS = new Set(["pass", "warn", "revise"]);
const VALID_SEVERITY = new Set(["critical", "major", "minor"]);

function counts(entries) {
  return {
    pass: entries.filter((item) => item.finalAudit.status === "pass").length,
    warn: entries.filter((item) => item.finalAudit.status === "warn").length,
    revise: entries.filter((item) => item.finalAudit.status === "revise").length,
  };
}

function main() {
  const vocabularyItems = vocabItems();
  const vocabulary = vocabularyByTarget();
  const runtime = readJson(RUNTIME_PATH);
  const audit = readJson(AUDIT_PATH);
  const rebuilt = buildAudit({ write: false });
  assert.deepEqual(audit, rebuilt, "full audit artifact is stale or hand-edited");

  assert.equal(vocabularyItems.length, 68);
  assert.equal(runtime.meta.datasetId, "eiken2-2026-1");
  assert.equal(runtime.meta.count, 68);
  assert.equal(runtime.contexts.length, 68);
  assert.equal(Math.min(...runtime.contexts.map((item) => item.q)), 1);
  assert.equal(Math.max(...runtime.contexts.map((item) => item.q)), 17);
  for (let q = 1; q <= 17; q += 1) assert.equal(runtime.contexts.filter((item) => item.q === q).length, 4, `q=${q} must have four items`);
  const sourceTargets = sourceItems(Array.from({ length: 17 }, (_, index) => index + 1)).map((item) => item.target);
  const runtimeTargets = runtime.contexts.map((item) => item.target);
  assert.deepEqual(runtimeTargets, sourceTargets, "Vocabulary/Runtime target order mismatch");
  assert.equal(new Set(runtimeTargets).size, 68, "duplicate runtime target");
  assert.deepEqual(audit.entries.map((item) => item.target), runtimeTargets, "audit target order mismatch");
  assert.equal(audit.entries.length, 68);

  for (const [index, item] of runtime.contexts.entries()) {
    const entry = audit.entries[index];
    const vocab = vocabulary.get(item.target);
    const effective = { ...item, targetSense: item.targetSense || item.meaning };
    const structural = validateContextItem(effective, vocab, { requireTargetSense: true });
    assert.equal(structural.status, "pass", `${item.target}: ${structural.errors.join(" / ")}`);
    assert.equal(compatibleSense(item.meaning, effective.targetSense), true, `${item.target}: incompatible target sense`);
    assert.equal(entry.senseCompatible, true);
    assert.ok(VALID_STATUS.has(entry.initialAudit.status));
    assert.ok(VALID_STATUS.has(entry.finalAudit.status));
    assert.equal(entry.structuralValidation, "pass");
    assert.deepEqual(entry.leakageValidation, validateContextLeakage(effective));
    for (const check of MANUAL_CHECKS) assert.equal(entry.manualAudit.checks[check], "pass", `${item.target}: manual ${check}`);
    for (const finding of entry.finalAudit.findings) {
      assert.ok(CATEGORIES.includes(finding.category), `${item.target}: invalid category`);
      assert.ok(VALID_SEVERITY.has(finding.severity), `${item.target}: invalid severity`);
    }
    if (entry.leakageValidation.status === "warn") {
      assert.equal(entry.manualAudit.status, "pass", `${item.target}: WARN not reviewed`);
      assert.ok(entry.manualAudit.reason.length > 20, `${item.target}: WARN review reason missing`);
    }
    assert.notEqual(entry.leakageValidation.status, "fail", `${item.target}: leakage FAIL remains`);
  }

  const summary = counts(audit.entries);
  const findings = audit.entries.flatMap((item) => item.finalAudit.findings);
  assert.equal(audit.summary.totalItems, 68);
  assert.equal(audit.summary.passItems, summary.pass);
  assert.equal(audit.summary.warnItems, summary.warn);
  assert.equal(audit.summary.reviseItems, summary.revise);
  assert.equal(audit.summary.passRate, summary.pass / 68);
  assert.equal(audit.summary.warnRate, summary.warn / 68);
  assert.equal(audit.summary.revisionRate, summary.revise / 68);
  assert.equal(audit.summary.criticalFindings, findings.filter((item) => item.severity === "critical").length);
  assert.equal(audit.summary.majorFindings, findings.filter((item) => item.severity === "major").length);
  assert.equal(audit.summary.minorFindings, findings.filter((item) => item.severity === "minor").length);
  for (const category of CATEGORIES) assert.equal(audit.categoryMetrics[category], findings.filter((item) => item.category === category).length);
  assert.equal(audit.summary.reviewedWarn, audit.entries.filter((item) => item.leakageValidation.status === "warn" && item.manualAudit.status === "pass").length);
  assert.equal(audit.summary.unreviewedWarn, 0);
  assert.equal(audit.summary.reviseItems, 0);
  assert.equal(audit.diversityAudit.status, "pass");
  const stories = runtime.contexts.map((item) => item.fullEnglish.join(" ").toLowerCase());
  assert.equal(new Set(stories).size, 68, "duplicate full context found");

  const baseline = JSON.parse(childProcess.execFileSync("git", ["show", `${BASE_COMMIT}:data/context_2026-1.json`], { cwd: ROOT, encoding: "utf8" }));
  assert.deepEqual(runtime, baseline, "Phase 11 audit must not alter runtime when no REVISE item exists");
  console.log(`full context dataset audit: OK (${summary.pass} PASS / ${summary.warn} WARN / ${summary.revise} REVISE)`);
}

main();
