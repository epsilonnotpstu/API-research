# R4b results: contract information with full, untruncated contracts (follow-up E-R4-2)
Claude (supervisor-delegated), 2026-11-24.

**Scoring.**
- Scored once with the frozen `plan/score_r4b.py` (`plan/r4b_plan_freeze.sha256`), run through `plan/r4b_score_with_D1.sh`.
- D1 is a documented normalisation of the invalid `policy_in_contract` = NA values to UNCLEAR. It was applied to copies of the codes, and it cannot affect any hypothesis.

**Freezes.** Packages: `plan/r4b_packages_freeze.sha256`. Outputs: `plan/r4b_outputs_freeze.sha256`.

**Records.**
- Raw output: `plan/r4b_score_output.txt`.
- Deviations: `plan/R4b_DEVIATIONS.md`:
  - R4b-F1: authorisation-header redaction before coding;
  - P-R4b-1: G4 report missing because of the usage limit;
  - D1.
- Audit: `plan/R4b_AUDIT.md`.

## Sample and reliability
- **Items.** 102 items from 54 repositories: the R4 items whose GPT final codes judged them access-control relevant.
- **Contracts.** Every coder saw **all** 504 contract documents in full, about 2.0 million lines; the largest item has 0.42 million lines.
- **Within-family κ** (GPT / Claude):
  - `contract_operation`: 0.77 / 0.86;
  - `contract_security`: 0.97 / 0.92;
  - `policy_in_contract`: 0.74 / 0.73.
- **Cross-family κ** on `contract_operation`: **1.00**. Both families decided 76 items and agreed on all of them.
- **Evidence validity.** Every PRESENT code cites a contract line that contains the coded path, for all four coders: G3 56/56, G4 58/58, H3 60/60, H4 61/61.

## Pre-registered results (GPT final codes)
| Measure | R4b (full contracts) | R4 (3,000-line truncation) | Verdict |
|---|---|---|---|
| E-R4-2a: vulnerable operation described in the contract | **56/102 = 0.55** [0.45, 0.64] | 41/102 = 0.40 | estimate |
| E-R4-2b: contract coverage UNCLEAR | 20/102 = 0.20 [0.13, 0.28] | 27/102 | estimate |
| **H-R4-3b**: violated rule absent from the contract (operation described, judgement decided) | **44/54 = 0.81** [0.69, 0.90]; p = 1.7 × 10⁻⁶ | 33/38 = 0.87 | **PASS** (Claude 51/57 = 0.89) |
| **H-R4-5**: documented vulnerable operation with **no** declared security requirement | **21/56 = 0.375** [0.26, 0.51]; binomial vs 0.1, p = 4.1 × 10⁻⁸ | — | **PASS** (Claude 18/56 = 0.32) |

## Agreement with R4 (exploratory; GPT final, R4 → R4b)
- **PRESENT → PRESENT:** 38.
- **UNCLEAR → PRESENT:** 18. These operations were beyond the 3,000-line truncation in R4.
- **ABSENT → ABSENT:** 22.
- **No R4 PRESENT became ABSENT.**
- **Other transitions:**
  - PRESENT → UNCLEAR: 3;
  - ABSENT → UNCLEAR: 7;
  - UNCLEAR → ABSENT: 4;
  - NO_CONTRACT → UNCLEAR: 5;
  - UNCLEAR → UNCLEAR: 5.

## Interpretation
1. **Truncation hid documented operations.** With full contracts, the share of vulnerable operations that are documented rises from 40% to 55%.
2. **The main R4 finding holds with full contracts and evidence citation.** Where the vulnerable operation is documented, the contract does not state the violated access rule in 81% of cases. By the Claude codes the figure is 89%.
3. **New finding (H-R4-5).** More than a third of the documented vulnerable operations declare no security requirement at all. A contract-driven tester would not even know that credentials are needed.
4. **Reliability.**
   - The coverage judgement is highly reliable once full contracts and locators are required: cross-family κ is 1.00 on decided items, and every locator is valid.
   - The rule judgement remains the hardest, with within-family κ of about 0.73–0.74.

## Threats
- **Population.** It is conditioned on R4's GPT relevance codes.
- **Process.**
  - One Claude run executed `git status` once, with its output discarded (audit).
  - G4 has no report (P-R4b-1).
- **Large contracts.** Coders searched them rather than reading them in full. This is a likely source of the remaining UNCLEAR codes.
