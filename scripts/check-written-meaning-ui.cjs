"use strict";

// 「例文を見て意味を書く」が Cloudflare 版だけに出ること、表記ゆれ一致・Jev 判定の採否を検証する。

const assert = require("node:assert/strict");
const { appJs, readText, extractFunctionBody } = require("./lib/app-source.cjs");

const source = appJs();

// --- 公開先による出し分け ---
const featureSource = [
  source.match(/const CLOUDFLARE_ONLY_FEATURES = \[[^\]]*\];/)[0],
  "let appConfig = {};",
  extractFunctionBody(source, "featureEnabled"),
  "return { featureEnabled, setConfig: (c) => { appConfig = c; } };",
].join("\n");
const feature = new Function(featureSource)();
assert.equal(feature.featureEnabled("writtenMeaning"), false, "config.json が無ければ出さない");
feature.setConfig({ deployTarget: "" });
assert.equal(feature.featureEnabled("writtenMeaning"), false, "GitHub Pages 版では出さない");
feature.setConfig({ deployTarget: "cloudflare" });
assert.equal(feature.featureEnabled("writtenMeaning"), true, "Cloudflare 版では出す");
assert.match(extractFunctionBody(source, "writtenMeaningEntry"), /if \(!featureEnabled\("writtenMeaning"\)/,
  "入口は featureEnabled で閉じる");

// config.json の deployTarget は Cloudflare のデプロイジョブだけが入れる
const workflow = readText(".github/workflows/pages.yml").replace(/\r\n/g, "\n");
const cfStart = workflow.indexOf("\n  deploy-cloudflare:\n");
assert.notEqual(cfStart, -1);
assert.equal((workflow.match(/DEPLOY_TARGET:/g) || []).length, 1, "DEPLOY_TARGET はひとつだけ");
assert.ok(workflow.indexOf("DEPLOY_TARGET: cloudflare") > cfStart, "DEPLOY_TARGET は Cloudflare ジョブの中だけ");
assert.match(readText("scripts/write-config.mjs"), /deployTarget: process\.env\.DEPLOY_TARGET \|\| ""/);
assert.match(readText("wrangler.jsonc"), /"main": "worker\/index\.mjs"/);
assert.match(readText("wrangler.jsonc"), /"run_worker_first": \["\/api\/\*"\]/);

// --- 表記ゆれ一致と Jev 判定の採否 ---
const logic = new Function([
  source.match(/const WRITTEN_AI_AUTO_THRESHOLD = [\d.]+;/)[0],
  source.match(/const WRITTEN_GRADES = \[[^\]]*\];/)[0],
  extractFunctionBody(source, "normalizeWrittenMeaning"),
  extractFunctionBody(source, "writtenLocalMatch"),
  extractFunctionBody(source, "decideWrittenAiGrade"),
  "return { writtenLocalMatch, decideWrittenAiGrade };",
].join("\n"))();
assert.equal(logic.writtenLocalMatch("同意", "同意する、就任する"), true);
assert.equal(logic.writtenLocalMatch(" 就任する。", "同意する、就任する"), true);
assert.equal(logic.writtenLocalMatch("賛成する", "同意する、就任する"), false, "同義語は Jev に任せる");
assert.equal(logic.writtenLocalMatch("", "同意する"), false);
assert.equal(logic.writtenLocalMatch("な", "危険な"), false);
assert.deepEqual(logic.decideWrittenAiGrade({ grade: "correct", confidence: 0.9 }), { auto: true, grade: "correct" });
assert.deepEqual(logic.decideWrittenAiGrade({ grade: "wrong", confidence: 0.5 }), { auto: false, grade: "wrong" });
assert.deepEqual(logic.decideWrittenAiGrade(null), { auto: false, grade: null });
assert.deepEqual(logic.decideWrittenAiGrade({ grade: "easy", confidence: 1 }), { auto: false, grade: null });

// --- 段階式の流れ: 単語だけ → 例文 → 答え、と再出題の位置 ---
const flow = new Function([
  source.match(/const WRITTEN_REASK_GAP = \d+;/)[0],
  extractFunctionBody(source, "writtenNextStep"),
  extractFunctionBody(source, "writtenReaskIndex"),
  "return { writtenNextStep, writtenReaskIndex };",
].join("\n"))();
assert.deepEqual(flow.writtenNextStep("word", false, "correct"), { next: "result", outcome: "learned" });
assert.deepEqual(flow.writtenNextStep("word", false, "partial"), { next: "example" }, "部分正解でも例文のヒントへ");
assert.deepEqual(flow.writtenNextStep("word", false, "wrong"), { next: "example" });
assert.deepEqual(flow.writtenNextStep("example", false, "correct"), { next: "result", outcome: "shaky" });
assert.deepEqual(flow.writtenNextStep("example", false, "wrong"), { next: "answer", outcome: "notLearned" });
assert.deepEqual(flow.writtenNextStep("word", true, "correct"), { next: "result", reaskResult: "correct" });
assert.deepEqual(flow.writtenNextStep("word", true, "wrong"), { next: "answer", reaskResult: "wrong" }, "再出題は例文を挟まない");
assert.equal(flow.writtenReaskIndex("notLearned", 0, 10), 4, "未習得は数問あと");
assert.equal(flow.writtenReaskIndex("notLearned", 8, 10), 10, "末尾を越えない");
assert.equal(flow.writtenReaskIndex("shaky", 2, 10), 10, "あやふやは最後");
assert.equal(flow.writtenReaskIndex("learned", 2, 10), -1, "覚えた語は再出題しない");
assert.match(extractFunctionBody(source, "recordWrittenResult"), /if \(entry\.reask\)[\s\S]*else[\s\S]*writtenQueue\.splice/,
  "再出題の結果では、さらに再出題を積まない");

// 書いて答える演習は途中保存しない（resume の形を変えない）
assert.match(source, /session\.mode === "contextLearn" \|\| session\.mode === "written";\n\s+if \(!isTransientContext\) saveResume\(\);/);

console.log("written meaning UI: OK (Cloudflare 版限定・表記ゆれ一致・Jev 判定の採否・段階式の流れ)");
