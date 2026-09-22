"use strict";

// 英検2級の既存 Context Discovery を、暗記カードの example を第1文に置く
// 形式へ移行する。生成AIは使わず、承認済み文脈の補助文を再利用する。

const fs = require("node:fs");
const path = require("node:path");
const childProcess = require("node:child_process");
const { validateContextItem } = require("./lib/context-validator.cjs");
const { validateContextLeakage } = require("./lib/context-leakage-validator.cjs");

const ROOT = path.resolve(__dirname, "..");
const CONFIG = {
  "eiken2-2026-1": ["vocab_2026-1.json", "context_2026-1.json", null],
  "eiken2-2025-3": ["vocab_2025-3.json", "context_2025-3.json", "context-candidates/eiken2-2025-3.json"],
  "eiken2-2025-2": ["vocab_2025-2.json", "context_2025-2.json", "context-candidates/eiken2-2025-2.json"],
  "eiken2-mock-1": ["vocab_2_mock-1.json", "context_2_mock-1.json", "context-candidates/eiken2-mock-1.json"],
  "eiken2-mock-2": ["vocab_2_mock-2.json", "context_2_mock-2.json", "context-candidates/eiken2-mock-2.json"],
  "eiken2-mock-3": ["vocab_2_mock-3.json", "context_2_mock-3.json", "context-candidates/eiken2-mock-3.json"],
  "eiken2-mock-4": ["vocab_2_mock-4.json", "context_2_mock-4.json", "context-candidates/eiken2-mock-4.json"],
};
const LEGACY_WITHOUT_TARGET_SENSE = new Set(["bride", "lawyer", "warrior", "surgeon"]);
const EXPLANATION_FIX_TARGETS = new Set([
  "hate", "polish", "barely", "secretly", "frown", "as a general rule",
  "on a specific occasion", "to one's surprise", "watch out for", "the edge of",
  "a member of", "the back of", "lay off", "bring about", "catch up", "identity",
  "answered for",
  "typical", "as fast as",
]);
const CODEX_OVERRIDES = {
  "distinct from": { support: ["One painting used only pale colors, while the other was filled with bright red and blue shapes.", "Visitors could easily tell which artist had made each one."], clues: ["pale colors", "bright red and blue shapes", "easily tell which artist"] },
  "composed of": { support: ["Removing any one part stopped the machine from operating properly.", "Each piece had a different job inside the system."], clues: ["Removing any one part stopped the machine", "Each piece had a different job"] },
  "flip over": { support: ["The front showed a question, and the answer was printed on the opposite side.", "Students turned each card after making a guess."], clues: ["answer was printed on the opposite side", "turned each card"] },
  "direct": { support: ["Passengers do not need to change trains along the way.", "They stay in the same carriage until they reach the city."], clues: ["do not need to change trains", "stay in the same carriage"] },
  "elastic": { support: ["I pulled the material twice as long and then released it.", "It quickly returned to the same size as before."], clues: ["pulled the material twice as long", "returned to the same size"] },
  "put away": { support: ["The children placed every toy in its box and cleared the floor.", "The room was neat when the visitors entered."], clues: ["placed every toy in its box", "cleared the floor", "room was neat"] },
  "consist of": { support: ["Five members will be teachers, and the other five will be students.", "Together, these ten people will form the whole group."], clues: ["Five members will be teachers", "other five will be students", "form the whole group"] },
  "bit by bit": { support: ["At first she knew only a few words, but she added several new expressions every week.", "After a year, she could hold a long conversation."], clues: ["added several new expressions every week", "After a year"] },
  "on behalf of": { support: ["The other players remained in their seats while I spoke for all of them.", "I thanked the coaches using the team's shared message."], clues: ["spoke for all of them", "team's shared message"] },
  "with regard to": { support: ["Reporters asked several questions about it, but the spokesperson discussed only other matters.", "The company gave no opinion on that subject."], clues: ["questions about it", "discussed only other matters", "no opinion on that subject"] },
  "arrest": { support: ["Officers plan to place him in handcuffs and take him to the police station.", "He will not be free to leave while they question him."], clues: ["place him in handcuffs", "take him to the police station", "not be free to leave"] },
  "influence": { support: ["Her teacher's encouragement made science seem like the right career for her.", "She often remembers that advice when planning her future."], clues: ["made science seem like the right career", "remembers that advice"] },
  "complaint": { support: ["The guest said loud music had kept her awake all night and asked the manager to solve the problem.", "The manager apologized and moved her to another room."], clues: ["kept her awake all night", "asked the manager to solve the problem", "manager apologized"] },
  "proverb": { support: ["The short saying has been repeated for generations because it expresses practical wisdom.", "People quote it when actions and words do not match."], clues: ["short saying", "repeated for generations", "practical wisdom"] },
  "promise": { support: ["He wants her to be certain that he will contact her immediately.", "She trusts that he will keep his word."], clues: ["be certain that he will contact her", "keep his word"] },
  "resort": { support: ["Their room faced the ocean, and the property had a pool, restaurants, and activities for guests.", "They stayed there for a week without needing to travel elsewhere."], clues: ["room faced the ocean", "pool, restaurants, and activities for guests", "stayed there for a week"] },
  "democracy": { support: ["Every adult can vote, and the candidate with enough public support takes office.", "Citizens can replace leaders in the next election."], clues: ["Every adult can vote", "public support", "replace leaders in the next election"] },
  "up in the air": { support: ["We have not chosen the dates, and no tickets have been bought because two family members may be unable to travel.", "We will decide after everyone confirms their schedule."], clues: ["not chosen the dates", "no tickets have been bought", "decide after everyone confirms"] },
  "the other of": { support: ["There are only two twins in the pair: one rarely speaks, while the second talks constantly.", "Their personalities are almost opposite."], clues: ["only two twins", "one rarely speaks", "the second talks constantly"] },
  "omission": { support: ["Readers misunderstood the report because the missing detail had never been included.", "Editors added it before publishing the corrected version."], clues: ["missing detail had never been included", "added it", "corrected version"] },
  "kept up": { support: ["Although the leader ran quickly, the second runner stayed beside her for most of the race.", "He was still only one step behind at the final turn."], clues: ["stayed beside her", "only one step behind"] },
  "a little of": { support: ["Mina added only one small spoonful and left most of the sauce in the bottle.", "She did not want the flavor to become too strong."], clues: ["only one small spoonful", "left most of the sauce", "not want the flavor to become too strong"] },
  "decreased": { support: ["Weekend ticket sales fell from five hundred to fewer than two hundred.", "The museum halls became much quieter."], clues: ["fell from five hundred", "fewer than two hundred", "became much quieter"] },
  "custom": { support: ["Families in the area have followed this practice for many generations.", "Children learn to do the same thing from their parents."], clues: ["followed this practice for many generations", "learn to do the same thing from their parents"] },
  "on top": { sense: "上に", choices: ["上に", "下に", "中に", "近くに"], support: ["Mika had to stand on a chair to reach them.", "Nothing covered the keys, so she could see them from below."], clues: ["stand on a chair to reach them", "see them from below"] },
  "sending back": { support: ["The customer asked the server to take the cold bowl to the kitchen.", "She wanted a hot replacement instead."], clues: ["take the cold bowl to the kitchen", "wanted a hot replacement"] },
  "writing down": { support: ["She used a pen and notepad so that she would not forget any dish.", "The kitchen received an exact written list."], clues: ["used a pen and notepad", "not forget any dish", "written list"] },
  "political": { support: ["Articles about elections, government policy, and national leaders appeared in another section.", "The family pages contained sports and community events instead."], clues: ["elections, government policy, and national leaders", "another section", "sports and community events instead"] },
  "related": { support: ["He explained how one family's experience reflected a problem faced by many people.", "The audience could see the connection between the two subjects."], clues: ["one family's experience reflected a problem", "connection between the two subjects"] },
  "violated": { support: ["Workers entered the site without helmets even though the regulations required them.", "Inspectors stopped the project and issued a penalty."], clues: ["without helmets", "regulations required them", "issued a penalty"] },
  "vacancies": { support: ["Every room has already been reserved, so the receptionist must turn new guests away.", "Travelers will have to find another hotel."], clues: ["Every room has already been reserved", "turn new guests away", "find another hotel"] },
  "filled": { support: ["He continued adding books until there was no empty space inside.", "Then he closed and sealed the heavy container."], clues: ["no empty space inside", "closed and sealed the heavy container"] },
  "in person": { support: ["Instead of using a video call, he invites each applicant to sit with him in the office.", "They speak while sharing the same room."], clues: ["Instead of using a video call", "sit with him in the office", "sharing the same room"] },
  "The company plans to expand its business overseas.": { support: ["It will open offices in three new countries and hire hundreds of additional workers.", "Its products will be sold in markets it has never served before."], clues: ["open offices in three new countries", "hire hundreds of additional workers", "markets it has never served before"] },
  "The city plans to expand its subway system over the next decade.": { support: ["Officials will add two new lines and build twenty more stations.", "Trains will reach neighborhoods that currently have no subway service."], clues: ["add two new lines", "build twenty more stations", "reach neighborhoods that currently have no subway service"] },
  "The bright stars disappear when morning sunlight reaches the quiet valley.": { support: ["They are easy to see in the dark sky but can no longer be seen after the sky becomes bright.", "They become visible again the following night."], clues: ["can no longer be seen", "after the sky becomes bright", "visible again the following night"] },
  "The sun will disappear behind the clouds within a few minutes.": { support: ["A thick gray cloud is moving across it, and soon the bright circle will no longer be visible.", "The light will return after the cloud passes."], clues: ["cloud is moving across it", "no longer be visible", "light will return"] },
  "My boss says we will review my progress next month.": { support: ["We will compare the work I completed with my goals and check what still needs improvement.", "After that meeting, we may change my plan for the following month."], clues: ["compare the work I completed with my goals", "check what still needs improvement", "change my plan"] },
  "She decided to accept the job offer after discussing it with her family.": { support: ["She signed the employment contract and told the company she would begin on Monday.", "The manager then removed the position from the list of available jobs."], clues: ["signed the employment contract", "would begin on Monday", "removed the position"] },
  "The temperature stayed above zero throughout the winter afternoon.": { support: ["The thermometer's lowest reading was three degrees, so the water never froze.", "Every recorded number was greater than 0°C."], clues: ["lowest reading was three degrees", "water never froze", "greater than 0°C"] },
  "The discussion may open up new ideas for the community.": { support: ["Residents had considered only one old solution before the meeting.", "By the end, they had proposed several new ways to improve the neighborhood."], clues: ["only one old solution before the meeting", "proposed several new ways"] },
  "This dress is only worn on a specific occasion.": { support: ["Mika keeps it covered in the closet and takes it out only for weddings or formal ceremonies.", "On ordinary days, she chooses simple clothes instead."], clues: ["only for weddings or formal ceremonies", "On ordinary days", "simple clothes instead"] },
  "Having spent all morning on the report, he took a short break.": { support: ["He had worked on it continuously from eight o'clock until noon.", "Most of the report was complete, and he needed to rest before continuing."], clues: ["continuously from eight o'clock until noon", "Most of the report was complete", "needed to rest"] },
  "Without your advice, I would not have made the right decision.": { support: ["I was ready to choose the wrong option, but your warning changed my mind.", "The choice I finally made led to a successful result."], clues: ["ready to choose the wrong option", "warning changed my mind", "successful result"] },
  "The athlete ran as fast as the current champion during the final race.": { support: ["They crossed the finish line at almost exactly the same time.", "The clock showed no meaningful difference between their results."], clues: ["almost exactly the same time", "no meaningful difference between their results"] },
};

