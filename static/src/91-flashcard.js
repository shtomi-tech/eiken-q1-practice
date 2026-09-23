/* ---- STEP 1: flashcards ---- */
function buildFlashCard(item) {
  const card = el("div", { class: "flash" });
  const head = el("div", { class: "flashHead" });
  const surface = surfaceOf(item);
  const surfaceKey = String(surface || "").toLowerCase();
  const displayLemma = flashcardDisplayLemmaMap[surfaceKey]
    || (item.type === "word" ? flashcardLemmaMap[surfaceKey] : "");
  const headword = displayLemma || canonicalHeadwordOf(item);
  const learning = learningEntryOf(item);
  const wordLine = el("div", { class: "flashWordLine" },
    // tabindex=-1: カード置換後に focusSessionContext() がここへフォーカスを移す（F-03）。語句テキストは変更しない。
    el("div", { class: "flashWord", tabindex: "-1" }, headword),
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

  const contextReflection = flashContextReflection(item);
  if (contextReflection) card.appendChild(contextReflection);

  const inner = el("div", { class: "flashBody" });
  inner.appendChild(flashRow("意味", learning.meaning || item.meaning, "flashMeaning"));
  if (item.coreImage) {
    inner.appendChild(flashCoreImage(item));
  } else if (item.type === "word") {
    const wordOrigin = flashWordOrigin(item);
    if (wordOrigin) inner.appendChild(wordOrigin);
  }
  if (item.example) inner.appendChild(flashExampleRow(item));
  card.appendChild(inner);
  return card;
}

function flashContextReflection(item) {
  if (!session || session.mode !== "learn") return null;
  const result = session.contextResults?.[itemKeyOf(item)];
  if (!result) return null;
  const reflection = el("div", { class: "flashContextReflection", role: "status" },
    el("p", { class: "flashContextReflectionLabel" }, "文脈からの推測"),
    el("p", { class: "flashContextReflectionGuess" },
      "あなたの推測：",
      el("strong", {}, result.pickedMeaning),
      result.correct ? " ✓" : "",
    ),
  );
  if (!result.correct) {
    reflection.appendChild(el("p", { class: "flashContextReflectionAnswer" },
      "正しい意味：",
      el("strong", {}, result.correctMeaning),
    ));
  }
  return reflection;
}

function scrollFlashCardIntoView() {
  const flash = $("#sessionPanel .flash");
  if (!flash) return;
  const target = flash.getBoundingClientRect().top + window.scrollY - 8;
  window.scrollTo({ top: Math.max(0, target), left: 0, behavior: "auto" });
}

// 暗記カードのスワイプは、既存の前へ／次へボタンを補助する操作。
// 現在の表示位置と指の速度から始めることで、途中でつかみ直しても動きが飛ばないようにする。
function flashTranslateX(card) {
  const transform = getComputedStyle(card).transform;
  if (!transform || transform === "none") return 0;
  const matrix3d = transform.match(/^matrix3d\(([^)]+)\)$/);
  if (matrix3d) return Number(matrix3d[1].split(",")[12]) || 0;
  const matrix = transform.match(/^matrix\(([^)]+)\)$/);
  return matrix ? Number(matrix[1].split(",")[4]) || 0 : 0;
}

function setFlashGestureTransform(card, x) {
  const rotation = Math.max(-4, Math.min(4, x * 0.025));
  const opacity = Math.max(0.86, 1 - Math.abs(x) / 1400);
  card.style.transform = `translate3d(${x.toFixed(2)}px, 0, 0) rotate(${rotation.toFixed(2)}deg)`;
  card.style.opacity = opacity.toFixed(3);
}

function clearFlashGesture(card) {
  card.classList.remove("gestureActive");
  card.style.transform = "";
  card.style.opacity = "";
  card.style.willChange = "";
}

function stopFlashSpring(card) {
  if (!card._flashGestureRaf) return;
  cancelAnimationFrame(card._flashGestureRaf);
  card._flashGestureRaf = 0;
}

