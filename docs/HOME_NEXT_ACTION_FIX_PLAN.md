# ホームの「次にやること」修正計画

> 対象: `eiken-q1-practice`。UX摩擦監査（2026-08-25、1級・過去問2026年度第1回で実機確認）で特定した重大な摩擦3件を直す。
> 関連: [HOME_LAYOUT_UNIFICATION_PLAN.md](HOME_LAYOUT_UNIFICATION_PLAN.md)（並び順の共通基準）/ [STATE_TRANSITIONS.md](STATE_TRANSITIONS.md) / [../DESIGN.md](../DESIGN.md)
> 状態: 計画（未着手）。作成日 2026-08-25。

## 1. 直す摩擦

| # | 摩擦 | 実測した事実 |
|---|---|---|
| ① | 他セットの進捗・途中保存が見えず、ラベルが実態と食い違う | `eiken_q1_progress_eiken1-mock-3` に第9問・暗記カード段階の途中保存があるのに、Unitカードは「全—問・—語／0 / —問／**この回を始める**」と表示する |
| ② | 同じ状態で、完了画面とホームの推奨が逆転する | 第5問を誤答で終えると完了画面は「間違えた1問を復習する」を主CTA。一覧へ戻ると主CTAは「第1問を学習する」に変わり、誤答は「！要復習1問」に格下げされる |
| ③ | 主CTAの直後の理論値カードが作業リストを押し下げる | 375px幅でホーム全高6801px（約8.4画面）。`.vocabGoalCard` が732px、「問題一覧」は top 3331px |

## 2. 決定事項

| 項目 | 決定 | 却下した案 |
|---|---|---|
| ②の統一方向 | **ホーム側を復習優先に揃える**（完了画面 [mode-q1.js:3699](../static/mode-q1.js) が正、ホーム [mode-q1.js:1857](../static/mode-q1.js) を直す） | 完了画面を新規優先へ／閾値ルールの共有（根拠となるデータが現時点でない） |
| ③の範囲 | **「このペースで学べる語句」だけ折りたたむ**。`.vocabGoalCard` は C層のまま動かさない | カードごと問題一覧の下へ移す（`HOME_LAYOUT_UNIFICATION_PLAN.md` のC層規定と kobun 側の改訂を伴う） |
| ①の総数の出典 | **`data/manifest.json` に総数を持たせ、`check_q1_data.py` で実データとの一致を検証する** | 他セットJSONの遅延読み込み（初回ホームで最大36ファイルの追加取得と「—」の残存） |

③でC層を動かさないため、**`HOME_LAYOUT_UNIFICATION_PLAN.md` と kobun-vocab-learning は本計画の対象外**になる。

## 3. 変更①: Unitカードに途中保存と総数を出す

### 3-1. `data/manifest.json`（正本への追記）

`q1` の各エントリへ2キーを追加する。既存キー（`label` / `shortLabel` / `vocabUrl` / `questionsUrl`）と `defaultDatasetId` は変更しない。

```json
"eiken1-mock-3": {
  "label": "英検1級 模試 第3回",
  "shortLabel": "1級",
  "vocabUrl": "data/vocab_1_mock-3.json",
  "questionsUrl": "data/questions_1_mock-3.json",
  "totalQuestions": 25,
  "totalVocabulary": 100
}
```

**値の定義（ここを外すと現在セットと他セットで数字がずれる）**

アプリの表示元は `state.qList.length` と `allVocabularyItems().length` （[mode-q1.js:2447](../static/mode-q1.js)）。`state.qList` は questions.json ではなく **vocab側の `q` から作られる**（[mode-q1.js:1567-1576](../static/mode-q1.js)）。したがって manifest の値は次で定義する。

- `totalQuestions` = vocab の `words` + `idioms` に現れる **`q` の異なり数**
- `totalVocabulary` = vocab の `words` + `idioms` の **要素数**（ユニーク語句数ではなく設問スロット数）

全19セットで確認済みの値（本計画作成時に実測。`questions.json` の設問数とも全セット一致した）:

