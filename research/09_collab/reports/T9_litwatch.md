# T9 — R1 literature watch: অক্টোবর–নভেম্বর ২০২৬

**যাচাই:** 2026-11-13; cutoff 2026-11-13। **লেখক:** Codex। Web search ও primary-source page inspection করা হয়েছে; কোনো external code, package বা SUT চালানো হয়নি। কাজের পরিধি: `09_collab/tasks/T9.md:1`। পূর্বের অবস্থান: `06_final_recommendations/R1_novelty_check_E0.md:19` ও `:151`।

## সিদ্ধান্ত

**⚠️ Conditional GO:** পরিদর্শিত প্রমাণে REST/OpenAPI conformance failure-কে **spec defect বনাম implementation fault** হিসেবে স্বয়ংক্রিয়ভাবে নির্ণয়ের সরাসরি সমতুল্য পদ্ধতি নিশ্চিত হয়নি। এটি অনুসন্ধানের ফল, কাজটির অনস্তিত্বের প্রমাণ নয়। বিশেষত FDRRestTest-এর diagnosis/repair অংশের পূর্ণ পাঠ যাচাই অসম্পূর্ণ; তাই এখনই “প্রথম মূল্যায়িত পদ্ধতি” দাবি অনুমোদনযোগ্য নয় (C3, §৫)।

**Runtime evidence থেকে OpenAPI patch generation ইতিমধ্যেই tool capability:** Beeceptor এটি স্পষ্টভাবে বর্ণনা করে; মানুষের review ও approval লাগে। ফলে বিস্তৃত “প্রথম runtime-based spec repair tool” দাবি পরিহার করা উচিত (C5)। অক্টোবরের Agent4Spec specification repair করে, কিন্তু পরিদর্শিত evaluation syntax/structural defect-এ সীমিত; নভেম্বরের RESTberus failure attribution করে, কিন্তু তার label target service বনাম downstream service (C1–C2)।

**সবচেয়ে ঘনিষ্ঠ অতিরিক্ত প্রতিদ্বন্দ্বী DualMine:** runtime evidence দিয়ে spec-derived constraint সমর্থন/খণ্ডন এবং counterexample দিয়ে constraint দুর্বল/বিশেষায়িত করে। ⚠️ R1-এর evidence reconciliation ও refinement-এ উল্লেখযোগ্য overlap; তবে failure-origin label বা OpenAPI patch লেখার সমতুল্য ফল পরিদর্শিত পদ্ধতিতে নেই (C4)।

## ১. পদ্ধতি ও overlap-এর অর্থ

প্রথমে protocol, task, board ও E0 পড়া হয়েছে (`09_collab/PROTOCOL.md:1`; `09_collab/tasks/T9.md:1`; `09_collab/COLLAB_BOARD.md`, T9 row; `06_final_recommendations/R1_novelty_check_E0.md:1`)। অক্টোবর ১ থেকে নভেম্বর ১৩ প্রধান সময়সীমা; পরিচিত baseline ও search-এ উঠে আসা পুরোনো ঘনিষ্ঠ কাজও রাখা হয়েছে। Primary arXiv HTML/abstract, publisher record, conference program এবং tool-এর নিজস্ব documentation ব্যবহৃত হয়েছে। Search-engine তারিখকে publication date ধরে নেওয়া হয়নি।

এখানে **strong** = R1-এর অন্তত একটি মূল capability-তে সরাসরি overlap; **partial** = প্রাসঙ্গিক evidence/repair/diagnosis আছে, কিন্তু target attribution প্রতিষ্ঠিত নয়; **none** = পরিদর্শিত বর্ণনায় দুই target capability-র কোনোটিই প্রতিষ্ঠিত নয়। সব overlap classification **⚠️ বিশ্লেষণাত্মক সিদ্ধান্ত**। Abstract-only/metadata-only evidence দিয়ে capability-র চূড়ান্ত অনুপস্থিতি দাবি করা হয়নি।

