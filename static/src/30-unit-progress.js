/* ---- 語句単位の進捗（意味だけ練習でのみ使用。既存の units とは別ブロック） ---- */
const LEITNER_LADDER = [1, 3, 7, 14, 30, 60, 120]; // 正解のたびに進む復習間隔（日）
// FSRSは連続値の間隔を返すため、内訳はバケットで数える（上限 days 未満に入る）。
const MEANING_INTERVALS = [
  { label: "未実施" },
  { label: "要再確認" },
  { days: 3, label: "3日以内" },
  { days: 7, label: "1週間" },
  { days: 14, label: "2週間" },
  { days: 30, label: "1か月" },
  { days: 90, label: "3か月" },
  { days: Infinity, label: "半年以上" },
];
const MEANING_SESSION_SIZE = 30; // 1回に出す語句の上限
const MEANING_PROGRESS_VERSION = 3;

/* ---- FSRS-6（static/vendor/fsrs の ts-fsrs UMD, グローバル名 FSRS） ----
   間隔は語ごとの stability / difficulty から算出する。LEITNER_LADDER は
   ライブラリが読み込めなかったときのフォールバックとしてのみ残す。 */
const FSRS_PARAMS = Object.freeze({
  request_retention: 0.9,  // 目標保持率。Ankiの既定と同じ
  maximum_interval: 180,   // 英検受験という用途に合わせて短縮（既定36500日は使わない）
  enable_short_term: true, // 1m/10m の当日ステップを使う
  enable_fuzz: true,       // 同じ日に大量の語が固まるのを防ぐ（乱数を含む）
});
// ts-fsrs の Rating。Easy(4) は自己申告UIが無く根拠を作れないため使わない。
const FSRS_RATING = Object.freeze({ again: 1, hard: 2, good: 3 });
const FSRS_MAX_SCHEDULED_DAYS = FSRS_PARAMS.maximum_interval + 1; // 丸めで上限+1になる
let fsrsSchedulerCache = null;

function fsrsLib() {
  return (typeof globalThis !== "undefined" && globalThis.FSRS) || null;
}
// ライブラリ未読込（配信漏れ・ネットワーク失敗）でも学習は止めない。呼び出し側がフォールバックする。
function fsrsScheduler() {
  const lib = fsrsLib();
  if (!lib) return null;
  if (!fsrsSchedulerCache) fsrsSchedulerCache = lib.fsrs(FSRS_PARAMS);
  return fsrsSchedulerCache;
}
function fsrsDate(value, fallback) {
  const time = value ? new Date(value).getTime() : NaN;
  return Number.isFinite(time) ? new Date(time) : fallback;
}
function fsrsNumber(value, fallback) {
  return Number.isFinite(Number(value)) ? Number(value) : fallback;
}
// 保存形式(JSON) → ts-fsrs の Card。日付を Date へ戻すのはこの関数だけ。
function toFsrsCard(saved, now) {
  const lib = fsrsLib();
  if (!lib) return null;
  const empty = lib.createEmptyCard(now);
  if (!saved || typeof saved !== "object") return empty;
  return {
    ...empty,
    due: fsrsDate(saved.due, empty.due),
    stability: fsrsNumber(saved.stability, empty.stability),
    difficulty: fsrsNumber(saved.difficulty, empty.difficulty),
    elapsed_days: fsrsNumber(saved.elapsed_days, empty.elapsed_days),
    scheduled_days: fsrsNumber(saved.scheduled_days, empty.scheduled_days),
    reps: fsrsNumber(saved.reps, empty.reps),
    lapses: fsrsNumber(saved.lapses, empty.lapses),
    // 当日ステップの何段目かを保持する。落とすと Learning から抜けられなくなる。
    learning_steps: fsrsNumber(saved.learning_steps, empty.learning_steps),
    state: fsrsNumber(saved.state, empty.state),
    last_review: saved.last_review ? fsrsDate(saved.last_review, null) : undefined,
  };
}
// ts-fsrs の Card → 保存形式(JSON)。日付を ISO 文字列にするのはこの関数だけ。
function fromFsrsCard(card) {
  return {
    due: new Date(card.due).toISOString(),
    stability: card.stability,
    difficulty: card.difficulty,
    elapsed_days: card.elapsed_days,
    scheduled_days: card.scheduled_days,
    reps: card.reps,
    lapses: card.lapses,
    learning_steps: card.learning_steps,
    state: card.state,
    last_review: card.last_review ? new Date(card.last_review).toISOString() : null,
  };
}
// 正誤と回答時間の判定を ts-fsrs の Rating へ写す。
function meaningRating(isCorrect, grade) {
  if (!isCorrect) return FSRS_RATING.again;
  return grade === "hard" ? FSRS_RATING.hard : FSRS_RATING.good;
}
const LEARNING_HISTORY_LIMIT = 500;
// ponytail: 閾値はこの4つだけ。初期値は実データを見て調整する前提。
const RT_HARD_FLOOR_MS = 8000;
const RT_HARD_CEIL_MS = 20000;
const RT_HARD_RATIO = 1.6;
const RT_OUTLIER_MS = 60000;
const DEFAULT_ITEM_STATE = Object.freeze({
  wrongCount: 0,
  leitnerStage: 0,
  nextReviewAt: null,
  lastAnsweredAt: null,
  lastMs: null,
  avgMs: null,
  fsrs: null,
});

