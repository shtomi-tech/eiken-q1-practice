# 使用者ごとに学習する級を1つに固定する実装計画

対象: `static/mode-q1.js` / 新規 `scripts/check-grade-scope.cjs`
状態: 実装済み（2026-08-20、未コミット）

## 0. 目的

使用者（生徒）ごとに最初に学習する級を1つ決め、**その級以外の情報を画面に出さない**。
級ボタン・他級の復習期限・他級の問題セットを消し、ホームをその級の学習だけに絞る。

## 1. 現状（調査結果）

アプリ内部はすでに級単位で動いている。

- `gradeOf(datasetId)` が `eiken1 / eiken2 / eikenp1 / eikenp2 / eikentopic` を返し
  （[mode-q1.js:111](../static/mode-q1.js)）、間隔復習のプール `pooledDataByGrade`、
  語彙目標カード、進捗キーはすべてこの級単位。
- 他級が露出しているのは実質3か所で、いずれも `availableDatasets()` / `DATASETS` が根。

| 箇所 | 関数 | 露出内容 |
| --- | --- | --- |
| 問題セット選択 | `datasetPicker()` / `datasetGrades()` | 級ボタン列と他級のUnitカード |
| 間隔復習カード | `otherGradeDueCounts()` | 「他の級に期限到来◯語」 |
| 起動時の既定 | `DEFAULT_DATASET_ID`（manifest の `eiken2-2026-1`） | 常に2級から始まる |

- 使用者の識別はすでにある。共有URL `?s=<id>&t=<token>` → `cloud.getSession()` →
  `storageStudentId`（[mode-q1.js:22](../static/mode-q1.js)）。localStorage は
  `scopedStorageKey()` で生徒ごとに分離済み。

## 2. 方式：`DATASETS` を起動時に絞る（下流は無改修）

級の判定・プール化・目標・進捗はすべて `DATASETS` から派生するため、
**`DATASETS` を1級ぶんに差し替えるだけ**で下流の描画コードは変更不要になる。

```js
// テーマ別（eikentopic）は当面どの級にも含めない。
const GRADE_PREFIXES = {
  "2":    ["eiken2"],
  "pre2": ["eikenp2"],
  "pre1": ["eikenp1"],
  "1":    ["eiken1"],
};

function applyGradeScope(gradeCode) {
  const prefixes = GRADE_PREFIXES[gradeCode];
  if (!prefixes) return false;
  const scoped = Object.fromEntries(
    Object.entries(DATASETS).filter(([id]) => prefixes.includes(gradeOf(id))),
  );
  if (!Object.keys(scoped).length) return false; // manifestに該当セットが無い場合は絞らない
  DATASETS = scoped;
  if (!DATASETS[DEFAULT_DATASET_ID]) DEFAULT_DATASET_ID = Object.keys(DATASETS)[0];
  return true;
}
```

これで自動的にこうなる。

- `datasetPicker()` の級ボタンは1つだけ、Unitカードもその級のみ。
- `otherGradeDueCounts()` は `datasetGrades()` が1件になるため常に空配列。
- `loadDatasetId()` は保存済みIDが `DATASETS` に無ければ既定へ戻すので、
  級を変えた直後も範囲外のセットを開かない。
- `loadPooledItems` / 語彙目標 / 間隔復習は元から `currentGrade()` 依存なので変化なし。

**他級の進捗データは localStorage に残したまま触らない。** 級を戻せば元通り見える。

### 2.1 `DATASETS` を全件見なければならない箇所

絞り込みで壊れないよう、絞る前の全ID一覧を保持しておく。

```js
let ALL_DATASET_IDS = [];        // loadManifest() の末尾で Object.keys(DATASETS) を控える
```

- `collectAllProgress()`（[mode-q1.js:662](../static/mode-q1.js)）は `Object.keys(DATASETS)` を
  走査して**全セットの進捗をまとめてクラウドへ送る** `getPayload`。絞った `DATASETS` のままだと
  他級の進捗を落とした地図でクラウドを上書きしうる。ここは `ALL_DATASET_IDS` を使う。
  （現状は `getPatch` が定義済みで `push()` がパッチ経路に入るため `getPayload` は呼ばれない。
  それでも将来 `getPatch` を外したときに黙って進捗を失う罠になるので、先に潰しておく。）
