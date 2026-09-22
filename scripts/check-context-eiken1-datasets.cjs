"use strict";

// 英検1級セットのContext Discoveryデータを検証する。
// data/context-src/eiken1-*.json（原稿）から生成された data/context_1_*.json が
// 2級側と同じ品質規則（context-validator / leakage-validator）を満たし、
// manifest と一致していることを確かめる。

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { validateContextItem } = require("./lib/context-validator.cjs");
const { validateContextLeakage } = require("./lib/context-leakage-validator.cjs");

const ROOT = path.resolve(__dirname, "..");
const SRC_DIR = path.join(ROOT, "data", "context-src");

function read(name) { return JSON.parse(fs.readFileSync(path.join(ROOT, "data", name), "utf8")); }
function surface(item) { return item.word || item.phrase; }

const rounds = fs.readdirSync(SRC_DIR)
  .filter((name) => /^eiken1-.+\.json$/.test(name))
  .map((name) => name.replace(/^eiken1-/, "").replace(/\.json$/, ""))
  .sort();
assert.ok(rounds.length > 0, "英検1級のContext原稿が1件も見つかりません");

const manifest = read("manifest.json").q1;
let total = 0;
for (const round of rounds) {
  const datasetId = `eiken1-${round}`;
  const contextName = `context_1_${round}.json`;
  const vocab = read(`vocab_1_${round}.json`);
  const source = [...(vocab.words || []), ...(vocab.idioms || [])];
  const sourceByTarget = new Map(source.map((item) => [surface(item), item]));
  const payload = read(contextName);

  assert.equal(payload.meta.datasetId, datasetId, `${datasetId}: datasetId mismatch`);
  assert.equal(payload.meta.grade, "EIKEN Grade 1", `${datasetId}: grade mismatch`);
  assert.equal(payload.meta.count, payload.contexts.length, `${datasetId}: context count mismatch`);
  assert.equal(manifest[datasetId].contextUrl, `data/${contextName}`, `${datasetId}: manifest contextUrl mismatch`);
  assert.equal(manifest[datasetId].contextTotal, payload.contexts.length, `${datasetId}: manifest contextTotal mismatch`);
  assert.ok(payload.contexts.length > 0, `${datasetId}: context is empty`);
  assert.ok(payload.contexts.length <= source.length, `${datasetId}: context exceeds Vocabulary Data`);
  assert.equal(new Set(payload.contexts.map((item) => item.target)).size, payload.contexts.length, `${datasetId}: duplicate target`);

  const sourceOrder = source.map(surface);
  const projected = payload.contexts.map((item) => sourceOrder.indexOf(item.target));
  assert.ok(projected.every((value, index) => value >= 0 && (index === 0 || value > projected[index - 1])),
    `${datasetId}: context order differs from Vocabulary Data`);

  for (const item of payload.contexts) {
    const vocabItem = sourceByTarget.get(item.target);
    assert.ok(vocabItem, `${datasetId}/${item.target}: unexpected target`);
    assert.equal(item.level, "EIKEN Grade 1", `${datasetId}/${item.target}: level mismatch`);
    assert.equal(item.fullEnglish[0], vocabItem.example, `${datasetId}/${item.target}: 1文目は語彙データのexampleと一致させる`);
    const result = validateContextItem(item, vocabItem, { requireTargetSense: true });
    assert.equal(result.status, "pass", `${datasetId}/${item.target}: ${result.errors.join(" | ")}`);
    const leakage = validateContextLeakage(item);
    assert.notEqual(leakage.status, "fail", `${datasetId}/${item.target}: leakage FAIL`);
  }
  total += payload.contexts.length;
}
console.log(`eiken1 context datasets: OK (${total} contexts across ${rounds.length} dataset${rounds.length > 1 ? "s" : ""})`);
