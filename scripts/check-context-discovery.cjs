"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const readJson = (file) => JSON.parse(fs.readFileSync(path.join(ROOT, file), "utf8"));
const manifest = readJson("data/manifest.json");
const vocab = readJson("data/vocab_2026-1.json");
const lemmas = readJson("data/lemmas.json");
const context = readJson("data/context_2026-1.json");
const homeSource = fs.readFileSync(path.join(ROOT, "static/src/80-home.js"), "utf8");
const sessionSource = fs.readFileSync(path.join(ROOT, "static/src/90-learn-session.js"), "utf8");
const pagesWorkflow = fs.readFileSync(path.join(ROOT, ".github/workflows/pages.yml"), "utf8");

const dataset = manifest.q1["eiken2-2026-1"];
assert.equal(dataset.contextUrl, "data/context_2026-1.json", "2級第1セットのcontextUrlが必要");
assert.equal(dataset.contextTotal, 68, "2級第1セットの文脈数が必要");
assert.match(pagesWorkflow, /cp data\/context_\*\.json _site\/data\//, "Pages公開物に文脈データを含める必要があります");
assert.equal(context.meta.count, 68, "文脈データの件数メタデータが不正です");

const vocabItems = [...(vocab.words || []), ...(vocab.idioms || [])];
const contexts = context.contexts || [];
assert.equal(vocabItems.length, 68, "基準セットの語句数が不正です");
assert.equal(contexts.length, vocabItems.length, "語句と文脈の件数が一致しません");

const vocabTargets = new Set(vocabItems.map((item) => item.word || item.phrase));
const cardMeaningByTarget = new Map(vocabItems.map((item) => {
  const surface = item.word || item.phrase;
  const lemma = item.word
    ? (lemmas.lemmas?.[String(surface).toLowerCase()] || surface)
    : surface;
  return [surface, lemmas.entries?.[lemma]?.meaning || item.meaning];
}));
const contextTargets = new Set();
const japanese = /[\u3040-\u30ff\u3400-\u9fff]/;
const countOf = (text, needle) => {
  const source = String(text).toLowerCase();
  const target = String(needle).toLowerCase();
  return target ? source.split(target).length - 1 : 0;
};

for (const item of contexts) {
  assert.ok(!contextTargets.has(item.target), `文脈が重複しています: ${item.target}`);
  contextTargets.add(item.target);
  assert.ok(vocabTargets.has(item.target), `基準セットにない語句です: ${item.target}`);
  assert.equal(item.meaning, cardMeaningByTarget.get(item.target),
    `文脈の意味は暗記カードの意味と一致させてください: ${item.target}`);
  assert.ok(Array.isArray(item.fullEnglish) && item.fullEnglish.length >= 2 && item.fullEnglish.length <= 3,
    `英文は2〜3文にしてください: ${item.target}`);
  const story = item.fullEnglish.join(" ");
  assert.equal(countOf(story, item.target), 1, `targetは英文中に1回だけ必要です: ${item.target}`);
  assert.ok(!japanese.test(story), `fullEnglishに日本語が混ざっています: ${item.target}`);
  assert.ok(Array.isArray(item.contextClues) && item.contextClues.length >= 2,
    `context clueが不足しています: ${item.target}`);
  for (const clue of item.contextClues) {
    assert.ok(story.toLowerCase().includes(String(clue.text).toLowerCase()),
      `clueが英文中にありません: ${item.target} / ${clue.text}`);
  }
  assert.deepEqual(item.inferencePath.at(-1), item.target, `inferencePathの末尾がtargetではありません: ${item.target}`);
  for (const [key, value] of Object.entries(item.validation || {})) {
    assert.equal(value, true, `validation.${key}がfalseです: ${item.target}`);
  }
}

assert.deepEqual([...contextTargets].sort(), [...vocabTargets].sort(), "語句と文脈のtarget集合が一致しません");
assert.match(homeSource, /function contextDiscoveryCard\(\)/, "ホームに文脈推測カードが必要です");
assert.match(homeSource, /startContextPractice\(\)/, "ホームから文脈推測を開始できません");
assert.match(sessionSource, /function startContextPractice\(\)/, "文脈推測セッションの開始処理が必要です");
assert.match(sessionSource, /function renderContext\(body\)/, "文脈推測画面の描画処理が必要です");
assert.match(sessionSource, /function contextMeaningChoices\(item/, "文脈推測の4択生成処理が必要です");
assert.match(sessionSource, /contextChoiceBtn/, "文脈推測の意味4択ボタンが必要です");
assert.match(sessionSource, /contextPicked/, "文脈推測の選択結果を保持する必要があります");
assert.match(sessionSource, /contextClues/, "文脈の手がかり表示が必要です");
assert.match(sessionSource, /contextMeaningOf\(context, itemHint/, "文脈の意味は暗記カードの意味を参照する必要があります");
assert.match(sessionSource, /enterContextOrCheck\(\)/, "既存の意味4択の前に文脈推測を挿入する必要があります");
console.log("context discovery data and UI contract: OK (68 contexts)");
