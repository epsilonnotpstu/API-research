# R3 blind-run audit (2026-11-18), before the output freeze and before scoring
Produced by `collab/scripts/r3_audit.py` and a direct log grep.

**GPT coders G1/G2 (Codex, high effort, `packages/r3_blind`, one run each, no usage limit).**
- G1: 47 commands; G2: 35 commands.
- Each wrote 136 rows in `items.csv` order, with valid values and a report.
- No path outside the package and no `git` command was used, and no plan, scorer or mining file was read. The only `/home/...` strings in the logs are Codex start-up messages about unrelated skill files and the workdir line.

**Claude coders H1/H2 (sonnet subagents, fresh context, `r3_kb1`–`r3_kb10`, 20 runs).**
- Each run wrote all rows of its batch, with valid values and a report.
- Tool calls per run: 7–18. Runs took 31–67 seconds.
- ⚠️ Faster and with fewer tool calls than the R1 kind coders. This is recorded as a threat: the coders mostly read `diff.patch` and the item files in bulk.
- **Boundary.** Six runs (H1 kb1, H2 kb1, H1 kb3, H1 kb4, H1 kb6, H1 kb10) issued `ls ../../../research/09_collab/PROTOCOL.md`. TASK_R3.md permits reading this file, but the permission system denied the call. No content was read and none of the runs retried.
- **Other flags were false positives.** They are coder locators written as `after/.../File.java` and an in-batch `sed` on `diff.patch`.
- **Order.** `r3_kb9/codes_H2.csv` holds the same 14 IDs as `items.csv`, without duplicates, but in a different order from row 3. The scorer keys rows by `item_id`, so the order has no effect.

**Verdict.** No out-of-package reads were found. All outputs are complete.
