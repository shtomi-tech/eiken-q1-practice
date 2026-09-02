"use strict";

/* ============================================================
   英検 大問1 単語アプリ
   学習フロー：暗記カード → 理解チェック → 本番演習（設問ごと）
   ※ 間隔反復（Leitner）は全級の「意味だけ練習」に対応。進捗は localStorage に保存。
   kobun-vocab と同じ方式で IIFE に閉じ、{ mount, handleKey } のみを公開する。

   ※ このファイルは static/src/*.js から生成される。直接編集しないこと。
      編集は static/src/ 側で行い、`npm run build` で再生成する。
   ============================================================ */

const EikenQ1App = (function () {

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
  let flashcardDisplayLemmaMap = {};
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
/* ---- progress (localStorage) ---- */
// localStorage への書き込みは失敗しても学習を止めない（容量超過・プライベートモード等）。
function writeStored(key, value) {
  try { localStorage.setItem(key, value); } catch (e) { /* ignore */ }
}
function writeStoredJson(key, value) {
  writeStored(key, JSON.stringify(value));
}
function removeStored(key) {
  try { localStorage.removeItem(key); } catch (e) { /* ignore */ }
}
function loadDatasetId() {
  try {
    const id = localStorage.getItem(datasetStorageKey());
    if (id && DATASETS[id]) return id;
  } catch (e) { /* ignore */ }
  return defaultDatasetId();
}
function dataset() {
  return DATASETS[state.datasetId] || DATASETS[defaultDatasetId()];
}
function datasetCleared(datasetId) {
  const saved = progressFor(datasetId);
  return Boolean(saved && saved.finalCheck && saved.finalCheck.cleared);
}
// datasetId から級プレフィックス（eiken5 / eiken1 / eiken2 / eikenp1 / eikenp2 / iuhw）を取り出す。
// 意味だけ練習の間隔反復（Leitner）とプール化は、この級単位で行う。
function gradeOf(datasetId) {
  const match = DATASET_ID_RE.exec(datasetId || "");
  return match ? match[1] : null;
}
function currentGrade() {
  return gradeOf(state.datasetId);
}
function studyPlanDatasetIds(grade = "eiken1") {
  const source = Object.keys(ALL_DATASETS).length ? ALL_DATASETS : DATASETS;
  return Object.keys(source).filter((id) => gradeOf(id) === grade && !datasetIsTopic(id));
}
function gradeQuestionEntries(grade = "eiken1") {
  const ids = new Set(studyPlanDatasetIds(grade));
  const entries = [];
  const seen = new Set();
  const add = (datasetId, q) => {
    const numericQ = Number(q);
    if (!ids.has(datasetId) || !Number.isInteger(numericQ)) return;
    const key = `${datasetId}:${numericQ}`;
    if (seen.has(key)) return;
    seen.add(key);
    const progress = progressFor(datasetId) || {};
    entries.push({
      datasetId,
      q: numericQ,
      unit: progress.units && progress.units[numericQ] && typeof progress.units[numericQ] === "object"
        ? progress.units[numericQ]
        : {},
    });
  };
  const pooled = pooledData(grade);
  if (pooled) {
    pooled.items.forEach((item) => add(item._datasetId, item.q));
  } else if (grade === currentGrade()) {
    state.qList.forEach((q) => add(state.datasetId, q));
  }
  return entries.sort((a, b) => a.datasetId.localeCompare(b.datasetId) || a.q - b.q);
}
function gradeVocabularyItems(grade = "eiken1") {
  const ids = new Set(studyPlanDatasetIds(grade));
  const pooled = pooledData(grade);
  if (pooled) return pooled.items.filter((item) => ids.has(item._datasetId));
  if (grade === currentGrade()) return allVocabularyItems().map((item) => ({ ...item, _datasetId: state.datasetId }));
  return [];
}
function learnedVocabularyCount(grade, entries = gradeQuestionEntries(grade)) {
  const answeredIds = new Set(answeredQuestionEntries(entries).map(questionEntryId));
  const seen = new Set();
  gradeVocabularyItems(grade).forEach((item) => {
    const datasetId = item._datasetId;
    const q = Number(item.q);
    if (!answeredIds.has(`${datasetId}:${q}`)) return;
    seen.add(`${datasetId}:${itemKeyOf(item)}`);
  });
  return seen.size;
}
function studyPlanQuestionLimit() {
  return Math.max(1, gradeQuestionEntries("eiken1").length);
}
function defaultStudyPlan() {
  return normalizeStudyPlan(null, studyPlanQuestionLimit());
}
function datasetIsTopic(datasetId = state.datasetId) {
  return String(datasetId || "").startsWith("eikentopic-");
}
function datasetSectionName(datasetId = state.datasetId) {
  return datasetIsTopic(datasetId) ? "テーマ別表現" : "大問1";
}
function datasetHeadline(datasetId = state.datasetId) {
  const data = DATASETS[datasetId] || dataset();
  const prefix = String(datasetId || "").startsWith("eiken") ? "英検" : "";
  return datasetIsTopic(datasetId) ? `${prefix}${data.shortLabel}表現` : `${prefix}${data.shortLabel} 大問1`;
}
// 1描画（＝1回のキュー生成）の間だけ、非アクティブ回のブロックをメモ化する。
// ホーム描画は語句ごとに progressFor を呼ぶため、無いと localStorage.getItem + JSON.parse が
// 数百回走る。書き込み系（recordMeaningResult など）は描画パスの外なので、
// 従来どおり毎回 localStorage から読み直してから保存する（古いコピーでの上書きを避ける）。
let progressReadCache = null;
function withProgressReadCache(fn) {
  const outer = progressReadCache; // ネストしても内側で破棄しない
  if (!outer) progressReadCache = new Map();
  try {
    return fn();
  } finally {
    if (!outer) progressReadCache = null;
  }
}
// datasetId のブロックを読み書きする。アクティブ回は state.progress をそのまま使い、
// 別コピーを作らない（renderHome→finalProgress の常時保存が古いコピーで上書きするのを防ぐ）。
function progressFor(datasetId) {
  if (datasetId === state.datasetId) return state.progress;
  if (progressReadCache) {
    if (!progressReadCache.has(datasetId)) progressReadCache.set(datasetId, loadProgress(datasetId));
    return progressReadCache.get(datasetId);
  }
  return loadProgress(datasetId);
}
function saveProgressFor(datasetId, progress) {
  if (datasetId === state.datasetId) { saveProgress(); return; }
  writeStoredJson(progressKey(datasetId), progress);
  if (cloud) cloud.queueSave({
    datasetId,
    progress,
    meta: cloudMeta(),
  });
}
function progressKey(datasetId = state.datasetId) {
  return scopedStorageKey(STORE_PREFIX + datasetId);
}
function loadProgress(datasetId = state.datasetId) {
  let raw = null;
  try {
    raw = localStorage.getItem(progressKey(datasetId));
    if (!raw && !storageStudentId && datasetId === DEFAULT_DATASET_ID) raw = localStorage.getItem(LEGACY_STORE_KEY);
  } catch (e) { return { units: {} }; }
  if (!raw) return { units: {} };
  try {
    const progress = JSON.parse(raw);
    if (!progress || typeof progress !== "object" || Array.isArray(progress)) throw new Error("invalid progress");
    // 旧形式の項目は削除しない。現行フローから参照しなくても、復旧用に元データを残す。
    if (!progress.units || typeof progress.units !== "object" || Array.isArray(progress.units)) {
      progress._recovery = {
        ...(progress._recovery || {}),
        invalidUnits: progress.units,
      };
      progress.units = {};
    }
    return progress;
  } catch (e) {
    // 壊れたJSONを空データとして保存し直さないよう、原文を別キーへ退避する。
    try {
      const backupKey = scopedStorageKey(CORRUPT_PROGRESS_PREFIX + datasetId);
      if (!localStorage.getItem(backupKey)) localStorage.setItem(backupKey, raw);
    } catch (backupError) { /* ignore */ }
    return {
      units: {},
      _recovery: { type: "corrupt-local-record", datasetId },
    };
  }
}

function readStudyPlanLocal() {
  try {
    const raw = localStorage.getItem(scopedStorageKey(STUDY_PLAN_KEY));
    if (!raw) return null;
    const value = JSON.parse(raw);
    return value && typeof value === "object" && !Array.isArray(value) ? value : null;
  } catch (e) {
    return null;
  }
}
function saveStudyPlan() {
  if (!studyPlan) return;
  writeStoredJson(scopedStorageKey(STUDY_PLAN_KEY), studyPlan);
}
function loadStudyPlan() {
  const limit = studyPlanQuestionLimit();
  const local = readStudyPlanLocal();
  const localPlan = local ? normalizeStudyPlan(local, limit) : null;
  const cloudPlan = pendingCloudStudyPlan && typeof pendingCloudStudyPlan === "object" && !Array.isArray(pendingCloudStudyPlan)
    ? normalizeStudyPlan(pendingCloudStudyPlan, limit)
    : null;
  studyPlan = sharedMode() && cloudPlan ? cloudPlan : (localPlan || defaultStudyPlan());
  if (sharedMode() && cloudPlan) saveStudyPlan();
  return studyPlan;
}
function migrateStudyPlanFirstAnswers() {
  const changedDatasetIds = [];
  studyPlanDatasetIds("eiken1").forEach((datasetId) => {
    let raw = null;
    try { raw = localStorage.getItem(progressKey(datasetId)); } catch (e) { /* ignore */ }
    if (!raw) return;
    const progress = loadProgress(datasetId);
    if (!migrateFirstAnsweredAt(progress)) return;
    try {
      localStorage.setItem(progressKey(datasetId), JSON.stringify(progress));
      changedDatasetIds.push(datasetId);
    } catch (e) { /* 移行できなくても元データは残す */ }
  });
  return changedDatasetIds;
}

function readStoredObject(key) {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const value = JSON.parse(raw);
    return value && typeof value === "object" ? value : null;
  } catch (e) {
    return null;
  }
}

let migratedLegacyDatasetIds = [];
function migrateLegacyPre1Progress(legacyStore) {
  migratedLegacyDatasetIds = [];
  if (!legacyStore || typeof legacyStore !== "object" || !legacyStore.rounds) return false;
  let changed = false;
  Object.entries(legacyStore.rounds).forEach(([roundId, oldRound]) => {
    const datasetId = `eikenp1-${roundId}`;
    if (!DATASETS[datasetId] || !oldRound || typeof oldRound !== "object") return;
    const target = loadProgress(datasetId);
    if (target.migrations?.pre1ProgressV1 === PRE1_MIGRATION_VERSION) return;
    if (!target.units || typeof target.units !== "object") target.units = {};

    Object.entries(oldRound.questions || {}).forEach(([key, saved]) => {
      const match = /^reading1:(\d+)$/.exec(key);
      if (!match || !saved || !saved.answered) return;
      const q = Number(match[1]);
      const correct = Boolean(saved.correct);
      const current = target.units[q];
      if (current && current.learned) return;
      target.units[q] = {
        learned: true,
        solvedCorrect: correct,
        needsReview: !correct,
        answerResult: correct ? "correct" : "incorrect",
        attempts: 1,
        wrongCount: correct ? 0 : 1,
        lastAnsweredAt: saved.answeredAt || null,
      };
    });

    if (oldRound.finalCheck && typeof oldRound.finalCheck === "object") {
      target.finalCheck = {
        ...oldRound.finalCheck,
        ...(target.finalCheck || {}),
      };
    }
    target.migrations = {
      ...(target.migrations || {}),
      pre1ProgressV1: PRE1_MIGRATION_VERSION,
      migratedAt: new Date().toISOString(),
    };
    try {
      localStorage.setItem(progressKey(datasetId), JSON.stringify(target));
      migratedLegacyDatasetIds.push(datasetId);
      changed = true;
    } catch (e) { /* 移行できなくても旧データは残す */ }
  });

  try {
    const currentDatasetId = localStorage.getItem(datasetStorageKey());
    const oldRound = localStorage.getItem(LEGACY_PRE1_ROUND_KEY);
    if (!storageStudentId && !currentDatasetId && oldRound && DATASETS[`eikenp1-${oldRound}`]) {
      localStorage.setItem(datasetStorageKey(), `eikenp1-${oldRound}`);
    }
  } catch (e) { /* ignore */ }
  return changed;
}
function saveProgress() {
  writeStoredJson(progressKey(), state.progress);
  if (cloud) cloud.queueSave();
}
function itemSnapshot(item) {
  return item ? { type: item.type, surface: surfaceOf(item), datasetId: item._datasetId || null } : null;
}
// pool省略時は現在の回のみを検索（従来どおり）。級プール済みセッションの再開時は
// pool を渡す。datasetId が付いたスナップショットは同名衝突（例:"coup"）を優先的に厳密一致させ、
// 見つからなければ従来どおり (type, surface) だけで解決する（旧形式のスナップショットとの互換）。
function resolveItem(snapshot, pool) {
  if (!snapshot) return null;
  const candidates = pool || allVocabularyItems();
  if (snapshot.datasetId) {
    const exact = candidates.find((item) => item.type === snapshot.type && surfaceOf(item) === snapshot.surface && item._datasetId === snapshot.datasetId);
    if (exact) return exact;
  }
  return candidates.find((item) => item.type === snapshot.type && surfaceOf(item) === snapshot.surface) || null;
}
function resumeIndexSupported(value, length, allowEnd = false) {
  const index = Number(value);
  const upperBound = allowEnd ? length : length - 1;
  return Number.isInteger(index) && index >= 0 && index <= upperBound;
}
function resumeQuestionSupported(value) {
  const q = Number(value);
  return Number.isInteger(q) && Array.isArray(state.itemsByQ[q]) && state.itemsByQ[q].length > 0;
}
function resumeDataSupported(saved, items, checkOrder, meaningWrongItems = []) {
  if (!resumeStageAllowed(saved.mode, saved.stage)) return false;
  if (saved.mode === "learn") {
    if (!resumeQuestionSupported(saved.q) || !items.length) return false;
    if (saved.stage === "flash") return resumeIndexSupported(saved.flashIdx, items.length);
    if (["check", "practice"].includes(saved.stage) && !checkOrder.length) return false;
    if (saved.stage === "check" && !resumeIndexSupported(saved.checkIdx, checkOrder.length)) return false;
    return true;
  }
  if (saved.mode === "meaning" && saved.stage === "meaningReview") {
    const checked = Array.isArray(saved.meaningWrongChecked) ? saved.meaningWrongChecked : [];
    return checkOrder.length > 0
      && Array.isArray(meaningWrongItems)
      && meaningWrongItems.length > 0
      && checked.every((index) => resumeIndexSupported(index, meaningWrongItems.length));
  }
  if (!checkOrder.length) return false;
  return saved.stage === "done" || resumeIndexSupported(saved.checkIdx, checkOrder.length);
}
function resumeDescription(resume) {
  if (!resume) return "";
  if (resume.mode === "learn") {
    const stage = {
      flash: `STEP 1 暗記カード ${Number(resume.flashIdx || 0) + 1}/${resume.items?.length || 4}`,
      check: `STEP 2 4語句の意味確認 ${Number(resume.checkIdx || 0) + 1}/${resume.checkOrder?.length || 4}`,
      practice: "STEP 3 本番形式",
      done: "完了確認",
    }[resume.stage] || "学習中";
    return `第${resume.q}問・${stage}`;
  }
  if (resume.mode === "meaning") {
    if (resume.stage === "meaningReview") {
      const checked = Array.isArray(resume.meaningWrongChecked) ? resume.meaningWrongChecked.length : 0;
      const total = Array.isArray(resume.meaningWrongItems) ? resume.meaningWrongItems.length : 0;
      return `意味だけ復習・誤答見直し ${checked}/${total}`;
    }
    const label = resume.dueOnly ? "意味だけ復習" : "全語句の意味確認";
    return `${label} ${Number(resume.checkIdx || 0) + 1}/${resume.checkOrder?.length || 1}`;
  }
  if (resume.mode === "final") return `最終チェック ${Number(resume.checkIdx || 0) + 1}/${resume.checkOrder?.length || 1}`;
  return "学習の続き";
}
function resumableResume(resume) {
  return resume && RESUMABLE_MODES.has(resume.mode)
    && resumeStageAllowed(resume.mode, resume.stage) ? resume : null;
}
function currentResume() {
  const resume = resumableResume(state.progress && state.progress.resume);
  return resume && !resumeUnavailable ? resume : null;
}
function saveResume() {
  if (!session) return;
  state.progress.resume = {
    mode: session.mode,
    q: session.q,
    stage: session.stage,
    flashIdx: session.flashIdx,
    checkIdx: session.checkIdx,
    checkAnswered: Boolean(session.checkAnswered),
    checkPicked: session.checkPicked,
    checkCorrect: session.checkCorrect,
    checkOrder: (session.checkOrder || []).map(itemSnapshot),
    items: (session.items || []).map(itemSnapshot),
    meaningCorrect: session.meaningCorrect || 0,
    finalCorrect: session.finalCorrect || 0,
    dueOnly: Boolean(session.dueOnly),
    meaningVersion: session.meaningVersion || null,
    meaningBatchSize: session.meaningBatchSize || null,
    meaningWrongItems: (session.meaningWrongItems || []).map(itemSnapshot),
    meaningWrongChecked: session.meaningWrongChecked || [],
    practiceAnswered: Boolean(session.practiceAnswered),
    practiceResult: session.practiceResult,
    checkChoices: session._checkChoices || null,
    responseElapsedLog: session.responseElapsedLog || [],
    meaningRtLog: session.meaningRtLog || [],
  };
  resumeRecoveryMessage = "";
  resumeUnavailable = false;
  saveProgress();
}
function clearResume() {
  if (!state.progress.resume) return;
  delete state.progress.resume;
  resumeRecoveryMessage = "";
  resumeUnavailable = false;
  saveProgress();
}
async function restoreSession() {
  const saved = state.progress.resume;
  if (!saved || !saved.mode) return false;
  if (!RESUMABLE_MODES.has(saved.mode)) {
    resumeRecoveryMessage = "以前の形式の途中記録は保持しています。現在の学習フローでは、第1問から再開してください。";
    resumeUnavailable = true;
    return false;
  }
  if (!resumeStageAllowed(saved.mode, saved.stage)) {
    resumeRecoveryMessage = "途中記録は保持していますが、対応していない状態のため自動再開できません。第1問から再開してください。";
    resumeUnavailable = true;
    return false;
  }
  // プール済み「意味だけ演習」を再開する場合のみ、同じ級の全回プールを取得。
  // 取得失敗（オフライン等）は「対象が無い」と区別し、resumeを消さずに諦める。
  let pool = null;
  if (saved.mode === "meaning" && currentGrade()) {
    try {
      pool = (await loadPooledItems()).items;
    } catch (e) {
      return false;
    }
  }
  const items = (saved.items || []).map((s) => resolveItem(s, pool)).filter(Boolean);
  let checkOrder = (saved.checkOrder || []).map((s) => resolveItem(s, pool)).filter(Boolean);
  const meaningWrongItems = (saved.meaningWrongItems || []).map((s) => resolveItem(s, pool)).filter(Boolean);
  if (!resumeDataSupported(saved, items, checkOrder, meaningWrongItems)) {
    resumeRecoveryMessage = "途中記録は保持していますが、現在の問題データと一致しないため自動再開できません。第1問から再開してください。";
    resumeUnavailable = true;
    return false;
  }
  if (saved.mode === "meaning" && currentGrade()
    && (saved.meaningVersion !== MEANING_PROGRESS_VERSION
      || saved.meaningBatchSize !== MEANING_SESSION_SIZE
      || checkOrder.length > MEANING_SESSION_SIZE)) {
    return Boolean(await startMeaningPractice(true));
  }
  session = {
    ...saved,
    q: saved.q == null ? null : Number(saved.q),
    items,
    checkOrder,
    meaningWrongItems,
    meaningWrongChecked: Array.isArray(saved.meaningWrongChecked) ? saved.meaningWrongChecked : [],
    _checkChoices: saved.checkChoices || null,
    // 旧途中保存のaudioElapsedLogも、現在の表示起点ログとして引き継ぐ。
    responseElapsedLog: Array.isArray(saved.responseElapsedLog)
      ? saved.responseElapsedLog
      : (Array.isArray(saved.audioElapsedLog) ? saved.audioElapsedLog : []),
    meaningRtLog: Array.isArray(saved.meaningRtLog) ? saved.meaningRtLog : [],
  };
  resumeRecoveryMessage = "";
  resumeUnavailable = false;
  renderSession();
  resetSessionScroll();
  return true;
}
function unit(q) {
  if (!state.progress.units[q]) state.progress.units[q] = {};
  const u = state.progress.units[q];
  if (typeof u.learned !== "boolean") u.learned = false;
  if (typeof u.solvedCorrect !== "boolean") u.solvedCorrect = false;
  if (typeof u.needsReview !== "boolean") u.needsReview = false;
  if (typeof u.attempts !== "number") u.attempts = 0;
  if (typeof u.wrongCount !== "number") u.wrongCount = 0;
  if (!["correct", "incorrect", "unknown", "unseen"].includes(u.answerResult)) {
    u.answerResult = u.solvedCorrect ? "correct" : (u.needsReview ? "incorrect" : (u.learned ? "unknown" : "unseen"));
  }
  return state.progress.units[q];
}
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

/* ============================================================
   cloud sync（生徒別・共有URL ?s=&t=）— harness/cloud.js を利用
   共通スキーマ app_students / app_progress（app="eiken2-q1"）。
   config.json が無ければ no-op で、従来どおり匿名ローカル動作（無回帰）。
   RPC/認証/デバウンス保存は vendor/harness/cloud.js に集約。
   このアプリ固有＝複数データセットの進捗を1つのjsonbにまとめる点のみ。
   ============================================================ */
const APP_ID = "eiken2-q1";
let cloud = null; // harness createCloud のインスタンス（init で生成）
let legacyPre1Cloud = null;
let legacyPre1CloudProgress = null;
let pendingCloudProgress = null;

function cloudMeta() {
  return {
    lastDatasetId: state.datasetId,
    ...(studyPlan ? { studyPlanV1: studyPlan } : {}),
  };
}

function setShareStatus(message, tone = "") {
  const slot = $("#shareStatus");
  if (!slot) return;
  slot.innerHTML = "";
  slot.className = "shareStatus" + (tone ? " " + tone : "");
  if (!message) return;
  if (tone === "ok" || tone === "ng" || tone === "syncing") {
    slot.appendChild(el("span", { class: "shareStatusIcon", "aria-hidden": "true" }));
  }
  slot.appendChild(document.createTextNode(message));
}
// クラウド保存は全データセット分の進捗を1つのjsonbにまとめる: { [datasetId]: progress }
function collectAllProgress() {
  const map = {};
  // 級を絞っても他級の進捗を落とした地図でクラウドを上書きしないよう、manifest全件を見る。
  Object.keys(ALL_DATASETS).forEach((id) => {
    try {
      const raw = localStorage.getItem(progressKey(id));
      if (raw) map[id] = JSON.parse(raw);
    } catch (e) { /* ignore */ }
  });
  map[state.datasetId] = state.progress; // 直近のメモリ状態を優先
  map._meta = cloudMeta();
  return map;
}

/* ---- 級ごとに全回の語彙を読み込み、通常学習済みだけを意味練習へ回す ---- */
// 級をまたいでも取り違えないよう、プールは級プレフィックスをキーにして持つ。
const pooledPromiseByGrade = new Map(); // grade -> Promise<{items, meaningPool}>
const pooledDataByGrade = new Map();    // grade -> {items, meaningPool}（解決済みのみ）
function gradeDatasetIds(grade) {
  return Object.keys(DATASETS).filter((id) => gradeOf(id) === grade);
}
function wordOriginLemma(item) {
  if (!item || item.type !== "word") return "";
  const surface = String(surfaceOf(item) || "").toLowerCase();
  return String(lemmaMap[surface] || surface).toLowerCase();
}
function wordOriginFor(item) {
  const lemma = wordOriginLemma(item);
  return lemma ? wordOriginMap[lemma] || null : null;
}
// 同期的に使える解決済みプール。未読み込み・級不明のときは null。
function pooledData(grade = currentGrade()) {
  return (grade && pooledDataByGrade.get(grade)) || null;
}
async function loadPooledItems(grade = currentGrade()) {
  if (!grade) return { items: [], meaningPool: { word: [], idiom: [] } };
  const cached = pooledDataByGrade.get(grade);
  if (cached) return cached;
  if (!pooledPromiseByGrade.has(grade)) {
    pooledPromiseByGrade.set(grade, Promise.all(
      gradeDatasetIds(grade).map((id) => fetch(DATASETS[id].vocabUrl, { cache: "no-store" }).then((r) => r.json()).then((vocab) => ({ id, vocab })))
    ).then((loaded) => {
      const items = [];
      const meaningPool = { word: [], idiom: [] };
      const seenTopicItems = new Set();
      for (const { id, vocab } of loaded) {
        const words = (vocab.words || []).map((w) => ({ ...w, type: "word", _datasetId: id }));
        const idioms = (vocab.idioms || []).map((w) => ({ ...w, type: "idiom", _datasetId: id }));
        for (const it of words.concat(idioms)) {
          if (grade === "eikentopic") {
            const key = `${id}:${itemKeyOf(it)}`;
            if (seenTopicItems.has(key)) continue;
            seenTopicItems.add(key);
          }
          items.push(it);
          meaningPool[it.type].push(learningMeaningOf(it));
        }
      }
      return { items, meaningPool };
    }).catch((e) => {
      // 失敗したPromiseを残すと以後ずっと同じ失敗を返すため、再試行できるようにする。
      pooledPromiseByGrade.delete(grade);
      throw e;
    }));
  }
  const data = await pooledPromiseByGrade.get(grade);
  pooledDataByGrade.set(grade, data);
  return data;
}

function isLearnedQuestion(progress, q) {
  return Boolean(progress && progress.units && progress.units[q] && progress.units[q].learned);
}

function learnedPooledItems(items = []) {
  const learnedKeys = new Set(
    items
      .filter((item) => isLearnedQuestion(
        progressFor(item._datasetId || state.datasetId),
        item.q,
      ))
      .map((item) => `${item._datasetId || state.datasetId}:${itemKeyOf(item)}`),
  );
  return items.filter((item) => learnedKeys.has(
    `${item._datasetId || state.datasetId}:${itemKeyOf(item)}`,
  ));
}

function meaningPoolForItems(items) {
  const pool = { word: [], idiom: [] };
  for (const item of items) {
    if (!pool[item.type]) pool[item.type] = [];
    const meaning = learningMeaningOf(item);
    if (meaning && !pool[item.type].includes(meaning)) pool[item.type].push(meaning);
  }
  return pool;
}

// 学習済みだけで誤答を作ると、学習量が少ない段階では候補がその設問の残り語句に
// 固定され、消去法で正解できてしまう。候補が下限に満たない間は同じ級の未学習語の
// 意味で補い、それでも4択に足りなければ別type（word↔idiom）からも補う。
const MEANING_DISTRACTOR_MIN_POOL = 8;

function meaningDistractors(item, count = 3) {
  const correctMeaning = learningMeaningOf(item);
  const pooled = session.mode === "meaning" ? pooledData() : null;
  const learnedPool = pooled ? meaningPoolForItems(learnedPooledItems(pooled.items)) : state.meaningPool;
  const fullPool = pooled ? pooled.meaningPool : state.meaningPool;
  const sameType = (pool) => (pool[item.type] || []).filter((m) => m && m !== correctMeaning);
  const otherTypes = (pool) => Object.keys(pool)
    .filter((t) => t !== item.type)
    .reduce((acc, t) => acc.concat(pool[t] || []), [])
    .filter((m) => m && m !== correctMeaning);

  const candidates = [];
  const add = (list) => {
    for (const m of list) if (!candidates.includes(m)) candidates.push(m);
  };

  add(sameType(learnedPool));
  if (candidates.length < MEANING_DISTRACTOR_MIN_POOL) add(shuffle(sameType(fullPool)));
  if (candidates.length < count) add(shuffle(otherTypes(fullPool)));
  return shuffle(candidates).slice(0, count);
}

function meaningPracticeSummary() {
  const pooled = pooledData();
  if (!pooled) return { total: 0, learned: 0, due: 0, locked: 0 };
  const learned = learnedPooledItems(pooled.items);
  const due = learned.filter((item) => isItemDue(item));
  return {
    total: pooled.items.length,
    learned: learned.length,
    due: due.length,
    locked: Math.max(0, pooled.items.length - learned.length),
  };
}

// 他の級で復習期限が来ている語句数。語彙JSONは読まず、進捗の nextReviewAt だけで数える
// （items の記録は意味だけ復習で解答したときにしか作られないため、学習済み判定は要らない）。
// 級を切り替えると間隔復習カードの中身が丸ごと入れ替わるため、記録が別の級に残っていることを示す。
function otherGradeDueCounts(now = Date.now()) {
  const current = currentGrade();
  const rows = [];
  for (const grade of datasetGrades()) {
    if (!grade || grade === current) continue;
    let count = 0;
    let topId = "";
    let topCount = 0;
    for (const id of gradeDatasetIds(grade)) {
      const items = (progressFor(id) || {}).items || {};
      let dueHere = 0;
      for (const itemState of Object.values(items)) {
        if (itemState && itemState.nextReviewAt && new Date(itemState.nextReviewAt).getTime() <= now) dueHere += 1;
      }
      count += dueHere;
      if (dueHere > topCount) { topId = id; topCount = dueHere; }
    }
    if (count > 0) rows.push({ grade, label: datasetGradeLabel(grade), count, datasetId: topId });
  }
  return rows.sort((a, b) => b.count - a.count).slice(0, 3);
}

// 今回出題される語句を、直前の復習間隔で分類する。
function meaningIntervalLabel(item) {
  const itemState = readItemStateOf(item);
  if (!itemState.lastAnsweredAt) return "未実施";
  if (!itemState.nextReviewAt) return "要再確認";
  const elapsedDays = Math.round(
    (new Date(itemState.nextReviewAt).getTime() - new Date(itemState.lastAnsweredAt).getTime())
      / (24 * 60 * 60 * 1000),
  );
  return MEANING_INTERVALS.find(({ days }) => days === elapsedDays)?.label || "要再確認";
}

function meaningIntervalBreakdown(items) {
  const counts = Object.fromEntries(MEANING_INTERVALS.map(({ label }) => [label, 0]));
  items.forEach((item) => { counts[meaningIntervalLabel(item)] += 1; });
  const grid = el("div", {
    class: "meaningMissionIntervalGrid",
    "aria-label": "意味だけ復習の間隔別内訳",
  });
  MEANING_INTERVALS.forEach(({ label }) => {
    grid.appendChild(el("div", { class: "meaningMissionInterval" },
      el("strong", {}, String(counts[label])),
      el("span", {}, label),
    ));
  });
  return grid;
}
// クラウドから来た進捗（{datasetId: progress}）を localStorage へ反映
function applyCloudProgress(map) {
  if (!map || typeof map !== "object") return;
  pendingCloudStudyPlan = map._meta && map._meta.studyPlanV1
    && typeof map._meta.studyPlanV1 === "object"
    && !Array.isArray(map._meta.studyPlanV1)
    ? map._meta.studyPlanV1
    : null;
  if (studyPlan && pendingCloudStudyPlan) {
    studyPlan = normalizeStudyPlan(pendingCloudStudyPlan, studyPlanQuestionLimit());
    saveStudyPlan();
  }
  const lastDatasetId = map._meta && typeof map._meta.lastDatasetId === "string"
    ? map._meta.lastDatasetId
    : "";
  if (lastDatasetId && DATASETS[lastDatasetId]) {
    writeStored(datasetStorageKey(), lastDatasetId);
  }
  Object.entries(map).forEach(([id, prog]) => {
    if (DATASETS[id] && prog && typeof prog === "object") {
      writeStoredJson(progressKey(id), prog);
    }
  });
}
function applyLegacyPre1CloudProgress(value) {
  if (value && typeof value === "object" && value.rounds && typeof value.rounds === "object") {
    legacyPre1CloudProgress = value;
  }
}
function applySharedUi() {
  const enabled = Boolean(cloud && cloud.isEnabled());
  document.body.classList.toggle("sharedMode", enabled);
}
function sharedMode() {
  return Boolean(cloud && cloud.isEnabled());
}

/* ---- helpers ---- */
const $ = (sel) => document.querySelector(sel);
function el(tag, attrs = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") n.className = v;
    else if (k === "html") n.innerHTML = v;
    else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v);
  }
  for (const kid of kids) {
    if (kid == null) continue;
    n.appendChild(typeof kid === "string" ? document.createTextNode(kid) : kid);
  }
  return n;
}
function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
function surfaceOf(item) { return item.type === "idiom" ? item.phrase : item.word; }
function canonicalHeadwordOf(item) {
  const surface = surfaceOf(item);
  if (!item || item.type !== "word") return surface;
  return lemmaMap[String(surface || "").toLowerCase()] || surface;
}
function learningEntryOf(item) {
  const headword = canonicalHeadwordOf(item);
  const key = String(headword || "").toLowerCase();
  const entry = lemmaEntries[key];
  if (entry && typeof entry === "object") return entry;
  return {
    meaning: item?.meaning || "",
    ipa: item?.ipa || "",
    pos: item?.pos || "",
    audio: "",
    surfaces: [surfaceOf(item)],
  };
}
function learningMeaningOf(item) { return learningEntryOf(item).meaning || item?.meaning || ""; }
function learningPosOf(item) { return learningEntryOf(item).pos || item?.pos || ""; }
function lemmaAudioPathOf(item, useFlashcardLemma = false) {
  if (useFlashcardLemma) {
    const flashcardLemma = flashcardLemmaOf(item);
    if (flashcardLemma) {
      const entry = lemmaEntries[flashcardLemma];
      return entry?.audio || `assets/audio/lemma/${audioSlug(flashcardLemma)}.mp3`;
    }
  }
  return learningEntryOf(item).audio || vocabularyAudioPath(item);
}
function normalizedSurface(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[’']/g, "'")
    .replace(/\b(one's|his|her|my|your|our|their|its)\b/g, "@poss")
    .replace(/\s+/g, " ")
    .trim();
}
function audioSlug(value) {
  return normalizedSurface(value).replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}
function flashcardLemmaOf(item) {
  if (!item) return "";
  const surface = String(surfaceOf(item) || "").toLowerCase();
  return String(
    flashcardDisplayLemmaMap[surface]
      || (item.type === "word" ? flashcardLemmaMap[surface] : "")
      || "",
  ).trim().toLowerCase();
}
function vocabularyAudioDataset(item) {
  if (!item || (item.type !== "word" && item.type !== "idiom")) return null;
  const match = DATASET_ID_RE.exec((item._datasetId || state.datasetId) || "");
  return match ? { appGrade: match[1], round: match[2] } : null;
}
function vocabularyAudioPath(item) {
  const dataset = vocabularyAudioDataset(item);
  if (!dataset) return "";
  const audioGrade = GRADE_BY_PREFIX[dataset.appGrade];
  if (!audioGrade) return "";
  const slug = audioSlug(surfaceOf(item));
  if (!slug) return "";
  const folder = item.type === "idiom" ? "/idiom" : "";
  return `assets/audio/vocab/${audioGrade}/${dataset.round}${folder}/${slug}.mp3`;
}
function vocabularyAudioEnabled(item) { return Boolean(vocabularyAudioDataset(item)); }
let activeVocabAudio = null;
let activeVocabButton = null;
let activeVocabSpeech = null;
const AUDIO_STATE_LABEL = { idle: "音声", loading: "読込中", playing: "再生中", error: "再生できません" };
function setAudioButtonState(button, stateName) {
  if (!button) return;
  button.dataset.audioState = stateName;
  const label = button.querySelector(".audioLabel");
  if (label) label.textContent = " " + (AUDIO_STATE_LABEL[stateName] || AUDIO_STATE_LABEL.idle);
  const hasBars = Boolean(button.querySelector(".audioBars"));
  if (stateName === "playing" && !hasBars) {
    button.appendChild(el("span", { class: "audioBars", "aria-hidden": "true" },
      el("span", {}), el("span", {}), el("span", {})));
  } else if (stateName !== "playing" && hasBars) {
    button.querySelector(".audioBars").remove();
  }
}
function resetVocabAudioButton(button) {
  if (!button) return;
  button.disabled = false;
  setAudioButtonState(button, "idle");
}
function stopVocabSpeech() {
  if (!activeVocabSpeech) return;
  window.speechSynthesis.cancel();
  resetVocabAudioButton(activeVocabSpeech.button);
  activeVocabSpeech = null;
}
function playVocabSpeech(text, button) {
  if (!window.speechSynthesis || !window.SpeechSynthesisUtterance) {
    button.disabled = false;
    setAudioButtonState(button, "error");
    button.title = "このブラウザでは音声を再生できません。";
    return;
  }
  if (activeVocabAudio) {
    activeVocabAudio.pause();
    activeVocabAudio.currentTime = 0;
    activeVocabAudio = null;
  }
  resetVocabAudioButton(activeVocabButton);
  stopVocabSpeech();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  activeVocabSpeech = { utterance, button };
  button.disabled = true;
  setAudioButtonState(button, "loading");
  const finish = () => {
    resetVocabAudioButton(button);
    if (activeVocabSpeech?.utterance === utterance) activeVocabSpeech = null;
  };
  utterance.addEventListener("start", () => setAudioButtonState(button, "playing"), { once: true });
  utterance.addEventListener("end", finish, { once: true });
  utterance.addEventListener("error", () => {
    button.disabled = false;
    setAudioButtonState(button, "error");
    if (activeVocabSpeech?.utterance === utterance) activeVocabSpeech = null;
  }, { once: true });
  window.speechSynthesis.speak(utterance);
}
function playVocabAudio(path, button, text) {
  if (!path) {
    playVocabSpeech(text, button);
    return;
  }
  stopVocabSpeech();
  if (activeVocabAudio) {
    activeVocabAudio.pause();
    activeVocabAudio.currentTime = 0;
  }
  resetVocabAudioButton(activeVocabButton);
  const audio = new Audio(path);
  activeVocabAudio = audio;
  activeVocabButton = button;
  button.disabled = true;
  setAudioButtonState(button, "loading");
  const finish = () => {
    resetVocabAudioButton(button);
    if (activeVocabAudio === audio) {
      activeVocabAudio = null;
      activeVocabButton = null;
    }
  };
  audio.addEventListener("playing", () => setAudioButtonState(button, "playing"), { once: true });
  audio.addEventListener("ended", finish, { once: true });
  audio.addEventListener("error", () => {
    finish();
    button.title = "MP3を読み込めないため、ブラウザ音声を再生します。";
    playVocabSpeech(text, button);
  }, { once: true });
  audio.play().catch(finish);
}
function buildVocabAudioButton(item, className = "flashListenButton", useFlashcardLemma = false) {
  const surface = useFlashcardLemma ? flashcardLemmaOf(item) || canonicalHeadwordOf(item) : canonicalHeadwordOf(item);
  const audioButton = el("button", {
    class: className,
    type: "button",
    "aria-label": `${surface}の発音を聞く`,
    title: "発音を聞く",
    "data-audio-state": "idle",
  });
  audioButton.appendChild(el("span", { class: "audioIcon", "aria-hidden": "true" }, "▶"));
  audioButton.appendChild(el("span", { class: "audioLabel" }, " 音声"));
  audioButton.addEventListener("click", () => playVocabAudio(lemmaAudioPathOf(item, useFlashcardLemma), audioButton, surface));
  return audioButton;
}
function surfaceVariants(value) {
  const base = normalizedSurface(value);
  const variants = new Set([base]);
  if (base.endsWith("ies") && base.length > 3) variants.add(base.slice(0, -3) + "y");
  if (base.endsWith("ied") && base.length > 3) variants.add(base.slice(0, -3) + "y");
  if (base.endsWith("es") && base.length > 3) variants.add(base.slice(0, -2));
  if (base.endsWith("s") && base.length > 2) variants.add(base.slice(0, -1));
  if (base.endsWith("ed") && base.length > 3) {
    const stem = base.slice(0, -2);
    variants.add(stem);
    if (/(.)\1$/.test(stem)) variants.add(stem.slice(0, -1));
    if (stem.endsWith("i")) variants.add(stem.slice(0, -1) + "y");
    variants.add(stem + "e");
  }
  if (base.endsWith("ing") && base.length > 4) {
    const stem = base.slice(0, -3);
    variants.add(stem);
    if (/(.)\1$/.test(stem)) variants.add(stem.slice(0, -1));
    variants.add(stem + "e");
  }
  return variants;
}
function findItemForSurface(items, value) {
  const target = normalizedSurface(value);
  const exact = items.find((item) => normalizedSurface(surfaceOf(item)) === target);
  if (exact) return exact;
  const targetVariants = surfaceVariants(value);
  return items.find((item) => {
    for (const variant of surfaceVariants(surfaceOf(item))) {
      if (targetVariants.has(variant)) return true;
    }
    return false;
  }) || null;
}
// 回答後、4つの選択肢すべての意味を正解・ユーザー回答のラベル付きで一覧表示する
function practiceChoiceMeanings(q_, items, selectedIdx) {
  const section = el("section", {
    class: "practiceChoiceMeanings",
    "aria-labelledby": "practiceChoiceMeaningsTitle",
  });
  section.appendChild(el("h4", { id: "practiceChoiceMeaningsTitle" }, "4つの選択肢の意味"));

  const list = el("ol", { class: "practiceChoiceMeaningList" });
  q_.choices.forEach((choice, idx) => {
    const item = findItemForSurface(items, choice);
    const isCorrect = idx === q_.answerIndex;
    const isSelected = idx === selectedIdx;
    let stateLabel = "";
    if (isCorrect && isSelected) stateLabel = "✓ 正解・あなたの回答";
    else if (isCorrect) stateLabel = "✓ 正解";
    else if (isSelected) stateLabel = "あなたの回答";

    const head = el("div", { class: "practiceChoiceMeaningHead" },
      el("span", { class: "practiceChoiceMeaningWord" }, choice),
    );
    if (stateLabel) {
      head.appendChild(el("span", { class: "practiceChoiceMeaningState" }, stateLabel));
    }

    list.appendChild(el("li", {
      class: `practiceChoiceMeaningRow${isCorrect ? " isCorrect" : ""}${isSelected && !isCorrect ? " isSelectedWrong" : ""}`,
    },
      head,
      el("p", { class: "practiceChoiceMeaningText" }, item?.meaning || "意味を取得できませんでした"),
    ));
  });

  section.appendChild(list);
  return section;
}
// 選択肢を描画した瞬間の時刻を記録し、直後の誤クリックを無視する
function armChoiceGuard() { session._choicesReadyAt = performance.now() + CHOICE_GUARD_MS; }
function choicesLocked() { return performance.now() < (session._choicesReadyAt || 0); }
function armFlashNavGuard() { session._flashNavReadyAt = performance.now() + FLASH_NAV_GUARD_MS; }
function flashNavLocked() { return performance.now() < (session._flashNavReadyAt || 0); }
/* ============================================================
   load data
   ============================================================ */
async function loadData(datasetId = state.datasetId) {
  state.datasetId = datasetId;
  resumeRecoveryMessage = "";
  resumeUnavailable = false;
  state.itemsByQ = {};
  state.questions = {};
  state.qList = [];
  state.meaningPool = { word: [], idiom: [] };
  state.progress = loadProgress(datasetId);
  const savedResume = state.progress.resume;
  if (savedResume && (!RESUMABLE_MODES.has(savedResume.mode) || !resumeStageAllowed(savedResume.mode, savedResume.stage))) {
    resumeRecoveryMessage = "以前の形式の途中記録は保持しています。現在の学習フローでは、第1問から再開してください。";
    resumeUnavailable = true;
  }
  writeStored(datasetStorageKey(), datasetId);

  const current = dataset();
  const [vocab, qs] = await Promise.all([
    fetch(current.vocabUrl, { cache: "no-store" }).then((r) => r.json()),
    fetch(current.questionsUrl, { cache: "no-store" }).then((r) => r.json()),
  ]);

  const words = (vocab.words || []).map((w) => ({ ...w, type: "word" }));
  const idioms = (vocab.idioms || []).map((i) => ({ ...i, type: "idiom" }));
  const all = words.concat(idioms);
  for (const it of all) {
    if (!state.itemsByQ[it.q]) state.itemsByQ[it.q] = [];
    state.itemsByQ[it.q].push(it);
    state.meaningPool[it.type].push(learningMeaningOf(it));
  }
  for (const q of qs.questions) state.questions[q.q] = q;

  state.qList = Object.keys(state.itemsByQ)
    .map(Number)
    .sort((a, b) => a - b);
}

async function switchDataset(datasetId) {
  if (!DATASETS[datasetId] || datasetId === state.datasetId) return;
  await loadData(datasetId);
  if (cloud) cloud.queueSave();
  if (window.EikenActiveAppId !== "q1") return;
  session = null;
  renderHome();
}

function setChromeTitle(title) {
  const titleEl = document.getElementById("appTitle");
  if (titleEl) titleEl.textContent = title;
  document.title = title;
}

/* ============================================================
   HOME
   ============================================================ */
function renderHome() {
  // 同期処理のみ。await をまたぐとキャッシュが別パスへ漏れるので中で非同期処理を待たない。
  return withProgressReadCache(renderHomeContent);
}
function formatStudyPlanDate(date) {
  return date.toLocaleDateString("ja-JP", { month: "numeric", day: "numeric" });
}
function studyPlanProgress(label, value, max, valueText, detail) {
  const safeMax = Math.max(1, Number(max) || 1);
  const safeValue = Math.max(0, Number(value) || 0);
  const boundedValue = Math.min(safeValue, safeMax);
  const track = el("div", {
    class: "studyPlanProgress",
    role: "progressbar",
    "aria-label": label,
    "aria-valuemin": "0",
    "aria-valuemax": String(safeMax),
    "aria-valuenow": String(boundedValue),
    "aria-valuetext": valueText,
  });
  const fill = el("span", { class: "studyPlanProgressFill" });
  fill.style.width = `${(boundedValue / safeMax) * 100}%`;
  track.appendChild(fill);
  return el("div", { class: "studyPlanMetric" },
    el("div", { class: "studyPlanMetricHead" },
      el("strong", {}, label),
      el("span", { class: "studyPlanMetricValue" }, valueText),
    ),
    track,
    el("p", { class: "studyPlanMetricDetail" }, detail),
  );
}
function studyPlanPanel(entries = []) {
  const plan = studyPlan || defaultStudyPlan();
  const limit = studyPlanQuestionLimit();
  const summary = studyPlanSummary(new Date(), plan, entries);
  const num = (value) => Number(value).toLocaleString("ja-JP");
  const weekEndDate = new Date(summary.weekEnd);
  weekEndDate.setDate(weekEndDate.getDate() - 1);
  const weekRange = `${formatStudyPlanDate(summary.weekStart)}〜${formatStudyPlanDate(weekEndDate)}`;
  const totalStatus = summary.overallRemaining === 0 ? "✓ 総目標達成" : `あと${num(summary.overallRemaining)}問`;
  const dailyStatus = summary.dailyRemaining === 0 ? "✓ 今日の目標達成" : `あと${num(summary.dailyRemaining)}問`;
  const weeklyStatus = summary.weeklyRemaining === 0 ? "✓ 今週の目標達成" : `残り${num(summary.weeklyRemaining)}問`;
  const panel = el("div", { class: "studyPlanPanel", "aria-labelledby": "studyPlanTitle" });
  const settingsId = "studyPlanSettings";
  const settingsToggle = el("button", {
    class: "ghost studyPlanSettingsToggle",
    type: "button",
    "aria-expanded": "false",
    "aria-controls": settingsId,
  }, "学習目標を設定");
  const settings = el("form", {
    class: "studyPlanSettings hide",
    id: settingsId,
    "aria-labelledby": "studyPlanSettingsTitle",
  });
  const goalInput = el("input", {
    type: "number",
    min: "1",
    max: String(limit),
    value: String(plan.questionGoal),
    inputmode: "numeric",
  });
  const dailyInput = el("input", {
    type: "number",
    min: "1",
    max: String(limit),
    value: String(plan.dailyQuestionGoal),
    inputmode: "numeric",
  });
  const weekSelect = el("select", { name: "weekStartsOn" });
  ["日曜日", "月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日"].forEach((label, day) => {
    weekSelect.appendChild(el("option", { value: String(day) }, label));
  });
  weekSelect.value = String(plan.weekStartsOn);
  const error = el("p", { class: "studyPlanFormError", role: "alert", "aria-live": "polite" });
  function restoreSettingsForm() {
    goalInput.value = String(plan.questionGoal);
    dailyInput.value = String(plan.dailyQuestionGoal);
    weekSelect.value = String(plan.weekStartsOn);
    error.textContent = "";
  }
  const field = (label, input, hint) => el("label", { class: "studyPlanField" },
    el("span", { class: "fieldLabel" }, label),
    input,
    el("span", { class: "studyPlanFieldHint" }, hint),
  );
  settings.appendChild(el("h4", { id: "studyPlanSettingsTitle" }, "学習目標の設定"));
  settings.appendChild(el("p", { class: "hint" }, `総問題目標と1日の問題目標は1〜${num(limit)}問で設定できます。`));
  settings.appendChild(el("div", { class: "studyPlanFields" },
    field("総問題目標", goalInput, "このアプリで新規に解く総問題数"),
    field("1日の問題目標", dailyInput, "週間目標はこの7倍"),
    field("週の開始曜日", weekSelect, "日〜土から選択"),
  ));
  settings.appendChild(error);
  settings.appendChild(el("div", { class: "actions studyPlanFormActions" },
    el("button", { class: "cta", type: "submit" }, "保存"),
    el("button", { class: "ghost", type: "button", onclick: () => {
      restoreSettingsForm();
      settings.classList.add("hide");
      settingsToggle.setAttribute("aria-expanded", "false");
      settingsToggle.focus();
    } }, "キャンセル"),
  ));
  settings.addEventListener("submit", (event) => {
    event.preventDefault();
    const questionGoal = Number(goalInput.value);
    const dailyQuestionGoal = Number(dailyInput.value);
    const weekStartsOn = Number(weekSelect.value);
    const validInteger = (value, max) => Number.isInteger(value) && value >= 1 && value <= max;
    if (!validInteger(questionGoal, limit) || !validInteger(dailyQuestionGoal, limit)
      || !Number.isInteger(weekStartsOn) || weekStartsOn < 0 || weekStartsOn > 6) {
      error.textContent = `総問題目標と1日の問題目標は1〜${num(limit)}問、週の開始曜日は日〜土から選んでください。`;
      return;
    }
    studyPlan = normalizeStudyPlan({
      ...plan,
      questionGoal,
      dailyQuestionGoal,
      weekStartsOn,
    }, limit);
    saveStudyPlan();
    if (cloud) cloud.queueSave({
      datasetId: state.datasetId,
      progress: state.progress,
      meta: cloudMeta(),
    });
    renderHome();
  });
  settingsToggle.addEventListener("click", () => {
    const open = settings.classList.contains("hide");
    if (!open) {
      restoreSettingsForm();
      settings.classList.add("hide");
      settingsToggle.setAttribute("aria-expanded", "false");
      settingsToggle.focus();
      return;
    }
    settings.classList.toggle("hide", !open);
    settingsToggle.setAttribute("aria-expanded", String(open));
    if (open) goalInput.focus();
  });

  panel.appendChild(el("div", { class: "studyPlanHead" },
    el("div", {},
      el("p", { class: "label" }, "学習目標"),
      el("h3", { id: "studyPlanTitle" }, "今日と今週の新規問題"),
    ),
    settingsToggle,
  ));
  panel.appendChild(el("div", { class: "studyPlanMetrics" },
    studyPlanProgress(
      "総目標",
      summary.answeredOverall,
      plan.questionGoal,
      `回答済み ${num(summary.answeredOverall)} / ${num(plan.questionGoal)}問`,
      totalStatus,
    ),
    studyPlanProgress(
      "今日",
      summary.answeredToday,
      plan.dailyQuestionGoal,
      `${num(summary.answeredToday)} / ${num(plan.dailyQuestionGoal)}問`,
      `${dailyStatus}・新規${num(summary.answeredToday * STUDY_PLAN_VOCABULARY_PER_QUESTION)}語句`,
    ),
    studyPlanProgress(
      "今週",
      summary.answeredThisWeek,
      summary.weeklyGoal,
      `${num(summary.answeredThisWeek)} / ${num(summary.weeklyGoal)}問`,
      `${weekRange}・${weeklyStatus}`,
    ),
  ));
  panel.appendChild(el("p", { class: "studyPlanAdjustment" },
    summary.weeklyRemaining === 0
      ? "✓ 今週の目標達成"
      : `残り${num(summary.daysRemainingIncludingToday)}日なら、1日${num(summary.adjustedDailyTarget)}問`,
  ));
  panel.appendChild(settings);
  return panel;
}
function renderHomeContent() {
  $("#sessionPanel").classList.add("hide");
  const home = $("#homePanel");
  home.classList.remove("hide");
  home.innerHTML = "";
  if (needsGradeChoice) {
    setChromeTitle("英検 大問1 単語アプリ");
    return renderGradeChoice();
  }
  setChromeTitle(`${datasetHeadline()} 単語アプリ`);

  const total = state.qList.length;
  const learned = state.qList.filter((q) => unit(q).learned).length;
  const finalTotal = allVocabularyItems().length;
  const final = finalProgress(finalTotal);
  const currentDataset = dataset();
  // 意味だけ練習のバッジ・ラベル用（finalTotal とは別名。finalProgress の再判定に巻き込まない）。
  const grade = currentGrade();
  // 各級の収録セットの語彙を読み込むが、通常学習済みの設問に属する語句だけを対象にする。
  // ホーム画面を表示中で、かつ級が変わっていないときだけ再描画
  // （学習セッション中や級の切り替え後に、古い級の数字で画面が奪われないようにする）。
  if (grade && !pooledData(grade)) {
    loadPooledItems(grade).then(() => {
      if (grade === "eiken1") loadStudyPlan();
      if (currentGrade() === grade && !$("#homePanel").classList.contains("hide")) renderHome();
    }).catch(() => { /* オフライン等。次の描画で再試行する。 */ });
  }
  const pooled = pooledData(grade);
  const meaningSummary = grade ? meaningPracticeSummary() : null;
  const meaningItems = pooled ? learnedPooledItems(pooled.items) : [];
  const meaningQueue = pooled ? meaningPracticeQueue(meaningItems, true) : [];
  const meaningDueCount = meaningSummary ? meaningSummary.due : 0;
  const isStudyPlanGrade = currentGrade() === "eiken1";
  const studyPlanEntries = isStudyPlanGrade ? gradeQuestionEntries("eiken1") : [];
  const isFirstVisit = learned === 0;

  // hero は初回訪問（まだ何も学習していない）時だけ表示し、今日の学習カードとの説明重複を避ける
  if (isFirstVisit) {
    home.appendChild(el("section", { class: "card hero" },
      el("p", { class: "label" }, "学習の流れ"),
      el("h2", {}, `${datasetSectionName()}の語句を「覚えてから解く」`),
      el("p", { class: "hint" }, "各設問の4つの選択肢を、意味・補足情報で覚える → 意味を確認 → 本番形式で解く、の3ステップ。"),
    ));
  }

  // 層1：今日の学習（現在セット名・主CTA・その理由）。問題セット選択は独立sectionへ分離。
  const summary = el("section", { class: "card" });
  const headerTitle = final.cleared ? `${datasetHeadline()} CLEAR` : `${datasetHeadline()}を「覚えて→確かめて→解く」`;
  summary.appendChild(el("div", { class: "sectionHead" },
    el("div", {},
      el("p", { class: "label" }, final.cleared ? "達成状況" : "今日の学習"),
      el("h2", {}, headerTitle),
      el("p", { class: "hint" }, currentDataset.label),
    ),
  ));
  // --- 次にやること（Hickの法則：迷わせないため主導線は常に1つに絞る） ---
  const resume = currentResume();
  const resumeIsDone = resume?.stage === "done";
  const meaningResume = resume?.mode === "meaning" && !resumeIsDone;
  const coreResume = Boolean(resume && resume.mode !== "meaning" && !resumeIsDone);
  const nextQ = state.qList.find((q) => !unit(q).learned);
  const canStartFinal = finalUnlocked();
  const hasMeaningDue = Boolean(grade && meaningDueCount > 0);

  if (coreResume) {
    summary.appendChild(el("div", { class: "resumeNotice" },
      el("p", { class: "label" }, "途中保存"),
      el("p", { class: "resumeText" }, resumeDescription(resume)),
      el("p", { class: "hint" }, "この端末に保存されています。続きから再開できます。"),
    ));
  }
  if (resumeRecoveryMessage) {
    summary.appendChild(el("div", { class: "resumeNotice recoveryNotice" },
      el("p", { class: "label" }, "記録の扱い"),
      el("p", { class: "hint" }, resumeRecoveryMessage),
    ));
  }

  // おすすめ（主導線）＝状態に応じて1つだけ決める。詳細な進捗より先に置く。
  let primary;
  if (coreResume) {
    primary = {
      label: "続きから再開する",
      onclick: async () => { if (!(await restoreSession())) renderHome(); },
    };
  } else if (nextQ) {
    primary = {
      label: `第${nextQ}問を学習する`,
      // 初回訪問はheroで同じ3ステップを説明済みのため、ここでは重複させない
      why: isFirstVisit ? "" : "暗記カード → 意味確認 → 本番形式の3ステップで進みます。",
      onclick: () => startLearn(nextQ),
    };
  } else if (canStartFinal && !final.cleared) {
    primary = {
      label: `最終チェック${finalTotal}問に挑戦する`,
      why: `全${finalTotal}語の意味を通しで確認。${finalPassScore(finalTotal)}/${finalTotal}問以上（正答率80%以上）でCLEARです。`,
      onclick: startFinalCheck,
    };
  } else if (hasMeaningDue) {
    // 間隔復習は下の独立カードを主導線にする。もう一周は二次操作へ残す。
    primary = null;
  } else {
    primary = {
      label: "第1問からもう一周する",
      why: "はじめの設問から、覚え直し・解き直しをします。",
      onclick: () => startLearn(state.qList[0]),
    };
  }

  if (primary) {
    const rec = el("div", { class: "recommend" });
    rec.appendChild(el("p", { class: "recEyebrow" }, "▶ まずはここから"));
    rec.appendChild(el("button", { class: "cta startCta", type: "button", onclick: primary.onclick }, primary.label));
    if (primary.why) rec.appendChild(el("p", { class: "recWhy" }, primary.why));
    if (primary.secondary) {
      rec.appendChild(el("div", { class: "actions" },
        el("button", { class: "secondaryCta", type: "button", onclick: primary.secondary.onclick }, primary.secondary.label),
      ));
    }
    summary.appendChild(rec);
  } else {
    summary.appendChild(el("div", { class: "recommend" },
      el("p", { class: "recEyebrow" }, "▶ 今日の復習"),
      el("p", { class: "recWhy" }, "通常学習は完了しています。今日の間隔復習は下のカードから開始します。"),
    ));
    summary.appendChild(el("div", { class: "secondaryActions" },
      el("p", { class: "label" }, "通常学習をやり直す"),
      el("div", { class: "actions" },
        el("button", {
          class: "secondaryCta", type: "button", onclick: () => startLearn(state.qList[0]),
        }, "第1問からもう一周する"),
      ),
    ));
  }
  if (isStudyPlanGrade) summary.appendChild(studyPlanPanel(studyPlanEntries));
  home.appendChild(summary);

  // 語彙目標カード（級単位。問題セットより上位の目標なので、セット一覧より前に置く）
  const learnedVocabulary = isStudyPlanGrade
    ? learnedVocabularyCount("eiken1", studyPlanEntries)
    : (meaningSummary ? meaningSummary.learned : 0);
  const goalCard = grade ? vocabGoalCard(learnedVocabulary, Boolean(pooled)) : null;
  if (goalCard) home.appendChild(goalCard);

  if (grade) {
    home.appendChild(meaningMission(
      meaningSummary,
      Boolean(pooled),
      meaningQueue,
      meaningItems,
      meaningResume ? resume : null,
      coreResume,
      Boolean(primary),
    ));
  }

  // 層2：問題セットUnitカード（独立section。同じ級の過去問・模試を進捗付きで一覧表示）
  home.appendChild(el("section", { class: "card" }, datasetPicker()));

  // 層3：詳細（問題一覧。状態・種別フィルター付き）
  const path = el("section", { class: "card" });
  // 最終チェックの予告。全設問を終える前でも、このセットのゴール（全語句・80%でCLEAR）と残数を示す。
  const finalNote = final.cleared
    ? `✓ このセットはCLEAR済み（最終チェック ${final.bestScore} / ${finalTotal}語）`
    : finalUnlocked()
      ? `全${total}問を学習済み。最終チェック（全${finalTotal}語・${finalPassScore(finalTotal)}問正解でCLEAR）に挑戦できます`
      : `全${total}問を学習すると最終チェック（全${finalTotal}語・正答率80%でCLEAR）。あと${total - learned}問`;
  path.appendChild(el("div", { class: "pathHead" },
    el("p", { class: "label" }, "問題一覧"),
    el("h2", {}, `${datasetHeadline()}（全${total}問）`),
    el("p", { class: "hint" }, "各設問に出る4つの語句を覚えてから、その設問を解きます。クリックで開始。"),
    el("p", { class: "hint finalCheckNote" }, finalNote),
  ));
  const statusCounts = { all: state.qList.length, notStarted: 0, inProgress: 0, done: 0, incorrect: 0 };
  const typeCounts = { all: state.qList.length, word: 0, idiom: 0 };
  state.qList.forEach((q) => {
    statusCounts[questionCardStatus(q)]++;
    if (unit(q).answerResult === "incorrect") statusCounts.incorrect++;
    typeCounts[questionCardType(q)]++;
  });
  const filteredQList = state.qList.filter((q) =>
    questionMatchesStatusFilter(q, questionFilters.status)
    && (questionFilters.type === "all" || questionCardType(q) === questionFilters.type));
  path.appendChild(questionFilterBar({ status: statusCounts, type: typeCounts }));
  if (filteredQList.length) {
    const list = el("div", { class: "itemList" });
    filteredQList.forEach((q) => list.appendChild(buildQuestionCard(q)));
    path.appendChild(list);
  } else {
    path.appendChild(el("div", { class: "questionFilterEmpty" },
      el("p", {}, "条件に合う問題はありません"),
      el("button", { class: "secondaryCta", type: "button", onclick: () => resetQuestionFilters() }, "すべて表示"),
    ));
  }
  home.appendChild(path);

  const canChangeGrade = !new URLSearchParams(window.location.search).has("g");
  if (!sharedMode() || canChangeGrade) {
    const utility = el("section", { class: "card" });
    if (!sharedMode()) {
      utility.appendChild(el("details", { class: "moreDetails" },
        el("summary", { class: "label" }, "その他"),
        el("div", { class: "actions" },
          el("button", {
            class: "ghost", type: "button", onclick: () => {
              if (confirm("すべての進捗を消去します。よろしいですか？")) {
                state.progress = { units: {} };
                saveProgress();
                renderHome();
              }
            },
          }, "進捗リセット"),
        ),
      ));
    }
    if (canChangeGrade) {
      utility.appendChild(el("div", { class: "gradeScopeChange" },
        el("button", {
          class: "ghost smallGhost",
          type: "button",
          onclick: () => {
            if (!confirm("学習する級を変更します。現在の級以外の進捗も消えません。変更しますか？")) return;
            removeStored(scopedStorageKey(GRADE_KEY));
            needsGradeChoice = true;
            renderHome();
          },
        }, "級を変更"),
      ));
    }
    home.appendChild(utility);
  }
}

function renderGradeChoice() {
  const home = $("#homePanel");
  const buttons = GRADE_CHOICE_ORDER.map((code) => el("button", {
    class: "datasetGradeChoice",
    type: "button",
    onclick: async () => {
      writeStored(scopedStorageKey(GRADE_KEY), code);
      if (!applyGradeScope(code)) return;
      needsGradeChoice = false;
      state.datasetId = loadDatasetId();
      await loadData();
      if (code === "1") {
        try { await loadPooledItems("eiken1"); } catch (e) { /* ホーム描画後に再試行する */ }
        loadStudyPlan();
      }
      renderHome();
    },
  }, GRADE_LABELS[code] || code));
  home.appendChild(el("section", { class: "card gradeChoiceCard" },
    el("p", { class: "label" }, "学習範囲"),
    el("h2", {}, "学習する級を選んでください"),
    el("p", { class: "hint" }, "あとから変更できます。"),
    el("div", { class: "datasetGradeChoices", role: "group", "aria-label": "学習する級を選ぶ" }, ...buttons),
  ));
}

/* ---- 問題一覧の状態・種別フィルター（表示専用。永続化・保存キーには影響しない） ---- */
const questionFilters = { status: "all", type: "all" };
const QUESTION_STATUS_LABELS = { all: "すべて", notStarted: "未学習", inProgress: "途中", done: "完了", incorrect: "不正解あり" };
const QUESTION_TYPE_LABELS = { all: "すべて", word: "単語", idiom: "熟語" };

// 「不正解あり」は完了(done)のサブ状態。本番形式で誤答した設問だけに一致する。
function questionMatchesStatusFilter(q, filter) {
  if (filter === "all") return true;
  if (filter === "incorrect") return unit(q).answerResult === "incorrect";
  return questionCardStatus(q) === filter;
}

function resetQuestionFilters() {
  questionFilters.status = "all";
  questionFilters.type = "all";
  renderHome();
}

// 「学習中」は、いま再開できる設問（resume.q）だけに付与する。他の未学習設問との区別を
// 保存データだけから確実に判定できないため、推測で件数を出さない。
function questionCardStatus(q) {
  const u = unit(q);
  if (u.learned) return "done";
  const resume = currentResume();
  if (resume && resume.mode === "learn" && Number(resume.q) === q && resume.stage !== "done") return "inProgress";
  return "notStarted";
}
function questionCardType(q) {
  return state.itemsByQ[q][0].type === "idiom" ? "idiom" : "word";
}

function buildQuestionCard(q) {
  const u = unit(q);
  const status = questionCardStatus(q);
  const items = state.itemsByQ[q];
  const isIdiom = items[0].type === "idiom";
  const words = items.map(surfaceOf).join(" / ");
  const statText = {
      notStarted: "未学習",
      inProgress: "学習中",
      done: u.answerResult === "unknown"
        ? "✓ 学習済み・要確認"
        : u.answerResult === "incorrect"
          ? "✓ 学習済み・不正解あり"
          : "✓ 通常学習済み",
    }[status];
  const metaText = u.attempts > 0 ? `${u.attempts}回挑戦` : `${items.length}語句`;
  const cls = "qCard" + (status === "notStarted" ? "" : ` ${status}`);
  return el("button", { class: cls, type: "button", onclick: () => startLearn(q) },
    el("span", { class: "qCardNumber" }, String(q).padStart(2, "0")),
    el("div", { class: "qCardMain" },
      el("span", { class: "qno" }, `第${q}問 ・ ${isIdiom ? "熟語" : "単語"}`),
      el("span", { class: "qwords" }, words),
      el("span", { class: "qmeta" }, metaText),
      el("span", { class: "qstat" }, statText),
    ),
    el("span", { class: "qCardArrow", "aria-hidden": "true" }, "→"),
  );
}

function questionFilterBar(counts) {
  const statusGroup = el("div", { class: "filterGroup", role: "group", "aria-label": "状態で絞り込む" },
    el("span", { class: "filterGroupLabel", "aria-hidden": "true" }, "状態"),
  );
  for (const key of ["all", "notStarted", "inProgress", "done", "incorrect"]) {
    statusGroup.appendChild(el("button", {
      class: "filterChip",
      type: "button",
      "aria-pressed": String(questionFilters.status === key),
      onclick: () => { questionFilters.status = key; const y = window.scrollY; renderHome(); window.scrollTo(0, y); },
    }, `${QUESTION_STATUS_LABELS[key]} ${counts.status[key]}`));
  }
  const typeGroup = el("div", { class: "filterGroup", role: "group", "aria-label": "種別で絞り込む" },
    el("span", { class: "filterGroupLabel", "aria-hidden": "true" }, "種別"),
  );
  for (const key of ["all", "word", "idiom"]) {
    typeGroup.appendChild(el("button", {
      class: "filterChip",
      type: "button",
      "aria-pressed": String(questionFilters.type === key),
      onclick: () => { questionFilters.type = key; const y = window.scrollY; renderHome(); window.scrollTo(0, y); },
    }, `${QUESTION_TYPE_LABELS[key]} ${counts.type[key]}`));
  }
  return el("div", { class: "questionFilterBar" }, statusGroup, typeGroup);
}

// 語彙目標カード。前の級までは習得済みという前提で、前級目標→当級目標の区間を進捗として見せる。
// 分子の実績は「その級で通常学習まで終えた語句数」（meaningPracticeSummary().learned と同じ母集団）。
function vocabGoalCard(learned, ready) {
  const goal = VOCAB_GOALS[currentGrade()];
  if (!goal) return null;
  const gap = goal.target - goal.prev;
  const own = ready ? Math.min(learned, gap) : 0;
  const value = goal.prev + own;
  const pct = (n) => `${(n / goal.target) * 100}%`;
  const num = (n) => n.toLocaleString("ja-JP");
  const message = !ready ? "読み込み中…"
    : own === 0 ? `ここからが${dataset().shortLabel}の${num(gap)}語。まず1問めから。`
    : own < gap * 0.25 ? "一歩めが出ました。それがいちばん大変。"
    : own < gap * 0.5 ? "歩き出しました。この調子。"
    : own < gap * 0.75 ? "半分をこえました。"
    : "ゴールが見えてきました。";

  const walker = el("div", { class: "vgHedgehog", "aria-hidden": "true", "data-walking": own > 0 ? "1" : "" },
    el("span", { class: "vgHedgehogSprite" }));
  walker.style.left = pct(value);

  const base = el("div", { class: "vgFillBase" });
  base.style.width = pct(goal.prev);
  const ownFill = el("div", { class: "vgFillOwn" });
  ownFill.style.left = pct(goal.prev);
  ownFill.style.width = own > 0 ? `max(3px, ${pct(own)})` : "0";

  const track = el("div", {
    class: "vgTrack",
    role: "progressbar",
    "aria-label": `${dataset().shortLabel}の語彙目標進捗`,
    "aria-valuemin": "0",
    "aria-valuemax": String(goal.target),
    "aria-valuenow": String(value),
    "aria-valuetext": `${dataset().shortLabel}の目標${num(goal.target)}語のうち${num(value)}語。${goal.prevLabel}までの${num(goal.prev)}語に、このアプリで学習した${num(own)}語句を足した数です。`,
  }, base, ownFill, walker);

  const prevTick = el("span", { class: "vgTick vgTickMid" },
    el("strong", {}, num(goal.prev)), el("small", {}, goal.prevLabel));
  prevTick.style.left = pct(goal.prev);

  const forecast = currentGrade() === "eiken1"
    ? (ready
      // detailsにはroleが無くaria-labelledbyが効かないため、名前はsummary自身が持つ。
      ? el("details", { class: "vocabForecast" })
      : el("div", { class: "vocabForecast", "aria-labelledby": "vocabForecastTitle" }))
    : null;
  if (forecast) {
    if (!ready) {
      forecast.appendChild(el("h4", { id: "vocabForecastTitle" }, "このペースで学べる語句"));
      forecast.appendChild(el("p", { class: "hint" }, "英検1級通常問題の語句を読み込み中…"));
    } else {
      const goalForecast = vocabularyGoalForecast(new Date(), studyPlan || defaultStudyPlan(), learned);
      const periods = vocabularyForecast(studyPlan || defaultStudyPlan());
      const forecastSummary = el("summary", { id: "vocabForecastTitle" },
        el("span", { class: "vocabForecastSummaryTitle" }, "このペースで学べる語句"),
        el("span", { class: "vocabForecastLead" },
          `このペースなら14,000語まであと${num(goalForecast.remainingVocabulary)}語`),
      );
      forecast.appendChild(forecastSummary);
      forecast.appendChild(el("p", { class: "hint vocabForecastDate" }, goalForecast.remainingVocabulary === 0
        ? "14,000語の目安に到達しています。"
        : `1日${num(goalForecast.dailyVocabulary)}語句で、${goalForecast.estimatedDate.toLocaleDateString("ja-JP", { year: "numeric", month: "long", day: "numeric" })}ごろ（あと${num(goalForecast.daysToGoal)}日）`));
      forecast.appendChild(el("div", { class: "vocabForecastGrid", "aria-label": "期間別の理論上の語句予測" },
        ...periods.map(({ days, vocabulary }) => {
          const label = { 7: "1週間後", 30: "1か月後", 90: "3か月後", 180: "半年後", 365: "1年後" }[days] || `${days}日後`;
          return el("div", { class: "vocabForecastRow" },
            el("span", {}, label),
            el("strong", {}, `+${num(vocabulary)}語句`),
          );
        })),
      );
      forecast.appendChild(el("p", { class: "hint" },
        `理論上の学習量です。現在、このアプリの英検1級通常問題には${num(gradeVocabularyItems("eiken1").length)}語句を収録しています。このアプリだけの収録数を超える予測を含みます。`));
    }
  }

  return el("section", { class: "card vocabGoalCard", "aria-labelledby": "vocabGoalTitle" },
    el("div", { class: "vgHead" },
      el("div", {},
        el("p", { class: "label" }, "語彙の目標"),
        el("h3", { id: "vocabGoalTitle" }, `${dataset().shortLabel}の語彙 ${num(goal.target)}語`),
      ),
      el("p", { class: "vgCount" },
        el("strong", {}, num(value)),
        el("span", {}, ` 語 / ${num(goal.target)}語`)),
    ),
    el("div", { class: "vgBar" }, track,
      el("div", { class: "vgTicks" },
        el("span", { class: "vgTick vgTickStart" }, el("strong", {}, "0")),
        prevTick,
        el("span", { class: "vgTick vgTickEnd" },
          el("strong", {}, num(goal.target)), el("small", {}, dataset().shortLabel)),
      ),
    ),
    el("p", { class: "vgMessage" }, message),
    el("p", { class: "hint" },
      `${goal.prevLabel}までの${num(goal.prev)}語は習得済みとして計算しています。このアプリで学習した語句は${ready ? num(own) : "—"}語句。語彙数は目安です。`),
    forecast,
  );
}

function meaningMission(
  summary,
  ready,
  nextQueue = [],
  learnedItems = [],
  meaningResume = null,
  coreResume = false,
  hasPrimaryCta = false,
) {
  const total = summary.total;
  const learned = summary.learned;
  const due = summary.due;
  const batch = nextQueue.length || Math.min(due, MEANING_SESSION_SIZE);
  const remaining = Math.max(0, due - batch);
  const mission = el("section", {
    class: "card spacedReviewCard",
    "aria-labelledby": "spacedReviewCardTitle",
  },
    el("p", { class: "label" }, "間隔復習"),
    el("h3", { id: "spacedReviewCardTitle" }, `意味だけ復習（${dataset().shortLabel}）`),
    el("p", { class: "meaningMissionLead" },
      `${datasetSectionName()}の収録セットをまとめ、通常学習で最後まで解いた設問の語句を1回最大${MEANING_SESSION_SIZE}語句で復習します。正解すると1・3・7・14日後へ進みます。`),
    el("div", { class: "meaningMissionMetrics" },
      el("div", {}, el("strong", {}, ready ? `${learned} / ${total}` : "—"), el("span", {}, "対象語句")),
      el("div", { class: ready && due > 0 ? "meaningMissionMetricDue" : "" }, el("strong", {}, ready ? `${due}語句` : "—"), el("span", {}, "今すぐ復習")),
    ),
  );

  if (ready && learned > 0) {
    mission.appendChild(meaningIntervalBreakdown(learnedItems));
  } else if (ready) {
    mission.appendChild(el("p", { class: "hint" }, "まだ意味だけ復習の対象語句がありません。通常学習で本番形式まで解くと対象に加わります。"));
  }
  const otherDue = otherGradeDueCounts();
  if (otherDue.length) {
    const list = el("div", { class: "meaningMissionOtherGradeList" });
    otherDue.forEach((row) => {
      list.appendChild(el("button", {
        class: "ghost meaningMissionOtherGrade",
        type: "button",
        "aria-label": `${row.label}の復習待ち${row.count}語句へ移動`,
        onclick: () => switchDataset(row.datasetId),
      }, el("strong", {}, row.label), el("span", {}, `${row.count}語句`)));
    });
    mission.appendChild(el("div", { class: "meaningMissionOtherGrades" },
      el("p", { class: "label" }, "他の級の復習待ち"),
      list,
    ));
  }
  if (meaningResume) {
    mission.appendChild(el("div", { class: "resumeNotice" },
      el("p", { class: "label" }, "途中保存"),
      el("p", { class: "resumeText" }, resumeDescription(meaningResume)),
      el("p", { class: "hint" }, "意味だけ復習の続きから再開できます。"),
    ));
  }
  if (coreResume) {
    mission.appendChild(el("p", { class: "hint" }, "通常学習の続きがあるため、先に再開するのがおすすめです。"));
  }

  const buttonAttrs = { class: "cta reviewCta meaningMissionCta", type: "button", disabled: "disabled" };
  let buttonLabel = "対象を確認中…";
  let note = "";
  if (meaningResume && ready) {
    buttonLabel = "意味だけ復習の続きを再開する";
    delete buttonAttrs.disabled;
    buttonAttrs.onclick = async () => { if (!(await restoreSession())) renderHome(); };
  } else if (ready && learned === 0) {
    buttonLabel = "通常学習後に利用できます";
  } else if (ready && due === 0) {
    buttonLabel = "今すぐ復習する語句はありません";
  } else if (ready) {
    buttonLabel = `今回の${batch}語句を復習する`;
    delete buttonAttrs.disabled;
    buttonAttrs.onclick = () => startMeaningPractice(true, nextQueue);
    if (remaining > 0) note = `今すぐ復習する${due}語句のうち、今回は${batch}語句を出題します。残り${remaining}語句は次回に回ります。`;
  }
  // 1画面の塗りCTAは1つ。主CTAがある限り、間隔復習は二次操作に落とす。
  // 主CTAが null（通常学習が終わり、間隔復習が実質の主導線になる分岐）のときだけ塗りのまま残す。
  if (hasPrimaryCta) buttonAttrs.class = "secondaryCta meaningMissionCta";
  mission.appendChild(el("button", buttonAttrs, buttonLabel));
  if (note) mission.appendChild(el("p", { class: "hint" }, note));
  return mission;
}

function datasetGrades() {
  const grades = [];
  for (const [id] of availableDatasets()) {
    const grade = gradeOf(id);
    if (grade && !grades.includes(grade)) grades.push(grade);
  }
  return grades;
}

function datasetGradeLabel(grade) {
  const entry = availableDatasets().find(([id]) => gradeOf(id) === grade);
  return entry ? entry[1].shortLabel : grade;
}

function datasetSetKind(datasetId) {
  if (datasetIsTopic(datasetId)) return "テーマ別";
  if (gradeOf(datasetId) === "iuhw") return "基礎試験";
  return datasetId.includes("-mock-") ? "模試" : "過去問";
}

function datasetSetLabel(datasetId, data) {
  const prefix = String(datasetId || "").startsWith("eiken") ? `英検${data.shortLabel || ""}` : "";
  let label = String(data.label || "");
  if (prefix && label.startsWith(prefix)) label = label.slice(prefix.length).trim();
  if (datasetSetKind(datasetId) === "模試") label = label.replace(/^模試\s*/, "");
  return label || data.label || datasetId;
}

// 保存形式は変えず、Unitカード表示用の数値・状態だけを読み取り専用で算出する。
function datasetSummary(datasetId, data) {
  const isCurrent = datasetId === state.datasetId;
  const progress = progressFor(datasetId);
  const units = Object.values((progress && progress.units) || {});
  const learnedQuestions = units.filter((u) => u.learned).length;
  const cleared = Boolean(progress && progress.finalCheck && progress.finalCheck.cleared);
  const resume = resumableResume(progress && progress.resume);
  const hasResume = Boolean(resume && resume.stage !== "done");
  const totalQuestions = isCurrent
    ? state.qList.length
    : (Number.isInteger(data.totalQuestions) ? data.totalQuestions : null);
  const totalVocabulary = isCurrent
    ? allVocabularyItems().length
    : (Number.isInteger(data.totalVocabulary) ? data.totalVocabulary : null);
  let status = "notStarted";
  if (cleared) status = "cleared";
  else if (learnedQuestions > 0) status = "inProgress";
  else if (hasResume) status = "resumable";
  return {
    totalQuestions,
    totalVocabulary,
    learnedQuestions,
    cleared,
    resume,
    hasResume,
    status,
  };
}

function datasetPrimaryLabel(summary) {
  if (summary.status === "cleared") return "もう一周する";
  const resumeQuestion = Number(summary.resume?.q);
  const resumeLabel = Number.isInteger(resumeQuestion)
    ? `続きから再開する（第${resumeQuestion}問）`
    : "続きから再開する";
  if (summary.status === "resumable") return resumeLabel;
  if (summary.status === "inProgress" && summary.hasResume) return resumeLabel;
  return "この回を始める";
}

// 1枚のUnitカード。番号は表示順（この級・この種別内の並び順）であり、永続IDとしては保存しない。
function datasetUnitCard(id, data, index) {
  const isCurrent = id === state.datasetId;
  const summary = datasetSummary(id, data);
  const label = datasetPrimaryLabel(summary);
  const totalQ = summary.totalQuestions != null ? summary.totalQuestions : "—";
  const totalV = summary.totalVocabulary != null ? summary.totalVocabulary : "—";
  const progressLine = `${summary.learnedQuestions} / ${totalQ}問`;
  const resumeText = summary.hasResume ? `途中保存：${resumeDescription(summary.resume)}` : "";
  const cls = ["datasetUnitCard"];
  if (isCurrent) cls.push("current");
  if (summary.cleared) cls.push("cleared");
  const ariaParts = [datasetSetLabel(id, data), progressLine];
  if (summary.cleared) ariaParts.push("CLEAR");
  if (resumeText) ariaParts.push(resumeText);
  ariaParts.push(label);
  const attrs = {
    class: cls.join(" "),
    type: "button",
    "aria-label": ariaParts.join("・"),
    onclick: async () => {
      if (!isCurrent) {
        switchDataset(id);
        return;
      }
      if (summary.hasResume) {
        if (!(await restoreSession())) renderHome();
        return;
      }
      const nextQ = state.qList.find((q) => !unit(q).learned) || state.qList[0];
      if (nextQ != null) startLearn(nextQ);
    },
  };
  if (isCurrent) attrs["aria-current"] = "true";
  return el("button", attrs,
    el("span", { class: "datasetUnitCardNumber" }, String(index + 1).padStart(2, "0")),
    el("div", { class: "datasetUnitCardMain" },
      el("span", { class: "datasetUnitCardTitle" }, datasetSetLabel(id, data)),
      el("span", { class: "datasetUnitCardMeta" }, `全${totalQ}問・${totalV}語`),
      el("span", { class: "datasetUnitCardProgress" }, progressLine),
      summary.cleared
        ? el("span", { class: "datasetUnitCardClear" }, "✓ CLEAR")
        : null,
      summary.hasResume ? el("span", { class: "datasetUnitCardResume" }, resumeText) : null,
      el("span", { class: "datasetUnitCardAction" }, label),
    ),
    el("span", { class: "datasetUnitCardArrow", "aria-hidden": "true" }, "→"),
  );
}

// 同じ級の問題セットを種別ごとの小見出しに分けてUnitカードで並べる。
function datasetUnitCards(grade) {
  const entries = availableDatasets().filter(([id]) => gradeOf(id) === grade);
  const wrap = el("div", { class: "datasetUnitCards" });
  for (const kind of ["過去問", "模試", "テーマ別", "基礎試験"]) {
    const groupEntries = entries.filter(([id]) => datasetSetKind(id) === kind);
    if (!groupEntries.length) continue;
    wrap.appendChild(el("p", { class: "datasetUnitGroupLabel" }, `${datasetGradeLabel(grade)}・${kind}`));
    const grid = el("div", { class: "datasetUnitGrid" });
    groupEntries.forEach(([id, data], i) => grid.appendChild(datasetUnitCard(id, data, i)));
    wrap.appendChild(grid);
  }
  return wrap;
}

function datasetPicker() {
  const grades = datasetGrades();
  let pickerGrade = currentGrade() || grades[0];
  const wrap = el("div", { class: "datasetPicker" });
  const current = el("p", { class: "datasetPickerCurrent", "aria-live": "polite" });
  const gradeChoices = el("div", {
    class: "datasetGradeChoices",
    role: "group",
    "aria-label": "級を選ぶ",
  });
  const cardsHost = el("div", { class: "datasetUnitCardsHost" });

  function renderCards() {
    cardsHost.innerHTML = "";
    cardsHost.appendChild(datasetUnitCards(pickerGrade));
    const currentDatasetGrade = currentGrade();
    const currentLabel = `${dataset().label}${datasetCleared(state.datasetId) ? " ✅" : ""}`;
    current.textContent = currentDatasetGrade === pickerGrade
      ? `現在：${currentLabel}`
      : `現在：${currentLabel} ／ ${datasetGradeLabel(pickerGrade)}の回を選ぶと切り替わります`;
  }

  // 押下時に全ボタンを作り直すと新規ノードになりCSS transitionが効かないため、
  // 初回だけ生成し、以降はaria-pressedの更新のみで同じノードの背景色を切り替える。
  function renderGradeChoices() {
    if (gradeChoices.children.length) {
      [...gradeChoices.children].forEach((btn, i) => {
        btn.setAttribute("aria-pressed", String(grades[i] === pickerGrade));
      });
      return;
    }
    for (const grade of grades) {
      gradeChoices.appendChild(el("button", {
        class: "datasetGradeChoice",
        type: "button",
        "aria-pressed": String(grade === pickerGrade),
        onclick: () => {
          pickerGrade = grade;
          renderGradeChoices();
          renderCards();
        },
      }, datasetGradeLabel(grade)));
    }
  }

  wrap.appendChild(el("span", { class: "fieldLabel" }, "問題セット"));
  if (grades.length > 1) wrap.appendChild(gradeChoices);
  wrap.appendChild(current);
  wrap.appendChild(cardsHost);
  renderGradeChoices();
  renderCards();
  return wrap;
}

function answerActions(...buttons) {
  return el("div", { class: "actions answerActions" }, ...buttons);
}

function prefersReducedMotion() {
  return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}
function revealAnswerActions(actions) {
  requestAnimationFrame(() => {
    actions.scrollIntoView({ behavior: prefersReducedMotion() ? "auto" : "smooth", block: "center" });
  });
}

function allVocabularyItems() {
  return state.qList.flatMap((q) => state.itemsByQ[q] || []);
}

function finalUnlocked() {
  return state.qList.length > 0
    && state.qList.every((q) => unit(q).learned);
}
/* ============================================================
   LEARN FLOW (per question)
   stages: flash -> check -> practice -> done
   ============================================================ */
let session = null;

function resetSessionScroll() {
  window.scrollTo({ top: 0, left: 0, behavior: "auto" });
}

function startLearn(q) {
  const items = state.itemsByQ[q];
  if (!Array.isArray(items) || !items.length) {
    renderHome();
    return false;
  }
  session = {
    mode: "learn",
    q,
    items: shuffle(items),
    stage: "flash",
    flashIdx: 0,
    checkOrder: shuffle(items),
    checkIdx: 0,
    checkAnswered: false,
    meaningCorrect: 0,
  };
  renderSession();
  resetSessionScroll();
  return true;
}

// 語句の進捗を、その語句が属する回（item._datasetId、無ければ現在の回）から読み取る。
function readItemStateOf(item) {
  return readItemState(progressFor(item._datasetId || state.datasetId), itemKeyOf(item));
}
function isItemDue(item, now = Date.now()) {
  const itemState = readItemStateOf(item);
  // 旧形式の意味記録には回答時刻がないため、新仕様で一度だけ対象に戻す。
  if (!itemState.lastAnsweredAt) return true;
  const nextReviewAt = itemState.nextReviewAt;
  return !nextReviewAt || new Date(nextReviewAt).getTime() <= now;
}
// 誤答・直近の遅い正答・期限超過を合成して前に出す。
function weightedOrder(items) {
  // ES2019以降 Array#sort は安定。同点の並びはシャッフル順のままにする。
  const shuffled = shuffle(items);
  const now = Date.now();
  const dayMs = 24 * 60 * 60 * 1000;
  const scores = new Map(shuffled.map((item) => {
    const s = readItemStateOf(item);
    const overdueMs = s.nextReviewAt ? now - new Date(s.nextReviewAt).getTime() : 0;
    const overdueDays = Number.isFinite(overdueMs) ? Math.max(0, overdueMs / dayMs) : 0;
    // lastGradeは保存しない制約のため、絶対床以上の「直近の正答RT」をHard相当として復元する。
    const hard = Number.isFinite(s.lastMs) && s.lastMs >= RT_HARD_FLOOR_MS ? 1 : 0;
    return [item, 2 * (Number(s.wrongCount) || 0) + hard + 0.5 * overdueDays];
  }));
  return shuffled.sort((a, b) => scores.get(b) - scores.get(a));
}
// dueOnly=true: 復習日が来た語だけ。未学習語句や次回予定の語句は補充しない。
function meaningPracticeQueue(items, dueOnly) {
  return withProgressReadCache(() => {
    const candidates = dueOnly ? items.filter((it) => isItemDue(it)) : items;
    return weightedOrder(candidates).slice(0, MEANING_SESSION_SIZE);
  });
}

async function startMeaningPractice(dueOnly = true, queueOverride = null) {
  const grade = currentGrade();
  let queue;
  if (grade) {
    let pooled;
    try {
      pooled = await loadPooledItems(grade);
    } catch (e) {
      // オフライン等で収録セットを読めないときは、ホームに戻して次の操作で再試行させる。
      renderHome();
      return false;
    }
    queue = Array.isArray(queueOverride)
      ? queueOverride
      // await をまたがない同期ブロックとしてまとめて読む
      : withProgressReadCache(() => meaningPracticeQueue(learnedPooledItems(pooled.items), dueOnly));
  } else {
    // 級を判定できないdatasetIdへの保険。現在の回の語句だけで組む。
    queue = shuffle(allVocabularyItems()).slice(0, MEANING_SESSION_SIZE);
  }
  if (!queue.length) {
    renderHome();
    return false;
  }
  session = {
    mode: "meaning",
    q: null,
    items: queue,
    stage: "check",
    checkOrder: queue,
    checkIdx: 0,
    checkAnswered: false,
    meaningCorrect: 0,
    meaningWrongItems: [],
    meaningWrongChecked: [],
    dueOnly: Boolean(grade) && dueOnly,
    meaningVersion: grade ? MEANING_PROGRESS_VERSION : null,
    meaningBatchSize: grade ? MEANING_SESSION_SIZE : null,
  };
  renderSession();
  resetSessionScroll();
  return true;
}

function startFinalCheck() {
  if (!finalUnlocked()) {
    renderHome();
    return false;
  }
  const queue = shuffle(allVocabularyItems());
  session = {
    mode: "final",
    q: null,
    items: queue,
    stage: "check",
    checkOrder: queue,
    checkIdx: 0,
    checkAnswered: false,
    finalCorrect: 0,
    // 完了画面で「今回が初回CLEARかどうか」を判定するため、挑戦開始時点の状態を記録する。
    wasClearedBeforeAttempt: finalProgress(queue.length).cleared,
  };
  renderSession();
  resetSessionScroll();
  return true;
}

function renderSession() {
  saveResume();
  $("#homePanel").classList.add("hide");
  const panel = $("#sessionPanel");
  panel.classList.remove("hide");
  panel.classList.toggle("hasActionBar", session.stage === "flash");
  panel.innerHTML = "";

  const isMeaning = session.mode === "meaning";
  const isFinal = session.mode === "final";
  const q = session.q;
  const isIdiom = !isMeaning && !isFinal && session.items[0].type === "idiom";

  // 長いカードをスクロールしても現在地・戻る操作を見失わないための補助バー
  panel.appendChild(sessionStickyNav(q, isMeaning, isFinal));

  // header
  panel.appendChild(el("div", { class: "itemHead" },
     el("div", {},
       el("p", { class: "label" }, sessionLabel(q, isIdiom, isMeaning, isFinal)),
       el("h2", {}, stageTitle(session.stage)),
       el("p", { class: "sessionState" }, "中断してもこの位置から再開できます"),
     ),
  ));

  // stage bar
  if (isFinal) panel.appendChild(finalBar());
  else if (isMeaning) panel.appendChild(meaningBar());
  else panel.appendChild(stageBar(session.stage));
  // 意味だけ復習セッション中はプール解放率のバーを出さない。解放状況はホームの間隔復習カードが持ち、
  // セッション中の位置・正誤数は meaningBar に集約する（設問へ早く到達させるため画面上部を短くする）。
  if (!isMeaning) panel.appendChild(questionProgressBar());

  const body = el("div", {});
  panel.appendChild(body);

  if (session.stage === "flash") renderFlash(body);
  else if (session.stage === "check") renderCheck(body);
  else if (session.stage === "meaningReview") renderMeaningWrongReview(body);
  else if (session.stage === "practice") renderPractice(body);
  else if (session.stage === "done") renderDone(body);
}

// 元のitemHead/stageBar/q1Progressは残したまま、スクロール中も現在地が分かる補助バーを上に固定する。
function sessionStickyNav(q, isMeaning, isFinal) {
  const total = state.qList.length;
  const reviewChecked = session.meaningWrongChecked?.length || 0;
  const reviewTotal = session.meaningWrongItems?.length || 0;
  const posLabel = isFinal
    ? `${session.checkIdx + 1} / ${session.checkOrder.length}`
    : isMeaning && session.stage === "meaningReview"
      ? `見直し ${reviewChecked} / ${reviewTotal}`
      : isMeaning
        ? `${session.checkIdx + 1} / ${session.checkOrder.length}`
        : (q != null && total ? `第${state.qList.indexOf(q) + 1} / ${total}問` : "");
  const stageLabel = {
    flash: "覚える", check: "確かめる", meaningReview: "見直し", practice: "解く", done: "完了",
  }[session.stage] || "";
  return el("div", { class: "sessionStickyNav" },
    el("button", { class: "sessionStickyBack ghost", type: "button", onclick: () => { saveResume(); renderHome(); } }, "一覧へ戻る"),
    el("span", { class: "sessionStickyPos" }, posLabel),
    el("span", { class: "sessionStickyStage" }, stageLabel),
  );
}

function sessionLabel(q, isIdiom, isMeaning, isFinal) {
  if (isFinal) return `最終チェック ${session.checkIdx + 1} / ${session.checkOrder.length}`;
  if (isMeaning) {
    // 位置「n / m」は現在地バーと meaningBar が持つ。ここでは種別名だけを出して重複を避ける。
    return session.stage === "meaningReview" ? "意味だけ復習・見直し" : "意味だけ復習";
  }
  return `第${q}問 ・ ${isIdiom ? "熟語" : "単語"}`;
}

function stageTitle(stage) {
  if (session && session.mode === "final") return `最終チェック${session.checkOrder.length}問`;
  if (session && session.mode === "meaning" && session.stage === "meaningReview") return "間違えた語句を見直す";
  if (session && session.mode === "meaning") return `意味だけの復習（最大${MEANING_SESSION_SIZE}語句）`;
  return {
    flash: "STEP 1　覚える（暗記カード）",
    check: "STEP 2　確かめる（4語句の意味確認）",
    practice: "STEP 3　解く（本番形式）",
    done: "完了",
  }[stage];
}

function meaningBar() {
  if (session.stage === "meaningReview") {
    const total = session.meaningWrongItems?.length || 0;
    const checked = session.meaningWrongChecked?.length || 0;
    return el("div", { class: "stageBar meaningBar" },
      el("div", { class: "stagePill active" }, `誤答 ${total}語句`),
      el("div", { class: "stagePill" }, `確認済 ${checked} / ${total}`),
    );
  }
  const answered = session.checkIdx + (session.checkAnswered ? 1 : 0);
  // 位置は「n / m語句」で示す（現在地バーと同じ数え方）。「残り」の逆算はさせない。
  return el("div", { class: "stageBar meaningBar" },
    el("div", { class: "stagePill active" },
      `${session.checkIdx + 1} / ${session.checkOrder.length}語句`),
    el("div", { class: "stagePill" },
      `回答済 ${answered} / 正解 ${session.meaningCorrect}`),
  );
}

function refreshMeaningBar() {
  if (!session || session.mode !== "meaning") return;
  const bar = document.querySelector("#sessionPanel .meaningBar");
  if (!bar) return;
  const answered = session.checkIdx + (session.checkAnswered ? 1 : 0);
  const pills = bar.querySelectorAll(".stagePill");
  if (pills[0]) pills[0].textContent = `${session.checkIdx + 1} / ${session.checkOrder.length}語句`;
  if (pills[1]) pills[1].textContent = `回答済 ${answered} / 正解 ${session.meaningCorrect}`;
}

function finalBar() {
  return el("div", { class: "stageBar meaningBar" },
    el("div", { class: "stagePill active" },
      `最終チェック ${session.checkIdx + 1} / ${session.checkOrder.length}`),
    el("div", { class: "stagePill" },
      `回答済 ${session.checkIdx} / 正解 ${session.finalCorrect}`),
  );
}

function stageBar(stage) {
  const order = ["flash", "check", "practice"];
  const cur = order.indexOf(stage);
  const labels = { flash: "1 覚える", check: "2 確かめる", practice: "3 解く" };
  const bar = el("div", { class: "stageBar", role: "list", "aria-label": "学習ステップ" });
  order.forEach((s, i) => {
    let cls = "stagePill";
    if (stage === "done" || i < cur) cls += " cleared";
    if (s === stage) cls += " active";
    bar.appendChild(el("div", { class: cls, role: "listitem", "aria-current": s === stage ? "step" : "false" }, labels[s]));
  });
  return bar;
}

// キー単位で直近値を覚え、値が変わった回だけ残数のsettleと装飾fillのtransitionを発火する。
// リロード直後は前回値がないため発火しない（DESIGN.mdの完成条件どおり）。
const lastProgressByKey = {};
function progressTransition(key, value, total) {
  const prev = lastProgressByKey[key];
  lastProgressByKey[key] = { value, total };
  if (!prev || prev.total !== total || prev.value === value) return { settle: false, from: null };
  return { settle: true, from: prev.value };
}
function appendProgressFill(wrap, value, total, animateFrom) {
  const pct = (v) => (total ? Math.min(100, Math.max(0, (v / total) * 100)) : 0);
  const fill = el("div", { class: "q1ProgressFill" });
  const track = el("div", { class: "q1ProgressTrack", "aria-hidden": "true" }, fill);
  if (animateFrom != null && !prefersReducedMotion()) {
    fill.style.width = pct(animateFrom) + "%";
    wrap.appendChild(track);
    requestAnimationFrame(() => requestAnimationFrame(() => { fill.style.width = pct(value) + "%"; }));
  } else {
    fill.style.width = pct(value) + "%";
    wrap.appendChild(track);
  }
}

function questionProgressBar() {
  const total = state.qList.length;
  if (!total) return el("div", { class: "q1Progress hide" });

  const isQuestionSession = session.q != null;
  const current = isQuestionSession
    ? Math.max(1, state.qList.indexOf(session.q) + 1)
    : state.qList.filter((q) => unit(q).learned).length;
  const value = Math.min(total, current);
  const remaining = Math.max(0, total - value);
  const label = isQuestionSession ? `第${value}問 / ${total}問` : `通常学習済み ${value} / ${total}問`;
  const t = progressTransition(`q:${state.datasetId}`, value, total);
  const settleCls = t.settle ? " progressSettle" : "";

  const wrap = el("div", { class: "q1Progress" },
    el("div", { class: "q1ProgressHead" },
      el("span", { class: "label" }, `${datasetSectionName()} 設問進捗`),
      el("strong", { class: "q1ProgressValue" + settleCls }, label),
      el("span", { class: "q1ProgressRemaining" + settleCls }, `残り${remaining}問`),
    ),
  );
  const progress = el("progress", {
    class: "q1ProgressBar",
    max: total,
    value,
    "aria-label": `${datasetSectionName()}の設問進捗`,
  });
  progress.setAttribute("aria-valuetext", `${label}、残り${remaining}問`);
  wrap.appendChild(progress);
  // 覚える（暗記カード）ステージでは全幅の塗りバーを出さない。1問ずつ読み進める段階では
  // 25問中どこかは操作の判断に使えず、Clay塗りのバーがカード見出しを画面下へ押し下げる。
  // 数値行（第n問 / m問）とスクリーンリーダー用<progress>は残す。
  if (!session || session.stage !== "flash") appendProgressFill(wrap, value, total, t.from);
  return wrap;
}

/* ---- STEP 1: flashcards ---- */
function buildFlashCard(item) {
  const card = el("div", { class: "flash" });
  const head = el("div", { class: "flashHead" });
  const surface = surfaceOf(item);
  const surfaceKey = String(surface || "").toLowerCase();
  const displayLemma = flashcardDisplayLemmaMap[surfaceKey]
    || (item.type === "word" ? flashcardLemmaMap[surfaceKey] : "");
  const headword = displayLemma || canonicalHeadwordOf(item);
  const learning = learningEntryOf(item);
  const wordLine = el("div", { class: "flashWordLine" },
    el("div", { class: "flashWord" }, headword),
  );
  if (learning.ipa) wordLine.appendChild(el("div", { class: "flashIpa" }, learning.ipa));
  if (vocabularyAudioEnabled(item)) wordLine.appendChild(buildVocabAudioButton(item, "flashListenButton", true));
  const headContent = el("div", {}, wordLine);
  if (headword !== surface) {
    const lemmaNote = el("div", { class: "flashLemmaNote" },
      el("span", { class: "flashLemmaLabel" }, "出題形"),
      el("span", { class: "flashLemmaSurface" }, surface),
    );
    headContent.appendChild(lemmaNote);
  }
  headContent.appendChild(el("div", { class: "flashPos" }, learningPosOf(item)));
  head.appendChild(headContent);
  card.appendChild(head);

  const inner = el("div", { class: "flashBody" });
  inner.appendChild(flashRow("意味", learning.meaning || item.meaning, "flashMeaning"));
  if (item.type === "word") {
    const wordOrigin = flashWordOrigin(item);
    if (wordOrigin) inner.appendChild(wordOrigin);
  } else if (item.type === "idiom" && item.coreImage) {
    inner.appendChild(flashCoreImage(item));
  }
  if (item.example) inner.appendChild(flashExampleRow(item));
  card.appendChild(inner);
  return card;
}

function scrollFlashCardIntoView() {
  const flash = $("#sessionPanel .flash");
  if (!flash) return;
  const sticky = $("#sessionPanel .sessionStickyNav");
  const stickyHeight = sticky ? sticky.getBoundingClientRect().height : 0;
  const target = flash.getBoundingClientRect().top + window.scrollY - stickyHeight - 8;
  window.scrollTo({ top: Math.max(0, target), left: 0, behavior: "auto" });
}

// 暗記カードのスワイプは、既存の前へ／次へボタンを補助する操作。
// 現在の表示位置と指の速度から始めることで、途中でつかみ直しても動きが飛ばないようにする。
function flashTranslateX(card) {
  const transform = getComputedStyle(card).transform;
  if (!transform || transform === "none") return 0;
  const matrix3d = transform.match(/^matrix3d\(([^)]+)\)$/);
  if (matrix3d) return Number(matrix3d[1].split(",")[12]) || 0;
  const matrix = transform.match(/^matrix\(([^)]+)\)$/);
  return matrix ? Number(matrix[1].split(",")[4]) || 0 : 0;
}

function setFlashGestureTransform(card, x) {
  const rotation = Math.max(-4, Math.min(4, x * 0.025));
  const opacity = Math.max(0.86, 1 - Math.abs(x) / 1400);
  card.style.transform = `translate3d(${x.toFixed(2)}px, 0, 0) rotate(${rotation.toFixed(2)}deg)`;
  card.style.opacity = opacity.toFixed(3);
}

function clearFlashGesture(card) {
  card.classList.remove("gestureActive");
  card.style.transform = "";
  card.style.opacity = "";
  card.style.willChange = "";
}

function stopFlashSpring(card) {
  if (!card._flashGestureRaf) return;
  cancelAnimationFrame(card._flashGestureRaf);
  card._flashGestureRaf = 0;
}

function animateFlashGesture(card, target, initialVelocity = 0, onComplete = null) {
  stopFlashSpring(card);
  if (prefersReducedMotion()) {
    clearFlashGesture(card);
    if (onComplete) onComplete();
    return;
  }

  card.classList.add("gestureActive");
  let position = flashTranslateX(card);
  let velocity = Math.max(-3200, Math.min(3200, Number(initialVelocity) || 0));
  let previousTime = performance.now();
  const stiffness = 360;
  const damping = 2 * Math.sqrt(stiffness); // 臨界減衰: 反発は指が勢いを持ったときだけ残す
  const step = (now) => {
    if (!card.isConnected) return;
    const delta = Math.min(0.032, Math.max(0.001, (now - previousTime) / 1000));
    previousTime = now;
    velocity += ((target - position) * stiffness - velocity * damping) * delta;
    position += velocity * delta;
    setFlashGestureTransform(card, position);
    if (Math.abs(target - position) < 0.5 && Math.abs(velocity) < 8) {
      setFlashGestureTransform(card, target);
      card._flashGestureRaf = 0;
      clearFlashGesture(card);
      if (onComplete) onComplete();
      return;
    }
    card._flashGestureRaf = requestAnimationFrame(step);
  };
  card._flashGestureRaf = requestAnimationFrame(step);
}

function flashRubberband(overshoot, dimension, constant = 0.55) {
  return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
}

function setupFlashGesture(card, canGoBack, canGoForward) {
  let pointerId = null;
  let startX = 0;
  let startY = 0;
  let startOffset = 0;
  let horizontal = false;
  let samples = [];

  const releasePointer = () => {
    if (pointerId == null) return;
    if (card.hasPointerCapture(pointerId)) card.releasePointerCapture(pointerId);
    pointerId = null;
  };

  const remember = (x, time) => {
    samples.push({ x, time });
    if (samples.length > 5) samples.shift();
  };

  const releaseVelocity = () => {
    if (samples.length < 2) return 0;
    const first = samples[Math.max(0, samples.length - 3)];
    const last = samples[samples.length - 1];
    const elapsed = Math.max(1, last.time - first.time);
    return ((last.x - first.x) / elapsed) * 1000;
  };

  const cancelTracking = () => {
    horizontal = false;
    samples = [];
    releasePointer();
  };

  const finish = (event, cancelled = false) => {
    if (pointerId !== event.pointerId) return;
    const position = flashTranslateX(card);
    remember(position, performance.now());
    const velocity = releaseVelocity();
    const canCommit = !cancelled && horizontal
      && (Math.abs(position) >= 56 || Math.abs(velocity) >= 480)
      && ((position < 0 && canGoForward) || (position > 0 && canGoBack));
    const direction = position < 0 ? 1 : -1;
    horizontal = false;
    releasePointer();
    card.classList.remove("gestureActive");

    if (!canCommit) {
      animateFlashGesture(card, 0, velocity);
      return;
    }

    armFlashNavGuard();
    const exitTarget = direction > 0
      ? -Math.max(window.innerWidth * 0.88, 280)
      : Math.max(window.innerWidth * 0.88, 280);
    animateFlashGesture(card, exitTarget, velocity, () => {
      if (!card.isConnected) return;
      if (direction > 0) {
        if (session.flashIdx === session.items.length - 1) session.stage = "check";
        else session.flashIdx++;
      } else {
        session.flashIdx = Math.max(0, session.flashIdx - 1);
      }
      renderSession();
      scrollFlashCardIntoView();
    });
  };

  card.addEventListener("pointerdown", (event) => {
    if (pointerId != null || (event.pointerType === "mouse" && event.button !== 0) || flashNavLocked()) return;
    const target = event.target instanceof Element ? event.target : null;
    if (target?.closest("button, a, input, select, textarea")) return;
    stopFlashSpring(card);
    pointerId = event.pointerId;
    startX = event.clientX;
    startY = event.clientY;
    startOffset = flashTranslateX(card);
    horizontal = false;
    samples = [];
    remember(startOffset, performance.now());
    card.setPointerCapture(pointerId);
  });

  card.addEventListener("pointermove", (event) => {
    if (pointerId !== event.pointerId) return;
    const rawX = startOffset + event.clientX - startX;
    const rawY = event.clientY - startY;
    if (!horizontal) {
      if (Math.abs(rawX) < 10 && Math.abs(rawY) < 10) return;
      if (Math.abs(rawY) > Math.abs(rawX)) {
        cancelTracking();
        return;
      }
      horizontal = true;
      card.classList.add("gestureActive");
    }
    event.preventDefault();
    const limit = Math.max(72, card.getBoundingClientRect().width * 0.28);
    let position = rawX;
    if ((rawX < 0 && !canGoForward) || (rawX > 0 && !canGoBack)) {
      const edge = rawX < 0 ? -limit : limit;
      position = edge + flashRubberband(rawX - edge, limit);
    }
    setFlashGestureTransform(card, position);
    remember(position, performance.now());
  });

  card.addEventListener("pointerup", (event) => finish(event));
  card.addEventListener("pointercancel", (event) => finish(event, true));
}

function originKindLabel(kind) {
  return { prefix: "接頭辞", root: "語根", suffix: "接尾辞" }[kind] || "構成要素";
}

function flashWordOrigin(item) {
  const origin = wordOriginFor(item);
  if (!origin) return null;
  const row = el("div", { class: "flashRow wordOriginRow" });
  row.appendChild(el("strong", {}, Array.isArray(origin.chain) ? "語源のイメージ" : "語源・なりたち"));

  if (Array.isArray(origin.chain) && origin.chain.length) {
    const chain = el("ol", { class: "coreChain originChain", "aria-label": "語源の連鎖" });
    origin.chain.forEach((step) => {
      const contents = [];
      if (step.term) contents.push(el("span", { class: "coreChainTerm" }, step.term));
      contents.push(el("span", { class: "coreChainGloss" }, step.gloss));
      chain.appendChild(el("li", { class: "coreChainStep" }, ...contents));
    });
    row.appendChild(chain);
    if (origin.note) row.appendChild(el("p", { class: "coreChainNote" }, origin.note));
    return row;
  }

  if (origin.type === "B") {
    if (origin.derivation) row.appendChild(el("p", { class: "originDerivation" }, origin.derivation));
    return origin.derivation ? row : null;
  }
  if (origin.type !== "A") return row;

  if (Array.isArray(origin.parts) && origin.parts.length) {
    const chips = el("div", { class: "originChips", "aria-label": "語源の構成" });
    origin.parts.forEach((part, index) => {
      if (index) chips.appendChild(el("span", { class: "originChipJoin", "aria-hidden": "true" }, "+"));
      const kind = originKindLabel(part.kind);
      chips.appendChild(el("span", {
        class: `originChip originChip-${part.kind}`,
        "aria-label": `${kind} ${part.form}：${part.gloss}`,
      },
      el("span", { class: "originChipKind" }, kind),
      el("span", { class: "originChipForm" }, part.form),
      el("span", { class: "originChipGloss" }, part.gloss)));
    });
    row.appendChild(chips);
  }
  if (origin.derivation) row.appendChild(el("p", { class: "originDerivation" }, origin.derivation));
  return row;
}

function flashCoreImage(item) {
  const core = item.coreImage;
  const row = el("div", { class: "flashRow coreImageRow" });
  row.appendChild(el("strong", {}, "核心イメージ"));

  const chain = el("ol", { class: "coreChain", "aria-label": "意味の連鎖" });
  (core.chain || []).forEach((step) => {
    const contents = [];
    if (step.term) contents.push(el("span", { class: "coreChainTerm" }, step.term));
    contents.push(el("span", { class: "coreChainGloss" }, step.gloss));
    chain.appendChild(el("li", { class: "coreChainStep" }, ...contents));
  });
  row.appendChild(chain);

  if (core.note) row.appendChild(el("p", { class: "coreChainNote" }, core.note));
  return row;
}

function renderFlash(body) {
  const items = session.items;
  const item = items[session.flashIdx];

  const flash = buildFlashCard(item);
  // 最後のカードから左へ送る操作は「意味チェックへ進む」に対応する。
  setupFlashGesture(flash, session.flashIdx > 0, true);
  body.appendChild(flash);

  const nav = el("div", { class: "actions flashNav" });
  const guardActive = flashNavLocked();
  const guardedAttrs = (attrs) => guardActive
    ? {
        ...attrs,
        class: `${attrs.class || ""} isGuarded`.trim(),
        "aria-disabled": "true",
      }
    : attrs;
  const canGoBack = session.flashIdx > 0;
  const prevAttrs = guardedAttrs(canGoBack ? { class: "ghost" } : { class: "ghost", disabled: "disabled" });
  prevAttrs.onclick = () => {
    if (!canGoBack || flashNavLocked()) return;
    armFlashNavGuard();
    session.flashIdx--;
    renderSession();
    scrollFlashCardIntoView();
  };
  const previousButton = el("button", prevAttrs, "← 前のカード");
  nav.appendChild(previousButton);
  const last = session.flashIdx === items.length - 1;
  const nextButton = el("button", guardedAttrs({
    class: "cta",
    onclick: () => {
      if (flashNavLocked()) return;
      armFlashNavGuard();
      if (last) { session.stage = "check"; renderSession(); }
      else { session.flashIdx++; renderSession(); }
      scrollFlashCardIntoView();
    },
  }), last ? "意味チェックへ進む →" : "次のカード →");
  nav.appendChild(el("span", { class: "flashNavCounter", "aria-live": "polite" },
    `カード ${session.flashIdx + 1} / ${items.length}`));
  nav.appendChild(nextButton);
  body.appendChild(el("div", { class: "sessionActionBar" }, nav));

  if (guardActive) {
    const remaining = Math.max(0, (session._flashNavReadyAt || 0) - performance.now());
    setTimeout(() => {
      [previousButton, nextButton].forEach((button) => {
        if (!button.isConnected) return;
        button.classList.remove("isGuarded");
        button.removeAttribute("aria-disabled");
      });
    }, remaining);
  }
}

function flashRow(labelText, text, cls) {
  return el("div", { class: "flashRow" },
    el("strong", {}, labelText),
    el("div", { class: cls }, text),
  );
}

// 例文中の出題形の位置を返す。見つからなければ null。
function exampleMatch(item) {
  if (!item) return null;
  const surface = String(surfaceOf(item) || "");
  const example = String(item.example || "");
  if (!surface || !example) return null;
  const escaped = surface.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  // 単語境界で区切る。境界を見ないと "When" の中の "he"、"president" の中の "preside" を拾う。
  const match = new RegExp(`(?<![A-Za-z])${escaped}(?![A-Za-z])`, "i").exec(example);
  if (!match) return null;
  return {
    before: example.slice(0, match.index),
    hit: match[0],
    after: example.slice(match.index + match[0].length),
  };
}

// 例文ノードを組み立て、対象語句だけを下線で示す。
function buildExampleText(item, match) {
  const fragment = document.createDocumentFragment();
  if (!match) {
    if (item?.example) fragment.appendChild(document.createTextNode(String(item.example)));
    return fragment;
  }
  fragment.appendChild(document.createTextNode(match.before));
  fragment.appendChild(el("span", { class: "exUnderline" }, match.hit));
  fragment.appendChild(document.createTextNode(match.after));
  return fragment;
}

function flashExampleRow(item) {
  const row = el("div", { class: "flashRow" });
  row.appendChild(el("strong", {}, "例文"));
  const match = exampleMatch(item);
  const p = el("div", { class: "flashEx" });
  p.appendChild(buildExampleText(item, match));
  row.appendChild(p);
  if (item.exampleTranslation) {
    row.appendChild(el("p", { class: "flashExampleTranslation" },
      el("span", { class: "flashExampleTranslationLabel" }, "日本語訳"),
      document.createTextNode(item.exampleTranslation),
    ));
  }
  return row;
}


function appendStemWithBreaks(target, stem) {
  const lines = stem
    .replace(/\s+(?=[AB]:\s)/g, "\n")
    .split("\n")
    .filter(Boolean);

  lines.forEach((line, lineIdx) => {
    const segs = line.split(/\(\s*\)/);
    segs.forEach((seg, i) => {
      target.appendChild(document.createTextNode(seg));
      if (i < segs.length - 1) target.appendChild(el("span", { class: "blank" }, "　"));
    });
    if (lineIdx < lines.length - 1) target.appendChild(el("br"));
  });
}

/* ---- STEP 2: meaning check ---- */
function renderCheck(body) {
  armChoiceGuard();
  const item = session.checkOrder[session.checkIdx];
  const surface = canonicalHeadwordOf(item);
  const correct = learningMeaningOf(item);
  const example = session.mode === "meaning" ? exampleMatch(item) : null;

  // 「4語句」はユニット学習（1ユニット＝4語句）だけの数。意味だけ復習(最大30)・最終チェック(全語句)では
  // 現在地バーと meaningBar/finalBar が位置を持つため roundInfo は出さない（"4語句…12/30" の矛盾表示を避ける）。
  if (session.mode === "learn") {
    body.appendChild(el("div", { class: "roundInfo" }, `4語句の意味確認 ${session.checkIdx + 1} / ${session.checkOrder.length}`));
  }

  // 出題表示の時刻。音声を押さなかった設問もここを起点に解答時間を測る
  if (!session.checkShownAt) session.checkShownAt = Date.now();

  const box = el("div", { class: "quizBox" });
  const listenButton = buildVocabAudioButton(item, "quizListenButton");
  if (example) {
    // 音声ボタンは設問文の行へ逃がす。例文と横に並べると英文の折り返しが早まる。
    box.appendChild(el("div", { class: "askExampleHead" },
      el("p", { class: "label" }, "下線部の意味として最も適当なものを選べ"),
      listenButton,
    ));
    const askExample = el("p", { class: "askExample" });
    askExample.appendChild(buildExampleText(item, example));
    box.appendChild(el("div", { class: "askExampleLine" }, askExample));
  } else {
    box.appendChild(el("p", { class: "label" }, "次の語句の意味は？"));
    box.appendChild(el("div", { class: "askWordLine" },
      el("p", { class: "askWord" }, surface),
      listenButton,
    ));
  }

  // choices: correct meaning + 3 distractors of same type
  if (!session._checkChoices) {
    session._checkChoices = shuffle([correct, ...meaningDistractors(item)]);
  }
  const choices = session._checkChoices;
  const last = session.checkIdx === session.checkOrder.length - 1;

  const choiceWrap = el("div", { class: "choices" });
  choices.forEach((m, i) => {
    const btn = el("button", { class: "choiceBtn" },
      el("span", { class: "key" }, String(i + 1)),
      el("span", {}, m),
    );
    if (session.checkAnswered) {
      btn.disabled = true;
      if (m === correct) btn.classList.add("correct");
      else if (m === session.checkPicked) btn.classList.add("wrong");
    }
    btn.addEventListener("click", () => {
      if (session.checkAnswered || choicesLocked()) return;
      session.checkAnswered = true;
      session.checkPicked = m;
      const answeredAt = Date.now();
      const responseMs = Number.isFinite(session.checkShownAt)
        ? Math.max(0, answeredAt - session.checkShownAt)
        : null;
      if (Number.isFinite(session.checkShownAt)) {
        session.checkElapsed = (answeredAt - session.checkShownAt) / 1000;
        (session.responseElapsedLog || (session.responseElapsedLog = [])).push(session.checkElapsed);
      }
      const isCorrect = m === correct;
      session.checkCorrect = isCorrect;
      if (!isCorrect && session.mode === "meaning") {
        (session.meaningWrongItems || (session.meaningWrongItems = [])).push(item);
      }
      [...choiceWrap.children].forEach((c) => {
        c.disabled = true;
        const txt = c.querySelector("span:last-child").textContent;
        if (txt === correct) c.classList.add("correct");
        else if (txt === m && !isCorrect) c.classList.add("wrong");
      });
      if ((session.mode === "meaning" || session.mode === "learn") && isCorrect) session.meaningCorrect += 1;
      if (session.mode === "final" && isCorrect) session.finalCorrect += 1;
      if (last && session.mode === "final") saveFinalResult();
      if (session.mode === "meaning" && currentGrade()) {
        // 平均は今回の解答を取り込む前の値を見せる（「前回まで」との比較にするため）。
        session.checkPrevAvgMs = readItemStateOf(item).avgMs;
        recordMeaningResult(item, isCorrect, responseMs);
      }
      saveResume();
      refreshMeaningBar();
      appendCheckFeedback(box, item, surface, correct, isCorrect);
    });
    choiceWrap.appendChild(btn);
  });
  box.appendChild(choiceWrap);
  if (session.checkAnswered) {
    appendCheckFeedback(box, item, surface, correct, session.checkCorrect);
  }
  body.appendChild(box);
}

function appendCheckFeedback(box, item, surface, correct, isCorrect) {
  if (box.querySelector(".checkFeedback")) return;
  const fb = el("div", { class: "feedback checkFeedback " + (isCorrect ? "ok" : "ng"), role: "status", "aria-live": "polite" },
    el("h3", {}, isCorrect ? "正解！" : "おしい！"),
    el("p", {}, `${surface}：${correct}`),
  );
  if (session.mode === "meaning" && item.exampleTranslation) {
    fb.appendChild(el("p", { class: "trans checkExampleTranslation" }, `例文訳：${item.exampleTranslation}`));
  }
  if (typeof session.checkElapsed === "number") {
    const average = session.checkPrevAvgMs;
    const compare = Number.isFinite(average) ? `（前回までの平均 ${(average / 1000).toFixed(1)} 秒）` : "";
    fb.appendChild(el("p", { class: "hint" },
      `出題から ${session.checkElapsed.toFixed(1)} 秒で解答${compare}`));
  }
  if (item.coreImage && Array.isArray(item.coreImage.chain)) {
    fb.appendChild(el("p", { class: "trans coreImageFeedback" },
      item.coreImage.chain.map((step) => step.gloss).join(" → ")));
  } else {
    const origin = item.type === "word" ? wordOriginFor(item) : null;
    if (origin?.derivation) fb.appendChild(el("p", { class: "trans" }, origin.derivation));
  }
  box.appendChild(fb);

  const last = session.checkIdx === session.checkOrder.length - 1;
  const actions = answerActions(
    el("button", {
      class: "cta",
      onclick: () => {
        session.checkAnswered = false;
        session.checkPicked = null;
        session.checkCorrect = null;
        session._checkChoices = null;
        session.checkShownAt = null;
        session.checkElapsed = null;
        session.checkPrevAvgMs = null;
        if (last) {
          session.stage = afterCheckDestination();
          renderSession();
        } else {
          session.checkIdx++;
          renderSession();
        }
      },
    }, last ? nextAfterCheckLabel() : "次へ →"),
  );
  box.appendChild(actions);
  revealAnswerActions(actions);
}

function afterCheckDestination() {
  if (session.mode === "meaning" && session.stage === "meaningReview") return "done";
  if (session.mode === "meaning" && session.meaningWrongItems?.length) return "meaningReview";
  return (session.mode === "meaning" || session.mode === "final") ? "done" : "practice";
}
function nextAfterCheckLabel() {
  if (afterCheckDestination() === "meaningReview") return "間違えた語句を見直す →";
  return afterCheckDestination() === "done" ? "結果を見る →" : "本番形式の問題へ →";
}

/* ---- 意味だけ復習: 誤答語句の見直し ---- */
function renderMeaningWrongReview(body) {
  const items = session.meaningWrongItems || [];
  const checked = new Set(session.meaningWrongChecked || []);
  const nextLabel = "結果を見る →";
  const lockedNextLabel = "すべて確認すると結果へ →";

  body.appendChild(el("p", { class: "hint" }, "間違えた英単語・熟語を見直してください。読み終えたら「確認した」を押してください。"));

  const listWrap = el("div", { class: "meaningWrongReview" });
  const hint = el("p", {
    id: "meaningWrongReviewProgress",
    class: "hint meaningReviewProgress",
    role: "status",
    "aria-live": "polite",
  });
  const nextBtn = el("button", {
    class: "cta",
    disabled: "disabled",
    "aria-describedby": "meaningWrongReviewProgress",
    onclick: () => {
      session.stage = "done";
      renderSession();
    },
  }, lockedNextLabel);
  const updateReviewState = () => {
    const remaining = items.length - checked.size;
    const complete = remaining === 0;
    hint.textContent = complete
      ? `見直し ${items.length}/${items.length}語句を確認済み`
      : `見直し ${checked.size}/${items.length}語句を確認済み（残り${remaining}語句）`;
    nextBtn.disabled = !complete;
    nextBtn.textContent = complete ? nextLabel : lockedNextLabel;
    const stickyPos = $("#sessionPanel .sessionStickyPos");
    if (stickyPos) stickyPos.textContent = `見直し ${checked.size} / ${items.length}`;
  };
  updateReviewState();

  items.forEach((item, index) => {
    const card = buildFlashCard(item);
    card.classList.add("meaningReviewCard");
    const checkBtn = el("button", { class: "ghost smallGhost meaningReviewCheckBtn", type: "button" }, "確認した");
    if (checked.has(index)) {
      checkBtn.disabled = true;
      checkBtn.textContent = "確認済み";
      card.classList.add("meaningReviewCardDone");
    }
    checkBtn.addEventListener("click", () => {
      if (checked.has(index)) return;
      checked.add(index);
      session.meaningWrongChecked = [...checked].sort((a, b) => a - b);
      const datasetId = item._datasetId || state.datasetId;
      const progress = progressFor(datasetId);
      appendLearningHistory(progress, {
        kind: "meaning-review",
        type: item.type,
        surface: surfaceOf(item),
        result: "viewed",
      });
      saveProgressFor(datasetId, progress);
      saveResume();
      checkBtn.disabled = true;
      checkBtn.textContent = "確認済み";
      card.classList.add("meaningReviewCardDone");
      updateReviewState();
    });
    card.appendChild(checkBtn);
    listWrap.appendChild(card);
  });

  body.appendChild(hint);
  body.appendChild(listWrap);
  body.appendChild(el("div", { class: "actions" }, nextBtn));
}

function saveFinalResult() {
  const finalTotal = session.checkOrder.length;
  const f = finalProgress(finalTotal);
  f.lastScore = session.finalCorrect;
  f.bestScore = Math.max(f.bestScore, session.finalCorrect);
  f.bestTotal = finalTotal;
  f.lastTriedAt = new Date().toISOString();
  if (session.finalCorrect >= finalPassScore(finalTotal)) {
    f.cleared = true;
    f.clearedAt = new Date().toISOString();
  }
  saveProgress();
}

/* ---- STEP 3: practice (actual question) ---- */
function renderPractice(body) {
  armChoiceGuard();
  const q = session.q;
  const q_ = state.questions[q];
  const items = state.itemsByQ[q];

  const box = el("div", { class: "quizBox" });
  box.appendChild(el("div", { class: "quizTop" },
    el("span", { class: "label", style: "margin:0" }, `第${q}問　本番形式`),
  ));

  // stem with blank
  const stemP = el("p", { class: "stem" });
  appendStemWithBreaks(stemP, q_.stem);
  box.appendChild(stemP);

  const choiceWrap = el("div", { class: "choices" });
  q_.choices.forEach((c, i) => {
    const btn = el("button", { class: "choiceBtn" },
      el("span", { class: "key" }, String(i + 1)),
      el("span", {}, c),
    );
    btn.addEventListener("click", () => onPracticeAnswer(i, box, choiceWrap, q_, items));
    choiceWrap.appendChild(btn);
  });
  box.appendChild(choiceWrap);
  body.appendChild(box);
}

function onPracticeAnswer(idx, box, choiceWrap, q_, items) {
  if (session.practiceAnswered || choicesLocked()) return;
  session.practiceAnswered = true;
  const correctIdx = q_.answerIndex;
  const isCorrect = idx === correctIdx;

  [...choiceWrap.children].forEach((c, i) => {
    c.disabled = true;
    if (i === correctIdx) c.classList.add("correct");
    else if (i === idx) c.classList.add("wrong");
  });

  const correctWord = q_.choices[correctIdx];

  const fb = el("div", { class: "feedback " + (isCorrect ? "ok" : "ng"), role: "status", "aria-live": "polite" },
    el("h3", {}, isCorrect ? "正解！" : "不正解"),
    el("p", {}, `正解：${correctIdx + 1}　${correctWord}`),
  );
  if (q_.translation) fb.appendChild(el("p", { class: "trans" }, "和訳：" + q_.translation));
  fb.appendChild(practiceChoiceMeanings(q_, items, idx));
  box.appendChild(fb);

  const u = unit(session.q);
  const answeredAt = new Date().toISOString();
  u.learned = true;
  u.attempts += 1;
  if (!isValidIsoDate(u.firstAnsweredAt)) u.firstAnsweredAt = answeredAt;
  u.lastAnsweredAt = answeredAt;
  u.solvedCorrect = isCorrect;
  // 誤答は結果として記録するが、専用の誤答復習キューには追加しない。
  u.needsReview = false;
  u.answerResult = isCorrect ? "correct" : "incorrect";
  if (!isCorrect) u.wrongCount += 1;
  appendLearningHistory(state.progress, {
    kind: "question",
    q: session.q,
    result: isCorrect ? "correct" : "wrong",
  });
  saveProgress();

  session.practiceResult = isCorrect;
  const actions = answerActions(
    el("button", { class: "cta", onclick: () => { session.stage = "done"; renderSession(); } }, "結果を見る →"),
  );
  box.appendChild(actions);
  revealAnswerActions(actions);
}

/* ---- DONE ---- */
function renderDone(body) {
  clearResume();
  const q = session.q;
  const isMeaning = session.mode === "meaning";
  const isFinal = session.mode === "final";
  const meaningSummary = isMeaning && currentGrade() ? meaningPracticeSummary() : null;
  const banner = el("div", { class: "doneBanner" });
  banner.appendChild(el("p", { class: "label", style: "color:rgba(250,249,246,.72)" }, "Step Complete"));
  if (isFinal) {
    const finalTotal = session.checkOrder.length;
    const passed = session.finalCorrect >= finalPassScore(finalTotal);
    // 再表示・再CLEAR時は演出しない。未CLEAR→CLEARに変わった今回の挑戦だけ強調する。
    const firstClear = passed && !session.wasClearedBeforeAttempt;
    banner.appendChild(el("div", { class: "big" + (firstClear ? " celebrate" : "") }, `${session.finalCorrect} / ${session.checkOrder.length}`));
    // firstClear時は既存CSS（h2.firstClear::before）が✓を演出するため、ここでは付けない（二重表示防止）。
    const finalSymbol = firstClear ? "" : (passed ? "✓ " : "! ");
    banner.appendChild(el("h2", { class: firstClear ? "firstClear" : "" }, finalSymbol + (passed
      ? `${datasetHeadline()} CLEAR`
      : `最終チェック完了。${session.finalCorrect}/${session.checkOrder.length}でした`)));
    banner.appendChild(el("p", { class: "hint" }, `${finalPassScore(finalTotal)}/${finalTotal}問以上（正答率80%以上）でCLEAR`));
  } else if (isMeaning) {
    banner.appendChild(el("div", { class: "big" }, `${session.meaningCorrect} / ${session.checkOrder.length}`));
    banner.appendChild(el("h2", {}, currentGrade()
      ? `今回の${session.checkOrder.length}語句を完了しました`
      : "意味チェックが完了しました"));
    if (meaningSummary) {
      banner.appendChild(el("p", { class: "hint" },
        `意味だけの復習対象は現在${meaningSummary.learned}/${meaningSummary.total}語句。未解放の語句は通常学習後に追加されます。`,
      ));
    }
  } else {
    // 締めの主役は「この設問の4語をどれだけ意味把握できたか」。本番形式1問の正誤は補助へ落とす。
    const missed = session.checkOrder.length - session.meaningCorrect;
    banner.appendChild(el("div", { class: "big" }, `${session.meaningCorrect} / ${session.checkOrder.length}`));
    banner.appendChild(el("h2", {}, `第${q}問の4語句を学習しました`));
    banner.appendChild(el("p", { class: "hint" },
      missed > 0 ? `意味を確認：${session.meaningCorrect}語つかめました（未定着 ${missed}語）` : `意味を確認：4語すべてつかめました`));
    banner.appendChild(el("p", { class: "hint" },
      `本番形式：${session.practiceResult ? "✓ 正解" : "! 不正解"}`));
  }
  const responseElapsedLog = session.responseElapsedLog || [];
  if (responseElapsedLog.length) {
    const avg = responseElapsedLog.reduce((a, b) => a + b, 0) / responseElapsedLog.length;
    banner.appendChild(el("p", { class: "hint" },
      `解答までの平均 ${avg.toFixed(1)} 秒（計測${responseElapsedLog.length}語句・最速${Math.min(...responseElapsedLog).toFixed(1)}秒／最遅${Math.max(...responseElapsedLog).toFixed(1)}秒）`));
  }
  body.appendChild(banner);

  const actions = el("div", { class: "actions" });
  if (isFinal) {
    if (session.finalCorrect < finalPassScore(session.checkOrder.length)) {
      actions.appendChild(el("button", { class: "cta finalCta", onclick: startFinalCheck }, `もう一度${session.checkOrder.length}問に挑戦する`));
    }
  } else if (isMeaning) {
    if (meaningSummary && meaningSummary.due > 0) {
      actions.appendChild(el("button", { class: "cta meaningCta", onclick: () => startMeaningPractice(true) },
        `次の意味だけ復習（今回${Math.min(meaningSummary.due, MEANING_SESSION_SIZE)}語句）へ →`));
    } else if (!meaningSummary) {
      actions.appendChild(el("button", { class: "cta meaningCta", onclick: () => startMeaningPractice(session.dueOnly) },
        "もう一度、意味だけの復習をする"));
    }
  } else {
    // 誤答の専用復習は行わず、次の設問への導線を主CTAにする。
    const nextQ = state.qList.find((qq) => !unit(qq).learned);
    if (nextQ) {
      actions.appendChild(el("button", { class: "cta", onclick: () => startLearn(nextQ) }, `次の設問へ（第${nextQ}問） →`));
    } else if (finalUnlocked() && !finalProgress(allVocabularyItems().length).cleared) {
      actions.appendChild(el("button", { class: "cta finalCta", onclick: startFinalCheck }, "最終チェックへ →"));
    } else {
      actions.appendChild(el("button", { class: "cta", onclick: renderHome }, "次の学習を選ぶ →"));
    }
    if (q != null && (session.meaningCorrect < session.checkOrder.length || session.practiceResult === false)) {
      actions.appendChild(el("button", {
        class: "secondaryCta",
        type: "button",
        onclick: () => startLearn(q),
      }, "この設問をもう一度学ぶ"));
    }
  }
  actions.appendChild(el("button", {
    class: "ghost",
    onclick: renderHome,
  }, "一覧へ戻る"));
  body.appendChild(actions);
}
/* ============================================================
   boot / mount（kobun-vocab と同じ: 初回のみ boot、以降はタブ復帰で renderHome のみ）
   ============================================================ */
let booted = false;

async function boot() {
  try {
    await loadManifest();
    try {
      const lemmaData = await fetch("data/lemmas.json", { cache: "no-store" }).then((r) => r.json());
      lemmaMap = lemmaData && lemmaData.lemmas && typeof lemmaData.lemmas === "object" && !Array.isArray(lemmaData.lemmas)
        ? lemmaData.lemmas
        : {};
      lemmaEntries = lemmaData && lemmaData.entries && typeof lemmaData.entries === "object" && !Array.isArray(lemmaData.entries)
        ? lemmaData.entries
        : {};
      flashcardLemmaMap = lemmaData && lemmaData.flashcardLemmas
        && typeof lemmaData.flashcardLemmas === "object" && !Array.isArray(lemmaData.flashcardLemmas)
        ? lemmaData.flashcardLemmas
        : {};
      flashcardDisplayLemmaMap = lemmaData && lemmaData.flashcardDisplayLemmas
        && typeof lemmaData.flashcardDisplayLemmas === "object" && !Array.isArray(lemmaData.flashcardDisplayLemmas)
        ? lemmaData.flashcardDisplayLemmas
        : {};
    } catch (e) {
      lemmaMap = {};
      lemmaEntries = {};
      flashcardLemmaMap = {};
      flashcardDisplayLemmaMap = {};
    }
    await loadWordOriginData();

    // 旧準1級アプリのクラウド進捗は読み取り専用で一度だけ取り込む。
    legacyPre1Cloud = createCloud({
      appId: LEGACY_PRE1_APP_ID,
      getPayload: () => readStoredObject(LEGACY_PRE1_PROGRESS_KEY) || {},
      applyLoaded: applyLegacyPre1CloudProgress,
      onStatus: () => {},
    });
    await legacyPre1Cloud.init();

    // 生徒別クラウド同期（共有URL ?s=&t= があり、config.json が揃っているときのみ有効）
    cloud = createCloud({
      appId: APP_ID,
      getPayload: collectAllProgress,
      getPatch: () => ({
        datasetId: state.datasetId,
        progress: state.progress,
        meta: cloudMeta(),
      }),
      applyLoaded: (progress) => { pendingCloudProgress = progress; },
      onStatus: setShareStatus,
    });
    await cloud.init();
    const cloudSession = cloud.getSession();
    storageStudentId = cloudSession.enabled && cloudSession.student
      ? cloudSession.student.id
      : (cloudSession.requested ? `unverified:${cloudSession.studentId || "unknown"}` : "");
    if (pendingCloudProgress) applyCloudProgress(pendingCloudProgress);
    applySharedUi();

    const legacyProgress = legacyPre1CloudProgress
      || (cloudSession.requested ? null : readStoredObject(LEGACY_PRE1_PROGRESS_KEY));
    const migratedLegacy = migrateLegacyPre1Progress(legacyProgress);
    const gradeCode = resolveGradeCode();
    needsGradeChoice = !applyGradeScope(gradeCode);
    state.datasetId = loadDatasetId();
    const migratedStudyPlanDatasetIds = migrateStudyPlanFirstAnswers();

    await loadData();
    if (currentGrade() === "eiken1") {
      try { await loadPooledItems("eiken1"); } catch (e) { /* 次のホーム描画で再試行する */ }
      loadStudyPlan();
    }
    if (migratedLegacy) {
      migratedLegacyDatasetIds.forEach((datasetId) => {
        cloud.queueSave({
          datasetId,
          progress: loadProgress(datasetId),
          meta: cloudMeta(),
        });
      });
    }
    migratedStudyPlanDatasetIds.forEach((datasetId) => {
      if (cloud) cloud.queueSave({
        datasetId,
        progress: loadProgress(datasetId),
        meta: cloudMeta(),
      });
    });
    if (window.EikenActiveAppId !== "q1") return;
    renderHome();
  } catch (e) {
    if (window.EikenActiveAppId !== "q1") return;
    $("#homePanel").innerHTML = "";
    $("#homePanel").appendChild(el("div", { class: "empty" },
      "データの読み込みに失敗しました。ローカルサーバー経由で開いているか確認してください。"));
    console.error(e);
  }
}

async function mount() {
  if (booted) {
    const preferredDatasetId = loadDatasetId();
    if (preferredDatasetId !== state.datasetId) {
      await loadData(preferredDatasetId);
      session = null;
    }
    renderHome();
    return;
  }
  booted = true;
  await boot();
}

function handleKey() { /* 大問1モードはキーボード操作なし */ }

return { mount, handleKey };
})();
