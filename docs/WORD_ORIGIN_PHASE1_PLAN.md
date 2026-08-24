# 単語語源 段階1: 語根・接辞辞書の確定

対象: `data/word_roots.json` / `scripts/check-word-origin-data.cjs` / `scripts/build_word_origin_stub.py`（新規）
関連: [WORD_ORIGIN_PLAN.md](WORD_ORIGIN_PLAN.md)（全体計画）/ [WORD_ORIGIN_AUTHORING.md](WORD_ORIGIN_AUTHORING.md)（作成基準）/ [WORD_ORIGIN_FIX_PLAN.md](WORD_ORIGIN_FIX_PLAN.md)（段階0の手当て）
前提: 段階0は `baf6fd4`「単語カードに語源表示を追加」でコミット済み（仕組み一式＋語根 `voc` の3語）
状態: 未着手

## 0. この段階でやること / やらないこと

**やること**: `data/word_roots.json` に**語根20個と接辞15個**を書き切る。辞書だけを1コミットで確定させる。

**やらないこと**: `data/word_origins.json` への語の追加（＝段階2以降のバッチ作業）。UIとCSSは触らない。

辞書を先に固めるのは、段階2で語根単位のバッチを回すときに、**バッチごとに辞書へ後追いで足す状況を避ける**ため。語根の訳と `variants` が途中で変わると、既に入れた語の `parts[].gloss` と食い違う。

## 1. 選定の方法と、その限界

`data/vocab_*.json` の全単語を `lemmas.json` で原形化した**1183語**に対し、ラテン・ギリシャ語根の候補約100グループを**部分文字列一致**させ、ヒットした語を人が目視で精査して偽陽性を落とした。

- 粗一致の段階では偽陽性が非常に多い。例: `ver` は23語ヒットするが `average` `govern` `quiver` `recover` `poverty` を含む。`nat` の17語も `abomination`（＝min系）`assassination` など大半が接尾辞 `-ation` の誤検出。
- したがって**下表の「精査後」は目視による見込み値**であり、確定値ではない。段階2で各語を実際にA/B/C判定した時点で増減する。ここでは**採用する語根を決めるための順位付け**として使う。

## 2. 採用する語根20個

| # | 語根 | `variants` | 意味 | 粗一致 | 精査後（見込み） | 代表語 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `spec` | `spic` `spect` | 見る | 11 | 11 | perspective / suspicion / specimen |
| 2 | `pos` | `pon` | 置く | 15 | 10 | propose / postpone / juxtapose |
| 3 | `vert` | `vers` | 回す・向ける | 12 | 9 | avert / invert / subversive |
| 4 | `fer` | — | 運ぶ | 9 | 8 | transfer / defer / proliferate |
| 5 | `port` | — | 運ぶ | 7 | 7 | import / rapport / proportion |
| 6 | `luc` | `lum` `lustr` | 光 | 10 | 6 | elucidate / illuminate / translucent |
| 7 | `duc` | `duct` | 導く | 5 | 5 | deduce / conductor / product |
| 8 | `gress` | `grad` | 歩む | 5 | 5 | transgression / gradual / digression |
| 9 | `voc` | `vok` | 呼ぶ・声 | 4 | 4 | equivocate / evoke / revoke（段階0で登録済み） |
| 10 | `scrib` | `script` | 書く | 4 | 4 | prescription / proscribe / ascribe |
| 11 | `nunc` | `nounc` | 告げる | 4 | 4 | renounce / enunciate / announcement |
| 12 | `ven` | `vent` | 来る | 7 | 4 | convene / contravene / venture |
| 13 | `ced` | `cess` | 行く・譲る | 6 | 4 | accede / cessation / successor |
| 14 | `cap` | `cept` `cip` | 取る | 9 | 4 | accept / recipient / perception |
| 15 | `lect` | `leg` `lig` | 集める・選ぶ | 11 | 4 | collect / eligible / negligent |
| 16 | `tract` | — | 引く | 3 | 3 | extract / detract / subtract |
| 17 | `quir` | `quis` `quest` | 求める | 4 | 3 | acquire / requisite / requirement |
| 18 | `plac` | — | なだめる・気に入る | 4 | 3 | placate / complacency / placebo |
| 19 | `cid` | `cis` | 切る・落ちる | 4 | 3 | incisive / coincidental / deciduous |
| 20 | `lev` | — | 軽い・上げる | 4 | 3 | alleviate / elevate / levity |

合計の見込みは**約100語**（1183語の8%強）。段階2はこの範囲を上から順に消化する。

### 同綴異根の注意（`note` に必ず書く）

- `cap`: 「取る」の *capere* と「頭」の *caput*（`capital` `precipitation` `escape`）は別語根。`caput` 由来の語をこの語根に入れない。
- `luc`: `lucrative` は *lucrum*（利益）で光ではない。`lustrous` `illustrate` は *lustrare* で同族として扱ってよい。
- `lect`: `deflect` `reflect` は `flect`（曲げる）であってこの語根ではない。`relegation` は *legare*（送る）。
- `val`: 見送り候補だが、採用するなら `ambivalent` は *valere*、`valley` `cavalier` は無関係。

## 3. 見送る候補と理由

