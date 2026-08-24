const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const DATA_DIR = path.join(ROOT, "data");
const LEMMA_PATH = path.join(DATA_DIR, "lemmas.json");
const ROOTS_PATH = path.join(DATA_DIR, "word_roots.json");
const ORIGINS_PATH = path.join(DATA_DIR, "word_origins.json");
const MANIFEST_PATH = path.join(DATA_DIR, "manifest.json");
const PAGES_WORKFLOW_PATH = path.join(ROOT, ".github", "workflows", "pages.yml");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function nonEmptyString(value, label) {
  assert.equal(typeof value, "string", `${label} は文字列である必要があります`);
  assert.ok(value.trim(), `${label} は空にできません`);
  return value.trim();
}

function normalize(value) {
  return String(value || "").toLowerCase().replace(/\s+/g, "");
}

function hasKanji(value) {
  return /[一-龯]/.test(value);
}

function meaningOverlap(derivation, meaning) {
  const tail = normalize(String(derivation).split(/(?:→|->)/).at(-1));
  const source = normalize(meaning);
  for (let length = Math.min(6, source.length); length >= 2; length -= 1) {
    for (let start = 0; start + length <= source.length; start += 1) {
      const slice = source.slice(start, start + length);
      if (length < 3 && !hasKanji(slice)) continue;
      if (tail.includes(slice)) return true;
    }
  }
  return false;
}

assert.equal(
  meaningOverlap("適当 → した", "統合した、固めた"),
  false,
  "意味の活用語尾だけではderivationを通してはいけません",
);

assert.ok(fs.existsSync(LEMMA_PATH), "data/lemmas.json が必要です");
assert.ok(fs.existsSync(ROOTS_PATH), "data/word_roots.json が必要です");
assert.ok(fs.existsSync(ORIGINS_PATH), "data/word_origins.json が必要です");
assert.ok(fs.existsSync(MANIFEST_PATH), "data/manifest.json が必要です");
assert.ok(fs.existsSync(PAGES_WORKFLOW_PATH), ".github/workflows/pages.yml が必要です");

const lemmaData = readJson(LEMMA_PATH);
const rootsData = readJson(ROOTS_PATH);
const originsData = readJson(ORIGINS_PATH);
const manifest = readJson(MANIFEST_PATH);

assert.ok(rootsData && typeof rootsData === "object", "word_roots.json はオブジェクトである必要があります");
assert.ok(originsData && typeof originsData === "object", "word_origins.json はオブジェクトである必要があります");
nonEmptyString(rootsData.meta?.note, "word_roots.meta.note");
nonEmptyString(originsData.meta?.note, "word_origins.meta.note");
assert.ok(rootsData.roots && typeof rootsData.roots === "object" && !Array.isArray(rootsData.roots), "roots 辞書が必要です");
assert.ok(rootsData.affixes && typeof rootsData.affixes === "object" && !Array.isArray(rootsData.affixes), "affixes 辞書が必要です");
assert.ok(originsData.origins && typeof originsData.origins === "object" && !Array.isArray(originsData.origins), "origins 辞書が必要です");

for (const [root, entry] of Object.entries(rootsData.roots)) {
  nonEmptyString(root, `roots.${root}`);
  assert.ok(entry && typeof entry === "object" && !Array.isArray(entry), `roots.${root} が不正です`);
  nonEmptyString(entry.gloss, `roots.${root}.gloss`);
  nonEmptyString(entry.origin, `roots.${root}.origin`);
  if (entry.note != null) nonEmptyString(entry.note, `roots.${root}.note`);
  if (entry.variants != null) {
    assert.ok(Array.isArray(entry.variants), `roots.${root}.variants は配列である必要があります`);
    entry.variants.forEach((variant, index) => nonEmptyString(variant, `roots.${root}.variants[${index}]`));
  }
}
for (const [affix, entry] of Object.entries(rootsData.affixes)) {
  nonEmptyString(affix, `affixes.${affix}`);
  assert.ok(entry && typeof entry === "object" && !Array.isArray(entry), `affixes.${affix} が不正です`);
  nonEmptyString(entry.gloss, `affixes.${affix}.gloss`);
  assert.ok(["prefix", "suffix"].includes(entry.kind), `affixes.${affix}.kind はprefix/suffixである必要があります`);
}

