# E10 results: fallback triage on new items (T48, V01–V40)
Claude (supervisor-delegated), 2026-11-16. The data were scored once, with the frozen scorers.

**Freezes:**
- `e10_plan_freeze.sha256`: plan and scorers, before T48.
- `e10_packages_freeze.sha256`: packages, TASK files and the cluster addendum, before any blind run.
- `e10_outputs_freeze.sha256`: the six outputs, before scoring.

All three were re-verified before scoring. The package trees were unchanged (`ad160454…` for all three).

**Raw outputs:** `e10_score_output.txt`, `e10_scores.csv`, `e10_cluster_output.txt`. The exploratory analyses are in `e10_exploratory_output.txt`.

## Data and runs
**Items:** 40 V items (truth SPEC 21 / IMPL 19, no BOTH). They come from **21 mined candidates** in 8 repos.

**Final kinds:** D/A/U = 24/13/3. Kind coders C9 and C10: κ = 0.853. All 3 UNCLEAR items are coder disagreements.

**Runs:** six blind Codex runs (gpt-6.1-sol, high effort).
- C9, C10: kind coders. TASK_CODE is byte-identical to E7's.
- L3, L4: M1, the zero-shot triage task with five possible answers.
- F1, F2: M1F, the forced choice between SPEC and IMPL.

Five runs hit the Codex usage limit and were resumed in their own sessions. All six finished with complete outputs (40 rows each, in order, valid values).

**Boundary audit:** every command in every log ran in the run's own directory. Nothing outside it was read except `PROTOCOL.md`. The only audit flags were sentences in the reports stating that the board had *not* been read.

## Pre-registered tests
| Test | Result | Verdict |
|---|---|---|
| **H-E10-1 (primary):** R correct on M1 abstention pairs | 6/6 pairs (L3 3/3, L4 3/3); binomial one-sided p = 0.0156. Unique items: 3/3, p = 0.125 | **INSUFFICIENT** (needs at least 8 pairs) |
| **H-E10-2 (key secondary):** FB better than M1F | Pooled: 0 wins, 8 losses (L3–F1 0/5, L4–F2 0/3); p = 1.0 | **NOT_BETTER**. The reverse test is significant: p = 0.0039, M1F better than FB |
| **H-E10-3:** replication of kind × direction | DELIBERATE → SPEC 19/24 vs ACCIDENTAL → SPEC 2/13; Fisher one-sided p = 2.7e-4 | **PASS** |

### Cluster sensitivity (frozen addendum)
| Test | By cluster |
|---|---|
| H-E10-1 | Only **1** cluster contains abstention pairs: R is right in 1, wrong in 0; p = 0.5 |
| H-E10-2 | FB better in 0 clusters, M1F better in 2, equal in 19. p(M1F > FB) = 0.25 |

As the addendum requires, the item-level reverse result for H-E10-2 is reported here next to its cluster-level result. The M1F advantage comes from just **2 of 21 clusters**, so at the cluster level it is not significant.

## Descriptive results (pre-registered)
| Method | macro-F1 | Decided accuracy | Coverage |
|---|---|---|---|
| R (kind rule) | 0.766 | 0.81 | 0.93 |
| M1, L3 / L4 | 0.575 / 0.639 | 0.65 / 0.71 | 0.85 / 0.85 |
| FB, L3 / L4 | 0.646 / 0.702 | 0.68 / 0.73 | 0.93 / 0.93 |
| FBS, L3 / L4 | 0.619 / 0.673 | 0.62 / 0.68 | 1.00 / 1.00 |
| M1F, F1 / F2 | 0.744 / 0.744 | 0.75 / 0.75 | 1.00 / 1.00 |

**Labeller agreement:** L3–L4 38/40; F1–F2 40/40.

**M1 correctness by kind:**
| Kind | L3 | L4 |
|---|---|---|
| DELIBERATE | 11/24 | 11/24 |
| ACCIDENTAL | 11/13 | 13/13 |
| UNCLEAR | 0/3 | 0/3 |

## Exploratory (post-hoc; not confirmatory)
1. **One cluster-heavy repo drives M1's drop.**
   - rhsm-subscriptions gives 10 items from only 2 clusters: 9 SPEC, all DELIBERATE.
   - Every labeller is right on just 1/10 there; all four call them IMPL. R is right on 9/10.
   - Across the sample, M1 misses 12 DELIBERATE/SPEC items. Of these misses, **9 are confident IMPL labels** and 3 are UNDECIDABLE, and they come from only 2 clusters.
   - So on this sample, M1 fails by being *wrong*, not by abstaining. That is unlike E9, and it is why the fallback pairs were too few for H-E10-1.
2. **R-first combination:** use R when it decides, otherwise the labeller.
   - R-first + M1: macro-F1 0.766.
   - R-first + M1F: macro-F1 0.822 (accuracy 0.82, coverage 1.00).
   - In E9 the opposite order looked best. The best combination therefore depends on the sample. Neither is established.
3. **H-E10-3 by cluster** (majority kind and direction, ties dropped): DELIBERATE → SPEC 7/11 vs ACCIDENTAL → SPEC 1/9, Fisher p = 0.025. The replication holds at the cluster level too.
4. **ACCIDENTAL items fixed in the SPEC:**
   - 2 items, both from one kratos cluster.
   - These are the first accidental → SPEC cases in any confirmatory sample (E7: 0/11, E8b: 0/10, E9: 0/24).
   - So "accidental → never SPEC" is not a law. These samples overlap (E9 Part B recoded the E7 and E8b items), so their counts are not summed here.

## Interpretation
- **RQ1 (kind predicts repair direction): replicated again, on a new sample.** It holds by item (p = 2.7e-4) and by cluster (p = 0.025). This is the robust finding of R1.
- **RQ2 (fallback pipeline): not supported.**
  - The pre-registered primary test is INSUFFICIENT, because M1 rarely abstained.
  - The fallback lost to forced choice at item level. At cluster level this rests on 2 clusters and is not significant.
  - The E9 post-hoc gain (0.976) did **not** replicate: FB here scores 0.646 / 0.702.
- **Robustness of the LLM triage itself:**
  - M1's macro-F1 fell from 0.90–0.91 (E9) to 0.58–0.64 on this sample, while the kind rule R held at 0.77.
  - With few clusters, the accuracy of an LLM triage can swing widely from sample to sample. That is a threat to every single-sample triage evaluation, ours included.

## Threats
- **Small and clustered sample:** 40 items, 21 clusters; one repo contributes 10 items in 2 clusters.
- **All coders and labellers are one model family** (gpt-6.1-sol). There is no human validation yet; the human spot-check is pending.
- **Ground truth assumes the developer's fix direction is the correct one.**
- **Codex usage-limit interruptions:** five runs were resumed in their own sessions, and the prompt was unchanged except for the resume note.
