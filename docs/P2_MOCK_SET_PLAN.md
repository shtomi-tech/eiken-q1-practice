# 準2級の自作模試セット（eikenp2-mock-1）を追加する実装計画

対象: 新規 `scripts/build_q1_p2_mock_1_data.py` / `data/questions_p2_mock-1.json` /
`data/vocab_p2_mock-1.json` / `data/manifest.json` / `scripts/check_q1_data.py` / `README.md`
状態: 実装済み（2026-08-20、未コミット）

## 0. 目的

準2級の問題セットを1つ増やす。**過去問の原本はなく、設問・語彙をすべて新規に生成する。**
過去問文は一切引用しないため、公開リポジトリのまま扱える。

## 1. IDと命名

`DATASET_ID_RE` が許すIDは `\d{4}-\d+` / `mock-\d+` / `set-\d+` の3種のみ
（[mode-q1.js:34](../static/mode-q1.js)）。これを外れると `gradeOf()` が null を返し、
**級固定フィルタからも意味だけ復習のプールからも丸ごと外れる**。

| 項目 | 値 |
| --- | --- |
| datasetId | `eikenp2-mock-1` |
| label | `英検準2級 模試 第1回` |
| shortLabel | `準2級` |
| questionsUrl | `data/questions_p2_mock-1.json` |
| vocabUrl | `data/vocab_p2_mock-1.json` |

`datasetSetKind()` が `-mock-` を見て「模試」に分類し、ホームでは
「準2級・模試」の小見出しに `datasetSetLabel()` が「第1回」と表示する。**UI側の改修は不要。**

## 2. 成果物

1. `scripts/build_q1_p2_mock_1_data.py` — `QUESTIONS` と `DETAILS` をベタ書きし、
   JSON 2本を出力する。[build_q1_mock_1_data.py](../scripts/build_q1_mock_1_data.py) と同型で、
   出力先と件数の検証だけ準2級向けに変える。正本がこの1ファイルに集約され、再生成できる。
2. `data/questions_p2_mock-1.json` / `data/vocab_p2_mock-1.json` — 生成物（コミットする）。
3. `scripts/check_p2_mock_data.py` — 生成セット専用の内容チェック（5節）。
4. `data/manifest.json` / `scripts/check_q1_data.py` / `README.md` の追記。

## 3. 出題設計

| 項目 | 値 | 根拠 |
| --- | --- | --- |
| 設問数 | 15問 | 既存の準2級3セットと同じ |
| 語 / 熟語 | 10問 / 5問（語40件・熟語20件） | `vocab_p2_2026-1.json` の counts |
| 会話文（A: / B:） | 6問 | 既存の準2級3セットは6問・6問・8問。本番の傾向に合わせる |
| 語彙レベル | CEFR A2〜B1 相当 | 準2級相当 |
| 場面 | 学校生活・買い物・旅行・仕事・家庭・地域行事から散らす | 同一場面の連続を避ける |

設問文の作法（既存セットに合わせる）:

- 空所は `(   )` 1か所のみ。stem に正答語そのものを出さない。
- 1〜2文、15〜35語程度。会話文は `A: ... B: ...` を1行に収める。
- 4択は**同一品詞・同レベル**で揃える（品詞違いは消去法で解けてしまう）。
- 誤答は文脈上明確に成立しないものにする。「文法的には入るが意味が弱い」は不可。
- `translation` は全文の自然な和訳。空所記号 `( )` を残さない。

語彙データ（`vocab_p2_mock-1.json`）の各項目は既存の準2級ファイルと同じ形にする。

```
q, is_answer, word|phrase, pos, meaning, example, exampleTranslation
（任意）ipa, etymology, collocation
```

- `ipa` は [enrich_flashcard_fields.py](../scripts/enrich_flashcard_fields.py) の
  `TARGET_PATTERN` に `vocab_p2_mock-\d+\.json` を足して Datamuse から取得する。
  取得できないものは**推測で埋めない**（同スクリプトの方針を踏襲）。
- `etymology` は手書き（ビルドスクリプトの `ETYMOLOGY` に持ち、欠落をビルド時に検出）。
  フラッシュカードの「語源・なりたち」行は `item.etymology` があるときだけ出るため必須。
  `collocation` は既存データにはあるがアプリが参照していないので付けない。
- 空所は既存の準2級3セットと同じ `(   )`（半角3スペース）で書く。
- `example` は見出し語をちょうど1回含む8語以上の短文、`exampleTranslation` はその和訳。

## 4. 語彙の選び方

- **既存の準2級3セット180語と重複させない。** 意味だけ復習は級単位でプールされるため、
  重複すると同じ語が二重に管理される。5節の機械チェックで落とす。
- 1級・準1級のセットとの重複は問題にしない（級が違えばプールが別）。
- 頻度リスト（NGSL 等）によるレベル判定は**今回は入れない**。レベルのばらつきが
  実際に問題になってから導入する。

## 5. 品質保証

