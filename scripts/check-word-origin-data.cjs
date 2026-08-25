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

const cReasons = new Map([
  ["thwart", "general: ゲルマン系の不透明語で、接辞＋語根の分解が学習上の助けにならない"],
  ["balk", "general: ゲルマン系の不透明語で、綴りから安全な語根を取り出せない"],
  ["desertification", "fac: -ficationの接尾辞だけが一致し、前半を安全に分解できない"],
  ["ratification", "fac: -ficationの接尾辞だけが一致し、前半を安全に分解できない"],
  ["altogether", "her: all+togetherのゲルマン系語で、haerereの語根ではない"],
  ["gather", "her: ゲルマン系の語で、haerereの語根ではない"],
  ["heresy", "her: ギリシャ語 hairesis（選択）由来で、haerereの語根ではない"],
  ["inheritance", "her: heres（相続人）由来で、haerere（くっつく）の語根ではない"],
  ["philosopher", "her: ギリシャ語 philos+sophia由来で、haerereの語根ではない"],
  ["synthesis", "her: ギリシャ語 syn+tithenai由来で、haerereの語根ではない"],
  ["synthesize", "her: ギリシャ語 syn+tithenai由来で、haerereの語根ではない"],
  ["tether", "her: ゲルマン系の語で、haerereの語根ではない"],
  ["treacherous", "her: treachery系の語で、haerereの語根ではない"],
  ["impregnable", "reg: prehendere（つかむ）由来で、regereの語根ではない"],
  ["insurrection", "reg: surgere（立ち上がる）由来で、regereの語根ではない"],
  ["regurgitate", "reg: gurges（渦・のど）由来で、regereの語根ではない"],
  ["autonomy", "nom: nomos（法）由来で、nomen/onyma（名前）の語根ではない"],
  ["economic", "nom: oikos+nomos（家の管理）由来で、名前の語根ではない"],
  ["convergence", "gen: vergere（向かう）由来で、genusの語根ではない"],
  ["divulgence", "gen: vulgare（公にする）由来で、genusの語根ではない"],
  ["gently", "gen: gentilis由来だが、今回のgen語根として安全に分解できない"],
  ["insurgent", "gen: surgere（立ち上がる）由来で、genusの語根ではない"],
  ["pungent", "gen: pungere（刺す）由来で、genusの語根ではない"],
  ["installer", "sist: stallum（席）由来で、stare/sistereの語根ではない"],
  ["nostalgia", "sist: ギリシャ語 nostos+algos由来で、stareの語根ではない"],
  ["painstaking", "sist: pain+stakeの英語の組み合わせで、stareの語根ではない"],
  ["stake", "sist: ゲルマン系の語で、stareの語根ではない"],
  ["stammer", "sist: ゲルマン系の語で、stareの語根ではない"],
  ["stampede", "sist: スペイン語系の語で、stareの語根ではない"],
  ["stand", "sist: 古英語由来で、stare/sistereの語根ではない"],
  ["staunch", "sist: ゲルマン・フランス語系の語で、stareの語根ではない"],
  ["immigration", "grat: migrare（移動する）由来で、gratusの語根ではない"],
  ["backlog", "log: back+logの英語の組み合わせで、logos/loquiの語根ではない"],
  ["log", "log: 木材を表すゲルマン系の語で、logos/loquiの語根ではない"],
  ["cavalier", "val: caballus（馬）由来で、valereの語根ではない"],
  ["rivalry", "val: rivus（小川）由来で、valereの語根ではない"],
  ["upheaval", "val: heave（持ち上げる）由来で、valereの語根ではない"],
  ["valley", "val: vallis（谷）由来で、valereの語根ではない"],
  ["livid", "vid: lividus（青黒い）由来で、videreの語根ではない"],
  ["divide", "vid: dividere（di-＋*videre＝分ける）由来で、videre（見る）の語根ではない"],
  ["individual", "vid: individuus（分けられない）由来で、videre（見る）の語根ではない"],
  ["accordingto", "cord: 語源表示対象外の句で、単語の語根カードには載せない"],
  ["curfew", "cur: couvre-feu（火を覆う）由来で、currereの語根ではない"],
  ["curly", "cur: curl系のゲルマン語で、currereの語根ではない"],
  ["obscurity", "cur: obscurus（暗い）由来で、currereの語根ではない"],
  ["security", "cur: securus（心配のない）由来で、currereの語根ではない"],
  ["procure", "cur: procurare（pro＋curare＝世話する）由来で、currereの語根ではない"],
]);
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

console.log(`word origin data contract: OK (${originEntries.length} origins / ${Object.keys(rootsData.roots).length} roots)`);
