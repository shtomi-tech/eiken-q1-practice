/* ---- 意味を書く演習（Cloudflare 版限定。featureEnabled("writtenMeaning")） ----
   意味だけ復習の対象（通常学習を終えた語句）から出題し、書いた答えを Jev で意味の近さで採点する。
   出題は段階式: まず単語だけで書く → 誤答・わからない → 例文をヒントにもう一度 → それでも誤答 → 答えを確認。
   単語だけで正解＝覚えた、例文で正解＝あやふや（セッションの最後にもう一度）、答えを見た＝未習得
   （数問あとに単語だけでもう一度）。記憶から引き出す負荷を先に掛け、例文は補助に回す
   （例文あり・なしの定着比較のリサーチより）。
   採点は Cloudflare Worker の /api/grade-meaning（worker/index.mjs）。Worker が無い・失敗した・
   確信度が低いときは自己採点に戻す。間隔復習（FSRS）の評価には混ぜない。ただし答えを見た語は、
   意味だけ復習の期限を今へ早める（評価は付けず、間隔の計算は次の復習の解答に任せる）。
   出題は直近の結果で選ぶ: 苦手（未習得 → あやふや）を約6割、まだ書いていない語を残りに充てる。
   参考: kobun-vocab-learning の「選択肢なしで思い出す」。 */
const WRITTEN_SESSION_SIZE = 10;
// 答えを見た語を、何問あとにもう一度出すか。
const WRITTEN_REASK_GAP = 3;
const WRITTEN_GRADE_URL = "api/grade-meaning";
// Jev の判定を自動で採用する確信度の下限（kobun-vocab-learning で jev-1.13.0 について決めた値）。
const WRITTEN_AI_AUTO_THRESHOLD = 0.8;
const WRITTEN_MAX_ANSWER_LENGTH = 60;
const WRITTEN_GRADES = ["correct", "partial", "wrong"];
const WRITTEN_NO_ANSWER = /^(?:わから(?:ない|ん|ず)|分から(?:ない|ん|ず)|わかりません|分かりません|しらない|知らない|知りません|不明|忘れた|[?？・…ー―\-.。、\s])+$/;
const WRITTEN_OUTCOME_LABELS = { learned: "単語だけで正解", shaky: "例文で正解", notLearned: "答えを確認" };
// 1回の出題のうち、苦手な語（未習得・あやふや）に充てる割合。残りはまだ書いていない語。
const WRITTEN_WEAK_SHARE = 0.6;

// 2段目のヒントに例文を使うため、例文の中に出題形が見つかる語句だけを出す。
function writtenMeaningItems(items = []) {
  return items.filter((item) => exampleMatch(item));
}

const WRITTEN_SIZE_CHOICES = [5, 10, 20];
const WRITTEN_SIZE_KEY = "eiken_q1_written_size_v1";

function writtenSizeChoices(available) {
  return [...new Set(WRITTEN_SIZE_CHOICES.map((size) => Math.min(size, available)))].filter((size) => size > 0);
}

function preferredWrittenSize(choices) {
  let stored = WRITTEN_SESSION_SIZE;
  try { stored = Number(localStorage.getItem(WRITTEN_SIZE_KEY)) || WRITTEN_SESSION_SIZE; } catch (e) { /* ignore */ }
  return choices.includes(stored) ? stored : choices[choices.length - 1];
}

/**
 * 「書く」の独立カード。意味だけ復習とは別の入口として、ホームの「書く」タブに置く。
 * Cloudflare 版以外では null。対象語句が無いときも、何をすれば使えるかを示す。
 */
