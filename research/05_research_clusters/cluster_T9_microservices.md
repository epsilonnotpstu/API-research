# Cluster T9 — Microservice APIs, Testing & Observability

**Primary:** P037, P038 · **Secondary:** P011, P014, P020, P036
**হালনাগাদ 2026-11-13:** P038 এখন সঠিক paper — Ponce et al. 2025, IST, ৭৪টি study-র SLR। আগের substitute (Ghani 2019) বাদ। ⇒ এই cluster-এর প্রমাণ “নিম্ন” থেকে “মাঝারি”-তে উন্নীত।
⚠️ = অনুমান। [H] = hypothesis।

## 1. ID ও নাম
T9 — Microservice-ভিত্তিক সিস্টেমে API testing ও observability (log, metric, trace)।

## 2. Problem ও motivation
- Microservice-এ API-র সংখ্যা ও পারস্পরিক নির্ভরতা বেশি। System ও integration level-এ testing কঠিন (P038 p.1)।
- Testing ও anomaly detection-এর জন্য multi-modal data ও system-level পদ্ধতি দরকার (P037)।

## 3. Core RQ
- Microservice testing-এ কোন level, objective, strategy প্রচলিত, আর কতটা পরিণত (P038)?
- API-error-চালিত anomaly কি log ও metric থেকে শনাক্তযোগ্য (P037)?

## 4. Paper
| ID | ধরন |
|---|---|
| P038 Ponce et al. (IST 2025) | ৭৪টি study-র SLR — SWEBOK, ISO 25010, TRL, SUT |
| P037 LO2 (PROMISE 2025) | Dataset + preliminary analysis |
| Secondary | P011 (industrial RPC microservice), P014 (log-ভিত্তিক BOLA), P020 (microservice API evolution), P036 (MCP server health) |

## 5. ঐতিহাসিক অবদান
- P038 অনুযায়ী ক্ষেত্রটি ২০১৫-এ শুরু, ২০১৮ থেকে দ্রুত বৃদ্ধি।
- P038 আগের secondary study-গুলো (Waseem, Ghani, Hui, Fischer, Simosa) সংশ্লেষণ করেছে।

## 6. সাম্প্রতিক উন্নয়ন
- ২০২৪-এ সর্বোচ্চ ১৪টি paper (P038)।
- **P037:** LO2 (২০২৫)।
- **Corpus-এর বাইরে (GV15):** AnoMod (EvoMaster-চালিত multimodal dataset), Lobrest (log-ভিত্তিক REST testing)।

## 7. Methodology
- **P038:** SLR — দুটি উৎস (Google Scholar + Scopus), Fleiss’ κ ০.৭৮, saturation-পর্যন্ত snowballing।
- **P037:** dataset নির্মাণ (Locust-এর correct ও error task), LogLead ML, PCA।

## 8. Tool
- **P038-এ উল্লিখিত:** Microusity (OpenAPI-ভিত্তিক BFF testing), microRTS, CCTS (contract + state model), Gremlin, MicroRank, MicroRCA, CAR-PT।
- **P037:** Light-OAuth2, Locust, Prometheus, Jaeger, LogLead।

## 9. Dataset ও benchmark
- **P038:** TrainTicket (১৬টি study) de-facto large SUT। Sock Shop (৬টি) এখন deprecated। Standard small বা medium MSA নেই।
- **P037:** LO2 — ১,৭৪০টি run, প্রায় ৫৪০ GB।

## 10. মূল্যায়ন
- **P038:** বর্ণনামূলক গণনা।
  - Laboratory experiment ৫০টি।
  - TRL ৩–৪।
  - Black-box প্রধান।
- **P037:** F1 ও AUC-ROC।

## 11. প্রতিষ্ঠিত ফলাফল
- **P038:**
  - System testing ৪৭টি, integration ২১, unit ১৫, acceptance ৫।
  - Functional objective: conformance ২৩, regression ১৪, API ৮।
  - Non-functional: performance ২১, reliability ১৪, flexibility ২।
  - Specification-based strategy প্রধান।
  - বেশিরভাগ approach early-stage (TRL ৩–৪)।
  - **কোনো primary study সরাসরি microservice security testing করেনি** (লেখকদের দাবি)।
- **P037:**
  - সব service-এর log একত্রে ব্যর্থ (F1 প্রায় ০.৬৬৭)।
  - Per-service model সফল, কিন্তু তার জন্য error আগে থেকে জানা দরকার।
  - Trace কার্যত অব্যবহারযোগ্য।

## 12. বিরোধ
- P038-এর “security testing নেই” দাবি বনাম corpus-এর REST API security কাজ (P012, P014, P015)।
- ⚠️ বিরোধটি P038-এর title-only query-র পরিধি থেকে আসা — বাস্তব বিরোধ নয়।

## 13. লেখক-স্বীকৃত সীমাবদ্ধতা
- **P038:** Google Scholar-এর reproducibility-ঝুঁকি; grey literature বাদ।
- **P037:** trace নেই, hardware anomaly নেই, task-এর probability সমান।

## 14. বিশ্লেষণী সীমাবদ্ধতা ⚠️
- **P038:**
  - Title-only query — API testing (৮টি) সম্ভবত কম-গণনা।
  - ছোট সংখ্যাগত অসঙ্গতি (৫৬ + ২১ বনাম ৭৪)।
  - Spec-এর মান নিয়ে আলোচনা নেই।
- **P037:** “anomaly” আসলে documented 4xx।

## 15. অপর্যাপ্ত প্রমাণ
- Microservice API security testing।
- Spec defect-এর multi-service প্রভাব।
- Industrial validation (TRL ৫+)।

## 16. Gap
- **G13:** observability oracle ও security anomaly dataset (Class C, partially weakened)।
- **G2:** microservice behavioural breaking change (T5-এর সাথে ভাগ করা)।
- **নতুন (Class A, P038):** microservice security testing — লেখকদের স্পষ্ট future work।
  - ⚠️ REST security কাজ (P012, P014, P015) দিয়ে আংশিক পূরণ।
  - Multi-service authorization এখনো খোলা।
- **নতুন (Class A, P038):** standard small বা medium MSA benchmark।

## 17. Technical উন্নতি
- Proper tracing।
- Attack traffic।
- Fuzzer-generated real-fault data।
- Medium MSA benchmark।

## 18. নতুন approach [H]
- **Spec-aware log oracle:** P037 × P008 × P001।
- **R1-এর microservice সম্প্রসারণ:** TrainTicket-এ spec defect বনাম implementation fault attribution। 2607.12101-এর injector TrainTicket spec সরবরাহ করে।

## 19. দক্ষতা ও resource
- Docker Compose, Prometheus, OpenTelemetry।
- প্রচুর storage।
- TrainTicket ভারী (৪০+ service)।

## 20. ঝুঁকি
- Infrastructure-ভারী।
- Ground truth তৈরি কঠিন।

## 21. Baseline ও metric
- **Baseline:** LogLead model, EvoMaster/RESTler on TrainTicket।
- **Metric:** F1, AUC, detection latency, coverage।

## 22. নতুন গবেষকের সুযোগ
- মাঝারি।
- R1-এর পরবর্তী পর্যায় হিসেবে microservice সম্প্রসারণ।
- অথবা security testing gap — তবে আগে লক্ষ্যভিত্তিক search দরকার।

## 23. প্রমাণের মান
**মাঝারি।**
- একটি কঠোর ও সাম্প্রতিক SLR (P038) এবং একটি dataset paper (P037)।
- Primary technique paper নেই।
