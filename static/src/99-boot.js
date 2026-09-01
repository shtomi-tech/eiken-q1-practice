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
