# Silent by Design? How Often REST Services Change Observable Behaviour Without Changing Their Contract

*Working draft v0.4 (2026-11-24; adds the pre-registered follow-up R3b §4.7; applies Codex review T59), target ICSME 2027 (see `paper/VENUE.md`). Design: frozen plan `plan/R3_PLAN.md`. Results: single scoring run (`plan/R3_RESULTS.md`). v0.3 applies the independent numeric and claim review `collab/reports/T55_report.md` (9 ERROR, 21 MINOR, all addressed).*

---

## Abstract
Spec-diff tools warn API clients only about changes visible in an OpenAPI document. We ask how often REST services change observable behaviour while leaving their contract files untouched. From a corpus of 54 open-source Java, Kotlin and Go services, we froze a pool of 18,590 commits since 2023 that modify behaviour-path code but no contract document. We drew a seeded sample of 136 commits from 47 repositories. Two GPT-family and two Claude-family LLM coders classified each commit blind to its message and history, under a pre-registered, hash-frozen protocol. By the primary (GPT) codes, 44% of the sampled commits (60/136; 95% CI 36–53%) change what some client can observe; 26 more remain unresolved. Depending on the coding model family, 9–24% are client-breaking: the two families agree on observable change (κ 0.94 on the 102 commits both decided) but not on breaking impact. Of the 32 breaking changes, 29 (91%; p = 1.3 × 10⁻⁶) edit no contract annotation, so by our annotation proxy even contract generation from code, as in AutoGuard, would likely miss them. Only 1 of the 60 changes concerned behaviour that the delivered parent-contract context specified. A pre-registered follow-up with full, untruncated contracts and quoted evidence confirms this: 2 of 60. Silent behavioural change is common, and it falls mostly where contracts say nothing. API change detection therefore needs behavioural evidence, not only document diffs.

## 1. Introduction
REST services evolve continuously, and their clients depend on behaviour they cannot see in the code. The usual safeguard is to diff the service's OpenAPI contract between versions. oasdiff and openapi-diff do this, and so does AutoGuard, which first generates the contract from code [Lercher et al. 2025]. A change that alters what an operation does but leaves the contract text unchanged is invisible to a document diff.

Practitioners know the problem only partly:
- In an interview study, all 17 participants treated structural changes as breaking, but only 5 of 17 saw behavioural changes as harmful [Lercher et al. 2024].
- The same participants noted that "the OpenAPI specification only describes the API structure, not the API behavior".
- A 2026 systematic review of 97 breaking-change studies concludes that "The main remaining gap is behavioral breaking changes that preserve syntactic interfaces" [Chen et al. 2026].

For libraries, behavioural breaking changes have been measured: 2.30% of Maven dependency updates had behavioural breaking changes that affected client tests [Jayasuriya et al. 2024]. For REST services, where the contract is the main means of communication with clients, we know of no such measurement.

We therefore ask how often REST services change observable behaviour without touching their contract, and what kind of changes these are.

- **RQ1 (prevalence).** Of the commits that change operation-implementing production code but no checked-in contract document, what share change observable API behaviour? What share do so in a client-breaking way?
- **RQ2 (kinds).** What kinds of observable change occur, and which kinds break clients?
- **RQ3 (visibility).** How many breaking silent changes edit no contract annotation, and so would likely stay invisible even to a contract generated from source annotations?
- **RQ4 (documentation lag).** When a breaking change alters behaviour the contract specified, is the contract updated within 90 days?

**Contributions.**
1. A measurement of silent behavioural changes in REST service histories, from a frozen random sample of 136 commits from 47 repositories of a 54-service corpus.
2. A closed taxonomy of silent change kinds, together with their client impact.
3. Evidence, through an annotation proxy, on how much code-level contract generation could recover.
4. A pre-registered, blind, two-model-family coding protocol and a replication package that re-scores every number byte for byte.

## 2. Background and Related Work
**Spec-based change detection.**
- oasdiff and openapi-diff compare two OpenAPI documents and report the differences, flagging those they classify as breaking.
- Yasmin et al. compared 2,224 specifications of 1,368 APIs from APIs.guru with such a diff tool (SwaggerDiff). They found that "87.3% of RESTful API versions that introduced breaking changes do not provide any deprecation information in the previous version" [Yasmin et al., ICSME 2020].
- These approaches see only what the document states.

