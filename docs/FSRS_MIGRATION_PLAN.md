# 間隔復習を ts-fsrs（FSRS-6）へ全面移行する実装計画

対象: 「意味だけ復習」の間隔算出。現行は固定Leitnerはしご `LEITNER_LADDER = [1, 3, 7, 14, 30, 60, 120]`（[static/src/30-unit-progress.js:2](../static/src/30-unit-progress.js)）。
これを ts-fsrs（FSRS-6）へ置き換える。**本書は計画のみ。実装は含まない。**

前提: 2026-09-09 に A案（はしごの4段→7段延長）を実装・デプロイ済み（`abda5eb`）。本計画はその上に載る。

## 0. 目的と非目標

**目的**: 語ごとの記憶モデル（安定性・難易度）に基づく間隔算出へ移行し、同じ保持率をより少ない復習回数で達成する。固定はしごでは「どの語も同じ速度で間隔が伸びる」ため、易しい語に過剰な復習を、難しい語に不足した復習を割り当てている。

**非目標（今回やらない）**
- パラメータ最適化（optimizer）。ts-fsrs はスケジューラのみで、21パラメータの再学習機能を持たない。**既定パラメータ固定**で運用する。
- 通常学習（`units` 側の進捗）の変更。今回触るのは意味だけ復習の `progress.items` のみ。
- 反応時間ロジック（`rtGrade` / `medianMs` / `avgMs`）の廃止。**Rating への写像元として継続利用する**（§2.3）。

## 1. 事前調査の結果（実測値）

### 1.1 ライブラリ

| 項目 | 実測値 |
| --- | --- |
| パッケージ | `ts-fsrs@5.4.2`（`FSRSVersion` = `v5.4.2 using FSRS-6.0`） |
| ライセンス | MIT |
| 依存 | なし（`dependencies` 無し） |
| UMD | `dist/index.umd.js` / **72,009 bytes**（minified 版は配布されていない） |
| UMDグローバル名 | **`FSRS`**（`factory(global.FSRS = {})`） |
| 既定値 | `request_retention=0.9` / `maximum_interval=36500` / `enable_fuzz=false` / `enable_short_term=true` / `w.length=21` |
| Rating | `Manual=0, Again=1, Hard=2, Good=3, Easy=4` |
| State | `New=0, Learning=1, Review=2, Relearning=3` |
| 学習ステップ既定 | `learning_steps=["1m","10m"]` / `relearning_steps=["10m"]` |

主要API: `fsrs(params)` → スケジューラ、`createEmptyCard(now)` → 初期カード、`scheduler.next(card, now, rating)` → `{card, log}`。
カードのフィールド: `due, stability, difficulty, elapsed_days, scheduled_days, reps, lapses, learning_steps, state, last_review`。

**⚠ 実装時に判明**: `learning_steps`（当日ステップの何段目か）は README に記載が無いが**保存必須**。落とすとカードが `Learning` 状態から永久に抜けられず、`scheduled_days` が 0 のままになる（実装中に実際に踏んだ）。

### 1.2 実測したスケジュール（fuzz無効・Good連続）

ローカルで UMD を読み込み実行した結果:

| 設定 | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- |
| `short_term=false, rr=0.9` | 3日 | 14日 | 57日 | 196日 | 586日 | 1559日 |
| `short_term=false, rr=0.85` | 4日 | 31日 | 173日 | 773日 | 2859日 | 9071日 |
| **`short_term=true, rr=0.9, max=180`** | **10分**(Learning) | **2日** | **11日** | **46日** | **163日** | **181日**(上限) |

- 成熟カード（Good×3, S=56.96, D=2.10）に対する分岐: `Hard=141日 / Good=196日 / Again=3日`（`short_term=false`）。
- 成熟カード（Good×5）に `Again`: `state=Relearning`、**due は10分後**、`lapses=1`、`S=2638→4.72` へ低下。
- `maximum_interval:180` 指定時の実測 `scheduled_days` は **181**（丸めのため+1）。上限の検査は `<= maximum_interval + 1` で書くこと。

