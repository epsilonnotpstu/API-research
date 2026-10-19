# Final Paper Catalog — PHASE B (Human-Download Catalog)

**প্রস্তুতকারী:** Claude | **তারিখ:** 2026-10-19 | **উৎস:** `final_papers.csv` (script-generated: `00_protocol/scripts/final_build.py`)

**মোট নির্বাচিত:** 38 | Cluster: T1 8, T2 3, T3 4, T4 4, T5 6, T6 3, T7 3, T8 5, T9 2 | Provenance: Codex only 4, Both 15, Claude only 19 | Access: OA (verified) 11, Preprint OA (verified arXiv) 21, Not verified 6

> **Link নীতি:** *Paper Link* = canonical landing (DOI বা proceedings/arXiv abs)। *PDF Link* = শুধু আমাদের নিজস্ব probe-এ `%PDF` signature-সহ যাচাইকৃত URL। “Preprint OA” মানে বৈধ arXiv/repository কপি — published version থেকে ভিন্ন হতে পারে। “Not verified” হলে নিচের subsection-এ unverified candidate route দেওয়া আছে (যেমন ACM PDF যা script-এ 403 দেয় কিন্তু browser-এ খুলতে পারে)।

> **প্রমাণের স্তর:** সব বর্ণনা abstract-ভিত্তিক; কোনো full text পড়া হয়নি (PHASE C-র কাজ)।

## মূল তালিকা