**Contract generation from code.**
- AutoGuard generates OpenAPI descriptions of two versions of a Spring Boot service from source code and diffs them in CI [Lercher et al. 2025].
- Its authors note that OpenAPI descriptions "do not capture semantic changes".
- The 2026 review likewise characterises it as "blind to semantic changes such as altered JSON response structures under the same status code" [Chen et al. 2026].

**Behavioural breaking changes.**
- Jayasuriya et al. updated 30,548 Maven dependencies and ran client test suites. 2.30% of updates had behavioural breaking changes that affected client tests, mostly in non-major releases [Jayasuriya et al. 2024].
- The 2026 review finds that "Detection of syntactic breaks is comparatively mature, while behavioral breaks remain difficult to detect automatically" [Chen et al. 2026].
- Neither study measures web APIs from service histories.

**Practitioner view.** Lercher et al. report that providers "miss tools for automatically extracting API changes from changes in their implementation". They also observe that "A dynamic API design improves structural backward compatibility but often shifts the problem, i.e., creates semantic breaking changes instead" [Lercher et al. 2024].

**Contract–implementation divergence.** A companion study (under review; omitted for anonymity), on the same corpus, examines how divergences between a service and its contract are *repaired* once noticed. Here we study how such divergences *arise*, and how many affect clients without any contract-file change. A second companion study (under review; omitted for anonymity) asks the same visibility question for fixes of real access-control vulnerabilities.

## 3. Study Design
*(Summarised from the frozen plan `plan/R3_PLAN.md`; deviations in `plan/R3_DEVIATIONS.md`.)*

### 3.1 Corpus
The corpus has 54 open-source REST services in Java, Kotlin and Go:
- 34 come from an earlier mining study.
- 20 were added using repository metadata only, without reading any commit content. The criteria were:
  - a checked-in OpenAPI or Swagger document at HEAD, outside test and example paths;
  - Java, Kotlin or Go as the primary language;
  - at least 300 commits;
  - not archived and not a fork;
  - an OSI-approved licence.

Every service has a contract document *at its recorded HEAD*. Older parent commits may predate it: 29 of the 136 sampled commits have no checked-in contract document at their parent. These commits are kept. For them, "contract unchanged" means only that no contract file was modified.

The sampled commits are Java 85, Go 48 and Kotlin 3.

### 3.2 Candidate commits and sampling
A **candidate** is a commit that meets all of the following:
- It is a non-merge commit on the default branch's first-parent history, up to the recorded HEAD.
- Its committer date (UTC) is on or after 2023-01-01.
- After whitespace-only and content-unchanged rename files are dropped, at least one production behaviour-path file remains: handlers, controllers, DTOs, validators, serializers or error mapping.
- Those retained files have at most 400 added plus deleted lines, in at most 8 files.
- It modifies no detected contract document.
- Its author does not match the predefined bot patterns.

**Freezes and sampling.**
- The pool was hash-frozen before any candidate patch was inspected for a behavioural judgement. Discovery read files mechanically only, for classification.
- Up to three candidates per repository were then drawn with a fixed seed, and the sample was frozen.
- Packages were then built and frozen before any coder ran.

**Resulting sample.**
- The pool holds 18,590 candidates.
- Seven repositories had no candidates.
- Three had fewer than three: two had one each and one had two.
- The sample therefore has 44 × 3 + 1 + 1 + 2 = 136 commits from 47 repositories, and all 136 were packaged.

### 3.3 Packages and blinding
Each sampled commit becomes a package. A package contains:
- the diff;
- the full before and after versions of the touched files;
- the contract context at the parent commit.

The contract context takes one of five forms (Table 1).

**Table 1.** Contract context delivered with each package (136 commits).
| Contract context | Commits |
|---|---|
| Projected to the affected operations | 3 |
| Bounded document prefix | 6 |
| Whole document | 5 |
| Raw fallback: the first 2,000 redacted lines of the root contract documents, used when projection failed | 93 |
| No contract document at the parent | 29 |

**Blinding.**
- Coders never see the commit message, author, date or later history.
- Distinctive message fragments, identities and credentials are redacted from all delivered text.

### 3.4 Coding
Two GPT-family coders and two Claude-family coders code each item independently, using the same task text. Per item they record:
- whether the commit changes observable API behaviour (YES, NO or UNCLEAR);
- if it does, the primary change kind, from 11 categories;
- the client impact (BREAKING, COMPATIBLE or UNCLEAR);
- whether the parent contract context specified the changed behaviour.

A family's final code is the agreement of its two coders; disagreement becomes UNCLEAR. UNCLEAR items stay in the denominator. The GPT final codes are primary, and the Claude final codes serve as a cross-family check.

