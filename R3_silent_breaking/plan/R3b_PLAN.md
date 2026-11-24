# R3b follow-up plan: is the changed behaviour specified in the full contract? (E-R3-2)

Pre-registered by Claude (supervisor-delegated) on 2026-11-24, before any R3b package was built or coded. This plan, `plan/score_r3b.py`, `plan/test_score_r3b.py` and `plan/TASK_R3b.md` are hash-frozen in `plan/r3b_plan_freeze.sha256`. The scorer runs once. R3's frozen results are unchanged; R3b is a follow-up robustness study.

## Motivation
R3 reports that only 1 of 60 observable changes concerned behaviour the parent contract specified (56 UNSPECIFIED, 3 UNCLEAR). That judgement rested on limited contract context:
- 93 of the 136 items received only a raw fallback: the first 2,000 redacted lines of the root contract documents;
- 29 items had no contract document at the parent.

R3b re-codes the specification question for the same 60 items. Coders get **all** contract documents at the parent commit, **untruncated**, and must cite evidence.

## Population
The 60 items whose R3 GPT final `observable_change` is YES, recomputed from the frozen R3 codes with the frozen `plan/score_r3.py` functions.

## Packages (`packages/r3b_blind`; Claude batches `r3b_kb*` of 15)
Item ids are re-shuffled with a new salt (`mining/key/r3b_shuffle_salt.txt`), giving `D001`…. The key `mining/key/r3b_key.csv` maps each R3b id to its R3 id. Each item folder contains:
- **`item.md`, `diff.patch`, `before/` and `after/`.** Copied byte-for-byte from the R3 package item.
- **`contract/`.** All files at the **parent** commit whose name contains `openapi` or `swagger` (case-insensitive), with extension `.yaml`, `.yml` or `.json`, and with no path segment in R3's excluded set (test, example, mock, vendor and similar). This is the R4 §3.1 file-name rule, applied here because R3's raw fallback has no file-level rule to reuse.
  - Full text; redaction covers e-mails, authorization-header values and known token prefixes only, with the line count preserved.
  - `contract/INDEX.md` lists each file with its line count.
  - Items with no such file get an empty `contract/` and an INDEX that says so.

## Coding (`plan/TASK_R3b.md`)
**Coders.** Two GPT-family coders (G5, G6; Codex `gpt-6.1-sol`, high effort, fresh sessions) and two Claude-family coders (H5, H6; fresh Sonnet subagents). All are blind to R3's codes.

**Fields per item:**
- **`changed_behaviour`:** one sentence describing the observable behaviour that changed, or `NONE`.
- **`affected_operation`:** `METHOD /path`, separated by `;`, or `UNKNOWN`.
- **`contract_operation`:** PRESENT, ABSENT, NO_CONTRACT or UNCLEAR. PRESENT requires `op_locator` = `contract/<file>:<line>`.
- **`contract_specified`:**
  - SPECIFIED: the contract explicitly states the behaviour that changed, such as that status code, that field, that constraint or that default. Requires `spec_quote`: at most 25 words copied verbatim from the contract.
  - UNSPECIFIED.
  - UNCLEAR.
- **`confidence`** (1–3) and **`rationale`** (at most 30 words).

**Final codes.** A family's final code is the field-wise agreement of its two coders; disagreement becomes UNCLEAR. GPT codes are primary.

## Measures (pre-registered; α = 0.05)
- **E-R3-2a:** the share SPECIFIED among the 60, with a Wilson CI, compared with R3's 1/60.
- **E-R3-2b:** the share of `contract_operation` PRESENT among the 60.
- **H-R3-4 (contracts rarely specify changed behaviour; replication with full contracts):**
  - Claim: among items with GPT final `contract_specified` decided, more than half are UNSPECIFIED.
  - Test: one-sided binomial against 0.5; minimum 20 items, else INSUFFICIENT.
  - The Claude-family value is also reported.
- **Reliability:** within-family κ per field, and cross-family κ on `contract_specified` over items both families decided.
- **Evidence validity (exploratory):** for each SPECIFIED code, check whether the `spec_quote`, with whitespace normalised, occurs verbatim in that item's `contract/` files. Report the share per coder.

## Threats (planned)
- The population is conditioned on R3's GPT codes.
- The file rule differs from R3's raw-fallback selection.
- The supervisor knows R3's results; the procedure is mechanical and frozen before coding.
