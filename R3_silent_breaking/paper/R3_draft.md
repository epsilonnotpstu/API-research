# Silent by Design? How Often REST Services Change Observable Behaviour Without Changing Their Contract

*Working draft v0.2 (2026-11-18). The design follows the frozen plan `plan/R3_PLAN.md`. Results come from the single scoring run (`plan/R3_RESULTS.md`).*

---

## Abstract
Spec-diff tools warn API clients only about changes visible in an OpenAPI document. We ask how often REST services change observable behaviour while leaving their contract untouched.

**Method.**
- From 54 open-source Java, Kotlin and Go services, we froze a pool of 18,590 commits since 2023 that modify behaviour code but no checked-in contract.
- We drew a seeded sample of 136 commits from 47 repositories.
- Two GPT-family and two Claude-family LLM coders classified each commit blind to its message and history, under a pre-registered, hash-frozen protocol.

**Results.**
- 44% of the commits (60/136; 95% CI 36–53%) change what some client can observe.
- Depending on the coding model family, 9–24% are client-breaking. The two families agree on observable change (κ 0.94) but not on breaking impact.
- Of the breaking changes, 91% (29/32) edit no contract annotation, so even contract generation from code, as in AutoGuard, would not reveal them (p = 1.3 × 10⁻⁶).
- The changed behaviour was specified by the prior contract in only 1 of 60 cases.

Silent behavioural change is therefore common, and it lives in the contract's blind spots. API change detection needs behavioural evidence, not only document diffs.

## 1. Introduction
REST services evolve continuously, and their clients depend on behaviour they cannot see in the code. The usual safeguard is to diff the service's OpenAPI contract between versions. oasdiff and openapi-diff do this, and so does AutoGuard, which first generates the contract from code. Any change that alters what an operation does but leaves the contract text unchanged is invisible to all of them.

Practitioners know the problem only partly:
- In an interview study, all 17 participants treated structural changes as breaking, but only 5 of 17 saw behavioural changes as harmful [Lercher et al. 2024].
- The same participants noted that "the OpenAPI specification only describes the API structure, not the API behavior".
- A 2026 systematic review of 97 breaking-change studies concludes that "the main remaining gap is behavioral breaking changes that preserve syntactic interfaces" [Chen et al. 2026].

For libraries, behavioural breaking changes have been measured: about 2.3% of Maven dependency updates broke client tests [Jayasuriya et al. 2024]. For REST services, where the contract is the main means of communication with clients, no such measurement exists.

We therefore ask how often REST services change observable behaviour without touching their contract, and what kind of changes these are.

- **RQ1 (prevalence).** Of the commits that change operation-implementing production code but not the checked-in contract, what share change observable API behaviour? What share do so in a client-breaking way?
- **RQ2 (kinds).** What kinds of observable change occur?
- **RQ3 (visibility).** How many breaking silent changes would stay invisible even to a contract generated from source annotations?
- **RQ4 (documentation lag).** How often is the contract updated within 90 days of such a change?

**Contributions.**
1. The first measurement of silent behavioural changes in REST service histories, from a frozen random sample of commits from 54 open-source services.
2. A closed taxonomy of silent change kinds, together with their client impact.
3. Evidence on how much code-level contract generation, as in AutoGuard, would recover.
4. A pre-registered, blind, two-model-family coding protocol and a replication package.

## 2. Background and Related Work
**Spec-based change detection.**
- oasdiff and openapi-diff compare two OpenAPI documents and report breaking changes such as removed operations, new required parameters and changed types.
- Yasmin et al. used such a diff (SwaggerDiff) on 2,224 specifications of 1,368 APIs from APIs.guru. They found that "87.3% of RESTful API versions that introduced breaking changes do not provide any deprecation information in the previous version" [Yasmin et al., ICSME 2020].
- These approaches see only what the document states.

**Contract generation from code.**
- AutoGuard generates OpenAPI descriptions of two versions of a Spring Boot service from source code and diffs them in CI [Lercher et al. 2025].
- Its authors note that OpenAPI descriptions "do not capture semantic changes".
- The 2026 review likewise characterises it as "blind to semantic changes such as altered JSON response structures under the same status code" [Chen et al. 2026].

