# R4 results: real access-control vulnerabilities vs contract-driven black-box testing
Claude (supervisor-delegated), 2026-11-23, about 20:40.

**Scoring and freezes.**
- Scored once with the frozen `plan/score_r4.py` (`plan/r4_plan_freeze.sha256`).
- Packages were frozen in `plan/r4_packages_freeze.sha256`, and outputs in `plan/r4_outputs_freeze.sha256` (41 files).
- The scorer was not changed.

**Supporting files.**
- Raw output: `plan/r4_score_output.txt`. Rows: `plan/r4_scores.csv`.
- Deviations: `plan/R4_DEVIATIONS.md`.
  - D1: two independent pipeline implementations, which agree exactly on pool and sample.
  - F1–F4: mechanical fixes before any coder ran.
  - P1: G1 was resumed after a capacity error.
- Audit: `plan/R4_AUDIT.md`.

**Note on the package freeze.** `R4_DEVIATIONS.md` is listed in the package freeze. Its frozen version is the one committed at `4e77402`. The current file has P1 appended, as deviations are append-only, so its live hash differs by design. Every package tree and every other frozen file verifies.

## Sample
- **Query.** GitHub reviewed advisories for Maven and Go, with access-control CWEs. It returned 2,025 advisories; 53 were withdrawn.
- **Fix commits.** 1,026 advisories resolved to a fix commit; 945 cite none, and one could not be fetched.
- **Eligible pool.** 176 items from 70 repositories, requiring a checked-in OpenAPI or Swagger document at the vulnerable version.
- **Sample.** At most 4 items per repository gives **138 items from 70 repositories**: Go 118 and Java 20, from the Maven ecosystem.
- **Within-family κ (GPT / Claude).**
  - `ac_relevant` 0.94 / 0.83;
  - `ac_kind` 0.91 / 0.86;
  - `principals_needed` 0.89 / 0.70;
  - `observable_via_http` 0.94 / 0.80;
  - `contract_operation` 0.73 / 0.76;
  - `contract_security` 0.73 / 0.85;
  - `policy_in_contract` 0.62 / 0.70;
  - `fix_location` 0.91 / 0.80.

## Pre-registered results (GPT final codes)
| Measure | Result | Verdict |
|---|---|---|
| E-R4-1: access-control relevant | 102/138 = **0.74** (Wilson [0.66, 0.81]; cluster bootstrap [0.64, 0.83]) | estimate |
| **H-R4-1**: at least two principals needed (decided items) | 49/89 = **0.55** (Wilson [0.45, 0.65]); p = 0.20 | **FAIL** |
| **H-R4-2**: silent fix (no contract file and no contract annotation changed) | 93/102 = **0.91** (Wilson [0.84, 0.95]); p = 5.0 × 10⁻¹⁹ | **PASS** |
| **H-R4-3**: violated rule absent from the contract, where the operation is described | 33/38 = **0.87** (Wilson [0.73, 0.94]); p = 2.1 × 10⁻⁶ | **PASS** |
| **H-R4-4**: cross-family κ on `ac_kind` | 72/83 agree, **κ = 0.83** | **PASS** |

**Cross-family check (Claude final codes).**
- H-R4-1: 40/80 = 0.50.
- H-R4-2: 96/105 = 0.91.
- H-R4-3: 35/39 = 0.90.
- Cross-family κ on `ac_relevant`: 0.86 (126 items decided by both).

**Leave one repository out.** H-R4-1 ranges 0.53–0.57, H-R4-2 0.91–0.93, and H-R4-3 0.86–0.89.

## Descriptives (GPT final codes, n = 102 access-control vulnerabilities)
- **Kinds:**
  - function level 25 (BFLA);
  - tenant isolation 19;
  - missing authentication 17;
  - object level 17 (BOLA);
  - property level 13;
  - other 3;
  - unclear 8.
- **Minimal black-box setup:**
  - two principals of the same role 27;
  - two roles 22;
  - anonymous request 21;
  - one principal 19;
  - unclear 13.
