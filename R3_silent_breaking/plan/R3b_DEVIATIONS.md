# R3b deviations (append-only)

## P-R3b-1 (2026-11-24 ~07:20): GPT coders G5 and G6 stopped at the Codex usage limit before writing any output
- **What happened.** G5 and G6 wrote no codes. The Codex limit resets at 22:09 the same day, after the sprint deadline.
- **Status.** The Claude coders H5 and H6 (8 runs) completed: 60 rows each, with valid values and a clean audit.
- **Decision.** The pre-registered scoring needs both families, so R3b is **not scored** until the GPT coders finish. No partial or Claude-only result is reported.
- **How to finish.** Run `collab/scripts/r3b_finish.sh` after the limit resets. It resumes G5 and G6, audits, freezes the outputs, scores once and commits.

## P-R3b-2 (2026-11-24 ~12:10, before any R3b output was inspected): Claude Opus substitutes for the GPT-family coders G5 and G6
- **Instruction.** The user instructed: "Codex er baki kaj tmi kore ses koro". Codex itself cannot run until 22:09.
- **What changes.**
  - The G5 and G6 slots are filled by two **fresh-context Claude Opus subagents**. They work in `packages/r3b_blind` with the unchanged `TASK_R3b.md` and write `codes_G5.csv` and `codes_G6.csv`.
  - The supervising agent knows R3's results, so it does **not** code.
  - `packages/r3b_blind` holds only the items, `items.csv` and the task. No other coder's codes are reachable there.
- **Consequence for the design.**
  - Both coder pairs are now from the **Claude family**: Opus (G5/G6 slots) and Sonnet (H5/H6). The pre-registered "GPT-family" label no longer holds.
  - "Cross-family κ" in the R3b output therefore measures **cross-model agreement within one family** (Opus vs Sonnet), not agreement across families.
  - The primary codes are the G-slot (Opus) pair, as the frozen scorer prescribes.
  - This is reported as a limitation in R3b_RESULTS and in the paper.
- **Unchanged.** The frozen scorer, the task and the packages.
