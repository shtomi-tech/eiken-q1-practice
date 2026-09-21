# Context Discovery generation prompt v1

## Role

Create a short Context Discovery learning item for an EIKEN learner. The target is the main unknown item; the learner must infer the selected `targetSense` by combining multiple clues.

## Input

```json
{
  "q": 3,
  "target": "...",
  "meaning": "Vocabulary Data meaning",
  "pos": "noun",
  "level": "EIKEN Grade 2"
}
```

## Required process

1. Select exactly one `targetSense` from the vocabulary meaning and record `senseSelectionReason`.
2. Write `fullEnglish` first: 2–3 coherent sentences, 100% English, with the target appearing once.
3. Extract at least two independent clues from the completed English context.
4. Segment the English without changing its text. Protect target and clue segments.
5. Start Japanese Support off. Set `supportDecision` to `not-needed` unless a non-clue phrase is meaningfully difficult and materially blocks comprehension. If needed, record a concrete `supportReason`.
6. Create four target-sense choices. Do not use another known sense of the same word as a distractor.
7. Write an inference explanation that names the clues and identifies the targetSense.

## Prohibitions

- Do not directly define or translate the target in the context.
- Do not use a simple synonym that gives away the answer.
- Do not Japanese-translate the target or a clue.
- Do not force a fixed Japanese ratio.
- Do not use advanced non-clue vocabulary when simpler English works.

## Output

Return a draft item with `targetSense`, `senseSelectionReason`, `fullEnglish`, `mixedEnglish`, `contextClues`, `inferencePath`, `segments`, `supportDecision`, `choices`, `answerIndex`, and `inferenceExplanation`. Generation must leave `manualReview.status` and `approval.status` as `pending`.
