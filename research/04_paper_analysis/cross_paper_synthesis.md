# Cross-Paper Synthesis — PHASE C (P001–P038)

> **হালনাগাদ 2026-11-13 — P038 সমস্যার সমাধান:** সঠিক paper (Ponce et al. 2025, IST 188:107870, author-hosted copy) এখন `paper/P038.pdf`-এ আছে। এর বিশ্লেষণ `04_paper_analysis/P038_analysis.md`-এ (৭৪টি study, confidence High)। এই নথিতে যেখানে P038-কে “substitute”, “P038*” বা “Ghani 2019” বলা হয়েছে, তা ঐতিহাসিক — সেগুলো এখন আর প্রযোজ্য নয়। T9-এর evidence strength এখন **মাঝারি** (`05_research_clusters/cluster_T9_microservices.md`)।


**তারিখ:** 2026-10-19 · **ভিত্তি:** ৩৮টি `Pxxx_analysis.md` + `evidence_matrix.csv` · **রীতি:** প্রতিটি দাবির পাশে paper ID; বিস্তারিত page/line `Pxxx_analysis.md`-এর §P-তে। ⚠️ = বিশ্লেষকের অনুমান; **[H]** = hypothesis (যাচাই হয়নি)।
**সতর্কতা:** P038 substitute document (Ghani et al. 2019; `document_integrity_report.md` §2)। এটি কেবল দুর্বল সহায়ক প্রমাণ।

---

## 1. Corpus-এর চিত্র

- **বছর:** ২০১৮ (১), ২০১৯ (৩), ২০২০ (২), ২০২১ (২), ২০২২ (৪), ২০২৩ (৭), ২০২৪ (৫), ২০২৫ (১১), ২০২৬ (৩)। ১৯টি (৫০%) ২০২৪-এর পরের।
- **ধরন:** survey/SLR/mapping ৫টি (P002, P009, P021, P029, P038*), dataset ১টি (P037), controlled experiment ১টি (P026), বাকিগুলো technique বা empirical।

**Cluster সদস্যপদ** (primary + secondary):

| Cluster | Primary | Secondary | মোট | মন্তব্য |
|---|---|---|---|---|
| T1 REST testing/fuzzing | P001–P008 | P011, P012, P015, P016, P018, P025, P033, P037, P038 | ১৭ | Corpus-এর কেন্দ্রীয় hub |
| T6 Docs/design/governance | P026–P028 | P001, P008, P009, P016, P018, P019, P020, P025, P030, P032, P035 | ১৪ | প্রায় সব cluster-কে স্পর্শ করে |
| T4 Spec inference | P016–P019 | P001, P003, P004, P005, P012, P013, P014, P027, P032 | ১৩ | T1-এর input-সমস্যার উত্তর |
| T8 LLM tool use/MCP | P032–P036 | P005, P007, P017, P022, P024, P031 | ১১ | সবচেয়ে নতুন; ২০২৪–২০২৬ |
| T5 Evolution | P020–P025 | P030, P031, P034, P035 | ১০ | |
| T3 Security | P012–P015 | P010, P029, P036, P037 | ৮ | |
| T7 API misuse | P029–P031 | P021, P024, P028, P034, P035 | ৮ | |
| T9 Microservices | P037, P038* | P011, P014, P020, P036 | ৬ | P038 substitute হওয়ায় দুর্বলতম primary প্রমাণ |
| T2 GraphQL/RPC | P009–P011 | — | ৩ | বিচ্ছিন্ন; কোনো secondary নেই |

- **Reproducibility:** বেশিরভাগ paper artifact (code/data) প্রকাশ করেছে। Low: P013, P038*। আংশিক: P006 (experiment data নেই), P025 (Medium-low)।
  - Medium বা ঝুঁকিপূর্ণ: live API বা proprietary LLM-নির্ভরতা (P007, P017, P032, P033, P035), confidential data (P011 industrial, P020)।

## 2. মূল আন্তঃ-paper থিম

### থিম ১ — Specification হলো সবকিছুর কেন্দ্র, কিন্তু spec-এর মান খারাপ

প্রায় প্রতিটি cluster-এ OpenAPI/spec হলো input, oracle বা documentation।

