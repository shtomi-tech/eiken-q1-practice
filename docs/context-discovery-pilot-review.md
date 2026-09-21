# Context Discovery Phase 3 pilot review

対象は `q=1` の4語だけです。各項目は、100% Englishのcanonical context、必要な場合だけ使うJapanese Support、target専用4択、推論説明を持ちます。

## bride

### Full English

1. At the wedding, the bride stood beside her new husband in a long white dress.
2. Everyone watched as they promised to live together.
3. After the ceremony, guests took pictures of the happy couple.

### Mixed Context

1. At the wedding, the bride stood beside her new husband in a long white dress.
2. Everyone watched as they promised to live together.
3. After the ceremony, guests took pictures of the happy couple.

### Clues

- `wedding` — situation
- `new husband` — category
- `long white dress` — example

### Choices

- A. 花嫁、新婦（正解）
- B. 花婿、新郎
- C. 結婚式の参列者
- D. 結婚式の司会者

### Support decision

Japanese Support: **不要**。`after` は基本語で、`ceremony` も直前の wedding から意味領域を推測できます。clueである wedding、new husband、long white dress は英語のまま残し、推測材料を保護しています。

### Inference

結婚式で新しい夫の隣に立ち、白いドレスを着ている人物という3つの情報を組み合わせると、brideの意味を推測できます。

## lawyer

### Full English

1. Mika got a letter about a problem with her neighbor.
2. The letter said that her neighbor wanted to take her to court.
3. She met a lawyer, who read the papers and explained what she should do.

### Mixed Context

1. Mika got a letter about a problem with her neighbor.
2. The letter said that her neighbor wanted to take her to court.
3. She met a lawyer, who read the papers and explained what she should do.

### Clues

- `take her to court` — situation
- `read the papers` — behavior
- `explained what she should do` — behavior

### Choices

- A. 弁護士、法律家（正解）
- B. 裁判官
- C. 警察官
- D. 記者

### Support decision

Japanese Support: **不要**。`Mika got a letter about a problem with her neighbor` は基本語で構成され、場面設定も英文のまま理解できます。`take her to court`、`read the papers`、`explained what she should do` はclueのため英語で保護しています。

### Inference

裁判に関する書類を読み、どうすればよいかを説明している人物なので、lawyerの意味を推測できます。

## warrior

### Full English

1. The museum showed a statue of a warrior holding a sword and shield.
2. The guide said he protected his people in many battles.
3. Children imagined him fighting long ago.

### Mixed Context

1. The museum showed a statue of a warrior holding a sword and shield.
2. The guide said he protected his people in many battles.
3. Children imagined him fighting long ago.

### Clues

- `sword and shield` — example
- `protected his people` — behavior
- `many battles` — situation

### Choices

- A. 戦士、武人（正解）
- B. 商人
- C. 農民
- D. 職人

### Support decision

Japanese Support: **不要**。語彙と文構造が比較的基本的で、重要な表現がすべてclueとして機能します。日本語化すると、武器・防衛・戦いという推測材料の一部を隠してしまいます。

### Inference

武器を持ち、人々を守るために多くの戦いで戦った人物という情報から、warriorの意味を推測できます。

## surgeon

### Full English

1. After the accident, David needed an operation, so a surgeon came to see him.
2. The doctor carefully operated on his injured leg.
3. A few hours later, the operation was finished and David began to recover.

### Mixed Context

1. After the accident, David needed an operation, so a surgeon came to see him.
2. The doctor carefully operated on his injured leg.
3. A few hours later, the operation was finished and David began to recover.

### Clues

- `needed an operation` — situation
- `doctor` — category
- `operated on his injured leg` — behavior

### Choices

- A. 外科医（正解）
- B. 看護師
- C. 患者
- D. 薬剤師

### Support decision

Japanese Support: **不要**。`After the accident` と `A few hours later` は基本的な時間・背景表現です。`needed an operation`、`doctor`、`operated on his injured leg` はtargetの意味を絞る中心的なclueのため英語で保護しています。

### Inference

手術が必要な場面で、医師として脚を手術している人物なので、surgeonの意味を推測できます。

## Review status

- Structural validator: PASS
- Japanese Support: 0 segments for all 4 items
- Target occurrence: 4語とも1回
- Context clues: 4語とも3件、すべてFull Englishに存在
- Target / clue protection: PASS
- Target-specific choices: 4語とも4件、正解は一意
- Structural validationとManual Review metadataを分離
- Manual review: 4語ともPASS（自然さ、targetの未知性、clue品質、leakage、Support必要性、distractor品質）
