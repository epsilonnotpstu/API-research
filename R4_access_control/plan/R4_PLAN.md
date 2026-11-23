# R4 plan: Could a contract-driven black-box tester find it? Real access-control vulnerabilities in OpenAPI-described REST services

Pre-registered by Claude (supervisor-delegated), 2026-11-23, before any advisory text, diff or contract was read. This plan, the scorer (`plan/score_r4.py`), its self-test (`plan/test_score_r4.py`) and the coder task (`plan/TASK_R4.md`) are hash-frozen in `plan/r4_plan_freeze.sha256` before mining. Deviations go to `plan/R4_DEVIATIONS.md`, and scoring runs once.

**Pre-freeze feasibility probe.** Before this freeze, one metadata-only count was run:
- The query asked for GitHub reviewed advisories, ecosystems maven and go, with access-control CWEs.
- Result: 866 maven advisories (413 with a commit reference, 174 repositories) and 1,057 go advisories (580 with a commit reference, 198 repositories).
- Only identifiers, reference counts and repository URLs were seen. No advisory text, diff or contract was read.

## 1. Motivation and gap
REST security testers are evaluated on seeded or vulnerable-by-design services:
- Access-policy oracles found missed-check faults only in an injected service, none in real APIs (P015).
- BOLA detectors and LLM-based repair benchmarks study real access-control vulnerabilities, but none of them asks whether the vulnerability is visible to, or detectable from, the API's **contract**.

Black-box REST testers (Schemathesis, RESTler, EvoMaster, the P015 oracles) take only the OpenAPI document and credentials as input. We measure, on real vulnerabilities in OpenAPI-described services:
- what a black-box tester would need in order to expose them;
- whether the contract even contains the information needed to recognise the violation.

This is gap G5 in `research/05_research_clusters/research_gap_register.csv`.

## 2. Research questions
- **RQ1 (kinds).** Which kinds of access-control vulnerabilities occur in OpenAPI-described Java/Kotlin/Go REST services? The kinds are object-, function-, property-level, missing authentication and tenant isolation.
- **RQ2 (test setup).** What minimal black-box setup exposes each vulnerability? The setups are: an anonymous request, one principal, two principals of the same role, or two roles. Is the violation observable through HTTP responses?
- **RQ3 (contract information).** Is the vulnerable operation described in the contract at the vulnerable version? Does the contract declare a security requirement for it? Is the violated access rule stated in, or derivable from, the contract?
- **RQ4 (fix visibility).** Does the fix change the contract document or a contract annotation, so that a spec-diff consumer would learn of it? Where is the fix located, and does it add a test?

## 3. Population, pool and sample (mechanical; implemented by `mining/` scripts; no judgement)
**Source.** GitHub Advisory Database, through the REST API `/advisories`, with these filters:
- `type=reviewed`;
- ecosystems `maven` and `go`;
- CWE in {284, 285, 639, 862, 863, 915, 269, 266, 425, 566, 708, 306}.

The query and all responses are cached and hashed.

**Fix commit.**
- **Candidate references.** A reference URL of the form `https://github.com/{owner}/{repo}/commit/{sha40 or shorter hex}`.
- **Repository match.** Prefer references whose `{owner}/{repo}` equals the advisory's `source_code_location` repository; otherwise use references in the order listed.
- **Choice.** The fix commit is the first candidate that resolves through the API (`/repos/{o}/{r}/commits/{sha}`).
- **Parent.** The parent is its first parent.
- **Exclusions.** Advisories without a resolvable commit are excluded, with reason `NO_COMMIT`.

**Eligibility.** All of the following must hold:
1. **Contract present.** The parent tree (`/git/trees/{parent}?recursive=1`) contains a checked-in OpenAPI/Swagger document. That means a path whose file name contains `openapi` or `swagger` (case-insensitive), with extension `.yaml`, `.yml` or `.json`, and no path segment in {test, tests, testdata, example, examples, sample, samples, fixture, fixtures, vendor, node_modules, third_party, e2e, mock, mocks}. This is the T50 detection rule. Otherwise the reason is `NO_CONTRACT_AT_PARENT`.
2. **Source change.** The fix commit modifies at least one non-test Java/Kotlin/Go source file. That means `.java`, `.kt` or `.go`, outside test paths, and not a `_test.go` file or a file under `src/test/`. Otherwise the reason is `NO_SOURCE_CHANGE`.
3. **Size.** At most 2,000 added plus deleted lines over those source files. Otherwise the reason is `TOO_LARGE`.

