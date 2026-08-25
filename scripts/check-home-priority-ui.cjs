const assert = require("node:assert/strict");
const fs = require("node:fs");

const js = fs.readFileSync("static/mode-q1.js", "utf8");
const css = fs.readFileSync("static/styles.css", "utf8");
const manifest = JSON.parse(fs.readFileSync("data/manifest.json", "utf8"));

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

const renderHomeBody = extractFunctionBody(js, "renderHomeContent");
const summaryBody = extractFunctionBody(js, "datasetSummary");
const labelBody = extractFunctionBody(js, "datasetPrimaryLabel");
const cardBody = extractFunctionBody(js, "datasetUnitCard");
const forecastBody = extractFunctionBody(js, "vocabGoalCard");
const meaningMissionBody = extractFunctionBody(js, "meaningMission");

const reviewBranch = renderHomeBody.indexOf("else if (reviewQs.length)");
const nextBranch = renderHomeBody.indexOf("else if (nextQ)");
assert.ok(reviewBranch !== -1, "ホームに復習優先の分岐が必要");
assert.ok(nextBranch !== -1, "ホームに未学習設問の分岐が必要");
assert.ok(reviewBranch < nextBranch, "ホームの復習分岐は次の設問分岐より前である必要がある");
assert.ok(renderHomeBody.includes("間違えた設問です。忘れないうちに1問ずつ確認します。"), "復習主CTAの理由文が必要");
assert.ok(renderHomeBody.includes("primaryIsReview"), "復習主CTAの状態を主CTAの見た目へ反映する必要がある");
// 1画面の塗りCTAは1つ。主CTAがある限り間隔復習は二次操作へ落とす。
assert.ok(renderHomeBody.includes("Boolean(primary),"), "主CTAの有無を意味復習カードへ渡す必要がある");
assert.ok(meaningMissionBody.includes("if (hasPrimaryCta) buttonAttrs.class = \"secondaryCta"), "主CTAがあるとき間隔復習CTAは二次操作にする必要がある");
assert.ok(renderHomeBody.includes("secondaryCta"), "復習主CTAには未学習設問への二次CTAが必要");
assert.ok(renderHomeBody.includes("reviewCta"), "復習主CTAはreviewCtaとして表示する必要がある");

assert.ok(summaryBody.includes("hasResume"), "datasetSummary() に途中保存状態が必要");
assert.ok(summaryBody.includes('status = "resumable"'), "学習済み0でも途中保存をresumableとして扱う必要がある");
assert.ok(labelBody.includes('summary.status === "resumable"'), "datasetPrimaryLabel() はresumableを扱う必要がある");
assert.ok(cardBody.includes("resumeDescription"), "UnitカードはresumeDescription()を再利用する必要がある");

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
