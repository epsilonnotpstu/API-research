# Ranked Research Topics — PHASE E1–E2

**তারিখ:** 2026-10-19 · **ভিত্তি:** `05_research_clusters/research_gap_register.csv`, `gap_validation.md`, cluster report · **Scoring script:** `00_protocol/scripts/score_topics.py` → `_scoring.json`
⚠️ = অনুমান। [H] = hypothesis। Score হলো **বিশ্লেষকের প্রমাণ-ভিত্তিক বিচার**, novelty-র বস্তুনিষ্ঠ প্রমাণ নয়।
- Weakened gap (G6, G7, G8, G11) থেকে প্রার্থী তৈরি করা হয়নি।

---

## 1. Candidate প্রস্তাব (E1)

### R1 — Spec-implementation mismatch-এর runtime triage ও dynamic OpenAPI repair (G14)

- **Research title:** *Spec or Bug? Automated Triage of OpenAPI Conformance Failures and Evidence-Driven Specification Repair*
- **সমস্যা:**
  - REST testing-এ সবচেয়ে বেশি failure spec-response অমিল থেকে আসে: P001-এ ৬৩% failure, ৫০% fault।
  - কিন্তু ত্রুটিটি spec-এ নাকি implementation-এ, তা আলাদা করা হয় না।
  - ফলে developer-এর triage বোঝা বাড়ে (P015: ১২,৪১৩টি schema fault, severity প্রশ্নসাপেক্ষ)।
  - একই সাথে ভুল spec পরের সব কাজকে দূষিত করে: fuzzing (P003), MCP generation (P032), LLM call (P035)।
- **বিদ্যমান approach ও সীমা:**
  - P001-এর failure clustering (NLD) — triage manual।
  - P032 SpecFix — কেবল static defect; লেখকরা runtime-only defect বাদ দিয়েছেন।
  - P018/P019 — code থেকে spec, কিন্তু runtime failure ব্যবহার করে না।
  - Spec fault-injection study (GV16, 2607.12101) — repair নয়।
- **RQ:**
  1. Conformance failure-কে {spec defect, implementation fault, non-determinism/environment} শ্রেণিতে কতটা নির্ভুলভাবে স্বয়ংক্রিয়ভাবে ভাগ করা যায়?
  2. Runtime evidence-ভিত্তিক spec patch কতটা সঠিক এবং regression-মুক্ত?
  3. Repaired spec কি downstream fuzzer-এর false failure কমায় এবং coverage বাড়ায়?
- **Hypothesis [H]:**
  - H1: একাধিক evidence-এর সমন্বয় (response schema diff, multi-request consistency, code-derived spec যেমন Respector/RestPi, documentation text) single-signal heuristic-এর চেয়ে উচ্চ triage F1 দেবে।
  - H2: Repaired spec fuzzing-এ F_OAS false failure উল্লেখযোগ্যভাবে কমাবে, কিন্তু fault-detection কমাবে না।
- **Technical contribution:**
  1. লেবেলকৃত conformance-failure dataset।
  2. Triage classifier (rule + LLM hybrid)।
  3. Evidence-driven patch generator, যেখানে validity, locality ও re-test দিয়ে যাচাই হয়।
- **Methodology:**
  1. Open-source SUT (EMB, P004-এর service, P018-এর ১৫টি Java API) চালানো।
  2. Schemathesis/EvoMaster দিয়ে failure সংগ্রহ।
  3. Code পড়ে ground-truth label তৈরি।
  4. Spec fault injection দিয়ে নিয়ন্ত্রিত label তৈরি (2607.12101-এর taxonomy)।
  5. P001 Zenodo dataset (10.5281/zenodo.6941292) দিয়ে বাহ্যিক যাচাই — কী data আছে তা আগে যাচাই করতে হবে।
