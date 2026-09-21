"use strict";

const { main: generateDraft } = require("./generate-context-draft.cjs");
const { sourceItems } = require("./lib/context-pipeline.cjs");

function main({ write = true } = {}) {
  const sources = sourceItems([3]);
  if (sources.length !== 4) throw new Error(`Expected exactly four q=3 source items, found ${sources.length}`);
  return generateDraft({ qs: [3], write });
}

if (require.main === module) {
  const checkOnly = process.argv.includes("--check");
  const draft = main({ write: !checkOnly });
  console.log(`${checkOnly ? "q=3 draft source check" : "q=3 draft generated"}: ${draft.items.map((item) => item.source.target).join(", ")}`);
}

module.exports = { main, sourceItems };