- `applyCloudProgress()`（[mode-q1.js:840](../static/mode-q1.js)）も `DATASETS[id]` で選別するが、
  **絞り込みより前（`boot()` の 2942行付近）に実行されるため改修不要**。この順序は崩さない。

## 3. 級の決め方（優先順）

| 優先 | 出所 | 想定 |
| --- | --- | --- |
| 1 | URL `?g=pre1`（共有URL `?s=&t=` に追記） | 先生が生徒ごとに固定。DB変更不要 |
| 2 | localStorage `scopedStorageKey("grade")` | 2回目以降。生徒ごとに分離される |
| 3 | 初回の級選択画面 | 共有URLなしの利用 |

- URL指定時は localStorage にも書き込み、以後URLなしで開いても維持する。
- 値は `GRADE_PREFIXES` のキー（`2` / `pre2` / `pre1` / `1`）。
  `GRADE_BY_PREFIX` の値と同じ表記に揃える。
- 未知の値は無視して優先順の次へ落とす。

```js
function resolveGradeCode() {
  const fromUrl = new URLSearchParams(window.location.search).get("g") || "";
  if (GRADE_PREFIXES[fromUrl]) {
    try { localStorage.setItem(scopedStorageKey(GRADE_KEY), fromUrl); } catch (e) { /* ignore */ }
    return fromUrl;
  }
  try {
    const saved = localStorage.getItem(scopedStorageKey(GRADE_KEY));
    if (GRADE_PREFIXES[saved]) return saved;
  } catch (e) { /* ignore */ }
  return "";
}
```

Supabase の `app_students` に持たせる案もあるが、スキーマとRPCの変更が要る。
URLパラメータで要件を満たすため今回は行わない。

## 4. 組み込み位置（`boot()`）

`storageStudentId` が確定するのは `cloud.init()` の後、
旧準1級進捗の移行（`migrateLegacyPre1Progress`）は絞り込み前に済ませる必要がある
（絞ると `DATASETS["eikenp1-..."]` を参照する移行判定が通らなくなるため）。

```js
    const migratedLegacy = migrateLegacyPre1Progress(legacyProgress);
+   const gradeCode = resolveGradeCode();
+   needsGradeChoice = !applyGradeScope(gradeCode);   // 未選択なら true
    state.datasetId = loadDatasetId();
```

順序の制約（いずれも既存コードの位置より**後ろ**に入れる）:

| 行 | 処理 | 絞り込み前でなければならない理由 |
| --- | --- | --- |
| 2939 | `storageStudentId` の確定 | `resolveGradeCode()` が生徒別キーを読む |
| 2942 | `applyCloudProgress` | `DATASETS[id]` で選別するため、絞ると他級の進捗を書き戻せない |
| 2947 | `migrateLegacyPre1Progress` | `DATASETS["eikenp1-..."]` を参照して移行判定する |

クラウド由来の `lastDatasetId` が他級のセットを指していても、`loadDatasetId()` が
絞り込み後の `DATASETS` に無いIDを弾いて既定へ戻すので問題ない。

`needsGradeChoice` が true のときは、既定セットのまま `loadData()` まで進み、
`renderHomeContent()` の先頭で級選択画面に差し替える。boot の構造は変えない。

```js
function renderHomeContent() {
  if (needsGradeChoice) return renderGradeChoice();
  ...
}
```

`renderGradeChoice()`（新規、`card` 1枚）:

- 見出し「学習する級を選んでください」＋「あとから変更できます」
- `Object.keys(GRADE_PREFIXES)` を 準2級→2級→準1級→1級 の順でボタン表示
- 押下時: localStorage 保存 → `applyGradeScope(code)` → `needsGradeChoice = false`
  → `state.datasetId = loadDatasetId()` → `await loadData()` → `renderHome()`
- ボタンは既存の `.datasetGradeChoice` を流用（`min-height: 44px` 済み、[styles.css:269](../static/styles.css)）。
  ただし `.datasetGradeChoices` は4列固定グリッドなので、選択画面では専用のクラスか
  `grid-template-columns` の上書きで縦並び／2列にする

## 5. 級の変更手段

