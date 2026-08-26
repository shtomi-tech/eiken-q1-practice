# 準2級の自作模試セットを3回分追加する実装計画（eikenp2-mock-2 / -3 / -4）

対象: `scripts/build_q1_p2_mock_{2,3,4}_data.py` /
`data/questions_p2_mock-{2,3,4}.json` / `data/vocab_p2_mock-{2,3,4}.json` /
`data/manifest.json` / `scripts/check_q1_data.py` / `scripts/check_p2_mock_data.py` /
`scripts/check-core-image-data.cjs`（C型があるときのみ）/ `README.md`
状態: 未着手

## 0. 前提と方針

- 準2級は現在4セット（過去問 2025-2 / 2025-3 / 2026-1 と自作模試 mock-1）。
  **追加する3セットも過去問を引用しない自作模試とする。** 未収録の過去問原本が
  リポジトリに無く、引用は公開リポジトリのままでは扱えないため
  （[P2_MOCK_SET_PLAN.md](P2_MOCK_SET_PLAN.md) 5.3 と同じ扱い）。
- 追加後は準2級7セット（105問・420語句）になる。**新規語彙は180件**で、
  4節の重複制約が mock-1 のときより一段厳しい。ここが本計画の最大の作業量。
- 手順は mock-1 の計画を踏襲する。**mock-1 の時点から変わった前提が3つある**ので、
  そこだけ本計画で上書きする（4節・5節）。

| 変更点 | mock-1 時点 | 現在 |
| --- | --- | --- |
| 原形辞書 `data/lemmas.json` | 無し | 有り。語彙追加が `npm test` を落とし得る（4.2） |
| 熟語の核心イメージ | 無し | 全配信セットの熟語に `coreImage` か `cReasons` が必須（4.3） |
| `check_p2_mock_data.py` | mock-1 決め打ち | 複数セット対応へ一般化が必要（5.1） |

## 1. IDと命名

`DATASET_ID_RE` が許すIDは `\d{4}-\d+` / `mock-\d+` / `set-\d+` のみ
（[mode-q1.js:34](../static/mode-q1.js)）。`mock-2` / `mock-3` / `mock-4` はこの範囲。

| datasetId | label | shortLabel | questionsUrl | vocabUrl |
| --- | --- | --- | --- | --- |
| `eikenp2-mock-2` | 英検準2級 模試 第2回 | 準2級 | `data/questions_p2_mock-2.json` | `data/vocab_p2_mock-2.json` |
| `eikenp2-mock-3` | 英検準2級 模試 第3回 | 準2級 | `data/questions_p2_mock-3.json` | `data/vocab_p2_mock-3.json` |
| `eikenp2-mock-4` | 英検準2級 模試 第4回 | 準2級 | `data/questions_p2_mock-4.json` | `data/vocab_p2_mock-4.json` |

`datasetSetKind()` が `-mock-` を見て「模試」に分類し、`datasetSetLabel()` が
「第2回」「第3回」「第4回」を出す。**UI（HTML/CSS/JS）の改修は不要。**

## 2. 成果物

1. `scripts/build_q1_p2_mock_{2,3,4}_data.py` — 1セット1本（1級模試と同じ運用）。
   [build_q1_p2_mock_1_data.py](../scripts/build_q1_p2_mock_1_data.py) と同型で、
   **`CORE_IMAGES` を追加で持たせる**（4.3）。正本がこの1ファイルに集約される。
2. `data/questions_p2_mock-{2,3,4}.json` / `data/vocab_p2_mock-{2,3,4}.json` — 生成物（コミットする）。
3. `scripts/check_p2_mock_data.py` の複数セット対応（5.1）。
4. `data/manifest.json` / `scripts/check_q1_data.py` の `EXPECTED_IDS` / `README.md` の追記。
5. `docs/P2_MOCK_SET_2_4_REVIEW.md` — 正答一意性レビューの記録（5.2）。3セット分を1ファイルにまとめる。

## 3. 出題設計（1セットあたり）

| 項目 | 値 | 根拠 |
| --- | --- | --- |
| 設問数 | 15問 | 既存の準2級4セットと同じ |
| 語 / 熟語 | 10問 / 5問（語40件・熟語20件） | 既存の準2級セットの counts |
| 会話文（`A: ... B: ...`） | 6〜8問 | 既存4セットは 8/6/6/6。`check_p2_mock_data.py` が範囲を強制 |
| 設問文の長さ | 15〜35語 | 同上（機械チェックあり） |
| 語彙レベル | CEFR A2〜B1 相当 | 準2級相当 |
| 場面 | 学校・買い物・旅行・仕事・家庭・地域行事から散らす | 同一場面の連続を避ける。3セット横断でも偏らせない |

