# 単語語源 段階5 バッチ1（`in-`）実装計画

対象: `data/word_roots.json` / `data/word_origins.json` / `data/word_origin_excluded.json`
関連: [WORD_ORIGIN_PHASE5_IMPL_PLAN.md](WORD_ORIGIN_PHASE5_IMPL_PLAN.md)（バッチ0＝仕組み）/ [WORD_ORIGIN_AUTHORING.md](WORD_ORIGIN_AUTHORING.md)（作成基準）
前提: バッチ0＝`db15433`（単発語根の解禁・`--prefix`・除外データの外部化）
状態: 未着手

## 0. 対象

`python scripts/build_word_origin_stub.py --prefix in` が出す**未判定36語**（判定済み5語は候補から除外済み）。

見込みはA型24〜28語、B型6〜8語、対象外3〜5語、C型1〜2語。**新しい語根が20個前後**増える。

## 1. 一次判定案（要確認）

**この表は綴りと意味からの一次案であり、確定ではない。** 1語ずつ語源を確認し、原形（ラテン語・ギリシャ語）が取れないものはB型か対象外へ落とす。

### A型（新しい語根を足す）

| 語 | 分解案 | 新語根 | 語根の `note` に書く別語 |
| --- | --- | --- | --- |
| `incarcerate` | in(中へ)＋carcer＋-ate | `carcer`＝牢屋（carcer） | incarceration |
| `inclement` | in(否定)＋clem＋-ent | `clem`＝穏やか（clemens） | **clemency**（収録済み） |
| `incompetent` | in(否定)＋com＋pet＋-ent | `pet`＝求める（petere） | appetite / compete |
| `incumbent` | in(上に)＋cumb＋-ent | `cumb`＝横たわる（cumbere） | succumb |
| `indictment` | in(に対して)＋dict＋-ment | `dic`/`dict`＝言う（dicere） | dictionary / verdict |
| `indiscretion` | in(否定)＋dis＋cre＋-ion | `cre`＝ふるい分ける（cernere） | **discretion / discreetly**（収録済み） |
| `indolence` | in(否定)＋dol＋-ence | `dol`＝痛む（dolere） | condolence |
| `infallible` | in(否定)＋fall＋-ible | `fall`＝だます（fallere） | fallacy / false |
| `influence` | in(中へ)＋flu＋-ence | `flu`＝流れる（fluere） | **fluctuate**（収録済み）/ fluent |
| `infraction` | in＋fract＋-ion | `fract`（variants: `fring`）＝壊す（frangere） | fragment / fragile |
| `infringe` | in＋fring | 同上 | — |
| `ingredient` | in(中へ)＋gred＋-ent | **既存 `gress` に variants `gred` を追加** | progress / gradual |
| `innately` | in(中へ)＋nat＋-ly | `nat`＝生まれる（nasci） | native / nation |
| `international` | inter(間の)＋nat＋-al | 同上 | — |
| `innocently` | in(否定)＋noc＋-ly | `noc`＝害する（nocere） | innocuous / obnoxious |
| `innovation` | in＋nov＋-ation | `nov`＝新しい（novus） | novel / renovate |
| `insignia` | in＋sign | `sign`＝印（signum） | **assignment / consignment**（収録済み） |
| `insipid` | in(否定)＋sip | `sip`＝味わう（sapere） | savory / sapient |
| `interact` | inter(間で)＋act | `act`＝行う（agere） | action / agent |
| `intrepid` | in(否定)＋trep＋-id | `trep`＝おののく（trepidus） | trepidation |
| `intricate` | in＋tric＋-ate | `tric`＝もつれ（tricae） | extricate |
| `intrigue` | in＋tric（intricare） | 同上 | — |
| `invader` | in(中へ)＋vad＋-er | `vad`＝行く（vadere） | **evade**（収録済み）/ invasion |
| `investigation` | in＋vestig＋-ation | `vestig`＝足跡（vestigium） | **vestige**（収録済み） |
| `invigorate` | in(中へ)＋vigor＋-ate | `vigor`＝活力（vigor） | vigorous |

