const assert = require("node:assert/strict");
const fs = require("node:fs");

const js = fs.readFileSync("static/mode-q1.js", "utf8");
const css = fs.readFileSync("static/styles.css", "utf8");

// meaningMission() 本体を波括弧の対応で抜き出す（次の関数名に依存しない）。
function extractFunctionBody(source, name) {
  const start = source.indexOf(`function ${name}(`);
  assert.ok(start !== -1, `function ${name}( が見つからない`);
  const braceStart = source.indexOf("{", start);
  assert.ok(braceStart !== -1, `${name} の開始 { が見つからない`);
  let depth = 0;
  for (let i = braceStart; i < source.length; i++) {
    if (source[i] === "{") depth++;
    else if (source[i] === "}") {
      depth--;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error(`${name} の閉じ } が見つからない`);
}

const meaningMissionBody = extractFunctionBody(js, "meaningMission");
const intervalBreakdownBody = extractFunctionBody(js, "meaningIntervalBreakdown");

// --- ラベル・見出し ---
assert.ok(meaningMissionBody.includes("間隔復習"), "meaningMission() は「間隔復習」ラベルを描画する必要がある");
assert.ok(meaningMissionBody.includes("意味だけ復習"), "meaningMission() は「意味だけ復習」見出しを描画する必要がある");
assert.ok(!meaningMissionBody.includes("中心学習"), "旧ラベル「中心学習」は meaningMission() から除去済みである必要がある");

// --- 英検固有仕様の維持 ---
assert.match(js, /const MEANING_SESSION_SIZE = 30;/, "MEANING_SESSION_SIZE は30のまま維持する");
const intervalsBlockMatch = js.match(/const MEANING_INTERVALS = \[[\s\S]*?\];/);
assert.ok(intervalsBlockMatch, "MEANING_INTERVALS の定義が見つからない");
const intervalsBlock = intervalsBlockMatch[0];
for (const label of ["未実施", "要再確認", "1日後", "3日後", "7日後", "14日後"]) {
  assert.ok(intervalsBlock.includes(label), `MEANING_INTERVALS に "${label}" が残っている必要がある`);
}

// --- 復習開始の呼び出しが維持されている ---
assert.ok(
  meaningMissionBody.includes("startMeaningPractice(true, nextQueue)"),
  "復習開始は引き続き startMeaningPractice(true, nextQueue) を呼ぶ必要がある",
);

// --- CTAの状態分岐が残っている ---
assert.ok(
  meaningMissionBody.includes("通常学習後に利用できます"),
  "対象0件のCTA文言「通常学習後に利用できます」が必要",
);
assert.ok(
  meaningMissionBody.includes("今すぐ復習する語句はありません"),
  "due 0件のCTA文言「今すぐ復習する語句はありません」が必要",
);
assert.ok(
  meaningMissionBody.includes("対象を確認中"),
  "読込中のCTA文言「対象を確認中…」が必要",
);
assert.match(
  meaningMissionBody,
  /disabled/,
  "対象0件・due 0件・読込中でCTAをdisabledにする分岐が必要",
);

// --- 新しい2指標・6セルグリッド用クラス ---
assert.ok(
  meaningMissionBody.includes("meaningMissionMetrics"),
  "2指標グリッド用クラス meaningMissionMetrics がJSに必要",
);
assert.ok(
  !meaningMissionBody.includes("今回の1回分") && !meaningMissionBody.includes("未解放"),
  "旧4指標（今回の1回分・未解放）はカード上部の指標から除去する必要がある",
);
assert.ok(
  !meaningMissionBody.includes("meaningMissionBadge") && !meaningMissionBody.includes("meaningMissionHead"),
  "旧pillバッジ・ヘッダー構成（meaningMissionBadge/meaningMissionHead）は除去する必要がある",
);
assert.ok(
  !meaningMissionBody.includes('el("progress"'),
  "既存の progress 要素は削除する必要がある",
);
assert.ok(
  intervalBreakdownBody.includes("meaningMissionInterval"),
  "6セルグリッド用クラス meaningMissionInterval がJSに必要",
);
assert.ok(
  !intervalBreakdownBody.includes("meaningMissionIntervalsLabel") && !intervalBreakdownBody.includes("meaningMissionIntervalsHelp"),
  "間隔内訳は説明文付きの独立パネルではなく簡潔な連結グリッドにする必要がある",
);

// --- resume時にCTAを二次操作へ落とす ---
assert.ok(
  meaningMissionBody.includes("通常学習の続きがあるため、先に再開するのがおすすめです。"),
  "resumeあり時の案内文が必要",
);

// --- CSS ---
for (const cls of [".meaningMission ", ".meaningMissionMetrics", ".meaningMissionCta", ".meaningMissionInterval"]) {
  assert.ok(css.includes(cls), `CSSに ${cls} の規則が必要`);
}
assert.ok(
  !css.includes(".meaningMissionHead") && !css.includes(".meaningMissionBadge") && !css.includes(".meaningMissionProgress"),
  "参照されなくなった旧CSS規則（meaningMissionHead/Badge/Progress）は削除する必要がある",
);
assert.ok(
  !css.includes(".meaningMissionIntervals ") && !css.includes(".meaningMissionIntervals{") && !css.includes(".meaningMissionIntervalsLabel") && !css.includes(".meaningMissionIntervalsHelp"),
  "間隔内訳の説明パネル用CSSは削除する必要がある",
);

console.log("meaning mission UI contract: OK");
