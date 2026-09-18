# 実装計画: UI・UX監査指摘への対応 (2026-09-06)

> 対象: `eiken-q1-practice`
> 状態: 計画（未着手）
> 入力: chao Web UIグラフィックデザイン監査、hisui UX摩擦監査（ユーザー提示）

## 目標

監査で確認済みの4件を、正本の `static/src/*.js` と `static/styles.css` で修正し、モバイルの操作配置、長い回答解説、動的カード更新時のフォーカス、途中再開時の主CTAを一貫させる。

条件付き指摘 HISUI-03 は通信失敗を実ブラウザで再現し、表示状態と途中進捗の保持を確認してから実装可否を決める。確認前にエラーUIの仕様や実装を確定しない。

## 入力監査

監査の原IDを保持し、この計画では `F-01` 形式へ正規化する。

| 指摘ID | 監査ID | 状態 | 重大度 | 根拠 | 対象箇所 |
|---|---|---|---|---|---|
| F-01 | CHAO-01 | 確認済み | medium | 375px/320pxで `.sessionHeadBack` の左端が16px、右端が102px。完了画面375pxでは右端344px | `static/src/90-learn-flow.js` `renderSession()`、`static/styles.css` `.itemHead` `.sessionHeadBack`、720px以下のメディアクエリ |
| F-02 | CHAO-02 | 確認済み | medium | 375px誤答直後に `.feedback` と `.answerActions` が約69.4px重複 | `static/src/90-learn-flow.js` `onPracticeAnswer()` `practiceChoiceMeanings()`、`static/styles.css` `.answerActions` `.practiceChoiceMeanings` |
| F-03 | HISUI-01 | 確認済み | medium | 第2問STEP1でカードが `book` から `tooth` に変わってもフォーカスが旧「次のカード」操作に残った | `static/src/90-learn-flow.js` `renderSession()` `renderFlash()` `buildFlashCard()`、`static/src/99-boot.js` `handleKey()` |
| F-04 | HISUI-02 | 確認済み | medium | 途中保存時、ホーム上部、現在の問題セットカード、間隔復習カードに競合する再開・開始導線が並ぶ | `static/src/80-home.js` `renderHomeContent()` `meaningMission()` `datasetUnitCard()` |
| F-05 | HISUI-03 | 要確認 | conditional medium | `loadPooledItems(...).catch(() => {})` と `restoreSession()` の取得失敗時 `return false` は確認済み。実通信失敗時の画面は未確認 | `static/src/80-home.js` `renderHomeContent()` `meaningMission()`、`static/src/20-storage.js` `restoreSession()`、`static/src/50-vocab-pool.js` `loadPooledItems()` |

監査で未確認の項目は、最終CLEAR、公開URL、クラウド復元・同期、スクリーンリーダー、Reduced Motion、アプリ全体のスマホ・タブレット表示である。これらを本計画の追加指摘にはしない。

## 対象範囲 / 対象外

### 対象

- F-01、F-02、F-03、F-04の正本修正と、該当する契約テスト・実ブラウザ検証。
- F-05の通信失敗再現、画面状態、再試行可能性、途中保存保持の確認。
- 正本変更後の `npm run build` による `static/mode-q1.js` の再生成と、`index.html` の該当 `?v=` 更新。
- 監査の指摘に直接対応する `DESIGN.md` の規範更新。

### 対象外

- F-05のエラーUI実装。再現結果が出る前は仕様を確定しない。
- 最終CLEAR、クラウド復元・同期、公開URL、スクリーンリーダー、Reduced Motionの追加監査。
- ホーム、学習フロー、回答解説以外のUI変更。
- データ、進捗スキーマ、依存関係、ビルド構成の変更。
- 無関係なリファクタリング、整形、文言変更。
- コミット、push、デプロイ。本書に記すコミットメッセージは実装時の単位を示すだけである。

## 前提と未確認事項

