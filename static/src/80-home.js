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

// --- 1日のノルマ（今日の面の先頭。Cloudflare 版限定 featureEnabled("dailyQuota")） ---
// 今日・復習・書くの残り数を出す。計算は dailyQuotaSummary（10-config.js）。
const DAILY_QUOTA_ITEMS = {
  today: { label: "今日", unit: "問", note: "新しい設問を解く", tab: null },
  review: { label: "復習", unit: "語句", note: `期限が来た語句から自動（最大${REVIEW_QUOTA_MAX}語句）`, tab: "review" },
  write: { label: "書く", unit: "語句", note: "意味を書く演習で答える", tab: "write" },
};

function gradeHistoryEvents(grade) {
  return withProgressReadCache(() => gradeDatasetIds(grade).flatMap((id) => {
    const history = (progressFor(id) || {}).history;
    return Array.isArray(history) ? history : [];
  }));
}

// タブのバッジとノルマカードが同じ集計を使うよう、描画のたびに1回だけ数える。
function dailyQuotaState(entries = [], reviewDue = 0, reviewReady = true) {
  const grade = currentGrade();
  const plan = currentStudyPlan(grade) || defaultStudyPlan(grade);
  const limit = studyPlanQuestionLimit(grade);
  const writeEnabled = featureEnabled("writtenMeaning");
  const summary = dailyQuotaSummary(new Date(), plan, {
    entries,
    reviewDone: meaningReviewDailyCount(new Date(), grade),
    reviewDue,
    history: gradeHistoryEvents(grade),
    writeEnabled,
  });
  // 語彙の読み込み前は期限の数が分からないので、復習の行を出さない（読み込み後に再描画される）。
  const items = summary.items.filter((item) => item.active && (item.id !== "review" || reviewReady));
  const achieved = items.filter((item) => item.remaining === 0).length;
  const allDone = items.length > 0 && achieved === items.length;
  return { grade, plan, limit, writeEnabled, items, achieved, allDone };
}

// タブのバッジ。ノルマの残り数を出し、達成した項目は ✓。ノルマに含めていない項目には付けない。
function quotaTabBadges(quota) {
  const num = (value) => Number(value).toLocaleString("ja-JP");
  return Object.fromEntries(quota.items.map((item) => {
    const meta = DAILY_QUOTA_ITEMS[item.id];
    const done = item.remaining === 0;
    return [item.id, {
      done,
      text: done ? "✓" : num(item.remaining),
      label: done ? `${meta.label}のノルマ達成` : `${meta.label}のノルマ あと${item.remaining}${meta.unit}`,
    }];
  }));
}