### 3.5 Mechanical measures
- **`annotation_touched`:** the diff edits a JVM contract annotation, such as OpenAPI or Swagger annotations, or a Go swagger comment. This is our proxy for visibility to contract generation from code. If no annotation is edited, an annotation-driven generator is unlikely to produce a different document. We did not run a generator.
- **`spec_updated_90d`:** some contract document of the repository changes within 90 days after the commit, observed up to the recorded HEAD.

### 3.6 Hypotheses and analysis
All four were pre-registered:
- **E-R3-1:** shares, with Wilson and repository-cluster bootstrap 95% CIs (2,000 resamples).
- **H-R3-1:** most breaking silent changes edit no contract annotation. Tested with a one-sided binomial test against 0.5.
- **H-R3-2:** among breaking changes to behaviour the parent contract *specified*, most see no repository-level contract update within 90 days. This needs at least 8 such changes. The plan's operation-level refinement of RQ4 is descriptive only.
- **H-R3-3:** cross-family κ on observable change is at least 0.6 on items both families decided, with at least 30 such items.

The scorer and its self-test were frozen before mining. Scoring ran once.

### 3.7 Process deviation
The GPT agent that wrote the mining scripts reached its usage limit midway. The supervising agent, which knew the hypotheses, completed mining with the same scripts. Before any coder ran, it made mechanical fixes:
- submodule handling;
- redaction thresholds;
- a raw contract fallback;
- path-scan rules;
- idempotent redaction.

No sampled commit was replaced, and no judgement step was involved. The GPT agent then reviewed the fixes and added tests. Superseded package builds were never opened by coders.

## 4. Results
*All numbers come from the single scoring run (`plan/r3_score_output.txt`). An independent recomputation (`collab/reports/T55_report.md`) reproduced them.*

### 4.1 RQ1: prevalence
**Table 2.** Shares of the 136 sampled commits, with Wilson 95% CIs for the primary codes.
| Measure | GPT final codes | Claude final codes |
|---|---|---|
| Observable API behaviour change | 60/136 = 0.44 [0.36, 0.53] | 55/136 = 0.40 |
| Client-breaking change | 32/136 = 0.24 [0.17, 0.31] | 12/136 = 0.09 |

- **Label distribution.** The GPT final codes for observable change are YES 60, NO 50 and UNCLEAR 26.
- **Reliability.**
  - Within-family κ for observable change is 0.90 (GPT) and 0.82 (Claude).
  - Across families, the two agree on 99 of the 102 items both decided: κ 0.94, so H-R3-3 passes.
- **Robustness.**
  - The repository-cluster bootstrap CIs, [0.35, 0.53] and [0.16, 0.31], are close to the Wilson CIs.
  - Leaving one repository out moves the breaking share by less than 0.01.

### 4.2 RQ2: kinds
**Figure 1.** Change kind and client impact of the 60 observable changes (GPT final codes). "Kind unclear" and "Impact unclear" mark coder disagreement.

- **Most frequent kinds:** response content (9), status or error mapping (9), response shape (8), side effects (7), and stricter input (6).
- **Kinds coded mostly or always as breaking:** stricter input (6/6), changed response content (7/9) and changed status or error mapping (7/9).
- **Kinds coded as always compatible:** all eight response-shape changes, which mainly add fields, and all five looser-input changes.

### 4.3 RQ3: visibility to contract generation
**H-R3-1 passes.** 29 of the 32 breaking changes edit no contract annotation or swagger comment (p = 1.3 × 10⁻⁶). Across all 60 observable changes, only 8 touched an annotation.

By our proxy, an annotation-driven generator such as AutoGuard would most likely report nothing for these 29 commits. We did not run a generator, so this is an estimate of its blind spot, not a measured recall.

### 4.4 RQ4: documentation lag
**H-R3-2 is INSUFFICIENT.** Only 1 breaking change concerned behaviour that the delivered parent-contract context specified; the plan requires at least 8. That one case did see a contract update within 90 days, so the no-update count is 0/1. Operation-level documentation lag could not be determined.

The reason lies in coverage. Of the 60 observable changes, the coders judged:
- 1 as specified;
- 56 as unspecified;
- 3 as unclear.

The changed behaviour was almost always behaviour the contract did not describe.

