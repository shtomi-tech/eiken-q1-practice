# 連鎖から不変化詞が抜けている問題の修正計画

対象: `data/vocab_*.json`（11ファイル・94件）/ `scripts/check-core-image-data.cjs`
関連: [CORE_IMAGE_ROLLOUT_PLAN.md](CORE_IMAGE_ROLLOUT_PLAN.md) / [CORE_IMAGE_ROLLOUT_FIX_PLAN.md](CORE_IMAGE_ROLLOUT_FIX_PLAN.md)
状態: 未着手。**公開済み**（`86af5fe`）のデータに欠陥がある

## 0. 症状

暗記カードの核心イメージは「構成語 → 不変化詞 → 派生義 → 中心義」の連鎖で意味を導くものだが、`particle` を持つ熟語 **174件のうち94件（54%）** で、連鎖に不変化詞のステップが存在しない。

```
正しい形（vocab_1_mock-1.json）
  hang(ぶら下がる) → out(外へ・こもらずに) → こもらずに人と一緒に過ごす → ぶらぶら過ごす、遊ぶ

欠陥（公開中）
  patch(つぎを当てて直す) → 整った状態まで仕上げる                       ← up が無い
  buckle(締め具を締める) → 気持ちを引き締めて向き合う → 気を引き締めて本腰を入れる  ← down が無い
```

`patch up` のカードでは、パネル見出しに「「up」のイメージ」と出るのに連鎖には `up` が無く、**カードの中で説明が繋がっていない**。

### 分布

| ファイル | 欠落 / particle付き熟語 |
| --- | --- |
| `vocab_1_2025-2.json` | 16 / 16 |
| `vocab_p2_mock-1.json` | 16 / 16 |
| `vocab_1_2025-3.json` | 15 |
| `vocab_1_2026-1.json` | 14 |
| `vocab_2025-2.json` | 8 |
| `vocab_2026-1.json` | 8 |
| `vocab_p2_2026-1.json` | 8 |
| `vocab_p2_2025-3.json` | 4 |
| `vocab_2025-3.json` | 3 |
| `vocab_1_mock-3.json` | 1 |
| `vocab_p2_2025-2.json` | 1 |

`mock-1`（手作業で作った最初の16件）と `mock-2` `mock-4` `mock-5` はほぼ無事。展開バッチで形が崩れた。

### 検査が素通りした理由

`check-core-image-data.cjs` の連鎖に関する契約は「2〜5段」「最後の要素に `term` が無い」の2つだけで、**`particle` が連鎖に現れることを要求していない**。核心イメージの前提そのものが検査されていなかった。

## 1. 先に検査を入れる（順序を守る）

データより先に検査を追加し、94件が落ちる状態にしてから直す。検査が後だと直し漏れを検出できない。

`scripts/check-core-image-data.cjs` に追加する契約:

- `coreImage.particle` があるとき、`chain` の `term` 付きステップに**その不変化詞が含まれる**こと。
  - 判定は `term` を小文字化して `particle` と完全一致で行う。`up to` のような複数語 particle は、連続する複数ステップに分けても1ステップにまとめてもよい（`chain` の `term` を空白連結した文字列に `particle` が含まれれば可）。
- 追加した検査は既存の「`chain` は2〜5段」と両立する。不変化詞ステップの挿入で2段→3段、3段→4段になるため上限5段は超えない（現状の最大は3段）。

## 2. 94件へ不変化詞ステップを挿入する

### 現状の形

欠落エントリは**すべて `term` 付きステップが1つだけ**（動詞のみ）で、形は次の2種類しかない。

| 現状 | 件数 | 修正後 |
| --- | --- | --- |
| 動詞 → 中心義（2段） | 78 | 動詞 → 不変化詞 → 中心義（3段） |
| 動詞 → 派生義 → 中心義（3段） | 16 | 動詞 → 不変化詞 → 派生義 → 中心義（4段） |

挿入位置は**動詞ステップの直後**で統一する。既存の `gloss` は書き換えない（公開済みで学習者が見ているため、変更は最小限にする）。

### 挿入する `gloss` の作り方

