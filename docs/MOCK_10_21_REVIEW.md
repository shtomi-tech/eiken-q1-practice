# 英検1級 模試第10回〜第21回 作成・レビュー記録

## 対象

| datasetId | ビルドスクリプト | データ |
| --- | --- | --- |
| `eiken1-mock-10` | `scripts/build_q1_mock_10_data.py` | `data/questions_1_mock-10.json` / `data/vocab_1_mock-10.json` |
| `eiken1-mock-11` | `scripts/build_q1_mock_11_data.py` | `data/questions_1_mock-11.json` / `data/vocab_1_mock-11.json` |
| `eiken1-mock-12` | `scripts/build_q1_mock_12_data.py` | `data/questions_1_mock-12.json` / `data/vocab_1_mock-12.json` |
| `eiken1-mock-13` | `scripts/build_q1_mock_13_data.py` | `data/questions_1_mock-13.json` / `data/vocab_1_mock-13.json` |
| `eiken1-mock-14` | `scripts/build_q1_mock_14_data.py` | `data/questions_1_mock-14.json` / `data/vocab_1_mock-14.json` |
| `eiken1-mock-15` | `scripts/build_q1_mock_15_data.py` | `data/questions_1_mock-15.json` / `data/vocab_1_mock-15.json` |
| `eiken1-mock-16` | `scripts/build_q1_mock_16_data.py` | `data/questions_1_mock-16.json` / `data/vocab_1_mock-16.json` |
| `eiken1-mock-17` | `scripts/build_q1_mock_17_data.py` | `data/questions_1_mock-17.json` / `data/vocab_1_mock-17.json` |
| `eiken1-mock-18` | `scripts/build_q1_mock_18_data.py` | `data/questions_1_mock-18.json` / `data/vocab_1_mock-18.json` |
| `eiken1-mock-19` | `scripts/build_q1_mock_19_data.py` | `data/questions_1_mock-19.json` / `data/vocab_1_mock-19.json` |
| `eiken1-mock-20` | `scripts/build_q1_mock_20_data.py` | `data/questions_1_mock-20.json` / `data/vocab_1_mock-20.json` |
| `eiken1-mock-21` | `scripts/build_q1_mock_21_data.py` | `data/questions_1_mock-21.json` / `data/vocab_1_mock-21.json` |

各セット 25問 / 100語句（84語 + 熟語16）。品詞構成は既存の模試第7回〜第9回と同じ
（名詞7問・動詞7問・形容詞6問・副詞1問・句動詞4問）。

## 出典と権利

- **AI生成（英検過去問の引用なし）・人手校閲**。設問文・和訳・例文はすべて新規作成。
- 収録語の選定元は、ユーザー提供の市販単語集の見出し語一覧（Unit1 動詞 / Unit2 名詞 / Unit3 形容詞・副詞 / Unit4 句動詞）。
  見出し語のみを語彙プールとして使い、単語集の例文・訳・解説は一切転記していない。
- 語彙の割り当ては `docs/SET_PLAN_1_mock-10-21.md` が正本。

## 語彙の重複制約（3節）

`SKILL.md` 3節の3条件を、計画段階で mock-10〜21 の1,200語すべてについて一括判定した。句動詞は活用形の違いを吸収する正規化（不規則動詞表＋`lemmas.json`）でも突き合わせた。

- 同じ級の全既存語句（`data/vocab_1_*.json` 12セット・延べ960語）: 衝突 0
- 全配信セットの熟語 `phrase`（`data/vocab_*.json` 全件）: 衝突 0
- `data/lemmas.json` の canonical `lemmas` / 表示専用 `flashcardLemmas` の全キー・全値: 4件が衝突したため差し替え

| 元の語 | 差し替え後 | 箇所 |
| --- | --- | --- |
| nomination | ordeal | mock-13 Q5 |
| scatter | lampoon | mock-14 Q11（正解を sever へ変更） |
| renounce | perish | mock-18 Q10 |
| flourish | avenge | mock-18 Q13 |

さらに、活用形が既存セットの熟語と実質的に同じになる句動詞2件も差し替えた（`phrase` の完全一致検査は通るが、同じ句動詞の重複になるため）。

| 元の句 | 差し替え後 | 箇所 | 衝突相手 |
| --- | --- | --- | --- |
| buy off | bawl out | mock-14 Q25 | `bought off`（mock-1） |
| strike up | butter up | mock-19 Q25 | `struck up`（mock-5） |

## 作成中の語の差し替え

