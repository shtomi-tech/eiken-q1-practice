# 単語カードに語源（接辞＋語根）を出す計画

対象: `data/word_roots.json`（新規）/ `data/word_origins.json`（新規）/ `static/mode-q1.js` / `static/styles.css` / `scripts/` / `.github/workflows/pages.yml`
関連: [CORE_IMAGE_PLAN.md](CORE_IMAGE_PLAN.md)（熟語版の導入）/ [CORE_IMAGE_AUTHORING.md](CORE_IMAGE_AUTHORING.md)（熟語版の作成基準）
状態: 実装済み（段階0、2026-08-24、未コミット）

熟語カードの「核心イメージ」（連鎖＋不変化詞パネル）と同じ構造を、単語カードに **接辞＋語根チップ＋導出行＋同語根の仲間語パネル** として実装する。表示位置は**意味の直下**（熟語カードと同じ）。導入は**頻出語根から段階的**に行い、全語カバーは目標にしない。

## 0. 前提（確認済みの実数）

- 単語カードの描画は `static/mode-q1.js` の `buildFlashCard`（2209行〜）。`coreImage` があれば `flashCoreImage`、無ければ `item.etymology` を1行表示する分岐が既にある（2237行）。**`etymology` を持つ単語データは0件**＝現状はデッドパス。
- `coreImage` の付与対象は熟語のみ（691行で `type === "idiom"` を判定し仲間例のローテーション枠 `_particleSlot` を割当）。
- 単語の見出しは `data/lemmas.json` で原形化して表示済み（2212行）。語源は**原形に紐づける**。
- 単語の総数: `data/vocab_*.json` 24ファイル・`words[]` 1232件、**原形ベースで1183語**（2セット以上に重複するのは48語）。
- `data/particle_images.json` と同じく、語源データは **表示専用**。進捗キー・音声パス・4択の選択肢生成には一切使わない。
- Pages配信は `.github/workflows/pages.yml` が**ファイル名を明示してコピー**している（54〜55行）。新規JSONは追記しないと本番で404になる。

### 規模の粗い見積り（未確認・上限として扱う）

主要なラテン／ギリシャ語根の候補約110個を1183語に**部分文字列一致**させると320語（27%）がヒットする。ただし `several`→`ver`、`alternate`→`nat` のような偽陽性を多く含むため、**実際にA型として成立するのは150〜250語程度**と見込む。この数字は執筆時に確定させる（計画の合格条件にはしない）。

## 1. データ設計

### `data/word_roots.json`（語根・接辞の辞書。`particle_images.json` の単語版）

```json
{
  "meta": { "note": "単語カードの語源パネル用。表示のみ。進捗キー・音声・選択肢には使わない。" },
  "roots": {
    "duct": { "gloss": "導く", "origin": "ラテン語 ducere", "note": "引いて連れて行くイメージ", "variants": ["duc"] },
    "voc":  { "gloss": "呼ぶ・声", "origin": "ラテン語 vocare", "variants": ["vok"] }
  },
  "affixes": {
    "pro":  { "gloss": "前へ", "kind": "prefix" },
    "equi": { "gloss": "等しい", "kind": "prefix" },
    "ate":  { "gloss": "〜にする（動詞化）", "kind": "suffix" }
  }
}
```

- `variants` は綴りゆれ（`duc`/`duct`、`spec`/`spic`）。**仲間語の逆引きはこの `variants` を含めて行う**。
- 接辞は語根ほど教育効果が高くないため、**`roots` に従属する脇役**として扱う（接辞だけのパネルは出さない）。

### `data/word_origins.json`（原形キーの分解表）

```json
{
  "meta": { "note": "キー = data/lemmas.json 適用後の原形（小文字）。表示のみ。" },
  "origins": {
    "equivocate": {
      "type": "A",
      "root": "voc",
      "parts": [
        { "form": "equi", "kind": "prefix", "gloss": "等しい" },
        { "form": "voc",  "kind": "root",   "gloss": "呼ぶ・声" },
        { "form": "ate",  "kind": "suffix", "gloss": "〜にする" }
      ],
      "derivation": "どちらとも等しく聞こえる声を出す → 言葉を濁す"
    },
    "liaison": {
      "type": "B",
      "derivation": "フランス語 lier（結ぶ）から。人と人を結ぶ役 → 連絡役"
    }
  }
}
```