順位は上位でも、**偽陽性が多く辞書として危ない**ものは入れない。段階2で必要になったら個別に追加する。

| 候補 | 粗一致 | 見送る理由 |
| --- | --- | --- |
| `ver` | 23 | 「真実」の *verus* に一致する語がほぼ無い。ヒットの大半が `-over-` `-vert-` の混入 |
| `nat` | 17 | ほぼ全て接尾辞 `-ation` の誤検出 |
| `her` | 13 | `altogether` `gather` `philosopher` など、語根と無関係な綴りの一致 |
| `min` | 12 | 真に *minor*（小さい）なのは `diminutive` 程度 |
| `cord` | 9 | 「心臓」の *cor* に該当するのは `cordial` `discord` のみ。`score` `escort` は無関係 |
| `aud` | 4 | `audacity`（*audere*＝敢えて）`fraudulent` を除くと2語 |
| `sequ` | 3 | `issue` `tissue` が誤検出。真は `sequentially` のみ |
| `grat` | 3 | `immigration` が誤検出。真は2語 |

## 4. 接辞15個

接辞は語根の脇役として、A型の `parts` に書く訳を統一するために置く。**接辞だけのパネルは出さない**（段階0の実装どおり）。

接頭辞10（1183語での出現順）

| 接辞 | 訳 | 備考 |
| --- | --- | --- |
| `in` / `im` | 中へ ／ 否定 | **2義あるので `note` で書き分ける**。`parts[].gloss` はどちらかを選んで書く |
| `re` | 再び・後ろへ | |
| `de` | 下へ・離れて・完全に | |
| `con` / `com` | ともに・完全に | |
| `dis` | 離れて・否定 | |
| `pro` | 前へ | |
| `ex` / `e` | 外へ | |
| `sub` | 下へ・副次的に | |
| `per` | 通して・徹底的に | |
| `pre` | 前もって | |

接尾辞5

| 接辞 | 訳 |
| --- | --- |
| `ate` | 〜にする（動詞化） |
| `ion` | 〜すること（名詞化） |
| `ive` | 〜する性質の |
| `ous` | 〜に満ちた |
| `ify` | 〜にする |

## 5. 記述ルール

`WORD_ORIGIN_AUTHORING.md` に従いつつ、辞書側は次を守る。

- `gloss` は**日本語で最大2語義**まで。長い説明は `note` に回す。
- `origin` は「ラテン語 ducere」の形で言語名＋原形。ギリシャ語由来は「ギリシャ語 〜」。
- `note` は「引いて連れて行くイメージ」のような**中心イメージ1文**。語源学の解説にしない。同綴異根がある語根では、**入れてはいけない語**を必ず書く。
- `variants` は**実際に語彙データに現れる綴り**だけを書く。使わない異形を先回りで足さない（逆引きのノイズになる）。
- 接辞の `kind` は `prefix` / `suffix` のみ。

## 6. 検査の追加

`scripts/check-word-origin-data.cjs` に足す。

- `roots` が20個以上、`affixes` が15個以上あること（段階1の完了条件を機械で固定する）。
- `variants` が他の語根の `root` キーや `variants` と**重複しない**こと（逆引きが二重に張られるのを防ぐ）。
- 各語根の `note` があること（同綴異根の注意を書く場所を強制する。現在は任意フィールド）。
- **未使用の語根を許す**こと（段階1では `origins` がまだ3語なので、参照されない語根が17個ある状態が正常）。この方針を検査のコメントに明記する。

## 7. 手順

1. 上表の20語根と15接辞を `data/word_roots.json` に書く。`voc` は段階0の記述をそのまま残す。
2. 検査（6章）を追加し、`npm test` を通す。
3. `scripts/build_word_origin_stub.py` を追加する（読み取り専用）。`--root <語根>` で、その語根と `variants` に一致する原形と `meaning` を一覧出力する。段階2のバッチ入力になる。語根の当てはめと `derivation` は生成しない。
4. ブラウザ確認は不要（表示は変わらない）。`equivocate` カードが段階0のまま動くことだけ確認する。
5. 1コミット（例: 「単語語源の語根・接辞辞書を確定する」）。

## 8. 合格条件

- `data/word_roots.json` に語根20・接辞15が揃い、`npm test` が通る。
- 同綴異根のある `cap` `luc` `lect` に、入れてはいけない語が `note` に書かれている。
- `data/word_origins.json` は3語のまま（この段階で語を増やさない）。
- 既存の `equivocate` カードの表示が変わっていない。

## 9. 段階2の入口（この計画の外）

辞書が固まったら、次の順で語根バッチを回す。1バッチ＝語根2〜3個＝1コミット。

1. `spec` / `pos` / `vert`（見込み30語。最大の塊を先に取る）
2. `fer` / `port` / `luc`（21語）
3. `duc` / `gress` / `scrib`（14語）
4. `nunc` / `ven` / `ced`（12語）
5. `cap` / `lect` / `quir`（11語）
6. `tract` / `plac` / `cid` / `lev`（12語）

各バッチで、粗一致リストからA/B/Cを判定し、A型だけを `word_origins.json` に入れる。C型は `check-word-origin-data.cjs` の `cReasons` に理由を1行足す。
