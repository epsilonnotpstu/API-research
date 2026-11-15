# E8 — Direction-blind propositions: pre-registration

**Status:** frozen before any E8 Codex run. Hashes are in `e8_plan_freeze.sha256`. Decided by Claude (supervisor-delegated), 2026-11-16.

## Why
E7 found that P(SPEC | DELIBERATE) = 26/33 and P(SPEC | ACCIDENTAL) = 0/11. However, a proposition-only coder reproduced the divergence_kind codes exactly (κ = 1.0; amendment A3). The propositions were written by the T45/T46 miner, who knew every fix direction. E8 removes that author: the proposition is written by a writer who has never seen the fix, the miner's proposition or the hypothesis.

## Materials
- **The same 70 items, with the same IDs and the same parent-state files as `e7_blind`.**
  - **`E2_labelling/e8_write/`:** `items.csv` (item_id, repo, operation only) plus `Xnn/contract/` and `Xnn/impl/`.
- **Truth:** `E7_mining/key/e7_key.csv` (`truth_direction`, `set`). Only set=new items with SPEC or IMPL truth enter the confirmatory analysis.
- **Claude's status:** Claude has opened the E7 key, so Claude makes no item-level judgement in E8. All judgements come from fresh Codex sessions (gpt-6.1-sol, high effort, `-s workspace-write`, cwd = the package directory). None of these sessions has seen the hypothesis, the key, the E7 propositions or E7 codes, except where stated below.

## Steps

### 1. Writer W1 (`e8_write/TASK_WRITE.md`)
- **Input:** each item's operation and files.
- **Task:** describe the single most salient discrepancy between the contract and the implementation for that operation. Use the format `"<METHOD> <path>: contract says <X>; implementation does <Y>"`, with locators. If there is none, write `NONE`.
- **Wording rule:** neutral and factual. Banned words: deliberate(ly), accidental(ly), intentional(ly), oversight, forgot, bug, wrong, correct, incorrect, should, mistake.
- **Output:** `props_W1.csv` with columns `item_id, proposition, contract_locators, impl_locators, confidence`.

### 2. Match judge J1 (`e8_match/TASK_MATCH.md`)
- **Input:** for each item, the E7 proposition (A) and W1's proposition (B). Neither contains direction information.
- **Task:** judge whether B describes the same contract–implementation discrepancy as A, meaning the same operation, the same behaviour facet and the same mismatch.
- **Codes:** SAME, PARTIAL, DIFFERENT, or NONE (B = NONE).
- **Output:** `match_J1.csv` with columns `item_id, match, rationale`.

### 3. Coders C3 and C4 (`e8_code/TASK_CODE.md`)
- **Input:** `e8_code/items.csv` (item_id, repo, operation and **W1's proposition**) plus the same files.
- **Instrument:** the E7 instrument, verbatim (`e7_blind/TASK_CODE.md`).
- **Exclusions:** items where W1 wrote NONE are excluded from coding.

### 4. Proposition-only coder P2 (descriptive)
- P2 codes W1's propositions without the files, using the A3 task text.

## Final code
- **divergence_kind:**
  - C3 = C4 → that value;
  - C3 ≠ C4 → UNCLEAR (no adjudication).
- UNCLEAR is excluded from the 2×2 tables and reported separately.

## Hypothesis and analysis
**H-E8-1 (confirmatory):** among set=new, SPEC/IMPL-truth items with J1 = SAME, P(SPEC | DELIBERATE) > P(SPEC | ACCIDENTAL).
- **Test:** one-sided Fisher exact test, α = 0.05.
- **Also reported:** Wilson CIs and the Haldane–Woolf odds ratio.
- **Minimum size:** each arm must have ≥ 8 items. Otherwise the result is reported as descriptive only, labelled INSUFFICIENT.

**Sensitivity analyses:**
- (a) J1 ∈ {SAME, PARTIAL};
- (b) all non-NONE items, whatever the match;
- (c) the exploratory set, with the same filter as the primary.

**Descriptive analyses:**
- κ between C3 and C4;
- κ between P2 and the final code;
- the counts of NONE, SAME, PARTIAL and DIFFERENT;
- the triage rule DELIBERATE → SPEC, ACCIDENTAL → IMPL on the primary set (macro-F1, as in E7).

## Interpretation
- **H-E8-1 PASS:** the E7 association survives direction-blind authoring. The practical triage claim can then be made for propositions derived from code reading. The scope is limited to discrepancies that a blind reader finds and matches.
- **H-E8-1 FAIL (p ≥ 0.05 with both arms ≥ 8):** the E7 association depended on direction-aware authoring. H12 is then downgraded to "artefact of proposition wording, not established".
- **INSUFFICIENT:** E8 is inconclusive. Both the counts and the reason (NONE or DIFFERENT) are reported.

## Threats (known in advance)
- The writer still sees a package whose files the miner selected around the mismatch. The selection is not direction-specific, because it includes both sides.
- J1 sees the miner's proposition. Matching is a semantic judgement, not a direction judgement.
- All roles are played by the same model family.