## ২. Queries ব্যবহৃত

নিচের query-গুলি এই session-এ চালানো হয়েছে; date operator-সহ search-ও index coverage-এর সীমা অতিক্রম করে না। Candidate title/ID পাওয়ার পরে সরাসরি primary URL খোলা হয়েছে (§৩–৪)।

| ID | Exact query |
|---|---|
| Q01 | `"OpenAPI" "specification" "repair" "2026"` |
| Q02 | `"REST" "failure" "attribution" specification implementation` |
| Q03 | `"OpenAPI" "October" "2026" testing` |
| Q04 | `"OpenAPI" "November" "2026" repair` |
| Q05 | `site:arxiv.org OpenAPI repair 2026 specification` |
| Q06 | `RESTest 2026 papers Segura specification` |
| Q07 | `EvoMaster 2026 papers Arcuri` |
| Q08 | `Schemathesis 2026 paper specification repair` |
| Q09 | `"OpenAPI" "repair" runtime specification arxiv 2026` |
| Q10 | `"RESTest" "2026" "specification"` |
| Q11 | `"Schemathesis: Multi-Phase Property-Based Testing of REST APIs"` |
| Q12 | `"OpenAPI" "failure classification"` |
| Q13 | `"OpenAPI" "runtime" "repair" after:2026-10-01 before:2026-11-14` |
| Q14 | `"REST" "specification" "implementation" "attribution" 2026` |
| Q15 | `"OpenAPI" "traffic" "patch" Beeceptor` |
| Q16 | `"RESTest at the REST League 2026 Tool Competition"` |
| Q17 | `"OpenAPI" "specification repair" after:2026-10-01 before:2026-11-14` |
| Q18 | `"REST" "specification defects" "2026" attribution` |
| Q19 | `"Online Machine Learning Prediction of Failed Calls to Enhance REST API Fuzzing"` |
| Q20 | `"OpenAPI" "runtime evidence" repair` |
| Q21 | `"DualMine" OpenAPI repair` |
| Q22 | `site:equixly.com "October 2026" "repair"` |
| Q23 | `"Online Machine Learning Prediction" "Failed Calls" QUATIC 2026` |
| Q24 | `"FDRRestTest" "repair" "schema"` |
| Q25 | `"FDRRestTest" "seven" diagnosis` |
| Q26 | `"Equixly October 2026 product update"` |
| Q27 | `"FDRRestTest" "diagnosis" "repair" -site:researchgate.net -site:dualmine.com` |
| Q28 | `"OpenAPI" "specification versus implementation"` |
| Q29 | `"OpenAPI" "specification or implementation" failure` |

## ৩. নতুন ও ঘনিষ্ঠ candidates

### C1 — RESTberus: Trace-Aware Benchmarking of Automated REST API Testing Tools Across Microservice Dependencies