function writtenMeaningCard(ready, learnedItems = []) {
  if (!featureEnabled("writtenMeaning")) return null;
  const items = ready ? writtenMeaningItems(learnedItems) : [];
  const card = el("section", { class: "card writtenMeaningCard", "aria-labelledby": "writtenMeaningTitle" },
    el("p", { class: "label" }, "書いて覚える"),
    el("h3", { id: "writtenMeaningTitle" }, `単語の意味を書く（${dataset().shortLabel}）`),
    el("p", { class: "writtenMeaningLead" },
      "選択肢なしで、単語を見て意味を自分の言葉で書きます。言い回しが違っても、意味が合っていれば正解です。"),
    el("ol", { class: "writtenMeaningSteps" },
      el("li", {}, el("strong", {}, "単語だけ"), el("span", {}, "まず何も見ずに書く")),
      el("li", {}, el("strong", {}, "例文ヒント"), el("span", {}, "わからなければ例文を見てもう一度")),
      el("li", {}, el("strong", {}, "答えを確認"), el("span", {}, "数問あとに単語だけでもう一度")),
    ),
  );
  const ctaClass = homeTabsEnabled() ? "cta writtenMeaningCta" : "secondaryCta writtenMeaningCta";
  if (!ready || !items.length) {
    card.appendChild(el("button", { class: ctaClass, type: "button", disabled: "disabled" },
      ready ? "通常学習後に利用できます" : "対象を確認中…"));
    if (ready) card.appendChild(el("p", { class: "hint" }, "通常学習で本番形式まで解いた語句から出題します。"));
    return card;
  }
  const choices = writtenSizeChoices(items.length);
  let size = preferredWrittenSize(choices);
  const startBtn = el("button", { class: ctaClass, type: "button", onclick: () => startWrittenMeaning(items, size) });
  const sizeButtons = choices.map((choice) => el("button", {
    class: "writtenSizeChoice",
    type: "button",
    onclick: () => {
      size = choice;
      writeStored(WRITTEN_SIZE_KEY, String(choice));
      sync();
    },
  }, `${choice}語句`));
  function sync() {
    sizeButtons.forEach((button, i) => button.setAttribute("aria-pressed", String(choices[i] === size)));
    startBtn.textContent = `書きはじめる（${size}語句）`;
  }
  sync();
  card.appendChild(el("div", { class: "writtenSizeRow" },
    el("span", { class: "fieldLabel", id: "writtenSizeLabel" }, "1回の語句数"),
    el("div", { class: "writtenSizeChoices", role: "group", "aria-labelledby": "writtenSizeLabel" }, ...sizeButtons),
  ));
  card.appendChild(startBtn);
  card.appendChild(el("p", { class: "hint" },
    `出題できる語句：${items.length}語句（通常学習を終えた語句から毎回ランダム）。採点はAIが意味の近さで行い、判定が難しいときは自分で判定します。`));
  return card;
}

/**
 * 語句ごとの「書く」の直近の結果を添える。progress.written が正本で、
 * 記録が無い語は学習履歴の written-meaning から拾う（progress.written を足す前の分）。
 */
function writtenEntries(items) {
  const fromHistory = new Map();
  const historyFor = (datasetId, progress) => {
    if (fromHistory.has(datasetId)) return fromHistory.get(datasetId);
    const latest = new Map();
    for (const event of Array.isArray(progress.history) ? progress.history : []) {
      if (!event || event.kind !== "written-meaning" || !WRITTEN_OUTCOME_LABELS[event.result]) continue;
      latest.set(`${event.type}:${String(event.surface || "").toLowerCase()}`, { outcome: event.result, at: event.at });
    }
    fromHistory.set(datasetId, latest);
    return latest;
  };
  return items.map((item) => {
    const datasetId = item._datasetId || state.datasetId;
    const progress = progressFor(datasetId) || {};
    const saved = progress.written && progress.written[itemKeyOf(item)];
    const last = saved && WRITTEN_OUTCOME_LABELS[saved.outcome]
      ? saved
      : historyFor(datasetId, progress).get(`${item.type}:${String(surfaceOf(item) || "").toLowerCase()}`);
    return { item, outcome: last ? last.outcome : null, at: last ? last.at : null };
  });
}

/**
 * 出題する語句を選ぶ純粋ロジック。entries: [{ item, outcome, at }]（まだ書いていない語は outcome: null）。
 * 苦手（未習得 → あやふや）を size の約6割、まだ書いていない語を残りに充て、足りない枠は互いに埋め合う。
 * それでも足りなければ、単語だけで正解した語を前に書いた順に足す。出題順はシャッフルする。
 */
