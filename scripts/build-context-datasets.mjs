"use strict";

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { validateContextItem, senseParts, occurrenceCount } = require("./lib/context-validator.cjs");
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const MODEL = process.env.CONTEXT_GENERATION_MODEL || "gemini-3.5-flash-lite";
const API_KEY = String(process.env.GEMINI_API_KEY || "").trim();
const DATASETS = {
  "eiken2-2025-3": ["vocab_2025-3.json", "context_2025-3.json"],
  "eiken2-2025-2": ["vocab_2025-2.json", "context_2025-2.json"],
  "eiken2-mock-1": ["vocab_2_mock-1.json", "context_2_mock-1.json"],
  "eiken2-mock-2": ["vocab_2_mock-2.json", "context_2_mock-2.json"],
  "eiken2-mock-3": ["vocab_2_mock-3.json", "context_2_mock-3.json"],
  "eiken2-mock-4": ["vocab_2_mock-4.json", "context_2_mock-4.json"],
};
const POS_MAP = {
  "名詞": "noun", "動詞": "verb", "形容詞": "adjective", "副詞": "adverb",
  "副詞句": "adverbial phrase", "句動詞": "phrasal verb", "名詞句": "noun phrase",
  "形容詞句": "adjective phrase",
};

function readJson(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
function writeJson(file, value) { fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }
function surface(item) { return item.word || item.phrase; }
function vocabItems(vocab) { return [...(vocab.words || []), ...(vocab.idioms || [])]; }
function esc(value) { return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }

const responseSchema = {
  type: "array",
  items: {
    type: "object",
    properties: {
      target: { type: "string" },
      targetSense: { type: "string" },
      fullEnglish: { type: "array", minItems: 2, maxItems: 3, items: { type: "string" } },
      contextClues: {
        type: "array", minItems: 2, maxItems: 3,
        items: {
          type: "object",
          properties: { text: { type: "string" }, type: { type: "string" } },
          required: ["text", "type"], additionalProperties: false,
        },
      },
      choices: { type: "array", minItems: 4, maxItems: 4, items: { type: "string" } },
      inferenceExplanation: { type: "string" },
    },
    required: ["target", "targetSense", "fullEnglish", "contextClues", "choices", "inferenceExplanation"],
    additionalProperties: false,
  },
};

function promptFor(items) {
  const inputs = items.map((item) => ({
    q: item.q, target: surface(item), meaning: item.meaning, pos: POS_MAP[item.pos] || item.pos,
    allowedTargetSenses: senseParts(item.meaning), example: item.example,
  }));
  return `Create EIKEN Grade 2 Context Discovery learning items for every input record.\n
Rules:\n
- Select targetSense exactly from allowedTargetSenses. Never combine or rewrite it.\n
- Write one coherent 2-3 sentence English scene. The first sentence MUST be the supplied example verbatim; it already contains the target. Add 1-2 supporting sentences about the same scene. The target must occur exactly once in the whole context.\n
- The target must be the main unknown. Use simple English around it.\n
- Supply 2-3 informative, reasonably independent clue phrases copied exactly from fullEnglish. Each clue must sit wholly inside one sentence and be a natural meaningful phrase, not a broken fragment. Clues must not contain, cross, or overlap the target and must not overlap each other.\n
- Do not directly define, translate, or immediately restate the target with an answer-equivalent synonym. Prefer situation, behavior, cause, contrast, and result.\n
- choices are Japanese, unique, exactly four, with targetSense exactly once at index 0. Do not use another sense of the target as a distractor. Distractors should share a plausible semantic area and grammatical category.\n
- inferenceExplanation is natural, concise Japanese. Quote every clue text exactly, explain the inference, and finish with「そのため、TARGETは「TARGET_SENSE」だと推測できます。」using the actual target and targetSense.\n
- Return records in exactly the input order.\n
INPUT:\n${JSON.stringify(inputs)}`;
}

async function generate(items) {
  if (!API_KEY) throw new Error("GEMINI_API_KEY is required");
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`;
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-goog-api-key": API_KEY },
    body: JSON.stringify({
      contents: [{ role: "user", parts: [{ text: promptFor(items) }] }],
      generationConfig: {
        temperature: 0.25,
        responseMimeType: "application/json",
        responseJsonSchema: responseSchema,
      },
    }),
  });
  if (!response.ok) throw new Error(`Gemini HTTP ${response.status}: ${(await response.text()).slice(0, 500)}`);
  const payload = await response.json();
  const text = payload.candidates?.[0]?.content?.parts?.map((part) => part.text || "").join("");
  if (!text) throw new Error(`Gemini returned no text: ${JSON.stringify(payload).slice(0, 500)}`);
  return JSON.parse(text);
}

function segmentSentence(sentence, target, clues) {
  const spans = [];
  const targetMatch = [...sentence.matchAll(new RegExp(esc(target), "gi"))];
  if (targetMatch.length > 1) throw new Error(`${target}: target occurs more than once in one sentence`);
  if (targetMatch.length === 1) {
    spans.push({ start: targetMatch[0].index, end: targetMatch[0].index + targetMatch[0][0].length, role: "target" });
  }
  for (const clue of clues) {
    const index = sentence.toLowerCase().indexOf(clue.text.toLowerCase());
    if (index >= 0) spans.push({ start: index, end: index + clue.text.length, role: "clue", clueType: clue.type });
  }
  spans.sort((a, b) => a.start - b.start || b.end - a.end);
  for (let i = 1; i < spans.length; i += 1) {
    if (spans[i].start < spans[i - 1].end) throw new Error(`${target}: target/clue spans overlap`);
  }
  const segments = [];
  let cursor = 0;
  for (const span of spans) {
    if (span.start > cursor) segments.push({ en: sentence.slice(cursor, span.start), role: "core", useJapanese: false });
    segments.push({ en: sentence.slice(span.start, span.end), role: span.role, ...(span.clueType ? { clueType: span.clueType } : {}), useJapanese: false });
    cursor = span.end;
  }
  if (cursor < sentence.length) segments.push({ en: sentence.slice(cursor), role: "core", useJapanese: false });
  return segments;
}

function runtimeItem(vocab, generated) {
  const target = surface(vocab);
  if (generated.target !== target) throw new Error(`${target}: generated target mismatch (${generated.target})`);
  if (occurrenceCount(generated.fullEnglish.join(" "), target) !== 1) {
    throw new Error(`${target}: target occurrence must be one: ${generated.fullEnglish.join(" ")}`);
  }
  if (generated.choices[0] !== generated.targetSense) throw new Error(`${target}: correct choice must be first`);
  const item = {
    q: vocab.q,
    type: vocab.phrase ? "idiom" : "word",
    target,
    meaning: vocab.meaning,
    targetSense: generated.targetSense,
    pos: POS_MAP[vocab.pos] || vocab.pos,
    level: "EIKEN Grade 2",
    fullEnglish: generated.fullEnglish,
    mixedEnglish: [...generated.fullEnglish],
    contextClues: generated.contextClues,
    inferencePath: [...generated.contextClues.map((clue) => clue.text), `targetSense: ${generated.targetSense}`, target],
    segments: generated.fullEnglish.map((sentence) => segmentSentence(sentence, target, generated.contextClues)),
    choices: generated.choices,
    answerIndex: 0,
    inferenceExplanation: generated.inferenceExplanation,
    quality: { targetOccurrence: 1, clueCount: generated.contextClues.length, targetProtected: true, cluesProtected: true },
    manualReview: { status: "pending" },
  };
  const result = validateContextItem(item, vocab, { requireTargetSense: true });
  if (result.status !== "pass") throw new Error(`${target}: ${result.errors.join(" | ")}`);
  return item;
}

async function buildDataset(datasetId, { limit = 0, outputDir = path.join(ROOT, "data", "context-candidates") } = {}) {
  const config = DATASETS[datasetId];
  if (!config) throw new Error(`Unknown dataset: ${datasetId}`);
  const vocab = readJson(path.join(ROOT, "data", config[0]));
  const allItems = vocabItems(vocab);
  const items = limit ? allItems.slice(0, limit) : allItems;
  fs.mkdirSync(outputDir, { recursive: true });
  const output = path.join(outputDir, `${datasetId}.json`);
  const existing = fs.existsSync(output) ? readJson(output) : null;
  const existingTargets = new Set((existing?.contexts || []).map((item) => item.target));
  const contexts = (existing?.contexts || []).filter((item) => items.some((source) => surface(source) === item.target));
  for (let offset = 0; offset < items.length; offset += 8) {
    const batch = items.slice(offset, offset + 8);
    let pending = batch.filter((item) => !existingTargets.has(surface(item)));
    for (let attempt = 1; pending.length && attempt <= 8; attempt += 1) {
      const generated = await generate(pending);
      const next = [];
      for (let index = 0; index < pending.length; index += 1) {
        try { contexts.push(runtimeItem(pending[index], generated[index])); }
        catch (error) {
          if (attempt === 8) throw error;
          console.warn(`[retry ${attempt}] ${surface(pending[index])}: ${error.message}`);
          next.push(pending[index]);
        }
      }
      pending = next;
    }
    console.log(`${datasetId}: ${Math.min(offset + batch.length, items.length)}/${items.length}`);
    const partialByTarget = new Map(contexts.map((item) => [item.target, item]));
    writeJson(output, {
      meta: { datasetId, grade: "EIKEN Grade 2", source: "Generated mini-context candidates for lexical inferencing", version: 1, count: partialByTarget.size, partial: true },
      contexts: items.map((item) => partialByTarget.get(surface(item))).filter(Boolean),
    });
  }
  const byTarget = new Map(contexts.map((item) => [item.target, item]));
  const ordered = items.map((item) => byTarget.get(surface(item)));
  writeJson(output, {
    meta: { datasetId, grade: "EIKEN Grade 2", source: "Generated mini-context candidates for lexical inferencing", version: 1, count: ordered.length },
    contexts: ordered,
  });
  console.log(`candidate written: ${path.relative(ROOT, output)}`);
  return output;
}

async function main() {
  const datasetArg = process.argv.find((arg) => arg.startsWith("--dataset="));
  const limitArg = process.argv.find((arg) => arg.startsWith("--limit="));
  const datasetIds = datasetArg ? datasetArg.slice(10).split(",") : Object.keys(DATASETS);
  const limit = limitArg ? Number(limitArg.slice(8)) : 0;
  for (const datasetId of datasetIds) await buildDataset(datasetId, { limit });
}

if (fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  main().catch((error) => { console.error(error.stack || error.message); process.exitCode = 1; });
}

export { DATASETS, buildDataset, runtimeItem, responseSchema };
