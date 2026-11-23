# R4 novelty: verification addendum (after the plan freeze; NOVELTY.md stays frozen)

## 2026-11-23, metadata and abstracts (arXiv API, Crossref)
- **Huang, Shi, Lu, Li, Meng, Li. "Detecting Broken Object-Level Authorization Vulnerabilities in Database-Backed Applications." ACM CCS 2024, doi 10.1145/3658644.3690227.**
  - Title, authors and venue verified via Crossref. The ACM page returned 403, and Crossref has no abstract.
  - ⚠️ The "101 real-world BOLA vulnerabilities from CVE and Huntr" figure comes from a search summary only. **Do not cite it until it is read.**
- **BACFuzz (arXiv 2507.15984; Dharmaadi, Alhanahnah, Pham, Mohsen, Turkmen; under review).**
  - A gray-box fuzzer for BOLA and BFLA in PHP web apps.
  - Abstract: "BAC is underexplored in automated testing due to key challenges: the lack of reliable oracles and the difficulty of generating semantically valid attack requests."
  - Relevance: this is exactly R4's question of what a tester needs.
- **BOLAZ (arXiv 2507.02309).** "Rethinking Broken Object Level Authorization Attacks Under Zero Trust Principle." A static-taint defence framework for RESTful APIs.
- **IDORacle (arXiv 2609.12426).** A runtime SQL-sink mediation for object-level authorization in Java.
- **Cross-evidence authorization state learning (arXiv 2611.00738).** Runtime BOLA detection in black-box web apps. Abstract: external monitors "lack access to source code, authorization policies, and object-ownership records".
- **BOLA in the wild (arXiv 2605.25865).** 107 HackerOne reports, 84 confirmed BOLA, and 11.9% vertical privilege failures.
- **BAC-Bench (arXiv 2610.34290).** 46 real broken-access-control vulnerabilities in 6 web apps, used as an LLM repair benchmark.

**Positioning.** None of these measures, on real fixed vulnerabilities in OpenAPI-described services, two things:
- the number and roles of principals a black-box test needs;
- whether the contract carries the violated rule.

The BACFuzz and 2611.00738 abstracts name the missing oracle and policy information as the core obstacle. R4 quantifies that obstacle on real cases.
