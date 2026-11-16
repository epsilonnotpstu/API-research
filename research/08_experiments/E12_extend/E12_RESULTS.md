# E12 results: fix-capped new items, GPT and Claude coders
Claude (supervisor-delegated), 2026-11-17. The data were scored once, with the frozen scorer plus one disclosed mechanical fix (see D1 below).

**Freezes:**
- `e12_plan_freeze.sha256`: the plan, the T49 task and its inputs, before mining.
- `e12_packages_freeze.sha256`: the five package trees, `items.csv`, the TASK files, the key and the scorer, before any blind run. A first version had CRLF line endings in four copies of `items.csv`; the content was identical. It was rewritten as LF and re-frozen before any run started.
- `e12_outputs_freeze.sha256`: the 16 code, label and report files, before scoring.

All of them were re-verified before scoring. **Raw output:** `e12_score_output.txt`, `e12_scores.csv`. **Post-hoc analyses:** `e12_exploratory_output.txt`.

## Items (T49, Codex miner, hypothesis-blind)
- T49 continued the frozen pool2 with a per-fix cap of 2 operations (45 operations dropped as `FIX_CAP`) and a combined repository cap of 10.
- It stopped below the 40-item target because every eligible repository was capped or exhausted. The yield was **36 items (SPEC 20, IMPL 16, BOTH 0)** from **24 candidates** in 6 repositories. The plan's stop rule (fewer than 20 items) did not apply.
- Verified independently by Claude:
  - all 73 tests re-run and pass;
  - every candidate has at most 2 items, and no candidate overlaps T48;
  - the key and the package match;
  - the earlier keys and pool2 are byte-identical;
  - the licence at each parent commit is permissive or copyleft only (`10_paper/LICENSE_REVIEW.md`);
  - a leakage scan of the package found only three pre-existing issue links in parent source.
- The T49 transcripts contain one encoded credential-like literal from an upstream patch. They are kept local (`09_collab/.gitignore`), and the package does not contain the literal (Codex's audit, plus Claude's secret scan of every committed file).

## Runs
| Role | ID | Family | Package | Result |
|---|---|---|---|---|
| Kind coder | C11, C12 | GPT (gpt-6.1-sol, Codex) | `e12_blind` | 36/36 rows each, valid, in order |
| Kind coder | K3, K4 | Claude (sonnet subagents, fresh context) | `e12_kb1`, `e12_kb2` (18 + 18) | 36/36 rows each, valid, in order |
| M1 labeller (may abstain) | L5 | GPT | `e12_m1` | 36/36: SPEC 17, IMPL 19, no abstentions |
| Forced-choice labeller | F3 | GPT | `e12_m1f` | 36/36: SPEC 17, IMPL 19 |

**Boundary audits.**
- *Codex logs:* every command's working directory was the run's own package. The flags were false positives: the API path segment `report_id`, and report text saying COLLAB_BOARD was *not* read.
- *Claude transcripts:* paths were resolved against the shell's working directory. No file outside the batch directory was read. The wrong-path attempt at `PROTOCOL.md` (K4 kb1) pointed at a file that does not exist. The paths flagged as "outside" were API paths inside grep patterns.
- *Disclosed deviations:*
  - K4 kb2 ran a final `ls`, after it had written `codes_K4.csv`, and saw the other coder's file *names*. It did not open them; the transcript shows no tool call on them.
  - Claude coders compared files across items within their own batch (`diff -rq . ../U31`), as in E11.

**D1, scorer deviation.** The frozen scorer crashed while loading `accepted_full_t49.csv`, because of a field over 128 KiB (Python's csv limit). The crash came before any result was printed. The fix is one added line, `csv.field_size_limit(sys.maxsize)`, with no logic change. The self-test still passes. Details are in `E12_DEVIATIONS.md`.

## Pre-registered tests
n = 36 (SPEC 20, IMPL 16) in 24 clusters (candidates). Coder agreement: C11–C12 κ = 1.000; K3–K4 κ = 0.889. Final kinds (D/A/U): GPT 17/19/0; Claude 17/17/2.

| Test | Result | Verdict |
|---|---|---|
| **H-E12-1:** kind × direction, GPT coders | Items: DELIBERATE → SPEC **17/17** vs ACCIDENTAL → SPEC **3/19**; Fisher one-sided p = 1.3e-7. Clusters: **11/11 vs 2/13**; p = 3.1e-5 | **PASS** |
| **H-E12-2:** kind × direction, Claude coders | Items: **17/17 vs 1/17**; p = 7.7e-9 | **PASS** |
| **H-E12-3:** GPT vs Claude final kinds | 34 items decided by both families: agree **34/34**, κ = **1.000** | **PASS** |
| **H-E12-4:** R vs F3 (exact McNemar) | On 36 items that R decides: R-only correct **0**, F3-only correct **0** | **INSUFFICIENT** (0 discordant pairs, fewer than 5) |

## Descriptives (pre-registered, no verdict)
| Method | Macro-F1 | Accuracy | Coverage |
|---|---|---|---|
| R with GPT kinds | 0.917 | 0.92 | 1.00 |
| R with Claude kinds | 0.944 | 0.97 | 0.94 |
| M1 (L5) | 0.917 | 0.92 | 1.00 |
| M1F (F3) | 0.917 | 0.92 | 1.00 |
| FB (L5, falling back to R) | 0.917 | 0.92 | 1.00 |

**Repositories (items / clusters):**
- ditto 9/6
- dockstore 5/3
- gravitee 4/2
- harbor 6/4
- open-banking-gateway 2/1
- service-api 10/8

**Pooled E10 + E12 (V + U, 76 items):**
- GPT kinds: items 36/41 vs 5/32, p = 3.0e-10; clusters 18/22 vs 3/22, p = 5.8e-6.
- Macro-F1: R 0.842, M1 (L3 + L5) 0.751, M1F (F1 + F3) 0.828.

## Post-hoc (exploratory, not pre-registered)
- **The predictions are identical on every item:** R = F3 = L5 on 36/36. On this sample, the GPT kind coders and the GPT labellers make the same decision item by item. So the kind rule adds no triage information over an LLM labeller here. The E10 advantage of R came from specific clusters (rhsm), and it does not recur in E12.
- **R's three errors:** all are ACCIDENTAL → truth SPEC, from 2 clusters (harbor 2, dockstore 1). Claude coded 2 of these 3 UNCLEAR, which is why R with Claude kinds scores higher (abstaining on them).
- **Claude kinds by cluster:** 11/11 vs 1/12, p = 8.9e-6.
- **Singleton-cluster items only (n = 12):** GPT kinds 5/5 vs 1/7, p = .0076.

## Interpretation
1. **The kind × direction association replicates for the third time on new items.** It holds with the per-fix cap, at cluster level and with two model families. Across E10, E11 and E12 it has never failed when the minimum sizes were met.
2. **Cross-family agreement is near-perfect again** (κ = 1.00; E11 0.96). Both families read the miner's proposition text, though. ⚠️ The agreement may therefore reflect cues in that text rather than independent judgement, and human coding is still required (open: `09_collab/human_check/`).
3. **No triage claim for the kind rule over LLM labellers comes from E12.** H-E12-4 has no discordant items. The pooled descriptives favour R over M1, but R ≈ M1F (0.842 vs 0.828). The defensible claim stays the one E10 made: kind is a strong *explanatory* variable for direction. Whether it is a *better triage signal* than a forced-choice LLM is not supported.
4. **Limits:**
   - the sample is small (36 items, 24 clusters, 6 repositories);
   - the item pool is exhausted, so more items need a new pool (T50);
   - every judgement is model-made, from static evidence only.
