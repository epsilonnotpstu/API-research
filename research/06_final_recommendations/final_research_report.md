# Final Research Report — Software API Research: Landscape, Gaps & Recommended Direction

**তারিখ:** 2026-10-19 · **প্রস্তুতকারী:** Claude (Codex-এর independent discovery-সহ) · **Supervisor:** Human Research Supervisor
**ভাষা:** বাংলা (শিরোনাম, DOI ও পরিভাষা ইংরেজিতে) · ⚠️ = বিশ্লেষকের অনুমান · [H] = hypothesis

---

## 1. Executive summary

- **৩৮টি নির্বাচিত paper-এর গভীর পাঠ:**
  - উৎস: ১০৪টি যাচাইকৃত merged candidate।
  - P038-এর প্রদত্ত PDF ভুল paper, তাই substitute হিসেবে চিহ্নিত।
- **ফলাফল:** ৯টি প্রমাণ-ভিত্তিক research cluster। কেন্দ্রে REST API testing (T1)।
- **তিনটি সর্বজনীন পর্যবেক্ষণ:**
  1. **API specification-এর মান** testing, security, evolution ও LLM agent — সব ক্ষেত্রেই প্রধান bottleneck।
  2. **Oracle ও মূল্যায়ন-পদ্ধতি দুর্বল:** status-code oracle, self-evaluation, seeded fault, proxy metric।
  3. **Behavioural আচরণ** (পরিবর্তন, fault, policy) syntactic আচরণের তুলনায় কম অধ্যয়িত।
- **Gap:**
  - ১৪টি প্রস্তাবিত gap ১৭টি লক্ষ্যভিত্তিক search দিয়ে যাচাই করা হয়েছে।
  - **চারটি দুর্বল বা বাতিল:** semantic oracle, hallucination benchmark, LLM security misuse, GraphQL testing — ২০২৫–২০২৬-এ সক্রিয়ভাবে সমাধান হচ্ছে।
- **সর্বোচ্চ সুপারিশ — R1:** “Spec or Bug? OpenAPI conformance failure-এর runtime triage ও evidence-driven spec repair”।
  - Base weighting-এ ১ম; পাঁচটির মধ্যে চারটি weighting-এ শীর্ষে বা যুগ্ম-শীর্ষে।
  - কিন্তু novelty-অনুমানের উপর সংবেদনশীল — পূর্ণ-পাঠ যাচাই আবশ্যক।
- **বিকল্প:**
  - **Option A (কম ঝুঁকি):** R2 — inferred spec-এর downstream মূল্যায়ন।
  - **Option C (উচ্চাকাঙ্ক্ষী):** R3 — REST-এর behavioural breaking change benchmark ও detector।

## 2. Research scope
- **বিষয়:** software API (Web/REST, GraphQL, RPC, library API, LLM tool/MCP) নিয়ে software engineering ও security গবেষণা।
- **সময়:** মূলত সাম্প্রতিক ৩–৪ বছর (২০২২–২০২৬), সঙ্গে ভিত্তিমূলক কাজ (২০১৮–২০২১)।
- **বাদ:** T10 (API recommendation) চূড়ান্ত নির্বাচনে নেই (PHASE B সিদ্ধান্ত)।

## 3. Search methodology
- **Phase A (Claude, Codex থেকে স্বাধীনভাবে):**
  - Broad ও focused দুই pass।
  - উৎস: OpenAlex, Crossref, DataCite, arXiv, Consensus, WebSearch।
  - Semantic Scholar ও DBLP access সীমাবদ্ধ ছিল।
  - ফল: ৭০টি যাচাইকৃত candidate।
- **Phase D gap validation:** WebSearch-এ ১৭টি query (GV01–GV17)।
- **মোট লগ:** `00_protocol/search_log.csv`-এ ৮৫টি query।
- **সীমাবদ্ধতা:**
  - OpenAlex daily credit শেষ হয়েছিল।
  - arXiv export ও Semantic Scholar-এ 429।
  - DBLP bot-wall।
  - Gap-validation search snippet-স্তরের।
- বিস্তারিত: `00_protocol/search_strategy.md`, `07_audit/research_quality_audit.md`।

