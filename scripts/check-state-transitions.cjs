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
const startMeaningBody = extractFunctionBody(js, "startMeaningPractice");
const startFinalBody = extractFunctionBody(js, "startFinalCheck");
const renderSessionBody = extractFunctionBody(js, "renderSession");
const restoreSessionBody = extractFunctionBody(js, "restoreSession");
const finalUnlockedBody = extractFunctionBody(js, "finalUnlocked");
const renderDoneBody = extractFunctionBody(js, "renderDone");
const migrateBody = extractFunctionBody(js, "migrateLegacyPre1Progress");
const currentResumeBody = extractFunctionBody(js, "currentResume");
const resumableResumeBody = extractFunctionBody(js, "resumableResume");
const answerBody = extractFunctionBody(js, "onPracticeAnswer");

for (const marker of ["Q1_UNLEARNED", "Q1_FLASH", "Q1_MEANING_CHECK", "Q1_PRACTICE", "Q1_DONE"]) {
  assert.ok(spec.includes(marker), `状態仕様に ${marker} が必要です`);
}
for (const removed of ["Q1_WRONG_REVIEW", "Q1_REVIEW", "wrongReview", "reviewQueue", "startReview"]) {
  assert.ok(!js.includes(removed) && !spec.includes(removed), `${removed} は削除されている必要があります`);
}
assert.match(spec, /eiken_q1_progress_<datasetId>/, "進捗保存境界を仕様に記録する必要があります");
assert.match(spec, /reading1:<q>/, "旧準1級移行の入力形式を仕様に記録する必要があります");

assert.ok(startLearnBody.includes('mode: "learn"'), "通常学習はlearnモードで開始する必要があります");
assert.ok(startLearnBody.includes('stage: "flash"'), "通常学習はflashから開始する必要があります");
assert.ok(startLearnBody.includes("checkOrder"), "通常学習は意味確認順を保存する必要があります");
assert.ok(startMeaningBody.includes('mode: "meaning"'), "意味復習はmeaningモードで開始する必要があります");
assert.ok(startMeaningBody.includes('stage: "check"'), "意味復習はcheckから開始する必要があります");
assert.ok(startMeaningBody.includes("MEANING_SESSION_SIZE"), "意味復習は最大件数を使う必要があります");
assert.ok(startFinalBody.includes('mode: "final"'), "最終チェックはfinalモードで開始する必要があります");
assert.ok(startFinalBody.includes("finalUnlocked"), "最終チェック開始時にも解放条件を検査する必要があります");

for (const stage of ["flash", "check", "practice", "done"]) {
  assert.ok(renderSessionBody.includes(`session.stage === "${stage}"`) || renderSessionBody.includes(`stage === "${stage}"`), `renderSessionに${stage}の描画分岐が必要です`);
}
assert.ok(finalUnlockedBody.includes("every"), "最終チェックは全設問を確認する必要があります");
assert.ok(finalUnlockedBody.includes("learned"), "最終チェックは全設問の回答済み状態を解放条件に使う必要があります");
assert.ok(renderDoneBody.includes("clearResume"), "完了画面で再開記録を削除する必要があります");
assert.ok(!renderDoneBody.includes("間違えた") && !renderDoneBody.includes("復習リスト"), "完了画面に誤答専用復習の導線を残してはいけません");

assert.match(js, /const RESUME_STAGE_RULES\s*=\s*\{/, "再開可能なmodeごとのstage契約が必要です");
assert.match(js, /function resumeStageAllowed\(/, "未知のstageを弾く判定関数が必要です");
assert.ok(restoreSessionBody.includes("resumeStageAllowed"), "restoreSessionは未対応stageを現行フローへ入れてはいけません");
assert.ok(restoreSessionBody.includes("resumeUnavailable"), "再開できない記録は削除せず案内状態にする必要があります");
assert.ok(resumableResumeBody.includes("resumeStageAllowed"), "未対応stageを通常の再開CTAへ流してはいけません");
assert.ok(currentResumeBody.includes("resumableResume"), "currentResume()は共通の再開可能判定を使う必要があります");

assert.ok(migrateBody.includes("eikenp1-"), "旧準1級進捗を現行datasetIdへ移す必要があります");
assert.ok(migrateBody.includes('learned: true'), "旧回答済み設問をlearnedとして移行する必要があります");
assert.ok(migrateBody.includes("migrations"), "旧準1級進捗の移行を一度だけ記録する必要があります");

assert.ok(answerBody.includes("firstAnsweredAt"), "本番形式の初回答時刻を保存する必要があります");
assert.ok(answerBody.includes("isValidIsoDate"), "既存の有効な初回答時刻を保持する必要があります");
assert.equal((answerBody.match(/u\.firstAnsweredAt\s*=/g) || []).length, 1, "初回答時刻は回答処理内の1箇所だけで設定する必要があります");
assert.ok(answerBody.includes("u.lastAnsweredAt = answeredAt"), "最終回答時刻は従来どおり更新する必要があります");
assert.ok(answerBody.includes("u.needsReview = false"), "誤答を専用復習キューへ追加してはいけません");

assert.match(packageJson.scripts.test, /node --check static\/app\.js/, "static/app.jsの構文検査をnpm testへ含める必要があります");
assert.match(packageJson.scripts.test, /scripts\/check-state-transitions\.cjs/, "状態遷移検査をnpm testへ含める必要があります");

console.log("state transitions contract: OK");
