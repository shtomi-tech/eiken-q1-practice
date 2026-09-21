"use strict";

const { senseParts } = require("./context-validator.cjs");

const TYPES = new Set([
  "DIRECT_DEFINITION", "SYNONYM_LEAKAGE", "PARAPHRASE_LEAKAGE", "TRANSLATION_LEAKAGE", "OTHER_LEAKAGE",
]);

const HINTS = {
  "for a fresh start": [{ text: "begin again", type: "SYNONYM_LEAKAGE" }],
  "on one's own": [
    { text: "without help", type: "PARAPHRASE_LEAKAGE" },
    { text: "without anyone beside", type: "PARAPHRASE_LEAKAGE" },
    { text: "no one helped", type: "PARAPHRASE_LEAKAGE" },
  ],
  "at a distance": [{ text: "from far away", type: "SYNONYM_LEAKAGE" }],
  "the edge of": [{ text: "farthest part", type: "SYNONYM_LEAKAGE" }],
  "the back of": [
    { text: "behind", type: "SYNONYM_LEAKAGE" },
    { text: "far from the front", type: "SYNONYM_LEAKAGE" },
  ],
  "back and forth": [{ text: "to the other side, then moved back again", type: "PARAPHRASE_LEAKAGE" }],
  "distinct from": [{ text: "different species", type: "SYNONYM_LEAKAGE" }],
  "flip over": [{ text: "turn it around", type: "SYNONYM_LEAKAGE" }],
};

function finding(type, text, severity, reason, sentenceIndex = null) {
  return { type, text, severity, reason, ...(sentenceIndex === null ? {} : { sentenceIndex }) };
}

function validateContextLeakage(item) {
  const findings = [];
  const target = String(item?.target || "");
  const targetLower = target.toLowerCase();
  const fullEnglish = item?.fullEnglish || [];
  const mixedEnglish = item?.mixedEnglish || [];
  const segments = (item?.segments || []).flat();

  for (const [sentenceIndex, sentence] of fullEnglish.entries()) {
    const lower = String(sentence).toLowerCase();
    const escapedTarget = targetLower.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace("one's", "(?:one's|my|your|his|her|our|their)");
    const targetMatch = new RegExp(escapedTarget, "i").exec(sentence);
    const targetIndex = targetMatch?.index ?? -1;
    const markers = ["which means", " means ", "meaning ", "in other words", "that is"];
    for (const marker of markers) {
      if (targetLower === marker.trim()) continue;
      const markerIndex = lower.indexOf(marker);
      if (targetIndex >= 0 && markerIndex > targetIndex) {
        findings.push(finding("DIRECT_DEFINITION", marker.trim(), "failure", `Definition marker follows ${target}.`, sentenceIndex));
      }
    }
  }

  const japaneseSources = [...fullEnglish, ...mixedEnglish, ...segments.filter((segment) => segment.useJapanese).map((segment) => segment.ja || "")];
  const japaneseSenses = [...new Set([item?.targetSense, ...senseParts(item?.meaning || "")].filter(Boolean))];
  for (const sense of japaneseSenses) {
    const exposed = japaneseSources.find((text) => String(text).includes(sense));
    if (exposed) findings.push(finding("TRANSLATION_LEAKAGE", sense, "failure", "Japanese target meaning is exposed before answer confirmation."));
  }

  const hintFindings = [];
  const story = fullEnglish.join(" ").toLowerCase();
  for (const hint of HINTS[targetLower] || []) {
    if (story.includes(hint.text.toLowerCase())) {
      hintFindings.push(finding(hint.type, hint.text, "warning", `This expression may be answer-equivalent to ${target}.`));
    }
  }
  findings.push(...hintFindings);
  if (hintFindings.length >= 2) {
    findings.push(finding("PARAPHRASE_LEAKAGE", hintFindings.map((item) => item.text).join(" + "), "failure",
      "Multiple answer-equivalent paraphrases make inference unnecessary."));
  }

  const status = findings.some((item) => item.severity === "failure")
    ? "fail"
    : findings.some((item) => item.severity === "warning") ? "warn" : "pass";
  return { status, findings };
}

function assertLeakagePublishable(item) {
  const result = item?.leakageValidation || validateContextLeakage(item);
  if (result.status === "fail") throw new Error(`${item.target}: leakage validation is FAIL`);
  if (result.status === "warn" && item?.leakageReview?.status !== "accepted") {
    throw new Error(`${item.target}: leakage WARN requires explicit reviewer acceptance`);
  }
  return result;
}

module.exports = { TYPES, HINTS, validateContextLeakage, assertLeakagePublishable };
