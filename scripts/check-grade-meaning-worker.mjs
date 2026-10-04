// 「例文を見て意味を書く」の採点 Worker（worker/grade-meaning.mjs・worker/index.mjs）を、Jev を呼ばずに検証する。
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  buildJevRequest, findAnswerKey, JEV_MODEL, MAX_ANSWER_LENGTH, parseJevResponse, validateGradeRequest, vocabPathFor,
} from "../worker/grade-meaning.mjs";
import worker from "../worker/index.mjs";

const readJson = (rel) => JSON.parse(readFileSync(new URL(`../${rel}`, import.meta.url), "utf8"));
const manifest = readJson("data/manifest.json");
const lemmas = readJson("data/lemmas.json");

// manifest の全セットを Worker が引けること（新しい回を足しても採点できる）
for (const datasetId of Object.keys(manifest.q1)) {
  assert.equal(validateGradeRequest({ datasetId, type: "word", surface: "x", answer: "y" }).ok, true, `datasetId を受け付ける: ${datasetId}`);
  assert.ok(vocabPathFor(manifest, datasetId), `vocabUrl を引ける: ${datasetId}`);
}
assert.equal(vocabPathFor(manifest, "eiken1-mock-999"), null);
assert.equal(vocabPathFor({ q1: { x: { vocabUrl: "../secret.json" } } }, "x"), null);

// 入力検査
const ok = { datasetId: "eiken1-mock-1", type: "word", surface: "concussion", answer: " 脳しんとう " };
assert.deepEqual(validateGradeRequest(ok), { ok: true, datasetId: "eiken1-mock-1", type: "word", surface: "concussion", answer: "脳しんとう" });
for (const body of [
  null, {}, { ...ok, datasetId: "../x" }, { ...ok, type: "phrase" }, { ...ok, surface: "" },
  { ...ok, answer: "  " }, { ...ok, answer: 3 }, { ...ok, answer: "あ".repeat(MAX_ANSWER_LENGTH + 1) },
]) {
  assert.equal(validateGradeRequest(body).ok, false, `拒否する: ${JSON.stringify(body)?.slice(0, 60)}`);
}

// 正解の引き当て: 語彙データと原形辞書から。例文も data から取る
const vocab = readJson(manifest.q1["eiken1-mock-1"].vocabUrl);
const word = vocab.words.find((w) => w.word === "concussion");
const key = findAnswerKey(vocab, lemmas, "word", "concussion");
assert.ok(key.meanings.includes(word.meaning));
assert.equal(key.example, word.example);
assert.equal(findAnswerKey(vocab, lemmas, "word", "no-such-word"), null);
const lemmaSurface = Object.keys(lemmas.lemmas).find((s) => vocab.words.some((w) => w.word === s));
if (lemmaSurface) {
  const lemmaKey = findAnswerKey(vocab, lemmas, "word", lemmaSurface);
  assert.equal(lemmaKey.headword, lemmas.lemmas[lemmaSurface]);
  assert.ok(lemmaKey.meanings.includes(lemmas.entries[lemmas.lemmas[lemmaSurface]].meaning), "原形辞書の意味も正解に入れる");
}
const idiom = vocab.idioms[0];
assert.ok(findAnswerKey(vocab, lemmas, "idiom", idiom.phrase).meanings.includes(idiom.meaning));

// 要求の組み立て: 版を固定し、正解は data から、答えは state の別欄に入れる
const request = buildJevRequest(key, "脳しんとう");
assert.equal(request.model, JEV_MODEL);
assert.notEqual(request.model, "jev-latest");
assert.deepEqual(request.state.item.meanings, key.meanings);
assert.equal(request.state.student_answer, "脳しんとう");
assert.deepEqual(Object.keys(request.questions.grade.criteria), ["correct", "partial", "wrong"]);

// 応答の読み取り
assert.deepEqual(parseJevResponse({ model: "jev-1.13.0", answers: { grade: { type: "choice", choice: "partial", probabilities: { correct: 0.2, partial: 0.7, wrong: 0.1 }, confidence: 0.6 } } }),
  { grade: "partial", confidence: 0.6, probabilities: { correct: 0.2, partial: 0.7, wrong: 0.1 }, model: "jev-1.13.0" });
for (const json of [null, {}, { answers: { grade: { type: "noul", noul: 1 } } }, { answers: { grade: { type: "choice", choice: "easy", confidence: 1 } } }]) {
  assert.equal(parseJevResponse(json), null);
}

// Worker 本体: /api 以外は静的アセットへ、キーが無ければ 503、入力が悪ければ Jev を呼ばずに 400/404
const assets = { fetch: async (req) => {
  const { pathname } = new URL(req.url);
  if (pathname.startsWith("/data/")) {
    try {
      return new Response(readFileSync(new URL(`..${pathname}`, import.meta.url), "utf8"));
    } catch {
      return new Response("not found", { status: 404 });
    }
  }
  return new Response(`asset:${pathname}`);
} };
const post = (body) => new Request("https://example.test/api/grade-meaning", { method: "POST", body: JSON.stringify(body) });
assert.equal(await (await worker.fetch(new Request("https://example.test/index.html"), { ASSETS: assets })).text(), "asset:/index.html");
assert.equal((await worker.fetch(post(ok), { ASSETS: assets })).status, 503);
assert.equal((await worker.fetch(new Request("https://example.test/api/grade-meaning"), { ASSETS: assets, TYPESAFE_API_KEY: "k" })).status, 405);
assert.equal((await worker.fetch(new Request("https://example.test/api/other"), { ASSETS: assets })).status, 404);

const realFetch = globalThis.fetch;
const jevCalls = [];
globalThis.fetch = async (url, init) => {
  jevCalls.push({ url, init });
  return new Response(JSON.stringify({ model: "jev-1.13.0", answers: { grade: { type: "choice", choice: "correct", probabilities: { correct: 0.9, partial: 0.1, wrong: 0 }, confidence: 0.85 } } }));
};
try {
  const env = { ASSETS: assets, TYPESAFE_API_KEY: "test-key" };
  assert.equal((await worker.fetch(post({ ...ok, answer: "" }), env)).status, 400);
  assert.equal((await worker.fetch(post({ ...ok, datasetId: "eiken1-mock-999" }), env)).status, 404);
  assert.equal((await worker.fetch(post({ ...ok, surface: "no-such-word" }), env)).status, 404);
  assert.equal(jevCalls.length, 0, "入力が悪いときは Jev を呼ばない");
  const response = await worker.fetch(post(ok), env);
  assert.equal(response.status, 200);
  assert.equal((await response.json()).grade, "correct");
  assert.equal(jevCalls.length, 1);
  assert.equal(jevCalls[0].init.headers.authorization, "Bearer test-key");
  assert.deepEqual(JSON.parse(jevCalls[0].init.body).state.item.meanings, key.meanings, "正解はサーバ側の data から引く");
} finally {
  globalThis.fetch = realFetch;
}

console.log("grade-meaning worker: OK (入力検査・正解の引き当て・要求・応答・振り分け)");
