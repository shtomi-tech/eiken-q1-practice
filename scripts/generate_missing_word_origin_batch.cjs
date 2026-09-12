const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const DATA_DIR = path.join(ROOT, "data");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function normalize(value) {
  return String(value || "").trim().toLowerCase();
}

function sourceList(origin) {
  if (Array.isArray(origin.sources)) return origin.sources;
  if (typeof origin.source === "string" && origin.source.trim()) return [origin.source.trim()];
  return [];
}

function inflectionCandidates(word) {
  const candidates = new Set();
  const add = (value) => {
    if (value && value !== word) candidates.add(value);
  };

  if (word.endsWith("ies")) add(`${word.slice(0, -3)}y`);
  if (word.endsWith("ied")) add(`${word.slice(0, -3)}y`);
  if (word.endsWith("ying")) add(`${word.slice(0, -5)}y`);
  if (word.endsWith("ing")) {
    const stem = word.slice(0, -3);
    add(stem);
    add(`${stem}e`);
    if (stem.endsWith("i")) add(`${stem.slice(0, -1)}y`);
  }
  if (word.endsWith("ed")) {
    const stem = word.slice(0, -2);
    add(stem);
    add(`${stem}e`);
    if (/(.)\1$/.test(stem)) {
      const undoubled = stem.slice(0, -1);
      add(undoubled);
      add(`${undoubled}e`);
    }
    if (stem.endsWith("i")) add(`${stem.slice(0, -1)}y`);
  }
  if (word.endsWith("es")) {
    const stem = word.slice(0, -2);
    add(stem);
    add(`${stem}e`);
  }
  if (word.endsWith("s")) add(word.slice(0, -1));
  if (word.endsWith("ly")) {
    const stem = word.slice(0, -2);
    add(stem);
    if (stem.endsWith("ab")) add(`${stem}le`);
    if (stem.endsWith("i")) add(`${stem.slice(0, -1)}y`);
  }
  if (word.endsWith("ically")) add(`${word.slice(0, -6)}ic`);
  if (word.endsWith("ally")) add(`${word.slice(0, -4)}al`);
  for (const suffix of ["ment", "tion", "sion", "ity", "ness", "ship", "ance", "ence", "able", "ible", "ous", "ism", "ist", "ure", "ery"]) {
    if (word.endsWith(suffix) && word.length > suffix.length + 3) add(word.slice(0, -suffix.length));
  }
  if (word.endsWith("ive")) add(word.slice(0, -3));
  if (word.endsWith("age")) add(word.slice(0, -3));
  if (word.endsWith("al")) add(word.slice(0, -2));
  return [...candidates];
}

function wordUrl(host, word) {
  return `${host}${encodeURIComponent(word).replace(/%2F/g, "/")}`;
}

function detectLanguage(etymology) {
  const text = String(etymology || "");
  if (/Anglo-French/i.test(text)) return "アングロ・フランス語";
  if (/Old French/i.test(text)) return "古フランス語";
  if (/Middle French/i.test(text)) return "中期フランス語";
  if (/Late Latin/i.test(text)) return "後期ラテン語";
  if (/Medieval Latin/i.test(text)) return "中世ラテン語";
  if (/Vulgar Latin/i.test(text)) return "俗ラテン語";
  if (/Greek/i.test(text)) return "ギリシャ語";
  if (/Latin/i.test(text)) return "ラテン語";
  if (/French/i.test(text)) return "フランス語";
  if (/German/i.test(text)) return "ドイツ語";
  if (/Arabic/i.test(text)) return "アラビア語";
  if (/Hindi/i.test(text)) return "ヒンディー語";
  if (/Spanish/i.test(text)) return "スペイン語";
  if (/Italian/i.test(text)) return "イタリア語";
  if (/Old English/i.test(text)) return "古英語";
  if (/Middle English/i.test(text)) return "中英語";
  return "英語";
}

