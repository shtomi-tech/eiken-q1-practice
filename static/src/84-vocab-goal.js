// 語彙目標カード。前の級までは習得済みという前提で、前級目標→当級目標の区間を進捗として見せる。
// 分子の実績は「その級で通常学習まで終えた語句数」（meaningPracticeSummary().learned と同じ母集団）。
function vocabGoalCard(learned, ready, studyPlanNode = null) {
  const goal = VOCAB_GOALS[currentGrade()];
  if (!goal) return null;
  const gap = goal.target - goal.prev;
  const own = ready ? Math.min(learned, gap) : 0;
  const value = goal.prev + own;
  const pct = (n) => `${(n / goal.target) * 100}%`;
  const num = (n) => n.toLocaleString("ja-JP");
  const message = !ready ? "読み込み中…"
    : own === 0 ? `ここからが${dataset().shortLabel}の${num(gap)}語。まず1問めから。`
    : own < gap * 0.25 ? "一歩めが出ました。それがいちばん大変。"
    : own < gap * 0.5 ? "歩き出しました。この調子。"
    : own < gap * 0.75 ? "半分をこえました。"
    : "ゴールが見えてきました。";

  const walker = el("div", { class: "vgHedgehog", "aria-hidden": "true", "data-walking": own > 0 ? "1" : "" },
    el("span", { class: "vgHedgehogSprite" }));
  walker.style.left = pct(value);

  const base = el("div", { class: "vgFillBase" });
  base.style.width = pct(goal.prev);
  const ownFill = el("div", { class: "vgFillOwn" });
  ownFill.style.left = pct(goal.prev);
  ownFill.style.width = own > 0 ? `max(3px, ${pct(own)})` : "0";

  const track = el("div", {
    class: "vgTrack",
    role: "progressbar",
    "aria-label": `${dataset().shortLabel}の語彙目標進捗`,
    "aria-valuemin": "0",
    "aria-valuemax": String(goal.target),
    "aria-valuenow": String(value),
    "aria-valuetext": goal.prev > 0
      ? `${dataset().shortLabel}の目標${num(goal.target)}語のうち${num(value)}語。${goal.prevLabel}までの${num(goal.prev)}語に、このアプリで学習した${num(own)}語句を足した数です。`
      : `${dataset().shortLabel}の目標${num(goal.target)}語のうち${num(value)}語。このアプリで学習した語句の数です。`,
  }, base, ownFill, walker);

  // 5級は前級を持たない（prev=0）ため、意味のない「0」の目盛りを出さない。
  const prevTick = goal.prev > 0
    ? el("span", { class: "vgTick vgTickMid" },
      el("strong", {}, num(goal.prev)), el("small", {}, goal.prevLabel))
    : null;
  if (prevTick) prevTick.style.left = pct(goal.prev);

  const forecast = isStudyPlanGrade(currentGrade())
    ? (ready
      // detailsにはroleが無くaria-labelledbyが効かないため、名前はsummary自身が持つ。
      ? el("details", { class: "vocabForecast" })
      : el("div", { class: "vocabForecast", "aria-labelledby": "vocabForecastTitle" }))
    : null;
  if (forecast) {
    if (!ready) {
      forecast.appendChild(el("h4", { id: "vocabForecastTitle" }, "このペースで学べる語句"));
      forecast.appendChild(el("p", { class: "hint" }, `英検${dataset().shortLabel}通常問題の語句を読み込み中…`));
    } else {
      const gradePlan = currentStudyPlan() || defaultStudyPlan();
      const goalForecast = vocabularyGoalForecast(new Date(), gradePlan, learned, goal);
      const periods = vocabularyForecast(gradePlan);
      const forecastSummary = el("summary", { id: "vocabForecastTitle" },
        el("span", { class: "vocabForecastSummaryTitle" }, "このペースで学べる語句"),
        el("span", { class: "vocabForecastLead" },
          `このペースなら${num(goal.target)}語まであと${num(goalForecast.remainingVocabulary)}語`),
      );
      forecast.appendChild(forecastSummary);
      forecast.appendChild(el("p", { class: "hint vocabForecastDate" }, goalForecast.remainingVocabulary === 0
        ? `${num(goal.target)}語の目安に到達しています。`
        : `1日${num(goalForecast.dailyVocabulary)}語句で、${goalForecast.estimatedDate.toLocaleDateString("ja-JP", { year: "numeric", month: "long", day: "numeric" })}ごろ（あと${num(goalForecast.daysToGoal)}日）`));
      forecast.appendChild(el("div", { class: "vocabForecastGrid", "aria-label": "期間別の理論上の語句予測" },
        ...periods.map(({ days, vocabulary }) => {
          const label = { 7: "1週間後", 30: "1か月後", 90: "3か月後", 180: "半年後", 365: "1年後" }[days] || `${days}日後`;
          return el("div", { class: "vocabForecastRow" },
            el("span", {}, label),
            el("strong", {}, `+${num(vocabulary)}語句`),
          );
        })),
      );
      forecast.appendChild(el("p", { class: "hint" },
        `理論上の学習量です。現在、このアプリの英検${dataset().shortLabel}通常問題には${num(gradeVocabularyItems().length)}語句を収録しています。このアプリだけの収録数を超える予測を含みます。`));
    }
  }

  // 見出し・語数・バー・ハリネズミ・目盛り・励ましメッセージは常時表示（ハリネズミの現在地が主モチベーション）。
  // 折りたたむのは期間別予測（forecast＝.vocabForecast）だけ。
  return el("section", { class: "card vocabGoalCard", "aria-labelledby": "vocabGoalTitle" },
    studyPlanNode,
    el("div", { class: "vgHead" },
      el("div", {},
        el("p", { class: "label" }, "語彙の目標"),
        el("h3", { id: "vocabGoalTitle" }, `${dataset().shortLabel}の語彙 ${num(goal.target)}語`),
      ),
      el("p", { class: "vgCount" },
        el("strong", {}, num(value)),
        el("span", {}, ` 語 / ${num(goal.target)}語`)),
    ),
    el("div", { class: "vgBar" }, track,
      el("div", { class: "vgTicks" },
        el("span", { class: "vgTick vgTickStart" }, el("strong", {}, "0")),
        prevTick,
        el("span", { class: "vgTick vgTickEnd" },
          el("strong", {}, num(goal.target)), el("small", {}, dataset().shortLabel)),
      ),
    ),
    el("p", { class: "vgMessage" }, message),
    forecast,
  );
}

