"use strict";

const assert = require("node:assert/strict");
const { appJs, extractFunctionBody } = require("./lib/app-source.cjs");

const js = appJs();
const startLearn = extractFunctionBody(js, "startLearn");
const setLearnItem = extractFunctionBody(js, "setLearnItem");
const advanceLearnFromFlash = extractFunctionBody(js, "advanceLearnFromFlash");
const renderContext = extractFunctionBody(js, "renderContext");
const renderFlash = extractFunctionBody(js, "renderFlash");
const renderCheck = extractFunctionBody(js, "renderCheck");
const renderDone = extractFunctionBody(js, "renderDone");
const recordContext = extractFunctionBody(js, "recordLearnContextResult");
const resumeDescription = extractFunctionBody(js, "resumeDescription");

assert.match(startLearn, /items:\s*orderedItems/, "通常学習はsession.itemsを学習順として保存する必要があります");
assert.match(startLearn, /checkOrder:\s*shuffle\(orderedItems\)/, "Meaning Checkだけは別順にshuffleする必要があります");
assert.match(startLearn, /session\.stage = session\.learnPhase/, "通常学習の開始phaseをContext有無から決める必要があります");

assert.match(setLearnItem, /session\.learnIdx = index/, "Context/Flash共通の現在語indexが必要です");
assert.match(setLearnItem, /contextItemFor\(item\)/, "次の語にContextがあるか判定する必要があります");
assert.match(advanceLearnFromFlash, /setLearnItem\(session\.learnIdx \+ 1\)/, "Flash後は次語のContextまたはFlashへ進む必要があります");
assert.match(advanceLearnFromFlash, /session\.stage = "check"/, "最後のFlash後はMeaning Checkへ進む必要があります");

assert.match(renderContext, /session\.items\[session\.learnIdx\]/, "通常学習のContextは現在のsession.itemsを参照する必要があります");
assert.match(renderContext, /recordLearnContextResult\(sourceItem, meaning, correctMeaning\)/, "ContextのpickedMeaning/correctMeaningを保存する必要があります");
assert.match(renderContext, /この単語を覚える →/, "Context回答後は同じ語を覚える導線が必要です");
assert.doesNotMatch(renderContext, /meaningCorrect\s*[+\-]=|meaningCorrect\s*\+\+/, "Contextの正誤をMeaning Checkの成績へ混ぜてはいけません");

assert.match(recordContext, /pickedMeaning/, "Context結果にpickedMeaningを保存する必要があります");
assert.match(recordContext, /correctMeaning/, "Context結果にcorrectMeaningを保存する必要があります");
assert.match(recordContext, /correct:/, "Context結果にcorrectを保存する必要があります");
assert.match(renderFlash, /session\.mode === "learn"/, "Flashは通常学習のlearnIdxを扱う必要があります");
assert.match(renderFlash, /advanceLearnFromFlash\(\)/, "Flashの次へはContext有無に応じて遷移する必要があります");
assert.match(renderFlash, /session\.mode === "contextLearn"/, "独立した試用Context→Flashモードを壊してはいけません");

assert.match(renderCheck, /session\.checkOrder\[session\.checkIdx\]/, "Meaning CheckはcheckOrderを使う必要があります");
assert.match(renderCheck, /session\.meaningCorrect \+= 1/, "Meaning Checkの正答は既存の成績へ記録する必要があります");
assert.match(renderDone, /contextCorrectCount/, "DoneはContextの結果を独立表示する必要があります");
assert.match(renderDone, /本番形式：/, "DoneはPracticeの結果を表示する必要があります");

assert.match(js, /function startContextPractice\(\)/, "独立Context Practiceを維持する必要があります");
assert.match(js, /const contextPromise = current\.contextUrl/, "contextUrlなしdatasetを読み込めるfallbackを維持する必要があります");
assert.match(js, /function normalizeLearnSessionResume\(\)/, "旧resumeを新しいlearnIdxへnormalizeする必要があります");
assert.match(js, /contextResults: session\.contextResults/, "Context結果を通常学習resumeへ保存する必要があります");
assert.match(resumeDescription, /resume\.learnIdx/, "resume表示はlearnIdxを使う必要があります");
assert.match(resumeDescription, /STEP 1 文脈から発見/, "Context中のresume表示が必要です");

console.log("integrated context learning flow contract: OK");
