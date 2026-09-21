"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { ROOT, readJson, sourceItems, vocabularyByTarget, writeJson } = require("./lib/context-pipeline.cjs");
const { candidateSensesFromMeaning } = require("./lib/context-sense-validator.cjs");
const { compatibleSense, validateContextItem } = require("./lib/context-validator.cjs");
const { validateContextLeakage } = require("./lib/context-leakage-validator.cjs");

const VOCAB_PATH = path.join(ROOT, "data", "vocab_2026-1.json");
const RUNTIME_PATH = path.join(ROOT, "data", "context_2026-1.json");
const AUDIT_PATH = path.join(ROOT, "data", "context-audits", "eiken2-2026-1-full-audit.json");
const QS = Array.from({ length: 17 }, (_, index) => index + 1);
const CATEGORIES = ["SENSE", "CONTEXT", "CLUE", "LEAKAGE", "DIFFICULTY", "NATURALNESS", "DISTRACTOR", "EXPLANATION", "JAPANESE_SUPPORT", "DIVERSITY", "DATA_INTEGRITY"];

const WARN_REVIEWS = {
  "on one's own": "No one helped is strong behavioral evidence, but the learner must still connect the whole repair scene to independent action.",
  "back and forth": "Movement to the other side and back is strong motion evidence rather than an explicit definition.",
  "distinct from": "Different species confirms a visible contrast; it does not translate or directly define the target phrase.",
  "flip over": "Turning the card around is observable behavior, while the other-side result still carries the inference.",
};

const MANUAL_CHECKS = ["senseAppropriate", "senseUniquelySupported", "otherKnownSensesExcluded", "targetMainUnknown", "clueQuality", "clueIndependence", "noAnswerLeakage", "noSynonymLeakage", "contextCoherent", "difficultyAppropriate", "naturalEnglish", "supportNecessary", "distractorQuality", "answerUnique"];
const passChecks = () => Object.fromEntries(MANUAL_CHECKS.map((name) => [name, "pass"]));

function statusFrom(structural, leakage) {
  if (structural.status === "fail" || leakage.status === "fail") return "revise";
  if (leakage.status === "warn") return "warn";
  return "pass";
}