function pickWrittenItems(entries, size, shuffleFn = shuffle) {
  const withOutcome = (outcome) => shuffleFn(entries.filter((entry) => entry.outcome === outcome));
  const weak = [...withOutcome("notLearned"), ...withOutcome("shaky")];
  const fresh = withOutcome(null);
  const learned = entries.filter((entry) => entry.outcome === "learned")
    .sort((a, b) => String(a.at || "").localeCompare(String(b.at || "")));
  const weakSlots = Math.min(weak.length, Math.ceil(size * WRITTEN_WEAK_SHARE));
  const picked = weak.slice(0, weakSlots);
  picked.push(...fresh.slice(0, size - picked.length));
  picked.push(...weak.slice(weakSlots, weakSlots + size - picked.length));
  picked.push(...learned.slice(0, size - picked.length));
  return shuffleFn(picked).map((entry) => entry.item);
}

/** 意味だけ復習の期限を now へ早める。まだ復習していない語（すでに対象）と期限切れの語は触らない。 */
function pullMeaningReviewForward(progress, key, now = new Date()) {
  const current = progress.items && progress.items[key];
  if (!current || !current.lastAnsweredAt || !current.nextReviewAt) return false;
  if (new Date(current.nextReviewAt).getTime() <= now.getTime()) return false;
  const due = now.toISOString();
  current.nextReviewAt = due;
  if (current.fsrs && typeof current.fsrs === "object") current.fsrs.due = due;
  return true;
}

function startWrittenMeaning(items, size = WRITTEN_SESSION_SIZE) {
  const pool = writtenMeaningItems(items);
  const picked = withProgressReadCache(() => pickWrittenItems(writtenEntries(pool), size));
  if (!picked.length) {
    renderHome();
    return false;
  }
  session = {
    mode: "written",
    q: null,
    items: picked,
    // 結果画面の「続けて書く」用。
    writtenPool: pool,
    writtenSize: size,
    stage: "written",
    // 出題順。{ item, reask }。あやふや・未習得の語は reask: true で後ろへ差し込む。
    writtenQueue: picked.map((item) => ({ item, reask: false })),
    writtenPos: 0,
    // 語句ごとの結果。{ item, outcome, answers: [], reaskResult }
    writtenResults: [],
  };
  wireWrittenEnterKey();
  resetWrittenTurn();
  renderSession();
  resetSessionScroll();
  return true;
}

function resetWrittenTurn() {
  session.writtenStep = "word"; // word → example（初回の誤答・わからない）
  session.writtenPhase = "input"; // input → grading → self → result | answer
  session.writtenAnswer = "";
  session.writtenAnswers = [];
  session.writtenAi = null;
  session.writtenGradedBy = null;
  session.writtenOutcome = null;
  session.writtenAdvanceReadyAt = Infinity;
}

/**
 * 1回の採点結果から次の段階を決める純粋ロジック。
 * step: "word" | "example"、reask: 再出題か、grade: "correct" | "partial" | "wrong"。
 * 戻り値の next は "example"（例文をヒントにもう一度）| "result"（正解で次へ）| "answer"（答えを確認）。
 */
function writtenNextStep(step, reask, grade) {
  const correct = grade === "correct";
  if (reask) return { next: correct ? "result" : "answer", reaskResult: correct ? "correct" : "wrong" };
  if (step === "word") return correct ? { next: "result", outcome: "learned" } : { next: "example" };
  return correct ? { next: "result", outcome: "shaky" } : { next: "answer", outcome: "notLearned" };
}

/** 再出題を差し込む位置。未習得は数問あと、あやふやはセッションの最後。 */
function writtenReaskIndex(outcome, pos, length, gap = WRITTEN_REASK_GAP) {
  if (outcome === "notLearned") return Math.min(pos + 1 + gap, length);
  if (outcome === "shaky") return length;
  return -1;
}

function normalizeWrittenMeaning(value) {
  return String(value || "")
    .normalize("NFKC")
    .replace(/[「」『』【】（）()［］[\]〔〕、。，．,.・／/〜~～;；:：!！?？\s]/g, "")
    .replace(/(?:すること|こと|する|な|の)$/u, "");
}

