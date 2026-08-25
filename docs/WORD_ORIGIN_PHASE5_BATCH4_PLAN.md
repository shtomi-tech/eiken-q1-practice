# 単語語源 段階5 バッチ4（`con-` / `com-`）実装計画

対象: `data/word_roots.json` / `data/word_origins.json` / `data/word_origin_excluded.json`
関連: [WORD_ORIGIN_PHASE5_IMPL_PLAN.md](WORD_ORIGIN_PHASE5_IMPL_PLAN.md)（バッチ0＝仕組み）/ [WORD_ORIGIN_PHASE5_BATCH3_PLAN.md](WORD_ORIGIN_PHASE5_BATCH3_PLAN.md)（バッチ3）/ [WORD_ORIGIN_AUTHORING.md](WORD_ORIGIN_AUTHORING.md)（作成基準）
前提: バッチ3（語根84個・A型195語・B型33語・単発語根45個）
状態: 完了（2026-08-25）。A型20語・B型3語を追加し、語根97個・A型215語・B型36語・単発語根52個

## 0. 対象と、計画からの変更

**`com-` の8語を、段階6から前倒ししてこのバッチに含める。** 段階5の実装計画では `con-`（バッチ4）と `com-`（段階6）を分けていたが、両者は同じ接頭辞の異形で、`con`/`com` の意味の当て方を1バッチで揃えたほうがよい（接頭辞単位でバッチを切った本来の理由）。分けると、同じ「ともに・完全に」を別々の回で判断することになる。

- `con-` 未判定15語（判定済み `convergence` は除外済み）
- `com-` 未判定8語

計23語。見込みはA型20語、B型3語。**新しい語根が13個**増え、終了時点でA型215語前後、カバー率20%台に乗る。

## 1. このバッチの特徴: 既存語根が育つ

これまでのバッチと違い、**既存語根に2語目以降が入る語が6つ**ある。単発語根の比率を下げる回になる。

| 語 | 既存語根 | 対応 |
| --- | --- | --- |
| `conjecture` | `ject`（バッチ2） | そのまま使える |
| `consignment` | `sign`（バッチ1） | そのまま使える（バッチ1の予告どおり） |
| `consensual` | `sent`（バッチ2） | **variants に `sens` を追加**（バッチ2の申し送り） |
| `contiguous` | `tang` | **variants に `tig` を追加** |
| `continuously` | `ten`（バッチ2） | **variants に `tin` を追加** |
| `compress` | `prim`（バッチ2） | **variants に `press` を追加** |

**新語根として二重登録しないこと。** 特に `sens` `tin` `press` は独立した語根に見えるので注意する。

## 2. 一次判定案（要確認）

### A型（新しい語根を足す）

| 語 | 分解案 | 新語根 | `note` に書く別語 |
| --- | --- | --- | --- |
| `conciliate` | con(ともに)＋cili＋-ate | `cili`＝呼び集める（concilium） | council / reconcile |
| `concussion` | con(強く)＋cuss＋-ion | `cuss`＝揺さぶる（quatere） | percussion / discuss |
| `condense` | con(完全に)＋dens | `dens`＝濃い（densus） | density / dense |
| `conservation` | con(完全に)＋serv＋-ation | `serv`＝保つ（servare） | preserve / reserve |
| `conserve` | con(完全に)＋serv | 同上 | — |
| `consolidate` | con(完全に)＋solid＋-ate | `solid`＝固い（solidus） | solid / solidify |
| `constellation` | con(ともに)＋stell＋-ation | `stell`＝星（stella） | stellar / interstellar |
| `contrite` | con(完全に)＋trit＋-ite | `trit`＝すりつぶす（terere） | attrition / detriment |
| `contempt` | con(強く)＋temp | `temp`＝軽んじる（temnere）**要確認** | contemptuous |
| `commendable` | com(ともに)＋mend | `mand`（variants `mend`）＝委ねる（mandare） | command / demand |
| `commission` | com(ともに)＋miss＋-ion | `mit`（variants `miss`）＝送る（mittere） | **emission / omit**（収録済み） |
| `commuter` | com(ともに)＋mut＋-er | `mut`＝変える（mutare） | mutation / mutual |
| `completed` | com(完全に)＋plet | `ple`（variants `plet`）＝満たす（plere） | **implement**（収録済み）/ supplement |
| `compliant` | com(ともに)＋pli＋-ant | `plic`（variants `pli` `ply`）＝折る（plicare） | **perplex**（収録済み）/ complicate |

### A型（既存語根を使う）

`conjecture`（ject）/ `consignment`（sign）/ `consensual`（sent＋sens）/ `contiguous`（tang＋tig）/ `continuously`（ten＋tin）/ `compress`（prim＋press）

### 注意が要る2語

- **`contempt` の `temp` は temnere（軽んじる）**で、`tempus`（時間）とは別語源。段階1で `temp` を語根候補から外したのは、`temperature` `tempest` `attempt` がすべて別語源だったため。**この綴りを語根にするなら、`note` に「tempus（時間）由来の語は含めない」を必ず書く**。原形の確認が取れなければB型に落とす。
- **`compress` の `prim`** は premere（押す）。バッチ2で `reprimand` 用に作った語根で、`primus`（第一）とは別という注意書きが既にある。variants に `press` を足すときも、その注意を消さないこと。

### B型（分解を出さず由来一行）

| 語 | 理由 |
| --- | --- |
| `connoisseur` | フランス語 connaître（知る）由来だが、綴りに語根が現れない |
| `complaint` | plangere（打つ・嘆く）由来。語根がマイナーで、`plaint` を切り出しても中心義に結び付かない |
| `compound` | componere 由来だが、綴りが `pon`/`pos` と一致しない。既存 `pos` に不自然な variants を足さない |

### C型・対象外

このバッチでは**なし**。`convergence` は既に記録済み。

## 3. 作業手順

1. `data/word_roots.json` に新語根13個を足す。`origin`（原形）と `note`（同語根の別語1つ以上）は必須。
2. **既存語根4つに variants を足す**（`sent`＋`sens`、`tang`＋`tig`、`ten`＋`tin`、`prim`＋`press`）。新語根として作らない。
3. `data/word_origins.json` にA型20語・B型3語を追加する。`gloss` は16文字以内・`meaning` の部分文字列。
4. `npm test`。`single-word roots` の増え方が45→52前後に**とどまる**ことを確認する（既存語根が育つ回のため）。
5. ブラウザで2枚見る。`consignment`（`sign` の仲間語に `insignia` が出る）と、`consolidate`（単発語根 `solid`）。375px幅も確認する。
6. 1コミット。`index.html` の `?v=` は上げない（データのみの変更）。

## 4. 合格条件

- A型20語前後・B型3語が入り、`npm test` が通る。
- `sens` `tin` `press` `tig` が**独立した語根として登録されていない**（variants として入っている）。
- `temp` を採用した場合、`note` に「tempus（時間）由来の語は含めない」がある。
- `consignment` のカードで `insignia` が仲間語として出る。
- 既存251語の表示が変わらない。
