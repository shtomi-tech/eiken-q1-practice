const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const util = require("node:util");

const ROOT = path.resolve(__dirname, "..");
const RESEARCH_PATH = path.join(ROOT, "data", "word_origin_research.json");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function writeJson(filePath, value) {
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function nonEmpty(value, label) {
  assert.equal(typeof value, "string", `${label} は文字列である必要があります`);
  assert.ok(value.trim(), `${label} は空にできません`);
  return value.trim();
}

function applyDictionaryPatch(ledger, dictionary) {
  if (dictionary === undefined) return { roots: 0, affixes: 0 };
  assert.ok(dictionary && typeof dictionary === "object" && !Array.isArray(dictionary), "batch.dictionaryが不正です");
  const counts = { roots: 0, affixes: 0 };
  for (const section of ["roots", "affixes"]) {
    if (dictionary[section] === undefined) continue;
    assert.ok(dictionary[section] && typeof dictionary[section] === "object" && !Array.isArray(dictionary[section]), `batch.dictionary.${section}が不正です`);
    for (const [key, value] of Object.entries(dictionary[section])) {
      assert.ok(key.trim(), `batch.dictionary.${section}のキーが空です`);
      assert.ok(value && typeof value === "object" && !Array.isArray(value), `batch.dictionary.${section}.${key}が不正です`);
      const existing = ledger.dictionary[section][key];
      if (existing !== undefined) {
        assert.ok(util.isDeepStrictEqual(existing, value), `batch.dictionary.${section}.${key}は既存定義と一致しません`);
        continue;
      }
      ledger.dictionary[section][key] = value;
      counts[section] += 1;
    }
  }
  return counts;
}

function applyExclusionsPatch(ledger, exclusions, batchEntries) {
  if (exclusions === undefined) return 0;
  assert.ok(exclusions && typeof exclusions === "object" && !Array.isArray(exclusions), "batch.exclusionsが不正です");
  let applied = 0;
  ledger.exclusions = ledger.exclusions || {};
  const allowedGroups = new Set(["general", ...Object.keys(ledger.dictionary?.roots || {})]);
  for (const [group, values] of Object.entries(exclusions)) {
    nonEmpty(group, "batch.exclusionsのgroup");
    assert.ok(allowedGroups.has(group), `batch.exclusions.${group}: 語根名またはgeneralを指定してください`);
    assert.ok(values && typeof values === "object" && !Array.isArray(values), `batch.exclusions.${group}が不正です`);
    ledger.exclusions[group] = ledger.exclusions[group] || {};
    for (const [lemma, rawReason] of Object.entries(values)) {
      nonEmpty(lemma, `batch.exclusions.${group}のlemma`);
      const reason = nonEmpty(rawReason, `batch.exclusions.${group}.${lemma}`);
      assert.equal(Object.prototype.hasOwnProperty.call(batchEntries, lemma), false, `${lemma}: 同じbatch内で語源entryと除外理由を両方指定できません`);
      const existingEntry = ledger.entries[lemma];
      assert.ok(!existingEntry || existingEntry.classification === "C", `${lemma}: origin entryをC型除外へ変更するには明示的な再分類が必要です`);
      const existingReason = ledger.exclusions[group][lemma];
      if (existingReason !== undefined) {
        assert.equal(existingReason, reason, `${lemma}: 既存の除外理由と一致しません`);
        continue;
      }
      ledger.exclusions[group][lemma] = reason;
      applied += 1;
    }
  }
  return applied;
}

function main() {
  const batchPath = process.argv[2];
  assert.ok(batchPath, "使い方: node scripts/apply-word-origin-research-batch.cjs <batch.json>");
  const batch = readJson(path.resolve(ROOT, batchPath));
  const ledger = readJson(RESEARCH_PATH);
  const batchId = nonEmpty(batch.meta?.batchId, "batch.meta.batchId");
  assert.ok(batch.entries && typeof batch.entries === "object" && !Array.isArray(batch.entries), "batch.entriesが必要です");
  const previousBatch = ledger.meta?.lastAppliedBatch;
  assert.notEqual(previousBatch, batchId, `${batchId}: 既に最後に適用されています`);
  const target = new Set(ledger.researchTarget?.lemmas || []);
  let applied = 0;

  for (const [lemma, patch] of Object.entries(batch.entries)) {
    assert.ok(patch && typeof patch === "object" && !Array.isArray(patch), `${lemma}: batch entryが不正です`);
    const isNew = !target.has(lemma);
    if (isNew) {
      assert.ok(Array.isArray(patch.surfaceForms) && patch.surfaceForms.length > 0, `${lemma}: 新規entryにはsurfaceFormsが必要です`);
      assert.ok(Array.isArray(patch.meanings) && patch.meanings.length > 0, `${lemma}: 新規entryにはmeaningsが必要です`);
      assert.equal(patch.classification, "B", `${lemma}: 新規entryはB型にしてください`);
      ledger.entries[lemma] = {
        surfaceForms: patch.surfaceForms,
        meanings: patch.meanings,
        classification: "B",
        display: {},
        research: {},
      };
      target.add(lemma);
      ledger.researchTarget.lemmas.push(lemma);
      ledger.researchTarget.count += 1;
    }
    const entry = ledger.entries[lemma];
    assert.ok(entry, `${lemma}: 研究台帳に存在しません`);
    if (patch.classification !== undefined) {
      assert.ok(["A", "B", "C"].includes(patch.classification), `${lemma}: classificationが不正です`);
      entry.classification = patch.classification;
      if (patch.classification !== "C") {
        entry.display = { ...(entry.display || {}), ...(patch.display || {}), type: patch.classification };
      }
    } else if (patch.display) {
      entry.display = { ...(entry.display || {}), ...patch.display };
    }
    assert.ok(patch.research && typeof patch.research === "object", `${lemma}: researchが必要です`);
    entry.research = {
      ...(entry.research || {}),
      ...patch.research,
      batch: batchId,
    };
    if (entry.research.status !== "reviewed") {
      throw new Error(`${lemma}: batch適用後のstatusはreviewedである必要があります`);
    }
    applied += 1;
  }

  const dictionaryCounts = applyDictionaryPatch(ledger, batch.dictionary);
  const appliedExclusions = applyExclusionsPatch(ledger, batch.exclusions, batch.entries);
  ledger.meta.lastAppliedBatch = batchId;
  ledger.meta.appliedBatches = [
    ...(Array.isArray(ledger.meta.appliedBatches) ? ledger.meta.appliedBatches : (previousBatch ? [{ batchId: previousBatch }] : [])),
    {
      batchId,
      entries: applied,
      roots: dictionaryCounts.roots,
      affixes: dictionaryCounts.affixes,
      exclusions: appliedExclusions,
    },
  ];
  writeJson(RESEARCH_PATH, ledger);
  console.log(`word origin research batch: applied ${applied} entries and ${appliedExclusions} exclusions (${batchId}), dictionary ${JSON.stringify(dictionaryCounts)}`);
  return 0;
}

try {
  process.exitCode = main();
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
