// 間隔復習のスケジューラ契約（FSRS-6）と、旧はしごからの移行を検証する。
//
// enable_fuzz が有効なため日数は乱数を含む。完全一致ではなく範囲で判定すること。
const assert = require("node:assert/strict");
const path = require("node:path");
const vm = require("node:vm");
const { appJsWithTestExports } = require("./lib/app-source.cjs");

const VENDOR = path.resolve(__dirname, "..", "static", "vendor", "fsrs", "index.umd.js");
const EXPORTS = "{ FSRS_PARAMS, FSRS_RATING, FSRS_MAX_SCHEDULED_DAYS, meaningRating, toFsrsCard, fromFsrsCard, applyFsrsResult, applyLadderResult, migrateFsrsV1, MEANING_INTERVALS, meaningIntervalBucket }";

// FSRS を読み込んだ環境 / 読み込めなかった環境で、それぞれ別コンテキストを作る。
function load({ withFsrs }) {
  const sandbox = withFsrs ? { FSRS: require(VENDOR) } : {};
  vm.runInNewContext(`${appJsWithTestExports(EXPORTS)}\nglobalThis.app = EikenQ1App;`, sandbox);
  return sandbox.app.__test;
}

const app = load({ withFsrs: true });
const DAY = 24 * 60 * 60 * 1000;
const intervalDays = (state, from) => (new Date(state.nextReviewAt).getTime() - from.getTime()) / DAY;

// --- パラメータ ---
assert.equal(app.FSRS_PARAMS.request_retention, 0.9, "目標保持率は0.9");
assert.equal(app.FSRS_PARAMS.maximum_interval, 180, "上限間隔は180日（英検という用途に合わせる）");
assert.equal(app.FSRS_PARAMS.enable_short_term, true, "当日ステップ（1m/10m）を使う");
assert.equal(app.FSRS_PARAMS.enable_fuzz, true, "同日への集中を避けるためfuzzを使う");

// --- Rating写像。Easy(4) は根拠が作れないため使わない ---
assert.equal(app.meaningRating(false, "good"), app.FSRS_RATING.again, "誤答は Again");
assert.equal(app.meaningRating(false, "hard"), app.FSRS_RATING.again, "誤答は回答時間によらず Again");
assert.equal(app.meaningRating(true, "hard"), app.FSRS_RATING.hard, "遅い正答は Hard");
assert.equal(app.meaningRating(true, "good"), app.FSRS_RATING.good, "速い正答は Good");
assert.deepEqual(Object.values(app.FSRS_RATING).sort(), [1, 2, 3], "Easy(4)/Manual(0) は使わない");

// --- 正答の初回は当日ステップ（10分後）へ入る ---
const now = new Date("2026-04-01T09:00:00.000Z");
const fresh = { fsrs: null, nextReviewAt: null };
assert.equal(app.applyFsrsResult(fresh, now, app.FSRS_RATING.good), true, "FSRSが有効なら true を返す");
assert.equal(fresh.nextReviewAt, fresh.fsrs.due, "nextReviewAt は due の写しである必要がある");
assert.equal(fresh.fsrs.state, 1, "初回正答は Learning へ入る");
assert.ok(intervalDays(fresh, now) < 1, "初回正答の次回は当日中（学習ステップ）");

// --- Good を重ねると間隔が伸び、上限で頭打ちになる ---
const grown = { fsrs: null, nextReviewAt: null };
let at = new Date(now);
const seen = [];
for (let i = 0; i < 12; i += 1) {
  app.applyFsrsResult(grown, at, app.FSRS_RATING.good);
  seen.push(grown.fsrs.scheduled_days);
  at = new Date(grown.fsrs.due);
}
assert.ok(grown.fsrs.state === 2, "Good を重ねた語は Review 状態になる");
assert.ok(seen[3] > seen[1], `間隔は単調に伸びる必要がある: ${seen.join(",")}`);
assert.ok(
  seen.every((days) => days <= app.FSRS_MAX_SCHEDULED_DAYS),
  `scheduled_days は上限${app.FSRS_MAX_SCHEDULED_DAYS}日を超えない: ${seen.join(",")}`,
);
assert.ok(seen.at(-1) >= 120, `十分に正解を重ねれば長期間隔へ到達する: ${seen.join(",")}`);