- **Setup by kind (exploratory; Figure 1):**
  - all 17 missing-authentication cases need only an anonymous request;
  - property-level cases mostly need one principal (11/13);
  - object-level cases mostly need two principals of the same role (12/17);
  - tenant-isolation cases mostly need two principals of the same role (15/19);
  - function-level cases mostly need two roles (18/25).
- **Observable via HTTP:** 101/102, plus 1 unclear.
- **Is the vulnerable operation in the contract?**
  - present 41 (0.40);
  - absent 29 (0.28);
  - unclear 27 (0.26);
  - no usable contract 5.
- **Security declared, where the operation is present:** declared 10, not declared 8, unclear 23.
- **Violated rule stated in the contract:**
  - yes 5;
  - no 69;
  - unclear 28;

  This covers all 102 vulnerabilities. Restricted to described operations, H-R4-3 gives 33/38 not stated.
- **Fix location:**
  - service logic 30;
  - middleware or filter 27;
  - handler 25;
  - other 5;
  - model binding 4;
  - data query 3;
  - unclear 8.
- **Silent fixes:** 93/102. Only 9 fixes touched a contract file or a contract annotation.
- **Tests:** 70/102 fixes (0.69) added or modified a test.
- **By ecosystem:**
  - Go: 89 access-control relevant, 85 silent, 40 multi-principal.
  - Maven: 13 relevant, 8 silent, 9 multi-principal.

## Interpretation
1. **Real access-control vulnerabilities split into two halves for a black-box tester (H-R4-1 fails).**
   - About 45% can in principle be provoked with no principal or one principal. These are missing authentication (17 anonymous) and property-level flaws (mostly one principal).
   - About 55% need a multi-principal setup, either two users of the same role or two roles. These are BOLA, tenant isolation and BFLA.
   - So the hypothesis "most need two or more principals" is not supported. The multi-principal half is exactly the half that today's single-credential fuzzers cannot reach.
2. **The contract rarely carries what an oracle needs (H-R4-3 passes).**
   - The vulnerable operation was clearly described in only 40% of cases. ⚠️ Part of the 26% unclear share is due to the 3,000-line truncation.
   - Even when it was described, the contract stated the violated rule in only 5 of 38 cases. Examples of such rules: ownership, required role or scope, read-only property.
   - Security requirements were declared for only 10 of the 41 described operations.
   - A contract-driven oracle therefore has, in most cases, no specification to check against.
3. **Fixes are silent (H-R4-2 passes).** 91% of fixes change neither the contract nor a contract annotation. API consumers relying on the contract learn nothing of the fix. This mirrors the companion finding for behavioural changes.
4. **Reliability.** Within-family κ is high for kind and setup. It is lowest for `policy_in_contract` (0.62 / 0.70), which is a harder judgement. Cross-family κ on kind is 0.83.

## Threats
- **Coders.**
  - Coders judged from code and advisory text, without running exploits.
  - The advisory text often describes the attack setup, so `principals_needed` partly reflects the advisory.
  - GPT coders took 12–25 minutes and Claude batches 61–156 s each. They may have relied mainly on `item.md` and the diff (⚠️ inference).
- **Contract context.** Truncated to 3,000 lines; this is a likely cause of many `contract_operation` UNCLEAR codes.
- **Redaction loss in `item.md`.** Found by a post-scoring check.
  - In 4 of 138 items (A004, A104, A108, A128), the whole advisory description was replaced by R3's attribution redaction: a one-line description containing an attribution-like phrase. Coders saw only the summary for these items.
  - In 71 items, part of the description was redacted (credits and links included).
  - Because the packages were frozen and coded, nothing was changed.
- **Sampling.** Only reviewed GitHub advisories with a resolvable fix commit and a checked-in contract are included. Go dominates (118/138). 831 resolved fixes were excluded because their project had no contract document.
- **Human check.** A human spot-check of 20 items is prepared (`human_check/r4_spotcheck.csv`) and will be reported separately.
