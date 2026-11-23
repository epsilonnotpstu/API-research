# R4 coder audit (Claude, 2026-11-23 20:36, before the output freeze and before any code was read)
The audit was run with `collab/scripts/r4_audit.py`; the full output is in `collab/reports/r4_audit_output.txt`. Only counts and short snippets were inspected, never codes.

**GPT coders G1 and G2 (Codex `gpt-6.1-sol`, high effort, `packages/r4_blind`).**
- Both delivered 138 of 138 rows, in order, with allowed values and a report.
- **Flags:** 0. Commands: G1 53, across the original log and one resume; G2 44.
- **G1 interruption.** G1 stopped once on a model-capacity error and was resumed in the same session (deviation P1).
- **Duration.** G2 finished in about 12 minutes; G1 took about 25 minutes in total.
- ⚠️ **Inference.** These are shorter than in R3, so the coders may have relied mainly on `item.md` and the diff. This is recorded as a threat.

**Claude coders H1 and H2 (Sonnet subagents, fresh context, `r4_kb1`–`r4_kb9`, 18 runs).**
- All 18 runs delivered complete, ordered, valid outputs with reports. Each run took 11–29 tool calls and 61–156 s.
- **Flags:** 5, all false positives:
  - three are `cd ../..` from an item's `contract/` folder back to the run's own batch folder;
  - two are the string "key/" inside the run's own report text ("recovery key/state").
- No read outside the run's own package was found.
