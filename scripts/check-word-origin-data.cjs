const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const DATA_DIR = path.join(ROOT, "data");
const LEMMA_PATH = path.join(DATA_DIR, "lemmas.json");
const ROOTS_PATH = path.join(DATA_DIR, "word_roots.json");
const ORIGINS_PATH = path.join(DATA_DIR, "word_origins.json");
const EXCLUDED_PATH = path.join(DATA_DIR, "word_origin_excluded.json");
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
  if (source.length === 1 && hasKanji(source)) return tail.includes(source);
  for (let length = Math.min(6, source.length); length >= 2; length -= 1) {
    for (let start = 0; start + length <= source.length; start += 1) {
      const slice = source.slice(start, start + length);
      if (length < 3 && !hasKanji(slice)) continue;
      if (tail.includes(slice)) return true;
    }
  }
  return false;
}

function validateOriginChain(chain, label) {
  assert.ok(Array.isArray(chain), `${label} はchain配列が必要です`);
  assert.ok(chain.length >= 2 && chain.length <= 5, `${label} は2〜5段にしてください`);
  chain.forEach((step, index) => {
    const stepLabel = `${label}[${index}]`;
    assert.ok(step && typeof step === "object" && !Array.isArray(step), `${stepLabel} が不正です`);
    if (step.term !== undefined) nonEmptyString(step.term, `${stepLabel}.term`);
    nonEmptyString(step.gloss, `${stepLabel}.gloss`);
  });
  const finalStep = chain.at(-1);
  assert.equal(
    Object.prototype.hasOwnProperty.call(finalStep, "term"),
    false,
    `${label} の最終段にはtermを付けず、中心義だけを置いてください`,
  );
  assert.doesNotMatch(finalStep.gloss, /(?:→|->)/, `${label} の最終段には導出矢印を入れず、中心義だけを置いてください`);
}

function validateOriginSources(sources, label) {
  assert.ok(Array.isArray(sources), `${label} はsources配列が必要です`);
  assert.ok(sources.length >= 2, `${label} は複数サイトのURLが必要です`);
  const urls = sources.map((source, index) => {
    const value = nonEmptyString(source, `${label}[${index}]`);
    let parsed;
    try {
      parsed = new URL(value);
    } catch (error) {
      assert.fail(`${label}[${index}] は有効なURLにしてください`);
    }
    assert.ok(["http:", "https:"].includes(parsed.protocol), `${label}[${index}] はhttp(s) URLにしてください`);
    return { value, host: parsed.hostname };
  });
  assert.equal(new Set(urls.map(({ value }) => value)).size, urls.length, `${label} に同じURLを重複登録できません`);
  assert.ok(new Set(urls.map(({ host }) => host)).size >= 2, `${label} は2サイト以上を参照してください`);
  return urls.map(({ value }) => value);
}

assert.equal(
  meaningOverlap("適当 → した", "統合した、固めた"),
  false,
  "意味の活用語尾だけではderivationを通してはいけません",
);

assert.ok(fs.existsSync(LEMMA_PATH), "data/lemmas.json が必要です");
assert.ok(fs.existsSync(ROOTS_PATH), "data/word_roots.json が必要です");
assert.ok(fs.existsSync(ORIGINS_PATH), "data/word_origins.json が必要です");
assert.ok(fs.existsSync(EXCLUDED_PATH), "data/word_origin_excluded.json が必要です");
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
assert.ok(Object.keys(rootsData.roots).length >= 20, "段階1では語根を20個以上登録してください");
assert.ok(Object.keys(rootsData.affixes).length >= 15, "段階1では接辞を15個以上登録してください");

// 段階1では辞書を先に確定させるため、originsから未参照の語根があっても正常です。
const rootNames = new Set(Object.keys(rootsData.roots).map((root) => normalize(root)));
const seenRootVariants = new Map();