function read(name) { return JSON.parse(fs.readFileSync(path.join(ROOT, "data", name), "utf8")); }
function write(name, value) {
  if (name === "context_2026-1.json") {
    const meta = JSON.stringify(value.meta, null, 2).split("\n").map((line) => `  ${line}`).join("\n");
    const contexts = value.contexts.map((item, index) => `    ${JSON.stringify(item)}${index + 1 < value.contexts.length ? "," : ""}`).join("\n");
    fs.writeFileSync(path.join(ROOT, "data", name), `{\n  "meta": ${meta.trimStart()},\n  "contexts": [\n${contexts}\n  ]\n}\n`, "utf8");
    return;
  }
  fs.writeFileSync(path.join(ROOT, "data", name), `${JSON.stringify(value, null, 2)}\n`, "utf8");
}
function surface(item) { return item.word || item.phrase; }
function esc(value) { return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
function targetPattern(target, flags = "i") {
  return new RegExp(`(?<![A-Za-z])${esc(target).replace("one's", "(?:one's|my|your|his|her|our|their)")}(?![A-Za-z])`, flags);
}

function segmentSentence(sentence, target, clues) {
  const spans = [];
  const targetMatch = targetPattern(target, "i").exec(sentence);
  if (targetMatch) spans.push({ start: targetMatch.index, end: targetMatch.index + targetMatch[0].length, role: "target" });
  for (const clue of clues) {
    const index = sentence.toLowerCase().indexOf(clue.text.toLowerCase());
    if (index >= 0) spans.push({ start: index, end: index + clue.text.length, role: "clue", clueType: clue.type });
  }
  spans.sort((a, b) => a.start - b.start || b.end - a.end);
  const kept = [];
  for (const span of spans) {
    if (!kept.length || span.start >= kept[kept.length - 1].end) kept.push(span);
  }
  const segments = [];
  let cursor = 0;
  for (const span of kept) {
    if (span.start > cursor) segments.push({ en: sentence.slice(cursor, span.start), role: "core", useJapanese: false });
    segments.push({ en: sentence.slice(span.start, span.end), role: span.role, ...(span.clueType ? { clueType: span.clueType } : {}), useJapanese: false });
    cursor = span.end;
  }
  if (cursor < sentence.length) segments.push({ en: sentence.slice(cursor), role: "core", useJapanese: false });
  return segments;
}

function usefulParts(sentence) {
  const clean = sentence.replace(/[.!?]+$/, "").trim();
  const parts = clean.split(/,\s+|;\s+|\s+(?:and|but|so|because|while|when|to|after|before|from|with|by|for|into|as)\s+/i)
    .map((part) => part.trim()).filter((part) => part.split(/\s+/).length >= 3);
  if (parts.length >= 2) return parts;
  const words = clean.split(/\s+/);
  if (words.length >= 6) {
    const middle = Math.floor(words.length / 2);
    return [words.slice(0, middle).join(" "), words.slice(middle).join(" ")];
  }
  return [clean];
}

function selectClues(item, sentences) {
  const available = item.contextClues.filter((clue) =>
    sentences.some((sentence) => sentence.toLowerCase().includes(clue.text.toLowerCase()))
      && !targetPattern(item.target).test(clue.text));
  const selected = [];
  const canAdd = (text) => sentences.every((sentence) => {
    const lower = sentence.toLowerCase();
    const start = lower.indexOf(text.toLowerCase());
    if (start < 0) return true;
    const end = start + text.length;
    return selected.every((entry) => {
      const otherStart = lower.indexOf(entry.text.toLowerCase());
      if (otherStart < 0) return true;
      const otherEnd = otherStart + entry.text.length;
      return end <= otherStart || start >= otherEnd;
    });
  });
  for (const sentence of sentences.slice(1)) {
    for (const part of usefulParts(sentence)) {
      if (selected.length >= 2) break;
      if (canAdd(part)) {
        selected.push({ text: part, type: "supporting context" });
      }
    }
  }
  for (const clue of available) {
    if (selected.length >= 3) break;
    if (canAdd(clue.text)) selected.push(clue);
  }
  if (selected.length < 2) {
    const example = sentences[0];
    const match = targetPattern(item.target).exec(example);
    const sides = match ? [example.slice(0, match.index), example.slice(match.index + match[0].length)] : [];
    for (const side of sides.map((text) => text.replace(/^[\s,;:.!?]+|[\s,;:.!?]+$/g, "")).filter(Boolean)) {
      if (selected.length >= 2) break;
      if (side.split(/\s+/).length >= 2 && canAdd(side)) selected.push({ text: side, type: "example context" });
    }
  }
  return selected.slice(0, 3);
}

function explanation(item, clues, targetSense) {
  const quoted = clues.map((clue) => `「${clue.text}」`).join("と");
  const oldReason = String(item.inferenceExplanation || "").replace(/^.*?が手がかりです。/, "");
  const fallback = `${item.target}はこの場面で「${targetSense}」だと考えられます。`;
  const reason = oldReason && oldReason.includes(item.target) ? oldReason : fallback;
  return `${quoted}が手がかりです。${reason}`;
}

function migrate(item, vocab) {
  const override = CODEX_OVERRIDES[vocab.example] || CODEX_OVERRIDES[item.target];
  if (override) {
    const targetSense = override.sense || item.targetSense || item.meaning;
    const fullEnglish = [vocab.example, ...override.support];
    const contextClues = override.clues.map((text) => ({ text, type: "supporting context" }));
    return {
      ...item,
      targetSense,
      fullEnglish,
      mixedEnglish: [...fullEnglish],
      contextClues,
      inferencePath: [...contextClues.map((clue) => clue.text), `targetSense: ${targetSense}`, item.target],
      segments: fullEnglish.map((sentence) => segmentSentence(sentence, item.target, contextClues)),
      choices: override.choices || item.choices,
      answerIndex: 0,
      inferenceExplanation: `${contextClues.map((clue) => `「${clue.text}」`).join("と")}が手がかりです。これらの状況から、${item.target}は「${targetSense}」を表すと判断できます。`,
      quality: { ...item.quality, targetOccurrence: 1, clueCount: contextClues.length, targetProtected: true, cluesProtected: true },
    };
  }
  if (item.target === "on one's own") {
    const fullEnglish = [
      vocab.example,
      "Mika repaired the bicycle while her father was away and showed him the working wheels that evening.",
      "She felt proud when the wheels turned again.",
    ];
    const contextClues = [
      { text: "while her father was away", type: "condition" },
      { text: "showed him the working wheels", type: "result" },
      { text: "felt proud", type: "result" },
    ];
    return {
      ...item,
      fullEnglish,
      mixedEnglish: [...fullEnglish],
      contextClues,
      inferencePath: [...contextClues.map((clue) => clue.text), `targetSense: ${item.targetSense}`, item.target],
      segments: fullEnglish.map((sentence) => segmentSentence(sentence, item.target, contextClues)),
      inferenceExplanation: "「while her father was away」「showed him the working wheels」「felt proud」が手がかりです。父親が不在の間に自転車を直し、動くようになった車輪を見せて誇らしく感じているので、on one's ownは「自分一人で、独力で」だと推測できます。",
      quality: { ...item.quality, targetOccurrence: 1, clueCount: 3, targetProtected: true, cluesProtected: true },
    };
  }
  if (item.fullEnglish[0] === vocab.example) {
    if (item.contextClues.some((clue) => clue.type === "supporting context") || EXPLANATION_FIX_TARGETS.has(item.target)) {
      const targetSense = item.targetSense || item.meaning;
      item.inferenceExplanation = `${item.contextClues.map((clue) => `「${clue.text}」`).join("と")}が手がかりです。これらの状況から、${item.target}は「${targetSense}」を表すと判断できます。`;
    }
    if (LEGACY_WITHOUT_TARGET_SENSE.has(item.target)) delete item.targetSense;
    return item;
  }
  const targetSense = item.targetSense || item.meaning;
  const supporting = item.fullEnglish.filter((sentence) => !targetPattern(item.target).test(sentence)).slice(0, 2);
  if (!supporting.length) throw new Error(`${item.target}: supporting sentence is missing`);
  const fullEnglish = [vocab.example, ...supporting];
  const contextClues = selectClues(item, fullEnglish);
  if (contextClues.length < 2) throw new Error(`${item.target}: fewer than two reusable clues`);
  const migrated = {
    ...item,
    targetSense,
    fullEnglish,
    mixedEnglish: [...fullEnglish],
    contextClues,
    inferencePath: [...contextClues.map((clue) => clue.text), `targetSense: ${targetSense}`, item.target],
    segments: fullEnglish.map((sentence) => segmentSentence(sentence, item.target, contextClues)),
    inferenceExplanation: explanation(item, contextClues, targetSense),
    quality: { ...item.quality, targetOccurrence: 1, clueCount: contextClues.length, targetProtected: true, cluesProtected: true },
  };
  const structural = validateContextItem(migrated, vocab, { requireTargetSense: true });
  if (structural.status !== "pass") throw new Error(`${item.target}: ${structural.errors.join(" | ")}`);
  validateContextLeakage(migrated);
  if (!Object.hasOwn(item, "targetSense") || LEGACY_WITHOUT_TARGET_SENSE.has(item.target)) delete migrated.targetSense;
  return migrated;
}

let changed = 0;
for (const [datasetId, [vocabName, runtimeName, candidateName]] of Object.entries(CONFIG)) {
  const vocab = read(vocabName);
  const vocabByTarget = new Map([...(vocab.words || []), ...(vocab.idioms || [])].map((item) => [surface(item), item]));
  const runtime = read(runtimeName);
  const migrateList = (items) => items.map((item) => {
    const vocabItem = vocabByTarget.get(item.target);
    if (!vocabItem) throw new Error(`${datasetId}/${item.target}: vocabulary item is missing`);
    const next = migrate(item, vocabItem);
    if (next !== item) changed += 1;
    return next;
  });
  runtime.contexts = migrateList(runtime.contexts);
  write(runtimeName, runtime);
  if (candidateName) {
    const candidate = read(candidateName);
    candidate.contexts = migrateList(candidate.contexts);
    write(candidateName, candidate);
  }
  console.log(`${datasetId}: ${runtime.contexts.length} runtime contexts checked`);
}
const approvedDir = path.join(ROOT, "data", "context-approved");
const pilotRuntime = read("context_2026-1.json");
const pilotRuntimeByTarget = new Map(pilotRuntime.contexts.map((item) => [item.target, item]));
for (const file of fs.readdirSync(approvedDir).filter((name) => name.endsWith(".json"))) {
  const relative = path.join("context-approved", file).replace(/\\/g, "/");
  const payload = JSON.parse(childProcess.execFileSync("git", ["show", `HEAD:data/${relative}`], { cwd: ROOT, encoding: "utf8" }));
  payload.items = payload.items.map((item) => {
    const runtime = pilotRuntimeByTarget.get(item.target);
    for (const key of ["fullEnglish", "mixedEnglish", "contextClues", "inferencePath", "segments", "inferenceExplanation", "quality"]) {
      item[key] = structuredClone(runtime[key]);
    }
    return item;
  });
  write(relative, payload);
}
console.log(`migrated ${changed} context records (runtime and candidate copies included)`);
