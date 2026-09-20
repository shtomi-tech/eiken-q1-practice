"use strict";

const assert = require("node:assert/strict");
const vm = require("node:vm");
const { appJs, extractFunctionBody } = require("./lib/app-source.cjs");

const js = appJs();
const functionSource = [
  "setLearnItem",
  "enterLearnFlash",
  "advanceLearnFromFlash",
  "hasLearnContextResult",
  "recordLearnContextResult",
  "normalizeLearnSessionResume",
].map((name) => extractFunctionBody(js, name)).join("\n");

const items = [
  { key: "a", target: "alpha" },
  { key: "b", target: "bravo" },
  { key: "c", target: "charlie" },
  { key: "d", target: "delta" },
];

function createHarness(contextKeys = new Set(items.map((item) => item.key))) {
  const sandbox = {
    Object,
    Number,
    Boolean,
    Array,
    Math,
    itemKeyOf: (item) => item.key,
    contextItemFor: (item) => item && contextKeys.has(item.key) ? { target: item.target } : null,
    resetContextState: () => {
      sandbox.session.contextRevealed = false;
      sandbox.session.contextPicked = null;
      sandbox.session.contextCorrect = null;
    },
    renderSession: () => {},
    resetSessionScroll: () => {},
  };
  vm.createContext(sandbox);
  vm.runInContext(functionSource, sandbox);
  sandbox.session = {
    mode: "learn",
    items,
    learnIdx: 0,
    learnPhase: null,
    flashIdx: 0,
    stage: null,
    checkIdx: 7,
    contextResults: {},
    contextTotal: 0,
    contextCorrectCount: 0,
    contextRevealed: false,
    contextPicked: null,
    contextCorrect: null,
  };
  return sandbox;
}

const allContext = createHarness();
allContext.setLearnItem(0);
assert.equal(allContext.session.stage, "context", "未回答のContextあり語はContextから始める必要があります");
allContext.recordLearnContextResult(items[0], "wrong", "right");
allContext.enterLearnFlash();
assert.equal(allContext.session.stage, "flash", "Context回答後は同じ語のFlashへ進む必要があります");
allContext.advanceLearnFromFlash();
assert.equal(allContext.session.learnIdx, 1, "Flash後は次語へ進む必要があります");
assert.equal(allContext.session.stage, "context", "未回答の次語はContextへ進む必要があります");
allContext.recordLearnContextResult(items[1], "wrong", "right");
allContext.enterLearnFlash();

// A Flash -> 前へ -> A Flash -> 次へ -> B Flash。B Contextを再出題しない。
allContext.setLearnItem(0, "flash");
allContext.advanceLearnFromFlash();
assert.equal(allContext.session.learnIdx, 1, "前へ戻った後の次へは同じ学習順へ戻る必要があります");
assert.equal(allContext.session.stage, "flash", "回答済みContextは前後移動で再出題してはいけません");

const partialContext = createHarness(new Set(["a", "c"]));
partialContext.setLearnItem(0);
partialContext.recordLearnContextResult(items[0], "right", "right");
partialContext.enterLearnFlash();
partialContext.advanceLearnFromFlash();
assert.equal(partialContext.session.learnIdx, 1, "Contextなし語へ進む必要があります");
assert.equal(partialContext.session.stage, "flash", "Contextなし語はFlashへ直接進む必要があります");

const lastFlash = createHarness();
lastFlash.setLearnItem(items.length - 1, "flash");
lastFlash.advanceLearnFromFlash();
assert.equal(lastFlash.session.stage, "check", "最後のFlash後はMeaning Checkへ進む必要があります");
assert.equal(lastFlash.session.learnPhase, null, "Meaning CheckではlearnPhaseを解除する必要があります");
assert.equal(lastFlash.session.checkIdx, 0, "Meaning Checkは先頭から開始する必要があります");

const immutable = createHarness();
immutable.session.meaningCorrect = 2;
immutable.session.wrongCount = 3;
immutable.session.fsrs = { lapses: 4 };
immutable.session.nextReviewAt = "2030-01-01T00:00:00.000Z";
immutable.recordLearnContextResult(items[0], "first guess", "correct meaning");
immutable.recordLearnContextResult(items[0], "second guess", "correct meaning");
assert.equal(JSON.stringify(immutable.session.contextResults.a), JSON.stringify({
  pickedMeaning: "first guess",
  correctMeaning: "correct meaning",
  correct: false,
}), "初回Context結果を前後移動で上書きしてはいけません");
assert.equal(immutable.session.meaningCorrect, 2, "Context結果をmeaningCorrectへ混ぜてはいけません");
assert.equal(immutable.session.wrongCount, 3, "Context結果をwrongCountへ混ぜてはいけません");
assert.equal(JSON.stringify(immutable.session.fsrs), JSON.stringify({ lapses: 4 }), "Context結果をFSRSへ混ぜてはいけません");
assert.equal(immutable.session.nextReviewAt, "2030-01-01T00:00:00.000Z", "Context結果で復習日時を変更してはいけません");

const resumed = createHarness();
resumed.session.stage = "context";
resumed.session.learnIdx = 1;
resumed.session.contextResults = {
  b: { pickedMeaning: "wrong", correctMeaning: "right", correct: false },
};
resumed.normalizeLearnSessionResume();
assert.equal(resumed.session.learnIdx, 1, "resumeは同じ語のlearnIdxを保持する必要があります");
assert.equal(resumed.session.stage, "flash", "回答済みContextのresumeはFlashから再開する必要があります");
assert.equal(resumed.session.learnPhase, "flash", "回答済みContextのresumeはFlash phaseにする必要があります");

const oldMeaningResume = extractFunctionBody(js, "startMeaningPractice");
assert.match(oldMeaningResume, /stage:\s*"check"/, "意味復習はcheckから始める必要があります");
assert.doesNotMatch(oldMeaningResume, /enterContextOrCheck|contextOrder|contextBeforeFlash|contextIdx/, "意味復習にContext状態を持ち込んではいけません");

const contextRecorder = extractFunctionBody(js, "recordLearnContextResult");
assert.doesNotMatch(contextRecorder, /meaningCorrect|wrongCount|fsrs|nextReviewAt/, "Context記録関数はFSRS・意味成績を変更してはいけません");

console.log("learn state transitions: OK");
