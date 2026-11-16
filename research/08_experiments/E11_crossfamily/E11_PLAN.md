# E11 pre-registration: cross-family replication of divergence-kind coding (Claude coders)
Claude (supervisor-delegated), 2026-11-16. Frozen in `e11_plan_freeze.sha256` before the package is built and before any coder runs.

## Motivation
- Every kind coder so far (C1–C10) was the same GPT model, so κ between coders shows within-family consistency only.
- E11 re-codes all confirmatory items with coders from another model family, blind to the hypothesis.

## Items
All 126 confirmatory "new" items, coded from the miner's proposition text, which is the same packages the GPT coders saw:
- X new: 45 items (`e7_key.csv`, `set=new`); the package is `e7_blind`;
- W: 41 items (`e8b_key.csv`); the package is `e8b_blind`;
- V: 40 items (`e10_key.csv`); the package is `e10_blind`.

The E6 exploratory X items are excluded. BOTH items are excluded from all tests.

Clusters come from `candidate_id` in `accepted_full.csv`, `accepted_full_t47.csv` and `accepted_full_t48.csv`.

## Package
- **Location:** `E2_labelling/e11_b1` … `e11_b6`, six batches of 21 items.
- **Contents:**
  - item directories copied byte-for-byte from the source packages;
  - `items.csv` rows copied unchanged;
  - `TASK_CODE.md` byte-identical to `e7_blind/TASK_CODE.md`.
- **Assignment:**
  - Items are shuffled across X, W and V with `random.Random(20261117)`, then cut into consecutive batches.
  - No GPT code, label, report or key file is copied.

## Coders
- **K1 and K2:** independent Claude subagents (model: sonnet), each started with a fresh context.
- Each coder codes each batch in its own fresh subagent, so there are 12 subagent runs in all.
- **Prompt:**
  - the coder ID and the batch directory;
  - the instruction to read `TASK_CODE.md` first, follow it exactly, and read nothing outside the batch directory except `../../../09_collab/PROTOCOL.md`;
  - nothing about hypotheses, directions or earlier results.
- **Output:** `codes_K1.csv` and `codes_K2.csv` in each batch directory, in the TASK_CODE format.
- **Claude final kind:** K1 and K2 agree → that code; otherwise UNCLEAR.
- **GPT final kind (existing, frozen):** the same rule over:
  - C1 and C2 for X;
  - C7 and C8 for W;
  - C9 and C10 for V.

## Hypotheses
**H-E11-1 (primary): kind × direction with Claude coders.**
- Test: one-sided Fisher, P(SPEC | DELIBERATE) > P(SPEC | ACCIDENTAL), over all 126 items.
- Required at **item level** and at **cluster level**.
- **Cluster level:** each cluster takes its majority Claude final kind among DELIBERATE and ACCIDENTAL items, and its majority truth. A cluster is dropped if either majority is tied.
- **PASS:** both tests have p < .05.
- **INSUFFICIENT:** fewer than 5 items in either arm at item level.

**H-E11-2 (primary): cross-family agreement.**
- Measure: Cohen's κ between the GPT final kind and the Claude final kind, over items where both are DELIBERATE or ACCIDENTAL.
- **PASS:** κ ≥ 0.6.
- **INSUFFICIENT:** fewer than 15 such items.

## Descriptives (no verdict)
- κ between K1 and K2 on `divergence_kind`, over all items.
- The 3 × 3 table of GPT final kind vs Claude final kind.
- The kind × direction table per set (X, W, V), with Claude kinds.
- Accuracy and coverage of kind rule R using Claude kinds, per set.

## Stop rules
- Each coder-batch runs once.
- A run that fails or stops early is resumed once with the same prompt plus "continue". If it is still incomplete, its missing items count as UNCLEAR for that coder.
- One look at the data, with the frozen scorer `score_e11.py` (self-test `test_score_e11.py`).
