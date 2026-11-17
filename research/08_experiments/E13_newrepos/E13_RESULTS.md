# E13 results: kind × direction on 20 previously unused repositories
Claude (supervisor-delegated), 2026-11-17. The run was scored once with the frozen `score_e13.py` (`e13_plan_freeze.sha256`) on the frozen packages (`e13_packages_freeze.sha256`) and outputs (`e13_outputs_freeze.sha256`). The raw output is `e13_score_output.txt` and the per-row CSV is `e13_scores.csv`.
- **Deviations:** P1 only, the T50b mining continuation (`E13_DEVIATIONS.md`). No scorer changes.

## Sample
**Items.** 61 Q items (SPEC 34, IMPL 27, BOTH 0), from 42 fixes (clusters) in 15 repositories that no earlier experiment used.
- The repositories were selected mechanically, from metadata only.
- Mining used T50/T50b: frozen pool3, round-robin review, per-fix cap 2, per-repo cap 10, and a licence gate at the parent commit.
- 947 of the 12,832 pool3 candidates were reviewed. Mining stopped at the ≥ 60-item target.

**Blind runs.** One run each:
- GPT kind coders C13 and C14 (κ 1.00);
- Claude sonnet kind coders K5 and K6, in three fresh-context batches (κ 0.89);
- M1 labeller L6 and M1F labeller F4.

**Audits.** All passed.
- No reads outside the batch: every flag was a false positive, i.e. in-item paths named `tasks/` or `labels_*`, or a path elision written as `.../`.
- The package trees were unchanged after the runs.

## Hypotheses
| Hypothesis | Result | Verdict |
|---|---|---|
| H-E13-1, GPT kinds | items: SPEC 33/43 DELIBERATE vs 1/18 ACCIDENTAL, p = 2.2e-7; clusters: 22/29 vs 1/13, p = 4.7e-5 | **PASS** |
| H-E13-2, Claude kinds | items: 34/40 vs 0/18, p = 3.0e-10; clusters: 23/28 vs 0/12, p = 1.1e-6 | **PASS** |
| H-E13-3, cross-family κ | 55/58 both-decided items agree; κ = 0.88 | **PASS** |
| H-E13-4, R (GPT kinds) vs F4 | 61 R-decided items; R-only correct 0, F4-only correct 7; McNemar p = 0.016 | **SIGNIFICANT, favouring F4** |

## Descriptives
**Macro-F1 (accuracy, coverage):**

| Method | Macro-F1 | Accuracy | Coverage |
|---|---|---|---|
| R, GPT kinds | 0.81 | 0.82 | 1.00 |
| R, Claude kinds | 0.86 | 0.90 | 0.95 |
| M1 (L6) | 0.90 | 0.90 | 1.00 |
| M1F (F4) | 0.93 | 0.93 | 1.00 |
| FB | 0.90 | 0.90 | 1.00 (L6 never abstained) |

**Rule precision (GPT kinds), Wilson 95% CI:**
- ACCIDENTAL → IMPL: 17/18 = 0.94 [0.74, 0.99];
- DELIBERATE → SPEC: 33/43 = 0.77 [0.62, 0.87].

**Leave-one-repository-out.** The largest H-E13-1 item-level p is 8.7e-6, without keto. No single repository carries the effect.

**Per-repository counts.** Items and clusters for each repository are in the score output.

## Pooled E10 + E12 + E13 (descriptive; 137 disjoint items)
- **GPT kind × direction:**
  - items: 69/84 vs 6/50, p = 4.2e-16;
  - clusters: 40/51 vs 4/35, p = 4.0e-10.
- **Rule precision:**
  - ACCIDENTAL → IMPL: 44/50 = 0.88 [0.76, 0.94];
  - DELIBERATE → SPEC: 69/84 = 0.82 [0.73, 0.89].
- **Macro-F1:**

  | Method | Macro-F1 | Coverage |
  |---|---|---|
  | R | 0.83 | 0.98 |
  | M1 | 0.82 | 0.96 |
  | M1F | 0.88 | 1.00 |

## Interpretation
1. **The association generalises to new repositories.** The kind × direction association holds on 15 repositories never used before, and holds at cluster level too.
   - It holds for both model families.
   - It does not depend on any one repository.
   - This is the strongest replication so far: new repositories, a new pool, mechanical selection, a per-fix cap, and cross-family coders.
2. **Kind is not a better triage rule than a forced-choice LLM.** Here F4 beat R significantly. All 7 discordant items went to F4.
   - In E12 the two methods were equal. Pooled, M1F has the highest macro-F1.
   - The paper's position is unchanged and now firmer: kind is an *explanatory* variable for direction, and is not proposed as a triage method that beats LLM labellers.
3. **The weak point of the rule is DELIBERATE → SPEC.** Its precision (0.77) is lower than ACCIDENTAL → IMPL (0.94).
   - Some deliberate-looking divergences were fixed in the code.
   - ⚠️ An inference: some of these may be cases where the developers' intent changed. This was not tested.

## Threats
- The miner wrote the propositions, and all coders read them. This is the same as in E10–E12.
- 42 clusters in 15 repositories. Clusters vary in size; the cluster-level tests address this.
- Only 7.4% of pool3 was reviewed, so the yield says nothing about prevalence.
- The licence classes recorded by Codex for tyk and halo are wrong. The corrected classes are in `10_paper/LICENSE_REVIEW.md`. Inclusion is unaffected.