- 作業開始時点で多数の未コミット差分がある。実装者は開始前後に `git status --short` と `git diff -- <対象ファイル>` を確認し、既存差分を編集、削除、整形、取り込みしない。対象ファイルに既存差分がある場合は、指摘に対応する最小ハンクだけを追加する。
- `static/mode-q1.js` は生成物である。直接編集せず、`static/src/*.js` の変更後に `npm run build` で再生成する。
- `static/mode-q1.js` または `static/styles.css` が変わるタスクでは、`index.html` の対応する `?v=` を1だけ上げる。
- F-02は375pxで確認済み、320pxは未確認である。修正後検証では両幅を対象にするが、320pxに別の症状があるとは断定しない。
- F-03の改善先は、暗記カードでは現在語句 `.flashWord`、暗記カード以外のステージ遷移ではセッション見出しとする。グローバルショートカット追加は行わない。
- F-05は条件付き指摘である。通信失敗時の実表示、再試行経路、途中保存の保持は未確認であり、T4の結果が出るまで実装判断を保留する。

## 変更方針

1. モバイル操作クロームの問題は、共通ブレークポイント `max-width: 720px` と本番形式回答後の修飾クラスで閉じる。解説全体の高さや文言を削らない。
2. 動的更新後のフォーカスは `renderSession()` の描画完了地点で一元管理し、暗記カードの現在語句と他ステージの見出しへ移す。現在地は既存 `.flashNavCounter[aria-live="polite"]`、語句・ステージはフォーカス対象の読み上げで伝える。
3. 途中保存時の再開操作はホーム上部の主CTAだけに残す。現在セットのUnitカードは途中保存状態の表示へ変え、間隔復習は明示的な二次操作として残す。
4. F-05は再現と証拠記録だけを行う。再現できた場合も、その場で `static/src` を変更せず、別の承認済み実装タスクへ切り出す。

## 変更ファイルマップ

| ファイル | 扱い | 責務 |
|---|---|---|
| `static/src/90-learn-flow.js` | 正本を変更 | セッション見出し、暗記カードのフォーカス、回答後操作の修飾クラス |
| `static/src/80-home.js` | 正本を変更 | 主CTA、間隔復習の二次導線、現在Unitカードの状態表示 |
| `static/styles.css` | 正本を変更 | モバイルの戻るボタン整列と、本番形式の長い解説に続く操作バー配置 |
| `DESIGN.md` | 正本を変更 | 動的セッションのフォーカス規範と、途中保存時のCTA優先順位 |
| `scripts/check-flashcard-nav-ui.cjs` | 変更 | セッション見出し・現在語句へのフォーカス契約 |
| `scripts/check-unit-learning-ui.cjs` | 変更 | `.sessionHeadBack` のモバイル右寄せと現在Unitカードの非重複導線 |
| `scripts/check-practice-feedback-ui.cjs` | 変更 | 本番形式回答後の専用クラスとモバイル通常フロー化 |
| `scripts/check-home-priority-ui.cjs` | 変更 | 途中保存時に上部だけが主CTAになる契約 |
| `scripts/check-meaning-mission-ui.cjs` | 変更 | 通常学習の再開中に間隔復習が二次操作になる契約 |
| `static/mode-q1.js` | 生成更新のみ | `npm run build` で `static/src/*.js` を連結した配信物。直接編集禁止 |
| `index.html` | 変更 | 変更されたCSS・JS配信物のキャッシュバスター更新 |

`static/src/20-storage.js`、`static/src/50-vocab-pool.js`、`static/src/99-boot.js` はF-05/F-03の照合先だが、この計画の確定実装では変更しない。F-05の結果から変更が必要になった場合は別計画で対象化する。

## 依存順のタスク

### T1: モバイルのセッション操作クロームを整える

- 対応する指摘: F-01（CHAO-01）、F-02（CHAO-02）
- 依存: なし
- 対象ファイル・関数・セレクタ:
  - `static/styles.css` `.sessionHeadBack`、`.itemHead`、`@media (max-width: 720px)`、`.answerActions`
  - `static/src/90-learn-flow.js` `onPracticeAnswer()`
  - `scripts/check-unit-learning-ui.cjs`
  - `scripts/check-practice-feedback-ui.cjs`
  - 生成更新のみ: `static/mode-q1.js`
  - キャッシュ更新: `index.html`
