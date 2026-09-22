"use strict";

/*
  英検1級セットの Context Discovery（文脈から推測）データを組み立てる。

  入力: data/context-src/eiken1-<round>.json（人が書く原稿）
    { "meta": { "round": "mock-1" },
      "items": [{ "q": 1, "target": "concussion", "sense": "脳震盪", "sentences": ["…", "…"],
                  "clues": [["…", "cause"], ["…", "result"]],
                  "distractors": ["…", "…", "…"], "reason": "…" }] }
  出力: data/context_1_<round>.json（ランタイム用）＋ data/manifest.json の
        contextUrl / contextTotal。

  sentences[0] は語彙データの example をそのまま使う。target は全体でちょうど1回。
  clue は1文の中に収まり、target と重ならず、clue 同士も重ならないこと。
  2級側と同じ context-validator / leakage-validator を通してから書き出す。
*/

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { validateContextItem, POS_MAP } = require("./lib/context-validator.cjs");
const { validateContextLeakage } = require("./lib/context-leakage-validator.cjs");

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SRC_DIR = path.join(ROOT, "data", "context-src");
const GRADE = "EIKEN Grade 1";

function readJson(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
function writeJson(file, value) { fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }
function surface(item) { return item.word || item.phrase; }
function esc(value) { return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }

function targetPattern(target, flags) {
  return new RegExp(`(?<![A-Za-z])${esc(target).replace("one's", "(?:one's|my|your|his|her|our|their)")}(?![A-Za-z])`, flags);
}

function segmentSentence(sentence, target, clues) {
  const spans = [];
  const matches = [...sentence.matchAll(targetPattern(target, "gi"))];
  if (matches.length > 1) throw new Error(`${target}: target occurs more than once in one sentence`);
  if (matches.length === 1) {
    spans.push({ start: matches[0].index, end: matches[0].index + matches[0][0].length, role: "target" });
  }
  for (const clue of clues) {
    const index = sentence.toLowerCase().indexOf(clue.text.toLowerCase());
    if (index < 0) continue;
    if (sentence.toLowerCase().indexOf(clue.text.toLowerCase(), index + 1) >= 0) {
      throw new Error(`${target}: clue appears twice in one sentence: ${clue.text}`);
    }
    spans.push({ start: index, end: index + clue.text.length, role: "clue", clueType: clue.type });
  }
  spans.sort((a, b) => a.start - b.start || b.end - a.end);
  for (let i = 1; i < spans.length; i += 1) {
    if (spans[i].start < spans[i - 1].end) throw new Error(`${target}: target/clue spans overlap`);
  }
  const segments = [];
  let cursor = 0;
  for (const span of spans) {
    if (span.start > cursor) segments.push({ en: sentence.slice(cursor, span.start), role: "core", useJapanese: false });
    segments.push({
      en: sentence.slice(span.start, span.end),
      role: span.role,
      ...(span.clueType ? { clueType: span.clueType } : {}),
      useJapanese: false,
    });
    cursor = span.end;
  }
  if (cursor < sentence.length) segments.push({ en: sentence.slice(cursor), role: "core", useJapanese: false });
  return segments;
}

function explanationFor(source, target, sense) {
  const quoted = source.clues.map(([text]) => `「${text}」`).join("と");
  const reason = String(source.reason).replace(/[。]$/, "");
  return `${quoted}という手がかりから、${reason}。そのため、${target}は「${sense}」だと推測できます。`;
}

function runtimeItem(vocab, source) {
  const target = surface(vocab);
  const sense = source.sense;
  const sentences = source.sentences;
  if (!Array.isArray(sentences) || sentences.length < 2 || sentences.length > 3) {
    throw new Error(`${target}: sentences must contain 2-3 sentences`);
  }
  if (sentences[0] !== vocab.example) {
    throw new Error(`${target}: first sentence must repeat the vocabulary example verbatim`);
  }
  const story = sentences.join(" ");
  const occurrences = [...story.matchAll(targetPattern(target, "gi"))].length;
  if (occurrences !== 1) throw new Error(`${target}: target must occur exactly once (found ${occurrences})`);
  const clues = source.clues.map(([text, type]) => ({ text, type }));
  if (clues.length < 2 || clues.length > 3) throw new Error(`${target}: 2-3 clues are required`);
  for (const clue of clues) {
    if (!sentences.some((sentence) => sentence.toLowerCase().includes(clue.text.toLowerCase()))) {
      throw new Error(`${target}: clue is not inside a single sentence: ${clue.text}`);
    }
  }
  const choices = [sense, ...source.distractors];
  const item = {
    q: vocab.q,
    type: vocab.phrase ? "idiom" : "word",
    target,
    meaning: vocab.meaning,
    targetSense: sense,
    pos: POS_MAP[vocab.pos] || vocab.pos,
    level: GRADE,
    fullEnglish: [...sentences],
    mixedEnglish: [...sentences],
    contextClues: clues,
    inferencePath: [...clues.map((clue) => clue.text), `targetSense: ${sense}`, target],
    segments: sentences.map((sentence) => segmentSentence(sentence, target, clues)),
    choices,
    answerIndex: 0,
    inferenceExplanation: explanationFor(source, target, sense),
    quality: { targetOccurrence: 1, clueCount: clues.length, targetProtected: true, cluesProtected: true },
  };
  if (/[\u0400-\u04ff\uac00-\ud7af\u0600-\u06ff]/.test(item.inferenceExplanation)) {
    throw new Error(`${target}: inferenceExplanation contains unexpected non-Japanese script`);
  }
  const result = validateContextItem(item, vocab, { requireTargetSense: true });
  if (result.status !== "pass") throw new Error(`${target}: ${result.errors.join(" | ")}`);
  const leakage = validateContextLeakage(item);
  if (leakage.status === "fail") {
    throw new Error(`${target}: leakage ${leakage.status}: ${leakage.findings.map((f) => `${f.type}/${f.text}`).join(", ")}`);
  }
  if (leakage.status === "warn" && source.leakageReview?.status !== "accepted") {
    throw new Error(`${target}: leakage WARN requires source leakageReview.status = "accepted"`);
  }
  return item;
}

function buildRound(round) {
  const datasetId = `eiken1-${round}`;
  const source = readJson(path.join(SRC_DIR, `${datasetId}.json`));
  const vocab = readJson(path.join(ROOT, "data", `vocab_1_${round}.json`));
  const sourceItems = [...(vocab.words || []), ...(vocab.idioms || [])];
  const byTarget = new Map(sourceItems.map((item) => [surface(item), item]));
  const order = sourceItems.map(surface);
  const seen = new Set();
  const items = [];
  for (const entry of source.items) {
    const vocabItem = byTarget.get(entry.target);
    if (!vocabItem) throw new Error(`${datasetId}: ${entry.target} is not in vocab_1_${round}.json`);
    if (vocabItem.q !== entry.q) throw new Error(`${datasetId}: ${entry.target} belongs to q=${vocabItem.q}, not q=${entry.q}`);
    if (seen.has(entry.target)) throw new Error(`${datasetId}: duplicate target ${entry.target}`);
    seen.add(entry.target);
    items.push(runtimeItem(vocabItem, entry));
  }
  items.sort((a, b) => order.indexOf(a.target) - order.indexOf(b.target));
  const outputName = `context_1_${round}.json`;
  writeJson(path.join(ROOT, "data", outputName), {
    meta: {
      datasetId,
      grade: GRADE,
      source: "Hand-authored mini-contexts for lexical inferencing",
      version: 1,
      count: items.length,
    },
    contexts: items,
  });
  const manifestPath = path.join(ROOT, "data", "manifest.json");
  const manifest = readJson(manifestPath);
  const entry = manifest.q1[datasetId];
  if (!entry) throw new Error(`${datasetId}: manifest entry is missing`);
  const rebuilt = {};
  for (const [key, value] of Object.entries(entry)) {
    if (key === "contextUrl" || key === "contextTotal") continue;
    rebuilt[key] = value;
    if (key === "questionsUrl") {
      rebuilt.contextUrl = `data/${outputName}`;
      rebuilt.contextTotal = items.length;
    }
  }
  if (!rebuilt.contextUrl) {
    rebuilt.contextUrl = `data/${outputName}`;
    rebuilt.contextTotal = items.length;
  }
  manifest.q1[datasetId] = rebuilt;
  writeJson(manifestPath, manifest);
  console.log(`${datasetId}: ${items.length} contexts -> data/${outputName}`);
  return items.length;
}

function rounds() {
  const args = process.argv.slice(2).filter((arg) => !arg.startsWith("--"));
  if (args.length) return args;
  return fs.readdirSync(SRC_DIR)
    .filter((name) => /^eiken1-.+\.json$/.test(name))
    .map((name) => name.replace(/^eiken1-/, "").replace(/\.json$/, ""));
}

let total = 0;
for (const round of rounds()) total += buildRound(round);
console.log(`built ${total} eiken1 contexts`);
