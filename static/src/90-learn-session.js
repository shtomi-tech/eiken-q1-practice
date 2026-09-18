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
    // FSRSのlapsesは累計の失敗回数。移行前の記録のために wrongCount へフォールバックする。
    const lapses = Number.isFinite(Number(s.fsrs?.lapses)) ? Number(s.fsrs.lapses) : (Number(s.wrongCount) || 0);
    return [item, 2 * lapses + hard + 0.5 * overdueDays];
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

  // header
  panel.appendChild(el("div", { class: "itemHead" },
     el("div", {},
       el("p", { class: "label" }, sessionLabel(q, isIdiom, isMeaning, isFinal)),
       // 固定ID + tabindex=-1: カード／ステージのDOM置換後、暗記カード以外はここへフォーカスを移す（F-03）。
       el("h2", { id: "sessionStageTitle", tabindex: "-1" }, stageTitle(session.stage)),
     ),
     el("button", { class: "sessionHeadBack ghost", type: "button", onclick: () => { saveResume(); renderHome(); } }, "一覧へ戻る"),
  ));

  // stage bar
  if (isFinal) panel.appendChild(finalBar());
  else if (isMeaning) panel.appendChild(meaningBar());
  else panel.appendChild(stageBar(session.stage));
  // 意味だけ復習・最終チェックは、それぞれ meaningBar/finalBar に位置・正誤数を集約する。
  // 重複する設問進捗カードは通常学習の3ステップだけに表示する。
  if (!isMeaning && !isFinal) panel.appendChild(questionProgressBar());

  const body = el("div", {});
  panel.appendChild(body);

  if (session.stage === "flash") renderFlash(body);
  else if (session.stage === "check") renderCheck(body);
  else if (session.stage === "meaningReview") renderMeaningWrongReview(body);
  else if (session.stage === "practice") renderPractice(body);
  else if (session.stage === "done") renderDone(body);

  focusSessionContext();
}

// カード・ステージをDOM置換した後、フォーカスを現在の内容へ一元的に移す（F-03）。
// 旧「次のカード」等の削除済み要素にフォーカスが残ると、次のTabが新画面の先頭から始まらない。
// 暗記カードは現在語句（.flashWord）、他ステージはセッション見出し（#sessionStageTitle）。
// スクロール位置は変えない（送り後の scrollFlashCardIntoView などと競合させない）。
function focusSessionContext() {
  const target = session && session.stage === "flash"
    ? $("#sessionPanel .flash .flashWord")
    : $("#sessionStageTitle");
  if (target && typeof target.focus === "function") {
    target.focus({ preventScroll: true });
  }
}

function sessionLabel(q, isIdiom, isMeaning, isFinal) {
  if (isFinal) return `最終チェック ${session.checkIdx + 1} / ${session.checkOrder.length}`;
  if (isMeaning) {
    // 位置「n / m」は meaningBar が持つ。ここでは種別名だけを出して重複を避ける。
    return session.stage === "meaningReview" ? "意味だけ復習・見直し" : "意味だけ復習";
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
  // 位置は「n / m語句」で示す（現在地バーと同じ数え方）。「残り」の逆算はさせない。
  return el("div", { class: "stageBar meaningBar" },
    el("div", { class: "stagePill active" },
      `${session.checkIdx + 1} / ${session.checkOrder.length}語句`),
    el("div", { class: "stagePill" },
      `回答済 ${answered} / 正解 ${session.meaningCorrect}`),
  );
}

function refreshMeaningBar() {
  if (!session || session.mode !== "meaning") return;
  const bar = document.querySelector("#sessionPanel .meaningBar");
  if (!bar) return;
  const answered = session.checkIdx + (session.checkAnswered ? 1 : 0);
  const pills = bar.querySelectorAll(".stagePill");
  if (pills[0]) pills[0].textContent = `${session.checkIdx + 1} / ${session.checkOrder.length}語句`;
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
  // 覚える（暗記カード）ステージでは全幅の塗りバーを出さない。1問ずつ読み進める段階では
  // 25問中どこかは操作の判断に使えず、Clay塗りのバーがカード見出しを画面下へ押し下げる。
  // 数値行（第n問 / m問）とスクリーンリーダー用<progress>は残す。
  if (!session || session.stage !== "flash") appendProgressFill(wrap, value, total, t.from);
  return wrap;
}

