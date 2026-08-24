const assert = require("node:assert/strict");
const fs = require("node:fs");

const js = fs.readFileSync("static/mode-q1.js", "utf8");
const css = fs.readFileSync("static/styles.css", "utf8");

function extractFunctionBody(source, name) {
  const start = source.indexOf(`function ${name}(`);
  assert.ok(start !== -1, `function ${name}( が見つからない`);
  const braceStart = source.indexOf("{", start);
  assert.ok(braceStart !== -1, `${name} の開始 { が見つからない`);
  let depth = 0;
  for (let i = braceStart; i < source.length; i += 1) {
    if (source[i] === "{") depth += 1;
    else if (source[i] === "}") {
      depth -= 1;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error(`${name} の閉じ } が見つからない`);
}

const buildFlashCardBody = extractFunctionBody(js, "buildFlashCard");
const flashCoreImageBody = extractFunctionBody(js, "flashCoreImage");
const appendCheckFeedbackBody = extractFunctionBody(js, "appendCheckFeedback");
const bootBody = extractFunctionBody(js, "boot");

const coreImageBranch = buildFlashCardBody.indexOf("item.coreImage");
const etymologyBranch = buildFlashCardBody.indexOf("item.etymology");
assert.ok(coreImageBranch !== -1, "buildFlashCard は coreImage を判定する必要があります");
assert.ok(etymologyBranch !== -1, "buildFlashCard は単語の etymology 表示を維持する必要があります");
assert.ok(coreImageBranch < etymologyBranch, "coreImage は etymology より先に評価する必要があります");

for (const marker of ["coreChain", "coreChainStep", "coreChainTerm", "coreChainGloss"]) {
  assert.ok(flashCoreImageBody.includes(marker), `flashCoreImage に ${marker} が必要です`);
}
assert.ok(flashCoreImageBody.includes('el("ol"'), "核心イメージの連鎖は ol で表現する必要があります");
assert.ok(flashCoreImageBody.includes('el("details"'), "不変化詞パネルは details で表現する必要があります");
assert.ok(flashCoreImageBody.includes("particleMap"), "不変化詞パネルは共有辞書を参照する必要があります");
assert.ok(!flashCoreImageBody.includes("→"), "暗記カードの矢印はCSS疑似要素で表現し、JSテキストに持たせないでください");

assert.ok(appendCheckFeedbackBody.includes("item.coreImage"), "意味チェックのフィードバックにも coreImage を反映する必要があります");
assert.ok(appendCheckFeedbackBody.includes("chain"), "フィードバックは chain を参照する必要があります");
assert.ok(appendCheckFeedbackBody.includes('join(" → ")'), "フィードバックの連鎖は1行の矢印で表示する必要があります");

assert.ok(bootBody.includes("particleMap"), "boot は particleMap を初期化する必要があります");
assert.ok(bootBody.includes('data/particle_images.json'), "boot は particle_images.json を1回読み込む必要があります");
assert.ok(bootBody.includes("catch"), "共有辞書の読み込み失敗を握りつぶして起動を継続する必要があります");

for (const selector of [
  ".coreChain",
  ".coreChainStep",
  ".coreChainTerm",
  ".coreChainGloss",
  ".particlePanel",
  ".particleSiblings",
]) {
  assert.ok(css.includes(selector), `CSSに ${selector} の規則が必要です`);
}
assert.match(css, /@media\s*\(max-width:\s*480px\)/, "480px以下の核心イメージ用レスポンシブ規則が必要です");
assert.match(css, /\.coreChainStep\s*\+\s*\.coreChainStep::before/, "連鎖の矢印は隣接ステップの疑似要素で表示する必要があります");

console.log("core image UI contract: OK");
