/* ============================================================
   LEARN FLOW (per question)
   stages: flash -> check -> practice -> done
   ============================================================ */
let session = null;

function resetSessionScroll() {
  window.scrollTo({ top: 0, left: 0, behavior: "auto" });
}

function startLearn(q) {
  const items = state.itemsByQ[q];
  if (!Array.isArray(items) || !items.length) {
    renderHome();
    return false;
  }
  session = {
    mode: "learn",
    q,
    items: shuffle(items),
    stage: "flash",
    flashIdx: 0,
    checkOrder: shuffle(items),
    checkIdx: 0,
    checkAnswered: false,
    meaningCorrect: 0,
  };
  renderSession();
  resetSessionScroll();
  return true;
}

// 語句の進捗を、その語句が属する回（item._datasetId、無ければ現在の回）から読み取る。
function readItemStateOf(item) {
  return readItemState(progressFor(item._datasetId || state.datasetId), itemKeyOf(item));
}
function isItemDue(item, now = Date.now()) {
  const itemState = readItemStateOf(item);
  // 旧形式の意味記録には回答時刻がないため、新仕様で一度だけ対象に戻す。
  if (!itemState.lastAnsweredAt) return true;
  const nextReviewAt = itemState.nextReviewAt;
  return !nextReviewAt || new Date(nextReviewAt).getTime() <= now;
}
// 誤答・直近の遅い正答・期限超過を合成して前に出す。
function weightedOrder(items) {
  // ES2019以降 Array#sort は安定。同点の並びはシャッフル順のままにする。
  const shuffled = shuffle(items);
  const now = Date.now();
  const dayMs = 24 * 60 * 60 * 1000;
  const scores = new Map(shuffled.map((item) => {
    const s = readItemStateOf(item);
    const overdueMs = s.nextReviewAt ? now - new Date(s.nextReviewAt).getTime() : 0;
    const overdueDays = Number.isFinite(overdueMs) ? Math.max(0, overdueMs / dayMs) : 0;
    // lastGradeは保存しない制約のため、絶対床以上の「直近の正答RT」をHard相当として復元する。
    const hard = Number.isFinite(s.lastMs) && s.lastMs >= RT_HARD_FLOOR_MS ? 1 : 0;
    return [item, 2 * (Number(s.wrongCount) || 0) + hard + 0.5 * overdueDays];
  }));
  return shuffled.sort((a, b) => scores.get(b) - scores.get(a));
}
// dueOnly=true: 復習日が来た語だけ。未学習語句や次回予定の語句は補充しない。
function meaningPracticeQueue(items, dueOnly) {
  return withProgressReadCache(() => {
    const candidates = dueOnly ? items.filter((it) => isItemDue(it)) : items;
    return weightedOrder(candidates).slice(0, MEANING_SESSION_SIZE);
  });
}

async function startMeaningPractice(dueOnly = true, queueOverride = null) {
  const grade = currentGrade();
  let queue;
  if (grade) {
    let pooled;
    try {
      pooled = await loadPooledItems(grade);
    } catch (e) {
      // オフライン等で収録セットを読めないときは、ホームに戻して次の操作で再試行させる。
      renderHome();
      return false;
    }
    queue = Array.isArray(queueOverride)
      ? queueOverride
      // await をまたがない同期ブロックとしてまとめて読む
      : withProgressReadCache(() => meaningPracticeQueue(learnedPooledItems(pooled.items), dueOnly));
  } else {
    // 級を判定できないdatasetIdへの保険。現在の回の語句だけで組む。
    queue = shuffle(allVocabularyItems()).slice(0, MEANING_SESSION_SIZE);
  }
  if (!queue.length) {
    renderHome();
    return false;
  }
  session = {
    mode: "meaning",
    q: null,
    items: queue,
    stage: "check",
    checkOrder: queue,
    checkIdx: 0,
    checkAnswered: false,
    meaningCorrect: 0,
    meaningWrongItems: [],
    meaningWrongChecked: [],
    dueOnly: Boolean(grade) && dueOnly,
    meaningVersion: grade ? MEANING_PROGRESS_VERSION : null,
    meaningBatchSize: grade ? MEANING_SESSION_SIZE : null,
  };
  renderSession();
  resetSessionScroll();
  return true;
}

function startFinalCheck() {
  if (!finalUnlocked()) {
    renderHome();
    return false;
  }
  const queue = shuffle(allVocabularyItems());
  session = {
    mode: "final",
    q: null,
    items: queue,
    stage: "check",
    checkOrder: queue,
    checkIdx: 0,
    checkAnswered: false,
    finalCorrect: 0,
    // 完了画面で「今回が初回CLEARかどうか」を判定するため、挑戦開始時点の状態を記録する。
    wasClearedBeforeAttempt: finalProgress(queue.length).cleared,
  };
  renderSession();
  resetSessionScroll();
  return true;
}

