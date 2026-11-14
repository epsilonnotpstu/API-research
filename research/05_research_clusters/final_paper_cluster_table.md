# Final Table — সব paper × cluster × মূল তথ্য (P001–P038)

উৎস: `04_paper_analysis/evidence_matrix.csv` + প্রতিটি `Pxxx_analysis.md`। Machine-readable: `final_paper_cluster_table.csv`।
Cluster: **T1** REST testing/fuzzing · **T2** GraphQL/RPC · **T3** Security/authz · **T4** Spec inference · **T5** Evolution · **T6** Docs/design · **T7** API misuse · **T8** LLM tool use/MCP · **T9** Microservices।

## T1 — REST testing/fuzzing (primary 8; secondary: P011, P012, P015, P016, P018, P025, P033, P037, P038)

| ID | Title | Year | Venue | Type | Secondary | মূল অবদান | প্রধান ফল | প্রধান সীমাবদ্ধতা | Conf. |
|---|---|---|---|---|---|---|---|---|---|
| P001 | Online testing of RESTful APIs: promises and challenges | 2022 | ESEC/FSE 2022 | Empirical | T4; T6 | RESTest-কে multi-bot online testing-এ রূপান্তর; ১৩টি industrial API-তে ১৫ দিন | ৩,৮৯,২১৬ failure; ১৪৭ fault, ৫০% spec-disconformity | Black-box; quota-সীমিত; triage manual | High |
| P002 | Testing RESTful APIs: A Survey | 2023 | TOSEM | SLR | — | REST API testing-এর ৯২ article-এর SLR | ৭৩% black-box; oracle মূলত 5xx/schema | জুন ২০২২ পর্যন্ত; LLM-যুগের আগে | High |
| P003 | Open Problems in Fuzzing RESTful APIs: A Comparison of Tools | 2023 | TOSEM | Tool comparison | T4 | ৭টি fuzzer × ১৯ SUT তুলনা ও open problem বিশ্লেষণ | কোনো tool >৬০% coverage নয়; WB +৭.৫% cov, +৩.৪ fault | EvoMaster লেখকদের নিজস্ব মূল্যায়ন | High |
| P004 | Automated test generation for REST APIs: no time to rest yet | 2022 | ISSTA 2022 | Tool comparison | T4 | ১০টি tool × ২০ service-এর independent তুলনা | EvoMasterWB line ৫২.৭৬%; ~৯৯% spec-এ mismatch | Java-only; LLM tool-এর আগে | High |
| P005 | LlamaRestTest: Effective REST API Testing with Small Language Models | 2025 | PACMSE (FSE 2025) | Technique | T4; T8 | Fine-tuned ছোট LLM (Llama3-8B) দিয়ে value ও IPD | Value validity ৭২.৪৪%; method coverage +১০–২২.৭ pp | অসম budget; একই গোষ্ঠীর benchmark | High |
| P006 | RESTler: Stateful REST API Fuzzing | 2019 | ICSE 2019 | Technique | — | Swagger-ভিত্তিক stateful fuzzing (RESTler) | GitLab-এ ২৮টি bug; dependency inference অপরিহার্য | কেবল 5xx oracle | High |
| P007 | A Multi-Agent Approach for REST API Testing with Semantic Graphs and LLM-Driven Inputs | 2025 | ICSE 2025 | Technique | T8 | Semantic dependency graph + multi-agent RL + LLM input | Method coverage ৫৮.৩%; ৪২টি 500-error | GPT-3.5 ও live API নির্ভর | High |
| P008 | AGORA: Automated Generation of Test Oracles for REST APIs | 2023 | ISSTA 2023 | Technique | T6 | OAS + traffic থেকে test oracle (invariant) inference — AGORA | Precision ৮১.২%; ১১টি বাস্তব bug | Seeded error; frequency ধারণা | High |

## T2 — GraphQL/RPC (primary 3; secondary: —)

| ID | Title | Year | Venue | Type | Secondary | মূল অবদান | প্রধান ফল | প্রধান সীমাবদ্ধতা | Conf. |
|---|---|---|---|---|---|---|---|---|---|
| P009 | GraphQL: A Systematic Mapping Study | 2023 | ACM CSUR | Mapping | T6 | GraphQL-এর systematic mapping | Testing study মাত্র ৪টি; ৩৯.৭৩% schema-তে cycle | ২০২১ পর্যন্ত; পুরোনো | High |
| P010 | A principled approach to GraphQL query cost analysis | 2020 | ESEC/FSE 2020 | Technique | T3 | GraphQL query cost-এর formal বিশ্লেষণ | Under-estimation শূন্য; GitHub DoS প্রকাশ | Resolver configuration manual | High |
| P011 | White-Box Fuzzing RPC-Based APIs with EvoMaster: An Industrial Case Study | 2023 | TOSEM | Technique | T1; T9 | EvoMaster দিয়ে RPC API white-box fuzzing, industrial | ৫০টি industrial API-তে ১২৬টি real fault; coverage ১৭.৪৯% | Industrial data গোপন; self-evaluation | High |

