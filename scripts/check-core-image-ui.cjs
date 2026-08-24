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
const rotatingSiblingWindowBody = extractFunctionBody(js, "rotatingSiblingWindow");
const appendCheckFeedbackBody = extractFunctionBody(js, "appendCheckFeedback");
const bootBody = extractFunctionBody(js, "boot");
const loadDataBody = extractFunctionBody(js, "loadData");
const loadPooledItemsBody = extractFunctionBody(js, "loadPooledItems");
const assignParticleSlotsBody = extractFunctionBody(js, "assignParticleSlots");

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
assert.ok(!flashCoreImageBody.includes('el("details"'), "不変化詞パネルは開閉させず、常に表示する必要があります");
assert.ok(flashCoreImageBody.includes("particlePanelTitle"), "不変化詞パネルには見出しが必要です");
assert.ok(flashCoreImageBody.includes("particleMap"), "不変化詞パネルは共有辞書を参照する必要があります");
assert.ok(flashCoreImageBody.includes("particleSense"), "不変化詞パネルはparticleSenseを参照する必要があります");
assert.ok(flashCoreImageBody.includes("core.siblings"), "coreImage.siblingsの例外上書きを参照する必要があります");
assert.ok(flashCoreImageBody.includes("_particleSlot"), "仲間例の決定的な表示位置を参照する必要があります");
assert.ok(flashCoreImageBody.includes("rotatingSiblingWindow"), "仲間例のローテーションは共通関数を使う必要があります");
assert.match(
  rotatingSiblingWindowBody,
  /siblings\[\(slot \+ k\) % siblings\.length\]/,
  "仲間例はslotから1つずつ進む決定的オフセットで選ぶ必要があります",
);
assert.equal(rotatingSiblingWindowBody.includes("slot * 3"), false, "仲間例の選択で3刻みのオフセットを使ってはいけません");
assert.equal(flashCoreImageBody.includes("Math.random"), false, "仲間例の表示に乱数を使ってはいけません");
const overrideIdx = flashCoreImageBody.indexOf("core.siblings");
const senseIdx = flashCoreImageBody.indexOf("particleSense");
const fallbackIdx = flashCoreImageBody.indexOf("particle.siblings");
assert.ok(overrideIdx < senseIdx && senseIdx < fallbackIdx, "仲間例の解決順は上書き→sense→既定である必要があります");
assert.ok(flashCoreImageBody.includes("particleSenseLabel"), "用法名を見出しへ渡す必要があります");
assert.ok(flashCoreImageBody.includes("(particle || overrideSiblings)"), "辞書にない不変化詞でもcoreImage.siblingsを表示できる必要があります");
assert.ok(!flashCoreImageBody.includes("→"), "暗記カードの矢印はCSS疑似要素で表現し、JSテキストに持たせないでください");
assert.ok(assignParticleSlotsBody.includes("_particleSlot"), "熟語へ実行時専用のparticle slotを付ける必要があります");
assert.ok(loadDataBody.includes("assignParticleSlots(all)"), "loadDataは熟語へparticle slotを付ける必要があります");
assert.match(loadDataBody, /fetch\(current\.vocabUrl,\s*\{\s*cache:\s*"no-store"\s*\}\)/, "通常学習の語彙JSONはキャッシュを使わず取得する必要があります");
assert.match(loadDataBody, /fetch\(current\.questionsUrl,\s*\{\s*cache:\s*"no-store"\s*\}\)/, "通常学習の問題JSONはキャッシュを使わず取得する必要があります");
assert.match(loadPooledItemsBody, /fetch\(DATASETS\[id\]\.vocabUrl,\s*\{\s*cache:\s*"no-store"\s*\}\)/, "意味復習用の語彙JSONはキャッシュを使わず取得する必要があります");

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
  ".particlePanelTitle",
  ".particleSiblings",
]) {
  assert.ok(css.includes(selector), `CSSに ${selector} の規則が必要です`);
}
assert.match(css, /@media\s*\(max-width:\s*480px\)/, "480px以下の核心イメージ用レスポンシブ規則が必要です");
assert.match(css, /\.coreChainStep\s*\+\s*\.coreChainStep::before/, "連鎖の矢印は隣接ステップの疑似要素で表示する必要があります");

console.log("core image UI contract: OK");