/** 正解の語義のどれかと表記ゆれ程度で一致すれば、Jev に送らず正解にする。 */
function writtenLocalMatch(answer, meaning) {
  const target = normalizeWrittenMeaning(answer);
  if (!target) return false;
  return String(meaning || "")
    .split(/[、；;／,，]/)
    .map(normalizeWrittenMeaning)
    .filter(Boolean)
    .includes(target);
}

/** Jev の判定を採用するか。採用しないときは参考表示にして自己採点へ戻す。 */
function decideWrittenAiGrade(result) {
  if (!result || !WRITTEN_GRADES.includes(result.grade)) return { auto: false, grade: null };
  const confidence = Number(result.confidence);
  if (!Number.isFinite(confidence) || confidence < WRITTEN_AI_AUTO_THRESHOLD) return { auto: false, grade: result.grade };
  return { auto: true, grade: result.grade };
}

async function requestWrittenGrade(item, answer) {
  const controller = typeof AbortController === "function" ? new AbortController() : null;
  const timer = controller ? setTimeout(() => controller.abort(), 12000) : null;
  try {
    const response = await fetch(WRITTEN_GRADE_URL, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        datasetId: item._datasetId || state.datasetId,
        type: item.type,
        surface: surfaceOf(item),
        answer,
      }),
      signal: controller ? controller.signal : undefined,
    });
    if (!response.ok) return null;
    return await response.json();
  } catch (e) {
    return null;
  } finally {
    if (timer) clearTimeout(timer);
  }
}

function currentWrittenEntry() {
  return session.writtenQueue[session.writtenPos];
}

async function submitWrittenAnswer(rawAnswer) {
  const answer = String(rawAnswer || "").trim().slice(0, WRITTEN_MAX_ANSWER_LENGTH);
  if (!answer || session.writtenPhase !== "input") return;
  const { item } = currentWrittenEntry();
  session.writtenAnswer = answer;
  if (WRITTEN_NO_ANSWER.test(answer)) {
    applyWrittenGrade("wrong", "local");
    return;
  }
  if (writtenLocalMatch(answer, learningMeaningOf(item)) || writtenLocalMatch(answer, item.meaning)) {
    applyWrittenGrade("correct", "local");
    return;
  }
  session.writtenPhase = "grading";
  renderSession();
  const current = session;
  const result = await requestWrittenGrade(item, answer);
  // 採点待ちの間に一覧へ戻った・別の演習を始めたときは結果を捨てる。
  if (session !== current || session.writtenPhase !== "grading") return;
  session.writtenAi = result;
  const decision = decideWrittenAiGrade(result);
  if (decision.auto) {
    applyWrittenGrade(decision.grade, "ai");
    return;
  }
  session.writtenPhase = "self";
  renderSession();
}

function applyWrittenGrade(grade, gradedBy) {
  const entry = currentWrittenEntry();
  const safeGrade = WRITTEN_GRADES.includes(grade) ? grade : "wrong";
  session.writtenGradedBy = gradedBy;
  session.writtenAnswers.push({ step: session.writtenStep, answer: session.writtenAnswer, grade: safeGrade, gradedBy });
  const step = writtenNextStep(session.writtenStep, entry.reask, safeGrade);
  if (step.next === "example") {
    session.writtenStep = "example";
    session.writtenPhase = "input";
    session.writtenAnswer = "";
    session.writtenAi = null;
    renderSession();
    return;
  }
  recordWrittenResult(entry, step);
  session.writtenPhase = step.next;
  session.writtenAdvanceReadyAt = performance.now();
  renderSession();
}

