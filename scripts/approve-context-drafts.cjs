"use strict";

const { assertContextItem } = require("./lib/context-validator.cjs");
const { assertTargetSense } = require("./lib/context-sense-validator.cjs");
const { assertLeakagePublishable } = require("./lib/context-leakage-validator.cjs");
const {
  parseQs,
  pipelinePaths,
  readJson,
  vocabularyByTarget,
  sameQs,
  writeJson,
} = require("./lib/context-pipeline.cjs");

function main({ qs = parseQs(), write = true } = {}) {
  const paths = pipelinePaths(qs);
  const draft = readJson(paths.draft);
  const review = readJson(paths.review);
  const vocabulary = vocabularyByTarget();
  if (!sameQs(draft.q, qs) || draft.items?.length !== draft.sourceCount) {
    throw new Error(`Only the selected ${paths.label} draft items may be approved`);
  }
  if (review.reviewStatus !== "complete") throw new Error("Manual review is not complete");

  const items = draft.items.map((draftItem) => {
    const target = draftItem.source.target;
    const reviewItem = review.items?.[target];
    if (!reviewItem || reviewItem.status !== "pass") throw new Error(`${target}: manual review is not PASS`);
    if (draftItem.structuralValidation?.status !== "pass") throw new Error(`${target}: structural validation is not PASS`);
    if (qs.some((q) => q >= 6)) {
      if (draftItem.senseValidation?.status !== "pass") throw new Error(`${target}: sense validation is not PASS`);
      assertTargetSense({ ...draftItem.source, ...draftItem }, vocabulary.get(target), { requireEligibleSenses: true });
      if (draftItem.senseConfidence === "low") throw new Error(`${target}: low-confidence sense cannot be auto-approved`);
      if (reviewItem.senseReview?.status !== "pass") throw new Error(`${target}: sense review is not PASS`);
    }
    if (draftItem.source.q >= 14) {
      draftItem.leakageReview = reviewItem.leakageReview;
      assertLeakagePublishable(draftItem);
    }
    if (draftItem.manualReview?.status !== "pending" || draftItem.approval?.status !== "pending") {
      throw new Error(`${target}: draft must start approval from pending states`);
    }
    const runtimeItem = {
      q: draftItem.source.q,
      type: draftItem.source.type || "word",
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
    if (qs.some((q) => q >= 6)) {
      runtimeItem.candidateSenses = draftItem.candidateSenses;
      runtimeItem.eligibleSenses = draftItem.eligibleSenses;
      runtimeItem.filteredOutSenses = draftItem.filteredOutSenses;
      runtimeItem.senseConfidence = draftItem.senseConfidence;
      runtimeItem.senseSelectionReason = draftItem.senseSelectionReason;
      runtimeItem.senseValidation = draftItem.senseValidation;
    }
    if (draftItem.source.q >= 14) {
      runtimeItem.leakageValidation = draftItem.leakageValidation;
      runtimeItem.leakageReview = reviewItem.leakageReview;
    }
    assertContextItem(runtimeItem, vocabulary.get(target), { requireTargetSense: true });
    return runtimeItem;
  });
  const approved = {
    schemaVersion: 1,
    datasetId: "eiken2-2026-1",
    q: qs.length === 1 ? qs[0] : qs,
    qs: [...qs],
    stage: "APPROVED",
    items,
  };
  if (write) writeJson(paths.approved, approved);
  return approved;
}

if (require.main === module) {
  const checkOnly = process.argv.includes("--check");
  const qs = parseQs();
  const approved = main({ qs, write: !checkOnly });
  console.log(`${checkOnly ? "approved draft check" : "approved draft written"} (${pipelinePaths(qs).label}): ${approved.items.map((item) => item.target).join(", ")}`);
}

module.exports = { main };
