"use strict";

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { runtimeItem, responseSchema } from "./build-context-datasets.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const API_KEY = String(process.env.GEMINI_API_KEY || "").trim();
const MODEL = process.env.CONTEXT_GENERATION_MODEL || "gemini-3.5-flash-lite";
const CONFIG = {
  "eiken2-2025-3": "vocab_2025-3.json", "eiken2-2025-2": "vocab_2025-2.json",
  "eiken2-mock-1": "vocab_2_mock-1.json", "eiken2-mock-2": "vocab_2_mock-2.json",
  "eiken2-mock-3": "vocab_2_mock-3.json", "eiken2-mock-4": "vocab_2_mock-4.json",
};
function readJson(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
function writeJson(file, value) { fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }
function surface(item) { return item.word || item.phrase; }
function exactTargetCount(text, target) {
  const escaped = target.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return [...text.matchAll(new RegExp(`(?<![A-Za-z])${escaped}(?![A-Za-z])`, "gi"))].length;
}

async function regenerate(records) {
  const prompt = `Revise every EIKEN Grade 2 Context Discovery item according to its review issues. The source target, meaning, POS, and allowedTargetSenses are fixed. Do not complain that a fixed target is too easy; create the best valid inferencing context for it.\n
Rules:\n
- targetSense must be copied exactly from allowedTargetSenses and fit the new context grammatically.\n
- Write a coherent 2-3 sentence scene containing the target exactly once with precisely the supplied spelling. Never pluralize, conjugate, or otherwise alter the target. You may replace the existing example when needed.\n
- Include 2-3 meaningful independent clue phrases copied exactly from one sentence each. They cannot contain, cross, or overlap the target or each other.\n
- Avoid direct definitions, Japanese exposure, and answer-equivalent synonym restatements. Use observable situation, behavior, contrast, cause, and result.\n
- Four unique Japanese choices; targetSense at index 0; no other target sense; only one contextually valid answer.\n
- Natural Japanese explanation must quote every clue exactly and finish:「そのため、TARGETは「TARGET_SENSE」だと推測できます。」\n
- Return records in input order.\n
INPUT:\n${JSON.stringify(records)}`;
  const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-goog-api-key": API_KEY },
    body: JSON.stringify({ contents: [{ role: "user", parts: [{ text: prompt }] }], generationConfig: {
      temperature: 0.25, responseMimeType: "application/json", responseJsonSchema: responseSchema,
    } }),
  });
  if (!response.ok) throw new Error(`Gemini revise HTTP ${response.status}: ${(await response.text()).slice(0, 500)}`);
  const payload = await response.json();
  const text = payload.candidates?.[0]?.content?.parts?.map((part) => part.text || "").join("");
  if (!text) throw new Error("Revision returned no text");
  return JSON.parse(text);
}

async function main() {
  if (!API_KEY) throw new Error("GEMINI_API_KEY is required");
  const selected = process.argv.find((arg) => arg.startsWith("--dataset="))?.slice(10).split(",");
  for (const [datasetId, vocabFile] of Object.entries(CONFIG).filter(([id]) => !selected || selected.includes(id))) {
    const candidatePath = path.join(ROOT, "data", "context-candidates", `${datasetId}.json`);
    const reviewPath = path.join(ROOT, "data", "context-reviews", `${datasetId}.json`);
    const candidate = readJson(candidatePath);
    const review = readJson(reviewPath);
    const vocab = readJson(path.join(ROOT, "data", vocabFile));
    const vocabByTarget = new Map([...(vocab.words || []), ...(vocab.idioms || [])].map((item) => [surface(item), item]));
    const contextByTarget = new Map(candidate.contexts.map((item) => [item.target, item]));
    const revisions = review.items.filter((item) => item.status === "revise" && !item.issues.every((issue) => /簡単すぎ|平易すぎ|目標語彙としては平易/.test(issue)));
    for (let offset = 0; offset < revisions.length; offset += 4) {
      let pending = revisions.slice(offset, offset + 4);
      for (let attempt = 1; pending.length && attempt <= 8; attempt += 1) {
        const records = pending.map((entry) => {
          const source = vocabByTarget.get(entry.target);
          const current = contextByTarget.get(entry.target);
          return { target: entry.target, meaning: source.meaning, pos: source.pos, allowedTargetSenses: current.meaning.split(/[；;、,／/]/).map((v) => v.trim()).filter(Boolean), current, issues: entry.issues };
        });
        const generated = await regenerate(records);
        const next = [];
        for (let index = 0; index < pending.length; index += 1) {
          const entry = pending[index];
          const source = vocabByTarget.get(entry.target);
          const revised = generated[index];
          if (exactTargetCount(revised.fullEnglish.join(" "), entry.target) !== 1) {
            revised.fullEnglish = [source.example, ...revised.fullEnglish].slice(0, 3);
          }
          try { contextByTarget.set(entry.target, runtimeItem(source, revised)); }
          catch (error) {
            if (attempt === 8) throw error;
            console.warn(`[revision retry ${attempt}] ${entry.target}: ${error.message}`);
            next.push(entry);
          }
        }
        pending = next;
      }
      console.log(`${datasetId}: revised ${Math.min(offset + 4, revisions.length)}/${revisions.length}`);
    }
    candidate.contexts = candidate.contexts.map((item) => contextByTarget.get(item.target));
    writeJson(candidatePath, candidate);
  }
}

if (fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  main().catch((error) => { console.error(error.stack || error.message); process.exitCode = 1; });
}