## 4. Paper selection process
1. **Merge:** Claude ৭০ + Codex ৬০ → **১০৪টি unique**।
   - Both ২৬, Claude-only ৪৪, Codex-only ৩৪।
   - ১০৪টিই registrar-verified।
2. **Stage 1 eligibility:** ৯৭টি eligible।
3. **Stage 2 weighted scoring:**
   - Relevance ০.২৫, Evidence ০.২৫, Analytical value ০.২০, Temporal ০.১৫, Access ০.১৫।
   - Citation count ইচ্ছাকৃতভাবে বাদ।
   - Cluster balance ও sensitivity analysis-সহ **৩৮টি নির্বাচিত**।
- বিস্তারিত: `02_screening/selection_methodology.md`।

## 5. Final literature catalog
সম্পূর্ণ তথ্য (মূল অবদান, ফল, সীমাবদ্ধতা): `05_research_clusters/final_paper_cluster_table.md` / `.csv`।

| ID | Title | Year | Venue | Primary | Secondary | DOI |
|---|---|---|---|---|---|---|
| P001 | Online testing of RESTful APIs: promises and challenges | 2022 | ESEC/FSE 2022 | T1 | T4; T6 | 10.1145/3540250.3549144 |
| P002 | Testing RESTful APIs: A Survey | 2023 | TOSEM | T1 | — | 10.1145/3617175 |
| P003 | Open Problems in Fuzzing RESTful APIs: A Comparison of Tools | 2023 | TOSEM | T1 | T4 | 10.1145/3597205 |
| P004 | Automated test generation for REST APIs: no time to rest yet | 2022 | ISSTA 2022 | T1 | T4 | 10.1145/3533767.3534401 |
| P005 | LlamaRestTest: Effective REST API Testing with Small Language Models | 2025 | PACMSE (FSE 2025) | T1 | T4; T8 | 10.1145/3715737 |
| P006 | RESTler: Stateful REST API Fuzzing | 2019 | ICSE 2019 | T1 | — | 10.1109/icse.2019.00083 |
| P007 | A Multi-Agent Approach for REST API Testing with Semantic Graphs and LLM-Driven Inputs | 2025 | ICSE 2025 | T1 | T8 | 10.1109/icse55347.2025.00179 |
| P008 | AGORA: Automated Generation of Test Oracles for REST APIs | 2023 | ISSTA 2023 | T1 | T6 | 10.1145/3597926.3598114 |
| P009 | GraphQL: A Systematic Mapping Study | 2023 | ACM CSUR | T2 | T6 | 10.1145/3561818 |
| P010 | A principled approach to GraphQL query cost analysis | 2020 | ESEC/FSE 2020 | T2 | T3 | 10.1145/3368089.3409670 |
| P011 | White-Box Fuzzing RPC-Based APIs with EvoMaster: An Industrial Case Study | 2023 | TOSEM | T2 | T1; T9 | 10.1145/3585009 |
| P012 | Automated Black-Box Testing of Mass Assignment Vulnerabilities in RESTful APIs | 2023 | ICSE 2023 | T3 | T1; T4 | 10.1109/icse48619.2023.00213 |
| P013 | Mobile Application Web API Reconnaissance: Web-to-Mobile Inconsistencies & Vulnerabilities | 2018 | IEEE S&P 2018 | T3 | T4 | 10.1109/sp.2018.00039 |
| P014 | Automated broken object-level authorization attack detection in REST APIs through OpenAPI to colored petri nets transformation | 2025 | IJIS | T3 | T9; T4 | 10.1007/s10207-024-00970-5 |
| P015 | Fuzzing for Detecting Access Policy Violations in REST APIs | 2025 | ISSRE 2025 | T3 | T1 | 10.1109/issre66568.2025.00025 |
| P016 | Specification and Automated Analysis of Inter-Parameter Dependencies in Web APIs | 2022 | IEEE TSC | T4 | T1; T6 | 10.1109/tsc.2021.3050610 |
| P017 | OOPS: Automated generation of REST API specification via LLMs | 2026 | JSS | T4 | T8 | 10.1016/j.jss.2026.112914 |
| P018 | Generating REST API Specifications through Static Analysis | 2024 | ICSE 2024 | T4 | T1; T6 | 10.1145/3597503.3639137 |
| P019 | RestPi: Path-Sensitive Type Inference for REST APIs | 2025 | PACMPL | T4 | T6 | 10.1145/3763055 |
| P020 | Microservice API Evolution in Practice: A Study on Strategies and Challenges | 2024 | JSS | T5 | T9; T6 | 10.1016/j.jss.2024.112110 |
| P021 | A Systematic Review of API Evolution Literature | 2021 | ACM CSUR | T5 | T7 | 10.1145/3470133 |
| P022 | Learning Evolving Tools for Large Language Models | 2025 | ICLR 2025 | T5 | T8 | Not applicable |
| P023 | Breaking bad? Semantic versioning and impact of breaking changes in Maven Central | 2022 | EMSE | T5 | — | 10.1007/s10664-021-10052-y |
| P024 | LLMs Meet Library Evolution: Evaluating Deprecated API Usage in LLM-Based Code Completion | 2025 | ICSE 2025 | T5 | T8; T7 | 10.1109/icse55347.2025.00245 |
| P025 | Differential regression testing for REST APIs | 2020 | ISSTA 2020 | T5 | T1; T6 | 10.1145/3395363.3397374 |
| P026 | Do RESTful API design rules have an impact on the understandability of Web APIs? | 2023 | EMSE | T6 | — | 10.1007/s10664-023-10367-y |
| P027 | RESTRuler: Towards Automatically Identifying Violations of RESTful Design Rules in Web APIs | 2024 | ICSA 2024 | T6 | T4 | 10.1109/icsa59870.2024.00020 |
| P028 | Automatic Detection of Five API Documentation Smells: Practitioners’ Perspectives | 2021 | SANER 2021 | T6 | T7 | 10.1109/saner50967.2021.00037 |
| P029 | Detecting Misuse of Security APIs: A Systematic Review | 2025 | ACM CSUR | T7 | T3 | 10.1145/3735968 |
| P030 | A Systematic Evaluation of Static API-Misuse Detectors | 2019 | TSE | T7 | T5; T6 | 10.1109/tse.2018.2827384 |
| P031 | Identifying and Mitigating API Misuse in Large Language Models | 2026 | TSE | T7 | T8; T5 | 10.1109/tse.2026.3651566 |
| P032 | From REST to MCP: An Empirical Study of API Wrapping and Automated Server Generation for LLM Agents | 2025 | arXiv (preprint) | T8 | T4; T6 | Not applicable |
| P033 | ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs | 2024 | ICLR 2024 | T8 | T1 | Not applicable |
| P034 | Gorilla: Large Language Model Connected with Massive APIs | 2024 | NeurIPS 2024 | T8 | T5; T7 | 10.52202/079017-4020 |
| P035 | On Mitigating Code LLM Hallucinations with API Documentation | 2025 | ICSE-SEIP 2025 | T8 | T6; T7; T5 | 10.1109/icse-seip66354.2025.00027 |
| P036 | Model Context Protocol (MCP) at First Glance: Studying the Security and Maintainability of MCP Servers | 2026 | TOSEM | T8 | T3; T9 | 10.1145/3814959 |
| P037 | LO2: Microservice API Anomaly Dataset of Logs and Metrics | 2025 | PROMISE 2025 | T9 | T1; T3 | 10.1145/3727582.3728682 |
| P038 | [SUBSTITUTE] Microservice Testing Approaches: A Systematic Literature Review (Ghani et al.) | 2019 | IJIE 2019 ⚠️ substitute | T9 | T1 | 10.30880/ijie.2019.11.08.008 |

