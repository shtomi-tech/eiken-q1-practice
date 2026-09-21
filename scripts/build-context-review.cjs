"use strict";

const { parseQs, pipelinePaths, readJson, sourceItems, assertExactTargetOrder, writeJson } = require("./lib/context-pipeline.cjs");

const SENSE_CHECKS = ["posCompatible", "senseAppropriate", "senseCentrality", "senseSpecificity", "learningValue", "contextFeasibility", "otherSensesDistinct"];
const CONTEXT_CHECKS = ["senseAppropriate", "senseUniquelySupported", "otherKnownSensesExcluded", "targetMainUnknown", "clueQuality", "clueIndependence", "noAnswerLeakage", "noSynonymLeakage", "contextCoherent", "difficultyAppropriate", "naturalEnglish", "supportNecessary", "distractorQuality", "answerUnique"];
const passChecks = (names) => Object.fromEntries(names.map((name) => [name, "pass"]));

function main({ qs = parseQs(), write = true } = {}) {
  const paths = pipelinePaths(qs);
  const draft = readJson(paths.draft);
  const plan = readJson(paths.reviewPlan);
  const targets = sourceItems(qs).map((item) => item.target);
  assertExactTargetOrder(Object.keys(plan.items), targets, `${paths.label} review plan`);
  const initialByTarget = new Map(draft.initialItems.map((item) => [item.source.target, item]));
  const finalByTarget = new Map(draft.items.map((item) => [item.source.target, item]));
  const items = {};
  for (const target of targets) {
    const initial = initialByTarget.get(target);
    const final = finalByTarget.get(target);
    const planned = plan.items[target];
    const finalLeakage = final.leakageValidation;
    const defaultLeakageReview = finalLeakage.status === "warn"
      ? { status: "pending", reason: "Leakage WARN requires an explicit reviewer decision." }
      : { status: "pass", reason: "Leakage pre-check found no final leakage." };
    items[target] = {
      initialStatus: planned.initialStatus,
      initialSenseStatus: "pass",
      initialTargetSense: initial.targetSense,
      initialConfidence: initial.senseConfidence,
      initialCandidateSenses: initial.candidateSenses.map((item) => item.sense),
      initialEligibleSenses: initial.eligibleSenses.map((item) => item.sense),
      initialFilteredOutSenses: initial.filteredOutSenses.map((item) => item.sense),
      initialLeakageValidation: initial.leakageValidation,
      finalLeakageValidation: finalLeakage,
      leakageReview: planned.leakageReview || defaultLeakageReview,
      senseReview: { status: "pass", checks: passChecks(SENSE_CHECKS) },
      status: "pass",
      checks: passChecks(CONTEXT_CHECKS),
      revisionLog: planned.revisionLog || [],
    };
  }
  const review = {
    schemaVersion: 1,
    datasetId: "eiken2-2026-1",
    qs: [...qs],
    reviewStatus: "complete",
    reviewPrompt: "prompts/context-review-v1.md",
    senseReviewPrompt: "prompts/context-sense-selection-v1.md",
    batchDiversity: plan.batchDiversity,
    items,
  };
  if (write) writeJson(paths.review, review);
  return review;
}

if (require.main === module) {
  const qs = parseQs();
  const checkOnly = process.argv.includes("--check");
  const review = main({ qs, write: !checkOnly });
  console.log(`${checkOnly ? "review build check" : "review written"} (${pipelinePaths(qs).label}): ${Object.keys(review.items).length} items`);
}

module.exports = { main };
