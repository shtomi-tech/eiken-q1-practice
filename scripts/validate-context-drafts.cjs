"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { assertContextItem } = require("./lib/context-validator.cjs");

const ROOT = path.resolve(__dirname, "..");
const VOCAB_PATH = path.join(ROOT, "data", "vocab_2026-1.json");
const DRAFT_PATH = path.join(ROOT, "data", "context-drafts", "eiken2-2026-1-q3.json");

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function vocabByTarget() {
  const vocab = readJson(VOCAB_PATH);
  return new Map([...(vocab.words || []), ...(vocab.idioms || [])]
    .map((item) => [item.word || item.phrase, item]));
}

function main({ write = true } = {}) {
  const draft = readJson(DRAFT_PATH);
  const vocabulary = vocabByTarget();
  if (draft.q !== 3 || draft.items?.length !== 4) throw new Error("The q=3 draft must contain exactly four items");
  for (const item of draft.items) {
    const vocab = vocabulary.get(item.source.target);
    const runtimeShape = { ...item.source, ...item };
    assertContextItem(runtimeShape, vocab, { requireTargetSense: true });
    if (item.manualReview?.status !== "pending") throw new Error(`${item.source.target}: manualReview must remain pending before review`);
    if (item.approval?.status !== "pending") throw new Error(`${item.source.target}: approval must remain pending before review`);
    item.structuralValidation = {
      status: "pass",
      checks: [
        "source", "targetSense", "fullEnglish", "targetOccurrence", "contextClues",
        "segments", "targetProtection", "clueProtection", "supportReason", "choices", "explanation",
      ],
    };
  }
  if (write) fs.writeFileSync(DRAFT_PATH, `${JSON.stringify(draft, null, 2)}\n`, "utf8");
  return draft;
}

if (require.main === module) {
  const checkOnly = process.argv.includes("--check");
  const draft = main({ write: !checkOnly });
  console.log(`q=3 structural validation: PASS (${draft.items.length} items)`);
}

module.exports = { main };