function renderSession() {
  saveResume();
  $("#homePanel").classList.add("hide");
  const panel = $("#sessionPanel");
  panel.classList.remove("hide");
  panel.classList.toggle("hasActionBar", session.stage === "flash");
  panel.innerHTML = "";

  const isMeaning = session.mode === "meaning";
  const isFinal = session.mode === "final";
  const q = session.q;
  const isIdiom = !isMeaning && !isFinal && session.items[0].type === "idiom";

  // 長いカードをスクロールしても現在地・戻る操作を見失わないための補助バー
  panel.appendChild(sessionStickyNav(q, isMeaning, isFinal));

  // header
  panel.appendChild(el("div", { class: "itemHead" },
     el("div", {},
       el("p", { class: "label" }, sessionLabel(q, isIdiom, isMeaning, isFinal)),
       el("h2", {}, stageTitle(session.stage)),
       el("p", { class: "sessionState" }, "現在地はこの端末に保存済み"),
     ),
  ));

  // stage bar
  if (isFinal) panel.appendChild(finalBar());
  else if (isMeaning) panel.appendChild(meaningBar());
  else panel.appendChild(stageBar(session.stage));
  panel.appendChild(questionProgressBar());

  const body = el("div", {});
  panel.appendChild(body);

  if (session.stage === "flash") renderFlash(body);
  else if (session.stage === "check") renderCheck(body);
  else if (session.stage === "meaningReview") renderMeaningWrongReview(body);
  else if (session.stage === "practice") renderPractice(body);
  else if (session.stage === "done") renderDone(body);
}

// 元のitemHead/stageBar/q1Progressは残したまま、スクロール中も現在地が分かる補助バーを上に固定する。
function sessionStickyNav(q, isMeaning, isFinal) {
  const total = state.qList.length;
  const reviewChecked = session.meaningWrongChecked?.length || 0;
  const reviewTotal = session.meaningWrongItems?.length || 0;
  const posLabel = isFinal
    ? `${session.checkIdx + 1} / ${session.checkOrder.length}`
    : isMeaning && session.stage === "meaningReview"
      ? `見直し ${reviewChecked} / ${reviewTotal}`
      : isMeaning
        ? `${session.checkIdx + 1} / ${session.checkOrder.length}`
        : (q != null && total ? `第${state.qList.indexOf(q) + 1} / ${total}問` : "");
  const stageLabel = {
    flash: "覚える", check: "確かめる", meaningReview: "見直し", practice: "解く", done: "完了",
  }[session.stage] || "";
  return el("div", { class: "sessionStickyNav" },
    el("button", { class: "sessionStickyBack ghost", type: "button", onclick: () => { saveResume(); renderHome(); } }, "一覧へ戻る"),
    el("span", { class: "sessionStickyPos" }, posLabel),
    el("span", { class: "sessionStickyStage" }, stageLabel),
  );
}

function sessionLabel(q, isIdiom, isMeaning, isFinal) {
  if (isFinal) return `最終チェック ${session.checkIdx + 1} / ${session.checkOrder.length}`;
  if (isMeaning) {
    const label = session.stage === "meaningReview" ? "意味だけ復習・見直し" : "意味だけ復習";
    return `${label} ${session.checkIdx + 1} / ${session.checkOrder.length}`;
  }
  return `第${q}問 ・ ${isIdiom ? "熟語" : "単語"}`;
}

function stageTitle(stage) {
  if (session && session.mode === "final") return `最終チェック${session.checkOrder.length}問`;
  if (session && session.mode === "meaning" && session.stage === "meaningReview") return "間違えた語句を見直す";
  if (session && session.mode === "meaning") return `意味だけの復習（最大${MEANING_SESSION_SIZE}語句）`;
  return {
    flash: "STEP 1　覚える（暗記カード）",
    check: "STEP 2　確かめる（4語句の意味確認）",
    practice: "STEP 3　解く（本番形式）",
    done: "完了",
  }[stage];
}

function meaningBar() {
  if (session.stage === "meaningReview") {
    const total = session.meaningWrongItems?.length || 0;
    const checked = session.meaningWrongChecked?.length || 0;
    return el("div", { class: "stageBar meaningBar" },
      el("div", { class: "stagePill active" }, `誤答 ${total}語句`),
      el("div", { class: "stagePill" }, `確認済 ${checked} / ${total}`),
    );
  }
  const answered = session.checkIdx + (session.checkAnswered ? 1 : 0);
  const remaining = Math.max(0, session.checkOrder.length - answered);
  return el("div", { class: "stageBar meaningBar" },
    el("div", { class: "stagePill active" },
      answered ? `残り ${remaining}語句` : `今回 ${session.checkOrder.length}語句`),
    el("div", { class: "stagePill" },
      `回答済 ${answered} / 正解 ${session.meaningCorrect}`),
  );
}

function refreshMeaningBar() {
  if (!session || session.mode !== "meaning") return;
  const bar = document.querySelector("#sessionPanel .meaningBar");
  if (!bar) return;
  const answered = session.checkIdx + (session.checkAnswered ? 1 : 0);
  const remaining = Math.max(0, session.checkOrder.length - answered);
  const pills = bar.querySelectorAll(".stagePill");
  if (pills[0]) pills[0].textContent = answered ? `残り ${remaining}語句` : `今回 ${session.checkOrder.length}語句`;
  if (pills[1]) pills[1].textContent = `回答済 ${answered} / 正解 ${session.meaningCorrect}`;
}

function finalBar() {
  return el("div", { class: "stageBar meaningBar" },
    el("div", { class: "stagePill active" },
      `最終チェック ${session.checkIdx + 1} / ${session.checkOrder.length}`),
    el("div", { class: "stagePill" },
      `回答済 ${session.checkIdx} / 正解 ${session.finalCorrect}`),
  );
}