- 具体的変更:
  1. 720px以下の規則へ `.sessionHeadBack { margin-left: auto; }` を追加する。既存の `min-height: 44px` と `align-self: flex-start` は維持する。
  2. `onPracticeAnswer()` で生成した `.answerActions` に `practiceAnswerActions` を追加し、本番形式の回答後だけを識別できるようにする。
  3. 720px以下では `.answerActions.practiceAnswerActions` を `position: static` にし、`bottom` と `z-index` を解除する。背景、上辺、余白、44px以上のボタン寸法は維持し、長い解説の後ろへ通常フローで配置する。
  4. `check-unit-learning-ui.cjs` に、720px以下の `.sessionHeadBack` が `margin-left: auto` を持つ契約を追加する。
  5. `check-practice-feedback-ui.cjs` に、`onPracticeAnswer()` が専用クラスを付与し、そのクラスが720px以下で `position: static` になる契約を追加する。
  6. `npm run build` で生成物を更新する。`index.html` のCSSとJSの `?v=` をそれぞれ1だけ上げる。
- 検証:
  - コマンド: `node scripts/check-unit-learning-ui.cjs && node scripts/check-practice-feedback-ui.cjs && npm run build && npm test`
  - 期待結果: すべて終了コード0。`npm test` の先頭で `mode-q1.js build freshness: OK` が出る。
  - 操作: `py -3 -m http.server 8061 --bind 127.0.0.1` で起動し、320px/375pxで暗記カード、意味確認、本番形式、完了画面を開く。DevToolsコンソールで `.sessionHeadBack.getBoundingClientRect().right` と `.wrap.getBoundingClientRect().right` を記録する。
  - 期待結果: 各画面で両right値の差が1px以内。375pxの本番形式で監査と同じ長い誤答解説を出し、320pxでも同じ操作を行う。両幅で `.feedback.getBoundingClientRect().bottom <= .answerActions.getBoundingClientRect().top` となり、最後の `.practiceChoiceMeaningRow` と「結果を見る」ボタンが重ならない。
- 受入基準:
  - 320px/375pxの暗記カード、意味確認、本番形式、完了画面で「一覧へ戻る」がコンテンツ右端に揃う。
  - 320px/375pxの本番形式回答後に解説と操作バーの重なりが0pxである。
  - 解説内容、選択肢意味行、回答結果の保存動作を変更していない。
  - 自動検証と実ブラウザ検証でコンソールエラーがない。
- コミット: `fix(ui): align mobile session controls and feedback actions`

### T2: 動的セッション更新後のフォーカスを現在内容へ移す

- 対応する指摘: F-03（HISUI-01）
- 依存: T1完了後
- 対象ファイル・関数・セレクタ:
  - `static/src/90-learn-flow.js` `renderSession()`、`buildFlashCard()`、`.flashWord`、セッション見出し
  - `DESIGN.md` コンポーネント規範
  - `scripts/check-flashcard-nav-ui.cjs`
  - 生成更新のみ: `static/mode-q1.js`
  - キャッシュ更新: `index.html`
- 具体的変更:
  1. `renderSession()` が作るステージ見出しへ固定ID `sessionStageTitle` と `tabindex="-1"` を付ける。
  2. `buildFlashCard()` が作る `.flashWord` へ `tabindex="-1"` を付ける。語句テキスト自体は変更しない。
  3. `renderSession()` の各ステージ描画後に1つの `focusSessionContext()` を呼ぶ。flashステージは現在の `.flashWord`、他ステージは `#sessionStageTitle` を選び、`focus({ preventScroll: true })` する。
  4. 既存 `.flashNavCounter[aria-live="polite"]` は維持し、カード番号の変化を通知する。フォーカス対象の現在語句または見出しと組み合わせ、カード内容と現在地を通知する。新しいグローバルkeydown処理は追加しない。
  5. `DESIGN.md` に「カード・ステージをDOM置換した後は、暗記カードなら現在語句、他ステージならセッション見出しへフォーカスを移し、スクロール位置は維持する」と追記する。
  6. `check-flashcard-nav-ui.cjs` に、両フォーカス対象の `tabindex`、一元化したフォーカス関数、`preventScroll: true`、既存live counterの保持を検査する契約を追加する。
  7. `npm run build` で生成物を更新し、`index.html` のJS `?v=` を1だけ上げる。
