/* ---- 例文を見て意味を書く（Cloudflare 版限定。featureEnabled("writtenMeaning")） ----
   意味だけ復習の対象（通常学習を終えた語句）から出題し、書いた答えを Jev で意味の近さで採点する。
   採点は Cloudflare Worker の /api/grade-meaning（worker/index.mjs）。Worker が無い・失敗した・
   確信度が低いときは自己採点に戻す。間隔復習（FSRS）の記録には混ぜず、学習履歴にだけ残す。
   参考: kobun-vocab-learning の「選択肢なしで思い出す」。 */
const WRITTEN_SESSION_SIZE = 10;
const WRITTEN_GRADE_URL = "api/grade-meaning";
// Jev の判定を自動で採用する確信度の下限（kobun-vocab-learning で jev-1.13.0 について決めた値）。
const WRITTEN_AI_AUTO_THRESHOLD = 0.8;
const WRITTEN_MAX_ANSWER_LENGTH = 60;
const WRITTEN_GRADES = ["correct", "partial", "wrong"];
const WRITTEN_NO_ANSWER = /^(?:わから(?:ない|ん|ず)|分から(?:ない|ん|ず)|わかりません|分かりません|しらない|知らない|知りません|不明|忘れた|[?？・…ー―\-.。、\s])+$/;

function writtenMeaningItems(items = []) {
  return items.filter((item) => exampleMatch(item));
}

/** 意味だけ復習カードに置く入口。Cloudflare 版以外・対象語句が無いときは null。 */
function writtenMeaningEntry(ready, learnedItems = []) {
  if (!featureEnabled("writtenMeaning") || !ready) return null;
  const items = writtenMeaningItems(learnedItems);
  if (!items.length) return null;
  const size = Math.min(WRITTEN_SESSION_SIZE, items.length);
  return el("div", { class: "writtenMeaningEntry" },
    el("p", { class: "label" }, "書いて答える"),
    el("p", { class: "hint" }, "例文の下線部の意味を自分の言葉で書きます。言い回しが違っても、意味が合っていれば正解です。"),
    el("button", {
      class: "secondaryCta writtenMeaningCta",
      type: "button",
      onclick: () => startWrittenMeaning(items),
    }, `例文を見て意味を書く（${size}語句）`),
  );
}

function startWrittenMeaning(items) {
  const queue = shuffle(writtenMeaningItems(items)).slice(0, WRITTEN_SESSION_SIZE);
  if (!queue.length) {
    renderHome();
    return false;
  }
  session = {
    mode: "written",
    q: null,
    items: queue,
    stage: "written",
    writtenIdx: 0,
    writtenResults: [],
  };
  resetWrittenItem();
  renderSession();
  resetSessionScroll();
  return true;
}

function resetWrittenItem() {
  session.writtenAnswer = "";
  session.writtenPhase = "input"; // input → grading → result | self
  session.writtenAi = null;
  session.writtenGrade = null;
  session.writtenGradedBy = null;
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

async function submitWrittenAnswer(item, rawAnswer) {
  const answer = String(rawAnswer || "").trim().slice(0, WRITTEN_MAX_ANSWER_LENGTH);
  if (!answer || session.writtenPhase !== "input") return;
  session.writtenAnswer = answer;
  const correct = learningMeaningOf(item);
  if (WRITTEN_NO_ANSWER.test(answer)) {
    finishWrittenItem(item, "wrong", "local");
    return;
  }
  if (writtenLocalMatch(answer, correct) || writtenLocalMatch(answer, item.meaning)) {
    finishWrittenItem(item, "correct", "local");
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
    finishWrittenItem(item, decision.grade, "ai");
    return;
  }
  session.writtenPhase = "self";
  renderSession();
}

function finishWrittenItem(item, grade, gradedBy) {
  session.writtenGrade = WRITTEN_GRADES.includes(grade) ? grade : "wrong";
  session.writtenGradedBy = gradedBy;
  session.writtenPhase = "result";
  session.writtenResults.push({ item, grade: session.writtenGrade, answer: session.writtenAnswer });
  const datasetId = item._datasetId || state.datasetId;
  const progress = progressFor(datasetId);
  appendLearningHistory(progress, {
    kind: "written-meaning",
    type: item.type,
    surface: surfaceOf(item),
    result: session.writtenGrade,
    gradedBy,
  });
  saveProgressFor(datasetId, progress);
  renderSession();
}

function writtenStageBar() {
  const results = session.writtenResults || [];
  const correct = results.filter((r) => r.grade === "correct").length;
  if (session.stage === "writtenDone") {
    return el("div", { class: "stageBar meaningBar" },
      el("div", { class: "stagePill active" }, `${session.items.length}語句`),
      el("div", { class: "stagePill" }, `正解 ${correct}`),
    );
  }
  return el("div", { class: "stageBar meaningBar" },
    el("div", { class: "stagePill active" }, `${session.writtenIdx + 1} / ${session.items.length}語句`),
    el("div", { class: "stagePill" }, `回答済 ${results.length} / 正解 ${correct}`),
  );
}

const WRITTEN_GRADE_LABELS = { correct: "正解", partial: "部分的に正解", wrong: "不正解" };

function renderWritten(body) {
  if (session.stage === "writtenDone") {
    renderWrittenDone(body);
    return;
  }
  const item = session.items[session.writtenIdx];
  const surface = surfaceOf(item);
  const correct = learningMeaningOf(item);
  const example = exampleMatch(item);

  const box = el("div", { class: "quizBox writtenBox" });
  box.appendChild(el("div", { class: "askExampleHead" }, buildVocabAudioButton(item, "quizListenButton")));
  const askExample = el("p", { class: "askExample" });
  askExample.appendChild(buildExampleText(item, example));
  box.appendChild(el("div", { class: "askExampleLine" }, askExample));

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
  const form = el("form", { class: "writtenForm" },
    el("label", { class: "writtenPrompt", for: inputId }, `下線部「${surface}」の意味を書いてください`),
    el("div", { class: "writtenInputRow" }, input, submitBtn),
  );
  const unknownBtn = el("button", { class: "ghost smallGhost", type: "button" }, "わからない");
  form.appendChild(el("div", { class: "writtenFormSub" }, unknownBtn));
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    submitWrittenAnswer(item, input.value);
  });
  unknownBtn.addEventListener("click", () => {
    if (session.writtenPhase !== "input") return;
    session.writtenAnswer = "わからない";
    finishWrittenItem(item, "wrong", "local");
  });
  if (session.writtenPhase !== "input") {
    input.disabled = true;
    submitBtn.disabled = true;
    unknownBtn.disabled = true;
  }
  box.appendChild(form);

  if (session.writtenPhase === "grading") {
    box.appendChild(el("p", { class: "hint writtenGrading", role: "status", "aria-live": "polite" }, "採点しています…"));
  } else if (session.writtenPhase === "self") {
    box.appendChild(writtenSelfGrade(item, surface, correct));
  } else if (session.writtenPhase === "result") {
    box.appendChild(writtenFeedback(item, surface, correct));
  }
  body.appendChild(box);

  if (session.writtenPhase === "input") {
    requestAnimationFrame(() => input.focus({ preventScroll: true }));
  }
}

