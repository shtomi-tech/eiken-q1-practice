# 単語語源 段階2 修正計画

対象: `data/word_origins.json` / `data/word_roots.json` / `data/lemmas.json` / `scripts/check-word-origin-data.cjs`
関連: [WORD_ORIGIN_PHASE2_PLAN.md](WORD_ORIGIN_PHASE2_PLAN.md)（投入計画）/ [WORD_ORIGIN_AUTHORING.md](WORD_ORIGIN_AUTHORING.md)（作成基準）/ [WORD_ORIGIN_PHASE1_PLAN.md](WORD_ORIGIN_PHASE1_PLAN.md)（辞書）
状態: 完了（2026-08-25）。段階2の投入と同じコミットに含めた

## 0. 現状の判定

候補138語の振り分けは妥当で、A型の分解内容も概ね正確。未登録32語（`lucrative` `deflect` `relegation` `capitalize` `precipitation` など）は、段階1で `note` に書いた「含めてはいけない語」がそのまま落ちている。仲間語パネルも `avert` カードで3語（vertical / subversive / revert）が出ることを実ブラウザで確認済み。

| | 語数 |
| --- | --- |
| A型 | 90 |
| B型 | 16 |
| 未登録（対象外） | 32 |

修正は4件。**AとBは段階3に進む前に必須**、Cは同時に、Dは独立して直せる。

| # | 症状 | 重大度 |
| --- | --- | --- |
| A | `spec` だけA型3語・B型8語で、他19語根と判定基準が揃っていない | 高 |
| B | 接辞辞書が20→63に膨張し、実在しない接尾辞が8つ入った | 高 |
| C | 接辞の当て方に2種類の誤り（多義の貼り付け／語根断片を接辞にした） | 中 |
| D | `positions` が原形化されずキーになっている | 低 |

## 1. A: `spec` の判定基準をそろえる

### 症状

`spec` は候補11語のうちA型3語・B型8語。他の19語根はA型優勢で、**最重要語根（候補数1位）だけがチップと仲間語パネルを持たない状態**になっている。`spectator`（`spect`+`ator`）をA型にした判断とも食い違う。

### 修正

接辞3つを追加し、6語をB型からA型へ上げる。

| 追加する接辞 | 訳 | kind |
| --- | --- | --- |
| `sus` | 下から | prefix |
| `intro` | 内側へ | prefix |
| `retro` | 後ろへ | prefix |

| 語 | A型の `parts` | `derivation` の方向 |
| --- | --- | --- |
| `suspicion` | sus（下から）＋ spic（見る）＋ -ion | 下からじっと見る → 疑い |
| `suspect` | sus ＋ spect | 下からじっと見る → 疑う |
| `introspective` | intro（内側へ）＋ spect ＋ -ive | 自分の内側を見る → 内省的な |
| `retrospect` | retro（後ろへ）＋ spect | 後ろを振り返って見る → 回顧 |
| `specter` | spect ＋ -er | 見えるものとして現れる → 幽霊 |
| `inconspicuous` | in（否定）＋ con（すっかり）＋ spic ＋ -ous | すっかり見える状態ではない → 目立たない |

`specter` と `inconspicuous` は**登録済みの接辞だけで書ける**のにB型になっていた。接辞不足が理由ではないので、判定そのものを見直す。

`auspice` `auspicious` は**B型のまま**とする。`au-` は接辞ではなく avis（鳥）の断片で、鳥占いという由来は一行で説明したほうが分かりやすい。

結果、`spec` はA型9語・B型2語になる。

## 2. B: 接辞辞書の名前空間を分ける

### 症状

段階2で接辞が20→63に増え、次の8つは形態素ではなく**綴りを連続でカバーするための分割**になっている。

| 現在のキー | 使っている語 | 本来の接尾辞 |
| --- | --- | --- |
| `ral` | referral | `-al` |
| `ual` | gradual | `-al` |
| `imen` | specimen | `-men` |
| `uous` | deciduous | `-ous` |
| `iate` | alleviate, enunciate | `-ate` |
| `ition` | disposition, positions, supposition | `-ion` |
| `ient` | gradient, recipient | `-ent` |
| `ibility` | accessibility | `-ity` |

原因は**接辞キーが接頭辞と接尾辞で同じ名前空間を共有している**こと。`al` は接頭辞（ad- の同化形）で埋まっているため、接尾辞の `-al` を書く場所が無く、`ual` `ral` `ical` に分割するしかなかった。

### 修正

接尾辞のキーを**先頭ハイフン付き**にする。

```json
"affixes": {
  "al":  { "gloss": "〜へ・完全に", "kind": "prefix" },
  "-al": { "gloss": "〜に関する", "kind": "suffix" }
}
```

- 検査の綴り包含判定は、**先頭のハイフンを外してから**行う（`-al` ⊂ `referral`）。
- 上表の8つを本来の接尾辞へ寄せる。すべて包含判定を通る（`-ate` ⊂ alleviate、`-ion` ⊂ disposition、`-ent` ⊂ recipient、`-ity` ⊂ accessibility）。
- `-ical` `-ential` `-ation` `-ator` `-ency` は連結形として英語で定着しているのでキーとして残してよい。**判断基準は「英語の接尾辞として辞書に載る形か」**。
- `kind: "suffix"` のキーはハイフン必須、`kind: "prefix"` のキーはハイフン禁止を検査で固定する。