function stageBar(stage) {
  const order = ["flash", "check", "practice"];
  const cur = order.indexOf(stage);
  const labels = { flash: "1 覚える", check: "2 確かめる", practice: "3 解く" };
  const bar = el("div", { class: "stageBar", role: "list", "aria-label": "学習ステップ" });
  order.forEach((s, i) => {
    let cls = "stagePill";
    if (stage === "done" || i < cur) cls += " cleared";
    if (s === stage) cls += " active";
    bar.appendChild(el("div", { class: cls, role: "listitem", "aria-current": s === stage ? "step" : "false" }, labels[s]));
  });
  return bar;
}

// キー単位で直近値を覚え、値が変わった回だけ残数のsettleと装飾fillのtransitionを発火する。
// リロード直後は前回値がないため発火しない（DESIGN.mdの完成条件どおり）。
const lastProgressByKey = {};
function progressTransition(key, value, total) {
  const prev = lastProgressByKey[key];
  lastProgressByKey[key] = { value, total };
  if (!prev || prev.total !== total || prev.value === value) return { settle: false, from: null };
  return { settle: true, from: prev.value };
}
function appendProgressFill(wrap, value, total, animateFrom) {
  const pct = (v) => (total ? Math.min(100, Math.max(0, (v / total) * 100)) : 0);
  const fill = el("div", { class: "q1ProgressFill" });
  const track = el("div", { class: "q1ProgressTrack", "aria-hidden": "true" }, fill);
  if (animateFrom != null && !prefersReducedMotion()) {
    fill.style.width = pct(animateFrom) + "%";
    wrap.appendChild(track);
    requestAnimationFrame(() => requestAnimationFrame(() => { fill.style.width = pct(value) + "%"; }));
  } else {
    fill.style.width = pct(value) + "%";
    wrap.appendChild(track);
  }
}

function questionProgressBar() {
  const total = state.qList.length;
  if (!total) return el("div", { class: "q1Progress hide" });

  if (session.mode === "meaning" && currentGrade()) return meaningProgressBar();

  const isQuestionSession = session.q != null;
  const current = isQuestionSession
    ? Math.max(1, state.qList.indexOf(session.q) + 1)
    : state.qList.filter((q) => unit(q).learned).length;
  const value = Math.min(total, current);
  const remaining = Math.max(0, total - value);
  const label = isQuestionSession ? `第${value}問 / ${total}問` : `通常学習済み ${value} / ${total}問`;
  const t = progressTransition(`q:${state.datasetId}`, value, total);
  const settleCls = t.settle ? " progressSettle" : "";

  const wrap = el("div", { class: "q1Progress" },
    el("div", { class: "q1ProgressHead" },
      el("span", { class: "label" }, `${datasetSectionName()} 設問進捗`),
      el("strong", { class: "q1ProgressValue" + settleCls }, label),
      el("span", { class: "q1ProgressRemaining" + settleCls }, `残り${remaining}問`),
    ),
  );
  const progress = el("progress", {
    class: "q1ProgressBar",
    max: total,
    value,
    "aria-label": `${datasetSectionName()}の設問進捗`,
  });
  progress.setAttribute("aria-valuetext", `${label}、残り${remaining}問`);
  wrap.appendChild(progress);
  appendProgressFill(wrap, value, total, t.from);
  return wrap;
}

function meaningProgressBar() {
  const summary = meaningPracticeSummary();
  const total = summary.total;
  if (!total) return el("div", { class: "q1Progress hide" });
  const remaining = Math.max(0, total - summary.learned);
  const label = `対象 ${summary.learned} / ${total}語句`;
  const t = progressTransition(`m:${state.datasetId}`, summary.learned, total);
  const settleCls = t.settle ? " progressSettle" : "";
  const wrap = el("div", { class: "q1Progress meaningProgress" },
    el("div", { class: "q1ProgressHead" },
      el("span", { class: "label" }, "意味練習の解放状況"),
      el("strong", { class: "q1ProgressValue" + settleCls }, label),
      el("span", { class: "q1ProgressRemaining" + settleCls }, `未解放${remaining}語句`),
    ),
  );
  const progress = el("progress", {
    class: "q1ProgressBar",
    max: total,
    value: summary.learned,
    "aria-label": `${dataset().shortLabel}の意味練習対象語句の解放状況`,
  });
  progress.setAttribute("aria-valuetext", `${label}、未解放${remaining}語句`);
  wrap.appendChild(progress);
  appendProgressFill(wrap, summary.learned, total, t.from);
  return wrap;
}

