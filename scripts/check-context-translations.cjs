"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const readJson = (relativePath) => JSON.parse(fs.readFileSync(path.join(ROOT, relativePath), "utf8"));
const manifest = readJson("data/manifest.json");
const japanese = /[ぁ-んァ-ヶ一-龠々]/;
let total = 0;
let datasetCount = 0;

for (const [datasetId, dataset] of Object.entries(manifest.q1)) {
  if (!dataset.contextUrl) continue;
  datasetCount += 1;
  assert.ok(dataset.contextTranslationUrl, `${datasetId}: contextTranslationUrl is required`);
  const contexts = readJson(dataset.contextUrl).contexts;
  const translations = readJson(dataset.contextTranslationUrl);
  assert.equal(translations.schemaVersion, 1, `${datasetId}: unknown translation schema`);
  assert.equal(translations.datasetId, datasetId, `${datasetId}: datasetId mismatch`);
  assert.equal(translations.count, contexts.length, `${datasetId}: count mismatch`);
  assert.equal(translations.items.length, contexts.length, `${datasetId}: item count mismatch`);

  translations.items.forEach((translation, index) => {
    const context = contexts[index];
    assert.equal(translation.q, context.q, `${datasetId} #${index}: q mismatch`);
    assert.equal(translation.target, context.target, `${datasetId} #${index}: target mismatch`);
    assert.equal(translation.english, context.fullEnglish[1], `${datasetId} ${context.target}: English mismatch`);
    assert.ok(japanese.test(translation.japanese), `${datasetId} ${context.target}: Japanese translation is required`);
    assert.match(translation.japanese, /[。！？]$/, `${datasetId} ${context.target}: sentence ending is required`);
    total += 1;
  });
}

assert.equal(datasetCount, 31, "context translation dataset count changed unexpectedly");
assert.equal(total, 2887, "context translation item count changed unexpectedly");
console.log(`context second-sentence translations: OK (${total} items across ${datasetCount} datasets)`);
