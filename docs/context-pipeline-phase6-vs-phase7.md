# Context Discovery Phase 6 vs Phase 7

Phase 6とPhase 7は、どちらもq=4語×2問の8語batchです。Phase 6のmetricsは `data/context-pipeline-metrics/eiken2-2026-1-q4-q5.json`、Phase 7のmetricsは `data/context-pipeline-metrics/eiken2-2026-1-q6-q7.json` に保存しています。

| Metric | Phase 6 q=4〜5 | Phase 7 q=6〜7 |
| --- | ---: | ---: |
| Generated | 8 | 8 |
| Initial PASS | 3 | 5 |
| Initial Pass Rate | 37.5% | 62.5% |
| Revision Rate | 62.5% | 37.5% |
| SENSE revisions | 4 / 8 | 3 / 8 |
| Sense Initial Pass Rate | 記録なし | 62.5% |
| Final PASS | 8 | 8 |
| Japanese Support Used | 0 | 0 |

Phase 7ではSense Selectionを独立させ、POS不一致や、文脈に合わない既知senseを初稿段階でレビュー対象にしました。Initial Pass Rateは37.5%から62.5%へ上がり、SENSE修正は4件から3件へ減りました。ただしbatch数が少ないため、全語展開の安全性を意味する数値ではありません。

## Phase 7 Sense revisions

- `chemical`: `化学物質` → `化学の`。source POSがadjective。
- `occur`: `（心に）浮かぶ` → `起こる、生じる`。停電という出来事のcontext。
- `tap`: `蛇口` → `（指などで）軽くたたく`。source POSがverb。

## Review conclusion

Sense Selectionを独立工程にしたことで、今回の3件はContext生成後ではなく、候補sense・POS・文脈のレビューで修正できました。次のbatchでは、sense parserの表記揺れと、close sense groupの扱いを引き続き確認します。
