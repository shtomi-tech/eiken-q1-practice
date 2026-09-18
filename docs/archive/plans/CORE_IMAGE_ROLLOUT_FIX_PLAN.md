# 核心イメージ全セット展開 修正計画

対象: `static/mode-q1.js` / `data/vocab_1_2025-2.json` / `data/particle_images.json` / `scripts/check-core-image-data.cjs`
関連: [CORE_IMAGE_ROLLOUT_PLAN.md](CORE_IMAGE_ROLLOUT_PLAN.md)（展開計画）
状態: 未着手。展開自体は**作業ツリーに未コミットで存在**（`npm test` は全項目 OK だが、テストが検出できない不具合が複数ある）

## 0. 現状の判定

`npm test` は通るが、**テストの網が粗く実害を検出できていない**箇所が4件ある。重大度順に並べる。

| # | 症状 | 重大度 |
| --- | --- | --- |
| A | 仲間例のスロット選択式が、プール件数が3の倍数のとき離れたスロット同士で完全に同じ3件を返す（「変化をつけたい」という当初の目的そのものに反する） | 致命 |
| B | `vocab_1_2025-2.json` の16件全件で連鎖が未完成。最終要素が意味ではなく方向語だけになっている | 致命 |
| C | `particleSense: "general"` が意味の向きが逆の熟語を同じ仲間例に束ねている。加えて `out` だけで16 sense に細分化され、1件しか参照しない sense が8つある | 高 |
| D | `coreImage.meaning` という未使用フィールドが265件中186件に残存。Bを覆い隠す形にもなっている | 低 |

## 1. A: スロット選択式の衝突バグ

### 症状

`static/mode-q1.js` の `flashCoreImage()` にある

```js
const visibleSiblings = filteredSiblings.length <= 3
  ? filteredSiblings
  : [0, 1, 2].map((k) => filteredSiblings[(slot * 3 + k) % filteredSiblings.length]);
```

は、プール件数が3の倍数（実データでは主に6件）のとき、周期が `poolSize / gcd(3, poolSize)` に縮まる。プール6件なら周期2、つまり**3件おきに同じ表示へ戻る**。

実例（`vocab_1_2026-1.json`、`up/general` プール6件）:

```
turn up  slot=0 → wake up, open up, speak up
trump up slot=1 → light up, warm up, stand up
clam up  slot=2 → wake up, open up, speak up   ← turn up と完全一致
```

`data/vocab_*.json` を機械的に走査したところ、**6ファイル・15箇所**で同型の衝突を確認した（`vocab_1_2025-2` `vocab_1_2026-1` `vocab_1_mock-2` `vocab_1_mock-3` `vocab_1_mock-4` `vocab_p2_mock-1`）。既存の検査（同一 sense を `n` 件が参照するならプールは `min(3+(n-1),6)` 件以上）はプールの**最小件数**しか見ておらず、この衝突を検出できない。

さらに、`loadPooledItems()`（間隔復習・意味練習で使う級内プール）は**級内の全セットを結合してから** `assignParticleSlots()` を呼ぶため、`loadData()`（通常学習・セット単位）よりスロットの累積カウントが大きくなり、衝突の危険がむしろ高い。現在のチェックはセット単位（`loadData` 相当）でしか見ていない。

### 修正

ステップ幅を3から1へ変える。

```js
const visibleSiblings = filteredSiblings.length <= 3
  ? filteredSiblings
  : [0, 1, 2].map((k) => filteredSiblings[(slot + k) % filteredSiblings.length]);
```

ステップ1は任意のプール件数と互いに素（`gcd(1, n) = 1`）なので、**周期は必ずプール件数と同じになる**。プール6件なら6スロット目まで重複しない（実データの最大出現数は5件なので実質衝突しない）。隣接スロットは3件中2件を共有するが、これは「完全一致」より明確に良い状態であり、既存のプール件数下限（3〜6件）を変えずに解決できる。

### 検査の追加（`scripts/check-core-image-data.cjs`）

現在の「最小件数」チェックに加えて、**実際の選択アルゴリズムをシミュレートして重複が無いことを直接検証**する。

1. `loadData()` 相当: ファイル単位で `assignParticleSlots` と同じ順序（words→idioms）でスロットを振り、同一 (`particle`, `particleSense`) を参照する熟語について、自己除外後のプールから選ばれる3件の組が全スロットで異なることを確認する。
2. `loadPooledItems()` 相当: `data/manifest.json` の `q1` から級ごとにセットをグルーピングし、**級内の配信対象セットをmanifest順に結合したうえで**同じシミュレーションを行う。通常学習では衝突しなくても間隔復習では衝突する、という抜けを防ぐ。

