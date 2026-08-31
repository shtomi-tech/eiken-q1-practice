const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const DATA_DIR = path.join(ROOT, "data");
const RESEARCH_PATH = path.join(DATA_DIR, "word_origin_research.json");
const LEMMA_PATH = path.join(DATA_DIR, "lemmas.json");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function normalize(value) {
  return String(value || "").trim().toLowerCase();
}

function nonEmpty(value, label) {
  assert.equal(typeof value, "string", `${label} は文字列である必要があります`);
  assert.ok(value.trim(), `${label} は空にできません`);
  return value.trim();
}

function validateSources(sources, label, required) {
  assert.ok(Array.isArray(sources), `${label} はsources配列が必要です`);
  const hosts = new Set();
  const values = new Set();
  for (const [index, source] of sources.entries()) {
    const value = nonEmpty(source, `${label}[${index}]`);
    const parsed = new URL(value);
    assert.ok(["http:", "https:"].includes(parsed.protocol), `${label}[${index}] はhttp(s) URLにしてください`);
    assert.equal(values.has(value), false, `${label} に同じURLを重複登録できません`);
    values.add(value);
    hosts.add(parsed.hostname);
  }
  if (required) {
    assert.ok(sources.length >= 2, `${label} は2つ以上のURLが必要です`);
    assert.ok(hosts.size >= 2, `${label} は2ホスト以上を参照してください`);
  }
}

function vocabularyContext() {
  const lemmaData = readJson(LEMMA_PATH);
  const lemmaMap = Object.fromEntries(
    Object.entries(lemmaData.lemmas || {}).map(([surface, lemma]) => [normalize(surface), normalize(lemma)]),
  );
  const byLemma = new Map();
  for (const fileName of fs.readdirSync(DATA_DIR).filter((name) => /^vocab_.*\.json$/.test(name)).sort()) {
    const vocab = readJson(path.join(DATA_DIR, fileName));
    for (const item of vocab.words || []) {
      const rawSurface = String(item.word || "").trim();
      const surface = normalize(rawSurface);
      if (!surface) continue;
      const lemma = lemmaMap[surface] || surface;
      const row = byLemma.get(lemma) || { surfaces: new Set(), meanings: new Set() };
      row.surfaces.add(rawSurface);
      if (String(item.meaning || "").trim()) row.meanings.add(String(item.meaning).trim());
      byLemma.set(lemma, row);
    }
  }
  return { lemmaMap, byLemma };
}