- URLに `g` が**無い**ときだけ、ホーム最下部に控えめな「級を変更」ボタンを出す。
  押すと確認（他級の進捗は消えない旨を明記）→ localStorage の級を削除 →
  `needsGradeChoice = true` → `renderHome()` で級選択画面へ。
- URLに `g` が**ある**ときは非表示（先生が固定した状態）。
- 級が1つしか無い状態では `datasetPicker()` の級ボタン列は情報量ゼロなので、
  `datasetGrades().length <= 1` のとき `gradeChoices` を **`wrap` に append しない**
  （`renderGradeChoices()` の呼び出しごと省く。4列グリッドに1個だけ残ると崩れる）。

## 6. 影響と既知の割り切り

- **テーマ別（`eikentopic-*`）はどの級にも含めないため、級を固定した使用者からは
  到達できなくなる。** 必要になったら `GRADE_PREFIXES` に `"topic": ["eikentopic"]` を
  足して選択肢に並べるだけでよい。データと進捗はそのまま残る。
- `manifest.defaultDatasetId`（2級）は変更しない。級を絞った時点で無効になれば
  `applyGradeScope` がその級の先頭セットへ差し替える。
- 保存形式（`app_save_progress_dataset` のパッチ）は不変。絞り込みは表示と選択の範囲だけ。
  `collectAllProgress` は 2.1 のとおり全ID走査へ直す。
- **選んだ級はクラウドに同期しない**（localStorage のみ）。生徒が別端末で開くと級未選択に戻る。
  共有URLに `&g=<級>` を含めておけば毎回そこで確定するため、運用上はそれで足りる。
  端末をまたいで自動追従させたくなったら `app_students` かクラウド進捗の `_meta` に持たせる。
- 共有URLの認証に失敗した場合 `storageStudentId` は `unverified:<id>` になる。級設定も
  そのキーで分離されるが、これは進捗の既存挙動と同じで新たな問題ではない。

## 7. 検証

既存の `scripts/check-*.cjs` と同じ vm サンドボックス方式で
`scripts/check-grade-scope.cjs` を追加し、`package.json` の `test` に連結する。

現行のサンドボックスは `{ URLSearchParams, encodeURIComponent }` しか渡していない
（[check-student-storage-scope.cjs](../scripts/check-student-storage-scope.cjs)）ため、
このテストでは追加で用意する:

- `window = { location: { search: "?g=pre1" } }` と最小の `localStorage` スタブ
- `return { mount, handleKey };` を差し替える既存手法で
  `__test: { setDatasets, applyGradeScope, resolveGradeCode, availableDatasets, defaultDatasetId,
  datasetGrades, otherGradeDueCounts }` を露出（`DATASETS` は manifest を fetch しないため注入する）
- `window` / `localStorage` を参照するのは関数本体の中だけに保ち、トップレベルでは触らない
  （既存チェックが `document` 無しで読み込めている前提を壊さない）

- `applyGradeScope("pre1")` 後、`availableDatasets()` が準1級のみ
- `defaultDatasetId()` が準1級のセットに差し替わる
- `datasetGrades()` が1件、`otherGradeDueCounts()` が空配列
- `resolveGradeCode()` が URL > localStorage の順で解決し、未知の値を無視する
- `applyGradeScope("存在しない級")` は false を返し `DATASETS` を壊さない

実ブラウザ確認（`?g=pre1` 付きで起動）:

- 級ボタン列が消え、準1級のUnitカードだけが並ぶ
- 間隔復習カードに他級の行が出ない
- 「級を変更」ボタンが出ない（`g` 指定時）
- `g` なしで開くと級選択画面 → 選択後に通常ホームへ遷移
- コンソールエラーなし、キーボード操作、主要な画面幅

## 8. 作業順

1. `ALL_DATASET_IDS` を控え、`collectAllProgress` をそちら参照に直す
2. `GRADE_PREFIXES` / `GRADE_KEY` / `applyGradeScope` / `resolveGradeCode` を追加
3. `boot()` に2行組み込み、`needsGradeChoice` を導入
4. `renderGradeChoice()` と「級を変更」ボタンを追加
5. `datasetPicker()` の級ボタン列を1級のとき非表示に
6. `scripts/check-grade-scope.cjs` 追加 + `npm test`
7. 実ブラウザ確認 → README の該当節に「級の固定」を追記
