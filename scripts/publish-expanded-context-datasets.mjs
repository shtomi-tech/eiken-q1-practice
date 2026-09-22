"use strict";

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const OUTPUTS = {
  "eiken2-2025-3": "context_2025-3.json", "eiken2-2025-2": "context_2025-2.json",
  "eiken2-mock-1": "context_2_mock-1.json", "eiken2-mock-2": "context_2_mock-2.json",
  "eiken2-mock-3": "context_2_mock-3.json", "eiken2-mock-4": "context_2_mock-4.json",
};
function readJson(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
function writeJson(file, value) { fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }

for (const [datasetId, outputName] of Object.entries(OUTPUTS)) {
  const candidates = readJson(path.join(ROOT, "data", "context-candidates", `${datasetId}.json`));
  const review = readJson(path.join(ROOT, "data", "context-reviews", `${datasetId}.json`));
  const statusByTarget = new Map(review.items.map((item) => [item.target, item.status]));
  const contexts = candidates.contexts
    .filter((item) => statusByTarget.get(item.target) === "pass")
    .map((item) => {
      const runtime = structuredClone(item);
      delete runtime.manualReview;
      return runtime;
    });
  writeJson(path.join(ROOT, "data", outputName), {
    meta: {
      datasetId, grade: "EIKEN Grade 2", source: "Reviewed mini-contexts for lexical inferencing",
      version: 1, count: contexts.length,
    },
    contexts,
  });
  console.log(`${datasetId}: published ${contexts.length}/${candidates.contexts.length}`);
}
