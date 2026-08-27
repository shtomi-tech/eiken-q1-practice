# 英検1級 模試第6回レビュー

## 出典と登録方針

- 入力: ユーザー提供画像5枚。画像上の原本表記は「模擬テスト 第1回」だが、依頼に合わせてアプリでは eiken1-mock-6（模試第6回）として登録した。
- 設問文: 画像の25問を転記した。
- 語句: 既存の1級語彙プール、data/lemmas.json、全配信データの熟語phraseとの重複を避けるため、下表の選択肢を置換した。置換後も設問文の空所位置と文脈は維持している。
- 熟語: 14件に核心イメージを付与し、come clean と rooted for は構成語からの導出が安定しないC型とした。

## 独立レビュー

ローカルの別モデル qwen3:8b に設問文と4択だけを渡し、正答キーを伏せて文脈上の成立性を確認した。Q1〜Q25はすべて、成立する選択肢が1つだけという判定だった。

| 設問 | 成立する選択肢（1-based） | 判定 |
| --- | ---: | --- |
| Q1 | 2 | UNIQUE |
| Q2 | 1 | UNIQUE |
| Q3 | 1 | UNIQUE |
| Q4 | 1 | UNIQUE |
| Q5 | 3 | UNIQUE |
| Q6 | 1 | UNIQUE |
| Q7 | 3 | UNIQUE |
| Q8 | 2 | UNIQUE |
| Q9 | 2 | UNIQUE |
| Q10 | 4 | UNIQUE |
| Q11 | 3 | UNIQUE |
| Q12 | 4 | UNIQUE |
| Q13 | 2 | UNIQUE |
| Q14 | 2 | UNIQUE |
| Q15 | 1 | UNIQUE |
| Q16 | 2 | UNIQUE |
| Q17 | 1 | UNIQUE |
| Q18 | 2 | UNIQUE |
| Q19 | 1 | UNIQUE |
| Q20 | 1 | UNIQUE |
| Q21 | 1 | UNIQUE |
| Q22 | 2 | UNIQUE |
| Q23 | 4 | UNIQUE |
| Q24 | 4 | UNIQUE |
| Q25 | 2 | UNIQUE |

## 置換した選択肢

| 設問 | 画像原稿 | 登録語句 | 理由 |
| --- | --- | --- | --- |
| Q1 | soaring | rambling | 既存1級語彙との重複回避 |
| Q3 | expedite / sedate | accelerate / soothe | 既存1級語彙との重複回避 |
| Q5 | echelons | strata | 語形を含む既存1級語彙との重複回避 |
| Q6 | inconspicuous / evocative | decorous / methodical | 既存1級語彙との重複回避 |
| Q7 | inherently | mechanically | 既存1級語彙との重複回避 |
| Q8 | pertinent | germane | 既存1級語彙との重複回避 |
| Q11 | inhaled / fazed / honed | shelved / neglected / sharpened | 既存1級語彙・原形辞書との重複回避 |
| Q13 | aberration | anomaly | 既存1級語彙との重複回避 |
| Q14 | stampede / perplex | celebrate / perambulate | 既存1級語彙・原形辞書との重複回避 |
| Q20 | caustic | insouciant | 既存1級語彙との重複回避 |
| Q21 | senile | frail | 既存1級語彙との重複回避 |
| Q22 | stand up to | turn off | 既存1級熟語phraseとの重複回避 |
| Q23 | buckle down / pan out / own up | hang around / wait around / come clean | 既存1級熟語phraseとの重複回避 |
| Q24 | frittered away | threw away | 既存1級熟語phraseとの重複回避 |
