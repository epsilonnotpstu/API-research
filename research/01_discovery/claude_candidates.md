# Claude Candidate Catalog — PHASE A (স্বাধীন অনুসন্ধান)

**প্রস্তুতকারী:** Claude | **তারিখ:** 2026-10-19 | **মেশিন-পাঠযোগ্য উৎস:** `claude_candidates.csv` (এই ফাইল সেখান থেকে script দিয়ে তৈরি — `00_protocol/scripts/build_catalog_md.py`)

> **প্রমাণের স্তর:** কোনো paper-এর full text পড়া হয়নি। Problem/Contribution/Methods/Findings কলাম **শুধু যাচাইকৃত abstract-এর** paraphrase (ইংরেজিতে রাখা হয়েছে যাতে অনুবাদে অর্থবিকৃতি না ঘটে)। “author claim/author-reported” মানে লেখকের দাবি — স্বাধীনভাবে যাচাই নয়। Inclusion reason, relevance ও uncertainty Claude-এর বিশ্লেষণ।

**Legend (Access):** 🟢 OA = publisher/proceedings/repository বা arXiv-only paper-এর PDF যাচাইকৃত · 🟡 Preprint OA = publisher version OA হিসেবে যাচাই হয়নি, কিন্তু বৈধ preprint PDF (arXiv) যাচাইকৃত (published version থেকে ভিন্ন হতে পারে) · 🔴 = শুধু landing page; unrestricted full text যাচাই হয়নি।

**PDF যাচাই পদ্ধতি:** URL-এ ranged GET; response body `%PDF` দিয়ে শুরু হলেই কেবল ‘verified’।

## সারসংক্ষেপ

- মোট included candidate: **64** (যাচাইকৃত seed ৭০টি থেকে; ৬টি screened-out — নিচে)
- Review status: Peer-reviewed: 60, Preprint: 4
- Era: Foundational: 12, Recent: 52
- Paper kind: Original: 51, Survey: 8, Benchmark: 4, Industrial: 1
- Access: 🟡 Preprint OA: 31, 🔴 Not verified: 19, 🟢 OA: 14
- বছর: 2019: 3, 2020: 5, 2021: 3, 2022: 3, 2023: 16, 2024: 12, 2025: 15, 2026: 7

### Taxonomy অনুযায়ী (code-এর সংজ্ঞা: `00_protocol/api_research_landscape.md`)

| Code | Area | Primary | Secondary membership |
|---|---|---|---|
| T1 | REST/Web API testing & fuzzing | 16 | 9 |
| T2 | GraphQL, RPC/gRPC & architecture styles | 5 | 1 |
| T3 | API security & authorization | 5 | 4 |
| T4 | API specification (OpenAPI) inference & enrichment | 5 | 5 |
| T5 | API evolution, breaking changes & deprecation | 9 | 1 |
| T6 | API documentation, design quality & governance | 5 | 2 |
| T7 | API misuse detection | 5 | 0 |
| T8 | LLM tool use, API calling & MCP | 10 | 7 |
| T9 | Microservice APIs | 2 | 2 |
| T10 | API recommendation | 1 | 0 |
| T11 | API monitoring & anomaly detection | 1 | 0 |

## মূল তালিকা (human review table)