## T3 — Security/authz (primary 4; secondary: P010, P029, P036, P037, P038)

| ID | Title | Year | Venue | Type | Secondary | মূল অবদান | প্রধান ফল | প্রধান সীমাবদ্ধতা | Conf. |
|---|---|---|---|---|---|---|---|---|---|
| P012 | Automated Black-Box Testing of Mass Assignment Vulnerabilities in RESTful APIs | 2023 | ICSE 2023 | Technique | T1; T4 | Mass assignment vulnerability-র black-box detection | CRUD ৯৮%; zero false positive | Seeded/vulnerable-by-design SUT | High |
| P013 | Mobile Application Web API Reconnaissance: Web-to-Mobile Inconsistencies & Vulnerabilities | 2018 | IEEE S&P 2018 | Technique | T4 | Mobile app থেকে web API reconnaissance | ১০,০০০-এর মধ্যে ৪,৫৬২ app flagged; ৮৮.৪% invalid request গৃহীত | Tool/data অপ্রকাশিত; ২০১৮ | Medium |
| P014 | Automated broken object-level authorization attack detection in REST APIs through OpenAPI to colored petri nets transformation | 2025 | IJIS | Technique | T9; T4 | OpenAPI → Colored Petri Net দিয়ে BOLA attack detection | Attempt-স্তরে সব ধরা; V2 precision ০.২২ | Juice Shop + একটি OSS | High |
| P015 | Fuzzing for Detecting Access Policy Violations in REST APIs | 2025 | ISSRE 2025 | Technique | T1 | Access-policy violation-এর fuzzing oracle | ২৭টি নতুন fault; real API-তে Missed-Check নেই | Ownership অনুমান; self-evaluation | High |

## T4 — Spec inference (primary 4; secondary: P001, P003, P004, P005, P012, P013, P014, P027, P032)

| ID | Title | Year | Venue | Type | Secondary | মূল অবদান | প্রধান ফল | প্রধান সীমাবদ্ধতা | Conf. |
|---|---|---|---|---|---|---|---|---|---|
| P016 | Specification and Automated Analysis of Inter-Parameter Dependencies in Web APIs | 2022 | IEEE TSC | Technique | T1; T6 | Inter-parameter dependency-র IDL ও CSP-ভিত্তিক বিশ্লেষণ | ১৪৯টি বাস্তব dependency প্রকাশযোগ্য | IDL manually লেখা | High |
| P017 | OOPS: Automated generation of REST API specification via LLMs | 2026 | JSS | Technique | T8 | LLM দিয়ে source code থেকে OpenAPI generation (OOPS) | Endpoint F1 ~৯৮.৮%; ~$০.৪১/API | Downstream মূল্যায়ন নেই | High |
| P018 | Generating REST API Specifications through Static Analysis | 2024 | ICSE 2024 | Technique | T1; T6 | Static analysis দিয়ে spec generation (Respector) | Developer spec-এ ২২৮ endpoint অনুপস্থিত; constraint recall ৫০% | Java/Spring; downstream মূল্যায়ন নেই | High |
| P019 | RestPi: Path-Sensitive Type Inference for REST APIs | 2025 | PACMPL | Technique | T6 | Path-sensitive response type inference (RestPi) | Response type +৭১.৯৭%; non-200 +১২৯% | Feasibility যাচাই নেই | High |

## T5 — Evolution (primary 6; secondary: P030, P031, P034, P035)

