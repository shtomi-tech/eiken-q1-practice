# 単語語源 段階5 バッチ6（`ex-` / `e-`）実装計画

対象: `data/word_roots.json` / `data/word_origins.json` / `data/word_origin_excluded.json`
関連: [WORD_ORIGIN_PHASE5_IMPL_PLAN.md](WORD_ORIGIN_PHASE5_IMPL_PLAN.md)（バッチ0＝仕組み）/ [WORD_ORIGIN_PHASE5_BATCH5_PLAN.md](WORD_ORIGIN_PHASE5_BATCH5_PLAN.md)（バッチ5）/ [WORD_ORIGIN_AUTHORING.md](WORD_ORIGIN_AUTHORING.md)（作成基準）
前提: バッチ5＝`d9a38ef`（語根108個・A型228語・B型40語・単発語根62個・カバー率22.7%）
状態: 未着手。**段階5の最終バッチ**

## 0. 対象

`ex-` の未判定13語に加え、**`e-`（＝ex- の異形）の語を選んで含める**。

ただし `--prefix e` は29語を返すが、その大半は**別の接頭辞**（`en-` `em-` `ec-` `ed-` `es-`）や接頭辞ではない語（`economic` `enigma` `echelon`）で、そのまま取り込んではいけない。**ex- 由来と確認できる次の6語だけを対象にする。**

`emanate` / `emission` / `elaborate` / `enumerate` / `enervating` / `esteem`

`enchant` `encrypt` `enrapture` `enroll` `entail` などの `en-`（中へ）は段階6の `en-` バッチで扱う。`eccentric`（ギリシャ語 ek＋kentron）は接頭辞が別系統なので、同じく段階6に回す。

計19語。見込みはA型14語、B型3語、C型1語、対象外1語。**新しい語根が11個**増える。

## 1. 一次判定案（要確認）

### A型（既存語根を使う）

| 語 | 分解案 | 語根 |
| --- | --- | --- |
| `emission` | e(外へ)＋miss＋-ion | **既存 `mit`**（variants `miss`・バッチ4） |
| `extraterrestrial` | extra(外の)＋terr＋-al | **`terr` は使えない**（下記の注意を参照） |

`extraterrestrial` の `terr` は **terra（土地）** で、バッチ3で作った `terr`＝terrere（怖がらせる）とは別語源。**新語根 `terra`＝土地（terra）を別キーで立てる**（note: territory / terrain）。バッチ3で `terr` の note に「terra 由来の語は含めない」と書いた約束をここで守る。接頭辞 `extra` も新規に追加する。

### A型（新しい語根を足す）

| 語 | 分解案 | 新語根 | `note` に書く別語 |
| --- | --- | --- | --- |
| `exasperate` | ex(強意)＋asper＋-ate | `asper`＝粗い（asper） | asperity / exasperation |
| `excruciating` | ex(強意)＋cruc | `cruc`＝十字架（crux） | crucial / crucify |
| `exemplary` | ex(外へ)＋empl | `empl`＝取り出す（emere＝買う・取る） | example / exemplify |
| `expedite` | ex(外へ)＋ped＋-ite | `ped`＝足（pes） | pedal / pedestrian |
| `expenditure` | ex(外へ)＋pend＋-ture | `pend`（variants `pens`）＝量る・吊るす（pendere） | pending / suspend |
| `expenses` | ex(外へ)＋pens | 同上 | — |
| `expensive` | ex(外へ)＋pens＋-ive | 同上 | — |
| `explosion` | ex(外へ)＋plos＋-ion | `plaud`（variants `plos` `plaus`）＝打つ・拍手する（plaudere） | applaud / plausible |
| `expropriate` | ex(外へ)＋propri＋-ate | `propri`＝自分のもの（proprius） | property / appropriate |
| `extraneous` | extra(外の)＋ne＋-ous | **`extra` を接頭辞として扱い、語根は立てない**（下記） |
| `exuberant` | ex(強意)＋uber＋-ant | `uber`＝豊か・乳房（uber） | exuberance |
| `emanate` | e(外へ)＋man＋-ate | `man`＝流れる（manare） | emanation |
| `elaborate` | e(外へ)＋labor＋-ate | `labor`＝働く（labor） | laborious / collaborate |
| `enumerate` | e(外へ)＋numer＋-ate | `numer`＝数（numerus） | numeral / innumerable |
| `enervating` | e(離れて)＋nerv | `nerv`＝筋・神経（nervus） | nerve / nervous |
| `esteem` | e(外へ)＋steem | `estim`（variants `steem`）＝評価する（aestimare） | estimate / estimation |