## 2. B: `vocab_1_2025-2.json` の連鎖を作り直す

16件全てが次の形になっている（`buckle down` の例）。

```json
"coreImage": {
  "particle": "down",
  "chain": [
    { "term": "buckle", "gloss": "締め具を締める" },
    { "gloss": "下へ" }
  ],
  "meaning": "本腰を入れて取り組む"
}
```

`flashCoreImage()` は `core.chain` しか読まないため、暗記カードには「buckle（締め具を締める）→ 下へ」という**意味の分からない連鎖**が表示される。実際の意味は誰も読まない `coreImage.meaning` に入っている。

対象16件: `pony up` `buckle down` `foul up` `cast down` `breeze in` `branch off` `crack down` `lop off` `dwell on` `reel off` `rustle up` `haul off` `fritter away` `rip off` `sound off` `crop up`

他14ファイルは同型の欠落が無く（`chain` の最終要素が実際の意味と整合する2〜5段になっている）、このファイルだけ生成過程で連鎖の後半が欠落したとみられる。**全16件を、他ファイルと同じ水準（構成語→中間の派生義→中心義）で作り直す。**

作業手順は [CORE_IMAGE_ROLLOUT_PLAN.md](CORE_IMAGE_ROLLOUT_PLAN.md) 4章と同じ。`particleSense` の割り当ては3章の見直し後に行う（`pony up` `foul up` `rustle up` `crop up` は現在 `up/general` を参照しており、3章の再編対象と重なる）。

## 3. C: `particleSense` の再編

### 症状

**用法の向きが逆の熟語が同じ束に入っている。**

```
up/general（6件の仲間例を共有）
  own up  = 白状する、認める   （表に出す方向）
  hush up = もみ消す、黙らせる （隠す方向・正反対）
```

**`general` への丸投げが常態化している。** `particleSense` を持つ熟語のうち、`general` の使用数（左）と全体（右）:

```
up:  general 19 / complete 2 / raise 8 / approach 1
off: general 13 / separate 6 / pull-away 3 / weaken 5
on:  general 6 / contact 6 / rely 4
out: general 8 / social 1 / escape 1 / spread 1 / withhold 1 / exhaust 2 /
     avoid 1 / remove 6 / reserve 3 / resolve 2 / scatter 2 / sound 1 /
     delegate 2 / withdraw 1 / react 1 / produce 3
```

**逆に `out` は16 senseに細分化されすぎている。** うち8つは参照する熟語が1件しかなく、その1件は常に同じ3件しか表示できない（sense分割の効果が出ない）。`escape` と `avoid`（どちらも「〜から逃れる」）、`spread` と `scatter`（どちらも「広がる」）は語義が重なり、`get out of` は `escape` と `avoid` の両方の仲間例プールに入っている。

### 方針

1. **`general` を全滅させる**。`up` 19件・`off` 13件・`on` 6件・`out` 8件（Bで作り直す4件を含む）について、各熟語の連鎖の最終 gloss を根拠に、既存 sense に収まるものは既存へ、収まらないものだけ新規 sense を作る。対象熟語と連鎖末尾の一覧は次のとおり（Bの4件は除く）。

   | particle | 熟語 | 連鎖末（現行） |
   | --- | --- | --- |
   | up | own up / hush up / turn up / trump up / clam up / keyed up / lap up / coop up / squared up / catch up / give up / make up my mind / pick up / set up | 表に出して認める／表面に出ないように収める／上向きに現れる・高める／表に持ち上げて作り上げる／口を閉じて黙る／興奮して、高揚して／喜んで受け入れる、がつがつ食べる／閉じ込める／勘定を清算した、対峙した／上の位置まで追いつく／手放してあきらめる／考えを組み上げて決める／上へ拾い上げる／上向きに整えて準備する |
   | off | branch off / reel off / haul off / rip off / sound off / choke off / polish off / played off / stave off / went off / show off / lay off / see it off | 離れて／離れて／離れて／離れて／外へ／流れを切って止める／残りを離して片付ける／対立させた、うまく利用した／食い止める、避ける／離れた状態へ動き出す／外へ出して目立たせる／仕事から離して置く／離れていく相手を見送る |
   | on | dwell on / drone on / frowned on / passed on / feed on / go on a voyage | 接して／そのまま続く／快く思わなかった、認めなかった／次の相手へ伝え渡す／対象に接して栄養を得る／旅を続ける流れに乗る |
   | out | dole out / mete out / punching out / watch out for / point out / fill it out / carry out | 外へ少しずつ配る／外へ与える／殴り倒す、退勤打刻する／外へ意識を向けて警戒する／外へ示して見えるようにする／外へ内容を出して書き上げる／外へ運び出して実行する |

   `go on a voyage` は動詞＋不変化詞というより「動詞＋前置詞句（voyageが目的語）」に近く、A型として無理に割らずB型（連鎖のみ・`particle`無し）へ落とすことも検討する。

