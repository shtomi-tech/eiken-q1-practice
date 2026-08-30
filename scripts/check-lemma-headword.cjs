const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const { appCss, appJs, extractFunctionBody, readJson, readText } = require("./lib/app-source.cjs");

const js = appJs();
const css = appCss();
const data = readJson("data/lemmas.json");
const pages = readText(".github/workflows/pages.yml");
const buildScript = readText("scripts/build_lemma_entries.py");
const allowMissingAudio = process.argv.includes("--allow-missing-audio");
const flashcardLemmas = data.flashcardLemmas && typeof data.flashcardLemmas === "object" && !Array.isArray(data.flashcardLemmas)
  ? data.flashcardLemmas
  : {};

function audioSlug(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[’']/g, "'")
    .replace(/\b(one's|his|her|my|your|our|their|its)\b/g, "@poss")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function normalizeMeaning(value) {
  return String(value || "")
    .trim()
    .replace(/[（(]複数[）)]/g, "")
    .replace(/\s+/g, " ")
    .replace(/する[（(]こと[）)]/g, "する")
    .replace(/[（(]こと[）)]/g, "")
    .replace(/／/g, "、")
    .replace(/^[ 、]+|[ 、]+$/g, "");
}


assert.equal(data.meta?.schemaVersion, 2, "lemmas.json はschemaVersion 2である必要があります");
assert.ok(data.lemmas && typeof data.lemmas === "object" && !Array.isArray(data.lemmas));
assert.ok(data.entries && typeof data.entries === "object" && !Array.isArray(data.entries));
for (const [key, value] of Object.entries(data.lemmas)) {
  assert.ok(key && key === key.trim().toLowerCase(), `原形キーが正規化されていない: ${key}`);
  assert.ok(typeof value === "string" && value.trim(), `原形値が空: ${key}`);
  assert.equal(value, value.trim().toLowerCase(), `原形値が正規化されていない: ${key}`);
  assert.notEqual(key, value, `同じ語を原形マップに入れない: ${key}`);
}

const vocabWords = new Set();
for (const name of fs.readdirSync("data").filter((value) => /^vocab_.*\.json$/.test(value))) {
  const vocab = JSON.parse(fs.readFileSync(path.join("data", name), "utf8"));
  for (const item of vocab.words || []) vocabWords.add(String(item.word || "").toLowerCase());
}
for (const [surface, lemma] of Object.entries(flashcardLemmas)) {
  assert.equal(surface, surface.trim().toLowerCase(), `暗記カード原形キーが正規化されていない: ${surface}`);
  assert.ok(typeof lemma === "string" && lemma.trim(), `暗記カード原形値が空: ${surface}`);
  assert.equal(lemma, lemma.trim().toLowerCase(), `暗記カード原形値が正規化されていない: ${surface}`);
  assert.notEqual(surface, lemma, `暗記カード原形マップに同じ語を入れない: ${surface}`);
  assert.ok(vocabWords.has(surface), `暗記カード原形マップの出題形が語彙データにありません: ${surface}`);
}
for (const key of Object.keys(data.lemmas)) {
  assert.ok(vocabWords.has(key), `語彙データにない原形キー: ${key}`);
}

const targetLemmas = new Set(Object.values(data.lemmas));
assert.equal(data.meta?.meaningReviewedEntries, targetLemmas.size,
  "全原形の意味監査件数を記録する必要があります");
assert.equal(data.meta?.posReviewedEntries, targetLemmas.size,
  "全原形の品詞監査件数を記録する必要があります");
assert.equal(Object.keys(data.entries).length, targetLemmas.size,
  "辞書エントリは原形ごとに1件必要です");
const expectedSurfaces = new Map([...targetLemmas].map((lemma) => [lemma, new Set()]));
const expectedSourceMeanings = new Map([...targetLemmas].map((lemma) => [lemma, new Set()]));
for (const name of fs.readdirSync("data").filter((value) => /^vocab_.*\.json$/.test(value))) {
  const vocab = JSON.parse(fs.readFileSync(path.join("data", name), "utf8"));
  for (const item of vocab.words || []) {
    const surface = String(item.word || "").trim();
    const key = surface.toLowerCase();
    const lemma = data.lemmas[key] || (targetLemmas.has(key) ? key : "");
    if (lemma) {
      expectedSurfaces.get(lemma).add(surface);
      const meaning = normalizeMeaning(item.meaning);
      if (meaning) expectedSourceMeanings.get(lemma).add(meaning);
    }
  }
}

const meaningReviewSnapshot = [...targetLemmas]
  .sort()
  .map((lemma) => [lemma, [...expectedSourceMeanings.get(lemma)].sort(), data.entries[lemma]?.meaning || ""]);
const meaningReviewDigest = crypto
  .createHash("sha256")
  .update(JSON.stringify(meaningReviewSnapshot), "utf8")
  .digest("hex");
const reviewedDigestMatch = buildScript.match(/REVIEWED_MEANING_DIGEST\s*=\s*"([0-9a-f]{64})"/);
assert.ok(reviewedDigestMatch, "語義レビューの承認済みハッシュがありません");
assert.equal(data.meta?.meaningReviewDigest, meaningReviewDigest,
  "元語義または統合後語義がレビュー後に変更されています");
assert.equal(reviewedDigestMatch[1], meaningReviewDigest,
  "語義レビューの承認済みハッシュが現在のデータと一致しません");
assert.equal(data.meta?.meaningReviewedSourceMeanings,
  meaningReviewSnapshot.reduce((sum, row) => sum + row[1].length, 0),
  "レビュー済みの元語義件数が一致しません");

const audioPaths = new Set();
let missingAudio = 0;
for (const lemma of targetLemmas) {
  const entry = data.entries[lemma];
  assert.ok(entry && typeof entry === "object" && !Array.isArray(entry), `辞書エントリがありません: ${lemma}`);
  assert.equal(lemma, lemma.trim().toLowerCase(), `辞書キーが正規化されていない: ${lemma}`);
  assert.ok(typeof entry.meaning === "string" && entry.meaning.trim(), `辞書的意味が空です: ${lemma}`);
  assert.match(entry.ipa, /^\/.*\/$/, `原形IPAが不正です: ${lemma}`);
  assert.ok(typeof entry.audio === "string" && entry.audio, `原形音声パスが空です: ${lemma}`);
  assert.equal(entry.audio, `assets/audio/lemma/${audioSlug(lemma)}.mp3`, `原形音声パスが規約外です: ${lemma}`);
  assert.ok(!audioPaths.has(entry.audio), `原形音声パスが衝突しています: ${entry.audio}`);
  audioPaths.add(entry.audio);
  assert.ok(typeof entry.pos === "string" && entry.pos.trim(), `辞書品詞が空です: ${lemma}`);
  assert.equal(entry.reviewed, true, `辞書エントリがレビュー済みとして記録されていません: ${lemma}`);
  assert.ok(Array.isArray(entry.surfaces) && entry.surfaces.length, `出題形一覧が空です: ${lemma}`);
  assert.deepEqual(new Set(entry.surfaces), expectedSurfaces.get(lemma), `出題形一覧が不一致です: ${lemma}`);
  for (const surface of entry.surfaces) {
    assert.ok(vocabWords.has(String(surface).toLowerCase()), `語彙データにない出題形です: ${lemma} <- ${surface}`);
    const key = String(surface).toLowerCase();
    assert.equal(data.lemmas[key] || key, lemma, `出題形が別の辞書へ解決されます: ${surface}`);
  }
  const audioPath = path.resolve(entry.audio);
  if (!fs.existsSync(audioPath) || fs.statSync(audioPath).size === 0) missingAudio += 1;
}

assert.equal(data.entries.liaison.meaning, "連絡、連携、協力関係；密通",
  "liaison の収録済み語義が統合されていません");
assert.equal(data.entries.scamper.meaning, "走り回る、ちょこちょこ走る、走り去る",
  "scamper の収録済み語義が統合されていません");
assert.equal(data.entries.deify.pos, "動詞", "deify の原形品詞が不正です");
assert.equal(data.entries.incarcerate.pos, "動詞", "incarcerate の原形品詞が不正です");
assert.equal(data.entries.provision.meaning, "条項、備え；食料、備蓄",
  "provision の語義統合が不正です");

assert.match(pages, /mkdir -p _site\/static\/vendor\/harness _site\/data _site\/assets\/audio\/vocab _site\/assets\/audio\/lemma/,
  "Pagesの準備処理に原形音声ディレクトリがありません");
assert.match(pages, /cp -R assets\/audio\/lemma\/\* _site\/assets\/audio\/lemma\//,
  "Pagesで原形音声をコピーしていません");
assert.match(pages, /lemma_audio_count|lemma_count|audio\/lemma/,
  "Pages成果物の原形音声件数チェックがありません");

const buildFlashCard = extractFunctionBody(js, "buildFlashCard");
assert.match(buildFlashCard, /canonicalHeadwordOf/);
assert.match(buildFlashCard, /flashcardLemmaMap/);
assert.match(buildFlashCard, /buildVocabAudioButton\(item, "flashListenButton", true\)/);
assert.match(buildFlashCard, /learningEntryOf/);
assert.match(buildFlashCard, /learningPosOf/);
assert.match(buildFlashCard, /flashLemmaNote/);
const renderCheck = extractFunctionBody(js, "renderCheck");
assert.match(renderCheck, /canonicalHeadwordOf/);
assert.match(renderCheck, /learningMeaningOf/);
assert.match(extractFunctionBody(js, "meaningPoolForItems"), /learningMeaningOf/);
const lemmaAudioPath = extractFunctionBody(js, "lemmaAudioPathOf");
assert.match(lemmaAudioPath, /vocabularyAudioPath/);
assert.match(lemmaAudioPath, /useFlashcardLemma/);
const vocabAudioButton = extractFunctionBody(js, "buildVocabAudioButton");
assert.match(vocabAudioButton, /flashcardLemmaMap/);
assert.match(vocabAudioButton, /useFlashcardLemma/);
const boot = extractFunctionBody(js, "boot");
assert.match(boot, /data\/lemmas\.json/);
assert.match(boot, /lemmaEntries/);
assert.match(boot, /flashcardLemmaMap/);

for (const name of ["surfaceOf", "itemKeyOf", "vocabularyAudioPath"]) {
  assert.doesNotMatch(extractFunctionBody(js, name), /lemmaMap|lemmaEntries|flashcardLemmaMap|lemmas|canonicalHeadwordOf|learningEntryOf/,
    `${name} は原形マップを参照してはいけません`);
}

assert.match(css, /\.flashLemmaNote\s*\{/);

if (missingAudio && !allowMissingAudio) {
  assert.fail(`原形MP3が${missingAudio}/${targetLemmas.size}件不足しています。音声生成後に再実行してください。`);
}
if (missingAudio) {
  console.log(`lemma audio files: allowed missing (${missingAudio}/${targetLemmas.size}; --allow-missing-audio)`);
}
console.log(`lemma headword contract: OK (${Object.keys(data.lemmas).length} map entries / ${targetLemmas.size} dictionary entries)`);