- **Input/Output:** OpenAPI + SUT + test log → failure label + spec patch।
- **Dataset/benchmark:** EMB, P018-এর ১৫টি API (developer spec সহ), P001 dataset, APIs.guru।
- **Baseline:**
  - সব F_OAS-কে implementation bug ধরা (naive)।
  - P001-এর NLD clustering।
  - SpecFix (static)।
  - শুধু LLM-prompt classifier।
- **Metric:** triage precision/recall/F1; patch correctness (manual), validity, locality; downstream false-failure হ্রাস, coverage, fault।
- **Implementation:** Python, Docker, Schemathesis/EvoMaster, OpenAPI parser, LLM API (ঐচ্ছিক local model)।
- **Effort:** মাঝারি (৪–৬ মাস ⚠️ অনুমান); GPU ছাড়াই সম্ভব।
- **ঝুঁকি:**
  - Ground-truth label-এর subjectivity।
  - Injected fault-এর বাস্তবতা।
  - SpecFix-এর পরবর্তী version-এর overlap।
- **Novelty অনিশ্চয়তা:** মাঝারি। Runtime triage + repair পাওয়া যায়নি, কিন্তু এলাকা চলমান।
- **গুরুত্ব:** testing, spec quality ও agent — তিনটির সংযোগস্থলে।
- **Supporting paper:** P001, P003, P004, P015, P018, P019, P025, P032, P035।
- **আরও যাচাই:**
  - 2607.12101 পূর্ণ পাঠ।
  - P032-এর সর্বশেষ arXiv version।
  - “OpenAPI repair dynamic/runtime” লক্ষ্যভিত্তিক search।

### R2 — Inferred/enriched spec-এর downstream মূল্য (G9)

- **Title:** *Do Inferred API Specifications Pay Off? A Downstream Evaluation for REST Fuzzing and LLM Tool Use*
- **সমস্যা:**
  - P017, P018, P019 spec-element accuracy মাপে।
  - কিন্তু inferred বা enriched spec fuzzer বা agent-এর ফল কতটা বদলায়, তা অজানা।
- **বিদ্যমান:** ICICL (GV13) কেবল example-এর প্রভাব দেখায়।
- **RQ:** developer, inferred ও merged spec-এ coverage, fault ও false failure কেমন বদলায়? কোন spec element (constraint, response, dependency) সবচেয়ে বেশি প্রভাব ফেলে?
- **Hypothesis [H]:** Constraint ও non-200 response সমৃদ্ধকরণ সবচেয়ে বেশি সুবিধা দেবে।
- **Contribution:** element-ablation-সহ empirical study ও open harness।
- **Methodology:**
  - P018-এর ১৫টি API (developer spec + Respector artifact)।
  - RestPi Rails app।
  - EvoMaster BB, Schemathesis, RESTler।
  - ১০টি run, A12।
- **Baseline ও metric:** developer spec; coverage, unique failure, mutation score।
- **Effort:** নিম্ন-মাঝারি।
- **ঝুঁকি:**
  - Tool-গুলোর artifact চালানো (পুরোনো dependency)।
  - ফল “প্রত্যাশিত” মনে হতে পারে।
- **Novelty অনিশ্চয়তা:** মাঝারি-উচ্চ (সরল নকশা)।
- **Supporting paper:** P003, P004, P016–P019, P032।
- **আরও যাচাই:** 2504.07250 পূর্ণ পাঠ।

### R3 — REST API-র behavioural breaking change: benchmark ও detection (G1 + G2)

- **Title:** *Beyond Schema Diffs: A Benchmark and Detector for Behavioural Breaking Changes in REST APIs*
- **সমস্যা:**
  - Schema-diff tool (oasdiff) behavioural পরিবর্তন দেখে না।
  - Practitioner-রা তা অবহেলা করেন: P020-এ ৫/১৭।
  - REST-এ open ground truth নেই (P021, P023, P025)।
