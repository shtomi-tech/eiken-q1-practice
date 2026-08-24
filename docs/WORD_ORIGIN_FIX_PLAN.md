# 単語語源表示 修正計画

対象: `index.html` / `README.md` / `DESIGN.md` / `static/styles.css` / `scripts/check-word-origin-data.cjs` / `scripts/check-word-origin-ui.cjs` / `docs/WORD_ORIGIN_PLAN.md`
関連: [WORD_ORIGIN_PLAN.md](WORD_ORIGIN_PLAN.md)（導入計画）/ [WORD_ORIGIN_AUTHORING.md](WORD_ORIGIN_AUTHORING.md)（作成基準）
状態: 実装済み（2026-08-24、未コミット）。A〜Hを反映し、`npm test` と実ブラウザで確認済み

## 0. 現状の判定

実装そのものは動いている。確認済みの事実:

- `equivocate` カードで DOM順が `flashRow:意味 → wordOriginRow → flashRow:例文`。チップ3枚＋導出行＋語根パネルが出る。
- 仲間語は別セット（`vocab_1_mock-4.json` の `evocative`）から補われる＝`pooledData` フォールバックが機能している。
- 熟語カード（`reel in`）は従来どおり核心イメージを表示＝回帰なし。コンソールエラー0、375px幅で横溢れなし。

修正対象は下表の8件。**AとBは公開（Pagesデプロイ）の前に必須**、C〜Fは段階1に進む前、G・Hは同時にやってよい後始末。

| # | 症状 | 重大度 | 直す場所 |
| --- | --- | --- | --- |
| A | `index.html` のキャッシュバスター未更新。JS/CSSを変更したのに `?v=` が据え置き | 公開前必須 | `index.html` |
| B | `README.md` / `DESIGN.md` 未更新。UIの正本に語源表示の規則が無い | 公開前必須 | `README.md` `DESIGN.md` |
| C | `meaningOverlap` が2文字一致で通り、活用語尾だけで素通りする | 中 | `check-word-origin-data.cjs` |
| D | 仲間語1語でもパネルを出す（計画の「2語以下は保留」と不一致） | 中 | `WORD_ORIGIN_PLAN.md`（計画側を修正） |
| E | 仲間語が大文字＋monoで出て、見出し語の表記と割れる | 中 | `styles.css` |
| F | 375pxで「+」を消して強制改行するため、合成ではなく箇条書きに見える | 小 | `styles.css` |
| G | `.flashEtym` が死にルール | 小 | `styles.css` |
| H | UI検査のCSSアサーション2件が空振り | 小 | `check-word-origin-ui.cjs` |

## A. キャッシュバスターを上げる（公開前必須）

`static/mode-q1.js` と `static/styles.css` を変更したのに、`index.html` の参照が据え置きになっている。

```
10:<link rel="stylesheet" href="static/styles.css?v=1.1.5">
29:<script src="static/mode-q1.js?v=1.2.0"></script>
```

このリポジトリは `058c302`〜`86af5fe` まで、JS/CSSを触るコミットで必ずこの番号を上げている。据え置くと再訪ユーザーに古いJSと新しいCSS（またはその逆）が配信され、語源が出ない／枠だけ出る状態になる。

- `styles.css?v=1.1.6`、`mode-q1.js?v=1.2.1` にする。
- 再発防止として `check-word-origin-ui.cjs` に、`index.html` の `mode-q1.js?v=` と `styles.css?v=` が**存在すること**だけを検査する行を足す（番号の妥当性は機械で判定できないため、存在確認にとどめる）。

## B. 正本（README / DESIGN）を更新する（公開前必須）

AGENTS.md は「UIは対象リポジトリの `DESIGN.md` を正本とする」と定めており、熟語の核心イメージ導入時（`058c302`）は `DESIGN.md` と `README.md` を同じコミットで更新している。

`README.md`

