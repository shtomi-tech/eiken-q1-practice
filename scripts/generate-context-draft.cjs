"use strict";

const {
  parseQs,
  pipelinePaths,
  readJson,
  sourceItems,
  writeJson,
} = require("./lib/context-pipeline.cjs");

function candidateValue(entry) {
  if (entry && entry.final) return entry.final;
  return entry;
}

function initialValue(entry) {
  if (entry && entry.initial) return entry.initial;
  return null;
}

function contextFields(source, candidate) {
  return {
    source,
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
  const sourceTargets = sources.map((item) => item.target).sort();
  const candidateTargets = Object.keys(candidates).sort();
  if (JSON.stringify(sourceTargets) !== JSON.stringify(candidateTargets)) {
    throw new Error(`Candidate targets do not match Vocabulary Data for ${paths.label}: ${candidateTargets.join(", ")}`);
  }

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