| ID | Title | Year | Venue | Type / Review | Kind | Tax. | Access | Paper link | PDF (verified) | Conf. |
|---|---|---|---|---|---|---|---|---|---|---|
| C01 | RESTler: Stateful REST API Fuzzing | 2019 | 2019 IEEE/ACM 41st International Conference on Software Engineering (ICSE) | Conference paper (PR) | Original – technique | T1 | 🔴 Not verified | [landing](https://doi.org/10.1109/icse.2019.00083) | Not verified | High |
| C02 | RESTful API Automated Test Case Generation with EvoMaster | 2019 | ACM Transactions on Software Engineering and Methodology | Journal article (PR) | Original – technique | T1 | 🔴 Not verified | [landing](https://doi.org/10.1145/3293455) | Not verified | High |
| C03 | Automated test generation for REST APIs: no time to rest yet | 2022 | Proceedings of the 31st ACM SIGSOFT International Symposium on Software Testing and Analysis | Conference paper (PR) | Original – empirical (tool comparison) | T1 | 🟡 Preprint OA | [landing](https://doi.org/10.1145/3533767.3534401) | [PDF](https://arxiv.org/pdf/2204.08348) | High |
| C04 | Testing RESTful APIs: A Survey | 2023 | ACM Transactions on Software Engineering and Methodology | Journal article (PR) | Survey / SLR | T1 | 🟡 Preprint OA | [landing](https://doi.org/10.1145/3617175) | [PDF](https://arxiv.org/pdf/2212.14604) | High |
| C05 | Open Problems in Fuzzing RESTful APIs: A Comparison of Tools | 2023 | ACM Transactions on Software Engineering and Methodology | Journal article (PR) | Original – empirical (tool comparison) | T1 | 🟡 Preprint OA | [landing](https://doi.org/10.1145/3597205) | [PDF](https://arxiv.org/pdf/2205.05325) | High |
| C06 | Adaptive REST API Testing with Reinforcement Learning | 2023 | 2023 38th IEEE/ACM International Conference on Automated Software Engineering (ASE) | Conference paper (PR) | Original – technique | T1 | 🟡 Preprint OA | [landing](https://doi.org/10.1109/ase56229.2023.00218) | [PDF](https://arxiv.org/pdf/2309.04583) | High |
| C07 | Enhancing REST API Testing with NLP Techniques | 2023 | Proceedings of the 32nd ACM SIGSOFT International Symposium on Software Testing and Analysis | Conference paper (PR) | Original – technique | T1 (+T4) | 🔴 Not verified | [landing](https://doi.org/10.1145/3597926.3598131) | Not verified | High |
| C08 | DeepREST: Automated Test Case Generation for REST APIs Exploiting Deep Reinforcement Learning | 2024 | Proceedings of the 39th IEEE/ACM International Conference on Automated Software Engineering | Conference paper (PR) | Original – technique | T1 | 🟡 Preprint OA | [landing](https://doi.org/10.1145/3691620.3695511) | [PDF](https://arxiv.org/pdf/2408.08594) | High |
| C09 | Leveraging Large Language Models to Improve REST API Testing | 2024 | Proceedings of the 2024 ACM/IEEE 44th International Conference on Software Engineering: New Ideas and Emerging Results | Conference paper (PR) | Original – technique (new-ideas track) | T1 (+T4) | 🟡 Preprint OA | [landing](https://doi.org/10.1145/3639476.3639769) | [PDF](https://arxiv.org/pdf/2312.00894) | Medium |
| C10 | LlamaRestTest: Effective REST API Testing with Small Language Models | 2025 | Proceedings of the ACM on Software Engineering | Journal article (PR) | Original – technique | T1 (+T4) | 🟡 Preprint OA | [landing](https://doi.org/10.1145/3715737) | [PDF](https://arxiv.org/pdf/2501.08598) | High |
| C11 | A Multi-Agent Approach for REST API Testing with Semantic Graphs and LLM-Driven Inputs | 2025 | 2025 IEEE/ACM 47th International Conference on Software Engineering (ICSE) | Conference paper (PR) | Original – technique | T1 | 🟡 Preprint OA | [landing](https://doi.org/10.1109/icse55347.2025.00179) | [PDF](https://arxiv.org/pdf/2411.07098) | High |
| C13 | AGORA: Automated Generation of Test Oracles for REST APIs | 2023 | Proceedings of the 32nd ACM SIGSOFT International Symposium on Software Testing and Analysis | Conference paper (PR) | Original – technique | T1 (+T1) | 🔴 Not verified | [landing](https://doi.org/10.1145/3597926.3598114) | Not verified | High |
| C14 | EMB: A Curated Corpus of Web/Enterprise Applications And Library Support for Software Testing Research | 2023 | 2023 IEEE Conference on Software Testing, Verification and Validation (ICST) | Conference paper (PR) | Benchmark / dataset | T1 (+T2) | 🔴 Not verified | [landing](https://doi.org/10.1109/icst57152.2023.00047) | Not verified | High |
| C15 | Specification and Automated Analysis of Inter-Parameter Dependencies in Web APIs | 2022 | IEEE Transactions on Services Computing | Journal article (PR) | Original – technique | T4 (+T1) | 🟡 Preprint OA | [landing](https://doi.org/10.1109/tsc.2021.3050610) | [PDF](https://arxiv.org/pdf/2005.03320) | High |
| C16 | Effective REST APIs Testing with Error Message Analysis | 2025 | Proceedings of the ACM on Software Engineering | Journal article (PR) | Original – technique | T1 | 🔴 Not verified | [landing](https://doi.org/10.1145/3728964) | Not verified | High |
| C18 | Detecting and Mitigating Flakiness in REST API Fuzzing | 2026 | arXiv (preprint) | Preprint | Original – empirical + technique | T1 | 🟢 OA | [landing](https://arxiv.org/abs/2603.28452) | [PDF](https://arxiv.org/pdf/2603.28452) | Medium |
| C19 | WFC/WFD: Web Fuzzing Commons, Dataset and Guidelines to Support Experimentation in REST API Fuzzing | 2025 | arXiv (preprint) | Preprint | Benchmark / dataset + guidelines | T1 (+T3) | 🟢 OA | [landing](https://arxiv.org/abs/2509.01612) | [PDF](https://arxiv.org/pdf/2509.01612) | Medium |
| C21 | GraphQL: A Systematic Mapping Study | 2023 | ACM Computing Surveys | Journal article (PR) | Survey / systematic mapping | T2 | 🔴 Not verified | [landing](https://doi.org/10.1145/3561818) | Not verified | High |
| C22 | Random Testing and Evolutionary Testing for Fuzzing GraphQL APIs | 2024 | ACM Transactions on the Web | Journal article (PR) | Original – technique | T2 | 🔴 Not verified | [landing](https://doi.org/10.1145/3609427) | Not verified | High |
| C23 | A principled approach to GraphQL query cost analysis | 2020 | Proceedings of the 28th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering | Conference paper (PR) | Original – technique (formal) | T2 | 🟡 Preprint OA | [landing](https://doi.org/10.1145/3368089.3409670) | [PDF](https://arxiv.org/pdf/2009.05632) | High |
| C25 | White-Box Fuzzing RPC-Based APIs with EvoMaster: An Industrial Case Study | 2023 | ACM Transactions on Software Engineering and Methodology | Journal article (PR) | Original – technique + industrial study | T2 (+T9) | 🟡 Preprint OA | [landing](https://doi.org/10.1145/3585009) | [PDF](https://arxiv.org/pdf/2208.12743) | High |
| C26 | REST vs GraphQL: A Controlled Experiment | 2020 | 2020 IEEE International Conference on Software Architecture (ICSA) | Conference paper (PR) | Original – empirical (controlled experiment) | T2 | 🟡 Preprint OA | [landing](https://doi.org/10.1109/icsa47634.2020.00016) | [PDF](https://arxiv.org/pdf/2003.04761) | Medium |
| C27 | Checking Security Properties of Cloud Service REST APIs | 2020 | 2020 IEEE 13th International Conference on Software Testing, Validation and Verification (ICST) | Conference paper (PR) | Original – technique | T3 (+T1) | 🔴 Not verified | [landing](https://doi.org/10.1109/icst46399.2020.00046) | Not verified | High |
| C28 | Automated Black-Box Testing of Mass Assignment Vulnerabilities in RESTful APIs | 2023 | 2023 IEEE/ACM 45th International Conference on Software Engineering (ICSE) | Conference paper (PR) | Original – technique | T3 (+T1) | 🟡 Preprint OA | [landing](https://doi.org/10.1109/icse48619.2023.00213) | [PDF](https://arxiv.org/pdf/2301.01261) | High |
| C29 | Automated broken object-level authorization attack detection in REST APIs through OpenAPI to colored petri nets transformation | 2025 | International Journal of Information Security | Journal article (PR) | Original – technique (formal) | T3 | 🟢 OA | [landing](https://doi.org/10.1007/s10207-024-00970-5) | [PDF](https://link.springer.com/content/pdf/10.1007/s10207-024-00970-5.pdf) | Medium |
| C30 | Fuzzing for Detecting Access Policy Violations in REST APIs | 2025 | 2025 IEEE 36th International Symposium on Software Reliability Engineering (ISSRE) | Conference paper (PR) | Original – technique | T3 (+T1) | 🔴 Not verified | [landing](https://doi.org/10.1109/issre66568.2025.00025) | Not verified | Medium |
| C31 | Security testing of RESTful APIs: Approaches and research challenges | 2026 | Computer Science Review | Journal article (PR) | Survey | T3 | 🔴 Not verified | [landing](https://doi.org/10.1016/j.cosrev.2026.101043) | Not verified | Low |
| C32 | Generating REST API Specifications through Static Analysis | 2024 | Proceedings of the IEEE/ACM 46th International Conference on Software Engineering | Conference paper (PR) | Original – technique | T4 (+T1) | 🔴 Not verified | [landing](https://doi.org/10.1145/3597503.3639137) | Not verified | High |
| C33 | Carving UI Tests to Generate API Tests and API Specification | 2023 | 2023 IEEE/ACM 45th International Conference on Software Engineering (ICSE) | Conference paper (PR) | Original – technique | T4 (+T1) | 🟡 Preprint OA | [landing](https://doi.org/10.1109/icse48619.2023.00167) | [PDF](https://arxiv.org/pdf/2305.14692) | High |
| C34 | Generating OpenAPI Specifications from Online API Documentation with Large Language Models | 2025 | Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 6: Industry Track) | Conference paper (PR) | Original – technique (industry track) | T4 (+T8) | 🟢 OA | [landing](https://doi.org/10.18653/v1/2025.acl-industry.18) | [PDF](https://aclanthology.org/2025.acl-industry.18.pdf) | Medium |
| C35 | OOPS: Automated generation of REST API specification via LLMs | 2026 | Journal of Systems and Software | Journal article (PR) | Original – technique | T4 (+T8) | 🟡 Preprint OA | [landing](https://doi.org/10.1016/j.jss.2026.112914) | [PDF](https://arxiv.org/pdf/2601.12735) | High |
| C36 | An Analysis of Public REST Web Service APIs | 2021 | IEEE Transactions on Services Computing | Journal article (PR) | Original – empirical | T6 | 🔴 Not verified | [landing](https://doi.org/10.1109/tsc.2018.2847344) | Not verified | High |
| C37 | A Systematic Review of API Evolution Literature | 2021 | ACM Computing Surveys | Journal article (PR) | Survey / SLR | T5 | 🔴 Not verified | [landing](https://doi.org/10.1145/3470133) | Not verified | High |
| C38 | Microservice API Evolution in Practice: A Study on Strategies and Challenges | 2024 | Journal of Systems and Software | Journal article (PR) | Original – empirical (qualitative) | T5 (+T9) | 🟡 Preprint OA | [landing](https://doi.org/10.1016/j.jss.2024.112110) | [PDF](https://arxiv.org/pdf/2311.08175) | High |
| C39 | Differential regression testing for REST APIs | 2020 | Proceedings of the 29th ACM SIGSOFT International Symposium on Software Testing and Analysis | Conference paper (PR) | Original – technique | T5 (+T1) | 🔴 Not verified | [landing](https://doi.org/10.1145/3395363.3397374) | Not verified | High |
| C40 | Understanding the Impact of APIs Behavioral Breaking Changes on Client Applications | 2024 | Proceedings of the ACM on Software Engineering | Journal article (PR) | Original – empirical | T5 | 🔴 Not verified | [landing](https://doi.org/10.1145/3643782) | Not verified | High |
| C41 | Breaking bad? Semantic versioning and impact of breaking changes in Maven Central | 2022 | Empirical Software Engineering | Journal article (PR) | Original – empirical (replication) | T5 | 🟢 OA | [landing](https://doi.org/10.1007/s10664-021-10052-y) | [PDF](https://hal.science/hal-03378089v1/document) | High |
| C43 | Web API evolution patterns: A usage-driven approach | 2023 | Journal of Systems and Software | Journal article (PR) | Original – technique | T5 | 🟢 OA | [landing](https://doi.org/10.1016/j.jss.2023.111609) | [PDF](https://upcommons.upc.edu/server/api/core/bitstreams/58775b55-bbc6-47a3-8db4-0e209560f47b/content) | Medium |
| C44 | A First Look at the Deprecation of RESTful APIs: An Empirical Study | 2020 | 2020 IEEE International Conference on Software Maintenance and Evolution (ICSME) | Conference paper (PR) | Original – empirical + tool | T5 | 🟡 Preprint OA | [landing](https://doi.org/10.1109/icsme46990.2020.00024) | [PDF](https://arxiv.org/pdf/2008.12808) | High |
| C45 | Automatic Detection of Five API Documentation Smells: Practitioners’ Perspectives | 2021 | 2021 IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER) | Conference paper (PR) | Original – empirical + technique | T6 | 🟡 Preprint OA | [landing](https://doi.org/10.1109/saner50967.2021.00037) | [PDF](https://arxiv.org/pdf/2102.08486) | High |
| C46 | Do RESTful API design rules have an impact on the understandability of Web APIs? | 2023 | Empirical Software Engineering | Journal article (PR) | Original – empirical (controlled experiment) | T6 | 🟢 OA | [landing](https://doi.org/10.1007/s10664-023-10367-y) | [PDF](https://link.springer.com/content/pdf/10.1007/s10664-023-10367-y.pdf) | High |
| C47 | RESTRuler: Towards Automatically Identifying Violations of RESTful Design Rules in Web APIs | 2024 | 2024 IEEE 21st International Conference on Software Architecture (ICSA) | Conference paper (PR) | Original – technique + tool | T6 | 🟡 Preprint OA | [landing](https://doi.org/10.1109/icsa59870.2024.00020) | [PDF](https://arxiv.org/pdf/2402.13710) | High |
| C48 | API Governance at Scale | 2024 | Proceedings of the 46th International Conference on Software Engineering: Software Engineering in Practice | Conference paper (PR) | Industrial – action research | T6 | 🔴 Not verified | [landing](https://doi.org/10.1145/3639477.3639713) | Not verified | Medium |
| C49 | A Systematic Evaluation of Static API-Misuse Detectors | 2019 | IEEE Transactions on Software Engineering | Journal article (PR) | Original – empirical (benchmark evaluation) | T7 | 🟡 Preprint OA | [landing](https://doi.org/10.1109/tse.2018.2827384) | [PDF](https://arxiv.org/pdf/1712.00242) | High |
| C50 | Detecting Misuse of Security APIs: A Systematic Review | 2025 | ACM Computing Surveys | Journal article (PR) | Survey / SLR | T7 | 🟡 Preprint OA | [landing](https://doi.org/10.1145/3735968) | [PDF](https://arxiv.org/pdf/2306.08869) | High |
| C51 | Generating API Parameter Security Rules with LLM for API Misuse Detection | 2025 | Proceedings 2025 Network and Distributed System Security Symposium | Conference paper (PR) | Original – technique | T7 | 🟢 OA | [landing](https://doi.org/10.14722/ndss.2025.230465) | [PDF](https://www.ndss-symposium.org/wp-content/uploads/2025-465-paper.pdf) | Medium |
| C52 | An Investigation into Misuse of Java Security APIs by Large Language Models | 2024 | Proceedings of the 19th ACM Asia Conference on Computer and Communications Security | Conference paper (PR) | Original – empirical | T7 (+T8) | 🟡 Preprint OA | [landing](https://doi.org/10.1145/3634737.3661134) | [PDF](https://arxiv.org/pdf/2404.03823) | High |
| C53 | Identifying and Mitigating API Misuse in Large Language Models | 2026 | IEEE Transactions on Software Engineering | Journal article (PR) | Original – empirical + technique | T7 (+T8) | 🟡 Preprint OA | [landing](https://doi.org/10.1109/tse.2026.3651566) | [PDF](https://arxiv.org/pdf/2503.22821) | High |
| C55 | Gorilla: Large Language Model Connected with Massive APIs | 2024 | Advances in Neural Information Processing Systems 37 | Conference paper (PR) | Original – technique + benchmark | T8 (+T6) | 🟡 Preprint OA | [landing](https://doi.org/10.52202/079017-4020) | [PDF](https://arxiv.org/pdf/2305.15334) | High |
| C56 | ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs | 2024 | International Conference on Learning Representations (ICLR 2024) | Conference paper (PR) | Original – technique + dataset | T8 | 🟢 OA | [landing](https://proceedings.iclr.cc/paper_files/paper/2024/hash/28e50ee5b72e90b50e7196fde8ea260e-Abstract-Conference.html) | [PDF](https://proceedings.iclr.cc/paper_files/paper/2024/file/28e50ee5b72e90b50e7196fde8ea260e-Paper-Conference.pdf) | High |
| C57 | API-Bank: A Comprehensive Benchmark for Tool-Augmented LLMs | 2023 | Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing | Conference paper (PR) | Benchmark | T8 | 🟢 OA | [landing](https://doi.org/10.18653/v1/2023.emnlp-main.187) | [PDF](https://aclanthology.org/2023.emnlp-main.187.pdf) | High |
| C58 | StableToolBench: Towards Stable Large-Scale Benchmarking on Tool Learning of Large Language Models | 2024 | Findings of the Association for Computational Linguistics ACL 2024 | Conference paper (PR) | Benchmark | T8 (+T5) | 🟢 OA | [landing](https://doi.org/10.18653/v1/2024.findings-acl.664) | [PDF](https://aclanthology.org/2024.findings-acl.664.pdf) | High |
| C59 | RestGPT: Connecting Large Language Models with Real-World RESTful APIs | 2023 | arXiv (preprint) | Preprint | Original – technique + benchmark | T8 (+T4) | 🟢 OA | [landing](https://arxiv.org/abs/2306.06624) | [PDF](https://arxiv.org/pdf/2306.06624) | Medium |
| C60 | On Mitigating Code LLM Hallucinations with API Documentation | 2025 | 2025 IEEE/ACM 47th International Conference on Software Engineering: Software Engineering in Practice (ICSE-SEIP) | Conference paper (PR) | Original – empirical + technique | T8 (+T6) | 🟡 Preprint OA | [landing](https://doi.org/10.1109/icse-seip66354.2025.00027) | [PDF](https://arxiv.org/pdf/2407.09726) | High |
| C61 | Tool learning with large language models: a survey | 2025 | Frontiers of Computer Science | Journal article (PR) | Survey | T8 | 🟡 Preprint OA | [landing](https://doi.org/10.1007/s11704-024-40678-2) | [PDF](https://arxiv.org/pdf/2405.17935) | High |
| C62 | Model Context Protocol (MCP): Landscape, Security Threats, and Future Research Directions | 2026 | ACM Transactions on Software Engineering and Methodology | Journal article (PR) | Survey / systematic study | T8 (+T3) | 🟡 Preprint OA | [landing](https://doi.org/10.1145/3796519) | [PDF](https://arxiv.org/pdf/2503.23278) | High |
| C63 | Model Context Protocol (MCP) at First Glance: Studying the Security and Maintainability of MCP Servers | 2026 | ACM Transactions on Software Engineering and Methodology | Journal article (PR) | Original – empirical | T8 (+T3) | 🟡 Preprint OA | [landing](https://doi.org/10.1145/3814959) | [PDF](https://arxiv.org/pdf/2506.13538) | High |
| C64 | From REST to MCP: An Empirical Study of API Wrapping and Automated Server Generation for LLM Agents | 2025 | arXiv (preprint) | Preprint | Original – empirical + technique | T8 (+T4) | 🟢 OA | [landing](https://arxiv.org/abs/2507.16044) | [PDF](https://arxiv.org/pdf/2507.16044) | Medium |
| C65 | Microservices testing: A systematic literature review | 2025 | Information and Software Technology | Journal article (PR) | Survey / SLR | T9 | 🔴 Not verified | [landing](https://doi.org/10.1016/j.infsof.2025.107870) | Not verified | Medium |
| C66 | SAINT: Service-level Integration Test Generation with Program Analysis and LLM-based Agents | 2026 | Proceedings of the 2026 IEEE/ACM 48th International Conference on Software Engineering | Conference paper (PR) | Original – technique | T9 (+T1) | 🟡 Preprint OA | [landing](https://doi.org/10.1145/3744916.3773185) | [PDF](https://arxiv.org/pdf/2511.13305) | High |
| C67 | API Traffic Anomaly Detection in Microservice Architecture | 2023 | 2023 IEEE/ACM 23rd International Symposium on Cluster, Cloud and Internet Computing Workshops (CCGridW) | Conference paper (PR) | Original – technique (workshop) | T11 (+T3) | 🔴 Not verified | [landing](https://doi.org/10.1109/ccgridw59191.2023.00044) | Not verified | Low |
| C68 | Revisiting, Benchmarking and Exploring API Recommendation: How Far Are We? | 2023 | IEEE Transactions on Software Engineering | Journal article (PR) | Original – empirical (benchmark) | T10 (+T8) | 🟡 Preprint OA | [landing](https://doi.org/10.1109/tse.2022.3197063) | [PDF](https://arxiv.org/pdf/2112.12653) | High |
| C69 | LLMs Meet Library Evolution: Evaluating Deprecated API Usage in LLM-Based Code Completion | 2025 | 2025 IEEE/ACM 47th International Conference on Software Engineering (ICSE) | Conference paper (PR) | Original – empirical + technique | T5 (+T8) | 🟡 Preprint OA | [landing](https://doi.org/10.1109/icse55347.2025.00245) | [PDF](https://arxiv.org/pdf/2406.09834) | High |
| C70 | Learning Evolving Tools for Large Language Models | 2025 | International Conference on Learning Representations (ICLR 2025) | Conference paper (PR) | Original – technique + benchmark | T5 (+T8) | 🟢 OA | [landing](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d8d1d325f822e07d16866780cc23deb2-Abstract-Conference.html) | [PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/d8d1d325f822e07d16866780cc23deb2-Paper-Conference.pdf) | High |

(PR = peer-reviewed)

## প্রতিটি candidate-এর বিস্তারিত

### C01 — RESTler: Stateful REST API Fuzzing

- **Authors:** Vaggelis Atlidakis; Patrice Godefroid; Marina Polishchuk
- **Year / Venue:** 2019 — 2019 IEEE/ACM 41st International Conference on Software Engineering (ICSE)
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique | **Era:** Foundational
- **DOI:** 10.1109/icse.2019.00083 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1109/icse.2019.00083
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** REST API testing & fuzzing — **Taxonomy:** T1
- **Problem:** Automatically testing cloud services through their REST APIs requires generating valid stateful request sequences from the API specification.
- **Claimed contribution:** RESTler, described by the authors as the first stateful REST API fuzzer.
- **Methods:** Infers producer–consumer dependencies among request types from the specification and uses dynamic response feedback to prune invalid sequences.
- **Key findings (abstract-level):** Abstract reports 28 bugs found in GitLab and several in Azure/Office365 services, confirmed and fixed by owners.
- **অন্তর্ভুক্তির কারণ:** Stateful REST fuzzing-এর ভিত্তি; প্রায় সব পরবর্তী tool এর সঙ্গে তুলনা করে (baseline)।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** যেকোনো REST testing গবেষণার baseline ও ধারণাগত ভিত্তি।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP028 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Full text paywalled (IEEE); OA PDF যাচাই হয়নি। arXiv-এ ভিন্ন শিরোনামে পূর্বসংস্করণ থাকতে পারে (যাচাই হয়নি)।

### C02 — RESTful API Automated Test Case Generation with EvoMaster

- **Authors:** Andrea Arcuri
- **Year / Venue:** 2019 — ACM Transactions on Software Engineering and Methodology
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – technique | **Era:** Foundational
- **DOI:** 10.1145/3293455 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1145/3293455
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** REST API testing & fuzzing — **Taxonomy:** T1
- **Problem:** White-box, developer-side automated test generation for RESTful APIs, including creating prerequisite resources.
- **Claimed contribution:** Evolutionary white-box test generation with REST-aware smart sampling, implemented in the open-source EvoMaster tool.
- **Methods:** Evolutionary algorithm rewarded by code coverage and fault-finding; sampling templates based on REST design conventions.
- **Key findings (abstract-level):** 80 real bugs found in five open-source services; coverage was lower than existing manual test suites (author-reported limitation).
- **অন্তর্ভুক্তির কারণ:** White-box search-based REST testing-এর ভিত্তি; EvoMaster বহু পরবর্তী গবেষণার platform।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** White-box বনাম black-box তুলনা ও SQL/database handling-এর মতো open problem-এর উৎস।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: crossref)
- **Sources:** Discovered: OP008;CO001 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Full text OA যাচাই হয়নি (ACM)।

### C03 — Automated test generation for REST APIs: no time to rest yet

- **Authors:** Myeongsoo Kim; Qi Xin; Saurabh Sinha; Alessandro Orso
- **Year / Venue:** 2022 — Proceedings of the 31st ACM SIGSOFT International Symposium on Software Testing and Analysis
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – empirical (tool comparison) | **Era:** Recent
- **DOI:** 10.1145/3533767.3534401 | **arXiv:** 2204.08348
- **Canonical landing:** https://doi.org/10.1145/3533767.3534401
- **Direct PDF (verified):** https://arxiv.org/pdf/2204.08348
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** REST API testing & fuzzing — **Taxonomy:** T1
- **Problem:** REST API testing tools were evaluated on different benchmarks and metrics, making comparison difficult.
- **Claimed contribution:** Empirical comparison of 10 REST API testing tools on 20 real-world open-source services.
- **Methods:** Systematic tool selection; measured code coverage and unique failures.
- **Key findings (abstract-level):** Identifies strengths, weaknesses and limitations of tools and strategies (details only in full text).
- **অন্তর্ভুক্তির কারণ:** ক্ষেত্রের সবচেয়ে প্রভাবশালী tool-comparison; open problem-এর primary evidence।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Gap analysis-এর জন্য author-documented limitation পাওয়ার সম্ভাবনা বেশি।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP001;OP008;CO001 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** নির্দিষ্ট ফলাফল abstract-এ নেই; full text (arXiv 2204.08348) পড়তে হবে।

### C04 — Testing RESTful APIs: A Survey

- **Authors:** Amid Golmohammadi; Man Zhang; Andrea Arcuri
- **Year / Venue:** 2023 — ACM Transactions on Software Engineering and Methodology
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Survey / SLR | **Era:** Recent
- **DOI:** 10.1145/3617175 | **arXiv:** 2212.14604
- **Canonical landing:** https://doi.org/10.1145/3617175
- **Direct PDF (verified):** https://arxiv.org/pdf/2212.14604
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** REST API testing & fuzzing — **Taxonomy:** T1
- **Problem:** Fragmented research on automated verification of RESTful APIs.
- **Claimed contribution:** Review of 92 scientific articles on RESTful API testing with categorisation and challenges.
- **Methods:** Database search on seven databases, predefined criteria, snowballing.
- **Key findings (abstract-level):** Interest has grown since 2017; many open research challenges remain (author statement).
- **অন্তর্ভুক্তির কারণ:** REST testing-এর সবচেয়ে উদ্ধৃত সাম্প্রতিক survey; backward-citation-এর উৎস।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Taxonomy ও challenge-তালিকা cluster গঠনে কাজে লাগবে।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: crossref)
- **Sources:** Discovered: OP001;OP002;CO001 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Survey ২০২২ পর্যন্ত সাহিত্য কভার করে বলে ধারণা; LLM-যুগের কাজ অনুপস্থিত থাকতে পারে।

### C05 — Open Problems in Fuzzing RESTful APIs: A Comparison of Tools

- **Authors:** Man Zhang; Andrea Arcuri
- **Year / Venue:** 2023 — ACM Transactions on Software Engineering and Methodology
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – empirical (tool comparison) | **Era:** Recent
- **DOI:** 10.1145/3597205 | **arXiv:** 2205.05325
- **Canonical landing:** https://doi.org/10.1145/3597205
- **Direct PDF (verified):** https://arxiv.org/pdf/2205.05325
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** REST API testing & fuzzing — **Taxonomy:** T1
- **Problem:** Black-box REST fuzzers are rarely analysed for what code they actually fail to cover.
- **Claimed contribution:** Comparison of seven fuzzers on 18 open-source, 1 industrial and 1 artificial API with source-level analysis of uncovered code.
- **Methods:** Coverage measurement plus manual analysis of uncovered code regions.
- **Key findings (abstract-level):** Points to clear limitations of current fuzzers and lists concrete follow-up challenges (details in full text).
- **অন্তর্ভুক্তির কারণ:** 'Open problems' সরাসরি তালিকাভুক্ত — Class A gap-এর সম্ভাব্য উৎস।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** LLM-based tool এই open problem সমাধান করেছে কিনা — যাচাইয়ের ভিত্তিরেখা।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: crossref)
- **Sources:** Discovered: OP040 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Authors EvoMaster group থেকে — নিজস্ব tool-এর পক্ষে bias সম্ভাব্য (hypothesis)।

### C06 — Adaptive REST API Testing with Reinforcement Learning

- **Authors:** Myeongsoo Kim; Saurabh Sinha; Alessandro Orso
- **Year / Venue:** 2023 — 2023 38th IEEE/ACM International Conference on Automated Software Engineering (ASE)
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique | **Era:** Recent
- **DOI:** 10.1109/ase56229.2023.00218 | **arXiv:** 2309.04583
- **Canonical landing:** https://doi.org/10.1109/ase56229.2023.00218
- **Direct PDF (verified):** https://arxiv.org/pdf/2309.04583
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** REST API testing & fuzzing — **Taxonomy:** T1
- **Problem:** Testing tools treat all operations/parameters equally and lack prioritisation; struggle without response schemas.
- **Claimed contribution:** ARAT-RL: adaptive REST API testing using reinforcement learning to prioritise operations and parameters.
- **Methods:** RL-based prioritisation, dynamic request/response analysis, sampling-based feedback processing; ablation study.
- **Key findings (abstract-level):** Outperforms state-of-the-art tools on ten services in coverage, efficiency and fault finding (author claim).
- **অন্তর্ভুক্তির কারণ:** RL-ভিত্তিক REST testing-এর প্রতিনিধি; পরবর্তী কাজের baseline।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** RL বনাম LLM পদ্ধতির তুলনামূলক বিশ্লেষণে প্রয়োজন।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP040 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** ১০টি service-এ মূল্যায়ন — সাধারণীকরণ যাচাই দরকার।

### C07 — Enhancing REST API Testing with NLP Techniques

- **Authors:** Myeongsoo Kim; Davide Corradini; Saurabh Sinha; Alessandro Orso; Michele Pasqua; Rachel Tzoref-Brill; Mariano Ceccato
- **Year / Venue:** 2023 — Proceedings of the 32nd ACM SIGSOFT International Symposium on Software Testing and Analysis
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique | **Era:** Recent
- **DOI:** 10.1145/3597926.3598131 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1145/3597926.3598131
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** REST API testing & fuzzing — **Taxonomy:** T1 (+T4)
- **Problem:** Natural-language parts of OpenAPI specifications (examples, inter-parameter dependencies) are neglected by testing tools.
- **Claimed contribution:** NLPtoREST: extracts OpenAPI rules from human-readable descriptions and enhances the specification, with a validation step for spurious rules.
- **Methods:** NLP rule extraction + validation; evaluated with eight testing tools.
- **Key findings (abstract-level):** Extracts many relevant rules with high accuracy and significantly improves tools' performance (author claim).
- **অন্তর্ভুক্তির কারণ:** Specification enrichment ধারণার সূচনা; T1–T4 সংযোগকারী।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Spec quality কীভাবে testing প্রভাবিত করে — তার প্রমাণ।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP008;OP040 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** OA PDF যাচাই হয়নি।

### C08 — DeepREST: Automated Test Case Generation for REST APIs Exploiting Deep Reinforcement Learning

- **Authors:** Davide Corradini; Zeno Montolli; Michele Pasqua; Mariano Ceccato
- **Year / Venue:** 2024 — Proceedings of the 39th IEEE/ACM International Conference on Automated Software Engineering
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique | **Era:** Recent
- **DOI:** 10.1145/3691620.3695511 | **arXiv:** 2408.08594
- **Canonical landing:** https://doi.org/10.1145/3691620.3695511
- **Direct PDF (verified):** https://arxiv.org/pdf/2408.08594
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** REST API testing & fuzzing — **Taxonomy:** T1
- **Problem:** OAS lacks business-logic semantics such as implicit operation ordering and input constraints, limiting black-box testing.
- **Claimed contribution:** DeepREST: black-box REST testing using curiosity-driven deep reinforcement learning to uncover implicit constraints.
- **Methods:** Deep RL agent learns operation order and input generation; alternates exploration with mutation-based exploitation.
- **Key findings (abstract-level):** High coverage and fault detection, superior to a state-of-the-art baseline (author claim; abstract via Consensus CO001).
- **অন্তর্ভুক্তির কারণ:** Implicit/business-logic constraint — testing-এর গুরুত্বপূর্ণ সমস্যা।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Business-logic oracle/constraint gap যাচাইয়ে প্রাসঙ্গিক।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: Consensus search CO001 (full abstract; OpenAlex copy truncated))
- **Sources:** Discovered: CO001 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** OpenAlex abstract কাটা; পূর্ণ abstract Consensus থেকে। একটিমাত্র baseline-এর সঙ্গে তুলনা (abstract অনুযায়ী)।

### C09 — Leveraging Large Language Models to Improve REST API Testing

- **Authors:** Myeongsoo Kim; Tyler Stennett; Dhruv Shah; Saurabh Sinha; Alessandro Orso
- **Year / Venue:** 2024 — Proceedings of the 2024 ACM/IEEE 44th International Conference on Software Engineering: New Ideas and Emerging Results
- **Type / Review:** Conference paper — Peer-reviewed; ICSE NIER (new ideas) track | **Kind:** Original – technique (new-ideas track) | **Era:** Recent
- **DOI:** 10.1145/3639476.3639769 | **arXiv:** 2312.00894
- **Canonical landing:** https://doi.org/10.1145/3639476.3639769
- **Direct PDF (verified):** https://arxiv.org/pdf/2312.00894
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** REST API testing & fuzzing — **Taxonomy:** T1 (+T4)
- **Problem:** Existing rule-extraction techniques from specification text are limited and inaccurate.
- **Claimed contribution:** RESTGPT: uses LLMs to extract machine-interpretable rules and generate example values from OpenAPI descriptions.
- **Methods:** LLM prompting over specifications; augments the spec.
- **Key findings (abstract-level):** Outperforms existing techniques in rule extraction and value generation (author claim).
- **অন্তর্ভুক্তির কারণ:** REST testing-এ LLM প্রয়োগের প্রথম দিকের প্রভাবশালী কাজ; C10/C11-এর baseline।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** LLM-for-spec-enrichment ধারার ভিত্তি।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP001;OP040 | Verified: Crossref, OpenAlex
- **Confidence:** Medium — **অনিশ্চয়তা:** NIER (short paper) — মূল্যায়ন সীমিত হতে পারে।

### C10 — LlamaRestTest: Effective REST API Testing with Small Language Models

- **Authors:** Myeongsoo Kim; Saurabh Sinha; Alessandro Orso
- **Year / Venue:** 2025 — Proceedings of the ACM on Software Engineering
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – technique | **Era:** Recent
- **DOI:** 10.1145/3715737 | **arXiv:** 2501.08598
- **Canonical landing:** https://doi.org/10.1145/3715737
- **Direct PDF (verified):** https://arxiv.org/pdf/2501.08598
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** REST API testing & fuzzing — **Taxonomy:** T1 (+T4)
- **Problem:** LLM use in REST API testing is unexplored and large models are costly.
- **Claimed contribution:** LlamaRestTest: two fine-tuned, quantized Llama3-8B models for input generation and inter-parameter dependency discovery.
- **Methods:** Fine-tuning on mined REST example values/dependencies; 2/4/8-bit quantization; ablation; compared with RESTGPT, RESTler, MoRest, EvoMaster, ARAT-RL on 12 services.
- **Key findings (abstract-level):** Fine-tuned small models outperform much larger ones for dependency rules and valid inputs; higher coverage and more 500 errors than compared tools (author claim).
- **অন্তর্ভুক্তির কারণ:** Small LM-এ কার্যকারিতা — সীমিত infrastructure-এ গবেষণার সম্ভাব্যতা।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Feasible research direction নির্ধারণে গুরুত্বপূর্ণ (কম compute)।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: crossref)
- **Sources:** Discovered: OP001;OP042 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** ১২টি service; একই group-এর পূর্বের tool-এর সঙ্গে তুলনা।

### C11 — A Multi-Agent Approach for REST API Testing with Semantic Graphs and LLM-Driven Inputs

- **Authors:** Myeongsoo Kim; Tyler Stennett; Saurabh Sinha; Alessandro Orso
- **Year / Venue:** 2025 — 2025 IEEE/ACM 47th International Conference on Software Engineering (ICSE)
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique | **Era:** Recent
- **DOI:** 10.1109/icse55347.2025.00179 | **arXiv:** 2411.07098
- **Canonical landing:** https://doi.org/10.1109/icse55347.2025.00179
- **Direct PDF (verified):** https://arxiv.org/pdf/2411.07098
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** REST API testing & fuzzing — **Taxonomy:** T1
- **Problem:** Tools optimise test elements in isolation, lowering coverage and fault detection.
- **Claimed contribution:** AutoRestTest: multi-agent RL with a semantic property dependency graph and LLM value generation.
- **Methods:** Four cooperating agents (API, dependency, parameter, value), SPDG, MARL; ablation; 12 services.
- **Key findings (abstract-level):** Outperforms four leading black-box tools including RESTGPT-assisted ones; only tool to trigger a 500 error in Spotify (author claim).
- **অন্তর্ভুক্তির কারণ:** ICSE 2025 — REST testing-এ সাম্প্রতিক state-of-the-art দাবি।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** বর্তমান SOTA baseline হিসেবে প্রয়োজন।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP032;OP040;OP042 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Evaluation-এর পরিসর ও reproducibility full text-এ যাচাই।

### C13 — AGORA: Automated Generation of Test Oracles for REST APIs

- **Authors:** Juan C. Alonso; Sergio Segura; Antonio Ruiz-Cortés
- **Year / Venue:** 2023 — Proceedings of the 32nd ACM SIGSOFT International Symposium on Software Testing and Analysis
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique | **Era:** Recent
- **DOI:** 10.1145/3597926.3598114 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1145/3597926.3598114
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** REST API testing & fuzzing (test oracles) — **Taxonomy:** T1 (+T1)
- **Problem:** Test oracles of REST testing tools only detect crashes, regressions and spec violations.
- **Claimed contribution:** AGORA: generates test oracles by detecting likely invariants of API responses (extended Daikon; Beet instrumenter).
- **Methods:** Dynamic invariant detection over request/response logs; up to 105 invariant types.
- **Key findings (abstract-level):** 81.2% precision on 11 operations from 7 industrial APIs; detected 6 of 10 seeded errors; revealed 11 bugs in popular APIs (author-reported).
- **অন্তর্ভুক্তির কারণ:** Oracle problem — REST testing-এর মৌলিক দুর্বলতা।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Business-logic/semantic oracle gap-এর জন্য সরাসরি প্রমাণ।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP014;OP031 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** TOSEM 2025-এ সম্ভবত extended version আছে (10.1145/3726524) — PHASE B-তে সম্পর্ক যাচাই।

### C14 — EMB: A Curated Corpus of Web/Enterprise Applications And Library Support for Software Testing Research

- **Authors:** Andrea Arcuri; Man Zhang; Amid Golmohammadi; Asma Belhadi; Juan P. Galeotti; Bogdan Marculescu; Susruthan Seran
- **Year / Venue:** 2023 — 2023 IEEE Conference on Software Testing, Verification and Validation (ICST)
- **Type / Review:** Conference paper — Peer-reviewed; ICST (tool/benchmark paper; track Not verified) | **Kind:** Benchmark / dataset | **Era:** Recent
- **DOI:** 10.1109/icst57152.2023.00047 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1109/icst57152.2023.00047
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** REST API testing & fuzzing (benchmarks) — **Taxonomy:** T1 (+T2)
- **Problem:** No common, easy-to-run benchmark for comparing web-service fuzzers.
- **Claimed contribution:** EMB: curated corpus of web/enterprise applications (REST, GraphQL, RPC) with tooling for experiments.
- **Methods:** Corpus curation and library support (databases, auth, start/stop scripts).
- **Key findings (abstract-level):** Describes design and use; maintained since 2017 (abstract).
- **অন্তর্ভুক্তির কারণ:** Dataset availability — feasibility মূল্যায়নের মূল উপাদান।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** যেকোনো testing পরীক্ষার benchmark।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP037;OP040 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Corpus EvoMaster-এর জন্য তৈরি — selection bias সম্ভব।

### C15 — Specification and Automated Analysis of Inter-Parameter Dependencies in Web APIs

- **Authors:** Alberto Martin-Lopez; Sergio Segura; Carlos Muller; Antonio Ruiz-Cortes
- **Year / Venue:** 2022 — IEEE Transactions on Services Computing _(note: OpenAlex lists 2021 (likely early-access/online-first))_
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – technique | **Era:** Foundational
- **DOI:** 10.1109/tsc.2021.3050610 | **arXiv:** 2005.03320
- **Canonical landing:** https://doi.org/10.1109/tsc.2021.3050610
- **Direct PDF (verified):** https://arxiv.org/pdf/2005.03320
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** OpenAPI specification & inter-parameter dependencies — **Taxonomy:** T4 (+T1)
- **Problem:** OpenAPI cannot formally express inter-parameter dependencies.
- **Claimed contribution:** IDL (Inter-parameter Dependency Language), mapping to CSP, seven analysis operations, and a tool suite.
- **Methods:** DSL design, constraint programming.
- **Key findings (abstract-level):** Enables automated analysis of IDL specifications (abstract; no quantitative result stated).
- **অন্তর্ভুক্তির কারণ:** Inter-parameter dependency ধারণার formal ভিত্তি; পরবর্তী বহু LLM কাজ এটি লক্ষ্য করে।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Spec expressiveness gap — T1/T4 সংযোগ।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP013;OP014 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Online 2021, issue 2022 — বছর দুটোই রেকর্ড।

### C16 — Effective REST APIs Testing with Error Message Analysis

- **Authors:** Lixin Xu; Huayao Wu; Zhenyu Pan; Tongtong Xu; Shaohua Wang; Xintao Niu; Changhai Nie
- **Year / Venue:** 2025 — Proceedings of the ACM on Software Engineering
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – technique | **Era:** Recent
- **DOI:** 10.1145/3728964 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1145/3728964
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** REST API testing & fuzzing — **Taxonomy:** T1
- **Problem:** Testing approaches use status codes but ignore error-message content when inferring input constraints.
- **Claimed contribution:** EmRest: black-box testing that statistically analyses 4xx error messages to infer constraints and 5xx messages to focus effort.
- **Methods:** Combinatorial sampling of value-assignment strategies + statistical error-message analysis + mutation.
- **Key findings (abstract-level):** Higher operation coverage than SOTA in 50% of 16 APIs; 226 unique bugs undetected by others (author-reported).
- **অন্তর্ভুক্তির কারণ:** Error message-কে feedback হিসেবে ব্যবহার — নতুন signal।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** LLM ছাড়াই কার্যকর পদ্ধতি — তুলনার জন্য গুরুত্বপূর্ণ।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: crossref)
- **Sources:** Discovered: OP001;OP042 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** OA PDF যাচাই হয়নি।

### C18 — Detecting and Mitigating Flakiness in REST API Fuzzing

- **Authors:** Man Zhang; Chongyang Shen; Andrea Arcuri; Tao Yue
- **Year / Venue:** 2026 — arXiv (preprint) _(note: arXiv v1 2026; 1 version(s) on arXiv)_
- **Type / Review:** Preprint — Not peer-reviewed (no peer-reviewed version found as of 2026-10-19) | **Kind:** Original – empirical + technique | **Era:** Recent
- **DOI:** Not applicable | **arXiv:** 2603.28452
- **Canonical landing:** https://arxiv.org/abs/2603.28452
- **Direct PDF (verified):** https://arxiv.org/pdf/2603.28452
- **Access:** Open (arXiv)
- **Area:** REST API testing & fuzzing (flakiness) — **Taxonomy:** T1
- **Problem:** Flakiness in system-level REST API tests is under-explored compared to unit tests.
- **Claimed contribution:** Empirical study of flakiness in EvoMaster-generated tests on 36 APIs; taxonomy of sources from ~3000 failing tests; FlakyCatch.
- **Methods:** Empirical categorisation + detection/mitigation tool.
- **Key findings (abstract-level):** FlakyCatch effective for white-box and black-box fuzzers' tests (author claim).
- **অন্তর্ভুক্তির কারণ:** নতুন উদীয়মান সমস্যা (2026)।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Reproducibility/oracle reliability gap।
- **Metadata verification:** DataCite record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: datacite)
- **Sources:** Discovered: OP007 | Verified: DataCite, OpenAlex
- **Confidence:** Medium — **অনিশ্চয়তা:** Preprint (peer review হয়নি)।

### C19 — WFC/WFD: Web Fuzzing Commons, Dataset and Guidelines to Support Experimentation in REST API Fuzzing

- **Authors:** Omur Sahin; Man Zhang; Andrea Arcuri
- **Year / Venue:** 2025 — arXiv (preprint) _(note: arXiv v1 2025; 1 version(s) on arXiv)_
- **Type / Review:** Preprint — Not peer-reviewed (no peer-reviewed version found as of 2026-10-19) | **Kind:** Benchmark / dataset + guidelines | **Era:** Recent
- **DOI:** Not applicable | **arXiv:** 2509.01612
- **Canonical landing:** https://arxiv.org/abs/2509.01612
- **Direct PDF (verified):** https://arxiv.org/pdf/2509.01612
- **Access:** Open (arXiv)
- **Area:** REST API testing & fuzzing (benchmarks) — **Taxonomy:** T1 (+T3)
- **Problem:** Authentication handling, fault cataloguing and fair case-study selection hinder REST fuzzing research.
- **Claimed contribution:** WFC (libraries/schemas for auth & fault types) and WFD (36 APIs); comparison guidelines.
- **Methods:** Experiments with EvoMaster vs ARAT-RL, EmRest, LlamaRestTest, RESTler, Schemathesis.
- **Key findings (abstract-level):** Discusses common pitfalls in tool comparisons (details in full text).
- **অন্তর্ভুক্তির কারণ:** Evaluation methodology-র সমস্যা স্পষ্টভাবে নথিভুক্ত।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** পরীক্ষার নকশা ও baseline নির্বাচন।
- **Metadata verification:** DataCite record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: datacite)
- **Sources:** Discovered: OP007 | Verified: DataCite, OpenAlex
- **Confidence:** Medium — **অনিশ্চয়তা:** Preprint; EvoMaster group।

### C21 — GraphQL: A Systematic Mapping Study

- **Authors:** Antonio Quiña-Mera; Pablo Fernandez; José María García; Antonio Ruiz-Cortés
- **Year / Venue:** 2023 — ACM Computing Surveys _(note: OpenAlex lists 2022 (likely early-access/online-first))_
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Survey / systematic mapping | **Era:** Recent
- **DOI:** 10.1145/3561818 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1145/3561818
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** GraphQL — **Taxonomy:** T2
- **Problem:** State of GraphQL research and knowledge gaps.
- **Claimed contribution:** Systematic mapping of 84 primary studies (from 3,185).
- **Methods:** SMS with classification.
- **Key findings (abstract-level):** Adoption growing; need for more rigorous empirical evidence and studies on GraphQL components, especially consumption (author statement).
- **অন্তর্ভুক্তির কারণ:** GraphQL ক্ষেত্রের একমাত্র উচ্চ-মানের mapping study।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** GraphQL gap-এর author-documented উৎস।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: crossref)
- **Sources:** Discovered: OP009;OP010 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** OpenAlex 2022 বনাম Crossref 2023 — online বছর পার্থক্য।

### C22 — Random Testing and Evolutionary Testing for Fuzzing GraphQL APIs

- **Authors:** Asma Belhadi; Man Zhang; Andrea Arcuri
- **Year / Venue:** 2024 — ACM Transactions on the Web _(note: OpenAlex lists 2023 (likely early-access/online-first))_
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – technique | **Era:** Recent
- **DOI:** 10.1145/3609427 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1145/3609427
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** GraphQL — **Taxonomy:** T2
- **Problem:** Automated testing of GraphQL APIs.
- **Claimed contribution:** Framework for white-box (evolutionary) and black-box (random) GraphQL testing in EvoMaster.
- **Methods:** Schema extraction, evolutionary search vs random; 7 open-source + 31 online APIs.
- **Key findings (abstract-level):** Statistically significant improvement of evolutionary over random in white-box mode; black-box finds real faults (author-reported).
- **অন্তর্ভুক্তির কারণ:** GraphQL testing-এর প্রধান peer-reviewed technique।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** GraphQL testing baseline।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: crossref)
- **Sources:** Discovered: OP010;OP040 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Crossref issue বছর 2024; প্রথম প্রকাশ 2023 (OpenAlex)।

### C23 — A principled approach to GraphQL query cost analysis

- **Authors:** Alan Cha; Erik Wittern; Guillaume Baudart; James C. Davis; Louis Mandel; Jim A. Laredo
- **Year / Venue:** 2020 — Proceedings of the 28th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique (formal) | **Era:** Foundational
- **DOI:** 10.1145/3368089.3409670 | **arXiv:** 2009.05632
- **Canonical landing:** https://doi.org/10.1145/3368089.3409670
- **Direct PDF (verified):** https://arxiv.org/pdf/2009.05632
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** GraphQL (performance/security) — **Taxonomy:** T2
- **Problem:** Clients can send overly expensive GraphQL queries; providers lack principled cost estimation.
- **Claimed contribution:** Linear-time, provably correct static GraphQL query cost analysis supporting common conventions.
- **Methods:** Formal semantics; evaluated on a query-response corpus of two commercial APIs.
- **Key findings (abstract-level):** Consistently obtains tight upper bounds; existing static analyses over/under-estimate (author-reported).
- **অন্তর্ভুক্তির কারণ:** GraphQL security/performance-এর formal ভিত্তি।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** API DoS/resource management গবেষণা।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP046 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** OA PDF যাচাই হয়নি।

### C25 — White-Box Fuzzing RPC-Based APIs with EvoMaster: An Industrial Case Study

- **Authors:** Man Zhang; Andrea Arcuri; Yonggang Li; Yang Liu; Kaiming Xue
- **Year / Venue:** 2023 — ACM Transactions on Software Engineering and Methodology
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – technique + industrial study | **Era:** Recent
- **DOI:** 10.1145/3585009 | **arXiv:** 2208.12743
- **Canonical landing:** https://doi.org/10.1145/3585009
- **Direct PDF (verified):** https://arxiv.org/pdf/2208.12743
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** RPC/gRPC API testing — **Taxonomy:** T2 (+T9)
- **Problem:** No tool for automated testing of modern RPC-based APIs (gRPC, Thrift, Dubbo).
- **Claimed contribution:** First approach for white-box fuzzing of RPC APIs, schema specification + parser, integrated in EvoMaster and an industrial pipeline.
- **Methods:** Search-based testing with RPC-specific heuristics; 2 artificial + 4 industrial services; 50 more industrial APIs.
- **Key findings (abstract-level):** 41 real faults identified and fixed; significant coverage improvement (author-reported).
- **অন্তর্ভুক্তির কারণ:** gRPC/RPC-এর একমাত্র শক্তিশালী peer-reviewed প্রতিনিধি।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** REST-এর বাইরে API architecture কভারেজ।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: crossref)
- **Sources:** Discovered: OP040 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Industrial data — পুনরুৎপাদন সীমিত।

### C26 — REST vs GraphQL: A Controlled Experiment

- **Authors:** Gleison Brito; Marco Tulio Valente
- **Year / Venue:** 2020 — 2020 IEEE International Conference on Software Architecture (ICSA)
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – empirical (controlled experiment) | **Era:** Foundational
- **DOI:** 10.1109/icsa47634.2020.00016 | **arXiv:** 2003.04761
- **Canonical landing:** https://doi.org/10.1109/icsa47634.2020.00016
- **Direct PDF (verified):** https://arxiv.org/pdf/2003.04761
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** API architecture styles (REST vs GraphQL) — **Taxonomy:** T2
- **Problem:** Lack of empirical evidence on GraphQL vs REST implementation effort.
- **Claimed contribution:** Controlled experiment with 22 students implementing 8 queries.
- **Methods:** Controlled experiment, effort measured in time.
- **Key findings (abstract-level):** GraphQL required less effort (median 6 vs 9 minutes); gains larger for complex endpoints (author-reported).
- **অন্তর্ভুক্তির কারণ:** API architecture style তুলনায় একমাত্র rigorous experiment পাওয়া গেছে।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Architecture-comparison গবেষণার পদ্ধতিগত উদাহরণ।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP009 | Verified: Crossref, OpenAlex
- **Confidence:** Medium — **অনিশ্চয়তা:** ছোট নমুনা, শুধু ছাত্র — external validity সীমিত (analyst inference)।

### C27 — Checking Security Properties of Cloud Service REST APIs

- **Authors:** Vaggelis Atlidakis; Patrice Godefroid; Marina Polishchuk
- **Year / Venue:** 2020 — 2020 IEEE 13th International Conference on Software Testing, Validation and Verification (ICST)
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique | **Era:** Foundational
- **DOI:** 10.1109/icst46399.2020.00046 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1109/icst46399.2020.00046
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** API security testing — **Taxonomy:** T3 (+T1)
- **Problem:** Attackers can exploit vulnerabilities in REST APIs of cloud services.
- **Claimed contribution:** Four security rules for REST APIs and active property checkers in a stateful fuzzer.
- **Methods:** Extension of stateful fuzzing (RESTler) with modular checkers.
- **Key findings (abstract-level):** New bugs found in production Azure/Office365 services, all fixed (author-reported).
- **অন্তর্ভুক্তির কারণ:** REST API security testing-এর ভিত্তিমূলক কাজ।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Security oracle ধারণার উৎস।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP012 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** OA PDF যাচাই হয়নি; শুধু Microsoft services-এ মূল্যায়ন।

### C28 — Automated Black-Box Testing of Mass Assignment Vulnerabilities in RESTful APIs

- **Authors:** Davide Corradini; Michele Pasqua; Mariano Ceccato
- **Year / Venue:** 2023 — 2023 IEEE/ACM 45th International Conference on Software Engineering (ICSE)
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique | **Era:** Recent
- **DOI:** 10.1109/icse48619.2023.00213 | **arXiv:** 2301.01261
- **Canonical landing:** https://doi.org/10.1109/icse48619.2023.00213
- **Direct PDF (verified):** https://arxiv.org/pdf/2301.01261
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** API security testing — **Taxonomy:** T3 (+T1)
- **Problem:** Mass assignment vulnerabilities in RESTful APIs.
- **Claimed contribution:** Black-box detection: clustering to find read-only fields, template-based attack sequences, specific oracle.
- **Methods:** OpenAPI-driven test generation; evaluated on case studies in different languages.
- **Key findings (abstract-level):** Effective on seeded vulnerabilities with high accuracy (author claim).
- **অন্তর্ভুক্তির কারণ:** OWASP API Top-10 দুর্বলতার স্বয়ংক্রিয় শনাক্তকরণ (ICSE)।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Security testing-এ seeded বনাম বাস্তব vulnerability মূল্যায়ন প্রশ্ন।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP035 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Seeded vulnerability-তে মূল্যায়ন — বাস্তব কার্যকারিতা অনিশ্চিত (analyst inference)।

### C29 — Automated broken object-level authorization attack detection in REST APIs through OpenAPI to colored petri nets transformation

- **Authors:** Ailton Santos Filho; Ricardo J. Rodríguez; Eduardo L. Feitosa
- **Year / Venue:** 2025 — International Journal of Information Security
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – technique (formal) | **Era:** Recent
- **DOI:** 10.1007/s10207-024-00970-5 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1007/s10207-024-00970-5
- **Direct PDF (verified):** https://link.springer.com/content/pdf/10.1007/s10207-024-00970-5.pdf
- **Access:** Open access (publisher/repository PDF verified)
- **Area:** API security (authorization/BOLA) — **Taxonomy:** T3
- **Problem:** Detecting broken object-level authorization (BOLA) attacks in REST APIs.
- **Claimed contribution:** Transformation from OpenAPI to Colored Petri Nets and a tool for BOLA attack detection from server logs.
- **Methods:** Formal modelling + log/trace analysis; case study on a vulnerable web application.
- **Key findings (abstract-level):** >95% detection accuracy in proposed scenarios (author-reported).
- **অন্তর্ভুক্তির কারণ:** BOLA = OWASP API #1; formal পদ্ধতির প্রতিনিধি।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Authorization testing gap।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: crossref)
- **Sources:** Discovered: OP011 | Verified: Crossref, OpenAlex
- **Confidence:** Medium — **অনিশ্চয়তা:** একটি case study; তুলনামূলক baseline নেই (abstract অনুযায়ী)।

### C30 — Fuzzing for Detecting Access Policy Violations in REST APIs

- **Authors:** Andrea Arcuri; Omur Sahin; Man Zhang
- **Year / Venue:** 2025 — 2025 IEEE 36th International Symposium on Software Reliability Engineering (ISSRE)
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique | **Era:** Recent
- **DOI:** 10.1109/issre66568.2025.00025 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1109/issre66568.2025.00025
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** API security (authorization) — **Taxonomy:** T3 (+T1)
- **Problem:** REST fuzzers focus on crashes (5xx) and miss access-policy violations.
- **Claimed contribution:** Automated oracles for access-policy violations integrated in EvoMaster as a post-fuzzing security phase.
- **Methods:** Oracle design; artificial examples + 13 real-world APIs.
- **Key findings (abstract-level):** Detected security issues in some APIs (author-reported).
- **অন্তর্ভুক্তির কারণ:** Security oracle-কে fuzzer-এ সংযুক্ত করার সাম্প্রতিক কাজ।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Authorization oracle gap।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP007;OP031;OP042 | Verified: Crossref, OpenAlex
- **Confidence:** Medium — **অনিশ্চয়তা:** JSS 2026 extension আছে বলে মনে হয় (10.1016/j.jss.2026.113060) — সম্পর্ক যাচাই।

### C31 — Security testing of RESTful APIs: Approaches and research challenges

- **Authors:** J. Abinaya; P.Santhi Thilagam; K. Sivakumar; Alwyn Roshan Pais
- **Year / Venue:** 2026 — Computer Science Review _(note: Crossref issue year 2027 (article in press); OpenAlex year used; journal issue/volume year 2027)_
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Survey | **Era:** Recent
- **DOI:** 10.1016/j.cosrev.2026.101043 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1016/j.cosrev.2026.101043
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** API security testing — **Taxonomy:** T3
- **Problem:** Security testing approaches for RESTful APIs (title only).
- **Claimed contribution:** Not assessed (no abstract retrievable).
- **Methods:** Not assessed
- **Key findings (abstract-level):** Not assessed
- **অন্তর্ভুক্তির কারণ:** REST API security testing-এর সর্বশেষ survey (title অনুযায়ী) — সম্ভাব্য গুরুত্বপূর্ণ।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Security cluster-এর challenge-তালিকা।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Metadata only (abstract source: None)
- **Sources:** Discovered: OP032 | Verified: Crossref, OpenAlex
- **Confidence:** Low — **অনিশ্চয়তা:** শুধু metadata; abstract পাওয়া যায়নি; Crossref issue বছর 2027 (article-in-press)।

### C32 — Generating REST API Specifications through Static Analysis

- **Authors:** Ruikai Huang; Manish Motwani; Idel Martinez; Alessandro Orso
- **Year / Venue:** 2024 — Proceedings of the IEEE/ACM 46th International Conference on Software Engineering
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique | **Era:** Recent
- **DOI:** 10.1145/3597503.3639137 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1145/3597503.3639137
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** OpenAPI specification inference — **Taxonomy:** T4 (+T1)
- **Problem:** OpenAPI specifications are time-consuming to maintain and often incomplete or inconsistent.
- **Claimed contribution:** Respector: static and symbolic analysis generating REST API specifications from source code.
- **Methods:** Static + symbolic program analysis; 15 real-world APIs; precision/recall.
- **Key findings (abstract-level):** Promising precision/recall; found missing endpoints/parameters/constraints and spec–implementation inconsistencies; outperforms annotation- and invocation-based techniques (author claim).
- **অন্তর্ভুক্তির কারণ:** Spec inference-এর SOTA (ICSE 2024)।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Spec quality → testing/agents।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP036;OP040 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** OA PDF যাচাই হয়নি; Java-কেন্দ্রিক হতে পারে।

### C33 — Carving UI Tests to Generate API Tests and API Specification

- **Authors:** Rahulkrishna Yandrapally; Saurabh Sinha; Rachel Tzoref-Brill; Ali Mesbah
- **Year / Venue:** 2023 — 2023 IEEE/ACM 45th International Conference on Software Engineering (ICSE)
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique | **Era:** Recent
- **DOI:** 10.1109/icse48619.2023.00167 | **arXiv:** 2305.14692
- **Canonical landing:** https://doi.org/10.1109/icse48619.2023.00167
- **Direct PDF (verified):** https://arxiv.org/pdf/2305.14692
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** OpenAPI specification inference — **Taxonomy:** T4 (+T1)
- **Problem:** API testing tools need specifications which may be missing or inconsistent.
- **Claimed contribution:** Carving API tests and OpenAPI specs from UI test navigation, including endpoint inference via directed probing.
- **Methods:** Dynamic analysis via UI navigation; 7 web applications.
- **Key findings (abstract-level):** 98% precision, 56% recall in endpoint inference; coverage gains when added to tool-generated suites (author-reported).
- **অন্তর্ভুক্তির কারণ:** Dynamic spec inference-এর প্রতিনিধি।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Static (C32) বনাম dynamic বনাম LLM (C34, C35) তুলনা।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP013;OP014;OP040 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** ৭টি app — সাধারণীকরণ।

### C34 — Generating OpenAPI Specifications from Online API Documentation with Large Language Models

- **Authors:** Koren Lazar; Matan Vetzler; Kiran Kate; Jason Tsay; David Boaz; Himanshu Gupta; Avraham Shinnar; Rohith D Vallam; David Amid; Esther Goldbraich; Jim Laredo; Ateret Anaby Tavor
- **Year / Venue:** 2025 — Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 6: Industry Track)
- **Type / Review:** Conference paper — Peer-reviewed; ACL Industry Track | **Kind:** Original – technique (industry track) | **Era:** Recent
- **DOI:** 10.18653/v1/2025.acl-industry.18 | **arXiv:** 2507.05316
- **Canonical landing:** https://doi.org/10.18653/v1/2025.acl-industry.18
- **Direct PDF (verified):** https://aclanthology.org/2025.acl-industry.18.pdf | **Alternative legal OA:** https://arxiv.org/pdf/2507.05316
- **Access:** Open access (publisher/repository PDF verified)
- **Area:** OpenAPI specification inference — **Taxonomy:** T4 (+T8)
- **Problem:** API information online is unstructured HTML documentation, not machine-readable specs needed by agents.
- **Claimed contribution:** Framework (OASBuilder per arXiv title) converting documentation pages into OpenAPI specs with LLMs + rule-based algorithms.
- **Methods:** LLM + rule-based pipeline guided by documentation-page structure.
- **Key findings (abstract-level):** Generalises across hundreds of APIs; valid OpenAPI; deployed in an enterprise setting (author claim, from ACL Anthology abstract).
- **অন্তর্ভুক্তির কারণ:** Spec generation ও LLM agent-এর সংযোগ সরাসরি।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Agent-ready API গবেষণা।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: ACL Anthology landing page)
- **Sources:** Discovered: OP036;OP047 | Verified: Crossref, OpenAlex
- **Confidence:** Medium — **অনিশ্চয়তা:** Industry track; quantitative বিবরণ abstract-এ নেই।

### C35 — OOPS: Automated generation of REST API specification via LLMs

- **Authors:** Hao Chen; Yunchun Li; Chen Chen; Fengxu Lin; Wei Li
- **Year / Venue:** 2026 — Journal of Systems and Software
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – technique | **Era:** Recent
- **DOI:** 10.1016/j.jss.2026.112914 | **arXiv:** 2601.12735
- **Canonical landing:** https://doi.org/10.1016/j.jss.2026.112914
- **Direct PDF (verified):** https://arxiv.org/pdf/2601.12735
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** OpenAPI specification inference — **Taxonomy:** T4 (+T8)
- **Problem:** OAS generation approaches rely on technology-specific rules and experts; LLMs suffer context limits and hallucination.
- **Claimed contribution:** OOPS: technology-agnostic LLM-agent static analysis of server code for OAS generation.
- **Methods:** API dependency graph for context; multi-stage generation and self-refine; 12 APIs, 5 languages, 8 frameworks.
- **Key findings (abstract-level):** Average F1 >98% endpoint methods, 97% params/responses, 92% constraints (author-reported).
- **অন্তর্ভুক্তির কারণ:** LLM-ভিত্তিক spec inference-এর সাম্প্রতিক peer-reviewed কাজ।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** C32-এর সঙ্গে তুলনা।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: DataCite (arXiv 2601.12735))
- **Sources:** Discovered: OP013;OP021 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** ১২টি API — ছোট evaluation set।

### C36 — An Analysis of Public REST Web Service APIs

- **Authors:** Andy Neumann; Nuno Laranjeiro; Jorge Bernardino
- **Year / Venue:** 2021 — IEEE Transactions on Services Computing _(note: OpenAlex lists 2018 (likely early-access/online-first))_
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – empirical | **Era:** Foundational
- **DOI:** 10.1109/tsc.2018.2847344 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1109/tsc.2018.2847344
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** Web API design & ecosystem (empirical) — **Taxonomy:** T6
- **Problem:** Little concrete information on technical features of real REST APIs.
- **Claimed contribution:** Analysis of 500 public REST APIs from Alexa top-4000 sites.
- **Methods:** Manual/automated feature analysis; REST principle compliance.
- **Key findings (abstract-level):** Only 0.8% strictly comply with all REST principles; high diversity (author-reported).
- **অন্তর্ভুক্তির কারণ:** REST ecosystem-এর ভিত্তিমূলক empirical চিত্র।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Design quality ও 'REST assumption' যাচাই।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP006 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Early access 2018, issue 2021; ডেটা পুরোনো।

### C37 — A Systematic Review of API Evolution Literature

- **Authors:** Maxime Lamothe; Yann-Gaël Guéhéneuc; Weiyi Shang
- **Year / Venue:** 2021 — ACM Computing Surveys
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Survey / SLR | **Era:** Foundational
- **DOI:** 10.1145/3470133 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1145/3470133
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** API evolution & breaking changes — **Taxonomy:** T5
- **Problem:** Scattered literature on API evolution challenges.
- **Claimed contribution:** SLR on APIs and API evolution: trends, goals, methods, metrics, challenges.
- **Methods:** Systematic literature review.
- **Key findings (abstract-level):** Main remaining challenges: factors driving API changes; uniform benchmarks; impact across languages (author-stated).
- **অন্তর্ভুক্তির কারণ:** API evolution-এর সবচেয়ে প্রামাণিক SLR; Class A gap-এর উৎস।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Evolution cluster।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: crossref)
- **Sources:** Discovered: OP027;OP041 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** OA PDF যাচাই হয়নি।

### C38 — Microservice API Evolution in Practice: A Study on Strategies and Challenges

- **Authors:** Alexander Lercher; Johann Glock; Christian Macho; Martin Pinzger
- **Year / Venue:** 2024 — Journal of Systems and Software
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – empirical (qualitative) | **Era:** Recent
- **DOI:** 10.1016/j.jss.2024.112110 | **arXiv:** 2311.08175
- **Canonical landing:** https://doi.org/10.1016/j.jss.2024.112110
- **Direct PDF (verified):** https://arxiv.org/pdf/2311.08175
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** API evolution & breaking changes (microservices) — **Taxonomy:** T5 (+T9)
- **Problem:** Reasons behind microservice API evolution challenges are unknown.
- **Claimed contribution:** 17 interviews in 11 companies; six strategies, six challenges; two core problems (organizational coupling, consumer lock-in).
- **Methods:** Semi-structured interviews, grounded-theory open coding.
- **Key findings (abstract-level):** Proposes automating change-impact analysis and change communication as open research directions (author-stated).
- **অন্তর্ভুক্তির কারণ:** Web/microservice API evolution-এ author-documented research direction।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Class A gap-এর সরাসরি উৎস।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP002;OP015;OP023 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Qualitative; ১১টি কোম্পানি।

### C39 — Differential regression testing for REST APIs

- **Authors:** Patrice Godefroid; Daniel Lehmann; Marina Polishchuk
- **Year / Venue:** 2020 — Proceedings of the 29th ACM SIGSOFT International Symposium on Software Testing and Analysis
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique | **Era:** Foundational
- **DOI:** 10.1145/3395363.3397374 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1145/3395363.3397374
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** API evolution & breaking changes — **Taxonomy:** T5 (+T1)
- **Problem:** Detecting breaking changes across REST API versions (spec and service).
- **Claimed contribution:** Differential regression testing for REST APIs using RESTler-generated inputs.
- **Methods:** Differential testing across versions; handling non-determinism.
- **Key findings (abstract-level):** 14 regressions across 17 Azure networking API versions (5 spec, 9 service) (author-reported).
- **অন্তর্ভুক্তির কারণ:** Web API breaking-change detection-এর প্রধান technique।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Evolution × testing সংযোগ।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP028;CO002 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** শুধু Azure-এ মূল্যায়ন।

### C40 — Understanding the Impact of APIs Behavioral Breaking Changes on Client Applications

- **Authors:** Dhanushka Jayasuriya; Valerio Terragni; Jens Dietrich; Kelly Blincoe
- **Year / Venue:** 2024 — Proceedings of the ACM on Software Engineering
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – empirical | **Era:** Recent
- **DOI:** 10.1145/3643782 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1145/3643782
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** API evolution & breaking changes — **Taxonomy:** T5
- **Problem:** Behavioral (semantic) breaking changes in library updates are understudied.
- **Claimed contribution:** Large study: 30,548 dependencies; updates run against client test suites; taxonomy of effects.
- **Methods:** Automated dependency updates + client test execution.
- **Key findings (abstract-level):** 2.30% of updates had behavioral BCs; most in non-major updates violating semver (author-reported).
- **অন্তর্ভুক্তির কারণ:** Behavioral BC — syntactic BC-এর বাইরে নতুন দিক।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Evolution cluster; LLM-যুগের সঙ্গে সংযোগ সম্ভব।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: crossref)
- **Sources:** Discovered: OP016 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Java/Maven-এ সীমাবদ্ধ।

### C41 — Breaking bad? Semantic versioning and impact of breaking changes in Maven Central

- **Authors:** Lina Ochoa; Thomas Degueule; Jean-Rémy Falleri; Jurgen Vinju
- **Year / Venue:** 2022 — Empirical Software Engineering
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – empirical (replication) | **Era:** Recent
- **DOI:** 10.1007/s10664-021-10052-y | **arXiv:** 2110.07889
- **Canonical landing:** https://doi.org/10.1007/s10664-021-10052-y
- **Direct PDF (verified):** https://hal.science/hal-03378089v1/document | **Alternative legal OA:** https://arxiv.org/pdf/2110.07889
- **Access:** Open access (publisher/repository PDF verified)
- **Area:** API evolution & breaking changes — **Taxonomy:** T5
- **Problem:** Prior study claimed BCs are widespread regardless of semver in Maven Central.
- **Claimed contribution:** External differentiated replication with Maracas tool; 119,879 upgrades, 293,817 clients.
- **Methods:** Bytecode static analysis; replication.
- **Key findings (abstract-level):** 83.4% of upgrades comply with semver; only 7.9% clients affected — contrasts the original study (author-reported).
- **অন্তর্ভুক্তির কারণ:** Contradicting evidence-এর উৎকৃষ্ট উদাহরণ (prompt-এর 'contradiction' চাহিদা)।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Gap validation-এ সতর্কতা।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: DataCite (arXiv 2110.07889))
- **Sources:** Discovered: OP016 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Abstract arXiv version থেকে; journal version-এ সংখ্যা ভিন্ন হতে পারে।

### C43 — Web API evolution patterns: A usage-driven approach

- **Authors:** Rediana Koçi; Xavier Franch; Petar Jovanovic; Alberto Abelló
- **Year / Venue:** 2023 — Journal of Systems and Software
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – technique | **Era:** Recent
- **DOI:** 10.1016/j.jss.2023.111609 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1016/j.jss.2023.111609
- **Direct PDF (verified):** https://upcommons.upc.edu/server/api/core/bitstreams/58775b55-bbc6-47a3-8db4-0e209560f47b/content
- **Access:** Open access (publisher/repository PDF verified)
- **Area:** API evolution & breaking changes — **Taxonomy:** T5
- **Problem:** Web API evolution should be driven by consumers' actual usage.
- **Claimed contribution:** Process-mining, pattern-based method to detect usage patterns implying API changes.
- **Methods:** Usage-log analysis; two real-world WAPIs (FIB-UPC, DHIS2).
- **Key findings (abstract-level):** Consumer/provider feedback confirmed effectiveness (author-reported, qualitative).
- **অন্তর্ভুক্তির কারণ:** Usage-driven web API evolution — বিরল দৃষ্টিভঙ্গি।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Web API evolution cluster।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP015;OP041 | Verified: Crossref, OpenAlex
- **Confidence:** Medium — **অনিশ্চয়তা:** দুটি case; quantitative মূল্যায়ন সীমিত।

### C44 — A First Look at the Deprecation of RESTful APIs: An Empirical Study

- **Authors:** Jerin Yasmin; Yuan Tian; Jinqiu Yang
- **Year / Venue:** 2020 — 2020 IEEE International Conference on Software Maintenance and Evolution (ICSME)
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – empirical + tool | **Era:** Foundational
- **DOI:** 10.1109/icsme46990.2020.00024 | **arXiv:** 2008.12808
- **Canonical landing:** https://doi.org/10.1109/icsme46990.2020.00024
- **Direct PDF (verified):** https://arxiv.org/pdf/2008.12808
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** API evolution (deprecation) — **Taxonomy:** T5
- **Problem:** RESTful API deprecation practices are unstudied (prior work: Java/Android).
- **Claimed contribution:** RADA analyzer and study of 2,224 OpenAPI specs of 1,368 APIs from APIs.guru.
- **Methods:** Automated spec mining.
- **Key findings (abstract-level):** Several severe deprecation-related problems in existing RESTful APIs (author-reported).
- **অন্তর্ভুক্তির কারণ:** REST deprecation-এর প্রথম empirical study; APIs.guru dataset ব্যবহার।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Web API evolution; open dataset।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP044 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** —

### C45 — Automatic Detection of Five API Documentation Smells: Practitioners’ Perspectives

- **Authors:** Junaed Younus Khan; Md. Tawkat Islam Khondaker; Gias Uddin; Anindya Iqbal
- **Year / Venue:** 2021 — 2021 IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER)
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – empirical + technique | **Era:** Foundational
- **DOI:** 10.1109/saner50967.2021.00037 | **arXiv:** 2102.08486
- **Canonical landing:** https://doi.org/10.1109/saner50967.2021.00037
- **Direct PDF (verified):** https://arxiv.org/pdf/2102.08486
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** API documentation quality — **Taxonomy:** T6
- **Problem:** No automatic detection of API documentation smells.
- **Claimed contribution:** Catalog of five smells, benchmark of 1,000 documentation units, practitioner survey (21), classifiers.
- **Methods:** Manual labelling; rule-based, shallow and deep ML (BERT).
- **Key findings (abstract-level):** BERT F1 0.75–0.97; 95.2% developers report productivity harm (author-reported).
- **অন্তর্ভুক্তির কারণ:** Documentation quality-র প্রধান কাজ; benchmark আছে।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Docs cluster; LLM-যুগে পুনর্মূল্যায়নের সুযোগ (hypothesis)।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP018 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Java docs; web API docs-এ প্রযোজ্যতা অজানা।

### C46 — Do RESTful API design rules have an impact on the understandability of Web APIs?

- **Authors:** Justus Bogner; Sebastian Kotstein; Timo Pfaff
- **Year / Venue:** 2023 — Empirical Software Engineering
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – empirical (controlled experiment) | **Era:** Recent
- **DOI:** 10.1007/s10664-023-10367-y | **arXiv:** 2305.07346
- **Canonical landing:** https://doi.org/10.1007/s10664-023-10367-y
- **Direct PDF (verified):** https://link.springer.com/content/pdf/10.1007/s10664-023-10367-y.pdf | **Alternative legal OA:** https://arxiv.org/pdf/2305.07346
- **Access:** Open access (publisher/repository PDF verified)
- **Area:** REST API design quality — **Taxonomy:** T6
- **Problem:** Empirical evidence for RESTful API design rules is lacking.
- **Claimed contribution:** Controlled web experiment with 105 participants on 12 design rules.
- **Methods:** Hybrid crossover/between-subjects design.
- **Key findings (abstract-level):** Violations worse for 11 of 12 rules in comprehension (author-reported).
- **অন্তর্ভুক্তির কারণ:** Design rule-এর প্রমাণভিত্তিক মূল্যায়ন — rigorous design।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Design quality cluster।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: crossref)
- **Sources:** Discovered: OP024 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Snippet-ভিত্তিক — বাস্তব API-তে সাধারণীকরণ।

### C47 — RESTRuler: Towards Automatically Identifying Violations of RESTful Design Rules in Web APIs

- **Authors:** Justus Bogner; Sebastian Kotstein; Daniel Abajirov; Timothy Ernst; Manuel Merkel
- **Year / Venue:** 2024 — 2024 IEEE 21st International Conference on Software Architecture (ICSA)
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique + tool | **Era:** Recent
- **DOI:** 10.1109/icsa59870.2024.00020 | **arXiv:** 2402.13710
- **Canonical landing:** https://doi.org/10.1109/icsa59870.2024.00020
- **Direct PDF (verified):** https://arxiv.org/pdf/2402.13710
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** REST API design quality — **Taxonomy:** T6
- **Problem:** Practitioners struggle to identify REST design rule violations.
- **Claimed contribution:** RESTRuler: static analysis of OpenAPI for 14 rules (some NLP-based).
- **Methods:** Benchmark: 2,300+ public OpenAPI descriptions; 111 expert-constructed violations.
- **Key findings (abstract-level):** Precision 91%, recall 68% (per-rule variation) (author-reported).
- **অন্তর্ভুক্তির কারণ:** C46-এর প্রমাণকে tool-এ রূপান্তর।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Design quality; LLM দিয়ে recall বাড়ানোর সম্ভাবনা (hypothesis)।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP024 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Prototype।

### C48 — API Governance at Scale

- **Authors:** Mak Ahmad; J. J. Geewax; Andrew Macvean; David Karger; Kwan-Liu Ma
- **Year / Venue:** 2024 — Proceedings of the 46th International Conference on Software Engineering: Software Engineering in Practice
- **Type / Review:** Conference paper — Peer-reviewed; ICSE SEIP (in practice) track | **Kind:** Industrial – action research | **Era:** Recent
- **DOI:** 10.1145/3639477.3639713 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1145/3639477.3639713
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** API governance — **Taxonomy:** T6
- **Problem:** Scaling API governance in a large organization.
- **Claimed contribution:** Google's AIPs, API Linter, API Readability program; mixed-methods evaluation.
- **Methods:** Action research; survey + interviews.
- **Key findings (abstract-level):** Positive sentiment; newer API producers reported worse sentiment (author-reported).
- **অন্তর্ভুক্তির কারণ:** API governance-এর একমাত্র শক্তিশালী industrial প্রমাণ।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Governance cluster।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP018 | Verified: Crossref, OpenAlex
- **Confidence:** Medium — **অনিশ্চয়তা:** একটি কোম্পানি; OA PDF যাচাই হয়নি।

### C49 — A Systematic Evaluation of Static API-Misuse Detectors

- **Authors:** Sven Amann; Hoan Anh Nguyen; Sarah Nadi; Tien N. Nguyen; Mira Mezini
- **Year / Venue:** 2019 — IEEE Transactions on Software Engineering _(note: OpenAlex lists 2018 (likely early-access/online-first))_
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – empirical (benchmark evaluation) | **Era:** Foundational
- **DOI:** 10.1109/tse.2018.2827384 | **arXiv:** 1712.00242
- **Canonical landing:** https://doi.org/10.1109/tse.2018.2827384
- **Direct PDF (verified):** https://arxiv.org/pdf/1712.00242
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** API misuse detection — **Taxonomy:** T7
- **Problem:** Capabilities/limitations of static API-misuse detectors are unknown.
- **Claimed contribution:** MUC classification, MUBenchPipe benchmark, comparative evaluation with author validation.
- **Methods:** Benchmark-based evaluation; root-cause analysis.
- **Key findings (abstract-level):** Extremely low precision and recall; frequency-based 'deviation = misuse' assumption is a root cause (author-reported).
- **অন্তর্ভুক্তির কারণ:** API misuse-এর ভিত্তিমূলক মূল্যায়ন।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Misuse cluster; LLM-যুগে তুলনার baseline।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP005 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Online 2018, issue 2019।

### C50 — Detecting Misuse of Security APIs: A Systematic Review

- **Authors:** Zahra Mousavi; Chadni Islam; Muhammad Ali Babar; Alsharif Abuadbba; Kristen Moore
- **Year / Venue:** 2025 — ACM Computing Surveys
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Survey / SLR | **Era:** Recent
- **DOI:** 10.1145/3735968 | **arXiv:** 2306.08869
- **Canonical landing:** https://doi.org/10.1145/3735968
- **Direct PDF (verified):** https://arxiv.org/pdf/2306.08869
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** API misuse detection (security APIs) — **Taxonomy:** T7
- **Problem:** Detection of security API misuse.
- **Claimed contribution:** SLR of 69 articles: 6 API types, 30 misuses, detection techniques, 10 measures, 9 benchmarks.
- **Methods:** SLR.
- **Key findings (abstract-level):** Lack of coverage in several areas; need standardized evaluation (author-stated).
- **অন্তর্ভুক্তির কারণ:** Misuse cluster-এর সাম্প্রতিক SLR।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Class A gap উৎস।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: crossref)
- **Sources:** Discovered: OP027;OP041 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** OA PDF যাচাই হয়নি।

### C51 — Generating API Parameter Security Rules with LLM for API Misuse Detection

- **Authors:** Jinghua Liu; Yi Yang; Kai Chen; Miaoqian Lin
- **Year / Venue:** 2025 — Proceedings 2025 Network and Distributed System Security Symposium
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique | **Era:** Recent
- **DOI:** 10.14722/ndss.2025.230465 | **arXiv:** 2409.09288
- **Canonical landing:** https://doi.org/10.14722/ndss.2025.230465
- **Direct PDF (verified):** https://www.ndss-symposium.org/wp-content/uploads/2025-465-paper.pdf | **Alternative legal OA:** https://arxiv.org/pdf/2409.09288
- **Access:** Open access (publisher/repository PDF verified)
- **Area:** API misuse detection (LLM-assisted) — **Taxonomy:** T7
- **Problem:** Manual/heuristic generation of API parameter security rules (APSRs) misses rules.
- **Claimed contribution:** GPTAid: LLM-generated APSRs validated by execution feedback and refined by code differential analysis.
- **Methods:** LLM generation of rules and right/violation code, dynamic execution filtering; 200 APIs from 8 libraries.
- **Key findings (abstract-level):** Abstract truncated in OpenAlex; quantitative results Not verified.
- **অন্তর্ভুক্তির কারণ:** LLM-কে misuse rule-generation-এ ব্যবহার (NDSS)।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Misuse × LLM।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Partial abstract (abstract source: openalex)
- **Sources:** Discovered: OP038 | Verified: Crossref, OpenAlex
- **Confidence:** Medium — **অনিশ্চয়তা:** Abstract অসম্পূর্ণ; full text (NDSS OA) পড়তে হবে।

### C52 — An Investigation into Misuse of Java Security APIs by Large Language Models

- **Authors:** Zahra Mousavi; Chadni Islam; Kristen Moore; Alsharif Abuadbba; M. Ali Babar
- **Year / Venue:** 2024 — Proceedings of the 19th ACM Asia Conference on Computer and Communications Security
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – empirical | **Era:** Recent
- **DOI:** 10.1145/3634737.3661134 | **arXiv:** 2404.03823
- **Canonical landing:** https://doi.org/10.1145/3634737.3661134
- **Direct PDF (verified):** https://arxiv.org/pdf/2404.03823
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** API misuse in LLM-generated code — **Taxonomy:** T7 (+T8)
- **Problem:** Trustworthiness of LLM-generated code using Java security APIs.
- **Claimed contribution:** 48 tasks × 5 security APIs; automated + manual misuse detection on ChatGPT code.
- **Methods:** Empirical evaluation (30 attempts per task).
- **Key findings (abstract-level):** ~70% of instances contain misuse; 20 misuse types; ~half of tasks at 100% (author-reported).
- **অন্তর্ভুক্তির কারণ:** LLM-generated code-এ API misuse-এর quantitative প্রমাণ।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Misuse × LLM।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP038 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** শুধু ChatGPT ও Java; model সংস্করণ পুরোনো।

### C53 — Identifying and Mitigating API Misuse in Large Language Models

- **Authors:** Terry Yue Zhuo; Junda He; Jiamou Sun; Zhenchang Xing; David Lo; John Grundy; Xiaoning Du
- **Year / Venue:** 2026 — IEEE Transactions on Software Engineering
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – empirical + technique | **Era:** Recent
- **DOI:** 10.1109/tse.2026.3651566 | **arXiv:** 2503.22821
- **Canonical landing:** https://doi.org/10.1109/tse.2026.3651566
- **Direct PDF (verified):** https://arxiv.org/pdf/2503.22821
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** API misuse in LLM-generated code — **Taxonomy:** T7 (+T8)
- **Problem:** API misuse in LLM-generated code (method selection and parameters).
- **Claimed contribution:** Large study (3,209 method-level, 3,492 parameter-level misuses), four misuse types, Dr.Fix repair.
- **Methods:** Manual annotation; three LLMs (StarCoder-7B, Qwen2.5-Coder-7B, Copilot); Python & Java.
- **Key findings (abstract-level):** Persistent hallucination and intent misalignment; Dr.Fix gains up to 38.4 BLEU, 40% exact match (author-reported).
- **অন্তর্ভুক্তির কারণ:** TSE 2026 — সর্বশেষ বড় study।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Misuse × LLM; hallucination সংযোগ।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP038 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** BLEU repair-এর জন্য দুর্বল metric হতে পারে (analyst inference)।

### C55 — Gorilla: Large Language Model Connected with Massive APIs

- **Authors:** Shishir Patil; Tianjun Zhang; Xin Wang; Joseph Gonzalez
- **Year / Venue:** 2024 — Advances in Neural Information Processing Systems 37
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique + benchmark | **Era:** Recent
- **DOI:** 10.52202/079017-4020 | **arXiv:** 2305.15334
- **Canonical landing:** https://doi.org/10.52202/079017-4020
- **Direct PDF (verified):** https://arxiv.org/pdf/2305.15334
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** LLM tool use & API calling — **Taxonomy:** T8 (+T6)
- **Problem:** LLMs hallucinate API calls and generate wrong arguments.
- **Claimed contribution:** Gorilla (fine-tuned LLaMA) with retriever; APIBench (HuggingFace, TorchHub, TensorHub).
- **Methods:** Fine-tuning with retrieval-aware training.
- **Key findings (abstract-level):** Surpasses GPT-4 on writing API calls; adapts to doc changes; reduces hallucination (author claim).
- **অন্তর্ভুক্তির কারণ:** API calling-এর landmark।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** API hallucination ও documentation-change adaptation।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP006;OP019;OP020 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** নাম-সংঘাত: C68-এর benchmark-ও 'APIBench' নামে — আলাদা।

### C56 — ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs

- **Authors:** Yujia Qin; Shihao Liang; Yining Ye; Kunlun Zhu; Lan Yan; Yaxi Lu; Yankai Lin; Xin Cong; Xiangru Tang; Bill Qian; Sihan Zhao; Lauren Hong; Runchu Tian; Ruobing Xie; Jie Zhou; Mark Gerstein; Dahai Li; Zhiyuan Liu; Maosong Sun
- **Year / Venue:** 2024 — International Conference on Learning Representations (ICLR 2024) _(note: arXiv v1 2023; 2 version(s) on arXiv)_
- **Type / Review:** Conference paper — Peer-reviewed (ICLR proceedings page verified) | **Kind:** Original – technique + dataset | **Era:** Recent
- **DOI:** Not applicable | **arXiv:** 2307.16789
- **Canonical landing:** https://proceedings.iclr.cc/paper_files/paper/2024/hash/28e50ee5b72e90b50e7196fde8ea260e-Abstract-Conference.html
- **Direct PDF (verified):** https://proceedings.iclr.cc/paper_files/paper/2024/file/28e50ee5b72e90b50e7196fde8ea260e-Paper-Conference.pdf | **Alternative legal OA:** https://arxiv.org/pdf/2307.16789
- **Access:** Open (ICLR proceedings + arXiv)
- **Area:** LLM tool use & API calling — **Taxonomy:** T8
- **Problem:** Open-source LLMs are weak at using real-world APIs.
- **Claimed contribution:** ToolBench (16,464 RapidAPI REST APIs), DFSDT reasoning, ToolEval, ToolLLaMA, API retriever.
- **Methods:** ChatGPT-generated instructions/solution paths; fine-tuning LLaMA.
- **Key findings (abstract-level):** ToolLLaMA comparable to ChatGPT; generalises to unseen APIs (author claim).
- **অন্তর্ভুক্তির কারণ:** বাস্তব REST API-ভিত্তিক tool-use dataset-এর landmark (ICLR 2024)।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Agent-API cluster; StableToolBench-এর ভিত্তি।
- **Metadata verification:** DataCite record OK; venue verified on official proceedings page; OpenAlex record MISMATCH (title similarity 0.26) — OpenAlex data not used; retraction status Not assessed (no Crossref/usable OpenAlex record)
- **Evidence level:** Abstract (abstract source: DataCite (arXiv 2307.16789))
- **Sources:** Discovered: DataCite lookup after OP029 miss | Verified: DataCite
- **Confidence:** High — **অনিশ্চয়তা:** OpenAlex-এ arXiv DOI ভুল শিরোনামে map করা — DataCite/ICLR থেকে যাচাই করা হয়েছে।

### C57 — API-Bank: A Comprehensive Benchmark for Tool-Augmented LLMs

- **Authors:** Minghao Li; Yingxiu Zhao; Bowen Yu; Feifan Song; Hangyu Li; Haiyang Yu; Zhoujun Li; Fei Huang; Yongbin Li
- **Year / Venue:** 2023 — Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Benchmark | **Era:** Recent
- **DOI:** 10.18653/v1/2023.emnlp-main.187 | **arXiv:** 2304.08244
- **Canonical landing:** https://doi.org/10.18653/v1/2023.emnlp-main.187
- **Direct PDF (verified):** https://aclanthology.org/2023.emnlp-main.187.pdf | **Alternative legal OA:** https://arxiv.org/pdf/2304.08244
- **Access:** Open access (publisher/repository PDF verified)
- **Area:** LLM tool use & API calling (benchmark) — **Taxonomy:** T8
- **Problem:** How effective are LLMs at using tools and what obstacles remain.
- **Claimed contribution:** API-Bank: runnable system with 73 tools, 314 dialogues/753 calls; training set 1,888 dialogues; Lynx model.
- **Methods:** Benchmark + fine-tuning; error analysis.
- **Key findings (abstract-level):** GPT-4 excels in planning; Lynx +26 pts over Alpaca (author-reported).
- **অন্তর্ভুক্তির কারণ:** Tool-use benchmark-এর প্রধান peer-reviewed উৎস।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Evaluation methodology।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP019;OP020 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** —

### C58 — StableToolBench: Towards Stable Large-Scale Benchmarking on Tool Learning of Large Language Models

- **Authors:** Zhicheng Guo; Sijie Cheng; Hao Wang; Shihao Liang; Yujia Qin; Peng Li; Zhiyuan Liu; Maosong Sun; Yang Liu
- **Year / Venue:** 2024 — Findings of the Association for Computational Linguistics ACL 2024
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Benchmark | **Era:** Recent
- **DOI:** 10.18653/v1/2024.findings-acl.664 | **arXiv:** 2403.07714
- **Canonical landing:** https://doi.org/10.18653/v1/2024.findings-acl.664
- **Direct PDF (verified):** https://aclanthology.org/2024.findings-acl.664.pdf | **Alternative legal OA:** https://arxiv.org/pdf/2403.07714
- **Access:** Open access (publisher/repository PDF verified)
- **Area:** LLM tool use & API calling (benchmark) — **Taxonomy:** T8 (+T5)
- **Problem:** Tool-learning benchmarks are unstable because real API status changes.
- **Claimed contribution:** StableToolBench: virtual API server (cache + simulators) and stable evaluation.
- **Methods:** Caching, API simulation, GPT-4-based evaluator.
- **Key findings (abstract-level):** Demonstrates stability (author claim).
- **অন্তর্ভুক্তির কারণ:** API instability/evolution-কে benchmark সমস্যা হিসেবে নথিভুক্ত করে।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** API evolution × agent সংযোগের প্রমাণ।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP019 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** LLM-as-judge evaluation-এর validity প্রশ্ন (analyst inference)।

### C59 — RestGPT: Connecting Large Language Models with Real-World RESTful APIs

- **Authors:** Yifan Song; Weimin Xiong; Dawei Zhu; Wenhao Wu; Han Qian; Mingbo Song; Hailiang Huang; Cheng Li; Ke Wang; Rong Yao; Ye Tian; Sujian Li
- **Year / Venue:** 2023 — arXiv (preprint) _(note: arXiv v1 2023; 2 version(s) on arXiv)_
- **Type / Review:** Preprint — Not peer-reviewed (no peer-reviewed version found as of 2026-10-19) | **Kind:** Original – technique + benchmark | **Era:** Recent
- **DOI:** Not applicable | **arXiv:** 2306.06624
- **Canonical landing:** https://arxiv.org/abs/2306.06624
- **Direct PDF (verified):** https://arxiv.org/pdf/2306.06624
- **Access:** Open (arXiv)
- **Area:** LLM agents over REST APIs — **Taxonomy:** T8 (+T4)
- **Problem:** Connecting LLMs to real-world RESTful APIs for complex instructions.
- **Claimed contribution:** RestGPT (coarse-to-fine planning, API executor) and RestBench.
- **Methods:** LLM planning; two real-world scenarios with gold paths.
- **Key findings (abstract-level):** Impressive results and robustness (author claim).
- **অন্তর্ভুক্তির কারণ:** REST API-কে সরাসরি agent-এর লক্ষ্য হিসেবে ধরা।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Agent-facing REST API।
- **Metadata verification:** DataCite record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: datacite)
- **Sources:** Discovered: OP032 | Verified: DataCite, OpenAlex
- **Confidence:** Medium — **অনিশ্চয়তা:** Preprint (peer-reviewed venue পাওয়া যায়নি)।

### C60 — On Mitigating Code LLM Hallucinations with API Documentation

- **Authors:** Nihal Jain; Robert Kwiatkowski; Baishakhi Ray; Murali Krishna Ramanathan; Varun Kumar
- **Year / Venue:** 2025 — 2025 IEEE/ACM 47th International Conference on Software Engineering: Software Engineering in Practice (ICSE-SEIP)
- **Type / Review:** Conference paper — Peer-reviewed; ICSE SEIP (in practice) track | **Kind:** Original – empirical + technique | **Era:** Recent
- **DOI:** 10.1109/icse-seip66354.2025.00027 | **arXiv:** 2407.09726
- **Canonical landing:** https://doi.org/10.1109/icse-seip66354.2025.00027
- **Direct PDF (verified):** https://arxiv.org/pdf/2407.09726
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** LLM API hallucination — **Taxonomy:** T8 (+T6)
- **Problem:** Code LLMs hallucinate APIs, especially low-frequency ones.
- **Claimed contribution:** CloudAPIBench; analysis by API frequency; selective Documentation Augmented Generation.
- **Methods:** Benchmark + retrieval triggering via API index or model confidence.
- **Key findings (abstract-level):** GPT-4o 38.58% valid low-frequency invocations; DAG helps low-frequency but hurts high-frequency with weak retrievers; +8.20% absolute with selective DAG (author-reported).
- **অন্তর্ভুক্তির কারণ:** API hallucination ও documentation-এর সম্পর্ক — industrial (ICSE-SEIP)।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Documentation × LLM সংযোগ।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP021 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Cloud SDK API-তে সীমাবদ্ধ।

### C61 — Tool learning with large language models: a survey

- **Authors:** Changle Qu; Sunhao Dai; Xiaochi Wei; Hengyi Cai; Shuaiqiang Wang; Dawei Yin; Jun Xu; Ji-rong Wen
- **Year / Venue:** 2025 — Frontiers of Computer Science
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Survey | **Era:** Recent
- **DOI:** 10.1007/s11704-024-40678-2 | **arXiv:** 2405.17935
- **Canonical landing:** https://doi.org/10.1007/s11704-024-40678-2
- **Direct PDF (verified):** https://arxiv.org/pdf/2405.17935
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** LLM tool use & API calling (survey) — **Taxonomy:** T8
- **Problem:** Fragmented tool-learning literature.
- **Claimed contribution:** Survey organised by planning, selection, calling, response generation; benchmarks summary.
- **Methods:** Literature survey.
- **Key findings (abstract-level):** Discusses challenges and future directions (author statement).
- **অন্তর্ভুক্তির কারণ:** LLM tool-use-এর প্রধান survey।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Agent cluster-এর taxonomy।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: DataCite (arXiv 2405.17935))
- **Sources:** Discovered: OP019;OP043 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Survey পদ্ধতি systematic কিনা অনিশ্চিত।

### C62 — Model Context Protocol (MCP): Landscape, Security Threats, and Future Research Directions

- **Authors:** Xinyi Hou; Yanjie Zhao; Shenao Wang; Haoyu Wang
- **Year / Venue:** 2026 — ACM Transactions on Software Engineering and Methodology
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Survey / systematic study | **Era:** Recent
- **DOI:** 10.1145/3796519 | **arXiv:** 2503.23278
- **Canonical landing:** https://doi.org/10.1145/3796519
- **Direct PDF (verified):** https://arxiv.org/pdf/2503.23278
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** Model Context Protocol (agent-facing APIs) — **Taxonomy:** T8 (+T3)
- **Problem:** Architecture and security of the Model Context Protocol.
- **Claimed contribution:** MCP server lifecycle (4 phases, 16 activities), threat taxonomy (4 attacker types, 16 scenarios), case studies, safeguards.
- **Methods:** Systematic study + case studies.
- **Key findings (abstract-level):** Proposes safeguards and research directions (author statement).
- **অন্তর্ভুক্তির কারণ:** MCP — নতুন API paradigm; TOSEM।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Agent-facing API security।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: crossref)
- **Sources:** Discovered: OP039 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** OA PDF যাচাই হয়নি।

### C63 — Model Context Protocol (MCP) at First Glance: Studying the Security and Maintainability of MCP Servers

- **Authors:** Mohammed Mehedi Hasan; Hao Li; Emad Fallahzadeh; Gopi Krishnan Rajbahadur; Bram Adams; Ahmed E. Hassan
- **Year / Venue:** 2026 — ACM Transactions on Software Engineering and Methodology
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – empirical | **Era:** Recent
- **DOI:** 10.1145/3814959 | **arXiv:** 2506.13538
- **Canonical landing:** https://doi.org/10.1145/3814959
- **Direct PDF (verified):** https://arxiv.org/pdf/2506.13538
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** Model Context Protocol (agent-facing APIs) — **Taxonomy:** T8 (+T3)
- **Problem:** Health, security and maintainability of MCP servers.
- **Claimed contribution:** Large study of 1,899 open-source MCP servers with hybrid static analysis.
- **Methods:** Health metrics, general static analyser + MCP-specific scanner.
- **Key findings (abstract-level):** 8 vulnerability types (3 overlap traditional); 7.2% general vulns, 5.5% tool poisoning; 66% code smells (author-reported).
- **অন্তর্ভুক্তির কারণ:** MCP-এর প্রথম বড় empirical study (TOSEM)।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** MCP-specific detection-এর প্রয়োজন author-documented।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: crossref)
- **Sources:** Discovered: OP039 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Snapshot-ভিত্তিক — দ্রুত পরিবর্তনশীল ecosystem।

### C64 — From REST to MCP: An Empirical Study of API Wrapping and Automated Server Generation for LLM Agents

- **Authors:** Meriem Mastouri; Emna Ksontini; Amine Barrak; Wael Kessentini
- **Year / Venue:** 2025 — arXiv (preprint) _(note: arXiv v1 2025; 4 version(s) on arXiv)_
- **Type / Review:** Preprint — Not peer-reviewed (no peer-reviewed version found as of 2026-10-19) | **Kind:** Original – empirical + technique | **Era:** Recent
- **DOI:** Not applicable | **arXiv:** 2507.16044
- **Canonical landing:** https://arxiv.org/abs/2507.16044
- **Direct PDF (verified):** https://arxiv.org/pdf/2507.16044
- **Access:** Open (arXiv)
- **Area:** Model Context Protocol (agent-facing APIs) — **Taxonomy:** T8 (+T4)
- **Problem:** Relationship between MCP tool interfaces and underlying REST APIs is uncharacterised.
- **Claimed contribution:** Study of 116 official MCP servers; OpenAPI pairing; AutoMCP generation pipeline with spec repair.
- **Methods:** Four RQs; generation from 80 OpenAPI contracts.
- **Key findings (abstract-level):** 88.6% REST-backed; 92% bare wrappers; median 19% of operations exposed; generation 76% → 94.2% after repair (author-reported, v4).
- **অন্তর্ভুক্তির কারণ:** REST ↔ agent সেতুবন্ধন — T4 ও T8 সরাসরি যুক্ত।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Spec quality → agent tool success-এর প্রমাণ।
- **Metadata verification:** DataCite record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: datacite)
- **Sources:** Discovered: OP032 | Verified: DataCite, OpenAlex
- **Confidence:** Medium — **অনিশ্চয়তা:** Preprint; arXiv version-এর মধ্যে শিরোনাম ও সংখ্যা পরিবর্তিত হয়েছে (v1 বনাম v4)।

### C65 — Microservices testing: A systematic literature review

- **Authors:** Francisco Ponce; Roberto Verdecchia; Breno Miranda; Jacopo Soldani
- **Year / Venue:** 2025 — Information and Software Technology
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Survey / SLR | **Era:** Recent
- **DOI:** 10.1016/j.infsof.2025.107870 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1016/j.infsof.2025.107870
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** Microservice API testing — **Taxonomy:** T9
- **Problem:** Testing microservice systems.
- **Claimed contribution:** SLR of 74 primary studies classified by SWEBOK testing taxonomy (from partial abstract).
- **Methods:** SLR.
- **Key findings (abstract-level):** Dominated by early-stage proposals; need empirical validation and industry-grade benchmarks (partial abstract via web search).
- **অন্তর্ভুক্তির কারণ:** Microservice testing-এর সাম্প্রতিক SLR।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Microservice cluster।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Partial abstract (abstract source: Partial abstract via WebSearch snippet of institutional repository (flore.unifi.it))
- **Sources:** Discovered: OP027 | Verified: Crossref, OpenAlex
- **Confidence:** Medium — **অনিশ্চয়তা:** Abstract আংশিক (institutional repository snippet)।

### C66 — SAINT: Service-level Integration Test Generation with Program Analysis and LLM-based Agents

- **Authors:** Rangeet Pan; Raju Pavuluri; Ruikai Huang; Tyler Stennett; Rahul Krishna; Alessandro Orso; Saurabh Sinha
- **Year / Venue:** 2026 — Proceedings of the 2026 IEEE/ACM 48th International Conference on Software Engineering
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – technique | **Era:** Recent
- **DOI:** 10.1145/3744916.3773185 | **arXiv:** 2511.13305
- **Canonical landing:** https://doi.org/10.1145/3744916.3773185
- **Direct PDF (verified):** https://arxiv.org/pdf/2511.13305
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** Microservice API testing — **Taxonomy:** T9 (+T1)
- **Problem:** Service-level tests for enterprise Java apps without OpenAPI specs, beyond fuzzing.
- **Claimed contribution:** SAINT: static analysis + LLM agents for endpoint and scenario-based tests.
- **Methods:** Endpoint model, operation dependency graph, agentic plan/act/reflect; 8 Java apps incl. proprietary; developer survey.
- **Key findings (abstract-level):** Effective coverage, fault detection and scenario generation (author claim).
- **অন্তর্ভুক্তির কারণ:** ICSE 2026 — agentic testing-এর সর্বশেষ।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Spec-less testing।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP032 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** Proprietary app — আংশিক reproducibility।

### C67 — API Traffic Anomaly Detection in Microservice Architecture

- **Authors:** M Sowmya; Ankith J Rai; V Spoorthi; Md Irfan; Prasad B Honnavalli; S Nagasundari
- **Year / Venue:** 2023 — 2023 IEEE/ACM 23rd International Symposium on Cluster, Cloud and Internet Computing Workshops (CCGridW)
- **Type / Review:** Conference paper — Peer-reviewed; Workshop (CCGridW) | **Kind:** Original – technique (workshop) | **Era:** Recent
- **DOI:** 10.1109/ccgridw59191.2023.00044 | **arXiv:** Not found
- **Canonical landing:** https://doi.org/10.1109/ccgridw59191.2023.00044
- **Direct PDF (verified):** Not verified
- **Access:** Paywalled or not verified; landing page only — unrestricted full text NOT verified
- **Area:** API monitoring & anomaly detection — **Taxonomy:** T11 (+T3)
- **Problem:** Detecting anomalous API traffic in microservice architectures.
- **Claimed contribution:** API-TAD: ML-based two-level (general/app-specific) anomaly detection.
- **Methods:** Machine learning on API traffic.
- **Key findings (abstract-level):** Abstract gives no quantitative results.
- **অন্তর্ভুক্তির কারণ:** API monitoring ক্ষেত্রের প্রতিনিধি — উচ্চ-মানের বিকল্প পাওয়া যায়নি।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** দুর্বল-প্রমাণ ক্ষেত্রের নির্দেশক।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP025 | Verified: Crossref, OpenAlex
- **Confidence:** Low — **অনিশ্চয়তা:** Workshop paper; evaluation বিবরণ অজানা।

### C68 — Revisiting, Benchmarking and Exploring API Recommendation: How Far Are We?

- **Authors:** Yun Peng; Shuqing Li; Wenwei Gu; Yichen Li; Wenxuan Wang; Cuiyun Gao; Michael R. Lyu
- **Year / Venue:** 2023 — IEEE Transactions on Software Engineering _(note: OpenAlex lists 2022 (likely early-access/online-first))_
- **Type / Review:** Journal article — Peer-reviewed | **Kind:** Original – empirical (benchmark) | **Era:** Recent
- **DOI:** 10.1109/tse.2022.3197063 | **arXiv:** 2112.12653
- **Canonical landing:** https://doi.org/10.1109/tse.2022.3197063
- **Direct PDF (verified):** https://arxiv.org/pdf/2112.12653
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** API recommendation — **Taxonomy:** T10 (+T8)
- **Problem:** Lack of uniform task definition and benchmark for API recommendation.
- **Claimed contribution:** Benchmark (named APIBench) for query-based and code-based API recommendation; study of 11 approaches + 4 IDEs.
- **Methods:** Benchmarking.
- **Key findings (abstract-level):** Insights on query reformulation, data sources, low-resource, user-defined APIs (author statement).
- **অন্তর্ভুক্তির কারণ:** API recommendation-এর প্রধান benchmark।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Recommendation → LLM tool retrieval-এর স্থানান্তর বোঝা।
- **Metadata verification:** Crossref DOI record OK; OpenAlex consistent; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: openalex)
- **Sources:** Discovered: OP041 | Verified: Crossref, OpenAlex
- **Confidence:** High — **অনিশ্চয়তা:** নাম-সংঘাত: Gorilla-র APIBench (C55) থেকে আলাদা। Online 2022, issue 2023।

### C69 — LLMs Meet Library Evolution: Evaluating Deprecated API Usage in LLM-Based Code Completion

- **Authors:** Chong Wang; Kaifeng Huang; Jian Zhang; Yebo Feng; Lyuye Zhang; Yang Liu; Xin Peng
- **Year / Venue:** 2025 — 2025 IEEE/ACM 47th International Conference on Software Engineering (ICSE)
- **Type / Review:** Conference paper — Peer-reviewed | **Kind:** Original – empirical + technique | **Era:** Recent
- **DOI:** 10.1109/icse55347.2025.00245 | **arXiv:** 2406.09834
- **Canonical landing:** https://doi.org/10.1109/icse55347.2025.00245
- **Direct PDF (verified):** https://arxiv.org/pdf/2406.09834
- **Access:** Publisher version not verified as OA; legal preprint PDF verified on arXiv (version may differ from published)
- **Area:** API evolution x LLM code generation — **Taxonomy:** T5 (+T8)
- **Problem:** LLM-based code completion may use deprecated APIs due to library evolution.
- **Claimed contribution:** First evaluation of deprecated API usage: 7 LLMs, 145 API mappings, 8 Python libraries, 28,125 prompts; ReplaceAPI and InsertPrompt baselines.
- **Methods:** Empirical evaluation by model, prompt, library; lightweight fixes.
- **Key findings (abstract-level):** Reveals status quo and root causes (details in full text) (author statement).
- **অন্তর্ভুক্তির কারণ:** API evolution × LLM — সেতুবন্ধন ক্ষেত্র (ICSE 2025)।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Cross-cluster gap অনুসন্ধানের কেন্দ্রীয় paper।
- **Metadata verification:** Crossref DOI record OK; no retraction/correction notice found
- **Evidence level:** Abstract (abstract source: DataCite (arXiv 2406.09834))
- **Sources:** Discovered: CR001 | Verified: Crossref
- **Confidence:** High — **অনিশ্চয়তা:** Python library-তে সীমাবদ্ধ।

### C70 — Learning Evolving Tools for Large Language Models

- **Authors:** Guoxin Chen; Zhong Zhang; Xin Cong; Fangda Guo; Yesai Wu; Yankai Lin; Wenzheng Feng; Yasheng Wang
- **Year / Venue:** 2025 — International Conference on Learning Representations (ICLR 2025) _(note: arXiv v1 2024; 4 version(s) on arXiv)_
- **Type / Review:** Conference paper — Peer-reviewed (ICLR proceedings page verified) | **Kind:** Original – technique + benchmark | **Era:** Recent
- **DOI:** Not applicable | **arXiv:** 2410.06617
- **Canonical landing:** https://proceedings.iclr.cc/paper_files/paper/2025/hash/d8d1d325f822e07d16866780cc23deb2-Abstract-Conference.html
- **Direct PDF (verified):** https://proceedings.iclr.cc/paper_files/paper/2025/file/d8d1d325f822e07d16866780cc23deb2-Paper-Conference.pdf | **Alternative legal OA:** https://arxiv.org/pdf/2410.06617
- **Access:** Open (ICLR proceedings + arXiv)
- **Area:** API evolution x LLM tool use — **Taxonomy:** T5 (+T8)
- **Problem:** Tools/APIs change over time; LLMs trained on static environments fail.
- **Claimed contribution:** ToolEVO (MCTS-based exploration, self-reflection, self-updating tool usage) and ToolQA-D benchmark.
- **Methods:** Monte Carlo Tree Search in dynamic environments.
- **Key findings (abstract-level):** Effective and stable under tool variability (author claim).
- **অন্তর্ভুক্তির কারণ:** API evolution × agent tool use — সরাসরি সংযোগ (ICLR 2025)।
- **সম্ভাব্য গবেষণা-প্রাসঙ্গিকতা:** Cross-cluster gap।
- **Metadata verification:** DataCite record OK; venue verified on official proceedings page; retraction status Not assessed (no Crossref/usable OpenAlex record)
- **Evidence level:** Abstract (abstract source: datacite)
- **Sources:** Discovered: CO003 (Consensus) + WebSearch venue check | Verified: DataCite
- **Confidence:** High — **অনিশ্চয়তা:** ToolQA-D synthetic variability কিনা — যাচাই দরকার।

## Screened-out (যাচাইকৃত কিন্তু PHASE A তালিকা থেকে বাদ)

| Temp ID | Title | বাদের কারণ |
|---|---|---|
| C12 | KAT: Dependency-Aware Automated API Testing with Large Language Models | KAT (ICST 2024): C09/C10/C11-এর একই LLM-for-REST-testing ধারা; Katalon-এর industrial tool, তুলনামূলক কম স্বতন্ত্র অবদান। PHASE B-তে প্রয়োজনে পুনর্বিবেচনা। |
| C17 | Introducing Black-Box Fuzz Testing for REST APIs in Industry: Challenges and Solutions | Volkswagen industrial experience report (ICST 2025): ছোট experience paper; EvoMaster group-এর ৭টি paper ইতিমধ্যে আছে (concentration bias কমাতে বাদ)। তবে real-world challenge-এর উৎস হিসেবে PHASE D-তে gap-validation-এ উপযোগী। |
| C20 | RESTTESTGEN: Automated Black-Box Testing of RESTful APIs | RESTTESTGEN (ICST 2020): foundational, কিন্তু surveys (C04) ও tool comparisons (C03, C05)-এ আবৃত; পরবর্তী extended version (STVR 2022, ICSME 2022) আছে। |
| C24 | BenGQL: An Extensible Benchmarking Framework for Automated GraphQL Testing | BenGQL (ASE 2025 tool/demo track): benchmark resource হিসেবে মূল্যবান কিন্তু গবেষণা অবদান সীমিত; dataset-তালিকায় উল্লেখ থাকবে। |
| C42 | When and How to Make Breaking Changes | When and How to Make Breaking Changes (TOSEM 2021): ecosystem-norm/সামাজিক দিক; API engineering technique-এর বাইরে। Library evolution-এ C37/C40/C41 যথেষ্ট। |
| C54 | Toolformer: Language Models Can Teach Themselves to Use Tools | Toolformer (NeurIPS 2023): landmark, কিন্তু 'API' এখানে calculator/search-এর মতো toy tool; API engineering প্রশ্নের সঙ্গে সংযোগ দুর্বল। C55/C56 বাস্তব API নিয়ে কাজ করে। Landmark হিসেবে excluded-list-এ রাখা হলো, পুনঃঅন্তর্ভুক্তিযোগ্য। |

এগুলোর পূর্ণ verification record `raw/verify/<ID>.json`-এ সংরক্ষিত; PHASE B-তে প্রয়োজনে পুনর্বিবেচনা করা যাবে।