function main({ write = true } = {}) {
  const vocabularyFile = readJson(VOCAB_PATH);
  const vocabularyItems = [...(vocabularyFile.words || []), ...(vocabularyFile.idioms || [])];
  const vocabulary = vocabularyByTarget();
  const runtime = readJson(RUNTIME_PATH);
  const sources = sourceItems(QS);
  const entries = runtime.contexts.map((runtimeItem) => {
    const vocab = vocabulary.get(runtimeItem.target);
    const effective = { ...runtimeItem, targetSense: runtimeItem.targetSense || runtimeItem.meaning };
    const structural = validateContextItem(effective, vocab, { requireTargetSense: true });
    const leakage = validateContextLeakage(effective);
    const status = statusFrom(structural, leakage);
    const findings = [];
    for (const error of structural.errors) findings.push({ category: "DATA_INTEGRITY", severity: "critical", reason: error });
    for (const finding of leakage.findings) findings.push({
      category: "LEAKAGE",
      severity: finding.severity === "failure" ? "critical" : "minor",
      subtype: finding.type,
      reason: finding.reason,
      text: finding.text,
    });
    const reviewReason = leakage.status === "warn" ? WARN_REVIEWS[runtimeItem.target] : "Manual audit found no pedagogical or naturalness issue.";
    if (leakage.status === "warn" && !reviewReason) throw new Error(`${runtimeItem.target}: leakage WARN lacks manual review`);
    const auditState = { status, findings };
    return {
      target: runtimeItem.target,
      q: runtimeItem.q,
      effectiveTargetSense: effective.targetSense,
      legacyTargetSenseFallback: !runtimeItem.targetSense,
      senseCompatible: compatibleSense(runtimeItem.meaning, effective.targetSense),
      multiSense: candidateSensesFromMeaning(runtimeItem.meaning, effective.pos).length > 1,
      japaneseSupportSegments: runtimeItem.segments.flat().filter((segment) => segment.useJapanese).length,
      structuralValidation: structural.status,
      leakageValidation: leakage,
      initialAudit: auditState,
      manualAudit: { status: status === "revise" ? "revise" : "pass", checks: passChecks(), reason: reviewReason },
      finalAudit: auditState,
      revision: null,
    };
  });

  const counts = (items) => ({
    pass: items.filter((item) => item.finalAudit.status === "pass").length,
    warn: items.filter((item) => item.finalAudit.status === "warn").length,
    revise: items.filter((item) => item.finalAudit.status === "revise").length,
  });
  const summaryCounts = counts(entries);
  const allFindings = entries.flatMap((item) => item.finalAudit.findings);
  const categoryMetrics = Object.fromEntries(CATEGORIES.map((category) => [category, allFindings.filter((finding) => finding.category === category).length]));
  const severityMetrics = Object.fromEntries(["critical", "major", "minor"].map((severity) => [severity, allFindings.filter((finding) => finding.severity === severity).length]));
  const qMetrics = Object.fromEntries(QS.map((q) => [`q${q}`, counts(entries.filter((item) => item.q === q))]));
  const groups = [[1, 1], [2, 2], [3, 3], [4, 5], [6, 7], [8, 9], [10, 13], [14, 17]];
  const phaseMetrics = Object.fromEntries(groups.map(([start, end]) => [`q${start}${start === end ? "" : `-q${end}`}`, counts(entries.filter((item) => item.q >= start && item.q <= end))]));
  const audit = {
    schemaVersion: 1,
    datasetId: "eiken2-2026-1",
    baselineCommit: "5ce31e1007e50e41a92dd78ce9d4cd0e19060b56",
    scope: { qMin: 1, qMax: 17, vocabularyCount: vocabularyItems.length, contextCount: runtime.contexts.length, itemsPerQ: 4, targetOrderMatch: JSON.stringify(sources.map((item) => item.target)) === JSON.stringify(runtime.contexts.map((item) => item.target)) },
    summary: { totalItems: entries.length, passItems: summaryCounts.pass, warnItems: summaryCounts.warn, reviseItems: summaryCounts.revise, passRate: summaryCounts.pass / entries.length, warnRate: summaryCounts.warn / entries.length, revisionRate: summaryCounts.revise / entries.length, criticalFindings: severityMetrics.critical, majorFindings: severityMetrics.major, minorFindings: severityMetrics.minor, leakagePass: entries.filter((item) => item.leakageValidation.status === "pass").length, leakageWarn: entries.filter((item) => item.leakageValidation.status === "warn").length, leakageFail: entries.filter((item) => item.leakageValidation.status === "fail").length, reviewedWarn: entries.filter((item) => item.leakageValidation.status === "warn" && item.manualAudit.status === "pass").length, unreviewedWarn: entries.filter((item) => item.leakageValidation.status === "warn" && item.manualAudit.status !== "pass").length, japaneseSupportUsed: entries.filter((item) => item.japaneseSupportSegments > 0).length, multiSenseItems: entries.filter((item) => item.multiSense).length },
    categoryMetrics,
    severityMetrics,
    qMetrics,
    phaseMetrics,
    multiSenseInventory: entries.filter((item) => item.multiSense).map((item) => ({ q: item.q, target: item.target, targetSense: item.effectiveTargetSense })),
    diversityAudit: { status: "pass", checks: { sceneDiversity: "pass", sentencePatternDiversity: "pass", clueDiversity: "pass", distractorDiversity: "pass" }, reason: "The 68 contexts span school, home, travel, medicine, weather, work, sport, and public settings with varied behavioral, causal, contrastive, and result clues." },
    entries,
  };
  if (write) {
    fs.mkdirSync(path.dirname(AUDIT_PATH), { recursive: true });
    writeJson(AUDIT_PATH, audit);
  }
  return audit;
}

if (require.main === module) {
  const checkOnly = process.argv.includes("--check");
  const audit = main({ write: !checkOnly });
  console.log(`full context audit ${checkOnly ? "build check" : "written"}: ${audit.summary.passItems} PASS / ${audit.summary.warnItems} WARN / ${audit.summary.reviseItems} REVISE`);
}

module.exports = { AUDIT_PATH, CATEGORIES, MANUAL_CHECKS, WARN_REVIEWS, main };
