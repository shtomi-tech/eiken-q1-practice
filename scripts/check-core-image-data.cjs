const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const DATA_DIR = path.join(ROOT, "data");
const PARTICLE_PATH = path.join(DATA_DIR, "particle_images.json");
const PAGES_WORKFLOW_PATH = path.join(ROOT, ".github", "workflows", "pages.yml");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function tokens(value) {
  return String(value || "").toLowerCase().match(/[a-z]+(?:['-][a-z]+)*/g) || [];
}

const irregularBase = {
  bought: "buy",
  brought: "bring",
  caught: "catch",
  dealt: "deal",
  held: "hold",
  laid: "lay",
  lost: "lose",
  made: "make",
  paid: "pay",
  sold: "sell",
  stood: "stand",
  took: "take",
  went: "go",
};

function relatedTerm(termToken, phraseToken) {
  const termForms = [termToken, irregularBase[termToken] || ""];
  const phraseForms = [phraseToken, irregularBase[phraseToken] || ""];
  return termForms.some((termForm) => phraseForms.some((phraseForm) => (
    termForm === phraseForm
      || (termForm.length >= 3 && phraseForm.length >= 3
        && termForm.slice(0, 3) === phraseForm.slice(0, 3))
  )));
}

function assertNonEmptyString(value, label) {
  assert.equal(typeof value, "string", `${label} は文字列である必要があります`);
  assert.ok(value.trim(), `${label} は空にできません`);
}

assert.ok(fs.existsSync(PARTICLE_PATH), "data/particle_images.json が必要です");
assert.ok(fs.existsSync(PAGES_WORKFLOW_PATH), ".github/workflows/pages.yml が必要です");
assert.match(
  fs.readFileSync(PAGES_WORKFLOW_PATH, "utf8"),
  /cp data\/particle_images\.json _site\/data\//,
  "Pagesの静的ファイル準備でparticle_images.jsonをコピーする必要があります",
);
const particleData = readJson(PARTICLE_PATH);
assert.ok(particleData && typeof particleData === "object", "particle_images.json はオブジェクトである必要があります");
assert.ok(particleData.particles && typeof particleData.particles === "object" && !Array.isArray(particleData.particles), "particles 辞書が必要です");

for (const [particle, entry] of Object.entries(particleData.particles)) {
  assert.ok(entry && typeof entry === "object" && !Array.isArray(entry), `${particle}: 辞書項目が不正です`);
  assertNonEmptyString(entry.core, `${particle}.core`);
  assert.ok(Array.isArray(entry.siblings), `${particle}.siblings は配列である必要があります`);
  assert.ok(entry.siblings.length >= 1 && entry.siblings.length <= 4, `${particle}.siblings は1〜4件である必要があります`);
  entry.siblings.forEach((sibling, index) => {
    assertNonEmptyString(sibling && sibling.phrase, `${particle}.siblings[${index}].phrase`);
    assertNonEmptyString(sibling && sibling.gloss, `${particle}.siblings[${index}].gloss`);
  });
}

let coreImageCount = 0;
const vocabFiles = fs.readdirSync(DATA_DIR)
  .filter((name) => /^vocab_.*\.json$/.test(name))
  .sort();

for (const fileName of vocabFiles) {
  const vocab = readJson(path.join(DATA_DIR, fileName));
  for (const item of vocab.idioms || []) {
    if (!Object.prototype.hasOwnProperty.call(item, "coreImage")) continue;
    coreImageCount += 1;
    const label = `${fileName}/${item.phrase}`;
    const image = item.coreImage;
    assert.ok(image && typeof image === "object" && !Array.isArray(image), `${label}: coreImage が不正です`);
    assert.ok(Array.isArray(image.chain), `${label}: chain は配列である必要があります`);
    assert.ok(image.chain.length >= 2 && image.chain.length <= 5, `${label}: chain は2〜5要素である必要があります`);
    image.chain.forEach((step, index) => {
      assert.ok(step && typeof step === "object" && !Array.isArray(step), `${label}: chain[${index}] が不正です`);
      assertNonEmptyString(step.gloss, `${label}: chain[${index}].gloss`);
      if (Object.prototype.hasOwnProperty.call(step, "term")) {
        assertNonEmptyString(step.term, `${label}: chain[${index}].term`);
        assert.equal(step.term, step.term.toLowerCase(), `${label}: chain[${index}].term は小文字の原形で書きます`);
        assert.ok(
          tokens(step.term).every((termToken) => tokens(item.phrase).some((phraseToken) => relatedTerm(termToken, phraseToken))),
          `${label}: chain[${index}].term が phrase と対応していません`,
        );
      }
    });
    const lastStep = image.chain[image.chain.length - 1];
    assert.ok(!Object.prototype.hasOwnProperty.call(lastStep, "term"), `${label}: chain の最後は導出結果にしてください`);
    if (image.particle != null) {
      assertNonEmptyString(image.particle, `${label}: particle`);
      assert.ok(Object.prototype.hasOwnProperty.call(particleData.particles, image.particle), `${label}: particle辞書に ${image.particle} がありません`);
      const phraseTokens = tokens(item.phrase);
      assert.ok(
        tokens(image.particle).every((particleToken) => phraseTokens.includes(particleToken)),
        `${label}: particle が phrase に含まれていません`,
      );
    }
    if (image.note != null) assertNonEmptyString(image.note, `${label}: note`);
  }
}

assert.ok(coreImageCount > 0, "coreImage を持つ熟語が1件以上必要です");
console.log(`core image data contract: OK (${coreImageCount} entries)`);