### 4.5 Illustrative cases
Three commits that both model families coded as breaking. The descriptions were checked against the diffs.
- **Stricter input (ReportPortal service-api, Java).** Project creation now trims the name, then rejects it if it is shorter than the minimum length. A rename request now stores the trimmed name.
  - A client that sent a short name padded with spaces now gets a validation error instead of a created project.
  - No contract annotation changed. The parent commit had no checked-in contract.
- **Status mapping (Microcks, Java).** A repository-import endpoint used to answer 201 Created for every request: for an empty file, for a non-JSON upload, and even after it had caught an import exception.
  - It now answers 400, 415 and 500 in those cases.
  - A client that relied on 201 now sees errors.
  - No contract annotation changed. The coders judged these responses unspecified in the delivered contract context.
- **Default value (Traccar, Java).** Two video endpoints declared the `channel` query parameter as a primitive `int`, so it silently defaulted to 0 when absent. It now defaults to 1 through `@DefaultValue("1")`.
  - Clients that omitted the parameter now receive a different channel's stream.
  - This is one of the three breaking changes that *did* touch an annotation, so a generator could expose it as a changed default value.

### 4.6 Where the model families disagree on impact (exploratory)
*Not pre-registered; computed by `paper/exploratory_r3.py` from the frozen codes.* 50 commits were coded as an observable change by both families. On these, the families' client-impact codes cross as follows (Table 3).

**Table 3.** Final client-impact codes of the two model families on the 50 commits both coded as an observable change (exploratory).
| GPT impact | Claude: breaking | Claude: compatible | Claude: unclear |
|---|---|---|---|
| Breaking (30) | 11 | 7 | 12 |
| Compatible (16) | 0 | 15 | 1 |
| Unclear (4) | 0 | 2 | 2 |

- **Claude is the more conservative family.** It never coded as breaking a commit that GPT coded as compatible.
- **Most of the gap comes from Claude's own disagreement.** For 12 of the 30 GPT-breaking commits, Claude's two coders disagreed, so the final code is UNCLEAR. For 7 more, both Claude coders said compatible.
- **Reading.** The 9–24% range therefore mixes two things: genuine disagreement about what counts as breaking, and lower within-family reliability of Claude on impact (κ 0.74 vs 0.85).

### 4.7 Follow-up with full contracts (pre-registered)
The coverage result rests on limited contract context: raw fallback for 93 items, and no document for 29. A pre-registered follow-up (`plan/R3b_PLAN.md`) therefore re-coded the 60 observable changes.

**Design of the follow-up.**
- **Material.** All contract files at the parent commit, untruncated: 149 documents.
- **Task.** Coders had to name the affected operation and decide whether the changed behaviour is specified. Every "specified" judgement needed a verbatim contract quote.
- **Coders.** The GPT-family coders were unavailable (usage limit), so both pairs are from the Claude family: Opus and Sonnet.

**Results.**
- **Coverage.** The affected operation is described in 30 of 60 cases, and 25 changes have no contract file at the parent.
- **H-R3-4.** The changed behaviour is specified in only 2 of 60 changes. 58 of 60 are unspecified (97%; CI 89–99%; p = 1.6 × 10⁻¹⁵; Sonnet pair 47/48). This confirms the 1-of-60 result.
- **Evidence.** All quotes occur verbatim in the contracts.
- **Agreement.** The two pairs agree on 47 of the 48 items both decided. κ is uninformative at this prevalence (the κ paradox).

## 5. Discussion
- **Silent observable change is common.** In 44% of the sampled commits (40% by the Claude codes), behaviour-path changes that modify no contract file change what a client can observe. That is a little over two in five.
- **Document-based tooling cannot see most of these changes.** Spec diff cannot, by construction. Contract generation from code would also miss them, by our proxy, because 91% of the breaking changes touch no annotation.
- **The changes fall where contracts are silent.** Error mapping, response values, validation and side effects were almost never specified in the contract context the coders saw. A contract-diff tool therefore has nothing to compare against. Richer contracts would shrink this blind spot. Behavioural evidence, such as differential tests or recorded traffic, is needed to cover it.
- **"Breaking" is a judgement.** Two LLM families agreed almost perfectly on *whether* behaviour changed. But they differed by a factor of 2.7 on *how many* changes break clients. The difference is one-directional (§4.6): Claude's breaking labels are almost a subset of GPT's. Tools that triage breaking impact automatically should expect this variance, and studies should validate impact labels with humans.
- **Implications for API providers.** Silent changes cluster in a few kinds: stricter validation, changed status or error mapping, and changed response values. Review checklists and contract-coverage goals can target these kinds first, for example by documenting error responses and validation rules in the contract.