設問文の作法（mock-1 と同じ）:

- 空所は `(   )`（半角3スペース）1か所のみ。stem に正答語そのものを出さない。
- 4択は**同一品詞・同レベル**で揃える（品詞違いは消去法で解けてしまう）。
- 誤答は文脈上明確に成立しないものにする。「文法的には入るが意味が弱い」は不可。
- `translation` は全文の自然な和訳。空所記号 `( )` を残さない。
- `example` は見出し語をちょうど1回含む8語以上の短文。`exampleTranslation` はその和訳。

語彙データの各項目は既存の準2級ファイルと同形:

```
q, is_answer, word|phrase, pos, meaning, example, exampleTranslation, etymology
（熟語）type:"idiom", coreImage   （任意）ipa
```

- `ipa` は [enrich_flashcard_fields.py](../scripts/enrich_flashcard_fields.py) で付与する。
  `TARGET_PATTERN` は既に `p2_mock-\d+` を含むため**スクリプト側の変更は不要**。
  取得できないものは推測で埋めない。
- `etymology` はビルドスクリプトの `ETYMOLOGY` に持ち、欠落をビルド時に落とす。
  フラッシュカードの「語源・なりたち」行は `item.etymology` があるときだけ出るため必須。
- `collocation` はアプリが参照していないので付けない。

## 4. 語彙選定の制約（今回いちばん重い部分）

新規語彙は3セットで180件。**重複判定を後回しにすると差し替えが連鎖する**ので、
各セットとも設問を書く前に必ず 4.1〜4.3 を通す。

### 4.1 既存の準2級語彙と重複させない

意味だけ復習は級単位でプールされるため、重複すると同じ語が二重管理になる。
現在の準2級は4セット240語で、突き合わせ対象は積み上がる。

| 作るセット | 突き合わせ対象 |
| --- | --- |
| mock-2 | 既存240語 |
| mock-3 | 300語（mock-2 を含む） |
| mock-4 | 360語（mock-2・mock-3 を含む） |

`check_p2_mock_data.py` の重複検査は `vocab_p2_*.json` を glob するので、
**1セットずつ確定させてから次に進めば**自動的に前のセットも対象になる。
1級・準1級・2級との重複は級が違えばプールが別なので許容する（ただし 4.2・4.3 は別）。

### 4.2 `data/lemmas.json` の原形と衝突させない（新規の制約）

`scripts/check-lemma-headword.cjs`（`npm test` で実行）は `data/vocab_*.json` **全件**から
原形ごとの「出題形一覧」と「元の意味一覧」を集計し、`build_lemma_entries.py` の
`REVIEWED_MEANING_DIGEST` と照合する。**新語が `lemmas.json` の `lemmas` キー（259件）
または原形値（257件）に一致すると集計が変わり、`npm test` が落ちる。**

- 原則: **新語は `lemmas.json` の全キー・全原形値と一致しない語から選ぶ。**
  既存の準2級160語のうち32語はこの集合と重なっており、実際に起こり得る。
  一方 mock-1 の40語は0件なので、回避自体は可能。
- 選定直後に次で判定する（実装は 5.1 のチェックに組み込む）:

  ```
  新語の lower() ∈ set(lemmas.keys()) ∪ set(lemmas.values()) → 差し替え
  ```

- どうしても採りたい語が衝突する場合の追加作業（重いので原則避ける）:
  `py -3 scripts/build_lemma_entries.py --audit` で語義を確認 → 統合語義を決める →
  `REVIEWED_MEANING_DIGEST` を新しい digest に更新 → `lemmas.json` 再生成 →
  必要なら `assets/audio/lemma/<slug>.mp3` を追加 → `npm test`。
  **3セット分をまとめて1回で処理する**（セットごとに digest を更新し直さない）。

### 4.3 熟語の核心イメージ（新規の制約）

`scripts/check-core-image-data.cjs` は、manifest から配信される全セットの熟語に対し
**`coreImage` を付けるか `cReasons` に理由を書くかのどちらかを必須**にしている。
新規60熟語（20×3）は [CORE_IMAGE_AUTHORING.md](CORE_IMAGE_AUTHORING.md) に従ってA/B/Cへ分類する。

