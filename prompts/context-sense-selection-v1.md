# Context Discovery target sense selection prompt v1 (POS-aware)

## Role

Select the single target sense that a Context Discovery item will teach. This is a separate step from writing the English context.

## Input

```json
{
  "target": "occur",
  "meaning": "起こる、生じる；（心に）浮かぶ",
  "pos": "verb",
  "level": "EIKEN Grade 2",
  "candidateSenses": [
    { "sense": "起こる、生じる", "pos": "verb" },
    { "sense": "（心に）浮かぶ", "pos": "verb" }
  ],
  "eligibleSenses": [
    { "sense": "起こる、生じる", "pos": "verb" },
    { "sense": "（心に）浮かぶ", "pos": "verb" }
  ],
  "filteredOutSenses": []
}
```

## Required process

1. Parse the meaning into `candidateSenses`. Keep close expressions such as `育む、促進する` together; separate groups divided by `/`, `／`, or `；`.
2. Deterministically compare each candidate POS with the source POS. Put compatible candidates in `eligibleSenses` and put every incompatible candidate in `filteredOutSenses` with `reason: "source-pos-mismatch"`. Do not send filtered candidates to selection and never restore them.
3. If no candidate remains eligible, return a validation failure. If one remains, it is the deterministic candidate, but it still requires pedagogical review.
4. If several eligible candidates remain, choose one with appropriate learning value and specificity. Do not choose a narrow sense only because it is easy to write a context for.
5. Explain why the selected sense is supported and why the other eligible major senses are distinct.
6. Return `high`, `medium`, or `low` confidence. Low confidence requires manual review and cannot be auto-approved.

## Output

```json
{
  "candidateSenses": [
    { "sense": "起こる、生じる", "pos": "verb" },
    { "sense": "（心に）浮かぶ", "pos": "verb" }
  ],
  "eligibleSenses": [
    { "sense": "起こる、生じる", "pos": "verb" },
    { "sense": "（心に）浮かぶ", "pos": "verb" }
  ],
  "filteredOutSenses": [],
  "targetSense": "起こる、生じる",
  "senseSelectionReason": "...",
  "senseConfidence": "high"
}
```

Do not write the Context in this step. Do not mark review or approval as passed.