- **RQ:**
  1. Open-source REST service-এর version history-তে behavioural breaking change কত সাধারণ?
  2. Differential testing ও invariant diff কতটা নির্ভুলভাবে সেগুলো ধরে?
- **Hypothesis [H]:** Cross-version invariant diff (AGORA-ধাঁচ) + response diff, schema-diff-এর চেয়ে বেশি breaking change ধরবে, এবং গ্রহণযোগ্য false alarm-এ।
- **Contribution:**
  1. Labelled version-pair benchmark।
  2. Hybrid detector।
  3. P023-ধাঁচের client-impact বিশ্লেষণ।
- **Methodology:** git history থেকে version pair → build → একই test suite উভয় version-এ চালানো → diff ও invariant → manual label।
- **Dataset:** EMB, GitHub OpenAPI history (ICWE 2024 dataset)।
- **Baseline:** oasdiff, P025 diagonal diff।
- **Metric:** precision, recall, false-alarm হার।
- **Effort:** উচ্চ-মাঝারি। পুরোনো version build ও labelling-এ খরচ।
- **ঝুঁকি:** নমুনায় যথেষ্ট breaking change না-ও থাকতে পারে; build failure।
- **Novelty অনিশ্চয়তা:** মাঝারি। Library BBC কাজ আছে, REST-এ পাওয়া যায়নি।
- **Supporting paper:** P008, P020, P021, P023, P025, P022, P024।
- **আরও যাচাই:** MSR/ICSME ২০২৫–২০২৬; GitHub OpenAPI dataset paper পূর্ণ পাঠ।

### R4 — Neutral, budget-equal LLM REST testing tool তুলনা (G10)

- **Title:** *LLM-Assisted REST API Testing Under Equal Budgets: An Independent Replication with Mutation-Based Fault Evaluation*
- **সমস্যা:** P005 ও P007 একই গোষ্ঠীর, একই benchmark-এ, অসম budget-এ। শেষ neutral তুলনা P004 (২০২২)।
- **RQ:** সমান call, সময় ও খরচে LLM tool কি প্রচলিত tool-এর চেয়ে ভালো? Mutation score-এ পার্থক্য কেমন?
- **Contribution:** neutral তুলনা, cost-normalized ফল, fault severity বিশ্লেষণ।
- **Baseline:** EvoMaster, Schemathesis, RESTler, ARAT-RL, AutoRestTest, LlamaRestTest, RESTifAI।
- **Metric:** coverage, mutation score, unique failure, $/fault।
- **Effort:** মাঝারি (LLM API খরচ)।
- **ঝুঁকি:** tool configuration-এর fairness নিয়ে বিতর্ক; “replication” হিসেবে কম novelty।
- **Supporting paper:** P003, P004, P005, P007।

### R5 — Spec quality-র নিয়ন্ত্রিত পরিবর্তন ও LLM agent reliability (G4)

- **Title:** *How Much Does Specification Quality Matter to LLM Agents? A Controlled Mutation Study on OpenAPI-Backed Tools*
- **সমস্যা:**
  - P032 ও P035 সংযোগ নির্দেশ করে, কিন্তু নিয়ন্ত্রিত কার্যকারণ পরীক্ষা নেই।
  - P026-এর মানুষ-ভিত্তিক experiment-এর LLM সংস্করণ নেই।
- **RQ:** কোন spec ত্রুটি (description অনুপস্থিত, type ভুল, constraint অনুপস্থিত, P027 rule লঙ্ঘন) agent-এর task success সবচেয়ে বেশি কমায়?
- **Methodology:**
  - Fixed task set।
  - Spec mutation operator।
  - Function-calling বা MCP-wrapped tool।
  - একাধিক model।
- **Baseline:** অপরিবর্তিত spec; SpecFix-repaired spec।
- **Metric:** task success, invalid call, silent failure।
- **ঝুঁকি:**
  - SilentProbe ও 2605.14312-এর সাথে overlap।
  - LLM nondeterminism ও খরচ।
  - Memorization।