2. **`out` の既存15 sense を統合する。** 具体的には
   - `escape` と `avoid`（`get out of` `back out of` を共有）を1つに統合し、ラベルは「重荷・状況から逃れる」に寄せる
   - `spread` と `scatter`（`spread out` を共有）を統合するか、「広げて示す（他動詞的）」と「自然に広がる（自動詞的）」の違いが明確なら維持して重複phraseだけ解消する
   - 残り6つの単発 sense（`avoid` `escape` `social` `sound` `withdraw` `react` `withhold` のうち上記統合で減らせないもの）は、統合できるかを個別に判断する。統合できないものは残してよいが、**単発 sense のまま新規に増やさない**ことを今後のルールにする（4章に反映）。

3. **完了条件**: `particleSense: "general"` が全ファイルに1件も残らないこと。`out` の sense 数は10前後まで圧縮されていること（目安。無理な統合はしない）。

### 検査の追加

- `particleSense` に `"general"` を許可しない（`assert.notEqual`）。
- 同一 particle 内で、異なる sense の siblings に同じ phrase が重複する場合、**その phrase を参照する熟語自身の particleSense と一致する sense 側にのみ許可**する（教材としての例示的重複は許容しつつ、無関係な重複の増殖は防ぐ）。

## 4. D: `coreImage.meaning` の除去

265件中186件に、UIが読まない `coreImage.meaning`（`item.meaning` と同一値）が残っている。BやCの修正時に併せて削除する。修正対象外のファイルも含め、**全件から一括削除**する（値の突合はスクリプトで機械的に行える。`coreImage.meaning !== item.meaning` の食い違いが無いことを削除前に確認する）。

`scripts/check-core-image-data.cjs` に、`coreImage` オブジェクトが `chain` / `particle` / `particleSense` / `note` / `siblings` 以外のキーを持たないことを検査するチェックを追加し、再発を防ぐ。

## 5. 対象外・参考記録

- `vocab_2026-1.json` の熟語 `"bring out in"` は `phrase` 自体が誤り（設問の `collocation`「bring out the best in」から巻き込まれたとみられる、**このセッションの変更ではなく既存データの不具合**）。`coreImage` はこの誤った `phrase` に対して付与されている。今回のスコープでは修正しない。別途フラグを立てて報告する。

## 6. 実施順序

1. A（コード1箇所＋検査2種）→ 単独コミット。他の修正より先に入れる（B・Cのデータ作業がこの上に乗るため）。
2. B（`vocab_1_2025-2.json` 全16件作り直し）＋ D（同ファイルの `coreImage.meaning` 除去）→ 単独コミット。
3. C（sense再編、up/off/on/outの`general`解消＋`out`のsense統合）→ 対象ファイルすべてに影響するため単独コミット。D（残り全ファイルの `coreImage.meaning` 除去）を同時に行う。
4. `npm test` 通過を各コミットで確認。C完了後、1章の表を再実行して衝突ゼロを確認。
5. 3コミットまとめて公開してよいか、順次公開するかは実施時に判断する（データのみの変更なのでロールバックは容易）。

## 7. 検証

- `npm test`（新規検査含め全項目 OK）
- 1章のスロット衝突シミュレーションをセット単位・級プール単位の両方で再実行し、重複ゼロを確認
- `vocab_1_2025-2.json` の16件を全て表示シミュレーションし、連鎖の最終要素が実際の意味と整合することを目視確認
- `particleSense: "general"` の grep が0件であることを確認
- 実ブラウザ（公開後）: 2級2026年度第1回の第22問付近など、Cで再編した熟語を通しで確認