function recordWrittenResult(entry, step) {
  const { item } = entry;
  if (entry.reask) {
    const result = session.writtenResults.find((r) => r.item === item);
    if (result) result.reaskResult = step.reaskResult;
  } else {
    session.writtenOutcome = step.outcome;
    session.writtenResults.push({ item, outcome: step.outcome, answers: session.writtenAnswers.slice(), reaskResult: null });
    const at = writtenReaskIndex(step.outcome, session.writtenPos, session.writtenQueue.length);
    if (at >= 0) session.writtenQueue.splice(at, 0, { item, reask: true });
  }
  const datasetId = item._datasetId || state.datasetId;
  const progress = progressFor(datasetId);
  let reviewPulled = false;
  if (!entry.reask) {
    const key = itemKeyOf(item);
    const now = new Date();
    if (!progress.written || typeof progress.written !== "object") progress.written = {};
    progress.written[key] = { outcome: step.outcome, at: now.toISOString() };
    if (step.outcome === "notLearned") reviewPulled = pullMeaningReviewForward(progress, key, now);
  }
  appendLearningHistory(progress, {
    kind: "written-meaning",
    type: item.type,
    surface: surfaceOf(item),
    result: entry.reask ? `reask-${step.reaskResult}` : step.outcome,
    hintUsed: session.writtenAnswers.some((a) => a.step === "example"),
    gradedBy: session.writtenGradedBy,
    ...(reviewPulled ? { reviewPulled: true } : {}),
  });
  saveProgressFor(datasetId, progress);
}

function advanceWritten() {
  if (session.writtenPos >= session.writtenQueue.length - 1) {
    session.stage = "writtenDone";
  } else {
    session.writtenPos++;
    resetWrittenTurn();
  }
  renderSession();
}

/**
 * 結果画面（正解・答えの確認）で Enter を「次へ」として扱ってよいか。
 * 採点を送った Enter・押しっぱなし・IME 変換確定の Enter では進めない。
 * ボタンやリンクに焦点があるときはブラウザ標準の動作に任せる。
 */
function writtenEnterAdvances(event, phase, readyAt) {
  if (phase !== "result" && phase !== "answer") return false;
  if (event.key !== "Enter" || event.repeat || event.isComposing || event.keyCode === 229) return false;
  if (event.ctrlKey || event.altKey || event.metaKey || event.shiftKey) return false;
  if (!(event.timeStamp > readyAt)) return false;
  const tag = String(event.target?.tagName || "").toUpperCase();
  return !["BUTTON", "A", "INPUT", "TEXTAREA", "SELECT"].includes(tag);
}

let writtenEnterKeyWired = false;
function wireWrittenEnterKey() {
  if (writtenEnterKeyWired) return;
  writtenEnterKeyWired = true;
  document.addEventListener("keydown", (event) => {
    if (!session || session.mode !== "written" || session.stage !== "written") return;
    if (!writtenEnterAdvances(event, session.writtenPhase, session.writtenAdvanceReadyAt)) return;
    event.preventDefault();
    advanceWritten();
  });
}

function writtenStageBar() {
  const results = session.writtenResults || [];
  const learned = results.filter((r) => r.outcome === "learned").length;
  if (session.stage === "writtenDone") {
    return el("div", { class: "stageBar meaningBar" },
      el("div", { class: "stagePill active" }, `${session.items.length}語句`),
      el("div", { class: "stagePill" }, `単語だけで正解 ${learned}`),
    );
  }
  return el("div", { class: "stageBar meaningBar" },
    el("div", { class: "stagePill active" }, `${session.writtenPos + 1} / ${session.writtenQueue.length}問`),
    el("div", { class: "stagePill" }, `単語だけで正解 ${learned} / ${session.items.length}`),
  );
}

function renderWritten(body) {
  if (session.stage === "writtenDone") {
    renderWrittenDone(body);
    return;
  }
  const entry = currentWrittenEntry();
  const { item } = entry;
  const headword = canonicalHeadwordOf(item);
  const showExample = session.writtenStep === "example" || session.writtenPhase === "answer";

  const box = el("div", { class: "quizBox writtenBox" });
  if (entry.reask) box.appendChild(el("p", { class: "writtenReaskBadge" }, "もう一度"));
  box.appendChild(el("div", { class: "askWordLine" },
    el("p", { class: "askWord" }, headword),
    buildVocabAudioButton(item, "quizListenButton"),
  ));
  if (showExample) {
    const askExample = el("p", { class: "askExample" });
    askExample.appendChild(buildExampleText(item, exampleMatch(item)));
    box.appendChild(el("div", { class: "askExampleLine writtenHintExample" }, askExample));
  }

  const previous = session.writtenAnswers.filter((a) => a.step === "word");
  if (session.writtenStep === "example" && session.writtenPhase !== "answer" && previous.length) {
    box.appendChild(el("p", { class: "hint writtenPrevious" },
      `1回目の答え：${previous[previous.length - 1].answer}　→ 例文をヒントにもう一度書いてください。`));
  }

  if (session.writtenPhase === "input" || session.writtenPhase === "grading" || session.writtenPhase === "self") {
    box.appendChild(writtenForm(headword));
  }
  if (session.writtenPhase === "grading") {
    box.appendChild(el("p", { class: "hint writtenGrading", role: "status", "aria-live": "polite" }, "採点しています…"));
  } else if (session.writtenPhase === "self") {
    box.appendChild(writtenSelfGrade(item, headword));
  } else if (session.writtenPhase === "result") {
    box.appendChild(writtenCorrectFeedback(entry, headword));
  } else if (session.writtenPhase === "answer") {
    box.appendChild(writtenAnswerReveal(entry, headword));
  }
  body.appendChild(box);
}

