"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { assertContextItem } = require("./lib/context-validator.cjs");

const ROOT = path.resolve(__dirname, "..");
const VOCAB_PATH = path.join(ROOT, "data", "vocab_2026-1.json");
const APPROVED_PATH = path.join(ROOT, "data", "context-approved", "eiken2-2026-1-q3.json");
const RUNTIME_PATH = path.join(ROOT, "data", "context_2026-1.json");

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function vocabularyByTarget() {
  const vocab = readJson(VOCAB_PATH);
  return new Map([...(vocab.words || []), ...(vocab.idioms || [])]
    .map((item) => [item.word || item.phrase, item]));
}

function approvedItems(approved) {
  if (approved.stage !== "APPROVED" || approved.q !== 3 || approved.items?.length !== 4) {
    throw new Error("Publish requires exactly four APPROVED q=3 items");
  }
  const vocab = vocabularyByTarget();
  for (const item of approved.items) {
    if (item.approval?.status !== "approved") throw new Error(`${item.target}: approval is not approved`);
    if (item.manualReview?.status !== "pass") throw new Error(`${item.target}: manual review is not PASS`);
    assertContextItem(item, vocab.get(item.target), { requireTargetSense: true });
  }
  return approved.items;
}

function findRuntimeLine(lines, target) {
  return lines.findIndex((line) => {
    const trimmed = line.trim().replace(/,$/, "");
    if (!trimmed.startsWith("{")) return false;
    try {
      const item = JSON.parse(trimmed);
      return item.q === 3 && item.target === target;
    } catch {
      return false;
    }
  });
}

function publish({ dryRun = true, runtimePath = RUNTIME_PATH, approvedPath = APPROVED_PATH } = {}) {
  const approved = readJson(approvedPath);
  const items = approvedItems(approved);
  const raw = fs.readFileSync(runtimePath, "utf8");
  const lines = raw.split(/\r?\n/);
  const runtime = readJson(runtimePath);
  if (runtime.meta?.count !== 68 || runtime.contexts?.length !== 68) {
    throw new Error("Runtime context dataset count must remain 68");
  }
  const q3Runtime = runtime.contexts.filter((item) => item.q === 3).map((item) => item.target);
  const q3Approved = items.map((item) => item.target);
  if (JSON.stringify(q3Runtime) !== JSON.stringify(q3Approved)) {
    throw new Error("Runtime q=3 order/target set does not match approved draft");
  }

  const nextLines = [...lines];
  const changedTargets = [];
  for (const item of items) {
    const index = findRuntimeLine(nextLines, item.target);
    if (index < 0) throw new Error(`${item.target}: runtime line is missing`);
    const hadComma = nextLines[index].trimEnd().endsWith(",");
    const indent = nextLines[index].match(/^\s*/)?.[0] || "";
    const replacement = `${indent}${JSON.stringify(item)}${hadComma ? "," : ""}`;
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
  const result = publish({ dryRun: !process.argv.includes("--publish") });
  console.log(`${result.dryRun ? "context publish dry-run" : "context published"}: ${result.changedTargets.join(", ") || "no changes"}`);
}

module.exports = { publish, approvedItems };
