const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const js = fs.readFileSync("static/mode-q1.js", "utf8");
const css = fs.readFileSync("static/styles.css", "utf8");

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

const start = js.indexOf("function vocabGoalCard(");
assert.ok(start !== -1, "vocabGoalCard() が見つからない");
const body = js.slice(start, js.indexOf("\nfunction ", start + 1));
// 実績は差分区間を超えて描かない（バーが目標をはみ出さないため）
assert.match(body, /Math\.min\(learned, gap\)/, "実績は差分(gap)でクランプする必要がある");
// 目安であることと前級既習前提は必ず併記する（数値の性格を誤解させない）
assert.ok(body.includes("習得済みとして計算"), "前級を既習前提としている旨の注記が必要");
assert.ok(body.includes("目安です"), "語彙数が目安である旨の注記が必要");
assert.ok(body.includes('role: "progressbar"'), "バーは progressbar として読み上げ可能にする必要がある");
assert.ok(body.includes('"aria-valuetext"'), "aria-valuetext で内訳を読み上げる必要がある");
assert.ok(body.includes('"aria-hidden": "true"'), "装飾の猫は支援技術から隠す必要がある");

const renderHome = js.slice(js.indexOf("function renderHomeContent("));
assert.match(renderHome, /home\.appendChild\(goalCard\)/, "語彙目標カードはホーム直下へ追加する必要がある");

for (const cls of [".vgHead", ".vgTrack", ".vgFillBase", ".vgFillOwn", ".vgCat", ".vgTick"]) {
  assert.ok(css.includes(cls), `CSSに ${cls} の規則が必要`);
}
// ドット絵は2px刻み・10x6マス（34ドット）。崩れるとバー上で猫に見えなくなる。
const shadow = css.match(/\.vgCatSprite \{[\s\S]*?box-shadow:([\s\S]*?);/);
assert.ok(shadow, ".vgCatSprite の box-shadow が見つからない");
assert.equal(shadow[1].split(",").length, 34, "猫のドットは34個である必要がある");

console.log("vocab goal UI contract: OK");
