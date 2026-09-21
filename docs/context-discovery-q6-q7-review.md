# Context Discovery Phase 7 q=6〜7 review

対象はVocabulary Dataから取得したq=6・q=7の8語です。Sense SelectionをContext生成前の独立工程として扱い、初期候補、初期targetSense、confidence、修正理由、最終Contextを保存しています。

## Metrics

- Generated: 8
- Sense Initial PASS: 5
- Sense REVISE: 3
- Sense Initial Pass Rate: 62.5%
- Initial Low Confidence: 2
- Final Low Confidence: 0
- Overall Initial PASS: 5
- REVISE: 3
- REJECT: 0
- Final PASS: 8
- Overall Initial Pass Rate: 62.5%
- Revision Rate: 37.5%
- Japanese Support Used: 0 / 8

## q=6

### typical

- Full Meaning: 典型的な、いつも通りの
- POS: adjective
- Candidate Senses: `典型的な、いつも通りの`
- Initial Target Sense: `典型的な`
- Sense Confidence: high
- Initial Sense Review: PASS
- Final Target Sense: `典型的な`
- Sense Revision: なし
- Context: 普通の学校の一日、決まった時間、Nothing unusualという対比。
- Japanese Support: not-needed
- Final Review / Approval: PASS / approved

### gradual

- Full Meaning: 徐々の、段階的な
- POS: adjective
- Candidate Senses: `徐々の、段階的な`
- Initial Target Sense: `徐々の、段階的な`
- Sense Confidence: high
- Initial Sense Review: PASS
- Final Target Sense: `徐々の、段階的な`
- Sense Revision: なし
- Context: 毎週少しずつ暖かくなり、雪がゆっくり消える場面。
- Japanese Support: not-needed
- Final Review / Approval: PASS / approved

### chemical

- Full Meaning: 化学の／（名）化学物質
- POS: adjective
- Candidate Senses: `化学の` / `化学物質`
- Initial Target Sense: `化学物質`
- Initial Confidence: low
- Initial Sense Review: REVISE — noun senseで、source POS adjectiveと不一致。
- Final Target Sense: `化学の`
- Sense Revision: `化学物質` → `化学の`
- Context: chemical cleaner、germs、glovesから科学・清掃に関係する形容詞を推測。
- Japanese Support: not-needed
- Final Review / Approval: PASS / approved

### false

- Full Meaning: 誤った、偽の
- POS: adjective
- Candidate Senses: `誤った、偽の`
- Initial Target Sense: `誤った、偽の`
- Sense Confidence: high
- Initial Sense Review: PASS
- Final Target Sense: `誤った、偽の`
- Sense Revision: なし
- Context: messageの内容と、開館している現実が一致しない場面。
- Japanese Support: not-needed
- Final Review / Approval: PASS / approved

## q=7

### weep

- Full Meaning: （涙を流して）泣く、すすり泣く
- POS: verb
- Candidate Senses: `（涙を流して）泣く、すすり泣く`
- Initial Target Sense: `泣く`
- Sense Confidence: high
- Initial Sense Review: PASS
- Final Target Sense: `泣く`
- Sense Revision: なし
- Context: sad movie、涙、手で涙を隠す行動。
- Japanese Support: not-needed
- Final Review / Approval: PASS / approved

### occur

- Full Meaning: 起こる、生じる；（心に）浮かぶ
- POS: verb
- Candidate Senses: `起こる、生じる` / `（心に）浮かぶ`
- Initial Target Sense: `（心に）浮かぶ`
- Initial Confidence: medium
- Initial Sense Review: REVISE — power cutは心に浮かぶものではなく、起きる出来事。
- Final Target Sense: `起こる、生じる`
- Sense Revision: `（心に）浮かぶ` → `起こる、生じる`
- Context: storm、lights go out、electricity returnsというcause/result。
- Japanese Support: not-needed
- Final Review / Approval: PASS / approved

### swell

- Full Meaning: 膨らむ、腫れる
- POS: verb
- Candidate Senses: `膨らむ、腫れる`
- Initial Target Sense: `腫れる`
- Sense Confidence: high
- Initial Sense Review: PASS
- Final Target Sense: `腫れる`
- Sense Revision: なし
- Context: injured ankle、larger and tighter、iceという場面。
- Japanese Support: not-needed
- Final Review / Approval: PASS / approved

### tap

- Full Meaning: （指などで）軽くたたく／（名）蛇口
- POS: verb
- Candidate Senses: `（指などで）軽くたたく` / `蛇口`
- Initial Target Sense: `蛇口`
- Initial Confidence: low
- Initial Sense Review: REVISE — noun senseで、source POS verbと不一致。
- Final Target Sense: `（指などで）軽くたたく`
- Sense Revision: `蛇口` → `（指などで）軽くたたく`
- Context: one finger、light touch、several timesという画面操作。
- Japanese Support: not-needed
- Final Review / Approval: PASS / approved

## Pipeline status

- SOURCE: Vocabulary Dataからq=6・q=7の8語を取得
- SENSE PARSE: `/`・`／`・`；`でsense groupを分離し、近接表現はgroupとして保持
- SENSE SELECT / VALIDATE: candidateSenses、targetSense、POS、reason、confidenceを検証
- CONTEXT / CLUES / SEGMENTS / SUPPORT / CHOICES / EXPLANATION: 最終targetSenseを入力として生成・検証
- REVIEW: Sense reviewとContext reviewを分離
- APPROVE: Sense / Context structural PASS、Manual Review PASS、confidence highを確認
- PUBLISH: q=6・q=7の8項目だけruntimeへ反映
- q=1〜q=5 / q=8以降: 基準コミットとの差分なし
