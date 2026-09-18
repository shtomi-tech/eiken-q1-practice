# 完了済みの計画書（アーカイブ）

実装済み・役目を終えた計画書の置き場。2026-09-18 のリファクタリング（`docs/plans/2026-09-18-refactoring-plan.md` Phase 4）で `docs/` 直下から移した。

- 本文中のファイルパス・行番号・コード引用は**書かれた時点のもの**で、現在のコードとは一致しないことがある。運用の正本は `docs/` 直下の `*_AUTHORING.md`・`*_ALIGNMENT.md`・`STATE_TRANSITIONS.md` を見る。
- `static/src/90-learn-flow.js` は同日に次の4ファイルへ分割した（連結結果の `static/mode-q1.js` は同一）: `90-learn-session.js`（セッション・進捗バー）、`91-flashcard.js`（STEP 1）、`92-meaning-check.js`（STEP 2・誤答見直し）、`93-practice-done.js`（STEP 3・完了画面）。
- 同様に `static/src/80-home.js` は `80-home.js`・`82-question-list.js`・`84-vocab-goal.js`・`86-dataset-picker.js`・`88-answer-helpers.js` に分割した。
