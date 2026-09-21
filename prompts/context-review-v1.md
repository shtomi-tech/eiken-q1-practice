# Context Discovery review prompt v1

Review a generated Context Discovery draft independently from the generation step.

Return `PASS`, `REVISE`, or `REJECT`, with reasons for each failed or uncertain check.

## Review checks

- `senseAppropriate`
- `senseUniquelySupported`
- `otherKnownSensesExcluded`
- `targetMainUnknown`
- `clueQuality`
- `clueIndependence`
- `noAnswerLeakage`
- `noSynonymLeakage`
- `contextCoherent`
- `difficultyAppropriate`
- `naturalEnglish`
- `supportNecessary`
- `distractorQuality`
- `answerUnique`

Do not approve an item only because its structural fields are present. Check whether the context genuinely supports the selected targetSense and whether the choices remain uniquely answerable.
