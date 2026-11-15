# E7 — Repair-direction study: results

Pre-registration: `E7_PLAN.md` (frozen, sha `bacab54c…`), amendments A1–A2 (before coding) and A3 (post-hoc, after the primary result). Package, scorer and plan hashes are in `e7_package_freeze.sha256`; the freeze was re-verified OK before scoring. Claude's blind adjudication (`adjudication.csv`, 4 rows) was committed in `54e9ca4` before the key was opened.

## Data
- **Corpus:** 70 items in total.
  - **45 new real contract-alignment fixes:** 16 from T45 and 29 from T46, across 15 repos. By developer fix direction: SPEC 26, IMPL 18, BOTH 1.
  - **25 exploratory items:** the E6 items.
- **Coders:** two independent blind Codex coders, C1 and C2 (gpt-6.1-sol, high effort). Each saw only parent-state excerpts and the neutral proposition.
- **What was hidden from the coders:** the hypothesis, the fix direction and the version history.

## Reliability
| Field | Set | Agreement | κ |
|---|---|---|---|
| divergence_kind | new | 44/45 | 0.942 |
| divergence_kind | exploratory | 24/25 | 0.921 |
| contract_specificity | all 70 | 68/70 | — |

There were 4 disagreements in total, adjudicated blind:
- X17 → ACCIDENTAL;
- X28 → DELIBERATE;
- X27 → SPECIFIC;
- X66 → SPECIFIC.

⚠️ Both coders are the same model. A high κ shows that the instrument is consistent within that model, not that it is reliable across humans.

## H-E7-1 (primary, confirmatory): P(SPEC | DELIBERATE) > P(SPEC | ACCIDENTAL)
| Analysis | DELIBERATE: SPEC | ACCIDENTAL: SPEC | OR [95% CI] (Haldane–Woolf) | Fisher one-sided p |
|---|---|---|---|---|
| **Primary (new, SPEC/IMPL)** | **26/33 = 0.79** [0.62, 0.89] | **0/11 = 0.00** [0.00, 0.26] | 81.3 [4.3, 1545] | **< 0.0001 → PASS** |
| (a) mining confidence = 3 | 12/16 = 0.75 | 0/5 | 30.6 [1.4, 671] | 0.0062 |
| (b) no cross-item flag | 19/24 = 0.79 | 0/10 | 74.5 [3.7, 1482] | < 0.0001 |
| (c) C1 = C2 agreed only | 26/33 | 0/11 | 81.3 | < 0.0001 |
| Exploratory (25 E6 items) | 11/15 = 0.73 | 0/10 | 53.7 | 0.0003 |

Further checks:
- **Popularity split (descriptive):** for repos with < 500 stars, 12/16 vs 0/6 (p = 0.003). For repos with ≥ 500 stars, 14/17 vs 0/5 (p = 0.002).
- **Robustness (post-hoc, descriptive):**
  - Leaving out any single repo: the maximum p is 6.7e-5.
  - T45 alone: 8/11 vs 0/4 (p = 0.026). T46 alone: 18/22 vs 0/7 (p = 0.0002).
  - No repo has an ACCIDENTAL item that was repaired in the SPEC direction.
- **Adjudication impact:** the two divergence_kind adjudications fall on the BOTH item (X17, excluded from the primary) and an exploratory item (X28). They therefore do not affect the primary result. X28 was adjudicated against the hypothesis (DELIBERATE, IMPL truth).

## H-E7-2 (secondary): P(SPEC | GENERIC) > P(SPEC | SPECIFIC)
- **GENERIC:** 15/18 = 0.83 [0.61, 0.94].
- **SPECIFIC:** 11/26 = 0.42 [0.26, 0.61].
- **Test:** OR 5.97 [1.49, 23.9], Fisher p = 0.007 → **PASS**.
- **If both specificity adjudications are flipped to GENERIC:** 16/20 vs 10/24. The result still holds.

