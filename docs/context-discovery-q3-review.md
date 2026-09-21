# Context Discovery Phase 5 q=3 review

この文書は、生成Draftと既存Contextを比較し、Manual ReviewとApprovalを分けて記録するためのレビュー資料です。対象はVocabulary Dataから取得したq=3の4語だけです。

## difficulty

**Full Meaning:** 困難、難しさ；苦労
**Target Sense:** 困難、難しさ
**Sense Selection Reason:** 古いびんを何度も開けようとする場面で、行動の難しさを具体的に示せるため。

### Full English

1. Lena had difficulty opening an old jar because the lid was stuck.
2. She tried several times, but the lid would not move.
3. Her brother finally used a towel and opened it.

### Context Clues

- `opening an old jar` — situation
- `tried several times` — behavior
- `lid would not move` — result

### Japanese Support

`not-needed`。基本語で状況を理解でき、clueを日本語化する必要はありません。

### Choices

- A. 困難、難しさ（正解）
- B. 問題
- C. 成功
- D. 方法

**Inference Explanation:** 何度も試してもびんが開かない状況なので、difficultyは「困難、難しさ」だと推測できます。

### Existing Context comparison

既存Contextのびんの場面を維持しつつ、repeated attemptsとstuck lidを明示しました。生成版の方がclueの役割が分かれ、targetSenseを推測しやすいと判断しました。

**Structural Validation:** PASS
**Manual Review:** PASS
**Approval:** approved

## glory

**Full Meaning:** 栄光、名誉
**Target Sense:** 栄光、名誉
**Sense Selection Reason:** 勝利、観客の称賛、championという評価を一つの成功後の名誉へつなげられるため。

### Full English

1. The young runner won the race and heard the crowd cheer.
2. Newspapers praised her as the town's champion.
3. For a moment, she enjoyed the glory of her great victory.

### Context Clues

- `won the race` — cause
- `crowd cheer` — result
- `town's champion` — category

### Japanese Support

`not-needed`。勝利と称賛の場面は基本語で理解でき、clueの保護を優先しました。

### Choices

- A. 栄光、名誉（正解）
- B. 心配
- C. 計画
- D. 約束

**Inference Explanation:** レースに勝ち、観客から称賛され、町のchampionと呼ばれた人が得る名誉なので、gloryは「栄光、名誉」だと推測できます。

### Existing Context comparison

既存Contextのrunner・race・championの流れを保ちつつ、cause、public reaction、categoryを明確に分けました。生成版を採用しました。

**Structural Validation:** PASS
**Manual Review:** PASS
**Approval:** approved

## balance

**Full Meaning:** 均衡、バランス；（口座の）残高
**Target Sense:** 均衡、バランス
**Sense Selection Reason:** cyclist、wind、arms、stayed on the bikeという身体の安定場面で、口座の残高senseを自然に除外できるため。

### Full English

1. The cyclist lost his balance when a strong wind hit him.
2. He moved his arms, slowed down, and stayed on the bike.
3. A few seconds later, he was riding safely again.

### Context Clues

- `strong wind hit him` — cause
- `moved his arms` — behavior
- `stayed on the bike` — result

### Japanese Support

`not-needed`。physical stabilityの場面を基本語だけで理解でき、別senseを説明する語句もありません。

### Choices

- A. 均衡、バランス（正解）
- B. 速度
- C. 方向
- D. 体力

**Inference Explanation:** 風で倒れそうになったあと、腕を動かして自転車に乗り続けているので、balanceは「均衡、バランス」だと推測できます。

### Existing Context comparison

既存Contextと同じcycling sceneを用い、windをcause、armsをbehavior、stayed on the bikeをresultとして整理しました。口座や金銭の情報はなく、生成版のtargetSenseが一意です。

**Structural Validation:** PASS
**Manual Review:** PASS
**Approval:** approved

## priority

**Full Meaning:** 優先、優先事項
**Target Sense:** 優先、優先事項
**Sense Selection Reason:** fire alarmの後に安全を最初にする対比で、importance and orderの意味を具体化できるため。

### Full English

1. The fire alarm rang at school, so the teachers moved the children outside first.
2. Keeping everyone safe became their top priority.
3. They left the books and bags in the classroom.

### Context Clues

- `moved the children outside first` — behavior
- `Keeping everyone safe` — situation
- `top` — degree

### Japanese Support

`not-needed`。first、safe、topの関係から意味を推測でき、背景語が理解を妨げません。

### Choices

- A. 優先、優先事項（正解）
- B. 計画
- C. 結果
- D. 許可

**Inference Explanation:** 子どもたちを最初に安全な場所へ移し、全員の安全をtopに置いたので、priorityは「優先、優先事項」だと推測できます。

### Existing Context comparison

既存Contextのfire alarmと安全確保の場面を維持し、books and bags left behindを結果として残しました。生成版はfirstとtopがimportance/orderのclueとして明確です。

**Structural Validation:** PASS
**Manual Review:** PASS
**Approval:** approved

## Pipeline review status

- SOURCE: Vocabulary Dataからq=3の4語を取得
- SENSE: targetSenseとsenseSelectionReasonをDraftへ記録
- CONTEXT / CLUES / SEGMENTS / SUPPORT / CHOICES / EXPLANATION: Draft生成済み
- VALIDATE: 4語すべてPASS
- REVIEW: 4語すべてPASS
- APPROVE: 4語すべてapproved
- PUBLISH: q=3の4項目だけruntimeへ反映
- q=1 / q=2 / q=4以降: 変更なし