/* ---- STEP 1: flashcards ---- */
function buildFlashCard(item) {
  const card = el("div", { class: "flash" });
  const head = el("div", { class: "flashHead" });
  const surface = surfaceOf(item);
  const displayLemma = item.type === "word"
    ? flashcardLemmaMap[String(surface || "").toLowerCase()]
    : "";
  const headword = displayLemma || canonicalHeadwordOf(item);
  const learning = learningEntryOf(item);
  const wordLine = el("div", { class: "flashWordLine" },
    el("div", { class: "flashWord" }, headword),
  );
  if (learning.ipa) wordLine.appendChild(el("div", { class: "flashIpa" }, learning.ipa));
  if (vocabularyAudioEnabled(item)) wordLine.appendChild(buildVocabAudioButton(item, "flashListenButton", true));
  const headContent = el("div", {}, wordLine);
  if (headword !== surface) {
    const lemmaNote = el("div", { class: "flashLemmaNote" },
      el("span", { class: "flashLemmaLabel" }, "出題形"),
      el("span", { class: "flashLemmaSurface" }, surface),
    );
    headContent.appendChild(lemmaNote);
  }
  headContent.appendChild(el("div", { class: "flashPos" }, learningPosOf(item)));
  head.appendChild(headContent);
  card.appendChild(head);

  const inner = el("div", { class: "flashBody" });
  inner.appendChild(flashRow("意味", learning.meaning || item.meaning, "flashMeaning"));
  if (item.type === "word") {
    const wordOrigin = flashWordOrigin(item);
    if (wordOrigin) inner.appendChild(wordOrigin);
  } else if (item.type === "idiom" && item.coreImage) {
    inner.appendChild(flashCoreImage(item));
  }
  if (item.example) inner.appendChild(flashExampleRow(item));
  card.appendChild(inner);
  return card;
}

function scrollFlashCardIntoView() {
  const flash = $("#sessionPanel .flash");
  if (!flash) return;
  const sticky = $("#sessionPanel .sessionStickyNav");
  const stickyHeight = sticky ? sticky.getBoundingClientRect().height : 0;
  const target = flash.getBoundingClientRect().top + window.scrollY - stickyHeight - 8;
  window.scrollTo({ top: Math.max(0, target), left: 0, behavior: "auto" });
}

function originKindLabel(kind) {
  return { prefix: "接頭辞", root: "語根", suffix: "接尾辞" }[kind] || "構成要素";
}

function flashWordOrigin(item) {
  const origin = wordOriginFor(item);
  if (!origin) return null;
  const row = el("div", { class: "flashRow wordOriginRow" });
  row.appendChild(el("strong", {}, Array.isArray(origin.chain) ? "語源のイメージ" : "語源・なりたち"));

  if (Array.isArray(origin.chain) && origin.chain.length) {
    const chain = el("ol", { class: "coreChain originChain", "aria-label": "語源の連鎖" });
    origin.chain.forEach((step) => {
      const contents = [];
      if (step.term) contents.push(el("span", { class: "coreChainTerm" }, step.term));
      contents.push(el("span", { class: "coreChainGloss" }, step.gloss));
      chain.appendChild(el("li", { class: "coreChainStep" }, ...contents));
    });
    row.appendChild(chain);
    if (origin.note) row.appendChild(el("p", { class: "coreChainNote" }, origin.note));
    return row;
  }

  if (origin.type === "B") {
    const summary = el("div", { class: "originChips", "aria-label": "語源の概要" });
    summary.appendChild(el("span", {
      class: "originChip originChip-summary",
      "aria-label": "由来：B型。構成要素に分解せず一行で確認",
    },
    el("span", { class: "originChipKind" }, "由来"),
    el("span", { class: "originChipForm" }, "B型"),
    el("span", { class: "originChipGloss" }, "構成要素に分解せず一行で確認")));
    row.appendChild(summary);
    if (origin.derivation) row.appendChild(el("p", { class: "originDerivation" }, origin.derivation));
    return row;
  }
  if (origin.type !== "A") return row;

  if (Array.isArray(origin.parts) && origin.parts.length) {
    const chips = el("div", { class: "originChips", "aria-label": "語源の構成" });
    origin.parts.forEach((part, index) => {
      if (index) chips.appendChild(el("span", { class: "originChipJoin", "aria-hidden": "true" }, "+"));
      const kind = originKindLabel(part.kind);
      chips.appendChild(el("span", {
        class: `originChip originChip-${part.kind}`,
        "aria-label": `${kind} ${part.form}：${part.gloss}`,
      },
      el("span", { class: "originChipKind" }, kind),
      el("span", { class: "originChipForm" }, part.form),
      el("span", { class: "originChipGloss" }, part.gloss)));
    });
    row.appendChild(chips);
  }
  if (origin.derivation) row.appendChild(el("p", { class: "originDerivation" }, origin.derivation));
  return row;
}

function flashCoreImage(item) {
  const core = item.coreImage;
  const row = el("div", { class: "flashRow coreImageRow" });
  row.appendChild(el("strong", {}, "核心イメージ"));

  const chain = el("ol", { class: "coreChain", "aria-label": "意味の連鎖" });
  (core.chain || []).forEach((step) => {
    const contents = [];
    if (step.term) contents.push(el("span", { class: "coreChainTerm" }, step.term));
    contents.push(el("span", { class: "coreChainGloss" }, step.gloss));
    chain.appendChild(el("li", { class: "coreChainStep" }, ...contents));
  });
  row.appendChild(chain);

  if (core.note) row.appendChild(el("p", { class: "coreChainNote" }, core.note));
  return row;
}

