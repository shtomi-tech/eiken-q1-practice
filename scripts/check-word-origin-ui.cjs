const assert = require("node:assert/strict");
const fs = require("node:fs");

const js = fs.readFileSync("static/mode-q1.js", "utf8");
const css = fs.readFileSync("static/styles.css", "utf8");
const indexHtml = fs.readFileSync("index.html", "utf8");

function cssRule(source, selector) {
  const escapedSelector = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const matched = source.match(new RegExp(`${escapedSelector}\\s*\\{([^}]*)\\}`));
  assert.ok(matched, `CSSに ${selector} の規則が必要です`);
  return matched[1];
}

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
const flashWordOriginBody = extractFunctionBody(js, "flashWordOrigin");
const bootBody = extractFunctionBody(js, "boot");
const loadWordOriginDataBody = extractFunctionBody(js, "loadWordOriginData");
const appendCheckFeedbackBody = extractFunctionBody(js, "appendCheckFeedback");

const meaningIndex = buildFlashCardBody.indexOf('flashRow("意味"');
const originIndex = buildFlashCardBody.indexOf("flashWordOrigin");
const exampleIndex = buildFlashCardBody.indexOf("flashExampleRow");
assert.ok(meaningIndex !== -1 && originIndex !== -1 && exampleIndex !== -1, "カードの意味・語源・例文の描画経路が必要です");
assert.ok(meaningIndex < originIndex && originIndex < exampleIndex, "語源は意味の直下かつ例文の前に表示する必要があります");
assert.ok(buildFlashCardBody.includes('item.type === "word"'), "語源表示は単語だけを対象にする必要があります");
assert.ok(buildFlashCardBody.includes('item.type === "idiom"'), "熟語の核心イメージ分岐を維持する必要があります");
assert.equal(buildFlashCardBody.includes("item.etymology"), false, "単語カードは旧etymology分岐を使ってはいけません");
assert.equal(js.includes("flashEtym"), false, "旧flashEtymクラスを残してはいけません");
assert.equal(css.includes(".flashEtym"), false, "旧flashEtymルールを残してはいけません");

for (const marker of ["wordOriginFor", "originChain", "coreChain", 'el("ol"', "originChip", "originDerivation", "originChipKind", "originChipForm", "originChipGloss"]) {
  assert.ok(flashWordOriginBody.includes(marker), `flashWordOrigin に ${marker} が必要です`);
}
assert.ok(flashWordOriginBody.includes("type === \"B\""), "B型の語源を分解なしで表示できる必要があります");
// 単語カードは情報量を抑えるため、語根パネル（語根名・注記・仲間語リスト）を出さない。
assert.equal(flashWordOriginBody.includes("wordOriginPanel"), false, "単語カードに語根パネルを復活させてはいけません");
assert.equal(js.includes("wordOriginSiblingItems"), false, "語根パネル専用の逆引き関数を残してはいけません");
assert.equal(js.includes("wordOriginRootIndex"), false, "語根パネル専用のroot索引を残してはいけません");
assert.equal(css.includes(".wordOriginPanel"), false, "語根パネルのCSSを残してはいけません");
assert.equal(flashWordOriginBody.includes("Math.random"), false, "語源表示に乱数を使ってはいけません");

assert.ok(bootBody.includes("loadWordOriginData"), "bootは語源辞書を初期化する必要があります");
assert.ok(loadWordOriginDataBody.includes("word_origins.json"), "word_origins.jsonを読み込む必要があります");
assert.ok(loadWordOriginDataBody.includes("catch"), "語源辞書が未配信でも起動を継続する必要があります");
assert.equal(appendCheckFeedbackBody.includes("item.etymology"), false, "フィードバックも旧etymology分岐を使ってはいけません");

const isolatedFunctions = [
  "surfaceOf",
  "itemKeyOf",
  "vocabularyAudioPath",
  "buildVocabAudioButton",
  "meaningDistractors",
  "practiceChoiceMeanings",
  "recordMeaningResult",
];
for (const name of isolatedFunctions) {
  const body = extractFunctionBody(js, name);
  assert.equal(body.includes("wordOrigin"), false, `${name} に語源表示データを流し込んではいけません`);
}

for (const selector of [
  ".originChips",
  ".originChip",
  ".originChipKind",
  ".originChipForm",
  ".originChipGloss",
  ".originDerivation",
]) {
  cssRule(css, selector);
}
assert.match(cssRule(css, ".originChip"), /flex-wrap:\s*wrap/, "語源チップは折り返せる必要があります");
assert.match(cssRule(css, ".originChipKind"), /width:\s*100%/, "種別ラベルは1行を占める必要があります");
assert.doesNotMatch(cssRule(css, ".originDerivation"), /border-top\s*:/, "語源の導出文を独立した罫線で分けてはいけません");
assert.doesNotMatch(cssRule(css, ".originDerivation"), /padding-top\s*:/, "語源の導出文に独立ブロック用の上余白を置いてはいけません");
assert.match(css, /@media\s*\(max-width:\s*480px\)/, "モバイル用の語源レイアウト規則が必要です");
assert.match(indexHtml, /static\/styles\.css\?v=[^"'\s]+/, "styles.cssのキャッシュバスターが必要です");
assert.match(indexHtml, /static\/mode-q1\.js\?v=[^"'\s]+/, "mode-q1.jsのキャッシュバスターが必要です");

console.log("word origin UI contract: OK");
