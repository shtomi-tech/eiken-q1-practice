const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const util = require("node:util");

const ROOT = path.resolve(__dirname, "..");
const DATA_DIR = path.join(ROOT, "data");
const RESEARCH_PATH = path.join(DATA_DIR, "word_origin_research.json");
const ROOTS_PATH = path.join(DATA_DIR, "word_roots.json");
const ORIGINS_PATH = path.join(DATA_DIR, "word_origins.json");
const EXCLUDED_PATH = path.join(DATA_DIR, "word_origin_excluded.json");
const LEMMA_PATH = path.join(DATA_DIR, "lemmas.json");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function isFlatObject(value) {
  return value && typeof value === "object" && !Array.isArray(value)
    && Object.values(value).every((item) => item === null || typeof item !== "object");
}

function renderFlatObject(value) {
  return `{ ${Object.entries(value).map(([entryKey, entryValue]) => (
    `${JSON.stringify(entryKey)}: ${JSON.stringify(entryValue)}`
  )).join(", ")} }`;
}

function renderJson(value, level = 0, key = "") {
  const indent = "  ".repeat(level);
  const childIndent = "  ".repeat(level + 1);
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) {
    if (!value.length) return "[]";
    if (key === "variants" && value.every((item) => typeof item !== "object" || item === null)) {
      return `[${value.map((item) => JSON.stringify(item)).join(", ")}]`;
    }
    if ((key === "parts" || key === "chain") && value.every(isFlatObject)) {
      return `[\n${value.map((item) => `${childIndent}${renderFlatObject(item)}`).join(",\n")}\n${indent}]`;
    }
    return `[\n${value.map((item) => `${childIndent}${renderJson(item, level + 1)}`).join(",\n")}\n${indent}]`;
  }
  const entries = Object.entries(value);
  if (!entries.length) return "{}";
  return `{\n${entries.map(([entryKey, entryValue]) => (
    `${childIndent}${JSON.stringify(entryKey)}: ${key === "affixes" && entryKey !== "a" && isFlatObject(entryValue)
      ? renderFlatObject(entryValue)
      : renderJson(entryValue, level + 1, entryKey)}`
  )).join(",\n")}\n${indent}}`;
}