function writtenAnswerLines(item, surface, correct) {
  const lines = [
    el("p", {}, `あなたの答え：${session.writtenAnswer}`),
    el("p", {}, `${surface}：${correct}`),
  ];
  if (item.exampleTranslation) {
    lines.push(el("p", { class: "trans" }, `例文訳：${item.exampleTranslation}`));
  }
  return lines;
}

function writtenSelfGrade(item, surface, correct) {
  const ai = session.writtenAi;
  const decision = decideWrittenAiGrade(ai);
  const wrap = el("div", { class: "feedback writtenFeedback writtenSelf", role: "status", "aria-live": "polite" },
    el("h3", {}, "答え合わせ"),
    ...writtenAnswerLines(item, surface, correct),
    el("p", { class: "hint" }, decision.grade
      ? `AIの判定は「${WRITTEN_GRADE_LABELS[decision.grade]}」でしたが、確信が低いため自分で判定してください。`
      : "自動採点を使えなかったため、自分で判定してください。"),
  );
  const buttons = WRITTEN_GRADES.map((grade) => el("button", {
    class: "ghost writtenSelfBtn",
    type: "button",
    onclick: () => finishWrittenItem(item, grade, "self"),
  }, { correct: "合っていた", partial: "一部だけ合っていた", wrong: "違った" }[grade]));
  const actions = answerActions(...buttons);
  wrap.appendChild(actions);
  revealAnswerActions(actions);
  return wrap;
}

function writtenFeedback(item, surface, correct) {
  const grade = session.writtenGrade;
  const tone = grade === "correct" ? "ok" : grade === "partial" ? "partial" : "ng";
  const heading = { correct: "正解！", partial: "おしい（部分的に正解）", wrong: "不正解" }[grade];
  const fb = el("div", { class: `feedback writtenFeedback ${tone}`, role: "status", "aria-live": "polite" },
    el("h3", {}, heading),
    ...writtenAnswerLines(item, surface, correct),
  );
  if (session.writtenGradedBy === "ai" && session.writtenAi) {
    fb.appendChild(el("p", { class: "hint" },
      `AIが意味の近さで採点しました（確信度 ${Math.round(Number(session.writtenAi.confidence) * 100)}%）`));
  }
  const last = session.writtenIdx === session.items.length - 1;
  const actions = answerActions(el("button", {
    class: "cta",
    type: "button",
    onclick: () => {
      if (last) {
        session.stage = "writtenDone";
      } else {
        session.writtenIdx++;
        resetWrittenItem();
      }
      renderSession();
    },
  }, last ? "結果を見る →" : "次へ →"));
  fb.appendChild(actions);
  revealAnswerActions(actions);
  return fb;
}

function renderWrittenDone(body) {
  const results = session.writtenResults || [];
  const correct = results.filter((r) => r.grade === "correct").length;
  const banner = el("div", { class: "doneBanner" },
    el("p", { class: "label", style: "color:rgba(250,249,246,.72)" }, "Step Complete"),
    el("div", { class: "big" }, `${correct} / ${session.items.length}`),
    el("h2", {}, `例文を見て意味を書く ${session.items.length}語句を完了しました`),
  );
  body.appendChild(banner);
  const list = el("ul", { class: "writtenResultList" });
  results.forEach((r) => {
    list.appendChild(el("li", { class: `writtenResult ${r.grade}` },
      el("strong", {}, `${WRITTEN_GRADE_LABELS[r.grade]}　${surfaceOf(r.item)}`),
      el("span", {}, `${learningMeaningOf(r.item)}（あなたの答え：${r.answer}）`),
    ));
  });
  body.appendChild(list);
  body.appendChild(el("div", { class: "actions" },
    el("button", { class: "cta", type: "button", onclick: () => { session = null; renderHome(); } }, "一覧へ戻る"),
  ));
}
