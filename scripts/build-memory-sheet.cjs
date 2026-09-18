#!/usr/bin/env node
// 語彙データから A4縦1枚の暗記シートHTMLを生成する。
// 持ち歩いてスキマ時間に使うため、中央の折り線で縦half foldすると
// 左（英語）だけが表に出て、右（日本語）が裏へ隠れる形にする。開けば答え合わせ。
// 例: node scripts/build-memory-sheet.cjs --dataset eiken1-mock-9 --q 17-24
//     node scripts/build-memory-sheet.cjs --dataset vocab_1_2026-1 --from 1 --to 32 --no-example
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUT_DIR = path.join(ROOT, 'docs', 'memory-sheets');

// "eiken1-mock-10:1-7" / "eiken1-mock-9:25" を { dataset, qFrom, qTo } に読む。
function parseSet(value) {
  const m = /^(.+?):(\d+)(?:-(\d+))?$/.exec(String(value || '').trim());
  if (!m) throw new Error('--set は データセットID:問番号（例 eiken1-mock-10:1-7）の形式で指定してください');
  const qFrom = Number(m[2]);
  const qTo = Number(m[3] || m[2]);
  if (qTo < qFrom) throw new Error('--set の問番号は from <= to にしてください');
  return { dataset: m[1], qFrom, qTo };
}

function parseArgs(argv) {
  const args = { from: 1, to: 32, example: true, sets: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const key = argv[i];
    if (key === '--dataset') args.dataset = argv[++i];
    else if (key === '--from') args.from = Number(argv[++i]);
    else if (key === '--to') args.to = Number(argv[++i]);
    else if (key === '--out') args.out = argv[++i];
    else if (key === '--title') args.title = argv[++i];
    else if (key === '--q') args.q = argv[++i];
    // 1日の学習が複数セットにまたがる場合に使う。例: --set eiken1-mock-9:25 --set eiken1-mock-10:1-7
    else if (key === '--set') args.sets.push(parseSet(argv[++i]));
    else if (key === '--no-example') args.example = false;
    else throw new Error(`不明な引数: ${key}`);
  }
  if (args.sets.length) return args;
  if (!args.dataset) throw new Error('--dataset か --set が必要です（例: vocab_1_2026-1 / eiken1-mock-9:1-8）');
  if (args.q) {
    const m = /^(\d+)(?:-(\d+))?$/.exec(args.q.trim());
    if (!m) throw new Error('--q は 17 または 17-24 の形式で指定してください');
    args.qFrom = Number(m[1]);
    args.qTo = Number(m[2] || m[1]);
    if (args.qTo < args.qFrom) throw new Error('--q は from <= to にしてください');
    return args;
  }
  if (!Number.isInteger(args.from) || !Number.isInteger(args.to) || args.from < 1 || args.to < args.from) {
    throw new Error('--from / --to は 1 以上の整数で from <= to にしてください');
  }
  return args;
}

// manifest の datasetId（例: eiken1-mock-9）でも、data配下のファイル名でも受け付ける。
function resolveVocabFile(datasetId) {
  const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'manifest.json'), 'utf8'));
  for (const group of Object.values(manifest)) {
    if (group && typeof group === 'object' && group[datasetId] && group[datasetId].vocabUrl) {
      return path.join(ROOT, group[datasetId].vocabUrl);
    }
  }
  return path.join(ROOT, 'data', `${datasetId.replace(/\.json$/, '')}.json`);
}

function loadEntries(datasetId) {
  const file = resolveVocabFile(datasetId);
  if (!fs.existsSync(file)) throw new Error(`データセットが見つかりません: ${file}`);
  const raw = JSON.parse(fs.readFileSync(file, 'utf8'));
  const words = Array.isArray(raw.words) ? raw.words : [];
  const idioms = Array.isArray(raw.idioms) ? raw.idioms : [];
  const entries = [...words, ...idioms].map((item) => ({
    q: Number(item.q),
    term: item.word || item.phrase || '',
    ipa: item.ipa || '',
    pos: item.pos || '',
    meaning: item.meaning || '',
    example: item.example || '',
    exampleTranslation: item.exampleTranslation || '',
  })).filter((item) => item.term);
  return { meta: raw.meta || {}, entries, file };
}

const ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
function esc(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, (ch) => ESCAPES[ch]);
}