function rtGrade(ms, medianMs) {
  if (!Number.isFinite(ms)) return "good";
  if (ms >= RT_HARD_CEIL_MS) return "hard";
  if (ms < RT_HARD_FLOOR_MS) return "good";
  const baseline = Number.isFinite(medianMs) ? medianMs : RT_HARD_FLOOR_MS;
  return ms > RT_HARD_RATIO * baseline ? "hard" : "good";
}

function medianMs(values) {
  const valid = values.filter((value) => Number.isFinite(value) && value >= 0 && value < RT_OUTLIER_MS).sort((a, b) => a - b);
  if (valid.length < 5) return RT_HARD_FLOOR_MS;
  const middle = Math.floor(valid.length / 2);
  return valid.length % 2 ? valid[middle] : (valid[middle - 1] + valid[middle]) / 2;
}

// FSRS未読込時のフォールバック。通常の間隔算出には使わない。
function meaningResultState(stage, wrongCount, isCorrect, grade) {
  const lastStage = LEITNER_LADDER.length - 1;
  const maxStage = Number(wrongCount) >= 5 ? 1 : lastStage;
  const currentStage = Math.min(Math.max(Number(stage) || 0, 0), maxStage);
  if (!isCorrect) return { intervalDays: null, nextStage: 0 };
  return {
    intervalDays: LEITNER_LADDER[currentStage],
    nextStage: grade === "hard" ? currentStage : Math.min(currentStage + 1, maxStage),
  };
}

function nextAverageMs(previousMs, ms) {
  return Number.isFinite(previousMs) ? Math.round(previousMs * 0.7 + ms * 0.3) : ms;
}