for (const [root, entry] of Object.entries(rootsData.roots)) {
  nonEmptyString(root, `roots.${root}`);
  assert.ok(entry && typeof entry === "object" && !Array.isArray(entry), `roots.${root} が不正です`);
  nonEmptyString(entry.gloss, `roots.${root}.gloss`);
  nonEmptyString(entry.origin, `roots.${root}.origin`);
  nonEmptyString(entry.note, `roots.${root}.note`);
  if (entry.variants != null) {
    assert.ok(Array.isArray(entry.variants), `roots.${root}.variants は配列である必要があります`);
    entry.variants.forEach((variant, index) => {
      const normalizedVariant = nonEmptyString(variant, `roots.${root}.variants[${index}]`).toLowerCase();
      assert.notEqual(normalizedVariant, normalize(root), `${root}.variantsにroot自身を重複登録できません`);
      assert.equal(rootNames.has(normalizedVariant), false, `${root}.variantsが他の語根キーと重複しています`);
      const previousRoot = seenRootVariants.get(normalizedVariant);
      assert.equal(previousRoot, undefined, `${root}.variantsが${previousRoot}のvariantsと重複しています`);
      seenRootVariants.set(normalizedVariant, root);
    });
  }
}
for (const [affix, entry] of Object.entries(rootsData.affixes)) {
  nonEmptyString(affix, `affixes.${affix}`);
  assert.ok(entry && typeof entry === "object" && !Array.isArray(entry), `affixes.${affix} が不正です`);
  nonEmptyString(entry.gloss, `affixes.${affix}.gloss`);
  assert.ok(["prefix", "suffix"].includes(entry.kind), `affixes.${affix}.kind はprefix/suffixである必要があります`);
  if (entry.kind === "suffix") {
    assert.match(affix, /^-.+/, `affixes.${affix}: suffixのキーは先頭ハイフン付きである必要があります`);
  } else {
    assert.doesNotMatch(affix, /^-/, `affixes.${affix}: prefixのキーにハイフンは付けません`);
  }
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

const excludedData = readJson(EXCLUDED_PATH);
nonEmptyString(excludedData.meta?.note, "word_origin_excluded.meta.note");
assert.ok(
  excludedData.excluded && typeof excludedData.excluded === "object" && !Array.isArray(excludedData.excluded),
  "excluded 辞書が必要です",
);
// キー=語根名（またはgeneral）、値={ 原形: 理由 }。検査とスタブの両方がこのファイルを読む。
const cReasons = new Map();
for (const [group, words] of Object.entries(excludedData.excluded)) {
  assert.ok(
    group === "general" || Object.prototype.hasOwnProperty.call(rootsData.roots, group),
    `excluded.${group}: キーは語根名かgeneralである必要があります`,
  );
  assert.ok(words && typeof words === "object" && !Array.isArray(words), `excluded.${group} が不正です`);
  for (const [lemma, reason] of Object.entries(words)) {
    nonEmptyString(reason, `excluded.${group}.${lemma}`);
    assert.equal(cReasons.has(lemma), false, `excluded: ${lemma} が複数のグループに重複しています`);
    cReasons.set(lemma, `${group}: ${reason}`);
  }
}
for (const [lemma, reason] of cReasons) {
  nonEmptyString(reason, `cReasons.${lemma}`);
  const reasonRoot = reason.split(":", 1)[0].trim();
  assert.ok(
    reasonRoot === "general" || Object.prototype.hasOwnProperty.call(rootsData.roots, reasonRoot),
    `cReasons.${lemma} の理由には語根名またはgeneralを付けてください`,
  );
}

const originEntries = Object.entries(originsData.origins);
assert.ok(originEntries.length >= 3, "段階0ではパイロット語を3語以上登録してください");
const aOriginsByRoot = new Map();
for (const [lemma, origin] of originEntries) {
  assert.ok(vocabularyMeanings.has(lemma), `${lemma}: lemmas適用後の語彙データに存在しません`);
  assert.ok(origin && typeof origin === "object" && !Array.isArray(origin), `${lemma}: originが不正です`);
  assert.ok(["A", "B"].includes(origin.type), `${lemma}: 段階0のtypeはAまたはBです`);
  nonEmptyString(origin.derivation, `${lemma}.derivation`);
  if (origin.source !== undefined) {
    nonEmptyString(origin.source, `${lemma}.source`);
    assert.match(origin.source, /^https?:\/\/\S+$/, `${lemma}.source は有効なURLにしてください`);
  }
  if (origin.sources !== undefined) {
    const sources = validateOriginSources(origin.sources, `${lemma}.sources`);
    if (origin.source !== undefined) assert.ok(sources.includes(origin.source), `${lemma}.source はsourcesにも含めてください`);
  }
  if (origin.chain !== undefined) {
    validateOriginChain(origin.chain, `${lemma}.chain`);
    const finalGloss = normalize(origin.chain.at(-1).gloss);
    assert.ok(
      vocabularyMeanings.get(lemma).some((meaning) => normalize(meaning) === finalGloss),
      `${lemma}.chainの最終段はvocab meaningと一致させてください`,
    );
  }
  assert.equal(cReasons.has(lemma), false, `${lemma}: C型一覧の語にoriginsを付けてはいけません`);

  if (origin.type === "A") {
    const gloss = nonEmptyString(origin.gloss, `${lemma}.gloss`);
    assert.ok(Array.from(gloss).length <= 16, `${lemma}.gloss は16文字以内にしてください`);
    assert.ok(
      vocabularyMeanings.get(lemma).some((meaning) => String(meaning).includes(gloss)),
      `${lemma}.gloss は語彙データのmeaningの部分文字列である必要があります`,
    );
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
      const spellingForm = form.replace(/^-/, "");
      assert.ok(spellingForm, `${label}.form の綴り部分が空です`);
      assert.ok(normalize(lemma).includes(normalize(spellingForm)), `${label}.form が原形の綴りに含まれていません`);
      if (part.kind !== "root") {
        assert.ok(
          Object.prototype.hasOwnProperty.call(rootsData.affixes, form),
          `${label}.form の接辞 ${form} がaffixes辞書にありません`,
        );
      }
      if (part.kind === "root") {
        rootPartCount += 1;
        assert.ok(rootForms.has(form), `${label}.form はrootまたはvariantsに一致する必要があります`);
      }
    });
    assert.ok(rootPartCount >= 1, `${lemma}: A型にはrootのpartsが1つ以上必要です`);
    const rootLemmas = aOriginsByRoot.get(origin.root) || [];
    rootLemmas.push(lemma);
    aOriginsByRoot.set(origin.root, rootLemmas);
  } else {
    assert.equal(origin.parts, undefined, `${lemma}: B型にpartsは付けません`);
    assert.equal(origin.root, undefined, `${lemma}: B型にrootは付けません`);
  }

  assert.ok(
    vocabularyMeanings.get(lemma).some((meaning) => meaningOverlap(origin.derivation, meaning)),
    `${lemma}: derivationの末尾がvocab meaningの中心義と結び付いていません`,
  );
}

