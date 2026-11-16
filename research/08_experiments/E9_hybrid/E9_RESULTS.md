# E9: Hybrid triage results

Pre-registration: `E9_PLAN.md`, frozen in `1fe844e` before any E9 computation.

## Part A: retrospective on the 18 E6 items (exploratory, not confirmatory)
The kind codes come from the E7 exploratory C1/C2 codes. Agreement between the two coders gives the code. Disagreement gives UNCLEAR, and there is no adjudication. Counts: DELIBERATE 10, ACCIDENTAL 7, UNCLEAR 1.

| Method | macro-F1 | Decided-acc | Coverage |
|---|---|---|---|
| R rule | 0.856 | 0.88 | 0.94 |
| Y1 M1 = Y1 HYB | 0.857 | 0.88 | 0.94 |
| Y2 M1 = Y2 HYB | 0.879 | 0.94 | 0.89 |

- **Discordant items: 0** for both labellers. H-E9-1 is therefore INSUFFICIENT on these data.
- **ACCIDENTAL items:** M1 was already correct on all of them (7/7 for both Y1 and Y2).
- **DELIBERATE items:** all of M1's residual errors are here (7/10 correct for each labeller).
- **Reading:** on E6, the kind rule *explains* M1's success but does not *add* to it. The remaining errors sit where the rule is weakest, on DELIBERATE divergences, of which about 1 in 5 has an IMPL repair.

## Part B: confirmatory (one look, final)

### Runs
- **Sessions:** C7, C8, L1 and L2 were fresh Codex sessions (gpt-6.1-sol, high effort).
- **Usage limit:** all four hit the usage limit about 2 minutes after launch, before writing any output. Each was resumed in its own session after the reset, with no change to the task or the package. All four then exited 0.
- **Output checks:**
  - every row is present and in `items.csv` order;
  - every value is a valid label;
  - every rationale is at most 40 words.
- **Boundary:** the commands in the logs touch only each run's own directory and `../../../09_collab/PROTOCOL.md`. All four reports state that there were no boundary incidents.
- **Freezes:**
  - `e9_plan_freeze.sha256` was re-verified before scoring: 12 files plus the item-tree hash, all OK.
  - The `e8b_blind` W tree is byte-identical to the frozen E8b W-tree (`1a2510ee…`).
  - The outputs were hashed into `e9_outputs_freeze.sha256` before the scorer ran.
- **Scorer:** `score_e9.py` was unchanged, and its self-test passed. Results are in `e9_scores_B.csv`.
- **Kind coding of T47 (C7/C8):**
  - divergence_kind agreement 41/41 (κ = 1.0); contract_specificity agreement 38/41.
  - ⚠️ Perfect agreement within one model.
- **Items:** 85 SPEC/IMPL items (SPEC 49, IMPL 36). The BOTH item X17 is excluded. Kinds: DELIBERATE 61, ACCIDENTAL 24, UNCLEAR 0.

### H-E9-1 (primary): INSUFFICIENT
| Labeller | Discordant | Wins | Losses |
|---|---|---|---|
| L1 | 0 | 0 | 0 |
| L2 | 1 | 1 | 0 |
| **Pooled** | **1** | **1** | **0** (sign p = 0.50) |

**Verdict: INSUFFICIENT** (fewer than 5 discordant items).
- As in Part A, **M1 already labels ACCIDENTAL divergences correctly:** L1 got 24/24 and L2 got 23/24.
- The ACCIDENTAL → IMPL override therefore has almost nothing to change.
- Per the pre-registered interpretation, the kind rule **explains** the LLM's success but does **not improve** on it.

### Secondary (pre-registered)
| Method | macro-F1 | Decided-acc | Coverage |
|---|---|---|---|
| R rule | 0.845 | 0.86 | 1.00 |
| L1 M1 | 0.910 | 0.99 | 0.85 |
| L1 HYB | 0.910 | 0.99 | 0.85 |
| L2 M1 | 0.896 | 0.97 | 0.85 |
| L2 HYB | 0.903 | 0.97 | 0.86 |

- **HYB override precision: 24/24.** Every ACCIDENTAL item has IMPL truth. This is a third sample in which ACCIDENTAL → IMPL holds without exception.
- **L1–L2 agreement:** 81/85.

### Descriptive (pre-registered): where M1's residual errors fall
| | L1 | L2 |
|---|---|---|
| M1 correct, ACCIDENTAL | 24/24 | 23/24 |
| M1 correct, DELIBERATE | 47/61 | 47/61 |
| DELIBERATE misses: UNDECIDABLE with SPEC truth | 12 | 12 |
| DELIBERATE misses: IMPL label with SPEC truth | 1 | 2 |
| DELIBERATE misses: UNDECIDABLE with IMPL truth | 1 | 0 |

**What the split shows:**
- **M1's residual errors are almost all on DELIBERATE divergences.** They are mostly *abstentions* on items that the developer fixed in the spec.
- **When M1 does decide, it is almost always right:** decided-accuracy is 0.97–0.99.
- **Split by package:**
  - X only: M1 macro-F1 0.942 / 0.931 vs R 0.820.
  - W only: M1 macro-F1 0.861 / 0.848 vs R 0.870, because M1's coverage there is 0.76–0.78.

### Kind → direction on new data (descriptive, not a pre-registered E9 hypothesis)
- **W items** (T47, miner propositions, C7/C8 codes): DELIBERATE → SPEC 23/28, ACCIDENTAL → SPEC 0/13 (one-sided Fisher p = 4.9e-7).
  - This is the H-E7-1 table on T47 under the E7 condition (miner text plus files), with new coders.
  - Read together with E8b, it is consistent with the earlier results.
- **All of Part B:** 49/61 vs 0/24.

### Post-hoc (X, not pre-registered): R as a fallback when M1 abstains
**Prediction rule:** use M1 when it decides SPEC or IMPL; otherwise use R.

| | macro-F1 | Coverage |
|---|---|---|
| L1 | 0.976 | 1.00 |
| L2 | 0.976 | 1.00 |
| M1 alone | 0.90–0.91 | — |

- On M1's 13 abstentions, R is correct 12/13 for L1 and 13/13 for L2.
- ⚠️ This rule was formed **after seeing the Part B data**, so it is exploratory. It needs a new, pre-registered test on new items before any claim is made.
- **The plausible mechanism:** M1 abstains when the contract and a deliberate implementation choice disagree and nothing says which is intended. R resolves that case towards the spec, which was right about 4 times in 5 across E7, E8b and E9.

### Threats
- **Same model throughout.** Coders and labellers are the same model family, so their errors may be correlated. C7/C8 agreed perfectly.
- **Shared input text.** The kind coders and the M1 labellers both read the miner's proposition.
- **Item overlap.** The X items' kinds (C1/C2) were already analysed in E7. This is new M1 labelling, not new kind data. The W items' kinds are new.
- **Dependence.** Items cluster by repository and fix.

## Conclusion (Claude, supervisor-delegated)
1. **H-E9-1 is INSUFFICIENT, on two datasets.** The ACCIDENTAL → IMPL override is correct every time it fires (24/24), but a zero-shot LLM already makes the same call.
2. **The LLM's remaining errors are concentrated on DELIBERATE divergences.** They are mostly abstentions on spec-repaired items. This is exactly where R predicts "SPEC".
3. **Next step (proposed): E10.**
   - Pre-register the "M1, falling back to R when M1 abstains" pipeline.
   - Test it on fresh items not used in E6 through E9, which needs a new mining round.
   - Until then, the fallback result is exploratory only.
