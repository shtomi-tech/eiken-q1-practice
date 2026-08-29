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
const loadDataBody = extractFunctionBody(js, "loadData");
const loadPooledItemsBody = extractFunctionBody(js, "loadPooledItems");

const coreImageBranch = buildFlashCardBody.indexOf("item.coreImage");
const etymologyBranch = buildFlashCardBody.indexOf("item.etymology");
const wordOriginBranch = buildFlashCardBody.indexOf("flashWordOrigin");
assert.ok(coreImageBranch !== -1, "buildFlashCard は coreImage を判定する必要があります");
assert.equal(etymologyBranch, -1, "buildFlashCard は旧etymology表示を使ってはいけません");
assert.ok(wordOriginBranch !== -1, "buildFlashCard は単語の語源表示を判定する必要があります");
assert.ok(buildFlashCardBody.includes('item.type === "idiom"'), "coreImageは熟語カードでだけ表示する必要があります");

for (const marker of ["coreChain", "coreChainStep", "coreChainTerm", "coreChainGloss"]) {
  assert.ok(flashCoreImageBody.includes(marker), `flashCoreImage に ${marker} が必要です`);
}
assert.ok(flashCoreImageBody.includes('el("ol"'), "核心イメージの連鎖は ol で表現する必要があります");
assert.ok(!flashCoreImageBody.includes("→"), "暗記カードの矢印はCSS疑似要素で表現し、JSテキストに持たせないでください");
for (const marker of ["particlePanel", "particleMap", "particleSense", "core.siblings", "_particleSlot", "rotatingSiblingWindow"]) {
  assert.equal(flashCoreImageBody.includes(marker), false, `共有パネルの${marker}処理を残してはいけません`);
}
assert.equal(js.includes("particleMap"), false, "共有イメージ辞書を実行時に読み込んではいけません");
assert.equal(js.includes("particle_images.json"), false, "共有イメージ辞書を実行時に読み込んではいけません");
assert.equal(js.includes("assignParticleSlots"), false, "共有パネル用のparticle slot処理を残してはいけません");
assert.equal(js.includes("rotatingSiblingWindow"), false, "共有パネル用の仲間例ローテーションを残してはいけません");
assert.match(loadDataBody, /fetch\(current\.vocabUrl,\s*\{\s*cache:\s*"no-store"\s*\}\)/, "通常学習の語彙JSONはキャッシュを使わず取得する必要があります");
assert.match(loadDataBody, /fetch\(current\.questionsUrl,\s*\{\s*cache:\s*"no-store"\s*\}\)/, "通常学習の問題JSONはキャッシュを使わず取得する必要があります");
assert.match(loadPooledItemsBody, /fetch\(DATASETS\[id\]\.vocabUrl,\s*\{\s*cache:\s*"no-store"\s*\}\)/, "意味復習用の語彙JSONはキャッシュを使わず取得する必要があります");

assert.ok(appendCheckFeedbackBody.includes("item.coreImage"), "意味チェックのフィードバックにも coreImage を反映する必要があります");
assert.ok(appendCheckFeedbackBody.includes("chain"), "フィードバックは chain を参照する必要があります");
assert.ok(appendCheckFeedbackBody.includes('join(" → ")'), "フィードバックの連鎖は1行の矢印で表示する必要があります");

for (const selector of [
  ".coreChain",
  ".coreChainStep",
  ".coreChainTerm",
  ".coreChainGloss",
]) {
  assert.ok(css.includes(selector), `CSSに ${selector} の規則が必要です`);
}
for (const selector of [".particlePanel", ".particlePanelTitle", ".particleCore", ".particleSiblings"]) {
  assert.equal(css.includes(selector), false, `削除した共有パネルのCSSを残してはいけません: ${selector}`);
}
assert.match(css, /@media\s*\(max-width:\s*480px\)/, "480px以下の核心イメージ用レスポンシブ規則が必要です");
assert.match(css, /\.coreChainStep\s*\+\s*\.coreChainStep::before/, "連鎖の矢印は隣接ステップの疑似要素で表示する必要があります");

console.log("core image UI contract: OK");