- **Supporting paper:** P026, P027, P028, P032, P033, P035।

### R6 — REST-wrapping MCP server-এর access-policy testing (G3, narrowed)

- **সমস্যা:**
  - MCP wrapper auth বাদ দেয় (P032)।
  - mcp-scan excessive permission মিস করে (P036)।
  - কিন্তু broad MCP security ভিড়পূর্ণ (GV01, GV12)।
- **RQ:** Agent-mediated call-এ কি BOLA বা BFLA-ধাঁচের violation ঘটে, এবং P015-এর oracle কি সেগুলো ধরে?
- **ঝুঁকি:** খুব দ্রুত চলমান; ২০২৬-এর কাজ যাচাই আবশ্যক।
- **Supporting paper:** P012, P015, P032, P036।

### R7 — Real-world REST authorization vulnerability benchmark (G5)

- **সমস্যা:** সব security মূল্যায়ন seeded বা vulnerable-by-design SUT-এ (P012, P014, P015, P029)।
- **Methodology:** CVE বা fix-commit mining → reproducible Docker SUT → tool মূল্যায়ন।
- **ঝুঁকি:** কঠোর curation, নৈতিক সীমা, পর্যাপ্ত reproducible case না-ও মিলতে পারে।
- **Supporting paper:** P012, P014, P015, P029।

---

## 2. Weighted scoring (E2)

**ওজন (prompt-প্রস্তাবিত):** Novelty ২৫%, Feasibility ২৫%, Significance ২০%, Data/resource ১৫%, Evaluation/reproducibility ১৫%। প্রতিটি ১–৫।

| # | Topic | Novelty | Feasibility | Significance | Data | Eval | **Weighted** |
|---|---|---|---|---|---|---|---|
| 1 | **R1** Spec-impl triage + repair | 4 | 4 | 4 | 4 | 4 | **4.000** |
| 2 | **R2** Inferred spec downstream | 3 | 5 | 3 | 5 | 4 | **3.950** |
| 3 | **R4** Neutral LLM tool তুলনা | 2.5 | 4 | 3.5 | 5 | 5 | **3.825** |
| 4 | **R3** Behavioural breaking changes | 4 | 3 | 5 | 3 | 4 | **3.800** |
| 5 | **R5** Spec-quality × agents | 3 | 4 | 4.5 | 4 | 3.5 | **3.775** |
| 6 | **R6** MCP access-policy | 3 | 3 | 4 | 3.5 | 3 | **3.275** |
| 7 | **R7** Real security benchmark | 4 | 2 | 4.5 | 2 | 3.5 | **3.225** |

### Score-এর ব্যাখ্যা (প্রমাণসহ)

**R1**
- **Novelty ৪:** runtime triage বা repair পাওয়া যায়নি (GV16); SpecFix static-only।
- **Feasibility ৪:** tool ও SUT open; labelling মাঝারি।
- **Significance ৪:** ৬৩% failure (P001) এবং downstream প্রভাব (P032, P035)।
- **Data ৪:** P001 Zenodo, P018 API, APIs.guru।
- **Eval ৪:** label-ভিত্তিক F1, re-test দিয়ে patch যাচাই।

**R2**
- **Novelty ৩:** সরল নকশা; ICICL আংশিক overlap।
- **Feasibility ৫:** সব artifact প্রকাশিত।
- **Significance ৩:** T4-এর মূল্য প্রমাণ করে, কিন্তু সীমিত পরিধি।
- **Data ৫।**
- **Eval ৪:** coverage ও A12 প্রতিষ্ঠিত।

**R4**
- **Novelty ২.৫:** replication-ধরন।
- **Feasibility ৪:** LLM খরচ ও configuration।
- **Significance ৩.৫:** ক্ষেত্রের বিশ্বাসযোগ্যতা।
- **Data ৫, Eval ৫:** প্রতিষ্ঠিত benchmark ও metric।

