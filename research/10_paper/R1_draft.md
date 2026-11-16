# Spec or Bug? Predicting Which Side Developers Repair When a REST API and Its Contract Disagree

*Working draft v0.1 (2026-11-16). Numbers are taken from the frozen result files cited in brackets. Sections marked **[TODO]** need content that is not yet available. Sections marked **[E9]** are filled after E9 Part B is scored.*

---

## Abstract
When a REST implementation and its OpenAPI contract disagree, a test failure does not say which artifact is wrong. Tools and practitioners usually assume that the code is wrong. We study this question on real contract-alignment fixes mined from open-source Java, Kotlin and Go REST projects.

**Main findings:**
1. **Developers often repair the contract, not the code:** SPEC was the repair direction in 26 of 45 new fixes.
2. **The kind of divergence predicts the repair direction.**
   - We separate *deliberate* divergences, where code explicitly written for the behaviour produces it, from *accidental* ones, where the behaviour is a side effect of an omission.
   - Deliberate divergences were repaired in the contract in 79% of cases (26/33). Accidental divergences were never repaired in the contract (0/11; one-sided Fisher p < 10⁻⁴).
   - The association survives propositions written by a direction-blind reader (39/48 vs 0/10, p = 1.8 × 10⁻⁶).
3. **A zero-shot LLM already triages real fixes well** (macro-F1 0.86–0.88), and better than an explicit intent-evidence codebook (0.70–0.72).
4. **An explicit kind rule does not improve on the LLM.** A pre-registered hybrid that routes accidental divergences to the implementation changed only 1 of 85 labels, because the LLM already labels accidental divergences correctly. The LLM's residual errors are abstentions on deliberate divergences. A post-hoc fallback to the kind rule on those abstentions reached macro-F1 0.98; this result is exploratory.

All hypotheses were pre-registered with hash-frozen scorers. All coders were blind to the hypothesis and to the repair direction.

---

## 1. Introduction
**The problem.** Schema-based REST testing tools report failures whenever observed behaviour disagrees with the OpenAPI document. Examples are EvoMaster, Schemathesis, RESTler and RESTest. Such a failure has at least two possible origins:
- the implementation is faulty;
- the specification is wrong, incomplete, or stale.

**Why existing work does not answer it:**
- Prior studies classify these failures by hand. Examples are RESTifAI, the TOSEM study of specification/SUT discrepancies, and the RESTest bug reports.
- Fault-injection work measures how spec faults affect fuzzers, but does not attribute failures. An example is arXiv 2607.12101.
- The RESTest authors list automated failure-to-fault classification as an open opportunity.

**Our framing.** We treat the question as *repair-direction triage*: given a divergence, which artifact will the developer change? We answer it with a staged, pre-registered study.

- **RQ1 (Visibility).** How often do contract–implementation divergences surface under fuzzing, and is single-sided blame adequate?
- **RQ2 (Triage methods).** How well do a zero-shot LLM and an intent-evidence codebook predict the repaired side, on injected faults and on real fixes?
- **RQ3 (Predictors).** Does the *kind* of divergence (deliberate vs accidental) predict the repair direction? Does this hold when the divergence is described by someone who does not know the direction?
- **RQ4 (Hybrid).** Does routing accidental divergences to the implementation improve LLM triage?

**Contributions:**
1. **A labelled corpus.** 111 real contract-alignment fixes (25 E6, 45 E7, 41 T47), labelled with repair direction, plus excerpt packages of each item's parent state.
2. **A blind coding instrument for divergence kind.** Its within-model reliability is κ 0.89–1.00.
3. **Confirmatory evidence of the kind → direction association.** It holds under miner-written and direction-blind propositions.
4. **A comparison of LLM and codebook triage** on synthetic and real faults.
5. **A fully pre-registered, hash-frozen protocol** for LLM-coded empirical SE studies. Every amendment is disclosed.

## 2. Background and Related Work
*Citation keys `[Pnnn]` refer to `02_screening/final_papers.md`. Items marked ⚠️ were verified only from the abstract, HTML or vendor documentation (`06_final_recommendations/R1_novelty_check_E0.md`). **[TODO]** Convert to BibTeX.*

