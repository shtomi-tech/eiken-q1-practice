# Context Leakage Validator

The leakage pre-check runs after context generation and clue extraction, before manual review.

## Results

- `PASS`: no deterministic leakage or configured answer-equivalent hint was found.
- `WARN`: a strong synonym or paraphrase may be too close to the answer. Manual review must explicitly accept it before publication.
- `FAIL`: a direct definition, exposed Japanese meaning, or accumulated answer-equivalent paraphrases make inference unnecessary. Publication is blocked.

## Finding types

- `DIRECT_DEFINITION`: the target is followed by a definition marker such as `which means` or `that is`.
- `SYNONYM_LEAKAGE`: a near-synonym may give away the answer.
- `PARAPHRASE_LEAKAGE`: a phrase or combination of phrases may fully restate the answer.
- `TRANSLATION_LEAKAGE`: the Japanese target sense appears before answer confirmation.
- `OTHER_LEAKAGE`: a reviewed leakage pattern outside the categories above.

Synonym and paraphrase matches normally produce `WARN`; they are not rejected merely for being strong clues. Two configured answer-equivalent hints in one context produce `FAIL`. This keeps behavioral, cause/effect, contrast, result, and appearance clues usable.

The validator is a pre-check, not a replacement for human review. A published `WARN` requires `leakageReview.status = "accepted"` and a reason. `FAIL` cannot be published.

Regression fixtures cover the Phase 9 initial/final contexts for `for a fresh start`, `on one's own`, and `at a distance`, plus direct-definition and translation failures and strong-clue positive cases.