function dailyQuotaCard({ grade, plan, limit, writeEnabled, items, achieved, allDone }) {
  const num = (value) => Number(value).toLocaleString("ja-JP");

  const list = el("ul", { class: "quotaList" });
  items.forEach((item) => {
    const meta = DAILY_QUOTA_ITEMS[item.id];
    const done = item.remaining === 0;
    const shown = Math.min(item.done, item.goal);
    const track = el("div", {
      class: "studyPlanProgress quotaTrack",
      role: "progressbar",
      "aria-label": `${meta.label}のノルマ`,
      "aria-valuemin": "0",
      "aria-valuemax": String(Math.max(1, item.goal)),
      "aria-valuenow": String(item.goal > 0 ? shown : 1),
      "aria-valuetext": done ? `${meta.label}は達成` : `${meta.label}はあと${item.remaining}${meta.unit}`,
    });
    const fill = el("span", { class: "studyPlanProgressFill" });
    fill.style.width = item.goal > 0 ? `${(shown / item.goal) * 100}%` : "100%";
    track.appendChild(fill);
    const jump = meta.tab && homeTabsEnabled() ? el("button", {
      class: "quotaJump",
      type: "button",
      "aria-label": `${meta.label}を開く`,
      onclick: () => selectHomeTab(meta.tab, true),
    }, "開く →") : null;
    list.appendChild(el("li", { class: `quotaRow${done ? " is-done" : ""}` },
      el("div", { class: "quotaRowHead" },
        el("strong", { class: "quotaLabel" }, meta.label),
        el("span", { class: "quotaCount" }, item.goal > 0
          ? `${num(shown)} / ${num(item.goal)}${meta.unit}`
          : "期限の来た語句なし"),
        el("span", { class: "quotaRemain" }, done ? "✓ 達成" : `あと${num(item.remaining)}${meta.unit}`),
      ),
      track,
      el("div", { class: "quotaRowFoot" }, el("span", { class: "quotaNote" }, meta.note), jump),
    ));
  });

  // 設定。今日は学習目標の「1日の問題目標」と同じ値。復習は自動なので入力欄を置かない。
  const settingsId = "dailyQuotaSettings";
  const settingsToggle = el("button", {
    class: "ghost studyPlanSettingsToggle",
    type: "button",
    "aria-expanded": "false",
    "aria-controls": settingsId,
  }, "ノルマを設定");
  const settings = el("form", { class: "studyPlanSettings hide", id: settingsId, "aria-labelledby": "dailyQuotaSettingsTitle" });
  const quota = normalizeDailyQuota(plan.dailyQuota);
  const todayInput = el("input", { type: "number", min: "1", max: String(limit), value: String(plan.dailyQuestionGoal), inputmode: "numeric", name: "quota-today" });
  const writeMax = DAILY_QUOTA_LIMITS.write.max;
  const writeInput = writeEnabled
    ? el("input", { type: "number", min: "0", max: String(writeMax), value: String(quota.write), inputmode: "numeric", name: "quota-write" })
    : null;
  const error = el("p", { class: "studyPlanFormError", role: "alert", "aria-live": "polite" });
  const field = (label, input, hint) => el("label", { class: "studyPlanField" },
    el("span", { class: "fieldLabel" }, label),
    input,
    el("span", { class: "studyPlanFieldHint" }, hint),
  );
  const closeSettings = () => {
    todayInput.value = String(plan.dailyQuestionGoal);
    if (writeInput) writeInput.value = String(quota.write);
    error.textContent = "";
    settings.classList.add("hide");
    settingsToggle.setAttribute("aria-expanded", "false");
    settingsToggle.focus();
  };
  settings.appendChild(el("h4", { id: "dailyQuotaSettingsTitle" }, "1日のノルマ"));
  settings.appendChild(el("p", { class: "hint" },
    `復習は、その時点で期限が来ている語句数から自動で決まります（最大${REVIEW_QUOTA_MAX}語句）。${writeInput ? "書くを0にするとノルマから外します。" : ""}`));
  settings.appendChild(el("div", { class: "studyPlanFields" },
    field("今日（問）", todayInput, `新しい設問（1〜${num(limit)}）`),
    writeInput ? field("書く（語句）", writeInput, `意味を書く演習（0〜${writeMax}）`) : null,
  ));
  settings.appendChild(error);
  settings.appendChild(el("div", { class: "actions studyPlanFormActions" },
    el("button", { class: "cta", type: "submit" }, "保存"),
    el("button", { class: "ghost", type: "button", onclick: closeSettings }, "キャンセル"),
  ));
  settings.addEventListener("submit", (event) => {
    event.preventDefault();
    const read = (input) => (input.value.trim() === "" ? NaN : Number(input.value));
    const dailyQuestionGoal = read(todayInput);
    if (!Number.isInteger(dailyQuestionGoal) || dailyQuestionGoal < 1 || dailyQuestionGoal > limit) {
      error.textContent = `今日は1〜${num(limit)}問で入力してください。`;
      todayInput.focus();
      return;
    }
    const write = writeInput ? read(writeInput) : quota.write;
    if (!Number.isInteger(write) || write < 0 || write > writeMax) {
      error.textContent = `書くは0〜${writeMax}語句で入力してください。`;
      writeInput?.focus();
      return;
    }
    studyPlans[grade] = normalizeStudyPlan({
      ...plan,
      dailyQuestionGoal,
      dailyQuota: normalizeDailyQuota({ ...quota, write }),
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
    if (settings.classList.contains("hide")) {
      settings.classList.remove("hide");
      settingsToggle.setAttribute("aria-expanded", "true");
      todayInput.focus();
    } else {
      closeSettings();
    }
  });

  const headline = allDone ? "✓ 今日のノルマ達成" : `${num(items.length)}項目中 ${num(achieved)}項目達成`;
  return el("section", { class: `quotaPanel${allDone ? " is-done" : ""}`, "aria-labelledby": "dailyQuotaTitle" },
    el("div", { class: "studyPlanHead" },
      el("div", {},
        el("p", { class: "label" }, "1日のノルマ"),
        el("h2", { id: "dailyQuotaTitle" }, headline),
      ),
      settingsToggle,
    ),
    list,
    settings,
  );
}

// 画面右上の「ノルマ」ボタン。押すとノルマの中身（各項目と設定）を下に開く。残り数はふだんタブのバッジで見える。
// ホームを描き直すたびに中身を作り直し、開いていたかどうかは quotaMenuOpen で引き継ぐ。quota が null なら外す。
let quotaMenuOpen = false;
let quotaMenuWired = false;
function closeQuotaMenu() {
  quotaMenuOpen = false;
  $("#quotaMenuPanel")?.setAttribute("hidden", "");
  $(".quotaMenuButton")?.setAttribute("aria-expanded", "false");
}
function mountQuotaMenu(quota) {
  const header = $(".top");
  if (!header) return;
  let menu = $("#quotaMenu");
  if (!quota) {
    menu?.remove();
    return;
  }
  if (!menu) {
    menu = el("div", { class: "quotaMenu", id: "quotaMenu" });
    header.appendChild(menu);
  }
  menu.innerHTML = "";
  const { items, achieved, allDone } = quota;
  const panelId = "quotaMenuPanel";
  const button = el("button", {
    class: `quotaMenuButton${allDone ? " is-done" : ""}`,
    type: "button",
    "aria-expanded": String(quotaMenuOpen),
    "aria-controls": panelId,
    "aria-label": allDone ? "1日のノルマ（達成）" : `1日のノルマ（${items.length}項目中${achieved}項目達成）`,
  }, el("span", {}, "ノルマ"), items.length
    ? el("span", { class: "quotaMenuCount" }, allDone ? "✓" : `${achieved}/${items.length}`)
    : null);
  const panel = el("div", { class: "quotaMenuPanel", id: panelId }, dailyQuotaCard(quota));
  panel.hidden = !quotaMenuOpen;
  button.addEventListener("click", () => {
    quotaMenuOpen = panel.hidden;
    panel.hidden = !quotaMenuOpen;
    button.setAttribute("aria-expanded", String(quotaMenuOpen));
  });
  menu.append(button, panel);
  const home = $("#homePanel");
  menu.hidden = Boolean(home?.classList.contains("hide"));
  if (quotaMenuWired) return;
  quotaMenuWired = true;
  // 外側を押すか Esc で閉じる。
  document.addEventListener("click", (event) => {
    if (quotaMenuOpen && !$("#quotaMenu")?.contains(event.target)) closeQuotaMenu();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || !quotaMenuOpen) return;
    closeQuotaMenu();
    $(".quotaMenuButton")?.focus();
  });
  // 学習中（ホームを隠している間）はボタンも隠す。
  if (home && typeof MutationObserver === "function") {
    new MutationObserver(() => {
      const current = $("#quotaMenu");
      if (current) current.hidden = home.classList.contains("hide");
    }).observe(home, { attributes: true, attributeFilter: ["class"] });
  }
}

function contextDiscoveryCard() {
  const current = dataset();
  if (!current?.contextUrl) return null;
  const enabled = contextDiscoveryEnabled();
  return el("section", { class: "contextDiscoveryCard", "aria-labelledby": "contextDiscoveryTitle" },
    el("p", { class: "label" }, "学習モード"),
    el("h3", { id: "contextDiscoveryTitle" }, `文脈推測：${enabled ? "あり" : "なし"}`),
    el("p", { class: "contextDiscoveryLead" },
      enabled
        ? "通常学習で、暗記カードの前に英文から意味を推測します。"
        : "通常学習を暗記カードから始めます。"),
    el("p", { class: "hint contextDiscoveryTrialNote" }, "切り替えは、次に始める通常学習から反映されます。"),
    el("div", { class: "contextDiscoveryActions" },
      el("button", {
        class: "secondaryCta contextDiscoveryCta",
        type: "button",
        "aria-pressed": String(enabled),
        onclick: () => {
          setContextDiscoveryEnabled(!enabled);
          renderHome();
        },
      }, enabled ? "推測なしに切り替える" : "推測ありに切り替える"),
    ),
  );
}

function renderHomeContent() {
  $("#sessionPanel").classList.add("hide");
  const home = $("#homePanel");
  home.classList.remove("hide");
  home.innerHTML = "";
  homeTabMarks = [];
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
  const useContextDiscovery = contextDiscoveryEnabled();

  homeTabStart(home, "today");
  // hero は初回訪問（まだ何も学習していない）時だけ表示し、今日の学習カードとの説明重複を避ける
  if (isFirstVisit) {
    home.appendChild(el("section", { class: "card hero" },
      el("p", { class: "label" }, "学習の流れ"),
      el("h2", {}, useContextDiscovery
        ? `${datasetSectionName()}の語句を「発見して→覚えて→使う」`
        : `${datasetSectionName()}の語句を「覚えて→確かめて→使う」`),
      el("p", { class: "hint" }, useContextDiscovery
        ? "文脈から意味を発見 → 暗記カードで整理 → 意味を思い出す → 本番形式で使う、の学習サイクル。"
        : "暗記カードで整理 → 意味を思い出す → 本番形式で使う、の学習サイクル。"),
    ));
  }

  const quota = showStudyPlan && featureEnabled("dailyQuota")
    ? dailyQuotaState(studyPlanEntries, meaningDueCount, Boolean(pooled))
    : null;
  mountQuotaMenu(quota);

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

  const contextModeControl = contextDiscoveryCard();
  if (contextModeControl) summary.appendChild(contextModeControl);

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
      why: isFirstVisit
        ? ""
        : useContextDiscovery
        ? "文脈から発見 → 暗記カード → 意味確認 → 本番形式の学習サイクルで進みます。"
        : "暗記カード → 意味確認 → 本番形式の学習サイクルで進みます。",
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
      el("p", { class: "recWhy" }, homeTabsEnabled()
        ? "通常学習は完了しています。今日の間隔復習は「復習」から開始します。"
        : "通常学習は完了しています。今日の間隔復習は下のカードから開始します。"),
      homeTabsEnabled()
        ? el("button", { class: "cta startCta", type: "button", onclick: () => selectHomeTab("review", true) }, "今日の復習へ")
        : null,
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

  homeTabStart(home, "review");
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

  homeTabStart(home, "write");
  const writtenCard = grade ? writtenMeaningCard(Boolean(pooled), meaningItems) : null;
  if (writtenCard) home.appendChild(writtenCard);

  homeTabStart(home, "sets");
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
  // ノルマがある公開先ではタブにノルマの残り数を、無い公開先では従来どおり復習の期限数を出す。
  arrangeHomeTabs(home, quota ? quotaTabBadges(quota) : {
    review: hasMeaningDue ? { text: String(meaningDueCount), label: `${meaningDueCount}語句` } : null,
  });
}

/* ---- ホームのタブ（Cloudflare 版限定。featureEnabled("homeTabs")） ----
   1列に積んでいたホームを「今日・復習・書く・問題」の4面に分ける。
   描画中に homeTabStart で区切りを付け、最後に arrangeHomeTabs で各面へ振り分ける。
   タブが無い公開先では区切りを無視し、従来どおり1列のまま表示する。 */
const HOME_TABS = [
  { id: "today", label: "今日" },
  { id: "review", label: "復習" },
  { id: "write", label: "書く" },
  { id: "sets", label: "問題" },
];
const HOME_TAB_KEY = "eiken_q1_home_tab_v1";
let homeTabMarks = [];
function homeTabsEnabled() {
  return featureEnabled("homeTabs");
}
function homeTabStart(home, id) {
  homeTabMarks.push({ id, from: home.children.length });
}
function storedHomeTab() {
  const fromHash = String(window.location.hash || "").replace(/^#/, "");
  if (HOME_TABS.some((tab) => tab.id === fromHash)) return fromHash;
  try {
    const stored = localStorage.getItem(HOME_TAB_KEY);
    if (HOME_TABS.some((tab) => tab.id === stored)) return stored;
  } catch (e) { /* ignore */ }
  return "today";
}
function selectHomeTab(id, focus = false) {
  const bar = document.querySelector(".homeTabs");
  if (!bar) return;
  writeStored(HOME_TAB_KEY, id);
  try { history.replaceState(null, "", `${window.location.pathname}${window.location.search}#${id}`); } catch (e) { /* ignore */ }
  bar.querySelectorAll("[role=tab]").forEach((button) => {
    const selected = button.dataset.tab === id;
    button.setAttribute("aria-selected", String(selected));
    button.tabIndex = selected ? 0 : -1;
    if (selected && focus) button.focus();
  });
  document.querySelectorAll(".homeTabPanel").forEach((panel) => {
    panel.hidden = panel.dataset.tab !== id;
  });
  if (bar.getBoundingClientRect().top < 0) bar.scrollIntoView({ block: "start" });
}
function arrangeHomeTabs(home, badges) {
  const marks = homeTabMarks;
  homeTabMarks = [];
  if (!homeTabsEnabled() || !marks.length) return;
  const panels = {};
  HOME_TABS.forEach((tab) => {
    panels[tab.id] = el("div", {
      class: "homeTabPanel",
      id: `homeTabPanel-${tab.id}`,
      role: "tabpanel",
      "aria-labelledby": `homeTab-${tab.id}`,
      "data-tab": tab.id,
    });
  });
  Array.from(home.children).forEach((node, index) => {
    let id = marks[0].id;
    marks.forEach((mark) => { if (index >= mark.from) id = mark.id; });
    panels[id].appendChild(node);
  });
  const tabs = HOME_TABS.filter((tab) => panels[tab.id].children.length);
  if (!tabs.length) return;
  const stored = storedHomeTab();
  const active = tabs.some((tab) => tab.id === stored) ? stored : tabs[0].id;
  const bar = el("div", { class: "homeTabs", role: "tablist", "aria-label": "ホームの表示" });
  tabs.forEach((tab, i) => {
    const badge = badges[tab.id];
    const button = el("button", {
      class: "homeTab",
      id: `homeTab-${tab.id}`,
      type: "button",
      role: "tab",
      "aria-controls": `homeTabPanel-${tab.id}`,
      "data-tab": tab.id,
      onclick: () => selectHomeTab(tab.id),
    }, el("span", {}, tab.label), badge
      ? el("span", { class: `homeTabBadge${badge.done ? " is-done" : ""}`, "aria-label": badge.label }, badge.text)
      : null);
    button.addEventListener("keydown", (event) => {
      const step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
      if (!step) return;
      event.preventDefault();
      selectHomeTab(tabs[(i + step + tabs.length) % tabs.length].id, true);
    });
    bar.appendChild(button);
  });
  home.appendChild(bar);
  tabs.forEach((tab) => home.appendChild(panels[tab.id]));
  selectHomeTab(active);
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
  // タブ表示では「問題」タブの先頭なので、触っていなければ問題セットは開いておく。
  const stored = homeFoldState()[id];
  details.open = stored === undefined ? homeTabsEnabled() && id === "datasets" : stored === true;
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

