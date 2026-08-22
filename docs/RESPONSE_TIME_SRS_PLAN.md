# 解答時間を使った間隔復習アルゴリズムの実装計画

対象: `static/mode-q1.js`（意味チェック `renderCheck` と Leitner ブロック）
状態: 実装済み（2026-08-20）。`npm test` の `scripts/check-response-time-srs.cjs` で契約を固定している。

## 0. 問題

意味チェックの4択で解答時間を計測・表示するようにした（[:2313](../static/mode-q1.js)）が、**値はセッション内の表示にしか使われず、保存もスケジュール反映もされていない**。そのため「10秒迷って正解した語」と「1.5秒で即答した語」が同じ 14 日ルートに乗る。

| 目標 | 現状の担保 |
| --- | --- |
| 正答率の改善 | 誤答で `leitnerStage=0` / `nextReviewAt=null`（[:487](../static/mode-q1.js)）＋ `wrongCount` で出題順を前倒し |
| 解答時間の短縮 | **なし**（表示のみ） |
| 間隔復習 | Leitner `[1,3,7,14]`（[:434](../static/mode-q1.js)） |

## 1. 方針：解答時間で Again / Hard / Good を自動採点する

ボタンは増やさない。1タップの正誤と反応時間だけで Anki の Hard 相当を機械的に付ける。

```
誤答            → stage = 0,      nextReviewAt = null      （現状どおり）
正答かつ遅い    → stage 据え置き, next = ladder[stage]      （新設 = Hard）
正答かつ速い    → stage + 1,      next = ladder[stage]      （現状 = Good）
```

**長い間隔に進めるのは「速く正解できた語」だけ**になり、3つの目標が昇段条件という1本の軸に揃う。

間隔の値そのものは `[1,3,7,14]` から変えない。`meaningIntervalLabel` は `nextReviewAt - lastAnsweredAt` の日数をラベルへ逆算している（[:710](../static/mode-q1.js)）ため、**ホームの間隔別内訳・カードUIは無改修で動く**。ここを崩さないことが本計画の制約。

## 2. 「遅い」の判定

絶対値だけだと語の長さと選択肢の日本語量で歪み、相対値だけだと「全体が遅い日」に誰も Hard にならない。両方を組み合わせる。

```js
// ponytail: 閾値はこの3つだけ。初期値は暫定、実データを見て調整する前提
const RT_HARD_FLOOR_MS = 8000;   // これ未満は絶対に Hard にしない
const RT_HARD_CEIL_MS  = 20000;  // これ以上は無条件 Hard
const RT_HARD_RATIO    = 1.6;    // 今セッション中央値の何倍から遅いとみなすか
const RT_OUTLIER_MS    = 60000;  // 中断とみなし中央値の母数から除外（判定は Hard 扱い）

function rtGrade(ms, medianMs) {
  if (ms >= RT_HARD_CEIL_MS) return "hard";
  if (ms < RT_HARD_FLOOR_MS) return "good";
  return ms > RT_HARD_RATIO * medianMs ? "hard" : "good";
}
```

中央値は**そのセッションで既に正解した語の RT** から取り、5件未満のあいだは `RT_HARD_FLOOR_MS` を代用する。新しい永続データを増やさずに済み、ユーザーが速くなれば中央値も下がって閾値が自動追従する。

### 計測起点の修正（前提のバグ）

回答時間の起点は常に `session.checkShownAt`（問題表示時刻）とする。音声ボタンのクリック時刻は計時に使わない。

- **スケジュール判定には常に `checkShownAt` 起点の値を使う。**
- 画面表示も「出題から n 秒で解答」に統一し、表示用と判定用で起点を分けない。

## 3. 保存するもの

`progress.items[key]` に2フィールド追加。`DEFAULT_ITEM_STATE`（[:446](../static/mode-q1.js)）と `itemState`（[:456](../static/mode-q1.js)）へ既存フィールドと同じ流儀で足す。

