/* ============================================================
   HOME
   ============================================================ */
function renderHome() {
  // 同期処理のみ。await をまたぐとキャッシュが別パスへ漏れるので中で非同期処理を待たない。
  return withProgressReadCache(renderHomeContent);
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
  const grade = currentGrade();
  const plan = currentStudyPlan(grade) || defaultStudyPlan(grade);
  const limit = studyPlanQuestionLimit(grade);
  const summary = studyPlanSummary(new Date(), plan, entries);
  const num = (value) => Number(value).toLocaleString("ja-JP");
  const dailyStatus = summary.dailyRemaining === 0 ? "✓ 今日の目標達成" : `あと${num(summary.dailyRemaining)}問`;
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
  settings.appendChild(el("p", { class: "hint" }, `1日の問題目標は1〜${num(limit)}問で設定できます。`));
  settings.appendChild(el("div", { class: "studyPlanFields" },
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
    const dailyQuestionGoal = Number(dailyInput.value);
    const weekStartsOn = Number(weekSelect.value);
    const validInteger = (value, max) => Number.isInteger(value) && value >= 1 && value <= max;
    if (!validInteger(dailyQuestionGoal, limit)
      || !Number.isInteger(weekStartsOn) || weekStartsOn < 0 || weekStartsOn > 6) {
      error.textContent = `1日の問題目標は1〜${num(limit)}問、週の開始曜日は日〜土から選んでください。`;
      return;
    }
    studyPlans[grade] = normalizeStudyPlan({
      ...plan,
      dailyQuestionGoal,
      weekStartsOn,
    }, limit);
    saveStudyPlan(grade);
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
    if (open) dailyInput.focus();
  });

  panel.appendChild(el("div", { class: "studyPlanHead" },
    el("div", {},
      el("p", { class: "label" }, "学習目標"),
      el("h3", { id: "studyPlanTitle" }, "新規問題の進捗"),
    ),
    settingsToggle,
  ));
  // 日常の正本は「今日 n / m問」1つだけ常時表示する。
  panel.appendChild(el("div", { class: "studyPlanMetrics" },
    studyPlanProgress(
      "今日",
      summary.answeredToday,
      plan.dailyQuestionGoal,
      `${num(summary.answeredToday)} / ${num(plan.dailyQuestionGoal)}問`,
      dailyStatus,
    ),
  ));
  panel.appendChild(settings);
  return panel;
}

