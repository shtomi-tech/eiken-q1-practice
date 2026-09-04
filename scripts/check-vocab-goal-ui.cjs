const assert = require("node:assert/strict");
const vm = require("node:vm");
const { appCss, appJs } = require("./lib/app-source.cjs");

const js = appJs();
const css = appCss();

const block = js.match(/const VOCAB_GOALS = \{[\s\S]*?\n\};/);
assert.ok(block, "VOCAB_GOALS の定義が見つからない");
const sandbox = {};
vm.runInNewContext(`${block[0]}\nglobalThis.goals = VOCAB_GOALS;`, sandbox);
const goals = sandbox.goals;

// 級の並び。前級の target が次級の prev と一致していないと「累計＝前級＋差分」の説明が崩れる。
const order = ["eikenp2", "eiken2", "eikenp1", "eiken1"];
for (const grade of order) {
  const g = goals[grade];
  assert.ok(g, `VOCAB_GOALS に ${grade} が必要`);
  assert.ok(g.target > g.prev, `${grade} の target は prev より大きい必要がある`);
  assert.ok(g.prevLabel, `${grade} に prevLabel が必要`);
}
for (let i = 1; i < order.length; i++) {
  assert.equal(
    goals[order[i]].prev,
    goals[order[i - 1]].target,
    `${order[i]} の prev は ${order[i - 1]} の target と一致する必要がある（累計と差分の整合）`,
  );
}
// 生徒に示す丸めた目安。端数が出ると「あと2,000語」の説明ができなくなる。
for (const grade of order) {
  assert.equal(goals[grade].target % 500, 0, `${grade} の target は500の倍数にする`);
  assert.equal((goals[grade].target - goals[grade].prev) % 500, 0, `${grade} の差分は500の倍数にする`);
}

// 5級は前級を持たない起点なので上の連鎖には入れず、単独で妥当性を検査する。
const grade5 = goals.eiken5;
assert.ok(grade5, "VOCAB_GOALS に eiken5 が必要");
assert.equal(grade5.prev, 0, "5級は前級を持たないので prev は0にする");
assert.ok(grade5.target > grade5.prev, "5級の target は prev より大きい必要がある");
assert.equal(goals.eikenp2.prev, 1500, "準2級の prev（3級相当）は5級の target と連鎖させない");

const start = js.indexOf("function vocabGoalCard(");
assert.ok(start !== -1, "vocabGoalCard() が見つからない");
const body = js.slice(start, js.indexOf("\nfunction ", start + 1));
// 実績は差分区間を超えて描かない（バーが目標をはみ出さないため）
assert.match(body, /Math\.min\(learned, gap\)/, "実績は差分(gap)でクランプする必要がある");
// カード本体の前級注記は撤去済み。目安である旨は forecast 折りたたみ内の「理論上の学習量です／収録語句数」で担保する。
assert.ok(body.includes("理論上の学習量です"), "推定値であることの注記（forecast内）が必要");
assert.ok(body.includes('role: "progressbar"'), "バーは progressbar として読み上げ可能にする必要がある");
assert.ok(body.includes('"aria-valuetext"'), "aria-valuetext で内訳を読み上げる必要がある");
assert.match(body, /const prevTick = goal\.prev > 0/, "前級を持たない級（5級）では0の目盛りを出さない");
assert.ok(body.includes('"aria-hidden": "true"'), "装飾のハリネズミは支援技術から隠す必要がある");
assert.ok(body.includes("vocabularyGoalForecast"), "目標語数への到達予想を既存カードへ追加する必要がある");
assert.ok(body.includes("vocabularyForecast"), "期間別語句予測を既存カードへ追加する必要がある");
assert.ok(body.includes("現在、このアプリの英検${dataset().shortLabel}通常問題には"), "収録語句数の注記を表示する必要がある");
assert.ok(body.includes("1週間後") && body.includes("1年後"), "5期間の語句予測を表示する必要がある");

// バー・ハリネズミ・目盛り・メッセージ・前級注記は常時表示（折りたたまない）。折りたたむのは期間別予測（.vocabForecast）だけ。
assert.ok(!body.includes("vocabGoalDetails"), "語彙目標カード本体（バー・ハリネズミ・メッセージ）は折りたたまず常時表示する");
assert.ok(body.includes('class: "vgBar"') && body.includes('class: "vgMessage"'), "バー（.vgBar）と励ましメッセージ（.vgMessage）を常時描画する必要がある");

const renderHome = js.slice(js.indexOf("function renderHomeContent("));
assert.match(renderHome, /home\.appendChild\(goalCard\)/, "語彙目標カードはホーム直下へ追加する必要がある");

for (const cls of [".vgHead", ".vgTrack", ".vgFillBase", ".vgFillOwn", ".vgHedgehog", ".vgTick"]) {
  assert.ok(css.includes(cls), `CSSに ${cls} の規則が必要`);
}
// ドット絵は2px刻み・12x7マス（58ドット）。崩れるとバー上でハリネズミに見えなくなる。
const shadow = css.match(/\.vgHedgehogSprite \{[\s\S]*?box-shadow:([\s\S]*?);/);
assert.ok(shadow, ".vgHedgehogSprite の box-shadow が見つからない");
assert.equal(shadow[1].split(",").length, 58, "ハリネズミのドットは58個である必要がある");

console.log("vocab goal UI contract: OK");
