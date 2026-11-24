# R3b deviations (append-only)

## P-R3b-1 (2026-11-24 ~07:20): GPT coders G5 and G6 stopped at the Codex usage limit before writing any output
- **What happened.** G5 and G6 wrote no codes. The Codex limit resets at 22:09 the same day, after the sprint deadline.
- **Status.** The Claude coders H5 and H6 (8 runs) completed: 60 rows each, with valid values and a clean audit.
- **Decision.** The pre-registered scoring needs both families, so R3b is **not scored** until the GPT coders finish. No partial or Claude-only result is reported.
- **How to finish.** Run `collab/scripts/r3b_finish.sh` after the limit resets. It resumes G5 and G6, audits, freezes the outputs, scores once and commits.