function renderFlash(body) {
  const items = session.items;
  const item = items[session.flashIdx];

  body.appendChild(buildFlashCard(item));

  const nav = el("div", { class: "actions flashNav" });
  const guardActive = flashNavLocked();
  const guardedAttrs = (attrs) => guardActive
    ? {
        ...attrs,
        class: `${attrs.class || ""} isGuarded`.trim(),
        "aria-disabled": "true",
      }
    : attrs;
  const canGoBack = session.flashIdx > 0;
  const prevAttrs = guardedAttrs(canGoBack ? { class: "ghost" } : { class: "ghost", disabled: "disabled" });
  prevAttrs.onclick = () => {
    if (!canGoBack || flashNavLocked()) return;
    armFlashNavGuard();
    session.flashIdx--;
    renderSession();
    scrollFlashCardIntoView();
  };
  const previousButton = el("button", prevAttrs, "← 前のカード");
  nav.appendChild(previousButton);
  const last = session.flashIdx === items.length - 1;
  const nextButton = el("button", guardedAttrs({
    class: "cta",
    onclick: () => {
      if (flashNavLocked()) return;
      armFlashNavGuard();
      if (last) { session.stage = "check"; renderSession(); }
      else { session.flashIdx++; renderSession(); }
      scrollFlashCardIntoView();
    },
  }), last ? "意味チェックへ進む →" : "次のカード →");
  nav.appendChild(el("span", { class: "flashNavCounter", "aria-live": "polite" },
    `カード ${session.flashIdx + 1} / ${items.length}`));
  nav.appendChild(nextButton);
  body.appendChild(el("div", { class: "sessionActionBar" }, nav));

  if (guardActive) {
    const remaining = Math.max(0, (session._flashNavReadyAt || 0) - performance.now());
    setTimeout(() => {
      [previousButton, nextButton].forEach((button) => {
        if (!button.isConnected) return;
        button.classList.remove("isGuarded");
        button.removeAttribute("aria-disabled");
      });
    }, remaining);
  }
}

function flashRow(labelText, text, cls) {
  return el("div", { class: "flashRow" },
    el("strong", {}, labelText),
    el("div", { class: cls }, text),
  );
}
function flashExampleRow(item) {
  const surface = surfaceOf(item);
  const row = el("div", { class: "flashRow" });
  row.appendChild(el("strong", {}, "例文"));
  // 見出し語をハイライト
  const re = new RegExp("(" + surface.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "i");
  const parts = item.example.split(re);
  const p = el("div", { class: "flashEx" });
  parts.forEach((part) => {
    if (part.toLowerCase() === surface.toLowerCase()) p.appendChild(el("em", {}, part));
    else p.appendChild(document.createTextNode(part));
  });
  row.appendChild(p);
  if (item.exampleTranslation) {
    row.appendChild(el("p", { class: "flashExampleTranslation" },
      el("span", { class: "flashExampleTranslationLabel" }, "日本語訳"),
      document.createTextNode(item.exampleTranslation),
    ));
  }
  return row;
}


function appendStemWithBreaks(target, stem) {
  const lines = stem
    .replace(/\s+(?=[AB]:\s)/g, "\n")
    .split("\n")
    .filter(Boolean);

  lines.forEach((line, lineIdx) => {
    const segs = line.split(/\(\s*\)/);
    segs.forEach((seg, i) => {
      target.appendChild(document.createTextNode(seg));
      if (i < segs.length - 1) target.appendChild(el("span", { class: "blank" }, "　"));
    });
    if (lineIdx < lines.length - 1) target.appendChild(el("br"));
  });
}

/* ---- STEP 2: meaning check ---- */
function renderCheck(body) {
  armChoiceGuard();
  const item = session.checkOrder[session.checkIdx];
  const surface = canonicalHeadwordOf(item);
  const correct = learningMeaningOf(item);

  body.appendChild(el("div", { class: "roundInfo" }, `4語句の意味確認 ${session.checkIdx + 1} / ${session.checkOrder.length}`));

  // 出題表示の時刻。音声を押さなかった設問もここを起点に解答時間を測る
  if (!session.checkShownAt) session.checkShownAt = Date.now();

  const box = el("div", { class: "quizBox" });
  box.appendChild(el("p", { class: "label" }, "次の語句の意味は？"));
  const listenButton = buildVocabAudioButton(item, "quizListenButton");
  box.appendChild(el("div", { class: "askWordLine" },
    el("p", { class: "askWord" }, surface),
    listenButton,
  ));

  // choices: correct meaning + 3 distractors of same type
  if (!session._checkChoices) {
    session._checkChoices = shuffle([correct, ...meaningDistractors(item)]);
  }
  const choices = session._checkChoices;
  const last = session.checkIdx === session.checkOrder.length - 1;

  const choiceWrap = el("div", { class: "choices" });
  choices.forEach((m, i) => {
    const btn = el("button", { class: "choiceBtn" },
      el("span", { class: "key" }, String(i + 1)),
      el("span", {}, m),
    );
    if (session.checkAnswered) {
      btn.disabled = true;
      if (m === correct) btn.classList.add("correct");
      else if (m === session.checkPicked) btn.classList.add("wrong");
    }
    btn.addEventListener("click", () => {
      if (session.checkAnswered || choicesLocked()) return;
      session.checkAnswered = true;
      session.checkPicked = m;
      const answeredAt = Date.now();
      const responseMs = Number.isFinite(session.checkShownAt)
        ? Math.max(0, answeredAt - session.checkShownAt)
        : null;
      if (Number.isFinite(session.checkShownAt)) {
        session.checkElapsed = (answeredAt - session.checkShownAt) / 1000;
        (session.responseElapsedLog || (session.responseElapsedLog = [])).push(session.checkElapsed);
      }
      const isCorrect = m === correct;
      session.checkCorrect = isCorrect;
      if (!isCorrect && session.mode === "meaning") {
        (session.meaningWrongItems || (session.meaningWrongItems = [])).push(item);
      }
      [...choiceWrap.children].forEach((c) => {
        c.disabled = true;
        const txt = c.querySelector("span:last-child").textContent;
        if (txt === correct) c.classList.add("correct");
        else if (txt === m && !isCorrect) c.classList.add("wrong");
      });
      if ((session.mode === "meaning" || session.mode === "learn") && isCorrect) session.meaningCorrect += 1;
      if (session.mode === "final" && isCorrect) session.finalCorrect += 1;
      if (last && session.mode === "final") saveFinalResult();
      if (session.mode === "meaning" && currentGrade()) {
        // 平均は今回の解答を取り込む前の値を見せる（「前回まで」との比較にするため）。
        session.checkPrevAvgMs = readItemStateOf(item).avgMs;
        recordMeaningResult(item, isCorrect, responseMs);
      }
      saveResume();
      refreshMeaningBar();
      appendCheckFeedback(box, item, surface, correct, isCorrect);
    });
    choiceWrap.appendChild(btn);
  });
  box.appendChild(choiceWrap);
  if (session.checkAnswered) {
    appendCheckFeedback(box, item, surface, correct, session.checkCorrect);
  }
  body.appendChild(box);
}

