const assert = require("node:assert/strict");
const { appCss, appJs, extractFunctionBody, readJson } = require("./lib/app-source.cjs");

const js = appJs();
const css = appCss();
const manifest = readJson("data/manifest.json");


const renderHomeBody = extractFunctionBody(js, "renderHomeContent");
const summaryBody = extractFunctionBody(js, "datasetSummary");
const labelBody = extractFunctionBody(js, "datasetPrimaryLabel");
const cardBody = extractFunctionBody(js, "datasetUnitCard");
const forecastBody = extractFunctionBody(js, "vocabGoalCard");
const meaningMissionBody = extractFunctionBody(js, "meaningMission");

const nextBranch = renderHomeBody.indexOf("else if (nextQ)");
assert.ok(nextBranch !== -1, "ホームに未学習設問の分岐が必要");
assert.ok(!renderHomeBody.includes("reviewQs"), "ホームに誤答問題の復習キューを残してはいけません");
assert.ok(!renderHomeBody.includes("startReview"), "ホームに誤答問題の復習開始処理を残してはいけません");
assert.ok(!renderHomeBody.includes("primaryIsReview"), "ホームに誤答復習専用の主CTA状態を残してはいけません");
assert.ok(!renderHomeBody.includes("間違えた"), "ホームに誤答問題の復習文言を残してはいけません");
// 1画面の塗りCTAは1つ。主CTAがある限り間隔復習は二次操作へ落とす。
assert.ok(renderHomeBody.includes("Boolean(primary),"), "主CTAの有無を意味復習カードへ渡す必要がある");
assert.ok(meaningMissionBody.includes("if (hasPrimaryCta) buttonAttrs.class = \"secondaryCta"), "主CTAがあるとき間隔復習CTAは二次操作にする必要がある");

assert.ok(summaryBody.includes("hasResume"), "datasetSummary() に途中保存状態が必要");
assert.ok(summaryBody.includes('status = "resumable"'), "学習済み0でも途中保存をresumableとして扱う必要がある");
assert.ok(labelBody.includes('summary.status === "resumable"'), "datasetPrimaryLabel() はresumableを扱う必要がある");
assert.ok(cardBody.includes("resumeDescription"), "UnitカードはresumeDescription()を再利用する必要がある");

// F-04: 途中保存(coreResume)時、同じ再開先を開く主CTAはホーム上部の .startCta 1つだけ。
// coreResume分岐の primary は「続きから再開する」+ restoreSession の1オブジェクトに限る。
assert.match(
  renderHomeBody,
  /if \(coreResume\) \{\s*primary = \{\s*label: "続きから再開する",/,
  "coreResume時の主CTAはホーム上部の『続きから再開する』1つへ集約する必要がある（F-04）",
);
assert.match(
  renderHomeBody,
  /primary = \{\s*label: "続きから再開する",\s*onclick: async \(\) => \{[^}]*restoreSession\(\)/,
  "coreResume時の上部主CTAは restoreSession() を呼ぶ必要がある（F-04）",
);
assert.ok(
  renderHomeBody.includes('rec.appendChild(el("button", { class: "cta startCta"'),
  "上部の主CTAは .startCta として1つだけ描画する（既存維持・F-04）",
);
// 現在セットの途中保存Unitカードは操作要素ではなく状態表示コンテナ（div）にし、
// restoreSession をもう一つのCTAとして持たない。別セットは switchDataset で切替できる。
assert.ok(
  cardBody.includes('summary.resume.mode !== "meaning"') && cardBody.includes("isResumeStatus"),
  "現在セットの通常学習途中保存Unitは状態表示（isResumeStatus）へ切り替える判定が必要（F-04）",
);
assert.match(
  cardBody,
  /if \(isResumeStatus\) \{\s*return el\("div"/,
  "isResumeStatus のUnitカードは button ではなく div を返す必要がある（F-04）",
);
assert.ok(
  cardBody.includes('"aria-current": "true"') && cardBody.includes("datasetUnitCardProgress") && cardBody.includes("datasetUnitCardResume"),
  "状態表示化しても aria-current・進捗・途中保存文言は保持する必要がある（F-04）",
);

for (const [datasetId, data] of Object.entries(manifest.q1)) {
  for (const key of ["totalQuestions", "totalVocabulary"]) {
    assert.ok(Number.isInteger(data[key]) && data[key] > 0, `${datasetId}.${key} は正の整数である必要がある`);
  }
}

assert.ok(forecastBody.includes('el("details"'), "語彙予測はdetailsで折りたためる必要がある");
assert.ok(forecastBody.includes('el("summary"'), "語彙予測のsummaryが必要");
const summaryStart = forecastBody.indexOf('el("summary"');
const summaryEnd = forecastBody.indexOf("forecast.appendChild(forecastSummary)", summaryStart);
assert.ok(summaryEnd > summaryStart, "forecastSummary の組み立て範囲が特定できない");
assert.ok(
  !forecastBody.slice(summaryStart, summaryEnd).includes("vocabForecastDate"),
  "到達予想日はsummaryの外へ置く必要がある（開閉ボタンの読み上げ名を結論1行に保つ）",
);
for (const selector of [
  ".datasetUnitCardResume",
  ".vocabForecast > summary",
  ".vocabForecast h4,",
  "details.vocabForecast:not([open]) > :not(summary)",
]) {
  assert.ok(css.includes(selector), `CSSに ${selector} の規則が必要`);
}

console.log("home priority UI contract: OK");