**R3**
- **Novelty ৪:** behavioural label অনুপস্থিত (GV02, GV07, GV10)।
- **Feasibility ৩:** পুরোনো version build ও labelling।
- **Significance ৫:** তিন লেখক-গোষ্ঠী + practitioner প্রমাণ।
- **Data ৩:** নির্মাণ করতে হবে।
- **Eval ৪।**

**R5**
- **Novelty ৩:** adjacent কাজ আছে (GV03)।
- **Feasibility ৪।**
- **Significance ৪.৫:** agent-যুগে উচ্চ প্রাসঙ্গিকতা।
- **Data ৪:** APIs.guru।
- **Eval ৩.৫:** LLM nondeterminism।

**R6**
- **Novelty ৩:** ভিড়পূর্ণ এলাকা।
- **Feasibility ৩:** agent + auth setup।
- **Significance ৪।**
- **Data ৩.৫:** P036 dataset।
- **Eval ৩:** ground truth কঠিন।

**R7**
- **Novelty ৪।**
- **Feasibility ২:** curation খরচ।
- **Significance ৪.৫।**
- **Data ২:** তৈরি করতে হবে।
- **Eval ৩.৫।**

**Importance বনাম convenience:**
- “Significance” কলামে R3 (৫) ও R5/R7 (৪.৫) সবচেয়ে গুরুত্বপূর্ণ।
- R2 ও R4-এর উচ্চ score মূলত feasibility ও data-র সুবিধা থেকে।
- এই পার্থক্য সিদ্ধান্তে বিবেচনা করা হয়েছে (`best_research_direction.md`)।

## 3. Sensitivity analysis

| Weighting scheme (N/F/S/D/E) | ১ম | ২য় | ৩য় |
|---|---|---|---|
| Base ২৫/২৫/২০/১৫/১৫ | R1 4.00 | R2 3.95 | R4 3.83 |
| Importance-heavy ৩০/১৫/৩০/১০/১৫ | **R3 4.05** | R1 4.00 | R5 3.78 |
| Feasibility-heavy ১৫/৩৫/১৫/২০/১৫ | **R2 4.25** | R4 4.05 | R1 4.00 |
| Novelty-heavy ৪০/২০/২০/১০/১০ | R1 4.00 | R3 3.90 | R2 3.70 |
| Equal ২০ × ৫ | R1 = R2 = R4 4.00 | — | R3 = R5 3.80 |

**Perturbation (base weight):**
- R1-এর novelty ১ কমালে (৪→৩): ৩.৭৫, এবং R1 ৫ম স্থানে নেমে যায়।
- R5-এর novelty ১ বাড়ালে (৩→৪): ৪.০২৫, এবং R5 ১ম স্থানে ওঠে।
- R4-এর novelty +০.৫: ৩.৯৫।

**ব্যাখ্যা:**
- R1 পাঁচটির মধ্যে চারটি scheme-এ শীর্ষে বা যুগ্ম-শীর্ষে, এবং কোনোটিতেই ৩য়-এর নিচে নয়। তাই তুলনামূলকভাবে **robust**।
- কিন্তু R1-এর অগ্রাধিকার novelty-অনুমানের উপর সংবেদনশীল।
  - R1-এর novelty যদি ৩ হয় (যেমন পূর্ণ পাঠে 2607.12101 বা SpecFix-এর runtime সংস্করণ পাওয়া যায়), তাহলে R2, R4, R3 ও R5 সবাই R1-কে ছাড়িয়ে যায়।
  - তখন R2 ১ম হয়।
- অর্থাৎ **R1-এর পূর্ণ-পাঠ novelty যাচাই সিদ্ধান্ত-নির্ধারক।**
- গুরুত্ব-কেন্দ্রিক বিচারে R3 শীর্ষে। Feasibility-কেন্দ্রিক বিচারে R2।
