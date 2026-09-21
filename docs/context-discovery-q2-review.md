# Context Discovery Phase 4 q=2 review

対象はq=2の4語です。`meaning`はVocabulary Dataの全体意味、`targetSense`は今回のContextで発見する意味です。4語ともJapanese Supportは不要と判断しました。

## globe

**Full Meaning:** 地球儀、球体、地球
**Target Sense:** 地球儀

### Full English

1. In geography class, Ken could not find Brazil on the wall map.
2. His teacher gave him a globe, and he turned the round model until he found South America.
3. He then pointed to Japan on the same model.

### Mixed Context

Full Englishと同一です。

### Clues

- `geography class` — situation
- `turned the round model` — behavior
- `found South America` — example

### Choices

- A. 地球儀（正解）
- B. 地図
- C. 方位磁針
- D. 教科書

**Correct:** 地球儀
**Japanese Support:** 不要
**Support Reason:** 基本語と地理の場面で理解でき、SupportがなくてもtargetSenseの推測を妨げません。

### Sense Review

- `senseAppropriate`: PASS
- `senseUniquelySupported`: PASS — 国や大陸を探すために回す丸い模型なので、球体一般や地球そのものではなく地球儀です。
- `otherKnownSensesExcluded`: PASS — 「球体」「地球」はchoicesに入れていません。

**Distractor Review:** PASS。地理の授業で見かける物を選び、既知の別senseは避けています。
**Structural Validation:** PASS
**Manual Review:** PASS

## branch

**Full Meaning:** 枝；支店、部門
**Target Sense:** 枝
**Other Senses:** 支店、部門

### Full English

1. A bird landed on a branch high in the tree.
2. The thin part bent under its weight, but it did not break.
3. The bird soon flew to another part of the tree.

### Mixed Context

Full Englishと同一です。

### Clues

- `bird landed` — situation
- `thin part bent` — behavior
- `high in the tree` — location

### Choices

- A. 枝（正解）
- B. 幹
- C. 葉
- D. 根

**Correct:** 枝
**Japanese Support:** 不要
**Support Reason:** 木・鳥・曲がる細い部分という基本的な場面で理解でき、clueを隠すSupportは不要です。

### Sense Review

- `senseAppropriate`: PASS
- `senseUniquelySupported`: PASS — 鳥が木の高い場所で止まり、重さで曲がる木の一部なので「枝」です。
- `otherKnownSensesExcluded`: PASS — 「支店」「部門」は木の場面では成立せず、choicesにも入れていません。

**Distractor Review:** PASS。木の部分としてもっともらしい選択肢ですが、鳥が止まり曲がる細い部分というclueで枝だけに決まります。
**Structural Validation:** PASS
**Manual Review:** PASS

## scale

**Full Meaning:** 規模；目盛り；はかり；うろこ
**Target Sense:** はかり
**Other Senses:** 規模、目盛り、うろこ

### Full English

1. The nurse asked me to step on a scale before the checkup.
2. The numbers rose when I held my bag, so I put it on the floor.
3. The nurse wrote down my weight.

### Mixed Context

Full Englishと同一です。

### Clues

- `step on` — behavior
- `numbers rose` — result
- `wrote down my weight` — situation

### Choices

- A. はかり（正解）
- B. 温度計
- C. 時計
- D. 血圧計

**Correct:** はかり
**Japanese Support:** 不要
**Support Reason:** checkup、numbers、weightの関係が英文から理解でき、他のsenseを説明する語彙も出てきません。

### Sense Review

- `senseAppropriate`: PASS
- `senseUniquelySupported`: PASS — 乗る、数値が変わる、体重を記録するという一連の行動から、重さを測る「はかり」に一意に決まります。
- `otherKnownSensesExcluded`: PASS — 「規模」「目盛り」「うろこ」はchoicesに入れていません。

**Distractor Review:** PASS。健康診断で使う道具としては近いものを置いていますが、step onとweightで正解は一意です。
**Structural Validation:** PASS
**Manual Review:** PASS

## trail

**Full Meaning:** （山などの）小道；跡、痕跡
**Target Sense:** （山などの）小道
**Other Senses:** 跡、痕跡

### Full English

1. We followed a narrow trail through the forest.
2. Red marks on the trees showed us which way to go.
3. After an hour, the path led us to a lake.

### Mixed Context

Full Englishと同一です。

### Clues

- `followed` — behavior
- `narrow` — description
- `path led us to a lake` — result

### Choices

- A. （山などの）小道（正解）
- B. 道路
- C. 川
- D. 階段

**Correct:** （山などの）小道
**Japanese Support:** 不要
**Support Reason:** forest、narrow、path、lakeの場面で意味を推測でき、背景語が理解を妨げません。

### Sense Review

- `senseAppropriate`: PASS
- `senseUniquelySupported`: PASS — 森の中をたどり、湖へ続く狭い道なので「小道」です。
- `otherKnownSensesExcluded`: PASS — 「跡」「痕跡」は道をたどる場面の別解釈にならず、choicesにも入れていません。

**Distractor Review:** PASS。屋外の経路・地形として近い選択肢ですが、forestを通ってlakeへ続くnarrow pathなので小道だけが成立します。
**Structural Validation:** PASS
**Manual Review:** PASS

## Overall review

- q=1 golden sample: regression PASS
- q=2 targetSense: 4語すべて定義済み
- Japanese Support: 0 segments
- 別sense distractor: なし
- Context data outside q=1 and q=2: unchanged
