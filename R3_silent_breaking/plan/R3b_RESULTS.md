# R3b results: is the changed behaviour specified in the full contract? (follow-up E-R3-2)
Claude (supervisor-delegated), 2026-11-24.

**Scoring.**
- Scored once with the frozen `plan/score_r3b.py` (`plan/r3b_plan_freeze.sha256`).
- Packages are frozen in `plan/r3b_packages_freeze.sha256`, outputs in `plan/r3b_outputs_freeze.sha256`.
- The raw output is `plan/r3b_score_output.txt`. The audit is `plan/R3b_AUDIT.md`.

**Deviations** (`plan/R3b_DEVIATIONS.md`):
- **P-R3b-1.** The GPT coders were blocked by the Codex usage limit.
- **P-R3b-2.** At the user's instruction, the G5 and G6 slots were filled by fresh **Claude Opus** subagents. Both coder pairs are therefore from the Claude family: Opus in the G slots and Sonnet in the H slots. The output's "GPT" and "cross-family" labels mean Opus and Opus-vs-Sonnet.

## Sample
- 60 items from 37 repositories. These are R3's observable changes by the R3 GPT final codes.
- The full parent contracts comprise 149 documents.
- 22 items have no contract file at the parent, according to the file-name rule.

## Results (primary: Opus pair)
| Measure | R3b (full contracts) | R3 (raw fallback / projection) | Verdict |
|---|---|---|---|
| E-R3-2a: changed behaviour SPECIFIED in the contract | **2/60 = 0.03** [0.01, 0.11] | 1/60 | estimate |
| E-R3-2b: affected operation described in the contract | **30/60 = 0.50** [0.38, 0.62] | — | estimate |
| **H-R3-4**: UNSPECIFIED among decided judgements | **58/60 = 0.97** [0.89, 0.99]; p = 1.6 × 10⁻¹⁵ | — | **PASS** (Sonnet pair 47/48 = 0.98) |

**Coverage of the affected operation (Opus pair).**
- present 30;
- no contract 25;
- absent 4;
- unclear 1.

**Reliability.**
- Within-pair κ for `contract_specified`: Opus 1.00, Sonnet 0.22.
- Opus vs Sonnet κ on the 48 items both decided: 0.00, **with 47 of 48 in agreement (98%)**.
- This is the known κ paradox under extreme prevalence: almost every code is UNSPECIFIED, so chance agreement is near 1. Raw agreement is the informative measure here.
- Within-pair κ for `contract_operation`: Opus 0.97, Sonnet 0.88.

**Evidence.** Every SPECIFIED code quotes text that occurs verbatim in the item's contract: G5 2/2, G6 2/2, H5 3/3, H6 2/2.

## Interpretation
- R3's coverage finding holds with complete contracts and evidence citation. Even when the affected operation is documented (half of the cases), the contract states the changed behaviour in only 2 of 60 changes.
- Silent behavioural changes fall almost entirely where contracts are silent.

## Threats
- Both coder pairs are from one model family (P-R3b-2). The pre-registered two-family check was not possible.
- The population is conditioned on R3's GPT codes.
- The file-name rule for contracts differs from R3's raw-fallback selection.
