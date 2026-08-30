# 熟語の「核心イメージ」表示 実装計画

対象: `static/mode-q1.js`（STEP 1 暗記カード / 意味チェックのフィードバック）/ `static/styles.css` / 新規 `data/particle_images.json` / `data/vocab_1_mock-1.json`
状態: 未着手
スコープ: **①UI＋データ構造の実装＋1セット分の手書き**（全熟語のデータ整備・生成スクリプトは対象外）

## 0. 目的

熟語は現在、単語と同じ暗記カード（`buildFlashCard()` [mode-q1.js:2192](../static/mode-q1.js)）で「意味 → 語源・なりたち → 例文」を出すだけで、実際には `idioms[]` に `etymology` がほとんど無く、**意味の丸暗記になっている**。

単語の `etymology`（語源・なりたち）に相当する枠を熟語にも用意し、

```
hold（しっかり保持する）＋ up（完全に）→ 完全に止める → 遅らせる
```

という**動詞＋不変化詞から意味へ至る連鎖**と、**不変化詞の共通イメージ**（up＝完全に・空っぽに・いっぱいに / eat up・use up・fill up）を示す。

## 1. データ設計

### 1-1. 熟語エントリの任意フィールド `coreImage`

`data/vocab_*.json` の `idioms[]` に追加する。**任意フィールド**とし、無い熟語は現状のまま表示する。

```json
{
  "q": 22,
  "is_answer": false,
  "meaning": "持ち越す",
  "example": "The unused budget is carrying over to the next quarter.",
  "exampleTranslation": "未使用の予算は次の四半期へ持ち越される。",
  "pos": "熟語",
  "phrase": "carrying over",
  "coreImage": {
    "chain": [
      { "term": "carry", "gloss": "運ぶ" },
      { "term": "over",  "gloss": "越えて" },
      { "gloss": "境目を越えて運ぶ" },
      { "gloss": "持ち越す" }
    ],
    "particle": "over"
  }
}
```

| キー | 必須 | 内容 |
| --- | --- | --- |
| `chain` | ○ | 2〜5要素。`term` 付きの要素は構成語（**原形**で書く）、`term` 無しは導出された意味。最後の要素の `gloss` はその熟語の `meaning` の中心義とそろえる |
| `particle` | 任意 | `data/particle_images.json` のキー。省略時は下段パネルを出さない |
| `note` | 任意 | 連鎖だけで足りないときの1〜2文の補足 |

- `phrase` は活用形（`carrying over`）や文頭大文字（`Snap out of`）で入っているが、**`chain[].term` は原形・小文字**で書く。`phrase` 自体は書き換えない（進捗キー `itemKeyOf()` と音声パスの元になるため。[LEMMA_HEADWORD_PLAN.md](LEMMA_HEADWORD_PLAN.md) と同じ理由）。
- `particle` は `phrase` の末尾語から導出**しない**。`Snap out of` の核は `out`、`Stand up to` の核は `up to` のように末尾語と一致しないため、データに明示する。

### 1-2. `data/particle_images.json`（新規・不変化詞の共有辞書）

不変化詞の共通イメージは熟語ごとに書くと重複するため、正本を1つに分離する。

```json
{
  "meta": { "note": "熟語カードの核心イメージ下段パネル用。表示のみ。進捗キー・音声・選択肢には使わない。" },
  "particles": {
    "up": {
      "core": "完全に・空っぽに・いっぱいに",
      "note": "ある状態にして完了させるイメージ",
      "siblings": [
        { "phrase": "eat up",  "gloss": "食べ尽くす" },
        { "phrase": "use up",  "gloss": "使い切る" },
        { "phrase": "fill up", "gloss": "満たす" }
      ]
    }
  }
}
```

- `siblings` は2〜4件。多いほど良いわけではなく、**カードの縦が伸びる**ので3件を基準にする。
- 本計画で書くのは `vocab_1_mock-1.json` の16熟語が参照する範囲のみ（`up` / `out` / `off` / `on` / `over` / `down` / `away` / `up to` の想定）。

## 2. UI

### 2-1. 暗記カード（`buildFlashCard()`）

意味行の直下、単語の「語源・なりたち」と同じ位置に置く。

```js
inner.appendChild(flashRow("意味", item.meaning, "flashMeaning"));
if (item.coreImage) inner.appendChild(flashCoreImage(item));   // 熟語
else if (item.etymology) inner.appendChild(flashRow("語源・なりたち", item.etymology, "flashEtym"));
if (item.example) inner.appendChild(flashExampleRow(item));
```

`flashCoreImage(item)` が返す構造（既存 `.flashRow` の枠内に収める）:

```
.flashRow
  strong           「核心イメージ」（既存 flashRow の mono ラベル体裁を踏襲）
  ol.coreChain
    li.coreChainStep  ├ .coreChainTerm  hold      （term があるときだけ）
                      └ .coreChainGloss しっかり保持する
    …
  p.coreChainResult   hold up（遅らせる）
  p.coreChainNote     note があるときだけ
  details.particlePanel（particle があるときだけ）
    summary          「"up" のイメージは共通」
    p.particleCore   完全に・空っぽに・いっぱいに ／ note
    ul.particleSiblings  eat up 食べ尽くす / use up 使い切る / fill up 満たす
```

- 連鎖の矢印は `li + li::before` の CSS 装飾（`aria-hidden` 相当。テキストとして持たない）。`<ol>` なので読み上げ順は「hold → up → 完全に止める → 遅らせる」で自然に通る。
- `<details>` は既定で閉じる。開閉トグルは min-height 44px（DESIGN.md「44px以上のタップターゲットを死守」）。
- 写真のようなアイコン（🔒 STOP ⏰）は**この段階では入れない**。テキストだけで成立する構造を先に確定し、アイコンは後から任意フィールドで足せる形にしておく。

