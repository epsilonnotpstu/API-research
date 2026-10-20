# Research Execution Roadmap — PHASE E4 (Top recommendation: R1)

**তারিখ:** 2026-10-19 · ⚠️ = অনুমান। [H] = hypothesis। সময়-অনুমান আনুমানিক।
- Publication-এর নিশ্চয়তা দেওয়া হচ্ছে না।
- Global novelty দাবি করা হচ্ছে না।

## 1. Refined research title
**Spec or Bug? Evidence-Driven Triage of OpenAPI Conformance Failures and Runtime Specification Repair for REST APIs**

## 2. সুনির্দিষ্ট problem statement
- REST API testing tool-গুলো response ও OpenAPI spec-এর অমিলকে failure হিসেবে রিপোর্ট করে।
- এগুলোই failure-এর সবচেয়ে বড় অংশ: P001-এ ৬৩% failure ও ৫০% confirmed fault।
- কিন্তু অমিলের উৎস তিনটির যেকোনোটি হতে পারে:
  - ভুল বা অসম্পূর্ণ spec।
  - ভুল implementation।
  - Non-deterministic বা পরিবেশগত noise।
- বর্তমানে এই পৃথকীকরণ manual (P001)। একমাত্র স্বয়ংক্রিয় spec-repair পদ্ধতি static analysis-এ সীমিত (P032 SpecFix)।
- ফলাফল:
  - Developer-এর triage বোঝা বাড়ে (P015)।
  - ভুল spec fuzzing (P003), MCP tool generation (P032) ও LLM API call (P035)-কে দূষিত করে।

## 3. Objectives
- **O1:** Conformance failure-এর একটি লেবেলকৃত dataset ও taxonomy তৈরি।
- **O2:** Failure triage-এর স্বয়ংক্রিয় পদ্ধতি — multi-evidence, rule + LLM।
- **O3:** Runtime evidence-ভিত্তিক spec patch generation ও যাচাই।
- **O4:** Repaired spec-এর downstream প্রভাব পরিমাপ (R2-এর অন্তর্ভুক্তি)।

## 4. Research questions
- **RQ1 (characterisation):** Open-source REST API-তে conformance failure-এর কত অংশ spec defect, কত অংশ implementation fault, আর কত অংশ noise? কোন spec element-এ সবচেয়ে বেশি?
- **RQ2 (triage):** প্রস্তাবিত triage পদ্ধতি baseline-এর তুলনায় কতটা নির্ভুল?
- **RQ3 (repair):** Generated patch কতটা সঠিক, local ও regression-মুক্ত?
- **RQ4 (downstream):** Repaired বা enriched spec দিয়ে fuzzer-এর false failure, coverage ও fault-detection কীভাবে বদলায়?

## 5. Hypotheses [H]
- **H1:** Spec-defect-জনিত failure সংখ্যাগরিষ্ঠ নয়, কিন্তু উল্লেখযোগ্য (≥৩০%)।
  - ⚠️ এটি P001 ও P004-এর পরোক্ষ ইঙ্গিত থেকে অনুমান।
- **H2:** Multi-evidence triage (multi-request consistency + code-derived spec + documentation text) single-signal baseline-এর চেয়ে উচ্চ macro-F1 দেবে।
- **H3:** Repaired spec fuzzing-এ F_OAS-ধাঁচের false failure কমাবে, কিন্তু implementation-fault detection কমাবে না।

## 6. প্রস্তাবিত system ও experimental approach

```
OpenAPI spec + SUT ──▶ Fuzzer (Schemathesis / EvoMaster BB) ──▶ Conformance failures
                                                            │
     Evidence collectors:                                   ▼
     (a) multi-request consistency (same op, varied inputs) ─┐
     (b) code-derived spec (Respector / RestPi, if available)├─▶ Triage classifier
     (c) spec text & examples, docs                          │   (rules + LLM, explainable)
     (d) cross-version / history (optional)                  ┘          │
                                       spec-defect ◀────────────────────┤──────▶ impl-fault report
                                            ▼                                    (to developer)
                              Patch generator (minimal JSON-Patch on OAS)
                                            ▼
                     Validation: parse validity · locality · re-test (no new failures)
                                            ▼
                         Repaired spec ──▶ downstream re-fuzzing (RQ4)
```

## 7. Data requirements
- **SUT:**
  - P018-এর ১৫টি open-source Java REST API, developer spec সহ (Software Heritage-এ archived)।
  - EMB-এর REST API (P003)।
  - P004-এর ২০টি service।
  - ঐচ্ছিক: P019-এর Rails app।
- **বাহ্যিক dataset:** P001 Zenodo (10.5281/zenodo.6941292)।
  - ⚠️ এতে raw request/response আছে কিনা, প্রথম সপ্তাহে যাচাই করতে হবে।
- **Ground truth:**
  - Source code পড়ে manual label — দুইজন labeller ও Cohen's κ।
  - Spec fault injection (2607.12101-এর taxonomy, পূর্ণ পাঠের পর) থেকে নিয়ন্ত্রিত label।