## 6. Analysis methodology
- **পাঠের উপাদান:**
  - Markdown: pdftotext, page marker সহ।
  - প্রতিটি paper-এ A–P কাঠামো, page ও line প্রমাণসহ।
  - লেখক-স্বীকৃত (J) ও বিশ্লেষক-অনুমিত (K ⚠️) সীমাবদ্ধতা আলাদা।
  - Opportunity hypothesis হিসেবে লেবেল করা।
- **Machine-readable matrix:** `04_paper_analysis/evidence_matrix.csv` (script-generated)।
- **Integrity:** `04_paper_analysis/document_integrity_report.md`।
  - P038 identity mismatch ধরা পড়েছে first-author check-এ।
  - P032-এর NUL byte পরিষ্কার করা হয়েছে।
- **Synthesis:** `04_paper_analysis/cross_paper_synthesis.md`।

## 7. Research landscape
- **সময়রেখা:**
  - ভিত্তি (২০১৮–২০২১)।
  - পরিণতি (২০২২–২০২৩)।
  - LLM মোড় (২০২৪–২০২৬)।
- **Corpus-এ বছরভিত্তিক:** ২০২৫-এ ১১টি paper, সবচেয়ে বেশি।
- **সংযোগ:**
  - T1↔T4 সবচেয়ে ঘন।
  - T6 (docs/spec quality) cross-cutting — ১১টি paper-এর secondary।
  - T8 সবচেয়ে বেশি cluster-এর সাথে যুক্ত।