**判断**: `enable_short_term=false` は初回正解でいきなり3日、2回目で14日と伸びが急すぎ、現行の学習体験（1日→3日）から乖離する。**`enable_short_term=true` を採用**する（§2.2）。

### 1.3 現行実装の読み取り面（変更の継ぎ目）

`progress.items[key]` を読む箇所は以下がすべて。FSRS化で全部が影響を受ける。

| 箇所 | 用途 | 影響 |
| --- | --- | --- |
| [30-unit-progress.js:88 `recordMeaningResult`](../static/src/30-unit-progress.js) | 唯一の書き込み口 | **全面書き換え** |
| [30-unit-progress.js:46 `meaningResultState`](../static/src/30-unit-progress.js) | はしご算出 | 通常経路から外す（実装ではフォールバック専用として残置。§10） |
| [90-learn-flow.js:37 `isItemDue`](../static/src/90-learn-flow.js) | 期限判定 | `nextReviewAt` を維持すれば変更不要 |
| [90-learn-flow.js:44 `weightedOrder`](../static/src/90-learn-flow.js) | 出題順（`wrongCount`・`lastMs`・期限超過） | `wrongCount` → `lapses` へ寄せる（§2.5） |
| [50-vocab-pool.js:151 `meaningIntervalLabel`](../static/src/50-vocab-pool.js) | 内訳ラベル（`days` 完全一致） | **完全一致は成立しなくなる。バケット化必須**（§4） |
| [50-vocab-pool.js:125 `otherGradeDueCounts`](../static/src/50-vocab-pool.js) | 他級の期限到来数 | `nextReviewAt` 維持で変更不要 |
| [40-cloud.js:39](../static/src/40-cloud.js) | `{ [datasetId]: progress }` を丸ごと jsonb 保存 | スキーマ変更不要（自由形式JSON） |

**重要**: `nextReviewAt`（ISO文字列）を FSRS の `card.due` の写しとして**必ず残す**。これを保てば due 判定・他級集計・クラウド同期は無変更で通る。

## 2. 設計判断

### 2.1 vendoring の方式

- `static/vendor/fsrs/index.umd.js` に **バージョンを固定して実ファイルを置く**（CDN 参照にしない。オフライン・可用性のため）。既存の `static/vendor/harness/cloud.js` と同じ扱い。
- 出所・版・取得日を `static/vendor/fsrs/README.md` に記録し、MIT ライセンス本文を `static/vendor/fsrs/LICENSE` として同梱する。
- [index.html:29](../index.html) の `cloud.js` の直後、`mode-q1.js` の**前**に `<script src="static/vendor/fsrs/index.umd.js?v=5.4.2"></script>` を追加。`mode-q1.js` は IIFE 内で `globalThis.FSRS` を参照する。
- **⚠ 最大の落とし穴**: [.github/workflows/pages.yml](../.github/workflows/pages.yml) の `Prepare static files` は**コピーするファイルを明示列挙している**（`cp static/vendor/harness/cloud.js _site/static/vendor/harness/`）。ここに追記しないと**本番だけ 404 になり、スケジューラが丸ごと落ちる**。ローカルでは絶対に再現しない。§5 の T2 と T7 で対応する。

### 2.2 パラメータ

```
FSRS_PARAMS = {
  request_retention: 0.9,      // 既定。Anki既定と同じ
  maximum_interval: 180,       // 英検受験という用途に合わせて短縮（既定36500日は無意味）
  enable_short_term: true,     // 1m/10m の当日ステップを使う（§1.2の判断）
  enable_fuzz: true,           // 同日に大量の語が固まるのを防ぐ
}
```

- `maximum_interval: 180` は「試験までの期間を超える間隔を出さない」方針。実測どおり `scheduled_days` は最大181になる。
- `enable_fuzz: true` は**乱数を含む**ため、契約検査では期待値を範囲で書く（完全一致で書かない）。
- `w`（21パラメータ）は既定のまま。**将来 optimizer を入れる余地として、パラメータは1箇所の定数に集約しておく**。

