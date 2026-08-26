# 準2級 自作模試 第2回〜第4回のレビュー指摘を直す実装計画

対象: `scripts/build_q1_p2_mock_{2,3,4}_data.py`（正本）/ `data/questions_p2_mock-{2,3,4}.json` /
`data/vocab_p2_mock-{2,3,4}.json`（生成物）/ `scripts/check_p2_mock_data.py` /
`docs/P2_MOCK_SET_2_4_REVIEW.md`
状態: 未着手（[P2_MOCK_SET_2_4_PLAN.md](P2_MOCK_SET_2_4_PLAN.md) の実装後レビューで出た指摘への対応）

## 0. 前提

- **正本はビルドスクリプト**、JSONは生成物。設問・選択肢・語彙・語源・核心イメージは
  すべて `build_q1_p2_mock_N_data.py` 側を直し、JSONは再生成する。
- **再生成すると `ipa` が落ちる**（ビルドスクリプトが持っていないため）。
  JSONを作り直したら必ず `enrich_flashcard_fields.py` を回す。これは全セット共通の運用。
- 既存の機械チェック（`check_q1_data.py` / `check_p2_mock_data.py` / `npm test`）は
  現状すべて通っている。**今回の指摘はいずれも既存チェックが見ていない領域**なので、
  直すだけでなく**再発を防ぐ検査を足す**（8節）。
- 語彙の入れ替えを伴う修正は、既存の重複制約（準2級の全語句・`lemmas.json` の原形・
  全配信セットの熟語 phrase）を再度通す必要がある。

## 1. 修正項目

| # | 指摘 | 優先 | 機械化 |
| --- | --- | --- | --- |
| A-1 | ダミー選択肢が設問文中にそのまま出ている（8問） | 高 | 可（8.1） |
| A-2 | 正答位置の偏り（mock-2 は15問中9問が①） | 高 | 可（8.2） |
| B-1 | 新規熟語60件が全て前置詞句・副詞句で句動詞ゼロ（`particle` 0/60） | 中 | 一部（8.3） |
| B-2 | 熟語の `pos` が全件 `熟語`（既存は 句動詞／前置詞句／慣用句 等） | 中 | 可（8.3） |
| B-3 | 統語クラスの違いで意味を読まずに消去できる設問 | 中 | 不可（目視） |
| C-1 | `noticeboard` が英用法（他データは米語基調） | 低 | 不可 |
| C-2 | レビュー文書の mock-2 Q11 修正履歴が最終データと矛盾 | 低 | 不可 |
| C-3 | `check_p2_mock_data.py` の `MOCK_ROUNDS` がハードコード | 低 | — |

## 2. A-1 ダミー選択肢の本文出現（8問）

既存の準2級4セット・1級・準1級はいずれも0件で、**新規3セットだけの現象**。
本文にある語は「答えではない」と分かるため、意味を知らなくても消せる。

| セット | Q | 該当ダミー | 本文中の出現 |
| --- | --- | --- | --- |
| mock-2 | 5 | `calendar` | `wrote the (   ) on my calendar` |
| mock-3 | 1 | `island` | `The island's old (   )` |
| mock-3 | 4 | `tenant` | `the tenants should stay home` |
| mock-3 | 5 | `traffic` | `Traffic moved slowly` |
| mock-4 | 2 | `treatment` | `choosing the right treatment` |
| mock-4 | 3 | `passenger` | `Passengers should wait` |
| mock-4 | 4 | `storm` | `After the storm` |
| mock-4 | 10 | `compare` | `compare the prices and (   )` |

**直し方の原則: ダミー側を差し替える。**本文の語を消すと、正答を一意にしている文脈
（`calendar` に書く＝予定、`tenants` が待つ＝家主が来る、など）が壊れる。

- 差し替えるダミーは、**同一品詞・同レベルで、その設問の文脈では明確に成立しないもの**。
  当該設問の他のダミーと意味が近すぎないこと。