- `parts` がチップ列、`derivation` が「◯◯ → 中心義」の1行。**`derivation` の末尾は `vocab_*.json` の `meaning` の中心義とそろえる**（熟語の `chain` 末尾と同じ規約）。
- `vocab_*.json` には**書かない**。同じ語が複数セットに出るため、中央ファイルで一元管理する。
- 既存の `item.etymology` フィールドは使わない（B型は `derivation` に統合し、2237行の分岐から `etymology` を外す）。

### 仲間語は手書きしない

熟語版は `siblings` を手書きしているが、単語版は **`root`（＋`variants`）の逆引きをUI側で組み立てる**。

- 起動時に `word_origins.json` から `root → 原形[]` の索引を作る。表示時に**現在のデータセットに含まれる語**を優先し、無ければ全体から補う。
- 訳は `vocab_*.json` の `meaning` から引く（追加執筆ゼロ）。
- 表示は最大3語。3語を超える場合は既存 `_particleSlot` と同じローテーション（2275行）を共通関数化して使い、カードごとに違う仲間語を見せる。
- **語根辞書にエントリがある語は、仲間語が0語でもパネルを出す**（見出しとnoteだけを表示する）。語根辞書にない場合はパネルを出さない。仲間語が1語以上あれば、語根の説明に続けて最大3語を表示する。

## 2. UI（`mode-q1.js` / `styles.css`）

- `flashWordOrigin(item)` を追加し、`buildFlashCard` の2237行を差し替える。
  - `item.type === "word"` かつ原形が `word_origins.json` にある → `flashWordOrigin`
  - `item.type === "idiom"` かつ `coreImage` あり → 既存 `flashCoreImage`
  - どちらでもない → 何も出さない（`etymology` 分岐は削除）
- 挿入位置は `inner.appendChild(flashRow("意味", ...))` の直後＝**意味の直下**、例文の前。
- 見出しは「語源・なりたち」。
- チップ（`.originChip`）は `form`（英字・大きめ）＋ `gloss`（日本語・小さめ）の2段、`+` 区切りで横並び、`flex-wrap` で折返し。`kind` で背景を変えつつ、**色だけに頼らず** `prefix`/`root`/`suffix` を `aria-label` と視覚ラベルで示す。
- 導出行（`.originDerivation`）はチップの下に区切り線を挟んで1行。
- 仲間語パネルは既存 `.particlePanel`（`styles.css` 979行〜）のCSSを流用し、見出しを「語根「duct」＝導く（ラテン語）」の形にする。
- B型は `derivation` の1行のみ（チップ・パネルなし）。
- 狭い幅でチップが2行になっても崩れないことをモバイル幅で確認する。

## 3. 執筆基準（A/B/C）

`docs/WORD_ORIGIN_AUTHORING.md` を新規作成し、熟語版と同じ思想で正本とする。

| 型 | 判定 | 付けるもの | 例 |
| --- | --- | --- | --- |
| A | 接辞＋語根に分解でき、現代の意味が導ける | `parts` ＋ `root` ＋ `derivation`（仲間語パネルあり） | `equivocate` `produce` `intrepid` |
| B | 由来話は有効だが分解は効かない（借用語・比喩由来） | `derivation` のみ | `liaison` `graft` |
| C | 分解がこじつけになる／ゲルマン系の不透明語 | **何も付けない**＋`cReasons` に理由1行 | `thwart` `balk` |

やってはいけないこと（検査では拾いきれない部分）:

- **民間語源**: 綴りが似ているだけの語を同じ語根に入れない（`several` を `ver`(真実) に入れない）。
- **循環**: `parts[].gloss` に単語の訳をそのまま書かない。構成要素は構成要素自身の意味を書く。
- **件数の消化を目的にしない**。迷ったらCにして理由を書く。

## 4. 検査（`npm test` に追加）

`scripts/check-word-origin-data.cjs`