function itemKeyOf(item) {
  const stableKey = item?.itemKey || surfaceOf(item);
  return `${item.type}:${String(stableKey || "").toLowerCase()}`;
}
// 読み取り専用。フィルタ/ソート/件数計算で使う（生成しない＝localStorageを汚さない）。
function readItemState(progress, key) {
  return (progress.items && progress.items[key]) || DEFAULT_ITEM_STATE;
}
// 破壊的。解答を記録する一箇所だけで使う。
function itemState(progress, key) {
  if (!progress.items) progress.items = {};
  if (!progress.items[key]) progress.items[key] = {};
  const s = progress.items[key];
  if (typeof s.wrongCount !== "number") s.wrongCount = 0;
  if (typeof s.leitnerStage !== "number") s.leitnerStage = 0;
  if (typeof s.nextReviewAt !== "string" && s.nextReviewAt !== null) s.nextReviewAt = null;
  if (typeof s.lastAnsweredAt !== "string" && s.lastAnsweredAt !== null) s.lastAnsweredAt = null;
  if (!Number.isFinite(s.lastMs)) s.lastMs = null;
  if (!Number.isFinite(s.avgMs)) s.avgMs = null;
  if (!s.fsrs || typeof s.fsrs !== "object") s.fsrs = null;
  return s;
}
function appendLearningHistory(progress, event) {
  if (!Array.isArray(progress.history)) progress.history = [];
  progress.history.push({ at: new Date().toISOString(), ...event });
  if (progress.history.length > LEARNING_HISTORY_LIMIT) {
    progress.history.splice(0, progress.history.length - LEARNING_HISTORY_LIMIT);
  }
}
// FSRSで次回を決める。ライブラリが無い場合は false を返し、呼び出し側がはしごへ落ちる。
function applyFsrsResult(s, answeredAt, rating) {
  const scheduler = fsrsScheduler();
  if (!scheduler) return false;
  const next = scheduler.next(toFsrsCard(s.fsrs, answeredAt), answeredAt, rating).card;
  s.fsrs = fromFsrsCard(next);
  // nextReviewAt は due の写し。期限判定・他級集計・クラウド同期はこの値だけを見る。
  s.nextReviewAt = s.fsrs.due;
  return true;
}
// FSRS未読込時のみ使う旧はしご。leitnerStage はここでだけ進む。
function applyLadderResult(s, answeredAt, isCorrect, grade) {
  const result = meaningResultState(s.leitnerStage, s.wrongCount, isCorrect, grade);
  s.leitnerStage = result.nextStage;
  if (result.intervalDays === null) {
    s.nextReviewAt = null;
    return;
  }
  const next = new Date(answeredAt);
  next.setDate(next.getDate() + result.intervalDays);
  s.nextReviewAt = next.toISOString();
}
// 意味だけ演習の解答結果を進捗へ反映する。item._datasetId があれば本来の回の進捗へ書く。
function recordMeaningResult(item, isCorrect, responseMs) {
  const datasetId = item._datasetId || state.datasetId;
  const progress = progressFor(datasetId);
  const s = itemState(progress, itemKeyOf(item));
  const answeredAt = new Date();
  const ms = Number.isFinite(responseMs) ? responseMs : null;
  s.lastAnsweredAt = answeredAt.toISOString();
  // 誤答は Again。正答は回答時間の判定で Hard / Good に分ける。
  const grade = isCorrect ? rtGrade(ms, medianMs(session?.meaningRtLog || [])) : "good";
  if (!applyFsrsResult(s, answeredAt, meaningRating(isCorrect, grade))) {
    applyLadderResult(s, answeredAt, isCorrect, grade);
  }
  if (isCorrect) {
    if (ms !== null) {
      // lastMs/avgMs は正答時だけ更新する。誤答は wrongCount と即時再出題で既に重みが付くため。
      s.lastMs = ms;
      s.avgMs = nextAverageMs(s.avgMs, ms);
      if (ms < RT_OUTLIER_MS) (session.meaningRtLog || (session.meaningRtLog = [])).push(ms);
    }
  } else {
    // wrongCount は出題順のフォールバックと移行時のdifficulty推定に使うため維持する。
    s.wrongCount += 1;
  }
  appendLearningHistory(progress, {
    kind: "meaning",
    type: item.type,
    surface: surfaceOf(item),
    result: isCorrect ? "correct" : "wrong",
  });
  saveProgressFor(datasetId, progress);
}

const FINAL_PASS_RATE = 0.8;

function finalPassScore(finalTotal) {
  return Math.ceil(finalTotal * FINAL_PASS_RATE);
}

function finalProgress(finalTotal) {
  if (!state.progress.finalCheck) state.progress.finalCheck = {};
  const f = state.progress.finalCheck;
  if (typeof f.bestScore !== "number") f.bestScore = 0;
  if (typeof f.lastScore !== "number") f.lastScore = 0;
  if (typeof f.cleared !== "boolean") f.cleared = false;
  let changed = false;
  if (typeof finalTotal === "number" && typeof f.bestTotal !== "number") {
    f.bestTotal = f.cleared ? f.bestScore : finalTotal;
    changed = true;
  }
  // 語彙データが後から増減した場合、以前のCLEAR判定をそのまま引き継がない。
  if (f.cleared && typeof finalTotal === "number" && f.bestTotal !== finalTotal) {
    f.cleared = false;
    changed = true;
  }
  if (!f.cleared && typeof finalTotal === "number"
    && f.bestTotal === finalTotal && f.bestScore >= finalPassScore(finalTotal)) {
    f.cleared = true;
    f.clearedAt = f.clearedAt || new Date().toISOString();
    changed = true;
  }
  if (changed) {
    saveProgress();
  }
  return f;
}

