# E12 pre-registration: kind × direction and triage on T49 items, with GPT and Claude coders
Claude (supervisor-delegated), 2026-11-16. Frozen in `e12_plan_freeze.sha256` **before T49 mining starts**.

The scorer `score_e12.py` and its self-test will be frozen in a round-2 freeze (`e12_packages_freeze.sha256`). That happens after T49 and before any blind run, together with the packages. The scorer implements exactly the rules below.

## Motivation
E10 showed two things:
1. **The kind × direction association replicates,** in H-E10-3.
2. **LLM triage accuracy swings strongly between clustered samples.**
   - Its cause: one repository gave 10 items from 2 fixes.
   - So T49 caps the number of items per fix.

Every coder so far has been from one model family, so E12 adds two Claude coders as well.

## Items
- **Source:** the T49 mining task (`09_collab/tasks/T49.md`).
- **Pool:** the frozen pool2, continued.
- **Caps:**
  - at most **2 items per mined candidate (fix)**, chosen by a direction-neutral rule;
  - at most 10 items per repository, combined across T45–T49.
- **IDs and key:** `Unn`; key `E7_mining/key/e12_key.csv`; clusters = `candidate_id` in `key/accepted_full_t49.csv`.
- **Exclusions:** BOTH items are excluded from all tests.

## Blind runs (after round-2 freeze)
| Role | ID | Model | Task |
|---|---|---|---|
| Kind coders | C11, C12 | Codex gpt-6.1-sol, high | `TASK_CODE.md`, byte-identical to E7 |
| Kind coders | K3, K4 | Claude subagents (sonnet), fresh context | Same TASK_CODE; the YOUR_ID line is the only difference |
| M1 labeller | L5 | Codex | `TASK_M1.md` (E10; only the item count changes) |
| M1F labeller | F3 | Codex | `TASK_M1F.md` (E10; only the item count changes) |

**Kind rules:**
- **GPT final kind:** C11 and C12 agree → that code; otherwise UNCLEAR.
- **Claude final kind:** the same rule, applied to K3 and K4.
- **Kind rule R:** DELIBERATE → SPEC, ACCIDENTAL → IMPL, otherwise abstain.

## Hypotheses
**H-E12-1 (primary): kind × direction with GPT coders, on new items with fix caps.**
- Test: one-sided Fisher, P(SPEC | DELIBERATE) > P(SPEC | ACCIDENTAL), at **item level and at cluster level**.
- At cluster level, each cluster takes its majority final kind and its majority truth. A cluster is dropped if either majority is tied or if the cluster has no DELIBERATE or ACCIDENTAL item.
- **PASS:** both tests have p < .05.
- **INSUFFICIENT:** fewer than 5 items in either arm at item level.

**H-E12-2 (primary, cross-family): kind × direction with Claude coders.**
- Test: the same item-level Fisher test, using the Claude final kinds on the U items.
- PASS if p < .05; INSUFFICIENT under the same rule as H-E12-1.

**H-E12-3: cross-family agreement.**
- Measure: Cohen's κ between the GPT final kind and the Claude final kind, over items where both are DELIBERATE or ACCIDENTAL.
- **PASS:** κ ≥ 0.6.
- **INSUFFICIENT:** fewer than 15 such items.

**H-E12-4 (secondary): kind rule vs forced-choice LLM.**
- Data: the items where R decides.
- Compare R correct vs F3 correct with an exact two-sided McNemar test.
- Report the direction. No directional prediction is made.
- **INSUFFICIENT:** fewer than 5 discordant items.

## Descriptives (pre-registered, no verdict)
- Macro-F1 (`E4_triage/score_e4.py::two_direction`), with decided accuracy and coverage, for:
  - R (GPT kinds), and R (Claude kinds);
  - M1 (L5), M1F (F3);
  - FB: L5, then R (GPT kinds) when L5 abstains.
- Coder κ for C11–C12 and for K3–K4.
- Per-repository counts of items and clusters.

## Pooled analysis across E10 and E12 (pre-registered, descriptive)
- Both item sets are disjoint from all earlier samples.
- Report: GPT-kind × direction, pooled at item level and at cluster level.
- Report: macro-F1 for R, M1 and M1F, pooled over V and U items. Use L3 and F1 from E10.

## Stop rules
- Each blind role runs once. Usage-limit interruptions are resumed in the same session.
- If T49 yields fewer than 20 items:
  - E12 runs on the items available;
  - every test whose minimum is not met is INSUFFICIENT;
  - no further look is taken.