| ID | Paper Title | Year | Venue | Research Area | Main Contribution | Importance | Paper Link | PDF Link | Access |
|---|---|---|---|---|---|---|---|---|---|
| P001 | Online testing of RESTful APIs: promises and challenges | 2022 | Proceedings of the 30th ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering | T1 — REST/Web API testing & fuzzing | Automated online testing of 13 industrial APIs for 15 days (>1M tests, 254 bugs) | High | [Link](https://doi.org/10.1145/3540250.3549144) | [PDF](https://idus.us.es/bitstreams/0592cee5-2a9b-407f-bde5-8a2941fa41d8/download) | OA (verified) |
| P002 | Testing RESTful APIs: A Survey | 2023 | ACM Transactions on Software Engineering and Methodology | T1 — REST/Web API testing & fuzzing | Review of 92 studies on RESTful API testing; taxonomy and open challenges | High | [Link](https://doi.org/10.1145/3617175) | [PDF](https://arxiv.org/pdf/2212.14604) | Preprint OA (verified arXiv) |
| P003 | Open Problems in Fuzzing RESTful APIs: A Comparison of Tools | 2023 | ACM Transactions on Software Engineering and Methodology | T1 — REST/Web API testing & fuzzing | Compares 7 REST fuzzers on 20 APIs and analyses uncovered code to list open problems | High | [Link](https://doi.org/10.1145/3597205) | [PDF](https://arxiv.org/pdf/2205.05325) | Preprint OA (verified arXiv) |
| P004 | Automated test generation for REST APIs: no time to rest yet | 2022 | Proceedings of the 31st ACM SIGSOFT International Symposium on Software Testing and Analysis | T1 — REST/Web API testing & fuzzing | Empirical comparison of 10 REST testing tools on 20 real services (coverage, failures) | High | [Link](https://doi.org/10.1145/3533767.3534401) | [PDF](https://arxiv.org/pdf/2204.08348) | Preprint OA (verified arXiv) |
| P005 | LlamaRestTest: Effective REST API Testing with Small Language Models | 2025 | Proceedings of the ACM on Software Engineering | T1 — REST/Web API testing & fuzzing | Fine-tuned, quantized small LMs (Llama3-8B) for REST test inputs and parameter dependencies | High | [Link](https://doi.org/10.1145/3715737) | [PDF](https://arxiv.org/pdf/2501.08598) | Preprint OA (verified arXiv) |
| P006 | RESTler: Stateful REST API Fuzzing | 2019 | 2019 IEEE/ACM 41st International Conference on Software Engineering (ICSE) | T1 — REST/Web API testing & fuzzing | RESTler: first stateful REST API fuzzer using producer–consumer dependencies | High | [Link](https://doi.org/10.1109/icse.2019.00083) | [PDF](https://www.microsoft.com/en-us/research/uploads/prod/2021/03/RESTler.pdf) | OA (verified) |
| P007 | A Multi-Agent Approach for REST API Testing with Semantic Graphs and LLM-Driven Inputs | 2025 | 2025 IEEE/ACM 47th International Conference on Software Engineering (ICSE) | T1 — REST/Web API testing & fuzzing | AutoRestTest: multi-agent RL + semantic dependency graph + LLM value generation | High | [Link](https://doi.org/10.1109/icse55347.2025.00179) | [PDF](https://arxiv.org/pdf/2411.07098) | Preprint OA (verified arXiv) |
| P008 | AGORA: Automated Generation of Test Oracles for REST APIs | 2023 | Proceedings of the 32nd ACM SIGSOFT International Symposium on Software Testing and Analysis | T1 — REST/Web API testing & fuzzing | AGORA: test oracles for REST APIs via likely-invariant detection (extended Daikon) | High | [Link](https://doi.org/10.1145/3597926.3598114) | **Not verified** | Not verified |
| P009 | GraphQL: A Systematic Mapping Study | 2023 | ACM Computing Surveys | T2 — GraphQL, RPC/gRPC & architecture styles | Systematic mapping of 84 GraphQL studies; identifies evidence gaps | High | [Link](https://doi.org/10.1145/3561818) | [PDF](https://idus.us.es/bitstreams/85cae9eb-bcbe-45f8-845d-cce7736e862b/download) | OA (verified) |
| P010 | A principled approach to GraphQL query cost analysis | 2020 | Proceedings of the 28th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering | T2 — GraphQL, RPC/gRPC & architecture styles | Provably correct linear-time static cost analysis for GraphQL queries | High | [Link](https://doi.org/10.1145/3368089.3409670) | [PDF](https://arxiv.org/pdf/2009.05632) | Preprint OA (verified arXiv) |
| P011 | White-Box Fuzzing RPC-Based APIs with EvoMaster: An Industrial Case Study | 2023 | ACM Transactions on Software Engineering and Methodology | T2 — GraphQL, RPC/gRPC & architecture styles | First white-box fuzzing approach for RPC (gRPC/Thrift/Dubbo) APIs; 41 industrial faults | Medium | [Link](https://doi.org/10.1145/3585009) | [PDF](https://arxiv.org/pdf/2208.12743) | Preprint OA (verified arXiv) |
| P012 | Automated Black-Box Testing of Mass Assignment Vulnerabilities in RESTful APIs | 2023 | 2023 IEEE/ACM 45th International Conference on Software Engineering (ICSE) | T3 — API security & authorization | Black-box detection of mass-assignment vulnerabilities from OpenAPI specs | High | [Link](https://doi.org/10.1109/icse48619.2023.00213) | [PDF](https://arxiv.org/pdf/2301.01261) | Preprint OA (verified arXiv) |
| P013 | Mobile Application Web API Reconnaissance: Web-to-Mobile Inconsistencies & Vulnerabilities | 2018 | 2018 IEEE Symposium on Security and Privacy (SP) | T3 — API security & authorization | WARDroid: static analysis of Android apps to find web-API input-validation inconsistencies | Medium | [Link](https://doi.org/10.1109/sp.2018.00039) | [PDF](https://ieeexplore.ieee.org/ielx7/8418581/8418583/08418636.pdf) | OA (verified) |
| P014 | Automated broken object-level authorization attack detection in REST APIs through OpenAPI to colored petri nets transformation | 2025 | International Journal of Information Security | T3 — API security & authorization | OpenAPI → Coloured Petri Nets for detecting BOLA attacks from server logs | Medium | [Link](https://doi.org/10.1007/s10207-024-00970-5) | [PDF](https://link.springer.com/content/pdf/10.1007/s10207-024-00970-5.pdf) | OA (verified) |
| P015 | Fuzzing for Detecting Access Policy Violations in REST APIs | 2025 | 2025 IEEE 36th International Symposium on Software Reliability Engineering (ISSRE) | T3 — API security & authorization | Automated oracles for access-policy violations integrated into a REST fuzzer | High | [Link](https://doi.org/10.1109/issre66568.2025.00025) | **Not verified** | Not verified |
| P016 | Specification and Automated Analysis of Inter-Parameter Dependencies in Web APIs | 2022 | IEEE Transactions on Services Computing | T4 — API specification inference & enrichment | IDL: a language and CSP-based analysis for inter-parameter dependencies in web APIs | High | [Link](https://doi.org/10.1109/tsc.2021.3050610) | [PDF](https://arxiv.org/pdf/2005.03320) | Preprint OA (verified arXiv) |
| P017 | OOPS: Automated generation of REST API specification via LLMs | 2026 | Journal of Systems and Software | T4 — API specification inference & enrichment | OOPS: technology-agnostic LLM-agent static analysis to generate OpenAPI specs | High | [Link](https://doi.org/10.1016/j.jss.2026.112914) | [PDF](https://arxiv.org/pdf/2601.12735) | Preprint OA (verified arXiv) |
| P018 | Generating REST API Specifications through Static Analysis | 2024 | Proceedings of the IEEE/ACM 46th International Conference on Software Engineering | T4 — API specification inference & enrichment | Respector: static + symbolic analysis generating REST API specs from source code | High | [Link](https://doi.org/10.1145/3597503.3639137) | **Not verified** | Not verified |
| P019 | RestPi: Path-Sensitive Type Inference for REST APIs | 2025 | Proceedings of the ACM on Programming Languages | T4 — API specification inference & enrichment | RestPi: path-sensitive type inference generating REST API response types (Ruby) | Medium | [Link](https://doi.org/10.1145/3763055) | **Not verified** | Not verified |
| P020 | Microservice API Evolution in Practice: A Study on Strategies and Challenges | 2024 | Journal of Systems and Software | T5 — API evolution, breaking changes & deprecation | 17 interviews in 11 companies: microservice API evolution strategies and challenges | High | [Link](https://doi.org/10.1016/j.jss.2024.112110) | [PDF](https://arxiv.org/pdf/2311.08175) | Preprint OA (verified arXiv) |
| P021 | A Systematic Review of API Evolution Literature | 2021 | ACM Computing Surveys | T5 — API evolution, breaking changes & deprecation | SLR of API evolution research: goals, methods, metrics and remaining challenges | High | [Link](https://doi.org/10.1145/3470133) | [PDF](https://ece.uwaterloo.ca/~wshang/pubs/mlamothe_csur_2021.pdf) | OA (verified) |
| P022 | Learning Evolving Tools for Large Language Models | 2025 | International Conference on Learning Representations (ICLR 2025) | T5 — API evolution, breaking changes & deprecation | ToolEVO: LLM agents adapting to evolving tools/APIs via MCTS; ToolQA-D benchmark | High | [Link](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d8d1d325f822e07d16866780cc23deb2-Abstract-Conference.html) | [PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/d8d1d325f822e07d16866780cc23deb2-Paper-Conference.pdf) | OA (verified) |
| P023 | Breaking bad? Semantic versioning and impact of breaking changes in Maven Central | 2022 | Empirical Software Engineering | T5 — API evolution, breaking changes & deprecation | Replication on Maven Central: 83.4% of upgrades follow semver; only 7.9% clients affected | High | [Link](https://doi.org/10.1007/s10664-021-10052-y) | [PDF](https://hal.science/hal-03378089v1/document) | OA (verified) |
| P024 | LLMs Meet Library Evolution: Evaluating Deprecated API Usage in LLM-Based Code Completion | 2025 | 2025 IEEE/ACM 47th International Conference on Software Engineering (ICSE) | T5 — API evolution, breaking changes & deprecation | Deprecated API usage in LLM code completion: 7 LLMs, 8 Python libraries, 28,125 prompts | High | [Link](https://doi.org/10.1109/icse55347.2025.00245) | [PDF](https://arxiv.org/pdf/2406.09834) | Preprint OA (verified arXiv) |
| P025 | Differential regression testing for REST APIs | 2020 | Proceedings of the 29th ACM SIGSOFT International Symposium on Software Testing and Analysis | T5 — API evolution, breaking changes & deprecation | Differential regression testing across 17 Azure REST API versions (14 regressions) | High | [Link](https://doi.org/10.1145/3395363.3397374) | **Not verified** | Not verified |
| P026 | Do RESTful API design rules have an impact on the understandability of Web APIs? | 2023 | Empirical Software Engineering | T6 — API documentation, design quality & governance | Controlled experiment (105 participants): 11 of 12 REST design-rule violations hurt comprehension | High | [Link](https://doi.org/10.1007/s10664-023-10367-y) | [PDF](https://link.springer.com/content/pdf/10.1007/s10664-023-10367-y.pdf) | OA (verified) |
| P027 | RESTRuler: Towards Automatically Identifying Violations of RESTful Design Rules in Web APIs | 2024 | 2024 IEEE 21st International Conference on Software Architecture (ICSA) | T6 — API documentation, design quality & governance | RESTRuler: static detection of 14 REST design-rule violations in OpenAPI (P 91%, R 68%) | Medium | [Link](https://doi.org/10.1109/icsa59870.2024.00020) | [PDF](https://arxiv.org/pdf/2402.13710) | Preprint OA (verified arXiv) |
| P028 | Automatic Detection of Five API Documentation Smells: Practitioners’ Perspectives | 2021 | 2021 IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER) | T6 — API documentation, design quality & governance | Catalogue of five API documentation smells, 1,000-unit benchmark, BERT detector | Medium | [Link](https://doi.org/10.1109/saner50967.2021.00037) | [PDF](https://arxiv.org/pdf/2102.08486) | Preprint OA (verified arXiv) |
| P029 | Detecting Misuse of Security APIs: A Systematic Review | 2025 | ACM Computing Surveys | T7 — API misuse detection | SLR of 69 studies on security-API misuse: 30 misuse types, detection & evaluation | High | [Link](https://doi.org/10.1145/3735968) | [PDF](https://arxiv.org/pdf/2306.08869) | Preprint OA (verified arXiv) |
| P030 | A Systematic Evaluation of Static API-Misuse Detectors | 2019 | IEEE Transactions on Software Engineering | T7 — API misuse detection | MUBench-based evaluation: static API-misuse detectors have very low precision/recall | High | [Link](https://doi.org/10.1109/tse.2018.2827384) | [PDF](https://arxiv.org/pdf/1712.00242) | Preprint OA (verified arXiv) |
| P031 | Identifying and Mitigating API Misuse in Large Language Models | 2026 | IEEE Transactions on Software Engineering | T7 — API misuse detection | Taxonomy of API misuse in LLM-generated code (6,700+ annotated misuses) and Dr.Fix repair | High | [Link](https://doi.org/10.1109/tse.2026.3651566) | [PDF](https://arxiv.org/pdf/2503.22821) | Preprint OA (verified arXiv) |
| P032 | From REST to MCP: An Empirical Study of API Wrapping and Automated Server Generation for LLM Agents | 2025 | arXiv | T8 — LLM tool use, API calling & MCP | 116 MCP servers: 88.6% REST-backed, expose median 19% of operations; AutoMCP generation | High | [Link](https://arxiv.org/abs/2507.16044) | [PDF](https://arxiv.org/pdf/2507.16044) | OA (verified) · PREPRINT |
| P033 | ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs | 2024 | International Conference on Learning Representations (ICLR 2024) | T8 — LLM tool use, API calling & MCP | ToolBench (16,464 RapidAPI REST APIs), DFSDT reasoning, ToolLLaMA | High | [Link](https://proceedings.iclr.cc/paper_files/paper/2024/hash/28e50ee5b72e90b50e7196fde8ea260e-Abstract-Conference.html) | [PDF](https://proceedings.iclr.cc/paper_files/paper/2024/file/28e50ee5b72e90b50e7196fde8ea260e-Paper-Conference.pdf) | OA (verified) |
| P034 | Gorilla: Large Language Model Connected with Massive APIs | 2024 | Advances in Neural Information Processing Systems 37 | T8 — LLM tool use, API calling & MCP | Gorilla: retrieval-aware fine-tuned LLM for API calls; APIBench | High | [Link](https://doi.org/10.52202/079017-4020) | [PDF](https://arxiv.org/pdf/2305.15334) | Preprint OA (verified arXiv) |
| P035 | On Mitigating Code LLM Hallucinations with API Documentation | 2025 | 2025 IEEE/ACM 47th International Conference on Software Engineering: Software Engineering in Practice (ICSE-SEIP) | T8 — LLM tool use, API calling & MCP | CloudAPIBench: low-frequency API hallucination; selective documentation-augmented generation | High | [Link](https://doi.org/10.1109/icse-seip66354.2025.00027) | [PDF](https://arxiv.org/pdf/2407.09726) | Preprint OA (verified arXiv) |
| P036 | Model Context Protocol (MCP) at First Glance: Studying the Security and Maintainability of MCP Servers | 2026 | ACM Transactions on Software Engineering and Methodology | T8 — LLM tool use, API calling & MCP | 1,899 MCP servers: 8 vulnerability types, 5.5% tool poisoning, 66% code smells | High | [Link](https://doi.org/10.1145/3814959) | [PDF](https://arxiv.org/pdf/2506.13538) | Preprint OA (verified arXiv) |
| P037 | LO2: Microservice API Anomaly Dataset of Logs and Metrics | 2025 | Proceedings of the 21st International Conference on Predictive Models and Data Analytics in Software Engineering | T9 — Microservice APIs, reliability & observability | LO2: labelled logs/metrics from API calls of a production microservice system | Medium | [Link](https://doi.org/10.1145/3727582.3728682) | [PDF](https://arxiv.org/pdf/2504.12067) | Preprint OA (verified arXiv) |
| P038 | Microservices testing: A systematic literature review | 2025 | Information and Software Technology | T9 — Microservice APIs, reliability & observability | SLR of 74 microservice testing studies classified by SWEBOK | Medium | [Link](https://doi.org/10.1016/j.infsof.2025.107870) | **Not verified** | Not verified |

## প্রতিটি নির্বাচিত paper-এর বিস্তারিত

### T1 — REST/Web API testing & fuzzing

#### P001 — Online testing of RESTful APIs: promises and challenges

- **Authors:** Alberto Martin-Lopez; Sergio Segura; Antonio Ruiz-Cortés
- **Year / Venue:** 2022 — Proceedings of the 30th ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering (Conference paper; Peer-reviewed)
- **ধরন:** Recent · Original (industrial-scale empirical) | **Importance:** High | **Provenance:** Codex only (Claude —, Codex C015, merged M075) | **Score:** 4.7
- **DOI:** 10.1145/3540250.3549144 | **arXiv:** Not found
- **Paper link:** https://doi.org/10.1145/3540250.3549144
- **PDF (verified):** https://idus.us.es/bitstreams/0592cee5-2a9b-407f-bde5-8a2941fa41d8/download — _idUS repository; OpenAlex labels 'submittedVersion' — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** Do research REST test generators scale to online testing of industrial APIs in production?
- **কেন নির্বাচিত:** শিল্প-স্কেলের বিরল প্রমাণ; ল্যাব বনাম বাস্তবতার পার্থক্য দেখায় (Codex-এর অবদান)।
- **বর্তমানে যা জানা (abstract-level):** Problem — Unclear whether research tools scale to industrial size and work in an online (production) testing setup. · Contribution — Automated online testing of 13 industrial APIs for 15 days (>1M tests, 254 bugs) · Findings — Over one million test cases; ~390K failures triaged conservatively into 254 bugs, 65 acknowledged (abstract).
- **Full paper পড়লে কী লাভ:** Scalability চ্যালেঞ্জ, false-positive triage পদ্ধতি ও practitioner implication।
- **যা যাচাই করতে হবে:** idUS কপি 'submitted version' — published version-এর সঙ্গে সংখ্যা মিলিয়ে দেখা; RESTest-কেন্দ্রিক সাধারণীকরণ।

#### P002 — Testing RESTful APIs: A Survey

- **Authors:** Amid Golmohammadi; Man Zhang; Andrea Arcuri
- **Year / Venue:** 2023 — ACM Transactions on Software Engineering and Methodology (Journal article; Peer-reviewed)
- **ধরন:** Recent · Survey | **Importance:** High | **Provenance:** Both (Claude C04, Codex C001, merged M001) | **Score:** 4.6
- **DOI:** 10.1145/3617175 | **arXiv:** 2212.14604
- **Paper link:** https://doi.org/10.1145/3617175
- **PDF (verified):** https://arxiv.org/pdf/2212.14604 — _arXiv preprint — may differ from published version_
- **Unverified candidate route:** https://dl.acm.org/doi/pdf/10.1145/3617175 (Codex-listed; our probe: NOT a PDF/blocked)
- **প্রশ্ন যা paper-টি সমাধান করে:** What techniques exist for testing RESTful APIs and which challenges remain open?
- **কেন নির্বাচিত:** T1-এর মানচিত্র ও open challenge-এর author-documented তালিকা; দুই agent-ই স্বাধীনভাবে বেছে নিয়েছে।
- **বর্তমানে যা জানা (abstract-level):** Problem — Fragmented research on automated verification of RESTful APIs. · Contribution — Review of 92 studies on RESTful API testing; taxonomy and open challenges · Findings — Interest has grown since 2017; many open research challenges remain (author statement).
- **Full paper পড়লে কী লাভ:** Full text-এর challenge-তালিকা ও শ্রেণিবিন্যাস Class A gap-এর প্রত্যক্ষ উৎস; কোন বছর পর্যন্ত সাহিত্য কভার করা হয়েছে তা দেখা দরকার।
- **যা যাচাই করতে হবে:** Search cut-off তারিখ; LLM-ভিত্তিক কাজ কভার হয়েছে কিনা; survey-র নির্বাচন পদ্ধতির মান।

#### P003 — Open Problems in Fuzzing RESTful APIs: A Comparison of Tools

- **Authors:** Man Zhang; Andrea Arcuri
- **Year / Venue:** 2023 — ACM Transactions on Software Engineering and Methodology (Journal article; Peer-reviewed)
- **ধরন:** Recent · Original (empirical tool comparison) | **Importance:** High | **Provenance:** Both (Claude C05, Codex C002, merged M002) | **Score:** 4.6
- **DOI:** 10.1145/3597205 | **arXiv:** 2205.05325
- **Paper link:** https://doi.org/10.1145/3597205
- **PDF (verified):** https://arxiv.org/pdf/2205.05325 — _arXiv preprint — may differ from published version_
- **Unverified candidate route:** https://dl.acm.org/doi/pdf/10.1145/3597205 (Codex-listed; our probe: NOT a PDF/blocked)
- **প্রশ্ন যা paper-টি সমাধান করে:** Where and why do state-of-the-art REST fuzzers fail to cover code?
- **কেন নির্বাচিত:** Open problem-গুলো সোর্স-কোড স্তরে বিশ্লেষিত — gap যাচাইয়ের সবচেয়ে শক্ত প্রমাণগুলোর একটি; দুই agent-ই বেছেছে।
- **বর্তমানে যা জানা (abstract-level):** Problem — Black-box REST fuzzers are rarely analysed for what code they actually fail to cover. · Contribution — Compares 7 REST fuzzers on 20 APIs and analyses uncovered code to list open problems · Findings — Points to clear limitations of current fuzzers and lists concrete follow-up challenges (details in full text).
- **Full paper পড়লে কী লাভ:** প্রতিটি open problem-এর উদাহরণ, পরিমাণ ও কারণ শুধু full text-এ আছে।
- **যা যাচাই করতে হবে:** লেখকরা EvoMaster-এর নির্মাতা — নিজস্ব tool-এর পক্ষে bias; LLM-যুগের tool এই সমস্যা সমাধান করেছে কিনা (P005, P007-এর সঙ্গে তুলনা)।

#### P004 — Automated test generation for REST APIs: no time to rest yet

- **Authors:** Myeongsoo Kim; Qi Xin; Saurabh Sinha; Alessandro Orso
- **Year / Venue:** 2022 — Proceedings of the 31st ACM SIGSOFT International Symposium on Software Testing and Analysis (Conference paper; Peer-reviewed)
- **ধরন:** Recent · Original (empirical tool comparison) | **Importance:** High | **Provenance:** Both (Claude C03, Codex C014, merged M010) | **Score:** 4.55
- **DOI:** 10.1145/3533767.3534401 | **arXiv:** 2204.08348
- **Paper link:** https://doi.org/10.1145/3533767.3534401
- **PDF (verified):** https://arxiv.org/pdf/2204.08348 — _arXiv preprint — may differ from published version_
- **Unverified candidate route:** https://dl.acm.org/doi/pdf/10.1145/3533767.3534401 (Codex-listed; our probe: NOT a PDF/blocked)
- **প্রশ্ন যা paper-টি সমাধান করে:** How do REST API testing tools compare on a common benchmark, and what limits them?
- **কেন নির্বাচিত:** ক্ষেত্রের সবচেয়ে প্রভাবশালী independent tool comparison; P003-এর সঙ্গে মিলিয়ে দেখার সুযোগ।
- **বর্তমানে যা জানা (abstract-level):** Problem — REST API testing tools were evaluated on different benchmarks and metrics, making comparison difficult. · Contribution — Empirical comparison of 10 REST testing tools on 20 real services (coverage, failures) · Findings — Identifies strengths, weaknesses and limitations of tools and strategies (details only in full text).
- **Full paper পড়লে কী লাভ:** Tool-ভিত্তিক শক্তি/দুর্বলতা ও ভবিষ্যৎ গবেষণার implication full text-এ।
- **যা যাচাই করতে হবে:** P003-এর সিদ্ধান্তের সঙ্গে মিল/অমিল; benchmark-এর ২০টি service-এর প্রতিনিধিত্ব।

#### P005 — LlamaRestTest: Effective REST API Testing with Small Language Models

- **Authors:** Myeongsoo Kim; Saurabh Sinha; Alessandro Orso
- **Year / Venue:** 2025 — Proceedings of the ACM on Software Engineering (Journal article; Peer-reviewed)
- **ধরন:** Recent · Original technique | **Importance:** High | **Provenance:** Both (Claude C10, Codex C013, merged M009) | **Score:** 4.4
- **DOI:** 10.1145/3715737 | **arXiv:** 2501.08598
- **Paper link:** https://doi.org/10.1145/3715737
- **PDF (verified):** https://arxiv.org/pdf/2501.08598 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** Can small fine-tuned language models match or beat large LLMs for REST API test generation?
- **কেন নির্বাচিত:** কম compute-এ কার্যকারিতা — সীমিত infrastructure-এ গবেষণার সম্ভাব্যতা নির্ধারণে গুরুত্বপূর্ণ।
- **বর্তমানে যা জানা (abstract-level):** Problem — LLM use in REST API testing is unexplored and large models are costly. · Contribution — Fine-tuned, quantized small LMs (Llama3-8B) for REST test inputs and parameter dependencies · Findings — Fine-tuned small models outperform much larger ones for dependency rules and valid inputs; higher coverage and more 500 errors than compared tools (author claim).
- **Full paper পড়লে কী লাভ:** Fine-tuning dataset, quantization trade-off, baseline কনফিগারেশন ও ablation-এর বিস্তারিত।
- **যা যাচাই করতে হবে:** Dataset ও model প্রকাশিত কিনা; ১২টি service-এর বাইরে সাধারণীকরণ; একই group-এর tool-এর সঙ্গে তুলনার fairness।

#### P006 — RESTler: Stateful REST API Fuzzing

- **Authors:** Vaggelis Atlidakis; Patrice Godefroid; Marina Polishchuk
- **Year / Venue:** 2019 — 2019 IEEE/ACM 41st International Conference on Software Engineering (ICSE) (Conference paper; Peer-reviewed)
- **ধরন:** Foundational · Original technique | **Importance:** High | **Provenance:** Both (Claude C01, Codex C018, merged M012) | **Score:** 4.4
- **DOI:** 10.1109/icse.2019.00083 | **arXiv:** 1806.09739
- **Paper link:** https://doi.org/10.1109/icse.2019.00083
- **PDF (verified):** https://www.microsoft.com/en-us/research/uploads/prod/2021/03/RESTler.pdf — _Microsoft Research-hosted copy; first page title = ICSE 2019 paper_
- **প্রশ্ন যা paper-টি সমাধান করে:** How can stateful request sequences be generated automatically from an API specification?
- **কেন নির্বাচিত:** প্রায় সব পরবর্তী কাজের baseline ও ধারণাগত ভিত্তি; দুই agent-ই বেছেছে।
- **বর্তমানে যা জানা (abstract-level):** Problem — Automatically testing cloud services through their REST APIs requires generating valid stateful request sequences from the API specification. · Contribution — RESTler: first stateful REST API fuzzer using producer–consumer dependencies · Findings — Abstract reports 28 bugs found in GitLab and several in Azure/Office365 services, confirmed and fixed by owners.
- **Full paper পড়লে কী লাভ:** Dependency inference ও dynamic feedback-এর অ্যালগরিদমিক বিবরণ, যা পরবর্তী কাজ উত্তরাধিকারসূত্রে পেয়েছে।
- **যা যাচাই করতে হবে:** Microsoft-hosted PDF ও ICSE version-এর পাঠ্য-সমতা; GitLab-এর বাইরের মূল্যায়ন (proprietary)।

#### P007 — A Multi-Agent Approach for REST API Testing with Semantic Graphs and LLM-Driven Inputs

- **Authors:** Myeongsoo Kim; Tyler Stennett; Saurabh Sinha; Alessandro Orso
- **Year / Venue:** 2025 — 2025 IEEE/ACM 47th International Conference on Software Engineering (ICSE) (Conference paper; Peer-reviewed)
- **ধরন:** Recent · Original technique | **Importance:** High | **Provenance:** Claude only (Claude C11, Codex —, merged M028) | **Score:** 4.4
- **DOI:** 10.1109/icse55347.2025.00179 | **arXiv:** 2411.07098
- **Paper link:** https://doi.org/10.1109/icse55347.2025.00179
- **PDF (verified):** https://arxiv.org/pdf/2411.07098 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** Does decomposing REST testing into cooperating learning agents improve coverage and fault detection?
- **কেন নির্বাচিত:** ICSE 2025-এর SOTA দাবি; বর্তমান baseline।
- **বর্তমানে যা জানা (abstract-level):** Problem — Tools optimise test elements in isolation, lowering coverage and fault detection. · Contribution — AutoRestTest: multi-agent RL + semantic dependency graph + LLM value generation · Findings — Outperforms four leading black-box tools including RESTGPT-assisted ones; only tool to trigger a 500 error in Spotify (author claim).
- **Full paper পড়লে কী লাভ:** Agent নকশা, reward, SPDG নির্মাণ, ablation ও failure-analysis।
- **যা যাচাই করতে হবে:** Reproducibility (tool/demo M006 [excluded] নয়); P005-এর সঙ্গে একই group — স্বাধীন মূল্যায়ন আছে কিনা।

#### P008 — AGORA: Automated Generation of Test Oracles for REST APIs

- **Authors:** Juan C. Alonso; Sergio Segura; Antonio Ruiz-Cortés
- **Year / Venue:** 2023 — Proceedings of the 32nd ACM SIGSOFT International Symposium on Software Testing and Analysis (Conference paper; Peer-reviewed)
- **ধরন:** Recent · Original technique | **Importance:** High | **Provenance:** Both (Claude C13, Codex C006, merged M003) | **Score:** 4.1
- **DOI:** 10.1145/3597926.3598114 | **arXiv:** Not found
- **Paper link:** https://doi.org/10.1145/3597926.3598114
- **PDF (verified):** Not verified
- **Unverified candidate route:** https://dl.acm.org/doi/pdf/10.1145/3597926.3598114 (OpenAlex: publisher OA 'bronze'; HTTP 403 to scripts — try in browser)
- **প্রশ্ন যা paper-টি সমাধান করে:** Can expected API behaviour be learned as invariants to build oracles beyond crashes and spec violations?
- **কেন নির্বাচিত:** Oracle problem (H3) — ক্ষেত্রের মৌলিক দুর্বলতা; দুই agent-ই বেছেছে; manual override-এ অন্তর্ভুক্ত।
- **বর্তমানে যা জানা (abstract-level):** Problem — Test oracles of REST testing tools only detect crashes, regressions and spec violations. · Contribution — AGORA: test oracles for REST APIs via likely-invariant detection (extended Daikon) · Findings — 81.2% precision on 11 operations from 7 industrial APIs; detected 6 of 10 seeded errors; revealed 11 bugs in popular APIs (author-reported).
- **Full paper পড়লে কী লাভ:** Invariant-এর প্রকার, false-positive বিশ্লেষণ, seeded-error পরীক্ষার নকশা।
- **যা যাচাই করতে হবে:** TOSEM 2025 extended version (AGORA+, 10.1145/3726524)-এর সঙ্গে পার্থক্য; precision ৮১.২% কোন dataset-এ।

### T2 — GraphQL, RPC/gRPC & architecture styles

#### P009 — GraphQL: A Systematic Mapping Study

- **Authors:** Antonio Quiña-Mera; Pablo Fernandez; José María García; Antonio Ruiz-Cortés
- **Year / Venue:** 2023 — ACM Computing Surveys (Journal article; Peer-reviewed) _[year note: OpenAlex/online-first year 2022]_
- **ধরন:** Recent · Survey (systematic mapping) | **Importance:** High | **Provenance:** Both (Claude C21, Codex C042, merged M021) | **Score:** 4.5
- **DOI:** 10.1145/3561818 | **arXiv:** Not found
- **Paper link:** https://doi.org/10.1145/3561818
- **PDF (verified):** https://idus.us.es/bitstreams/85cae9eb-bcbe-45f8-845d-cce7736e862b/download — _idUS repository; OpenAlex labels 'submittedVersion' — may differ from published version_
- **Unverified candidate route:** https://dl.acm.org/doi/pdf/10.1145/3561818 (Codex-listed; our probe: NOT a PDF/blocked)
- **প্রশ্ন যা paper-টি সমাধান করে:** What is the state and what are the knowledge gaps of GraphQL research?
- **কেন নির্বাচিত:** GraphQL ক্ষেত্রের একমাত্র উচ্চ-মানের mapping; author-documented gap; দুই agent-ই বেছেছে।
- **বর্তমানে যা জানা (abstract-level):** Problem — State of GraphQL research and knowledge gaps. · Contribution — Systematic mapping of 84 GraphQL studies; identifies evidence gaps · Findings — Adoption growing; need for more rigorous empirical evidence and studies on GraphQL components, especially consumption (author statement).
- **Full paper পড়লে কী লাভ:** Gap তালিকা ও উপ-বিষয়ভিত্তিক শ্রেণিবিন্যাস।
- **যা যাচাই করতে হবে:** Search cut-off; idUS কপি submitted version।

#### P010 — A principled approach to GraphQL query cost analysis

- **Authors:** Alan Cha; Erik Wittern; Guillaume Baudart; James C. Davis; Louis Mandel; Jim A. Laredo
- **Year / Venue:** 2020 — Proceedings of the 28th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering (Conference paper; Peer-reviewed)
- **ধরন:** Foundational · Original technique (formal) | **Importance:** High | **Provenance:** Claude only (Claude C23, Codex —, merged M033) | **Score:** 4.25
- **DOI:** 10.1145/3368089.3409670 | **arXiv:** 2009.05632
- **Paper link:** https://doi.org/10.1145/3368089.3409670
- **PDF (verified):** https://arxiv.org/pdf/2009.05632 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** How can GraphQL providers bound query cost before execution?
- **কেন নির্বাচিত:** GraphQL security/performance-এর formal ভিত্তি; architecture-specific ঝুঁকির উদাহরণ।
- **বর্তমানে যা জানা (abstract-level):** Problem — Clients can send overly expensive GraphQL queries; providers lack principled cost estimation. · Contribution — Provably correct linear-time static cost analysis for GraphQL queries · Findings — Consistently obtains tight upper bounds; existing static analyses over/under-estimate (author-reported).
- **Full paper পড়লে কী লাভ:** Formal semantics, cost model ও commercial API corpus-এর মূল্যায়ন।
- **যা যাচাই করতে হবে:** Corpus প্রকাশিত কিনা; পরবর্তী GraphQL DoS কাজ (যেমন WENDIGO) একে ছাড়িয়েছে কিনা।

#### P011 — White-Box Fuzzing RPC-Based APIs with EvoMaster: An Industrial Case Study

- **Authors:** Man Zhang; Andrea Arcuri; Yonggang Li; Yang Liu; Kaiming Xue
- **Year / Venue:** 2023 — ACM Transactions on Software Engineering and Methodology (Journal article; Peer-reviewed)
- **ধরন:** Recent · Original technique + industrial case study | **Importance:** Medium | **Provenance:** Claude only (Claude C25, Codex —, merged M034) | **Score:** 3.95
- **DOI:** 10.1145/3585009 | **arXiv:** 2208.12743
- **Paper link:** https://doi.org/10.1145/3585009
- **PDF (verified):** https://arxiv.org/pdf/2208.12743 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** How can modern RPC-based APIs be fuzzed automatically in industrial settings?
- **কেন নির্বাচিত:** gRPC/RPC-এর একমাত্র শক্তিশালী প্রতিনিধি — architecture-diversity।
- **বর্তমানে যা জানা (abstract-level):** Problem — No tool for automated testing of modern RPC-based APIs (gRPC, Thrift, Dubbo). · Contribution — First white-box fuzzing approach for RPC (gRPC/Thrift/Dubbo) APIs; 41 industrial faults · Findings — 41 real faults identified and fixed; significant coverage improvement (author-reported).
- **Full paper পড়লে কী লাভ:** RPC schema extraction, heuristic ও industrial pipeline-এর বিবরণ।
- **যা যাচাই করতে হবে:** Industrial data-র reproducibility; EvoMaster group (group cap-এর অংশ)।

### T3 — API security & authorization

#### P012 — Automated Black-Box Testing of Mass Assignment Vulnerabilities in RESTful APIs

- **Authors:** Davide Corradini; Michele Pasqua; Mariano Ceccato
- **Year / Venue:** 2023 — 2023 IEEE/ACM 45th International Conference on Software Engineering (ICSE) (Conference paper; Peer-reviewed)
- **ধরন:** Recent · Original technique | **Importance:** High | **Provenance:** Both (Claude C28, Codex C019, merged M013) | **Score:** 4.2
- **DOI:** 10.1109/icse48619.2023.00213 | **arXiv:** 2301.01261
- **Paper link:** https://doi.org/10.1109/icse48619.2023.00213
- **PDF (verified):** https://arxiv.org/pdf/2301.01261 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** Can mass-assignment vulnerabilities be detected automatically using only the API specification?
- **কেন নির্বাচিত:** OWASP API Top-10 দুর্বলতা; দুই agent-ই বেছেছে।
- **বর্তমানে যা জানা (abstract-level):** Problem — Mass assignment vulnerabilities in RESTful APIs. · Contribution — Black-box detection of mass-assignment vulnerabilities from OpenAPI specs · Findings — Effective on seeded vulnerabilities with high accuracy (author claim).
- **Full paper পড়লে কী লাভ:** Clustering-ভিত্তিক read-only field শনাক্তকরণ, test template ও oracle।
- **যা যাচাই করতে হবে:** Seeded বনাম বাস্তব vulnerability; M077 [excluded] (EASE 2024)-এর সঙ্গে পরবর্তী উন্নয়ন।

#### P013 — Mobile Application Web API Reconnaissance: Web-to-Mobile Inconsistencies & Vulnerabilities

- **Authors:** Abner Mendoza; Guofei Gu
- **Year / Venue:** 2018 — 2018 IEEE Symposium on Security and Privacy (SP) (Conference paper; Peer-reviewed)
- **ধরন:** Foundational-era · Original technique (security) | **Importance:** Medium | **Provenance:** Codex only (Claude —, Codex C021, merged M078) | **Score:** 3.9
- **DOI:** 10.1109/sp.2018.00039 | **arXiv:** Not found
- **Paper link:** https://doi.org/10.1109/sp.2018.00039
- **PDF (verified):** https://ieeexplore.ieee.org/ielx7/8418581/8418583/08418636.pdf
- **প্রশ্ন যা paper-টি সমাধান করে:** Do web API services replicate the input validation enforced by their mobile clients?
- **কেন নির্বাচিত:** Client-side বনাম server-side validation অসামঞ্জস্য — business-logic security-র ভিন্ন দৃষ্টিভঙ্গি (Codex-এর অবদান; IEEE S&P)।
- **বর্তমানে যা জানা (abstract-level):** Problem — Input validation implemented in mobile clients may not be replicated by the web API service, enabling attacks. · Contribution — WARDroid: static analysis of Android apps to find web-API input-validation inconsistencies · Findings — 10,000 apps analysed; problematic logic in APIs used by >4,000 apps; 1,000 apps tested for hijacking vulnerabilities (abstract).
- **Full paper পড়লে কী লাভ:** Template extraction ও server-validation testing-এর পদ্ধতি; ethical disclosure।
- **যা যাচাই করতে হবে:** ২০১৮-এর ফল এখনও প্রাসঙ্গিক কিনা; tool উপলব্ধতা।

#### P014 — Automated broken object-level authorization attack detection in REST APIs through OpenAPI to colored petri nets transformation

- **Authors:** Ailton Santos Filho; Ricardo J. Rodríguez; Eduardo L. Feitosa
- **Year / Venue:** 2025 — International Journal of Information Security (Journal article; Peer-reviewed)
- **ধরন:** Recent · Original technique (formal) | **Importance:** Medium | **Provenance:** Claude only (Claude C29, Codex —, merged M036) | **Score:** 3.85
- **DOI:** 10.1007/s10207-024-00970-5 | **arXiv:** Not found
- **Paper link:** https://doi.org/10.1007/s10207-024-00970-5
- **PDF (verified):** https://link.springer.com/content/pdf/10.1007/s10207-024-00970-5.pdf
- **প্রশ্ন যা paper-টি সমাধান করে:** Can formal models derived from OpenAPI detect broken object-level authorization attacks?
- **কেন নির্বাচিত:** BOLA = OWASP API #1; formal পদ্ধতির প্রতিনিধি; OA।
- **বর্তমানে যা জানা (abstract-level):** Problem — Detecting broken object-level authorization (BOLA) attacks in REST APIs. · Contribution — OpenAPI → Coloured Petri Nets for detecting BOLA attacks from server logs · Findings — >95% detection accuracy in proposed scenarios (author-reported).
- **Full paper পড়লে কী লাভ:** Transformation নিয়ম, log analysis ও accuracy-র হিসাব।
- **যা যাচাই করতে হবে:** একটি case study মাত্র — baseline অনুপস্থিত কিনা।

#### P015 — Fuzzing for Detecting Access Policy Violations in REST APIs

- **Authors:** Andrea Arcuri; Omur Sahin; Man Zhang
- **Year / Venue:** 2025 — 2025 IEEE 36th International Symposium on Software Reliability Engineering (ISSRE) (Conference paper; Peer-reviewed)
- **ধরন:** Recent · Original technique | **Importance:** High | **Provenance:** Claude only (Claude C30, Codex —, merged M037) | **Score:** 3.85
- **DOI:** 10.1109/issre66568.2025.00025 | **arXiv:** Not found
- **Paper link:** https://doi.org/10.1109/issre66568.2025.00025
- **PDF (verified):** Not verified
- **Unverified candidate route:** https://arxiv.org/abs/2604.00702 (preprint of the EXTENDED JSS 2026 version 'Enhancing REST API Fuzzing with Access Policy Violation Checks and Injection Attacks' — a DIFFERENT, longer paper; use only if ISSRE version unavailable and record this)
- **প্রশ্ন যা paper-টি সমাধান করে:** Can fuzzers detect access-control policy violations, not only crashes?
- **কেন নির্বাচিত:** Authorization oracle gap-এর সরাসরি প্রমাণ।
- **বর্তমানে যা জানা (abstract-level):** Problem — REST fuzzers focus on crashes (5xx) and miss access-policy violations. · Contribution — Automated oracles for access-policy violations integrated into a REST fuzzer · Findings — Detected security issues in some APIs (author-reported).
- **Full paper পড়লে কী লাভ:** Oracle-গুলোর সংজ্ঞা, real-world API-তে পাওয়া সমস্যার প্রকৃতি।
- **যা যাচাই করতে হবে:** JSS 2026 extension (10.1016/j.jss.2026.113060)-এর সম্পর্ক; full text access (IEEE paywall)।

### T4 — API specification inference & enrichment

#### P016 — Specification and Automated Analysis of Inter-Parameter Dependencies in Web APIs

- **Authors:** Alberto Martin-Lopez; Sergio Segura; Carlos Muller; Antonio Ruiz-Cortes
- **Year / Venue:** 2022 — IEEE Transactions on Services Computing (Journal article; Peer-reviewed) _[year note: OpenAlex/online-first year 2021]_
- **ধরন:** Foundational · Original technique (DSL/CSP) | **Importance:** High | **Provenance:** Both (Claude C15, Codex C023, merged M015) | **Score:** 4.25
- **DOI:** 10.1109/tsc.2021.3050610 | **arXiv:** 2005.03320
- **Paper link:** https://doi.org/10.1109/tsc.2021.3050610
- **PDF (verified):** https://arxiv.org/pdf/2005.03320 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** How can inter-parameter dependencies be formally specified and analysed?
- **কেন নির্বাচিত:** Inter-parameter dependency ধারণার formal ভিত্তি; পরবর্তী বহু LLM কাজ এটি লক্ষ্য করে; দুই agent-ই বেছেছে।
- **বর্তমানে যা জানা (abstract-level):** Problem — OpenAPI cannot formally express inter-parameter dependencies. · Contribution — IDL: a language and CSP-based analysis for inter-parameter dependencies in web APIs · Findings — Enables automated analysis of IDL specifications (abstract; no quantitative result stated).
- **Full paper পড়লে কী লাভ:** Dependency catalogue, IDL semantics ও analysis operation।
- **যা যাচাই করতে হবে:** OpenAPI-তে IDL-এর গ্রহণযোগ্যতা; online-first (2021) বনাম issue (2022) বছর।

#### P017 — OOPS: Automated generation of REST API specification via LLMs

- **Authors:** Hao Chen; Yunchun Li; Chen Chen; Fengxu Lin; Wei Li
- **Year / Venue:** 2026 — Journal of Systems and Software (Journal article; Peer-reviewed)
- **ধরন:** Recent · Original technique | **Importance:** High | **Provenance:** Both (Claude C35, Codex C060, merged M026) | **Score:** 4.2
- **DOI:** 10.1016/j.jss.2026.112914 | **arXiv:** 2601.12735
- **Paper link:** https://doi.org/10.1016/j.jss.2026.112914
- **PDF (verified):** https://arxiv.org/pdf/2601.12735 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** Can LLM agents generate accurate OpenAPI specifications from server code across frameworks?
- **কেন নির্বাচিত:** LLM-ভিত্তিক spec inference; দুই agent-ই বেছেছে।
- **বর্তমানে যা জানা (abstract-level):** Problem — OAS generation approaches rely on technology-specific rules and experts; LLMs suffer context limits and hallucination. · Contribution — OOPS: technology-agnostic LLM-agent static analysis to generate OpenAPI specs · Findings — Average F1 >98% endpoint methods, 97% params/responses, 92% constraints (author-reported).
- **Full paper পড়লে কী লাভ:** Dependency graph, self-refine, hallucination নিয়ন্ত্রণ ও ১২টি API-র ফল।
- **যা যাচাই করতে হবে:** F1 >৯৮% দাবির ground truth কীভাবে তৈরি; P018-এর সঙ্গে তুলনা আছে কিনা।

#### P018 — Generating REST API Specifications through Static Analysis

- **Authors:** Ruikai Huang; Manish Motwani; Idel Martinez; Alessandro Orso
- **Year / Venue:** 2024 — Proceedings of the IEEE/ACM 46th International Conference on Software Engineering (Conference paper; Peer-reviewed)
- **ধরন:** Recent · Original technique | **Importance:** High | **Provenance:** Claude only (Claude C32, Codex —, merged M039) | **Score:** 4.1
- **DOI:** 10.1145/3597503.3639137 | **arXiv:** Not found
- **Paper link:** https://doi.org/10.1145/3597503.3639137
- **PDF (verified):** Not verified
- **Unverified candidate route:** https://par.nsf.gov/servlets/purl/10537946 (NSF PAR; found by WebSearch; request timed out — NOT verified); https://dl.acm.org/doi/pdf/10.1145/3597503.3639137 (OpenAlex: publisher OA 'hybrid'; HTTP 403 to scripts — try in browser)
- **প্রশ্ন যা paper-টি সমাধান করে:** Can static/symbolic analysis infer complete and correct REST API specifications?
- **কেন নির্বাচিত:** Static spec inference-এর SOTA (ICSE 2024); spec–implementation inconsistency-র প্রমাণ।
- **বর্তমানে যা জানা (abstract-level):** Problem — OpenAPI specifications are time-consuming to maintain and often incomplete or inconsistent. · Contribution — Respector: static + symbolic analysis generating REST API specs from source code · Findings — Promising precision/recall; found missing endpoints/parameters/constraints and spec–implementation inconsistencies; outperforms annotation- and invocation-based techniques (author claim).
- **Full paper পড়লে কী লাভ:** Precision/recall-এর বিস্তারিত ও inconsistency-র উদাহরণ।
- **যা যাচাই করতে হবে:** Java framework-এ সীমাবদ্ধতা (পরবর্তী কাজের সমালোচনা অনুযায়ী); full text (ACM, browser download)।

#### P019 — RestPi: Path-Sensitive Type Inference for REST APIs

- **Authors:** Mark W. Aldrich; Kyla H. Levin; Michael Coblenz; Jeffrey S. Foster
- **Year / Venue:** 2025 — Proceedings of the ACM on Programming Languages (Journal article; Peer-reviewed)
- **ধরন:** Recent · Original technique (PL) | **Importance:** Medium | **Provenance:** Codex only (Claude —, Codex C026, merged M080) | **Score:** 3.9
- **DOI:** 10.1145/3763055 | **arXiv:** Not found
- **Paper link:** https://doi.org/10.1145/3763055
- **PDF (verified):** Not verified
- **Unverified candidate route:** https://dl.acm.org/doi/pdf/10.1145/3763055 (OpenAlex: publisher OA 'diamond'; HTTP 403 to scripts — try in browser)
- **প্রশ্ন যা paper-টি সমাধান করে:** Can path-sensitive type inference enumerate all response types of REST endpoints?
- **কেন নির্বাচিত:** Spec inference-এ PL-ভিত্তিক ভিন্ন পদ্ধতি — static (P018) ও LLM (P017)-এর সঙ্গে তুলনা (Codex-এর অবদান)।
- **বর্তমানে যা জানা (abstract-level):** Problem — REST API specifications should describe all response types, but existing generators struggle to do so automatically. · Contribution — RestPi: path-sensitive type inference generating REST API response types (Ruby) · Findings — 132 endpoints in 5 open-source APIs; more precise and complete types than an HTTP-proxy approach (abstract).
- **Full paper পড়লে কী লাভ:** Type system নকশা ও মূল্যায়নের বিস্তারিত।
- **যা যাচাই করতে হবে:** Ruby-তে সীমাবদ্ধ; full text (ACM PACMPL, OA 'diamond' — browser download)।

### T5 — API evolution, breaking changes & deprecation

#### P020 — Microservice API Evolution in Practice: A Study on Strategies and Challenges

- **Authors:** Alexander Lercher; Johann Glock; Christian Macho; Martin Pinzger
- **Year / Venue:** 2024 — Journal of Systems and Software (Journal article; Peer-reviewed)
- **ধরন:** Recent · Original (qualitative empirical) | **Importance:** High | **Provenance:** Both (Claude C38, Codex C035, merged M018) | **Score:** 4.6
- **DOI:** 10.1016/j.jss.2024.112110 | **arXiv:** 2311.08175
- **Paper link:** https://doi.org/10.1016/j.jss.2024.112110
- **PDF (verified):** https://arxiv.org/pdf/2311.08175 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** Which strategies and challenges shape API evolution in microservice systems?
- **কেন নির্বাচিত:** Author-documented research direction (change impact analysis, communication); দুই agent-ই বেছেছে।
- **বর্তমানে যা জানা (abstract-level):** Problem — Reasons behind microservice API evolution challenges are unknown. · Contribution — 17 interviews in 11 companies: microservice API evolution strategies and challenges · Findings — Proposes automating change-impact analysis and change communication as open research directions (author-stated).
- **Full paper পড়লে কী লাভ:** Challenge ও strategy-র বিস্তারিত উদ্ধৃতি ও coding।
- **যা যাচাই করতে হবে:** Interview নমুনার প্রতিনিধিত্ব; পরবর্তী follow-up (যেমন AutoGuard) আছে কিনা।

#### P021 — A Systematic Review of API Evolution Literature

- **Authors:** Maxime Lamothe; Yann-Gaël Guéhéneuc; Weiyi Shang
- **Year / Venue:** 2021 — ACM Computing Surveys (Journal article; Peer-reviewed)
- **ধরন:** Foundational · Survey (SLR) | **Importance:** High | **Provenance:** Claude only (Claude C37, Codex —, merged M042) | **Score:** 4.6
- **DOI:** 10.1145/3470133 | **arXiv:** Not found
- **Paper link:** https://doi.org/10.1145/3470133
- **PDF (verified):** https://ece.uwaterloo.ca/~wshang/pubs/mlamothe_csur_2021.pdf — _author-hosted copy (U. Waterloo); first page title verified; version-of-record equivalence not verified_
- **প্রশ্ন যা paper-টি সমাধান করে:** What has API evolution research achieved and what challenges remain?
- **কেন নির্বাচিত:** Evolution cluster-এর প্রামাণিক SLR; Class A gap।
- **বর্তমানে যা জানা (abstract-level):** Problem — Scattered literature on API evolution challenges. · Contribution — SLR of API evolution research: goals, methods, metrics and remaining challenges · Findings — Main remaining challenges: factors driving API changes; uniform benchmarks; impact across languages (author-stated).
- **Full paper পড়লে কী লাভ:** Challenge-তালিকা ও benchmark অভাবের প্রমাণ।
- **যা যাচাই করতে হবে:** Author-hosted কপি ও published version-এর সমতা; web API কতটা কভার।

#### P022 — Learning Evolving Tools for Large Language Models

- **Authors:** Guoxin Chen; Zhong Zhang; Xin Cong; Fangda Guo; Yesai Wu; Yankai Lin; Wenzheng Feng; Yasheng Wang
- **Year / Venue:** 2025 — International Conference on Learning Representations (ICLR 2025) (Conference paper; Peer-reviewed)
- **ধরন:** Recent · Original technique + benchmark | **Importance:** High | **Provenance:** Claude only (Claude C70, Codex —, merged M066) | **Score:** 4.3
- **DOI:** Not applicable | **arXiv:** 2410.06617
- **Paper link:** https://proceedings.iclr.cc/paper_files/paper/2025/hash/d8d1d325f822e07d16866780cc23deb2-Abstract-Conference.html
- **PDF (verified):** https://proceedings.iclr.cc/paper_files/paper/2025/file/d8d1d325f822e07d16866780cc23deb2-Paper-Conference.pdf
- **বিকল্প verified PDF:** https://arxiv.org/pdf/2410.06617
- **প্রশ্ন যা paper-টি সমাধান করে:** How can LLM agents remain correct when the tools/APIs they call change over time?
- **কেন নির্বাচিত:** API evolution × LLM agent — cross-cluster hypothesis H2-এর কেন্দ্রীয় paper (ICLR 2025)।
- **বর্তমানে যা জানা (abstract-level):** Problem — Tools/APIs change over time; LLMs trained on static environments fail. · Contribution — ToolEVO: LLM agents adapting to evolving tools/APIs via MCTS; ToolQA-D benchmark · Findings — Effective and stable under tool variability (author claim).
- **Full paper পড়লে কী লাভ:** Tool variability কীভাবে মডেল করা হয়েছে এবং benchmark-এর নকশা।
- **যা যাচাই করতে হবে:** Variability synthetic কিনা — বাস্তব web API evolution-এর সঙ্গে মিল।

#### P023 — Breaking bad? Semantic versioning and impact of breaking changes in Maven Central

- **Authors:** Lina Ochoa; Thomas Degueule; Jean-Rémy Falleri; Jurgen Vinju
- **Year / Venue:** 2022 — Empirical Software Engineering (Journal article; Peer-reviewed)
- **ধরন:** Recent · Original (replication) | **Importance:** High | **Provenance:** Both (Claude C41, Codex C038, merged M020) | **Score:** 4.25
- **DOI:** 10.1007/s10664-021-10052-y | **arXiv:** 2110.07889
- **Paper link:** https://doi.org/10.1007/s10664-021-10052-y
- **PDF (verified):** https://hal.science/hal-03378089v1/document
- **বিকল্প verified PDF:** https://arxiv.org/pdf/2110.07889
- **প্রশ্ন যা paper-টি সমাধান করে:** Do Java library releases follow semantic versioning and how often do breaking changes affect clients?
- **কেন নির্বাচিত:** পূর্ববর্তী গবেষণার বিপরীত ফল — contradiction evidence; দুই agent-ই বেছেছে।
- **বর্তমানে যা জানা (abstract-level):** Problem — Prior study claimed BCs are widespread regardless of semver in Maven Central. · Contribution — Replication on Maven Central: 83.4% of upgrades follow semver; only 7.9% clients affected · Findings — 83.4% of upgrades comply with semver; only 7.9% clients affected — contrasts the original study (author-reported).
- **Full paper পড়লে কী লাভ:** Original study-র protocol limitation ও Maracas tool-এর বিবরণ।
- **যা যাচাই করতে হবে:** HAL কপি বনাম journal version-এর সংখ্যা; M019 [excluded]/M089 [excluded]-এর (2.30%, 11.58%) সঙ্গে আপাত-বিরোধ ব্যাখ্যা।

#### P024 — LLMs Meet Library Evolution: Evaluating Deprecated API Usage in LLM-Based Code Completion

- **Authors:** Chong Wang; Kaifeng Huang; Jian Zhang; Yebo Feng; Lyuye Zhang; Yang Liu; Xin Peng
- **Year / Venue:** 2025 — 2025 IEEE/ACM 47th International Conference on Software Engineering (ICSE) (Conference paper; Peer-reviewed)
- **ধরন:** Recent · Original (empirical + baseline fixes) | **Importance:** High | **Provenance:** Claude only (Claude C69, Codex —, merged M065) | **Score:** 4.15
- **DOI:** 10.1109/icse55347.2025.00245 | **arXiv:** 2406.09834
- **Paper link:** https://doi.org/10.1109/icse55347.2025.00245
- **PDF (verified):** https://arxiv.org/pdf/2406.09834 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** How often do LLMs use deprecated APIs in code completion, and why?
- **কেন নির্বাচিত:** Library evolution × LLM — H2-এর প্রমাণ (ICSE 2025)।
- **বর্তমানে যা জানা (abstract-level):** Problem — LLM-based code completion may use deprecated APIs due to library evolution. · Contribution — Deprecated API usage in LLM code completion: 7 LLMs, 8 Python libraries, 28,125 prompts · Findings — Reveals status quo and root causes (details in full text) (author statement).
- **Full paper পড়লে কী লাভ:** Root cause বিশ্লেষণ ও ReplaceAPI/InsertPrompt-এর ফল।
- **যা যাচাই করতে হবে:** Web/REST API-তে একই ঘটনার কোনো প্রমাণ আছে কিনা (সম্ভাব্য gap)।

#### P025 — Differential regression testing for REST APIs

- **Authors:** Patrice Godefroid; Daniel Lehmann; Marina Polishchuk
- **Year / Venue:** 2020 — Proceedings of the 29th ACM SIGSOFT International Symposium on Software Testing and Analysis (Conference paper; Peer-reviewed)
- **ধরন:** Foundational · Original technique | **Importance:** High | **Provenance:** Claude only (Claude C39, Codex —, merged M043) | **Score:** 3.95
- **DOI:** 10.1145/3395363.3397374 | **arXiv:** Not found
- **Paper link:** https://doi.org/10.1145/3395363.3397374
- **PDF (verified):** Not verified
- **Unverified candidate route:** https://www.microsoft.com/en-us/research/publication/differential-regression-testing-for-rest-apis/ (MSR page; earlier technical report MSR-TR-2019-23 — PDF not verified, may differ from ISSTA version)
- **প্রশ্ন যা paper-টি সমাধান করে:** How can breaking changes in evolving REST APIs and their specifications be detected automatically?
- **কেন নির্বাচিত:** Web/REST breaking-change DETECTION-এর একমাত্র প্রধান technique; manual quota-সমন্বয়ে অন্তর্ভুক্ত।
- **বর্তমানে যা জানা (abstract-level):** Problem — Detecting breaking changes across REST API versions (spec and service). · Contribution — Differential regression testing across 17 Azure REST API versions (14 regressions) · Findings — 14 regressions across 17 Azure networking API versions (5 spec, 9 service) (author-reported).
- **Full paper পড়লে কী লাভ:** Non-determinism ও response-diff abstraction-এর কৌশল।
- **যা যাচাই করতে হবে:** Full text (ACM paywall; MSR technical report version থাকতে পারে); Azure-এর বাইরে প্রয়োগ।

### T6 — API documentation, design quality & governance

#### P026 — Do RESTful API design rules have an impact on the understandability of Web APIs?

- **Authors:** Justus Bogner; Sebastian Kotstein; Timo Pfaff
- **Year / Venue:** 2023 — Empirical Software Engineering (Journal article; Peer-reviewed)
- **ধরন:** Recent · Original (controlled experiment) | **Importance:** High | **Provenance:** Claude only (Claude C46, Codex —, merged M046) | **Score:** 4.8
- **DOI:** 10.1007/s10664-023-10367-y | **arXiv:** 2305.07346
- **Paper link:** https://doi.org/10.1007/s10664-023-10367-y
- **PDF (verified):** https://link.springer.com/content/pdf/10.1007/s10664-023-10367-y.pdf
- **বিকল্প verified PDF:** https://arxiv.org/pdf/2305.07346
- **প্রশ্ন যা paper-টি সমাধান করে:** Do RESTful API design rules affect the understandability of web APIs?
- **কেন নির্বাচিত:** Rigorous experiment-ভিত্তিক design-quality প্রমাণ; OA।
- **বর্তমানে যা জানা (abstract-level):** Problem — Empirical evidence for RESTful API design rules is lacking. · Contribution — Controlled experiment (105 participants): 11 of 12 REST design-rule violations hurt comprehension · Findings — Violations worse for 11 of 12 rules in comprehension (author-reported).
- **Full paper পড়লে কী লাভ:** Experiment নকশা, effect size ও threat to validity।
- **যা যাচাই করতে হবে:** Snippet-ভিত্তিক — বাস্তব API-তে প্রযোজ্যতা।

#### P027 — RESTRuler: Towards Automatically Identifying Violations of RESTful Design Rules in Web APIs

- **Authors:** Justus Bogner; Sebastian Kotstein; Daniel Abajirov; Timothy Ernst; Manuel Merkel
- **Year / Venue:** 2024 — 2024 IEEE 21st International Conference on Software Architecture (ICSA) (Conference paper; Peer-reviewed)
- **ধরন:** Recent · Original technique (tool) | **Importance:** Medium | **Provenance:** Claude only (Claude C47, Codex —, merged M047) | **Score:** 3.7
- **DOI:** 10.1109/icsa59870.2024.00020 | **arXiv:** 2402.13710
- **Paper link:** https://doi.org/10.1109/icsa59870.2024.00020
- **PDF (verified):** https://arxiv.org/pdf/2402.13710 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** Can design-rule violations in OpenAPI descriptions be detected automatically?
- **কেন নির্বাচিত:** P026-এর প্রমাণকে tool-এ রূপান্তর; recall-এর ঘাটতি স্পষ্ট।
- **বর্তমানে যা জানা (abstract-level):** Problem — Practitioners struggle to identify REST design rule violations. · Contribution — RESTRuler: static detection of 14 REST design-rule violations in OpenAPI (P 91%, R 68%) · Findings — Precision 91%, recall 68% (per-rule variation) (author-reported).
- **Full paper পড়লে কী লাভ:** Rule-ভিত্তিক precision/recall ও ব্যর্থতার কারণ।
- **যা যাচাই করতে হবে:** P026-এর একই group — স্বাধীন মূল্যায়ন।

#### P028 — Automatic Detection of Five API Documentation Smells: Practitioners’ Perspectives

- **Authors:** Junaed Younus Khan; Md. Tawkat Islam Khondaker; Gias Uddin; Anindya Iqbal
- **Year / Venue:** 2021 — 2021 IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER) (Conference paper; Peer-reviewed)
- **ধরন:** Foundational-era · Original (empirical + classifiers) | **Importance:** Medium | **Provenance:** Both (Claude C45, Codex C029, merged M017) | **Score:** 3.65
- **DOI:** 10.1109/saner50967.2021.00037 | **arXiv:** 2102.08486
- **Paper link:** https://doi.org/10.1109/saner50967.2021.00037
- **PDF (verified):** https://arxiv.org/pdf/2102.08486 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** Which documentation smells exist and can they be detected automatically?
- **কেন নির্বাচিত:** Documentation cluster-এর প্রতিনিধি (manual override); দুই agent-ই বেছেছে।
- **বর্তমানে যা জানা (abstract-level):** Problem — No automatic detection of API documentation smells. · Contribution — Catalogue of five API documentation smells, 1,000-unit benchmark, BERT detector · Findings — BERT F1 0.75–0.97; 95.2% developers report productivity harm (author-reported).
- **Full paper পড়লে কী লাভ:** Smell-সংজ্ঞা ও benchmark labelling পদ্ধতি।
- **যা যাচাই করতে হবে:** Java docs — web API (OpenAPI) docs-এ প্রযোজ্যতা।

### T7 — API misuse detection

#### P029 — Detecting Misuse of Security APIs: A Systematic Review

- **Authors:** Zahra Mousavi; Chadni Islam; Muhammad Ali Babar; Alsharif Abuadbba; Kristen Moore
- **Year / Venue:** 2025 — ACM Computing Surveys (Journal article; Peer-reviewed)
- **ধরন:** Recent · Survey (SLR) | **Importance:** High | **Provenance:** Claude only (Claude C50, Codex —, merged M050) | **Score:** 4.35
- **DOI:** 10.1145/3735968 | **arXiv:** 2306.08869
- **Paper link:** https://doi.org/10.1145/3735968
- **PDF (verified):** https://arxiv.org/pdf/2306.08869 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** How is misuse of security APIs detected and evaluated?
- **কেন নির্বাচিত:** Misuse cluster-এর সাম্প্রতিক SLR; author-documented gap।
- **বর্তমানে যা জানা (abstract-level):** Problem — Detection of security API misuse. · Contribution — SLR of 69 studies on security-API misuse: 30 misuse types, detection & evaluation · Findings — Lack of coverage in several areas; need standardized evaluation (author-stated).
- **Full paper পড়লে কী লাভ:** Benchmark ও evaluation measure-এর তালিকা।
- **যা যাচাই করতে হবে:** Search cut-off; LLM-যুগের কাজ কভার।

#### P030 — A Systematic Evaluation of Static API-Misuse Detectors

- **Authors:** Sven Amann; Hoan Anh Nguyen; Sarah Nadi; Tien N. Nguyen; Mira Mezini
- **Year / Venue:** 2019 — IEEE Transactions on Software Engineering (Journal article; Peer-reviewed) _[year note: OpenAlex/online-first year 2018]_
- **ধরন:** Foundational · Original (benchmark evaluation) | **Importance:** High | **Provenance:** Claude only (Claude C49, Codex —, merged M049) | **Score:** 4.25
- **DOI:** 10.1109/tse.2018.2827384 | **arXiv:** 1712.00242
- **Paper link:** https://doi.org/10.1109/tse.2018.2827384
- **PDF (verified):** https://arxiv.org/pdf/1712.00242 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** What are the capabilities and limits of static API-misuse detectors?
- **কেন নির্বাচিত:** Misuse-এর ভিত্তিমূলক benchmark; LLM-যুগের তুলনার baseline।
- **বর্তমানে যা জানা (abstract-level):** Problem — Capabilities/limitations of static API-misuse detectors are unknown. · Contribution — MUBench-based evaluation: static API-misuse detectors have very low precision/recall · Findings — Extremely low precision and recall; frequency-based 'deviation = misuse' assumption is a root cause (author-reported).
- **Full paper পড়লে কী লাভ:** Root-cause বিশ্লেষণ ও MUC classification।
- **যা যাচাই করতে হবে:** LLM-ভিত্তিক detector-এর জন্য এই সিদ্ধান্ত বদলেছে কিনা (P031, M014 [excluded])।

#### P031 — Identifying and Mitigating API Misuse in Large Language Models

- **Authors:** Terry Yue Zhuo; Junda He; Jiamou Sun; Zhenchang Xing; David Lo; John Grundy; Xiaoning Du
- **Year / Venue:** 2026 — IEEE Transactions on Software Engineering (Journal article; Peer-reviewed)
- **ধরন:** Recent · Original (empirical + repair) | **Importance:** High | **Provenance:** Claude only (Claude C53, Codex —, merged M052) | **Score:** 4.15
- **DOI:** 10.1109/tse.2026.3651566 | **arXiv:** 2503.22821
- **Paper link:** https://doi.org/10.1109/tse.2026.3651566
- **PDF (verified):** https://arxiv.org/pdf/2503.22821 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** What kinds of API misuse do LLMs make and can they be repaired automatically?
- **কেন নির্বাচিত:** LLM-যুগের সবচেয়ে বড় misuse study (TSE 2026)।
- **বর্তমানে যা জানা (abstract-level):** Problem — API misuse in LLM-generated code (method selection and parameters). · Contribution — Taxonomy of API misuse in LLM-generated code (6,700+ annotated misuses) and Dr.Fix repair · Findings — Persistent hallucination and intent misalignment; Dr.Fix gains up to 38.4 BLEU, 40% exact match (author-reported).
- **Full paper পড়লে কী লাভ:** Annotation protocol, taxonomy ও repair-এর মূল্যায়ন।
- **যা যাচাই করতে হবে:** BLEU/EM metric-এর উপযুক্ততা; inter-rater agreement।

### T8 — LLM tool use, API calling & MCP

#### P032 — From REST to MCP: An Empirical Study of API Wrapping and Automated Server Generation for LLM Agents

- **Authors:** Meriem Mastouri; Emna Ksontini; Amine Barrak; Wael Kessentini
- **Year / Venue:** 2025 — arXiv (Preprint; Not peer-reviewed)
- **ধরন:** Recent · Original (empirical + generator) · PREPRINT | **Importance:** High | **Provenance:** Claude only (Claude C64, Codex —, merged M061) | **Score:** 4.5
- **DOI:** Not applicable | **arXiv:** 2507.16044
- **Paper link:** https://arxiv.org/abs/2507.16044
- **PDF (verified):** https://arxiv.org/pdf/2507.16044
- **প্রশ্ন যা paper-টি সমাধান করে:** How do MCP servers wrap REST APIs, and can MCP servers be generated from OpenAPI specs?
- **কেন নির্বাচিত:** REST ↔ agent সেতুবন্ধন (T4×T8); H1/H5-এর প্রধান প্রমাণ।
- **বর্তমানে যা জানা (abstract-level):** Problem — Relationship between MCP tool interfaces and underlying REST APIs is uncharacterised. · Contribution — 116 MCP servers: 88.6% REST-backed, expose median 19% of operations; AutoMCP generation · Findings — 88.6% REST-backed; 92% bare wrappers; median 19% of operations exposed; generation 76% → 94.2% after repair (author-reported, v4).
- **Full paper পড়লে কী লাভ:** Exposure pattern, generation failure ও spec repair-এর বিশ্লেষণ।
- **যা যাচাই করতে হবে:** Preprint (peer review হয়নি); v1–v4-এ শিরোনাম ও সংখ্যা বদলেছে — কোন version ডাউনলোড হলো তা রেকর্ড করতে হবে।

#### P033 — ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs

- **Authors:** Yujia Qin; Shihao Liang; Yining Ye; Kunlun Zhu; Lan Yan; Yaxi Lu; Yankai Lin; Xin Cong; Xiangru Tang; Bill Qian; Sihan Zhao; Lauren Hong; Runchu Tian; Ruobing Xie; Jie Zhou; Mark Gerstein; Dahai Li; Zhiyuan Liu; Maosong Sun
- **Year / Venue:** 2024 — International Conference on Learning Representations (ICLR 2024) (Conference paper; Peer-reviewed)
- **ধরন:** Recent · Original technique + dataset | **Importance:** High | **Provenance:** Claude only (Claude C56, Codex —, merged M053) | **Score:** 4.3
- **DOI:** Not applicable | **arXiv:** 2307.16789
- **Paper link:** https://proceedings.iclr.cc/paper_files/paper/2024/hash/28e50ee5b72e90b50e7196fde8ea260e-Abstract-Conference.html
- **PDF (verified):** https://proceedings.iclr.cc/paper_files/paper/2024/file/28e50ee5b72e90b50e7196fde8ea260e-Paper-Conference.pdf
- **বিকল্প verified PDF:** https://arxiv.org/pdf/2307.16789
- **প্রশ্ন যা paper-টি সমাধান করে:** How can open LLMs learn to use large numbers of real-world REST APIs?
- **কেন নির্বাচিত:** বাস্তব REST API-ভিত্তিক tool-use dataset-এর landmark (ICLR 2024)।
- **বর্তমানে যা জানা (abstract-level):** Problem — Open-source LLMs are weak at using real-world APIs. · Contribution — ToolBench (16,464 RapidAPI REST APIs), DFSDT reasoning, ToolLLaMA · Findings — ToolLLaMA comparable to ChatGPT; generalises to unseen APIs (author claim).
- **Full paper পড়লে কী লাভ:** API collection, instruction generation ও ToolEval-এর validity।
- **যা যাচাই করতে হবে:** API অস্থিরতা (M055 [excluded] StableToolBench উল্লেখ করে); ChatGPT-উৎপন্ন data-র মান।

#### P034 — Gorilla: Large Language Model Connected with Massive APIs

- **Authors:** Shishir Patil; Tianjun Zhang; Xin Wang; Joseph Gonzalez
- **Year / Venue:** 2024 — Advances in Neural Information Processing Systems 37 (Conference paper; Peer-reviewed)
- **ধরন:** Recent · Original technique + benchmark | **Importance:** High | **Provenance:** Both (Claude C55, Codex C057, merged M025) | **Score:** 4.15
- **DOI:** 10.52202/079017-4020 | **arXiv:** 2305.15334
- **Paper link:** https://doi.org/10.52202/079017-4020
- **PDF (verified):** https://arxiv.org/pdf/2305.15334 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** Can fine-tuning with retrieval reduce hallucinated API calls and adapt to documentation changes?
- **কেন নির্বাচিত:** API hallucination ও documentation-change adaptation-এর landmark; দুই agent-ই বেছেছে।
- **বর্তমানে যা জানা (abstract-level):** Problem — LLMs hallucinate API calls and generate wrong arguments. · Contribution — Gorilla: retrieval-aware fine-tuned LLM for API calls; APIBench · Findings — Surpasses GPT-4 on writing API calls; adapts to doc changes; reduces hallucination (author claim).
- **Full paper পড়লে কী লাভ:** Retrieval-aware training ও doc-change পরীক্ষার নকশা।
- **যা যাচাই করতে হবে:** APIBench (ML model hub API) — web API-তে প্রযোজ্যতা; নাম-সংঘাত (TSE-এর APIBench আলাদা)।

#### P035 — On Mitigating Code LLM Hallucinations with API Documentation

- **Authors:** Nihal Jain; Robert Kwiatkowski; Baishakhi Ray; Murali Krishna Ramanathan; Varun Kumar
- **Year / Venue:** 2025 — 2025 IEEE/ACM 47th International Conference on Software Engineering: Software Engineering in Practice (ICSE-SEIP) (Conference paper; Peer-reviewed)
- **ধরন:** Recent · Original (empirical + mitigation, industrial) | **Importance:** High | **Provenance:** Claude only (Claude C60, Codex —, merged M057) | **Score:** 4.15
- **DOI:** 10.1109/icse-seip66354.2025.00027 | **arXiv:** 2407.09726
- **Paper link:** https://doi.org/10.1109/icse-seip66354.2025.00027
- **PDF (verified):** https://arxiv.org/pdf/2407.09726 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** How does API frequency affect code-LLM hallucination, and when does documentation retrieval help?
- **কেন নির্বাচিত:** Documentation × LLM — T6 ও T8-এর সংযোগ (ICSE-SEIP)।
- **বর্তমানে যা জানা (abstract-level):** Problem — Code LLMs hallucinate APIs, especially low-frequency ones. · Contribution — CloudAPIBench: low-frequency API hallucination; selective documentation-augmented generation · Findings — GPT-4o 38.58% valid low-frequency invocations; DAG helps low-frequency but hurts high-frequency with weak retrievers; +8.20% absolute with selective DAG (author-reported).
- **Full paper পড়লে কী লাভ:** Frequency annotation ও retrieval-trigger কৌশল।
- **যা যাচাই করতে হবে:** Cloud SDK API-তে সীমাবদ্ধতা; benchmark প্রকাশিত কিনা।

#### P036 — Model Context Protocol (MCP) at First Glance: Studying the Security and Maintainability of MCP Servers

- **Authors:** Mohammed Mehedi Hasan; Hao Li; Emad Fallahzadeh; Gopi Krishnan Rajbahadur; Bram Adams; Ahmed E. Hassan
- **Year / Venue:** 2026 — ACM Transactions on Software Engineering and Methodology (Journal article; Peer-reviewed)
- **ধরন:** Recent · Original (large-scale empirical) | **Importance:** High | **Provenance:** Claude only (Claude C63, Codex —, merged M060) | **Score:** 4.15
- **DOI:** 10.1145/3814959 | **arXiv:** 2506.13538
- **Paper link:** https://doi.org/10.1145/3814959
- **PDF (verified):** https://arxiv.org/pdf/2506.13538 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** How healthy, secure and maintainable are open-source MCP servers?
- **কেন নির্বাচিত:** MCP-এর প্রথম বড় empirical study (TOSEM); agent-facing API security।
- **বর্তমানে যা জানা (abstract-level):** Problem — Health, security and maintainability of MCP servers. · Contribution — 1,899 MCP servers: 8 vulnerability types, 5.5% tool poisoning, 66% code smells · Findings — 8 vulnerability types (3 overlap traditional); 7.2% general vulns, 5.5% tool poisoning; 66% code smells (author-reported).
- **Full paper পড়লে কী লাভ:** Scanner নকশা, vulnerability-সংজ্ঞা ও false-positive হার।
- **যা যাচাই করতে হবে:** Ecosystem দ্রুত বদলায় — snapshot তারিখ; scanner-এর validity।

### T9 — Microservice APIs, reliability & observability

#### P037 — LO2: Microservice API Anomaly Dataset of Logs and Metrics

- **Authors:** Alexander Bakhtin; Jesse Nyyssölä; Yuqing Wang; Noman Ahmad; Ke Ping; Matteo Esposito; Mika Mäntylä; Davide Taibi
- **Year / Venue:** 2025 — Proceedings of the 21st International Conference on Predictive Models and Data Analytics in Software Engineering (Conference paper; Peer-reviewed)
- **ধরন:** Recent · Dataset | **Importance:** Medium | **Provenance:** Codex only (Claude —, Codex C054, merged M101) | **Score:** 3.9
- **DOI:** 10.1145/3727582.3728682 | **arXiv:** 2504.12067
- **Paper link:** https://doi.org/10.1145/3727582.3728682
- **PDF (verified):** https://arxiv.org/pdf/2504.12067 — _arXiv preprint — may differ from published version_
- **প্রশ্ন যা paper-টি সমাধান করে:** Can a multi-modal dataset support anomaly detection research on microservice APIs?
- **কেন নির্বাচিত:** API monitoring/anomaly cluster-এর একমাত্র মানসম্পন্ন উৎস — PHASE A-র দুর্বল কভারেজ পূরণ (Codex-এর অবদান)।
- **বর্তমানে যা জানা (abstract-level):** Problem — Multi-modal anomaly detection in microservices lacks datasets combining logs, metrics and traces. · Contribution — LO2: labelled logs/metrics from API calls of a production microservice system · Findings — ~657,000 log files (>2 billion lines), >45 million metric files with 485 metrics; initial log analysis and PCA of metrics; trace collection challenges discussed (abstract).
- **Full paper পড়লে কী লাভ:** Labelling পদ্ধতি, ডেটা সংগ্রহের সীমাবদ্ধতা ও ব্যবহারের নির্দেশিকা।
- **যা যাচাই করতে হবে:** Dataset-এর লাইসেন্স ও প্রাপ্যতা; একক সিস্টেম থেকে সাধারণীকরণ।

#### P038 — Microservices testing: A systematic literature review

- **Authors:** Francisco Ponce; Roberto Verdecchia; Breno Miranda; Jacopo Soldani
- **Year / Venue:** 2025 — Information and Software Technology (Journal article; Peer-reviewed)
- **ধরন:** Recent · Survey (SLR) | **Importance:** Medium | **Provenance:** Both (Claude C65, Codex C056, merged M024) | **Score:** 3.85
- **DOI:** 10.1016/j.infsof.2025.107870 | **arXiv:** Not found
- **Paper link:** https://doi.org/10.1016/j.infsof.2025.107870
- **PDF (verified):** Not verified
- **Unverified candidate route:** https://hdl.handle.net/2158/1438341 and https://hdl.handle.net/11568/1331513 (Florence / Pisa repository records of the submitted version; OpenAlex marks them not OA — access NOT verified)
- **প্রশ্ন যা paper-টি সমাধান করে:** What testing approaches exist for microservices and how mature are they?
- **কেন নির্বাচিত:** Microservice testing-এর সাম্প্রতিক SLR; দুই agent-ই বেছেছে।
- **বর্তমানে যা জানা (abstract-level):** Problem — Testing microservice systems. · Contribution — SLR of 74 microservice testing studies classified by SWEBOK · Findings — Dominated by early-stage proposals; need empirical validation and industry-grade benchmarks (partial abstract via web search).
- **Full paper পড়লে কী লাভ:** Maturity মূল্যায়ন ও benchmark-অভাবের প্রমাণ।
- **যা যাচাই করতে হবে:** Full text (Elsevier paywall; Pisa/Florence repository record আছে কিন্তু PDF যাচাই হয়নি); abstract আংশিক।
