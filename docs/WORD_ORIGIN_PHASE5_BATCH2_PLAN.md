# 単語語源 段階5 バッチ2（`re-`）実装計画

対象: `data/word_roots.json` / `data/word_origins.json` / `data/word_origin_excluded.json`
関連: [WORD_ORIGIN_PHASE5_IMPL_PLAN.md](WORD_ORIGIN_PHASE5_IMPL_PLAN.md)（バッチ0＝仕組み）/ [WORD_ORIGIN_PHASE5_BATCH1_PLAN.md](WORD_ORIGIN_PHASE5_BATCH1_PLAN.md)（バッチ1）/ [WORD_ORIGIN_AUTHORING.md](WORD_ORIGIN_AUTHORING.md)（作成基準）
前提: バッチ1＝`241fcf1`（語根54個・A型161語・B型26語・単発語根18個）
状態: 未着手

## 0. 対象

`python scripts/build_word_origin_stub.py --prefix re` が出す**未判定26語**（判定済み `regurgitate` は除外済み）。

見込みはA型19語、B型5語、C型1語、対象外1語。**新しい語根が17個**増える。終了時点でA型180語前後、カバー率17%台になる。

## 1. 一次判定案（要確認）

**綴りと意味からの一次案であり、確定ではない。** 1語ずつ原形を確認し、取れないものはB型か対象外へ落とす。

### A型（新しい語根を足す）

| 語 | 分解案 | 新語根 | `note` に書く別語 |
| --- | --- | --- | --- |
| `reclaim` | re(元へ)＋claim | `claim`＝叫ぶ（clamare） | **acclaim / proclaim**（収録済み） |
| `redundant` | red(再び)＋und＋-ant | `und`＝波（unda） | inundate / abundant |
| `reflect` | re(元へ)＋flect | `flect`（variants `flex`）＝曲げる（flectere） | **deflect**（収録済み）/ flexible |
| `rejection` | re(元へ)＋ject＋-ion | `ject`＝投げる（jacere） | project / inject |
| `relieved` | re(再び)＋liev | **既存 `lev` に variants `liev` を追加** | alleviate / elevate |
| `remedial` | re(再び)＋med＋-al | `med`＝癒す（mederi） | remedy / medical |
| `repatriation` | re(元へ)＋patri＋-ation | `patri`＝父・祖国（patria） | patriot / expatriate |
| `repeatedly` | re(再び)＋peat＋-ly | **既存 `pet` に variants `peat` を追加** | appetite / compete |
| `reprisal` | re(元へ)＋pris＋-al | `pris`＝つかむ（prehendere） | **surprisingly**（収録済み）/ prison |
| `reptile` | rept＋-ile | `rept`＝這う（repere） | reptilian |
| `repulse` | re(元へ)＋puls | `puls`（variants `pel`）＝押す（pellere） | **impel**（収録済み）/ expel |
| `rescind` | re(元へ)＋scind | `scind`＝裂く（scindere） | rescission |
| `resentfully` | re(強意)＋sent＋-ly | `sent`（variants `sens`）＝感じる（sentire） | **sentiment / consensual**（収録済み） |
| `resilient` | re(元へ)＋sil＋-ent | `sal`（variants `sil`）＝跳ぶ（salire） | salient / assail |
| `resonate` | re(響き返す)＋son＋-ate | `son`＝響く（sonare） | sonic / resonance |
| `retentive` | re(保ち続ける)＋ten＋-ive | `ten`＝保つ（tenere） | **tenure**（収録済み）/ retain |
| `retribution` | re(返す)＋trib＋-ion | `trib`＝割り当てる（tribuere） | contribute / tribute |
| `revelation` | re(元へ)＋vel＋-ation | `vel`＝覆う（velare） | reveal / veil |
| `reprimand` | re(押し返す)＋prim | `prim`＝押す（premere）**要確認** | reprimand / oppress |

**後続バッチで仲間語が増える語根**（太字）: `claim`（`ac-` `pro-`）、`flect`（`de-`）、`pris`（接尾辞のみ）、`puls`（`im-`）、`sent`（接尾辞のみ）、`ten`（接尾辞のみ）。バッチ2で語根を作っておけば後から辞書を触らずに済む。

### 注意が要る3語

- **`reptile` の `re` は接頭辞ではない**。repere（這う）の語幹の一部で、スタブが綴りで拾っただけ。`parts` に `re` を入れない。
- **`reprimand` の `prim`** は premere（押す）由来で、`primus`（第一）とは別語源。同じ綴りで意味が逆方向になるため、`note` に「primus（第一）由来の語は含めない」と明記する。原形を確認できなければB型に落とす。
- **`resentfully` の `re`** は「再び」ではなく強意。`parts[].gloss` は「強く」の側を選ぶ（辞書の多義をそのまま貼らない）。

### B型（分解を出さず由来一行）

| 語 | 理由 |
| --- | --- |
| `reasonable` | ratio（計算・理）由来だが、綴りに語根が現れない |
| `receipt` | capere 由来だが、綴りに `cap`/`cept`/`cip` が現れない |
| `reciprocate` | reciprocus（行き来する）で、capere とは無関係。分解が効かない |
| `recover` | recuperare 由来。cover が英語として自明 |
| `resources` | surgere（起きる）由来だが、source が英語として自明 |

### C型（`word_origin_excluded.json` に記録）

| 語 | グループ | 記録する理由 |
| --- | --- | --- |
| `relegation` | `lect` | legare（送る）由来で、legere（集める・読む）の語根ではない |

### 対象外（記録しない）

`rebound`（bound が英語として自明な複合語）。

## 2. 作業手順

1. `data/word_roots.json` に新語根17個を足す。`origin`（原形）と `note`（同語根の別語1つ以上）は必須。
2. 既存語根に variants を足す（`lev`＋`liev`、`pet`＋`peat`）。**新語根として重複登録しない。**
3. `data/word_origins.json` にA型19語・B型5語を追加する。`gloss` は16文字以内・`meaning` の部分文字列。
4. `relegation` を `word_origin_excluded.json` の `lect` グループに追記する。
5. `npm test`。`single-word roots` が18→30前後に増えることを確認する（語根総数の8割には遠い）。
6. ブラウザで2枚見る。**仲間語0のカード**（例: `resonate`）と、**仲間語ありのカード**（`relieved`＝`lev` が3語目）。375px幅も確認する。
7. 1コミット。`index.html` の `?v=` は上げない（データのみの変更）。

## 3. 合格条件

- A型19語前後・B型5語が入り、`npm test` が通る。
- 新語根すべてに `origin` と、別の英単語を挙げた `note` がある。
- `relieved` のカードで `lev` の仲間語（alleviate / elevate）が出る。
- `reptile` の `parts` に接頭辞 `re` が入っていない。
- 既存187語の表示が変わらない。