**লেখক:** John Toniutti, Massimiliano Baldo, Marino Miculan, Vincenzo Riccio। **তারিখ:** 2026-11-03, v1। **ID/URL:** [arXiv:2611.04769](https://arxiv.org/abs/2611.04769); [HTML §III-D](https://arxiv.org/html/2611.04769v1#S3.SS4)। **প্রমাণ:** method section পরিদর্শিত।

Trace-এর latest-starting 5xx span দিয়ে failure target service-এ নাকি downstream dependency-তে ঘটেছে তা নির্ণয় করে; span না পেলে target-side default। ⚠️ **Overlap: partial**—automatic attribution আছে, কিন্তু spec-versus-implementation attribution বা spec repair নয়। R1-এ attribution-এর label স্পষ্ট লেখা জরুরি।

### C2 — Agent4Spec: An LLM-based Agentic System to Optimize API Specifications through Automated Validation and Market Analysis

**লেখক:** Yongjian Tang, Costel Moraru, Doruk Tuncel, Hanya Elhashemy, Steffen Klepke, Thomas Runkler। **তারিখ:** 2026-10-09, v1। **URL:** [arXiv:2610.13273](https://arxiv.org/abs/2610.13273); [HTML §III ও §V](https://arxiv.org/html/2610.13273v1)। **প্রমাণ:** architecture ও evaluation পরিদর্শিত।

Agent pipeline spec validate/revise করে; evaluation-এ YAML indentation, mandatory response description ও type/default inconsistency inject করা হয়েছে। ⚠️ **Overlap: partial**—automated OpenAPI repair গবেষণা আছে, কিন্তু পরিদর্শিত repair evaluation live API request/response evidence বা failure-origin diagnosis প্রতিষ্ঠা করে না।

### C3 — FDRRestTest: Feedback-Driven Logical Testing for REST APIs

**লেখক:** publisher record-এ Yutong Huo ও Dongcheng Li; conference program-এ অতিরিক্ত Man Zhao আছে—তফাত অমীমাংসিত। **তারিখ:** publisher publication 2026-10-05; talk 2026-10-08। **URL/DOI:** [publisher record, 10.4230/LIPIcs.ESEM.2026.20](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ESEM.2026.20); [conference program](https://conf.researchr.org/details/eseiw-2026/eseiw-2026-esem---technical-track/20/FDRRestTest-Feedback-Driven-Logical-Testing-for-REST-APIs)। **প্রমাণ:** publisher ও program abstract-only; PDF method নির্ভরযোগ্যভাবে পড়া যায়নি।

Abstract-এ runtime dependency evolution, **7-category failure diagnosis and repair loop**, logical oracles আছে। ⚠️ **Overlap: partial (provisional; strong হওয়ার সম্ভাবনা নিষ্পত্তি হয়নি)**—repair কোন artifact-এ এবং সাতটি category কী, তা না দেখে একে test repair বা spec repair কোনোটিই বলা যাবে না। এটি novelty claim-এর সর্বোচ্চ অগ্রাধিকারের follow-up।

### C4 — DualMine: Static-Dynamic REST API Constraint Discovery with Dual Validation

**লেখক:** Tu Nguyen, Huy Nguyen, Juan C.A. Valenzuela, Thanh Nguyen, Tien N. Nguyen, Vu Nguyen। **তারিখ:** arXiv page-এর submission history 2026-08-18, v1; ID-র `2609` prefix-এর সঙ্গে অস্বাভাবিক অমিল—তারিখ অনুমান করে সংশোধন করা হয়নি। **URL:** [arXiv:2609.27806 ও history](https://arxiv.org/abs/2609.27806); [HTML §IV-A–D](https://arxiv.org/html/2609.27806v1)। **প্রমাণ:** method section পরিদর্শিত; প্রধান window-এর বাইরের কাজ।

ExecValidator spec-derived constraint-কে supported/contradicted/unresolved বলে; targeted executions ও resolver constraint weaken/specialize করতে পারে। ⚠️ **Overlap: partial, ঘনিষ্ঠ**—runtime/spec reconciliation ও constraint refinement মিলে যায়; প্রকাশিত output validated constraint set, spec-versus-implementation failure label বা OpenAPI patch নয়। Runtime-কে সত্য ধরে ভুল implementation ঢেকে দেওয়ার ঝুঁকি R1-কে আলাদাভাবে মূল্যায়ন করতে হবে।

### C5 — API Contract Change Detection / AI-Powered OpenAPI Contract Drift Detection (Beta)

**লেখক/প্রকাশক:** Beeceptor; ব্যক্তিগত byline নেই। **তারিখ:** changelog-এ 2026-03-15; documentation-এর নিজস্ব publication date নেই (access 2026-11-13)। **URL:** [official documentation](https://beeceptor.com/docs/openapi-contract-drift-detection/index.html); [dated changelog](https://beeceptor.com/changelog/more/)। **প্রমাণ:** official documentation/changelog পরিদর্শিত; vendor capability claim, স্বাধীন evaluation নয়।

বাস্তব request/response baseline OpenAPI-র সঙ্গে মিলিয়ে drift দেখায় এবং AI-assisted patch তৈরি করে; user ঠিক করে drift intentional নাকি bug, approval-এর পরে merge হয়। ⚠️ **Overlap: strong, repair capability-তে**; automatic causal attribution প্রতিষ্ঠিত নয়। “Runtime-based OpenAPI patching নেই” বলা যাবে না।

### C6 — Equixly October 2026 product update: Smarter setup, clearer scans

**লেখক:** Edoardo Zatti, Zoran Gorgiev। **তারিখ:** 2026-10-05। **URL:** [official product update](https://equixly.com/blog/2026/10/05/equixly-october-2026-product-update-smarter-setup-clearer-scans/)। **প্রমাণ:** official article পরিদর্শিত।

Polaris service creation/update-এ parse না হওয়া OpenAPI/WSDL definition background-এ repair করার চেষ্টা করে। ⚠️ **Overlap: partial**—এই নতুন release automated specification repair-এর উদাহরণ; বর্ণিত trigger parsing error, live conformance evidence থেকে spec repair বা spec/implementation diagnosis নয়।

### C7 — ToolContractGate: Versioned Trusted Contracts for Drift-Safe Agent Tool Invocation

**লেখক:** Sachin Gupta। **তারিখ:** 2026-10-22, v1। **URL:** [arXiv:2610.33108](https://arxiv.org/abs/2610.33108)। **প্রমাণ:** abstract ও metadata-only; arXiv comments-এ ICCA 2026 acceptance দাবি।

Stored OpenAPI fingerprint ও access/schema/behavior declarations দিয়ে agent invocation-এর runtime contract decision দেয়। Abstract নিজেই semantic backend drift ও production traffic-কে ভবিষ্যৎ evaluation বলে। ⚠️ **Overlap: none, পরিদর্শিত scope-এ**—contract gate failure-origin diagnosis বা spec repair প্রতিষ্ঠা করে না।

## ৪. পরিচিত baseline ও তিন tool group-এর recent work

### C8 — Fault Injection in OpenAPI Specifications for Evaluating Black-Box Testing Effectiveness

**লেখক:** Hamza Bin Mazhar, Yuqing Wang, Mika V. Mäntylä। **তারিখ:** 2026-07-13, v1; arXiv comments-এ ISSRE 2026 accepted। **URL:** [arXiv:2607.12101](https://arxiv.org/abs/2607.12101)। **প্রমাণ:** বর্তমান abstract/history; পূর্বের method review `06_final_recommendations/R1_novelty_check_E0.md:39`।

Spec-fault taxonomy ও injection দিয়ে testing effectiveness মাপে। ⚠️ **Overlap: partial**—R1-এর ground truth ও experimental motivation-এ প্রাসঙ্গিক; E0 method review-এ attribution/repair তার scope-এর বাইরে (`06_final_recommendations/R1_novelty_check_E0.md:46`)।

### C9 — From REST to MCP: An Empirical Study of API Wrapping and Automated Server Generation for LLM Agents (SpecFix)

**লেখক:** Meriem Mastouri, Emna Ksontini, Amine Barrak, Wael Kessentini। **তারিখ:** v1 2025-07-21; সর্বশেষ দৃশ্যমান v4 2026-04-06। **URL:** [arXiv:2507.16044 ও history](https://arxiv.org/abs/2507.16044); [HTML §5.2 ও evaluation](https://arxiv.org/html/2507.16044v4)। **প্রমাণ:** relevant method/evaluation paragraph পরিদর্শিত।

SpecFix OpenAPI ও vendor documentation cues থেকে defect detect ও patch করে। Runtime-only category D/E evaluation থেকে স্পষ্টত বাদ। ⚠️ **Overlap: partial**—spec repair আছে; runtime evidence দিয়ে failure-origin attribution প্রতিষ্ঠা করে না। নতুন version পাওয়া যায়নি।

### C10 — RESTifAI: LLM-Based Workflow for Reusable REST API Testing

**লেখক:** Leon Kogler, Maximilian Ehrhart, Benedikt Dornauer, Eduard Paul Enoiu। **তারিখ:** 2025-12-09, v1; ICSE 2026 Demonstration track accepted (arXiv comments)। **URL:** [arXiv:2512.08706](https://arxiv.org/abs/2512.08706); [HTML §2–3](https://arxiv.org/html/2512.08706v1)। **প্রমাণ:** workflow/results পরিদর্শিত।

Runtime feedback দিয়ে happy path তৈরি ও structural/functional negative tests বানায়। ⚠️ **Overlap: partial**—failure-origin classification বা spec patch বর্ণিত output নয়। **E0 সংশোধন-প্রয়োজন:** E0-এর “Table 4; domain experts; Bug/Enhancement/Invalid” দাবি (`06_final_recommendations/R1_novelty_check_E0.md:79`) বর্তমান v1 HTML-এ পুনরুদ্ধার করা যায়নি; সেটি verified evidence হিসেবে পুনর্ব্যবহার করা হয়নি।

### C11 — Test Amplification for REST APIs via Single and Multi-Agent LLM Systems

**লেখক:** Robbe Nooyens, Tolgahan Bardakci, Mutlu Beyazit, Serge Demeyer। **তারিখ:** v1 2025-04-10; সর্বশেষ দৃশ্যমান v2 2025-08-04। **URL:** [arXiv:2504.08113](https://arxiv.org/abs/2504.08113); [HTML §4.3](https://arxiv.org/html/2504.08113v2#S4.SS3)। **প্রমাণ:** evaluation criteria পরিদর্শিত।

Failed/generated tests একজন author হাতে review করেন, অন্যজন verify করেন; label-এ API Bug Exposed, Missing Information, Semantically Incorrect, Runtime/Syntactical Error আছে। ⚠️ **Overlap: partial**—manual taxonomy কাজে লাগতে পারে, automated spec-versus-implementation attribution নয়।

### C12 — APISENSOR: Robust Discovery of Web API from Runtime Traffic Logs

**লেখক:** Yanjing Yang, Chenxing Zhong, Ke Han, Zeru Cheng, Jinwei Xu, Xin Zhou, He Zhang, Bohan Liu। **তারিখ:** 2026-03-25, v1। **URL:** [arXiv:2603.23852](https://arxiv.org/abs/2603.23852)। **প্রমাণ:** abstract/history-only।

Runtime traffic থেকে API discovery করে; abstract-এ community-confirmed documentation inconsistency উল্লেখ আছে। ⚠️ **Overlap: partial**—runtime evidence ও discrepancy finding প্রাসঙ্গিক; abstract থেকে OpenAPI repair বা causal attribution প্রতিষ্ঠিত নয়।

### C13 — RESTest at the REST League 2026 Tool Competition

**লেখক:** Alberto Mimbrero, Juan C. Alonso, Alberto Martin-Lopez, Sergio Segura। **তারিখ:** conference presentation 2026-04-12; পৃথক publication day যাচাই হয়নি। **URL:** [official SBFT program/abstract](https://conf.researchr.org/details/icse-2026/sbft-2026-papers/10/RESTest-at-the-REST-League-2026-Tool-Competition); [বর্তমান official repository](https://github.com/isa-group/RESTest)। **প্রমাণ:** abstract ও README-only।

Paper framework/configuration overview। বর্তমান README-তে RESTest 2 rewrite, OpenAPI ও replies থেকে test/check/report, reproducible curl আছে। ⚠️ **Overlap: none, বর্ণিত target capability-তে**—এই সূত্রে automatic origin diagnosis/spec patch ঘোষণা নেই; paper বা বর্তমান code-এর পূর্ণ audit করা হয়নি।

### C14 — EvoMaster at REST League 2026 Tool Competition

**লেখক:** Andrea Arcuri, Man Zhang, Susruthan Seran, Juan Pablo Galeotti, Amid Golmohammadi, Philip Garrett, Omur Sahin, Mohsen Taheri Shalmani, Franco Castagna, Iva Kertusha, Fanny Febriani Susilo, Guru Prasad Bhandari, Gebremariam Assres, Jefferson Seide Molléri। **তারিখ:** presentation 2026-04-12। **URL:** [official SBFT abstract](https://conf.researchr.org/details/icse-2026/sbft-2026-papers/12/EvoMaster-at-REST-League-2026-Tool-Competition)। **প্রমাণ:** abstract-only।

Search-based API fuzzer-এর competition results উপস্থাপন। ⚠️ **Overlap: none, পরিদর্শিত abstract-এ**—R1-এর causal attribution বা spec repair ঘোষিত contribution নয়; abstract-only সীমা প্রযোজ্য।

### C15 — Schemathesis: Multi-Phase Property-Based Testing of REST APIs

**লেখক:** Zac Hatfield-Dodds, Dmitry Dygalo। **তারিখ:** presentation 2026-04-12। **URL:** [official SBFT abstract](https://conf.researchr.org/details/icse-2026/sbft-2026-papers/8/Schemathesis-Multi-Phase-Property-Based-Testing-of-REST-APIs)। **প্রমাণ:** conference abstract-only।

Schema ও runtime response থেকে operation dependency inference, conformance checks ও failing-case reduction আছে। ⚠️ **Overlap: partial**—runtime adaptation আছে; বর্ণিত dependency inference-কে spec/implementation attribution বা specification patch বলা যাবে না।

### C16 — Triaging Failures (Schemathesis documentation)

**লেখক/প্রকাশক:** Schemathesis project; ব্যক্তিগত byline নেই। **তারিখ:** page publication/update day অজ্ঞাত; access 2026-11-13। **URL:** [official guide](https://schemathesis.readthedocs.io/en/latest/guides/triage/); [Baseline guide](https://schemathesis.readthedocs.io/en/latest/guides/baseline/)। **প্রমাণ:** relevant sections পরিদর্শিত।

Guide মানুষকে undocumented responses batch-এ annotate করতে, schema mismatch আলাদাভাবে investigate করতে এবং server error reproduce করতে বলে; baseline known failure suppress করে। ⚠️ **Overlap: partial, manual workflow-তে**—“triaging” নামটি স্বয়ংক্রিয় causal classifier-এর প্রমাণ নয়।

### C17 — Fuzzing REST APIs in Industry: Necessary Features and Open Problems

**লেখক:** Andrea Arcuri, Alexander Poth, Olsi Rrjolli, Philip Garrett, Juan P. Galeotti। **তারিখ:** 2026-04-02, v1; ICST'25 paper-এর extension (arXiv comments)। **URL:** [arXiv:2604.01759](https://arxiv.org/abs/2604.01759)। **প্রমাণ:** abstract/history-only।

Industry feedback, EvoMaster features ও open problems নিয়ে কাজ। ⚠️ **Overlap: none (abstract-ভিত্তিক provisional screening)**—target capability-র প্রমাণ abstract-এ নেই; full method সম্পর্কে চূড়ান্ত নেতিবাচক দাবি করা হয়নি।

### C18 — Online Machine Learning Prediction of Failed Calls to Enhance REST API Fuzzing

**লেখক:** Mohsen Taheri Shalmani, Amid Golmohammadi, Juan Pablo Galeotti, Andrea Arcuri। **তারিখ:** QUATIC presentation 2026-09-10; publication day অজ্ঞাত। **URL:** [official program](https://2026.quatic.org/program/scientific-program); [EvoMaster publication list](https://github.com/WebFuzzing/EvoMaster/blob/master/docs/publications.md)। **প্রমাণ:** **metadata-only**, full paper/abstract পরীক্ষা হয়নি।

⚠️ **Overlap: partial (screening-only)**—failed-call prediction title-এর জন্য রাখা হয়েছে; prediction target ও label না পড়ে এটিকে R1-এর classifier বলা বা বাতিল করা যাবে না।

## ৫. সীমা, অমীমাংসিত প্রশ্ন ও পরবর্তী সিদ্ধান্ত

- **FDRRestTest retrieval সীমা:** publisher PDF link প্রথমে index metadata দিয়েছে, পরের method-text fetch-গুলি timeout/অপ্রাপ্য হয়েছে। সাত category ও repair target অজানা; conference/publisher authorship-ও আলাদা (C3)। এটি final novelty verdict-এর বাধা, এই watch report লেখার বাধা নয়। আর retry বাড়ানো হয়নি; অর্জিত evidence ও অমীমাংসিত অংশ আলাদা রাখা হয়েছে।
- **Search completeness:** সরাসরি ACM DL/IEEE Xplore structured database search, Google Scholar citation graph ও সব group member-এর publication audit করা হয়নি। এই watch systematic literature review নয়; ফল না পাওয়া থেকে “কাজ নেই” সিদ্ধান্ত আসে না (§২)। EvoMaster official 2026 bibliography দেখা হয়েছে, কিন্তু সব listed paper-এর পূর্ণ পাঠ হয়নি ([publication list](https://github.com/WebFuzzing/EvoMaster/blob/master/docs/publications.md))।
- **তারিখ ও version:** DualMine page-এর date/ID অমিল প্রকাশকের কাছে যাচাইযোগ্য প্রশ্ন (C4)। Undated live docs থেকে অক্টোবর–নভেম্বরে capability প্রথম এসেছে বলা যাবে না (C5, C16)। Conference talk date ও publication date এক নয় (C13–C15, C18)।
- **Commercial প্রমাণ:** Beeceptor/Equixly capability vendor-এর দাবি; correctness, safety বা attribution accuracy স্বাধীনভাবে মাপা হয়নি (C5–C6)। কোনো tool চালানো হয়নি।
- **⚠️ R1-এর গ্রহণযোগ্য সংকীর্ণ অবস্থান:** intended contract ও runtime behavior-এর disagreement-এ **spec defect / implementation fault / insufficient evidence** সিদ্ধান্ত এবং তার ভিত্তিতে repair/abstention মূল্যায়ন করা। শুধু discrepancy detection বা observed behavior অনুসারে constraint বদলানো যথেষ্ট novelty নয়—C4–C5-এর সঙ্গে সরাসরি তুলনা দরকার। এটি সুপারিশ, প্রতিষ্ঠিত research result নয়।
- **Open questions:** C3-এর সাত category-তে specification defect আছে কি? Repair OpenAPI artifact পরিবর্তন করে কি? C18-এর failed-call label কী? C4-এর constraint adaptation ভুল implementation-কে কতটা অনুসরণ করে? C10-এর E0 Table 4 দাবি কোন version/source থেকে এসেছে? সংশ্লিষ্ট evidence C3/C18/C4/C10-এ দেওয়া আছে।

## ৬. সম্পন্ন কাজ ও validation

এই report-এ exact query log, candidate metadata, evidence depth, overlap ও conditional novelty verdict লেখা হয়েছে। কেবল task-এর report এবং board-এর T9 Status/Log লেখা হয়েছে (`09_collab/tasks/T9.md:6`; board T9 row)। Literature-only deliverable হওয়ায় software test প্রযোজ্য নয়; Markdown, source URL উপস্থিতি ও assigned-path সীমা local inspection-এ যাচাই করা হয়েছে।