**Behavioural breaking changes.**
- Jayasuriya et al. updated 30,548 Maven dependencies and ran client test suites. 2.30% of updates had behavioural breaking changes that affected clients, mostly in non-major releases [FSE 2024].
- The 2026 review finds that "detection of syntactic breaks is comparatively mature, while behavioral breaks remain difficult to detect automatically" [Chen et al. 2026].
- Neither study measures web APIs from service histories.

**Practitioner view.** Lercher et al. report that providers "miss tools for automatically extracting API changes from changes in their implementation". They also report that dynamic API designs improve structural compatibility but "often shift the problem, i.e., create semantic breaking changes instead" [JSS 2024].

**Contract–implementation divergence.**
- Our earlier study (R1, anonymised) examined how such divergences are *repaired* once noticed.
- Here we study how they *arise*, and how many affect clients without any visible contract change.

## 3. Study Design
*(Summarised from the frozen plan; see `plan/R3_PLAN.md`.)*

### 3.1 Corpus
54 open-source REST services (Java, Kotlin, Go), each with a checked-in OpenAPI/Swagger document. They were selected for an earlier study of contract–implementation divergence; 20 of them were chosen by metadata criteria alone. The sampled commits are Java 85, Go 48 and Kotlin 3.

### 3.2 Candidate commits and sampling
A **candidate** is a non-merge commit since 2023-01-01 that meets all of the following:
- it modifies production behaviour-path code (handlers, controllers, DTOs, validators, serializers, error mapping);
- it modifies no checked-in contract document;
- it has at most 400 changed lines in at most 8 files;
- it is not formatting-only;
- it is not authored by a bot.

The candidate pool was hash-frozen before any commit was read. Three candidates per repository were then drawn with a fixed seed. The pool held 18,590 candidates. Seven repositories had none and two had fewer than three, so the sample has 136 commits from 47 repositories. All 136 were packaged.

### 3.3 Packages and blinding
Each sampled commit becomes a package. The package contains:
- the diff;
- the full before and after versions of the touched files;
- the parent contract, projected to the affected operations.

Coders do not see the commit message, author, date, or later history.

### 3.4 Coding
Two GPT-family coders and two Claude-family coders code each item independently, using the same task text. Per item they record:
- whether the commit changes observable API behaviour;
- if so, the primary change kind (11 categories);
- the client impact (breaking or compatible);
- whether the parent contract specified the changed behaviour.

A final code is the agreement of the two coders of one family; disagreement becomes UNCLEAR. The GPT final codes are primary, and the Claude final codes serve as a cross-family check.

### 3.5 Mechanical measures
- **`annotation_touched`:** the diff edits a JVM contract annotation or a Go swagger comment. If it does not, a contract generated from code would not change either.
- **`spec_updated_90d`:** some contract document of the repository changes within 90 days after the commit.

### 3.6 Hypotheses and analysis
Pre-registered:
- **E-R3-1:** shares with Wilson and repository-cluster bootstrap CIs.
- **H-R3-1:** most breaking silent changes edit no contract annotation (one-sided binomial test).
- **H-R3-2:** most breaking changes to specified behaviour see no contract update within 90 days.
- **H-R3-3:** cross-family κ ≥ 0.6.

The scorer and its self-test were frozen before mining.

## 4. Results
*All numbers are from `plan/R3_RESULTS.md`, scored once.*

### 4.1 RQ1: prevalence
| Measure | GPT final codes | Claude final codes |
|---|---|---|
| Observable API behaviour change | 60/136 = 0.44 [0.36, 0.53] | 55/136 = 0.40 |
| Client-breaking change | 32/136 = 0.24 [0.17, 0.31] | 12/136 = 0.09 |

- **Reliability.**
  - Within-family κ for observable change is 0.90 (GPT) and 0.82 (Claude).
  - Across families, κ is 0.94 on the 102 items where both families decided (H-R3-3 PASS).
