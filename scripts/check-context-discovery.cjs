"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { occurrenceCount } = require("./lib/context-validator.cjs");
const { extractFunctionBody } = require("./lib/app-source.cjs");

const ROOT = path.resolve(__dirname, "..");
const readJson = (file) => JSON.parse(fs.readFileSync(path.join(ROOT, file), "utf8"));
const manifest = readJson("data/manifest.json");
const vocab = readJson("data/vocab_2026-1.json");
const lemmas = readJson("data/lemmas.json");
const context = readJson("data/context_2026-1.json");
const homeSource = fs.readFileSync(path.join(ROOT, "static/src/80-home.js"), "utf8");
const storageSource = fs.readFileSync(path.join(ROOT, "static/src/20-storage.js"), "utf8");
const sessionSource = fs.readFileSync(path.join(ROOT, "static/src/90-learn-session.js"), "utf8");
const stylesSource = fs.readFileSync(path.join(ROOT, "static/styles.css"), "utf8");
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
const vocabByTarget = new Map(vocabItems.map((item) => [item.word || item.phrase, item]));
const cardMeaningByTarget = new Map(vocabItems.map((item) => {
  const surface = item.word || item.phrase;
  const lemma = item.word
    ? (lemmas.lemmas?.[String(surface).toLowerCase()] || surface)
    : surface;
  return [surface, lemmas.entries?.[lemma]?.meaning || item.meaning];
}));
const contextTargets = new Set();
const japanese = /[\u3040-\u30ff\u3400-\u9fff]/;

for (const item of contexts) {
  assert.equal(item.fullEnglish[0], vocabByTarget.get(item.target)?.example,
    `${item.target}: 1文目は暗記カードのexampleと一致させる`);
  assert.ok(!contextTargets.has(item.target), `文脈が重複しています: ${item.target}`);
  contextTargets.add(item.target);
  assert.ok(vocabTargets.has(item.target), `基準セットにない語句です: ${item.target}`);
  assert.equal(item.meaning, cardMeaningByTarget.get(item.target),
    `文脈の意味は暗記カードの意味と一致させてください: ${item.target}`);
  assert.ok(Array.isArray(item.fullEnglish) && item.fullEnglish.length >= 2 && item.fullEnglish.length <= 3,
    `英文は2〜3文にしてください: ${item.target}`);
  const story = item.fullEnglish.join(" ");
  assert.equal(occurrenceCount(story, item.target), 1, `targetは英文中に1回だけ必要です: ${item.target}`);
  assert.ok(!japanese.test(story), `fullEnglishに日本語が混ざっています: ${item.target}`);
  assert.ok(Array.isArray(item.contextClues) && item.contextClues.length >= 2,
    `context clueが不足しています: ${item.target}`);
  for (const clue of item.contextClues) {
    assert.ok(story.toLowerCase().includes(String(clue.text).toLowerCase()),
      `clueが英文中にありません: ${item.target} / ${clue.text}`);
  }
  assert.deepEqual(item.inferencePath.at(-1), item.target, `inferencePathの末尾がtargetではありません: ${item.target}`);
}

assert.deepEqual([...contextTargets].sort(), [...vocabTargets].sort(), "語句と文脈のtarget集合が一致しません");
assert.match(homeSource, /function contextDiscoveryCard\(\)/, "ホームに文脈推測カードが必要です");
const contextDiscoveryCardBody = extractFunctionBody(homeSource, "contextDiscoveryCard");
assert.doesNotMatch(contextDiscoveryCardBody, /startContextPractice\(\)/, "Context Discoveryの入口を独立練習と統合練習に分けないでください");
assert.doesNotMatch(contextDiscoveryCardBody, /startContextLearning\(\)/, "Context Discoveryを通常学習とは別の入口にしないでください");
assert.match(contextDiscoveryCardBody, /setContextDiscoveryEnabled\(!enabled\)/, "文脈推測あり・なしを切り替える必要があります");
assert.match(contextDiscoveryCardBody, /aria-pressed/, "モード切替状態を支援技術へ伝える必要があります");
assert.equal((contextDiscoveryCardBody.match(/contextDiscoveryCta/g) || []).length, 1, "Context DiscoveryのCTAは1つにしてください");
assert.match(storageSource, /function contextDiscoveryEnabled\(\)/, "文脈推測モードの保存値を読む必要があります");
assert.match(extractFunctionBody(storageSource, "contextDiscoveryEnabled"), /=== "on"/, "文脈推測モードは初期状態を「なし」にしてください");
assert.match(extractFunctionBody(storageSource, "contextDiscoveryEnabled"), /catch \(e\) \{ return false; \}/, "保存値を読めない場合も文脈推測なしへ戻してください");
assert.match(extractFunctionBody(storageSource, "contextDiscoveryModeStorageKey"), /scopedStorageKey/, "文脈推測モードは学習者ごとに保存してください");
assert.match(extractFunctionBody(storageSource, "contextDiscoveryModeStorageKey"), /state\.datasetId/, "文脈推測モードはdatasetごとに保存してください");
assert.match(sessionSource, /function startContextPractice\(\)/, "文脈推測セッションの開始処理が必要です");
assert.match(sessionSource, /function startContextLearning\(/, "文脈推測から暗記カードへ進む試用モードが必要です");
assert.match(extractFunctionBody(sessionSource, "startLearn"), /contextDiscoveryEnabled\(\)/, "通常学習は文脈推測モードを参照する必要があります");
assert.match(sessionSource, /function renderContext\(body\)/, "文脈推測画面の描画処理が必要です");
const renderContextBody = extractFunctionBody(sessionSource, "renderContext");
assert.match(sessionSource, /class: "contextSentenceText"[^\n]+contextTextWithTarget\(sentence, item\.target\)/,
  "英文断片は語順を保つ単一inlineコンテナ内へ描画してください");
assert.match(extractFunctionBody(sessionSource, "contextTextWithTarget"), /one's\|my\|your\|his\|her\|our\|their/,
  "one'sを含む語句は本文中の所有格へ置き換わっても強調できる必要があります");
assert.match(stylesSource, /\.contextSentenceText\s*\{[^}]*flex:\s*1 1 auto;[^}]*min-width:\s*0;/s,
  "英文コンテナは行番号の隣で自然に折り返せる必要があります");
assert.match(sessionSource, /function contextMeaningChoices\(item/, "文脈推測の4択生成処理が必要です");
assert.match(sessionSource, /contextChoiceBtn/, "文脈推測の意味4択ボタンが必要です");
assert.match(sessionSource, /contextPicked/, "文脈推測の選択結果を保持する必要があります");
assert.match(renderContextBody, /正しい意味：\$\{correctMeaning\}/,
  "回答後に正しい意味を表示する必要があります");
assert.match(renderContextBody, /この単語を覚える →/,
  "回答後に暗記カードへ進むボタンが必要です");
assert.doesNotMatch(renderContextBody,
  /contextClueList|contextAnswer|item\.inferencePath|item\.inferenceExplanation/,
  "回答後に意味の詳細解説を表示してはいけません");
assert.match(sessionSource, /contextMeaningOf\(context, itemHint/, "文脈の意味は暗記カードの意味を参照する必要があります");
assert.doesNotMatch(sessionSource, /function enterContextOrCheck\(/, "意味復習専用の旧Context統合helperを残してはいけません");
assert.ok(!sessionSource.includes("contextGuess") && !sessionSource.includes("推測をメモ"),
  "文脈推測にメモ入力欄を追加しないでください");
console.log("context discovery data and UI contract: OK (68 contexts)");
