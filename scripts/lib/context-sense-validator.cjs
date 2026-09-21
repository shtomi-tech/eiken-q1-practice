"use strict";

const { POS_MAP, compatibleSense, normalizeSense } = require("./context-validator.cjs");

const VALID_CONFIDENCE = new Set(["high", "medium", "low"]);
const POS_LABELS = {
  noun: "noun",
  verb: "verb",
  adjective: "adjective",
  adverb: "adverb",
};

function splitMeaningGroups(value) {
  const groups = [];
  let current = "";
  let depth = 0;
  for (const char of String(value || "")) {
    if (char === "（" || char === "(") depth += 1;
    if (char === "）" || char === ")") depth = Math.max(0, depth - 1);
    if (!depth && ["／", "/", "；", ";"].includes(char)) {
      if (current.trim()) groups.push(current.trim());
      current = "";
    } else {
      current += char;
    }
  }
  if (current.trim()) groups.push(current.trim());
  return groups;
}

function markerPos(group, fallback) {
  const match = String(group).match(/^[（(](名|動|形|副)[）)]/);
  if (!match) return fallback;
  return ({ 名: "noun", 動: "verb", 形: "adjective", 副: "adverb" })[match[1]] || fallback;
}

function cleanSense(group) {
  return String(group || "")
    .replace(/^[（(](名|動|形|副)[）)]\s*/, "")
    .replace(/[（(]複数形\s+[^）)]*[）)]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function candidateSensesFromMeaning(meaning, pos) {
  return splitMeaningGroups(meaning).map((group) => ({
    sense: cleanSense(group),
    pos: markerPos(group, pos),
  }));
}

function filterEligibleSenses(candidateSenses, sourcePos) {
  const candidates = (candidateSenses || []).map(normalizeCandidate);
  const eligibleSenses = candidates.filter((candidate) => candidate.pos === sourcePos);
  const filteredOutSenses = candidates
    .filter((candidate) => candidate.pos !== sourcePos)
    .map((candidate) => ({ ...candidate, reason: "source-pos-mismatch" }));
  return { eligibleSenses, filteredOutSenses };
}

function normalizeCandidate(candidate) {
  return {
    sense: String(candidate?.sense || "").trim(),
    pos: POS_LABELS[candidate?.pos] || candidate?.pos,
  };
}

function validateTargetSense(item, vocab, options = {}) {
  const errors = [];
  const check = (condition, message) => {
    if (!condition) errors.push(message);
  };
  const target = vocab?.word || vocab?.phrase;
  check(item && vocab, "source vocabulary or sense item is missing");
  if (!item || !vocab) return { status: "fail", errors };

  const vocabPos = POS_MAP[vocab.pos] || vocab.pos;
  check(item.target === target, `${target}: target does not match Vocabulary Data`);
  check(item.meaning === vocab.meaning, `${target}: meaning does not match Vocabulary Data`);
  check(item.pos === vocabPos, `${target}: POS does not match Vocabulary Data`);
  check(Array.isArray(item.candidateSenses) && item.candidateSenses.length > 0,
    `${target}: candidateSenses are required`);
  check(typeof item.targetSense === "string" && item.targetSense.trim(), `${target}: targetSense is required`);
  check(typeof item.senseSelectionReason === "string" && item.senseSelectionReason.trim(),
    `${target}: senseSelectionReason is required`);
  check(VALID_CONFIDENCE.has(item.senseConfidence), `${target}: confidence must be high, medium, or low`);

  const expected = candidateSensesFromMeaning(vocab.meaning, vocabPos);
  const actual = (item.candidateSenses || []).map(normalizeCandidate);
  check(actual.length === expected.length, `${target}: candidateSenses do not match parsed meaning groups`);
  for (const expectedGroup of expected) {
    const match = actual.find((candidate) => normalizeSense(candidate.sense) === normalizeSense(expectedGroup.sense));
    check(Boolean(match), `${target}: missing candidate sense group: ${expectedGroup.sense}`);
    if (match) check(match.pos === expectedGroup.pos, `${target}: candidate sense POS is stale: ${match.sense}`);
  }
  const hasPrefilterFields = options.requireEligibleSenses === true
    || Array.isArray(item.eligibleSenses)
    || Array.isArray(item.filteredOutSenses);
  const expectedPrefilter = filterEligibleSenses(expected, vocabPos);
  let eligible = [];
  let filtered = [];
  if (hasPrefilterFields) {
    check(Array.isArray(item.eligibleSenses), `${target}: eligibleSenses are required`);
    check(Array.isArray(item.filteredOutSenses), `${target}: filteredOutSenses are required`);
    eligible = (item.eligibleSenses || []).map(normalizeCandidate);
    filtered = (item.filteredOutSenses || []).map((candidate) => ({
      ...normalizeCandidate(candidate),
      reason: candidate.reason,
    }));
    check(eligible.length > 0, `${target}: eligibleSenses must contain at least one sense`);
    check(
      JSON.stringify(eligible) === JSON.stringify(expectedPrefilter.eligibleSenses),
      `${target}: eligibleSenses do not match deterministic POS pre-filter`,
    );
    check(
      filtered.length === expectedPrefilter.filteredOutSenses.length,
      `${target}: filteredOutSenses count does not match deterministic POS pre-filter`,
    );
    for (const expectedFiltered of expectedPrefilter.filteredOutSenses) {
      const match = filtered.find((candidate) => candidate.sense === expectedFiltered.sense && candidate.pos === expectedFiltered.pos);
      check(Boolean(match), `${target}: missing filtered-out sense: ${expectedFiltered.sense}`);
      if (match) check(match.reason === "source-pos-mismatch", `${target}: wrong filtered-out reason: ${match.sense}`);
    }
    for (const candidate of eligible) {
      check(expected.some((group) => group.sense === candidate.sense && group.pos === candidate.pos),
        `${target}: eligible sense is outside candidateSenses: ${candidate.sense}`);
      check(candidate.pos === vocabPos, `${target}: eligible sense is POS-incompatible: ${candidate.sense}`);
    }
    for (const candidate of filtered) {
      check(!eligible.some((eligibleSense) => eligibleSense.sense === candidate.sense && eligibleSense.pos === candidate.pos),
        `${target}: filtered-out sense remains eligible: ${candidate.sense}`);
      check(!candidate.reason || candidate.reason === "source-pos-mismatch",
        `${target}: wrong filtered-out reason: ${candidate.sense}`);
    }
  }
  const targetGroup = expected.find((group) => compatibleSense(group.sense, item.targetSense));
  check(Boolean(targetGroup), `${target}: targetSense is outside the candidate sense space`);
  if (targetGroup) {
    check(targetGroup.pos === vocabPos, `${target}: targetSense is not POS-compatible with source`);
    const targetCandidate = actual.find((candidate) => normalizeSense(candidate.sense) === normalizeSense(targetGroup.sense));
    if (targetCandidate) check(targetCandidate.pos === vocabPos, `${target}: selected candidate sense is POS-incompatible`);
    if (hasPrefilterFields) {
      check(eligible.some((candidate) => compatibleSense(candidate.sense, targetGroup.sense)),
        `${target}: targetSense is outside eligibleSenses`);
      check(!filtered.some((candidate) => compatibleSense(candidate.sense, targetGroup.sense)),
        `${target}: filtered-out sense was selected as targetSense`);
    }
  }

  return {
    status: errors.length ? "fail" : "pass",
    errors,
    candidateSenses: actual,
    eligibleSenses: hasPrefilterFields ? eligible : undefined,
    filteredOutSenses: hasPrefilterFields ? filtered : undefined,
    expectedPrefilter,
    targetGroup,
    confidence: item.senseConfidence,
    lowConfidence: item.senseConfidence === "low",
    ...options,
  };
}

function assertTargetSense(item, vocab, options = {}) {
  const result = validateTargetSense(item, vocab, options);
  if (result.status !== "pass") throw new Error(result.errors.join("\n"));
  return result;
}

module.exports = {
  VALID_CONFIDENCE,
  splitMeaningGroups,
  cleanSense,
  candidateSensesFromMeaning,
  filterEligibleSenses,
  validateTargetSense,
  assertTargetSense,
};
