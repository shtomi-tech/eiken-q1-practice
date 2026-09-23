/* ============================================================
   LEARN FLOW (per question)
   stages: context/flash (one word at a time) -> check -> practice -> done
   contextLearn trial: context -> flash
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
  const orderedItems = shuffle(items);
  const contextEnabled = contextDiscoveryEnabled();
  session = {
    mode: "learn",
    q,
    items: orderedItems,
    stage: "flash",
    learnIdx: 0,
    learnPhase: "flash",
    flashIdx: 0,
    checkOrder: shuffle(orderedItems),
    checkIdx: 0,
    checkAnswered: false,
    meaningCorrect: 0,
    contextPool: state.contextItems,
    contextEnabled,
    contextResults: {},
    contextAvailableTotal: 0,
    contextTotal: 0,
    contextCorrectCount: 0,
    contextRevealed: false,
    contextChoices: null,
    contextChoiceTarget: "",
    contextPicked: null,
    contextCorrect: null,
  };
  session.contextAvailableTotal = contextEnabled
    ? session.items.filter((item) => contextItemFor(item)).length
    : 0;
  session.learnPhase = session.contextAvailableTotal > 0 && contextItemFor(session.items[0]) && !hasLearnContextResult(session.items[0])
    ? "context"
    : "flash";
  session.stage = session.learnPhase;
  renderSession();
  resetSessionScroll();
  return true;
}

function setLearnItem(index, phase = null) {
  session.learnIdx = index;
  session.flashIdx = index;
  const item = session.items[index];
  const nextPhase = phase || (session.contextEnabled !== false && contextItemFor(item) && !hasLearnContextResult(item) ? "context" : "flash");
  session.learnPhase = nextPhase;
  session.stage = nextPhase;
  if (nextPhase === "context") resetContextState();
}

function enterLearnFlash() {
  session.learnPhase = "flash";
  session.stage = "flash";
  session.flashIdx = session.learnIdx;
  resetContextState();
}

function advanceLearnFromFlash() {
  if (session.learnIdx >= session.items.length - 1) {
    session.stage = "check";
    session.learnPhase = null;
    session.checkIdx = 0;
    session.checkAnswered = false;
    session._checkChoices = null;
    renderSession();
    return;
  }
  setLearnItem(session.learnIdx + 1);
  renderSession();
  resetSessionScroll();
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

const CONTEXT_SESSION_SIZE = 10;

async function startContextPractice() {
  const url = dataset().contextUrl;
  if (!url) return false;
  let payload;
  try {
    payload = await fetch(url, { cache: "no-store" }).then((response) => {
      if (!response.ok) throw new Error(`context data: HTTP ${response.status}`);
      return response.json();
    });
  } catch (error) {
    console.error(error);
    renderHome();
    return false;
  }
  const fetchedContexts = Array.isArray(payload?.contexts) ? payload.contexts : [];
  const contexts = state.contextItems.length ? state.contextItems : fetchedContexts;
  const items = shuffle(contexts).slice(0, Math.min(CONTEXT_SESSION_SIZE, contexts.length));
  if (!items.length) {
    renderHome();
    return false;
  }
  session = {
    mode: "context",
    q: null,
    items,
    contextPool: contexts,
    stage: "context",
    contextIdx: 0,
    contextRevealed: false,
    contextChoices: null,
    contextChoiceTarget: "",
    contextPicked: null,
    contextCorrect: null,
  };
  renderSession();
  resetSessionScroll();
  return true;
}

function startContextLearning(q = null) {
  const targetQ = q == null
    ? (state.qList.find((candidate) => !unit(candidate).learned) || state.qList[0])
    : q;
  const items = state.itemsByQ[targetQ];
  if (!Array.isArray(items) || !items.length) {
    renderHome();
    return false;
  }
  session = {
    mode: "contextLearn",
    q: targetQ,
    items: shuffle(items),
    stage: "context",
    flashIdx: 0,
    contextPool: state.contextItems,
    contextOrder: [],
    contextIdx: 0,
    contextBeforeFlash: true,
    contextRevealed: false,
    contextChoices: null,
    contextChoiceTarget: "",
    contextPicked: null,
    contextCorrect: null,
  };
  session.contextOrder = session.items.filter((item) => contextItemFor(item));
  if (!session.contextOrder.length) {
    session = null;
    renderHome();
    return false;
  }
  renderSession();
  resetSessionScroll();
  return true;
}

function contextTargetKey(value) {
  return String(value || "").trim().toLowerCase();
}

function contextTargetMatchesItem(context, item) {
  if (!context || !item) return false;
  const target = contextTargetKey(context.target);
  return [surfaceOf(item), canonicalHeadwordOf(item)]
    .map(contextTargetKey)
    .filter(Boolean)
    .includes(target);
}

function contextVocabularyItem(context, itemHint = null) {
  if (itemHint && contextTargetMatchesItem(context, itemHint)) return itemHint;
  return allVocabularyItems().find((item) => contextTargetMatchesItem(context, item)) || null;
}

function contextMeaningOf(context, itemHint = null) {
  if (context?.targetSense) return String(context.targetSense);
  const item = contextVocabularyItem(context, itemHint);
  return item ? learningMeaningOf(item) : String(context?.meaning || "");
}

function contextExampleTranslationOf(context, itemHint = null) {
  const item = contextVocabularyItem(context, itemHint);
  const firstSentence = Array.isArray(context?.fullEnglish) ? String(context.fullEnglish[0] || "").trim() : "";
  const example = String(item?.example || "").trim();
  const translation = String(item?.exampleTranslation || "").trim();
  return firstSentence && example === firstSentence ? translation : "";
}

function contextSecondSentenceTranslationOf(context) {
  const entry = state.contextTranslations?.[context?.target];
  const secondSentence = Array.isArray(context?.fullEnglish) ? String(context.fullEnglish[1] || "").trim() : "";
  return secondSentence && String(entry?.english || "").trim() === secondSentence
    ? String(entry.japanese || "").trim()
    : "";
}

function contextItemFor(item) {
  if (!item || (item._datasetId && item._datasetId !== state.datasetId)) return null;
  const pool = Array.isArray(session?.contextPool) && session.contextPool.length
    ? session.contextPool
    : state.contextItems;
  return pool.find((context) => contextTargetMatchesItem(context, item)) || null;
}

function resetContextState() {
  session.contextRevealed = false;
  session.contextChoices = null;
  session.contextChoiceTarget = "";
  session.contextPicked = null;
  session.contextCorrect = null;
}

function hasLearnContextResult(item) {
  if (!session || session.mode !== "learn" || !item) return false;
  const results = session.contextResults;
  return Boolean(results
    && typeof results === "object"
    && Object.prototype.hasOwnProperty.call(results, itemKeyOf(item)));
}

function recordLearnContextResult(item, pickedMeaning, correctMeaning) {
  if (!session || session.mode !== "learn" || !item) return;
  const key = itemKeyOf(item);
  if (!session.contextResults || typeof session.contextResults !== "object") session.contextResults = {};
  if (Object.prototype.hasOwnProperty.call(session.contextResults, key)) return;
  session.contextResults[key] = {
    pickedMeaning,
    correctMeaning,
    correct: pickedMeaning === correctMeaning,
  };
  const results = Object.values(session.contextResults);
  session.contextTotal = results.length;
  session.contextCorrectCount = results.filter((result) => result.correct).length;
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
  const isTransientContext = session.mode === "context" || session.mode === "contextLearn";
  if (!isTransientContext) saveResume();
  $("#homePanel").classList.add("hide");
  const panel = $("#sessionPanel");
  panel.classList.remove("hide");
  panel.classList.toggle("hasActionBar", session.stage === "flash");
  panel.innerHTML = "";

  const isMeaning = session.mode === "meaning";
  const isFinal = session.mode === "final";
  const isContext = session.mode === "context" || session.stage === "context";
  const q = session.q;
  const isIdiom = !isMeaning && !isFinal && !isContext && session.items[0].type === "idiom";

  // header
  panel.appendChild(el("div", { class: "itemHead" },
     el("div", {},
       el("p", { class: "label" }, sessionLabel(q, isIdiom, isMeaning, isFinal)),
       // 固定ID + tabindex=-1: カード／ステージのDOM置換後、暗記カード以外はここへフォーカスを移す（F-03）。
       el("h2", { id: "sessionStageTitle", tabindex: "-1" }, stageTitle(session.stage)),
     ),
     el("button", { class: "sessionHeadBack ghost", type: "button", onclick: () => {
       if (isTransientContext) session = null;
       else saveResume();
       renderHome();
     } }, "一覧へ戻る"),
  ));

  // stage bar
  if (isFinal) panel.appendChild(finalBar());
  else if (isContext) panel.appendChild(contextProgressBar());
  else if (session.mode === "learn" && session.stage === "flash") panel.appendChild(contextProgressBar());
  else if (isMeaning) panel.appendChild(meaningBar());
  else panel.appendChild(stageBar(session.stage));
  // 意味だけ復習・最終チェックは、それぞれ meaningBar/finalBar に位置・正誤数を集約する。
  // 重複する設問進捗カードは通常学習の3ステップだけに表示する。
  // 既存の通常学習契約: if (!isMeaning && !isFinal) panel.appendChild(questionProgressBar());
  if (!isContext && !isMeaning && !isFinal) panel.appendChild(questionProgressBar());

  const body = el("div", {});
  panel.appendChild(body);

  if (session.stage === "flash") renderFlash(body);
  else if (session.stage === "context") renderContext(body);
  else if (session.stage === "check") renderCheck(body);
  else if (session.stage === "meaningReview") renderMeaningWrongReview(body);
  else if (session.stage === "practice") renderPractice(body);
  else if (session.stage === "done") renderDone(body);

  focusSessionContext();
}

// カード・ステージをDOM置換した後、フォーカスを現在の内容へ一元的に移す（F-03）。
// 旧「次のカード」等の削除済み要素にフォーカスが残ると、次のTabが新画面の先頭から始まらない。
// 暗記カードは現在語句（.flashWord）、回答済みContextは結果見出し、それ以外はセッション見出し。
// スクロール位置は変えない（送り後の scrollFlashCardIntoView などと競合させない）。
function focusSessionContext() {
  const target = session && session.stage === "context" && session.contextRevealed === true
    ? $("#contextResultTitle")
    : session && session.stage === "flash"
    ? $("#sessionPanel .flash .flashWord")
    : $("#sessionStageTitle");
  if (target && typeof target.focus === "function") {
    target.focus({ preventScroll: true });
  }
}

function contextProgressBar() {
  if (session.mode === "learn") {
    return el("div", { class: "stageBar contextProgressBar" },
      el("div", { class: "stagePill active" }, `${session.learnIdx + 1} / ${session.items.length}語句`),
      el("div", { class: "stagePill" }, session.stage === "context" ? "文脈から発見" : "意味を覚える"),
    );
  }
  const integrated = session.mode !== "context";
  const beforeFlash = integrated && session.contextBeforeFlash;
  const total = beforeFlash
    ? session.contextOrder.length
    : (integrated ? session.checkOrder.length : session.items.length);
  const current = beforeFlash
    ? session.contextIdx + 1
    : (integrated ? session.checkIdx + 1 : session.contextIdx + 1);
  return el("div", { class: "stageBar contextProgressBar" },
    el("div", { class: "stagePill active" }, `${current} / ${total}語句`),
    el("div", { class: "stagePill" }, beforeFlash
      ? "暗記カードの前に推測"
      : integrated
      ? (session.contextRevealed ? "次に意味4択" : "まず意味を推測")
      : (session.contextRevealed ? "4択に回答済み" : "まず意味を推測")),
  );
}

function escapeContextRegExp(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function contextTextWithTarget(text, target) {
  const fragment = document.createDocumentFragment();
  const source = String(text);
  const targetPattern = escapeContextRegExp(target).replace("one's", "(?:one's|my|your|his|her|our|their)");
  const match = new RegExp(targetPattern, "i").exec(source);
  if (!match) {
    fragment.appendChild(document.createTextNode(source));
    return fragment;
  }
  fragment.appendChild(document.createTextNode(source.slice(0, match.index)));
  fragment.appendChild(el("mark", { class: "contextTargetMark" }, match[0]));
  fragment.appendChild(document.createTextNode(source.slice(match.index + match[0].length)));
  return fragment;
}

function contextMeaningChoices(item, itemHint = null) {
  if (session.contextChoiceTarget === item.target && Array.isArray(session.contextChoices)) {
    return session.contextChoices;
  }
  const pool = Array.isArray(session.contextPool) ? session.contextPool : session.items;
  const correctMeaning = contextMeaningOf(item, itemHint);
  const suppliedChoices = Array.isArray(item.choices)
    ? item.choices.filter((meaning, index, meanings) => meanings.indexOf(meaning) === index)
    : [];
  if (suppliedChoices.length === 4 && suppliedChoices.includes(correctMeaning)) {
    session.contextChoices = shuffle(suppliedChoices);
    session.contextChoiceTarget = item.target;
    return session.contextChoices;
  }
  const distractors = shuffle(pool
    .filter((candidate) => candidate !== item && contextMeaningOf(candidate) && contextMeaningOf(candidate) !== correctMeaning)
    .map((candidate) => contextMeaningOf(candidate))
    .filter((meaning, index, meanings) => meanings.indexOf(meaning) === index))
    .slice(0, 3);
  session.contextChoices = shuffle([correctMeaning, ...distractors]);
  session.contextChoiceTarget = item.target;
  return session.contextChoices;
}

function renderContext(body) {
  const isStandalone = session.mode === "context";
  const isLearn = session.mode === "learn";
  const integrated = !isStandalone;
  const beforeFlash = isLearn || (integrated && session.contextBeforeFlash);
  const sourceItem = isLearn
    ? session.items[session.learnIdx]
    : integrated
    ? (beforeFlash ? session.contextOrder[session.contextIdx] : session.checkOrder[session.checkIdx])
    : null;
  const item = isLearn || integrated ? contextItemFor(sourceItem) : session.items[session.contextIdx];
  if (!item) {
    if (isLearn) {
      enterLearnFlash();
      renderSession();
      resetSessionScroll();
    } else {
      session.stage = "check";
      renderSession();
    }
    return;
  }
  const correctMeaning = contextMeaningOf(item, sourceItem);
  const exampleTranslation = contextExampleTranslationOf(item, sourceItem);
  const secondSentenceTranslation = contextSecondSentenceTranslationOf(item);
  const last = isLearn
    ? false
    : isStandalone
    ? session.contextIdx === session.items.length - 1
    : (beforeFlash ? session.contextIdx === session.contextOrder.length - 1 : true);
  const choices = contextMeaningChoices(item, sourceItem);
  const card = el("article", { class: "contextCard" },
    el("div", { class: "contextCardHead" },
      el("p", { class: "label" }, `Q${item.q} ・ ${item.pos}`),
      el("h3", { class: "contextTargetWord" }, item.target),
    ),
    el("p", { class: "contextInstruction" },
      "targetを知らないつもりで、英文の手がかりを組み合わせて意味を推測してください。"),
  );
  const story = el("div", { class: "contextStory" });
  const displayEnglish = Array.isArray(item.mixedEnglish) && item.mixedEnglish.length === item.fullEnglish.length
    ? item.mixedEnglish
    : item.fullEnglish;
  displayEnglish.forEach((sentence, index) => {
    story.appendChild(el("p", { class: "contextSentence" },
      el("span", { class: "contextSentenceNo" }, String(index + 1)),
      el("span", { class: "contextSentenceText" }, contextTextWithTarget(sentence, item.target)),
    ));
  });
  card.appendChild(story);

  card.appendChild(el("p", { class: "label contextChoiceLabel" }, "推測した意味は？"));
  const choiceWrap = el("div", {
    class: `choices contextChoices${session.contextRevealed ? " contextChoicesAnswered" : ""}`,
    role: "group",
    "aria-label": "推測した意味の4択",
  });
  choices.forEach((meaning, index) => {
    const isCorrectChoice = meaning === correctMeaning;
    const isPicked = meaning === session.contextPicked;
    const isDim = session.contextRevealed && !isCorrectChoice && !isPicked;
    const button = el("button", {
      class: `choiceBtn contextChoiceBtn${isDim ? " contextChoiceDim" : ""}`,
      type: "button",
      onclick: () => {
        if (session.contextRevealed) return;
        session.contextPicked = meaning;
        session.contextCorrect = meaning === correctMeaning;
        session.contextRevealed = true;
        if (isLearn) recordLearnContextResult(sourceItem, meaning, correctMeaning);
        renderSession();
      },
    },
    el("span", { class: "key" }, String(index + 1)),
    el("span", { class: "contextChoiceText" }, meaning));
    if (session.contextRevealed) {
      button.disabled = true;
      if (isCorrectChoice) button.classList.add("correct");
      else if (isPicked) button.classList.add("wrong");
      if (isCorrectChoice) button.appendChild(el("span", { class: "contextChoiceState" }, "✓ 正解"));
      else if (isPicked) button.appendChild(el("span", { class: "contextChoiceState" }, "あなたの回答"));
    }
    choiceWrap.appendChild(button);
  });
  card.appendChild(choiceWrap);

  if (session.contextRevealed) {
    const isCorrect = session.contextCorrect === true;
    card.appendChild(el("div", {
      class: `feedback contextResult ${isCorrect ? "ok" : "ng"}`,
      role: "status",
      "aria-live": "polite",
    },
      el("div", { class: "contextResultHead" },
        el("span", { class: "contextResultIcon", "aria-hidden": "true" }, isCorrect ? "✓" : "!"),
        el("div", {},
          el("h3", { class: "contextResultTitle", id: "contextResultTitle", tabindex: "-1" }, isCorrect ? "正解！" : "おしい！"),
          el("p", { class: "contextResultLead" }, isCorrect ? "文脈から意味を見抜けました" : "正解を確認してから覚えましょう"),
        ),
      ),
      el("p", {}, `正しい意味：${correctMeaning}`),
      !isCorrect ? el("p", { class: "trans" }, `あなたの選択：${session.contextPicked}`) : null,
      exampleTranslation ? el("p", { class: "trans contextExampleTranslation" }, `例文の訳：${exampleTranslation}`) : null,
      secondSentenceTranslation ? el("p", { class: "trans contextSecondSentenceTranslation" }, `2文目の訳：${secondSentenceTranslation}`) : null,
    ));
    card.appendChild(el("div", { class: "actions contextActions" },
      el("button", {
        class: "cta",
        type: "button",
        onclick: () => {
          if (isLearn) {
            enterLearnFlash();
            renderSession();
            resetSessionScroll();
            return;
          }
          if (integrated && beforeFlash) {
            if (last) {
              session.contextBeforeFlash = false;
              session.stage = "flash";
              session.flashIdx = 0;
            } else {
              session.contextIdx += 1;
            }
            resetContextState();
            renderSession();
            return;
          }
          if (integrated) {
            session.stage = "check";
            resetContextState();
            renderSession();
            return;
          }
          if (last) {
            session = null;
            renderHome();
            return;
          }
          session.contextIdx += 1;
          session.contextRevealed = false;
          session.contextChoices = null;
          session.contextChoiceTarget = "";
          session.contextPicked = null;
          session.contextCorrect = null;
          renderSession();
        },
      }, isLearn ? "この単語を覚える →" : beforeFlash ? (last ? "暗記カードへ →" : "次の語句へ →")
        : (integrated ? "意味4択へ →" : (last ? "文脈推測を終える" : "次の語句へ →"))),
    ));
  }
  body.appendChild(card);
}

function sessionLabel(q, isIdiom, isMeaning, isFinal) {
  if (isFinal) return `最終チェック ${session.checkIdx + 1} / ${session.checkOrder.length}`;
  if (session?.mode === "learn" && session?.stage === "context") return `第${q}問 ・ 文脈から発見`;
  if (session?.mode === "context" || session?.stage === "context") return "文脈から推測";
  if (isMeaning) {
    // 位置「n / m」は meaningBar が持つ。ここでは種別名だけを出して重複を避ける。
    return session.stage === "meaningReview" ? "意味だけ復習・見直し" : "意味だけ復習";
  }
  return `第${q}問 ・ ${isIdiom ? "熟語" : "単語"}`;
}

function stageTitle(stage) {
  if (session && session.mode === "final") return `最終チェック${session.checkOrder.length}問`;
  if (session && session.mode === "meaning" && session.stage === "meaningReview") return "間違えた語句を見直す";
  if (session && session.mode === "context") return `文脈推測 ${session.contextIdx + 1} / ${session.items.length}`;
  if (session && session.mode === "learn" && session.stage === "context") {
    return `STEP 1　文脈から発見（${session.learnIdx + 1} / ${session.items.length}）`;
  }
  if (session && session.stage === "context") {
    const current = session.contextBeforeFlash ? session.contextIdx + 1 : session.checkIdx + 1;
    const total = session.contextBeforeFlash ? session.contextOrder.length : session.checkOrder.length;
    return `文脈から推測（${current} / ${total}）`;
  }
  if (session && session.mode === "meaning") return `意味だけの復習（最大${MEANING_SESSION_SIZE}語句）`;
  return {
    flash: session?.mode === "learn" ? "STEP 1　意味を覚える（暗記カード）" : "STEP 1　覚える（暗記カード）",
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

