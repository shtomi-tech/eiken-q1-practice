# 単語語源 段階5 バッチ3（`de-`）実装計画

対象: `data/word_roots.json` / `data/word_origins.json` / `data/word_origin_excluded.json`
関連: [WORD_ORIGIN_PHASE5_IMPL_PLAN.md](WORD_ORIGIN_PHASE5_IMPL_PLAN.md)（バッチ0＝仕組み）/ [WORD_ORIGIN_PHASE5_BATCH2_PLAN.md](WORD_ORIGIN_PHASE5_BATCH2_PLAN.md)（バッチ2）/ [WORD_ORIGIN_AUTHORING.md](WORD_ORIGIN_AUTHORING.md)（作成基準）
前提: バッチ2＝`5d0075d`（語根71個・A型180語・B型31語・単発語根34個）
状態: 完了（2026-08-25）。A型15語・B型2語・C型1語を追加し、語根84個・A型195語・B型33語・単発語根45個

## 0. 対象

`python scripts/build_word_origin_stub.py --prefix de` が出す**未判定21語**（判定済み `desertification` は除外済み）。

見込みはA型15語、B型2語、C型1語、対象外3語。**新しい語根が13個**増える。終了時点でA型195語前後、カバー率19%台になる。

このバッチは**候補に対するA型の歩留まりが最も低い**（21語中15語、うち3語は英語の複合語で最初から捨てる）。件数を追わず、`deadline` `deadlock` のような語を無理に拾わないこと。

## 1. 一次判定案（要確認）

### A型

| 語 | 分解案 | 語根 | `note` に書く別語 |
| --- | --- | --- | --- |
| `deflect` | de(離れて)＋flect | **既存 `flect`**（バッチ2で作成済み） | reflect（登録済み） |
| `definition` | de(完全に)＋fin＋-ion | `fin`＝境界・終わり（finis） | define / infinite |
| `definitive` | de(完全に)＋fin＋-ive | 同上 | — |
| `dehydrate` | de(離れて)＋hydr＋-ate | `hydr`＝水（ギリシャ語 hydor） | hydrogen / hydrant |
| `delusion` | de(離れて)＋lus＋-ion | `lud`（variants `lus`）＝遊ぶ・だます（ludere） | illusion / elude |
| `democracy` | dem＋-cracy | `dem`＝民衆（ギリシャ語 demos） | epidemic / demographic |
| `deprecate` | de(離れて)＋prec＋-ate | `prec`＝祈る・願う（precari） | pray / precarious |
| `depreciate` | de(下へ)＋preci＋-ate | `preci`＝値段・価値（pretium） | price / appreciate |
| `descendant` | de(下へ)＋scend＋-ant | `scend`＝登る（scandere） | ascend / transcend |
| `deterrent` | de(離れて)＋terr＋-ent | `terr`＝怖がらせる（terrere） | terror / terrify |
| `detonate` | de(強意)＋ton＋-ate | `ton`＝雷鳴（tonare） | astonish / thunder |
| `devious` | de(離れて)＋vi＋-ous | `vi`＝道（via） | obvious / previous |
| `devoutly` | de(完全に)＋vout＋-ly | `vot`（variants `vout`）＝誓う（vovere） | devotion / vote |
| `decorate` | decor＋-ate | `decor`＝飾り（decus / decorare） | decoration / decorum |
| `debilitate` | de(離れて)＋bil＋-ate | `bil`＝力（bilis）**要確認** | debility |

新しい接尾辞: **`-cracy`**（〜による支配。ギリシャ語 kratos）。`democracy` の後半は語根が2つ重なる語なので、後半を接尾辞として登録して1語根に収める。

### 注意が要る4語

- **`decorate` の `de` は接頭辞ではない**。decus/decorare の語幹の一部で、スタブが綴りで拾っただけ。`parts` に `de` を入れない（バッチ2の `reptile` と同じ扱い）。
- **`terr` は「怖がらせる」（terrere）**。`terra`（土地）とは別語源で、収録済みの `extraterrestrial` は terra 側なので**この語根に含めない**。`note` に明記する。
- **`prec`（祈る・precari）と `preci`（価値・pretium）は綴りが近い別語根**。両方の `note` に相互の注意を書く。同じバッチで入るので混ざりやすい。
- **`debilitate`** は bilis（力）の確認が取れなければB型（「力を奪うことから」）に落とす。

### B型（分解を出さず由来一行）

| 語 | 理由 |
| --- | --- |
| `demeanor` | minare（追い立てる）由来。語根がマイナーで中心義に結び付けにくい |
| `deteriorate` | deterior（より悪い）自体が語幹で、`de` は接頭辞ではない。分解して見せる利点が薄い |

### C型（`word_origin_excluded.json` に記録）

| 語 | グループ | 記録する理由 |
| --- | --- | --- |
| `delectable` | `lect` | delectare（楽しませる）由来で、legere（集める・読む）の語根ではない |

### 対象外（記録しない）

`deadline` `deadlock` `debrief`。いずれも英語の複合語で、語源の説明を付ける対象ではない。

## 2. 仲間語の見通し

このバッチで2語になる語根は `fin`（definition / definitive）と `flect`（reflect / deflect）だけで、**残る11語根は単発のまま**。単発語根は32→43前後に増えるが、語根総数の8割という歯止めには達しない。

`hydr` `dem` `ton` などは、収録語彙に他の語が無いことを確認済み（`hydration` `epidemic` `astonish` はいずれも未収録）。**アプリ外の語を `note` に書くことで語根の実在を示す**という段階5の方針どおりに扱う。

## 3. 作業手順

1. `data/word_roots.json` に新語根13個と接尾辞 `-cracy` を足す。`origin`（原形）と `note`（同語根の別語1つ以上）は必須。
2. `data/word_origins.json` にA型15語・B型2語を追加する。`gloss` は16文字以内・`meaning` の部分文字列。
3. `delectable` を `word_origin_excluded.json` の `lect` グループに追記する。
4. `npm test`。`single-word roots` が34→43前後になることを確認する。
5. ブラウザで2枚見る。`deflect`（`flect` の仲間語に `reflect` が出る）と、単発語根のカード（例: `detonate`）。375px幅も確認する。
6. 1コミット。`index.html` の `?v=` は上げない（データのみの変更）。

## 4. 合格条件

- A型15語前後・B型2語が入り、`npm test` が通る。
- `decorate` の `parts` に接頭辞 `de` が入っていない。
- `terr` の `note` に「terra（土地）由来の語は含めない」がある。
- `deflect` のカードで `reflect` が仲間語として出る。
- 既存211語の表示が変わらない。
