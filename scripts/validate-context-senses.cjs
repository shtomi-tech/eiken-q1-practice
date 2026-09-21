"use strict";

const assert = require("node:assert/strict");
const {
  parseQs,
  pipelinePaths,
  readJson,
  sourceItems,
  vocabularyByTarget,
} = require("./lib/context-pipeline.cjs");
const { validateTargetSense } = require("./lib/context-sense-validator.cjs");

function main({ qs = parseQs(["--q", "6,7"]), write = false } = {}) {
  const paths = pipelinePaths(qs);
  const candidates = readJson(paths.candidate).items || {};
  const vocabulary = vocabularyByTarget();
  const results = [];
  for (const source of sourceItems(qs)) {
    const entry = candidates[source.target];
    assert.ok(entry?.final, `${source.target}: final sense selection is missing`);
    const finalItem = { ...source, ...entry.final };
    const result = validateTargetSense(finalItem, vocabulary.get(source.target));
    assert.equal(result.status, "pass", `${source.target}: final sense validation failed\n${result.errors.join("\n")}`);
    results.push({ target: source.target, result });
  }
  if (write) throw new Error("Sense selection validator does not write production data");
  return results;
}

if (require.main === module) {
  const qs = parseQs();
  const results = main({ qs });
  console.log(`target sense validation: PASS (${results.length} items: ${results.map((item) => item.target).join(", ")})`);
}

module.exports = { main };
