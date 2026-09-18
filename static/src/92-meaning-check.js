/* ---- STEP 2: meaning check ---- */
function renderCheck(body) {
  armChoiceGuard();
  const item = session.checkOrder[session.checkIdx];
  const surface = canonicalHeadwordOf(item);
  const correct = learningMeaningOf(item);
  const example = session.mode === "meaning" ? exampleMatch(item) : null;

  // 「4語句」はユニット学習（1ユニット＝4語句）だけの数。意味だけ復習(最大30)・最終チェック(全語句)では
  // 現在地バーと meaningBar/finalBar が位置を持つため roundInfo は出さない（"4語句…12/30" の矛盾表示を避ける）。
  if (session.mode === "learn") {
    body.appendChild(el("div", { class: "roundInfo" }, `4語句の意味確認 ${session.checkIdx + 1} / ${session.checkOrder.length}`));
  }

  // 出題表示の時刻。音声を押さなかった設問もここを起点に解答時間を測る
  if (!session.checkShownAt) session.checkShownAt = Date.now();

  const box = el("div", { class: "quizBox" });
  const listenButton = buildVocabAudioButton(item, "quizListenButton");
  if (example) {
    // 音声ボタンは設問文の行へ逃がす。例文と横に並べると英文の折り返しが早まる。
    box.appendChild(el("div", { class: "askExampleHead" }, listenButton));
    const askExample = el("p", { class: "askExample" });
    askExample.appendChild(buildExampleText(item, example));
    box.appendChild(el("div", { class: "askExampleLine" }, askExample));
  } else {
    box.appendChild(el("p", { class: "label" }, "次の語句の意味は？"));
    box.appendChild(el("div", { class: "askWordLine" },
      el("p", { class: "askWord" }, surface),
      listenButton,
    ));
  }

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
  if (session.mode === "meaning" && item.exampleTranslation) {
    fb.appendChild(el("p", { class: "trans checkExampleTranslation" }, `例文訳：${item.exampleTranslation}`));
  }
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

