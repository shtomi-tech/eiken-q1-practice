const LEGACY_STORE_KEY = "eiken2_q1_v1";
const STORE_PREFIX = "eiken_q1_progress_";
const DATASET_KEY = "eiken_q1_dataset";
const LEGACY_PRE1_PROGRESS_KEY = "eiken_pre1_progress_v1";
const LEGACY_PRE1_ROUND_KEY = "eiken_pre1_round";
const LEGACY_PRE1_APP_ID = "eiken-pre1";
const PRE1_MIGRATION_VERSION = 1;
const CORRUPT_PROGRESS_PREFIX = "eiken_q1_corrupt_";
const MANIFEST_URL = "data/manifest.json";
let storageStudentId = "";
function scopedStorageKey(key) {
  return storageStudentId
    ? `eiken_q1_student_${encodeURIComponent(storageStudentId)}_${key}`
    : key;
}
function datasetStorageKey() {
  return scopedStorageKey(DATASET_KEY);
}
// datasetId の級プレフィックス → 音声フォルダ名。級の判定・同一級のプール化にも使う。
// ここに無いプレフィックスは「級不明」として扱い、意味練習のプール対象から外す。
const GRADE_BY_PREFIX = { eiken1: "1", eiken2: "2", eikenp1: "pre1", eikenp2: "pre2", eiken5: "5", eikentopic: "topic", iuhw: "iuhw" };
const DATASET_ID_RE = new RegExp(`^(${Object.keys(GRADE_BY_PREFIX).join("|")})-(\\d{4}-\\d+|mock-\\d+|set-\\d+)$`);
const GRADE_KEY = "grade";
const GRADE_PREFIXES = {
  "5": ["eiken5"],
  pre2: ["eikenp2"],
  "2": ["eiken2"],
  pre1: ["eikenp1"],
  "1": ["eiken1"],
  iuhw: ["iuhw"],
};
const GRADE_CHOICE_ORDER = ["5", "pre2", "2", "pre1", "1", "iuhw"];
const GRADE_LABELS = { "5": "5級", pre2: "準2級", "2": "2級", pre1: "準1級", "1": "1級", iuhw: "医療福祉" };
const STUDY_PLAN_KEY = "eiken_q1_study_plan_v1";
const STUDY_PLAN_VERSION = 1;
const STUDY_PLAN_TARGET_VOCABULARY = 14000;
const STUDY_PLAN_BASE_VOCABULARY = 9000;
const STUDY_PLAN_VOCABULARY_PER_QUESTION = 4;
const STUDY_PLAN_FORECAST_DAYS = [7, 30, 90, 180, 365];
let studyPlan = null;
let pendingCloudStudyPlan = null;
// 級ごとの語彙目標。英検公式は必要語彙数を公表していないため、95%カバー率解析
// （ei-raku.com の推定 1,650/3,000/5,100/8,900/14,400）を生徒が扱いやすい丸い数字にした目安。
// prev は「前の級までは習得済み」という前提の起点で、累計と差分（+1,500/+2,000/+4,000/+5,000）が一致するよう丸めてある。
const VOCAB_GOALS = {
  eikenp2: { prev: 1500, target: 3000, prevLabel: "3級" },
  eiken2: { prev: 3000, target: 5000, prevLabel: "準2級" },
  eikenp1: { prev: 5000, target: 9000, prevLabel: "2級" },
  eiken1: { prev: 9000, target: 14000, prevLabel: "準1級" },
};
// 問題セット一覧は data/manifest.json（"q1"キー）から読み込む。
// 回を追加するときはデータJSONを置いてmanifest.jsonに1エントリ足すだけでよく、このファイルの編集は不要。
  let DATASETS = {};
  let ALL_DATASETS = {};
  let DEFAULT_DATASET_ID = null;
  let lemmaMap = {};
  let lemmaEntries = {};
  let flashcardLemmaMap = {};
let wordOriginMap = {};

function isValidIsoDate(value) {
  return typeof value === "string"
    && /^\d{4}-\d{2}-\d{2}T/.test(value)
    && Number.isFinite(new Date(value).getTime());
}

function normalizeStudyPlan(candidate, limit = 1) {
  const cap = Number.isInteger(limit) && limit > 0 ? limit : 1;
  const fallback = {
    version: STUDY_PLAN_VERSION,
    questionGoal: cap,
    dailyQuestionGoal: Math.min(8, cap),
    weekStartsOn: 1,
  };
  const source = candidate && typeof candidate === "object" && !Array.isArray(candidate)
    ? candidate
    : {};
  const integerInRange = (value, min, max) => Number.isInteger(value) && value >= min && value <= max;
  return {
    ...source,
    version: source.version === STUDY_PLAN_VERSION ? STUDY_PLAN_VERSION : fallback.version,
    questionGoal: integerInRange(source.questionGoal, 1, cap) ? source.questionGoal : fallback.questionGoal,
    dailyQuestionGoal: integerInRange(source.dailyQuestionGoal, 1, cap)
      ? source.dailyQuestionGoal
      : fallback.dailyQuestionGoal,
    weekStartsOn: integerInRange(source.weekStartsOn, 0, 6) ? source.weekStartsOn : fallback.weekStartsOn,
  };
}