### 2.3 正誤・反応時間 → Rating の写像

現行の `rtGrade()`（8秒未満=速い / 20秒以上=遅い / 中間は当該回の中央値の1.6倍で判定, [30-unit-progress.js:27](../static/src/30-unit-progress.js)）をそのまま流用する。

| 現行の結果 | Rating |
| --- | --- |
| 誤答 | `Rating.Again` (1) |
| 正答 かつ `rtGrade === "hard"` | `Rating.Hard` (2) |
| 正答 かつ `rtGrade === "good"` | `Rating.Good` (3) |
| — | `Rating.Easy` は**使わない**（自己申告UIが無く、根拠を作れないため） |

Easy を使わない判断は明示的に記録する。将来導入するなら「非常に速い正答（例: 中央値の0.5倍未満）」が候補になるが、**根拠が無いまま閾値を足さない**。

### 2.4 保存形式

`progress.items[key]` に FSRS カードを入れる。既存フィールドは**消さない**。

```js
{
  // 既存（維持）
  wrongCount, lastAnsweredAt, lastMs, avgMs,
  nextReviewAt,            // = new Date(card.due).toISOString()。due判定の正本として維持
  // 追加（FSRSカード）
  fsrs: {
    due,                   // ISO文字列
    stability, difficulty, // number
    elapsed_days, scheduled_days, reps, lapses, // number
    learning_steps,        // 当日ステップの段数。保存必須（§1.1の注記）
    state,                 // 0..3
    last_review,           // ISO文字列 or null
  },
  // leitnerStage は移行後は読まない（データは残す。§2.6・§7）
}
```

- `Date` オブジェクトは JSON 化で文字列になるため、**読み出し時に `new Date()` へ戻す変換層**（`toFsrsCard` / `fromFsrsCard`）を1箇所に置く。ここを散らかすと日付型のバグが必ず出る。
- `MEANING_PROGRESS_VERSION` を **2 → 3** に上げる（[30-unit-progress.js:15](../static/src/30-unit-progress.js)）。[20-storage.js:448](../static/src/20-storage.js) で保存済みセッションの復元可否に使われているため、**移行をまたぐセッション再開は破棄される**（意図した挙動。壊れた状態で再開させない）。

### 2.5 出題順（`weightedOrder`）の扱い

現行スコア: `2 * wrongCount + hard + 0.5 * overdueDays`。

- `wrongCount`（累計誤答）は FSRS の `lapses` とほぼ同義になる。**移行後は `lapses` を優先し、`wrongCount` はフォールバックとする**（`lapses ?? wrongCount`）。
- `difficulty`（1〜10）が使えるようになるためスコアへ加える案があるが、**これは新規の仕様追加**であり間隔移行とは別の判断。**今回はスコア式を変えない**（変更を最小に保つ）。

### 2.6 既存データの移行

既存ユーザーは `leitnerStage`（0〜6）と `nextReviewAt` を持つ。**過去の解答履歴からFSRS状態は再構成できない**（`progress.history` は直近500件かつ経過日数・gradeを持たない, [30-unit-progress.js:80](../static/src/30-unit-progress.js)）。したがって**ワンショットの近似移行**を行う。

方式: 現行はしごの間隔を「その語の安定性」とみなして初期値を与える。

| leitnerStage | 直前の間隔 | 付与する `stability` | `state` |
| --- | --- | --- | --- |
| 0（未到達 / 誤答直後） | — | カード作成のみ（`createEmptyCard`） | New |
| 1 | 1日 | 1 | Review |
| 2 | 3日 | 3 | Review |
| 3 | 7日 | 7 | Review |
| 4 | 14日 | 14 | Review |
| 5 | 30日 | 30 | Review |
| 6 | 60日以上 | 60 | Review |