function animateFlashGesture(card, target, initialVelocity = 0, onComplete = null) {
  stopFlashSpring(card);
  if (prefersReducedMotion()) {
    clearFlashGesture(card);
    if (onComplete) onComplete();
    return;
  }

  card.classList.add("gestureActive");
  let position = flashTranslateX(card);
  let velocity = Math.max(-3200, Math.min(3200, Number(initialVelocity) || 0));
  let previousTime = performance.now();
  const stiffness = 360;
  const damping = 2 * Math.sqrt(stiffness); // 臨界減衰: 反発は指が勢いを持ったときだけ残す
  const step = (now) => {
    if (!card.isConnected) return;
    const delta = Math.min(0.032, Math.max(0.001, (now - previousTime) / 1000));
    previousTime = now;
    velocity += ((target - position) * stiffness - velocity * damping) * delta;
    position += velocity * delta;
    setFlashGestureTransform(card, position);
    if (Math.abs(target - position) < 0.5 && Math.abs(velocity) < 8) {
      setFlashGestureTransform(card, target);
      card._flashGestureRaf = 0;
      clearFlashGesture(card);
      if (onComplete) onComplete();
      return;
    }
    card._flashGestureRaf = requestAnimationFrame(step);
  };
  card._flashGestureRaf = requestAnimationFrame(step);
}

function flashRubberband(overshoot, dimension, constant = 0.55) {
  return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
}

function setupFlashGesture(card, canGoBack, canGoForward) {
  let pointerId = null;
  let startX = 0;
  let startY = 0;
  let startOffset = 0;
  let horizontal = false;
  let samples = [];

  const releasePointer = () => {
    if (pointerId == null) return;
    if (card.hasPointerCapture(pointerId)) card.releasePointerCapture(pointerId);
    pointerId = null;
  };

  const remember = (x, time) => {
    samples.push({ x, time });
    if (samples.length > 5) samples.shift();
  };

  const releaseVelocity = () => {
    if (samples.length < 2) return 0;
    const first = samples[Math.max(0, samples.length - 3)];
    const last = samples[samples.length - 1];
    const elapsed = Math.max(1, last.time - first.time);
    return ((last.x - first.x) / elapsed) * 1000;
  };

  const cancelTracking = () => {
    horizontal = false;
    samples = [];
    releasePointer();
  };

  const finish = (event, cancelled = false) => {
    if (pointerId !== event.pointerId) return;
    const position = flashTranslateX(card);
    remember(position, performance.now());
    const velocity = releaseVelocity();
    const canCommit = !cancelled && horizontal
      && (Math.abs(position) >= 56 || Math.abs(velocity) >= 480)
      && ((position < 0 && canGoForward) || (position > 0 && canGoBack));
    const direction = position < 0 ? 1 : -1;
    horizontal = false;
    releasePointer();
    card.classList.remove("gestureActive");

    if (!canCommit) {
      animateFlashGesture(card, 0, velocity);
      return;
    }

    armFlashNavGuard();
    const exitTarget = direction > 0
      ? -Math.max(window.innerWidth * 0.88, 280)
      : Math.max(window.innerWidth * 0.88, 280);
    animateFlashGesture(card, exitTarget, velocity, () => {
      if (!card.isConnected) return;
      if (direction > 0) {
        if (session.mode === "learn") {
          if (session.learnIdx === session.items.length - 1) {
            session.stage = "check";
            session.learnPhase = null;
          } else {
            setLearnItem(session.learnIdx + 1);
          }
        } else if (session.flashIdx === session.items.length - 1) session.stage = "check";
        else session.flashIdx++;
      } else {
        if (session.mode === "learn") setLearnItem(Math.max(0, session.learnIdx - 1), "flash");
        else session.flashIdx = Math.max(0, session.flashIdx - 1);
      }
      renderSession();
      scrollFlashCardIntoView();
    });
  };

  card.addEventListener("pointerdown", (event) => {
    if (pointerId != null || (event.pointerType === "mouse" && event.button !== 0) || flashNavLocked()) return;
    const target = event.target instanceof Element ? event.target : null;
    if (target?.closest("button, a, input, select, textarea")) return;
    stopFlashSpring(card);
    pointerId = event.pointerId;
    startX = event.clientX;
    startY = event.clientY;
    startOffset = flashTranslateX(card);
    horizontal = false;
    samples = [];
    remember(startOffset, performance.now());
    card.setPointerCapture(pointerId);
  });

  card.addEventListener("pointermove", (event) => {
    if (pointerId !== event.pointerId) return;
    const rawX = startOffset + event.clientX - startX;
    const rawY = event.clientY - startY;
    if (!horizontal) {
      if (Math.abs(rawX) < 10 && Math.abs(rawY) < 10) return;
      if (Math.abs(rawY) > Math.abs(rawX)) {
        cancelTracking();
        return;
      }
      horizontal = true;
      card.classList.add("gestureActive");
    }
    event.preventDefault();
    const limit = Math.max(72, card.getBoundingClientRect().width * 0.28);
    let position = rawX;
    if ((rawX < 0 && !canGoForward) || (rawX > 0 && !canGoBack)) {
      const edge = rawX < 0 ? -limit : limit;
      position = edge + flashRubberband(rawX - edge, limit);
    }
    setFlashGestureTransform(card, position);
    remember(position, performance.now());
  });

  card.addEventListener("pointerup", (event) => finish(event));
  card.addEventListener("pointercancel", (event) => finish(event, true));
}

