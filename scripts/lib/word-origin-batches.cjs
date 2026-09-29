"use strict";

const assert = require("node:assert/strict");

function appliedBatchIds(meta = {}) {
  const ids = new Set(
    (Array.isArray(meta.appliedBatches) ? meta.appliedBatches : [])
      .map((entry) => entry?.batchId)
      .filter((batchId) => typeof batchId === "string" && batchId.trim()),
  );
  if (typeof meta.lastAppliedBatch === "string" && meta.lastAppliedBatch.trim()) {
    ids.add(meta.lastAppliedBatch);
  }
  return ids;
}

function assertBatchNotApplied(meta, batchId) {
  assert.equal(
    appliedBatchIds(meta).has(batchId),
    false,
    batchId + ": 既に適用済みです",
  );
}

function validateAppliedBatchHistory(meta = {}) {
  if (meta.appliedBatches === undefined) return;
  assert.ok(Array.isArray(meta.appliedBatches), "meta.appliedBatchesは配列である必要があります");
  const ids = meta.appliedBatches.map((entry, index) => {
    assert.ok(entry && typeof entry === "object" && !Array.isArray(entry), "meta.appliedBatches[" + index + "]が不正です");
    assert.ok(typeof entry.batchId === "string" && entry.batchId.trim(), "meta.appliedBatches[" + index + "].batchIdが必要です");
    return entry.batchId;
  });
  assert.equal(new Set(ids).size, ids.length, "meta.appliedBatches.batchIdに重複があります");
  if (meta.lastAppliedBatch !== undefined) {
    assert.equal(ids.at(-1), meta.lastAppliedBatch, "meta.lastAppliedBatchはappliedBatchesの最後と一致する必要があります");
  }
}

module.exports = { appliedBatchIds, assertBatchNotApplied, validateAppliedBatchHistory };
