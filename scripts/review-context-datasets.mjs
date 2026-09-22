"use strict";

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const API_KEY = String(process.env.GEMINI_API_KEY || "").trim();
const MODEL = process.env.CONTEXT_REVIEW_MODEL || "gemini-3.5-flash";
const DATASETS = ["eiken2-2025-3", "eiken2-2025-2", "eiken2-mock-1", "eiken2-mock-2", "eiken2-mock-3", "eiken2-mock-4"];
const schema = {
  type: "array",
  items: {
    type: "object",
    properties: {
      target: { type: "string" },
      status: { type: "string", enum: ["pass", "revise"] },
      issues: { type: "array", items: { type: "string" } },
    },
    required: ["target", "status", "issues"], additionalProperties: false,
  },
};

function readJson(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
function writeJson(file, value) { fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }

async function review(items) {
  const compact = items.map((item) => ({
    target: item.target, meaning: item.meaning, targetSense: item.targetSense, pos: item.pos,
    fullEnglish: item.fullEnglish, clues: item.contextClues.map((clue) => clue.text),
    choices: item.choices, explanation: item.inferenceExplanation,
  }));
  const prompt = `You are an independent reviewer of EIKEN Grade 2 Context Discovery materials. Review every item. Return pass only when all criteria hold:\n
1. The target is used naturally with the stated POS and targetSense.\n
2. A learner can infer targetSense uniquely from at least two meaningful and reasonably independent clues.\n
3. The target is the main unknown; surrounding English is accessible at EIKEN Grade 2.\n
4. There is no direct definition, Japanese answer exposure, or answer-equivalent synonym restatement before answering.\n
5. The 2-3 sentences form one coherent scene and are grammatically natural.\n
6. Four Japanese choices are unique, plausible, same broad category where reasonable, and only targetSense is valid. Other senses of the target are not distractors.\n
7. The Japanese explanation accurately connects every listed clue to targetSense and reads naturally.\n
The source target and vocabulary meaning are fixed curriculum data. Do not mark an item revise merely because the target seems easy for Grade 2. Judge whether the supplied context teaches that fixed target correctly.\n
For revise, list concrete issues in Japanese. Do not invent stylistic complaints when the material is already sound. Keep output in input order.\n
ITEMS:\n${JSON.stringify(compact)}`;
  const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-goog-api-key": API_KEY },
    body: JSON.stringify({
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      generationConfig: { temperature: 0.1, responseMimeType: "application/json", responseJsonSchema: schema },
    }),
  });
  if (!response.ok) throw new Error(`Gemini review HTTP ${response.status}: ${(await response.text()).slice(0, 500)}`);
  const payload = await response.json();
  const text = payload.candidates?.[0]?.content?.parts?.map((part) => part.text || "").join("");
  if (!text) throw new Error("Review returned no text");
  return JSON.parse(text);
}

async function main() {
  if (!API_KEY) throw new Error("GEMINI_API_KEY is required");
  const selected = process.argv.find((arg) => arg.startsWith("--dataset="))?.slice(10).split(",") || DATASETS;
  const reviewDir = path.join(ROOT, "data", "context-reviews");
  fs.mkdirSync(reviewDir, { recursive: true });
  for (const datasetId of selected) {
    const candidate = readJson(path.join(ROOT, "data", "context-candidates", `${datasetId}.json`));
    const results = [];
    for (let offset = 0; offset < candidate.contexts.length; offset += 16) {
      const batch = candidate.contexts.slice(offset, offset + 16);
      const batchResults = await review(batch);
      if (batchResults.length !== batch.length || batchResults.some((result, index) => result.target !== batch[index].target)) {
        throw new Error(`${datasetId}: review output order mismatch at ${offset}`);
      }
      results.push(...batchResults);
      console.log(`${datasetId}: reviewed ${results.length}/${candidate.contexts.length}`);
    }
    const counts = results.reduce((out, result) => ({ ...out, [result.status]: (out[result.status] || 0) + 1 }), {});
    writeJson(path.join(reviewDir, `${datasetId}.json`), { datasetId, model: MODEL, counts, items: results });
  }
}

if (fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  main().catch((error) => { console.error(error.stack || error.message); process.exitCode = 1; });
}