- `difficulty` は `wrongCount` から近似する: `clamp(5 + wrongCount, 1, 10)`（誤答が多い語ほど難しい）。5が中庸値。
- `lapses = wrongCount`、`reps` は不明なので `leitnerStage + 1` を入れる（FSRS-6 の計算には使われないが、表示・診断のために保持）。
- **`nextReviewAt` は書き換えない**。移行によって「明日出るはずだった語が今日出る／来月に飛ぶ」が起きると、生徒には記録の破壊に見える。次回の解答時から FSRS が効き始める。
- 移行済みマークは既存の仕組みに合わせ `progress.migrations.fsrsV1` に記録する（[20-storage.js:253](../static/src/20-storage.js) の `pre1ProgressV1` と同じパターン）。**冪等**にすること。
- `leitnerStage` は**削除せず残す**。ロールバック（§7）で必要になる。

### 2.7 容量

`items` 1件あたり約7フィールド増える。1級だけで語彙3,704件、これが級×セット分の `progress` に分散する。localStorage は 5MB 程度が上限で、書き込みは既に try/catch で握り潰している（[20-storage.js:4](../static/src/20-storage.js)）。**移行前後で実際のバイト数を計測し、本書へ追記する**（T9）。閾値に近ければキー短縮の案があるが、**計測前に最適化しない**。

## 3. 変更対象ファイル

| ファイル | 変更 |
| --- | --- |
| `static/vendor/fsrs/index.umd.js` | 新規（vendoring, 72KB） |
| `static/vendor/fsrs/LICENSE` / `README.md` | 新規（出所・版・取得日） |
| `index.html` | `<script>` 追加、`mode-q1.js` / `styles.css` のキャッシュバスター更新 |
| `.github/workflows/pages.yml` | **vendor/fsrs のコピー追加**（§2.1の落とし穴） |
| `static/src/30-unit-progress.js` | スケジューラ本体の置換、パラメータ定数、変換層。`meaningResultState` は**削除せずフォールバック専用として残す**（T3の要件を満たすため。計画時の「削除」から変更） |
| `static/src/20-storage.js` | 移行関数 `migrateFsrsV1`、バージョン参照 |
| `static/src/50-vocab-pool.js` | `meaningIntervalLabel` のバケット化 |
| `static/src/80-home.js` | 内訳グリッドの説明文 |
| `static/src/90-learn-flow.js` | `weightedOrder` の `lapses` 参照 |
| `static/styles.css` | 内訳グリッドの列数 |
| `static/mode-q1.js` | 生成物（`npm run build`） |
| `scripts/check-response-time-srs.cjs` | はしご前提のアサートを FSRS 前提へ書き換え |
| `scripts/check-meaning-mission-ui.cjs` | ラベル必須リストをバケット名へ |
| `scripts/check-fsrs-vendor.cjs` | 新規（版固定・workflowコピー・script順の検査） |
| `scripts/check-fsrs-schedule.cjs` | 新規（スケジューラ契約・移行の検査） |
| `package.json` | `npm test` へ新規検査2本を追加 |
| `README.md` / `DESIGN.md` | 仕様記述の更新 |

## 4. UI変更

`MEANING_INTERVALS` の「1日後/3日後/…」という**完全一致ラベルは成立しなくなる**（FSRSは連続値を返す）。バケットへ置き換える。

| バケット | 条件（`nextReviewAt - lastAnsweredAt`） |
| --- | --- |
| 未実施 | `lastAnsweredAt` なし |
| 要再確認 | `nextReviewAt` なし、または1日未満（当日中） |
| 3日以内 | < 3日 |
| 1週間 | < 7日 |
| 2週間 | < 14日 |
| 1か月 | < 30日 |
| 3か月 | < 90日 |
| 半年以上 | >= 90日 |

- 8バケット。グリッドは `repeat(4, …)`（狭幅は `repeat(2, …)`）で 4×2 に割り切る。現在は9ラベル3×3（[static/styles.css:618](../static/styles.css)）。
- 説明文（[80-home.js:623](../static/src/80-home.js)）は「正解すると1→3→7→…日後へ間隔が延びます」から、**固定はしごを約束しない文言**へ変更する。例: 「正解の速さとこれまでの記録から、語句ごとに次回の日を決めます。」
- DESIGN.md の該当記述を更新する。色以外の状態表現・44px・キーボード操作の要件は現行のまま維持。

