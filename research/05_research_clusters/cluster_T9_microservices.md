# Cluster T9 — Microservice APIs, Testing & Observability

**Primary:** P037, P038* · **Secondary:** P011, P014, P020, P036
⚠️ **P038 substitute:** Ghani et al. 2019, নির্বাচিত Ponce et al. 2025 নয় (`document_integrity_report.md` §2)। এই cluster-এর প্রমাণ সবচেয়ে দুর্বল।
⚠️ = অনুমান। [H] = hypothesis।

## 1. ID ও নাম
T9 — Microservice-ভিত্তিক সিস্টেমে API testing ও observability (log, metric, trace)।

## 2. Problem ও motivation
- Microservice-এ API-র সংখ্যা ও পারস্পরিক নির্ভরতা বেশি।
- Testing ও anomaly detection-এর জন্য multi-modal data ও system-level পদ্ধতি দরকার (P037, P038*)।

## 3. Core RQ
- API-error-চালিত anomaly কি log ও metric থেকে শনাক্তযোগ্য (P037)?
- Microservice testing-এ কোন approach ও level প্রচলিত (P038*)?

## 4. Paper
| ID | ধরন |
|---|---|
| P037 LO2 (PROMISE 2025) | Dataset + preliminary analysis |
| P038* (Ghani, IJIE 2019) | ১৫-study review (substitute) |
| Secondary | P011 (industrial RPC microservice), P014 (log-ভিত্তিক BOLA), P020 (microservice API evolution), P036 (MCP server health) |

## 5. ঐতিহাসিক অবদান
- কোনো শক্তিশালী ঐতিহাসিক paper corpus-এ নেই।

## 6. সাম্প্রতিক উন্নয়ন
- **P037:** LO2 (২০২৫)।
- **Corpus-এর বাইরে (GV15):**
  - AnoMod — EvoMaster-চালিত multimodal dataset।
  - Lobrest — log-ভিত্তিক REST testing।

## 7. Methodology
- Dataset নির্মাণ (Locust-এর correct ও error task)।
- LogLead ML।
- PCA।

## 8. Tool
- Light-OAuth2, Locust, Prometheus, Jaeger, LogLead (P037)।

## 9. Dataset
- **P037:** LO2 — ১,৭৪০টি run, প্রায় ৫৪০ GB।
- **P038\*:** ১৫টি study।

## 10. মূল্যায়ন
- F1 ও AUC-ROC (P037)।
- বর্ণনামূলক শতাংশ (P038*)।

## 11. প্রতিষ্ঠিত ফলাফল
- **P037:**
  - সব service-এর log একত্রে ব্যবহার ব্যর্থ (F1 প্রায় ০.৬৬৭)।
  - Per-service model সফল, কিন্তু তার জন্য error আগে থেকে জানা দরকার।
  - Trace কার্যত অব্যবহারযোগ্য।
- **P038\*:**
  - Unit testing প্রায় ৭৫%।
  - মাত্র ১/১৫ study পূর্ববর্তী কাজের সাথে তুলনা করেছে (দুর্বল প্রমাণ)।

## 12. বিরোধ
- পর্যাপ্ত paper নেই।

## 13. লেখক-স্বীকৃত সীমাবদ্ধতা
- **P037:**
  - Trace নেই।
  - Hardware anomaly নেই।
  - Task-এর probability সমান।
  - অসম্পূর্ণ documentation।

## 14. বিশ্লেষণী সীমাবদ্ধতা ⚠️
- **P037-এর “anomaly” আসলে documented 4xx** — সিস্টেম প্রত্যাশিত আচরণই করছে।
- **P038 নির্বাচিত paper নয়।**
- System-level microservice API testing-এর শক্তিশালী primary paper corpus-এ নেই।

## 15. অপর্যাপ্ত প্রমাণ
- পুরো cluster-এই প্রমাণ অপর্যাপ্ত।
- Ponce et al. 2025 পাঠ না করা পর্যন্ত state-of-the-art অনিশ্চিত।

## 16. Gap
- **G13:** observability oracle ও security anomaly dataset (Class C, Partially weakened)।
- **G2:** microservice behavioural breaking change (T5-এর সাথে ভাগ করা)।

## 17. Technical উন্নতি
- Proper tracing।
- Attack traffic।
- Fuzzer-generated real-fault data।

## 18. নতুন approach [H]
- **Spec-aware log oracle:** fuzzing চলাকালীন OpenAPI-documented response বনাম log-এ প্রতিফলিত আচরণের অসঙ্গতি (P037 × P008 × P001)।

## 19. দক্ষতা ও resource
- Docker Compose, Prometheus, OpenTelemetry।
- প্রচুর storage (LO2 প্রায় ৫৪০ GB)।

## 20. ঝুঁকি
- Infrastructure-ভারী।
- Ground truth তৈরি কঠিন।
- Corpus-এর প্রমাণ দুর্বল।

## 21. Baseline ও metric
- **Baseline:** LogLead model।
- **Metric:** F1, AUC, detection latency।

## 22. নতুন গবেষকের সুযোগ
- কম। প্রথমে P038-এর সঠিক paper ও AnoMod পড়া দরকার।

## 23. প্রমাণের মান
**নিম্ন।**
- একটি dataset paper ও একটি substitute review।
- এই cluster-এর ভিত্তিতে কোনো শক্তিশালী সুপারিশ করা উচিত নয়।