| ID | Title | Year | Venue | Type | Secondary | মূল অবদান | প্রধান ফল | প্রধান সীমাবদ্ধতা | Conf. |
|---|---|---|---|---|---|---|---|---|---|
| P020 | Microservice API Evolution in Practice: A Study on Strategies and Challenges | 2024 | JSS | Interview | T9; T6 | Microservice API evolution — ১৭ সাক্ষাৎকার | মাত্র ৫/১৭ behavioural change-কে breaking ধরে | Qualitative; ছোট নমুনা | High |
| P021 | A Systematic Review of API Evolution Literature | 2021 | ACM CSUR | SLR | T7 | API evolution-এর SLR | ৬৩.৯% কেবল Java; ৭৪%-এ statistics নেই | ২০২০ পর্যন্ত; সংখ্যায় অসঙ্গতি | High |
| P022 | Learning Evolving Tools for Large Language Models | 2025 | ICLR 2025 | Technique | T8 | Evolving tool-এ LLM অভিযোজন (ToolEVO, MCTS) | Static-SFT deprecated call পুনরাবৃত্তি করে | GPT-4-generated পরিবর্তন; synthetic | High |
| P023 | Breaking bad? Semantic versioning and impact of breaking changes in Maven Central | 2022 | EMSE | Empirical (replication) | — | Maven Central-এ semver ও breaking change replication | Non-major-এর ২০.১% breaking; মাত্র ৭.৯% client প্রভাবিত | Java-only; syntactic | High |
| P024 | LLMs Meet Library Evolution: Evaluating Deprecated API Usage in LLM-Based Code Completion | 2025 | ICSE 2025 | Empirical + fix | T8; T7 | LLM code completion-এ deprecated API usage | Outdated context-এ DUR ৭০–৯০% | Python library; ছোট open model | High |
| P025 | Differential regression testing for REST APIs | 2020 | ISSTA 2020 | Technique | T1; T6 | REST API-র differential regression testing | ১৪টি regression (৯টি service-side) | Azure-নির্দিষ্ট; manual triage | High |

## T6 — Docs/design (primary 3; secondary: P001, P008, P009, P016, P018, P019, P020, P025, P030, P032, P035)

| ID | Title | Year | Venue | Type | Secondary | মূল অবদান | প্রধান ফল | প্রধান সীমাবদ্ধতা | Conf. |
|---|---|---|---|---|---|---|---|---|---|
| P026 | Do RESTful API design rules have an impact on the understandability of Web APIs? | 2023 | EMSE | Experiment | — | RESTful design rule-এর understandability পরীক্ষা | ১২টির ১১টি rule violation বোঝাপড়া কমায় | প্রতি rule-এ একটি stimulus | High |
| P027 | RESTRuler: Towards Automatically Identifying Violations of RESTful Design Rules in Web APIs | 2024 | ICSA 2024 | Technique | T4 | Design-rule violation detector (RESTRuler) | ১,৬৯,০৬১টি violation; precision ৯১.২%, recall ৬৭.৬% | Syntactic rule; বড় ফাইলে RAM | High |
| P028 | Automatic Detection of Five API Documentation Smells: Practitioners’ Perspectives | 2021 | SANER 2021 | Technique | T7 | API documentation smell detection | ৭৮% unit-এ smell; BERT F1 ০.৭৫–০.৯৭ | Java docs; REST নয় | High |

## T7 — API misuse (primary 3; secondary: P021, P024, P028, P034, P035)

| ID | Title | Year | Venue | Type | Secondary | মূল অবদান | প্রধান ফল | প্রধান সীমাবদ্ধতা | Conf. |
|---|---|---|---|---|---|---|---|---|---|
| P029 | Detecting Misuse of Security APIs: A Systematic Review | 2025 | ACM CSUR | SLR | T3 | Security API misuse detection-এর SLR | Benchmark মাত্র ৫টি, সবই Java crypto/SSL | LLM-যুগ অনাবৃত | High |
| P030 | A Systematic Evaluation of Static API-Misuse Detectors | 2019 | TSE | Benchmark eval | T5; T6 | Static API-misuse detector-এর মূল্যায়ন (MUBench) | সব detector-এর precision <১২% | Java; ২০১৯ | High |
| P031 | Identifying and Mitigating API Misuse in Large Language Models | 2026 | TSE | Empirical + repair | T8; T5 | LLM code-এ API misuse ও Dr.Fix repair | Hallucination সবচেয়ে সাধারণ misuse | Execution-ভিত্তিক যাচাই নেই | High |

## T8 — LLM tool use/MCP (primary 5; secondary: P005, P007, P017, P022, P024, P031)

| ID | Title | Year | Venue | Type | Secondary | মূল অবদান | প্রধান ফল | প্রধান সীমাবদ্ধতা | Conf. |
|---|---|---|---|---|---|---|---|---|---|
| P032 | From REST to MCP: An Empirical Study of API Wrapping and Automated Server Generation for LLM Agents | 2025 | arXiv (preprint) | Empirical + tool | T4; T6 | REST→MCP wrapping-এর empirical অধ্যয়ন ও AutoMCP/SpecFix | ৯২% bare wrapper; tool success ৭৬%→৯৪.২% | Preprint; সংখ্যায় অসঙ্গতি | Medium |
| P033 | ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs | 2024 | ICLR 2024 | Technique | T1 | ১৬,০০০+ real API-তে tool use (ToolLLM, DFSDT) | ToolLLaMA ChatGPT-এর কাছাকাছি | LLM judge; live API | High |
| P034 | Gorilla: Large Language Model Connected with Massive APIs | 2024 | NeurIPS 2024 | Technique | T5; T7 | Retrieval-aware API call generation (Gorilla) | Zero-shot GPT-4-এর চেয়ে +২০.৪৩% | AST match; ML API | High |
| P035 | On Mitigating Code LLM Hallucinations with API Documentation | 2025 | ICSE-SEIP 2025 | Empirical + mitigation | T6; T7; T5 | Documentation দিয়ে code-LLM hallucination হ্রাস | Spec যোগে ৪১.৮০%→৮৬.৮২% | AWS-কেন্দ্রিক; benchmark অনিশ্চিত | High |
| P036 | Model Context Protocol (MCP) at First Glance: Studying the Security and Maintainability of MCP Servers | 2026 | TOSEM | Empirical | T3; T9 | MCP server-এর health, security ও maintainability | ৭.২%-এ vulnerability, ৫.৫%-এ tool poisoning | Static ও sample-ভিত্তিক | High |