### 2.1 The contract as oracle in REST testing
- **Black-box and white-box REST fuzzers use the OpenAPI document as both input model and oracle.** Examples are RESTler [P006], EvoMaster [P011], Schemathesis and RESTest [P001]; surveys and tool comparisons are [P002, P003, P004].
- **The usual oracles are 5xx responses and schema violations.** Their findings are often of doubtful severity [P015].
- **Spec–response disconformity dominates what such tools report.**
  - In fifteen days of online testing of 13 industrial APIs, 63% of failures and 50% of faults were disconformities between the specification and the response [P001].
  - Nearly all of more than 1,000 public specifications showed mismatches [P004].
  - Faulty or under-specified schemas are a main obstacle to fuzzer coverage [P003].
- **Such a failure has two possible causes:** the implementation is wrong, or the contract is wrong. No tool says which.
- **The RESTest authors name the gap.** They list automated classification of failures into faults as an open opportunity (replication package of [P001]).

### 2.2 Contract quality, inference and repair
- **Inference.** Static and path-sensitive analyses infer specifications from code [P018, P019]. They find many undocumented endpoints, parameters and responses, and developers confirmed some of the inconsistencies found [P018].
- **Repair.** SpecFix repairs documentation-detectable spec defects for LLM-agent wrapping [P032]. These are authentication, base URL and undocumented headers, and it works statically only.
- **Fault injection.** Mazhar et al. inject faults into OpenAPI documents to measure their effect on black-box fuzzers (arXiv 2607.12101). They hold the implementation fixed and do not attribute or repair failures.
- **Runtime reconciliation (⚠️).** DualMine reconciles spec-derived constraints with runtime executions (arXiv 2609.27806). Its output is a constraint set, not a failure-origin label.
- **Shared assumption.** All of this work treats the contract as the artifact to be improved. None asks whether the developer would instead change the code.

### 2.3 Failure diagnosis and triage
- **FDRRestTest (ESEM 2026)** diagnoses failed requests into seven categories and repairs the *test*: value substitution, prerequisite insertion, reordering. It does not attribute a failure to the spec or the implementation.
- **Manual labelling elsewhere.** RESTifAI (arXiv 2512.08706) and LLM test-amplification studies label failing tests by hand as Bug, Enhancement or Invalid. Some "Invalid" cases are business rules missing from the contract, which shows that the distinction matters in practice and is still made manually.
- **Practitioner drift tools (⚠️)** compare live traffic against the OpenAPI document and propose patches. Examples are Beeceptor contract drift and api-drift-detector. A human decides whether the drift is intended.
- **Their question is ours.** Is the divergence deliberate, so the contract should follow, or accidental, so the code should be fixed?

### 2.4 Gap
We found no work that:
1. predicts which artifact a developer will repair when contract and implementation disagree;
2. evaluates such a prediction against real developer fixes;
3. identifies an observable property of the divergence that predicts the repair direction.

This paper addresses all three.

## 3. Study Design

### 3.1 Overview
| Stage | Data | Purpose | Status |
|---|---|---|---|
| Pilot (E1) | scout-api + 3 SUTs; spec mutants and code mutants; fuzzing | RQ1 | descriptive |
| E4 | injected faults (spec and code side) | RQ2, synthetic | confirmatory |
| E5 | code mutants; codebook v3 | RQ2, safety of the codebook | confirmatory |
| E6 | 18 real fixes, 11 repos | RQ2, real | confirmatory |
| E7 | 45 new real fixes, 15 repos (+25 E6 items, exploratory) | RQ3 | confirmatory |
| E8 / E8b | E7 items + 41 new (T47) with direction-blind propositions | RQ3, leakage control | confirmatory (pooled) |
| E9 | 85 new items (44 E7 + 41 T47) | RQ4 | confirmatory (INSUFFICIENT) |

### 3.2 Mining real contract-alignment fixes
Protocol sources: `09_collab/tasks/T42.md`, `T45.md`, `T46.md`, `T47.md`.
- **Repositories:**
  - bare, read-only clones of OSS REST projects (Java, Kotlin, Go);
  - each has a contract surface: a checked-in OpenAPI/Swagger file, or swagger/springdoc/JAX-RS annotations.
- **Candidates:**
  - **Commit selection:** commits that touch the contract surface and/or the behaviour surface of the same operation, with a correction cue in the message (e.g. `swagger`, `openapi`, `spec`, `required`, `status code`, `nullable`, `align`, `fix`, `correct`).
  - **Exclusions:** merges, mass reformatting, dependency bumps and new-endpoint additions.