function compactSourcePhrase(etymology, fallbackWord) {
  const text = String(etymology || "").replace(/\s+/g, " ").trim();
  const relationPattern = /(?:an alteration of|back-formation from|directly from|borrowed from|derived from|from|via)\s+((?:Anglo-French|Old French|Middle French|Late Latin|Medieval Latin|Vulgar Latin|Old English|Middle English|French|Latin|Greek|German|Arabic|Hindi|Spanish|Italian))\s+([^\s,;()]+)(?:\s+\([^)]*\))*\s*(?:["“]([^"”]+)["”])?/gi;
  let firstRelation = null;
  let informativeRelation = null;
  for (const relation of text.matchAll(relationPattern)) {
    const current = { language: relation[1], term: relation[2], gloss: relation[3] || "" };
    if (!firstRelation) firstRelation = current;
    if (current.gloss && !informativeRelation) informativeRelation = current;
  }
  const relation = informativeRelation || firstRelation;
  if (relation) {
    return `${relation.language} ${relation.term}`;
  }
  const compound = text.match(/(?:from|of)\s+([A-Za-z][A-Za-z-]*)\s*(?:\([^)]*\))?\s*\+\s*(-?[A-Za-z][A-Za-z-]*)/i);
  if (compound) return `${compound[1]}＋${compound[2]}`;
  const plain = text.match(/(?:from|via)\s+([A-Za-z][A-Za-z-]*)/i);
  if (plain) return plain[1];
  return fallbackWord;
}

function sourceWordFor(lemma, etymologies) {
  if (etymologies.has(lemma)) return lemma;
  const manual = {
    complicit: "complicity",
  };
  if (manual[lemma] && etymologies.has(manual[lemma])) return manual[lemma];
  for (const candidate of inflectionCandidates(lemma)) {
    if (etymologies.has(candidate)) return candidate;
  }
  if (lemma.startsWith("on") && etymologies.has(lemma.slice(2))) return lemma.slice(2);
  return lemma;
}

function derivationFor(lemma, sourceWord, etymology, meaning) {
  const meaningText = String(meaning || "").trim();
  if (!etymology) {
    return `英語 ${sourceWord}の語源には諸説がある → ${meaningText}`;
  }
  const compact = compactSourcePhrase(etymology, sourceWord);
  const qualifier = /uncertain origin|unknown origin|origin is unknown|perhaps|possibly|may be/i.test(etymology)
    ? "（由来には不確かな点がある）"
    : "";
  const isCompound = lemma === "onrush" && sourceWord === "rush";
  const isRelated = lemma === "complicit" && sourceWord === "complicity";
  if (isCompound) return `英語 on＋${sourceWord}の複合語 → ${meaningText}`;
  const surfaceNote = isRelated
    ? `${sourceWord}と同系の語。`
    : lemma === sourceWord
      ? ""
      : `原形${sourceWord}からの語形変化。`;
  return `${detectLanguage(compact)} ${compact.replace(/^(?:Anglo-French|Old French|Middle French|Late Latin|Medieval Latin|Vulgar Latin|Old English|Middle English|French|Latin|Greek|German|Arabic|Hindi|Spanish|Italian)\s+/i, "")}に由来${qualifier}。${surfaceNote} → ${meaningText}`;
}

