# E8: Direction-blind propositions (results)

**Pre-registration.** The plan is `E8_PLAN.md`, frozen in commit `7bf6308`. The round-2 inputs were frozen in `d5ecbcf` before J1, C3, C4 and P2 ran. Both freezes were re-verified OK before scoring, and the scorer was not changed afterwards.

## Runs
All runs used Codex gpt-6.1-sol at high effort. Each run was a fresh session, worked only in its own directory, and had no access to the hypothesis, the E7 key, the E7 propositions or the E7 codes, except that J1 saw the E7 propositions, as the plan specifies. The logs show no access outside each run's directory.

| Run | Task | Outcome |
|---|---|---|
| W1 | Wrote propositions from the operation and files only | 67 propositions plus 3 NONE; no banned words |
| J1 | Matched each W1 proposition against the E7 proposition | New set: SAME 35, PARTIAL 2, DIFFERENT 7, NONE 1 (excludes the BOTH item) |
| C3, C4 | Coded the W1 propositions with the files | Agreement 67/67 on divergence_kind (κ = 1.000) |
| P2 | Coded the W1 propositions without the files | κ = 0.956 against the final C3/C4 code |

C3 and C4 hit the Codex usage limit only after they had written and self-validated their outputs (each has 67 rows in item order, with valid codes). Only their final chat message is missing.

⚠️ C3 and C4 are the same model, and their agreement was perfect, so their errors are probably correlated.

## H-E8-1 (confirmatory)
The primary set is the new set, restricted to SPEC/IMPL items that J1 coded SAME.

| Analysis | DELIBERATE: SPEC | ACCIDENTAL: SPEC | OR [95% CI] | Fisher one-sided p | Verdict |
|---|---|---|---|---|---|
| **Primary (SAME)** | 22/29 = 0.76 [0.58, 0.88] | **0/6** [0.00, 0.39] | 39.0 [2.0, 778] | 0.0011 | **INSUFFICIENT** (ACCIDENTAL arm 6 < 8) |
| (a) SAME + PARTIAL | 24/31 | 0/6 | 42.5 | 0.0007 | — |
| (b) all non-NONE | 25/37 = 0.68 | 1/7 = 0.14 | 8.8 [1.3, 59] | 0.013 | — |
| (c) exploratory, SAME | 6/8 | 0/6 | 33.8 | 0.009 | — |

Triage rule on the primary set: macro-F1 0.747 (n = 35).

**Verdict per the pre-registered rule: INSUFFICIENT.** The point estimates go in the hypothesised direction and p = 0.001. But the plan required at least 8 items in each arm before a confirmatory claim, so no confirmatory claim is made.

## Descriptive: why the ACCIDENTAL arm shrank
This analysis is post-hoc and descriptive. It cross-tabulates the E7 code, the J1 match and the E8 code for the 44 new SPEC/IMPL items.

| E7 code | J1 match | E8 code | Truth | n |
|---|---|---|---|---|
| ACCIDENTAL | SAME | ACCIDENTAL | IMPL | 6 |
| ACCIDENTAL | DIFFERENT | DELIBERATE | IMPL | 5 |
| DELIBERATE | SAME | DELIBERATE | SPEC | 22 |
| DELIBERATE | SAME | DELIBERATE | IMPL | 7 |
| DELIBERATE | PARTIAL | DELIBERATE | SPEC | 2 |
| DELIBERATE | DIFFERENT | DELIBERATE / ACCIDENTAL | SPEC | 1 / 1 |

**1. Re-authoring did not change any code on the matched items.** On all 35 SAME items, the E8 code equals the E7 code. The direction-blind propositions therefore yield the same deliberate/accidental code as the miner's propositions. This counts against the "authoring leakage" explanation from E7 amendment A3, at least for discrepancies a blind reader finds. It is consistent with the "inherent property of Y" explanation. P2's κ of 0.956 with the code supports the same reading, now on direction-blind text.

**2. Blind reading misses accidental divergences more often.**
- The blind reader missed 5 of 11 accidental divergences: it reported a different, deliberate-type discrepancy for the same operation instead.
- For deliberate divergences, the miss count depends on how PARTIAL is treated:
  - counting only DIFFERENT as a miss: 2 of 33 missed;
  - counting DIFFERENT and PARTIAL as misses: 4 of 33 missed.
- Exact one-sided Fisher test, post-hoc: p = 0.007 when only DIFFERENT counts as a miss, and p = 0.030 when PARTIAL counts too.

**Interpretation.** The ACCIDENTAL arm shrank because the blind reader missed these divergences, not because their codes flipped. Accidental divergences (unhandled exceptions, missing branches) are less salient to a static reader than explicit code choices. In practice, a pipeline that finds discrepancies through static reading will under-sample exactly the class whose repair direction is most predictable, which is IMPL. A runtime conformance tool (fuzzer failure) is the natural source for those discrepancies.

## Status of H12
- **E7 result:** the association between divergence kind and repair direction holds statistically (E7 primary PASS).
- **What E8 adds:**
  - Its confirmatory test is INSUFFICIENT.
  - On the matched items, it shows that the deliberate/accidental code does not depend on who wrote the proposition.
  - Read together with E7, this makes the authoring-leakage explanation unlikely for the found items. That reading is descriptive, not confirmatory.

## Threats
- **One writer.** Which discrepancy counts as "most salient" is a single model's choice.
- **Matching.** J1 is a single LLM judgement.
- **Same model throughout.** All roles were played by the same model family.
- **Files chosen around the miner's mismatch.** The package files were selected around the miner's mismatch, which helps the writer find it.
- **Small arms and a zero cell.** The arms are small, and the zero cell makes the odds-ratio confidence interval very wide.
- **Post-hoc analyses.** The cross-tab and the miss-rate test above were not pre-registered.

## Next step (Claude, supervisor-delegated)
E8b would enlarge the ACCIDENTAL arm, with the analysis fixed before any new data is seen. See `E8_PLAN_AMENDMENTS.md` (B1).
