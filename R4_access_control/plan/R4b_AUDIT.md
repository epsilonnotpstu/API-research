# R4b coder audit (Claude, 2026-11-24, before the output freeze)
Run with `collab/scripts/r4b_audit.py`; only counts and snippets were inspected.

**GPT coders (Codex).**
- **G3:** 102 of 102 rows, in order, with allowed values and a report; 0 flags.
- **G4:** 102 of 102 rows, in order, with allowed values. There is no report, because G4 hit the usage limit (P-R4b-1). 0 flags.

**Claude coders (H3, H4; 12 runs, each 17 items, 24–49 tool calls, 98–173 s).** All outputs are complete, in order and valid, with reports.

**Flags.** Most are relative moves within the run's own batch (`cd ../../Cnnn`), which is permitted. One incident:
- **H3 kb4:** ran `git -C . status >/dev/null 2>&1` once, inside an item folder.
- **Effect:** none. The output was discarded and no history or other file was read.
- **Status:** recorded as a minor boundary breach without effect on the codes.