## 5. タスク

**単一レーン（`SERIAL_ONLY`）**。T1〜T9 は依存が強く、2レーンへ安全に分割できない（全タスクが `30-unit-progress.js` と生成物 `mode-q1.js` を書く）。`yuna` を2つ使わないこと。

| # | 種別 | 内容 | 受入条件 | 検証 |
| --- | --- | --- | --- | --- |
| T1 | IMPLEMENT | `ts-fsrs@5.4.2` の UMD・LICENSE・出所メモを `static/vendor/fsrs/` へ配置 | ファイルが npm 配布物と同一（sha256一致）。構文検査が通る | `node --check static/vendor/fsrs/index.umd.js` |
| T2 | IMPLEMENT | `index.html` へ `<script>` 追加（`cloud.js` の後、`mode-q1.js` の前）／**`pages.yml` の `cp` へ vendor/fsrs を追加** | ローカルとCIの両方でファイルが配信される | T10 の公開URL確認まで完了扱いにしない |
| T3 | IMPLEMENT | `30-unit-progress.js`: `FSRS_PARAMS` 定数、`toFsrsCard`/`fromFsrsCard` 変換層、`fsrsScheduler()`（遅延生成・シングルトン） | `globalThis.FSRS` 不在時に**学習を止めず**、A案のはしごへフォールバックする | T6 |
| T4 | IMPLEMENT | `recordMeaningResult` を FSRS へ置換。`meaningResultState` を削除し、Rating写像（§2.3）を実装。`nextReviewAt` は `card.due` の写しとして維持 | 誤答→Relearning（10分後）、正答→state遷移、`lapses` 増加が確認できる | T6 |
| T5 | IMPLEMENT | `migrateFsrsV1`（§2.6）。冪等・`nextReviewAt` 不変・`progress.migrations.fsrsV1` 記録。`MEANING_PROGRESS_VERSION` を 3 へ | 既存進捗JSONを2回流して結果が同一。`nextReviewAt` が1件も変わらない | T7 |
| T6 | IMPLEMENT | `scripts/check-fsrs-schedule.cjs` 新規。スケジューラ契約（Rating写像・上限181日・Again→Relearning・fuzz有効時は範囲判定）とフォールバック | `npm test` に組み込まれ通る | `npm test` |
| T7 | IMPLEMENT | `scripts/check-fsrs-vendor.cjs` 新規。①vendorの版が固定 ②`pages.yml` が vendor/fsrs をコピーする ③`index.html` の script 順が vendor→mode-q1 | 3項目すべてを assert。`pages.yml` の記述を消すと**必ず落ちる** | `npm test` |
| T8 | IMPLEMENT | UI（§4）: バケット化、CSS列数、説明文、`check-meaning-mission-ui.cjs` のラベル更新 | 8バケットが4×2で崩れない | T9 |
| T9 | VERIFY_ONLY | 実ブラウザ確認: 初回・途中再開・完了・次の学習の4状態、コンソールエラー0、スマホ幅、キーボード操作。**移行前後の localStorage バイト数を計測して本書へ追記**（§2.7） | 4状態で崩れ・エラーなし。容量の実測値が記録される | 手動 |
| T10 | VERIFY_ONLY | デプロイ後の公開URL検証: `static/vendor/fsrs/index.umd.js` が **200 で返る**、`mode-q1.js` に FSRS 呼び出しが含まれる | curl で両方確認 | 手動 |
| T11 | EXTERNAL_EVIDENCE | 実運用での効果測定（1日あたりの due 件数・正答率の推移） | — | `WAITING_FOR_EVIDENCE`。実装完了の条件に**含めない** |

## 6. 検査の要点（既存契約との衝突）