原本がないため、既存の [check_q1_data.py](../scripts/check_q1_data.py) だけでは足りない。
同スクリプトは過去問を正しい前提として**構造しか見ていない**（4択・番号連番・
語彙と選択肢の対応・意味重複）。内容側を別に見る。

### 5.1 機械チェック（`scripts/check_p2_mock_data.py` 新規）

生成セットだけを対象に、失敗したら非ゼロ終了する。

| 検査 | 落とすもの |
| --- | --- |
| 正答語が stem に出現していない | 答えが本文に書いてある設問 |
| 4択の `pos` が全て一致 | 品詞で消去法が効く設問 |
| 既存の全 `vocab_p2_*.json` と表層が重複しない | プールの二重管理（`surface_variants` を再利用） |
| `translation` に `( )` `（　）` が残っていない | 訳の作り忘れ |
| `example` に見出し語がちょうど1回・8語以上 | 例文の使い回し・短すぎ |
| 同一セット内で `example` の骨格が重複しない | 例文の使い回し |
| 語40件・熟語20件・15問 | 件数ずれ |

`surface_variants` / `example_skeleton` は `check_q1_data.py` から import して使い回す
（同じ正規化を二重実装しない）。

### 5.2 独立レビュー

機械では落とせない「正答の一意性」と「英文の自然さ」は、生成とは別のモデルに見せる。

- `codex:rescue` サブエージェントに **15問と4択だけ**を渡し（正答は伏せる）、
  各設問で成立する選択肢を挙げさせる。2つ以上成立した設問は差し替える。
- 判定が割れた設問は、語を替えるのではなく**文脈を足して一意にする**。
- レビュー結果は `docs/P2_MOCK_SET_REVIEW.md` に残し、どの設問をなぜ差し替えたか追えるようにする。

### 5.3 由来の明示

`meta.source` に「AI生成（英検過去問の引用なし）・人手校閲」と書く。
UI上は「準2級・模試 第1回」と表示され、過去問と区別できる。

## 6. 組み込み

1. `data/manifest.json` の `q1` に1エントリ追加（1節の表）。並びは準2級3回の直後。
2. `scripts/check_q1_data.py` の `EXPECTED_IDS` に `"eikenp2-mock-1"` を追加。
   ここは集合一致で検証しているため、追加しないと必ず落ちる。
3. `README.md`:
   - 冒頭の「合計22セット」→「23セット」、`scripts/check_q1_data.py` の説明も同様
   - 対象データ節に `data/questions_p2_mock-1.json` / `vocab_p2_mock-1.json` を追記
   - 間隔復習の表の準2級行（51/45/54 と 180）に模試1回分（+15問・+60語）を反映
   - 自作模試であること（過去問ではないこと）を1行明記
4. `index.html` のキャッシュバスターは**変更不要**。`manifest.json` は `cache: "no-store"`
   で取得し（[mode-q1.js:61](../static/mode-q1.js)）、語彙・設問JSONは通常の fetch だが
   **今回は新規URLのため既存キャッシュと衝突しない**。JS/CSSを触った場合のみ `?v=` を上げる。

## 7. 検証

```powershell
py -3 scripts/build_q1_p2_mock_1_data.py
py -3 scripts/enrich_flashcard_fields.py   # ipa 付与（TARGET_PATTERN 拡張後）
py -3 scripts/check_q1_data.py
py -3 scripts/check_p2_mock_data.py
npm test
```

実ブラウザ（`?g=pre2` で起動）:

- ホームに「準2級・模試」の見出しと「第1回」カードが出る
- カードを開くと15問・60語、フラッシュカード→意味チェック→4択が最後まで通る
- 意味だけ復習の対象語句上限が 180 → 240 に増える
- 級固定（準2級）のまま他級が出ない、コンソールエラーなし

## 8. 作業順

1. 語彙60件を選定し、既存180語との重複チェックを先に通す（後戻りが一番大きいため最初）
2. 15問の stem・4択・正答・和訳を作る
3. `build_q1_p2_mock_1_data.py` を書いてJSON出力
4. `check_p2_mock_data.py` を書いて通す
5. `codex:rescue` で正答一意性レビュー → 差し替え → 2〜4を再実行
6. `enrich_flashcard_fields.py` の対象拡張と ipa 付与
7. manifest / EXPECTED_IDS / README を更新し、`check_q1_data.py` と `npm test`
8. 実ブラウザ確認 → コミット → デプロイ（GitHub Pages）

## 9. リスクと割り切り

- **生成した設問の正答一意性が最大のリスク。** 5.2 のレビューを省かない。
  1問でも二重解釈が残ると、生徒は正解しても誤答扱いになる。
- 語彙レベルの妥当性は人手判断に依存する。頻度リスト導入は次段階。
- 2セット目以降が必要になったら `mock-2` として同じ手順を繰り返す。
  ビルドスクリプトは回ごとに1本（1級模試と同じ運用）。