// Etymology chips are intentionally curated. A spelling overlap alone is not
// enough to claim a prefix/root decomposition in a learning card.
const A_CLASSIFICATIONS = {
  prelude: { root: "lud", parts: [["pre", "prefix", "前もって"], ["lud", "root", "遊ぶ・だます"]], bridge: "前もって演奏する" },
  precluded: { root: "clud", parts: [["pre", "prefix", "前もって"], ["clud", "root", "閉じる"]], bridge: "前もって閉じて入れない" },
  endemic: { root: "dem", parts: [["en", "prefix", "中に"], ["dem", "root", "民衆"], ["-ic", "suffix", "〜の性質の"]], bridge: "その土地の民衆の中に固有の" },
  abject: { root: "ject", parts: [["ab", "prefix", "離れて"], ["ject", "root", "投げる"]], bridge: "遠くへ投げ捨てられた" },
  invariable: { root: "vari", parts: [["in", "prefix", "〜でない"], ["vari", "root", "変化する"]], bridge: "変化しない" },
  prelate: { root: "lat", parts: [["pre", "prefix", "前もって"], ["lat", "root", "運ぶ・持たれる"]], bridge: "前に運ばれ、選ばれた者" },
  commotion: { root: "mov", parts: [["com", "prefix", "ともに"], ["mot", "root", "動かす"]], bridge: "ともに激しく動かす" },
  propensity: { root: "pend", parts: [["pro", "prefix", "前へ"], ["pens", "root", "吊るす・傾ける"], ["-ty", "suffix", "性質・状態"]], bridge: "前へ傾く性質" },
  revitalized: { root: "vit", parts: [["re", "prefix", "再び"], ["vit", "root", "生命・生きる"]], bridge: "再び生命を与えた" },
  distorted: { root: "tort", parts: [["dis", "prefix", "別の方向へ"], ["tort", "root", "ねじる"]], bridge: "別の方向へねじった" },
  perfunctory: { root: "funct", parts: [["per", "prefix", "通して"], ["funct", "root", "果たす・実行する"]], bridge: "仕事を通り抜けるだけの" },
  amiability: { root: "ami", parts: [["ami", "root", "友・愛する"], ["-ity", "suffix", "〜であること"]], bridge: "友好的である性質" },
  subsidize: { root: "sid", parts: [["sid", "root", "座る・前に座る"], ["-ize", "suffix", "〜にする"]], bridge: "支えとなる状態にする" },
  tenacious: { root: "ten", parts: [["ten", "root", "保つ"], ["-ous", "suffix", "〜に満ちた"]], bridge: "しっかり保つ性質の" },
  explicit: { root: "plic", parts: [["ex", "prefix", "外へ"], ["plic", "root", "折る"]], bridge: "外へ折り開いて明らかにした" },
  abdicated: { root: "dic", parts: [["ab", "prefix", "離れて"], ["dic", "root", "言う"]], bridge: "権利を離れると宣言した" },
  disparate: { root: "par", parts: [["dis", "prefix", "離れて"], ["par", "root", "等しい"]], bridge: "等しくない、離れた" },
  diatribe: { root: "trib", parts: [["dia", "prefix", "通して"], ["trib", "root", "割り当てる"]], bridge: "言葉を通して激しく論じる" },
  ingratiated: { root: "grat", parts: [["in", "prefix", "中へ"], ["grat", "root", "喜ばせる・感謝"]], bridge: "好意の中へ入った" },
  adorned: { root: "orn", parts: [["ad", "prefix", "〜へ"], ["orn", "root", "飾る・装備する"]], bridge: "飾り付けた" },
  retorted: { root: "tort", parts: [["re", "prefix", "返して"], ["tort", "root", "ねじる"]], bridge: "言葉をねじり返した" },
  ingenious: { root: "gen", parts: [["in", "prefix", "内に"], ["gen", "root", "生む・種"]], bridge: "内から生み出した" },
  inundation: { root: "und", parts: [["in", "prefix", "中へ"], ["und", "root", "波"]], bridge: "波が中へあふれ込むこと" },
  anonymity: { root: "nom", parts: [["nym", "root", "名前"], ["-ity", "suffix", "〜であること"]], bridge: "名前がない状態" },
  precept: { root: "cap", parts: [["pre", "prefix", "前もって"], ["cept", "root", "取る"]], bridge: "前もって受け取った教え" },
  inception: { root: "cap", parts: [["in", "prefix", "中へ"], ["cept", "root", "取る"]], bridge: "中へ取り込んで始めること" },
  incurred: { root: "cur", parts: [["in", "prefix", "中へ"], ["cur", "root", "走る"]], bridge: "身に走り込んできた負担を負った" },
  invoked: { root: "voc", parts: [["in", "prefix", "中へ"], ["vok", "root", "呼ぶ・声"]], bridge: "呼び寄せた" },
  interspersed: { root: "spers", parts: [["inter", "prefix", "間に"], ["spers", "root", "散らす・広げる"]], bridge: "間に散らした" },
  recanted: { root: "cant", parts: [["re", "prefix", "再び"], ["cant", "root", "歌う"]], bridge: "言ったことを取り消して言い直した" },
  pervaded: { root: "vad", parts: [["per", "prefix", "通して"], ["vad", "root", "行く"]], bridge: "全体を通り抜けて行き渡った" },
  presided: { root: "sid", parts: [["pre", "prefix", "前に"], ["sid", "root", "座る・前に座る"]], bridge: "前に座って取り仕切った" },
  apathetic: { root: "path", parts: [["path", "root", "感じる・苦しむ"], ["-ic", "suffix", "〜の性質の"]], bridge: "感情を感じない性質の" },
  conducive: { root: "duc", parts: [["con", "prefix", "ともに"], ["duc", "root", "導く"], ["-ive", "suffix", "〜する性質の"]], bridge: "よい方向へともに導く性質の" },
  innocuous: { root: "noc", parts: [["in", "prefix", "〜でない"], ["noc", "root", "害する"]], bridge: "害を与えない" },
  effusive: { root: "fus", parts: [["fus", "root", "注ぐ・溶かす"], ["-ive", "suffix", "〜する性質の"]], bridge: "外へ注ぎ出す性質の" },
  ineligible: { root: "lect", parts: [["in", "prefix", "〜でない"], ["lig", "root", "集める・選ぶ"]], bridge: "選ばれる資格がない" },
  admonished: { root: "mon", parts: [["ad", "prefix", "〜へ"], ["mon", "root", "知らせる・警告する"]], bridge: "注意を向けて警告した" },
  propelled: { root: "puls", parts: [["pro", "prefix", "前へ"], ["pel", "root", "押す"]], bridge: "前へ押し出した" },
  deposed: { root: "pos", parts: [["de", "prefix", "下へ"], ["pos", "root", "置く"]], bridge: "下へ置いて地位から退けた" },
  detested: { root: "test", parts: [["de", "prefix", "強く"], ["test", "root", "証言する・証人"]], bridge: "強く拒む気持ちを証言した" },
  efficacious: { root: "fac", parts: [["fic", "root", "作る・なす"], ["-ous", "suffix", "〜に満ちた"]], bridge: "効果を生み出す性質の" },
  delinquent: { root: "linqu", parts: [["de", "prefix", "離れて"], ["linqu", "root", "残す・離れる"]], bridge: "義務から離れて残された" },
  defunct: { root: "funct", parts: [["de", "prefix", "離れて"], ["funct", "root", "果たす・実行する"]], bridge: "役目を果たし終えた" },
  progeny: { root: "gen", parts: [["pro", "prefix", "前へ"], ["gen", "root", "生む・種"]], bridge: "生み出された子孫" },
  remit: { root: "mit", parts: [["re", "prefix", "再び"], ["mit", "root", "送る"]], bridge: "再び送る、または送り返す" },
  transpired: { root: "spir", parts: [["trans", "prefix", "越えて"], ["spir", "root", "息"]], bridge: "通り抜けて外へ息が出た" },
  insidious: { root: "sid", parts: [["in", "prefix", "中に"], ["sid", "root", "座る・前に座る"]], bridge: "中に座って気づかれず進む" },
  derisive: { root: "rid", parts: [["de", "prefix", "離れて"], ["ris", "root", "笑う"], ["-ive", "suffix", "〜する性質の"]], bridge: "笑いものにする性質の" },
  infamy: { root: "fam", parts: [["in", "prefix", "悪い方向に"], ["fam", "root", "話す・評判"]], bridge: "悪い評判" },
  epitomize: { root: "tom", parts: [["tom", "root", "切る"], ["-ize", "suffix", "〜にする"]], bridge: "切り詰めて典型にする" },
  exhale: { root: "hale", parts: [["ex", "prefix", "外へ"], ["hale", "root", "息をする"]], bridge: "息を外へ出す" },
  extricate: { root: "tric", parts: [["ex", "prefix", "外へ"], ["tric", "root", "もつれ"]], bridge: "もつれから外へ出す" },
  defuse: { root: "fus", parts: [["de", "prefix", "離れて"], ["fus", "root", "注ぐ・溶かす"]], bridge: "溶かして取り除く" },
  invincible: { root: "vinc", parts: [["in", "prefix", "〜でない"], ["vinc", "root", "打ち勝つ"]], bridge: "打ち負かすことができない" },
  incessant: { root: "ced", parts: [["in", "prefix", "〜でない"], ["cess", "root", "行く・譲る"]], bridge: "止むことなく進む" },
  electorate: { root: "lect", parts: [["lect", "root", "集める・選ぶ"], ["-ate", "suffix", "〜にする（動詞化）"]], bridge: "選ぶ人々のまとまり" },
  interlude: { root: "lud", parts: [["inter", "prefix", "間の"], ["lud", "root", "遊ぶ・だます"]], bridge: "間に置かれた劇" },
  encapsulate: { root: "cap", parts: [["en", "prefix", "中へ"], ["cap", "root", "取る"], ["-ate", "suffix", "〜にする（動詞化）"]], bridge: "中に取り込んで包む" },
  denounce: { root: "nounce", parts: [["de", "prefix", "強く"], ["nounce", "root", "知らせる・報告する"]], bridge: "公に強く告げ知らせる" },
  obsequious: { root: "sequ", parts: [["ob", "prefix", "相手に向かって"], ["sequ", "root", "追う"]], bridge: "相手に従って追う" },
  oblique: { root: "obliqu", parts: [["ob", "prefix", "〜に対して"], ["obliqu", "root", "斜め・曲がった"]], bridge: "まっすぐでなく曲がった方向の" },
  extenuating: { root: "tenu", parts: [["ex", "prefix", "外へ"], ["tenu", "root", "細い・薄い"]], bridge: "外へ細くして軽くする" },
  generic: { root: "gen", parts: [["gen", "root", "生む・種"], ["-ic", "suffix", "〜の性質の"]], bridge: "同じ種・種類に属する性質の" },
  exquisite: { root: "quir", parts: [["ex", "prefix", "外へ"], ["quis", "root", "求める"]], bridge: "外へ求め抜いて選び出した" },
  intractable: { root: "tract", parts: [["in", "prefix", "〜でない"], ["tract", "root", "引く"]], bridge: "引いて扱うことができない" },
  summarily: { root: "summ", parts: [["summ", "root", "合計・頂点"], ["-ly", "suffix", "〜な状態で"]], bridge: "要点をまとめた状態で" },
  repercussion: { root: "cuss", parts: [["re", "prefix", "返して"], ["cuss", "root", "揺さぶる"]], bridge: "打ち返して響くこと" },
  desist: { root: "sist", parts: [["de", "prefix", "離れて"], ["sist", "root", "立つ"]], bridge: "その場から離れて立ち止まる" },
  deplored: { root: "plor", parts: [["de", "prefix", "強く"], ["plor", "root", "泣く・叫ぶ"]], bridge: "強く嘆き、非難した" },
  deplorable: { root: "plor", parts: [["de", "prefix", "強く"], ["plor", "root", "泣く・叫ぶ"], ["-able", "suffix", "〜できる・〜に値する"]], bridge: "嘆かわしいと思うほどの" },
  complicit: { root: "plic", parts: [["com", "prefix", "ともに"], ["plic", "root", "折る"]], bridge: "ともに絡み合って関与する" },
};