function appendCheckFeedback(box, item, surface, correct, isCorrect) {
  if (box.querySelector(".checkFeedback")) return;
  const fb = el("div", { class: "feedback checkFeedback " + (isCorrect ? "ok" : "ng"), role: "status", "aria-live": "polite" },
    el("h3", {}, isCorrect ? "正解！" : "おしい！"),
    el("p", {}, `${surface}：${correct}`),
  );
  if (typeof session.checkElapsed === "number") {
    const average = session.checkPrevAvgMs;
    const compare = Number.isFinite(average) ? `（前回までの平均 ${(average / 1000).toFixed(1)} 秒）` : "";
    fb.appendChild(el("p", { class: "hint" },
      `出題から ${session.checkElapsed.toFixed(1)} 秒で解答${compare}`));
  }
  if (item.coreImage && Array.isArray(item.coreImage.chain)) {
    fb.appendChild(el("p", { class: "trans coreImageFeedback" },
      item.coreImage.chain.map((step) => step.gloss).join(" → ")));
  } else {
    const origin = item.type === "word" ? wordOriginFor(item) : null;
    if (origin?.derivation) fb.appendChild(el("p", { class: "trans" }, origin.derivation));
  }
  box.appendChild(fb);

  const last = session.checkIdx === session.checkOrder.length - 1;
  const actions = answerActions(
    el("button", {
      class: "cta",
      onclick: () => {
        session.checkAnswered = false;
        session.checkPicked = null;
        session.checkCorrect = null;
        session._checkChoices = null;
        session.checkShownAt = null;
        session.checkElapsed = null;
        session.checkPrevAvgMs = null;
        if (last) {
          session.stage = afterCheckDestination();
          renderSession();
        } else {
          session.checkIdx++;
          renderSession();
        }
      },
    }, last ? nextAfterCheckLabel() : "次へ →"),
  );
  box.appendChild(actions);
  revealAnswerActions(actions);
}

function afterCheckDestination() {
  if (session.mode === "meaning" && session.stage === "meaningReview") return "done";
  if (session.mode === "meaning" && session.meaningWrongItems?.length) return "meaningReview";
  return (session.mode === "meaning" || session.mode === "final") ? "done" : "practice";
}
function nextAfterCheckLabel() {
  if (afterCheckDestination() === "meaningReview") return "間違えた語句を見直す →";
  return afterCheckDestination() === "done" ? "結果を見る →" : "本番形式の問題へ →";
}

