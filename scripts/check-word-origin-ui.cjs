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
const wordOriginSiblingsBody = extractFunctionBody(js, "wordOriginSiblingItems");
const rotatingSiblingWindowBody = extractFunctionBody(js, "rotatingSiblingWindow");
const bootBody = extractFunctionBody(js, "boot");
const loadWordOriginDataBody = extractFunctionBody(js, "loadWordOriginData");
const loadDataBody = extractFunctionBody(js, "loadData");
const loadPooledItemsBody = extractFunctionBody(js, "loadPooledItems");
const assignWordOriginSlotsBody = extractFunctionBody(js, "assignWordOriginSlots");
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

for (const marker of ["wordOriginFor", "originChip", "originDerivation", "originChipKind", "originChipForm", "originChipGloss"]) {
  assert.ok(flashWordOriginBody.includes(marker), `flashWordOrigin に ${marker} が必要です`);
}
assert.ok(flashWordOriginBody.includes("wordOriginSiblingItems"), "語根の仲間語パネルは逆引き関数を使う必要があります");
assert.ok(flashWordOriginBody.includes("particlePanel"), "仲間語パネルは既存particlePanelの構造を流用する必要があります");
assert.ok(flashWordOriginBody.includes("wordOriginPanel"), "語根パネルを識別できるクラスが必要です");
assert.ok(flashWordOriginBody.includes("type === \"B\""), "B型の語源を分解なしで表示できる必要があります");
assert.ok(wordOriginSiblingsBody.includes("wordOriginMap"), "仲間語候補は語源辞書を参照する必要があります");
assert.equal(wordOriginSiblingsBody.includes("pooledData"), false, "仲間語候補は級別のpooledDataに依存してはいけません");
assert.ok(wordOriginSiblingsBody.includes("wordOriginRootIndex"), "仲間語の逆引きはroot索引を使う必要があります");
assert.ok(wordOriginSiblingsBody.includes("sameStem"), "仲間語の語幹変異形は後順位にする必要があります");
assert.ok(flashWordOriginBody.includes("sibling.gloss"), "仲間語パネルは語源辞書の短いglossを表示する必要があります");
assert.match(rotatingSiblingWindowBody, /siblings\[\(slot \+ k\) % siblings\.length\]/, "仲間語のローテーションは決定的なslotで行う必要があります");
assert.equal(flashWordOriginBody.includes("Math.random"), false, "仲間語の表示に乱数を使ってはいけません");

assert.ok(bootBody.includes("loadWordOriginData"), "bootは語源辞書を初期化する必要があります");
assert.ok(loadWordOriginDataBody.includes("word_roots.json"), "word_roots.jsonを読み込む必要があります");
assert.ok(loadWordOriginDataBody.includes("word_origins.json"), "word_origins.jsonを読み込む必要があります");
assert.ok(loadWordOriginDataBody.includes("catch"), "語源辞書が未配信でも起動を継続する必要があります");
assert.ok(assignWordOriginSlotsBody.includes("_wordOriginSlot"), "単語へ実行時専用の語源slotを付ける必要があります");
assert.ok(loadDataBody.includes("assignWordOriginSlots"), "通常学習の語彙へ語源slotを付ける必要があります");
assert.ok(loadPooledItemsBody.includes("assignWordOriginSlots"), "意味復習用の語彙へ語源slotを付ける必要があります");
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
  ".wordOriginPanel",
  ".wordOriginPanel .particleSiblings strong",
]) {
  cssRule(css, selector);
}
assert.match(cssRule(css, ".originChip"), /flex-wrap:\s*wrap/, "語源チップは折り返せる必要があります");
assert.match(cssRule(css, ".originChipKind"), /width:\s*100%/, "種別ラベルは1行を占める必要があります");
assert.match(
  cssRule(css, ".wordOriginPanel .particleSiblings strong"),
  /text-transform:\s*none/,
  "単語の仲間語は見出し語と同じ小文字表記にする必要があります",
);
assert.match(css, /@media\s*\(max-width:\s*480px\)/, "モバイル用の語源レイアウト規則が必要です");
assert.match(indexHtml, /static\/styles\.css\?v=[^"'\s]+/, "styles.cssのキャッシュバスターが必要です");
assert.match(indexHtml, /static\/mode-q1\.js\?v=[^"'\s]+/, "mode-q1.jsのキャッシュバスターが必要です");

console.log("word origin UI contract: OK");
