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
  // 本番形式の回答後だけを識別する修飾クラス。長い意味一覧の後ろで固定を解除するため（F-02）。
  actions.classList.add("practiceAnswerActions");
  box.appendChild(actions);
  revealAnswerActions(actions);
}

/* ---- DONE ---- */
function renderDone(body) {
  clearResume();
  const q = session.q;
  const isMeaning = session.mode === "meaning";
  const isFinal = session.mode === "final";
  const grade = currentGrade();
  const doneStudyPlan = !isMeaning && !isFinal && isStudyPlanGrade(grade)
    ? studyPlanSummary(new Date(), currentStudyPlan(grade), gradeQuestionEntries(grade))
    : null;
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
      banner.appendChild(el("p", {
        class: "hint meaningDueRemaining",
        role: "status",
        "aria-live": "polite",
      }, meaningSummary.due > 0
        ? `今すぐ復習する残り：${meaningSummary.due}語句`
        : "今すぐ復習する語句はありません"));
    }
  } else {
    // 締めの主役は「この設問の4語をどれだけ意味把握できたか」。本番形式1問の正誤は補助へ落とす。
    const missed = session.checkOrder.length - session.meaningCorrect;
    banner.appendChild(el("div", { class: "big" }, `${session.meaningCorrect} / ${session.checkOrder.length}`));
    banner.appendChild(el("h2", {}, `第${q}問の4語句を学習しました`));
    banner.appendChild(el("p", { class: "hint" },
      missed > 0 ? `意味を確認：${session.meaningCorrect}語つかめました（未定着 ${missed}語）` : `意味を確認：4語すべてつかめました`));
    banner.appendChild(el("p", { class: "hint" },
      `本番形式：${session.practiceResult ? "✓ 正解" : "! 不正解"}`));
    if (doneStudyPlan) {
      const dailyRemaining = doneStudyPlan.dailyRemaining;
      banner.appendChild(el("p", {
        class: "hint studyPlanDoneStatus",
        role: "status",
        "aria-live": "polite",
      }, dailyRemaining === 0
        ? "✓ 今日の学習目標を達成しました"
        : `今日の学習目標まであと${Number(dailyRemaining).toLocaleString("ja-JP")}問`));
    }
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
    } else {
      // セットを一通り終えたら、同じ種別の次のセットへそのまま進めるようにする。
      const nextSet = nextDatasetEntry();
      banner.appendChild(el("p", { class: "hint" }, `✓ ${datasetSetLabel(state.datasetId, dataset())}の全${state.qList.length}問を学習しました`));
      if (nextSet) {
        const [nextId, nextData] = nextSet;
        actions.appendChild(el("button", { class: "cta", onclick: () => startNextDataset(nextId) },
          `次のセットへ（${datasetSetLabel(nextId, nextData)}） →`));
      } else {
        actions.appendChild(el("button", { class: "cta", onclick: renderHome }, "次の学習を選ぶ →"));
      }
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