- **Ranking:**
  - Candidates are ranked deterministically by cue strength and by whether an operation-specific path is present.
  - The ranking gives no bonus to either direction.
  - The pool is hash-frozen before review.
  - From T46 on, a precise path filter excluded CI, config and workflow YAML files.
- **Review:**
  - Candidates are reviewed in rank order, with no direction targeting or quotas.
  - Stopping rule: a fixed number of accepted items, or a per-repo review budget.
- **Acceptance:** the commit resolves a specific, pre-existing mismatch between contract and behaviour for an existing operation.
  - New features with their docs are not accepted.
  - Changes that move both artifacts to new behaviour are not accepted either.
- **Propositions:**
  - Written from the parent state only, in a fixed neutral template: `"<METHOD> <path>: contract says <X>; implementation does <Y>"`.
  - Each proposition has parent-side locators and does not mention which side changed.
- **Repair direction:**
  - **SPEC:** only the contract changes;
  - **IMPL:** only the behaviour changes;
  - **BOTH:** excluded from the primary analyses.
- **Miner:** a Codex agent that knew neither hypothesis. It wrote each proposition from the parent state and recorded a direction key.
- **Cap:** at most 6 items per repository.
- **Upstream code was never executed.**

### 3.3 Packages and blinding
**Item packages:**
- Each item package contains only the parent state: a contract excerpt and at most 8 implementation files.
- It has no fix, commit message, date, SHA or history.

**Role separation (all roles are fresh LLM sessions confined to one directory):**
| Role | Knows the hypothesis? | Knows the direction? | Sees |
|---|---|---|---|
| Miner | no | yes (writes the key) | repo history |
| Coder (C1–C8) | no | no | proposition + package |
| Proposition-only coder (P1–P4) | no | no | proposition only |
| Direction-blind writer (W1, W2) | no | no | operation + package |
| Matcher (J1, J2) | no | no | W and miner propositions |
| Triage labeller (Y, G, L) | no | no | proposition + package |

**Protocol controls:**
- Boundary compliance was checked in every log.
- Every plan, task text, package tree and scorer was SHA-256 frozen and committed before the run that used it.
- Every freeze was re-verified before scoring.

### 3.4 Divergence-kind instrument
The coders read "the implementation does Y" and judge whether Y comes from project code explicitly written to produce it.

- **DELIBERATE:** Y comes from explicit code written for it, such as:
  - a guard, validation or required flag;
  - an explicit status code or response;
  - a serialization, naming or type choice;
  - an explicit branch;
  - a declared route.
- **ACCIDENTAL:** Y is a side effect of an omission or oversight, such as:
  - an unhandled exception or null dereference;
  - a missing branch;
  - an unset header or content type;
  - an unhandled framework default;
  - an ordering error;
  - a reused variable or cache.
- **UNCLEAR:** the artifacts do not settle it.

**Requirements:** every code has a parent `file:line` locator and a rationale of at most 40 words.

**Secondary field, contract specificity:**
- **SPECIFIC:** the contract has an explicit, dedicated statement about this behaviour.
- **GENERIC:** the contract's position comes from boilerplate, a default, a shared schema or silence.

### 3.5 Analyses
**Fisher test (H-E7-1, H-E7-2, H-E8-1):**
- One-sided Fisher exact test on a 2 × 2 table, with α = 0.05.
- Wilson 95% CIs for proportions.
- Haldane–Woolf CIs for odds ratios.
- Each arm must contain ≥ 8 items before a confirmatory claim is made.

**Triage metrics (RQ2, RQ4):**
- Macro-F1 over SPEC and IMPL. Any other label, or an abstention, counts as a miss.
- Decided-accuracy and coverage are also reported.

**Hybrid test (RQ4):** an exact one-sided sign test on discordant items.

## 4. Results

### 4.1 RQ1: Visibility (pilot, descriptive)
Source: `PILOT_SUMMARY.md` H1, H2, H6, H7, H9.
- **Spec faults are often invisible to positive-only fuzzing.** Replay and negative data expose them, but with noise. A mutated operation's signal cleared the noise floor in 34 of 61 fresh runs. For REQUEST_LOOSE it cleared in only 6 of 25.
- **Single-sided blame is inadequate.** 27% of baseline divergences (30/112) needed both the spec and the code changed.
- **The test oracle is itself a source of error:** 16% of baseline failures (26/161) were caused by the test.
- **Code faults surface in fresh fuzzing:** 25 of 31 mutants cleared the noise floor across paired seeds.
- **The pattern repeats across fuzzers.** The same fault-class pattern appears under EvoMaster (20/26) and Schemathesis (19/26).

