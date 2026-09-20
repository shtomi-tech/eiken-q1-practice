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
  state.contextItems = [];
  state.progress = loadProgress(datasetId);
  const savedResume = state.progress.resume;
  // Phase 1で保存された「意味復習中のContext」は、現在の責務では意味チェックへ戻す。
  // 保存データを捨てず、同じcheckIdxから純粋なretrievalとして再開する。
  if (savedResume?.mode === "meaning" && savedResume.stage === "context") {
    savedResume.stage = "check";
    savedResume.contextRevealed = false;
    savedResume.contextPicked = null;
    savedResume.contextCorrect = null;
  }
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
  const [vocab, qs, contextPayload] = await Promise.all([
    fetch(current.vocabUrl, { cache: "no-store" }).then((r) => r.json()),
    fetch(current.questionsUrl, { cache: "no-store" }).then((r) => r.json()),
    contextPromise,
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
