const assert = require("node:assert/strict");
const { appCss, appJs, extractFunctionBody, readText } = require("./lib/app-source.cjs");

const js = appJs();
const css = appCss();
const design = readText("DESIGN.md");


const renderSessionBody = extractFunctionBody(js, "renderSession");
const stickyBody = extractFunctionBody(js, "sessionStickyNav");
const renderFlashBody = extractFunctionBody(js, "renderFlash");
const scrollBody = extractFunctionBody(js, "scrollFlashCardIntoView");
const gestureBody = extractFunctionBody(js, "setupFlashGesture");
const springBody = extractFunctionBody(js, "animateFlashGesture");

// 固定バーはflashステージだけ。renderSession全体へスクロール処理を混ぜない。
assert.ok(renderSessionBody.includes('panel.classList.toggle("hasActionBar", session.stage === "flash")'));
assert.ok(!renderSessionBody.includes("scrollFlashCardIntoView"), "他ステージへスクロール処理を持ち込まない");

// 前後の2経路の両方で、新しいカードをsticky見出しの下へ戻す。
assert.equal(
  (renderFlashBody.match(/scrollFlashCardIntoView\(\)/g) || []).length,
  2,
  "前カード・次カードの両方でscrollFlashCardIntoView()が必要",
);
assert.ok(scrollBody.includes("window.scrollTo"), "カード送り後はwindow.scrollToを使う必要がある");
assert.ok(scrollBody.includes('behavior: "auto"'), "カード送り後のスクロールは即時である必要がある");
assert.ok(scrollBody.includes("sessionStickyNav"), "stickyバーの高さをスクロール位置から引く必要がある");

// 450msガードは無効化せず、受付済みの見た目だけを付ける。disabledは使わない。
assert.ok(renderFlashBody.includes("flashNavLocked()"), "flashNavLocked()を使う必要がある");
assert.ok(renderFlashBody.includes("isGuarded"), "ガード中の状態クラスが必要");
assert.ok(renderFlashBody.includes('"aria-disabled": "true"'), "ガード中はaria-disabledを付ける必要がある");
const guardedAttrsStart = renderFlashBody.indexOf("const guardedAttrs");
const guardedAttrsEnd = renderFlashBody.indexOf("const canGoBack", guardedAttrsStart);
assert.ok(guardedAttrsStart !== -1 && guardedAttrsEnd > guardedAttrsStart, "guardedAttrsの範囲が特定できない");
assert.ok(
  !renderFlashBody.slice(guardedAttrsStart, guardedAttrsEnd).includes('disabled: "disabled"'),
  "ガード表現にdisabled属性を使わない",
);
assert.ok(renderFlashBody.includes("removeAttribute(\"aria-disabled\")"), "ガード終了時にaria-disabledを外す必要がある");

// カウンタは固定バー中央へ一本化する。
assert.ok(!stickyBody.includes("sessionStickyFlash"), "上部stickyバーに暗記カードカウンタを残さない");
assert.ok(!renderFlashBody.includes("cardCounter"), "下部の旧カウンタを残さない");
assert.ok(renderFlashBody.includes("flashNavCounter"), "固定バー中央のカウンタが必要");
assert.ok(renderFlashBody.includes("sessionActionBar"), "固定バーのラッパーが必要");

// スワイプはボタン操作を置き換えず、暗記カードの補助操作として直接操作できるようにする。
assert.ok(renderFlashBody.includes("setupFlashGesture"), "暗記カードにスワイプ操作を接続する必要がある");
for (const token of ["setPointerCapture", "pointermove", "pointerup", "releaseVelocity", "flashRubberband"]) {
  assert.ok(gestureBody.includes(token), `スワイプ実装に${token}が必要`);
}
assert.ok(springBody.includes("requestAnimationFrame"), "スワイプの着地にフレーム同期処理が必要");

// CSS契約。固定バーはParchment＋hairlineで、safe-areaと本文の逃げを持つ。
assert.match(css, /#sessionPanel\.hasActionBar\s*\{[\s\S]*padding-bottom:\s*calc\(76px \+ env\(safe-area-inset-bottom\)\)/);
assert.match(css, /\.sessionActionBar\s*\{[\s\S]*position:\s*fixed;[\s\S]*z-index:\s*6;[\s\S]*background:\s*var\(--parchment\);[\s\S]*border-top:\s*1px solid var\(--line\)/);
assert.match(
  css,
  /\.sessionActionBar\s*\{[\s\S]*padding:\s*12px 0 max\(12px, env\(safe-area-inset-bottom\)\)/,
);
assert.match(css, /\.flashNav\s*\{[\s\S]*gap:\s*12px/);
assert.match(css, /\.flashNav \.cta\s*\{[\s\S]*min-width:\s*min\(100%, 160px\)/);
assert.match(css, /\.flashNav \.isGuarded\s*\{[\s\S]*opacity:\s*\.6/);
assert.match(css, /\.flash\s*\{[\s\S]*touch-action:\s*pan-y/);
assert.match(css, /\.flash\.gestureActive\s*\{[\s\S]*will-change:\s*transform, opacity/);
assert.match(css, /@media \(prefers-reduced-transparency: reduce\)[\s\S]*backdrop-filter:\s*none/);
assert.match(css, /@media \(prefers-contrast: more\)[\s\S]*border-color:\s*var\(--ink\)/);
assert.match(css, /\.flashMeaning\s*\{[^}]*font-size:\s*(\d+)px[^}]*font-weight:\s*600/);
const meaningSize = Number(css.match(/\.flashMeaning\s*\{[^}]*font-size:\s*(\d+)px/)[1]);
assert.ok(meaningSize >= 22, "意味は22px以上である必要がある");
assert.match(css, /\.flashMeaning,\s*\.flashExampleTranslation\s*\{[^}]*max-inline-size:\s*34em/);
const exampleWidth = Number(css.match(/\.flashEx\s*\{[^}]*max-inline-size:\s*(\d+)ch/)[1]);
assert.ok(exampleWidth <= 70, "例文の行幅は70ch以下である必要がある");
assert.ok(!css.includes(".sessionStickyFlash"), "未使用のsessionStickyFlash CSSを残さない");
assert.ok(!css.includes(".cardCounter"), "未使用のcardCounter CSSを残さない");

// DESIGN.mdを実装と同じ正本へ更新する。
// 行幅はCSSの実装値をそのまま照合する。固定値を書くと、実装だけ変えたときに
// DESIGN.mdとCSSが食い違ったまま通ってしまう（実際に70ch/58chで食い違った）。
for (const token of [".sessionActionBar", ".flashMeaning", "34em", `${exampleWidth}ch`]) {
  assert.ok(design.includes(token), `DESIGN.mdに${token}の規範が必要`);
}

console.log("flashcard navigation UI contract: OK");