### 4.2 RQ2: Triage methods
Sources: `E4_RESULTS.md`, `E5_*`, `E6_RESULTS.md`.

| Setting | M1 zero-shot LLM, macro-F1 | M2 codebook + intent tool, macro-F1 |
|---|---|---|
| Injected faults (E4) | 0.94 | 0.66–0.70 |
| Real fixes (E6, n = 18) | 0.86, 0.88 | 0.72, 0.70 |

- **The codebook makes no misattributions, but abstains often.** The intent-evidence codebook (E5 v3) made 0 misattributions. It returned UNDECIDABLE whenever independent intent evidence was absent.
- **On real fixes the codebook is not safer.** The pre-registered "M2 is safer" criterion (Q3) failed: decided-accuracy was similar, 0.85–0.94.
- **Shared errors.** Both methods failed on two items. In each, a lenient contract (an optional field, or a default) met deliberately strict code, and the developer tightened the spec. These items motivated RQ3.

### 4.3 RQ3: Divergence kind predicts repair direction

**E7: miner-written propositions.**
- **Data:** 45 new items. By repair direction: SPEC 26, IMPL 18, BOTH 1.
- **Reliability:** κ(kind) = 0.942.

| | DELIBERATE | ACCIDENTAL | OR [95% CI] | p |
|---|---|---|---|---|
| P(SPEC) | 26/33 = 0.79 [0.62, 0.89] | 0/11 [0.00, 0.26] | 81.3 [4.3, 1545] | < 10⁻⁴ |

- **Sensitivity:** the result holds when restricted to high-confidence mining, when cross-flagged items are excluded, and when only agreed codes are used. It also holds within each popularity stratum and in a leave-one-repo-out analysis (maximum p 6.7 × 10⁻⁵).
- **H-E7-2 (secondary):** P(SPEC | GENERIC) = 15/18 vs P(SPEC | SPECIFIC) = 11/26, p = 0.007.

**Leakage control (A3, proposition-only coder).**
- A coder that saw only the one-line proposition reproduced every kind code (κ = 1.0).
- The kind is therefore recoverable from the proposition text. That leaves two explanations:
  - kind is an inherent property of the described behaviour;
  - the direction-aware miner phrased the behaviour in a way that leaks the direction.

**E8 / E8b: direction-blind propositions.**
- **Design:**
  1. A writer who knew neither the direction nor the miner's text wrote its own proposition from the parent package.
  2. A matcher kept only the items where the writer described the same divergence as the miner (SAME).
  3. Fresh coders then coded the writer's text with the files.
- **E8 result:** on SAME items the kind code was unchanged in 35/35. E8 alone was INSUFFICIENT, because its accidental arm had 6 items, below the threshold of 8.
- **E8b (pre-registered, one further look, pooled with E8):**

| | DELIBERATE | ACCIDENTAL | OR [95% CI] | p |
|---|---|---|---|---|
| P(SPEC), pooled SAME | 39/48 = 0.81 [0.68, 0.90] | 0/10 [0.00, 0.28] | 87.3 [4.7, 1626] | 1.8 × 10⁻⁶ |

**Figure 1** (`figures/fig_kind_direction.pdf`; generated by `figures/make_fig_kind.py`, data in `fig_kind_direction_table.csv`).
- **What it shows:** the share of divergences repaired in the contract, by divergence kind, with Wilson 95% CIs.
- **Rows are not independent samples.**
  - E8 + E8b re-describes the E7 items and the T47 items.
  - The T47 row codes the same T47 items from the miner's text.
  - The E6 row is the exploratory set from which the hypothesis came.
- **In every row, no accidental divergence was repaired in the contract.**

- **The rule's errors are asymmetric.**
  - ACCIDENTAL → IMPL had precision 1.00 on every set.
  - DELIBERATE → SPEC was wrong about one time in five.
- **One post-hoc claim was not replicated.** E8 suggested that blind readers miss accidental divergences more often. The pre-registered E8b test gave p = 0.31, so we retract that claim.