/* ---- 意味だけ復習: 誤答語句の見直し ---- */
function renderMeaningWrongReview(body) {
  const items = session.meaningWrongItems || [];
  const checked = new Set(session.meaningWrongChecked || []);
  const nextLabel = "結果を見る →";
  const lockedNextLabel = "すべて確認すると結果へ →";

  body.appendChild(el("p", { class: "hint" }, "間違えた英単語・熟語を見直してください。読み終えたら「確認した」を押してください。"));

  const listWrap = el("div", { class: "meaningWrongReview" });
  const hint = el("p", {
    id: "meaningWrongReviewProgress",
    class: "hint meaningReviewProgress",
    role: "status",
    "aria-live": "polite",
  });
  const nextBtn = el("button", {
    class: "cta",
    disabled: "disabled",
    "aria-describedby": "meaningWrongReviewProgress",
    onclick: () => {
      session.stage = "done";
      renderSession();
    },
  }, lockedNextLabel);
  const updateReviewState = () => {
    const remaining = items.length - checked.size;
    const complete = remaining === 0;
    hint.textContent = complete
      ? `見直し ${items.length}/${items.length}語句を確認済み`
      : `見直し ${checked.size}/${items.length}語句を確認済み（残り${remaining}語句）`;
    nextBtn.disabled = !complete;
    nextBtn.textContent = complete ? nextLabel : lockedNextLabel;
    const stickyPos = $("#sessionPanel .sessionStickyPos");
    if (stickyPos) stickyPos.textContent = `見直し ${checked.size} / ${items.length}`;
  };
  updateReviewState();

  items.forEach((item, index) => {
    const card = buildFlashCard(item);
    card.classList.add("meaningReviewCard");
    const checkBtn = el("button", { class: "ghost smallGhost meaningReviewCheckBtn", type: "button" }, "確認した");
    if (checked.has(index)) {
      checkBtn.disabled = true;
      checkBtn.textContent = "確認済み";
      card.classList.add("meaningReviewCardDone");
    }
    checkBtn.addEventListener("click", () => {
      if (checked.has(index)) return;
      checked.add(index);
      session.meaningWrongChecked = [...checked].sort((a, b) => a - b);
      const datasetId = item._datasetId || state.datasetId;
      const progress = progressFor(datasetId);
      appendLearningHistory(progress, {
        kind: "meaning-review",
        type: item.type,
        surface: surfaceOf(item),
        result: "viewed",
      });
      saveProgressFor(datasetId, progress);
      saveResume();
      checkBtn.disabled = true;
      checkBtn.textContent = "確認済み";
      card.classList.add("meaningReviewCardDone");
      updateReviewState();
    });
    card.appendChild(checkBtn);
    listWrap.appendChild(card);
  });

  body.appendChild(hint);
  body.appendChild(listWrap);
  body.appendChild(el("div", { class: "actions" }, nextBtn));
}

function saveFinalResult() {
  const finalTotal = session.checkOrder.length;
  const f = finalProgress(finalTotal);
  f.lastScore = session.finalCorrect;
  f.bestScore = Math.max(f.bestScore, session.finalCorrect);
  f.bestTotal = finalTotal;
  f.lastTriedAt = new Date().toISOString();
  if (session.finalCorrect >= finalPassScore(finalTotal)) {
    f.cleared = true;
    f.clearedAt = new Date().toISOString();
  }
  saveProgress();
}

/* ---- STEP 3: practice (actual question) ---- */
function renderPractice(body) {
  armChoiceGuard();
  const q = session.q;
  const q_ = state.questions[q];
  const items = state.itemsByQ[q];

  const box = el("div", { class: "quizBox" });
  box.appendChild(el("div", { class: "quizTop" },
    el("span", { class: "label", style: "margin:0" }, `第${q}問　本番形式`),
  ));

  // stem with blank
  const stemP = el("p", { class: "stem" });
  appendStemWithBreaks(stemP, q_.stem);
  box.appendChild(stemP);

  const choiceWrap = el("div", { class: "choices" });
  q_.choices.forEach((c, i) => {
    const btn = el("button", { class: "choiceBtn" },
      el("span", { class: "key" }, String(i + 1)),
      el("span", {}, c),
    );
    btn.addEventListener("click", () => onPracticeAnswer(i, box, choiceWrap, q_, items));
    choiceWrap.appendChild(btn);
  });
  box.appendChild(choiceWrap);
  body.appendChild(box);
}

function onPracticeAnswer(idx, box, choiceWrap, q_, items) {
  if (session.practiceAnswered || choicesLocked()) return;
  session.practiceAnswered = true;
  const correctIdx = q_.answerIndex;
  const isCorrect = idx === correctIdx;

  [...choiceWrap.children].forEach((c, i) => {
    c.disabled = true;
    if (i === correctIdx) c.classList.add("correct");
    else if (i === idx) c.classList.add("wrong");
  });

  const correctWord = q_.choices[correctIdx];

  const fb = el("div", { class: "feedback " + (isCorrect ? "ok" : "ng"), role: "status", "aria-live": "polite" },
    el("h3", {}, isCorrect ? "正解！" : "不正解"),
    el("p", {}, `正解：${correctIdx + 1}　${correctWord}`),
  );
  if (q_.translation) fb.appendChild(el("p", { class: "trans" }, "和訳：" + q_.translation));
  fb.appendChild(practiceChoiceMeanings(q_, items, idx));
  box.appendChild(fb);

  const u = unit(session.q);
  const answeredAt = new Date().toISOString();
  u.learned = true;
  u.attempts += 1;
  if (!isValidIsoDate(u.firstAnsweredAt)) u.firstAnsweredAt = answeredAt;
  u.lastAnsweredAt = answeredAt;
  u.solvedCorrect = isCorrect;
  // 誤答は結果として記録するが、専用の誤答復習キューには追加しない。
  u.needsReview = false;
  u.answerResult = isCorrect ? "correct" : "incorrect";
  if (!isCorrect) u.wrongCount += 1;
  appendLearningHistory(state.progress, {
    kind: "question",
    q: session.q,
    result: isCorrect ? "correct" : "wrong",
  });
  saveProgress();

  session.practiceResult = isCorrect;
  const actions = answerActions(
    el("button", { class: "cta", onclick: () => { session.stage = "done"; renderSession(); } }, "結果を見る →"),
  );
  box.appendChild(actions);
  revealAnswerActions(actions);
}

