// Cloudflare Workers 版だけで動く Worker。/api/* だけをここで処理し、それ以外は静的アセット（_site）をそのまま返す。
// GitHub Pages / Netlify 版にはこの Worker が無いため、/api を使う機能は Cloudflare 版限定になる。
// Jev の API キーは Worker の Secret `TYPESAFE_API_KEY`（ダッシュボードの Variables & Secrets）に置く。
import {
  JEV_URL, buildJevRequest, findAnswerKey, parseJevResponse, validateGradeRequest, vocabPathFor,
} from "./grade-meaning.mjs";

const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status,
  headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
});

async function assetJson(env, request, path) {
  const response = await env.ASSETS.fetch(new Request(new URL(path, request.url)));
  if (!response.ok) return null;
  try {
    return await response.json();
  } catch {
    return null;
  }
}

async function gradeMeaning(request, env) {
  if (request.method !== "POST") return json({ error: "method not allowed" }, 405);
  if (!env.TYPESAFE_API_KEY) return json({ error: "grading unavailable" }, 503);

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "invalid json" }, 400);
  }
  const input = validateGradeRequest(body);
  if (!input.ok) return json({ error: input.error }, 400);

  const manifest = await assetJson(env, request, "/data/manifest.json");
  const vocabPath = vocabPathFor(manifest, input.datasetId);
  if (!vocabPath) return json({ error: "unknown dataset" }, 404);
  const vocab = await assetJson(env, request, vocabPath);
  if (!vocab) return json({ error: "unknown dataset" }, 404);
  const lemmas = input.type === "word" ? await assetJson(env, request, "/data/lemmas.json") : null;
  const key = findAnswerKey(vocab, lemmas, input.type, input.surface);
  if (!key) return json({ error: "unknown item" }, 404);

  let jevResponse;
  try {
    jevResponse = await fetch(JEV_URL, {
      method: "POST",
      headers: { authorization: `Bearer ${env.TYPESAFE_API_KEY}`, "content-type": "application/json" },
      body: JSON.stringify(buildJevRequest(key, input.answer)),
      signal: AbortSignal.timeout(8000),
    });
  } catch {
    return json({ error: "grader unreachable" }, 502);
  }
  if (!jevResponse.ok) {
    console.log("jev error", jevResponse.status, (await jevResponse.text()).slice(0, 300));
    return json({ error: "grader error" }, 502);
  }
  const result = parseJevResponse(await jevResponse.json());
  if (!result) return json({ error: "unexpected grader response" }, 502);
  return json(result);
}

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);
    if (pathname === "/api/grade-meaning") return gradeMeaning(request, env);
    if (pathname.startsWith("/api/")) return json({ error: "not found" }, 404);
    return env.ASSETS.fetch(request);
  },
};
