# R3 novelty: full-text verification addendum (written after the plan freeze; NOVELTY.md stays frozen)

## Full-text verification (2026-11-17, later the same day)
These entries are now verified from full text: arXiv HTML, or a local pdftotext of the PDF. They replace the ⚠️ status in §1.

- **Jayasuriya, Terragni, Dietrich, Blincoe (FSE 2024), doi 10.1145/3643782** (pdftotext, `lit/jayasuriya2024/`).
  - Data: Maven projects, 30,548 dependency updates under 8,086 artifacts. Out-of-date dependencies were updated automatically and the client test suites run.
  - Result: "2.30% of these updates had behavioral breaking changes that impacted client tests". Most occurred in non-major updates.
  - Effects taxonomy: Test Failures and Test Errors.
  - Scope: libraries only. No web APIs.
- **Yasmin, Tian, Yang, "A First Look at the Deprecation of RESTful APIs"** (arXiv 2008.12808; ICSME 2020 according to the conference PDF URL).
  - Data: APIs.guru, 2,224 specs of 1,368 APIs, compared with SwaggerDiff.
  - Result: "87.3% of RESTful API versions that introduced breaking changes do not provide any deprecation information in the previous version."
  - Scope: specification documents only.
- **Lercher, Glock, Macho, Pinzger, "Microservice API Evolution in Practice"** (arXiv 2311.08175; JSS 2024, doi 10.1016/j.jss.2024.112110). Based on 17 interviews in 11 companies.
  - "All participants (17/17) considered structural changes … breaking", but "only a few participants (5/17) identified behavioral changes … as harmful".
  - "the OpenAPI specification only describes the API structure, not the API behavior".
  - "providers miss tools for automatically extracting API changes from changes in their implementation".
  - "A dynamic API design improves structural backward compatibility but often shifts the problem, i.e., creates semantic breaking changes instead."
- **Chen, Bi, Wang, Thongtanunam, "Breaking Changes in Software Ecosystems: A Systematic Literature Review"** (arXiv 2605.24397, May 2026). Covers 97 primary studies, including Web APIs.
  - "Detection of syntactic breaks is comparatively mature, while behavioral breaks remain difficult to detect automatically."
  - "The main remaining gap is behavioral breaking changes that preserve syntactic interfaces."
  - On AutoGuard, which it includes as S30: "blind to semantic changes such as altered JSON response structures under the same status code".
  - **Unverified:** the "9 of 21" count (from a model summary). Do not cite it.

**Conclusion.** The gap stands, and the 2026 SLR states it directly. No primary study measures behavioural changes in REST services that leave the contract unchanged.
