"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { ROOT } = require("./lib/context-pipeline.cjs");

function duplicateKeys(text, file) {
  let index = 0;
  const duplicates = [];
  const skip = () => { while (/\s/.test(text[index] || "")) index += 1; };
  const parseString = () => {
    const start = index;
    index += 1;
    while (index < text.length) {
      if (text[index] === "\\") index += 2;
      else if (text[index] === '"') { index += 1; break; }
      else index += 1;
    }
    return JSON.parse(text.slice(start, index));
  };
  const parseValue = (trail) => {
    skip();
    if (text[index] === "{") return parseObject(trail);
    if (text[index] === "[") return parseArray(trail);
    if (text[index] === '"') return parseString();
    const match = text.slice(index).match(/^(?:true|false|null|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)/);
    assert.ok(match, `${file}: invalid JSON near offset ${index}`);
    index += match[0].length;
    return null;
  };
  const parseObject = (trail) => {
    index += 1;
    skip();
    const keys = new Set();
    while (text[index] !== "}") {
      skip();
      assert.equal(text[index], '"', `${file}: expected object key near offset ${index}`);
      const key = parseString();
      if (keys.has(key)) duplicates.push(`${trail}.${key}`);
      keys.add(key);
      skip();
      assert.equal(text[index], ":", `${file}: expected colon near offset ${index}`);
      index += 1;
      parseValue(`${trail}.${key}`);
      skip();
      if (text[index] === ",") { index += 1; continue; }
      assert.equal(text[index], "}", `${file}: expected object end near offset ${index}`);
    }
    index += 1;
  };
  const parseArray = (trail) => {
    index += 1;
    skip();
    let itemIndex = 0;
    while (text[index] !== "]") {
      parseValue(`${trail}[${itemIndex}]`);
      itemIndex += 1;
      skip();
      if (text[index] === ",") { index += 1; continue; }
      assert.equal(text[index], "]", `${file}: expected array end near offset ${index}`);
    }
    index += 1;
  };
  parseValue("$");
  skip();
  assert.equal(index, text.length, `${file}: trailing JSON content`);
  return duplicates;
}

const directory = path.join(ROOT, "data", "context-pipeline-metrics");
const files = fs.readdirSync(directory).filter((file) => file.endsWith(".json")).sort();
for (const file of files) {
  const duplicates = duplicateKeys(fs.readFileSync(path.join(directory, file), "utf8"), file);
  assert.deepEqual(duplicates, [], `${file}: duplicate JSON keys: ${duplicates.join(", ")}`);
}
console.log(`context pipeline metrics duplicate-key check: OK (${files.length} files)`);

module.exports = { duplicateKeys };