- `origins` のキーが `lemmas.json` 適用後の原形集合に存在する（タイポ・活用形混入の検知）。
- `parts[].form` が原形の綴りに実際に含まれる（`voc` ⊂ `equivocate`）。`variants` も許容。
- A型は `parts` に `kind: "root"` を1つ以上持ち、`root` が `word_roots.json` の `roots` に存在し、`parts` にも現れる。
- `derivation` は必須・非空。末尾が対応する `meaning` の中心義と語を共有する（緩い一致。落ちたら人が確認）。
- C型は `cReasons` に理由必須。`cReasons` にある語へ `origins` を付けたら落とす（熟語版と同じ双方向の縛り）。
- `word_roots.json` / `word_origins.json` が `pages.yml` の `cp` 行に載っていること。

`scripts/check-word-origin-ui.cjs`

- `flashWordOrigin` が意味行の直後に挿入されていること。
- 語源データが**進捗キー・音声パス・選択肢生成に流れ込んでいない**こと（`word_origins`/`wordOrigin` を参照する関数が `surfaceOf` 経由の進捗系・`buildVocabAudioButton`・選択肢生成に現れない）。

## 5. 段階導入

**バッチ境界は「問題セット」ではなく「語根」**にする。語根単位で入れれば、その語根の仲間語パネルがそのバッチで完成する。

| 段階 | 内容 | 成果物 |
| --- | --- | --- |
| 0 | 仕組み一式（loader・`flashWordOrigin`・CSS・検査2本・`pages.yml`）＋パイロット3語 | 空に近い `word_origins.json` でも本番が壊れないこと |
| 1 | **頻出語根20個＋接辞15個の辞書を確定**（`word_roots.json` のみ） | 語根の訳・由来・`variants` が固まる |
| 2〜 | 語根2〜3個ずつ＝1バッチ＝1コミット（1バッチ15〜30語） | A型データが語根単位で増える |
| 終 | 残ったB型の由来1行、C型の理由記録 | カバレッジの確定値を README に記録 |

段階1の語根選定は、`scripts/build_word_origin_stub.py`（読み取り専用・下記）が出す候補頻度で決める。粗い一致での上位は `ver / nat / ten / lat / pos / min / tin / par / sta / fer / cur / spec / val / ven / port / ple / vers / vert / duc / lect` だが、**偽陽性を人が落としてから確定**する。接辞は `in / re / de / con / dis / pro / ex / im / en / com / per / se / pre / ab / inter` が上位。

## 6. 生成補助（読み取り専用）

`scripts/build_word_origin_stub.py` を `build_core_image_stub.py` に倣って追加する。

- 全 `vocab_*.json` の `words[]` を原形化して集約し、`word_roots.json` の語根・`variants` に**部分文字列一致**する候補と、その語の `meaning` を並べて出力する。
- 語根の当てはめと `derivation` は**書かない**（民間語源を機械が量産するため）。人／LLMが確定させ、検査で縛る。
- `--root duct` で語根単位のバッチ用リストを出す。

## 7. 1バッチの手順

1. `python scripts/build_word_origin_stub.py --root <語根>` で候補を出す。
2. A/B/C を判定し、A型のみ `word_origins.json` に追記する。偽陽性はC（または対象外）として落とす。
3. `npm test` を通す。
4. ブラウザでそのバッチの単語カードを1枚開き、意味直下の表示・仲間語パネル・モバイル幅の折返しを確認する。
5. 1バッチ＝1コミット。辞書の追記が必要になったら同じコミットに含める。

## 8. 合格条件 / 非目標

合格条件:

- 語源データが無い単語のカードが、現在とまったく同じ見た目で動くこと。
- 語源データを消しても表示が消えるだけで、進捗・音声・出題が変わらないこと（ロールバックは `word_origins.json` を空にするだけ）。
- `npm test` が通ること。

非目標:

- 1183語すべてに語源を付けること。
- 学術的な語源記述。**中心義を思い出す助けになるかどうか**だけで採否を決める。

## 9. リスク

| リスク | 対策 |
| --- | --- |
| 民間語源の混入 | A/B/C分類と `cReasons`、綴り包含の機械検査、迷ったらC |
| 新規JSONが本番で404 | `pages.yml` への `cp` 追記を検査で強制 |
| 仲間語が少なく薄いパネルになる | 語根の説明を主役にし、語根辞書にエントリがあれば仲間語0語でも見出し＋noteを表示する |
| カードの情報過多 | チップ＋1行＋仲間語3語に上限を固定。例文より上に置くのは語源まで |
