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
4. **[E9]** Whether an explicit kind rule improves on the LLM.

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
- **RQ4 (Hybrid).** Does routing accidental divergences to the implementation improve LLM triage? **[E9]**

**Contributions:**
1. **A labelled corpus.** 111 real contract-alignment fixes (25 E6, 45 E7, 41 T47), labelled with repair direction, plus excerpt packages of each item's parent state.
2. **A blind coding instrument for divergence kind.** Its within-model reliability is κ 0.89–1.00.
3. **Confirmatory evidence of the kind → direction association.** It holds under miner-written and direction-blind propositions.
4. **A comparison of LLM and codebook triage** on synthetic and real faults.
5. **A fully pre-registered, hash-frozen protocol** for LLM-coded empirical SE studies. Every amendment is disclosed.

## 2. Background and Related Work
**[TODO]** This section needs a full literature pass. The sources are `06_final_recommendations/R1_novelty_check_E0.md` §2 and §7 and `04_paper_analysis/cross_paper_synthesis.md`.

- **REST fuzzing and oracles:** EvoMaster, Schemathesis, RESTler, RESTest/P001. Schema conformance as the oracle.
- **Spec quality and spec faults:**
  - 2607.12101, fault injection in OpenAPI;
  - SpecFix (P032), static spec repair;
  - DualMine (2609.27806), runtime constraint reconciliation.
- **Failure diagnosis:**
  - FDRRestTest (ESEM 2026): request/test-side diagnosis and repair;
  - RESTifAI (2512.08706): manual Bug / Enhancement / Invalid labels.
- **Practitioner drift tools:** Beeceptor, api-drift-detector. These detect drift, and a human decides whether it is intended.
- **Gap:** none of these predicts which artifact will be repaired, or evaluates such a prediction against developer fixes.

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
| E9 | 85 new items | RQ4 | **[E9]** |

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

- **The rule's errors are asymmetric.**
  - ACCIDENTAL → IMPL had precision 1.00 on every set.
  - DELIBERATE → SPEC was wrong about one time in five.
- **One post-hoc claim was not replicated.** E8 suggested that blind readers miss accidental divergences more often. The pre-registered E8b test gave p = 0.31, so we retract that claim.

### 4.4 RQ4: Hybrid triage [E9]
**Part A (retrospective, exploratory; data seen before):**
- On the 18 E6 items, M1's errors were all on DELIBERATE items. M1 was correct on 7/7 ACCIDENTAL items and on 7/10 DELIBERATE items, for both labellers.
- The hybrid therefore changed no labels.

**Part B (confirmatory, 85 new items):** **[E9]**

## 5. Discussion
- **The default assumption is wrong for a large share of fixes.** Tools that assume "the implementation is wrong" would misroute a large share of real fixes. In our sample, developers repaired the contract in more than half of them.
- **Accidental divergences can be routed to code automatically.** No accidental divergence in our data was resolved by changing the contract, so a pipeline can route these to the code with high precision.
- **Deliberate divergences need a human decision.** They lean towards spec repair, but about one in five is still repaired in the code. This matches practitioner tools, where a human decides whether drift is intended.
- **Why does the LLM already do well?** One reading is that it implicitly recognises the deliberate/accidental distinction. **[E9]** will test whether the explicit rule adds anything.
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
**[TODO]** Plan the replication package:
- packages, keys, codes, labels, scorers, freezes, the analysis scripts and the logs;
- licence review for the upstream excerpts.
