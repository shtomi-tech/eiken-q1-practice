const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const DATA_DIR = path.join(ROOT, "data");
const EXPECTED = {
  "2025-2": [
    "take in", "even out", "figure on", "make do", "hold out", "shoot down", "get over", "snap up",
    "tune up", "touch on", "tear down", "free up", "get down", "round out", "die away", "lay out",
  ],
  "2025-3": [
    "live off", "make for", "pass on", "wipe out", "iron out", "toss in", "take on", "size up",
    "sound off", "draw back", "turn up", "rule out", "chip in", "pull off", "stick around", "bear up",
  ],
  "2026-1": [
    "sank in", "let out", "went under", "lived off", "add up", "read into", "take off", "fall out",
    "slip away", "tear up", "drop out", "follow up", "fed off", "burnt out", "fell through", "ate up",
  ],
};

for (const [round, expectedSurfaces] of Object.entries(EXPECTED)) {
  const vocab = JSON.parse(fs.readFileSync(path.join(DATA_DIR, `vocab_pre1_${round}.json`), "utf8"));
  assert.deepEqual(vocab.idioms || [], [], `${round}: 既存進捗互換のためidiomsへ移してはいけません`);
  const phrasalWords = (vocab.words || []).filter((item) => String(item.word || "").includes(" "));
  assert.deepEqual(
    phrasalWords.map((item) => item.word),
    expectedSurfaces,
    `${round}: 句動詞の表層形・順序を変えてはいけません`,
  );
  for (const item of phrasalWords) {
    assert.ok(item.coreImage && Array.isArray(item.coreImage.chain), `${round}/${item.word}: coreImageが必要です`);
    assert.equal(Object.prototype.hasOwnProperty.call(item, "phrase"), false, `${round}/${item.word}: phraseへ移してはいけません`);
  }
}

console.log("pre1 core image compatibility: OK (48 word-keyed phrasal verbs)");