- **Robustness of the estimates.**
  - Repository-cluster bootstrap CIs are close to the Wilson CIs.
  - Leaving one repository out moves the breaking share by less than 0.01.

### 4.2 RQ2: kinds
- **Most frequent kinds:** response content, status or error mapping, response shape, side effects, and input validation.
- **Mostly breaking:** stricter input (6/6), changed response content (7/9) and changed status or error mapping (7/9).
- **Always compatible:** added response fields (response shape, 8/8) and looser input (5/5).

### 4.3 RQ3: visibility to contract generation
**H-R3-1 PASSES.** 29 of the 32 breaking changes edit no contract annotation or swagger comment (p = 1.3 × 10⁻⁶). Across all 60 observable changes, only 8 touched an annotation.

### 4.4 RQ4: documentation lag
**H-R3-2 is INSUFFICIENT.** Only 1 breaking change concerned behaviour the prior contract specified. Of the 60 changes, 56 altered behaviour the contract was silent about.

## 5. Discussion
- **Silent change is the norm, not the exception.** Roughly two in five behaviour-touching commits that leave the contract unchanged change observable behaviour.
- **These changes are invisible to document-based tooling.** That covers spec diff, and also contract generation from code: 91% of breaking changes touch no annotation.
- **The changes fall into what contracts do not say.** Error mapping, response values, validation and side effects are rarely specified. Contract-diff tools therefore cannot even in principle flag a conflict. Better contracts would shrink this blind spot. Behavioural evidence such as differential tests or recorded traffic is needed to cover it.
- **"Breaking" is a judgement.** Two LLM families agreed almost perfectly on *whether* behaviour changed, but differed by a factor of 2.7 on *how many* changes break clients. Tools that triage breaking impact automatically should expect this variance, and studies should validate impact labels with humans.

## 6. Threats to Validity
- **Construct.**
  - "Observable" is judged from code, not by executing the service.
  - Some changes are observable only under rare inputs.
  - Coders may over- or under-estimate reachability from HTTP operations.
- **LLM coders.**
  - Both coder families are LLMs. The cross-family κ is reported, and a human spot-check of 20 items is planned.
- **Sampling.**
  - Three commits per repository weight repositories equally, not by commit volume.
  - Only services with a checked-in OpenAPI document are included.
  - The window starts in 2023.
- **Visibility proxy.**
  - `annotation_touched` approximates what code-level contract generation would see. A generator may also infer some behaviour from types, or miss some annotations.
- **Documentation lag.**
  - `spec_updated_90d` is measured at repository level. It over-counts updates, which makes H-R3-2 conservative.

## 7. Conclusion
In 54 REST services, 44% of behaviour-changing commits that leave the OpenAPI document unchanged alter observable behaviour. 9–24% break clients, depending on the coder family. Almost none of these changes are visible to spec-diff tools or to contract generation from code, because they concern behaviour the contract never described. Detecting API breakage requires behavioural evidence.

## Data availability
The plan, scorer, task text, mining scripts, frozen pool hashes, sample, keys, codes and packages will be released in an anonymous archive. Upstream excerpts will carry their licences.

## References (verified 2026-11-17; see `notes/NOVELTY_VERIFIED.md`)
- Lercher, Bauer, Macho, Pinzger. AutoGuard: Reporting Breaking Changes of REST APIs from Java Spring Boot Source Code. 2025.
- Lercher, Glock, Macho, Pinzger. Microservice API Evolution in Practice: A Study on Strategies and Challenges. JSS 2024, doi 10.1016/j.jss.2024.112110.
- Jayasuriya, Terragni, Dietrich, Blincoe. Understanding the Impact of APIs Behavioral Breaking Changes on Client Applications. FSE 2024, doi 10.1145/3643782.
- Yasmin, Tian, Yang. A First Look at the Deprecation of RESTful APIs: An Empirical Study. ICSME 2020 (arXiv 2008.12808).
- Chen, Bi, Wang, Thongtanunam. Breaking Changes in Software Ecosystems: A Systematic Literature Review. arXiv 2605.24397, 2026.