## Triage rule DELIBERATE → SPEC, ACCIDENTAL → IMPL (descriptive, new set)
| Measure | Value |
|---|---|
| macro-F1 | 0.820 |
| SPEC precision / recall | 0.79 / 1.00 |
| IMPL precision / recall | 1.00 / 0.61 |
| Coverage | 1.00 |
| Majority baseline (all SPEC) macro-F1 | 0.371 |

ACCIDENTAL is a perfect IMPL signal. DELIBERATE is a weaker SPEC signal: 7 of 33 DELIBERATE divergences were nonetheless repaired in the code.

## Proposition-only control (A3, post-hoc)
A fresh Codex coder P1 coded the same 70 items from `items.csv` alone, with no source files. It used the identical definitions. The log confirms it never touched `e7_blind`. Scorer: `score_e7_p1.py`. The analysis and its interpretation rule were committed in `7699f24` before P1 ran.

| Field (new set, SPEC/IMPL) | P1 vs truth | κ, P1 vs final C1/C2 code |
|---|---|---|
| divergence_kind | DELIBERATE 26/33 vs ACCIDENTAL 0/11, p < 0.0001 (**identical to the primary**) | **1.000** (44/44) |
| contract_specificity | GENERIC 5/6 vs SPECIFIC 21/38, p = 0.20 (not reproduced) | 0.371 (32/44) |

**Interpretation (A3 rule):**
- **divergence_kind:** the A3 condition is met. **The H-E7-1 association cannot be attributed to code reading.** For these items, the deliberate/accidental distinction is fully recoverable from the one-line proposition.
- **Two explanations remain, and this design cannot separate them.**
  - **Inherent:** whether a divergence is deliberate or accidental is a property of the described behaviour Y. For example, "throws an unhandled exception" versus "returns an explicit 204". Reading code adds nothing once Y is stated accurately.
  - **Authoring leakage:** the miner, who knew the direction, phrased Y in ways that encode it.
- **Consequence:** H-E7-1 holds as a statistical association in this corpus. **The practical claim that "code-structure triage predicts the repair direction" requires propositions written by a direction-blind author**, for example from a conformance-tool failure or a parent-only reading, before it can be made.
- **contract_specificity:** the code-reading coders and P1 disagree (κ 0.37), and P1 does not reproduce H-E7-2. Contract reading therefore did add information for H-E7-2. That makes H-E7-2 the less leakage-exposed of the two results, despite being secondary.

## Threats
- **Proposition authorship.**
  - The propositions were written by a miner who knew each fix direction, although not the hypothesis. A3 tests this.
  - A crude lexical check of Y (unhandled, null, missing, default, exception…) does not track the fix direction: 5/26 SPEC vs 4/18 IMPL items contain a cue.
- **T46 retrieval.** The pool2 filter was corrected after the miner had previewed some candidates, so the freeze is not fully outcome-naive (T46_report). The miner was hypothesis-blind.
- **Hypothesis origin.** The hypothesis was derived from post-hoc coding of the E6 items. The exploratory row is therefore not independent evidence; the new set is.
- **Independence of items.**
  - Some items share a fix commit or a parent file.
  - 18 of the 70 items are cross-flagged, 10 of them in the primary set. Excluding them leaves the result unchanged (sensitivity b).
  - 15 repos contribute; cwms, nessie, fineract and basyx contribute 5–6 items each.
- **Same-model coders.** C1 and C2 are the same LLM, so their errors may be correlated. No human coder took part.
- **Corpus scope.**
  - The selection is restricted to correction-cue commits in OSS Java/Kotlin/Go REST projects.
  - "ACCIDENTAL → never SPEC" rests on 11 items (upper CI 0.26).
  - BOTH and deferred candidates are excluded.
- **Wide odds-ratio CIs.** The zero cell makes the interval very wide. The direction of the effect is clear; its size is not.

## Next step (decided by Claude, supervisor-delegated): E8 — direction-blind propositions
1. A fresh, direction-blind writer receives only the operation and the parent-state package. It writes its own neutral contract-says/implementation-does proposition.
2. If it finds no mismatch, it writes NONE.
3. Fresh coders then code divergence_kind from that text plus the files.
4. H-E7-1 is re-tested on the re-authored propositions. Pre-register this before running.