- বিস্তারিত: `05_research_clusters/research_landscape_report.md`, `cluster_relationships.md`।

## 8. Cluster descriptions

| Cluster | Primary | সংক্ষিপ্ত বিবরণ | Evidence strength |
|---|---|---|---|
| T1 REST testing/fuzzing | P001–P008 | Coverage ছাদ (<৬০%), dependency inference, LLM input, invariant oracle | উচ্চ |
| T2 GraphQL/RPC | P009–P011 | Mapping, cost analysis, RPC fuzzing | মাঝারি |
| T3 Security/authz | P012–P015 | Mass assignment, BOLA, access policy, mobile API | মাঝারি-উচ্চ |
| T4 Spec inference | P016–P019 | IDL, static/LLM spec generation, type inference | উচ্চ |
| T5 Evolution | P020–P025 | Semver, practitioner, differential regression, LLM ও deprecated API | উচ্চ |
| T6 Docs/design | P026–P028 | Design rule-এর প্রভাব, linting, doc smell | মাঝারি-উচ্চ |
| T7 API misuse | P029–P031 | Detector-এর মূল্যায়ন, security misuse SLR, LLM misuse | উচ্চ (novelty কম) |
| T8 LLM tool/MCP | P032–P036 | Tool use, hallucination, MCP wrapping ও security | মাঝারি |
| T9 Microservices | P037, P038* | Observability dataset; substitute review | নিম্ন |

প্রতিটির ২৩-বিন্দু বিশ্লেষণ: `05_research_clusters/cluster_T*.md`।

## 9. Comparative research findings
- **প্রতিষ্ঠিত:**
  - REST fuzzer coverage <৬০% (P003, P004, P007, P011)।
  - Spec-implementation অমিল ব্যাপক (P001, P004, P018, P019, P025, P013)।
  - Status-code oracle অপর্যাপ্ত (P001, P015, P002)।
  - Breaking change-এর প্রভাব usage-নির্ভর (P023, P020)।
  - LLM context অনুসরণ করে (P024, P035, P034)।
  - বড় model API-ভুল কমায় না (P024, P034)।
- **বিরোধ:**
  - Coverage ≈ fault? (P004 বনাম P006, P003)।
  - Retrieval-এর মূল্য (P033 বনাম P034, P035)।
  - Spec mismatch = fault? (P001 বনাম P015)।
- বিস্তারিত: `cross_paper_synthesis.md` §4, `cluster_comparison.md`।

## 10. Evidence-backed limitations (সাহিত্যের)
- **Self-evaluation:**
  - EvoMaster গোষ্ঠী: P003, P011, P015।
  - LlamaRestTest ও AutoRestTest: P005, P007।
- **Seeded বা vulnerable-by-design benchmark:** P008, P012, P014, P015।
- **Live API ও proprietary LLM-এর কারণে replication ভঙ্গুর:** P001, P007, P032, P033, P035।
- **Paper-এর ভেতরে সংখ্যার অসঙ্গতি:** P009, P021, P029, P031, P032, P034, P036, P038*।
- **Proxy metric:**
  - Unique 500।
  - Error-free invocation (P032)।
  - AST match (P034)।
  - LLM judge (P033)।