- 差し替えた語は語彙60件のうちの1件なので、**`meaning` / `example` /
  `exampleTranslation` / `etymology` を新たに書き、`ipa` は再取得**する。
- 差し替え後に4.1の重複制約（準2級の全語句・`lemmas.json` の原形）を通す。
- mock-4 Q10 は本文が `compare the prices and (   ) the model` と動詞が並ぶ形なので、
  ダミー `compare` の差し替えに加えて本文を `check the prices and (   )` のように
  整えてもよい（本文側を変える場合は設問訳も直す）。

## 3. A-2 正答位置の偏り

**本番形式4択はデータの順番のまま表示される**（`static/mode-q1.js:3671` の
`q_.choices.forEach` にシャッフルは無い。意味チェックの4択だけ `shuffle` される）。
したがって偏りはそのまま生徒の当てずっぽうに効く。

| セット | 現状（①②③④） | 既存セットの帯 |
| --- | --- | --- |
| mock-2 | **9 / 2 / 3 / 1** | 過去問3セットと mock-1 はいずれも各位置 2〜5 |
| mock-3 | 2 / 3 / 6 / 4 | 同上 |
| mock-4 | 6 / 3 / 4 / 2 | 同上 |

- mock-2 を最優先で組み替える。mock-4 も①を1〜2問ずらす。
- **各位置3〜5件**に収める（15問なので均等は3.75件）。
- ビルドスクリプトの `QUESTIONS` で `choices` の並びと `answerIndex` を同時に直す。
  語彙JSONは `choices` の順で生成されるため**自動で追随する**（`check_q1_data.py` は
  語彙と選択肢を集合で照合しており、順序は要求していない）。
- 並べ替えのついでに、正答が毎回同じ位置に固まらないか3セット通しで確認する。

## 4. B-1 句動詞をゼロから戻す

新規60熟語はすべて前置詞句・副詞句で、`coreImage.particle` は 0/60。
既存は mock-1 が 16/20、過去問 2026-1 が 8/20。影響は2つ。

- 準2級 大問1の熟語は句動詞が主要層。3セット続けて `look after` 型が1件も出ない。
- 暗記カードの**不変化詞パネルと仲間例はA型（`particle` 付き）でのみ出る**ため、
  新セットではこの機能が一切働かない。

### 4.1 差し替え範囲

熟語は Q11〜Q15 に4件ずつ入り、**同一設問の4択は `pos` を揃える必要がある**ため、
語単位ではなく**設問単位で差し替える**。

- **各セット Q11・Q12 の計8件を句動詞（A型）へ差し替える**（3セットで24件）。
  結果として `particle` は各セット 8/20 となり、過去問 2026-1 と同水準になる。
- Q13〜Q15 の12件は前置詞句・副詞句のまま据え置き（B型）。
- mock-2 は20件中18件が「in/at/on/with + 名詞 + of」型で単調なので、
  据え置く12件のうち重なりの強いもの（`in the middle of` と `in the center of` など）は
  片方を別型の表現へ替える。

### 4.2 使える句動詞

全配信データの熟語 phrase と重複しないことが条件（8.3の検査で強制）。
準2級相当の候補50件を照合したところ**34件が未使用**で、必要な24件は十分に確保できる。

```
put off / take care of / get along with / bring up / call off / deal with / figure out /
fill out / find out / get over / give in / hand in / hold on / keep up with / leave out /
look into / look up / make up / put up with / show up / turn out / cut down on / drop by /
put together / check out / clean up / break down / catch up with / come up with / end up /
hang up / pass away / stay up / throw away
```

（使用済みで選べないもの: look after, give up, run out of, look forward to, carry out,
come across, pick up, point out, set up, take off, take over, turn down, turn in,
work out, get rid of, go over）

### 4.3 核心イメージ（A型）の作り方

[CORE_IMAGE_AUTHORING.md](CORE_IMAGE_AUTHORING.md) に従う。A型は `chain` ＋ `particle` ＋
`particleSense` を付ける。機械側の制約で効いてくるのは次の2点。

