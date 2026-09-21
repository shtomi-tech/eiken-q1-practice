# Context Discovery Phase 6 q=4〜5 batch review

この文書は、q=4〜5の8語について、初稿と初回レビュー、修正内容、最終レビューを追跡するための記録です。初稿は `data/context-drafts/eiken2-2026-1-q4-q5-candidates.json`、最終Draftは `data/context-drafts/eiken2-2026-1-q4-q5.json`、レビュー結果は `data/context-drafts/eiken2-2026-1-q4-q5-review.json` に保存しています。

## Batch metrics

- Generated: 8
- Initial PASS: 3
- REVISE: 5
- REJECT: 0
- Final PASS: 8
- Initial Pass Rate: 0.375
- Revision Rate: 0.625
- Japanese Support Used: 0 / 8
- Revision reasons: SENSE 4, CONTEXT 1, CLUE 1, DISTRACTOR 1

## q=4

### tendency

- Full Meaning: 傾向、性向、癖
- Target Sense: 傾向
- Initial Review: REVISE — 初稿の「癖」は、繰り返しの場面からはやや狭すぎるため。
- Revision: SENSE — 「癖」から「傾向」へ変更。
- Final Review: PASS
- Japanese Support: not-needed。基本語だけで、緊張時の同じ行動を理解できる。
- Distractors: 原因 / 結果 / 計画。別senseを混ぜず、文脈上のtargetSenseを一意にした。

### discrimination

- Full Meaning: 差別；識別、区別
- Target Sense: 差別
- Initial Review: REVISE — 初稿の「識別、区別」は、年齢を理由にした不公平な扱いと合わない。
- Revision: SENSE — 「差別」へ変更。
- Final Review: PASS
- Japanese Support: not-needed。年齢・能力・法律というclueを英語で保護した。
- Distractors: 協力 / 報酬 / 昇進。中立的な識別senseは選択肢に入れていない。

### shelter

- Full Meaning: 避難所、シェルター；保護
- Target Sense: 避難所、シェルター
- Initial Review: REVISE — 初稿の「保護」は抽象的で、木造の小屋という具体的な場所を十分に反映しない。
- Revision: SENSE — 「避難所、シェルター」へ変更。
- Final Review: PASS
- Japanese Support: not-needed。雨・小屋・暖かさの因果関係がそのまま読める。
- Distractors: 危険 / 景色 / 食事。

### content

- Full Meaning: 中身、内容（複数形 contents）／（形）満足して
- Target Sense: 中身、内容
- Initial Review: REVISE — 初稿の「満足して」は品詞・場面ともに不一致で、別sense distractorにもなる。
- Revision: SENSE + DISTRACTOR — 「中身、内容」へ変更し、「満足して」を選択肢から除外。
- Final Review: PASS
- Japanese Support: not-needed。箱の中の具体例が強いclueになる。
- Distractors: 箱 / 鍵 / 手紙。別senseを使わず、容器と中身の関係を保った。

## q=5

### foster

- Full Meaning: （能力・感情などを）育む、促進する／里子として育てる
- Target Sense: 育む、促進する
- Initial Review: REVISE — 初稿は結果が「クラブを楽しむ」に留まり、能力や感情の成長が弱い。
- Revision: CLUE + CONTEXT — 活動を増やし、時間の経過後に自信が高まる結果へ変更。
- Final Review: PASS
- Japanese Support: not-needed。学習活動・愛着・自信の成長を英語で理解できる。
- Distractors: 隠す / 止める / 測る。里子の別senseは選択肢に入れていない。

### hate

- Full Meaning: 憎む、ひどく嫌う
- Target Sense: ひどく嫌う
- Initial Review: PASS
- Final Review: PASS
- Japanese Support: not-needed。疲れと、列が終わった後の安心という対比がclueになる。
- Distractors: 期待する / 忘れる / 選ぶ。

### divide

- Full Meaning: 分ける、分割する；割り算する
- Target Sense: 分ける、分割する
- Initial Review: PASS
- Final Review: PASS
- Japanese Support: not-needed。ケーキを同じ量にする具体的な動作を保持した。
- Distractors: 集める / 隠す / 焼く。算数の別senseは選択肢に入れていない。

### pronounce

- Full Meaning: 発音する；宣言する
- Target Sense: 発音する
- Initial Review: PASS
- Final Review: PASS
- Japanese Support: not-needed。音を繰り返し、名前が伝わるという結果が明確。
- Distractors: 翻訳する / 隠す / 書き直す。宣言の別senseは選択肢に入れていない。

## Pipeline status

- SOURCE: Vocabulary Dataからq=4・q=5の8語を取得
- SENSE: targetSenseとsenseSelectionReasonを記録
- CONTEXT / CLUES / SEGMENTS / SUPPORT / CHOICES / EXPLANATION: 初稿と最終Draftを保存
- VALIDATE: 8語すべてStructural PASS
- REVIEW: 初回3 PASS / 5 REVISE、最終8 PASS
- APPROVE: 最終PASSの8語をapproved
- PUBLISH: q=4・q=5の8項目だけruntimeへ反映
- q=1〜q=3 / q=6以降: 基準コミットとの差分なし
