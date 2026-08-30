const assert = require("node:assert/strict");
const { appCss, appJs, extractFunctionBody } = require("./lib/app-source.cjs");

const js = appJs();
const css = appCss();

// 対応する閉じ } まで、次の関数名に依存せず本体を抜き出す（check-unit-learning-ui.cjs と同方式）。

const renderPracticeBody = extractFunctionBody(js, "renderPractice");
const onPracticeAnswerBody = extractFunctionBody(js, "onPracticeAnswer");
const choiceMeaningsBody = extractFunctionBody(js, "practiceChoiceMeanings");

// --- practiceChoiceMeanings の中身 ---
assert.ok(
  choiceMeaningsBody.includes("q_.choices.forEach"),
  "practiceChoiceMeanings は q_.choices.forEach で全選択肢を走査する必要がある",
);
assert.ok(
  choiceMeaningsBody.includes("findItemForSurface("),
  "practiceChoiceMeanings は findItemForSurface() を使う必要がある",
);
assert.ok(choiceMeaningsBody.includes('el("section"'), "意味一覧は section を生成する必要がある");
assert.ok(choiceMeaningsBody.includes('el("h4"'), "意味一覧は見出し h4 を生成する必要がある");
assert.ok(choiceMeaningsBody.includes('el("ol"'), "意味一覧は ol を生成する必要がある");
assert.ok(choiceMeaningsBody.includes('el("li"'), "意味一覧は li を生成する必要がある");
assert.ok(choiceMeaningsBody.includes("4つの選択肢の意味"), "意味一覧の見出し文言が必要");
assert.ok(choiceMeaningsBody.includes("✓ 正解"), "正解ラベル「✓ 正解」が必要");
assert.ok(choiceMeaningsBody.includes("あなたの回答"), "選択ラベル「あなたの回答」が必要");
assert.ok(choiceMeaningsBody.includes("practiceChoiceMeaningsTitle"), "見出しIDが必要");
assert.ok(choiceMeaningsBody.includes("aria-labelledby"), "section に aria-labelledby が必要");
assert.ok(
  choiceMeaningsBody.includes("意味を取得できませんでした"),
  "意味が見つからない場合のフォールバック文言が必要",
);

// --- 呼び出し順序 ---
assert.ok(
  onPracticeAnswerBody.includes("practiceChoiceMeanings("),
  "onPracticeAnswer() は practiceChoiceMeanings(...) を呼ぶ必要がある",
);
assert.ok(
  !renderPracticeBody.includes("practiceChoiceMeanings("),
  "renderPractice() は回答前に practiceChoiceMeanings(...) を呼んではいけない",
);

const answerActionsCallIdx = onPracticeAnswerBody.indexOf("answerActions(");
const choiceMeaningsCallIdx = onPracticeAnswerBody.indexOf("practiceChoiceMeanings(");
assert.ok(answerActionsCallIdx !== -1, "onPracticeAnswer() は answerActions(...) を呼ぶ必要がある");
assert.ok(
  choiceMeaningsCallIdx !== -1 && choiceMeaningsCallIdx < answerActionsCallIdx,
  "意味一覧の追加は answerActions(...) より前に行う必要がある",
);

// --- CSS ---
for (const cls of [
  ".practiceChoiceMeanings",
  ".practiceChoiceMeaningList",
  ".practiceChoiceMeaningRow",
  ".practiceChoiceMeaningHead",
  ".practiceChoiceMeaningText",
  ".practiceChoiceMeaningState",
]) {
  assert.ok(css.includes(cls), `CSSに ${cls} の規則が必要`);
}

console.log("practice feedback UI contract: OK");