| セット | 元の語 | 差し替え後 | 理由 |
| --- | --- | --- | --- |
| mock-11 Q18 | forlorn | diffident | 同一セットの副詞 `forlornly` と紛らわしい |
| mock-12 Q19 | erudite | atrocious | 同一セットの名詞 `erudition` と紛らわしい |
| mock-14 Q25 | gloat over | leaf through | 同一セット Q13 の動詞 `gloat` と紛らわしい |
| mock-16 Q6 | inoculation | conflagration | 同一セット Q11 の動詞 `inoculate` と紛らわしい |
| mock-17 Q18 | virulent | poignant | 同一セット Q4 の名詞 `virulence` と紛らわしい |
| mock-18 Q11 | prone | fathom | 単語集の動詞ページにある `prone` は形容詞のため |
| mock-18 Q25 | creep up on | come by | 既存 `crept up on`（mock-2）と実質重複 |
| mock-19 Q24 | load up on | tear into | mock-15 の `loaded up` と同じ句動詞のため |
| mock-20 Q19 | contingent | strident | 同一セット Q5 の名詞 `contingency` と紛らわしい |
| mock-21 Q16 | indulgent | fervent | 同一セット Q9 の動詞 `indulge` と紛らわしい |

差し替え語はいずれも重複3条件を再判定して衝突なしを確認した。

## 独立レビュー（6節）

生成に使ったモデルとは別のモデルに、**設問文と4択だけ**（正答を伏せた状態）を渡して
成立する選択肢を列挙させた。

- レビュー実施モデル: **GPT-5 / GPT-5 Codex**（`codex:codex-rescue` サブエージェント経由、3回）
- 入力: 75問の `stem` と `choices` のみ。`answerIndex`・`meaning`・`translation` は渡していない。

### 1巡目（75問）

複数成立 5問 / 正解なし 0問 / 英文の不自然さ 1問。

| 問題 | 指摘 | 対応 |
| --- | --- | --- |
| mock-11 Q13 | `swirled` と `churned` が両立 | 設問文を「バターになるまでクリームをかき回す」文脈へ変更 |
| mock-11 Q16 | `poised` と `conciliatory` が両立 | 「何週間もの敵対的なやり取りの後」を追加し、ダミーを `perfunctory` へ差し替え |
| mock-11 Q20 | `propitious` と `momentous` が両立 | 最上級＋「近代史で」の文脈を追加し、ダミーを `facetious` へ差し替え |
| mock-11 Q21 | `moves so elusively` が不自然 | 設問文を差し替え |
| mock-12 Q14 | `fathom` と `decipher` が両立 | 「換字式暗号」の文脈を追加し、ダミーを `inter` へ差し替え |
| mock-12 Q18 | `appalling` と `acrid` が両立 | 「目にしみた」の文脈を追加し、ダミーを `immaculate` へ差し替え |

### 2巡目（修正した6問）

一意 2問 / 複数成立 4問。Q13・Q20・Q14・Q18 は文脈追加だけでは一意にならなかったため、
上表のとおりダミー語の差し替えを行った（差し替え語は重複3条件を再判定済み）。

### 3巡目（再修正した5問）

**全5問が一意**。英文の自然さについて2件の指摘があり、両方とも反映した。

- mock-11 Q13: `until it thickened into butter` → `until the butter finally formed`
- mock-11 Q21: `stayed elusively out of reach` → `hovered elusively beyond the reach of investigators`

## 独立レビュー（mock-13〜15）

同じ手順で、生成に使ったモデルとは別のモデルへ75問の `stem` と `choices` だけを渡した。

- レビュー実施モデル: **GPT-5 / Codex**（`codex:codex-rescue` サブエージェント経由、2回）

### 1巡目（75問）

複数成立 3問 / 成立なし 1問。

| 問題 | 指摘 | 対応 |
| --- | --- | --- |
| mock-13 Q18 | `dreary` と `insufferable` が両立 | ダミーを `decrepit` へ差し替え |
| mock-14 Q22 | `goofed off` と `milled about` が両立 | 設問文を「so badly ... that both were dismissed」へ変更 |
| mock-15 Q1 | `frenzy` と `fervor` が両立 | ダミーを `protrusion` へ差し替え |
| mock-15 Q23 | `egged on him` の語順が不正で成立する選択肢なし | 目的語を名詞句にして `egged on the young apprentice` の語順へ修正 |

### 2巡目（修正した4問）

**全4問が一意**。英文の不自然さの指摘なし。

## 独立レビュー（mock-16〜18）

- レビュー実施モデル: **GPT-5 / GPT-5.4 Codex**（`codex:codex-rescue` 経由、4巡）

### 1巡目（75問）

複数成立 10問 / 成立なし 0問 / 英文の軽微な不自然さ 2件。