function shortGloss(meaning) {
  const value = String(meaning || "").trim();
  return value.split(/[、,／/]/, 1)[0].trim() || value;
}

function buildAClassificationPatch(ledger, lemma, definition) {
  const entry = ledger.entries[lemma];
  if (!entry) throw new Error(`${lemma}: 研究台帳に存在しません`);
  const rootEntry = ledger.dictionary.roots[definition.root];
  if (!rootEntry) throw new Error(`${lemma}: root ${definition.root} が辞書にありません`);
  const parts = definition.parts.map(([form, kind, gloss]) => {
    if (kind === "root") {
      const valid = [definition.root, ...(rootEntry.variants || [])].map(normalize);
      if (!valid.includes(normalize(form))) throw new Error(`${lemma}: ${form} は${definition.root}のroot/variantではありません`);
    } else {
      const affix = ledger.dictionary.affixes[form];
      if (!affix || affix.kind !== kind) throw new Error(`${lemma}: ${form} がaffixes辞書にありません`);
    }
    if (!normalize(lemma).includes(normalize(form.replace(/^-/, "")))) throw new Error(`${lemma}: ${form} が原形に含まれていません`);
    return { form, kind, gloss };
  });
  const meaning = entry.meanings[0];
  const derivation = `${definition.bridge} → ${meaning}`;
  return {
    classification: "A",
    display: { type: "A", gloss: shortGloss(meaning), root: definition.root, parts, derivation },
    research: {
      status: "reviewed",
      components: parts,
      rootCandidates: [definition.root],
      semanticBridge: definition.bridge,
      summary: derivation,
      notes: "A型。接辞と語根の対応が確認できるため、構成チップで表示。",
    },
  };
}

