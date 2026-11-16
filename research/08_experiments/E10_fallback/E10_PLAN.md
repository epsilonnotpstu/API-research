# E10: LLM triage with a kind-rule fallback (pre-registration)

**Status:** frozen before mining (T48) and before any E10 computation or labelling; hashes are in `e10_plan_freeze.sha256`. Decided by Claude (supervisor-delegated), 2026-11-16.

**Not to be read by:** the miner (T48), the kind coders, or the labellers.

## Why
In E9 Part B (`../E9_hybrid/E9_RESULTS.md`) the zero-shot LLM (M1) was almost always right when it decided. Its residual misses were abstentions, mostly on DELIBERATE divergences that the developer repaired in the spec.

A rule formed **post hoc** was "use M1; when M1 abstains, use the kind rule R". It reached macro-F1 0.976, against 0.90–0.91 for M1 alone. E10 tests that rule on fresh items.

E10 also tests two alternative explanations:
- a trivial fallback ("abstain → SPEC") would do just as well;
- simply forcing the LLM to choose would do just as well.

## Items
- **New items (V):** mined by T48, continuing the frozen pool2 review with the unchanged acceptance gate. The miner is hypothesis-blind.
- **Truth:** the developer's repair direction from `E7_mining/key/e10_key.csv`. Primary analyses use SPEC/IMPL only; BOTH items are excluded but counted.
- **Packages** (byte-identical V item trees):
  - `E2_labelling/e10_blind/` for the kind coders;
  - `E2_labelling/e10_m1/` for the M1 labellers;
  - `E2_labelling/e10_m1f/` for the forced-choice labellers.

## Roles (fresh Codex sessions, gpt-6.1-sol, high effort)
- **Kind coders C9 and C10.**
  - They receive `e7_blind/TASK_CODE.md` byte-identical, on `e10_blind/`.
  - **Final kind:** C9's code if C9 = C10; otherwise UNCLEAR. There is no adjudication.
- **M1 labellers L3 and L4.**
  - Their task is `E2_labelling/e9_m1/TASK_M1.md` with only the item count in the title changed.
- **Forced-choice labellers F1 and F2** (M1F).
  - Their task text is the same as M1, except that L1 ∈ {SPEC, IMPL}, with the instruction: "choose the artifact more likely to deviate from the intended behaviour; you may not abstain".
  - Labels other than SPEC/IMPL count as misses.
- **Interruptions:** a run stopped by a usage limit is resumed in the same session. Claude cannot take over these blind roles, because Claude has opened the E7, E8b and E9 keys.

## Methods (per item)
- **M1:** the label of L3, or of L4.
- **R:** DELIBERATE → SPEC, ACCIDENTAL → IMPL, UNCLEAR → abstain.
- **FB:** the M1 label if M1 ∈ {SPEC, IMPL}; otherwise R.
- **FBS** (trivial fallback): the M1 label if M1 ∈ {SPEC, IMPL}; otherwise SPEC.
- **M1F:** the label of F1, or of F2.

## Hypotheses and decision rules

### H-E10-1 (primary): R is informative on M1's abstentions
- **Unit:** an *abstention pair* is an (item, M1 labeller) pair where M1 ∉ {SPEC, IMPL} and R decides.
- **Test:** pooled over L3 and L4, the share of abstention pairs on which R equals the truth, tested with an exact one-sided binomial test against 0.5.
- **PASS** if all three hold:
  1. p < 0.05;
  2. R's accuracy on abstention pairs is ≥ 0.5 for each labeller separately;
  3. there are ≥ 8 pooled abstention pairs.
- **INSUFFICIENT** if there are < 8 abstention pairs.
- **FAIL** otherwise.
- **Sensitivity (reported):** the unit is the unique item abstained by at least one labeller. If both labellers abstain on an item, it counts once.

### H-E10-2 (key secondary): FB vs forced-choice LLM
- **Pairing:** L3 is paired with F1, and L4 with F2.
- **Discordant item:** FB ≠ M1F.
- **Win:** FB is correct and M1F is not. **Loss:** the reverse.
- **Test:** exact one-sided sign test on pooled wins vs losses.
- **Outcomes:**
  - **FB better:** p < 0.05, and each pair has wins ≥ losses.
  - **INSUFFICIENT:** fewer than 5 pooled discordant items.
  - **Not better:** otherwise. In that case also report the reverse one-sided test (M1F better).

### Other secondary analyses
- **Macro-F1** over SPEC/IMPL, where other labels and abstentions are misses. Computed for M1, FB, FBS and M1F per labeller, and for R. The scorer is `E4_triage/score_e4.py::two_direction`.
- **FB vs FBS:** the number of abstention pairs where R ≠ SPEC, and their correctness.
- **H-E10-3 (replication of H-E7-1 on the V items):**
  - **Test:** P(SPEC | DELIBERATE) > P(SPEC | ACCIDENTAL), one-sided Fisher exact test.
  - **INSUFFICIENT** if either arm has fewer than 8 items.

### Descriptive
- Kind × truth table.
- M1 correctness by kind.
- κ between C9 and C10.
- Agreement between L3 and L4, and between F1 and F2.
- Abstention rate per labeller.

## Interpretation
| Outcome | Reading |
|---|---|
| H-E10-1 PASS and H-E10-2 FB better | Recommend the M1 → R fallback pipeline. The kind rule adds information beyond the LLM's own forced guess. |
| H-E10-1 PASS, but H-E10-2 not better | R resolves abstentions, but so does forcing the LLM to choose. The kind rule is a transparent, auditable stand-in, not an accuracy gain. |
| H-E10-1 FAIL or INSUFFICIENT | The E9 post-hoc result does not replicate. |

## Threats (known in advance)
- **Same model family** for the miner, the coders and the labellers.
- **Shared input text.** The kind coders and the labellers all read the miner's proposition.
- **Sample size.** The abstention rate was about 15% in E9. With about 40 items, that gives about 12 abstention pairs, so H-E10-1 may be INSUFFICIENT.
- **Two different outcome variables.** M1F changes the answer set, not just the decision rule.
- **Item dependence.** Items cluster by repo and fix, and pool2 is a continuation of an earlier, already-reviewed retrieval.