| 型 | 付けるもの |
| --- | --- |
| A 動詞＋不変化詞 | `chain` ＋ `particle` ＋ `particleSense`（`data/particle_images.json` に無い particle は使わない） |
| B 構成語から意味を導ける定型表現 | `chain` のみ |
| C 連鎖がこじつけになるもの | 何も付けず `check-core-image-data.cjs` の `cReasons` に phrase と理由を1行追記 |

機械側の主な規則: `chain` は2〜5要素、最終要素に `term` を置かない、`term` は小文字原形で
phrase と対応、`particleSense` は辞書にある id で `general` 不可、仲間例に自分自身を含めない。
同じ `particle` × `particleSense` を1セット内で使い回すほど、辞書側に必要な仲間例が増える
（`3 + (使用回数 - 1)`、上限6）ため、**1セット内で同じ sense に偏らせない。**

- 併せて、**同じ phrase が他の配信セットにもある場合は `coreImage` の有無を一致させる**
  必要がある。4.1 の準2級内重複回避に加え、**他級セットの熟語との phrase 重複も避ける**のが安全。
- `py -3 scripts/build_core_image_stub.py`（読み取り専用）で型と particle の候補を出せる。
- **`coreImage` は必ずビルドスクリプトの `CORE_IMAGES` に持たせる。**
  mock-1 は `coreImage` が JSON 側にしか無く、`build_q1_p2_mock_1_data.py` を再実行すると
  消える状態になっている。mock-2/3/4 で同じ轍を踏まない（mock-1 の是正は本計画の範囲外）。

## 5. 品質保証

### 5.1 機械チェック（`scripts/check_p2_mock_data.py` を一般化）

現状は `DATASET_ID = "eikenp2-mock-1"` 決め打ち。**セット定義をリスト化し
`data/vocab_p2_mock-*.json` を全件検査する形へ変える**（引数で単一セット指定も可。
3セットを1件ずつ作る間、対象を絞れると回転が速い）。
既存の検査項目（件数 15/40/20、正答項目1件、会話文6〜8問、設問文15〜35語、
正答語の非露出、4択の品詞一致、訳の空所記号、例文の語数・出現回数・骨格重複、
準2級既存語彙との重複）はそのまま全セットへ適用する。

**今回追加する検査:**

| 検査 | 落とすもの |
| --- | --- |
| 新語が `lemmas.json` のキー・原形値と一致しない | `npm test`（原形digest）を落とす語（4.2） |
| 全 `vocab_*.json` の熟語 phrase と重複しない | 配信セット間の `coreImage` 有無不一致（4.3） |

`surface_variants` / `example_skeleton` は `check_q1_data.py` から import して使い回す
（同じ正規化を二重実装しない）。

### 5.2 独立レビュー（省かない）

正答の一意性と英文の自然さは機械では落とせない。生成とは別のモデルに見せる。

- `codex:rescue` サブエージェントに **15問と4択だけ**を渡し（正答は伏せる）、
  各設問で成立する選択肢を挙げさせる。2つ以上成立した設問は差し替える。
- **セットごとに実施する。**3セットまとめて最後に回さない（差し替えが4節の重複判定に
  跳ね返るため、確定していないセットの上に次を積まない）。
- 判定が割れた設問は、語を替えるのではなく**文脈を足して一意にする**。
- 結果は `docs/P2_MOCK_SET_2_4_REVIEW.md` にセット別の節で、どの設問をなぜ差し替えたかまで残す。

### 5.3 由来の明示

`meta.source` に「AI生成（英検過去問の引用なし）・人手校閲」と書く。
UI上は「準2級・模試 第2回〜第4回」と表示され、過去問と区別できる。

## 6. 組み込み

1. `data/manifest.json` の `q1` に3エントリ追加（1節の表、`eikenp2-mock-1` の直後）。
   `totalQuestions: 15` / `totalVocabulary: 60`。
2. `scripts/check_q1_data.py` の `EXPECTED_IDS` に `"eikenp2-mock-2"` `"eikenp2-mock-3"`
   `"eikenp2-mock-4"` を追加。集合一致で検証しているため、追加しないと必ず落ちる。