function contextDiscoveryCard() {
  const current = dataset();
  if (!current?.contextUrl) return null;
  const total = Number(current.contextTotal) || 0;
  return el("section", { class: "card contextDiscoveryCard", "aria-labelledby": "contextDiscoveryTitle" },
    el("p", { class: "label" }, "Context Discovery"),
    el("h3", { id: "contextDiscoveryTitle" }, "英文の流れから意味を推測する"),
    el("p", { class: "contextDiscoveryLead" },
      "日本語訳を先に見ず、英文の中の手がかりを組み合わせて語句の意味を考えます。"),
    el("p", { class: "contextDiscoveryMeta" }, `英検2級・${total}語句から1回10語`),
    el("p", { class: "hint contextDiscoveryTrialNote" }, "どちらも通常学習の進捗には影響しません。"),
    el("div", { class: "contextDiscoveryActions" },
      el("button", {
        class: "secondaryCta contextDiscoveryCta",
        type: "button",
        onclick: () => startContextPractice(),
      }, "文脈推測を試す →"),
      el("button", {
        class: "secondaryCta contextDiscoveryCta",
        type: "button",
        onclick: () => startContextLearning(),
      }, "文脈→暗記カードを試す →"),
    ),
  );
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
      if (isStudyPlanGrade(grade)) loadStudyPlan(grade);
      if (currentGrade() === grade && !$("#homePanel").classList.contains("hide")) renderHome();
    }).catch(() => { /* オフライン等。次の描画で再試行する。 */ });
  }
  const pooled = pooledData(grade);
  const meaningSummary = grade ? meaningPracticeSummary() : null;
  const meaningItems = pooled ? learnedPooledItems(pooled.items) : [];
  const meaningQueue = pooled ? meaningPracticeQueue(meaningItems, true) : [];
  const meaningDueCount = meaningSummary ? meaningSummary.due : 0;
  const showStudyPlan = isStudyPlanGrade(currentGrade());
  const studyPlanEntries = showStudyPlan ? gradeQuestionEntries(currentGrade()) : [];
  const isFirstVisit = learned === 0;
  // 級の変更は URL で級を固定していないときだけ。下部の「その他」ではなく先頭カードの右上へ置く。
  const canChangeGrade = !new URLSearchParams(window.location.search).has("g");

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
  const sectionHead = el("div", { class: "sectionHead" },
    el("div", {},
      el("p", { class: "label" }, final.cleared ? "達成状況" : "今日の学習"),
      el("h2", {}, headerTitle),
      el("p", { class: "hint" }, currentDataset.label),
    ),
  );
  if (canChangeGrade) {
    sectionHead.appendChild(el("button", {
      class: "ghost smallGhost gradeChangeButton",
      type: "button",
      onclick: () => {
        if (!confirm("学習する級を変更します。現在の級以外の進捗も消えません。変更しますか？")) return;
        removeStored(scopedStorageKey(GRADE_KEY));
        needsGradeChoice = true;
        renderHome();
      },
    }, "級を変更"));
  }
  summary.appendChild(sectionHead);
  // --- 次にやること（Hickの法則：迷わせないため主導線は常に1つに絞る） ---
  const resume = currentResume();
  const resumeIsDone = resume?.stage === "done";
  const meaningResume = resume?.mode === "meaning" && !resumeIsDone;
  const coreResume = Boolean(resume && resume.mode !== "meaning" && !resumeIsDone);
  const nextQ = state.qList.find((q) => !unit(q).learned);
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
  home.appendChild(summary);

  // 語彙目標カード（級単位。1級は日次学習目標を上段に統合。問題セットより上位の目標なので、セット一覧より前に置く）
  const learnedVocabulary = showStudyPlan
    ? learnedVocabularyCount(grade, studyPlanEntries)
    : (meaningSummary ? meaningSummary.learned : 0);
  const studyPlanNode = showStudyPlan ? studyPlanPanel(studyPlanEntries) : null;
  const goalCard = grade ? vocabGoalCard(learnedVocabulary, Boolean(pooled), studyPlanNode) : null;
  if (goalCard) home.appendChild(goalCard);
  flushStudyTime();
  home.appendChild(studyTimeCard());

  const contextCard = contextDiscoveryCard();
  if (contextCard) home.appendChild(contextCard);

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
  // 問題セット・問題一覧は既定で閉じる（開閉状態は端末に記憶）
  home.appendChild(el("section", { class: "card" }, homeFold(
    "datasets",
    el("span", { class: "homeFoldTitle" },
      el("span", { class: "label" }, "問題セット"),
      el("strong", {}, `${dataset().label}${datasetCleared(state.datasetId) ? " ✅" : ""}`),
    ),
    datasetPicker(),
  )));

  // 層3：詳細（問題一覧。状態・種別フィルター付き）
  const path = el("div", {});
  path.appendChild(el("div", { class: "pathHead" },
    el("p", { class: "hint" }, "各設問に出る4つの語句を覚えてから、その設問を解きます。クリックで開始。"),
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
  home.appendChild(el("section", { class: "card" }, homeFold(
    "questions",
    el("span", { class: "homeFoldTitle" },
      el("span", { class: "label" }, "問題一覧"),
      el("strong", {}, `${datasetHeadline()}（全${total}問）`),
    ),
    path,
  )));

  // 級の変更は先頭カードの右上へ移動済み。ここは「その他」（進捗リセット）だけを扱う。
  if (!sharedMode()) {
    const utility = el("section", { class: "card" });
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
    home.appendChild(utility);
  }
}

const HOME_FOLD_KEY = "eiken_q1_home_fold_v1";
function homeFoldState() {
  return readStoredObject(HOME_FOLD_KEY) || {};
}
function homeFold(id, summaryContent, body) {
  const details = el("details", { class: "homeFold" },
    el("summary", {}, summaryContent),
    el("div", { class: "homeFoldBody" }, body),
  );
  details.open = homeFoldState()[id] === true;
  details.addEventListener("toggle", () => {
    writeStoredJson(HOME_FOLD_KEY, { ...homeFoldState(), [id]: details.open });
  });
  return details;
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
      const nextGrade = currentGrade();
      if (isStudyPlanGrade(nextGrade)) {
        try { await loadPooledItems(nextGrade); } catch (e) { /* ホーム描画後に再試行する */ }
        loadStudyPlan(nextGrade);
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

