# E13 deviations and process notes
Every entry here was recorded before any E13 blind run and before any score.

## P1: T50 continuation (T50b), 2026-11-17, Claude (supervisor-delegated)
**What happened.** T50 used its optional budget stop after two round-robin rounds. At that point:
- 40 of 12,832 pool3 candidates had been reviewed;
- the run had produced 8 items, against the 60-item target;
- Codex had not reached a usage limit.

**What changed.** The supervisor withdrew the budget stop and continued the identical procedure on the unchanged frozen pool3, from rank 3 (`09_collab/tasks/T50b.md`). The 8-item outputs are superseded, and the package is rebuilt from all accepted items with the existing salt.

**What the decision was based on.** Only `yield_t50.csv` and the non-direction parts of `T50_report.md`:
- no per-item or aggregate direction was viewed;
- no blind role had opened the package.

**Effect.** The E13 plan stop rule ("fewer than 20 items → run anyway; no further look") applies to the *final* T50 yield. The continuation is part of mining, not a look at outcomes.