### あわせて足す

`a` `ac` `ag` `al` `an` は ad- の同化形だが、**基本形の `ad` が辞書に無い**。`in`/`im`、`con`/`com`、`ex`/`e` は基本形と異形の両方を持っているので、`ad` を足して揃える。

## 3. C: 接辞の当て方を直す

### C-1. 多義の接辞を語ごとに1つ選ぶ

`parts[].gloss` は**その語での意味**を書く決まり（`WORD_ORIGIN_PHASE2_PLAN.md` 5章）だが、辞書の多義をそのまま貼っている箇所が31ある。うち**意味が食い違う次の14箇所を直す**。

| 接辞 | 語 | 現在 | 直す方向 |
| --- | --- | --- | --- |
| `a` | avert | 〜へ・離れて | 離れて（ab- 由来） |
| `a` | ascribe | 〜へ | そのまま（ad- 由来）。**同じ `a` が逆の意味を持つことを辞書の `note` に書く** |
| `al` | alleviate | 〜へ・離れて | 〜へ（ad- 由来。辞書の `gloss` とも食い違っている） |
| `re` | reduce / reduction / revoke / renounce / recipient / requirement / requisite / referral | 再び・後ろへ | 語ごとに「後ろへ」「再び」を選ぶ |
| `il` | illuminate / illustrate / illustrious | 中へ・上に | 中へ・上に（in- 由来）→「〜の上に」に寄せる |
| `an` | announcement | 〜へ・上に | 〜へ（ad- 由来） |
| `ag` | aggression | 〜へ・向かって | 〜へ向かって |
| `en` | enunciate | 中へ・完全に | 外へ（ex- 由来の e-/en- ではなく、enuntiare は ex+nuntiare）※要確認 |

`-ent` `-ant` `-or` `-ment` `-ure` の「〜するもの・人」のような**近い意味の併記は直さない**（読み手に有益で、誤りではない）。

### C-2. 語根の断片を接辞にしない

| 語 | 現在 | 問題 | 直す方向 |
| --- | --- | --- | --- |
| `proliferate` | pro ＋ fer ＋ -ate | `pro` は接頭辞ではなく proles（子孫）の一部 | **B型へ落とす**。「子孫を生み出すことから → 急増する」 |
| `participant` | par ＋ cip ＋ -ant | `par` は pars（部分）＝語根であって接辞ではない | `parts` から `par` を外し、`cip ＋ -ant` にする。「一部を取って加わる」は `derivation` の文で表す |

`par` が他の語で使われていないことを確認したうえで、接辞辞書から `par` を削除する。

これで `fer` のA型は6→5語、`cap` は4語のまま（`participant` はA型を維持）。いずれも仲間語の逆引き2語以上の条件を満たす。

## 4. D: `positions` を原形化する

`data/lemmas.json` に `positions → position` が無いため、`word_origins.json` のキーが `positions` になり、カード見出しも「positions」のまま出る。

- `lemmas.json` に `"positions": "position"` を1行足す。
- `word_origins.json` のキーを `position` に変える。
- `npm test`（`check-lemma-headword.cjs` と語源検査の両方が通ること）。

同様に語尾 `s` のキーを確認したが、`auspicious` `inconspicuous` `illustrious` `lustrous` `deciduous` は原形であり修正不要。

## 5. 検査に足すもの

- `kind: "suffix"` のキーは先頭ハイフン必須、`kind: "prefix"` のキーはハイフン禁止。
- 綴り包含判定はハイフンを外してから行う（既存の `parts[].form` 検査の修正）。
- `parts[].form` が接辞辞書にあるかの検査（段階2で追加済み）は、ハイフン付きキーでも引けるようにする。

**機械化しないもの**: 「多義をそのまま貼らない」（C-1）は判定できないので、`WORD_ORIGIN_AUTHORING.md` に一文追加して基準側で縛る。

## 6. 手順

1. B（接辞のハイフン化）とその検査を先に入れる。**キーの形式が変わるので、後続の修正が全部これに乗る。**
2. C-1・C-2（接辞の当て方）を直す。
3. A（`spec` の6語をA型へ、接辞 `sus` `intro` `retro` と `ad` を追加）。
4. D（`positions`）。
5. `npm test`。
6. ブラウザで `suspicion`（新規A型）と `avert`（接辞の訳を直した語）を1枚ずつ確認する。375px幅も見る。
7. 段階2の106語ごと**1コミット**にまとめる（例:「語根20個の語源データを追加する」）。修正前の状態は未コミットなので、分ける必要はない。

## 7. 合格条件

- `spec` のA型が9語になり、カードにチップと仲間語パネルが出る。
- `affixes` に実在しない接尾辞（`ral` `ual` `imen` `uous` `iate` `ition` `ient` `ibility`）が無い。
- `parts[].gloss` に、その語で成り立たない意味が残っていない（C-1の14箇所）。
- `proliferate` がB型、`participant` の `parts` から `par` が消えている。
- カード見出しが `position` になる。
- `npm test` が通り、A型の語根がすべて逆引き2語以上を保つ。

## 8. 非目標

- 未登録32語の再検討。判定は妥当と確認済み。
- B型16語のうち、1章で挙げた6語以外の見直し。
- 語根の追加（段階3の話）。
