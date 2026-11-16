# E9 — Hybrid triage: divergence-kind rule + zero-shot LLM (pre-registration)

**Status:** frozen before any E9 computation or Codex run; hashes in `e9_plan_freeze.sha256`. Decided by Claude (supervisor-delegated), 2026-11-16.

## Why
- **What earlier experiments found:**
  - E6: zero-shot LLM triage (M1) reached macro-F1 0.86–0.88 on real fixes.
  - E7/E8b: an ACCIDENTAL divergence was never repaired by changing the spec (pooled 0/10 in E8b, 0/11 in E7).
- **E9 tests:** does overriding M1 with "ACCIDENTAL → IMPL" improve triage? And are M1's errors concentrated on DELIBERATE divergences?

## Methods (per item)
- **M1:** zero-shot LLM label (L1 ∈ SPEC, IMPL, TEST, ENV, UNDECIDABLE). The prompt is the E6 M1 instruction text, adapted only to the excerpt package layout.
- **R (rule):** DELIBERATE → SPEC, ACCIDENTAL → IMPL, UNCLEAR → abstain.
- **HYB:** if the final kind is ACCIDENTAL → IMPL; otherwise → the M1 label.

## Final divergence kind
- **Base data:** blind C-coder codes from the miner proposition plus files.
- **If the two coders agree:** use that value.
- **If they disagree:** UNCLEAR. There is no adjudication, so Claude makes no item-level judgement.
- **Sources:**
  - E7 new items (X): C1/C2.
  - T47 items (W): new coders C7/C8, given the byte-identical `e7_blind/TASK_CODE.md` on `e8b_blind/`.
  - E6 items in Part A: C1/C2 exploratory codes.

## Part A — retrospective (exploratory, NOT confirmatory)
**Data:**
- the 18 scored E6 items;
- M1 labels Y1/Y2 from E6;
- kinds from C1/C2 on the mapped X items (K → `source_item` → fix_commit + operation → X).

**Why not confirmatory:** all of these data were seen before. This part only checks whether the hybrid could matter at all.

## Part B — confirmatory
**Items:**
- 44 E7 new items (X; the BOTH item is excluded at scoring);
- 41 T47 items (W).
- Truth is SPEC/IMPL only, from the key: `e7_key.csv` / `e8b_key.csv`.

**Labelling package:**
- `E2_labelling/e9_m1/` holds copies of the X (new only) and W item dirs.
- `items.csv` has columns `item_id, repo, operation, proposition` (the miner's proposition, as in E6).
- `TASK_M1.md` is used.

**Labellers:**
- L1 and L2: fresh Codex sessions, gpt-6.1-sol, high effort.
- If a labeller stops on a usage limit, the same session is resumed after the reset. Claude cannot take over a blind role, because Claude has opened the keys.

**Primary H-E9-1:** HYB beats M1.
- **Per labeller:** a discordant item is one where HYB ≠ M1, which happens only when the kind is ACCIDENTAL and M1 ≠ IMPL.
  - **Win:** HYB is correct and M1 is wrong.
  - **Loss:** the reverse.
- **PASS** if all three hold:
  1. pooled wins vs losses over both labellers give an exact one-sided sign test p < 0.05;
  2. each labeller has wins ≥ losses;
  3. there are ≥ 5 pooled discordant items.
- **INSUFFICIENT** if there are < 5 discordant items. This would mean M1 already handles accidental divergences, so the override adds nothing in practice.
- **FAIL** otherwise.

**Secondary:**
- Macro-F1 over SPEC/IMPL, with any other label or abstention counted as a miss:
  - M1 per labeller;
  - R;
  - HYB per labeller.
- HYB override precision: correct overrides ÷ all overrides.

**Descriptive:**
- M1 accuracy split by final kind (DELIBERATE vs ACCIDENTAL);
- L1–L2 agreement;
- the same analyses within X only and within W only.

## Interpretation
- **PASS:** recommend the hybrid pipeline. The kind rule routes ACCIDENTAL divergences to IMPL, and the LLM handles the rest.
- **INSUFFICIENT or FAIL:** the kind rule is an explanation of the LLM's success, not an improvement over it.
- In every case, report where M1's residual errors fall, by kind.

## Threats (known in advance)
- **Same model family.** The coders and the M1 labellers are the same model family, so their errors may be correlated.
- **Proposition wording.** Both the kind and M1 see the miner's proposition.
- **Package difference.** These are excerpt packages (≤ 8 implementation files), whereas E6 used whole modules.
- **Item dependence.** Some items share a repo or a fix.
