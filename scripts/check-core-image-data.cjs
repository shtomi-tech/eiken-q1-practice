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

function normalizedPhrase(value) {
  return String(value || "").toLowerCase().replace(/\s+/g, " ").trim();
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
  if (entry.siblings != null) {
    assert.ok(Array.isArray(entry.siblings), `${particle}.siblings は配列である必要があります`);
    assert.ok(entry.siblings.length >= 1 && entry.siblings.length <= 4, `${particle}.siblings は1〜4件である必要があります`);
    entry.siblings.forEach((sibling, index) => {
      assertNonEmptyString(sibling && sibling.phrase, `${particle}.siblings[${index}].phrase`);
      assertNonEmptyString(sibling && sibling.gloss, `${particle}.siblings[${index}].gloss`);
    });
  }
  if (entry.senses != null) {
    assert.ok(Array.isArray(entry.senses), `${particle}.senses は配列である必要があります`);
    const senseIds = new Set();
    entry.senses.forEach((sense, index) => {
      const label = `${particle}.senses[${index}]`;
      assert.ok(sense && typeof sense === "object" && !Array.isArray(sense), `${label} が不正です`);
      assertNonEmptyString(sense.id, `${label}.id`);
      assert.ok(!senseIds.has(sense.id), `${particle}: sense id ${sense.id} が重複しています`);
      senseIds.add(sense.id);
      assertNonEmptyString(sense.label, `${label}.label`);
      assert.ok(Array.isArray(sense.siblings), `${label}.siblings は配列である必要があります`);
      assert.ok(sense.siblings.length >= 3 && sense.siblings.length <= 6, `${label}.siblings は3〜6件である必要があります`);
      sense.siblings.forEach((sibling, siblingIndex) => {
        assertNonEmptyString(sibling && sibling.phrase, `${label}.siblings[${siblingIndex}].phrase`);
        assertNonEmptyString(sibling && sibling.gloss, `${label}.siblings[${siblingIndex}].gloss`);
      });
    });
  }
  assert.ok(entry.siblings || entry.senses, `${particle}: siblings または senses が必要です`);
}

let coreImageCount = 0;
const vocabFiles = fs.readdirSync(DATA_DIR)
  .filter((name) => /^vocab_.*\.json$/.test(name))
  .sort();

for (const fileName of vocabFiles) {
  const vocab = readJson(path.join(DATA_DIR, fileName));
  const senseUseCounts = new Map();
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
    const particleEntry = image.particle != null ? particleData.particles[image.particle] : null;
    if (image.particle != null) {
      assertNonEmptyString(image.particle, `${label}: particle`);
      assert.ok(particleEntry, `${label}: particle辞書に ${image.particle} がありません`);
      const phraseTokens = tokens(item.phrase);
      assert.ok(
        tokens(image.particle).every((particleToken) => phraseTokens.includes(particleToken)),
        `${label}: particle が phrase に含まれていません`,
      );
    }
    if (Array.isArray(particleEntry && particleEntry.senses)) {
      assertNonEmptyString(image.particleSense, `${label}: sensesを持つparticleにはparticleSenseが必要です`);
      const senseEntry = particleEntry.senses.find((sense) => sense.id === image.particleSense);
      assert.ok(
        senseEntry,
        `${label}: particleSense ${image.particleSense} が辞書にありません`,
      );
      const senseKey = `${image.particle}\u0000${image.particleSense}`;
      const reference = senseUseCounts.get(senseKey) || {
        particle: image.particle,
        senseId: image.particleSense,
        count: 0,
      };
      reference.count += 1;
      senseUseCounts.set(senseKey, reference);
    } else if (image.particleSense != null) {
      assertNonEmptyString(image.particleSense, `${label}: particleSense`);
      assert.fail(`${label}: particleSenseにはsenses辞書が必要です`);
    }
    if (image.siblings != null) {
      assert.ok(Array.isArray(image.siblings), `${label}: coreImage.siblings は配列である必要があります`);
      assert.ok(image.siblings.length >= 1 && image.siblings.length <= 3, `${label}: coreImage.siblings は1〜3件である必要があります`);
      image.siblings.forEach((sibling, index) => {
        assertNonEmptyString(sibling && sibling.phrase, `${label}: coreImage.siblings[${index}].phrase`);
        assertNonEmptyString(sibling && sibling.gloss, `${label}: coreImage.siblings[${index}].gloss`);
      });
    }
    const senseEntry = image.particleSense && particleEntry && Array.isArray(particleEntry.senses)
      ? particleEntry.senses.find((sense) => sense.id === image.particleSense)
      : null;
    const resolvedSiblings = image.siblings || senseEntry?.siblings || particleEntry?.siblings || [];
    const ownPhrases = new Set([
      normalizedPhrase(item.phrase),
      normalizedPhrase((image.chain || []).filter((step) => step.term).map((step) => step.term).join(" ")),
    ]);
    resolvedSiblings.forEach((sibling) => {
      assert.ok(!ownPhrases.has(normalizedPhrase(sibling.phrase)), `${label}: 仲間例に自分自身を含めないでください`);
    });
    if (image.note != null) assertNonEmptyString(image.note, `${label}: note`);
  }
  for (const { particle, senseId, count } of senseUseCounts.values()) {
    const sense = particleData.particles[particle].senses.find((candidate) => candidate.id === senseId);
    const minimumPoolSize = Math.min(3 + (count - 1), 6);
    assert.ok(
      sense.siblings.length >= minimumPoolSize,
      `${fileName}/${particle}/${senseId}: ${count}件参照されるため仲間例は${minimumPoolSize}件以上必要です`,
    );
  }
}

assert.ok(coreImageCount > 0, "coreImage を持つ熟語が1件以上必要です");
console.log(`core image data contract: OK (${coreImageCount} entries)`);
