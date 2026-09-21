# Context Discovery target sense selection prompt v1

## Role

Select the single target sense that a Context Discovery item will teach. This is a separate step from writing the English context.

## Input

```json
{
  "target": "scale",
  "meaning": "規模；目盛り；はかり；うろこ",
  "pos": "noun",
  "level": "EIKEN Grade 2"
}
```

## Required process

1. Parse the meaning into sense groups. Keep close expressions such as `育む、促進する` together; separate groups divided by `/`, `／`, or `；`.
2. Use the source POS as a hard filter. Do not select a noun sense for an adjective source, or an adjective sense for a noun source.
3. Choose one sense with appropriate learning value and appropriate specificity. Do not choose a narrow sense only because it is easy to write a context for.
4. Explain why the selected sense is supported and why the other major senses are distinct.
5. Return `high`, `medium`, or `low` confidence. Low confidence requires manual review and cannot be auto-approved.

## Output

```json
{
  "candidateSenses": [
    { "sense": "規模", "pos": "noun" },
    { "sense": "目盛り", "pos": "noun" },
    { "sense": "はかり", "pos": "noun" },
    { "sense": "うろこ", "pos": "noun" }
  ],
  "targetSense": "はかり",
  "senseSelectionReason": "...",
  "senseConfidence": "high"
}
```

Do not write the Context in this step. Do not mark review or approval as passed.