function startOfLocalDay(date = new Date()) {
  const value = new Date(date);
  value.setHours(0, 0, 0, 0);
  return value;
}

function startOfWeek(date = new Date(), weekStartsOn = 1) {
  const day = startOfLocalDay(date);
  const start = Number.isInteger(weekStartsOn) && weekStartsOn >= 0 && weekStartsOn <= 6 ? weekStartsOn : 1;
  const distance = (day.getDay() - start + 7) % 7;
  day.setDate(day.getDate() - distance);
  return day;
}

function nextWeekStart(date = new Date(), weekStartsOn = 1) {
  const next = startOfWeek(date, weekStartsOn);
  next.setDate(next.getDate() + 7);
  return next;
}

function questionEntryId(entry) {
  return `${entry.datasetId}:${Number(entry.q)}`;
}

function answeredQuestionEntries(entries = []) {
  const unique = new Map();
  entries.forEach((entry) => {
    const unitState = entry && entry.unit;
    if (!entry || !entry.datasetId || !Number.isInteger(Number(entry.q)) || !unitState) return;
    const answered = isValidIsoDate(unitState.firstAnsweredAt)
      || Number(unitState.attempts) > 0
      || unitState.learned === true;
    if (!answered) return;
    const normalized = { ...entry, q: Number(entry.q) };
    const key = questionEntryId(normalized);
    if (!unique.has(key)) unique.set(key, normalized);
  });
  return [...unique.values()];
}

function calendarDaysUntil(start, end) {
  const cursor = new Date(start);
  let days = 0;
  while (cursor < end && days < 8) {
    days += 1;
    cursor.setDate(cursor.getDate() + 1);
  }
  return Math.max(1, days);
}

function studyPlanSummary(now = new Date(), plan = {}, entries = []) {
  const planLimit = Math.max(
    1,
    Number(plan?.questionGoal) || 1,
    Number(plan?.dailyQuestionGoal) || 1,
  );
  const safe = normalizeStudyPlan(plan, planLimit);
  const answered = answeredQuestionEntries(entries);
  const todayStart = startOfLocalDay(now);
  const tomorrowStart = new Date(todayStart);
  tomorrowStart.setDate(tomorrowStart.getDate() + 1);
  const weekStart = startOfWeek(now, safe.weekStartsOn);
  const weekEnd = nextWeekStart(now, safe.weekStartsOn);
  const inRange = (value, start, end) => {
    if (!isValidIsoDate(value)) return false;
    const timestamp = new Date(value).getTime();
    return timestamp >= start.getTime() && timestamp < end.getTime();
  };
  const answeredToday = answered.filter((entry) => inRange(entry.unit.firstAnsweredAt, todayStart, tomorrowStart)).length;
  const answeredThisWeek = answered.filter((entry) => inRange(entry.unit.firstAnsweredAt, weekStart, weekEnd)).length;
  const weeklyGoal = safe.dailyQuestionGoal * 7;
  const weeklyRemaining = Math.max(0, weeklyGoal - answeredThisWeek);
  const daysRemainingIncludingToday = calendarDaysUntil(startOfLocalDay(now), weekEnd);
  return {
    questionGoal: safe.questionGoal,
    dailyQuestionGoal: safe.dailyQuestionGoal,
    weekStartsOn: safe.weekStartsOn,
    answeredToday,
    dailyRemaining: Math.max(0, safe.dailyQuestionGoal - answeredToday),
    answeredThisWeek,
    weeklyGoal,
    weeklyRemaining,
    daysRemainingIncludingToday,
    adjustedDailyTarget: weeklyRemaining > 0 ? Math.ceil(weeklyRemaining / daysRemainingIncludingToday) : 0,
    answeredOverall: answered.length,
    overallRemaining: Math.max(0, safe.questionGoal - answered.length),
    weekStart,
    weekEnd,
  };
}

function vocabularyForecast(plan = {}) {
  const dailyVocabulary = Math.max(1, Number(plan.dailyQuestionGoal) || 1) * STUDY_PLAN_VOCABULARY_PER_QUESTION;
  return STUDY_PLAN_FORECAST_DAYS.map((days) => ({ days, vocabulary: dailyVocabulary * days }));
}

function vocabularyGoalForecast(now = new Date(), plan = {}, learnedVocabulary = 0) {
  const dailyVocabulary = Math.max(1, Number(plan.dailyQuestionGoal) || 1) * STUDY_PLAN_VOCABULARY_PER_QUESTION;
  const currentVocabulary = Math.min(
    STUDY_PLAN_TARGET_VOCABULARY,
    STUDY_PLAN_BASE_VOCABULARY + Math.max(0, Number(learnedVocabulary) || 0),
  );
  const remainingVocabulary = Math.max(0, STUDY_PLAN_TARGET_VOCABULARY - currentVocabulary);
  const daysToGoal = remainingVocabulary > 0 ? Math.ceil(remainingVocabulary / dailyVocabulary) : 0;
  const estimatedDate = startOfLocalDay(now);
  estimatedDate.setDate(estimatedDate.getDate() + daysToGoal);
  return {
    currentVocabulary,
    remainingVocabulary,
    dailyVocabulary,
    daysToGoal,
    estimatedDate,
  };
}