- 検証:
  - コマンド: `node scripts/check-flashcard-nav-ui.cjs && npm run build && npm test`
  - 期待結果: すべて終了コード0。生成物鮮度、構文、既存契約テストが通る。
  - 操作: 暗記カード第1枚でTabにより「次のカード」へ移動してEnterを押し、第2枚へ進む。続けて「意味チェックへ進む」、意味確認の回答後の次操作、本番形式への遷移をキーボードで行う。
  - 期待結果: 第2枚表示後の `document.activeElement` は新しい `.flashWord`。ステージ遷移後は `#sessionStageTitle`。フォーカス移動でページが意図せず先頭・末尾へ跳ばず、Tabを1回押すと新画面内の次の操作へ進む。
- 受入基準:
  - 動的更新で削除された旧ボタンにフォーカスが残らない。
  - 現在語句または現在ステージがフォーカス対象になり、カード番号のlive通知が残る。
  - マウス・タッチの前後カード操作、スワイプ、既存の44px操作寸法を変更していない。
  - 自動検証とキーボード実操作でコンソールエラーがない。
- コミット: `fix(a11y): move focus to updated session content`

### T3: 途中保存時の再開CTAをホーム上部へ一本化する

- 対応する指摘: F-04（HISUI-02）
- 依存: T2完了後
- 対象ファイル・関数・セレクタ:
  - `static/src/80-home.js` `renderHomeContent()`、`meaningMission()`、`datasetUnitCard()`、`.startCta`、`.meaningMissionCta`、`.datasetUnitCard`
  - `DESIGN.md` 「移動・再開ラベル」「現在Unitの開始・再開」「間隔復習カード」
  - `scripts/check-home-priority-ui.cjs`
  - `scripts/check-meaning-mission-ui.cjs`
  - `scripts/check-unit-learning-ui.cjs`
  - 生成更新のみ: `static/mode-q1.js`
  - キャッシュ更新: `index.html`
- 具体的変更:
  1. `coreResume` が真のとき、`renderHomeContent()` の上部 `.startCta` だけに「続きから再開する」と `restoreSession()` を残す。
  2. 現在セットかつ `summary.hasResume` のUnitカードはbuttonではなく状態表示コンテナとして描画する。`aria-current="true"`、進捗、`途中保存：${resumeDescription(...)}` は残し、操作ラベルを「途中保存あり」にする。`onclick`、`type="button"`、操作矢印は付けない。
  3. 現在セット以外のUnitカードは従来どおりbuttonとしてセット切替を行う。途中保存のある別セットはカード上で状態を示し、切替後にホーム上部の主CTAから再開する。
  4. `meaningMission()` では `coreResume` 時の「先に再開するのがおすすめです」という重複案内を削除する。復習対象がある場合の操作は `.secondaryCta.meaningMissionCta` として残し、上部の `.startCta` と同じ視覚強度へ上げない。
  5. `DESIGN.md` を更新し、通常学習の途中保存がある現在Unitは状態表示、上部を唯一の再開操作とする規範を明記する。別セットのカードは切替操作、間隔復習は二次操作として残す。
  6. `check-home-priority-ui.cjs` に、`coreResume` 分岐の主CTAが1つであることを追加する。`check-unit-learning-ui.cjs` に、現在の途中保存Unitが操作要素にならず、別セットは切替可能である契約を追加する。
  7. `check-meaning-mission-ui.cjs` の旧「先に再開するのがおすすめです」必須契約を削除し、`coreResume` 時も `.secondaryCta.meaningMissionCta` を使う契約へ置き換える。
  8. `npm run build` で生成物を更新し、`index.html` のJS `?v=` を1だけ上げる。
