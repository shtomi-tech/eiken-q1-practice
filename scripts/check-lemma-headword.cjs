const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const js = fs.readFileSync("static/mode-q1.js", "utf8");
const css = fs.readFileSync("static/styles.css", "utf8");
const data = JSON.parse(fs.readFileSync("data/lemmas.json", "utf8"));

function extractFunctionBody(source, name) {
  const start = source.indexOf(`function ${name}(`);
  assert.ok(start !== -1, `function ${name}( が見つからない`);
  const braceStart = source.indexOf("{", start);
  assert.ok(braceStart !== -1, `${name} の開始 { が見つからない`);
  let depth = 0;
  for (let i = braceStart; i < source.length; i++) {
    if (source[i] === "{") depth++;
    if (source[i] === "}") {
      depth--;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  assert.fail(`${name} の本体を閉じる } が見つからない`);
}

assert.ok(data.lemmas && typeof data.lemmas === "object" && !Array.isArray(data.lemmas));
for (const [key, value] of Object.entries(data.lemmas)) {
  assert.ok(key && key === key.trim().toLowerCase(), `原形キーが正規化されていない: ${key}`);
  assert.ok(typeof value === "string" && value.trim(), `原形値が空: ${key}`);
  assert.notEqual(key, value, `同じ語を原形マップに入れない: ${key}`);
}

const vocabWords = new Set();
for (const name of fs.readdirSync("data").filter((value) => /^vocab_.*\.json$/.test(value))) {
  const vocab = JSON.parse(fs.readFileSync(path.join("data", name), "utf8"));
  for (const item of vocab.words || []) vocabWords.add(String(item.word || "").toLowerCase());
}
for (const key of Object.keys(data.lemmas)) {
  assert.ok(vocabWords.has(key), `語彙データにない原形キー: ${key}`);
}

const buildFlashCard = extractFunctionBody(js, "buildFlashCard");
assert.match(buildFlashCard, /lemmaMap/);
assert.match(buildFlashCard, /flashLemmaNote/);
assert.match(extractFunctionBody(js, "boot"), /data\/lemmas\.json/);

for (const name of ["surfaceOf", "itemKeyOf", "vocabularyAudioPath"]) {
  assert.doesNotMatch(extractFunctionBody(js, name), /lemmaMap|lemmas/,
    `${name} は原形マップを参照してはいけない`);
}

assert.match(css, /\.flashLemmaNote\s*\{/);

console.log(`lemma headword contract: OK (${Object.keys(data.lemmas).length} entries)`);