// --- 遅い正答(Hard)は速い正答(Good)より短い ---
const base = { fsrs: null, nextReviewAt: null };
let baseAt = new Date(now);
for (let i = 0; i < 4; i += 1) {
  app.applyFsrsResult(base, baseAt, app.FSRS_RATING.good);
  baseAt = new Date(base.fsrs.due);
}
const asHard = { fsrs: { ...base.fsrs }, nextReviewAt: base.nextReviewAt };
const asGood = { fsrs: { ...base.fsrs }, nextReviewAt: base.nextReviewAt };
app.applyFsrsResult(asHard, baseAt, app.FSRS_RATING.hard);
app.applyFsrsResult(asGood, baseAt, app.FSRS_RATING.good);
assert.ok(
  asHard.fsrs.scheduled_days < asGood.fsrs.scheduled_days,
  `Hard は Good より短い間隔になる必要がある（${asHard.fsrs.scheduled_days} < ${asGood.fsrs.scheduled_days}）`,
);

// --- 誤答は Relearning へ落ち、lapses が増え、安定性が下がる ---
const lapsed = { fsrs: { ...base.fsrs }, nextReviewAt: base.nextReviewAt };
const stabilityBefore = base.fsrs.stability;
const lapsesBefore = base.fsrs.lapses;
app.applyFsrsResult(lapsed, baseAt, app.FSRS_RATING.again);
assert.equal(lapsed.fsrs.state, 3, "誤答した成熟語は Relearning へ入る");
assert.equal(lapsed.fsrs.lapses, lapsesBefore + 1, "誤答で lapses が増える");
assert.ok(lapsed.fsrs.stability < stabilityBefore, "誤答で安定性が下がる");
assert.ok(intervalDays(lapsed, baseAt) < 1, "誤答直後は当日中に戻す");

// --- 保存形式は JSON へ載る（Dateを残さない） ---
assert.equal(typeof lapsed.fsrs.due, "string", "due はISO文字列で保存する");
assert.equal(typeof lapsed.fsrs.last_review, "string", "last_review はISO文字列で保存する");
// vm コンテキスト間の比較になるため、prototype を見る deepEqual ではなく文字列で突き合わせる。
assert.equal(
  JSON.stringify(JSON.parse(JSON.stringify(lapsed.fsrs))),
  JSON.stringify(lapsed.fsrs),
  "保存形式は JSON 往復で変化しない必要がある",
);
for (const key of ["due", "stability", "difficulty", "scheduled_days", "reps", "lapses", "learning_steps", "state", "last_review"]) {
  assert.ok(key in lapsed.fsrs, `保存形式に ${key} を含める必要がある`);
}
// 文字列で保存した状態から復元できる
const restored = app.toFsrsCard(JSON.parse(JSON.stringify(lapsed.fsrs)), now);
// realm をまたぐため instanceof は使えない。Date として振る舞うかで見る。
const isDate = (value) => !!value && typeof value.getTime === "function" && Number.isFinite(value.getTime());
assert.ok(isDate(restored.due), "toFsrsCard は due を Date へ戻す必要がある");
assert.equal(restored.stability, lapsed.fsrs.stability, "復元で安定性が失われない");

// --- 壊れた記録でも例外を投げない ---
for (const broken of [null, undefined, {}, { due: "x", stability: "y" }]) {
  const card = app.toFsrsCard(broken, now);
  assert.ok(isDate(card.due), "壊れた記録は空カードとして扱う");
  assert.ok(Number.isFinite(card.stability), "壊れた記録から NaN を作らない");
}

