# R3 novelty check (E0), 2026-11-17, Claude
**Topic.** Silent behavioural breaking changes in REST APIs: changes to an operation's observable behaviour, made in the implementation, that leave the API contract unchanged and that schema or spec-diff tools therefore cannot see.

**Method.**
- Web searches (standard and extended), run on 2026-11-17. The queries are listed in §3.
- AutoGuard was read in full from its PDF: `lit/autoguard/` (pdftotext).
- The other entries were assessed from abstracts and search snippets only, marked ⚠️, and need a full read before they are cited.

## 1. Closest work
| Work | What it does | Why it does not cover R3 |
|---|---|---|
| **AutoGuard**: Lercher, Bauer, Macho, Pinzger (2025, tool paper; read in full) | Generates OpenAPI descriptions from Spring Boot source for two versions (AutoOAS), diffs them with OpenAPI-diff, and reports breaking changes in CI | Detects only changes visible in the generated OpenAPI. Its stated limitation: OpenAPI descriptions "do not capture semantic changes, e.g., changed parameter dependencies". No empirical prevalence study |
| ⚠️ Jayasuriya, Terragni, Dietrich, Blincoe, "Understanding the Impact of APIs Behavioral Breaking Changes on Client Applications", FSE 2024 (doi 10.1145/3643782) | About 2.3% of 30,548 library dependency updates broke client tests through behavioural changes; a taxonomy | Library (Maven) APIs, not web APIs. Measured through client test suites. Gives the method precedent and the "behavioural BC" terminology |
| ⚠️ Yasmin, Tian, Yang, "A First Look at the Deprecation of RESTful APIs", ICSME 2020 (arXiv 2008.12808) | APIs.guru spec histories; breaking changes introduced without deprecation | Spec-diff only. It cannot see changes that leave the spec unchanged |
| ⚠️ Lercher et al., "Microservice API Evolution in Practice" (arXiv 2311.08175; catalogue P020) | Interviews: only 5/17 practitioners saw behavioural changes as harmful | Qualitative. Motivates R3 |
| ⚠️ SLR, "Breaking Changes in Software Ecosystems" (arXiv 2605.24397, 2026) | Behavioural changes appear in 9 of 21 papers on the nature of breaking changes. They "evade static detection" | Ecosystem libraries. Confirms that behavioural BCs are under-studied |
| ⚠️ Regression study of an evolving healthcare IoT REST API (arXiv 2410.12547) | Regressions across releases of one API | Single system, test-based, not about contract visibility |
| oasdiff, openapi-diff, brake (tools) | Spec-to-spec diff with 100+ breaking-change checks | By construction, blind to unchanged specs |

## 2. Gap (provisional)
No study found that:
1. measures, on REST service histories, how often implementation changes alter observable API behaviour while the contract stays unchanged;
2. classifies those changes by kind and by client impact (breaking or compatible);
3. measures how many would be visible even to a contract generated from code (AutoGuard-style), as opposed to a checked-in contract.

**Link to R1 (different research question).** R1 asked which side gets repaired once a divergence is fixed. R3 asks how divergences that affect clients arise, and how many of them are invisible.

## 3. Queries run
- "behavioral breaking changes REST API undocumented OpenAPI implementation change empirical study" (extended)
- "silent breaking changes web API backward compatibility mining git history OpenAPI specification drift 2025 2026" (extended)
- "oasdiff limitations behavioral changes not visible in API specification study"
- "\"behavioral breaking changes\" web API OR REST API detection study client impact" (extended)
- "arXiv 2026 REST API evolution undocumented behavior change implementation without specification update empirical" (extended)

## 4. To do before submission
- Read the ⚠️ items in full.
- Search ACM DL, IEEE Xplore and Semantic Scholar for "REST API" × ("behavioral change" | "semantic change" | "silent") for 2023–2026.
