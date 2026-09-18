# 不変化詞パネルを語義（sense）単位に割る計画

対象: `data/particle_images.json` / `data/vocab_1_mock-1.json` / `static/mode-q1.js` / `scripts/check-core-image-data.cjs`
状態: 未着手
前提: [CORE_IMAGE_PLAN.md](CORE_IMAGE_PLAN.md)（核心イメージの導入。実装・公開済み）

## 0. 問題

不変化詞パネルの仲間例が**不変化詞ごとに1組しかない**ため、同じセット内で同じ画面が繰り返される。`vocab_1_mock-1.json` の16件では `out` が5件あり、5枚とも `find out / carry out / leave out` が出る。

さらに問題なのは、その5件は `out` の語義自体が異なることである。

| 熟語 | 連鎖中の `out` の語義 |
| --- | --- |
| hanging out | 外へ・こもらずに |
| Snap out of | 外へ |
| Hold out on | 外へ出したまま（＝出さずに留める） |
| lay out | 外へ広げる |
| eked out | 外へ・最後まで |

`Hold out on`（出さずに留める）のカードに `find out`（調べて分かる）が仲間例として出るのは、**変化が無いだけでなく説明として合っていない**。同じ状況は `up`（drum up＝上へ・盛り上げる / soaked up＝完全に）、`on`（settle on＝〜の上に / bargained on＝〜を前提に）、`off`、`up to` でも起きている。

→ 不変化詞を語義単位に割り、カードごとに**その用法の仲間**を出す。変化は結果として付く。

## 1. データ設計

### 1-1. `data/particle_images.json` に `senses` を追加

既存の `core` / `note` / `siblings` は残し、`senses` を任意で足す。

```json
"out": {
  "core": "外へ・外に出た状態へ",
  "note": "内側から離れ、状態の外へ出すイメージ",
  "senses": [
    {
      "id": "social",
      "label": "こもらずに外へ出る",
      "siblings": [
        { "phrase": "go out", "gloss": "出かける" },
        { "phrase": "eat out", "gloss": "外食する" },
        { "phrase": "ask out", "gloss": "誘う" },
        { "phrase": "stay out", "gloss": "外にいる" },
        { "phrase": "night out", "gloss": "夜の外出" }
      ]
    },
    { "id": "spread",   "label": "広げて全体に示す",     "siblings": [ … ] },
    { "id": "withhold", "label": "出さずに手元へ留める", "siblings": [ … ] },
    { "id": "exhaust",  "label": "最後まで出し切る",     "siblings": [ … ] }
  ]
}
```

| キー | 必須 | 内容 |
| --- | --- | --- |
| `senses[].id` | ○ | 熟語側から参照するキー。同一不変化詞内で一意 |
| `senses[].label` | ○ | パネル見出しに出す日本語の用法名 |
| `senses[].siblings` | ○ | **3〜6件**。表示は3件で、残りは 2-2 のオフセット用の余剰 |

- トップレベルの `siblings` は `senses` を持たない不変化詞のフォールバックとして残す（`over` `down` `away` は当面1用法のままでよい）。

### 1-2. 熟語側の `particleSense`

```json
"coreImage": {
  "chain": [ … ],
  "particle": "out",
  "particleSense": "withhold"
}
```

- 任意フィールド。無い場合はトップレベル `siblings`、それも無ければパネルを出さない（現行動作）。
- 割り当ては**連鎖中のその不変化詞の `gloss` と一致する用法**を選ぶ。連鎖と説明が食い違う状態を作らない。

### 1-3. 例外の上書き `coreImage.siblings`

辞書に収まらない熟語のために、`coreImage.siblings`（`phrase`/`gloss` の配列、1〜3件）を直接書けるようにし、**あれば辞書より優先**する。逃げ道が無いと辞書設計が窮屈になるため用意するが、常用しない。

## 2. 表示ロジック

### 2-1. 仲間例の解決順（`flashCoreImage()`）

1. `coreImage.siblings` があればそれ（例外上書き）
2. `particleSense` があり、辞書に該当 sense があればその `siblings`
3. どちらも無ければトップレベル `siblings`
4. 何も取れなければパネルを出さない

見出しは用法名を含める。

```
現行: 「out」のイメージは共通
変更: 「out」のイメージ：出さずに手元へ留める     ← sense があるとき
```

説明文（`.particleCore`）は sense があるとき `label` を主にし、不変化詞全体の `core` を副として続ける（`出さずに手元へ留める ／ 外へ・外に出た状態へ`）。用法が違っても**同じ不変化詞の一族である**ことは見せ続ける。

### 2-2. 決定的オフセットで3件を切り出す

同じ (`particle`, `particleSense`) の熟語が同じセットに複数あると、sense を割ってもまだ被る。プール（3〜6件）から次で3件を選ぶ。

```
表示 = pool[(slot * 3 + k) % pool.length]   （k = 0,1,2）
```

