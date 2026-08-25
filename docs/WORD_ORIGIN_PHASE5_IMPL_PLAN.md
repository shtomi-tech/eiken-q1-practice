# 単語語源 段階5 実装計画

対象: `static/mode-q1.js` / `scripts/check-word-origin-ui.cjs` / `scripts/check-word-origin-data.cjs` / `scripts/build_word_origin_stub.py` / `docs/WORD_ORIGIN_AUTHORING.md` / `index.html` / `data/word_roots.json` / `data/word_origins.json`
関連: [WORD_ORIGIN_PHASE5_PLAN.md](WORD_ORIGIN_PHASE5_PLAN.md)（方針と見込み）/ [WORD_ORIGIN_AUTHORING.md](WORD_ORIGIN_AUTHORING.md)（作成基準）
前提: 段階4＝`bcfb4c0`。方針は `4e36e69` の段階5計画で確定
状態: 未着手

## 0. 全体の順序

**先に仕組み（バッチ0）を1コミットで通し、そのあとデータのバッチを6本積む。** 仕組みを後回しにすると、仲間語0のカードが「パネルなし」で先に大量に入り、目視確認ができない。

| コミット | 内容 | 規模 |
| --- | --- | --- |
| バッチ0 | 作業1〜6（UI・検査・スタブ・基準・キャッシュバスター） | コード変更のみ |
| バッチ1〜6 | `in-` `re-` `de-` `con-` `dis-` `ex-` のデータ投入 | 1バッチ15〜45語の候補 |

## 1. 作業1: 仲間語0でも語根パネルを出す

`static/mode-q1.js` の `flashWordOrigin`（2447〜2468行）。現在はパネル全体が `visibleSiblings.length` で囲まれている。

```js
// 変更前（2452行）
if (visibleSiblings.length) {
  const rootEntry = wordRoots.roots[origin.root] || {};
  const panel = el("div", { class: "particlePanel wordOriginPanel" });
  …見出し・note…
  const siblingList = el("ul", { class: "particleSiblings" });
  visibleSiblings.forEach(…);
  panel.appendChild(siblingList);
  row.appendChild(panel);
}
```

```js
// 変更後
const rootEntry = wordRoots.roots[origin.root];
if (rootEntry) {
  const panel = el("div", { class: "particlePanel wordOriginPanel" });
  const rootOrigin = rootEntry.origin ? `（${rootEntry.origin}）` : "";
  panel.appendChild(el("p", { class: "particlePanelTitle" },
    `語根「${origin.root}」＝${rootEntry.gloss || "共通の語根"}${rootOrigin}`));
  if (rootEntry.note) panel.appendChild(el("p", { class: "particleCore" }, rootEntry.note));
  if (visibleSiblings.length) {
    const siblingList = el("ul", { class: "particleSiblings" });
    visibleSiblings.forEach(…);      // 中身は現状のまま
    panel.appendChild(siblingList);
  }
  row.appendChild(panel);
}
```

- 条件を `wordRoots.roots[origin.root] || {}` から**実在チェック**に変える。辞書に無い語根でパネルの見出しだけ出す状態（「＝共通の語根」）を作らないため。
- 既存136語の表示は変わらない（すべて語根が辞書にあり、仲間語も1語以上ある）。
- CSSの変更は不要。`.wordOriginPanel` の `margin-top` はそのまま効く。

## 2. 作業2: `check-word-origin-ui.cjs` を条件変更に追随させる

現在の検査はパネルとリストを区別していない。**パネルの生成が仲間語の有無より先に来ること**を機械で固定する。

```js
const panelIdx = flashWordOriginBody.indexOf("wordOriginPanel");
const siblingGateIdx = flashWordOriginBody.indexOf("visibleSiblings.length");
assert.ok(panelIdx !== -1 && siblingGateIdx !== -1, "語根パネルと仲間語の分岐が必要です");
assert.ok(panelIdx < siblingGateIdx, "語根パネルは仲間語の有無に関係なく描く必要があります");
assert.ok(flashWordOriginBody.includes("particleSiblings"), "仲間語リストのクラスが必要です");
```

既存の `particlePanel` `wordOriginPanel` `sibling.gloss` のアサーション（57・58・64行）はそのまま残す。

## 3. 作業3: `check-word-origin-data.cjs` に進捗ログを足す

判定は増やさない。**A型が1語だけの語根の数**を最後に出す。方針の副作用（単発語根ばかりになる）を毎回目に入れるため。