### 2-2. 意味チェックのフィードバック（`appendCheckFeedback()` [mode-q1.js:2586](../static/mode-q1.js)）

現在は `item.etymology` を1行出している。熟語で `coreImage` があるときは、`chain` の各 `gloss` を `→` で連結した**1行版**を同じ位置に出す（フル図はカードだけ。フィードバックは再接触が目的なので図は出さない）。

```
しっかり保持する → 完全に → 完全に止める → 遅らせる
```

### 2-3. 読み込み（`boot()` [mode-q1.js:2902](../static/mode-q1.js)）

`data/lemmas.json` と同じ方式で `data/particle_images.json` を1回 fetch し、`particleMap` に入れる。**失敗しても落とさない**（catch して空オブジェクト。ファイルが無くても連鎖部分は従来通り表示される）。

### 2-4. CSS（`static/styles.css`、`.flashEtym` の隣）

DESIGN.md の既存トークンのみを使う。**新色・新影は足さない**。

| 要素 | 指定 |
| --- | --- |
| `.coreChain` | `display:grid; grid-auto-flow:column; gap:8px; align-items:stretch`。480px 未満で `grid-auto-flow:row` に切替え、矢印も下向きに |
| `.coreChainStep` | Parchment 地＋hairline 枠＋角丸 md（DESIGN.md「タブ／グリッドタイル」規範） |
| `.coreChainTerm` | 英字なので `--sans`、太字、16px |
| `.coreChainGloss` | 13px、`--muted` |
| 矢印 | `--muted` の `→`（縦積み時は `↓`）を疑似要素で |
| `.coreChainResult` | Ink 地＋Parchment 文字・角丸 md（DESIGN.md「強調タイル」の縮小版）。結論であることを面で示す |
| `.particlePanel` | hairline の上罫のみ。`summary` は mono ラベル体裁 |
| `.particleSiblings` | `display:flex; flex-wrap:wrap; gap:12px`。各項目は角丸 pill のチップにしない（語数が多く読みにくいため、phrase を太字＋gloss を `--muted` の2段） |

アニメーションは追加しない（`<details>` の既定開閉のみ）。

## 3. データ作成範囲（この計画で書く分）

`data/vocab_1_mock-1.json` の熟語 **16件**（第22〜25問）に `coreImage` を付ける。

| 問 | 熟語 | 想定 particle |
| --- | --- | --- |
| 22 | carrying over / cracking down / hanging out / wasting away | over / down / out / away |
| 23 | Snap out of / Act up to / Hold out on / Stand up to | out / up to / out / up to |
| 24 | lay out / drum up / settle on / seal off | out / up / on / off |
| 25 | bargained on / bought off / eked out / soaked up | on / off / out / up |

- 語義の根拠は既存の `meaning` と `example` を第一とし、連鎖が無理筋になる熟語（比喩の飛躍が大きく、こじつけになるもの）は**`coreImage` を付けない**。任意フィールドなので欠けていても壊れない。全16件を埋めることを目的にしない。
- 迷ったものは `coreImage` を付けずに残し、報告で列挙する（AGENTS.md「不確かな語義・解釈は断定せず、要確認として扱う」）。

## 4. 検証

`package.json` の `test` に追加する新規スクリプト2本:

### `scripts/check-core-image-data.cjs`
- `data/vocab_*.json` 全件を走査し、`coreImage` があるエントリについて
  - `chain` は配列で2〜5要素、各要素に `gloss`（非空文字列）がある
  - `chain` の最後の要素に `term` が無い（＝導出結果で終わる）
  - `particle` があるとき、`data/particle_images.json` の `particles` にキーが存在する
  - `particle` の各語が `phrase` を小文字化したトークン列に含まれる
  - `chain[].term` が `phrase` の語と無関係でないこと（原形先頭3文字の一致で緩く確認。活用形があるため厳密一致にしない）
- `particle_images.json` 側は `core` 必須、`siblings` は1〜4件で `phrase`/`gloss` 必須

### `scripts/check-core-image-ui.cjs`
- `check-unit-learning-ui.cjs` と同じ `extractFunctionBody()` 方式で
  - `buildFlashCard` が `coreImage` 分岐を持ち、`etymology` 分岐より先に評価している
  - `flashCoreImage` が `<ol>` を使い、矢印文字を JS 側で生成していない
  - `appendCheckFeedback` が `coreImage` の1行版を出している
  - `styles.css` に `.coreChain` `.coreChainResult` `.particlePanel` と 480px 未満のメディアクエリ分岐が存在する

### 手動確認（実ブラウザ）
- 1級模試第1回 → 熟語を含む第22〜25問で暗記カードを開き、連鎖・結論・不変化詞パネルの表示、`<details>` 開閉、コンソールエラー無しを確認
- `coreImage` を持たない熟語（他セット）で従来表示のままであることを確認
- 幅 375px / 768px / 1280px で連鎖の折り返しを確認
- `data/particle_images.json` を一時的に 404 にして、連鎖だけは表示され落ちないことを確認

## 5. 影響範囲・非対象

- 進捗キー・localStorage・音声パス・4択の選択肢テキストは**一切変更しない**（`phrase` を触らないため）。
- 単語（`words[]`）の `etymology` の表示は変更しない。
- 生成スクリプト（`verb_images.json` を含む自動組み立て）、全570熟語のデータ整備、写真のキャラクター・吹き出し等の装飾は**このスコープ外**。
- 完了後に更新する文書: [README.md](../README.md)（対象データの節に `data/particle_images.json` を追記）、[DESIGN.md](../DESIGN.md)（コンポーネント規範に「核心イメージブロック」を1項追記）。
