"use strict";

// npm test の本体。CHECKS を上から順に実行し、最初に失敗したところで止めて同じ終了コードを返す。
// チェックを追加するときはこの配列に足す（package.json の test は変更不要）。

const { spawnSync } = require("node:child_process");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");

// 各要素は node に渡す引数列。
const CHECKS = [
  ["scripts/build-mode-q1.cjs", "--check"],
  ["scripts/rebuild-word-origin-dictionaries.cjs", "--check"],
  ["scripts/check-word-origin-research.cjs"],
  ["--check", "static/app.js"],
  ["--check", "static/mode-q1.js"],
  ["--check", "scripts/measure-flashcard.js"],
  ["scripts/check-core-image-data.cjs"],
  ["scripts/check-core-image-ui.cjs"],
  ["scripts/check-pre1-core-image-compat.cjs"],
  ["scripts/check-response-time-srs.cjs"],
  ["scripts/check-fsrs-vendor.cjs"],
  ["scripts/check-fsrs-schedule.cjs"],
  ["scripts/check-context-discovery.cjs"],
  ["scripts/check-student-storage-scope.cjs"],
  ["scripts/check-cloud-progress-namespace.cjs"],
  ["scripts/check-meaning-mission-ui.cjs"],
  ["scripts/check-unit-learning-ui.cjs"],
  ["scripts/check-practice-feedback-ui.cjs"],
  ["scripts/check-lemma-headword.cjs"],
  ["scripts/check-vocab-goal-ui.cjs"],
  ["scripts/check-grade-scope.cjs"],
  ["scripts/check-word-origin-data.cjs"],
  ["scripts/check-word-origin-ui.cjs"],
  ["scripts/check-state-transitions.cjs"],
  ["scripts/check-study-plan.cjs"],
  ["scripts/check-study-plan-ui.cjs"],
  ["scripts/check-home-priority-ui.cjs"],
  ["scripts/check-flashcard-nav-ui.cjs"],
  ["scripts/check-meaning-example-ui.cjs"],
];

for (const args of CHECKS) {
  const result = spawnSync(process.execPath, args, { cwd: ROOT, stdio: "inherit" });
  if (result.status !== 0) {
    console.error(`\nFAILED: node ${args.join(" ")}`);
    process.exit(result.status ?? 1);
  }
}
console.log(`\nall ${CHECKS.length} checks passed`);