// 例文中の見出し語を空所（____）にする。折って英語面だけを見たとき、
// 語義だけでなく「その語が入る文脈」も想起できるようにするため。
// 語形変化や熟語の語順ゆれに備えて語幹の前方一致で探し、見つからない語は原文のまま残す。
function blankExample(example, term) {
  let out = esc(example);
  const parts = String(term).trim().split(/\s+/).filter(Boolean);
  for (const part of parts) {
    const stem = part.length > 6 ? part.slice(0, part.length - 2) : part;
    const escaped = stem.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const pattern = new RegExp(`\\b${escaped}[a-z]*\\b`, 'i');
    if (pattern.test(out)) out = out.replace(pattern, '<span class="blank">&nbsp;</span>');
  }
  return out;
}

function renderRow(entry, index, opts) {
  const cls = opts.groupStart ? ' groupStart' : '';
  const en = `<div class="cell en${cls}">`
    + `<div class="term"><span class="no">${index}</span><b>${esc(entry.term)}</b>`
    + (entry.pos ? `<span class="pos">${esc(entry.pos)}</span>` : '')
    + (entry.ipa ? `<span class="ipa">${esc(entry.ipa)}</span>` : '')
    + '<span class="checks" aria-hidden="true">□□□</span>'
    + '</div>'
    + (opts.withExample && entry.example
      ? `<div class="ex">${blankExample(entry.example, entry.term)}</div>` : '')
    + '</div>';
  const ja = `<div class="cell ja${cls}">`
    + `<div class="meaning">${esc(entry.meaning)}</div>`
    + (opts.withExample && entry.exampleTranslation
      ? `<div class="exja">${esc(entry.exampleTranslation)}</div>` : '')
    + '</div>';
  return en + ja;
}

function buildHtml({ title, subtitle, entries, withExample, startNo }) {
  let lastQ = null;
  const rows = entries.map((entry, i) => {
    // セットをまたぐ場合は「データセット:問」で区切る。同じ問番号が続いても別の問として扱う。
    const key = entry.gkey || String(entry.q);
    const groupStart = lastQ !== null && key !== lastQ;
    lastQ = key;
    return renderRow(entry, startNo + i, { withExample, groupStart });
  }).join('\n');
  return `<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>${esc(title)}</title>
<style>
  @page { size: A4 portrait; margin: 7mm 7mm 4mm; }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: "Yu Gothic", "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif;
         color: #000; background: #fff; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .sheet { width: 196mm; margin: 0 auto; }
  header { display: flex; align-items: baseline; gap: 4mm; border-bottom: 1.2pt solid #000;
           padding-bottom: 1mm; margin-bottom: 1mm; }
  header h1 { font-size: 10.5pt; margin: 0; letter-spacing: .02em; white-space: nowrap; }
  header .sub { font-size: 6.8pt; color: #333; white-space: nowrap; }
  header .how { margin-left: auto; font-size: 6.5pt; color: #333; }
  .rounds { display: flex; gap: 4mm; font-size: 6.3pt; color: #333; margin: 0 0 1mm; }
  .rounds span.slot { border-bottom: .4pt solid #999; min-width: 28mm; }

  /* 左=英語 / 右=日本語。中央の折り線で谷折りすると右半分が裏へ回る。 */
  .grid { display: grid; grid-template-columns: 114mm 1fr; column-gap: 0; }
  .cell { border-bottom: .4pt solid #ccc; padding: .25mm 0 .3mm; }
  .cell.en { padding-right: 3mm; }
  .cell.ja { padding-left: 3mm; border-left: .5pt dashed #999; }
  .cell.groupStart { border-top: .8pt solid #000; padding-top: .9mm; }

  .term { display: flex; align-items: baseline; gap: 1.5mm; }
  .term b { font-size: 8.6pt; font-family: "Times New Roman", serif; }
  .no { font-size: 6.5pt; color: #666; min-width: 4.5mm; }
  .pos { font-size: 6pt; color: #222; border: .4pt solid #888; border-radius: 1mm; padding: 0 .8mm; }
  .ipa { font-size: 6.5pt; color: #555; }
  .checks { margin-left: auto; font-size: 7.5pt; color: #aaa; letter-spacing: .2mm; }
  .ex { font-size: 6.1pt; color: #333; margin: 0 0 0 4.5mm; line-height: 1.15;
        font-family: "Times New Roman", serif; }
  .blank { display: inline-block; min-width: 11mm; border-bottom: .6pt solid #000;
           vertical-align: baseline; }
  .meaning { font-size: 7.8pt; line-height: 1.2; }
  .exja { font-size: 5.9pt; color: #555; line-height: 1.15; margin-top: 0; }

  /* 折り位置の目印。紙を縦半分に折ったとき、この線が折り目になる。 */
  .foldMark { display: grid; grid-template-columns: 114mm 1fr; font-size: 6pt; color: #666;
              margin: .5mm 0 0; }
  .foldMark .left { text-align: right; padding-right: 1mm; }
  .foldMark .right { padding-left: 2mm; }
  footer { margin-top: .8mm; font-size: 6.3pt; color: #555; display: flex; gap: 4mm; }
  footer .right { margin-left: auto; }
  @media screen { body { padding: 8mm; } }
</style>
</head>
<body>
<div class="sheet">
  <header>
    <h1>${esc(title)}</h1>
    <span class="sub">${esc(subtitle)}</span>
    <span class="how">縦の破線で折る → 英語だけが表に出る。訳と空所に入る語を思い出してから開いて確認。</span>
  </header>
  <div class="rounds">
    <span class="slot">1回目 当日　　/</span>
    <span class="slot">2回目 翌日　　/</span>
    <span class="slot">3回目 1週間後　/</span>
    <span>思い出せなかった語だけ □ にチェック → 次の周回はチェックのある語だけ見る</span>
  </div>
  <div class="grid">
${rows}
  </div>
  <div class="foldMark">
    <span class="left">▲ この縦線で折る</span>
    <span class="right">開くと日本語。裏返して折れば 日本語 → 英語 にも使える</span>
  </div>
  <footer>
    <span>${esc(entries.length)} 語　/　太線は出題1問（4語）の区切り</span>
    <span class="right">3回とも即答できた語は番号を塗りつぶして卒業</span>
  </footer>
</div>
</body>
</html>
`;
}

