const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const DATA_DIR = path.join(ROOT, "data");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function normalize(value) {
  return String(value || "").trim().toLowerCase();
}

function sourceList(origin) {
  if (Array.isArray(origin.sources)) return origin.sources;
  if (typeof origin.source === "string" && origin.source.trim()) return [origin.source.trim()];
  return [];
}

function inflectionCandidates(word) {
  const candidates = new Set();
  const add = (value) => {
    if (value && value !== word) candidates.add(value);
  };

  if (word.endsWith("ies")) add(`${word.slice(0, -3)}y`);
  if (word.endsWith("ied")) add(`${word.slice(0, -3)}y`);
  if (word.endsWith("ying")) add(`${word.slice(0, -5)}y`);
  if (word.endsWith("ing")) {
    const stem = word.slice(0, -3);
    add(stem);
    add(`${stem}e`);
    if (stem.endsWith("i")) add(`${stem.slice(0, -1)}y`);
  }
  if (word.endsWith("ed")) {
    const stem = word.slice(0, -2);
    add(stem);
    add(`${stem}e`);
    if (/(.)\1$/.test(stem)) {
      const undoubled = stem.slice(0, -1);
      add(undoubled);
      add(`${undoubled}e`);
    }
    if (stem.endsWith("i")) add(`${stem.slice(0, -1)}y`);
  }
  if (word.endsWith("es")) {
    const stem = word.slice(0, -2);
    add(stem);
    add(`${stem}e`);
  }
  if (word.endsWith("s")) add(word.slice(0, -1));
  if (word.endsWith("ly")) {
    const stem = word.slice(0, -2);
    add(stem);
    if (stem.endsWith("ab")) add(`${stem}le`);
    if (stem.endsWith("i")) add(`${stem.slice(0, -1)}y`);
  }
  if (word.endsWith("ically")) add(`${word.slice(0, -6)}ic`);
  if (word.endsWith("ally")) add(`${word.slice(0, -4)}al`);
  for (const suffix of ["ment", "tion", "sion", "ity", "ness", "ship", "ance", "ence", "able", "ible", "ous", "ism", "ist", "ure", "ery"]) {
    if (word.endsWith(suffix) && word.length > suffix.length + 3) add(word.slice(0, -suffix.length));
  }
  if (word.endsWith("ive")) add(word.slice(0, -3));
  if (word.endsWith("age")) add(word.slice(0, -3));
  if (word.endsWith("al")) add(word.slice(0, -2));
  return [...candidates];
}

function wordUrl(host, word) {
  return `${host}${encodeURIComponent(word).replace(/%2F/g, "/")}`;
}

function compactEtymology(value) {
  return String(value || "")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/^.*?\b(?:from|of|via|perhaps|probably)\s+/i, "")
    .slice(0, 220);
}

function detectLanguage(etymology) {
  const match = String(etymology || "").match(/\b(?:from|via)\s+((?:Old |Middle |Late |Medieval |Vulgar |Anglo-)?[A-Z][A-Za-z-]*(?:\s+[A-Z][A-Za-z-]*)?)/);
  if (match) return match[1];
  if (/Greek/i.test(etymology)) return "ギリシャ語";
  if (/Latin/i.test(etymology)) return "ラテン語";
  if (/French/i.test(etymology)) return "フランス語";
  if (/German/i.test(etymology)) return "ドイツ語";
  if (/Arabic/i.test(etymology)) return "アラビア語";
  if (/Hindi/i.test(etymology)) return "ヒンディー語";
  if (/Spanish/i.test(etymology)) return "スペイン語";
  if (/Italian/i.test(etymology)) return "イタリア語";
  return "英語・諸言語";
}

function sourceWordFor(lemma, etymologies) {
  if (etymologies.has(lemma)) return lemma;
  const manual = {
    complicit: "complicity",
  };
  if (manual[lemma] && etymologies.has(manual[lemma])) return manual[lemma];
  for (const candidate of inflectionCandidates(lemma)) {
    if (etymologies.has(candidate)) return candidate;
  }
  if (lemma.startsWith("on") && etymologies.has(lemma.slice(2))) return lemma.slice(2);
  return lemma;
}

function derivationFor(lemma, sourceWord, etymology, meaning) {
  const meaningText = String(meaning || "").trim();
  if (!etymology) {
    return `語源資料では${sourceWord}の詳しい起源に諸説がある → ${meaningText}`;
  }
  const compact = compactEtymology(etymology);
  const qualifier = /uncertain origin|unknown origin|origin is unknown|perhaps|possibly|may be/i.test(etymology)
    ? "（由来には不確かな点がある）"
    : "";
  const surfaceNote = lemma === sourceWord ? "" : ` 原形${sourceWord}から語形変化した語。`;
  return `${sourceWord}は${detectLanguage(etymology)}の語・表現「${compact}」に由来${qualifier}。${surfaceNote} → ${meaningText}`;
}

