/* ---- helpers ---- */
const $ = (sel) => document.querySelector(sel);
function el(tag, attrs = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") n.className = v;
    else if (k === "html") n.innerHTML = v;
    else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v);
  }
  for (const kid of kids) {
    if (kid == null) continue;
    n.appendChild(typeof kid === "string" ? document.createTextNode(kid) : kid);
  }
  return n;
}
function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
function surfaceOf(item) { return item.type === "idiom" ? item.phrase : item.word; }
function canonicalHeadwordOf(item) {
  const surface = surfaceOf(item);
  if (!item || item.type !== "word") return surface;
  return lemmaMap[String(surface || "").toLowerCase()] || surface;
}
function learningEntryOf(item) {
  const headword = canonicalHeadwordOf(item);
  const key = String(headword || "").toLowerCase();
  const entry = lemmaEntries[key];
  if (entry && typeof entry === "object") return entry;
  return {
    meaning: item?.meaning || "",
    ipa: item?.ipa || "",
    pos: item?.pos || "",
    audio: "",
    surfaces: [surfaceOf(item)],
  };
}
function learningMeaningOf(item) { return learningEntryOf(item).meaning || item?.meaning || ""; }
function learningPosOf(item) { return learningEntryOf(item).pos || item?.pos || ""; }
function lemmaAudioPathOf(item, useFlashcardLemma = false) {
  if (useFlashcardLemma) {
    const flashcardLemma = flashcardLemmaOf(item);
    if (flashcardLemma) {
      const entry = lemmaEntries[flashcardLemma];
      return entry?.audio || `assets/audio/lemma/${audioSlug(flashcardLemma)}.mp3`;
    }
  }
  return learningEntryOf(item).audio || vocabularyAudioPath(item);
}
function normalizedSurface(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[’']/g, "'")
    .replace(/\b(one's|his|her|my|your|our|their|its)\b/g, "@poss")
    .replace(/\s+/g, " ")
    .trim();
}
function audioSlug(value) {
  return normalizedSurface(value).replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}
function flashcardLemmaOf(item) {
  if (!item) return "";
  const surface = String(surfaceOf(item) || "").toLowerCase();
  return String(
    flashcardDisplayLemmaMap[surface]
      || (item.type === "word" ? flashcardLemmaMap[surface] : "")
      || "",
  ).trim().toLowerCase();
}
function vocabularyAudioDataset(item) {
  if (!item || (item.type !== "word" && item.type !== "idiom")) return null;
  const match = DATASET_ID_RE.exec((item._datasetId || state.datasetId) || "");
  return match ? { appGrade: match[1], round: match[2] } : null;
}
function vocabularyAudioPath(item) {
  const dataset = vocabularyAudioDataset(item);
  if (!dataset) return "";
  const audioGrade = GRADE_BY_PREFIX[dataset.appGrade];
  if (!audioGrade) return "";
  const slug = audioSlug(surfaceOf(item));
  if (!slug) return "";
  const folder = item.type === "idiom" ? "/idiom" : "";
  return `assets/audio/vocab/${audioGrade}/${dataset.round}${folder}/${slug}.mp3`;
}
function vocabularyAudioEnabled(item) { return Boolean(vocabularyAudioDataset(item)); }
let activeVocabAudio = null;
let activeVocabButton = null;
let activeVocabSpeech = null;
const AUDIO_STATE_LABEL = { idle: "音声", loading: "読込中", playing: "再生中", error: "再生できません" };
function setAudioButtonState(button, stateName) {
  if (!button) return;
  button.dataset.audioState = stateName;
  const label = button.querySelector(".audioLabel");
  if (label) label.textContent = " " + (AUDIO_STATE_LABEL[stateName] || AUDIO_STATE_LABEL.idle);
  const hasBars = Boolean(button.querySelector(".audioBars"));
  if (stateName === "playing" && !hasBars) {
    button.appendChild(el("span", { class: "audioBars", "aria-hidden": "true" },
      el("span", {}), el("span", {}), el("span", {})));
  } else if (stateName !== "playing" && hasBars) {
    button.querySelector(".audioBars").remove();
  }
}
function resetVocabAudioButton(button) {
  if (!button) return;
  button.disabled = false;
  setAudioButtonState(button, "idle");
}
function stopVocabSpeech() {
  if (!activeVocabSpeech) return;
  window.speechSynthesis.cancel();
  resetVocabAudioButton(activeVocabSpeech.button);
  activeVocabSpeech = null;
}
function playVocabSpeech(text, button) {
  if (!window.speechSynthesis || !window.SpeechSynthesisUtterance) {
    button.disabled = false;
    setAudioButtonState(button, "error");
    button.title = "このブラウザでは音声を再生できません。";
    return;
  }
  if (activeVocabAudio) {
    activeVocabAudio.pause();
    activeVocabAudio.currentTime = 0;
    activeVocabAudio = null;
  }
  resetVocabAudioButton(activeVocabButton);
  stopVocabSpeech();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  activeVocabSpeech = { utterance, button };
  button.disabled = true;
  setAudioButtonState(button, "loading");
  const finish = () => {
    resetVocabAudioButton(button);
    if (activeVocabSpeech?.utterance === utterance) activeVocabSpeech = null;
  };
  utterance.addEventListener("start", () => setAudioButtonState(button, "playing"), { once: true });
  utterance.addEventListener("end", finish, { once: true });
  utterance.addEventListener("error", () => {
    button.disabled = false;
    setAudioButtonState(button, "error");
    if (activeVocabSpeech?.utterance === utterance) activeVocabSpeech = null;
  }, { once: true });
  window.speechSynthesis.speak(utterance);
}
function playVocabAudio(path, button, text) {
  if (!path) {
    playVocabSpeech(text, button);
    return;
  }
  stopVocabSpeech();
  if (activeVocabAudio) {
    activeVocabAudio.pause();
    activeVocabAudio.currentTime = 0;
  }
  resetVocabAudioButton(activeVocabButton);
  const audio = new Audio(path);
  activeVocabAudio = audio;
  activeVocabButton = button;
  button.disabled = true;
  setAudioButtonState(button, "loading");
  const finish = () => {
    resetVocabAudioButton(button);
    if (activeVocabAudio === audio) {
      activeVocabAudio = null;
      activeVocabButton = null;
    }
  };
  audio.addEventListener("playing", () => setAudioButtonState(button, "playing"), { once: true });
  audio.addEventListener("ended", finish, { once: true });
  audio.addEventListener("error", () => {
    finish();
    button.title = "MP3を読み込めないため、ブラウザ音声を再生します。";
    playVocabSpeech(text, button);
  }, { once: true });
  audio.play().catch(finish);
}
function buildVocabAudioButton(item, className = "flashListenButton", useFlashcardLemma = false) {
  const surface = useFlashcardLemma ? flashcardLemmaOf(item) || canonicalHeadwordOf(item) : canonicalHeadwordOf(item);
  const audioButton = el("button", {
    class: className,
    type: "button",
    "aria-label": `${surface}の発音を聞く`,
    title: "発音を聞く",
    "data-audio-state": "idle",
  });
  audioButton.appendChild(el("span", { class: "audioIcon", "aria-hidden": "true" }, "▶"));
  audioButton.appendChild(el("span", { class: "audioLabel" }, " 音声"));
  audioButton.addEventListener("click", () => playVocabAudio(lemmaAudioPathOf(item, useFlashcardLemma), audioButton, surface));
  return audioButton;
}
function surfaceVariants(value) {
  const base = normalizedSurface(value);
  const variants = new Set([base]);
  if (base.endsWith("ies") && base.length > 3) variants.add(base.slice(0, -3) + "y");
  if (base.endsWith("ied") && base.length > 3) variants.add(base.slice(0, -3) + "y");
  if (base.endsWith("es") && base.length > 3) variants.add(base.slice(0, -2));
  if (base.endsWith("s") && base.length > 2) variants.add(base.slice(0, -1));
  if (base.endsWith("ed") && base.length > 3) {
    const stem = base.slice(0, -2);
    variants.add(stem);
    if (/(.)\1$/.test(stem)) variants.add(stem.slice(0, -1));
    if (stem.endsWith("i")) variants.add(stem.slice(0, -1) + "y");
    variants.add(stem + "e");
  }
  if (base.endsWith("ing") && base.length > 4) {
    const stem = base.slice(0, -3);
    variants.add(stem);
    if (/(.)\1$/.test(stem)) variants.add(stem.slice(0, -1));
    variants.add(stem + "e");
  }
  return variants;
}
function findItemForSurface(items, value) {
  const target = normalizedSurface(value);
  const exact = items.find((item) => normalizedSurface(surfaceOf(item)) === target);
  if (exact) return exact;
  const targetVariants = surfaceVariants(value);
  return items.find((item) => {
    for (const variant of surfaceVariants(surfaceOf(item))) {
      if (targetVariants.has(variant)) return true;
    }
    return false;
  }) || null;
}
// 回答後、4つの選択肢すべての意味を正解・ユーザー回答のラベル付きで一覧表示する
function practiceChoiceMeanings(q_, items, selectedIdx) {
  const section = el("section", {
    class: "practiceChoiceMeanings",
    "aria-labelledby": "practiceChoiceMeaningsTitle",
  });
  section.appendChild(el("h4", { id: "practiceChoiceMeaningsTitle" }, "4つの選択肢の意味"));

  const list = el("ol", { class: "practiceChoiceMeaningList" });
  q_.choices.forEach((choice, idx) => {
    const item = findItemForSurface(items, choice);
    const isCorrect = idx === q_.answerIndex;
    const isSelected = idx === selectedIdx;
    let stateLabel = "";
    if (isCorrect && isSelected) stateLabel = "✓ 正解・あなたの回答";
    else if (isCorrect) stateLabel = "✓ 正解";
    else if (isSelected) stateLabel = "あなたの回答";

    const head = el("div", { class: "practiceChoiceMeaningHead" },
      el("span", { class: "practiceChoiceMeaningWord" }, choice),
    );
    if (stateLabel) {
      head.appendChild(el("span", { class: "practiceChoiceMeaningState" }, stateLabel));
    }

    list.appendChild(el("li", {
      class: `practiceChoiceMeaningRow${isCorrect ? " isCorrect" : ""}${isSelected && !isCorrect ? " isSelectedWrong" : ""}`,
    },
      head,
      el("p", { class: "practiceChoiceMeaningText" }, item?.meaning || "意味を取得できませんでした"),
    ));
  });

  section.appendChild(list);
  return section;
}
// 選択肢を描画した瞬間の時刻を記録し、直後の誤クリックを無視する
function armChoiceGuard() { session._choicesReadyAt = performance.now() + CHOICE_GUARD_MS; }
function choicesLocked() { return performance.now() < (session._choicesReadyAt || 0); }
function armFlashNavGuard() { session._flashNavReadyAt = performance.now() + FLASH_NAV_GUARD_MS; }
function flashNavLocked() { return performance.now() < (session._flashNavReadyAt || 0); }
