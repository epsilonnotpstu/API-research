# Semantic matching of paired propositions

**Supervisor authorization:** this task overrides the general instruction in `research/AGENTS.md` / `09_collab/PROTOCOL.md` to read `COLLAB_BOARD.md` or coordinator task files. Do not read the board or any coordinator task files. Read only `../../../09_collab/PROTOCOL.md` and this task file.

## What you are given
`pairs.csv` has one row per item, with the columns `item_id, operation, proposition_A, proposition_B`. Both propositions take the form `"<METHOD> <path>: contract says <X>; implementation does <Y>"`. They were written independently, by two readers, about the same artifacts. `proposition_B` may be `NONE`.

## Your task (per row)
Decide whether B describes **the same contract–implementation discrepancy** as A.
- **SAME:** the same operation, the same behaviour facet and the same mismatch. Wording, detail or locators may differ. For example, both say the contract declares a 404 and the code returns a 204 for the same condition.
- **PARTIAL:** the same operation and an overlapping facet, but B's X or Y differs materially from A's. For example, the same field, but a different aspect of it; or a broader or narrower condition.
- **DIFFERENT:** B describes another discrepancy.
- **NONE:** B is `NONE`.

Judge only semantic correspondence. Do not judge which proposition is accurate, or which artifact is right.

## Output
Write `match_<YOUR_ID>.csv` with these columns, one row per item, in `pairs.csv` order:
`item_id, match, rationale`
- `rationale`: at most 25 words.

## Rules
- **Your first command must be `cat TASK_MATCH.md`.**
- Read only `pairs.csv`, this file and `../../../09_collab/PROTOCOL.md`. Open, list or search nothing else. No network.
- Write only `match_<YOUR_ID>.csv` and, optionally, `match_work_<YOUR_ID>/` in this directory.
- YOUR_ID is supplied at launch.
