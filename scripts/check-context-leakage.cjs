"use strict";

const assert = require("node:assert/strict");
const path = require("node:path");
const { ROOT, readJson } = require("./lib/context-pipeline.cjs");
const { validateContextLeakage, assertLeakagePublishable } = require("./lib/context-leakage-validator.cjs");

function item(target, targetSense, fullEnglish, extra = {}) {
  return { target, targetSense, meaning: targetSense, fullEnglish, mixedEnglish: [...fullEnglish], segments: [], ...extra };
}

function main() {
  const phase9 = readJson(path.join(ROOT, "data", "context-drafts", "eiken2-2026-1-q10-q11-q12-q13-candidates.json")).items;
  for (const target of ["for a fresh start", "on one's own", "at a distance"]) {
    assert.notEqual(validateContextLeakage({ ...phase9[target].initial, target }).status, "pass", `${target}: known initial leakage missed`);
  }
  assert.equal(validateContextLeakage({ ...phase9["for a fresh start"].final, target: "for a fresh start" }).status, "pass");
  assert.equal(validateContextLeakage({ ...phase9["at a distance"].final, target: "at a distance" }).status, "pass");
  assert.notEqual(validateContextLeakage({ ...phase9["on one's own"].final, target: "on one's own" }).status, "fail");

  const definition = validateContextLeakage(item("on one's own", "自分だけで", ["He did it on his own, which means he did it without help."]));
  assert.equal(definition.status, "fail");
  assert.ok(definition.findings.some((finding) => finding.type === "DIRECT_DEFINITION"));

  const translation = validateContextLeakage(item("slip", "滑る", ["Ken began to slip on the wet floor."], {
    mixedEnglish: ["Ken began to 滑る on the wet floor."],
    segments: [[{ en: "slip", ja: "滑る", role: "target", useJapanese: true }]],
  }));
  assert.equal(translation.status, "fail");
  assert.ok(translation.findings.some((finding) => finding.type === "TRANSLATION_LEAKAGE"));

  const warning = validateContextLeakage(item("on one's own", "自分だけで", [
    "Mina repaired the chair on her own.", "No one helped her while she followed the guide.",
  ]));
  assert.equal(warning.status, "warn");
  assert.throws(() => assertLeakagePublishable({ ...item("on one's own", "自分だけで", warning.fullEnglish || []), leakageValidation: warning }));
  assert.doesNotThrow(() => assertLeakagePublishable({ target: "on one's own", leakageValidation: warning, leakageReview: { status: "accepted", reason: "Strong but indirect evidence." } }));

  const positives = [
    item("slip", "滑る", ["The floor was wet, and Ken's foot suddenly moved forward.", "He almost fell and grabbed the rail."]),
    item("frown", "眉をひそめる", ["Maya's eyebrows moved down when she read the bad news.", "Her face looked unhappy for the rest of the day."]),
    item("as a general rule", "概して、一般に", ["As a general rule, the library closes at six.", "However, it stays open later on Fridays."]),
    item("balance", "均衡、バランス", ["Ken held out both arms while riding his bicycle.", "He stayed steady even when the wind became strong."]),
    item("scale", "はかり", ["The nurse asked me to step on a scale.", "She wrote down my weight."]),
  ];
  for (const positive of positives) assert.notEqual(validateContextLeakage(positive).status, "fail", `${positive.target}: strong clue became a false FAIL`);
  console.log("context leakage validator: OK");
}

main();
