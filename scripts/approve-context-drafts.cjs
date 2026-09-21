"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { assertContextItem } = require("./lib/context-validator.cjs");

const ROOT = path.resolve(__dirname, "..");
const VOCAB_PATH = path.join(ROOT, "data", "vocab_2026-1.json");
const DRAFT_PATH = path.join(ROOT, "data", "context-drafts", "eiken2-2026-1-q3.json");
const REVIEW_PATH = path.join(ROOT, "data", "context-drafts", "eiken2-2026-1-q3-review.json");
const APPROVED_PATH = path.join(ROOT, "data", "context-approved", "eiken2-2026-1-q3.json");

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function vocabularyByTarget() {
  const vocab = readJson(VOCAB_PATH);
  return new Map([...(vocab.words || []), ...(vocab.idioms || [])]
    .map((item) => [item.word || item.phrase, item]));
}

function main({ write = true } = {}) {
  const draft = readJson(DRAFT_PATH);
  const review = readJson(REVIEW_PATH);
  const vocabulary = vocabularyByTarget();
  if (draft.q !== 3 || draft.items?.length !== 4) throw new Error("Only the four q=3 draft items may be approved");
  if (review.reviewStatus !== "complete") throw new Error("Manual review is not complete");

  const items = draft.items.map((draftItem) => {
    const target = draftItem.source.target;
    const reviewItem = review.items?.[target];
    if (!reviewItem || reviewItem.status !== "pass") throw new Error(`${target}: manual review is not PASS`);
    if (draftItem.structuralValidation?.status !== "pass") throw new Error(`${target}: structural validation is not PASS`);
    if (draftItem.manualReview?.status !== "pending" || draftItem.approval?.status !== "pending") {
      throw new Error(`${target}: draft must start approval from pending states`);
    }
    const runtimeItem = {
      q: draftItem.source.q,
      type: "word",
      target,
      meaning: draftItem.source.meaning,
      targetSense: draftItem.targetSense,
      pos: draftItem.source.pos,
      level: draftItem.source.level,
      fullEnglish: draftItem.fullEnglish,
      mixedEnglish: draftItem.mixedEnglish,
      contextClues: draftItem.contextClues,
      inferencePath: draftItem.inferencePath,
      segments: draftItem.segments,
      choices: draftItem.choices,
      answerIndex: draftItem.answerIndex,
      inferenceExplanation: draftItem.inferenceExplanation,
      quality: {
        targetOccurrence: 1,
        clueCount: draftItem.contextClues.length,
        targetProtected: true,
        cluesProtected: true,
      },
      manualReview: {
        status: "pass",
        checks: reviewItem.checks,
      },
      approval: { status: "approved" },
    };
    assertContextItem(runtimeItem, vocabulary.get(target), { requireTargetSense: true });
    return runtimeItem;
  });
  const approved = {
    schemaVersion: 1,
    datasetId: "eiken2-2026-1",
    q: 3,
    stage: "APPROVED",
    items,
  };
  if (write) fs.writeFileSync(APPROVED_PATH, `${JSON.stringify(approved, null, 2)}\n`, "utf8");
  return approved;
}

if (require.main === module) {
  const checkOnly = process.argv.includes("--check");
  const approved = main({ write: !checkOnly });
  console.log(`${checkOnly ? "approved draft check" : "approved draft written"}: ${approved.items.map((item) => item.target).join(", ")}`);
}

module.exports = { main };
