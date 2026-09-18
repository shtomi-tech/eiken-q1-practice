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

