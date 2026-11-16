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

---

# E8b: the pooled extension (amendment B1; one further look, final)

## Runs
- **New data:** T47 added 41 new items: SPEC 23, IMPL 18. They come from continuing the frozen pool2 review, which stayed hypothesis-blind. They form a separate W-package.
- **Pipeline:** the same as E8, run in fresh sessions with byte-identical task texts:
  - W2 wrote 37 propositions and 4 NONE.
  - J2 matched them: SAME 24, PARTIAL 5, DIFFERENT 8, NONE 4.
  - C5 and C6 coded them: κ = 0.895, with 1 disagreement (scored UNCLEAR).
  - P3 coded W2's propositions without files: κ vs the final code = 0.488.
  - P4 coded the miner's propositions without files.
- **Interruptions:**
  - W2 stopped on a "model at capacity" error after writing its outputs. I validated those outputs independently: row order, word limits, and the existence of every locator file.
  - All other runs exited 0.
- **Checks:**
  - No run accessed anything outside its own directory.
  - All freezes (`e8b_freeze`, `e8b_round1_freeze`, `e8b_round2_freeze`) were verified, including the W-tree hash.

## H-E8-1, pooled (confirmatory, final)
| Analysis | DELIBERATE: SPEC | ACCIDENTAL: SPEC | OR [95% CI] | Fisher one-sided p | Verdict |
|---|---|---|---|---|---|
| **PRIMARY, pooled E8 + T47, SAME** | **39/48 = 0.81** [0.68, 0.90] | **0/10** [0.00, 0.28] | 87.3 [4.7, 1626] | **1.8e-6** | **PASS** |
| Secondary: T47 alone, SAME | 17/19 = 0.89 | 0/4 | 63.0 | 0.0017 | — |
| Sensitivity: pooled SAME + PARTIAL | 43/54 | 0/11 | 87.0 | < 1e-4 | — |
| Sensitivity: pooled, all non-NONE | 47/68 = 0.69 | 1/12 = 0.08 | 16.9 [2.9, 100] | 0.0001 | — |

1 item is UNCLEAR and is excluded from the tables.

Triage rule on the pooled primary set (descriptive): macro-F1 0.79.

| Class | Precision | Recall |
|---|---|---|
| SPEC | 0.81 | 1.00 |
| IMPL | 1.00 | 0.53 |

**Verdict per B1: PASS.** The association survives propositions written by a reader who does not know the repair direction. As in E7, when an accidental divergence is described, it is repaired in the code.

## Pre-registered miss-rate test (T47): not replicated
- **Missed accidental divergences:** 5/11 counted as DIFFERENT or PARTIAL, using P4's code of the miner's propositions.
- **Missed deliberate divergences:** 8/26.
- **Fisher one-sided p:** 0.31.

The E8 post-hoc finding, that blind reading misses accidental divergences more often, is **not confirmed**.

⚠️ This pre-registered test excluded NONE. W2 wrote NONE for 4 items, and all 4 are accidental and IMPL according to P4. Counted post-hoc with NONE as a miss, the figures are 9/15 vs 8/26. That count is descriptive only.

## Descriptive (T47)
- **Re-authoring and the kind code.** On the SAME items, P4's code of the miner's proposition equals the final E8b code in 21/24. The 3 changes are:
  - 2 items that P4 coded ACCIDENTAL from the miner's text. Both have SPEC truth, and C5/C6 coded both DELIBERATE after reading the files.
  - 1 item that C5 and C6 left UNCLEAR.
- **The proposition text is not always the signal.** In T47, miner-text-only coding (P4) would have put 2 SPEC items into the ACCIDENTAL arm. Reading the code corrected both.
- **Proposition-only coding of W2's text agrees less here** (κ 0.488, against 0.956 in E8). So in T47 the files mattered to the code.

## Updated status of H12 (E7 + E8 + E8b)
- **The association holds under three conditions:**
  - miner-written propositions (E7);
  - direction-blind propositions, pooled (E8b, PASS);
  - blind coders reading code.
- **Divergence kind is a strong predictor of the repair direction:**
  - ACCIDENTAL implies an IMPL repair (0 SPEC of 10 matched accidental items in the pooled primary);
  - DELIBERATE leans SPEC (about 0.8).
- **The asymmetry matters in practice:**
  - The ACCIDENTAL → IMPL rule has precision 1.00 here.
  - The DELIBERATE → SPEC rule is wrong about 1 time in 5.
  - So the rule is safe for routing accidental divergences to code repair, but it cannot by itself decide the deliberate ones.

## Remaining threats
- **Same model throughout.** All roles were played by the same model family, with no human coder.
- **The extension was decided after E8.** It was disclosed and limited to one further look.
- **T47 previewed beyond its prefix.** Its patch preview looked at 41 candidates beyond the final review prefix (T47_report).
- **Correlated items.** Many items share a repo and some share a fix.
- **The miss-rate claim failed.**
- **Small zero cell.** The ACCIDENTAL arm has 10 items, so the 95% upper bound on its SPEC rate is 0.28.