| セット群 | totalQuestions | totalVocabulary |
|---|---:|---:|
| 2級 3セット | 17 | 68 |
| 準2級 3セット＋模試第1回 | 15 | 60 |
| 準1級 3セット | 18 | 72 |
| 1級 過去問3セット | 22 | 88 |
| 1級 模試第1〜5回 | 25 | 100 |
| 医療福祉 基礎試験 | 15 | 60 |

テーマ別セット（`eikentopic-*`）は `manifest.q1` に登録されていないため対象外。

### 3-2. `scripts/check_q1_data.py`

1. `check_dataset()` の戻り値へ `counts: {"totalQuestions": …, "totalVocabulary": …}` を追加する。読み込み済みの `items` と、そこから作る `q` の集合で算出できるため追加I/Oはない（[check_q1_data.py:92-106](../scripts/check_q1_data.py)）。
2. `main()` で、manifest の申告値と算出値を比較し、**不一致・欠落はエラーで落とす**。既存の `set(q1) != EXPECTED_IDS` チェックの直後に置く。エントリ内の追加キーは既存チェックに触れない（キー集合の検査は `manifest` の第1階層のみ, [:260-264](../scripts/check_q1_data.py)）。
3. `--update-manifest` オプションを追加し、算出値を manifest へ書き戻す（19セット×2値＝38値の手入力を避け、再実行可能にする）。既定は検証のみ。書き出しは `ensure_ascii=False`・インデント2・末尾改行で、既存の整形を変えない。

### 3-3. `static/mode-q1.js`

**`datasetSummary()`（[:2297-2311](../static/mode-q1.js)）**

- `totalQuestions` / `totalVocabulary` を `isCurrent ? 実測 : manifest の申告値` にする。現在セットは従来どおり実データから出し、manifest 値は他セット用のフォールバックとして使う（申告値が無い場合のみ `null` → 「—」を維持）。
- `hasResume` を追加する。判定は既存の再開可否と同じ条件を使い、重複実装しない: `progress.resume` が存在し、`RESUMABLE_MODES.has(mode)` かつ `resumeStageAllowed(mode, stage)` かつ `stage !== "done"`（[:344-351](../static/mode-q1.js), [:731-736](../static/mode-q1.js)）。`currentResume()` は `state.progress` 固定なので、`resume` を引数に取る小関数へ切り出して両方から呼ぶ。`resumeUnavailable` はグローバルな現在セットの状態なので、他セット判定には使わない。
- `status` の優先順位を `cleared → review → inProgress → resumable → notStarted` にする。`learned` が1問もなくても途中保存があれば `resumable`。

**`datasetPrimaryLabel()`（[:2313-2319](../static/mode-q1.js)）**

- `status === "resumable"` → `続きから（第n問）`。`n` は `resume.q`。
- 既存の `inProgress` / `isCurrent` の「続きから」も、`resume` があれば同じく設問番号を付ける。

**`datasetUnitCard()`（[:2322-2360](../static/mode-q1.js)）**

- 進捗行の下に、途中保存があるとき `.datasetUnitCardResume` として `途中保存：第n問・STEP 1 暗記カード 4/4` を出す。文言は既存の `resumeDescription()`（[:711-729](../static/mode-q1.js)）を再利用し、書式を二重管理しない。
- `ariaParts` に同じ文字列を追加する。
- 色だけに頼らないというDESIGN.mdの規範どおり、状態は必ず文言併記（`✓ CLEAR` / `！要復習n問` / `途中保存：…`）。

**CSS（`static/styles.css`）**

- `.datasetUnitCardResume` を追加。既存の `.datasetUnitCardReview` と同じ字送り・サイズで、色は Muted（Clayは要復習に予約済み）。左罫は Ink の `current` と衝突するため足さない。

### 3-4. `DESIGN.md`

「問題セットUnitカード（`.datasetUnitCard`）」節へ、状態を5値（未着手／途中保存あり／学習中／要復習あり／CLEAR）に増やす旨と、途中保存の文言併記を追記する。

## 4. 変更②: 主CTAの優先順位を復習優先へ統一

`renderHomeContent()` の `primary` 決定（[mode-q1.js:1856-1890](../static/mode-q1.js)）の分岐順を入れ替える。

