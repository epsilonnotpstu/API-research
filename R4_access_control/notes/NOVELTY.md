# R4 novelty (pre-freeze, 2026-11-23; based on search-result summaries and abstracts; full texts not yet read ⚠️)

**Gap G5 (research_gap_register.csv): "Real (non-seeded) REST API security benchmarks for BOLA/mass assignment/access policy".** Status: Supported, novelty risk Medium.

Evidence in our corpus:
- P015: missed-check faults were found only in an injected SUT, none in real APIs.
- P014: validated on Juice Shop plus one OSS service.
- P012: seeded faults only.

## Closest related work (found 2026-11-23)
| Work | What it does | Why R4 differs |
|---|---|---|
| Detecting BOLA vulnerabilities in database-backed applications (ACM CCS 2024, doi 10.1145/3658644.3690227; title per search result) | Analyses 101 real BOLA vulnerabilities from CVE and Huntr (per search summary ⚠️) and proposes a static detector | Covers BOLA only. Does not ask about contract visibility or about the black-box setup a contract-driven tester would need |
| arXiv 2605.25865, BOLA in the wild: taxonomy of 107 HackerOne reports | Taxonomy of bug-bounty BOLA reports (families, action type, vertical privilege share 11.9%) | Based on reports, not code or fix commits. No contract and no fix analysis |
| arXiv 2610.34290, BAC-Bench: LLM repair of broken access control (46 real vulnerabilities, 6 web apps) | Repair benchmark with a repair-strategy framework (Position, Coverage, Mechanism, Content) | Studies repair, not detection or contract information. Our `fix_location` relates to its Position dimension |

## R4's distinct questions
On real advisories in **OpenAPI-described** services:
1. What black-box setup (number and roles of principals) a tester would need.
2. Whether the contract describes the operation, declares security, and states the violated rule.
3. Whether the fix is visible in the contract. This links to the companion study of silent behavioural changes.

To do after scoring: full-text read of the CCS 2024 paper and of 2610.34290, and a search for "OpenAPI security requirement coverage" studies.