function main() {
  const requireComplete = process.argv.includes("--require-complete");
  assert.ok(fs.existsSync(RESEARCH_PATH), "data/word_origin_research.json が必要です");
  const ledger = readJson(RESEARCH_PATH);
  assert.equal(ledger.meta?.schemaVersion, 1, "研究台帳のschemaVersionは1である必要があります");
  assert.ok(ledger.entries && typeof ledger.entries === "object" && !Array.isArray(ledger.entries), "entries辞書が必要です");
  assert.ok(ledger.dictionary?.roots && typeof ledger.dictionary.roots === "object", "dictionary.rootsが必要です");
  assert.ok(ledger.dictionary?.affixes && typeof ledger.dictionary.affixes === "object", "dictionary.affixesが必要です");

  const { lemmaMap, byLemma } = vocabularyContext();
  const allowedStatuses = new Set(["pending", "reviewed", "needs_review", "legacy"]);
  const allowedClassifications = new Set(["A", "B", "C"]);
  const statusCounts = {};
  const classificationCounts = {};

  for (const [lemma, entry] of Object.entries(ledger.entries)) {
    assert.equal(normalize(lemma), lemma, `${lemma}: entriesのキーは小文字の原形にしてください`);
    assert.ok(byLemma.has(lemma), `${lemma}: 語彙データに存在しません`);
    assert.ok(allowedClassifications.has(entry.classification), `${lemma}: classificationが不正です`);
    classificationCounts[entry.classification] = (classificationCounts[entry.classification] || 0) + 1;

    assert.ok(Array.isArray(entry.surfaceForms) && entry.surfaceForms.length > 0, `${lemma}: surfaceFormsが必要です`);
    for (const [index, surface] of entry.surfaceForms.entries()) {
      nonEmpty(surface, `${lemma}.surfaceForms[${index}]`);
      const mapped = lemmaMap[normalize(surface)] || normalize(surface);
      assert.equal(mapped, lemma, `${lemma}.surfaceForms[${index}] が原形に解決できません`);
    }
    assert.ok(Array.isArray(entry.meanings) && entry.meanings.length > 0, `${lemma}: meaningsが必要です`);
    entry.meanings.forEach((meaning, index) => nonEmpty(meaning, `${lemma}.meanings[${index}]`));

    assert.ok(entry.research && typeof entry.research === "object", `${lemma}: researchが必要です`);
    const research = entry.research;
    assert.ok(allowedStatuses.has(research.status), `${lemma}.research.statusが不正です`);
    statusCounts[research.status] = (statusCounts[research.status] || 0) + 1;
    validateSources(research.sources, `${lemma}.research.sources`, research.status === "reviewed");

    if (entry.classification === "C") {
      assert.ok(entry.exclusion && typeof entry.exclusion === "object", `${lemma}: C型にはexclusionが必要です`);
      nonEmpty(entry.exclusion.reason, `${lemma}.exclusion.reason`);
    } else {
      assert.ok(entry.display && typeof entry.display === "object", `${lemma}: displayが必要です`);
      assert.equal(entry.display.type, entry.classification, `${lemma}: display.typeとclassificationが一致しません`);
      nonEmpty(entry.display.derivation, `${lemma}.display.derivation`);
      if (entry.classification === "B") {
        assert.equal(entry.display.root, undefined, `${lemma}: B型にrootは付けません`);
        assert.equal(entry.display.parts, undefined, `${lemma}: B型にpartsは付けません`);
      }
    }

    if (research.status === "reviewed") {
      nonEmpty(research.originLanguage, `${lemma}.research.originLanguage`);
      assert.ok(Array.isArray(research.etymons), `${lemma}.research.etymonsは配列が必要です`);
      assert.ok(Array.isArray(research.historicalPath) && research.historicalPath.length > 0, `${lemma}.research.historicalPathが必要です`);
      assert.ok(Array.isArray(research.components), `${lemma}.research.componentsは配列が必要です`);
      assert.ok(Array.isArray(research.rootCandidates), `${lemma}.research.rootCandidatesは配列が必要です`);
      assert.ok(Array.isArray(research.sourceNotes) && research.sourceNotes.length >= 2, `${lemma}.research.sourceNotesが必要です`);
      const sourceSet = new Set(research.sources);
      for (const [index, note] of research.sourceNotes.entries()) {
        assert.ok(note && typeof note === "object" && !Array.isArray(note), `${lemma}.research.sourceNotes[${index}]が不正です`);
        assert.ok(sourceSet.has(nonEmpty(note.url, `${lemma}.research.sourceNotes[${index}].url`)), `${lemma}.research.sourceNotes[${index}].urlがsourcesにありません`);
        nonEmpty(note.note, `${lemma}.research.sourceNotes[${index}].note`);
      }
      nonEmpty(research.semanticBridge, `${lemma}.research.semanticBridge`);
      nonEmpty(research.summary, `${lemma}.research.summary`);
      assert.ok(["high", "medium", "low"].includes(research.confidence), `${lemma}.research.confidenceが不正です`);
    }
  }

  const target = ledger.researchTarget;
  assert.equal(target?.type, "B", "researchTarget.typeはBである必要があります");
  assert.equal(target?.count, target?.lemmas?.length, "researchTarget.countとlemmasの数が一致しません");
  assert.equal(new Set(target.lemmas).size, target.lemmas.length, "researchTarget.lemmasに重複があります");
  for (const lemma of target.lemmas) {
    assert.ok(ledger.entries[lemma], `researchTargetの${lemma}がentriesにありません`);
  }
  if (requireComplete) {
    for (const lemma of target.lemmas) {
      assert.equal(ledger.entries[lemma].research.status, "reviewed", `${lemma}: 個別再調査が未完了です`);
    }
  }

  console.log(`word origin research ledger: OK (${JSON.stringify({
    entries: Object.keys(ledger.entries).length,
    target: target.lemmas.length,
    classifications: classificationCounts,
    statuses: statusCounts,
    complete: requireComplete,
  })})`);
  return 0;
}

try {
  process.exitCode = main();
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