function originKindLabel(kind) {
  return { prefix: "接頭辞", root: "語根", suffix: "接尾辞" }[kind] || "構成要素";
}

function flashWordOrigin(item) {
  const origin = wordOriginFor(item);
  if (!origin) return null;
  const row = el("div", { class: "flashRow wordOriginRow" });
  row.appendChild(el("strong", {}, "語源・なりたち"));

  if (origin.type === "A" && Array.isArray(origin.parts) && origin.parts.length) {
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

  if (origin.type === "A" && origin.derivation) {
    row.appendChild(el("p", { class: "originDerivation" }, origin.derivation));
  }

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
    if (origin.derivation) row.appendChild(el("p", { class: "originDerivation" }, origin.derivation));
    return origin.derivation ? row : null;
  }
  if (origin.type !== "A") return row;
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
  const isLearn = session.mode === "learn";
  const index = isLearn ? session.learnIdx : session.flashIdx;
  const item = items[index];

  const flash = buildFlashCard(item);
  // 最後のカードから左へ送る操作は「意味チェックへ進む」に対応する。
  setupFlashGesture(flash, index > 0, true);
  body.appendChild(flash);

  const nav = el("div", { class: "actions flashNav" });
  const guardActive = flashNavLocked();
  const guardedAttrs = (attrs) => guardActive
    ? {
        ...attrs,
        class: `${attrs.class || ""} isGuarded`.trim(),
        "aria-disabled": "true",
      }
    : attrs;
  const canGoBack = index > 0;
  const prevAttrs = guardedAttrs(canGoBack ? { class: "ghost" } : { class: "ghost", disabled: "disabled" });
  prevAttrs.onclick = () => {
    if (!canGoBack || flashNavLocked()) return;
    armFlashNavGuard();
    if (isLearn) setLearnItem(index - 1, "flash");
    else session.flashIdx--;
    renderSession();
    scrollFlashCardIntoView();
  };
  const previousButton = el("button", prevAttrs, "← 前のカード");
  nav.appendChild(previousButton);
  const last = index === items.length - 1;
  const nextButton = el("button", guardedAttrs({
    class: "cta",
    onclick: () => {
      if (flashNavLocked()) return;
      armFlashNavGuard();
      if (last) {
        if (session.mode === "contextLearn") {
          session = null;
          renderHome();
          return;
        }
        if (isLearn) {
          advanceLearnFromFlash();
          return;
        }
        session.stage = "check";
        renderSession();
      } else if (isLearn) {
        advanceLearnFromFlash();
        return;
      } else { session.flashIdx++; renderSession(); }
      scrollFlashCardIntoView();
    },
  }), last ? "意味チェックへ進む →" : "次の語句へ →");
  nav.appendChild(el("span", { class: "flashNavCounter", "aria-live": "polite" },
    `カード ${index + 1} / ${items.length}`));
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

// 例文中の出題形の位置を返す。見つからなければ null。
function exampleMatch(item) {
  if (!item) return null;
  const surface = String(surfaceOf(item) || "");
  const example = String(item.example || "");
  if (!surface || !example) return null;
  const escaped = surface.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  // 単語境界で区切る。境界を見ないと "When" の中の "he"、"president" の中の "preside" を拾う。
  const match = new RegExp(`(?<![A-Za-z])${escaped}(?![A-Za-z])`, "i").exec(example);
  if (!match) return null;
  return {
    before: example.slice(0, match.index),
    hit: match[0],
    after: example.slice(match.index + match[0].length),
  };
}

// 例文ノードを組み立て、対象語句だけを下線で示す。
function buildExampleText(item, match) {
  const fragment = document.createDocumentFragment();
  if (!match) {
    if (item?.example) fragment.appendChild(document.createTextNode(String(item.example)));
    return fragment;
  }
  fragment.appendChild(document.createTextNode(match.before));
  fragment.appendChild(el("span", { class: "exUnderline" }, match.hit));
  fragment.appendChild(document.createTextNode(match.after));
  return fragment;
}

function flashExampleRow(item) {
  const row = el("div", { class: "flashRow" });
  row.appendChild(el("strong", {}, "例文"));
  const match = exampleMatch(item);
  const p = el("div", { class: "flashEx" });
  p.appendChild(buildExampleText(item, match));
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