**後続バッチで仲間語が増える語根**（表の太字）: `clem` `cre` `flu` `sign` `vad` `vestig`。バッチ1の時点では単発でも、`dis-` `con-` `ex-` のバッチで2語以上になる。**先に語根を作っておくこと**で後から辞書を触らずに済む。

必要な接辞の追加: **`inter`（prefix・間の／相互に）**。`intra` はあるが `inter` が未登録。

### B型（分解を出さず由来一行）

| 語 | 理由 |
| --- | --- |
| `infiltrate` | filter が英語として自明。「こし器を通す」由来を一行で足りる |
| `insinuate` | sinus（曲がり・懐）がマイナーで、中心義に結び付けにくい |
| `insolent` | solere（慣れる）が `sol`（solvere/solus/solidus）と綴りで衝突する。語根にしない |
| `insulate` | insula（島）。`sul` を語根に切り出すと不自然。「島のように切り離す」の一行で足りる |
| `internal` | inter＋-al で語根が無い |
| `increase` | crescere（育つ）。`creas` の切り出しが不自然 |
| `infatuated` | fatuus（愚か）。A型でもよいが、迷ったらB型（基準どおり） |
| `indebted` | debt が英語として自明 |

### 対象外（記録しない）

`interact` を除く `intern` 系の複合語 `internship`、`incompetent` 以外で語根が取れない一般語 `increase`（B型に回すなら不要）など、**英語の複合語・自明語**。表に挙げた語以外は記録を残さない。

### C型（`word_origin_excluded.json` に記録）

| 語 | 記録する理由 |
| --- | --- |
| `intravenous` | `ven`: vena（静脈）由来で、venire（来る）の語根ではない |

`intravenous` は現在どこにも記録が無く、`ven` の候補として再浮上する。今回記録する。

## 2. 作業手順

1. `data/word_roots.json` に新語根20個前後と接頭辞 `inter` を足す。各語根に `origin`（原形）と `note`（同語根の別語1つ以上）を必ず書く。
2. `data/word_origins.json` にA型を追加する。`gloss` は16文字以内・`meaning` の部分文字列。
3. B型を `derivation` のみで追加する。
4. C型を `data/word_origin_excluded.json` の該当語根グループに追記する。
5. `npm test`。`word origin roots: N roots / M single-word roots` の M が20前後に増えることを確認する。
6. ブラウザで2枚見る。**仲間語0のカード**（例: `incarcerate`）と、**仲間語ありのカード**（例: `international`＝`nat` が2語）。375px幅も確認する。
7. 1コミット。`index.html` の `?v=` は**上げない**（データのみの変更で、JS・CSSは変わらないため）。

## 3. 注意点

- **単発語根が一気に20個増える**。バッチ0で入れたログ（`single-word roots`）が0→20前後になる。段階5計画の歯止め（語根総数の8割超で見直し）に達しないことを、この時点で確認する。
- `nat` は段階1で「粗一致17語のほとんどが `-ation` の誤検出」として見送った語根。**今回は `innately` と `international` の2語に限って採用する**。`abomination` `assassination` などを後から混ぜない旨を `note` に書く。
- `dic`/`dict` は段階3でも見送った語根だが、`indictment` を足すと後続バッチ（`pre-` の `prediction` など）で伸びる可能性がある。variants に `dict` を入れておく。
- `fract`/`fring` のように**同じ語根の綴り違いを variants にまとめる**こと。別語根として2エントリ作らない（検査が重複で落ちる）。

## 4. 合格条件

- A型24語前後・B型8語前後が入り、`npm test` が通る。
- 新語根すべてに `origin` と、別の英単語を挙げた `note` がある。
- 仲間語0のカードで、語根パネルが見出し＋noteだけで出る。
- 既存154語の表示が変わらない。
