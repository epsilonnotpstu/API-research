# Baseline violation-এর চূড়ান্ত label — চার SUT, seed 1 (2026-11-14)

**ফাইল:** `final_labels_baseline_s1.csv` (161টি সারি)। তৈরি হয় `build_final_labels.py` দিয়ে, চারটি adjudication sheet থেকে। B014/B077 = BOTH (supervisor)।

**পদ্ধতি:**
- Labeller A (Claude) ও B (Codex, blind) source code, log আর exchange দেখে label দিয়েছে।
- Supervisor মতভেদের adjudication করেছেন।
- নিয়মগুলো codebook v0.4 §10-এ।

**চূড়ান্ত label-এর উৎস:**

| উৎস | n | অর্থ |
|---|---|---|
| agreed | 93 | A = B |
| supervisor | 57 | Supervisor-এর সিদ্ধান্ত |
| rule-applied | 11 | Supervisor-অনুমোদিত §10.6 নিয়ম Claude প্রয়োগ করেছে; item ধরে আলাদাভাবে দেখা হয়নি |

| SUT | n | SPEC | SPEC_PARTIAL | IMPL | BOTH | TEST | UNDECIDABLE | PENDING |
|---|---|---|---|---|---|---|---|---|
| scout-api | 99 | 31 | 0 | 32 | 17 | 1 | 18 | 0 |
| swagger-petstore | 43 | 4 | 3 | 7 | 7 | 20 | 2 | 0 |
| market | 13 | 4 | 0 | 2 | 6 | 1 | 0 | 0 |
| cwa-verification | 6 | 1 | 1 | 0 | 0 | 4 | 0 | 0 |
| **মোট** | **161** | **40** | **4** | **41** | **30** | **26** | **20** | **0** |

## Labeller A–B agreement (adjudication-এর আগে, L1)
| SUT | n | Agreement | κ |
|---|---|---|---|
| scout-api | 99 | 81.8% | 0.70 |
| swagger-petstore | 43 | 83.7% | 0.75 |
| market | 13 | 53.8% (BOTH-রীতি মেলালে 100%) | 0.43 |
| cwa-verification | 6 | 100% | 1.00 |
| **মোট** | **161** | **80.7%** (BOTH-রীতি মেলালে 84.5%) | **0.73** (0.77) |

- "BOTH-রীতি মেলালে" মানে codebook §10.1 অনুযায়ী A-র L1 = BOTH-কে প্রাথমিক IMPL ধরা।
- দুটোই LLM labeller; মানব inter-rater reliability নয়।

## পড়ার নিয়ম ও প্রাথমিক পর্যবেক্ষণ
- **Decidable defect** (SPEC + SPEC_PARTIAL + IMPL + BOTH) মোট 115টি:
  - SPEC-দিক: 44 (38%)।
  - IMPL: 41 (36%)।
  - BOTH: 30 (26%)।
- ⚠️ [H] চার SUT-এর baseline-এ প্রতি চারটি নির্ণয়যোগ্য অমিলের একটিতে spec আর code দুটোই বদলাতে হয়। তাই শুধু "spec নাকি code" — এই এক-কথার attribution অপর্যাপ্ত। এটা R1-এর একটি প্রধান empirical দাবির প্রার্থী।
- **TEST 26টি (16%)** আমাদের নিজেদের tooling-এর সীমা: checker-এর coverage, int64 format, fuzzer-এর probe। এটা পরিমাপের নির্ভরযোগ্যতার একটা আলাদা ফল।
- **UNDECIDABLE 20টি (12%)** প্রায় সবই policy-ambiguous: open schema বনাম কঠোর binding, container policy।
- **Stateful fault** (petstore user, #952): একটি root cause পাঁচটি operation-এ ছড়িয়ে আছে। Per-operation attribution-এর একটা সীমা।

## সীমা
- একক হলো **fingerprint**, root cause নয়। scout-এর 99টি fingerprint মাত্র ~8–18টি root cause থেকে আসে, তাই root-cause স্তরে অনুপাত ভিন্ন হতে পারে।
- চারটিই Java SUT; একটি fuzzer; seed 1।
- দুই labeller-ই LLM, আর adjudication একজন মানুষের। এটা মানব inter-rater reliability নয়।
- 11টি "rule-applied" label supervisor item ধরে দেখেননি।