## T9 — Microservices (primary 2; secondary: P011, P014, P020, P036)

| ID | Title | Year | Venue | Type | Secondary | মূল অবদান | প্রধান ফল | প্রধান সীমাবদ্ধতা | Conf. |
|---|---|---|---|---|---|---|---|---|---|
| P037 | LO2: Microservice API Anomaly Dataset of Logs and Metrics | 2025 | PROMISE 2025 | Dataset | T1; T3 | Microservice API-error anomaly dataset (LO2) | সব service-এর log একত্রে ব্যর্থ (F1 ~০.৬৬৭) | Anomaly = documented 4xx | High |
| P038 | Microservices testing: A systematic literature review | 2025 | IST 2025 | SLR | T1; T3 | ৭৪টি microservice testing study-র SLR (SWEBOK, TRL, SUT) | System testing ৪৭; API ৮; TRL ৩–৪; TrainTicket প্রধান | Title-only query; security gap-দাবি সংকীর্ণ | High |

## Cluster membership matrix (● primary, ○ secondary)

| ID | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 |
|---|---|---|---|---|---|---|---|---|---|
| P001 | ● |  |  | ○ |  | ○ |  |  |  |
| P002 | ● |  |  |  |  |  |  |  |  |
| P003 | ● |  |  | ○ |  |  |  |  |  |
| P004 | ● |  |  | ○ |  |  |  |  |  |
| P005 | ● |  |  | ○ |  |  |  | ○ |  |
| P006 | ● |  |  |  |  |  |  |  |  |
| P007 | ● |  |  |  |  |  |  | ○ |  |
| P008 | ● |  |  |  |  | ○ |  |  |  |
| P009 |  | ● |  |  |  | ○ |  |  |  |
| P010 |  | ● | ○ |  |  |  |  |  |  |
| P011 | ○ | ● |  |  |  |  |  |  | ○ |
| P012 | ○ |  | ● | ○ |  |  |  |  |  |
| P013 |  |  | ● | ○ |  |  |  |  |  |
| P014 |  |  | ● | ○ |  |  |  |  | ○ |
| P015 | ○ |  | ● |  |  |  |  |  |  |
| P016 | ○ |  |  | ● |  | ○ |  |  |  |
| P017 |  |  |  | ● |  |  |  | ○ |  |
| P018 | ○ |  |  | ● |  | ○ |  |  |  |
| P019 |  |  |  | ● |  | ○ |  |  |  |
| P020 |  |  |  |  | ● | ○ |  |  | ○ |
| P021 |  |  |  |  | ● |  | ○ |  |  |
| P022 |  |  |  |  | ● |  |  | ○ |  |
| P023 |  |  |  |  | ● |  |  |  |  |
| P024 |  |  |  |  | ● |  | ○ | ○ |  |
| P025 | ○ |  |  |  | ● | ○ |  |  |  |
| P026 |  |  |  |  |  | ● |  |  |  |
| P027 |  |  |  | ○ |  | ● |  |  |  |
| P028 |  |  |  |  |  | ● | ○ |  |  |
| P029 |  |  | ○ |  |  |  | ● |  |  |
| P030 |  |  |  |  | ○ | ○ | ● |  |  |
| P031 |  |  |  |  | ○ |  | ● | ○ |  |
| P032 |  |  |  | ○ |  | ○ |  | ● |  |
| P033 | ○ |  |  |  |  |  |  | ● |  |
| P034 |  |  |  |  | ○ |  | ○ | ● |  |
| P035 |  |  |  |  | ○ | ○ | ○ | ● |  |
| P036 |  |  | ○ |  |  |  |  | ● | ○ |
| P037 | ○ |  | ○ |  |  |  |  |  | ● |
| P038 | ○ |  | ○ |  |  |  |  |  | ● |
| **মোট (●/○)** | 8/9 | 3/0 | 4/5 | 4/9 | 6/4 | 3/11 | 3/5 | 5/6 | 2/4 |
