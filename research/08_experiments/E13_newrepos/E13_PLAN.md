# E13 pre-registration: kind × direction on 20 previously unused repositories (T50), with GPT and Claude coders
Claude (supervisor-delegated), 2026-11-17. The plan, `score_e13.py`, its self-test and the T50 inputs are frozen in `e13_plan_freeze.sha256` **before T50 mining starts**. The packages are frozen in a round-2 freeze (`e13_packages_freeze.sha256`) after T50 and before any blind run.

## Motivation
E10 and E12 replicated the kind × direction association on new items, but every item came from the 34 repositories used since T45, and pool2 is now exhausted. E13 tests whether the association **generalises to repositories never used before**.
- The repositories were selected by mechanical metadata criteria, with no commit content read (`E7_mining/t50_repo_selection/SELECTION.md`).
- Items are capped per fix (2) and per repository (10), and reviewed round-robin.

## Items
- **Source:** the T50 mining task (`09_collab/tasks/T50.md`), using the frozen pool3 from 20 new repositories.
- **IDs and key:** `Qnn`; key `E7_mining/key/e13_key.csv`; clusters = `candidate_id` in `key/accepted_full_t50.csv`.
- **Exclusions:** BOTH items are excluded from all tests.

## Blind runs (after round-2 freeze)
| Role | ID | Model | Package |
|---|---|---|---|
| Kind coders | C13, C14 | Codex gpt-6.1-sol, high | `e13_blind` (`TASK_CODE.md` byte-identical to E7) |
| Kind coders | K5, K6 | Claude subagents (sonnet), fresh context | `e13_kb1` … `e13_kbN`: consecutive slices of `items.csv` in order, at most 21 items each. Prompt as in E12; only the ID, the batch and the ID letter differ |
| M1 labeller | L6 | Codex | `e13_m1` (`TASK_M1.md` of E10; only the item count changes) |
| M1F labeller | F4 | Codex | `e13_m1f` (`TASK_M1F.md` of E10; only the item count changes) |

**Kind rules:**
- **GPT final kind:** C13 and C14 agree → that code; otherwise UNCLEAR.
- **Claude final kind:** the same rule, applied to K5 and K6.
- **Kind rule R:** DELIBERATE → SPEC, ACCIDENTAL → IMPL, otherwise abstain.

**Cluster rule (all cluster tests):** each cluster takes its majority final kind and its majority truth. A cluster is dropped if either majority is tied or if the cluster has no DELIBERATE or ACCIDENTAL item.

## Hypotheses
**H-E13-1 (primary): kind × direction with GPT coders, on new repositories.**
- Test: one-sided Fisher, P(SPEC | DELIBERATE) > P(SPEC | ACCIDENTAL), at item level and at cluster level.
- **PASS:** both tests have p < .05.
- **INSUFFICIENT:** fewer than 5 items in either arm at item level.

**H-E13-2 (primary, cross-family): kind × direction with Claude coders.**
- Test: the same item-level and cluster-level tests, using the Claude final kinds.
- PASS and INSUFFICIENT follow the H-E13-1 rules.

**H-E13-3: cross-family agreement.**
- Measure: Cohen's κ between the GPT final kind and the Claude final kind, over items where both are DELIBERATE or ACCIDENTAL.
- **PASS:** κ ≥ 0.6.
- **INSUFFICIENT:** fewer than 15 such items.

**H-E13-4 (secondary): kind rule (GPT kinds) vs forced-choice LLM.**
- Data: the items where R decides.
- Test: exact two-sided McNemar on R correct vs F4 correct.
- **SIGNIFICANT:** p < .05. **NS:** otherwise. **INSUFFICIENT:** fewer than 5 discordant items.
- No directional prediction is made.

## Descriptives (pre-registered, no verdict)
- Coder κ for C13–C14 and for K5–K6; final kind counts.
- Macro-F1 (`E4_triage/score_e4.py::two_direction`), with accuracy and coverage, for:
  - R (GPT kinds), R (Claude kinds);
  - M1 (L6), M1F (F4);
  - FB: L6, then R (GPT kinds) when L6 abstains.
- Rule precision with Wilson 95% CIs (GPT kinds): ACCIDENTAL → IMPL and DELIBERATE → SPEC.
- Per-repository items and clusters.
- Leave-one-repository-out: the H-E13-1 item-level p with each repository removed. Report the largest p.

## Pooled analysis across E10, E12 and E13 (pre-registered, descriptive)
- The three item sets are mutually disjoint, and disjoint from all earlier samples.
- Report:
  - GPT-kind × direction, pooled at item and cluster level;
  - rule precision with Wilson 95% CIs;
  - macro-F1 for R, M1 and M1F (L3 + L5 + L6; F1 + F3 + F4).

## Stop rules
- Each blind role runs once. Usage-limit interruptions are resumed in the same session.
- If T50 yields fewer than 20 items:
  - E13 still runs on the items available;
  - every test whose minimum is not met is INSUFFICIENT;
  - no further look is taken.
- The scorer is frozen before mining. Any later change is limited to mechanical fixes that change no logic, and is disclosed in `E13_DEVIATIONS.md` before scores are reported.
