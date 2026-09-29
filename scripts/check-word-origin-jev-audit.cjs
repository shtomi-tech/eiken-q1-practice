"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const auditPath = path.join(ROOT, "data", "audit", "word-origin-jev-2026-09-29.json");
const batchPath = path.join(ROOT, "data", "word_origin_research_batch_052.json");
const requirementsPath = path.join(ROOT, "requirements-jev.txt");
const audit = JSON.parse(fs.readFileSync(auditPath, "utf8"));
const batch = JSON.parse(fs.readFileSync(batchPath, "utf8"));
const requirements = fs.readFileSync(requirementsPath, "utf8");

assert.equal(batch.meta.selectionReport, "data/audit/word-origin-jev-2026-09-29.json", "batch-052 must reference its committed selection audit");
assert.equal(audit.schemaVersion, 1, "Jev audit schemaVersion must be 1");
assert.equal(audit.run.requested, audit.run.succeeded + audit.run.failed, "requested count must equal successes plus failures");
assert.equal(audit.run.requested, 2787, "audit target count must match the recorded run");
assert.equal(audit.run.succeeded, 2787, "all recorded target entries must have results");
assert.equal(audit.run.failed, 0, "the recorded run must retain its zero-failure count");
assert.match(audit.run.classifier.sha256, /^[a-f0-9]{64}$/, "audit must retain the classifier source hash");
assert.equal(audit.run.sdk.distribution, "typesafe-sdk");
assert.match(audit.run.sdk.version, /^\d+\.\d+\.\d+$/, "audit must retain the historical SDK version");
assert.equal(audit.run.model.status, "not_recorded", "the historical model gap must remain explicit");
assert.match(requirements, /^typesafe-sdk==0\.7\.2\s*$/m, "the Jev SDK dependency must stay pinned");

const categoryTotal = Object.values(audit.categoryCounts).reduce((sum, count) => sum + count, 0);
assert.equal(categoryTotal, audit.run.succeeded, "category counts must cover every successful result");
const candidates = audit.selection.candidates;
assert.equal(candidates.length, audit.selection.candidateCount);
assert.equal(audit.selection.acceptedCount + audit.selection.excludedCount, candidates.length);
assert.equal(audit.selection.category, "compound_clipping");
assert.equal(new Set(candidates.map((candidate) => candidate.word)).size, candidates.length, "candidate words must be unique");

const acceptedWords = candidates.filter((candidate) => candidate.decision === "accepted").map((candidate) => candidate.word).sort();
assert.deepEqual(acceptedWords, audit.selection.acceptedWords, "acceptedWords must match candidate decisions");
assert.deepEqual(acceptedWords, Object.keys(batch.entries).sort(), "accepted candidates must match batch-052 entries");
for (const candidate of candidates) {
  assert.equal(candidate.classifierCategory, audit.selection.category, candidate.word + ": classifier category must match the selection");
  if (candidate.decision === "accepted") {
    assert.deepEqual(candidate.exclusionReasons, [], candidate.word + ": accepted candidate cannot have exclusion reasons");
  } else {
    assert.ok(candidate.exclusionReasons.length, candidate.word + ": excluded candidate needs a reason");
    if (candidate.exclusionReasons.includes("manual_exclusion_for_complex_form_or_meaning")) {
      assert.ok(candidate.reasonBasis, candidate.word + ": inferred manual exclusion needs its evidence boundary");
    }
  }
}

console.log("word origin Jev audit: OK (2787 results / 55 candidates / 18 accepted / 37 excluded)");