```js
s.lastMs = ms;                                              // 直近の反応時間
s.avgMs  = s.avgMs ? Math.round(s.avgMs * 0.7 + ms * 0.3)   // 指数移動平均（正答時のみ更新）
                   : ms;
```

用途は3つ。①出題順の重み、②結果画面で「前回 8.2秒 → 今回 4.1秒」を出す（時間短縮の可視化そのものが目標）、③閾値を後から実データで詰めるための素材。

未設定（`undefined`）でも Good 相当として動くよう書き、**既存レコードの移行処理は行わない**。

## 4. 出題順（`weightedOrder` [:1650](../static/mode-q1.js)）

`wrongCount` 降順のみ → 3信号の合成スコア降順へ差し替える。

```
score = 2 * wrongCount
      + 1 * (直近が hard か ? 1 : 0)
      + 0.5 * 期限超過日数
```

期限超過を入れるのは、`MEANING_SESSION_SIZE = 30` から溢れた語が延々と後回しになるのを防ぐため。ソートの安定性に依存した現行のコメント（確率抽選が不要な理由）はそのまま有効。

## 5. leech（沼語）の頭打ち

`wrongCount >= 5` の語は `leitnerStage` を 1（＝3日）で上限とする。5回落ちる語を14日後に送るのは正答率をいちばん悪化させる経路なので、ここだけ例外を置く。

## 6. 変更箇所

| ファイル / 関数 | 変更 |
| --- | --- |
| `mode-q1.js` 定数ブロック（:434 付近） | `RT_*` 4定数と `rtGrade()` を追加 |
| `DEFAULT_ITEM_STATE` (:446) / `itemState` (:456) | `lastMs` / `avgMs` を追加 |
| `recordMeaningResult` (:474) | 第3引数 `ms` を受け、Hard 分岐・leech 上限・`lastMs`/`avgMs` 更新 |
| `renderCheck` の選択ハンドラ (:2311) | 判定用 RT（`checkShownAt` 起点）を算出して `recordMeaningResult` へ渡す／セッションRTログへ push |
| `weightedOrder` (:1650) | 合成スコアへ差し替え |
| `saveResume` (:326) / `restoreSession` (:367) | 問題表示起点の `responseElapsedLog` を保存・復元（旧 `audioElapsedLog` は読み込み時のみ互換扱い） |
| `appendCheckFeedback` | 解答直後に「前回までの平均 n 秒」を併記（`avgMs` の読み手） |

UI改修・データ改修・新規ファイルなし。実質50〜70行。

## 7. 検証

- `npm test`（`node --check` と既存の `scripts/check-*.cjs` 一式）。
- `rtGrade` と昇段ロジックは純関数として切り出し、`node` で走る最小の assert 自己チェックを1つ残す（境界: 7999 / 8000 / 20000ms、中央値5件未満、`avgMs` 未設定）。
- 実ブラウザで意味だけ復習を1セット通し、①遅い正答で `nextReviewAt` が伸びないこと、②誤答で `要再確認` に戻ること、③ホームの間隔別内訳の数が壊れないことを localStorage で確認する。

## 8. 見送った案

| 案 | 理由 |
| --- | --- |
| SM-2 / FSRS | ease factor と可変間隔を入れると `MEANING_INTERVALS` のラベル逆算（1日/3日/7日/14日の固定表示）が壊れ、ホームUIまで改修が波及する。精度差に対して改修量が大きい。1日あたりの復習量が制御できなくなって初めて検討する |
| RT を連続値で間隔の倍率にする | 同上でラベルが崩れる。加えて閾値2本より調整が難しい |
| ラダーを `[1,3,7,14,30]` へ延長 | 「速い正答だけが上に行く」設計を入れた後、14日到達語が溜まってから足せば足りる |
| RT のユーザー基準値を永続化 | セッション中央値で足りる。永続化すると級・セット間で基準が混ざる問題を新たに抱える |
