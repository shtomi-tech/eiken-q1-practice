const assert = require("node:assert/strict");
const { appCss, appJs, extractFunctionBody } = require("./lib/app-source.cjs");

const js = appJs();
const css = appCss();

// 対応する閉じ } まで、次の関数名に依存せず本体を抜き出す（check-meaning-mission-ui.cjs と同方式）。

const renderHomeBody = extractFunctionBody(js, "renderHomeContent");
const datasetPickerBody = extractFunctionBody(js, "datasetPicker");
const datasetUnitCardsBody = extractFunctionBody(js, "datasetUnitCards");
const datasetUnitCardBody = extractFunctionBody(js, "datasetUnitCard");
const buildQuestionCardBody = extractFunctionBody(js, "buildQuestionCard");
const questionFilterBarBody = extractFunctionBody(js, "questionFilterBar");
const sessionStickyNavBody = extractFunctionBody(js, "sessionStickyNav");
const renderSessionBody = extractFunctionBody(js, "renderSession");
const renderDoneBody = extractFunctionBody(js, "renderDone");

// --- 集計関数（Task2） ---
assert.match(js, /function datasetSummary\(datasetId, ?data\)/, "datasetSummary(datasetId, data) が必要");
assert.match(js, /function datasetPrimaryLabel\(/, "datasetPrimaryLabel が必要");

// --- 問題セットUnitカード（Task3） ---
assert.ok(
  datasetPickerBody.includes("datasetUnitCards("),
  "datasetPicker() は datasetUnitCards() を使う必要がある",
);
assert.ok(!datasetPickerBody.includes('el("select"'), "問題セットのselect要素は撤去する必要がある");
assert.ok(datasetUnitCardBody.includes("switchDataset("), "Unitカードのクリックは switchDataset() を呼ぶ必要がある");
assert.ok(datasetUnitCardBody.includes("aria-current"), "現在のセットのUnitカードは aria-current を持つ必要がある");
assert.ok(datasetUnitCardBody.includes("CLEAR"), "CLEAR済みセットは文言でCLEARを示す必要がある");
assert.ok(datasetUnitCardsBody.includes("過去問") && datasetUnitCardsBody.includes("模試"), "過去問・模試の小見出しが必要");

// --- 問題カード（Task4） ---
for (const cls of ["qCardNumber", "qCardMain", "qCardArrow"]) {
  assert.ok(buildQuestionCardBody.includes(cls), `問題カードは ${cls} を生成する必要がある`);
}
assert.ok(buildQuestionCardBody.includes('"aria-hidden": "true"'), "矢印は装飾なので aria-hidden が必要");
assert.ok(renderHomeBody.includes("buildQuestionCard("), "renderHomeContent は buildQuestionCard() を使う必要がある");

// --- フィルター（Task5） ---
assert.ok(questionFilterBarBody.includes("aria-pressed"), "フィルターボタンは aria-pressed を使う必要がある");
assert.ok(questionFilterBarBody.includes('role: "group"'), "状態・種別フィルターは別グループのrole=groupにする必要がある");
assert.ok(js.includes("すべて表示"), "フィルター0件時の復帰操作「すべて表示」が必要");
assert.ok(js.includes("questionFilters"), "表示専用の questionFilters state が必要");

// --- ホーム三層構成（Task6） ---
const datasetPickerCallIdx = renderHomeBody.indexOf("datasetPicker()");
const buildQuestionCardCallIdx = renderHomeBody.indexOf("buildQuestionCard(");
assert.ok(datasetPickerCallIdx !== -1, "renderHomeContent は datasetPicker() を呼ぶ必要がある");
assert.ok(buildQuestionCardCallIdx !== -1, "renderHomeContent は buildQuestionCard() を呼ぶ必要がある");
assert.ok(
  datasetPickerCallIdx < buildQuestionCardCallIdx,
  "問題セットUnitカードは問題一覧より前に描画する必要がある",
);
assert.match(
  renderHomeBody,
  /home\.appendChild\(meaningMission\(/,
  "間隔復習カードは引き続きホーム直下へ追加する必要がある（既存契約を維持）",
);

// --- sticky現在地ナビ（Task7） ---
assert.ok(renderSessionBody.includes("sessionStickyNav("), "renderSession は sessionStickyNav() を描画する必要がある");
assert.ok(
  renderSessionBody.indexOf("sessionStickyNav(") < renderSessionBody.indexOf('class: "itemHead"'),
  "sticky版は既存の itemHead より前（上）に描画する必要がある",
);
assert.ok(sessionStickyNavBody.includes("renderHome"), "sticky版にも一覧へ戻る操作が必要");

// --- 完了画面（Task8） ---
assert.ok(
  renderDoneBody.indexOf("startLearn(nextQ)") < renderDoneBody.lastIndexOf("startFinalCheck"),
  "誤答専用復習を挟まず、次の設問から最終チェックへ進める必要がある",
);
assert.ok(!renderDoneBody.includes("pendingReviews"), "完了画面に誤答復習待ちの状態を残してはいけません");
assert.ok(!renderDoneBody.includes("間違えた"), "完了画面に誤答問題の復習文言を残してはいけません");

// --- CSS ---
for (const cls of [".datasetUnitCard", ".datasetUnitGrid", ".qCardNumber", ".qCardMain", ".qCardArrow", ".questionFilterBar", ".sessionStickyNav"]) {
  assert.ok(css.includes(cls), `CSSに ${cls} の規則が必要`);
}
assert.match(css, /@media \(max-width: 720px\)/, "720px以下のレスポンシブ規則が必要");
assert.match(css, /@media \(prefers-reduced-motion: reduce\)/, "prefers-reduced-motion の規則が必要（既存維持）");

console.log("unit learning UI contract: OK");
