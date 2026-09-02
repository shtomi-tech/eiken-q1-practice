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
      el("h3", { id: "studyPlanTitle" }, "新規問題の進捗"),
    ),
    settingsToggle,
  ));
  // 日常の正本は「今日 n / m問」1つだけ常時表示。総目標・今週・再配分の目安は折りたたみへ。
  panel.appendChild(el("div", { class: "studyPlanMetrics" },
    studyPlanProgress(
      "今日",
      summary.answeredToday,
      plan.dailyQuestionGoal,
      `${num(summary.answeredToday)} / ${num(plan.dailyQuestionGoal)}問`,
      `${dailyStatus}・新規${num(summary.answeredToday * STUDY_PLAN_VOCABULARY_PER_QUESTION)}語句`,
    ),
  ));
  const planMore = el("details", { class: "studyPlanMore" });
  planMore.appendChild(el("summary", {},
    el("span", { class: "studyPlanMoreTitle" }, "総目標・今週の進捗"),
    el("span", { class: "studyPlanMoreLead" }, `総目標 ${totalStatus} ・ 今週 ${weeklyStatus}`),
  ));
  planMore.appendChild(el("div", { class: "studyPlanMetrics" },
    studyPlanProgress(
      "総目標",
      summary.answeredOverall,
      plan.questionGoal,
      `回答済み ${num(summary.answeredOverall)} / ${num(plan.questionGoal)}問`,
      totalStatus,
    ),
    studyPlanProgress(
      "今週",
      summary.answeredThisWeek,
      summary.weeklyGoal,
      `${num(summary.answeredThisWeek)} / ${num(summary.weeklyGoal)}問`,
      `${weekRange}・${weeklyStatus}`,
    ),
  ));
  planMore.appendChild(el("p", { class: "studyPlanAdjustment" },
    summary.weeklyRemaining === 0
      ? "✓ 今週の目標達成"
      : `残り${num(summary.daysRemainingIncludingToday)}日なら、1日${num(summary.adjustedDailyTarget)}問`,
  ));
  panel.appendChild(planMore);
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

  // 常時表示はサマリー（見出し＋「n 語 / m語」）1行。バー・ハリネズミ・メッセージ・注記・期間別予測は展開時。
  const details = el("details", { class: "vocabGoalDetails" });
  details.appendChild(el("summary", {},
    el("div", { class: "vgHead" },
      el("div", {},
        el("p", { class: "label" }, "語彙の目標"),
        el("h3", { id: "vocabGoalTitle" }, `${dataset().shortLabel}の語彙 ${num(goal.target)}語`),
      ),
      el("p", { class: "vgCount" },
        el("strong", {}, num(value)),
        el("span", {}, ` 語 / ${num(goal.target)}語`)),
    ),
  ));
  details.appendChild(el("div", { class: "vgBar" }, track,
    el("div", { class: "vgTicks" },
      el("span", { class: "vgTick vgTickStart" }, el("strong", {}, "0")),
      prevTick,
      el("span", { class: "vgTick vgTickEnd" },
        el("strong", {}, num(goal.target)), el("small", {}, dataset().shortLabel)),
    ),
  ));
  details.appendChild(el("p", { class: "vgMessage" }, message));
  details.appendChild(el("p", { class: "hint" },
    `${goal.prevLabel}までの${num(goal.prev)}語は習得済みとして計算しています。このアプリで学習した語句は${ready ? num(own) : "—"}語句。語彙数は目安です。`));
  if (forecast) details.appendChild(forecast);

  return el("section", { class: "card vocabGoalCard", "aria-labelledby": "vocabGoalTitle" }, details);
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
    // 行動指標は「今すぐ復習」1つに絞る。プール全体の解放数（旧・左指標）は日常判断に使わないため出さない。
    el("div", { class: "meaningMissionMetrics" },
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