### 4.4 RQ4: Hybrid triage [E9]
**Part A (retrospective, exploratory; data seen before):**
- On the 18 E6 items, M1's errors were all on DELIBERATE items. M1 was correct on 7/7 ACCIDENTAL items and on 7/10 DELIBERATE items, for both labellers.
- The hybrid therefore changed no labels.

**Part B (confirmatory, 85 new items: SPEC 49, IMPL 36; kinds DELIBERATE 61, ACCIDENTAL 24):**

| Method | Labeller 1 macro-F1 | Labeller 2 macro-F1 |
|---|---|---|
| R (kind rule) | 0.845 | 0.845 |
| M1 (zero-shot LLM) | 0.910 | 0.896 |
| HYB (ACCIDENTAL → IMPL, else M1) | 0.910 | 0.903 |

- **H-E9-1 is INSUFFICIENT.** HYB and M1 disagreed on only 1 item (pooled 1 win, 0 losses), below the pre-registered minimum of 5 discordant items.
- **M1 already labels accidental divergences correctly:** 24/24 and 23/24.
- **The override was always right:** precision 24/24. This is the third sample with no accidental divergence repaired in the spec.
- **M1's residual errors are almost all on DELIBERATE items:** 47/61 correct for each labeller. Most misses are UNDECIDABLE on items whose spec was later repaired (12 per labeller).
- **Post-hoc (exploratory):** using R only when M1 abstains raised macro-F1 to 0.976 for both labellers, with full coverage. This rule was formed after seeing the data and needs a new pre-registered test.

## 5. Discussion
- **The default assumption is wrong for a large share of fixes.** Tools that assume "the implementation is wrong" would misroute a large share of real fixes. In our sample, developers repaired the contract in more than half of them.
- **Accidental divergences can be routed to code automatically.** No accidental divergence in our data was resolved by changing the contract, so a pipeline can route these to the code with high precision.
- **Deliberate divergences need a human decision.** They lean towards spec repair, but about one in five is still repaired in the code. This matches practitioner tools, where a human decides whether drift is intended.
- **Why does the LLM already do well?** It appears to recognise the deliberate/accidental distinction implicitly. It never needed the accidental override (E9). Its weakness is deciding between a deliberate implementation choice and the contract when nothing says which is intended. There it abstains, while the kind rule's prior towards SPEC is right about 4 times in 5. Combining the two is the most promising practical pipeline (exploratory).
- **Implication for fuzzers.**
  - A runtime failure of the accidental kind (an unhandled exception, a 500, a missing header) is a strong signal of an implementation bug.
  - A clean, explicit rejection that contradicts the spec is more often a stale or under-specified contract.
- **[TODO]** Discuss contract specificity: generic contracts are repaired more often.

## 6. Threats to Validity
- **Construct.**
  - The truth label is the developer's repair direction, not an objective fault location.
  - Some SPEC repairs may legitimise a bug.
- **Same-model coders.**
  - Every coder, labeller and judge is from one LLM family, so high κ shows within-model consistency only.
  - **[TODO]** Report the human spot-check: 20 items, coded by the author, with κ against the model codes.
- **Proposition authorship.** Addressed by E8 and E8b. The remaining limits are a single writer and a single matcher.
- **Sampling.**
  - Only correction-cue commits, and only OSS Java, Kotlin and Go projects.
  - Items cluster by repository and fix.
  - The accidental arm is small (n = 10–11), so the odds-ratio CIs are very wide.
- **Hypothesis origin and forking paths.**
  - H-E7-1 came from post-hoc coding of the E6 items, which are reported as exploratory only.
  - All amendments were frozen before use and are disclosed: E7 A1–A3 and E8 B1, the single further look.
  - Some mining stages previewed candidates beyond their final prefix, as documented in the T46 and T47 reports.

## 7. Conclusion
**[TODO]** Write after E9.

## Data availability
Upstream licences are documented in `LICENSE_REVIEW.md`, checked at each item's parent commit. One repository later adopted a restrictive licence, but every excerpt we use comes from versions under MIT, Apache-2.0 or CC BY-NC 4.0, and the excerpts are released under those terms. As a robustness check, the headline results do not change without the three items closest to the restrictive period: E8b pooled 37/46 vs 0/10, p = 2.6e-6.

**[TODO]** Plan the replication package:
- packages, keys, codes, labels, scorers, freezes, the analysis scripts and the logs;
- licence review for the upstream excerpts.