**Dedup.** Advisories that share a fix commit become one item. The item keeps the lowest GHSA id and lists the others.

**Pool freeze.** The eligible pool (advisory ids, repositories, fix and parent SHAs, mechanical fields) is written to `mining/pool.json` and hash-frozen in `mining/pool_freeze.json` before any package is built or any advisory text is shown to a coder.

**Sample.**
- If the pool holds at most 160 items, all are taken.
- Otherwise, at most 4 items per repository are taken, with `random.Random("r4:" + repo).sample(sorted(item ids), min(4, n))`.
- If more than 160 items remain after that, a seeded sample of 160 is drawn with `random.Random("r4-sample-20261123").sample(sorted(ids), 160)`.

The sample is hash-frozen in `mining/sample_freeze.json`.

## 4. Packages and blinding
Each item folder `Annn/` (ids are shuffled with a stored salt) contains:
- **`item.md`.** It holds:
  - the repository name and language;
  - the advisory summary and description (redacted of URLs to commits and pull requests, and of reporter names);
  - the CWE ids;
  - the list of touched files.
- **`diff.patch`.** The fix commit's diff for source files only, without commit message, author or date.
- **`before/` and `after/`.** The touched source files (non-test), up to 20 files.
- **`contract/`.** The contract documents at the **parent** commit. If there are several, the largest three by size, each truncated to its first 3,000 lines. A `contract/INDEX.md` lists all contract paths with their sizes.

Privacy and secret scans are run as in R3: emails, credentials, and tokens with known prefixes are redacted. Coders do not see the commit message, the author, dates, or later history. The task text does not mention the hypotheses.

## 5. Coding (closed scheme; `plan/TASK_R4.md`)
**Coders.**
- Two GPT-family coders (G1 and G2; Codex CLI, `gpt-6.1-sol`, high effort) code the package `r4_blind`.
- Two Claude-family coders (H1 and H2; fresh-context Claude Sonnet subagents) code the same items in batches `r4_kb*`.

**Fields per item:**
- **`ac_relevant`:** YES, NO or UNCLEAR. Is this an access-control flaw (who may perform which operation on which object or property, or whether an operation requires authentication at all) reachable through an HTTP operation of this service? Flaws in cryptography, token validation, session fixation, SSRF, injection, DoS or client libraries are **NO**.
- **The remaining fields** apply only if `ac_relevant` is YES; otherwise they are NA:
  - **`ac_kind`:**
    - OBJECT_LEVEL: acting on another principal's object of the same type (BOLA/IDOR).
    - FUNCTION_LEVEL: invoking an operation reserved for another role (BFLA).
    - PROPERTY_LEVEL: reading or writing object properties beyond one's rights (mass assignment, excessive exposure).
    - MISSING_AUTHENTICATION: an operation callable without any credentials although it should require them.
    - TENANT_ISOLATION: crossing an organisation, tenant, realm or project boundary.
    - OTHER.
  - **`principals_needed`:** the minimal black-box setup in which the violation shows:
    - NONE: an anonymous request suffices;
    - ONE: a single authenticated principal suffices;
    - TWO_SAME_ROLE;
    - TWO_ROLES;
    - UNCLEAR.
  - **`observable_via_http`:** YES if the violation shows in HTTP responses (status or body of this call or a later call); NO if it is only visible through side channels; UNCLEAR.
  - **`contract_operation`:** PRESENT, ABSENT, NO_CONTRACT or UNCLEAR. Is the vulnerable operation described in the parent contract?
  - **`contract_security`:** DECLARED, NOT_DECLARED, NA or UNCLEAR. Does the contract declare a security requirement for that operation, either at operation level or globally? NA if the operation is not PRESENT.
  - **`policy_in_contract`:** YES, NO or UNCLEAR. Does the contract state, or let one derive, the violated rule? Examples: an ownership statement, a role or scope required for the operation, a property marked read-only, a tenant parameter whose binding is stated. A bare security scheme without the rule is NO.
  - **`fix_location`:**
    - HANDLER: controller or route method;
    - MIDDLEWARE_FILTER: filter, interceptor, security configuration or route-level guard;
    - SERVICE_LOGIC;
    - DATA_QUERY: owner or tenant scoping in a query or repository;
    - MODEL_BINDING: DTO field allow-list or ignore;
    - OTHER.