```
現在: coreResume → nextQ → reviewQs → canStartFinal → hasMeaningDue → もう一周
変更: coreResume → reviewQs → nextQ → canStartFinal → hasMeaningDue → もう一周
```

- 復習の `why` を差し替える。現在の「まちがえた設問をつぶすと、最終チェックが解放されます。」は、未学習が残る段階では成立しない（最終チェックの解放条件は全設問の `solvedCorrect`, [:2451-2455](../static/mode-q1.js)）。→ **「間違えた設問です。忘れないうちに1問ずつ確認します。」**
- 復習が主CTAのとき、未学習が残っていれば**二次CTAとして `次の設問へ（第n問）`** を並べる。完了画面と同じ構成（[:3700-3707](../static/mode-q1.js)）にし、日次目標（今日8問）が復習で止まらない逃げ道を同じ形で残す。二次は `secondaryCta`（塗りなし）にして、1画面の塗りCTAを1つに保つ。
- 間隔復習カードの `meaningMissionCta` は、**主CTAが存在する限り** `secondaryCta` へ落とす。塗りのまま残すのは `primary === null`（通常学習が終わり、間隔復習が実質の主導線になる分岐）のときだけ。実測で、ホーム上に Ink と Clay の塗りCTAが2つ同時に出る状態があった。

  > 初版はこの条件を「主CTAが復習系のときだけ」と誤記しており、実装レビュー時に Ink主CTA＋Clay間隔復習CTA の並びが残っていることを実測で確認して修正した。

## 5. 変更③: ペース予測を折りたたむ

`vocabGoalCard()` の `forecast`（[mode-q1.js:2138-2165](../static/mode-q1.js)）を `<details>` にする。

- `<summary>` に **「このペースで学べる語句」＋到達予想の1行**（`このペースなら14,000語まであと4,996語`）を残し、開かなくても現在ペースの結論が読めるようにする。
- 折りたたむのは、到達予想日の行（`.vocabForecastDate`）、5期間の内訳グリッド（`.vocabForecastGrid`）、「理論上の学習量です…」の注記。`<summary>` の中身はそのまま開閉ボタンの読み上げ名になるため、結論の1行までに絞る。
- 既定は閉。開閉状態は保存しない（`localStorage` のキーを増やさない）。
- 読み込み中（`!ready`）は現状どおり `英検1級通常問題の語句を読み込み中…` を出す。この段は折りたたまない。
- `h4#vocabForecastTitle` を `summary` へ置き換える。`<details>` には role がなく `aria-labelledby` が効かないため、展開後は付けない（読み込み中の `div` 版のみ従来どおり）。
- CSS: `.vocabForecast > summary` に `min-height: 44px`・`cursor: pointer`・`list-style` の指定を足す。開閉マーカーは記号を併記し、色だけで開閉を示さない。

既存の `scripts/check-vocab-goal-ui.cjs` は `vocabularyForecast` / `1週間後` / `1年後` / `現在、このアプリの英検1級通常問題には` の**文字列の存在**しか見ていない（[:47-50](../scripts/check-vocab-goal-ui.cjs)）。`<details>` 化しても文字列は残るため、このテストは修正不要。

## 6. 検証

### 6-1. 追加する自動検証 `scripts/check-home-priority-ui.cjs`

既存の `.cjs` と同じ、ソース文字列に対する契約テストにする。`package.json` の `test` 連鎖の末尾へ追加する。

1. `renderHomeContent` の本文で、`reviewQs.length` の出現位置が `nextQ` を主CTAにする分岐より**前**にあること（②の回帰）。
2. 完了画面 `renderDone` 側の順序は `scripts/check-unit-learning-ui.cjs:87` が既に担保しているため重複させない。両者が同順である旨をコメントで相互参照する。
3. `datasetSummary` の本文に `hasResume` があり、`datasetPrimaryLabel` が `resumable` を扱うこと（①）。
4. `datasetUnitCard` が `resumeDescription` を呼ぶこと（文言の二重管理を防ぐ）。
5. `data/manifest.json` の `q1` 全エントリに `totalQuestions` / `totalVocabulary` が正の整数であること。
6. `vocabGoalCard` の本文に `el("details"` と `el("summary"` があること（③）。
7. `styles.css` に `.datasetUnitCardResume` と `.vocabForecast > summary` の規則があること。