function loadEtymologies(indexPath) {
  const index = readJson(indexPath);
  const etymologies = new Map();
  for (const entry of index) {
    if (!entry || !entry.word || !entry.etymology) continue;
    const etymology = String(entry.etymology).trim();
    const word = normalize(entry.word);
    etymologies.set(word, etymology);
    const alias = word.replace(/\s+\([^)]*\)$/, "");
    if (alias && !etymologies.has(alias)) etymologies.set(alias, etymology);
    const unhyphenated = word.replace(/-/g, "");
    if (unhyphenated && !etymologies.has(unhyphenated)) etymologies.set(unhyphenated, etymology);
  }
  return etymologies;
}

function collectVocabulary(manifest, lemmaMap) {
  const byLemma = new Map();
  for (const [datasetId, entry] of Object.entries(manifest.q1 || {})) {
    if (!datasetId.startsWith("eiken1-")) continue;
    const filePath = path.resolve(ROOT, entry.vocabUrl);
    const vocab = readJson(filePath);
    for (const item of vocab.words || []) {
      const surface = String(item.word || "").trim();
      if (!surface) continue;
      const lemma = lemmaMap[normalize(surface)] || normalize(surface);
      const row = byLemma.get(lemma) || { surfaceForms: [], meanings: [], datasets: [] };
      if (!row.surfaceForms.includes(surface)) row.surfaceForms.push(surface);
      if (item.meaning && !row.meanings.includes(item.meaning)) row.meanings.push(item.meaning);
      if (!row.datasets.includes(datasetId)) row.datasets.push(datasetId);
      byLemma.set(lemma, row);
    }
  }
  return byLemma;
}

