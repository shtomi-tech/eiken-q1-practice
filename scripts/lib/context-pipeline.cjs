"use strict";

const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "../..");
const VOCAB_PATH = path.join(ROOT, "data", "vocab_2026-1.json");
const DATASET_ID = "eiken2-2026-1";
const POS_MAP = {
  "名詞": "noun",
  "動詞": "verb",
  "形容詞": "adjective",
  "副詞": "adverb",
};

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeJson(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function vocabItems() {
  const vocab = readJson(VOCAB_PATH);
  return [...(vocab.words || []), ...(vocab.idioms || [])];
}

function sourceItems(qs) {
  const wanted = new Set(qs);
  return vocabItems()
    .filter((item) => wanted.has(item.q))
    .map((item) => ({
      q: item.q,
      target: item.word || item.phrase,
      meaning: item.meaning,
      pos: POS_MAP[item.pos] || item.pos,
      level: "EIKEN Grade 2",
    }));
}

function vocabularyByTarget() {
  return new Map(vocabItems().map((item) => [item.word || item.phrase, item]));
}

function parseQs(argv = process.argv.slice(2), fallback = [3]) {
  const index = argv.findIndex((arg) => arg === "--q" || arg.startsWith("--q="));
  if (index < 0) return [...fallback];
  const raw = argv[index].startsWith("--q=") ? argv[index].slice(4) : argv[index + 1];
  if (!raw) throw new Error("--q requires one or more comma-separated question numbers");
  const qs = raw.split(",").map((value) => Number(value.trim())).filter((value) => Number.isInteger(value));
  if (!qs.length || qs.some((q) => q < 1)) throw new Error(`Invalid --q value: ${raw}`);
  return [...new Set(qs)];
}

function qLabel(qs) {
  return qs.length === 1 ? `q${qs[0]}` : qs.map((q) => `q${q}`).join("-");
}

function pipelinePaths(qs) {
  const label = qLabel(qs);
  const draftDir = path.join(ROOT, "data", "context-drafts");
  return {
    label,
    candidate: path.join(draftDir, `${DATASET_ID}-${label}-candidates.json`),
    draft: path.join(draftDir, `${DATASET_ID}-${label}.json`),
    review: path.join(draftDir, `${DATASET_ID}-${label}-review.json`),
    approved: path.join(ROOT, "data", "context-approved", `${DATASET_ID}-${label}.json`),
    metrics: path.join(ROOT, "data", "context-pipeline-metrics", `${DATASET_ID}-${label}.json`),
  };
}

function metadataFor(qs) {
  return {
    q: qs.length === 1 ? qs[0] : qs,
    qs: [...qs],
    datasetId: DATASET_ID,
    sourceCount: sourceItems(qs).length,
  };
}

function sameQs(actual, qs) {
  const normalized = Array.isArray(actual) ? actual : [actual];
  return JSON.stringify(normalized) === JSON.stringify(qs);
}

module.exports = {
  ROOT,
  VOCAB_PATH,
  DATASET_ID,
  POS_MAP,
  readJson,
  writeJson,
  vocabItems,
  sourceItems,
  vocabularyByTarget,
  parseQs,
  qLabel,
  pipelinePaths,
  metadataFor,
  sameQs,
};
