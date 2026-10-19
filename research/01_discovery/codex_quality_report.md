# Codex discovery quality report

## Counts

- Unique qualified candidates: **60**.
- Bibliographically verified: **60** (57 DOI records reconciled through OpenAlex/Crossref or official venue evidence; 3 arXiv-only records verified through OpenAlex plus reachable arXiv records).
- Recent papers (2023–2026): **32**.
- Explicitly marked foundational papers: **12**.
- Peer-reviewed publications: **57**.
- Preprints: **3**.
- Records with abstract-level evidence: **52**; metadata-only: **8**.
- Verified direct PDF links (HTTP 200 and PDF content type, including the corrected official NDSS PDF): **21**.
- Candidate PDF URLs present but blocked/inconclusive/non-PDF: **17**.
- No direct PDF identified in queried metadata: **22**.

## Publication-year distribution

| Year | Count |
|---:|---:|
| 2014 | 2 |
| 2015 | 1 |
| 2017 | 1 |
| 2018 | 2 |
| 2019 | 4 |
| 2020 | 2 |
| 2021 | 6 |
| 2022 | 10 |
| 2023 | 11 |
| 2024 | 12 |
| 2025 | 8 |
| 2026 | 1 |

## Research-area distribution

| Area | Count |
|---|---:|
| API testing, automated testing, and fuzzing | 18 |
| API security and authorization | 4 |
| API specification inference, generation, and validation | 6 |
| API documentation and usability | 6 |
| API evolution and breaking changes | 7 |
| GraphQL and alternative API architectures | 5 |
| API discovery, recommendation, composition, and reuse | 5 |
| Microservice reliability, testing, and observability | 5 |
| LLM- and AI-assisted API engineering | 4 |

## Verification assessment

All 60 records have a resolved bibliographic identity. “Verified” here means that title, authorship, year/venue, and identifier were reconciled through the cited metadata sources; it does **not** mean the paper's scientific claims were independently reproduced or that the full text was read. Eight records lacked an OpenAlex abstract and therefore remain metadata-only for contribution screening. Several Crossref/OpenAlex year differences reflect online-first versus issue publication dates and are recorded row by row.

## Duplicate handling

- DOI strings were normalized case-insensitively and no duplicate DOI remains.
- When a peer-reviewed version and arXiv copy represented the same work, the peer-reviewed DOI is the primary identity and the arXiv identifier/PDF is recorded as an access route.
- Three works remain arXiv-only because no verified peer-reviewed version was found during this pass.
- Similarly named workshop/tool papers were retained only when they represented distinct studies (for example, Morest's primary ICSE paper rather than the separate industry-practice item).

## Potential bias and inadequate representation

- The set favors English-language papers indexed by OpenAlex/Crossref and established software-engineering venues.
- Testing/fuzzing is intentionally overrepresented because it is a mature, technically dense API research cluster.
- API authorization/business-logic security, API gateways, performance/scalability, gRPC/event-driven APIs, and API observability are underrepresented.
- Recommendation/composition papers rely heavily on registry-style offline datasets; production evidence may be limited.
- Citation counts favor older publications and were used only as a secondary inclusion signal.
- Search-result ranking can suppress less-cited work and non-Western venues.
- Abstract-only screening may miss negative results, threats to validity, artifact limitations, or contradictions found in full text.

## Corrections/retractions

No retraction was surfaced in the queried OpenAlex/Crossref metadata. This is not a definitive retraction audit. One DOI metadata inconsistency was found and documented for the NDSS 2025 GPTAid paper; the official/arXiv-supported DOI is used in the catalog.