function meaningMission(
  summary,
  ready,
  nextQueue = [],
  learnedItems = [],
  meaningResume = null,
  coreResume = false,
  hasPrimaryCta = false,
) {
  const learned = summary.learned;
  const due = summary.due;
  const batch = nextQueue.length || Math.min(due, MEANING_SESSION_SIZE);
  const remaining = Math.max(0, due - batch);
  const mission = el("section", {
    class: "card spacedReviewCard",
    "aria-labelledby": "spacedReviewCardTitle",
  },
    el("p", { class: "label" }, "間隔復習"),
    el("h3", { id: "spacedReviewCardTitle" }, `意味だけ復習（${dataset().shortLabel}）`),
    el("p", { class: "meaningMissionLead" },
      `${datasetSectionName()}の収録セットをまとめ、通常学習で最後まで解いた設問の語句を1回最大${MEANING_SESSION_SIZE}語句で復習します。正解の速さとこれまでの記録から、語句ごとに次回の日を決めます。`),
    // 行動指標は「今すぐ復習」1つに絞る。プール全体の解放数（旧・左指標）は日常判断に使わないため出さない。
    el("div", { class: "meaningMissionMetrics" },
      el("div", { class: ready && due > 0 ? "meaningMissionMetricDue" : "" }, el("strong", {}, ready ? `${due}語句` : "—"), el("span", {}, "今すぐ復習")),
    ),
  );

  if (ready && learned > 0) {
    mission.appendChild(meaningIntervalBreakdown(learnedItems));
  } else if (ready) {
    mission.appendChild(el("p", { class: "hint" }, "まだ意味だけ復習の対象語句がありません。通常学習で本番形式まで解くと対象に加わります。"));
  }
  const otherDue = otherGradeDueCounts();
  if (otherDue.length) {
    const list = el("div", { class: "meaningMissionOtherGradeList" });
    otherDue.forEach((row) => {
      list.appendChild(el("button", {
        class: "ghost meaningMissionOtherGrade",
        type: "button",
        "aria-label": `${row.label}の復習待ち${row.count}語句へ移動`,
        onclick: () => switchDataset(row.datasetId),
      }, el("strong", {}, row.label), el("span", {}, `${row.count}語句`)));
    });
    mission.appendChild(el("div", { class: "meaningMissionOtherGrades" },
      el("p", { class: "label" }, "他の級の復習待ち"),
      list,
    ));
  }
  if (meaningResume) {
    mission.appendChild(el("div", { class: "resumeNotice" },
      el("p", { class: "label" }, "途中保存"),
      el("p", { class: "resumeText" }, resumeDescription(meaningResume)),
      el("p", { class: "hint" }, "意味だけ復習の続きから再開できます。"),
    ));
  }
  // coreResume（通常学習の途中保存）時は、ホーム上部の .startCta と .resumeNotice が再開を案内する。
  // ここで重ねて案内しない。CTA自体は下の hasPrimaryCta 分岐で二次操作（.secondaryCta.meaningMissionCta）へ落とす。

  const buttonAttrs = { class: "cta reviewCta meaningMissionCta", type: "button", disabled: "disabled" };
  let buttonLabel = "対象を確認中…";
  let note = "";
  if (meaningResume && ready) {
    buttonLabel = "意味だけ復習の続きを再開する";
    delete buttonAttrs.disabled;
    buttonAttrs.onclick = async () => { if (!(await restoreSession())) renderHome(); };
  } else if (ready && learned === 0) {
    buttonLabel = "通常学習後に利用できます";
  } else if (ready && due === 0) {
    buttonLabel = "今すぐ復習する語句はありません";
  } else if (ready) {
    buttonLabel = `今日の復習を始める（${batch}語句）`;
    delete buttonAttrs.disabled;
    buttonAttrs.onclick = () => startMeaningPractice(true, nextQueue);
    if (remaining > 0) note = `今すぐ復習する${due}語句のうち、今回は${batch}語句を出題します。残り${remaining}語句は次回に回ります。`;
  }
  // 1画面の塗りCTAは1つ。主CTAがある限り、間隔復習は二次操作に落とす。
  // 主CTAが null（通常学習が終わり、間隔復習が実質の主導線になる分岐）のときだけ塗りのまま残す。
  if (hasPrimaryCta) buttonAttrs.class = "secondaryCta meaningMissionCta";
  mission.appendChild(el("button", buttonAttrs, buttonLabel));
  if (note) mission.appendChild(el("p", { class: "hint" }, note));
  return mission;
}