function main() {
  if (process.argv[2] === "--classify-a") {
    const outputPath = process.argv[3] || path.join(DATA_DIR, "word_origin_research_batch_055.json");
    const ledger = readJson(path.join(DATA_DIR, "word_origin_research.json"));
    const entries = {};
    for (const [lemma, definition] of Object.entries(A_CLASSIFICATIONS)) {
      if (ledger.entries[lemma]?.research?.batch !== "batch-054") continue;
      entries[lemma] = buildAClassificationPatch(ledger, lemma, definition);
    }
    fs.writeFileSync(outputPath, `${JSON.stringify({
      meta: {
        batchId: "batch-055",
        note: "英検1級模試第10回〜第21回のうち、接辞と語根を確認できる語を画像例と同じA型チップ表示へ整形するバッチ。",
      },
      entries,
    }, null, 2)}\n`, "utf8");
    console.log(JSON.stringify({ outputPath, entries: Object.keys(entries).length }, null, 2));
    return;
  }

  if (process.argv[2] === "--reformat") {
    const indexPath = process.argv[3];
    const inputPath = process.argv[4];
    const outputPath = process.argv[5] || path.join(DATA_DIR, "word_origin_research_batch_054.json");
    if (!indexPath || !inputPath) throw new Error("使い方: node scripts/generate_missing_word_origin_batch.cjs --reformat <etymonline-index.json> <input-batch.json> [output.json]");
    const etymologies = loadEtymologies(indexPath);
    const input = readJson(inputPath);
    const entries = {};
    for (const [lemma, patch] of Object.entries(input.entries || {})) {
      const sourceWord = patch.research?.etymons?.[0] || lemma;
      const etymology = etymologies.get(sourceWord) || "";
      const meaning = patch.meanings?.[0] || "意味未登録";
      const derivation = derivationFor(lemma, sourceWord, etymology, meaning);
      entries[lemma] = {
        display: { type: "B", derivation },
        research: { status: "reviewed", summary: derivation },
      };
    }
    fs.writeFileSync(outputPath, `${JSON.stringify({
      meta: {
        batchId: "batch-054",
        note: "既存B型の表示文を、他セットと同じ日本語の短い語源経路＋意味の形式へ統一する再整形バッチ。",
      },
      entries,
    }, null, 2)}\n`, "utf8");
    console.log(JSON.stringify({ outputPath, entries: Object.keys(entries).length }, null, 2));
    return;
  }

  const indexPath = process.argv[2];
  const outputPath = process.argv[3] || path.join(DATA_DIR, "word_origin_research_batch_053.json");
  if (!indexPath) throw new Error("使い方: node scripts/generate_missing_word_origin_batch.cjs <etymonline-index.json> [output.json]");

  const etymologies = loadEtymologies(indexPath);
  const lemmaMap = Object.fromEntries(
    Object.entries(readJson(path.join(DATA_DIR, "lemmas.json")).lemmas || {})
      .map(([surface, lemma]) => [normalize(surface), normalize(lemma)]),
  );
  const manifest = readJson(path.join(DATA_DIR, "manifest.json"));
  const origins = readJson(path.join(DATA_DIR, "word_origins.json")).origins || {};
  const exclusions = readJson(path.join(DATA_DIR, "word_origin_excluded.json")).excluded || {};
  const excluded = new Set(Object.values(exclusions).flatMap((group) => Object.keys(group)));
  const vocabulary = collectVocabulary(manifest, lemmaMap);
  const entries = {};
  const coverage = { direct: 0, inflected: 0, unavailable: 0 };

  for (const [lemma, row] of vocabulary) {
    if (origins[lemma] || excluded.has(lemma)) continue;
    const sourceWord = sourceWordFor(lemma, etymologies);
    const etymology = etymologies.get(sourceWord) || "";
    if (etymology && sourceWord === lemma) coverage.direct += 1;
    else if (etymology) coverage.inflected += 1;
    else coverage.unavailable += 1;
    const meaning = row.meanings[0] || "意味未登録";
    const etymonline = wordUrl("https://www.etymonline.com/word/", sourceWord);
    const merriam = wordUrl("https://www.merriam-webster.com/dictionary/", sourceWord);
    const derivation = derivationFor(lemma, sourceWord, etymology, meaning);
    entries[lemma] = {
      surfaceForms: row.surfaceForms,
      meanings: row.meanings,
      classification: "B",
      display: { type: "B", derivation },
      research: {
        status: "reviewed",
        sources: [etymonline, merriam],
        sourceNotes: [
          {
            url: etymonline,
            note: etymology
              ? `Etymonline由来データで${sourceWord}の語源記述を確認。${lemma === sourceWord ? "" : `表示語は${sourceWord}の語形変化として扱った。`}`
              : `${sourceWord}の語源ページを確認対象として登録。詳細な起源は断定しない。`,
          },
          {
            url: merriam,
            note: `Merriam-Websterの${sourceWord}辞書項目を独立した語義・見出し確認先として登録。`,
          },
        ],
        originLanguage: detectLanguage(etymology),
        etymons: etymology ? [sourceWord] : [],
        historicalPath: etymology
          ? [`${detectLanguage(etymology)}の語・表現`, `英語 ${sourceWord}`, `英語 ${lemma}`]
          : [`${sourceWord}の語源は諸説あり`, `英語 ${lemma}`],
        components: [],
        rootCandidates: [],
        semanticBridge: etymology
          ? `${sourceWord}の語源的な意味から、現在の${meaning}へ意味が広がった。`
          : `確定的な語源経路を示さず、現在の${meaning}だけを学習上の中心義として残した。`,
        summary: derivation,
        confidence: etymology ? "medium" : "low",
        notes: "B型。綴りの類似だけで語根分解せず、個別の語源説明として収録。",
      },
    };
  }

  const result = {
    meta: {
      batchId: "batch-053",
      note: "英検1級模試第10回〜第21回で不足していた語源表示を追加するバッチ。Etymonline由来データとMerriam-Webster項目を参照先として登録。",
      coverage,
    },
    entries,
  };
  fs.writeFileSync(outputPath, `${JSON.stringify(result, null, 2)}\n`, "utf8");
  console.log(JSON.stringify({ outputPath, entries: Object.keys(entries).length, coverage }, null, 2));
}

main();
