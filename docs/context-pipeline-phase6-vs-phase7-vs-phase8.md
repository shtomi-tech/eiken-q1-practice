# Context Discovery pipeline comparison

この表は、各Phaseの対象batchについて実測した値を記録する。対象語がPhaseごとに異なるため、数値だけで改善の因果を断定しない。

| Metric | Phase 6 (q=4–5) | Phase 7 (q=6–7) | Phase 8 (q=8–9) |
| --- | ---: | ---: | ---: |
| Generated | 8 | 8 | 8 |
| Initial PASS | 3 | 5 | 8 |
| Initial Pass Rate | 37.5% | 62.5% | 100% |
| Revision Rate | 62.5% | 37.5% | 0% |
| SENSE revisions | 4 | 3 | 0 |
| Sense Initial Pass Rate | — | 62.5% | 100% |
| POS-filtered items | — | — | 0 |
| POS-filtered senses | — | — | 0 |
| POS-prevented revisions | — | — | 0 |
| Final PASS | 8 | 8 | 8 |

## Phase 8 batch observation

q=8–9では、`illustrate`、`occupy`、`polish` が複数の同一POS候補を持ち、5語はeligible senseが1件だった。今回のbatchにはPOS不一致候補がなかったため、`posPreventedRevisionCount` は0である。`chemical` と `tap` のPOS除外、`occur` の同一POS複数候補は、Phase 8の回帰fixtureで別途検証する。

Japanese Supportは8語すべてで不要だった。初稿レビューは8件すべてPASSで、修正履歴はない。
