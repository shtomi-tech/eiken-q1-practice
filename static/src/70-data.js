/* ============================================================
   load data
   ============================================================ */
function normalizeMeaningResume(saved) {
  if (!saved || saved.mode !== "meaning" || saved.stage !== "context") return saved;
  // Phase 1で保存されたMeaning Contextは、同じcheckIdxのretrievalへ戻す。
  saved.stage = "check";
  saved.contextRevealed = false;
  saved.contextPicked = null;
  saved.contextCorrect = null;
  return saved;
}

async function loadData(datasetId = state.datasetId) {
  state.datasetId = datasetId;
  resumeRecoveryMessage = "";
  resumeUnavailable = false;
  state.itemsByQ = {};
  state.questions = {};
  state.qList = [];
  state.meaningPool = { word: [], idiom: [] };
  state.contextItems = [];
  state.contextTranslations = {};
  state.progress = loadProgress(datasetId);
  const savedResume = normalizeMeaningResume(state.progress.resume);
  if (savedResume && (!RESUMABLE_MODES.has(savedResume.mode) || !resumeStageAllowed(savedResume.mode, savedResume.stage))) {
    resumeRecoveryMessage = "以前の形式の途中記録は保持しています。現在の学習フローでは、第1問から再開してください。";
    resumeUnavailable = true;
  }
  writeStored(datasetStorageKey(), datasetId);

  const current = dataset();
  const contextPromise = current.contextUrl
    ? fetch(current.contextUrl, { cache: "no-store" })
      .then((r) => {
        if (!r.ok) throw new Error(`context data: HTTP ${r.status}`);
        return r.json();
      })
      .catch(() => null)
    : Promise.resolve(null);
  const contextTranslationPromise = current.contextTranslationUrl
    ? fetch(current.contextTranslationUrl, { cache: "no-store" })
      .then((r) => {
        if (!r.ok) throw new Error(`context translation data: HTTP ${r.status}`);
        return r.json();
      })
      .catch(() => null)
    : Promise.resolve(null);
  const [vocab, qs, contextPayload, contextTranslationPayload] = await Promise.all([
    fetch(current.vocabUrl, { cache: "no-store" }).then((r) => r.json()),
    fetch(current.questionsUrl, { cache: "no-store" }).then((r) => r.json()),
    contextPromise,
    contextTranslationPromise,
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

  state.contextItems = Array.isArray(contextPayload?.contexts)
    ? contextPayload.contexts
    : [];
  state.contextTranslations = Object.fromEntries(
    (Array.isArray(contextTranslationPayload?.items) ? contextTranslationPayload.items : [])
      .map((item) => [item.target, item]),
  );

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