function migrateFirstAnsweredAt(progress) {
  if (!progress || typeof progress !== "object" || Array.isArray(progress)) return false;
  if (progress.migrations?.studyPlanFirstAnsweredAtV1 === 1) return false;
  const firstByQuestion = new Map();
  (Array.isArray(progress.history) ? progress.history : []).forEach((event) => {
    if (!event || event.kind !== "question" || !Number.isInteger(Number(event.q)) || !isValidIsoDate(event.at)) return;
    const q = Number(event.q);
    const current = firstByQuestion.get(q);
    if (!current || new Date(event.at).getTime() < new Date(current).getTime()) firstByQuestion.set(q, event.at);
  });
  if (!progress.units || typeof progress.units !== "object" || Array.isArray(progress.units)) progress.units = {};
  Object.entries(progress.units).forEach(([q, unitState]) => {
    if (!unitState || typeof unitState !== "object" || isValidIsoDate(unitState.firstAnsweredAt)) return;
    const firstAnsweredAt = firstByQuestion.get(Number(q));
    if (firstAnsweredAt) unitState.firstAnsweredAt = firstAnsweredAt;
  });
  progress.migrations = {
    ...(progress.migrations || {}),
    studyPlanFirstAnsweredAtV1: 1,
  };
  return true;
}

async function loadManifest() {
  const manifest = await fetch(MANIFEST_URL, { cache: "no-store" }).then((r) => r.json());
  ALL_DATASETS = manifest.q1;
  DATASETS = ALL_DATASETS;
  DEFAULT_DATASET_ID = manifest.defaultDatasetId;
}

async function loadWordOriginData() {
  wordOriginMap = {};
  try {
    const response = await fetch("data/word_origins.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`word_origins.json: HTTP ${response.status}`);
    const data = await response.json();
    if (data && data.origins && typeof data.origins === "object" && !Array.isArray(data.origins)) {
      wordOriginMap = Object.fromEntries(
        Object.entries(data.origins).map(([lemma, origin]) => [String(lemma).toLowerCase(), origin]),
      );
    }
  } catch (e) {
    // 語源辞書が未配信でも、通常の単語カードはそのまま使える。
  }
}

function applyGradeScope(gradeCode) {
  const prefixes = GRADE_PREFIXES[gradeCode];
  if (!prefixes) return false;
  const source = Object.keys(ALL_DATASETS).length ? ALL_DATASETS : DATASETS;
  const scoped = Object.fromEntries(
    Object.entries(source).filter(([id]) => prefixes.includes(gradeOf(id))),
  );
  if (!Object.keys(scoped).length) return false;
  DATASETS = scoped;
  if (!DATASETS[DEFAULT_DATASET_ID]) DEFAULT_DATASET_ID = Object.keys(DATASETS)[0];
  return true;
}

function resolveGradeCode() {
  const fromUrl = new URLSearchParams(window.location.search).get("g") || "";
  if (GRADE_PREFIXES[fromUrl]) {
    writeStored(scopedStorageKey(GRADE_KEY), fromUrl);
    return fromUrl;
  }
  try {
    const saved = localStorage.getItem(scopedStorageKey(GRADE_KEY));
    if (GRADE_PREFIXES[saved]) return saved;
  } catch (e) { /* ignore */ }
  return "";
}

function availableDatasets() {
  return Object.entries(DATASETS);
}
function defaultDatasetId() {
  return DEFAULT_DATASET_ID;
}
// 選択肢を描画した直後、この時間だけクリックを無視する（誤ダブルクリック防止）
const CHOICE_GUARD_MS = 400;
const FLASH_NAV_GUARD_MS = 450;

const state = {
  datasetId: null, // loadManifest() 完了後、boot() 内で loadDatasetId() により確定する
  itemsByQ: {},   // q -> [item, ...]
  questions: {},  // q -> {stem, choices, answerIndex, translation}
  qList: [],      // [1..n]
  meaningPool: { word: [], idiom: [] }, // ダミー用の意味プール
  progress: { units: {} },
};

const RESUME_STAGE_RULES = {
  learn: ["flash", "check", "practice", "done"],
  meaning: ["check", "meaningReview", "done"],
  final: ["check", "done"],
};
const RESUMABLE_MODES = new Set(Object.keys(RESUME_STAGE_RULES));
let resumeRecoveryMessage = "";
let resumeUnavailable = false;
let needsGradeChoice = false;

function resumeStageAllowed(mode, stage) {
  return Boolean(RESUME_STAGE_RULES[mode]?.includes(stage));
}
