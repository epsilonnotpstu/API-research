# Silent by Design? How Often REST Services Change Observable Behaviour Without Changing Their Contract

*Working draft v0.1 (2026-11-17). Written before any data was seen. The design follows the frozen plan `plan/R3_PLAN.md` (`plan/r3_plan_freeze.sha256`). Results sections are empty until the single scoring run.*

---

## Abstract
**[TODO after scoring]** One paragraph covering:
- motivation: spec-diff tools cannot see behaviour changes that leave the contract untouched;
- method: commits from 54 REST services, a frozen random sample, and blind two-family coding;
- prevalence of observable and breaking silent changes;
- the share invisible even to contract generation from code;
- documentation lag;
- implications for API change detection.

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
54 open-source REST services (Java, Kotlin, Go), each with a checked-in OpenAPI/Swagger document. They were selected for an earlier study of contract–implementation divergence; 20 of them were chosen by metadata criteria alone. **[TODO: per-language counts from T53]**

### 3.2 Candidate commits and sampling
A **candidate** is a non-merge commit since 2023-01-01 that meets all of the following:
- it modifies production behaviour-path code (handlers, controllers, DTOs, validators, serializers, error mapping);
- it modifies no checked-in contract document;
- it has at most 400 changed lines in at most 8 files;
- it is not formatting-only;
- it is not authored by a bot.

The candidate pool was hash-frozen before any commit was read. Three candidates per repository were then drawn with a fixed seed. **[TODO: pool size, sample size]**

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
**[TODO after the single scoring run]**

## 5. Discussion
**[TODO]**

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
**[TODO]**

## Data availability
The plan, scorer, task text, mining scripts, frozen pool hashes, sample, keys, codes and packages will be released in an anonymous archive. Upstream excerpts will carry their licences.

## References (verified 2026-11-17; see `notes/NOVELTY_VERIFIED.md`)
- Lercher, Bauer, Macho, Pinzger. AutoGuard: Reporting Breaking Changes of REST APIs from Java Spring Boot Source Code. 2025.
- Lercher, Glock, Macho, Pinzger. Microservice API Evolution in Practice: A Study on Strategies and Challenges. JSS 2024, doi 10.1016/j.jss.2024.112110.
- Jayasuriya, Terragni, Dietrich, Blincoe. Understanding the Impact of APIs Behavioral Breaking Changes on Client Applications. FSE 2024, doi 10.1145/3643782.
- Yasmin, Tian, Yang. A First Look at the Deprecation of RESTful APIs: An Empirical Study. ICSME 2020 (arXiv 2008.12808).
- Chen, Bi, Wang, Thongtanunam. Breaking Changes in Software Ecosystems: A Systematic Literature Review. arXiv 2605.24397, 2026.