### 6-2. 既存の検証

```powershell
py -3 scripts/check_q1_data.py
npm test
```

`npm test` は `node --check` と17本の契約テストを含む。①のmanifest追記は `check_q1_data.py` 側で数値一致まで検証される。

### 6-3. 実ブラウザでの4状態確認

`py -3 -m http.server 8062 --bind 127.0.0.1` で起動し、**1級と、級をまたいで2級のどちらか1つ**で確認する。

| 状態 | 確認 |
|---|---|
| 初回開始 | 進捗ゼロのプロファイル（別ブラウザプロファイルか別ポート）で、Unitカードが全セット「全n問・n語／0 / n問／この回を始める」になる。「—」が1つも出ない |
| 途中再開 | 他セットに途中保存を作ってからホームへ戻り、そのカードに「途中保存：第n問・…」と「続きから（第n問）」が出る。押すと同じ場所へ戻る |
| 完了 | 1問を誤答込みで解き切り、完了画面→一覧へ戻った後の主CTAが**両画面とも復習**になる。二次CTAに「次の設問へ」がある |
| 次の学習 | 塗りCTAが同時に2つ出ない。375px幅で問題一覧までのスクロール量を実測し、改善前（top 3331px）と比較して記録する |

あわせて、375px / 1280px でコンソールエラーなし・横スクロールなし・キーボードで `<summary>` が開閉できること・タップ対象44px以上を確認する。

## 7. 完了条件

1. `py -3 scripts/check_q1_data.py` と `npm test`（新規 `check-home-priority-ui.cjs` を含む）が通る。
2. ホームの主CTAが、完了画面と同じ状態で同じ行動を指す。
3. 全19セットのUnitカードに問題数・語句数が出る。「—」は manifest 未記載時のフォールバックとしてのみ残る。
4. 途中保存のあるセットが、切り替え前にカード上で識別できる。
5. 375px幅で、問題一覧までのスクロール量が改善前より減っていることを実測値で示す。
6. `DESIGN.md` のUnitカード節が5状態に更新されている。

## 8. やらないこと

- `.vocabGoalCard` の位置移動、`HOME_LAYOUT_UNIFICATION_PLAN.md` とC層規定の改訂、kobun-vocab-learning への波及。
- 語彙目標カードの長期予測そのものの削除・数式変更。
- 保存データ形式の変更。`eiken_q1_progress_<datasetId>` のスキーマ、SRSの間隔、`studyPlanV1`、クラウド同期の内容は一切触らない（①は既存の `resume` を**読むだけ**）。
- 完了画面の「Step Complete!」の文言、「次の設問へ（第1問）」が順番の次に見える件。監査で挙げたが本計画の3件には含めない（別途）。
- テーマ別セット（`eikentopic-*`）。`manifest.q1` に登録がない。

## 9. リスク・未確認

- **`data/manifest.json` は正本**であり、19セット全てに追記する。`--update-manifest` の書き出しで既存の整形（キー順・インデント）が変わらないことを、実行後に `git diff` で確認する。差分が数値追加のみでない場合は手動追記へ切り替える。
- 他セットの `hasResume` 判定は `progressFor()` 経由で localStorage を読む。ホーム描画は `withProgressReadCache` の同期処理内で行われる（[mode-q1.js:1597-1600](../static/mode-q1.js)）ため、`await` を挟まないこと。
- 旧形式の途中記録（`RESUMABLE_MODES` 外）は `hasResume=false` として扱う。現在セットでは `resumeRecoveryMessage` で説明されるが、他セットのカードには出さない。`STATE_TRANSITIONS.md` 不変条件7（旧記録を削除しない）に反しないことを確認する。
- ②の変更後、誤答が溜まった状態で日次の新規問題目標が進みにくくなる可能性がある。二次CTAで逃げ道は残すが、実利用での影響は**未検証**。1〜2週間使ってから、日次実績の推移で判断する。
- `STATE_TRANSITIONS.md` 1章の「計17セット」は現在の manifest（19セット）と食い違っている。本計画の対象外だが、①で manifest を触るため気付いた点として記録する。
