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
  // 最終チェック未達でも、全設問を一通り学習したセットは完了として緑の印を付ける。
  const completed = cleared || (Number.isInteger(totalQuestions) && totalQuestions > 0
    && learnedQuestions >= totalQuestions);
  let status = "notStarted";
  if (completed) status = "cleared";
  else if (learnedQuestions > 0) status = "inProgress";
  else if (hasResume) status = "resumable";
  return {
    totalQuestions,
    totalVocabulary,
    learnedQuestions,
    cleared,
    completed,
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
  // 現在セットで通常学習（meaning以外）の途中保存があるとき、このカードは状態表示に徹する。
  // 同じ保存位置を開く再開操作はホーム上部の .startCta 1つへ集約し、競合CTAを増やさない（F-04）。
  // 別セットのカードは従来どおり切替操作を持つ。
  const isResumeStatus = isCurrent && summary.hasResume
    && summary.resume && summary.resume.mode !== "meaning";
  const actionLabel = isResumeStatus ? "途中保存あり" : label;
  const cls = ["datasetUnitCard"];
  if (isCurrent) cls.push("current");
  if (summary.completed) cls.push("cleared");
  if (isResumeStatus) cls.push("isResumeStatus");
  const ariaParts = [datasetSetLabel(id, data), progressLine];
  if (summary.cleared) ariaParts.push("CLEAR");
  else if (summary.completed) ariaParts.push("学習済み");
  if (resumeText) ariaParts.push(resumeText);
  ariaParts.push(actionLabel);
  const inner = [
    el("span", { class: "datasetUnitCardNumber" }, String(index + 1).padStart(2, "0")),
    el("div", { class: "datasetUnitCardMain" },
      el("span", { class: "datasetUnitCardTitle" }, datasetSetLabel(id, data)),
      el("span", { class: "datasetUnitCardMeta" }, `全${totalQ}問・${totalV}語`),
      el("span", { class: "datasetUnitCardProgress" }, progressLine),
      summary.completed
        ? el("span", { class: "datasetUnitCardClear" }, summary.cleared ? "✓ CLEAR" : "✓ 学習済み")
        : null,
      summary.hasResume ? el("span", { class: "datasetUnitCardResume" }, resumeText) : null,
      el("span", { class: "datasetUnitCardAction" }, actionLabel),
    ),
    isResumeStatus ? null : el("span", { class: "datasetUnitCardArrow", "aria-hidden": "true" }, "→"),
  ];

  // 途中保存の現在Unitは操作要素にしない（onclick・type=button・矢印を持たない）。
  if (isResumeStatus) {
    return el("div", {
      class: cls.join(" "),
      "aria-current": "true",
      "aria-label": ariaParts.join("・"),
    }, ...inner);
  }

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
  return el("button", attrs, ...inner);
}

// 現在セットと同じ級・種別で、一覧の並び順に次の未完了セットを返す（なければ null）。
function nextDatasetEntry() {
  const currentId = state.datasetId;
  const grade = gradeOf(currentId);
  const kind = datasetSetKind(currentId);
  const group = availableDatasets().filter(([id]) => gradeOf(id) === grade && datasetSetKind(id) === kind);
  const index = group.findIndex(([id]) => id === currentId);
  if (index < 0) return null;
  const after = group.slice(index + 1).concat(group.slice(0, index));
  return after.find(([id, data]) => !datasetSummary(id, data).completed) || null;
}

async function startNextDataset(datasetId) {
  await switchDataset(datasetId);
  if (state.datasetId !== datasetId || window.EikenActiveAppId !== "q1") return;
  const nextQ = state.qList.find((q) => !unit(q).learned) || state.qList[0];
  if (nextQ != null) startLearn(nextQ);
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

