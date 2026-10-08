#!/usr/bin/env bash
# 公開用の静的ファイルを _site/ に集める（GitHub Pages / Cloudflare 共通）。
# 事前に scripts/write-config.mjs で static/config.json を生成しておくこと。
set -euo pipefail

rm -rf _site
mkdir -p _site/static/vendor/harness _site/data _site/assets/audio/vocab _site/assets/audio/lemma
mkdir -p _site/data/context-translations
mkdir -p _site/static/vendor/fsrs
cp index.html .nojekyll _site/
cp static/app.js static/mode-q1.js static/styles.css static/config.json _site/static/
cp static/vendor/harness/cloud.js _site/static/vendor/harness/
cp static/vendor/fsrs/index.umd.js static/vendor/fsrs/LICENSE _site/static/vendor/fsrs/
cp data/manifest.json data/lemmas.json _site/data/
cp data/context_*.json _site/data/
cp data/context-translations/*.json _site/data/context-translations/
cp data/particle_images.json _site/data/
cp data/word_roots.json data/word_origins.json _site/data/
cp data/questions_[0-9]*.json data/questions_p2_*.json data/questions_pre1_*.json _site/data/
cp data/vocab_[0-9]*.json data/vocab_p2_*.json data/vocab_pre1_*.json _site/data/
cp data/questions_iuhw_*.json data/vocab_iuhw_*.json _site/data/
cp -R assets/audio/vocab/* _site/assets/audio/vocab/
cp -R assets/audio/lemma/* _site/assets/audio/lemma/
expected_lemma_audio_count=$(node -e 'const fs=require("fs"); const data=JSON.parse(fs.readFileSync("data/lemmas.json", "utf8")); const entries=Object.keys(data.entries || {}); const display=Object.values(data.flashcardLemmas || {}); const displayOnly=Object.values(data.flashcardDisplayLemmas || {}); console.log(new Set([...entries, ...display, ...displayOnly]).size)')
lemma_audio_count=$(find assets/audio/lemma -type f -name '*.mp3' | wc -l)
site_lemma_audio_count=$(find _site/assets/audio/lemma -type f -name '*.mp3' | wc -l)
# Retired cards may retain audio for existing learner history. Verify required
# coverage and every copied file rather than treating archived audio as an error.
test "$lemma_audio_count" -ge "$expected_lemma_audio_count"
test "$site_lemma_audio_count" -eq "$lemma_audio_count"
node <<'NODE'
const fs = require('fs');
const assert = require('node:assert/strict');
const data = JSON.parse(fs.readFileSync('data/lemmas.json', 'utf8'));
const required = new Set([
  ...Object.keys(data.entries || {}),
  ...Object.values(data.flashcardLemmas || {}),
  ...Object.values(data.flashcardDisplayLemmas || {}),
]);
const slug = value => String(value).toLowerCase().replace(/[’']/g, "'")
  .replace(/\b(one's|his|her|my|your|our|their|its)\b/g, '@poss')
  .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
for (const lemma of required) {
  const file = `_site/assets/audio/lemma/${slug(lemma)}.mp3`;
  assert.ok(fs.existsSync(file) && fs.statSync(file).size > 0, `Missing lemma audio: ${lemma}`);
}
for (const file of fs.readdirSync('assets/audio/lemma').filter(file => file.endsWith('.mp3'))) {
  assert.ok(fs.readFileSync(`assets/audio/lemma/${file}`).equals(
    fs.readFileSync(`_site/assets/audio/lemma/${file}`)), `Copied lemma audio differs: ${file}`);
}
console.log(`Lemma audio: ${required.size} required; all copied files verified.`);
NODE
