# 単語語源 段階5 バッチ5（`dis-` / `di-`）実装計画

対象: `data/word_roots.json` / `data/word_origins.json` / `data/word_origin_excluded.json` / `data/lemmas.json`
関連: [WORD_ORIGIN_PHASE5_IMPL_PLAN.md](WORD_ORIGIN_PHASE5_IMPL_PLAN.md)（バッチ0＝仕組み）/ [WORD_ORIGIN_PHASE5_BATCH4_PLAN.md](WORD_ORIGIN_PHASE5_BATCH4_PLAN.md)（バッチ4）/ [WORD_ORIGIN_AUTHORING.md](WORD_ORIGIN_AUTHORING.md)（作成基準）
前提: バッチ4＝`a71e667`（語根97個・A型215語・B型36語・単発語根52個・カバー率21.2%）
状態: 完了（2026-08-25）。A型13語・B型4語・C型1語を追加し、語根108個・A型228語・B型40語・単発語根62個

## 0. 対象

バッチ4で `con-`/`com-` をまとめたのと同じ理由で、**`di-` を `dis-` と同じバッチにする**（同じ接頭辞の異形。`dis-` は母音・有声音の前で `di-` になる）。

- `dis-` 未判定16語
- `di-` 未判定のうち `dis` で始まらない4語（`diagram` `dilapidate` `diminutive` `divulgence`）

計20語。見込みはA型13語、B型4語、C型1語、対象外2語。**新しい語根が11個**増える。

## 1. 先に片付ける3つの前提作業

判定より先に、データ側の整合を取る必要がある。

### 1-1. `divulgence` を除外記録から外す

`data/word_origin_excluded.json` の `gen` グループに「vulgare（公にする）由来で、genusの語根ではない」として記録済み。**この判断は `gen` 語根の候補としては正しい**が、今回 `vulg`（vulgus＝大衆）という語根で採用するため、**除外記録から削除する**。残したままA型を足すと検査（C型一覧の語にoriginsを付けてはいけない）で落ちる。

### 1-2. `disparities` の原形を足す

`data/lemmas.json` に `disparities → disparity` のマッピングが無く、原形が複数形のままになる。`positions → position` と同じ扱いで1行足し、`word_origins.json` のキーは `disparity` にする。

### 1-3. `dissipate` は既存 `sip` と綴りが衝突する

`dissipate` は dis＋supare（投げ散らす）で、既存語根 `sip`＝sapere（味わう）とは**別語源**。同じ綴りを語根に当てられないため、**C型として記録する**（`sip` グループ）。

## 2. 一次判定案（要確認）

### A型（既存語根を使う）

| 語 | 分解案 | 語根 |
| --- | --- | --- |
| `discreetly` | dis(離れて)＋cre＋-ly | **既存 `cre`**（バッチ1・cernere） |
| `discretion` | dis(離れて)＋cre＋-ion | 同上 |

バッチ1の予告どおり、`cre` がここで3語（`indiscretion` を含む）になる。

### A型（新しい語根を足す）

| 語 | 分解案 | 新語根 | `note` に書く別語 |
| --- | --- | --- | --- |
| `discrimination` | dis(離れて)＋crimin＋-ation | `crimin`＝ふるい分ける・罪（crimen） | crime / incriminate |
| `disparity` | dis(否定)＋par＋-ity | `par`＝等しい（par） | parity / compare |
| `dispirit` | dis(離れて)＋spir | `spir`＝息（spirare） | inspire / respiratory |
| `dissuade` | dis(離れて)＋suad | `suad`＝勧める（suadere） | persuade |
| `distinction` | dis(離れて)＋tinct＋-ion | `tinct`＝分ける・刺す（stinguere） | distinguish / extinct |
| `distortion` | dis(離れて)＋tort＋-ion | `tort`＝ねじる（torquere） | torture / retort |
| `distress` | dis(離れて)＋stress | `string`（variants `stress` `strict`）＝締める（stringere） | strict / restrict |
| `diagram` | dia(通して)＋gram | `gram`＝書かれたもの（ギリシャ語 gramma） | grammar / telegram |
| `dilapidate` | di(離れて)＋lapid＋-ate | `lapid`＝石（lapis） | lapidary |
| `diminutive` | di(離れて)＋minu＋-ive | `min`＝小さくする（minuere） | diminish / minimum |
| `divulgence` | di(広く)＋vulg＋-ence | `vulg`＝大衆（vulgus） | vulgar / divulge |

新しい接頭辞: **`dia`**（通して。ギリシャ語）。

### 注意が要る3語

- **`min` は段階1で見送った語根**（粗一致12語のうち真は `diminutive` 程度で、`abomination` `culmination` などは `-mination` の誤検出）。**今回は `diminutive` 1語に限って採用し、`note` に「-mination の一致は含めない」と明記する。**
- **`crimin` と `cre` は語源的には同族**（どちらも cernere に遡る）だが、綴りが離れているため別語根として扱う。`crimin` の `note` に「`cre`（ふるい分ける）と同系だが、綴りが違うので別に立てている」と書いておくと、後から統合を考える人が迷わない。
- **`tinct` の綴り**は `distinction` では `tinct`、`extinct` では `tinct`。`stinguere` の `s` は接頭辞に吸収されるため、語根キーは `tinct` にする。

### B型（分解を出さず由来一行）

| 語 | 理由 |
| --- | --- |
| `disembark` | bark（船）はフランス語経由で、embark が英語として自明 |
| `dishevel` | 古仏 chevel（髪）由来。語根がマイナーで、綴りも英語に残っていない |
| `dispatch` | イタリア語 dispacciare 由来で、ラテン語の語根に還元できない |
| `distraught` | `distract` の古い異形。`tract` の variants に `traught` を足すのは不自然 |

### C型（`word_origin_excluded.json` に記録）

| 語 | グループ | 記録する理由 |
| --- | --- | --- |
| `dissipate` | `sip` | supare（投げ散らす）由来で、sapere（味わう）の語根ではない |

### 対象外（記録しない）

`disappear`（appear が英語として自明）/ `dislodge`（lodge が英語として自明）。

## 3. 作業手順

1. **前提作業（1章）を先に行う。** `divulgence` を除外記録から削除、`lemmas.json` に `disparities → disparity` を追加。
2. `data/word_roots.json` に新語根11個と接頭辞 `dia` を足す。`origin` と `note`（同語根の別語1つ以上）は必須。
3. `data/word_origins.json` にA型13語・B型4語を追加する。`gloss` は16文字以内・`meaning` の部分文字列。
4. `dissipate` を `word_origin_excluded.json` の `sip` グループに追記する。
5. `npm test`。`single-word roots` が52→62前後になることを確認する。
6. ブラウザで2枚見る。`discretion`（`cre` の仲間語に `indiscretion` `discreetly` が出る）と、単発語根のカード（例: `distortion`）。375px幅も確認する。
7. 1コミット。`index.html` の `?v=` は上げない（データのみの変更）。

## 4. 合格条件

- A型13語前後・B型4語が入り、`npm test` が通る。
- `divulgence` が除外記録から消え、A型として登録されている（両方に存在すると検査が落ちる）。
- カードの見出しが `disparity`（単数形）で出る。
- `min` の `note` に「-mination の一致は含めない」がある。
- `discretion` のカードで `cre` の仲間語が2語出る。
- 既存251語の表示が変わらない。
