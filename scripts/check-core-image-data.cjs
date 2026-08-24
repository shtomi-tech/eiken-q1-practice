const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const DATA_DIR = path.join(ROOT, "data");
const PARTICLE_PATH = path.join(DATA_DIR, "particle_images.json");
const MANIFEST_PATH = path.join(DATA_DIR, "manifest.json");
const PAGES_WORKFLOW_PATH = path.join(ROOT, ".github", "workflows", "pages.yml");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function tokens(value) {
  return String(value || "").toLowerCase().match(/[a-z]+(?:['-][a-z]+)*/g) || [];
}

const irregularBase = {
  bought: "buy",
  brought: "bring",
  caught: "catch",
  dealt: "deal",
  held: "hold",
  laid: "lay",
  lost: "lose",
  made: "make",
  paid: "pay",
  sold: "sell",
  stood: "stand",
  took: "take",
  felt: "feel",
  went: "go",
};

function relatedTerm(termToken, phraseToken) {
  const termForms = [termToken, irregularBase[termToken] || ""];
  const phraseForms = [phraseToken, irregularBase[phraseToken] || ""];
  return termForms.some((termForm) => phraseForms.some((phraseForm) => (
    termForm === phraseForm
      || (termForm.length >= 3 && phraseForm.length >= 3
        && termForm.slice(0, 3) === phraseForm.slice(0, 3))
  )));
}

function assertNonEmptyString(value, label) {
  assert.equal(typeof value, "string", `${label} は文字列である必要があります`);
  assert.ok(value.trim(), `${label} は空にできません`);
}

function normalizedPhrase(value) {
  return String(value || "").toLowerCase().replace(/\s+/g, " ").trim();
}

assert.ok(fs.existsSync(PARTICLE_PATH), "data/particle_images.json が必要です");
assert.ok(fs.existsSync(MANIFEST_PATH), "data/manifest.json が必要です");
assert.ok(fs.existsSync(PAGES_WORKFLOW_PATH), ".github/workflows/pages.yml が必要です");
assert.match(
  fs.readFileSync(PAGES_WORKFLOW_PATH, "utf8"),
  /cp data\/particle_images\.json _site\/data\//,
  "Pagesの静的ファイル準備でparticle_images.jsonをコピーする必要があります",
);
const particleData = readJson(PARTICLE_PATH);
const manifest = readJson(MANIFEST_PATH);
assert.ok(particleData && typeof particleData === "object", "particle_images.json はオブジェクトである必要があります");
assert.ok(particleData.particles && typeof particleData.particles === "object" && !Array.isArray(particleData.particles), "particles 辞書が必要です");

for (const [particle, entry] of Object.entries(particleData.particles)) {
  assert.ok(entry && typeof entry === "object" && !Array.isArray(entry), `${particle}: 辞書項目が不正です`);
  assertNonEmptyString(entry.core, `${particle}.core`);
  if (entry.siblings != null) {
    assert.ok(Array.isArray(entry.siblings), `${particle}.siblings は配列である必要があります`);
    assert.ok(entry.siblings.length >= 3 && entry.siblings.length <= 6, `${particle}.siblings は3〜6件である必要があります`);
    entry.siblings.forEach((sibling, index) => {
      assertNonEmptyString(sibling && sibling.phrase, `${particle}.siblings[${index}].phrase`);
      assertNonEmptyString(sibling && sibling.gloss, `${particle}.siblings[${index}].gloss`);
    });
  }
  if (entry.senses != null) {
    assert.ok(Array.isArray(entry.senses), `${particle}.senses は配列である必要があります`);
    const senseIds = new Set();
    entry.senses.forEach((sense, index) => {
      const label = `${particle}.senses[${index}]`;
      assert.ok(sense && typeof sense === "object" && !Array.isArray(sense), `${label} が不正です`);
      assertNonEmptyString(sense.id, `${label}.id`);
      assert.ok(!senseIds.has(sense.id), `${particle}: sense id ${sense.id} が重複しています`);
      senseIds.add(sense.id);
      assertNonEmptyString(sense.label, `${label}.label`);
      assert.ok(Array.isArray(sense.siblings), `${label}.siblings は配列である必要があります`);
      assert.ok(sense.siblings.length >= 3 && sense.siblings.length <= 6, `${label}.siblings は3〜6件である必要があります`);
      sense.siblings.forEach((sibling, siblingIndex) => {
        assertNonEmptyString(sibling && sibling.phrase, `${label}.siblings[${siblingIndex}].phrase`);
        assertNonEmptyString(sibling && sibling.gloss, `${label}.siblings[${siblingIndex}].gloss`);
      });
    });
  }
  if (particle === "out" && Array.isArray(entry.senses)) {
    assert.ok(entry.senses.length <= 10, "out の sense は10前後まで統合する必要があります");
  }
  assert.ok(entry.siblings || entry.senses, `${particle}: siblings または senses が必要です`);
}

let coreImageCount = 0;
const deliveryVocabFiles = new Set(
  Object.values(manifest.q1 || {})
    .map((dataset) => path.basename(dataset.vocabUrl || ""))
    .filter((fileName) => fileName.startsWith("vocab_") && fileName.endsWith(".json")),
);
const progressRows = [];
const uniqueDeliveryEntries = new Map();
const cReasons = new Map([
  ["provided that", "接続詞句で、条件節そのものを連鎖化しない"],
  ["rather than", "接続詞句で、比較・選択の機能を優先する"],
  ["even though", "接続詞句で、譲歩節の機能を優先する"],
  ["shake hands", "動詞＋名詞の定型表現で、不変化詞の連鎖にならない"],
  ["give way", "動詞＋名詞の定型表現で、意味の中心が語の組合せにある"],
  ["take pains", "動詞＋名詞の定型表現で、意味の中心が語の組合せにある"],
  ["make sense", "動詞＋名詞の定型表現で、意味の中心が語の組合せにある"],
  ["more or less", "等位の定型表現で、動詞＋不変化詞ではない"],
  ["sooner or later", "等位の定型表現で、動詞＋不変化詞ではない"],
  ["day and night", "等位の定型表現で、動詞＋不変化詞ではない"],
  ["before and after", "対になる副詞句で、動詞＋不変化詞ではない"],
  ["bit by bit", "反復構造の副詞句で、動詞＋不変化詞ではない"],
  ["far and away", "等位の副詞句で、動詞＋不変化詞ではない"],
  ["all or nothing", "選択を表す定型表現で、動詞＋不変化詞ではない"],
  ["safe and sound", "等位の形容詞句で、動詞＋不変化詞ではない"],
  ["make a move", "動詞＋名詞の定型表現で、不変化詞の連鎖にならない"],
  ["take a nap", "動詞＋名詞の定型表現で、不変化詞の連鎖にならない"],
  ["make a wish", "動詞＋名詞の定型表現で、不変化詞の連鎖にならない"],
  ["take a chance", "動詞＋名詞の定型表現で、不変化詞の連鎖にならない"],
  ["learn by heart", "動詞＋名詞を含む定型表現で、不変化詞の連鎖にならない"],
  ["come of age", "動詞＋名詞を含む定型表現で、不変化詞の連鎖にならない"],
  ["take it easy", "動詞＋目的語＋形容詞の定型表現で、連鎖がこじつけになる"],
  ["have a dream", "動詞＋名詞の定型表現で、不変化詞の連鎖にならない"],
  ["have a word", "動詞＋名詞の定型表現で、不変化詞の連鎖にならない"],
  ["make an excuse", "動詞＋名詞の定型表現で、不変化詞の連鎖にならない"],
  ["make a start", "動詞＋名詞の定型表現で、不変化詞の連鎖にならない"],
  ["none of your business", "名詞句の定型表現で、動詞＋不変化詞ではない"],
]);
const expected2025_2Terminals = new Map([
  ["pony up", "支払いのために金を出す"],
  ["buckle down", "気を引き締めて本腰を入れる"],
  ["foul up", "手順を乱して失敗させる"],
  ["cast down", "気持ちを落とし込んで落胆させる"],
  ["breeze in", "ふらりと中へ入ってくる"],
  ["branch off", "本道から分かれて別方向へ進む"],
  ["crack down", "厳しく押さえ込んで取り締まる"],
  ["lop off", "余分な部分を切り離して落とす"],
  ["dwell on", "対象に意識をとどめてくよくよ考える"],
  ["reel off", "次々と外へ繰り出してすらすら言う"],
  ["rustle up", "材料をかき集めて急いで用意する"],
  ["haul off", "その場から急に持ち去る"],
  ["fritter away", "少しずつ遠ざけて浪費する"],
  ["rip off", "相手から不当に奪い取る"],
  ["sound off", "外へ声を出して意見をぶちまける"],
  ["crop up", "問題などが突然現れる"],
]);
const allowedCoreImageKeys = new Set(["chain", "particle", "particleSense", "note", "siblings"]);
const senseRefsByPhrase = new Map();
const senseSiblingLocations = new Map();
const vocabFiles = fs.readdirSync(DATA_DIR)
  .filter((name) => /^vocab_.*\.json$/.test(name))
  .sort();

function simulatedSiblingPool(item) {
  const image = item.coreImage;
  if (!image || !image.particle) return [];
  const particleEntry = particleData.particles[image.particle];
  const senseEntry = image.particleSense && Array.isArray(particleEntry?.senses)
    ? particleEntry.senses.find((sense) => sense.id === image.particleSense)
    : null;
  return image.siblings || senseEntry?.siblings || particleEntry?.siblings || [];
}

function simulatedVisibleSiblings(item) {
  const pool = simulatedSiblingPool(item);
  const ownPhrases = new Set([
    normalizedPhrase(item.phrase),
    normalizedPhrase((item.coreImage.chain || []).filter((step) => step.term).map((step) => step.term).join(" ")),
  ]);
  const filtered = pool.filter((sibling) => !ownPhrases.has(normalizedPhrase(sibling.phrase)));
  if (filtered.length <= 3) return filtered.map((sibling) => normalizedPhrase(sibling.phrase));
  return [0, 1, 2].map((offset) => normalizedPhrase(filtered[(item._particleSlot + offset) % filtered.length].phrase));
}

function simulatedFilteredSiblingCount(item) {
  const ownPhrases = new Set([
    normalizedPhrase(item.phrase),
    normalizedPhrase((item.coreImage.chain || []).filter((step) => step.term).map((step) => step.term).join(" ")),
  ]);
  return simulatedSiblingPool(item).filter((sibling) => !ownPhrases.has(normalizedPhrase(sibling.phrase))).length;
}

function assertNoSimulatedSlotCollisions(items, label) {
  const slots = new Map();
  const selections = new Map();
  for (const item of items) {
    const image = item.coreImage;
    if (!image || !image.particle) continue;
    const datasetId = item._datasetId || label;
    const senseId = image.particleSense || "";
    const key = `${datasetId}:${image.particle}:${senseId}`;
    const slot = slots.get(key) || 0;
    item._particleSlot = slot;
    slots.set(key, slot + 1);
    // 3件以下のプールは仕様上全件表示するため、同じ組になること自体は衝突ではない。
    if (simulatedFilteredSiblingCount(item) <= 3) continue;
    const signature = simulatedVisibleSiblings(item).join("\u0001");
    const previous = selections.get(key)?.get(signature);
    assert.equal(
      previous,
      undefined,
      `${label}/${item.phrase}: slot ${slot} が ${previous?.phrase || "別の熟語"} と同じ仲間例を選びました`,
    );
    const group = selections.get(key) || new Map();
    group.set(signature, { phrase: item.phrase, slot });
    selections.set(key, group);
  }
}

for (const fileName of vocabFiles) {
  const vocab = readJson(path.join(DATA_DIR, fileName));
  const items = [
    ...(vocab.words || []).map((item) => ({ ...item, type: "word", _datasetId: fileName })),
    ...(vocab.idioms || []).map((item) => ({ ...item, type: "idiom", _datasetId: fileName })),
  ];
  assertNoSimulatedSlotCollisions(items, `loadData/${fileName}`);
}

// assignParticleSlots() はスロットキーに datasetId を含むため、級プールでもスロットはセット単位で振られる。
// この検査はその前提（級をまたいでスロットが連番にならないこと）が崩れていないことの確認であり、
// 意図的にファイル単位の検査と同じ結果になる。
const pooledByGrade = new Map();
for (const [datasetId, dataset] of Object.entries(manifest.q1 || {})) {
  const match = datasetId.match(/^(eiken1|eiken2|eikenp1|eikenp2|eikentopic|iuhw)-/);
  if (!match) continue;
  const vocabPath = path.join(DATA_DIR, path.basename(dataset.vocabUrl || ""));
  if (!fs.existsSync(vocabPath)) continue;
  const vocab = readJson(vocabPath);
  const gradeItems = pooledByGrade.get(match[1]) || [];
  gradeItems.push(
    ...(vocab.words || []).map((item) => ({ ...item, type: "word", _datasetId: datasetId })),
    ...(vocab.idioms || []).map((item) => ({ ...item, type: "idiom", _datasetId: datasetId })),
  );
  pooledByGrade.set(match[1], gradeItems);
}
for (const [grade, items] of pooledByGrade.entries()) {
  assertNoSimulatedSlotCollisions(items, `loadPooledItems/${grade}`);
}

for (const fileName of vocabFiles) {
  const vocab = readJson(path.join(DATA_DIR, fileName));
  const senseUseCounts = new Map();
  const phraseCorePresence = new Map();
  let fileCoreImageCount = 0;
  for (const item of vocab.idioms || []) {
    const phraseKey = normalizedPhrase(item.phrase);
    const hasCoreImage = Object.prototype.hasOwnProperty.call(item, "coreImage");
    if (deliveryVocabFiles.has(fileName)) {
      const existing = uniqueDeliveryEntries.get(phraseKey);
      if (existing) {
        assert.equal(
          existing.hasCoreImage,
          hasCoreImage,
          `${fileName}/${item.phrase}: 配信セット間でcoreImageの有無が一致していません`,
        );
      } else {
        uniqueDeliveryEntries.set(phraseKey, { phrase: item.phrase, hasCoreImage, item });
      }
    }
    if (phraseCorePresence.has(phraseKey)) {
      assert.equal(
        phraseCorePresence.get(phraseKey),
        hasCoreImage,
        `${fileName}/${item.phrase}: 同一セット内の重複phraseでcoreImageの有無が一致していません`,
      );
    } else {
      phraseCorePresence.set(phraseKey, hasCoreImage);
    }
    if (!hasCoreImage) continue;
    coreImageCount += 1;
    fileCoreImageCount += 1;
    const label = `${fileName}/${item.phrase}`;
    const image = item.coreImage;
    Object.keys(image).forEach((key) => {
      assert.ok(allowedCoreImageKeys.has(key), `${label}: coreImage.${key} は未使用フィールドです`);
    });
    if (fileName === "vocab_1_2025-2.json") {
      const expectedTerminal = expected2025_2Terminals.get(normalizedPhrase(item.phrase));
      assert.equal(
        image.chain.at(-1).gloss,
        expectedTerminal,
        `${label}: chainの最終要素は中心義に合わせて作り直してください`,
      );
    }
    assert.ok(image && typeof image === "object" && !Array.isArray(image), `${label}: coreImage が不正です`);
    assert.ok(Array.isArray(image.chain), `${label}: chain は配列である必要があります`);
    assert.ok(image.chain.length >= 2 && image.chain.length <= 5, `${label}: chain は2〜5要素である必要があります`);
    image.chain.forEach((step, index) => {
      assert.ok(step && typeof step === "object" && !Array.isArray(step), `${label}: chain[${index}] が不正です`);
      assertNonEmptyString(step.gloss, `${label}: chain[${index}].gloss`);
      if (Object.prototype.hasOwnProperty.call(step, "term")) {
        assertNonEmptyString(step.term, `${label}: chain[${index}].term`);
        assert.equal(step.term, step.term.toLowerCase(), `${label}: chain[${index}].term は小文字の原形で書きます`);
        assert.ok(
          tokens(step.term).every((termToken) => tokens(item.phrase).some((phraseToken) => relatedTerm(termToken, phraseToken))),
          `${label}: chain[${index}].term が phrase と対応していません`,
        );
      }
    });
    const lastStep = image.chain[image.chain.length - 1];
    assert.ok(!Object.prototype.hasOwnProperty.call(lastStep, "term"), `${label}: chain の最後は導出結果にしてください`);
    const particleEntry = image.particle != null ? particleData.particles[image.particle] : null;
    if (image.particle != null) {
      assertNonEmptyString(image.particle, `${label}: particle`);
      assert.ok(particleEntry, `${label}: particle辞書に ${image.particle} がありません`);
      const phraseTokens = tokens(item.phrase);
      assert.ok(
        tokens(image.particle).every((particleToken) => phraseTokens.includes(particleToken)),
        `${label}: particle が phrase に含まれていません`,
      );
    }
    if (Array.isArray(particleEntry && particleEntry.senses)) {
      assertNonEmptyString(image.particleSense, `${label}: sensesを持つparticleにはparticleSenseが必要です`);
      assert.notEqual(image.particleSense, "general", `${label}: particleSense=general は使わないでください`);
      const senseEntry = particleEntry.senses.find((sense) => sense.id === image.particleSense);
      assert.ok(
        senseEntry,
        `${label}: particleSense ${image.particleSense} が辞書にありません`,
      );
      const senseKey = `${image.particle}\u0000${image.particleSense}`;
      const phraseSenseKey = `${image.particle}\u0000${normalizedPhrase(item.phrase)}`;
      const phraseSenseRefs = senseRefsByPhrase.get(phraseSenseKey) || new Set();
      phraseSenseRefs.add(image.particleSense);
      senseRefsByPhrase.set(phraseSenseKey, phraseSenseRefs);
      const reference = senseUseCounts.get(senseKey) || {
        particle: image.particle,
        senseId: image.particleSense,
        count: 0,
      };
      reference.count += 1;
      senseUseCounts.set(senseKey, reference);
    } else if (image.particleSense != null) {
      assertNonEmptyString(image.particleSense, `${label}: particleSense`);
      assert.fail(`${label}: particleSenseにはsenses辞書が必要です`);
    }
    if (image.siblings != null) {
      assert.ok(Array.isArray(image.siblings), `${label}: coreImage.siblings は配列である必要があります`);
      assert.ok(image.siblings.length >= 1 && image.siblings.length <= 3, `${label}: coreImage.siblings は1〜3件である必要があります`);
      image.siblings.forEach((sibling, index) => {
        assertNonEmptyString(sibling && sibling.phrase, `${label}: coreImage.siblings[${index}].phrase`);
        assertNonEmptyString(sibling && sibling.gloss, `${label}: coreImage.siblings[${index}].gloss`);
      });
    }
    const senseEntry = image.particleSense && particleEntry && Array.isArray(particleEntry.senses)
      ? particleEntry.senses.find((sense) => sense.id === image.particleSense)
      : null;
    const resolvedSiblings = image.siblings || senseEntry?.siblings || particleEntry?.siblings || [];
    const ownPhrases = new Set([
      normalizedPhrase(item.phrase),
      normalizedPhrase((image.chain || []).filter((step) => step.term).map((step) => step.term).join(" ")),
    ]);
    resolvedSiblings.forEach((sibling) => {
      assert.ok(!ownPhrases.has(normalizedPhrase(sibling.phrase)), `${label}: 仲間例に自分自身を含めないでください`);
    });
    if (image.note != null) assertNonEmptyString(image.note, `${label}: note`);
  }
  for (const { particle, senseId, count } of senseUseCounts.values()) {
    const sense = particleData.particles[particle].senses.find((candidate) => candidate.id === senseId);
    const minimumPoolSize = Math.min(3 + (count - 1), 6);
    assert.ok(
      sense.siblings.length >= minimumPoolSize,
      `${fileName}/${particle}/${senseId}: ${count}件参照されるため仲間例は${minimumPoolSize}件以上必要です`,
    );
  }
  if (deliveryVocabFiles.has(fileName) && (vocab.idioms || []).length > 0) {
    progressRows.push({ fileName, idioms: vocab.idioms.length, coreImage: fileCoreImageCount });
  }
}

for (const [particle, entry] of Object.entries(particleData.particles)) {
  for (const sense of entry.senses || []) {
    for (const sibling of sense.siblings || []) {
      const key = `${particle}\u0000${normalizedPhrase(sibling.phrase)}`;
      const locations = senseSiblingLocations.get(key) || new Set();
      locations.add(sense.id);
      senseSiblingLocations.set(key, locations);
    }
  }
}
for (const [key, locations] of senseSiblingLocations.entries()) {
  if (locations.size <= 1) continue;
  const referencedSenses = senseRefsByPhrase.get(key) || new Set();
  assert.ok(
    [...locations].some((senseId) => referencedSenses.has(senseId)),
    `${key}: 重複する仲間例は参照元のparticleSenseと一致するsense側に限定してください`,
  );
}

assert.ok(coreImageCount > 0, "coreImage を持つ熟語が1件以上必要です");
assert.equal(progressRows.length, 15, "manifest配信対象の熟語セットは15セットである必要があります");
assert.equal(progressRows.reduce((sum, row) => sum + row.idioms, 0), 292, "manifest配信対象の熟語数は292件である必要があります");
for (const row of progressRows) {
  console.log(`core image progress: ${row.fileName}: ${row.idioms} idioms / ${row.coreImage} coreImage`);
}
const uniqueCoreRows = [...uniqueDeliveryEntries.values()];
const unannotatedRows = uniqueCoreRows.filter((row) => !row.hasCoreImage);
for (const row of unannotatedRows) {
  assert.ok(cReasons.has(normalizedPhrase(row.phrase)), `${row.phrase}: 未注釈の理由をC型一覧に記録してください`);
}
for (const phrase of cReasons.keys()) {
  assert.ok(
    unannotatedRows.some((row) => normalizedPhrase(row.phrase) === phrase),
    `${phrase}: C型一覧にある熟語へcoreImageを付けないでください`,
  );
}
const particleBackedCount = uniqueCoreRows.filter((row) => row.hasCoreImage && row.item.coreImage.particle).length;
const chainOnlyCount = uniqueCoreRows.filter((row) => row.hasCoreImage && !row.item.coreImage.particle).length;
assert.equal(unannotatedRows.length, cReasons.size, "未注釈のC型熟語数が記録と一致していません");
console.log(`core image unique categories: particle-backed ${particleBackedCount} / chain-only ${chainOnlyCount} / C ${unannotatedRows.length}`);
console.log(`core image data contract: OK (${coreImageCount} entries)`);