// --set で複数セットをまたぐとき用。指定順に連結し、出典と問番号を保ったまま通し番号を振り直す。
function buildFromSets(args) {
  const slices = args.sets.map((set) => {
    const { meta, entries } = loadEntries(set.dataset);
    const picked = entries
      .filter((item) => item.q >= set.qFrom && item.q <= set.qTo)
      .map((item) => ({ ...item, gkey: `${set.dataset}:${item.q}` }));
    if (!picked.length) throw new Error(`${set.dataset} の第${set.qFrom}問–第${set.qTo}問に語がありません`);
    const range = set.qFrom === set.qTo ? `第${set.qFrom}問` : `第${set.qFrom}問–第${set.qTo}問`;
    return { meta, picked, label: `${set.dataset} ${range}` };
  });
  return {
    entries: slices.flatMap((s) => s.picked),
    subtitle: slices.map((s) => s.label).join('　＋　'),
    grade: slices[0].meta.grade || '',
    fileStem: args.sets
      .map((set) => `${set.dataset}_q${set.qFrom}${set.qFrom === set.qTo ? '' : `-${set.qTo}`}`)
      .join('+'),
  };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.sets.length) {
    const built = buildFromSets(args);
    const title = args.title || `${built.grade} 暗記シート`.trim();
    const html = buildHtml({
      title,
      subtitle: built.subtitle,
      entries: built.entries,
      withExample: args.example,
      startNo: 1,
    });
    const out = args.out
      ? path.resolve(ROOT, args.out)
      : path.join(OUT_DIR, `${built.fileStem}.html`);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, html, 'utf8');
    process.stdout.write(`${path.relative(ROOT, out)} を生成しました（${built.entries.length} 語）\n`);
    return;
  }
  const { meta, entries } = loadEntries(args.dataset);
  const byQuestion = Boolean(args.q);
  // 問番号で絞る場合も、シート内の通し番号は1から振り直す。
  const slice = byQuestion
    ? entries.filter((item) => item.q >= args.qFrom && item.q <= args.qTo)
    : entries.slice(args.from - 1, args.to);
  if (!slice.length) throw new Error(`指定範囲に語がありません（全 ${entries.length} 語）`);
  const startNo = byQuestion ? 1 : args.from;
  const range = byQuestion
    ? `第${args.qFrom}問–第${args.qTo}問`
    : `No.${args.from}–${args.from + slice.length - 1}`;
  const title = args.title || `${meta.grade || ''} ${meta.round || args.dataset} 暗記シート`.trim();
  const subtitle = `${args.dataset} / ${range}`;
  const html = buildHtml({ title, subtitle, entries: slice, withExample: args.example, startNo });
  const out = args.out
    ? path.resolve(ROOT, args.out)
    : path.join(OUT_DIR, byQuestion
      ? `${args.dataset}_q${args.qFrom}-${args.qTo}.html`
      : `${args.dataset}_${args.from}-${args.from + slice.length - 1}.html`);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, html, 'utf8');
  process.stdout.write(`${path.relative(ROOT, out)} を生成しました（${slice.length} 語 / 全 ${entries.length} 語中）\n`);
}

main();