- [check-response-time-srs.cjs](../scripts/check-response-time-srs.cjs) は `meaningResultState(0,0,true,"good") → (1日, stage1)` 等を固定している。**T4で関数ごと消えるため、該当ブロックを書き換える**。`rtGrade` / `medianMs` / `nextAverageMs` のアサートは**残す**（Rating写像の入力として生き続けるため）。
- [check-meaning-mission-ui.cjs:113](../scripts/check-meaning-mission-ui.cjs) は「1日後」〜「120日後」の9ラベルを必須にしている。T8 でバケット名へ差し替える。
- `enable_fuzz: true` のため、**日数の完全一致を assert してはいけない**。検査では fuzz を無効にしたスケジューラを別途生成して境界を見る。

## 7. ロールバック

- `leitnerStage` を残すため（§2.6）、FSRS 呼び出しを外して A案のはしごへ戻せば**データを失わずに復帰できる**。この性質を壊す変更（`leitnerStage` の削除など）を後から入れないこと。
- 公開後に問題が出た場合の最短手順: 直前コミットへ revert → push（Pages が自動で再デプロイ）→ 公開URLで `mode-q1.js` の内容を確認。

## 8. リスクと未確定事項

| # | 内容 | 扱い |
| --- | --- | --- |
| R1 | `pages.yml` の `cp` 漏れで**本番だけスケジューラが落ちる** | T7 の検査で機械的に防ぐ。T3 のフォールバックで最悪でも学習は止まらない |
| R2 | 移行の近似（stability の割り当て）が実態と合わない | 初回解答時にFSRSが補正する。`nextReviewAt` を動かさないため体感の破壊は起きない |
| R3 | localStorage 容量 | **T9で実測済み**: 7語で 1,134 → 2,592 bytes（1語あたり約 +208 bytes、約2.3倍）。1級3,704語すべてが記録されても約0.9MBで、5MB上限には収まる。短縮最適化は不要と判断 |
| R4 | `enable_short_term=true` により10分後 due の語が発生し、同日に再出題される | 仕様として意図的（Anki と同じ）。ただし**生徒への説明が必要**。README に明記する |
| R5 | パラメータ最適化ができない | 既定パラメータは大規模な実レビューで学習済み。将来 optimizer を入れるなら `w` を差し替えられるよう §2.2 で定数を1箇所に集約しておく |
| R6 | `maximum_interval: 180` の妥当性 | 英検受験という用途からの判断。**未検証の仮定**。試験日が遠い生徒には短すぎる可能性がある |

## 9. 完了条件

T1〜T10 がすべて完了し、`npm test`（新規2本を含む）が最終編集後の状態で通り、公開URLで vendor ファイルが 200 を返し、4状態のブラウザ確認が済んだ状態。T11 は完了条件に含めない。

## 10. 実装結果（2026-09-09）

T1〜T9 を実装。`npm test`（27検査、うち新規2本）が最終編集後の状態で通過。

計画からの差分:

1. **`meaningResultState` を削除せず残した**。T3 が要求する「FSRS未読込時のフォールバック」に旧はしごが必要なため。既存の `check-response-time-srs.cjs` もそのまま通る。
2. **`learning_steps` の保存を追加**（§1.1の注記）。計画時点のフィールド一覧に漏れていた。
3. **`pages.yml` の `mkdir` は行を分けた**。既存の `check-lemma-headword.cjs` が元の `mkdir -p` 行を完全一致で固定しているため、そこへ追記せず `mkdir -p _site/static/vendor/fsrs` を別行にした。
4. **検査での realm 越え比較**。`vm.runInNewContext` 内で作られた `Date` / 配列は `instanceof` と `deepEqual`（prototype比較）が通らない。文字列化・duck typing で判定している。

ブラウザ実測（T9）:

- `globalThis.FSRS` = `v5.4.2 using FSRS-6.0`、コンソールエラー 0。
- 旧形式（leitnerStage 0〜6）の記録を投入して再読込 → `migrations.fsrsV1 = 1`、stability が 1/3/7/14/30/60 へ写り、**`nextReviewAt` は 7件すべて不変**、`leitnerStage` も保持。
- 内訳グリッド: 1100px幅で 4×2（各セル150px、文字あふれ無し）、720px以下で 2×4。

未実施: T10（デプロイ後の公開URL検証）、T11（運用での効果測定）。
