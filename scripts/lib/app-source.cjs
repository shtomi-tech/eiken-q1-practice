"use strict";

// check-*.cjs 共通のソース読み込みとテキスト抽出。
// 各チェックが個別に readFileSync していた分をここへ集約する。
// mode-q1.js を分割した場合も、appJs() の中だけを直せば全チェックが追従する。

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..", "..");

const cache = new Map();
function readText(relPath) {
  if (!cache.has(relPath)) cache.set(relPath, fs.readFileSync(path.join(ROOT, relPath), "utf8"));
  return cache.get(relPath);
}

function readJson(relPath) {
  return JSON.parse(readText(relPath));
}

// アプリ本体のJS。分割時はここで結合して返す（呼び出し側は変更不要）。
const APP_JS_FILES = ["static/mode-q1.js"];
function appJs() {
  return APP_JS_FILES.map(readText).join("\n");
}

function appCss() {
  return readText("static/styles.css");
}

// IIFE の公開部を差し替えて内部関数をテストへ露出させる。
function appJsWithTestExports(exportsExpr) {
  const source = appJs();
  const marker = "return { mount, handleKey };";
  assert.ok(source.includes(marker), `${marker} が見つからない`);
  return source.replace(marker, `return { mount, handleKey, __test: ${exportsExpr} };`);
}

// `function name(` から対応する閉じ } までを、次の関数名に依存せず抜き出す。
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

module.exports = { ROOT, readText, readJson, appJs, appCss, appJsWithTestExports, extractFunctionBody };
