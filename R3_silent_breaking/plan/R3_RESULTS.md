# R3 results: silent behavioural changes in REST APIs
Claude (supervisor-delegated), 2026-11-18. The analysis was scored once with the frozen `plan/score_r3.py` (`r3_plan_freeze.sha256`). The packages were frozen in `r3_packages_freeze.sha256` and the outputs in `r3_outputs_freeze.sha256`. Raw output: `r3_score_output.txt`. Rows: `r3_scores.csv`. Deviations: `R3_DEVIATIONS.md` (D1: mining completed by Claude with Codex's scripts; mechanical fixes F1–F6d before any coder). Audit: `R3_AUDIT.md`. The scorer was not changed.

## Sample
- The frozen pool has 18,590 candidate commits from 54 repositories, all made since 2023-01-01. Each candidate touches behaviour code and leaves the checked-in OpenAPI document unchanged.
- The seeded sample has 3 commits per repository. That gives 136 commits from 47 repositories: 7 repositories had no candidates, and 2 had fewer than 3.
- By language: Java 85, Go 48, Kotlin 3.
- All 136 commits were packaged.
- Coders: two GPT coders (κ: observable_change 0.90, change_kind 0.88, client_impact 0.85, contract_specified 0.87) and two Claude coders (0.82, 0.83, 0.74, 0.85).

## Pre-registered results
| Measure | Result | Verdict |
|---|---|---|
| **E-R3-1**: share with an observable API behaviour change | 60/136 = **0.44** (Wilson [0.36, 0.53]; repository-cluster bootstrap [0.35, 0.53]) | estimate |
| **E-R3-1**: share with a client-breaking change | 32/136 = **0.24** (Wilson [0.17, 0.31]; bootstrap [0.16, 0.31]) | estimate |
| **H-R3-1**: breaking changes that edit no contract annotation, so a code-generated contract diff would miss them | **29/32 = 0.91**, one-sided binomial p = 1.3 × 10⁻⁶ | **PASS** |
| **H-R3-2**: breaking changes to behaviour the contract *specified*, with no contract update within 90 days | 0/1 | **INSUFFICIENT** (n = 1 < 8) |
| **H-R3-3**: cross-family κ on observable_change | 99/102 both-decided, **κ = 0.94** | **PASS** |

## Descriptives (GPT final codes)
- **Kinds among the 60 observable changes:**
  - response content 9;
  - status / error mapping 9;
  - response shape 8;
  - side effect / state 7;
  - stricter input 6;
  - looser input 5;
  - authz 4;
  - header / media type 2;
  - default / optionality 2;
  - ordering / pagination 2;
  - other 1;
  - unclear 5.
- **Kinds that were mostly breaking:**
  - response content 7/9;
  - status / error mapping 7/9;
  - stricter input 6/6.
- **Kinds that were mostly compatible:**
  - response shape 8/8, which is mainly added fields;
  - looser input 5/5.
- **Contract coverage:**
  - Of the 60 changes, only **1** altered behaviour that the parent contract specified. 56 were UNSPECIFIED and 3 were unclear.
  - Contracts are silent about almost all the behaviour these commits change.
- **Contract annotations:** 8 of the 60 observable changes touched a contract annotation.
- **By language:** breaking changes in Go 13/48, Java 19/85, Kotlin 0/3.
- **Leave one repository out:** the breaking share stays between 0.226 and 0.241.

## Cross-family check: an important caveat
The two model families agree on whether behaviour changed (κ 0.94). They disagree strongly on whether the change breaks clients.

| Family | Observable change | Breaking |
|---|---|---|
| GPT final codes | 60/136 | 32/136 |
| Claude final codes | 55/136 | 12/136 |

So client impact is a judgement call that depends on the coding model. The pre-registered estimate uses the GPT codes. **We therefore report the breaking share as 9–24% depending on the model family.** The prevalence of silent observable changes (40–44%) is robust across families.

⚠️ This is an inference: Claude coders seem to label more changes COMPATIBLE or UNCLEAR. One possible reason is that they read "a client that worked correctly" more strictly. It was not tested.

## Interpretation
1. **Silent behavioural change is common.** About two in five behaviour-touching commits that leave the OpenAPI document unchanged still change what a client observes.
2. **Spec-diff tools miss these by construction, and so does contract generation from code.** Of the GPT-coded breaking changes, 29/32 touch no contract annotation. Even a tool such as AutoGuard, which generates the contract from code, would report nothing for them.
3. **Contracts rarely specify the behaviour that changes.** Only 1 of 60 changes concerned specified behaviour. Silent changes therefore mostly fall into the contract's blind spots, not into conflicts with what it states. This is also why H-R3-2 could not be tested.
4. **What is breaking is model-dependent.** Claims about breaking prevalence need human validation. The planned human spot-check (20 items) should focus on `client_impact`.

## Threats
- **LLM coders.**
  - Coders judged from code, not by execution.
  - The Claude coders ran fast (31–67 s per batch of 14), which suggests they mostly read the diffs; see `R3_AUDIT.md`.
- **Contract context.** 93 of the 136 items use the raw-fallback contract (the first 2,000 lines, redacted), and 29 have no checked-in contract at the parent commit. Judgements of `contract_specified` are therefore approximate.
- **Sampling.** Three commits per repository, since 2023. Only services with a checked-in OpenAPI document are included.
- **Process.** Mining was completed by Claude using Codex's scripts, with mechanical fixes made before any coder ran (`R3_DEVIATIONS.md` D1). There was no judgement step.