function writtenForm(headword) {
  const inputId = "writtenAnswerInput";
  const input = el("input", {
    id: inputId,
    class: "writtenAnswerInput",
    type: "text",
    maxlength: String(WRITTEN_MAX_ANSWER_LENGTH),
    autocomplete: "off",
    autocapitalize: "off",
    spellcheck: "false",
    placeholder: "例：同意する",
  });
  input.value = session.writtenAnswer || "";
  const submitBtn = el("button", { class: "cta", type: "submit" }, "採点する");
  const prompt = session.writtenStep === "example"
    ? `例文の下線部「${headword}」の意味を書いてください`
    : `「${headword}」の意味を書いてください`;
  const form = el("form", { class: "writtenForm" },
    el("label", { class: "writtenPrompt", for: inputId }, prompt),
    el("div", { class: "writtenInputRow" }, input, submitBtn),
  );
  const unknownBtn = el("button", { class: "ghost smallGhost", type: "button" },
    session.writtenStep === "word" && !currentWrittenEntry().reask ? "わからない（例文を見る）" : "わからない（答えを見る）");
  form.appendChild(el("div", { class: "writtenFormSub" }, unknownBtn));
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    submitWrittenAnswer(input.value);
  });
  unknownBtn.addEventListener("click", () => {
    if (session.writtenPhase !== "input") return;
    session.writtenAnswer = "わからない";
    applyWrittenGrade("wrong", "local");
  });
  if (session.writtenPhase !== "input") {
    input.disabled = true;
    submitBtn.disabled = true;
    unknownBtn.disabled = true;
  } else {
    requestAnimationFrame(() => input.focus({ preventScroll: true }));
  }
  return form;
}

function writtenSelfGrade(item, headword) {
  const decision = decideWrittenAiGrade(session.writtenAi);
  const wrap = el("div", { class: "feedback writtenFeedback writtenSelf", role: "status", "aria-live": "polite" },
    el("h3", {}, "答え合わせ"),
    el("p", {}, `あなたの答え：${session.writtenAnswer}`),
    el("p", {}, `${headword}：${learningMeaningOf(item)}`),
    el("p", { class: "hint" }, decision.grade
      ? `AIの判定は「${{ correct: "正解", partial: "部分的に正解", wrong: "不正解" }[decision.grade]}」でしたが、確信が低いため自分で判定してください。`
      : "自動採点を使えなかったため、自分で判定してください。"),
  );
  const buttons = [["correct", "合っていた"], ["wrong", "違った"]].map(([grade, label]) => el("button", {
    class: "ghost writtenSelfBtn",
    type: "button",
    onclick: () => applyWrittenGrade(grade, "self"),
  }, label));
  const actions = answerActions(...buttons);
  wrap.appendChild(actions);
  revealAnswerActions(actions);
  return wrap;
}

function writtenAiNote() {
  if (session.writtenGradedBy !== "ai" || !session.writtenAi) return null;
  return el("p", { class: "hint" },
    `AIが意味の近さで採点しました（確信度 ${Math.round(Number(session.writtenAi.confidence) * 100)}%）`);
}

