# Cluster T4 — API Specification Inference & Constraints

**Primary:** P016, P017, P018, P019 · **Secondary:** P001, P003, P004, P005, P012, P013, P014, P027, P032
⚠️ = অনুমান। [H] = hypothesis।

## 1. ID ও নাম
T4 — Source code, LLM বা documentation থেকে OpenAPI spec, response type ও inter-parameter dependency inference এবং প্রকাশ।

## 2. Problem ও motivation
- Spec প্রায়ই অনুপস্থিত, অসম্পূর্ণ বা ভুল (P004-এ প্রায় ৯৯% mismatch; P018-এ developer spec থেকে endpoint ও parameter বাদ)।
- অথচ testing (T1), security (T3) ও agent (T8) — সবই spec-নির্ভর।

## 3. Core RQ
- Inter-parameter dependency কি প্রকাশ ও বিশ্লেষণযোগ্য (P016)?
- Static analysis (P018), path-sensitive type inference (P019) বা LLM (P017) দিয়ে কি নির্ভুল spec পাওয়া যায়?

## 4. Paper
| ID | পদ্ধতি | ভাষা/পরিধি |
|---|---|---|
| P016 IDL (TSC 2022) | DSL + CSP-ভিত্তিক analysis | ২২টি API-র ১৪৯টি dependency |
| P018 Respector (ICSE 2024) | Static analysis + symbolic constraint | Java/Spring |
| P019 RestPi (PACMPL 2025) | Path-sensitive type inference | Ruby on Rails (৫টি app, ১৩২ endpoint) |
| P017 OOPS (JSS 2026) | LLM, multi-stage | ১২টি API (৮ open-source, ৪ proprietary; ৫ ভাষা) |

## 5. ঐতিহাসিক অবদান
- **P016:** IDL — RESTest-এ dependency-সচেতন generation-এর ভিত্তি।

## 6. সাম্প্রতিক উন্নয়ন
- LLM-ভিত্তিক spec generation (P017; endpoint F1 প্রায় ৯৮.৮%)।
- ReAct-agent variant-এ recall ৪৩.৮% কম — অর্থাৎ agentic পদ্ধতি সবসময় ভালো নয়।

## 7. Methodology
- DSL ও constraint solving।
- Static program analysis।
- Type inference।
- LLM prompting pipeline।

## 8. Tool
- IDL analysis tool-suite (P016)।
- Respector (P018)।
- RestPi (P019)।
- OOPS (P017)।

## 9. Dataset
- **P016:** পূর্ববর্তী অধ্যয়নে ৪০টি API-র ২,৫৫৭ operation-এ ৬৩৩টি dependency; expressiveness-এ ২২টি API-র ১৪৯টি; ১৭৮টি test case।
- **P018:** ১৫টি open-source Java REST API (developer spec সহ); লেখক-নির্মিত ground truth।
- **P019:** ৫টি Rails app-এর ১৩২টি endpoint (Code.org, Discourse, Canvas ইত্যাদি)।
- **P017:** ১২টি API (৮টি open-source, ৪টি proprietary); expert ground truth।

## 10. মূল্যায়ন
- Developer spec বা হাতে-তৈরি gold-এর বিপরীতে precision/recall।
- **Downstream কাজে (fuzzing বা agent) মূল্যায়ন নেই** ⚠️।

## 11. প্রতিষ্ঠিত ফলাফল
- **Developer spec থেকে ব্যাপক বাদ (P018):** ২২৮টি endpoint, ২,৭৯৫টি parameter, ৫০২টি response।
- **Constraint recall কম:** P018-এ গড় ৫০%।
- **Non-200 response সবচেয়ে অবহেলিত:** P019-এ +১২৯%।
- **Spec প্রকাশক্ষমতা কম ব্যবহৃত:** OpenAPI links মাত্র ৯/১,৯৫৫ (P014)।

## 12. বিরোধ
- **Static বনাম LLM:**
  - P017 constraint-এ ৯২.৫% F1 দাবি করে, যেখানে P018-এর constraint recall ৫০%।
  - ভিন্ন benchmark, তাই সরাসরি তুলনীয় নয় ⚠️।

## 13. লেখক-স্বীকৃত সীমাবদ্ধতা
- **P018:** reflection ও unresolvable function।
- **P019:** কেবল Rails; feasibility যাচাই নেই।
- **P017:** ছোট model ব্যর্থ; auth ও 4xx inference নেই।
- **P016:** IDL manually লেখা।

## 14. বিশ্লেষণী সীমাবদ্ধতা ⚠️
- একই ভাষা বা framework-এ সীমিত।
- Gold standard ছোট।
- কেউ inferred spec দিয়ে test বা agent চালিয়ে মূল্য দেখায়নি।

## 15. অপর্যাপ্ত প্রমাণ
- Spec-এর কোন ঘাটতি downstream-এ সবচেয়ে ক্ষতিকর?
- Dependency (IDL)-এর স্বয়ংক্রিয় inference।

## 16. Gap
- **G9:** downstream মূল্যায়ন (Class B, Supported)।
- **G14:** runtime triage ও repair (Class B, Supported)।
- **G4:** spec quality → agent reliability (Class B/C)।

## 17. Technical উন্নতি
- Static + LLM hybrid (P018 extension)।
- LLM দিয়ে IDL inference (P016/P017 extension)।
- DB/ORM-মধ্যস্থ dependency।

## 18. নতুন approach [H]
- **“Spec completeness ablation”:** developer spec বনাম Respector/RestPi/OOPS-enriched spec → একই fuzzer ও agent-এ coverage, fault ও task success পরিমাপ।

## 19. দক্ষতা ও resource
- Static analysis (Soot/WALA, Ruby AST)।
- LLM API (খরচ কম: P017-এ প্রায় $০.৪১/API)।
- P018-এর ১৫টি Java API; EMB service।

## 20. ঝুঁকি
- Gold spec তৈরি ব্যয়বহুল।
- ভাষা-নির্দিষ্ট tool।
- LLM nondeterminism।

## 21. Baseline ও metric
- **Baseline:** Respector, springdoc, OOPS, developer spec।
- **Metric:** element precision/recall; downstream coverage, fault, task success।

## 22. নতুন গবেষকের সুযোগ
- G9 — tool ও SUT প্রকাশিত, feasibility উচ্চ।

## 23. প্রমাণের মান
**উচ্চ।**
- চারটি peer-reviewed paper; artifact প্রকাশিত।
- Downstream প্রভাবের প্রমাণ কেবল পরোক্ষ (P003, P004, P032)।