function writeJson(filePath, value, options = {}) {
  const content = options.preserveDisplayArrays
    ? renderJson(value)
    : JSON.stringify(value, null, 2);
  fs.writeFileSync(filePath, `${content}\n`, "utf8");
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function normalize(value) {
  return String(value || "").trim().toLowerCase();
}

function loadVocabularyContext() {
  const lemmaData = readJson(LEMMA_PATH);
  const lemmaMap = Object.fromEntries(
    Object.entries(lemmaData.lemmas || {}).map(([surface, lemma]) => [normalize(surface), normalize(lemma)]),
  );
  const byLemma = new Map();
  const fileNames = fs.readdirSync(DATA_DIR).filter((name) => /^vocab_.*\.json$/.test(name)).sort();

  for (const fileName of fileNames) {
    const vocab = readJson(path.join(DATA_DIR, fileName));
    for (const item of vocab.words || []) {
      const rawSurface = String(item.word || "").trim();
      const surface = normalize(rawSurface);
      if (!surface) continue;
      const lemma = lemmaMap[surface] || surface;
      const row = byLemma.get(lemma) || { surfaceForms: [], meanings: [] };
      if (!row.surfaceForms.includes(rawSurface)) row.surfaceForms.push(rawSurface);
      const meaning = String(item.meaning || "").trim();
      if (meaning && !row.meanings.includes(meaning)) row.meanings.push(meaning);
      byLemma.set(lemma, row);
    }
  }
  return byLemma;
}

function sourceList(origin) {
  if (Array.isArray(origin.sources)) return origin.sources.filter((source) => typeof source === "string" && source.trim());
  if (typeof origin.source === "string" && origin.source.trim()) return [origin.source.trim()];
  return [];
}

function buildInitialLedger() {
  const originsData = readJson(ORIGINS_PATH);
  const rootsData = readJson(ROOTS_PATH);
  const excludedData = readJson(EXCLUDED_PATH);
  const vocabulary = loadVocabularyContext();
  const entries = {};

  for (const [lemma, origin] of Object.entries(originsData.origins || {})) {
    const normalizedLemma = normalize(lemma);
    const context = vocabulary.get(normalizedLemma) || { surfaceForms: [lemma], meanings: [] };
    const classification = origin.type;
    const sources = sourceList(origin);
    entries[lemma] = {
      surfaceForms: context.surfaceForms.length ? context.surfaceForms : [lemma],
      meanings: context.meanings,
      classification,
      display: clone(origin),
      research: {
        status: classification === "B" ? "pending" : "legacy",
        sources,
        sourceNotes: [],
        originLanguage: "",
        etymons: [],
        historicalPath: [],
        components: [],
        rootCandidates: [],
        semanticBridge: "",
        summary: "",
        confidence: "",
        notes: classification === "B"
          ? "既存の表示用データから移行。個別再調査前。"
          : "既存A型を移行。再構築する語根辞書との整合監査対象。",
      },
    };
  }

  const researchTargetLemmas = Object.entries(entries)
    .filter(([, entry]) => entry.classification === "B")
    .map(([lemma]) => lemma);

  return {
    meta: {
      schemaVersion: 1,
      note: "語源再調査のauthoring正本。entriesは原形キーで、displayからword_origins.jsonを生成する。",
      scope: "現在のword_origins.jsonにある単語語源。B型1,255語を個別再調査し、A/B/Cを再判定する。",
      entryKey: "data/lemmas.json適用後の原形（小文字）",
      sourcePolicy: {
        reviewed: "一語ごとに2つ以上の独立ホストの出典URLを確認し、語源の経路と意味のつながりを要約する。",
        decomposition: "綴りの類似だけで語根や接辞を割り当てず、出典が支える場合だけA型にする。",
      },
    },
    researchTarget: {
      type: "B",
      count: researchTargetLemmas.length,
      lemmas: researchTargetLemmas,
    },
    outputMeta: {
      origins: clone(originsData.meta || {}),
      roots: clone(rootsData.meta || {}),
      excluded: clone(excludedData.meta || {}),
    },
    dictionary: {
      roots: clone(rootsData.roots || {}),
      affixes: clone(rootsData.affixes || {}),
    },
    exclusions: clone(excludedData.excluded || {}),
    entries,
  };
}

function displayFor(entry) {
  const display = clone(entry.display || {});
  const research = entry.research || {};
  if (research.status === "reviewed") {
    const sources = Array.isArray(research.sources) ? research.sources.filter((source) => String(source).trim()) : [];
    if (sources.length) {
      display.source = sources[0];
      display.sources = sources;
    }
  }
  return display;
}

function project(ledger) {
  const origins = {};
  const exclusions = clone(ledger.exclusions || {});

  for (const [lemma, entry] of Object.entries(ledger.entries || {})) {
    if (entry.classification === "C") {
      const group = entry.exclusion?.group || "general";
      exclusions[group] = exclusions[group] || {};
      exclusions[group][lemma] = entry.exclusion?.reason || "個別調査で安全な語源表示を作成できない";
      continue;
    }
    origins[lemma] = displayFor(entry);
  }

  return {
    origins: {
      meta: clone(ledger.outputMeta?.origins || {}),
      origins,
    },
    roots: {
      meta: clone(ledger.outputMeta?.roots || {}),
      roots: clone(ledger.dictionary?.roots || {}),
      affixes: clone(ledger.dictionary?.affixes || {}),
    },
    excluded: {
      meta: clone(ledger.outputMeta?.excluded || {}),
      excluded: exclusions,
    },
  };
}

function summarize(ledger) {
  const counts = {};
  const statuses = {};
  for (const entry of Object.values(ledger.entries || {})) {
    counts[entry.classification] = (counts[entry.classification] || 0) + 1;
    const status = entry.research?.status || "missing";
    statuses[status] = (statuses[status] || 0) + 1;
  }
  return {
    entries: Object.keys(ledger.entries || {}).length,
    classifications: counts,
    statuses,
    researchTarget: ledger.researchTarget?.lemmas?.length || 0,
    roots: Object.keys(ledger.dictionary?.roots || {}).length,
    affixes: Object.keys(ledger.dictionary?.affixes || {}).length,
  };
}

function assertProjectionMatchesFiles(ledger) {
  const projected = project(ledger);
  const actual = {
    origins: readJson(ORIGINS_PATH),
    roots: readJson(ROOTS_PATH),
    excluded: readJson(EXCLUDED_PATH),
  };
  assert.ok(util.isDeepStrictEqual(projected.origins, actual.origins), "word_origins.json が研究台帳から生成された状態ではありません");
  assert.ok(util.isDeepStrictEqual(projected.roots, actual.roots), "word_roots.json が研究台帳から生成された状態ではありません");
  assert.ok(util.isDeepStrictEqual(projected.excluded, actual.excluded), "word_origin_excluded.json が研究台帳から生成された状態ではありません");
}

function main() {
  const mode = process.argv[2];
  if (!["--init", "--write", "--check"].includes(mode)) {
    console.error("使い方: node scripts/rebuild-word-origin-dictionaries.cjs --init|--write|--check");
    return 2;
  }

  if (mode === "--init") {
    assert.equal(fs.existsSync(RESEARCH_PATH), false, "研究台帳が既に存在します。上書きする場合は手動で確認してください");
    const ledger = buildInitialLedger();
    writeJson(RESEARCH_PATH, ledger);
    console.log(`word origin research ledger: initialized (${JSON.stringify(summarize(ledger))})`);
    return 0;
  }

  assert.ok(fs.existsSync(RESEARCH_PATH), "data/word_origin_research.json が必要です。先に --init を実行してください");
  const ledger = readJson(RESEARCH_PATH);
  const projected = project(ledger);

  if (mode === "--check") {
    assertProjectionMatchesFiles(ledger);
    console.log(`word origin dictionary projections: OK (${JSON.stringify(summarize(ledger))})`);
    return 0;
  }

  writeJson(ORIGINS_PATH, projected.origins, { preserveDisplayArrays: true });
  writeJson(ROOTS_PATH, projected.roots, { preserveDisplayArrays: true });
  writeJson(EXCLUDED_PATH, projected.excluded, { preserveDisplayArrays: true });
  console.log(`word origin dictionary projections: written (${JSON.stringify(summarize(ledger))})`);
  return 0;
}

try {
  process.exitCode = main();
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
