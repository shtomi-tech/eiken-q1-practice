"use strict";

const JAPANESE = /[\u3040-\u30ff\u3400-\u9fff]/;
const POS_MAP = {
  "名詞": "noun",
  "動詞": "verb",
  "形容詞": "adjective",
  "副詞": "adverb",
};

function normalizeSense(value) {
  return String(value || "")
    .normalize("NFKC")
    .replace(/[（(][^）)]*[）)]/g, "")
    .replace(/[、；;,]/g, "")
    .replace(/\s+/g, "")
    .trim();
}

function senseParts(value) {
  return String(value || "")
    .split(/[；;]/)
    .flatMap((part) => part.split(/[、,]/))
    .map((part) => part.trim())
    .filter(Boolean);
}

function compatibleSense(meaning, targetSense) {
  const targetParts = senseParts(targetSense).map(normalizeSense).filter(Boolean);
  const meaningParts = senseParts(meaning).map(normalizeSense).filter(Boolean);
  return targetParts.some((target) => meaningParts.some((meaningPart) => (
    target === meaningPart || target.includes(meaningPart) || meaningPart.includes(target)
  )));
}

function occurrenceCount(text, target) {
  const escaped = String(target).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const pattern = new RegExp(`(?<![A-Za-z])${escaped}(?![A-Za-z])`, "gi");
  return [...String(text).matchAll(pattern)].length;
}

function segmentProjection(segments, useJapanese) {
  return segments.map((sentence) => sentence.map((segment) => (
    useJapanese && segment.useJapanese ? segment.ja : segment.en
  )).join(""));
}

function validateContextItem(item, vocab, options = {}) {
  const errors = [];
  const requireTargetSense = options.requireTargetSense !== false;
  const check = (condition, message) => {
    if (!condition) errors.push(message);
  };
  const target = vocab?.word || vocab?.phrase;
  const correctSense = item?.targetSense || item?.meaning;

  check(item && vocab, "source vocabulary or context item is missing");
  if (!item || !vocab) return { status: "fail", errors };
  check(item.q === vocab.q, `${item.target}: q does not match Vocabulary Data`);
  check(item.target === target, `${target}: target does not match Vocabulary Data`);
  check(item.meaning === vocab.meaning, `${target}: meaning does not match Vocabulary Data`);
  check(item.pos === POS_MAP[vocab.pos] || item.pos === vocab.pos, `${target}: POS does not match Vocabulary Data`);
  if (requireTargetSense) {
    check(typeof item.targetSense === "string" && item.targetSense.trim(), `${target}: targetSense is required`);
    check(compatibleSense(item.meaning, item.targetSense), `${target}: targetSense is incompatible with meaning`);
  }

  check(Array.isArray(item.fullEnglish) && item.fullEnglish.length >= 2 && item.fullEnglish.length <= 3,
    `${target}: fullEnglish must contain 2-3 sentences`);
  const fullStory = (item.fullEnglish || []).join(" ");
  check(!JAPANESE.test(fullStory), `${target}: fullEnglish must be 100% English`);
  check(occurrenceCount(fullStory, target) === 1, `${target}: target must occur once in fullEnglish`);

  check(Array.isArray(item.contextClues) && item.contextClues.length >= 2,
    `${target}: at least two context clues are required`);
  for (const clue of item.contextClues || []) {
    check(fullStory.toLowerCase().includes(String(clue.text).toLowerCase()),
      `${target}: clue is absent from fullEnglish: ${clue.text}`);
  }

  check(Array.isArray(item.segments) && item.segments.length === (item.fullEnglish || []).length,
    `${target}: segments must align with fullEnglish`);
  check(Array.isArray(item.mixedEnglish) && item.mixedEnglish.length === (item.fullEnglish || []).length,
    `${target}: mixedEnglish must align with fullEnglish`);
  if (Array.isArray(item.segments) && Array.isArray(item.fullEnglish) && Array.isArray(item.mixedEnglish)) {
    check(JSON.stringify(segmentProjection(item.segments, false)) === JSON.stringify(item.fullEnglish),
      `${target}: segments do not reconstruct fullEnglish`);
    check(JSON.stringify(segmentProjection(item.segments, true)) === JSON.stringify(item.mixedEnglish),
      `${target}: segments do not reconstruct mixedEnglish`);
  }

  const flatSegments = (item.segments || []).flat();
  const targetSegments = flatSegments.filter((segment) => segment.role === "target");
  check(targetSegments.length === 1, `${target}: exactly one target segment is required`);
  if (targetSegments.length === 1) {
    check(targetSegments[0].en === target, `${target}: target segment is not protected`);
    check(targetSegments[0].useJapanese === false, `${target}: target cannot use Japanese`);
  }
  for (const clue of item.contextClues || []) {
    const clueSegments = flatSegments.filter((segment) => String(segment.en).toLowerCase().includes(String(clue.text).toLowerCase()));
    check(clueSegments.length > 0, `${target}: clue segment is missing: ${clue.text}`);
    check(clueSegments.every((segment) => segment.role === "clue" && segment.useJapanese === false),
      `${target}: clue cannot use Japanese: ${clue.text}`);
  }
  for (const segment of flatSegments) {
    check(["target", "clue", "core", "background", "difficult", "difficult-non-clue"].includes(segment.role),
      `${target}: unknown segment role: ${segment.role}`);
    if (segment.useJapanese) {
      check(segment.role !== "target" && segment.role !== "clue", `${target}: target/clue cannot use Japanese`);
      check(typeof segment.supportReason === "string" && segment.supportReason.trim(),
        `${target}: Japanese support requires supportReason`);
    }
  }
  if (item.supportDecision === "needed") {
    check(flatSegments.some((segment) => segment.useJapanese), `${target}: supportDecision says needed but no segment uses Japanese`);
  }

  check(Array.isArray(item.choices) && item.choices.length === 4, `${target}: exactly four choices are required`);
  if (Array.isArray(item.choices)) {
    check(new Set(item.choices).size === 4, `${target}: choices must be unique`);
    check(item.choices.filter((choice) => choice === correctSense).length === 1,
      `${target}: targetSense must occur exactly once in choices`);
    check(item.choices[item.answerIndex] === correctSense, `${target}: answerIndex must point to targetSense`);
    const otherSenses = senseParts(item.meaning)
      .map(normalizeSense)
      .filter((sense) => sense && !senseParts(item.targetSense || item.meaning).map(normalizeSense).includes(sense));
    check(!item.choices.some((choice) => otherSenses.includes(normalizeSense(choice))),
      `${target}: another known sense is used as a distractor`);
  }

  check(typeof item.inferenceExplanation === "string" && item.inferenceExplanation.trim(),
    `${target}: inferenceExplanation is required`);
  if (item.inferenceExplanation) {
    check(item.inferenceExplanation.includes(correctSense), `${target}: explanation must identify targetSense`);
    for (const clue of item.contextClues || []) {
      check(item.inferenceExplanation.toLowerCase().includes(String(clue.text).toLowerCase()),
        `${target}: explanation must reference clue: ${clue.text}`);
    }
  }
  return {
    status: errors.length ? "fail" : "pass",
    errors,
    supportCount: flatSegments.filter((segment) => segment.useJapanese).length,
  };
}

function assertContextItem(item, vocab, options = {}) {
  const result = validateContextItem(item, vocab, options);
  if (result.status !== "pass") throw new Error(result.errors.join("\n"));
  return result;
}

module.exports = {
  POS_MAP,
  compatibleSense,
  normalizeSense,
  senseParts,
  segmentProjection,
  validateContextItem,
  assertContextItem,
};
