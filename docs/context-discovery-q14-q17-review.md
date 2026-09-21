# Context Discovery q=14–17 Review

Source of truth: `data/vocab_2026-1.json`. Full initial/final contexts, sense candidates, clues, choices, leakage findings, review checks, and revisions are recorded in `data/context-drafts/eiken2-2026-1-q14-q15-q16-q17-review.json`.

## Batch result

| q | Target | Target sense | Initial leakage | Final leakage | Revision | Approval |
|---|---|---|---|---|---|---|
| 14 | a series of | 一連の、ひと続きの | PASS | PASS | — | approved |
| 14 | the edge of | 〜の端、縁 | WARN | PASS | manual LEAKAGE | approved |
| 14 | a member of | 〜の一員、メンバー | PASS | PASS | — | approved |
| 14 | the back of | 〜の後ろ、裏 | FAIL | PASS | pre-review LEAKAGE | approved |
| 15 | in other words | 言い換えれば、つまり | PASS | PASS | — | approved |
| 15 | in the beginning | 最初は、初めのうちは | PASS | PASS | — | approved |
| 15 | back and forth | 行ったり来たり、前後に | WARN | WARN (accepted) | — | approved |
| 15 | on the contrary | それどころか、（前言を否定して）逆に | PASS | PASS | — | approved |
| 16 | distinct from | 〜とは異なる、別個の | WARN | WARN (accepted) | — | approved |
| 16 | composed of | 〜から構成されている | PASS | PASS | — | approved |
| 16 | absent from | 〜を欠席して、〜にいない | PASS | PASS | — | approved |
| 16 | threatening to | 〜しそうで | PASS | PASS | — | approved |
| 17 | lay off | （従業員を）一時解雇する、レイオフする | PASS | PASS | — | approved |
| 17 | flip over | ひっくり返る、裏返す | WARN | WARN (accepted) | — | approved |
| 17 | bring about | 引き起こす、もたらす | PASS | PASS | — | approved |
| 17 | catch up | （遅れを）取り戻す | PASS | PASS | — | approved |

## Leakage revisions

`the back of` initially combined `behind` and `far from the front`; the validator classified the accumulated paraphrase as `FAIL`. Before manual review, it was replaced with observable evidence: old letters must be removed before the keys can be reached.

`the edge of` initially used `farthest part`. Manual review replaced it with the bird's position near a rain gutter and its downward view.

The remaining warnings were accepted because they are strong contextual evidence rather than direct definitions: repeated movement across a court (`back and forth`), a visible species distinction (`distinct from`), and changing which side of a card is visible (`flip over`).

Japanese Support was not needed for any item. Target and clue segments remain English. Batch diversity passed for scenes, sentence patterns, clue types, distractors, and leakage-avoidance patterns.