3. `README.md`:
   - 冒頭「合計24セット」→「27セット」、「準2級の自作模試第1回」→「第1回〜第4回」
   - 間隔復習の表の準2級行 `60 / 240` → `105 / 420`
   - 対象データ節に `questions_p2_mock-{2,3,4}.json` / `vocab_p2_mock-{2,3,4}.json` を追記
   - スクリプト節に `build_q1_p2_mock_{2,3,4}_data.py` を追記、
     `check_q1_data.py`「24セット」→「27セット」、
     `check_p2_mock_data.py` の説明を「準2級自作模試（全回）の内容チェック」へ
4. `index.html` のキャッシュバスターは**変更不要**。`manifest.json` は `cache: "no-store"`
   で取得し（[mode-q1.js:61](../static/mode-q1.js)）、語彙・設問JSONは新規URLで既存キャッシュと
   衝突しない。JS/CSSを触った場合のみ `?v=` を上げる。

## 7. 音声（任意・別枠）

`generate_tts_1.py` の `pre2` は `vocab_p2_*.json` を拾うため、キーがあれば

```
py -3 scripts/generate_tts_1.py --grade pre2 --round mock-2
```

で `assets/audio/vocab/pre2/mock-2/` に生成できる（Azure Speech のキーが必要。`--round all` で一括）。
**現状 `assets/audio/vocab/pre2/` は過去問3回分のみで mock-1 の音声が無い**（1級は模試5回分すべて有り）。
音声が無くても再生はエラー時に停止するだけで学習は成立するので本計画では必須にしない。
生成するなら mock-1 も併せて埋めるのが自然。

## 8. 検証

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

- ホーム「準2級・模試」に「第1回」〜「第4回」が並ぶ
- 各カードで15問・60語、フラッシュカード→意味チェック→4択が最後まで通る
- 熟語カードに核心イメージが出る（C型は出ないのが正しい）
- 意味だけ復習の対象語句上限が 240 → 420 に増える
- 級固定（準2級）のまま他級が出ない、コンソールエラーなし

## 9. 作業順

**1セットずつ完成させてから次に進む**（4.1 の重複判定を積み上げるため、
3セット並行で作らない）。1セットあたり次の1〜7を回す。

1. 語彙60件を選定し、4.1（準2級の既存語彙）・4.2（`lemmas.json`）・
   4.3（全セットの熟語 phrase）の重複判定を**先に**通す。後戻りが一番大きい。
2. 15問の stem・4択・正答・和訳を作る。
3. 熟語20件をA/B/Cに分類し、`CORE_IMAGES` と（C型があれば）`cReasons` を書く。
4. `build_q1_p2_mock_N_data.py` を書いてJSON出力。
5. `check_p2_mock_data.py`（mock-2 の回で複数セット対応へ一般化）を通す。
6. `codex:rescue` で正答一意性レビュー → 差し替え → 4〜5を再実行。
7. `enrich_flashcard_fields.py` で ipa 付与。

8. mock-2 → mock-3 → mock-4 の順に 1〜7 を繰り返す。
9. manifest / `EXPECTED_IDS` / README を更新し、`check_q1_data.py` と `npm test`。
10. 実ブラウザ確認 → コミット → デプロイ（GitHub Pages）。

コミットは**セット単位で分ける**（3セットを1コミットにすると、後から
どの設問がどのレビューで直ったか追えなくなる）。組み込み（9）は最後に1コミット。

## 10. リスクと割り切り

- **生成した設問の正答一意性が最大のリスク。** 5.2 を省かない。1問でも二重解釈が
  残ると、生徒は正解しても誤答扱いになる。3セット分では見落としが増えるので、
  レビューをセットごとに区切る。
- **語彙180件を既存240語・原形辞書・全熟語 phrase と衝突させずに選ぶ制約**が
  mock-1 のときより明確に厳しい。準2級レベルの未使用語が枯れてきたら、同じ語の
  別語義でごまかさず、語と熟語の比率見直し（10/5 → 9/6 など）で逃がす判断が要る。
  **mock-4 まで作った時点で準2級は7セット420語**になるため、次に増やすときは
  レベル判定（NGSL 等の頻度リスト）の導入を先に検討する。
- 語彙レベルの妥当性は人手判断に依存する。
- 本計画は**過去問セットの追加ではない**。2026年度第2回などの過去問を入れる場合は
  原本の入手と著作権判断が別途必要で、手順もデータ作法も変わる。