**Spec ও implementation-এর অমিল ব্যাপক:**
- Online testing-এ failure-এর ৬৩% এবং fault-এর ৫০% spec-response disconformity (P001)।
- ১,০০০+ APIs.guru spec-এর প্রায় ৯৯%-এ mismatch (P004)।
- Developer spec-এ ২২৮টি endpoint, ২,৭৯৫টি parameter ও ৫০২টি response বাদ পড়েছে। ৪টি constraint inconsistency developer নিশ্চিত করেছেন (P018)।
- Test-ভিত্তিক spec-এর তুলনায় static path analysis-এ response type ৭২% বেশি পাওয়া গেছে, non-200 response ১২৯% বেশি (P019)।
- Unspecified response property থেকে ৯টি service regression (P025)।
- Web-to-mobile inconsistency থেকে বাস্তব exploit (P013)।

**Spec-এর প্রকাশক্ষমতা কম ব্যবহৃত:**
- OpenAPI links ১,৯৫৫টির মধ্যে মাত্র ৯টি spec-এ (P014)।
- Inter-parameter dependency-র জন্য আলাদা IDL প্রয়োজন হয় (P016)।
- Parameter description-এ মাত্র ৩২% value-এর ইঙ্গিত থাকে (P004)।

**Documentation ও design-এর মান:**
- Documentation unit-এর ৭৮%-এ smell আছে (P028)।
- ১,৬৯,০৬১টি design-rule violation পাওয়া গেছে (P027)।
- Violation understandability কমায় — ১২টির মধ্যে ১১টি rule-এ (P026)।

**Downstream প্রভাব:**
- Fuzzer coverage-এর প্রধান বাধা faulty বা underspecified schema (P003)।
- MCP server generation-এ tool success ৭৬%। Spec defect ঠিক করলে তা ৯৪.২% হয় (P032)।
- LLM hallucination কমাতে API specification-ই মূল documentation উপাদান (৪১.৮০% → ৮৬.৮২%) (P035)।

⇒ **সংশ্লেষণ:** Spec-এর মান **testing, security, evolution ও LLM agent — চারটি ক্ষেত্রেই** একই bottleneck।
- T4-এর spec inference tool-গুলো (P017, P018, P019) মূলত **downstream মূল্য দেখায়নি**।
  - কোনো tool generated spec দিয়ে fuzzing বা agent কাজের end-to-end মূল্যায়ন করেনি (P017, P018-এর analyst limitation)।
  - P032-এর SpecFix একমাত্র ব্যতিক্রম, যদিও আংশিক।

### থিম ২ — Oracle সমস্যা অমীমাংসিত, এবং বেশিরভাগ “fault” দুর্বল সংকেত

- **প্রচলিত oracle:** 5xx ও schema violation (P002 survey; P001, P003–P007)।
- **এই oracle-এর ফল সন্দেহজনক:**
  - P015 দেখায় existing oracle ৮১২টি 500 ও ১২,৪১৩টি schema fault রিপোর্ট করে, যার severity প্রশ্নসাপেক্ষ।
  - P001-এ ৬টি server error বনাম ৫২টি invalid-input-accepted — অর্থাৎ 5xx-কেন্দ্রিক oracle বেশিরভাগ fault মিস করে।
- **বিকল্প oracle:**
  - Invariant mining (P008, precision ৮১.২%)।
  - Differential (P025)।
  - Access policy (P015)।
  - BOLA CPN (P014)।
  - Mass assignment (P012)।
  - Log/metric anomaly (P037 — কিন্তু anomaly = documented 4xx ⚠️)।
- **Frequency = correctness ভ্রান্তি:**
  - Static misuse detector-এর precision ১২%-এর নিচে, প্রধান কারণ valid-but-uncommon usage (P030)।
  - একই অনুমান invariant mining (P008)-এ আছে, এবং LLM hallucination-এ উল্টোভাবে দেখা যায় — low-frequency API-তে বেশি ভুল (P035)। ⚠️
- **Security-তে oracle প্রায় সবসময় seeded বা ownership-অনুমানভিত্তিক** (P012, P014, P015)।
  - BOLA-র V2 detection precision ০.২২ (P014)।

⇒ **সংশ্লেষণ:** “আরও coverage” থেকে “আরও **অর্থবহ** fault”-এর দিকে যাওয়ার প্রধান বাধা হলো oracle।
- LLM-ভিত্তিক semantic oracle-এর প্রস্তাব অনেক paper-এ আছে (P001, P006, P008, P011, P015 extension)।
- কিন্তু **কোনো paper এর মূল্যায়ন করেনি**।

### থিম ৩ — REST testing-এর coverage ছাদ ও তার কারণ

