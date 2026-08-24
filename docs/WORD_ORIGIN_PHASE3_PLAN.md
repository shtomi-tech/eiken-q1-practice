# 単語語源 段階3: 語根の第2波

対象: `data/word_roots.json` / `data/word_origins.json` / `scripts/check-word-origin-data.cjs`
関連: [WORD_ORIGIN_PHASE2_PLAN.md](WORD_ORIGIN_PHASE2_PLAN.md)（第1波の投入）/ [WORD_ORIGIN_PHASE2_FIX_PLAN.md](WORD_ORIGIN_PHASE2_FIX_PLAN.md)/ [WORD_ORIGIN_AUTHORING.md](WORD_ORIGIN_AUTHORING.md)（作成基準）
前提: 段階2＝`a649b42`（語根20個・A型94語・B型12語）
状態: 完了（2026-08-25）。13語根・A型42語・B型6語を追加し、段階3終了時点でA型136語・B型18語

## 0. 方針と、その根拠

段階2の8章に挙げた選択肢のうち、**1（語根を増やす）を主軸にする**。ただし収穫は段階2より明確に落ちる。先に数字を示す。

- 未登録の原形は**1077語**（全1183語中）。
- 未検討の語根候補約80グループを粗一致にかけ、目視で偽陽性を落とした結果、**A型として成立しそうなのは13語根・約50語**。
- 段階2は20語根で106語だったので、**1語根あたりの収穫は5.3語→3.8語に落ちる**。

2（借用語のB型を増やす）を単独で走らせない理由は、**対象の切れ目が無い**こと。B型は「由来を一行書けば成立する」ため、書こうと思えば1000語すべてに書けてしまい、件数消化が目的化する。代わりに、**語根バッチの中で拾った語に限ってB型を書く**という段階2の運用をそのまま続ける。

### 打ち切りの基準

段階3の後に段階4を作るかどうかは、次で判断する。

- 1語根あたりの真の候補が**3語を下回る**語根しか残らなくなったら、語根の拡張は終了する。
- そのときは、A型100〜150語という到達点を README に記録して、この機能は「完成」として扱う。全語カバーは最初から目標ではない（`WORD_ORIGIN_AUTHORING.md`）。

## 1. 追加する語根13個

| # | 語根 | `variants` | 意味 | 粗一致 | 精査後（見込み） | 代表語 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `fac` | `fect` `fic` | 作る・なす | 22 | 8 | defect / deficiency / superficial / faction |
| 2 | `her` | `hes` | くっつく | 13 | 5 | cohesive / hesitant / inherent / inheritance |
| 3 | `reg` | `rect` | まっすぐにする・支配する | 12 | 5 | direct / rectify / regime / deregulation |
| 4 | `nom` | `nym` | 名前 | 6 | 4 | anonymous / pseudonym / misnomer / nomination |
| 5 | `gen` | `gener` | 生む・種 | 8 | 4 | degenerate / generosity / congeniality |
| 6 | `sist` | `stit` `sta` | 立つ | 4 | 4 | consistent / substitute / destitute |
| 7 | `grat` | `grac` | 喜ばせる・感謝 | 4 | 3 | congratulate / gratify / graceful |
| 8 | `log` | `loqu` `locut` | 言葉・話す | 5 | 3 | colloquial / elocution / apologize |
| 9 | `val` | — | 強い・価値がある | 7 | 3 | value / convalescence / ambivalent |
| 10 | `vid` | `vis` | 見える | 6 | 3 | provision / proviso / visa |
| 11 | `cord` | — | 心 | 4 | 3 | cordial / cordially / discord |
| 12 | `tang` | `tact` | 触れる | 5 | 3 | tangible / intangible / contact |
| 13 | `cur` | `curr` | 走る | 8 | 3 | occur / incursion / curriculum |

合計の見込みは**約50語**。段階3を終えると **A型は約145語**（1183語の12%前後）になる。

### `vid` と `spec` の使い分け（説明が競合する）

どちらも「見る」で、カードに並ぶと違いが分からなくなる。辞書の `gloss` と `note` で書き分ける。

- `spec`＝**注意して見る・観察する**（perspective / suspicion / spectator）
- `vid`＝**視覚に入る・見える**（provision / visa）

## 2. 見送る候補と理由

粗一致の上位でも、真の該当語が2語以下、または偽陽性が多すぎるものは入れない。

