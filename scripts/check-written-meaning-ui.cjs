"use strict";

// 「単語の意味を書く」とホームのタブが Cloudflare 版だけに出ること、表記ゆれ一致・Jev 判定の採否を検証する。

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
assert.equal(feature.featureEnabled("homeTabs"), true, "ホームのタブも Cloudflare 版では出す");
feature.setConfig({ deployTarget: "" });
assert.equal(feature.featureEnabled("homeTabs"), false, "ホームのタブは GitHub Pages 版では出さない");
assert.match(extractFunctionBody(source, "writtenMeaningCard"), /if \(!featureEnabled\("writtenMeaning"\)\) return null;/,
  "入口は featureEnabled で閉じる");
assert.match(extractFunctionBody(source, "homeTabsEnabled"), /return featureEnabled\("homeTabs"\);/);
assert.match(extractFunctionBody(source, "arrangeHomeTabs"), /if \(!homeTabsEnabled\(\) \|\| !marks\.length\) return;/,
  "タブが無い公開先ではホームを並べ替えない");
// 書く演習は意味だけ復習カードの中ではなく、ホームの独立カードとして置く
assert.doesNotMatch(extractFunctionBody(source, "meaningMission"), /writtenMeaning/);
assert.match(extractFunctionBody(source, "renderHomeContent"), /homeTabStart\(home, "write"\);\s+const writtenCard = grade \? writtenMeaningCard\(/);

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

// --- 出題の選び方: 苦手を約6割、残りはまだ書いていない語。足りない枠は埋め合う ---
const picker = new Function([
  source.match(/const WRITTEN_WEAK_SHARE = [\d.]+;/)[0],
  extractFunctionBody(source, "pickWrittenItems"),
  extractFunctionBody(source, "pullMeaningReviewForward"),
  "return { pickWrittenItems, pullMeaningReviewForward };",
].join("\n"))();
const same = (list) => list.slice();
const entries = (outcome, n, prefix = outcome || "new") =>
  Array.from({ length: n }, (_, i) => ({ item: `${prefix}${i}`, outcome, at: `2026-10-0${i + 1}` }));
const countBy = (picked, prefix) => picked.filter((name) => name.startsWith(prefix)).length;
let picked = picker.pickWrittenItems([...entries("learned", 5), ...entries(null, 10), ...entries("shaky", 4), ...entries("notLearned", 4)], 10, same);
assert.equal(picked.length, 10);
assert.equal(countBy(picked, "notLearned"), 4, "未習得を先に取る");
assert.equal(countBy(picked, "shaky"), 2, "苦手枠は6語まで");
assert.equal(countBy(picked, "new"), 4, "残りはまだ書いていない語");
assert.equal(countBy(picked, "learned"), 0);
picked = picker.pickWrittenItems([...entries(null, 2), ...entries("shaky", 9)], 10, same);
assert.equal(countBy(picked, "new"), 2);
assert.equal(countBy(picked, "shaky"), 8, "未出題が足りなければ苦手で埋める");
picked = picker.pickWrittenItems([...entries("learned", 5), ...entries(null, 3), ...entries("notLearned", 1)], 10, same);
assert.equal(picked.length, 9, "対象が足りなければあるだけ出す");
picked = picker.pickWrittenItems([...entries("learned", 5), ...entries(null, 3)], 5, same);
assert.deepEqual(picked, ["new0", "new1", "new2", "learned0", "learned1"], "覚えた語は前に書いた順に足す");
assert.equal(picker.pickWrittenItems([...entries("shaky", 3)], 5, same).length, 3);

// 答えを見た語は、意味だけ復習の期限を今へ早める（評価は付けない）
const now = new Date("2026-10-13T00:00:00Z");
const scheduled = { items: { k: { lastAnsweredAt: "2026-10-01T00:00:00Z", nextReviewAt: "2026-11-01T00:00:00Z", fsrs: { due: "2026-11-01T00:00:00Z", stability: 20, reps: 3 } } } };
assert.equal(picker.pullMeaningReviewForward(scheduled, "k", now), true);
assert.equal(scheduled.items.k.nextReviewAt, now.toISOString());
assert.equal(scheduled.items.k.fsrs.due, now.toISOString());
assert.equal(scheduled.items.k.fsrs.stability, 20, "間隔の記憶は変えない");
assert.equal(picker.pullMeaningReviewForward({ items: {} }, "k", now), false, "まだ復習していない語は触らない");
assert.equal(picker.pullMeaningReviewForward({ items: { k: { lastAnsweredAt: "x", nextReviewAt: "2026-10-01T00:00:00Z" } } }, "k", now), false, "期限切れはそのまま");
assert.match(extractFunctionBody(source, "recordWrittenResult"), /if \(step\.outcome === "notLearned"\) reviewPulled = pullMeaningReviewForward\(/);
assert.match(extractFunctionBody(source, "startWrittenMeaning"), /pickWrittenItems\(writtenEntries\(pool\), size\)/);

// 書いて答える演習は途中保存しない（resume の形を変えない）
assert.match(source, /session\.mode === "contextLearn" \|\| session\.mode === "written";\n\s+if \(!isTransientContext\) saveResume\(\);/);

console.log("written meaning UI: OK (Cloudflare 版限定・表記ゆれ一致・Jev 判定の採否・段階式の流れ・出題の選び方)");
