"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { validateContextItem } = require("./lib/context-validator.cjs");

const ROOT = path.resolve(__dirname, "..");
const CONFIG = {
  "eiken2-2025-3": ["vocab_2025-3.json", "context_2025-3.json"],
  "eiken2-2025-2": ["vocab_2025-2.json", "context_2025-2.json"],
  "eiken2-mock-1": ["vocab_2_mock-1.json", "context_2_mock-1.json"],
  "eiken2-mock-2": ["vocab_2_mock-2.json", "context_2_mock-2.json"],
  "eiken2-mock-3": ["vocab_2_mock-3.json", "context_2_mock-3.json"],
  "eiken2-mock-4": ["vocab_2_mock-4.json", "context_2_mock-4.json"],
};
function read(name) { return JSON.parse(fs.readFileSync(path.join(ROOT, "data", name), "utf8")); }
function surface(item) { return item.word || item.phrase; }

const manifest = read("manifest.json").q1;
let total = 0;
for (const [datasetId, [vocabName, contextName]] of Object.entries(CONFIG)) {
  const vocab = read(vocabName);
  const source = [...(vocab.words || []), ...(vocab.idioms || [])];
  const sourceByTarget = new Map(source.map((item) => [surface(item), item]));
  const payload = read(contextName);
  const review = read(path.join("context-reviews", `${datasetId}.json`));
  const approvedTargets = review.items.filter((item) => item.status === "pass").map((item) => item.target);
  assert.equal(payload.meta.datasetId, datasetId, `${datasetId}: datasetId mismatch`);
  assert.equal(payload.meta.count, payload.contexts.length, `${datasetId}: context count mismatch`);
  assert.equal(manifest[datasetId].contextUrl, `data/${contextName}`, `${datasetId}: manifest contextUrl mismatch`);
  assert.equal(manifest[datasetId].contextTotal, payload.contexts.length, `${datasetId}: manifest contextTotal mismatch`);
  assert.equal(new Set(payload.contexts.map((item) => item.target)).size, payload.contexts.length, `${datasetId}: duplicate target`);
  assert.deepEqual(payload.contexts.map((item) => item.target), approvedTargets, `${datasetId}: runtime must contain every and only review-passed target`);
  const sourceOrder = source.map(surface);
  const projectedOrder = payload.contexts.map((item) => sourceOrder.indexOf(item.target));
  assert.ok(projectedOrder.every((value, index) => value >= 0 && (index === 0 || value > projectedOrder[index - 1])), `${datasetId}: context order differs from Vocabulary Data`);
  for (const item of payload.contexts) {
    const vocabItem = sourceByTarget.get(item.target);
    assert.ok(vocabItem, `${datasetId}/${item.target}: unexpected target`);
    const result = validateContextItem(item, vocabItem, { requireTargetSense: true });
    assert.equal(result.status, "pass", `${datasetId}/${item.target}: ${result.errors.join(" | ")}`);
    assert.equal(item.fullEnglish[0], vocabItem.example,
      `${datasetId}/${item.target}: first sentence must repeat the vocabulary example verbatim`);
  }
  total += payload.contexts.length;
}
assert.equal(total, 455, "review-approved expanded context total changed unexpectedly");
const remaining = Object.keys(CONFIG).flatMap((datasetId) => {
  const review = read(path.join("context-reviews", `${datasetId}.json`));
  return review.items.filter((item) => item.status === "revise").map((item) => `${datasetId}/${item.target}`);
});
assert.deepEqual(remaining, ["eiken2-2025-2/the most of"], "only the invalid official distractor may remain excluded");
console.log(`expanded context datasets: OK (${total} reviewed contexts across 6 datasets)`);