## 11. Research gap analysis
| শ্রেণি/অবস্থা | Gap |
|---|---|
| Supported | G1/G2 (REST behavioural breaking changes), G14 (spec-vs-impl triage), G9 (inferred spec downstream), G10 (neutral LLM tool তুলনা), G5 (real security benchmark) |
| Partially weakened / Class C | G4 (spec quality → agent), G3 (MCP authz, narrowed), G13 (observability oracle), G12 (AsyncAPI) |
| Weakened | G6, G7, G8, G11 |

- প্রতিটির D3-প্রশ্নের উত্তর ও search-প্রমাণ: `05_research_clusters/gap_validation.md`, `research_gap_register.csv`।
- **শিক্ষা:** corpus-এর লেখকদের “future work” (Class A) ২০২৫–২০২৬-এ দ্রুত পূরণ হচ্ছে। তাই বাইরের যাচাই ছাড়া gap অতিরঞ্জিত হতো।

## 12. Ranked research opportunities
| Rank (base) | Topic | Score |
|---|---|---|
| 1 | R1 Spec-impl mismatch triage + dynamic repair | 4.000 |
| 2 | R2 Inferred spec-এর downstream মূল্য | 3.950 |
| 3 | R4 Neutral budget-equal LLM REST tool তুলনা | 3.825 |
| 4 | R3 Behavioural breaking change benchmark + detector | 3.800 |
| 5 | R5 Spec-quality × LLM agents | 3.775 |
| 6 | R6 MCP access-policy testing | 3.275 |
| 7 | R7 Real-world REST authz benchmark | 3.225 |

**Sensitivity:**
- Importance-heavy weighting-এ R3 ১ম।
- Feasibility-heavy weighting-এ R2 ১ম।
- R1-এর novelty ১ কমলে R1 ৫ম স্থানে নামে।
- বিস্তারিত: `ranked_research_topics.md`।

## 13. Recommended research direction
**R1 (Option B), R2-কে প্রথম experiment হিসেবে অন্তর্ভুক্ত করে।**

**যুক্তি:**
- সমস্যাটি ৯টি paper-এ প্রমাণিত।
- Runtime triage বা repair-এর পূর্ববর্তী কাজ snippet-search-এ পাওয়া যায়নি।
- Data ও tool open, GPU লাগে না।
- তিনটি পরিমাপযোগ্য মূল্যায়ন অক্ষ আছে।

**বিকল্প:**
- Option A: R2।
- Option C: R3 (বিকল্প C′: R5)।

বিস্তারিত: `best_research_direction.md`।

## 14. Suggested initial experiments
1. **E0:** novelty যাচাই — 2607.12101, SpecFix-এর সর্বশেষ version, লক্ষ্যভিত্তিক scholarly search।
2. **E1:** ৩–৫টি SUT (P018-এর Java API, EMB) চালিয়ে conformance failure সংগ্রহ।
3. **E2:** ২০০টি failure-এর pilot double labelling (κ) ও taxonomy।
4. **E3:** R2 pilot — developer বনাম Respector spec দিয়ে fuzzing।
5. **E4–E6:** rule-based ও LLM triage, patch generator, scale-up।

সময়সূচি ও ঝুঁকি: `research_execution_roadmap.md`।

## 15. Study limitations ও next steps
**সীমাবদ্ধতা:**
- **P038 identity mismatch:** T9-এর প্রমাণ দুর্বল। সঠিক PDF (Ponce et al. 2025, 10.1016/j.infsof.2025.107870) প্রয়োজন।
- **Version:** ২৪টি paper preprint version থেকে পড়া; published version-এর সাথে মিলিয়ে দেখা হয়নি।
- **Conversion:** table column-split ও figure অনুপস্থিত। কিছু সংখ্যা PDF-এ যাচাই করা দরকার (P010, P022, P033, P037)।
- **Gap-validation:** search snippet-স্তরের; ২০২৫–২০২৬-এর উদ্ধৃত কাজ পূর্ণ পাঠে যাচাই হয়নি।
- **Corpus:** ৩৮টি paper, T1-ঘন। Research-group concentration আছে।
- **Score:** বিশ্লেষকের বিচার, novelty-র প্রমাণ নয়।

**Next steps:**
- Supervisor-এর সিদ্ধান্ত: `research_execution_roadmap.md` §14।
- P038 প্রতিস্থাপন।
- R1-এর E0 novelty যাচাই।