## 6. Threats to Validity
- **Construct.**
  - "Observable" is judged from code, not by executing the service.
  - Some changes are observable only under rare inputs.
  - Coders may over- or under-estimate whether code is reachable from HTTP operations.
  - 26 of the 136 commits remain unresolved (UNCLEAR) by the primary codes.
- **Contract context.**
  - 93 items received the raw-fallback contract text instead of a projection, and 29 had no contract document at the parent.
  - Redaction sometimes removes whole lines, and truncation can cut context.
  - Judgements of `contract_specified` in the main coding are therefore approximate.
  - The pre-registered follow-up with full contracts and quoted evidence (§4.7) confirms the coverage result: 2/60 specified. Its coders all come from one model family.
- **LLM coders.**
  - All coders are LLMs.
  - Each Claude batch of 10–14 items took 31–67 s, so those coders may have read mostly the diffs (an audit inference, not an observation).
  - We report the cross-family κ. A human spot-check of 20 items, stratified by GPT breaking impact, is prepared and will be reported separately.
- **Blinding.**
  - The audit found no reads outside the packages.
  - Very short commit-message fragments are not redacted. If such a fragment also appears in the source, it could hint at intent.
- **Sampling.**
  - Up to three commits per repository reduces the dominance of high-volume repositories. Three repositories contributed fewer.
  - Only services with a contract document at HEAD are included.
  - The window starts in 2023.
  - Pure-submodule commits that look like behaviour changes could have entered the pool, but none was sampled.
- **Visibility proxy.**
  - `annotation_touched` approximates what code-level contract generation would see. A generator may also infer some behaviour from types, or miss some annotations.
- **Documentation lag.**
  - `spec_updated_90d` is measured at repository level, which over-counts updates.
  - It is right-censored at the recorded HEAD. In a post-hoc check (`paper/exploratory_r3.py`), 15 commits had less than 90 days of follow-up, and for 5 of them the field is false. H-R3-2's verdict does not depend on these commits.
- **Process.** Mining was completed by the hypothesis-aware supervising agent, using mechanical fixes only (§3.7).

## 7. Conclusion
We sampled 136 commits from 47 REST services in which behaviour-path code changes but no contract file does. In 44% of them, observable behaviour changes. Depending on the coding model family, 9–24% of all sampled commits break clients. Almost none of these changes would show up in a spec diff. By an annotation proxy, most would also escape contract generation from code, because they concern behaviour the contract did not describe. Detecting API breakage requires behavioural evidence.

## Data availability
An anonymised replication archive accompanies this submission ([anonymous link to be added]). It contains:
- the frozen plan, the scorer and its self-test;
- the coder task text;
- the mining scripts;
- the frozen pool and sample hashes;
- the key;
- all blind packages with the upstream licence of every excerpt;
- all codes;
- one script that verifies the three freezes and re-scores every number byte for byte.

## Disclosure of AI use
- **LLMs as instruments.** The study uses LLMs as measurement instruments. The GPT-family coders were `gpt-6.1-sol` via the Codex CLI, at high reasoning effort. The Claude-family coders were Claude Sonnet subagents. Their role, prompts and outputs are part of the method (§3.4) and of the archive.
- **LLM assistants.** The authors also used LLM assistants (Claude and Codex) to:
  - write mining and analysis scripts (§3);
  - check the paper's numbers against the scorer output (§4);
  - draft and edit the text of all sections.
- **Author responsibility.** The authors reviewed all generated content and take responsibility for it.

## References (verified 2026-11-17/18; see `notes/NOVELTY_VERIFIED.md`)
- Lercher, Bauer, Macho, Pinzger. AutoGuard: Reporting Breaking Changes of REST APIs from Java Spring Boot Source Code. 2025.
- Lercher, Glock, Macho, Pinzger. Microservice API Evolution in Practice: A Study on Strategies and Challenges. JSS 2024, doi 10.1016/j.jss.2024.112110.
- Jayasuriya, Terragni, Dietrich, Blincoe. Understanding the Impact of APIs Behavioral Breaking Changes on Client Applications. FSE 2024, doi 10.1145/3643782.
- Yasmin, Tian, Yang. A First Look at the Deprecation of RESTful APIs: An Empirical Study. ICSME 2020 (arXiv 2008.12808).
- Chen, Bi, Wang, Thongtanunam. Breaking Changes in Software Ecosystems: A Systematic Literature Review. arXiv 2605.24397, 2026.