- 検証:
  - コマンド: `node scripts/check-home-priority-ui.cjs && node scripts/check-meaning-mission-ui.cjs && node scripts/check-unit-learning-ui.cjs && npm run build && npm test`
  - 期待結果: すべて終了コード0。生成物鮮度、構文、ホーム・復習・Unitカードの既存契約が通る。
  - 操作: 通常学習を第2問で途中保存し、意味復習対象が4語句以上ある状態でホームを表示する。キーボードのTab順とDOMを確認する。
  - 期待結果: 「続きから再開する」は上部 `.startCta` の1個だけ。現在Unitは「途中保存あり」の状態表示で、Tab停止点にならない。意味復習は二次ボタンとして操作でき、別セットのカードは切替操作として残る。上部CTAを押すと第2問の保存位置へ戻る。
- 受入基準:
  - 通常学習の途中保存時、同じ保存位置を開く再開操作がホーム内に1個だけ存在する。
  - 現在Unitの進捗・途中保存情報は失われない。
  - 意味復習への導線は消えず、主CTAより低い二次スタイルになる。
  - 別セットへの切替、途中進捗、localStorageキー、クラウドデータ形式を変更していない。
- コミット: `fix(ux): make resume the single primary home action`

### T4: 意味復習データの通信失敗状態を再現する検証ゲート

- 対応する指摘: F-05（HISUI-03、要確認）
- 依存: T1〜T3とは独立。F-05の実装計画を作る前に完了させる
- 対象ファイル・関数・セレクタ:
  - 読み取り対象: `static/src/80-home.js` `renderHomeContent()` `meaningMission()`
  - 読み取り対象: `static/src/20-storage.js` `restoreSession()`
  - 読み取り対象: `static/src/50-vocab-pool.js` `loadPooledItems()`
  - 画面対象: `.spacedReviewCard` `.meaningMissionCta` `.resumeNotice`
  - 恒久ファイル変更: なし
- 具体的変更:
  1. このタスクではコード、CSS、テスト、データを変更しない。
  2. 通信成功時に1級の意味復習セッションを開始して途中でホームへ戻り、`eiken_q1_progress_<datasetId>` の `resume` が存在することをDevToolsで記録する。
  3. Chrome DevToolsのNetwork request blockingで、現在セットではない同級データ1件 `*/data/vocab_1_mock-9.json*` だけを遮断する。現在セットは `eiken1-2026-1` とし、ページを再読み込みする。これにより現在セット本体は読み込めるが、級全体の `loadPooledItems()` は失敗する条件を作る。
  4. ホームの間隔復習カードについて、読み込み中表示が残り続けるか、明示的エラーが出るか、再試行操作があるかを、表示文言・disabled状態・Networkログ・コンソールログとともに記録する。
  5. 上部の途中再開操作を押し、意味復習の復元が失敗したときの表示を記録する。操作前後で同じlocalStorageキーの `resume` が保持されていることを確認する。
  6. request blockingを解除し、ページ再読み込みまたは既存の再操作でデータ取得が成功するかを確認する。
- 検証:
  - コマンド: `py -3 -m http.server 8061 --bind 127.0.0.1`
  - 操作: 上記2〜6をChromeで実行し、成功時、遮断時、遮断解除後の3状態を記録する。
  - 期待結果: F-05を「再現確認済み」または「再現せず」に分類できる。途中保存の `resume` は通信失敗前後で削除されない。遮断解除後に取得を再試行できるか否かが判明する。
- 受入基準:
  - 実通信失敗時の画面文言、ボタン状態、再試行可否、コンソール、Network失敗URL、`resume`保持の6点が記録されている。
  - 再現できた場合はF-05を別の実装計画へ昇格し、「読み込み中・対象なし・失敗」の状態契約と再試行導線をユーザー確認後に定める。
  - 再現しない場合は、再現条件と結果を残し、F-05を実装しない。
  - このタスクでリポジトリ差分が増えていない。
