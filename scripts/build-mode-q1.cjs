"use strict";

// static/src/*.js を連結して static/mode-q1.js を生成する。
//
// static/mode-q1.js は生成物。直接編集せず static/src/ 側を直して
//   npm run build
// を実行すること。--check を付けると生成物が最新かどうかだけを検証する（npm test で使用）。
//
// src の各ファイルは単体では完結しない断片（全体で1つのIIFE）。
// 連結順は PARTS の並び順で固定する。

const assert = require("node:assert/strict");
const { execFileSync } = require("node:child_process");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const SRC_DIR = path.join(ROOT, "static", "src");
const OUT = path.join(ROOT, "static", "mode-q1.js");

// 連結順。ファイル名の数値接頭辞と一致させる。
const PARTS = [
  "00-prelude.js",
  "10-config.js",
  "20-storage.js",
  "30-unit-progress.js",
  "40-cloud.js",
  "50-vocab-pool.js",
  "60-helpers.js",
  "70-data.js",
  "80-home.js",
  "90-learn-flow.js",
  "99-boot.js",
];

function build() {
  const found = fs.readdirSync(SRC_DIR).filter((f) => f.endsWith(".js")).sort();
  assert.deepEqual(found, [...PARTS].sort(), "static/src の構成と PARTS が一致していません");
  return PARTS.map((f) => fs.readFileSync(path.join(SRC_DIR, f), "utf8")).join("");
}

const built = build();
const checkOnly = process.argv.includes("--check");

if (checkOnly) {
  const current = fs.existsSync(OUT) ? fs.readFileSync(OUT, "utf8") : "";
  // 全文比較のダンプは巨大で読めないので、ハッシュだけを突き合わせる。
  const digest = (text) => crypto.createHash("sha256").update(text, "utf8").digest("hex").slice(0, 12);
  assert.equal(
    digest(current),
    digest(built),
    `static/mode-q1.js が static/src と一致しません（生成物=${digest(current)} / src=${digest(built)}）。\`npm run build\` を実行してください。`
  );
  console.log("mode-q1.js build freshness: OK");
} else {
  fs.writeFileSync(OUT, built);
  execFileSync(process.execPath, ["--check", OUT], { stdio: "inherit" });
  const lines = built.split(/\r?\n/).length;
  console.log(`built static/mode-q1.js from ${PARTS.length} parts (${lines} lines)`);
}