- `particle` は `data/particle_images.json` にあるものだけ。`particleSense` はその辞書の
  sense id で、`general` は不可。
- **同一セット内で同じ `particle` × `particleSense` を使い回すほど、辞書側に必要な
  仲間例が増える**（`3 + (使用回数 - 1)`、上限6）。8件を選ぶ時点で
  `up` / `out` / `off` / `in` などに偏らせず、sense も散らす。

## 5. B-2 `pos` ラベル

現状は熟語60件すべて `熟語`。既存データは `句動詞` / `前置詞句` / `動詞句` /
`慣用句` / `接続詞句` と区別しており、`熟語` は今回が初出。

- 差し替えた句動詞は `句動詞`。
- 据え置く前置詞句は `前置詞句`、単独で副詞的に働くもの（`in the long run`,
  `on purpose`, `at first sight` など）は `副詞句`。
- **同一設問の4択は `pos` が一致する必要がある**（`check_p2_mock_data.py`）。
  `前置詞句` と `副詞句` が同じ設問に混ざる場合は、**選択肢の組み替えで揃える**。
  これは6節と同じ作業になる。

## 6. B-3 統語クラスで消去できる設問

mock-4 Q14 は `(   ), visitors must use the main entrance.` で、正答 `for this reason`
以外の3件（`in comparison with` / `in spite of` / `on the basis of`）が目的語必須のため、
意味を読まずに答えが決まる。レビュー文書の mock-4 Q15 では「目的語を必要とする
`in the form of` へ差し替えた」と、これを一意化の手段として使っており方針が逆。

- **1設問の4択は、統語的にはどれも空所に入れられる**ものにする
  （4件とも目的語を取る／4件とも単独で副詞的に働く、のどちらかに統一）。
- 一意化は**文脈を足して**行う（`P2_MOCK_SET_PLAN.md` の方針）。
- 対象は mock-4 Q14・Q15 を中心に、Q11〜Q15 を通しで見直す。5節のラベル統一と同時に行う。

## 7. C 軽微

- **C-1 `noticeboard`（mock-4 Q1 正答）**: 米語では `bulletin board`。ただし
  **2語にするとビルドスクリプトが `idioms` バケットへ入れてしまい 40/20 の件数が崩れる**
  （`if " " in choice` で振り分けている）。1語の米語名詞へ差し替えるか、設問ごと
  別の名詞へ作り替える。本文の `timetable` も `schedule` 系の語に寄せるか併せて判断する。
- **C-2 レビュー文書**: `docs/P2_MOCK_SET_2_4_REVIEW.md` の mock-2 修正履歴に Q11 が
  2件あり、後者「駅から逃げた泥棒を追う文脈へ修正」は最終データ（珍しい鳥）と食い違う。
  最終状態に合わせて履歴を整理する。今回の修正分も追記する。
- **C-3 `MOCK_ROUNDS`**: `("mock-1", ..., "mock-4")` のハードコード。
  `data/vocab_p2_mock-*.json` の glob へ変える（計画どおり）。mock-5 を足したときの
  検査漏れを防ぐ。`--dataset` での単一指定は残す。

## 8. 追加する検査（`scripts/check_p2_mock_data.py`）

いずれも既存4セット（過去問3＋mock-1）でも通ることを確認してから入れる。
**過去問セットに対しては落とさない**（`check_p2_mock_data.py` の対象は模試のみ）。

### 8.1 ダミー選択肢の本文出現

- 単語の選択肢は、語形変化（`-s` / `-es` / `-ed` / `-ing` / `-ies`）込みで stem に
  出現したら落とす。正答については既存の検査があるので、**誤答3件に広げる**形。
- 熟語の選択肢は phrase 全体の一致で見る（構成語 `of` `in` 等の一致は無視する）。

### 8.2 正答位置の分布

- 15問で各位置3〜5件。範囲外は落とす。

### 8.3 熟語の型とラベル