- コミット: なし（検証ゲートであり、恒久ファイルを変更しない）

## トレーサビリティ

| 指摘ID | 監査ID | 重大度 | 概要 | 対応タスク | 受入チェック |
|---|---|---|---|---|---|
| F-01 | CHAO-01 | medium | スマホ幅でセッション戻るボタンが左端へ移動 | T1 | 320px/375pxの対象4画面で戻るボタンとコンテンツの右端差が1px以内 |
| F-02 | CHAO-02 | medium | 長い本番形式解説が固定操作バーに隠れる | T1 | 320px/375pxで `.feedback.bottom <= .answerActions.top`、最後の意味行が可視 |
| F-03 | HISUI-01 | medium | カード更新後も旧「次のカード」操作にフォーカスが残る | T2 | 新カードは `.flashWord`、他ステージは `#sessionStageTitle` がactiveElement |
| F-04 | HISUI-02 | medium | 途中保存時に競合するCTAが複数表示される | T3 | 同じ再開先を開く操作は上部 `.startCta` の1個だけ |
| F-05 | HISUI-03 | conditional medium、要確認 | 意味復習データ取得失敗時に明示的エラー・再試行がない可能性 | T4（検証のみ） | 通信失敗時の6点を記録し、実装するか否かを判定 |

## 今回対応しない指摘と理由

- F-05の実装: 実通信失敗時の画面が監査で未確認であり、条件付き指摘だから。T4で再現した後、ユーザー判断を得て別計画にする。
- 監査で未確認の最終CLEAR、公開URL、クラウド復元・同期、スクリーンリーダー、Reduced Motion、アプリ全体のスマホ・タブレット表示: 指摘として確定しておらず、今回の監査結果から実装内容を導けないため。
- `static/src/99-boot.js` の空 `handleKey()`: F-03は描画後フォーカスの問題として閉じる。監査にグローバルキーボードショートカットの要件がないため変更しない。

## リスクとロールバック

- T1の `position: static` を共通 `.answerActions` 全体へ適用すると意味確認の操作感まで変わる。`practiceAnswerActions` に限定し、問題が出た場合はT1コミットだけをrevertして元のsticky動作へ戻す。
- T2で描画ごとにフォーカスを移すと、クリック操作時にも読み上げやフォーカスリングが変わる。`focusSessionContext()` を1か所に閉じ、問題が出た場合はT2コミットをrevertする。進捗データには触れない。
- T3で現在Unitカードを非操作化すると、既存の「現在Unitカード自体から再開」のDESIGN規範が変わる。上部CTAが常に存在する `coreResume` 条件に限定し、別セット切替を維持する。問題が出た場合はT3コミットと対応するDESIGN差分を一緒にrevertする。
- `scripts/check-*.cjs` と `package.json` には既存未コミット差分がある。既存ハンクを上書きせず、実装前後に対象ファイル限定のdiffを確認する。`package.json` のtest連鎖は既存チェックファイルを更新するだけなので変更しない。
- `static/mode-q1.js` の復元は手編集で行わない。正本を戻した後に `npm run build` を実行する。
- `index.html` の `?v=` は正本・生成物を戻した内容に合わせて元の値へ戻す。キャッシュ番号だけを単独で残さない。
- T4はDevToolsの一時的なrequest blockingだけを使う。検証後に解除し、ローカルストレージの途中保存は削除しない。

## 実装前に必要な判断

- F-01〜F-04は監査の改善方向と既存DESIGN規範から実装可能で、追加の仕様判断は不要。
- F-05はT4の結果を確認した後、「別計画でエラー・再試行UIを実装する」か「今回は実装しない」かをユーザーが判断する。

## 完了条件

- F-01〜F-04の各受入基準と `npm test` が通る。
- F-05はT4の記録により、確認済みまたは再現せずへ分類される。
- トレーサビリティ表の5件すべてに対応先または非対応理由がある。
- `static/mode-q1.js` は `npm run build` 以外で変更されていない。
- 既存の未コミット差分が、各タスクの対象ハンク以外で変化していない。