### 注意が要る4語

- **`extraterrestrial` の `terr`**（terra＝土地）は、バッチ3の `terr`（terrere＝怖がらせる）と**別語根**。キーが衝突するので `terra` を別に立て、両方の `note` に相互の注意を書く。**同じ語根に混ぜてはいけない**。
- **`extraneous`** は extra＋-aneus で、切り出せる語根が無い。`extra` を接頭辞として登録したうえで、**B型に落とすか、接頭辞＋接尾辞だけのA型にするかを判断する**。段階5の基準では語根が無い語はB型なので、**B型を既定とする**。
- **`emanate` の `man`** は manare（流れる）で、`manu`（手）とは別語源。段階3で `man`（手）を見送った経緯があるので、キー名を `man` にするなら note に「manu（手）由来の語は含めない」を必ず書く。
- **`expedite` の `ped`** は pes（足）。`pedantic` はギリシャ語 paidos（子ども）由来で別語源なので、note で除外する。

### B型（分解を出さず由来一行）

| 語 | 理由 |
| --- | --- |
| `extraneous` | extra＋-aneus で、独立した語根が取り出せない |
| `expound` | exponere 由来だが、綴りが `pos`/`pon` と一致しない（`compound` と同じ理由） |
| `escaped` | ex＋cappa（マント）由来。「マントを脱いで逃げる」は説明として遠い |

### C型（`word_origin_excluded.json` に記録）

| 語 | グループ | 記録する理由 |
| --- | --- | --- |
| `editor` | `dic` | dare（与える）由来の ex＋dare で、dicere（言う）の語根ではない |

### 対象外（記録しない）

`eccentric`（接頭辞が `ec-` でギリシャ語系。段階6の判断に回す）。

## 2. 作業手順

1. `data/word_roots.json` に新語根11個（`asper` `cruc` `empl` `ped` `pend` `plaud` `propri` `uber` `man` `labor` `numer` `nerv` `estim` `terra` のうち採用分）と接頭辞 `extra` を足す。`origin` と `note` は必須。
2. `terr`（terrere）の `note` に `terra` へのリンクを追記し、`terra` の `note` にも逆の注意を書く。
3. `data/word_origins.json` にA型14語・B型3語を追加する。`gloss` は16文字以内・`meaning` の部分文字列。
4. `editor` を `word_origin_excluded.json` の `dic` グループに追記する。
5. `npm test`。`single-word roots` が62→70前後になることを確認する（`pend` が3語入るので増え方は緩む）。
6. ブラウザで2枚見る。`expenses`（`pend` の仲間語に `expenditure` `expensive` が出る）と `extraterrestrial`（単発語根 `terra`）。375px幅も確認する。
7. 1コミット。`index.html` の `?v=` は上げない（データのみの変更）。

## 3. 合格条件

- A型14語前後・B型3語が入り、`npm test` が通る。
- `terra`（土地）と `terr`（怖がらせる）が別語根として存在し、双方の `note` に相互の注意がある。
- `extraterrestrial` の語根が `terra` になっている。
- `expenses` のカードで `pend` の仲間語が2語出る。
- 既存268語の表示が変わらない。

## 4. 段階5の締め

このバッチで段階5（接頭辞バッチ）は完了する。終了時点の見込みは**語根120個前後・A型242語前後・カバー率24%前後**。

締めとして次を行う。

- `README.md` の件数を更新する。
- `WORD_ORIGIN_PHASE5_PLAN.md` の状態を「完了」にし、**実績（当初見込みA型225語・21%に対する実測）**を1行残す。
- 段階6（`en-` `im-` `pro-` `per-` `pre-` `co-` `ac-` と接尾辞のみの215語）に進むかどうかは、実績を見てから判断する。
