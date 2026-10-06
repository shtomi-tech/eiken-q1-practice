"use strict";

// 意味だけ復習の1日上限（120問）に達した後、本人が選んだときだけ続けて解けること（Cloudflare 版のみ）を検証する。

const assert = require("node:assert/strict");
const { appJs, extractFunctionBody } = require("./lib/app-source.cjs");

const source = appJs();

// --- 公開先による出し分け ---
const featureSource = [
  source.match(/const CLOUDFLARE_ONLY_FEATURES = \[[^\]]*\];/)[0],
  "let appConfig = {};",
  extractFunctionBody(source, "featureEnabled"),
  "return { featureEnabled, setConfig: (c) => { appConfig = c; } };",
].join("\n");
const feature = new Function(featureSource)();
assert.equal(feature.featureEnabled("reviewBeyondCap"), false, "config.json が無ければ出さない");
feature.setConfig({ deployTarget: "cloudflare" });
assert.equal(feature.featureEnabled("reviewBeyondCap"), true, "Cloudflare 版では出す");
assert.match(extractFunctionBody(source, "reviewBeyondCapEnabled"), /return featureEnabled\("reviewBeyondCap"\);/);

// --- 上限は既定のまま ---
assert.match(source, /const MEANING_DAILY_LIMIT = 120;/, "1日の上限は120問のまま");

// --- 入口: ホームの間隔復習カードと完了画面 ---
const mission = extractFunctionBody(source, "meaningMission");
assert.match(mission, /todayRemaining === 0 && reviewBeyondCapEnabled\(\)/, "上限到達かつ有効なときだけ追加の入口を出す");
assert.match(mission, /startMeaningPractice\(true, null, true\)/, "ホームから上限後の追加分を始められる");
assert.match(mission, /buttonLabel = "今日の上限に達しました";/, "機能が無効な公開先では従来どおり無効のボタン");
const done = extractFunctionBody(source, "renderDone");
assert.match(done, /reviewBeyondCapEnabled\(\)[\s\S]*startMeaningPractice\(true, null, true\)/, "完了画面からも続けられる");

// --- 追加分は1日の上限で打ち切らないが、記録は通常どおり ---
const start = extractFunctionBody(source, "startMeaningPractice");
assert.match(start, /beyondCap = Boolean\(beyondCap\) && dueOnly && reviewBeyondCapEnabled\(\);/, "無効な公開先では追加分にしない");
assert.match(start, /meaningBeyondCap: Boolean\(grade\) && beyondCap,/);
assert.match(start, /meaningDailyRemaining: grade && dueOnly && !beyondCap \? limit : null,/);
assert.match(extractFunctionBody(source, "meaningPracticeQueue"), /dueOnly && !beyondCap/, "追加分は1回分の上限だけを守る");
assert.match(source, /if \(session\.dueOnly && !session\.meaningBeyondCap\) \{\s+const dailyRemaining/, "追加分は回答ごとの打ち切りをしない");
assert.match(source, /if \(session\?\.dueOnly\) recordSpacedReviewDailyAnswer\(progress, answeredAt\);/, "追加分も今日の回答数に数える");

// --- 途中保存と再開 ---
assert.match(extractFunctionBody(source, "saveResume"), /meaningBeyondCap: Boolean\(session\.meaningBeyondCap\),/);
const restore = extractFunctionBody(source, "restoreSession");
assert.match(restore, /saved\.dueOnly && !saved\.meaningBeyondCap && saved\.stage === "check"/, "追加分の再開では上限で切り詰めない");
assert.match(restore, /startMeaningPractice\(true, null, Boolean\(restoredSnapshot\.meaningBeyondCap\)\)/);

console.log("review beyond daily cap: OK");
