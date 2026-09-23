"use strict";

const assert = require("node:assert/strict");
const { appCss, appJs, extractFunctionBody } = require("./lib/app-source.cjs");

const js = appJs();
const css = appCss();
const renderContext = extractFunctionBody(js, "renderContext");
const focusSessionContext = extractFunctionBody(js, "focusSessionContext");

// 回答後も4択を残し、選択肢上で回答状態を伝える。
assert.match(renderContext, /class: `choices contextChoices\$\{session\.contextRevealed \? " contextChoicesAnswered"/,
  "Context回答後も4択コンテナを描画する必要がある");
assert.match(renderContext, /card\.appendChild\(choiceWrap\);\s*if \(session\.contextRevealed\)/,
  "回答後フィードバックより先に4択をDOMへ追加する必要がある");
assert.match(renderContext, /button\.disabled = true/, "回答後の選択肢はdisabledにする必要がある");
assert.match(renderContext, /button\.classList\.add\("correct"\)/, "正解選択肢にcorrectを付ける必要がある");
assert.match(renderContext, /button\.classList\.add\("wrong"\)/, "選択した誤答にwrongを付ける必要がある");
assert.match(renderContext, /contextChoiceDim/, "残りの選択肢を薄くする必要がある");
assert.match(renderContext, /"✓ 正解"/, "正解ラベルをテキストでも示す必要がある");
assert.match(renderContext, /"あなたの回答"/, "選んだ誤答をテキストでも示す必要がある");

// 結果カードは正誤を明示し、既存の説明情報と遷移を維持する。
assert.match(renderContext, /contextResult \$\{isCorrect \? "ok" : "ng"\}/, "通常学習でも結果カードにok/ngを付ける必要がある");
assert.match(renderContext, /id: "contextResultTitle", tabindex: "-1"/, "結果タイトルはプログラムからfocus可能にする必要がある");
assert.match(renderContext, /role: "status"[\s\S]*?"aria-live": "polite"/, "結果カードのstatus読み上げを維持する必要がある");
assert.match(renderContext, /aria-hidden": "true"/, "結果アイコンは装飾として扱う必要がある");
assert.match(renderContext, /正しい意味：\$\{correctMeaning\}/, "正しい意味を表示する必要がある");
assert.match(renderContext, /例文の訳：\$\{exampleTranslation\}/, "例文訳を表示する必要がある");
assert.match(renderContext, /2文目の訳：\$\{secondSentenceTranslation\}/, "2文目訳を表示する必要がある");
assert.match(renderContext, /あなたの選択：\$\{session\.contextPicked\}/, "誤答時に選んだ意味をカードにも表示する必要がある");
assert.match(renderContext, /この単語を覚える →/, "通常学習のCTAを維持する必要がある");
assert.doesNotMatch(renderContext, /meaningCorrect\s*[+\-]=|meaningCorrect\s*\+\+/, "Context正誤をMeaning Check得点へ加えてはいけない");
assert.doesNotMatch(renderContext, /item\.contextClues|item\.inferencePath|item\.inferenceExplanation|contextClueList/,
  "詳しいContext解説を表示してはいけない");

// DOM差し替え後は結果タイトルへフォーカスを移す。
assert.match(focusSessionContext, /session\.stage === "context" && session\.contextRevealed === true[\s\S]*?\$\("#contextResultTitle"\)/,
  "回答済みContextでは結果タイトルへfocusする必要がある");
assert.match(focusSessionContext, /focus\(\{ preventScroll: true \}\)/, "focus移動でスクロール位置を動かしてはいけない");

// 既存モーションと色トークンを使い、 disabled 全体の薄化は抑え、残りだけを弱める。
for (const cls of [
  ".contextChoicesAnswered .contextChoiceBtn:disabled",
  ".contextChoicesAnswered .contextChoiceBtn.contextChoiceDim",
  ".contextChoiceState",
  ".contextResultHead",
  ".contextResultIcon",
  ".contextResultTitle",
  ".contextResultLead",
]) {
  assert.ok(css.includes(cls), `CSSに ${cls} の規則が必要`);
}
assert.match(css, /\.contextChoicesAnswered \.contextChoiceBtn:disabled\s*\{[^}]*opacity:\s*1/,
  "disabled時に選択肢全体を薄くしてはいけない");
assert.match(css, /\.contextChoicesAnswered \.contextChoiceBtn:hover:disabled\s*\{[^}]*background:\s*var\(--paper\)[^}]*color:\s*var\(--ink\)/,
  "hover中のdisabled選択肢は紙色とInk文字を維持する必要がある");
assert.match(css, /\.contextChoicesAnswered \.contextChoiceBtn\.contextChoiceDim\s*\{[^}]*opacity:\s*\.56/,
  "対象外の選択肢だけを弱める必要がある");
assert.match(css, /\.contextResult\.ok \.contextResultIcon\s*\{[^}]*animation:\s*kStatusCheck/,
  "正解アイコンは既存kStatusCheckを使う必要がある");
assert.match(css, /\.choiceBtn\.correct[^}]*kAnswerSuccess/,
  "正解選択肢は既存の成功モーションを使う必要がある");
assert.match(css, /\.choiceBtn\.wrong[^}]*kAnswerError/,
  "誤答選択肢は既存のエラーモーションを使う必要がある");
assert.match(css, /@media \(prefers-reduced-motion: reduce\)/,
  "reduced-motion対応を維持する必要がある");
assert.doesNotMatch(css, /\.contextResult\.contextNeutral/, "未使用のcontextNeutralスタイルを残してはいけない");

console.log("context feedback UI contract: OK");
