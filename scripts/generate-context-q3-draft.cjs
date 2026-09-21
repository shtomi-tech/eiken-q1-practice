"use strict";

const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const VOCAB_PATH = path.join(ROOT, "data", "vocab_2026-1.json");
const CANDIDATE_PATH = path.join(ROOT, "data", "context-drafts", "eiken2-2026-1-q3-candidates.json");
const DRAFT_PATH = path.join(ROOT, "data", "context-drafts", "eiken2-2026-1-q3.json");

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function sourceItems() {
  const vocab = readJson(VOCAB_PATH);
  return [...(vocab.words || []), ...(vocab.idioms || [])]
    .filter((item) => item.q === 3)
    .map((item) => ({
      q: item.q,
      target: item.word || item.phrase,
      meaning: item.meaning,
      pos: ({ "名詞": "noun", "動詞": "verb", "形容詞": "adjective", "副詞": "adverb" })[item.pos] || item.pos,
      level: "EIKEN Grade 2",
    }));
}

function main({ write = true } = {}) {
  const sources = sourceItems();
  if (sources.length !== 4) throw new Error(`Expected exactly four q=3 source items, found ${sources.length}`);
  const candidates = readJson(CANDIDATE_PATH).items || {};
  const sourceTargets = sources.map((item) => item.target).sort();
  const candidateTargets = Object.keys(candidates).sort();
  if (JSON.stringify(sourceTargets) !== JSON.stringify(candidateTargets)) {
    throw new Error(`Candidate targets do not match q=3 Vocabulary Data: ${candidateTargets.join(", ")}`);
  }

  const items = sources.map((source) => ({
    source,
    targetSense: candidates[source.target].targetSense,
    senseSelectionReason: candidates[source.target].senseSelectionReason,
    fullEnglish: candidates[source.target].fullEnglish,
    mixedEnglish: candidates[source.target].mixedEnglish,
    contextClues: candidates[source.target].contextClues,
    inferencePath: candidates[source.target].inferencePath,
    segments: candidates[source.target].segments,
    supportDecision: candidates[source.target].supportDecision || "not-needed",
    choices: candidates[source.target].choices,
    answerIndex: candidates[source.target].answerIndex,
    inferenceExplanation: candidates[source.target].inferenceExplanation,
    structuralValidation: { status: "pending" },
    manualReview: { status: "pending" },
    approval: { status: "pending" },
  }));
  const draft = {
    schemaVersion: 1,
    datasetId: "eiken2-2026-1",
    q: 3,
    stage: "DRAFT",
    sourceCount: sources.length,
    items,
  };
  if (write) fs.writeFileSync(DRAFT_PATH, `${JSON.stringify(draft, null, 2)}\n`, "utf8");
  return draft;
}

if (require.main === module) {
  const checkOnly = process.argv.includes("--check");
  const draft = main({ write: !checkOnly });
  console.log(`${checkOnly ? "q=3 draft source check" : "q=3 draft generated"}: ${draft.items.map((item) => item.source.target).join(", ")}`);
}

module.exports = { main, sourceItems };