- `pos` は既存データで使われているラベル集合のみ許可（`熟語` を弾く）。
- 1セットの熟語20件のうち `coreImage.particle` を持つものが**4件以上**あること
  （句動詞ゼロを二度と作らない下限。過去問 2026-1 が8/20、2025-3 が4/20）。
- 熟語 phrase が全配信データと重複しないことは既に実装済みなのでそのまま。

### 8.4 検査できないもの（目視で残す）

- 4択の統語クラスの揃い（6節）
- 品詞バランス（現状3セットとも 名詞20 / 形容詞12 / 動詞8 / 副詞0。
  過去問は 名詞16 / 動詞16 / 形容詞4 / 副詞4 前後）。**次に語彙を差し替えるときは
  副詞と動詞を増やす方向に寄せる**。今回の修正では設問の作り直しに合わせて
  可能な範囲で寄せ、機械の下限は設けない。
- 正答の一意性（`codex:rescue` による独立レビュー）

## 9. 作業順

セット単位ではなく**指摘単位**で進める（A-1・A-2 は独立で安全、B は設問の作り直しを伴う）。

1. **検査を先に足す**（8.1〜8.3）。既存4セットで通ることを確認し、新規3セットが
   意図どおり落ちることを確認する。落ちない検査は役に立たない。
2. A-1（8問のダミー差し替え）→ 差し替えた語の `meaning` / `example` /
   `exampleTranslation` / `etymology` を書く。
3. A-2（mock-2 中心に正答位置を組み替え）。
4. B-1・B-2・B-3 をセットごとにまとめて実施（Q11・Q12 を句動詞へ、
   Q13〜Q15 のラベルと統語クラスを整える）。mock-2 → mock-3 → mock-4 の順。
5. 各セットで `build → enrich_flashcard_fields → check_p2_mock_data → check_q1_data`。
6. 差し替えた設問（A-1の8問＋B-1で作り直した6問）だけを `codex:rescue` に渡して
   正答一意性を再確認する。全45問を再レビューする必要はない。
7. `npm test`（核心イメージ検査・原形辞書検査を含む）。
8. `docs/P2_MOCK_SET_2_4_REVIEW.md` を最終状態に合わせて更新（C-2）。
9. 実ブラウザ確認 → コミット。

コミットは「検査追加」「A-1/A-2」「B（セット別）」「文書更新」で分ける。

## 10. 検証

```powershell
py -3 scripts/build_q1_p2_mock_2_data.py
py -3 scripts/build_q1_p2_mock_3_data.py
py -3 scripts/build_q1_p2_mock_4_data.py
py -3 scripts/enrich_flashcard_fields.py
py -3 scripts/check_q1_data.py
py -3 scripts/check_p2_mock_data.py
npm test
```

実ブラウザ（`?g=pre2` で起動）:

- 第2回〜第4回の本番形式4択で、正答が①に偏っていない
- Q11・Q12 の熟語カードに**不変化詞パネルと仲間例**が出る（A型）
- Q13〜Q15 のB型は連鎖のみで、パネルが出ないのが正しい
- 差し替えた語のフラッシュカードに意味・例文・語源・IPA・音声が揃う
  （音声は `assets/audio/vocab/pre2/mock-*` を作っていなければ再生ボタンが無音で止まる。
  既知の未対応で、本計画の範囲外）

## 11. リスク

- **差し替えが新しい重複を生む。** 語も熟語も、準2級の全語句・`lemmas.json` の原形・
  全配信セットの熟語 phrase と突き合わせ直す。検査を先に足す（9-1）のはこのため。
- **B-1 は設問を作り直す作業**なので、正答一意性のリスクが再び立つ。6節で
  「文脈で一意にする」を守り、9-6のレビューを省かない。
- A型の `particleSense` を偏らせると、辞書側の仲間例不足で `npm test` が落ちる（4.3）。
  8件の選定時点で particle と sense を散らす。
- `ipa` の再取得は Datamuse 依存。取得できない語は**推測で埋めず**、
  差し替え候補を変えるか空のままにする（既存方針）。
