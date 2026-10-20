# Cluster T1 — REST API Testing & Fuzzing

**তারিখ:** 2026-10-19 · **Primary:** P001–P008 · **Secondary:** P011, P012, P015, P016, P018, P025, P033, P037, P038*
**ভিত্তি:** `04_paper_analysis/Pxxx_analysis.md`; gap যাচাই `research_gap_register.csv` (GV01–GV17)।
⚠️ = বিশ্লেষকের অনুমান। [H] = hypothesis।

## 1. ID ও নাম
T1 — Automated black-box/white-box test generation, fuzzing ও oracle for REST/OpenAPI APIs।

## 2. Research problem ও motivation
- REST API বাস্তবে সর্বব্যাপী, অথচ manual testing ব্যয়বহুল।
- OpenAPI spec থেকে স্বয়ংক্রিয়ভাবে বৈধ ও stateful request sequence তৈরি করা এবং fault শনাক্ত করা দরকার।
- Fault শনাক্তে প্রধান বাধা দুটি:
  - Parameter-এর valid value ও inter-parameter dependency।
  - Oracle।

## 3. Core research questions
- কীভাবে বেশি coverage ও বেশি fault পাওয়া যায় (P003–P007)?
- Research tool-গুলো industrial বা online পরিবেশে টেকে কি (P001)?
- Status code ছাড়া কীভাবে fault চেনা যায় (P008)?
- কোন open problem coverage আটকে রাখে (P003, P004)?

## 4. প্রাসঙ্গিক paper
| ID | ভূমিকা |
|---|---|
| P006 RESTler (ICSE 2019) | Stateful fuzzing-এর ভিত্তি: producer-consumer dependency inference ও dynamic-feedback pruning |
| P002 Survey (TOSEM) | ৯২টি article; ক্ষেত্রের মানচিত্র ও challenge |
| P003 Open problems (TOSEM) | ৭টি fuzzer × ১৯ SUT; open problem-এর শ্রেণিবিন্যাস |
| P004 No time to REST yet (ISSTA 2022) | ১০টি tool-এর independent তুলনা |
| P001 Online testing (FSE 2022) | ১৩টি industrial API, ১৫ দিন, multi-bot |
| P008 AGORA (ISSTA 2023) | Invariant-ভিত্তিক oracle |
| P005 LlamaRestTest (FSE 2025) | ছোট fine-tuned LLM |
| P007 AutoRestTest (ICSE 2025) | Multi-agent RL + semantic graph + LLM |
| Secondary | P011 (RPC fuzzing), P012/P015 (security oracle), P016/P018 (dependency/spec), P025 (regression), P033 (dependency → agent planning), P037 (negative test data), P038* (microservice testing level) |

## 5. গুরুত্বপূর্ণ ঐতিহাসিক অবদান
- **P006:** spec থেকে dependency inference ও feedback pruning — পরবর্তী প্রায় সব black-box tool-এর ভিত্তি।
- **P004 ও P003:** প্রথম বড় independent বা আধা-independent তুলনা। এরা “coverage ছাদ” ও open problem-এর তালিকা প্রতিষ্ঠা করে।

## 6. সাম্প্রতিক উন্নয়ন (২০২৪–২০২৬)
- **LLM-চালিত input:** P005 (fine-tuned SLM, quantization), P007 (GPT-3.5 + MARL)।
- **Oracle-এ বিস্ফোরণ (corpus-এর বাইরে, GV04):** MASTOR, RESTOR, SATORI, RBCTest, AGORA+ (TOSEM 2025)।
- **Corpus-এর বাইরে আরও (GV06, GV15):** RESTifAI, APIPilot, Lobrest (log-ভিত্তিক)। কেবল snippet-স্তরে দেখা।

## 7. প্রধান methodology
- Black-box (৭৩%, P002) বনাম white-box (EvoMaster-ভিত্তিক)।
- Search-based (evolutionary MIO — EvoMaster)।
- Reinforcement learning (Q-learning — ARAT-RL, AutoRestTest)।
- Grammar বা spec-driven generation।
- LLM-assisted value generation।
- Invariant mining।

## 8. Algorithm, tool ও architecture
- **Tool:** RESTler (BFS/RandomWalk), EvoMaster (MIO), RESTest (constraint-based, IDL), Schemathesis (property-based), ARAT-RL, MoRest, RESTGPT, LlamaRestTest, AutoRestTest (SPDG + ৪টি Q-learning agent), AGORA (Beet + Daikon)।
- **Architecture:** multi-bot online testing (P001)।

## 9. Dataset ও benchmark
- **EMB (EvoMaster Benchmark):** P003-এ ১৯টি API।
- **P004:** ২০টি Java/Kotlin service (৯৭৭K LOC)।
- **P005/P007:** একই ১২টি service (৯টি open + FDIC, Spotify, OhSome)।
- **P001:** ১৩টি industrial API — ৩৯০K failure dataset, Zenodo-তে।
- **P008:** ৭টি industrial API-র ১১টি operation।
- **APIs.guru spec corpus:** P004, P005, P014।

## 10. মূল্যায়ন রীতি
- **Coverage:** JaCoCo বা c8 দিয়ে line/branch/method; operation coverage।
- **Fault:** unique 500 error বা failure point।
- **Statistics:** Mann-Whitney ও A12 (P003, P011)।
- **ঘাটতি:**
  - P005-এ budget অসম।
  - P005/P007-এ fault গণনা “unique 500 per operation” ভিত্তিক।
  - Mutation-based মূল্যায়ন প্রায় নেই (P004 extension)।

