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
  const isPlainObject = (value) => value && typeof value === "object" && !Array.isArray(value);
  const meta = isPlainObject(map._meta) ? map._meta : {};
  const byGrade = isPlainObject(meta.studyPlanByGradeV1) ? meta.studyPlanByGradeV1 : {};
  const incoming = {};
  STUDY_PLAN_GRADES.forEach((grade) => {
    const candidate = grade === STUDY_PLAN_LEGACY_GRADE ? meta.studyPlanV1 : byGrade[grade];
    if (isPlainObject(candidate)) incoming[grade] = candidate;
  });
  pendingCloudStudyPlans = Object.keys(incoming).length ? incoming : null;
  STUDY_PLAN_GRADES.forEach((grade) => {
    if (!studyPlans[grade] || !incoming[grade]) return;
    studyPlans[grade] = normalizeStudyPlan(incoming[grade], studyPlanQuestionLimit(grade));
    saveStudyPlan(grade);
  });
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

