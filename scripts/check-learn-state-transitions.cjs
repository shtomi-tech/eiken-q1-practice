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
  "normalizeMeaningResume",
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
    contextAvailableTotal: contextKeys.size,
    contextTotal: 0,
    contextCorrectCount: 0,
    contextRevealed: false,
    contextPicked: null,
    contextCorrect: null,
  };
  return sandbox;
}

const allContext = createHarness();
for (let index = 0; index < items.length; index += 1) {
  allContext.setLearnItem(index);
  assert.equal(allContext.session.stage, "context", "完走ケースでは各Contextあり語をContextから始める必要があります");
  allContext.recordLearnContextResult(items[index], index === 0 ? "right" : "wrong", "right");
  allContext.enterLearnFlash();
  if (index < items.length - 1) allContext.advanceLearnFromFlash();
}
allContext.advanceLearnFromFlash();
assert.equal(allContext.session.contextTotal, allContext.session.contextAvailableTotal, "通常学習完走時はcontextTotalとcontextAvailableTotalが一致する必要があります");
assert.ok(allContext.session.contextCorrectCount <= allContext.session.contextTotal, "contextCorrectCountはcontextTotal以下である必要があります");
assert.equal(allContext.session.stage, "check", "全Context/Flash完走後はMeaning Checkへ進む必要があります");

const firstContext = createHarness();
firstContext.setLearnItem(0);
assert.equal(firstContext.session.stage, "context", "未回答のContextあり語はContextから始める必要があります");
firstContext.recordLearnContextResult(items[0], "wrong", "right");
firstContext.enterLearnFlash();
assert.equal(firstContext.session.stage, "flash", "Context回答後は同じ語のFlashへ進む必要があります");
firstContext.advanceLearnFromFlash();
assert.equal(firstContext.session.learnIdx, 1, "Flash後は次語へ進む必要があります");
assert.equal(firstContext.session.stage, "context", "未回答の次語はContextへ進む必要があります");
firstContext.recordLearnContextResult(items[1], "wrong", "right");
firstContext.enterLearnFlash();

// A Flash -> 前へ -> A Flash -> 次へ -> B Flash。B Contextを再出題しない。
firstContext.setLearnItem(0, "flash");
firstContext.advanceLearnFromFlash();
assert.equal(firstContext.session.learnIdx, 1, "前へ戻った後の次へは同じ学習順へ戻る必要があります");
assert.equal(firstContext.session.stage, "flash", "回答済みContextは前後移動で再出題してはいけません");

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

const noContext = createHarness(new Set());
for (let index = 0; index < items.length - 1; index += 1) {
  noContext.setLearnItem(index);
  assert.equal(noContext.session.stage, "flash", "Context 0件の語はFlashから開始する必要があります");
  noContext.advanceLearnFromFlash();
}
noContext.setLearnItem(items.length - 1);
assert.equal(noContext.session.stage, "flash", "Context 0件の最後の語もFlashから開始する必要があります");
noContext.advanceLearnFromFlash();
assert.equal(noContext.session.stage, "check", "Context 0件でもFlash完走後はMeaning Checkへ進む必要があります");
assert.equal(noContext.session.contextTotal, 0, "Context 0件ではcontextTotalが0である必要があります");
assert.equal(noContext.session.contextAvailableTotal, 0, "Context 0件ではcontextAvailableTotalが0である必要があります");

const contextModeOff = createHarness();
contextModeOff.session.contextEnabled = false;
contextModeOff.session.contextAvailableTotal = 0;
contextModeOff.setLearnItem(0);
assert.equal(contextModeOff.session.stage, "flash", "文脈推測なしモードはContextデータがあってもFlashから始める必要があります");
contextModeOff.advanceLearnFromFlash();
assert.equal(contextModeOff.session.stage, "flash", "文脈推測なしモードは次語もFlashへ進む必要があります");
const doneSource = extractFunctionBody(js, "renderDone");
assert.match(doneSource, /if \(contextAvailableTotal > 0\)/, "Context 0件ではDoneのContext行を条件付き表示にする必要があります");
assert.doesNotMatch(doneSource, /文脈データのない語句のみ/, "Context 0件で内部データ事情をDoneへ表示してはいけません");

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

const resumedWithoutContext = createHarness();
resumedWithoutContext.session.contextEnabled = false;
resumedWithoutContext.session.stage = "context";
resumedWithoutContext.normalizeLearnSessionResume();
assert.equal(resumedWithoutContext.session.stage, "flash", "文脈推測なしで保存した学習はFlashから再開する必要があります");
assert.equal(resumedWithoutContext.session.contextAvailableTotal, 0, "文脈推測なしのresumeはContext件数を0に保つ必要があります");

const oldMeaningResume = extractFunctionBody(js, "startMeaningPractice");
assert.match(oldMeaningResume, /stage:\s*"check"/, "意味復習はcheckから始める必要があります");
assert.doesNotMatch(oldMeaningResume, /enterContextOrCheck|contextOrder|contextBeforeFlash|contextIdx/, "意味復習にContext状態を持ち込んではいけません");

const oldResume = {
  mode: "meaning",
  stage: "context",
  checkIdx: 2,
  checkOrder: ["a", "b", "c"],
  meaningCorrect: 1,
  contextPicked: "old guess",
  contextCorrect: false,
};
const normalizedMeaningResume = createHarness().normalizeMeaningResume(oldResume);
assert.equal(normalizedMeaningResume.mode, "meaning", "旧Meaning Context resumeのmodeを保持する必要があります");
assert.equal(normalizedMeaningResume.stage, "check", "旧Meaning Context resumeはMeaning Checkへ移行する必要があります");
assert.equal(normalizedMeaningResume.checkIdx, 2, "旧Meaning Context resumeのcheckIdxを保持する必要があります");
assert.equal(JSON.stringify(normalizedMeaningResume.checkOrder), JSON.stringify(["a", "b", "c"]), "旧Meaning Context resumeのcheckOrderを保持する必要があります");
assert.equal(normalizedMeaningResume.meaningCorrect, 1, "旧Meaning Context resumeのmeaningCorrectを保持する必要があります");

const contextRecorder = extractFunctionBody(js, "recordLearnContextResult");
assert.doesNotMatch(contextRecorder, /meaningCorrect|wrongCount|fsrs|nextReviewAt/, "Context記録関数はFSRS・意味成績を変更してはいけません");

console.log("learn state transitions: OK");