// --- 移行（§2.6）: 冪等・nextReviewAt不変 ---
const legacy = {
  units: {},
  items: {
    "word:alpha": { leitnerStage: 4, wrongCount: 2, lastAnsweredAt: "2026-03-01T00:00:00.000Z", nextReviewAt: "2026-03-15T00:00:00.000Z" },
    "word:beta": { leitnerStage: 0, wrongCount: 7, lastAnsweredAt: "2026-03-02T00:00:00.000Z", nextReviewAt: null },
    "word:gamma": { leitnerStage: 6, wrongCount: 0, lastAnsweredAt: "2026-02-01T00:00:00.000Z", nextReviewAt: "2026-04-02T00:00:00.000Z" },
    "word:delta": {},
  },
};
const before = JSON.stringify(Object.fromEntries(
  Object.entries(legacy.items).map(([k, v]) => [k, v.nextReviewAt ?? null]),
));
assert.equal(app.migrateFsrsV1(legacy), true, "未移行の進捗は移行される");
assert.equal(legacy.migrations.fsrsV1, 1, "移行済みマークを残す");
const after = JSON.stringify(Object.fromEntries(
  Object.entries(legacy.items).map(([k, v]) => [k, v.nextReviewAt ?? null]),
));
assert.equal(after, before, "移行で nextReviewAt を書き換えてはいけない");
assert.equal(legacy.items["word:alpha"].fsrs.stability, 14, "leitnerStage 4 は 14日相当の安定性");
assert.equal(legacy.items["word:alpha"].fsrs.difficulty, 7, "difficulty は 5 + wrongCount");
assert.equal(legacy.items["word:alpha"].fsrs.lapses, 2, "lapses は wrongCount を引き継ぐ");
assert.equal(legacy.items["word:alpha"].fsrs.state, 2, "到達済みの語は Review 状態で移行する");
assert.equal(legacy.items["word:alpha"].fsrs.due, "2026-03-15T00:00:00.000Z", "due は既存の nextReviewAt と一致する");
assert.equal(legacy.items["word:gamma"].fsrs.stability, 60, "leitnerStage 6 は 60日相当の安定性");
assert.equal(legacy.items["word:beta"].fsrs.state, 0, "stage 0 は New のまま移行する");
assert.equal(legacy.items["word:delta"].fsrs.state, 0, "空の記録も New として移行する");
assert.ok(legacy.items["word:beta"].fsrs.difficulty <= 10, "difficulty は 10 を超えない");
assert.equal(legacy.items["word:alpha"].leitnerStage, 4, "ロールバック用に leitnerStage を残す");

const snapshot = JSON.stringify(legacy);
assert.equal(app.migrateFsrsV1(legacy), false, "移行は冪等（2回目は何もしない）");
assert.equal(JSON.stringify(legacy), snapshot, "2回目の移行で内容が変わってはいけない");

// --- 内訳バケット（FSRSは連続値を返すため上限未満で数える） ---
const intervals = Array.from(app.MEANING_INTERVALS);
assert.equal(
  intervals.map((entry) => entry.label).join(","),
  ["未実施", "要再確認", "3日以内", "1週間", "2週間", "1か月", "3か月", "半年以上"].join(","),
  "内訳は8バケット",
);
// 境界は「以下」。移行直後の記録はちょうど 1/3/7/14/30/60 日になるため、
// 「未満」だと14日の語が「1か月」に落ちる（実際に一度そうなった）。
assert.equal(app.meaningIntervalBucket(1), "3日以内", "1日はちょうど下限でも3日以内");
assert.equal(app.meaningIntervalBucket(3), "3日以内", "ちょうど3日は3日以内");
assert.equal(app.meaningIntervalBucket(3.5), "1週間", "3日超は1週間バケット");
assert.equal(app.meaningIntervalBucket(7), "1週間", "ちょうど7日は1週間");
assert.equal(app.meaningIntervalBucket(14), "2週間", "ちょうど14日は2週間（1か月に落とさない）");
assert.equal(app.meaningIntervalBucket(30), "1か月", "ちょうど30日は1か月");
assert.equal(app.meaningIntervalBucket(60), "3か月", "60日は3か月バケット");
assert.equal(app.meaningIntervalBucket(90), "3か月", "ちょうど90日は3か月");
assert.equal(app.meaningIntervalBucket(181), "半年以上", "上限付近は半年以上");
assert.equal(app.meaningIntervalBucket(0.5), "要再確認", "当日中は要再確認");
assert.equal(app.meaningIntervalBucket(NaN), "要再確認", "数値にならない間隔は要再確認");

const bounds = intervals.filter((entry) => entry.days !== undefined).map((entry) => entry.days);
assert.equal(
  bounds.join(","),
  [...bounds].sort((a, b) => a - b).join(","),
  "バケットの上限は昇順である必要がある",
);

// --- FSRSが読み込めない環境（配信漏れ・ネットワーク失敗）でも学習を止めない ---
const offline = load({ withFsrs: false });
const fallback = { fsrs: null, nextReviewAt: null, leitnerStage: 0, wrongCount: 0 };
assert.equal(
  offline.applyFsrsResult(fallback, now, offline.FSRS_RATING.good),
  false,
  "FSRS未読込なら applyFsrsResult は false を返す必要がある",
);
offline.applyLadderResult(fallback, now, true, "good");
assert.equal(intervalDays(fallback, now), 1, "フォールバックは旧はしご（初回1日）で動く");
assert.equal(fallback.leitnerStage, 1, "フォールバック時は leitnerStage が進む");
assert.equal(offline.migrateFsrsV1({ units: {}, items: {} }), false, "FSRS未読込なら移行しない（次回やり直す）");

console.log("fsrs schedule contract: OK");
