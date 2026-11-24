# R4b follow-up plan: contract information with full, untruncated contracts (E-R4-2)

Pre-registered by Claude (supervisor-delegated) on 2026-11-24, before any R4b package was built or coded. This plan, `plan/score_r4b.py`, `plan/test_score_r4b.py` and `plan/TASK_R4b.md` are hash-frozen in `plan/r4b_plan_freeze.sha256` before packaging. The scorer runs once. R4's own frozen results are unchanged; R4b is a follow-up robustness study and is reported as such.

## Motivation
R4's RQ3 result (H-R4-3: the contract does not state the violated rule in 33 of 38 decided cases) has two documented weaknesses:
1. Contract documents were truncated to their first 3,000 lines. As a result, 27 of the 102 access-control items were coded `contract_operation` = UNCLEAR.
2. An over-broad attribution redaction removed the whole advisory description in 4 items.

R4b re-codes only the contract fields for the same items, with full contracts and a corrected redaction. Coders must also cite evidence.

## Population
All 102 items whose R4 GPT final `ac_relevant` is YES (`plan/r4_score_output.txt`), identified by the item ids in the frozen R4 codes.

## Packages (`packages/r4b_blind`, Claude batches `r4b_kb*` with 17 items each)
Item ids are re-shuffled with a new salt (`mining/key/r4b_shuffle_salt.txt`), giving ids `C001`…. The key `mining/key/r4b_key.csv` maps each R4b id to its R4 id. Each item folder contains:
- **`item.md`.** The repository short name, language, CWE ids, and the advisory summary and description.
  - Redaction: links, e-mail addresses, credit sections (R4's F2/F3 rule), and token and key patterns.
  - **No line-level attribution redaction of the advisory text.** This fixes the R4 redaction loss.
- **`diff.patch`, `before/` and `after/`.** As in R4: source files only, at most 20 files, and R3 redaction of the code.
- **`contract/`.**
  - **All** contract documents at the vulnerable (parent) version, by R4's §3.1 file-name rule, **untruncated**. Token, key and e-mail redaction only; line count preserved.
  - `contract/INDEX.md` lists each document with its line count.

## Coding (`plan/TASK_R4b.md`)
**Coders.** Two GPT-family coders (G3, G4; Codex `gpt-6.1-sol`, high effort, fresh sessions) and two Claude-family coders (H3, H4; fresh Claude Sonnet subagents), all blind to R4's codes and results.

**Fields per item:**
- **`operation`:** the vulnerable HTTP operation(s), written `METHOD /path` and separated by `;`, or `UNKNOWN`.
- **`contract_operation`:** PRESENT, ABSENT, NO_CONTRACT or UNCLEAR. PRESENT requires `op_locator` = `file:line` of the path entry in `contract/`.
- **`contract_security`:** DECLARED, NOT_DECLARED, UNCLEAR, or NA when the operation is not PRESENT. DECLARED requires `sec_locator`.
- **`policy_in_contract`:** YES, NO or UNCLEAR. YES requires `policy_quote`, at most 25 words copied verbatim from the contract.
- **`confidence`** (1–3) and **`rationale`** (at most 30 words).

**Final codes.** A family's final code is the field-wise agreement of its two coders; disagreement becomes UNCLEAR. `contract_security` counts only where both coders say PRESENT. GPT codes are primary.

## Measures (all pre-registered; α = 0.05)
- **E-R4-2a (descriptive):** the share of `contract_operation` = PRESENT among the 102, with a Wilson CI, set beside R4's 41/102.
- **E-R4-2b (descriptive):** the share of UNCLEAR, set beside R4's 27/102.
- **H-R4-3b (replication of H-R4-3 with full contracts):**
  - Claim: among items with GPT final `contract_operation` = PRESENT and `policy_in_contract` decided, more than half have `policy_in_contract` = NO.
  - Test: one-sided binomial against 0.5; minimum 20 items, else INSUFFICIENT.
  - The Claude-family value is also reported.
- **H-R4-5 (contract security declarations are incomplete):**
  - Claim: among items with GPT final `contract_operation` = PRESENT and `contract_security` decided, the share DECLARED is below 0.9.
  - Test: one-sided binomial of the number NOT_DECLARED against p0 = 0.1, upper tail; minimum 20 items.
  - This tests whether more than 10% of documented vulnerable operations lack any declared security requirement.
- **Reliability:** within-family κ per field, and cross-family κ on `contract_operation` over items both families decided.
- **Evidence validity (mechanical, exploratory):** for each coder's PRESENT code, check that `op_locator`'s file exists in `contract/` and that the cited line, or one of the ±3 lines around it, contains a path segment of the coded operation. Report the share valid per coder.
- **Agreement with R4 (exploratory):** a cross-tab of R4 GPT final `contract_operation` against R4b GPT final `contract_operation`.

## Threats (planned)
- **Selection.** R4b codes only the 102 items that R4's GPT coders judged access-control relevant. This conditions on R4's GPT codes.
- **Process.** The supervisor knows R4's results. R4b's packages, task and scorer are mechanical, and frozen before any coding.
- **Large contracts.** Coders must search them, and some may still be judged UNCLEAR.
