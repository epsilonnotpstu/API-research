# E11 results: cross-family replication of divergence-kind coding
Claude (supervisor-delegated), 2026-11-16. The data were scored once, with the frozen scorer.

**Freezes:**
- `e11_plan_freeze.sha256`: plan, scorer and inputs, before the package was built.
- `e11_package_freeze.sha256`: the six batch trees, `items.csv` and `TASK_CODE.md`, before coding.
- `e11_outputs_freeze.sha256`: the 12 code files, before scoring.

All of them were re-verified before scoring. **Raw output:** `e11_score_output.txt`, `e11_scores.csv`.

## Runs
**Coders and batches:**
- K1 and K2 were Claude subagents (sonnet), each started with a fresh context. They were told nothing about the hypotheses, the directions or any earlier result.
- There were 12 runs (2 coders × 6 batches of 21 items). Each run completed, with all items in order, valid values and a report.

**The data are 125 items, not 126.** `e7_key.csv` has 45 `set=new` X items, but one of them is BOTH, and the frozen scorer excludes it as the plan requires. The remaining 125 items are X 44, W 41 and V 40 (SPEC 70, IMPL 55), in 82 clusters.

**Boundary audit:** every tool call in every transcript was checked by resolving each path against the shell's working directory. No run read a file outside its batch directory, apart from `PROTOCOL.md`.

**Protocol deviations, disclosed by the coders:**
- K1 b2 compared one file across two item pairs with `md5sum`.
- K2 b1 listed file sizes in a second item directory.
- K1 b1 and K1 b6 saw the other coder's file *names* in an `ls`; they did not open the files.

None of these exposes directions or hypotheses.

## Pre-registered tests
| Test | Result | Verdict |
|---|---|---|
| **H-E11-1:** kind × direction with Claude coders | Items: DELIBERATE → SPEC **67/81** vs ACCIDENTAL → SPEC **1/39**; Fisher one-sided p = 2.1e-18. Clusters: 38/51 vs 1/30; p = 7.1e-11 | **PASS** |
| **H-E11-2:** GPT vs Claude final kind | 116/118 agree on items both decided; **κ = 0.960** | **PASS** |

## Descriptives
- **K1–K2 agreement:** κ = 0.912.
- **Final kinds (D/A/U):** Claude 81/39/5, GPT 85/37/3.
- **GPT (rows) × Claude (columns):**

| GPT \ Claude | D | A | U |
|---|---|---|---|
| D | 81 | 2 | 2 |
| A | 0 | 35 | 2 |
| U | 0 | 2 | 1 |

**Per set, using Claude kinds:**
| Set | DELIBERATE → SPEC | ACCIDENTAL → SPEC | R correct | Coverage |
|---|---|---|---|---|
| X | 26/33 | 0/11 | 37/44 | 44/44 |
| W | 23/26 | 0/15 | 38/41 | 41/41 |
| V | 18/22 | 1/13 | 30/35 | 35/40 |

## Interpretation
1. **The central finding does not depend on the model family of the coders.** Claude coders reproduce the kind × direction association on all 125 confirmatory items, at item level and at cluster level.
2. **The two families agree almost perfectly (κ 0.96).** This rules out the explanation that one model family's idiosyncratic reading creates the result.
3. **⚠️ What E11 does *not* show.**
   - All coders read the miner's proposition, which was written with knowledge of the fix.
   - E7's proposition-only control (κ = 1.0) showed that the kind is largely readable from that text.
   - High agreement across families is therefore consistent with both families reading the same textual cue.
   - E8b, which used direction-blind propositions, remains the evidence against a pure text artifact.
   - **Human coding is still required** to show that the construct, not only the model readings, is valid.

## Threats
- **One family per role:** sonnet for Claude, gpt-6.1-sol for GPT. Other families, open models for example, are untested.
- **Batching:** each subagent saw 21 items. Batch effects are not modelled.
- **Overlapping text:** the same miner text was shown to both families.
