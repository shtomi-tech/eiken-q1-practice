// vendoring した ts-fsrs が「本番でも配信される」ことを機械的に守るための検査。
//
// pages.yml の Prepare static files はコピー対象を明示列挙しているため、
// 追記を忘れると本番だけ 404 になり、ローカルでは絶対に再現しない。
// ここが落ちる状態でデプロイしてはいけない。
const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const VENDOR_REL = "static/vendor/fsrs/index.umd.js";
const EXPECTED_VERSION = "5.4.2";
const EXPECTED_SHA256 = "59b7444121d0aae5bb969097ed95df38eff4a4f878e459703c63720f6b6a176b";

const read = (rel) => fs.readFileSync(path.join(ROOT, rel), "utf8");

// --- 実ファイルが版ごと固定されている ---
const vendor = fs.readFileSync(path.join(ROOT, VENDOR_REL));
assert.equal(
  crypto.createHash("sha256").update(vendor).digest("hex"),
  EXPECTED_SHA256,
  `${VENDOR_REL} が配布物と一致しない。差し替えたなら static/vendor/fsrs/README.md と本スクリプトを更新すること`,
);
const vendorText = vendor.toString("utf8");
assert.ok(
  vendorText.includes(`version="${EXPECTED_VERSION}"`) && vendorText.includes("using FSRS-6.0"),
  `vendor は ts-fsrs ${EXPECTED_VERSION}（FSRS-6）である必要がある`,
);
assert.ok(
  vendorText.includes("global.FSRS = {}"),
  "UMDのグローバル名は FSRS である必要がある（mode-q1.js が globalThis.FSRS を見る）",
);
assert.ok(
  fs.existsSync(path.join(ROOT, "static/vendor/fsrs/LICENSE")),
  "MITライセンス本文を同梱する必要がある",
);
const vendorReadme = read("static/vendor/fsrs/README.md");
assert.ok(vendorReadme.includes(EXPECTED_VERSION), "vendor README に版を記録する必要がある");
assert.ok(vendorReadme.includes(EXPECTED_SHA256), "vendor README に sha256 を記録する必要がある");

// --- 本番へコピーされる（これが本検査の主目的） ---
const workflow = read(".github/workflows/pages.yml");
assert.ok(
  workflow.includes("_site/static/vendor/fsrs"),
  "pages.yml が _site/static/vendor/fsrs を作る必要がある（漏れると本番だけ404）",
);
assert.match(
  workflow,
  /cp\s+static\/vendor\/fsrs\/index\.umd\.js[^\n]*_site\/static\/vendor\/fsrs\//,
  "pages.yml が vendor/fsrs/index.umd.js を _site へコピーする必要がある（漏れると本番だけ404）",
);

// --- 読み込み順（vendor が mode-q1.js より前） ---
const html = read("index.html");
const vendorIdx = html.indexOf("static/vendor/fsrs/index.umd.js");
const appIdx = html.indexOf("static/mode-q1.js");
assert.ok(vendorIdx !== -1, "index.html が vendor/fsrs を読み込む必要がある");
assert.ok(appIdx !== -1, "index.html が mode-q1.js を読み込む必要がある");
assert.ok(vendorIdx < appIdx, "vendor/fsrs は mode-q1.js より前に読み込む必要がある");

console.log(`fsrs vendor contract: OK (ts-fsrs ${EXPECTED_VERSION})`);
