"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const readJson = (file) => JSON.parse(fs.readFileSync(path.join(ROOT, file), "utf8"));
const contextData = readJson("data/context_2026-1.json");
const vocabData = readJson("data/vocab_2026-1.json");
const PILOT_TARGETS = ["bride", "lawyer", "warrior", "surgeon"];
const JAPANESE = /[\u3040-\u30ff\u3400-\u9fff]/;
const POS_MAP = {
  "名詞": "noun",
  "動詞": "verb",
  "形容詞": "adjective",
  "副詞": "adverb",
};
const MANUAL_REVIEW_REQUIRED = [
  "natural English",
  "target is the main unknown",
  "direct definition absence",
  "synonym leakage absence",
  "single coherent scene",
];

function escapeRegExp(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function occurrenceCount(text, target) {
  const pattern = new RegExp(`(?<![A-Za-z])${escapeRegExp(target)}(?![A-Za-z])`, "gi");
  return [...String(text).matchAll(pattern)].length;
}

function vocabularyItem(target) {
  return [...(vocabData.words || []), ...(vocabData.idioms || [])]
    .find((item) => (item.word || item.phrase) === target);
}

function contextItem(target) {
  return (contextData.contexts || []).find((item) => item.target === target);
}

function segmentProjection(segments, useJapanese) {
  return segments.map((sentence) => sentence.map((segment) => {
    if (useJapanese && segment.useJapanese) return segment.ja;
    return segment.en;
  }).join(""));
}

function validateItem(target) {
  const vocab = vocabularyItem(target);
  const item = contextItem(target);
  assert.ok(vocab, `${target}: vocabulary item is missing`);
  assert.ok(item, `${target}: context item is missing`);
  assert.equal(item.q, 1, `${target}: pilot must remain in q=1`);
  assert.equal(item.meaning, vocab.meaning, `${target}: meaning must match vocabulary data`);
  assert.equal(item.pos, POS_MAP[vocab.pos], `${target}: POS must match vocabulary data`);
  assert.ok(Array.isArray(item.fullEnglish) && item.fullEnglish.length >= 2 && item.fullEnglish.length <= 3,
    `${target}: fullEnglish must contain 2-3 sentences`);
  const fullStory = item.fullEnglish.join(" ");
  assert.equal(occurrenceCount(fullStory, target), 1, `${target}: target must occur once in fullEnglish`);
  assert.ok(!JAPANESE.test(fullStory), `${target}: fullEnglish must be 100% English`);

  assert.ok(Array.isArray(item.contextClues) && item.contextClues.length >= 2,
    `${target}: at least two context clues are required`);
  for (const clue of item.contextClues) {
    assert.ok(fullStory.toLowerCase().includes(clue.text.toLowerCase()), `${target}: clue is absent: ${clue.text}`);
  }

  for (const key of ["senseConsistent", "posConsistent", "targetIsMainUnknown", "hasMultipleClues",
    "noDirectDefinition", "noSynonymLeakage", "contextIsCoherent", "difficultyAppropriate", "naturalEnglish"]) {
    assert.equal(item.validation?.[key], true, `${target}: validation.${key} must be true`);
  }

  assert.ok(Array.isArray(item.segments) && item.segments.length === item.fullEnglish.length,
    `${target}: segments must align with fullEnglish`);
  assert.ok(Array.isArray(item.mixedEnglish) && item.mixedEnglish.length === item.fullEnglish.length,
    `${target}: mixedEnglish must align with fullEnglish`);
  assert.deepEqual(segmentProjection(item.segments, false), item.fullEnglish,
    `${target}: segments must reconstruct fullEnglish`);
  assert.deepEqual(segmentProjection(item.segments, true), item.mixedEnglish,
    `${target}: segments must reconstruct mixedEnglish`);

  const flatSegments = item.segments.flat();
  const targetSegments = flatSegments.filter((segment) => segment.role === "target");
  assert.equal(targetSegments.length, 1, `${target}: exactly one target segment is required`);
  assert.equal(targetSegments[0].en, target, `${target}: target segment must contain the target`);
  assert.equal(targetSegments[0].useJapanese, false, `${target}: target must remain English`);
  for (const clue of item.contextClues) {
    const clueSegments = flatSegments.filter((segment) => segment.en.toLowerCase().includes(clue.text.toLowerCase()));
    assert.ok(clueSegments.length > 0, `${target}: clue segment is missing: ${clue.text}`);
    assert.ok(clueSegments.every((segment) => segment.role === "clue" && segment.useJapanese === false),
      `${target}: clue must remain English: ${clue.text}`);
  }
  for (const segment of flatSegments) {
    assert.ok(["target", "clue", "core", "background", "difficult"].includes(segment.role),
      `${target}: unknown segment role: ${segment.role}`);
    if (segment.useJapanese) {
      assert.notEqual(segment.role, "target", `${target}: target cannot be Japanese`);
      assert.notEqual(segment.role, "clue", `${target}: clue cannot be Japanese`);
      assert.ok(segment.ja && JAPANESE.test(segment.ja), `${target}: Japanese support must contain Japanese text`);
    }
  }

  assert.ok(Array.isArray(item.choices) && item.choices.length === 4, `${target}: exactly four choices are required`);
  assert.equal(new Set(item.choices).size, 4, `${target}: choices must be unique`);
  assert.equal(item.choices.filter((choice) => choice === item.meaning).length, 1,
    `${target}: correct meaning must appear exactly once in choices`);
  assert.equal(item.choices[item.answerIndex], item.meaning, `${target}: answerIndex must point to the meaning`);
  assert.ok(item.inferenceExplanation, `${target}: inferenceExplanation is required`);
  for (const clue of item.contextClues) {
    assert.ok(item.inferenceExplanation.toLowerCase().includes(clue.text.toLowerCase()),
      `${target}: explanation must refer to clue: ${clue.text}`);
  }
  assert.equal(item.quality?.targetOccurrence, 1, `${target}: quality targetOccurrence must be 1`);
  assert.equal(item.quality?.clueCount, item.contextClues.length, `${target}: quality clueCount is stale`);
  assert.equal(item.quality?.targetProtected, true, `${target}: target protection metadata is required`);
  assert.equal(item.quality?.cluesProtected, true, `${target}: clue protection metadata is required`);
  assert.equal(item.quality?.manualReview, "pass", `${target}: manual review must be marked pass`);

  return { item, vocab };
}

assert.equal(contextData.meta?.count, 68, "context dataset count must remain 68");
const pilot = PILOT_TARGETS.map(validateItem);
assert.deepEqual(pilot.map(({ item }) => item.target), PILOT_TARGETS, "pilot target order must be stable");

console.log(`context pilot validator: OK (${PILOT_TARGETS.length} q=1 items)`);
console.log(`manual review required: ${MANUAL_REVIEW_REQUIRED.join(", ")}`);
for (const { item } of pilot) {
  console.log(`\nTARGET: ${item.target}\nFULL ENGLISH:\n${item.fullEnglish.map((line) => `- ${line}`).join("\n")}\nMIXED:\n${item.mixedEnglish.map((line) => `- ${line}`).join("\n")}\nCLUES:\n${item.contextClues.map((clue) => `- ${clue.type}: ${clue.text}`).join("\n")}\nCHOICES:\n${item.choices.map((choice, index) => `${String.fromCharCode(65 + index)}. ${choice}`).join("\n")}\nANSWER: ${item.choices[item.answerIndex]}\nEXPLANATION: ${item.inferenceExplanation}\nVALIDATION: PASS`);
}
