# Contract specificity on the later samples (EXPLORATORY)
Claude, 2026-11-17. This analysis is **post hoc**: it was written after E10, E12 and E13 had all been scored, and it was not pre-registered.

**Question.** Does H-E7-2, P(SPEC | GENERIC) > P(SPEC | SPECIFIC), hold up on the disjoint new-item samples?

**Method.**
- A specificity code counts only when both coders of a family agree.
- BOTH items are excluded.
- One-sided Fisher test.
- Script: `specificity_explore.py`. Output: `specificity_explore_output.txt`.

| Sample, coders | All kinds: GENERIC vs SPECIFIC → SPEC | p | DELIBERATE only | p |
|---|---|---|---|---|
| E7, C1/C2 (H-E7-2, confirmatory) | 15/18 vs 11/26 | 0.007 | — | — |
| E10, GPT | 17/18 vs 3/15 | 1.5e-5 | 17/18 vs 1/2 | 0.20 |
| E12, GPT | 11/13 vs 8/18 | 0.027 | 11/11 vs 5/5 | 1 |
| E12, Claude | 6/14 vs 10/17 | 0.89 | 6/6 vs 7/7 | 1 |
| E13, GPT | 9/12 vs 25/46 | 0.17 | 9/11 vs 24/32 | 0.50 |
| E13, Claude | 8/11 vs 23/44 | 0.19 | 8/8 vs 23/28 | 0.26 |
| **Pooled GPT, E10 + E12 + E13** | **37/43 vs 36/79** | **7.6e-6** | **37/40 vs 30/39** | **0.052** |

Specificity agreement, as Cohen's κ:

| Sample | GPT vs Claude final codes | Within GPT | Within Claude |
|---|---|---|---|
| E12 | 0.66 | 0.72 | 0.72 |
| E13 | 0.81 | 0.86 | 0.72 |

## Reading
1. **Pooled across kinds, the generic-contract → SPEC tendency recurs, but it is unstable.** It is significant in E10 and E12 (GPT coders), not significant in E13, and reversed in E12 with Claude coders.
2. **It largely overlaps with divergence kind.** Accidental divergences are mostly against SPECIFIC contracts, and they are repaired in the code.
   - Within DELIBERATE divergences the specificity effect is small: pooled 0.93 vs 0.77, p = 0.052.
   - Specificity therefore adds little beyond kind.
3. **E7 points the same way.** In E7 the proposition-only coder did not reproduce H-E7-2 (κ 0.37 for specificity), so specificity depends on reading the contract.
4. **Paper consequence.** Report specificity as a secondary, partly kind-confounded signal. Do not present it as an independent predictor.