/* ---- DONE ---- */
function renderDone(body) {
  clearResume();
  const q = session.q;
  const isMeaning = session.mode === "meaning";
  const isFinal = session.mode === "final";
  const meaningSummary = isMeaning && currentGrade() ? meaningPracticeSummary() : null;
  const banner = el("div", { class: "doneBanner" });
  banner.appendChild(el("p", { class: "label", style: "color:rgba(250,249,246,.72)" }, "Step Complete"));
  if (isFinal) {
    const finalTotal = session.checkOrder.length;
    const passed = session.finalCorrect >= finalPassScore(finalTotal);
    // 再表示・再CLEAR時は演出しない。未CLEAR→CLEARに変わった今回の挑戦だけ強調する。
    const firstClear = passed && !session.wasClearedBeforeAttempt;
    banner.appendChild(el("div", { class: "big" + (firstClear ? " celebrate" : "") }, `${session.finalCorrect} / ${session.checkOrder.length}`));
    // firstClear時は既存CSS（h2.firstClear::before）が✓を演出するため、ここでは付けない（二重表示防止）。
    const finalSymbol = firstClear ? "" : (passed ? "✓ " : "! ");
    banner.appendChild(el("h2", { class: firstClear ? "firstClear" : "" }, finalSymbol + (passed
      ? `${datasetHeadline()} CLEAR`
      : `最終チェック完了。${session.finalCorrect}/${session.checkOrder.length}でした`)));
    banner.appendChild(el("p", { class: "hint" }, `${finalPassScore(finalTotal)}/${finalTotal}問以上（正答率80%以上）でCLEAR`));
  } else if (isMeaning) {
    banner.appendChild(el("div", { class: "big" }, `${session.meaningCorrect} / ${session.checkOrder.length}`));
    banner.appendChild(el("h2", {}, currentGrade()
      ? `今回の${session.checkOrder.length}語句を完了しました`
      : "意味チェックが完了しました"));
    if (meaningSummary) {
      banner.appendChild(el("p", { class: "hint" },
        `意味だけの復習対象は現在${meaningSummary.learned}/${meaningSummary.total}語句。未解放の語句は通常学習後に追加されます。`,
      ));
    }
  } else {
    banner.appendChild(el("div", { class: "big" }, session.practiceResult ? "✓ 正解！" : "! 不正解"));
    banner.appendChild(el("h2", {}, `第${q}問の4語句を学習しました`));
    banner.appendChild(el("p", { class: "hint" },
      `意味確認 ${session.meaningCorrect}/${session.checkOrder.length}・誤答 ${session.checkOrder.length - session.meaningCorrect}語`));
  }
  const responseElapsedLog = session.responseElapsedLog || [];
  if (responseElapsedLog.length) {
    const avg = responseElapsedLog.reduce((a, b) => a + b, 0) / responseElapsedLog.length;
    banner.appendChild(el("p", { class: "hint" },
      `解答までの平均 ${avg.toFixed(1)} 秒（計測${responseElapsedLog.length}語句・最速${Math.min(...responseElapsedLog).toFixed(1)}秒／最遅${Math.max(...responseElapsedLog).toFixed(1)}秒）`));
  }
  body.appendChild(banner);

  const actions = el("div", { class: "actions" });
  if (isFinal) {
    if (session.finalCorrect < finalPassScore(session.checkOrder.length)) {
      actions.appendChild(el("button", { class: "cta finalCta", onclick: startFinalCheck }, `もう一度${session.checkOrder.length}問に挑戦する`));
    }
  } else if (isMeaning) {
    if (meaningSummary && meaningSummary.due > 0) {
      actions.appendChild(el("button", { class: "cta meaningCta", onclick: () => startMeaningPractice(true) },
        `次の意味だけ復習（今回${Math.min(meaningSummary.due, MEANING_SESSION_SIZE)}語句）へ →`));
    } else if (!meaningSummary) {
      actions.appendChild(el("button", { class: "cta meaningCta", onclick: () => startMeaningPractice(session.dueOnly) },
        "もう一度、意味だけの復習をする"));
    }
  } else {
    // 誤答の専用復習は行わず、次の設問への導線を主CTAにする。
    const nextQ = state.qList.find((qq) => !unit(qq).learned);
    if (nextQ) {
      actions.appendChild(el("button", { class: "cta", onclick: () => startLearn(nextQ) }, `次の設問へ（第${nextQ}問） →`));
    } else if (finalUnlocked() && !finalProgress(allVocabularyItems().length).cleared) {
      actions.appendChild(el("button", { class: "cta finalCta", onclick: startFinalCheck }, "最終チェックへ →"));
    } else {
      actions.appendChild(el("button", { class: "cta", onclick: renderHome }, "次の学習を選ぶ →"));
    }
    if (q != null && (session.meaningCorrect < session.checkOrder.length || session.practiceResult === false)) {
      actions.appendChild(el("button", {
        class: "secondaryCta",
        type: "button",
        onclick: () => startLearn(q),
      }, "この設問をもう一度学ぶ"));
    }
  }
  actions.appendChild(el("button", {
    class: "ghost",
    onclick: renderHome,
  }, "一覧へ戻る"));
  body.appendChild(actions);
}