const mock6ManifestEntry = manifest.q1["eiken1-mock-6"];
assert.ok(mock6ManifestEntry && mock6ManifestEntry.vocabUrl, "英検1級模試第6回のvocabUrlが必要です");
const mock6Vocab = readJson(path.resolve(ROOT, mock6ManifestEntry.vocabUrl));
assert.equal(mock6Vocab.words?.length, 84, "英検1級模試第6回は84語を対象にしてください");
for (const item of mock6Vocab.words) {
  const surface = String(item.word || "").toLowerCase();
  const lemma = lemmaMap[surface] || surface;
  const origin = originsData.origins[lemma];
  assert.ok(origin, `mock-6 ${surface}: 語源データが必要です`);
  nonEmptyString(origin.source, `mock-6 ${surface}.source`);
  validateOriginSources(origin.sources, `mock-6 ${surface}.sources`);
  validateOriginChain(origin.chain, `mock-6 ${surface}.chain`);
}

for (const [root, lemmas] of aOriginsByRoot) {
  if (lemmas.length < 2) continue;
  const reverseHits = originEntries.filter(([, origin]) => origin.type === "A" && origin.root === root);
  assert.ok(reverseHits.length >= 2, `${root}: A型の仲間語逆引きが2語未満です`);
  assert.ok(new Set(reverseHits.map(([lemma]) => lemma)).size >= 2, `${root}: A型の仲間語が重複しています`);
}

for (const [lemma, reason] of cReasons) {
  assert.ok(reason.trim(), `${lemma}: C型の理由が空です`);
  assert.equal(Object.prototype.hasOwnProperty.call(originsData.origins, lemma), false, `${lemma}: C型一覧にある語へoriginを付けてはいけません`);
}

const pages = fs.readFileSync(PAGES_WORKFLOW_PATH, "utf8");
assert.match(pages, /cp data\/word_roots\.json data\/word_origins\.json _site\/data\//, "Pagesで語源辞書をコピーする必要があります");
assert.ok(manifest.q1 && typeof manifest.q1 === "object", "manifest.q1 が必要です");

const singleRootCount = [...aOriginsByRoot.values()].filter((lemmas) => lemmas.length === 1).length;
console.log(`word origin roots: ${Object.keys(rootsData.roots).length} roots / ${singleRootCount} single-word roots`);
console.log(`mock-6 word origin chain: OK (${mock6Vocab.words.length} words)`);
console.log(`word origin data contract: OK (${originEntries.length} origins / ${Object.keys(rootsData.roots).length} roots)`);
