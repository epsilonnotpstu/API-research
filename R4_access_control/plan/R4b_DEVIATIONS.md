# R4b deviations (append-only)

## R4b-F1 (2026-11-24 ~07:15): authorization-header tokens; first build discarded before any coder
- **Problem.** The pre-coding privacy audit found example and PoC tokens in `Authorization: Bearer|Basic …` headers: in 3 advisory descriptions (`item.md`) and in 1 contract.
- **Fix.** The header value is now replaced by `[REDACTED]` in `item.md` and in contract text. The line count is unchanged.
- **Effect.** The first build, its salt and its key were deleted, and the build was re-run with a fresh salt.
- **No influence on results.** No coder had been launched, and no package content other than the audit counts was inspected.

## P-R4b-1 (2026-11-24 ~07:15): G4 stopped at the Codex usage limit after writing complete codes
- **What happened.** G4 wrote `codes_G4.csv` with all 102 rows, in order and with allowed values. It hit the Codex usage limit during a final security-locator verification, before writing `codes_report_G4.md`.
- **Decision.** The CSV is used as delivered, because the plan requires codes, not the report.
- **Why there is no resume.** The usage limit resets at 22:09, after the sprint deadline.
- **Output freeze.** Contains G4's CSV without a report.

## D1 (2026-11-24, at scoring): policy_in_contract = NA written by the Claude coders
- **Problem.** H3 wrote `NA` in 35 rows and H4 in 25 rows, always where `contract_operation` is ABSENT, NO_CONTRACT or UNCLEAR. `NA` is not an allowed value, so the frozen scorer raised an error before producing any result.
- **Fix.** `plan/r4b_score_with_D1.sh` maps `NA` to UNCLEAR, the conservative non-decision, in **copies** of the code files, then runs the unchanged frozen `score_r4b.py` on those copies. The original codes stay as frozen.
- **Effect on the hypotheses.** None:
  - H-R4-3b and H-R4-5 use only items with `contract_operation` = PRESENT, where no `NA` occurs.
  - Affected: only the Claude-family descriptive distribution of `policy_in_contract`, and its within-family κ.