- **Also recorded:** `confidence` (1–3), `locators` and `rationale` (at most 40 words).

**Final codes.** A family's final code is the field-wise agreement of its two coders; disagreement becomes UNCLEAR. Dependent fields count only when both coders said `ac_relevant` = YES. The GPT final codes are primary, and the Claude final codes are a cross-family check.

## 6. Mechanical measures (mining, no judgement)
- **`fix_touches_contract`:** the fix commit modifies a contract document, by the rule of §3.1.
- **`fix_touches_annotation`:** the fix diff adds or removes a line containing a JVM contract annotation, from R3's `annotation_patterns.json` plus `SecurityRequirement`, `SecurityScheme` and `SecurityRequirements`, or a Go swagger comment (R3 pattern).
- **`fix_silent`:** neither of the two above holds.
- **`test_in_fix`:** the fix commit adds or modifies a test file.
- **`fix_lines`:** added plus deleted lines in source files.

## 7. Hypotheses and analysis (all on GPT final codes unless stated; α = 0.05, one-sided where stated)
- **E-R4-1 (descriptive).** Distributions of `ac_kind`, `principals_needed`, `fix_location` and the contract fields over AC-relevant items, with Wilson 95% CIs and repository-cluster bootstrap CIs (2,000 resamples, seed 1).
- **H-R4-1 (multi-principal).**
  - Claim: among AC-relevant items with `principals_needed` decided (not UNCLEAR), more than half need at least two principals (TWO_SAME_ROLE or TWO_ROLES).
  - Test: one-sided binomial against 0.5.
  - Minimum: at least 20 decided items, else INSUFFICIENT.
- **H-R4-2 (silent fixes).**
  - Claim: among AC-relevant items, more than half have `fix_silent` = true.
  - Test: one-sided binomial against 0.5.
  - Minimum: at least 20 items.
- **H-R4-3 (policy absent from the contract).**
  - Claim: among AC-relevant items with `contract_operation` = PRESENT and `policy_in_contract` decided, more than half have `policy_in_contract` = NO.
  - Test: one-sided binomial against 0.5.
  - Minimum: at least 20 items.
- **H-R4-4 (reliability).**
  - Claim: cross-family κ on `ac_kind` is at least 0.6.
  - Basis: items where both families' final `ac_relevant` is YES and both `ac_kind` are decided.
  - Minimum: at least 30 such items, else INSUFFICIENT.
- **Within-family κ.** Reported per field.
- **Exploratory, labelled as such:**
  - `principals_needed` × `contract_security`;
  - `ac_kind` × `fix_location`;
  - the per-ecosystem breakdown;
  - leave-one-repository-out ranges for H-R4-1 to H-R4-3.

## 8. Threats (planned)
- **Sampling.** Advisories are a biased sample of vulnerabilities (disclosed and reviewed ones only). The CWE filter may miss mislabelled advisories. Two ecosystems only.
- **Static judgement.** Coders judge from code and contract, not by executing exploits.
- **Contract context.** Contract documents are truncated to 3,000 lines each.
- **Advisory text.** Coders see the advisory text, which may state the setup, so coders and advisory are not independent judgements of the setup.
- **LLM coders.** A human spot-check of 20 items (stratified by `ac_kind`) is planned after scoring and reported separately.
