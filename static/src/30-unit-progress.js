/* ---- 語句単位の進捗（意味だけ練習でのみ使用。既存の units とは別ブロック） ---- */
const LEITNER_LADDER = [1, 3, 7, 14]; // 正解のたびに進む復習間隔（日）
const MEANING_INTERVALS = [
  { label: "未実施" },
  { label: "要再確認" },
  { days: 1, label: "1日後" },
  { days: 3, label: "3日後" },
  { days: 7, label: "7日後" },
  { days: 14, label: "14日後" },
];
const MEANING_SESSION_SIZE = 30; // 1回に出す語句の上限
const MEANING_PROGRESS_VERSION = 2;
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
  return s;
}
function appendLearningHistory(progress, event) {
  if (!Array.isArray(progress.history)) progress.history = [];
  progress.history.push({ at: new Date().toISOString(), ...event });
  if (progress.history.length > LEARNING_HISTORY_LIMIT) {
    progress.history.splice(0, progress.history.length - LEARNING_HISTORY_LIMIT);
  }
}
// 意味だけ演習の解答結果をLeitnerに反映する。item._datasetId があれば本来の回の進捗へ書く。
function recordMeaningResult(item, isCorrect, responseMs) {
  const datasetId = item._datasetId || state.datasetId;
  const progress = progressFor(datasetId);
  const s = itemState(progress, itemKeyOf(item));
  const answeredAt = new Date();
  const ms = Number.isFinite(responseMs) ? responseMs : null;
  s.lastAnsweredAt = answeredAt.toISOString();
  if (isCorrect) {
    const grade = rtGrade(ms, medianMs(session?.meaningRtLog || []));
    const result = meaningResultState(s.leitnerStage, s.wrongCount, true, grade);
    const next = new Date(answeredAt);
    next.setDate(next.getDate() + result.intervalDays);
    s.nextReviewAt = next.toISOString();
    s.leitnerStage = result.nextStage;
    if (ms !== null) {
      // lastMs/avgMs は正答時だけ更新する。誤答は wrongCount と即時再出題で既に重みが付くため。
      s.lastMs = ms;
      s.avgMs = nextAverageMs(s.avgMs, ms);
      if (ms < RT_OUTLIER_MS) (session.meaningRtLog || (session.meaningRtLog = [])).push(ms);
    }
  } else {
    s.wrongCount += 1;
    s.leitnerStage = meaningResultState(s.leitnerStage, s.wrongCount, false, "good").nextStage;
    s.nextReviewAt = null;
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