| 問題 | 指摘 | 対応 |
| --- | --- | --- |
| mock-16 Q10 | `flaunted` と `recanted` が両立 | 「以前の結論が誤りだったと認めた」を追加 |
| mock-16 Q12 | `antagonized` と `disconcerted` が両立 | 文脈追加のうえ、最終的にダミーを `presided` へ差し替え（`disconcerted` は同セット Q8 のダミーへ移動） |
| mock-16 Q19 | `effusive` と `fervent` が両立 | ダミーを `chronic` へ差し替え |
| mock-16 Q21 | `gallantly` と `vehemently` が両立 | 設問を「denounced ... shouting down two interruptions」へ変更 |
| mock-16 Q23 | `chewed over` と `waved aside` が両立 | 「利点を細かく比較しながら」を追加 |
| mock-17 Q2 | `harbinger` と `incarnation` が両立 | ダミーを `decorum` へ差し替え |
| mock-17 Q17 | `circumspect` と `nonchalant`（後に `strident`）が両立 | ダミーを `insufferable` と `propitious` へ差し替え |
| mock-18 Q8 | `maim` と `mesmerize` が両立 | `mesmerize` を同セット Q9 のダミーへ移し、Q8 は `scorn` に差し替え |
| mock-18 Q16 | `implausible` のほか `vacuous` `ludicrous` が両立 | ダミーを `nonchalant` `voracious` へ差し替え |
| mock-18 Q18 | `insubstantial` と `abysmal` `elliptical` が両立 | ダミーを `languid` `chivalrous` へ差し替え |

### 2〜4巡目

修正のたびに同じ手順で再レビューし、**最終的に全75問が一意**であることを確認した。
差し替えたダミー語はいずれも重複3条件（同級既存語・全級の熟語 `phrase`・`lemmas.json`）を再判定済み。

## 独立レビュー（mock-19〜21）

- レビュー実施モデル: **GPT-5 / GPT-5.4 Codex**（`codex:codex-rescue` 経由、3巡）

### 1巡目（75問）

複数成立 5問 / 成立なし 0問。

| 問題 | 指摘 | 対応 |
| --- | --- | --- |
| mock-19 Q14 | `manipulate` と `defuse` が両立 | 設問を「敵対する当事者間の緊張を暴力沙汰の前に」へ変更 |
| mock-20 Q18 | `extrinsic` と `ulterior` が両立 | 「寄付者が懸命に隠そうとしている」を追加のうえ、ダミーを `scrumptious` `poised` へ差し替え |
| mock-20 Q21 | `gingerly` と `warily` が両立 | `warily` を mock-21 へ移し、設問に「ひび割れを広げないよう」を追加 |
| mock-21 Q12 | `refute` と `squash` が両立 | `squash` を同セット Q13 のダミーへ移し、Q12 は `ensue` に差し替え |
| mock-21 Q16 | `complacent` `incendiary` が両立 | 設問を「応援演説のように読める」へ変更し、ダミーを `ludicrous` へ差し替え |

### 2〜3巡目

再レビューで残った mock-20 Q18 と mock-21 Q21 をさらに修正し、**最終的に全75問が一意**であることを確認した。

## 機械チェック

最終編集後の状態で実行し、いずれも成功。

```
py -3 scripts/build_q1_mock_10_data.py   # 各セット
py -3 scripts/enrich_flashcard_fields.py --file data/vocab_1_mock-10.json   # IPA +84
py -3 scripts/check_q1_data.py           # Q1 data: OK（全44セット）
py -3 scripts/audit_question_set.py eiken1-mock-10 ... eiken1-mock-21
                                         # ERROR 0 / WARN 0（12セット）
npm test                                 # exit 0
```

正答位置の分布（`audit_question_set.py` の出力）:

| セット | ①②③④ |
| --- | --- |
| mock-10 | 6 / 7 / 6 / 6 |
| mock-11 | 6 / 6 / 6 / 7 |
| mock-12 | 8 / 6 / 5 / 6 |
| mock-13 | 6 / 7 / 6 / 6 |
| mock-14 | 8 / 5 / 7 / 5 |
| mock-15 | 6 / 7 / 6 / 6 |
| mock-16 | 8 / 7 / 6 / 4 |
| mock-17 | 8 / 5 / 6 / 6 |
| mock-18 | 6 / 6 / 6 / 7 |
| mock-19 | 8 / 4 / 8 / 5 |
| mock-20 | 7 / 6 / 6 / 6 |
| mock-21 | 7 / 6 / 6 / 6 |

## 熟語の核心イメージ

各セット16件すべてに `coreImage` を付与した（12セットで192件、C型 0件）。
不変化詞辞書 `data/particle_images.json` に無い前置詞（`through` / `for` / `against` / `at` / `with` / `aside`）を
とる熟語は、`particle` を付けず連鎖のみのB型として扱った。
辞書への変更は1件のみ: mock-20 で `out` / `express` を2件が参照するため、仲間例に `cry out` を1件追加した（3件→4件）。

## 未実施・要確認

- **暗記カードの原形表示（4.5節）**: 出題形が `-ed` の動詞（`eschewed`・`ousted`・`tyrannized` など）について、
  `data/lemmas.json` の `flashcardLemmas` へ表示専用の原形対応を追加していない。
  `npm test` の原形辞書契約は通っているが、暗記カードは出題形のまま表示される。
- **実ブラウザ確認（8節）**: 未実施。
- **音声（MP3）**: 未生成。
- **commit / push / deploy**: 未実施。
