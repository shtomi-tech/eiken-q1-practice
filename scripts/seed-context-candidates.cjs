"use strict";

const path = require("node:path");
const {
  ROOT,
  parseQs,
  pipelinePaths,
  readJson,
  sourceItems,
  writeJson,
  assertExactTargetOrder,
} = require("./lib/context-pipeline.cjs");
const {
  candidateSensesFromMeaning,
  filterEligibleSenses,
} = require("./lib/context-sense-validator.cjs");

const RUNTIME_PATH = path.join(ROOT, "data", "context_2026-1.json");

function segmentSentence(sentence, target, clues) {
  const spans = [];
  const lower = sentence.toLowerCase();
  const addSpan = (text, role) => {
    const index = lower.indexOf(String(text).toLowerCase());
    if (index >= 0) spans.push({ start: index, end: index + text.length, role });
  };
  const targetPattern = String(target).replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace("one's", "(?:one's|my|your|his|her|our|their)");
  const targetMatch = new RegExp(targetPattern, "i").exec(sentence);
  if (targetMatch) spans.push({ start: targetMatch.index, end: targetMatch.index + targetMatch[0].length, role: "target" });
  for (const clue of clues) addSpan(clue.text, "clue");
  spans.sort((a, b) => a.start - b.start || b.end - a.end);
  const selected = [];
  for (const span of spans) {
    if (!selected.some((item) => span.start < item.end && span.end > item.start)) selected.push(span);
  }
  selected.sort((a, b) => a.start - b.start);
  const segments = [];
  let cursor = 0;
  for (const span of selected) {
    if (span.start > cursor) segments.push({ en: sentence.slice(cursor, span.start), role: "core", useJapanese: false });
    segments.push({ en: sentence.slice(span.start, span.end), role: span.role, useJapanese: false });
    cursor = span.end;
  }
  if (cursor < sentence.length) segments.push({ en: sentence.slice(cursor), role: "core", useJapanese: false });
  return segments.length ? segments : [{ en: sentence, role: "core", useJapanese: false }];
}

function buildCandidate(source, legacy, config, final) {
  const fullEnglish = final && config.finalFullEnglish ? config.finalFullEnglish : legacy.fullEnglish;
  const contextClues = final && config.finalContextClues ? config.finalContextClues : legacy.contextClues;
  const candidateSenses = candidateSensesFromMeaning(source.meaning, source.pos);
  const { eligibleSenses, filteredOutSenses } = filterEligibleSenses(candidateSenses, source.pos);
  const explanation = final || !config.finalFullEnglish
    ? config.inferenceExplanation
    : `「${contextClues.map((clue) => clue.text).join("」「")}」が手がかりです。文脈から、${source.target}は「${config.targetSense}」だと推測できます。`;
  return {
    candidateSenses,
    eligibleSenses,
    filteredOutSenses,
    targetSense: config.targetSense,
    senseSelectionReason: config.senseSelectionReason,
    senseConfidence: config.senseConfidence,
    fullEnglish,
    mixedEnglish: [...fullEnglish],
    contextClues,
    inferencePath: [...contextClues.map((clue) => clue.text), `targetSense: ${config.targetSense}`, source.target],
    segments: fullEnglish.map((sentence) => segmentSentence(sentence, source.target, contextClues)),
    supportDecision: "not-needed",
    choices: config.choices,
    answerIndex: 0,
    inferenceExplanation: explanation,
  };
}

function main({ qs = parseQs(), write = true } = {}) {
  const paths = pipelinePaths(qs);
  const authoring = readJson(paths.authoring);
  const sources = sourceItems(qs);
  const runtime = readJson(RUNTIME_PATH);
  const legacyByTarget = new Map(runtime.contexts.map((item) => [item.target, item]));
  const sourceTargets = sources.map((item) => item.target);
  const authoringTargets = Object.keys(authoring.items || {});
  assertExactTargetOrder(authoringTargets, sourceTargets, `${paths.label} authoring`);
  const items = {};
  for (const source of sources) {
    const legacy = legacyByTarget.get(source.target);
    const config = authoring.items[source.target];
    if (!legacy) throw new Error(`${source.target}: existing Context reference is missing`);
    items[source.target] = {
      initial: buildCandidate(source, legacy, config, false),
      final: buildCandidate(source, legacy, config, true),
    };
  }
  const output = { schemaVersion: 1, datasetId: "eiken2-2026-1", qs: [...qs], items };
  if (write) writeJson(paths.candidate, output);
  return output;
}

if (require.main === module) {
  const qs = parseQs();
  const checkOnly = process.argv.includes("--check");
  const output = main({ qs, write: !checkOnly });
  console.log(`${checkOnly ? "candidate seed check" : "candidate seed written"} (${pipelinePaths(qs).label}): ${Object.keys(output.items).join(", ")}`);
}

module.exports = { main, segmentSentence, buildCandidate };