**Coverage-এর মাত্রা:**
- কোনো fuzzer ৬০% line coverage ছাড়ায়নি (P003)।
- EvoMasterWB-এর line coverage ৫২.৭৬% (P004)।
- AutoRestTest-এর method coverage ৫৮.৩% (P007)।
- Industrial RPC-তে গড় ১৭.৪৯% (P011)।

**বারবার আসা কারণ:**
1. External service বা third-party dependency (P003, P011)।
2. Database state বা NoSQL (P003, P011)।
3. String/regex এবং business-level validation (P003, P011)।
4. Inter-parameter dependency (P004, P005, P016)।
5. Authentication ও প্রাথমিক data (P003)।
6. Underspecified schema (P003, P004)।

**LLM-এর অবদান:**
- Value validity ও IPD-তে উন্নতি (P005)।
- Semantic dependency graph (P007)।
- কিন্তু comparison budget অসম (P005: সমান call বা সময়ে তুলনা নয়) ⚠️।
- Independent head-to-head তুলনা নেই (P007 extension)।

**Coverage বনাম bug — টানাপোড়েন:**
- P004-এ coverage–error correlation প্রায় ০.৭৯।
- কিন্তু P006-এ RandomWalk কম coverage নিয়েও সবচেয়ে বেশি bug পেয়েছে।
- P003-এ white-box কৌশল +৭.৫% coverage দিয়েছে, কিন্তু fault মাত্র +৩.৪।
- ⇒ Coverage fault-detection-এর অপূর্ণ proxy।

### থিম ৪ — LLM সব cluster-এ ঢুকেছে, কিন্তু মূল্যায়ন ভঙ্গুর

| ভূমিকা | Paper | পর্যবেক্ষণ |
|---|---|---|
| Test input/value generation | P005, P007 | উন্নতি আছে, কিন্তু budget অসম, live API |
| Spec generation | P017 | Endpoint F1 প্রায় ৯৮.৮%; ReAct agent variant-এ recall ৪৩.৮% কম; ছোট model ব্যর্থ |
| Tool use / API calling | P033, P034 | Retrieved top-5 API oracle API-এর চেয়ে ভালো (P033)। অথচ imperfect retriever accuracy ৪৭–৫২% কমায় (P034) — **টানাপোড়েন** |
| Hallucination / misuse | P031, P034, P035 | Hallucination সবচেয়ে সাধারণ misuse (P031)। GPT-4 GPT-3.5-এর চেয়ে বেশি hallucinate করে (P034)। High-frequency API-তে documentation-augmentation ক্ষতি করে (P035) |
| Deprecated API | P024 | বড় model-এ deprecated usage বেশি; outdated context-এ ৭০–৯০% |
| Tool evolution | P022 | Static-SFT deprecated call পুনরাবৃত্তি করে; parameter পরিবর্তন সবচেয়ে ক্ষতিকর |
| MCP ecosystem | P032, P036 | REST-এর পাতলা wrapper (৯২%), median ১৯% operation coverage। ৭.২% server-এ vulnerability pattern, ৫.৫%-এ tool poisoning |

⇒ **সংশ্লেষণ:**
- **Scale সমাধান নয়** (P024, P034)।
- **Context বা documentation-এর মান** নির্ধারক (P024, P035, P032)।
- মূল্যায়ন প্রায়ই LLM judge, live API বা synthetic modification-নির্ভর (P022 GPT-4-generated changes, P033 ToolEval) ⚠️।
- **Execution-validated, version-pinned benchmark অনুপস্থিত।**

### থিম ৫ — Evolution: syntactic ভালো বোঝা গেছে, behavioural নয়

- **Library স্তর:**
  - Non-major upgrade-এর ২০.১% breaking, কিন্তু মাত্র ৭.৯% client প্রভাবিত (P023)।
  - API evolution SLR-এ ৬৩.৯% গবেষণা কেবল Java-তে, এবং ৭৪% empirical study-তে statistical test নেই (P021)।
- **Microservice অনুশীলন:**
  - সবাই breaking change এড়ায় ও API version রাখে।
  - কিন্তু ১৭টি প্রতিষ্ঠানের মধ্যে মাত্র ৫টি behavioural পরিবর্তনকে breaking ধরে।
  - Event-driven API ১৩টিতে ব্যবহৃত, কিন্তু documented মাত্র ৩টিতে।
  - Consumer অজানা (P020)।
