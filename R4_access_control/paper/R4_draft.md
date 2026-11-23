# What Would a Black-Box Tester Need? Real Access-Control Vulnerabilities in OpenAPI-Described REST Services

*Working draft v0.1 (2026-11-23). Design: frozen plan `plan/R4_PLAN.md`. Results: TODO after the single scoring run.*

---

## Abstract
TODO after scoring.

## 1. Introduction
Broken access control is the most critical class of API vulnerability: object-level authorization ranks first in the OWASP API Security Top 10. Automated REST testers mostly work black-box:
- Schemathesis, RESTler and EvoMaster take an OpenAPI document and credentials, generate requests, and judge responses with oracles.
- Recent tools add access-policy oracles that compare the responses of different users.

These tools are evaluated almost exclusively on seeded faults or vulnerable-by-design services. In one evaluation, missed-check faults were found only in a service with injected faults, and none in real APIs. Recent fuzzing work names the core obstacle directly: broken access control "is underexplored in automated testing due to key challenges: the lack of reliable oracles and the difficulty of generating semantically valid attack requests" (arXiv 2507.15984).

The usual answer to the oracle problem is the contract: the OpenAPI document says which operations exist and which security schemes protect them. But does the contract carry the information needed to recognise a real access-control violation? And what test setup would a black-box tester need to provoke one at all? We answer both questions on real, published, fixed vulnerabilities in open-source REST services that ship an OpenAPI document:

- **RQ1 (kinds).** Which kinds of access-control vulnerabilities occur?
- **RQ2 (test setup).** What minimal black-box setup exposes them, by number and roles of principals, and is the violation observable through HTTP responses?
- **RQ3 (contract information).** Does the contract describe the vulnerable operation, declare a security requirement for it, and state the violated rule?
- **RQ4 (fix visibility).** Does the fix change the contract, and where in the code is it made?

**Contributions.**
1. A frozen, reproducible sample of real access-control advisories for Java, Kotlin and Go REST services, each linked to its fix commit and to the contract at the vulnerable version.
2. Measurements of the black-box setup these vulnerabilities require, and of the contract information available to detect them.
3. Evidence on whether such fixes are visible to contract consumers.
4. A pre-registered, two-model-family blind coding protocol and a replication package.

## 2. Background and Related Work
**Black-box REST testing and security oracles.**
- Black-box testers generate requests from an OpenAPI document. Their default oracles detect crashes (5xx) and schema violations.
- Access-policy oracles go further and compare responses across principals.
- Evaluations rely on seeded faults or vulnerable-by-design services such as Juice Shop.

**Real access-control vulnerabilities.**
- Huang et al. detect BOLA in database-backed applications statically (CCS 2024).
- BACFuzz fuzzes PHP web apps for BOLA and BFLA with LLM-guided parameter selection and runtime feedback (arXiv 2507.15984).
- BOLAZ analyses the data flow of resource identifiers in RESTful APIs to prevent horizontal privilege escalation (arXiv 2507.02309).
- IDORacle mediates SQL sinks at runtime in Java (arXiv 2609.12426).
- A taxonomy of 107 HackerOne reports finds that 84 were confirmed BOLA, of which 11.9% are vertical privilege failures (arXiv 2605.25865).
- BAC-Bench collects 46 real broken-access-control vulnerabilities from six web applications to benchmark LLM repair (arXiv 2610.34290).

None of these works asks what a contract-driven black-box tester would need for real vulnerabilities, or whether the contract carries the violated rule.

**Contracts and silent change.** A companion study (under review; omitted for anonymity) finds that behavioural changes in REST services mostly leave the contract untouched. Here we ask the same question for security fixes.

## 3. Study Design
*(Summarised from the frozen plan `plan/R4_PLAN.md`.)*

### 3.1 Advisories and fix commits
We query the GitHub Advisory Database for reviewed advisories in the Maven and Go ecosystems with access-control-related CWEs: 284, 285, 639, 862, 863, 915, 269, 266, 425, 566, 708 and 306.

For each advisory, we take as the fix the first commit reference that resolves. References to the advisory's own source repository come first. The vulnerable version is the fix's first parent.

### 3.2 Eligibility, pool and sample
An advisory is eligible if all of the following hold:
- **Contract present.** The repository has a checked-in OpenAPI/Swagger document at the vulnerable version, outside test and example paths.
- **Source change.** The fix changes non-test Java, Kotlin or Go source.
- **Size.** The fix has at most 2,000 changed source lines.

Advisories that share a fix commit are merged. The pool is hash-frozen before any package is built. We take all items, up to 160, with at most four per repository by a seeded draw.

**Resulting counts.**
- **Query.** It returned 2,025 advisories; 53 were withdrawn.
- **Fix commits.** 945 advisories cite no fix commit, and one commit could not be fetched. 1,026 resolved to a fix commit.
- **Pool.**
  - 831 fixes had no checked-in contract at the vulnerable version.
  - 9 touched no non-test Java/Kotlin/Go source.
  - 1 exceeded 2,000 changed lines.
  - 9 duplicates were merged.
  - The eligible pool holds 176 items from 70 repositories (Go 136, Maven 40).
- **Sample.** The per-repository cap gives 138 items from 70 repositories.

### 3.3 Packages and blinding
Each item package contains:
- the advisory summary and description, with links and reporter credits removed;
- the fix diff;
- the touched files before and after the fix;
- the contract documents at the vulnerable version, truncated to 3,000 lines each.

Coders do not see the commit message, the author, dates, or later history. The task text does not state the hypotheses.

### 3.4 Coding
Two GPT-family coders and two Claude-family coders code every item independently with the same task text. The coding scheme is closed:
- whether the vulnerability is an access-control flaw reachable through HTTP;
- its kind: object-, function- or property-level, missing authentication, tenant isolation, or other;
- the minimal black-box setup: anonymous, one principal, two principals of the same role, or two roles;
- whether the violation is observable via HTTP;
- whether the contract describes the operation;
- whether the contract declares security for it;
- whether the contract states the violated rule;
- the fix location.

A family's final code is the agreement of its two coders; disagreement becomes UNCLEAR. The GPT codes are primary.

### 3.5 Mechanical measures
- **Fix touches the contract:** the fix modifies a contract document.
- **Fix touches an annotation:** the fix adds or removes a contract annotation, including security annotations, or a swagger comment.
- **Silent fix:** neither of the two above.
- **Test in fix:** the fix adds or modifies a test.

### 3.6 Hypotheses
All four are pre-registered with one-sided binomial tests against 0.5 and a minimum of 20 items:
- **H-R4-1:** most vulnerabilities need at least two principals to expose.
- **H-R4-2:** most fixes are silent.
- **H-R4-3:** when the contract describes the operation, it usually does not state the violated rule.
- **H-R4-4:** cross-family κ on the vulnerability kind is at least 0.6, on at least 30 items.

## 4. Results
TODO

## 5. Discussion
TODO

## 6. Threats to Validity
TODO (plan §8, plus deviations and the audit)

## 7. Conclusion
TODO

## Data availability
An anonymised replication archive will accompany the submission.

## Disclosure of AI use
TODO (as in R3).
