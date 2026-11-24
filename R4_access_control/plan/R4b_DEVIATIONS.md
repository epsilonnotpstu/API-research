# R4b deviations (append-only)

## R4b-F1 (2026-11-24 ~07:15): authorization-header tokens; first build discarded before any coder
- **Problem.** The pre-coding privacy audit found example and PoC tokens in `Authorization: Bearer|Basic …` headers: in 3 advisory descriptions (`item.md`) and in 1 contract.
- **Fix.** The header value is now replaced by `[REDACTED]` in `item.md` and in contract text. The line count is unchanged.
- **Effect.** The first build, its salt and its key were deleted, and the build was re-run with a fresh salt.
- **No influence on results.** No coder had been launched, and no package content other than the audit counts was inspected.