- `slot` は「**そのセットのデータ順で、同じ (particle, sense) が何番目に登場したか**」の連番。
- **セッションのシャッフル順ではなくデータ順**（`vocab_*.json` の `idioms[]` の並び）で振る。演習のたびに例が変わると記憶の手がかりが揺れるため、**同じカードは常に同じ3件**になることを保証する。
- 乱数は使わない（`Math.random()` は再現性を壊す）。
- 実装位置: データセット読み込み時（`loadDataset()` 付近、`_datasetId` を付けているのと同じ箇所）に `_particleSlot` を各熟語へ付与する。`_` 始まりの表示専用フィールドは既存慣習に合わせ、**保存も送信もしない**。
- `pool.length < 3` のときは持っている分だけ出す。

### 2-3. 自己除外

仲間例の `phrase` が、そのカードの熟語自身と一致する場合は飛ばす（`Stand up to` のカードに `stand up to` が出ていた件の恒久対策）。比較は小文字化し、`chain[].term` を連結した原形（`stand up to`）と `phrase` を小文字化したもの（`stand up to`）の両方に対して行う。除外後に3件を満たすため、切り出しは**除外後のプール**に対して行う。

## 3. データ作成範囲

`vocab_1_mock-1.json` の16件が使う不変化詞のみ。

| 不変化詞 | 割る用法 | 対象カード |
| --- | --- | --- |
| `out` | こもらずに外へ出る / 広げて全体に示す / 出さずに手元へ留める / 最後まで出し切る | hanging out・Snap out of / lay out / Hold out on / eked out |
| `up` | 完全に・し尽くす / 上へ・勢いを高める | soaked up / drum up |
| `up to` | 基準に達する / 相手に対して立つ | Act up to / Stand up to |
| `on` | 接触して上に載る | settle on |
| `on` | 前提として頼る | bargained on |
| `off` | 切り離す・遮断する | seal off |
| `off` | 引き離して手放させる | bought off |
| `over` `down` `away` | 分割しない（各1件のみ） | carrying over / cracking down / wasting away |

- 1 sense につき仲間例は**4〜5件**書く（表示3件＋オフセット用の余剰）。合計40〜55語程度。
- 仲間例は英検1級レベルに寄せすぎず、**用法のイメージが立つ平易な熟語**を選ぶ。
- 用法名が既存の連鎖の `gloss` と食い違う場合は、連鎖側ではなく用法名を実態に合わせる（連鎖は公開済みで学習者が見ている）。判断に迷うものは分割せず1用法のまま残し、報告する。

## 4. 後方互換

| 状態 | 挙動 |
| --- | --- |
| `senses` 無し・`particleSense` 無し | 現行どおりトップレベル `siblings` を表示 |
| `senses` あり・`particleSense` 無し | トップレベル `siblings` を表示（sense は使わない） |
| `particleSense` あり・辞書に該当 id 無し | トップレベル `siblings` にフォールバック。**画面は壊さない**（検査スクリプトで先に落とす） |
| `particle_images.json` 取得失敗 | 現行どおりパネル非表示、連鎖だけ表示 |

段階移行が可能なので、`out` から順に割っていける。

## 5. 検証

### `scripts/check-core-image-data.cjs` に追加
- `senses` があるとき: `id` が同一不変化詞内で一意、`label` 非空、`siblings` は3〜6件で `phrase`/`gloss` 必須
- `senses` と トップレベル `siblings` は**両方あってよい**（後者はフォールバック）が、どちらも無い不変化詞はエラー
- 熟語の `particleSense` があるとき、`particle` が指す辞書に同じ `id` の sense が存在する
- **仲間例に自分自身を含まない**: 各熟語について、解決される仲間例の `phrase`（小文字）が、その熟語の `phrase` および `chain[].term` 連結形と一致しないこと
- `coreImage.siblings`（例外上書き）があるとき: 1〜3件で `phrase`/`gloss` 必須

### `scripts/check-core-image-ui.cjs` に追加
- `flashCoreImage` が `particleSense` を参照し、解決順（上書き → sense → 既定）を持つ
- `Math.random` を含まない（決定的表示の担保）
- 見出しに用法名を出す分岐がある

### 手動確認（実ブラウザ）
- 第22〜25問を通しで見て、`out` の5枚が**それぞれ違う仲間例**になり、かつ各カードの連鎖の語義と一致していること
- 同じカードを2回開いて仲間例が変わらないこと（決定性）
- `particleSense` を持たない他セットの熟語が従来どおり表示されること
- 幅375px での折り返しとコンソールエラー無し

## 6. 影響範囲・非対象

- 進捗キー・localStorage・音声・4択の選択肢は変更しない。`_particleSlot` は実行時のみのフィールドで保存しない。
- 意味チェックのフィードバック（1行版）は変更しない。
- 他セット（570熟語）への `coreImage` 展開、生成スクリプトはこのスコープ外。
- 完了後: `DESIGN.md` の「熟語の核心イメージ」の項に用法名見出しを追記、`index.html` のキャッシュバスターを更新（`styles.css` を触った場合のみ CSS 側も）。