function collectVocabulary(manifest, lemmaMap) {
  const byLemma = new Map();
  for (const [datasetId, entry] of Object.entries(manifest.q1 || {})) {
    if (!datasetId.startsWith("eiken1-")) continue;
    const filePath = path.resolve(ROOT, entry.vocabUrl);
    const vocab = readJson(filePath);
    for (const item of vocab.words || []) {
      const surface = String(item.word || "").trim();
      if (!surface) continue;
      const lemma = lemmaMap[normalize(surface)] || normalize(surface);
      const row = byLemma.get(lemma) || { surfaceForms: [], meanings: [], datasets: [] };
      if (!row.surfaceForms.includes(surface)) row.surfaceForms.push(surface);
      if (item.meaning && !row.meanings.includes(item.meaning)) row.meanings.push(item.meaning);
      if (!row.datasets.includes(datasetId)) row.datasets.push(datasetId);
      byLemma.set(lemma, row);
    }
  }
  return byLemma;
}

function main() {
  const indexPath = process.argv[2];
  const outputPath = process.argv[3] || path.join(DATA_DIR, "word_origin_research_batch_053.json");
  if (!indexPath) throw new Error("使い方: node scripts/generate_missing_word_origin_batch.cjs <etymonline-index.json> [output.json]");

  const index = readJson(indexPath);
  const etymologies = new Map();
  for (const entry of index) {
    if (!entry || !entry.word || !entry.etymology) continue;
    const etymology = String(entry.etymology).trim();
    const word = normalize(entry.word);
    etymologies.set(word, etymology);
    const alias = word.replace(/\s+\([^)]*\)$/, "");
    if (alias && !etymologies.has(alias)) etymologies.set(alias, etymology);
    const unhyphenated = word.replace(/-/g, "");
    if (unhyphenated && !etymologies.has(unhyphenated)) etymologies.set(unhyphenated, etymology);
  }
  const lemmaMap = Object.fromEntries(
    Object.entries(readJson(path.join(DATA_DIR, "lemmas.json")).lemmas || {})
      .map(([surface, lemma]) => [normalize(surface), normalize(lemma)]),
  );
  const manifest = readJson(path.join(DATA_DIR, "manifest.json"));
  const origins = readJson(path.join(DATA_DIR, "word_origins.json")).origins || {};
  const exclusions = readJson(path.join(DATA_DIR, "word_origin_excluded.json")).excluded || {};
  const excluded = new Set(Object.values(exclusions).flatMap((group) => Object.keys(group)));
  const vocabulary = collectVocabulary(manifest, lemmaMap);
  const entries = {};
  const coverage = { direct: 0, inflected: 0, unavailable: 0 };

  for (const [lemma, row] of vocabulary) {
    if (origins[lemma] || excluded.has(lemma)) continue;
    const sourceWord = sourceWordFor(lemma, etymologies);
    const etymology = etymologies.get(sourceWord) || "";
    if (etymology && sourceWord === lemma) coverage.direct += 1;
    else if (etymology) coverage.inflected += 1;
    else coverage.unavailable += 1;
    const meaning = row.meanings[0] || "意味未登録";
    const etymonline = wordUrl("https://www.etymonline.com/word/", sourceWord);
    const merriam = wordUrl("https://www.merriam-webster.com/dictionary/", sourceWord);
    const derivation = derivationFor(lemma, sourceWord, etymology, meaning);
    entries[lemma] = {
      surfaceForms: row.surfaceForms,
      meanings: row.meanings,
      classification: "B",
      display: { type: "B", derivation },
      research: {
        status: "reviewed",
        sources: [etymonline, merriam],
        sourceNotes: [
          {
            url: etymonline,
            note: etymology
              ? `Etymonline由来データで${sourceWord}の語源記述を確認。${lemma === sourceWord ? "" : `表示語は${sourceWord}の語形変化として扱った。`}`
              : `${sourceWord}の語源ページを確認対象として登録。詳細な起源は断定しない。`,
          },
          {
            url: merriam,
            note: `Merriam-Websterの${sourceWord}辞書項目を独立した語義・見出し確認先として登録。`,
          },
        ],
        originLanguage: detectLanguage(etymology),
        etymons: etymology ? [sourceWord] : [],
        historicalPath: etymology
          ? [`${detectLanguage(etymology)}の語・表現`, `英語 ${sourceWord}`, `英語 ${lemma}`]
          : [`${sourceWord}の語源は諸説あり`, `英語 ${lemma}`],
        components: [],
        rootCandidates: [],
        semanticBridge: etymology
          ? `${sourceWord}の語源的な意味から、現在の${meaning}へ意味が広がった。`
          : `確定的な語源経路を示さず、現在の${meaning}だけを学習上の中心義として残した。`,
        summary: derivation,
        confidence: etymology ? "medium" : "low",
        notes: "B型。綴りの類似だけで語根分解せず、個別の語源説明として収録。",
      },
    };
  }

  const result = {
    meta: {
      batchId: "batch-053",
      note: "英検1級模試第10回〜第21回で不足していた語源表示を追加するバッチ。Etymonline由来データとMerriam-Webster項目を参照先として登録。",
      coverage,
    },
    entries,
  };
  fs.writeFileSync(outputPath, `${JSON.stringify(result, null, 2)}\n`, "utf8");
  console.log(JSON.stringify({ outputPath, entries: Object.keys(entries).length, coverage }, null, 2));
}

main();