| 候補 | 粗一致 | 見送る理由 |
| --- | --- | --- |
| `lat` | 13 | 真は `collate` のみ。残りは `-ulation` `-ation` の誤検出 |
| `ord` | 8 | `border` `affordable` `cordial` `according` が誤検出。真は `order` `ordinance` の2語 |
| `ple` | 8 | `compliant` `perplex` は `plic`（折る）系。真は2〜3語 |
| `sol` | 7 | solvere（解く）・solus（単独）・solidus（固い）が同じ綴りに集まり、危険 |
| `prob` | 4 | `provision` `proviso` は `vis` 系。真は0 |
| `temp` | 4 | `temperature` `tempest` `attempt` `contempt` すべて別語源。真は0 |
| `mort` | 5 | 真は `mortify` のみ（`moratorium` は mora＝遅延） |
| `man` | 4 | `emanate` は manare（流れる）、`reprimand` は premere。真は `maneuver` のみ |
| `aud` | 4 | `audacity` は audere（敢えて）。真は `audible` `audio` の2語 |
| `ped` | 5 | `pedantic` はギリシャ語 paid（子ども）。真は `expedite` 程度 |

## 3. `-ify` / `-fication` 語の扱い（新しい判断）

`fac` の粗一致22語のうち11語が `clarify` `magnify` `nullify` `qualify` `solidify` `typify` `deify` `sanctify` `ratification` `desertification` `mortify` のような **`-ify` / `-fication` 語**。

これらは語源的には確かに facere 系（-ify < -ficare）だが、**前半が別の語根**（clar / magn / null / typ …）で、その語根は辞書に無い。無理にA型にすると `clar` のような未登録の語根断片を接辞として登録することになり、段階2で直したばかりの誤りを再発させる。

**方針**: 前半が辞書に無い語根断片になる `-ify` / `-fication` 語は**A型にしない**（`clarify` `magnify` `nullify` など）。前半が登録済みの語根である語（`rectify`＝rect、`gratify`＝grat、`diversify`＝vers）はA型でよい。あわせて接尾辞 `-ify` の `gloss` に由来を織り込み、カード上は接尾辞の説明として機能させる。

```json
"-ify": { "gloss": "〜にする（facere＝作る から）", "kind": "suffix" }
```

`fac` のA型は、語根が語頭または明確な位置に出る `defect` `deficiency` `difficulty` `faction` `factor` `superficial` などに限る。

## 4. バッチ編成

1バッチ＝語根3〜4個＝1コミット。

| バッチ | 語根 | 見込み |
| --- | --- | --- |
| 1 | `fac` / `her` / `reg` | 18語 |
| 2 | `nom` / `gen` / `sist` / `grat` | 15語 |
| 3 | `log` / `val` / `vid` | 9語 |
| 4 | `cord` / `tang` / `cur` | 9語 |

バッチ1に `fac`（3章の判断が要る）と `her` `reg`（偽陽性が多い）を置き、難所を先に通す。

## 5. 手順（段階2と同じ）

1. 語根と接辞を `word_roots.json` に足す。`vid` の `note` には `spec` との使い分けを書く。
2. `python scripts/build_word_origin_stub.py --root <語根>` で候補を出す。
3. 対象外 / A / B / C の4分類。判断に迷う語は対象外ではなくCへ寄せ、`cReasons` に語根名つきで理由を書く。
4. `npm test`。
5. ブラウザでそのバッチの単語カードを1枚、375px幅でも確認する。
6. 1バッチ＝1コミット。

## 6. 検査

**追加しない**。段階2で入れた検査（接辞キーのハイフン規則、接辞の存在確認、逆引き非空、`cReasons` の語根名、綴り包含、`derivation` と `meaning` の結び付き）で足りる。

語根数の下限も `>= 20` のまま据え置く。件数の消化を目的にしないという方針を、検査で裏切らないため。

## 7. 合格条件

- 13語根すべてでバッチが完了し、各候補が4分類のいずれかに落ちている。
- 前半が未登録の語根断片になる `-ify` 語がA型に混ざっていない（3章）。
- `fac` `her` `reg` のような偽陽性の多い語根で、`note` に「含めない語」が書かれている。
- A型の語根がすべて逆引き2語以上を保ち、`npm test` が通る。
- 段階3終了時点のA型件数を README に記録し、打ち切り基準（0章）に照らして段階4の要否を判断する。

## 8. 非目標

- 未登録1077語のカバー率を上げること自体。
- B型を語根バッチの外で増やすこと。
- 熟語側（`coreImage`）への波及。