## 11. প্রতিষ্ঠিত ফলাফল
1. **Coverage ছাদ:** কোনো tool-এর line coverage প্রায় ৬০% ছাড়ায় না (P003, P004, P007)।
2. **Dependency inference অপরিহার্য** (P006), এবং LLM value-generation উন্নত করে (P005, P007)।
3. **Spec-implementation অমিল ব্যাপক:**
   - P001-এ ৬৩% failure।
   - P004 অনুযায়ী প্রায় ৯৯% spec-এ mismatch আছে।
4. **Coverage-এর বাধা:** external service, DB state, regex/business validation, auth (P003)।
5. **Online testing-এ** ৮৭% fault প্রথম ৩ দিনে পাওয়া যায়, এবং data perturbation সবচেয়ে কার্যকর (P001)।

## 12. বিরোধ
- **Coverage ও fault-এর সম্পর্ক:**
  - P004-এ correlation প্রায় ০.৭৯।
  - P006-এ RandomWalk কম coverage নিয়েও সবচেয়ে বেশি bug পেয়েছে।
  - P003-এ white-box +৭.৫% coverage দিয়েছে, কিন্তু fault মাত্র +৩.৪।
- **White-box-এর সুবিধা প্রসঙ্গনির্ভর:** P003-এ ocvn-rest-এ white-box খারাপ করেছে।

## 13. লেখক-স্বীকৃত সীমাবদ্ধতা
- **P001:** black-box; quota; triage manual।
- **P003:** EMB-এর বাইরে সাধারণীকরণ সীমিত।
- **P004:** কেবল Java।
- **P005:** non-enum value-এ সীমিত।
- **P007:** LLM cost ও nondeterminism।
- **P008:** arithmetic invariant-এর FP; seeded error।

## 14. অতিরিক্ত বিশ্লেষণী সীমাবদ্ধতা ⚠️
- **Self-evaluation:** EvoMaster গোষ্ঠী (P003, P011, P015); LlamaRestTest/AutoRestTest একই গোষ্ঠীর ও একই benchmark-এ।
- **“Unique 500” মেট্রিক** fault-এর severity বা প্রকৃত bug প্রতিফলিত করে না (P015-এর প্রমাণ)।
- **Live API** (Spotify, FDIC)-এর উপর নির্ভরতায় replication ভঙ্গুর।

## 15. অপর্যাপ্ত প্রমাণের এলাকা
- LLM tool-গুলোর neutral তুলনা।
- Real-fault benchmark।
- Non-Java SUT।
- Spec-ত্রুটি বনাম implementation-ত্রুটির পৃথকীকরণ।

## 16. সম্ভাব্য gap (register থেকে)
- **G10** Independent budget-equal LLM tool তুলনা — Class B, Supported।
- **G14** Spec-implementation mismatch-এর runtime triage ও repair — Class B, Supported।
- **G9** Inferred spec দিয়ে downstream fuzzing — Class B, Supported।
- **G6** Semantic oracle — **Weakened** (২০২৫–২০২৬-এ সক্রিয়ভাবে সমাধান হচ্ছে)।

## 17. সম্ভাব্য technical উন্নতি
- External-service mocking (P003, P011)।
- Regex বা constraint solver integration।
- NoSQL-aware generation।
- Mutation testing দিয়ে fault মূল্যায়ন।

## 18. সম্ভাব্য নতুন approach [H]
- P001-এর ৩৯০K failure dataset ব্যবহার করে **failure → {spec defect, impl fault, noise} classifier**, সঙ্গে SpecFix-ধাঁচের dynamic repair (G14)।
- **Spec-enrichment pipeline** (P018/P019 + LLM) → fuzzer coverage-এর পরিবর্তন পরিমাপ (G9)।

## 19. প্রয়োজনীয় দক্ষতা ও resource
- Java/Python, Docker।
- EvoMaster/Schemathesis/RESTler চালানো।
- JaCoCo; statistics (A12)।
- GPU ঐচ্ছিক — P005-এর মতো ছোট model laptop-এ চলে।

## 20. চ্যালেঞ্জ ও ঝুঁকি
- Tool configuration-এ fairness।
- Live API drift।
- Fault ground truth তৈরির manual খরচ।
- এলাকাটি দ্রুত চলমান — ২০২৬-এর নতুন tool।

## 21. Baseline ও metric
- **Baseline:** EvoMaster (BB/WB), Schemathesis, RESTler, ARAT-RL, AutoRestTest, LlamaRestTest।
- **Metric:** line/branch coverage, operation coverage, unique failure point, mutation score, A12।

## 22. নতুন গবেষকের জন্য সুযোগ
- **G10 (empirical replication)** — কম infrastructure, পরিষ্কার মূল্যায়ন।
- **G14** — P001-এর public dataset দিয়ে শুরু করা যায়।

## 23. প্রমাণের মান ও অনিশ্চয়তা
**উচ্চ।**
- ৮টি peer-reviewed primary paper।
- একাধিক independent তুলনা (P003, P004)।
- Artifact সহজলভ্য।

**অনিশ্চয়তা:**
- Preprint version (P003 v2 বনাম TOSEM)।
- ২০২৫–২০২৬-এর oracle সংক্রান্ত কাজ কেবল snippet-স্তরে দেখা।
