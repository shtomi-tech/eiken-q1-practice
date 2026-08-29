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
const renderHomeBody = extractFunctionBody(js, "renderHomeContent");
const meaningWrongReviewBody = extractFunctionBody(js, "renderMeaningWrongReview");

// --- ホーム上のカード境界とCTA所属 ---
assert.ok(
  !renderHomeBody.includes("summary.appendChild(meaningMission("),
  "間隔復習カードは通常学習カードへ入れ子にしない必要がある",
);
assert.match(
  renderHomeBody,
  /home\.appendChild\(meaningMission\(/,
  "間隔復習カードはホーム直下へ追加する必要がある",
);
assert.ok(
  !renderHomeBody.includes("startMeaningPractice(true, meaningQueue)"),
  "通常学習カードのprimary CTAから意味復習を直接開始してはいけない",
);
assert.match(
  renderHomeBody,
  /const resumeIsDone = resume\?\.stage === "done";/,
  "完了済みresumeは途中再開の表示対象から除外する必要がある",
);
assert.match(
  renderHomeBody,
  /const meaningResume = resume\?\.mode === "meaning" && !resumeIsDone;/,
  "meaning resumeはmodeで判定する必要がある",
);
assert.match(
  renderHomeBody,
  /const coreResume = Boolean\(resume && resume\.mode !== "meaning" && !resumeIsDone\);/,
  "通常学習resumeはmeaning以外として判定する必要がある",
);
assert.ok(
  renderHomeBody.includes("if (coreResume)"),
  "通常学習カードはcore resumeだけを表示対象にする必要がある",
);
assert.ok(
  !renderHomeBody.includes('why: "前回保存した位置から再開します。"'),
  "途中保存CTAの補足文は表示しない必要がある",
);
assert.ok(
  !renderHomeBody.includes('class: "missionNote"'),
  "最終チェック解放までの案内はホームに表示しない必要がある",
);
assert.ok(
  !renderHomeBody.includes("progressDetails"),
  "進捗の詳細ブロックはホームに表示しない必要がある",
);
assert.ok(
  !renderHomeBody.includes("recentLearningHistory()"),
  "最近の学習履歴ブロックはホームに表示しない必要がある",
);
assert.match(
  renderHomeBody,
  /meaningMission\([^;]*meaningResume[^;]*coreResume/s,
  "間隔復習カードへmeaning/coreのresume所属を渡す必要がある",
);
assert.ok(
  meaningMissionBody.includes('class: "card spacedReviewCard"'),
  "間隔復習カードのルートはcardとspacedReviewCardを持つ必要がある",
);
assert.ok(
  meaningMissionBody.includes('"aria-labelledby": "spacedReviewCardTitle"'),
  "間隔復習カードは見出しとaria-labelledbyで関連付ける必要がある",
);
assert.ok(
  meaningMissionBody.includes('id: "spacedReviewCardTitle"'),
  "間隔復習カードの見出しに一意なidが必要である",
);
assert.ok(
  meaningMissionBody.includes("restoreSession()") && meaningMissionBody.includes("意味だけ復習の続きを再開する"),
  "意味復習resumeは間隔復習カードから再開する必要がある",
);

// --- ラベル・見出し ---
assert.ok(meaningMissionBody.includes("間隔復習"), "meaningMission() は「間隔復習」ラベルを描画する必要がある");
assert.ok(meaningMissionBody.includes("意味だけ復習"), "meaningMission() は「意味だけ復習」見出しを描画する必要がある");
assert.ok(!meaningMissionBody.includes("中心学習"), "旧ラベル「中心学習」は meaningMission() から除去済みである必要がある");

// --- 意味だけ復習の誤答見直し ---
assert.ok(js.includes('meaning: ["check", "meaningReview", "done"]') && js.includes('return "meaningReview"'), "意味復習の誤答時に見直しstageへ遷移できる必要がある");
assert.ok(meaningWrongReviewBody.includes("buildFlashCard"), "誤答した単語・熟語を暗記カードで見直せる必要がある");
assert.ok(meaningWrongReviewBody.includes("すべて確認すると結果へ"), "全件確認後に結果へ進む導線が必要");
assert.ok(meaningWrongReviewBody.includes("saveResume"), "誤答語句の確認状態を途中保存する必要がある");

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

// --- 他の級の復習待ち ---
const otherGradeDueBody = extractFunctionBody(js, "otherGradeDueCounts");
assert.ok(
  !otherGradeDueBody.includes("fetch(") && !otherGradeDueBody.includes("loadPooledItems"),
  "他の級の復習待ち件数は語彙JSONを読まず進捗だけで数える必要がある",
);
assert.ok(
  meaningMissionBody.includes("otherGradeDueCounts()") && meaningMissionBody.includes("meaningMissionOtherGradeList"),
  "間隔復習カードは他の級の復習待ちを表示する必要がある",
);
assert.match(
  meaningMissionBody,
  /switchDataset\(row\.datasetId\)/,
  "他の級のチップはその級のセットへ移動する必要がある",
);
assert.ok(
  meaningMissionBody.includes("dataset().shortLabel"),
  "間隔復習カードの見出しはどの級のプールかを示す必要がある",
);

// --- CSS ---
for (const cls of [".spacedReviewCard", ".meaningMissionMetrics", ".meaningMissionCta", ".meaningMissionInterval", ".meaningMissionOtherGrade", ".meaningWrongReview", ".meaningReviewCheckBtn"]) {
  assert.ok(css.includes(cls), `CSSに ${cls} の規則が必要`);
}
assert.ok(!css.includes(".meaningMission {"), "旧入れ子パネル用のmeaningMissionルート規則は削除する必要がある");
assert.ok(
  !css.includes(".meaningMissionHead") && !css.includes(".meaningMissionBadge") && !css.includes(".meaningMissionProgress"),
  "参照されなくなった旧CSS規則（meaningMissionHead/Badge/Progress）は削除する必要がある",
);
assert.ok(
  !css.includes(".meaningMissionIntervals ") && !css.includes(".meaningMissionIntervals{") && !css.includes(".meaningMissionIntervalsLabel") && !css.includes(".meaningMissionIntervalsHelp"),
  "間隔内訳の説明パネル用CSSは削除する必要がある",
);

console.log("meaning mission UI contract: OK");