- データ一覧（52行目付近、`data/particle_images.json` の隣）に次を追加する。
  - 単語の語根・接辞辞書（表示専用）: `data/word_roots.json`
  - 単語の語源分解（表示専用・原形キー）: `data/word_origins.json`
- 95行目の「語源（収録されている場合）」の記述を、A型＝チップ＋導出行＋語根パネル、B型＝由来一行、という現在の実体に合わせる。

`DESIGN.md`

- 熟語の核心イメージの項（79行目）の直後に、単語の語源表示の規則を1項として追加する。書く内容:
  - 単語の暗記カードでは**意味の直下・例文の前**に置く。
  - 構成要素はチップ（`.originChip`）で横並びにし、`+` で連結する。チップは種別ラベル（接頭辞／語根／接尾辞）・綴り・訳の3段で、**色だけで種別を区別しない**。
  - 導出行（`.originDerivation`）はhairlineで区切った1行。矢印の後ろは中心義。
  - 語根パネル（`.wordOriginPanel`）は熟語の `.particlePanel` と同じ構造を流用し、見出しは「語根「〜」＝訳（出典）」。仲間語は最大3語。
  - 480px以下ではチップを縦積みにする（Fの結論を反映した表現にする）。

## C. `meaningOverlap` を厳しくする

### 症状

`derivation` の矢印以降と `meaning` の2文字一致で合格するため、活用語尾だけで通る。実測:

```
overlap("適当 → した", "統合した、固めた") === true
```

意味的に無関係な `derivation` でも「した」だけで通るため、検査として機能していない。

### 修正

一致の最小長を3にし、2文字一致は**漢字を含む場合だけ**認める。

```js
function hasKanji(value) {
  return /[一-龯]/.test(value);
}

function meaningOverlap(derivation, meaning) {
  const tail = normalize(String(derivation).split(/(?:→|->)/).at(-1));
  const source = normalize(meaning);
  for (let length = Math.min(6, source.length); length >= 2; length -= 1) {
    for (let start = 0; start + length <= source.length; start += 1) {
      const slice = source.slice(start, start + length);
      if (length < 3 && !hasKanji(slice)) continue;
      if (tail.includes(slice)) return true;
    }
  }
  return false;
}
```

### 検証済みの結果

現行3件は全て通り、偽陽性は落ちる。

| 語 | 一致した部分 | 判定 |
| --- | --- | --- |
| `equivocate` | 言葉を濁 | 通過 |
| `evocative` | 喚起する | 通過 |
| `liaison` | 連絡 | 通過（2件のmeaning両方） |
| 偽陽性「適当 → した」 | した | **落ちる** |

段階1以降でこの検査に落ちた語は、`derivation` を書き直すか、B型・C型へ落とす。

## D. 仲間語1語の扱い（計画側を直す）

現状 `voc` は2語なので、各カードの仲間語は1語。[WORD_ORIGIN_PLAN.md](WORD_ORIGIN_PLAN.md) には「2語以下は語根バッチ完了まで保留」と書いたが、**実装（1語でも出す）を正とし、計画の記述を撤回する**。

理由: パネルの主役は語根そのものの説明（「語根「voc」＝呼ぶ・声（ラテン語 vocare）」）で、仲間語は例示。実際に `equivocate` ⇔ `evocative` は相互に有効に見えている。0語で非表示という現在の挙動は維持する。

- `WORD_ORIGIN_PLAN.md` の「仲間語は手書きしない」節と「リスク」表の該当行を、**0語なら非表示・1語以上で表示**に書き換える。
- コードは変更しない。

## E. 仲間語の大文字表示を単語向けに戻す

`.particleSiblings strong` の `text-transform: uppercase`（mono）を継承し、仲間語が `EVOCATIVE` と表示される。見出し語は小文字セリフなので、同じカード内で同じ語の表記が割れる（`DESIGN.md` の一貫性・反復に反する）。

```css
.wordOriginPanel .particleSiblings strong { text-transform: none; }
```

