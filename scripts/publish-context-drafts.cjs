"use strict";

const fs = require("node:fs");
const { assertContextItem } = require("./lib/context-validator.cjs");
const { assertTargetSense } = require("./lib/context-sense-validator.cjs");
const {
  ROOT,
  parseQs,
  pipelinePaths,
  readJson,
  sourceItems,
  vocabularyByTarget,
  sameQs,
} = require("./lib/context-pipeline.cjs");

const RUNTIME_PATH = require("node:path").join(ROOT, "data", "context_2026-1.json");

function approvedItems(approved, qs = [3]) {
  const expectedCount = sourceItems(qs).length;
  if (approved.stage !== "APPROVED" || !sameQs(approved.q, qs) || !approved.items?.length ||
      (qs.length === 1 && approved.items.length !== expectedCount)) {
    throw new Error(`Publish requires APPROVED ${pipelinePaths(qs).label} items`);
  }
  const vocab = vocabularyByTarget();
  for (const item of approved.items) {
    if (!qs.includes(item.q)) throw new Error(`${item.target}: publish scope is outside ${pipelinePaths(qs).label}`);
    if (item.approval?.status !== "approved") throw new Error(`${item.target}: approval is not approved`);
    if (item.manualReview?.status !== "pass") throw new Error(`${item.target}: manual review is not PASS`);
    if (qs.some((q) => q >= 6)) {
      if (item.senseValidation?.status !== "pass") throw new Error(`${item.target}: sense validation is not PASS`);
      if (item.senseConfidence === "low") throw new Error(`${item.target}: low-confidence sense cannot be published`);
      assertTargetSense(item, vocab.get(item.target), { requireEligibleSenses: true });
    }
    assertContextItem(item, vocab.get(item.target), { requireTargetSense: true });
  }
  return approved.items;
}

function runtimeItem(item) {
  const {
    candidateSenses,
    eligibleSenses,
    filteredOutSenses,
    senseConfidence,
    senseSelectionReason,
    senseValidation,
    ...runtime
  } = item;
  return runtime;
}

function findRuntimeLine(lines, target, q) {
  return lines.findIndex((line) => {
    const trimmed = line.trim().replace(/,$/, "");
    if (!trimmed.startsWith("{")) return false;
    try {
      const item = JSON.parse(trimmed);
      return item.q === q && item.target === target;
    } catch {
      return false;
    }
  });
}

function publish({
  qs = [3],
  dryRun = true,
  runtimePath = RUNTIME_PATH,
  approvedPath,
} = {}) {
  const resolvedApprovedPath = approvedPath || pipelinePaths(qs).approved;
  const approved = readJson(resolvedApprovedPath);
  const items = approvedItems(approved, qs);
  const raw = fs.readFileSync(runtimePath, "utf8");
  const lines = raw.split(/\r?\n/);
  const runtime = readJson(runtimePath);
  if (runtime.meta?.count !== 68 || runtime.contexts?.length !== 68) {
    throw new Error("Runtime context dataset count must remain 68");
  }
  const allowedTargets = new Set(sourceItems(qs).map((item) => item.target));
  const runtimeTargets = runtime.contexts.filter((item) => allowedTargets.has(item.target)).map((item) => item.target);
  const approvedTargets = items.map((item) => item.target);
  let cursor = 0;
  for (const target of approvedTargets) {
    const next = runtimeTargets.indexOf(target, cursor);
    if (next < cursor) throw new Error(`${target}: approved item order does not follow runtime order`);
    cursor = next + 1;
  }

  const nextLines = [...lines];
  const changedTargets = [];
  for (const item of items) {
    const index = findRuntimeLine(nextLines, item.target, item.q);
    if (index < 0) throw new Error(`${item.target}: runtime line is missing`);
    const hadComma = nextLines[index].trimEnd().endsWith(",");
    const indent = nextLines[index].match(/^\s*/)?.[0] || "";
    const replacement = `${indent}${JSON.stringify(runtimeItem(item))}${hadComma ? "," : ""}`;
    if (nextLines[index] !== replacement) {
      nextLines[index] = replacement;
      changedTargets.push(item.target);
    }
  }
  const nextRaw = nextLines.join("\n");
  if (!dryRun && nextRaw !== raw) fs.writeFileSync(runtimePath, nextRaw, "utf8");
  return {
    dryRun,
    changedTargets,
    changed: nextRaw !== raw,
    itemOrderPreserved: true,
    metaCountPreserved: true,
  };
}

if (require.main === module) {
  const qs = parseQs();
  const result = publish({
    qs,
    dryRun: !process.argv.includes("--publish"),
    approvedPath: pipelinePaths(qs).approved,
  });
  console.log(`${result.dryRun ? "context publish dry-run" : "context published"} (${pipelinePaths(qs).label}): ${result.changedTargets.join(", ") || "no changes"}`);
}

module.exports = { publish, approvedItems };