```js
const singleRootCount = [...aOriginsByRoot.values()].filter((lemmas) => lemmas.length === 1).length;
console.log(`word origin roots: ${Object.keys(rootsData.roots).length} roots / ${singleRootCount} single-word roots`);
```

既存の `word origin data contract: OK (N origins / M roots)` の行はそのまま残す。

## 4. 作業4: スタブに `--prefix` を足す

`scripts/build_word_origin_stub.py` は語根単位でしか候補を出せない（109行 `--root` が必須）。接頭辞単位のバッチ用に追加する。

- `--root` と `--prefix` を**排他・どちらか必須**にする（`add_mutually_exclusive_group(required=True)`）。
- `--prefix in` は `data/word_roots.json` の `affixes` から `kind: "prefix"` のキーを引き、綴りが一致する**未登録の原形だけ**を出す（`word_origins.json` にあるものは除く）。`--root` 側の出力（原形・一致した綴り・既存の `meaning`・収録ファイル）と同じ形にする。
- 各行に**接尾辞が付くかどうか**を出す（`-ate` `-ous` などが末尾にあるか）。分解の見通しを付ける材料になる。
- 長さの下限を設ける（接頭辞＋4文字以上）。`in place` のような句や `income` のような短い語が上位に来るのを避ける。
- 読み取り専用は維持する。語根の割り当ても `derivation` も生成しない。

出力例:

```
## in-（中へ・否定）
- candidates: 45（未登録のみ）
- `incarcerate` [in] 接尾辞: -ate — 投獄する — vocab_1_mock-2.json
- `incumbent` [in] 接尾辞: なし — 現職の — vocab_1_2026-1.json
```

## 5. 作業5: `WORD_ORIGIN_AUTHORING.md` に単発語根の基準を足す

段階5計画の3章をそのまま基準に落とす。

- 語根は**複数語で使えることを要件にしない**。要件は「その語根を示すと中心義を思い出せること」だけ。
- 語根の `origin` にラテン語・ギリシャ語の原形を必ず書く。原形が書けない語根は登録しない。
- 語根の `note` に、その語根を持つ**英語の別の語を1つ以上**挙げる（アプリ未収録でよい）。`carcer` → `incarceration`、`cumb` → `succumb`。
- 迷ったらB型。分解しても中心義が出てこない語をA型にしない。

段階1計画の「複数語で使える語根だけ」という記述にも、段階5で撤回した旨を1行足す。

## 6. 作業6: キャッシュバスター

`index.html` の `mode-q1.js?v=1.2.2` を `1.2.3` にする。`styles.css` は変更しないので据え置く。

## 7. バッチ0の検証

- `npm test`（新しいログ行が出ること、既存の検査が通ること）。
- `python scripts/build_word_origin_stub.py --prefix in` が45語前後を返し、`--root spec` が従来どおり動くこと。
- ブラウザで既存カード（`equivocate` など）の表示が変わらないこと。
- **仲間語0のカードはこの時点ではまだ存在しない**（現在A型1語だけの語根は0個）。作業1の見た目の確認はバッチ1で最初の単発語根が入ったときに行う。バッチ0の段階では既存カードの非退行だけを見る。

## 8. バッチ1〜6の手順

1. `python scripts/build_word_origin_stub.py --prefix <接頭辞>` で候補を出す。
2. 対象外 / A / B / C に分ける。A型は語根を `word_roots.json` に足し、`word_origins.json` に `root` `parts` `derivation` `gloss` を書く。
3. C型は `cReasons` に語根名つきで理由を書く（`in place` のような句・複合語は「対象外」で記録しない）。
4. `npm test`。
5. ブラウザで2枚確認する。**仲間語0のカード1枚**（語根パネルが見出し＋noteだけで出ること）と、既存の仲間語ありカード1枚。375px幅も見る。
6. 1バッチ＝1コミット。

## 9. 合格条件

- バッチ0: `npm test` が通り、`--prefix` が動き、既存カードの表示が変わらない。
- バッチ1〜6: 段階5計画の合格条件（A型240語前後・カバー率21%前後・単発語根に `origin` と `note`）。
- 途中で `single-word roots` が語根総数の8割を超えたら、いったん止めて方針を見直す。

## 10. 非目標

- `flashCoreImage`（熟語側）の表示条件を変えること。熟語の不変化詞パネルは仲間例が要るので、今回の変更は単語側だけに閉じる。
- 仲間語の並べ替え・ローテーションの変更（段階4のまま）。
- CSSの変更。
