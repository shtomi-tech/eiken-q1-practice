"use strict";

const {
  parseQs,
  pipelinePaths,
  readJson,
  sourceItems,
  writeJson,
  assertExactTargetOrder,
} = require("./lib/context-pipeline.cjs");
const { filterEligibleSenses } = require("./lib/context-sense-validator.cjs");

function candidateValue(entry) {
  if (entry && entry.final) return entry.final;
  return entry;
}

function initialValue(entry) {
  if (entry && entry.initial) return entry.initial;
  if (entry && entry.final) return entry.final;
  return entry;
}

function contextFields(source, candidate) {
  const prefilter = candidate.candidateSenses
    ? filterEligibleSenses(candidate.candidateSenses, source.pos)
    : null;
  const senseFields = candidate.candidateSenses ? {
    candidateSenses: candidate.candidateSenses,
    eligibleSenses: candidate.eligibleSenses || prefilter.eligibleSenses,
    filteredOutSenses: candidate.filteredOutSenses || prefilter.filteredOutSenses,
    senseConfidence: candidate.senseConfidence,
    senseValidation: { status: "pending" },
  } : {};
  return {
    source,
    ...senseFields,
    targetSense: candidate.targetSense,
    senseSelectionReason: candidate.senseSelectionReason,
    fullEnglish: candidate.fullEnglish,
    mixedEnglish: candidate.mixedEnglish,
    contextClues: candidate.contextClues,
    inferencePath: candidate.inferencePath,
    segments: candidate.segments,
    supportDecision: candidate.supportDecision || "not-needed",
    choices: candidate.choices,
    answerIndex: candidate.answerIndex,
    inferenceExplanation: candidate.inferenceExplanation,
    structuralValidation: { status: "pending" },
    manualReview: { status: "pending" },
    approval: { status: "pending" },
  };
}

function main({ qs = parseQs(), write = true } = {}) {
  const paths = pipelinePaths(qs);
  const sources = sourceItems(qs);
  const candidates = readJson(paths.candidate).items || {};
  const sourceTargets = sources.map((item) => item.target);
  const candidateTargets = Object.keys(candidates);
  assertExactTargetOrder(candidateTargets, sourceTargets, `${paths.label} candidates`);

  const initialItems = [];
  const items = sources.map((source) => {
    const entry = candidates[source.target];
    const initial = initialValue(entry);
    if (initial) initialItems.push(contextFields(source, initial));
    return contextFields(source, candidateValue(entry));
  });
  const draft = {
    schemaVersion: 1,
    datasetId: "eiken2-2026-1",
    q: qs.length === 1 ? qs[0] : qs,
    qs: [...qs],
    stage: "DRAFT",
    sourceCount: sources.length,
    ...(initialItems.length ? { initialItems } : {}),
    items,
  };
  if (write) writeJson(paths.draft, draft);
  return draft;
}

if (require.main === module) {
  const checkOnly = process.argv.includes("--check");
  const qs = parseQs();
  const draft = main({ qs, write: !checkOnly });
  console.log(`${checkOnly ? "draft source check" : "draft generated"} (${pipelinePaths(qs).label}): ${draft.items.map((item) => item.source.target).join(", ")}`);
}

module.exports = { main, contextFields };
