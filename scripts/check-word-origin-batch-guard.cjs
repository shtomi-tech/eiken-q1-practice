"use strict";

const assert = require("node:assert/strict");
const {
  assertBatchNotApplied,
  validateAppliedBatchHistory,
} = require("./lib/word-origin-batches.cjs");

const history = {
  lastAppliedBatch: "batch-003",
  appliedBatches: [
    { batchId: "batch-001" },
    { batchId: "batch-002" },
    { batchId: "batch-003" },
  ],
};

for (const batchId of ["batch-001", "batch-002", "batch-003"]) {
  assert.throws(() => assertBatchNotApplied(history, batchId), /既に適用済みです/, batchId + "を再適用できてはいけません");
}
assert.doesNotThrow(() => assertBatchNotApplied(history, "batch-004"));
assert.throws(
  () => validateAppliedBatchHistory({ appliedBatches: [{ batchId: "batch-001" }, { batchId: "batch-001" }] }),
  /batchIdに重複があります/,
);
assert.throws(
  () => validateAppliedBatchHistory({ lastAppliedBatch: "batch-002", appliedBatches: [{ batchId: "batch-001" }] }),
  /最後と一致する必要があります/,
);
assert.doesNotThrow(() => validateAppliedBatchHistory({ lastAppliedBatch: "legacy-batch" }));

console.log("word origin batch guard: OK (all historical batch IDs are protected)");