## 8. Benchmark ও baseline strategy
- **Triage baseline:**
  - Naive — সব অমিল = implementation bug (tool-গুলোর বর্তমান ডিফল্ট)।
  - P001-এর NLD clustering + majority heuristic।
  - Zero-shot LLM classifier (একই প্রমাণ ছাড়া)।
- **Repair baseline:**
  - SpecFix (P032; artifact পাওয়া গেলে)।
  - Code-derived spec দিয়ে প্রতিস্থাপন (Respector)।
  - কোনো repair না করা।
- **Downstream baseline:** developer spec, Respector spec, merged spec।

## 9. Evaluation methodology
- **Triage:** per-class precision, recall ও macro-F1; confusion matrix; label-এর κ।
- **Repair:** manual correctness (correct / partial / wrong), parse validity, edit locality, re-test regression।
- **Downstream:**
  - Line/branch coverage (JaCoCo)।
  - False-failure হার।
  - Unique implementation fault।
  - Mutation score (ঐচ্ছিক)।
  - ১০টি run, Mann-Whitney U ও A12।
- **Threats:** label subjectivity, Java-কেন্দ্রিকতা, LLM nondeterminism (seed বা temperature ০; একাধিক run)।

## 10. সম্ভাব্য contribution
1. লেবেলকৃত conformance-failure dataset ও taxonomy (open)।
2. Triage পদ্ধতি ও tool।
3. Runtime evidence-ভিত্তিক spec repair।
4. Spec repair-এর downstream মূল্যের empirical প্রমাণ।

## 11. প্রধান ঝুঁকি
| ঝুঁকি | প্রশমন |
|---|---|
| Novelty overlap (SpecFix runtime version, 2607.12101) | মাস ১-এ পূর্ণ পাঠ। Overlap থাকলে RQ1 ও RQ4-এ (characterisation + downstream) পিভট |
| Label subjectivity | Double labelling, κ, ambiguity class |
| পুরোনো artifact build ব্যর্থ | Docker image; EMB-এর maintained SUT অগ্রাধিকার |
| Spec-defect-এর সংখ্যা কম | Fault injection দিয়ে সম্পূরক |
| LLM খরচ ও nondeterminism | ছোট local model; rule-first নকশা |

## 12. অনুপস্থিত প্রমাণ (শুরুর আগে)
- 2607.12101 (spec fault injection) ও SpecFix-এর সর্বশেষ arXiv version — পূর্ণ পাঠ।
- P001 Zenodo dataset-এর বিষয়বস্তু।
- “OpenAPI repair runtime/dynamic” ও “spec drift detection REST” — লক্ষ্যভিত্তিক scholarly search (OpenAlex/ACM DL)।
- P038-এর সঠিক paper (T9 প্রসঙ্গ; R1-এর জন্য গৌণ)।

## 13. প্রাথমিক experiment-এর ক্রম

| ধাপ | কাজ | আউটপুট | আনুমানিক সময় ⚠️ |
|---|---|---|---|
| E0 | Novelty যাচাই: উপরের পাঠ ও search | Go/pivot সিদ্ধান্ত-নোট | ১–২ সপ্তাহ |
| E1 | ৩–৫টি SUT (P018 + EMB) Docker-এ চালানো; Schemathesis/EvoMaster BB দিয়ে failure সংগ্রহ | Failure log | ২ সপ্তাহ |
| E2 | Pilot labelling: ২০০টি failure, দুইজন labeller, taxonomy খসড়া | κ, taxonomy v1 | ২ সপ্তাহ |
| E3 | **R2 pilot:** developer বনাম Respector spec দিয়ে fuzzing তুলনা | প্রথম empirical ফল (RQ4 প্রাথমিক) | ২–৩ সপ্তাহ |
| E4 | Rule-based triage baseline + evidence collector (a)–(c) | RQ2 প্রাথমিক F1 | ৩ সপ্তাহ |
| E5 | LLM-assisted triage ও patch generator; validation loop | RQ3 প্রাথমিক | ৪ সপ্তাহ |
| E6 | Scale-up (১০+ SUT), fault injection, পূর্ণ মূল্যায়ন | পূর্ণ ফল | ৬–৮ সপ্তাহ |

## 14. Supervisor বা মানুষের সিদ্ধান্ত দরকার
1. **P038:** সঠিক PDF (Ponce et al. 2025) সংগ্রহ করা হবে কি?
2. **Scope:** Java-only (P018 SUT) নাকি বহুভাষিক (Rails/Node)?
3. **LLM:** proprietary API ব্যবহার অনুমোদিত কি, নাকি কেবল local open model?
4. **Option:** R1 (B) গ্রহণযোগ্য, নাকি কম-ঝুঁকির R2 (A) বা উচ্চ-প্রভাবের R3 (C)?
5. **Labelling resource:** দ্বিতীয় labeller কে হবেন?
6. **লক্ষ্য venue বা সময়সীমা:** thesis, workshop নাকি conference? ⚠️ এর উপর scope নির্ভর করবে।
