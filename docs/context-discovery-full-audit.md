# Context Discovery Full Dataset Audit

## Dataset

- Dataset: `eiken2-2026-1`
- Baseline: `5ce31e1007e50e41a92dd78ce9d4cd0e19060b56`
- Vocabulary: 68
- Context: 68
- Scope: q=1–17, four items per q
- Target order: MATCH
- Runtime changes: 0

## Summary

- PASS: 64
- WARN: 4
- REVISE: 0
- Pass rate: 94.12%
- Warn rate: 5.88%
- Revision rate: 0%
- Critical findings: 0
- Major findings: 0
- Minor findings: 4

All 68 items passed dataset integrity, hardened sense compatibility, context structure, clue presence and protection, segment reconstruction, Japanese Support, choices, answer index, and inference-explanation checks. Manual review covered target sense, main-unknown control, clue independence, leakage, difficulty, naturalness, distractors, and answer uniqueness.

## Leakage review

Leakage results were 64 PASS, 4 WARN, and 0 FAIL. Every warning was reviewed and accepted; none is an unresolved exception.

| Target | q | Warning | Review |
|---|---:|---|---|
| on one's own | 12 | `no one helped` | Strong behavioral evidence; the complete repair scene must still be interpreted as independent action. |
| back and forth | 15 | `to the other side, then moved back again` | Strong motion evidence rather than an explicit definition or translation. |
| distinct from | 16 | `different species` | Confirms a visible contrast without directly defining the target phrase. |
| flip over | 17 | `turn it around` | Observable card-handling behavior; the other-side result remains part of the inference. |

The four warnings are retained as minor audit findings. Direct-definition, translation-leakage, and unresolved answer-equivalent leakage findings were zero.

## Multi-sense inventory

Twenty-one items have more than one parsed sense group:

`branch`, `scale`, `trail`, `difficulty`, `balance`, `discrimination`, `shelter`, `content`, `foster`, `divide`, `pronounce`, `chemical`, `occur`, `tap`, `illustrate`, `occupy`, `polish`, `slip`, `take away from`, `threatening to`, and `catch up`.

All selected senses matched an exact normalized sense part in Vocabulary Data and were manually reviewed as uniquely supported by their context. The audit no longer accepts arbitrary substring containment as sense compatibility.

## q results

- q1–q11: 44 PASS
- q12: 3 PASS, 1 WARN
- q13–q14: 8 PASS
- q15: 3 PASS, 1 WARN
- q16: 3 PASS, 1 WARN
- q17: 3 PASS, 1 WARN

Phase-group results are stored in the machine-readable artifact. Older and newer groups had no REVISE item.

## Naturalness and diversity

Manual review found no grammatical, collocational, target-usage, or scene-coherence issue requiring revision. Phrase and phrasal-verb contexts received the same checks as single words.

Cross-item diversity passed for scenes, sentence patterns, clue types, and distractors. Contexts cover school, home, travel, medicine, weather, work, sport, public services, and object-handling situations. No duplicate full context was found. Repeated names or ordinary three-sentence structure were not treated as defects by themselves.

## Japanese Support

Japanese Support is used by 0 of 68 items. This is valid: every context remained comprehensible at the intended level without translating targets or clues.

## Initial and final audit

The machine-readable artifact preserves `initialAudit`, `manualAudit`, `revision`, and `finalAudit` for every item. Because no item was marked REVISE, initial and final content are identical and `revision` is `null`. Runtime data was therefore left unchanged.

Machine-readable results: `data/context-audits/eiken2-2026-1-full-audit.json`.
