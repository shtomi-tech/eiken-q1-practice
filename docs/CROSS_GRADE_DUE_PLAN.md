# 他の級の復習待ちをホームに表示する実装計画

きっかけ: 生徒（冨田翔太）から「英検1級の復習の間隔がリセットされている」との申告。調査の結果**データは無傷**で、最後に開いたセットがテーマ別（`eikentopic-set-1`）だったため、ホームの間隔復習カードがテーマ別プール（学習済み12語・残りは未実施）を表示していたことが原因だった。1級側には464語の記録があり、うち43語が期限到来していた。

## 1. 目的

間隔復習カードは**現在選択中の級のプールだけ**を見る（`meaningPracticeSummary` → `pooledData()` → `currentGrade()`, [mode-q1.js:670](../static/mode-q1.js)）。級を切り替えると中身が丸ごと入れ替わるため、生徒には「記録が消えた」と見える。

**他の級に期限到来の語句があるとき、その件数をカード内に出す。** 記録が別の級に残っていることが一目で分かり、その級へ移動できるようにする。

## 2. 方式：語彙JSONを読まずに進捗だけで数える

期限到来数は `progress.items[key].nextReviewAt` だけで算出できる。`items` の記録は意味練習で解答したときにしか作られない（[recordMeaningResult](../static/mode-q1.js)）ので、**「学習済みかどうか」の判定を別途行う必要がない**。

- 語彙JSON（全22セット）を追加で fetch しない。`loadPooledItems` は級単位で全セットを読むため、他の級ぶんまで呼ぶと表示のたびに十数回の通信が増える。これは避ける。
- 読むのは `progressFor(datasetId)` のみ。ホーム描画は既に全セットぶん `progressFor` を呼んでおり（`datasetSummary`）、`withProgressReadCache` で1描画1回にメモ化されるため、**追加コストは実質ゼロ**。

### 追加する関数（`static/mode-q1.js`）

```
// 級ごとの「期限到来語句数」と、その中で最も多いセットを返す。現在の級は含めない。
function otherGradeDueCounts(now = Date.now())
  → [{ grade, label, count, datasetId }]  // count 降順
```

- 対象は `datasetGrades()`（[:1358](../static/mode-q1.js)）から現在の級を除いたもの。
- 各級の `gradeDatasetIds(grade)` について `progressFor(id).items` を走査し、`nextReviewAt` が現在時刻以下の件数を数える。
- `label` は `datasetGradeLabel(grade)`（manifest の `shortLabel`。1級 / 2級 / 準1級 / 準2級 / 1級テーマ別）。
- `datasetId` は、その級で期限到来が最も多いセット（同数なら manifest の並び順で先頭）。移動先に使う。
- 0件の級は返さない。

## 3. 表示（`meaningMission` 内, [:1299](../static/mode-q1.js)）

間隔別内訳の下に1行追加する。

```
他の級の復習待ち   [ 1級 43語 ]  [ 準1級 8語 ]
```

- チップは `button`。押すと `switchDataset(datasetId)` でその級のセットへ移動し、ホームを再描画する（既存の `switchDataset` をそのまま使う, [:1015](../static/mode-q1.js)）。
- 表示は上位3級まで。0件のときは行ごと出さない（通常時にノイズを増やさない）。
- 文言は「他の級の復習待ち」。テーマ別セットを開いているときは「1級 43語」と出るため、生徒は記録が残っていることを確認できる。

### DESIGN.md 準拠
- チップの高さは44px以上を確保する。
- 件数は色だけで区別しない（数値＋級名のテキストを常に持つ）。
- キーボード操作で到達・実行できること（`button` 要素をそのまま使う）。
- 既存の `meaningMissionIntervalGrid` と視覚的な重さを揃え、主CTA（意味だけ復習を始める）より弱い階層にする。

## 4. あわせて直す小さな点

現在のカード見出しは「意味だけ復習」で、どのプールを見ているかは説明文（`${datasetSectionName()}の収録セットをまとめ…`）の中にしかない。**見出し自体に級名を入れる**（例:「意味だけ復習（1級テーマ別）」）。1行の変更で、切り替わったことに気づきやすくなる。

## 5. 検証

- `scripts/check-meaning-mission-ui.cjs` を拡張する（既存の静的検査スクリプト。`meaningMission` の本体を抜き出して構造を assert する方式）。
  - `meaningMission` 本体に他級表示のチップが含まれること。
  - チップが `switchDataset` を呼ぶこと。
  - `otherGradeDueCounts` が `loadPooledItems` / `fetch` を呼ばないこと（語彙JSONを読まない方式の維持）。
- 実ブラウザ（`py -3 -m http.server 8061`）で、テーマ別セットを選んだ状態のホームに「1級 ○語」が出ること、押すと1級のセットへ移動して内訳が戻ることを確認する。スマホ幅でチップが折り返しても崩れないことも見る。
- 期限到来が0件のときに行が出ないことを確認する。

## 6. 作業順

| # | 作業 | 完了条件 |
| --- | --- | --- |
| 1 | `otherGradeDueCounts` を追加 | 進捗だけで件数が出る（fetchなし） |
| 2 | `meaningMission` にチップ行を追加、見出しに級名を入れる | 表示・遷移が動く |
| 3 | `styles.css` にチップのスタイル（44px以上・折返し） | スマホ幅で崩れない |
| 4 | `check-meaning-mission-ui.cjs` を拡張 | `node scripts/check-meaning-mission-ui.cjs` が通る |
| 5 | 実ブラウザ確認（§5） | 期限到来あり／なしの両方で確認 |
| 6 | コミット・push | Pages 配信が更新される |

## 7. 決定事項と実装状況

- **チップの遷移先は「その級で期限到来が最も多いセット」**に決定（2026-08-18）。級ごとの最終セットを保存する変更は行わない。
- テーマ別セットを1級の間隔復習と分離した設計は維持する（今回の申告はこの分離の副作用だが、分離は意図した仕様）。

### 実装済み（未コミット）
| ファイル | 内容 |
| --- | --- |
| `static/mode-q1.js` | `otherGradeDueCounts()` を追加。`meaningMission` にチップ行を追加。見出しを「意味だけ復習（1級テーマ別）」の形に変更 |
| `static/styles.css` | `.meaningMissionOtherGrades` / `.meaningMissionOtherGradeList` / `.meaningMissionOtherGrade`（`button.ghost` を継承、min-height 44px、折返し） |
| `scripts/check-meaning-mission-ui.cjs` | チップの存在・`switchDataset(row.datasetId)` の呼び出し・見出しの級名・`otherGradeDueCounts` が fetch / `loadPooledItems` を呼ばないことを assert |

### 検証結果
- `node scripts/check-meaning-mission-ui.cjs` → OK
- 実ブラウザ（テーマ別セットを選択、1級43語句・準1級8語句を期限到来として投入）
  - 見出し「意味だけ復習（1級テーマ別）」、チップ「1級 43語句」「準1級 8語句」が件数の多い順に表示
  - チップの高さ44px、`aria-label`「1級の復習待ち43語句へ移動」
  - チップを押すと `eiken1-mock-1` へ切り替わり、見出しが「意味だけ復習（1級）」、残るチップは「準1級 8語句」だけになる
  - コンソールエラーなし。375px幅でも横スクロールなし（チップ幅94px / 100px）
- 未確認: 期限到来0件のときに行が出ないこと（コード上は `otherDue.length` で分岐）。スクリーンショットはブラウザペイン非表示のため取得できず、DOM計測で代替した。
