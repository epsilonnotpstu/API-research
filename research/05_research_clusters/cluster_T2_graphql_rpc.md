# Cluster T2 — GraphQL & RPC APIs

**Primary:** P009, P010, P011 · **Secondary:** —
⚠️ = অনুমান। [H] = hypothesis।
**Cluster গঠনের যুক্তি:**
- তিনটি paper-এর মিল হলো non-REST API paradigm।
- পদ্ধতি ভিন্ন:
  - Mapping study (P009)।
  - Formal cost analysis (P010)।
  - White-box fuzzing (P011)।
- ⚠️ ছোট ও বৈচিত্র্যময় cluster। P011 পদ্ধতিগতভাবে T1-এর কাছাকাছি।

## 1. ID ও নাম
T2 — GraphQL ও RPC (gRPC/Thrift) API-র গবেষণা: testing, cost/DoS ও ecosystem।

## 2. Problem ও motivation
- GraphQL-এর নমনীয় query বড় খরচ ও DoS ঝুঁকি তৈরি করে (P010)।
- GraphQL গবেষণা খণ্ডিত (P009)।
- RPC API-তে REST fuzzing technique-এর স্থানান্তর প্রয়োজন, বিশেষত industrial microservice-এ (P011)।

## 3. Core RQ
- GraphQL গবেষণার অবস্থা কী (P009)?
- Query cost কি নির্ভরযোগ্যভাবে over-approximate করা যায় (P010)?
- White-box search কি industrial RPC-তে কার্যকর (P011)?

## 4. Paper
- **P009** GraphQL systematic mapping (ACM CSUR 2023)।
- **P010** Principled GraphQL query cost analysis (FSE 2020)।
- **P011** EvoMaster RPC industrial case study (TOSEM 2023)।

## 5. ঐতিহাসিক অবদান
- **P010:** linear-time static cost analysis।
  - GitHub-এ DoS vector প্রকাশ ও patch হয়েছে।
  - IBM API Connect-এ ship হয়েছে — বাস্তব প্রভাবের বিরল উদাহরণ।

## 6. সাম্প্রতিক উন্নয়ন
- **P011 (2023):** Meituan-এর ৫০টি industrial API।
- **Corpus-এর বাইরে (GV08, snippet-স্তর):**
  - EvoMaster GraphQL (TWEB 2024)।
  - PrediQL (LLM, 2025)।
  - SGAFuzzer (stateful, 2026)।
  - BenGQL benchmark (ASE 2025)।
- ⇒ P009-এর “মাত্র ৪টি testing study” এখন পুরোনো।

## 7. Methodology
- Mapping study (P009)।
- Formal semantics ও static analysis (P010)।
- Search-based white-box testing (MIO) (P011)।

## 8. Tool ও architecture
- P010-এর cost analysis library।
- EvoMaster RPC driver (P011)।

## 9. Dataset
- **P010:** ২টি commercial schema + ১০,০০০ query corpus (Zenodo)।
- **P009:** ২,০৯৪টি schema-র cycle তথ্য।
- **P011:** ৫০টি industrial API (গোপন) + artificial SUT।

## 10. মূল্যায়ন
- **P010:** over/under-estimation হার, median error।
- **P011:** line/target coverage, triaged real fault, A12 (৩০ run)।

## 11. প্রতিষ্ঠিত ফলাফল
- **P010:** under-estimation শূন্য; median error ১৯%, যেখানে libA-তে ৬৩৪%।
- **P011:** random-এর চেয়ে ভালো (A12 >০.৮০)।
  - Industrial coverage মাত্র ১৭.৪৯%।
  - ১২৬টি real fault, যার ৪১টি fixed।
- **P009:** ৩৯.৭৩% schema-তে cycle; directive, subscription ও validation সবচেয়ে কম অধ্যয়িত।

## 12. বিরোধ
- **P009 অনুযায়ী** GraphQL জটিল query-তে দ্রুত, কিন্তু সরল query-তে ধীর — অর্থাৎ পারফরম্যান্সের দাবি প্রসঙ্গনির্ভর।

## 13. লেখক-স্বীকৃত সীমাবদ্ধতা
- **P010:** resolver configuration manual।
- **P011:**
  - External service, business validation, বিশাল DTO ও DB state coverage আটকায়।
  - ৮,৩৭৭টি potential fault-এর triage বাকি।

## 14. বিশ্লেষণী সীমাবদ্ধতা ⚠️
- **P011:** industrial data গোপন এবং self-evaluation।
- **P009:** ২০২১-এর পরের কাজ অনাবৃত।
- **P010:** ৫ বছর পুরোনো; LLM agent query-র cost বিবেচিত নয়।

## 15. অপর্যাপ্ত প্রমাণ
- GraphQL authorization (field-level) testing।
- gRPC open benchmark।
- Subscription testing।

## 16. সম্ভাব্য gap
- **G11:** GraphQL/RPC testing — **Weakened** (GV08)।
  - Residual: GraphQL field-level authorization testing (Class C, যাচাই হয়নি)।

## 17. Technical উন্নতি
- Cycle-aware query generation।
- Cost-aware fuzzing (P010 + fuzzing)।
- Open gRPC benchmark।

## 18. নতুন approach [H]
- **LLM agent-এর GraphQL query-তে cost bound:** agent-উৎপন্ন query-র DoS ঝুঁকি (P010 × T8)।

## 19. দক্ষতা ও resource
- GraphQL server (Apollo বা graphql-java)।
- EvoMaster।
- Static analysis-এর জ্ঞান।

## 20. ঝুঁকি
- এলাকাটি ২০২৪–২০২৬-এ দ্রুত পূরণ হচ্ছে, তাই novelty ঝুঁকি উচ্চ।

## 21. Baseline ও metric
- **Baseline:** EvoMaster GraphQL, PrediQL, SGAFuzzer।
- **Metric:** coverage, fault, cost estimation error।

## 22. নতুন গবেষকের সুযোগ
- সীমিত।
- GraphQL authorization testing বিবেচ্য, তবে আগে লক্ষ্যভিত্তিক search প্রয়োজন।

## 23. প্রমাণের মান
**মাঝারি।**
- তিনটি শক্তিশালী peer-reviewed paper আছে।
- কিন্তু cluster ছোট ও বৈচিত্র্যময়।
- Corpus-এর বাইরের সাম্প্রতিক কাজ পূর্ণ পাঠে যাচাই হয়নি।