各熟語には `particleSense` が割り当て済みなので、**その用法のラベルを土台**にし、熟語の文脈へ合わせて短く整える。

| 例 | particle / sense | 挿入するステップ |
| --- | --- | --- |
| `patch up` | up / prepare（上向きに整えて用意する） | `{ "term": "up", "gloss": "整った状態まで" }` |
| `crack down` | down / suppress（押さえつけて動きを止める） | `{ "term": "down", "gloss": "下へ押さえつけて" }` |
| `branch off` | off / separate（切り離す・遮断する） | `{ "term": "off", "gloss": "本体から切り離して" }` |
| `breeze in` | in / (fallback) | `{ "term": "in", "gloss": "中へ入って" }` |

ラベルをそのまま貼らない。連鎖は「動詞 → 不変化詞 → 意味」と読んで通る日本語にする。

### 不変化詞別の件数（作業量の見積り）

```
off 20 / up 16 / out 16 / on 9 / in 7 / down 6 / away 4 /
by 3 / over 3 / into 3 / back 2 /
behind 1 / along 1 / about 1 / forward 1 / across 1
```

sense 単位では `off/separate` 11件、`in/(fallback)` 7件、`on/contact` 5件、`out/produce` 5件が多く、**同じ sense の中では挿入する gloss を揃えられる**ため、実質の判断回数は44 sense 分に近い。

### 注意が要るケース

3語以上の `phrase` が16件あり、不変化詞の位置が語頭側でないものがある。

```
see it off / take it back / fill it out / put it off / give it away   … particle が3語目
make up my mind / get off my back / go on a voyage / put out the light … 目的語が後続
look forward to / set off for / go along with / watch out for / take away from … 前置詞が後続
```

これらは**動詞の直後に不変化詞ステップを置く**方針で統一する（`fill it out` → `fill` → `out` → …）。`it` `my mind` などの目的語はステップにしない。

`bring out in` は `phrase` 自体が既存データの誤り（[CORE_IMAGE_ROLLOUT_FIX_PLAN.md](CORE_IMAGE_ROLLOUT_FIX_PLAN.md) 5章）。今回も `phrase` は修正せず、`out` のステップ挿入だけ行う。

## 3. バッチ分割

1ファイル＝1バッチとし、欠落の多い順に進める。各バッチで `npm test` を通す。

1. `vocab_1_2025-2.json`（16件）
2. `vocab_p2_mock-1.json`（16件）
3. `vocab_1_2025-3.json`（15件）
4. `vocab_1_2026-1.json`（14件）
5. `vocab_2025-2.json` / `vocab_2026-1.json` / `vocab_p2_2026-1.json`（各8件）
6. 残り4ファイル（4/3/1/1件）

検査を先に入れる関係で、1〜6が終わるまで `npm test` は落ち続ける。**途中でコミットする場合はテストが赤いまま**になるため、次のどちらかを選ぶ:

- **6-1（推奨）**: 検査追加＋全94件の修正を**1コミット**にまとめる。テストが赤い状態を残さない。
- 6-2: 検査追加を最後のコミットに回す。途中はテストが緑だが、直し漏れを検出できない期間ができる。

## 4. 検証

- `npm test`（新規検査を含め全項目 OK）
- 「`particle` を持つ174件すべてで連鎖に不変化詞が含まれる」ことをスクリプトで確認（現状 80/174 → 174/174）
- 連鎖の段数分布を確認し、2段の `particle` 付きエントリが0件になっていること
- 表示シミュレーションで、`patch up` が「patch → up → 整った状態まで仕上げる」と読めること
- 公開後に実ブラウザで `patch up`（1級2025年度第3回・第20問）のカードを確認する。今回の指摘はこのカードの実画面から出たため、同じ画面で直っていることを確かめる

## 5. 非対象

- 既存 `gloss` の書き換え（公開済みのため最小変更に留める）
- `particle` を持たない87件（前置詞句・定型表現型）。これらは不変化詞パネルを出さないため対象外
- `bring out in` の `phrase` 自体の誤り
- `up` の sense 細分化（12個・単発4つ）の見直し
