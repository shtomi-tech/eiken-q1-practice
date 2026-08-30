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
