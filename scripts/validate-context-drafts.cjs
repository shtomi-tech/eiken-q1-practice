"use strict";

const { assertContextItem } = require("./lib/context-validator.cjs");
const {
  parseQs,
  pipelinePaths,
  readJson,
  sourceItems,
  vocabularyByTarget,
  sameQs,
  writeJson,
} = require("./lib/context-pipeline.cjs");

function main({ qs = parseQs(), write = true } = {}) {
  const paths = pipelinePaths(qs);
  const draft = readJson(paths.draft);
  const vocabulary = vocabularyByTarget();
  const sources = sourceItems(qs);
  if (!sameQs(draft.q, qs) || !sameQs(draft.qs || draft.q, qs) || draft.items?.length !== sources.length) {
    throw new Error(`The ${paths.label} draft must contain exactly ${sources.length} source items`);
  }
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
  if (write) writeJson(paths.draft, draft);
  return draft;
}

if (require.main === module) {
  const checkOnly = process.argv.includes("--check");
  const qs = parseQs();
  const draft = main({ qs, write: !checkOnly });
  console.log(`${pipelinePaths(qs).label} structural validation: PASS (${draft.items.length} items)`);
}

module.exports = { main };