const lemmaMap = Object.fromEntries(
  Object.entries(lemmaData.lemmas || {}).map(([surface, lemma]) => [surface.toLowerCase(), String(lemma).toLowerCase()]),
);
const vocabularyMeanings = new Map();
for (const fileName of fs.readdirSync(DATA_DIR).filter((name) => /^vocab_.*\.json$/.test(name))) {
  const vocab = readJson(path.join(DATA_DIR, fileName));
  for (const item of vocab.words || []) {
    const surface = String(item.word || "").toLowerCase();
    const lemma = lemmaMap[surface] || surface;
    const meanings = vocabularyMeanings.get(lemma) || [];
    meanings.push(String(item.meaning || ""));
    vocabularyMeanings.set(lemma, meanings);
  }
}

const cReasons = new Map([
  ["thwart", "ゲルマン系の不透明語で、接辞＋語根の分解が学習上の助けにならない"],
  ["balk", "ゲルマン系の不透明語で、綴りから安全な語根を取り出せない"],
]);
for (const [lemma, reason] of cReasons) nonEmptyString(reason, `cReasons.${lemma}`);

const originEntries = Object.entries(originsData.origins);
assert.ok(originEntries.length >= 3, "段階0ではパイロット語を3語以上登録してください");
for (const [lemma, origin] of originEntries) {
  assert.ok(vocabularyMeanings.has(lemma), `${lemma}: lemmas適用後の語彙データに存在しません`);
  assert.ok(origin && typeof origin === "object" && !Array.isArray(origin), `${lemma}: originが不正です`);
  assert.ok(["A", "B"].includes(origin.type), `${lemma}: 段階0のtypeはAまたはBです`);
  nonEmptyString(origin.derivation, `${lemma}.derivation`);
  assert.equal(cReasons.has(lemma), false, `${lemma}: C型一覧の語にoriginsを付けてはいけません`);

  if (origin.type === "A") {
    nonEmptyString(origin.root, `${lemma}.root`);
    const rootEntry = rootsData.roots[origin.root];
    assert.ok(rootEntry, `${lemma}: root ${origin.root} が辞書にありません`);
    assert.ok(Array.isArray(origin.parts) && origin.parts.length >= 2, `${lemma}: A型にはpartsが必要です`);
    const rootForms = new Set([origin.root, ...(rootEntry.variants || [])].map((form) => String(form).toLowerCase()));
    let rootPartCount = 0;
    origin.parts.forEach((part, index) => {
      const label = `${lemma}.parts[${index}]`;
      assert.ok(part && typeof part === "object" && !Array.isArray(part), `${label} が不正です`);
      const form = nonEmptyString(part.form, `${label}.form`).toLowerCase();
      assert.ok(["prefix", "root", "suffix"].includes(part.kind), `${label}.kind が不正です`);
      nonEmptyString(part.gloss, `${label}.gloss`);
      assert.ok(normalize(lemma).includes(normalize(form)), `${label}.form が原形の綴りに含まれていません`);
      if (part.kind === "root") {
        rootPartCount += 1;
        assert.ok(rootForms.has(form), `${label}.form はrootまたはvariantsに一致する必要があります`);
      }
    });
    assert.ok(rootPartCount >= 1, `${lemma}: A型にはrootのpartsが1つ以上必要です`);
  } else {
    assert.equal(origin.parts, undefined, `${lemma}: B型にpartsは付けません`);
    assert.equal(origin.root, undefined, `${lemma}: B型にrootは付けません`);
  }

  assert.ok(
    vocabularyMeanings.get(lemma).some((meaning) => meaningOverlap(origin.derivation, meaning)),
    `${lemma}: derivationの末尾がvocab meaningの中心義と結び付いていません`,
  );
}

for (const [lemma, reason] of cReasons) {
  assert.ok(reason.trim(), `${lemma}: C型の理由が空です`);
  assert.equal(Object.prototype.hasOwnProperty.call(originsData.origins, lemma), false, `${lemma}: C型一覧にある語へoriginを付けてはいけません`);
}

const pages = fs.readFileSync(PAGES_WORKFLOW_PATH, "utf8");
assert.match(pages, /cp data\/word_roots\.json data\/word_origins\.json _site\/data\//, "Pagesで語源辞書をコピーする必要があります");
assert.ok(manifest.q1 && typeof manifest.q1 === "object", "manifest.q1 が必要です");

console.log(`word origin data contract: OK (${originEntries.length} origins / ${Object.keys(rootsData.roots).length} roots)`);
