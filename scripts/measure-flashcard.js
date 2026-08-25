/*
 * 暗記カードの実測用ブラウザスクリプト。
 *
 * ブラウザの JavaScript 実行環境でこのファイルを評価すると、次の関数を
 * window に公開します。
 *
 *   await window.measureQuestion("第1問")
 *   await window.measureQuestions(["第1問", "第2問"])
 *   window.backupFlashcardMeasurementState()
 *   window.restoreFlashcardMeasurementState()
 *
 * 出力項目の定義は docs/FLASHCARD_MEASUREMENT_PLAN.md に合わせています。
 * このファイルはアプリ本体から読み込まず、測定時だけブラウザで評価します。
 */

(function installFlashcardMeasurement(global) {
  "use strict";

  const DEFAULT_CARD_WAIT_MS = 520;
  const INITIAL_RENDER_WAIT_MS = 350;
  const GUARD_SAMPLE_MS = 100;
  // static/mode-q1.js の FLASH_NAV_GUARD_MS と同値。ガード明けを確実に過ぎてから比較する。
  const FLASH_NAV_GUARD_MS = 450;
  const GUARD_SETTLE_MARGIN_MS = 50;
  const MEASURE_BACKUP_KEY = "__measure_bak__";

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  function visible(element) {
    if (!element) return false;
    const rect = element.getBoundingClientRect();
    return element.offsetHeight > 0 && element.offsetWidth > 0 && rect.width > 0 && rect.height > 0;
  }

  async function waitFor(selector, timeoutMs = 2000) {
    const startedAt = performance.now();
    while (performance.now() - startedAt < timeoutMs) {
      const element = document.querySelector(selector);
      if (visible(element)) return element;
      await sleep(50);
    }
    return null;
  }

  function pixelRect(element) {
    const rect = element.getBoundingClientRect();
    return {
      l: Math.round(rect.left),
      t: Math.round(rect.top + scrollY),
      w: Math.round(rect.width),
      h: Math.round(rect.height),
    };
  }

  function measureText(selector) {
    const element = document.querySelector(selector);
    if (!element) return null;
    const styles = getComputedStyle(element);
    const fontSize = parseFloat(styles.fontSize);
    const width = element.getBoundingClientRect().width;
    return {
      fs: fontSize,
      em: +(width / fontSize).toFixed(1),
      chApprox: Math.round(width / (fontSize * 0.5)),
      maxWidth: styles.maxWidth,
    };
  }

  function gapBetween(firstSelector, secondSelector) {
    const first = document.querySelector(firstSelector);
    const second = document.querySelector(secondSelector);
    return first && second
      ? Math.round(second.getBoundingClientRect().top - first.getBoundingClientRect().bottom)
      : null;
  }

  // ガード中の見た目の変化を、同じ要素の時間差で比べるための署名。
  // class / aria-disabled だけでなく背景色・不透明度も含めるのは、押下フィードバックを
  // :active などの疑似クラスだけで実装した場合にクラス名が変わらないため。
  function buttonStateSignature(button) {
    if (!button) return null;
    const styles = getComputedStyle(button);
    return [
      button.className,
      button.getAttribute("aria-disabled"),
      button.disabled,
      styles.backgroundColor,
      styles.opacity,
    ].join("|");
  }

  function currentNextButton() {
    const nav = document.querySelector(".flashNav");
    return nav ? nextButton(nav) : null;
  }

  // M12: 送り後に見出し語が画面内に収まっているか。
  // カード送りでスクロール位置が持ち越されるため、M1（文書内の位置）だけでは
  // 「新しい語の見出しを見ないまま進む」状態を検出できない。
  function wordInView() {
    const word = document.querySelector(".flashWord");
    if (!word) return null;
    const rect = word.getBoundingClientRect();
    return rect.top >= 0 && rect.bottom <= innerHeight;
  }

  function nextButton(nav) {
    return [...nav.querySelectorAll("button")].find((button) =>
      /次のカード|意味チェックへ進む/.test(button.textContent));
  }

  function visibleSessionButtons() {
    return [...document.querySelectorAll("#sessionPanel button")].filter(visible);
  }

  function backupFlashcardMeasurementState() {
    const keys = Object.keys(localStorage).filter((key) => key.startsWith("eiken_q1_"));
    const backup = Object.fromEntries(keys.map((key) => [key, localStorage.getItem(key)]));
    sessionStorage.setItem(MEASURE_BACKUP_KEY, JSON.stringify(backup));
    return { saved: keys.length };
  }

  function restoreFlashcardMeasurementState() {
    const raw = sessionStorage.getItem(MEASURE_BACKUP_KEY);
    const backup = raw ? JSON.parse(raw) : null;
    if (!backup) return { restored: false, reason: "backup missing" };

    const originalKeys = new Set(Object.keys(backup));
    Object.keys(localStorage)
      .filter((key) => key.startsWith("eiken_q1_") && !originalKeys.has(key))
      .forEach((key) => localStorage.removeItem(key));
    Object.entries(backup).forEach(([key, value]) => localStorage.setItem(key, value));
    sessionStorage.removeItem(MEASURE_BACKUP_KEY);
    return {
      restored: Object.entries(backup).every(([key, value]) => localStorage.getItem(key) === value),
    };
  }

  async function returnToQuestionList() {
    const back = [...document.querySelectorAll("#sessionPanel button")]
      .find((button) => /一覧へ戻る/.test(button.textContent));
    if (!back) return false;
    back.click();
    await sleep(250);
    return true;
  }

  async function measureQuestion(qLabel, options = {}) {
    const cardWaitMs = Number.isFinite(options.cardWaitMs)
      ? Math.max(DEFAULT_CARD_WAIT_MS, options.cardWaitMs)
      : DEFAULT_CARD_WAIT_MS;
    const initialWaitMs = Number.isFinite(options.initialWaitMs)
      ? Math.max(0, options.initialWaitMs)
      : INITIAL_RENDER_WAIT_MS;
    const guardSampleMs = Number.isFinite(options.guardSampleMs)
      ? Math.max(0, options.guardSampleMs)
      : GUARD_SAMPLE_MS;

    if (document.fonts && document.fonts.ready) await document.fonts.ready;
    await returnToQuestionList();

    const card = [...document.querySelectorAll(".qCard")]
      .find((element) => element.textContent.includes(`${qLabel} ・`));
    if (!card) return [{ q: qLabel, err: "not found" }];

    card.click();
    await sleep(initialWaitMs);
    const firstFlash = await waitFor(".flash");
    if (!firstFlash) return [{ q: qLabel, err: "flash card did not render" }];

    const rows = [];
    for (let index = 0; index < 4; index += 1) {
      await sleep(cardWaitMs);
      const flash = document.querySelector(".flash");
      if (!flash) break;

      const nav = document.querySelector(".flashNav");
      if (!nav) {
        rows.push({ q: qLabel, idx: index + 1, err: "flash navigation did not render" });
        break;
      }

      const meaning = document.querySelector(".flashMeaning");
      const word = document.querySelector(".flashWord");
      const meaningStyles = meaning ? getComputedStyle(meaning) : null;
      const wordStyles = word ? getComputedStyle(word) : null;
      const cardHeight = Math.round(flash.getBoundingClientRect().height);
      const buttons = visibleSessionButtons();
      const next = nextButton(nav);

      const row = {
        q: qLabel,
        idx: index + 1,
        vw: innerWidth,
        vh: innerHeight,
        word: word ? word.textContent : null,
        mid: document.querySelector(".originChip")
          ? "語源"
          : (document.querySelector(".coreChain") ? "核心イメージ" : "なし"),
        M1_navBelowFold: Math.round(nav.getBoundingClientRect().top + scrollY) - innerHeight,
        M3_cardH: cardHeight,
        M4_rows: [...flash.querySelectorAll(".flashRow")].map((flashRow) => {
          const height = Math.round(flashRow.getBoundingClientRect().height);
          return {
            label: flashRow.querySelector("strong")
              ? flashRow.querySelector("strong").textContent
              : null,
            h: height,
            pct: +(height / cardHeight * 100).toFixed(1),
          };
        }),
        M5_meaning: meaningStyles
          ? {
              fs: meaningStyles.fontSize,
              fw: meaningStyles.fontWeight,
              vsWord: wordStyles
                ? +(parseFloat(meaningStyles.fontSize) / parseFloat(wordStyles.fontSize)).toFixed(2)
                : null,
            }
          : null,
        M6_measure: {
          meaning: measureText(".flashMeaning"),
          ex: measureText(".flashEx"),
          exTr: measureText(".flashExampleTranslation"),
          panel: measureText(".particlePanel p"),
        },
        M7_space: {
          edge: Math.round(flash.getBoundingClientRect().left),
          labelToContent: (() => {
            const firstRow = flash.querySelector(".flashRow");
            if (!firstRow) return null;
            const label = firstRow.querySelector("strong");
            const content = label && label.nextElementSibling;
            return content
              ? Math.round(content.getBoundingClientRect().top - label.getBoundingClientRect().bottom)
              : null;
          })(),
          rowPadding: (() => {
            const firstRow = flash.querySelector(".flashRow");
            return firstRow ? getComputedStyle(firstRow).padding : null;
          })(),
          cardToNav: gapBetween(".flash", ".flashNav"),
          navToCounter: gapBetween(".flashNav", ".cardCounter"),
        },
        M8_filledCta: buttons.filter((button) =>
          getComputedStyle(button).backgroundColor !== "rgba(0, 0, 0, 0)").length,
        M9_smallTargets: buttons
          .map((button) => ({ button, rect: button.getBoundingClientRect() }))
          .filter(({ rect }) => rect.height < 44 || rect.width < 44)
          .map(({ button, rect }) => ({
            t: button.textContent.trim().slice(0, 14),
            w: Math.round(rect.width),
            h: Math.round(rect.height),
          })),
        M10_overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
        M11_guardFeedback: null,
        M12_wordInViewAfterAdvance: null,
        _px: { flash: pixelRect(flash), nav: pixelRect(nav) },
      };

      rows.push(row);
      if (!next) break;
      // 最終カードは「意味チェックへ進む」で別ステージへ移るため、
      // 送りボタンのガード反応とは比較できない。
      if (/意味チェックへ進む/.test(next.textContent)) {
        row.M11_guardFeedback = null;
        break;
      }

      // 実利用と同じ経路にする。送りボタンまでスクロールせずに押すと、
      // 送り後のスクロール持ち越し（docs/FLASHCARD_MEASUREMENT_PLAN.md 4-4）が
      // 再現せず、M12が常に true になってしまう。
      next.scrollIntoView({ block: "end" });
      await sleep(80);
      next.click();
      await sleep(guardSampleMs);
      const duringGuard = buttonStateSignature(currentNextButton());
      await sleep(Math.max(0, FLASH_NAV_GUARD_MS + GUARD_SETTLE_MARGIN_MS - guardSampleMs));
      const afterGuard = buttonStateSignature(currentNextButton());
      row.M11_guardFeedback = duringGuard !== null && afterGuard !== null && duringGuard !== afterGuard;
      row.M12_wordInViewAfterAdvance = wordInView();
    }

    return rows;
  }

  async function measureQuestions(qLabels, options = {}) {
    const labels = Array.isArray(qLabels) ? qLabels : [];
    const rows = [];
    for (const qLabel of labels) rows.push(...await measureQuestion(qLabel, options));
    return { vw: innerWidth, n: rows.length, rows };
  }

  global.measureQuestion = measureQuestion;
  global.measureQuestions = measureQuestions;
  global.backupFlashcardMeasurementState = backupFlashcardMeasurementState;
  global.restoreFlashcardMeasurementState = restoreFlashcardMeasurementState;
}(typeof window === "undefined" ? globalThis : window));
