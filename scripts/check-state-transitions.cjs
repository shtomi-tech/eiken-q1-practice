const assert = require("node:assert/strict");
const fs = require("node:fs");

const js = fs.readFileSync("static/mode-q1.js", "utf8");
const spec = fs.readFileSync("docs/STATE_TRANSITIONS.md", "utf8");
const packageJson = JSON.parse(fs.readFileSync("package.json", "utf8"));

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

const startLearnBody = extractFunctionBody(js, "startLearn");
const startReviewBody = extractFunctionBody(js, "startReview");
const startMeaningBody = extractFunctionBody(js, "startMeaningPractice");
const startFinalBody = extractFunctionBody(js, "startFinalCheck");
const renderSessionBody = extractFunctionBody(js, "renderSession");
const restoreSessionBody = extractFunctionBody(js, "restoreSession");
const finalUnlockedBody = extractFunctionBody(js, "finalUnlocked");
const renderDoneBody = extractFunctionBody(js, "renderDone");
const migrateBody = extractFunctionBody(js, "migrateLegacyPre1Progress");
const currentResumeBody = extractFunctionBody(js, "currentResume");

for (const marker of ["Q1_UNLEARNED", "Q1_FLASH", "Q1_MEANING_CHECK", "Q1_WRONG_REVIEW", "Q1_PRACTICE", "Q1_DONE"]) {
  assert.ok(spec.includes(marker), `状態仕様に ${marker} が必要です`);
}
assert.match(spec, /eiken_q1_progress_<datasetId>/, "進捗保存境界を仕様に記録する必要があります");
assert.match(spec, /reading1:<q>/, "旧準1級移行の入力形式を仕様に記録する必要があります");

assert.ok(startLearnBody.includes('mode: "learn"'), "通常学習はlearnモードで開始する必要があります");
assert.ok(startLearnBody.includes('stage: "flash"'), "通常学習はflashから開始する必要があります");
assert.ok(startLearnBody.includes("checkOrder"), "通常学習は意味確認順を保存する必要があります");
assert.ok(startReviewBody.includes('mode: "review"'), "誤答復習はreviewモードで開始する必要があります");
assert.ok(startReviewBody.includes('stage: "practice"'), "誤答復習は本番形式から開始する必要があります");
assert.ok(startMeaningBody.includes('mode: "meaning"'), "意味復習はmeaningモードで開始する必要があります");
assert.ok(startMeaningBody.includes('stage: "check"'), "意味復習はcheckから開始する必要があります");
assert.ok(startMeaningBody.includes("MEANING_SESSION_SIZE"), "意味復習は最大件数を使う必要があります");
assert.ok(startFinalBody.includes('mode: "final"'), "最終チェックはfinalモードで開始する必要があります");
assert.ok(startFinalBody.includes("finalUnlocked"), "最終チェック開始時にも解放条件を検査する必要があります");

for (const stage of ["flash", "check", "wrongReview", "practice", "done"]) {
  assert.ok(renderSessionBody.includes(`session.stage === "${stage}"`) || renderSessionBody.includes(`stage === "${stage}"`), `renderSessionに${stage}の描画分岐が必要です`);
}
assert.ok(finalUnlockedBody.includes("every"), "最終チェックは全設問を確認する必要があります");
assert.ok(finalUnlockedBody.includes("solvedCorrect"), "最終チェックはsolvedCorrectを解放条件に使う必要があります");
assert.ok(finalUnlockedBody.includes("reviewQueue"), "最終チェックは復習対象がないことも解放条件にする必要があります");
assert.ok(renderDoneBody.includes("clearResume"), "完了画面で再開記録を削除する必要があります");

assert.match(js, /const RESUME_STAGE_RULES\s*=\s*\{/, "再開可能なmodeごとのstage契約が必要です");
assert.match(js, /function resumeStageAllowed\(/, "未知のstageを弾く判定関数が必要です");
assert.ok(restoreSessionBody.includes("resumeStageAllowed"), "restoreSessionは未対応stageを現行フローへ入れてはいけません");
assert.ok(restoreSessionBody.includes("resumeUnavailable"), "再開できない記録は削除せず案内状態にする必要があります");
assert.ok(currentResumeBody.includes("resumeStageAllowed"), "未対応stageを通常の再開CTAへ流してはいけません");

assert.ok(migrateBody.includes("eikenp1-"), "旧準1級進捗を現行datasetIdへ移す必要があります");
assert.ok(migrateBody.includes('learned: true'), "旧回答済み設問をlearnedとして移行する必要があります");
assert.ok(migrateBody.includes("migrations"), "旧準1級進捗の移行を一度だけ記録する必要があります");

assert.match(packageJson.scripts.test, /node --check static\/app\.js/, "static/app.jsの構文検査をnpm testへ含める必要があります");
assert.match(packageJson.scripts.test, /scripts\/check-state-transitions\.cjs/, "状態遷移検査をnpm testへ含める必要があります");

console.log("state transitions contract: OK");