熟語側（`EAT UP` 等）は現状維持。修正後、`equivocate` カードで `evocative` と小文字表示になることを確認する。

## F. 375pxのチップ連結

現在は `.originChipJoin { flex-basis: 100%; height: 0; overflow: hidden; }` で強制改行し、「+」を消している。結果、チップ3枚が縦積みかつ連結記号なしになり、合成ではなく箇条書きに見える。

方針は次のどちらかを選ぶ（**推奨は1**）。

1. **「+」を残して縦積みにする**: `height: 0` をやめ、`flex-basis: 100%` のまま「+」を行間に中央寄せで表示する。合成であることが見た目に残る。
2. 2枚/行に折り返す: `.originChip { flex: 1 1 calc(50% - 6px) }` にして「+」を保持。3枚目が単独行になる。

決めた側を `DESIGN.md`（B）に書く。375pxで横溢れが出ないことを再確認する（現状 `scrollWidth === clientWidth === 375`）。

## G. 死にルールの削除

`item.etymology` 分岐を削除したので `styles.css:928` の `.flashEtym` は未使用。削除する。`flashRow(..., "flashEtym")` の呼び出しが残っていないことを `grep` で確認してから消す。

## H. UI検査のCSSアサーションを効かせる

現在の2行は実質チェックになっていない。

- `css.includes(".originChip")` は `.originChips` にも一致する。
- `/\.originChip\s*\{[\s\S]*flex-wrap:\s*wrap/` は `[\s\S]*` が無制限なので、**後続の別ルール**の `flex-wrap` でも成立する。

規則ブロックを取り出してから中身を見る形にする。

```js
function cssRule(source, selector) {
  const pattern = new RegExp(`${selector.replace(/[.*+?^${}()|[\]\]/g, "\$&")}\s*\{([^}]*)\}`);
  const matched = source.match(pattern);
  assert.ok(matched, `CSSに ${selector} の規則が必要です`);
  return matched[1];
}

assert.match(cssRule(css, ".originChip"), /flex-wrap:\s*wrap/, "語源チップは折り返せる必要があります");
assert.match(cssRule(css, ".originChipKind"), /width:\s*100%/, "種別ラベルは1行を占める必要があります");
```

セレクタ存在確認も `includes` ではなく `cssRule()` 経由にして、`.originChips` と `.originChip` を区別する。Eで追加する `.wordOriginPanel .particleSiblings strong` も同じ形で検査する。

## 1. 手順

1. C・H（検査の強化）を先に入れ、`npm test` が通ることを確認する。**検査を強くしてから中身を直す**ことで、後続の修正が検査に守られる。
2. E・F・G（CSS）を入れる。
3. B（README / DESIGN）とD（計画の記述）を更新する。
4. A（キャッシュバスター）を最後に上げる。配信物の変更が確定してから上げるため。
5. `npm test`。
6. 実ブラウザで `equivocate` カードを1枚だけ確認する: 仲間語が小文字、375pxで「+」が見える、意味直下の順序が変わっていない、コンソールエラー0。
7. 1コミットにまとめる（段階0の仕上げとして扱う）。コミット後に `graft build` でグラフを更新する。

## 2. 合格条件

- `npm test` が通る。C適用後も現行3語が通り、偽陽性の例が落ちること（上表のとおり）。
- `index.html` の `?v=` が両方上がっている。
- `DESIGN.md` に単語の語源表示の規則があり、実装（意味直下・チップ・導出行・パネル・480px挙動）と一致している。
- `equivocate` カードで仲間語が `evocative`（小文字）と表示される。
- 熟語カードの表示が変わっていない。

## 3. 非目標

- 語源データの追加（段階1＝頻出語根20＋接辞15の辞書確定は本計画の外）。
- `pooledData` の読み込みタイミングの作り替え。現状ホーム経由でしかセッションに入れないため実害がなく、直すなら別件として扱う。
- 熟語側の `.particleSiblings` の表記変更。