- **REST স্তর:** একমাত্র differential regression testing (P025) — ১৪টি regression, যার ৯টি behavioural।
- **LLM consumer:** P022, P024 — evolution এখন agent ও code-LLM-কেও ভাঙে।
- ⇒ **Behavioural breaking-change detection** এবং **REST/OpenAPI evolution benchmark** বারবার gap হিসেবে উঠে আসে (P020, P021, P023, P025)।
  - Consumer এখন মানুষ নয়, বরং LLM agent — এই নতুন মাত্রা যোগ হয়েছে (P022, P024, P032)।

### থিম ৬ — API security: শক্তিশালী technique, দুর্বল benchmark

- **Technique:**
  - Mass assignment (P012)।
  - BOLA log-ভিত্তিক detection (P014)।
  - Access-policy fuzzing (P015)।
  - Mobile API reconnaissance (P013)।
  - GraphQL cost-based DoS (P010)।
  - Security API misuse SLR (P029)।
  - MCP security (P036)।
- **Benchmark দুর্বল:**
  - বেশিরভাগ seeded বা synthetic।
  - Real-world API-তে Missed-Check fault পাওয়া যায়নি (P015)।
  - Misuse benchmark মাত্র ৫টি, সবই Java crypto/SSL (P029)।
  - LO2-এ attack traffic নেই (P037) ⚠️।
- **নতুন surface:**
  - MCP/tool interface — credential exposure, tool poisoning, excessive permission (P036)।
  - REST wrapper auth বাদ দেয় (P032)।
  - ⚠️ API-level authorization বা least-privilege বিশ্লেষণ MCP-তে হয়নি।

### থিম ৭ — মূল্যায়ন-পদ্ধতির পদ্ধতিগত দুর্বলতা

- **Self-evaluation bias:**
  - EvoMaster গোষ্ঠী নিজের tool মূল্যায়ন করেছে (P003, P011, P015)।
  - LlamaRestTest ও AutoRestTest একই গোষ্ঠীর, একই ১২টি service-এ মূল্যায়িত (P005, P007)।
  - Independent তুলনা বিরল — কেবল P004।
- **সংখ্যার অভ্যন্তরীণ অসঙ্গতি:**
  - P009 (growth rate)।
  - P021 (৬৩.৯/৬৬/৭০.৪%)।
  - P029 (১০ বনাম ১১ metric)।
  - P031 (sample count)।
  - P032 (৮০ বনাম ৭৭ API)।
  - P034 (৬৯৬ বনাম ৬২৬)।
  - P036 (১,৮৯৯/৫৮৩/৭৩)।
  - P038* (তারিখ ও সময়সীমা)।
- **Live API ও proprietary model:** replication ভঙ্গুর (P001, P007, P032, P033, P035)।
- **Seeded fault বা ক্ষুদ্র benchmark:** P008 (৫৭.৩% seeded), P012, P015, P016 (১৪৯ dependency)।
- **Statistics ঘাটতি:** P021-এর মেটা-ফলাফল (৭৪%); P005 (অসম budget)।

## 3. Cluster-সংযোগ (প্রাথমিক; PHASE D-তে বিস্তারিত)

- **T4 → T1:** spec inference fuzzing-এর input উন্নত করে, কিন্তু downstream মূল্যায়ন নেই।
- **T4/T6 → T8:** spec ও documentation-এর মান agent ও MCP reliability নির্ধারণ করে (P032, P035)। ⚠️ এটি কার্যকারণ প্রমাণ নয়।
- **T1 → T3:** fuzzing infrastructure-এর উপর security oracle (P012, P015)।
- **T5 → T8/T7:** API evolution LLM consumer-কে ভাঙে (P022, P024, P034)।
- **T7 ↔ T8:** LLM-generated code-এ misuse ও hallucination (P031, P034, P035)।
- **T9 ↔ T1/T3:** observability data testing ও security-র oracle হতে পারে [H] (P014, P037)।
- **T2 বিচ্ছিন্ন:** GraphQL testing মাত্র ৪টি study (P009)। ⚠️ REST technique-এর স্থানান্তর অনাবিষ্কৃত।

## 4. বিরোধ ও টানাপোড়েন (তালিকা)

