"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { ROOT, appCss, appJs, extractFunctionBody } = require("./lib/app-source.cjs");

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function itemSurface(item) {
  return String(item?.phrase || item?.word || "").trim();
}

const dataDir = path.join(ROOT, "data");
const dataIssues = [];
let itemCount = 0;

for (const fileName of fs.readdirSync(dataDir).filter((name) => /^vocab_.*\.json$/.test(name)).sort()) {
  const filePath = path.join(dataDir, fileName);
  const data = JSON.parse(fs.readFileSync(filePath, "utf8"));
  for (const group of ["words", "idioms"]) {
    const items = Array.isArray(data[group]) ? data[group] : [];
    for (const item of items) {
      itemCount += 1;
      const surface = itemSurface(item);
      const example = String(item?.example || "");
      const translation = String(item?.exampleTranslation || "");
      if (!surface) dataIssues.push(`${fileName}: ${group} の出題形がありません`);
      if (!example.trim()) dataIssues.push(`${fileName} / ${surface}: example がありません`);
      if (!translation.trim()) dataIssues.push(`${fileName} / ${surface}: exampleTranslation がありません`);
      if (!surface || !example) continue;

      const exact = new RegExp(`(?<![A-Za-z])${escapeRegExp(surface)}(?![A-Za-z])`, "gi");
      const matchCount = (example.match(exact) || []).length;
      if (matchCount !== 1) {
        dataIssues.push(`${fileName} / ${surface}: 例文中の完全一致が${matchCount}件です\n  例文: ${example}`);
      }
    }
  }
}

assert.equal(dataIssues.length, 0, `例文データ契約違反:\n${dataIssues.join("\n")}`);

const js = appJs();
const css = appCss();
const renderCheckBody = extractFunctionBody(js, "renderCheck");
const feedbackBody = extractFunctionBody(js, "appendCheckFeedback");
const flashExampleBody = extractFunctionBody(js, "flashExampleRow");
const exampleMatchBody = extractFunctionBody(js, "exampleMatch");

// 実行時のマッチャは、上のデータ検査と同じ単語境界で切る必要がある。
// 境界を見ないと "When" の中の "he" を下線にしてしまい、検査は通るのに設問が壊れる。
assert.ok(
  exampleMatchBody.includes("(?<![A-Za-z])") && exampleMatchBody.includes("(?![A-Za-z])"),
  "exampleMatch は単語境界付きで一致判定する必要があります",
);

assert.match(renderCheckBody, /下線部の意味として最も適当なものを選べ/);
assert.match(renderCheckBody, /session\.mode === "meaning"/);
assert.ok(renderCheckBody.includes("exampleMatch(item)"), "renderCheck は例文の一致判定を使う必要があります");
assert.ok(renderCheckBody.includes("buildExampleText(item, example)"), "renderCheck は共通の例文ノードを使う必要があります");
assert.ok(renderCheckBody.includes('class: "askExampleLine"'), "meaning の出題部に例文レイアウトが必要です");
assert.ok(renderCheckBody.includes('class: "askWordLine"'), "不一致時の見出し語フォールバックが必要です");
assert.match(renderCheckBody, /if \(example\) \{[\s\S]*?else \{[\s\S]*?askWordLine/);

assert.match(feedbackBody, /session\.mode === "meaning" && item\.exampleTranslation/);
assert.ok(feedbackBody.includes("例文訳："), "意味復習のフィードバックに例文訳が必要です");

assert.ok(flashExampleBody.includes("exampleMatch(item)"), "flashExampleRow は共通の一致判定を使う必要があります");
assert.ok(flashExampleBody.includes("buildExampleText(item, match)"), "flashExampleRow は共通の例文ノードを使う必要があります");
assert.equal(flashExampleBody.includes('el("em"'), false, "flashExampleRow に旧emハイライトを残してはいけません");

assert.match(css, /--rule-underline:\s*1\.5px solid var\(--ink\)/);
assert.match(css, /\.exUnderline\s*\{[\s\S]*border-bottom:\s*var\(--rule-underline\)/);
assert.ok(!css.includes(".flashEx em"), "旧flashEx emの下線指定を残してはいけません");
assert.match(css, /\.askExampleLine\s*\{/);
// 設問として読ませる英文は本文の Inter（見出し用セリフは使わない）。DESIGN.md タイポグラフィ節。
assert.match(
  css,
  /\.askExample\s*\{[^}]*font-family:\s*var\(--sans\)[^}]*font-size:\s*20px[^}]*line-height:\s*1\.8[^}]*max-inline-size:\s*70ch/,
  "設問英文(.askExample)は本文Inter・20px・行間1.8・行幅70chである必要があります",
);
assert.ok(
  !/\.askExample\s*\{[^}]*var\(--serif\)/.test(css),
  "設問英文(.askExample)に見出し用セリフ体を使ってはいけません",
);

console.log(`meaning example UI contract: OK (${itemCount} vocabulary items)`);