function writtenCorrectFeedback(entry, headword) {
  const { item } = entry;
  const heading = entry.reask
    ? "正解！ 今度は単語だけで思い出せました"
    : session.writtenOutcome === "learned"
      ? "正解！ 単語だけで思い出せました"
      : "正解！ 例文を手がかりに思い出せました";
  const fb = el("div", { class: "feedback writtenFeedback ok", role: "status", "aria-live": "polite" },
    el("h3", {}, heading),
    el("p", {}, `あなたの答え：${session.writtenAnswer}`),
    el("p", {}, `${headword}：${learningMeaningOf(item)}`),
  );
  if (!entry.reask && session.writtenOutcome === "shaky") {
    fb.appendChild(el("p", { class: "hint" }, "まだあやふやなので、最後にもう一度単語だけで出します。"));
  }
  const ai = writtenAiNote();
  if (ai) fb.appendChild(ai);
  const last = session.writtenPos >= session.writtenQueue.length - 1;
  const actions = answerActions(el("button", { class: "cta", type: "button", onclick: advanceWritten },
    last ? "結果を見る →" : "次へ →"));
  fb.appendChild(actions);
  revealAnswerActions(actions);
  return fb;
}

/** 答えを例文と並べて確認させる。確認ボタンを押すまで次へ進めない。 */
function writtenAnswerReveal(entry, headword) {
  const { item } = entry;
  const fb = el("div", { class: "feedback writtenFeedback ng", role: "status", "aria-live": "polite" },
    el("h3", {}, "答えを確認しましょう"),
    el("p", { class: "writtenAnswerMeaning" }, `${headword}：${learningMeaningOf(item)}`),
  );
  session.writtenAnswers.forEach((a) => {
    fb.appendChild(el("p", { class: "trans" }, `${a.step === "word" ? "単語だけ" : "例文あり"}の答え：${a.answer}`));
  });
  if (item.exampleTranslation) fb.appendChild(el("p", { class: "trans" }, `例文訳：${item.exampleTranslation}`));
  fb.appendChild(el("p", { class: "hint" }, entry.reask
    ? "上の例文の中で、意味を確かめてから進んでください。"
    : `上の例文の中で、意味を確かめてから進んでください。${WRITTEN_REASK_GAP}問ほどあとに、もう一度単語だけで出します。`));
  const actions = answerActions(el("button", { class: "cta", type: "button", onclick: advanceWritten }, "確認した →"));
  fb.appendChild(actions);
  revealAnswerActions(actions);
  return fb;
}

function renderWrittenDone(body) {
  const results = session.writtenResults || [];
  const count = (outcome) => results.filter((r) => r.outcome === outcome).length;
  const reasked = results.filter((r) => r.reaskResult);
  const banner = el("div", { class: "doneBanner" },
    el("p", { class: "label", style: "color:rgba(250,249,246,.72)" }, "Step Complete"),
    el("div", { class: "big" }, `${count("learned")} / ${session.items.length}`),
    el("h2", {}, "単語だけで思い出せた語句"),
    el("p", { class: "hint", style: "color:rgba(250,249,246,.72)" },
      `例文で正解 ${count("shaky")}・答えを確認 ${count("notLearned")}${reasked.length
        ? `・再出題で正解 ${reasked.filter((r) => r.reaskResult === "correct").length} / ${reasked.length}`
        : ""}`),
  );
  body.appendChild(banner);
  const list = el("ul", { class: "writtenResultList" });
  results.forEach((r) => {
    const reask = r.reaskResult ? `／再出題：${r.reaskResult === "correct" ? "正解" : "不正解"}` : "";
    list.appendChild(el("li", { class: `writtenResult ${r.outcome}` },
      el("strong", {}, `${WRITTEN_OUTCOME_LABELS[r.outcome]}　${canonicalHeadwordOf(r.item)}`),
      el("span", {}, `${learningMeaningOf(r.item)}${reask}`),
    ));
  });
  body.appendChild(list);
  const { writtenPool, writtenSize } = session;
  body.appendChild(el("div", { class: "actions" },
    el("button", { class: "cta", type: "button", onclick: () => startWrittenMeaning(writtenPool, writtenSize) },
      `続けて書く（${Math.min(writtenSize, writtenPool.length)}語句）`),
    el("button", { class: "secondaryCta", type: "button", onclick: () => { session = null; renderHome(); } }, "ホームへ戻る"),
  ));
}