| বিষয় | পক্ষ A | পক্ষ B | মন্তব্য |
|---|---|---|---|
| Coverage ≈ fault? | P004 (r প্রায় ০.৭৯) | P006 (RandomWalk), P003 (WB +৭.৫% cov, +৩.৪ fault) | Metric নির্ভর; mutation-based মূল্যায়ন দরকার (P004 extension) |
| Retrieval-এর মূল্য | P033 (retrieved > oracle) | P034 (imperfect retriever ক্ষতিকর), P035 (high-freq API-তে DAG ক্ষতিকর) | Confidence-gated retrieval (P035 DAG++) সম্ভাব্য সমাধান |
| বড় model ভালো? | P033 (GPT-4 শীর্ষ) | P024 (বড় model-এ deprecated বেশি), P034 (GPT-4 বেশি hallucinate করে) | Task-নির্ভর |
| Spec mismatch = fault? | P001 (৫০% fault F_OAS), P018 | P015 (schema fault-এর severity প্রশ্নসাপেক্ষ) | Spec error বনাম implementation error আলাদা করা দরকার |
| Perceived বনাম actual | P026: perceived difficulty ও প্রকৃত ভুল মেলে না | — | Self-report-ভিত্তিক survey-এর (P028) সীমা ⚠️ |
| Status-code oracle | P002, P001–P007 (প্রচলিত) | P015, P030 | Oracle-এর মান যাচাই করে না |

## 5. প্রাথমিক gap তালিকা (PHASE D-তে Class A/B/C যাচাই হবে)

| # | Gap | প্রমাণ (paper) | সমর্থনের ধরন |
|---|---|---|---|
| G1 | **REST/OpenAPI evolution benchmark** — breaking change-এর ground truth সহ, behavioural পরিবর্তন সহ | P021 (uniform benchmark চ্যালেঞ্জ), P023 (REST-এ এমন study নেই), P025 (খোলা version history নেই), P020 | একাধিক লেখকের explicit future work |
| G2 | **Behavioural breaking-change detection** (REST/microservice) | P020 (৫/১৭), P023, P025 | Explicit ও inferred |
| G3 | **MCP/tool interface-এর testing ও security** (fuzzing, access policy, least privilege) | P032, P036 (extension), P015 ও P012 (technique স্থানান্তর) [H] | Explicit (P036) + inferred |
| G4 | **Agent-centric MCP মূল্যায়ন** এবং spec-quality → agent-reliability কার্যকারণ | P032, P035, P033 | Inferred ⚠️ |
| G5 | **Real (non-seeded) REST security benchmark** | P012, P014, P015, P029 | Explicit ও inferred |
| G6 | **Semantic/LLM oracle**-এর মূল্যায়িত পদ্ধতি | P001, P002, P006, P008, P015 | Explicit future work |
| G7 | **Execution-validated, version-pinned API hallucination benchmark** (REST/OpenAPI) | P031, P034, P035 | Explicit |
| G8 | **LLM-যুগের (security) API misuse** — web API client | P029, P030, P031 | Explicit |
| G9 | **Generated spec-এর downstream মূল্যায়ন** (fuzzing, agent) | P017, P018, P019 | Inferred ⚠️ |
| G10 | **Independent, budget-equal REST tool তুলনা** (LLM-যুগ) | P004 (শেষ independent), P005, P007 | Inferred ⚠️ |
| G11 | **GraphQL/gRPC testing** — REST technique স্থানান্তর | P009, P011 | Explicit |
| G12 | **Event-driven/AsyncAPI** evolution ও documentation | P020 | Explicit (একটি উৎস — দুর্বল) |
| G13 | **Observability-ভিত্তিক oracle ও security anomaly dataset** | P037, P014 | Inferred ⚠️ |

*PHASE D-তে যোগ:* **G14** — runtime-এ spec-implementation mismatch-এর triage ও repair (P001, P004, P015, P018, P032)। চূড়ান্ত অবস্থা: `05_research_clusters/research_gap_register.csv`।

## 6. PHASE D-র জন্য নোট

- **Gap যাচাই:** G3, G4, G7, G12 সময়-সংবেদনশীল (২০২৫–২০২৬-এ দ্রুত পরিবর্তনশীল)। তাই লক্ষ্যভিত্তিক search প্রয়োজন।
- **P038 প্রতিস্থাপন:** না হওয়া পর্যন্ত T9 cluster report-এ evidence strength **নিম্ন** ঘোষণা করতে হবে।
- **Final table:** `evidence_matrix.csv`-এর ভিত্তিতে তৈরি করা হবে (সব paper × cluster × মূল তথ্য)।
