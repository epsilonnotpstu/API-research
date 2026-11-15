# Baseline violation-এর চূড়ান্ত label — চার SUT, seed 1 (2026-11-14; 2026-11-15-এ হালনাগাদ)

**ফাইল:** `final_labels_baseline_s1.csv` (161টি সারি)। তৈরি হয় `build_final_labels.py` দিয়ে, চারটি adjudication sheet থেকে। B014/B077 = BOTH (supervisor)।

**2026-11-15 হালনাগাদ:**
- Supervisor নিশ্চিত করেছেন: P043, P021 আর P019 SPEC_PARTIAL থেকে **UNDECIDABLE**।
- কারণ: SPEC component-এর ভিত্তি শুধু একটা code guard, স্বাধীন intent-প্রমাণ নেই (codebook v0.6 §11.4, §12.4; T36 pilot)।
- পরিবর্তন করা হয়েছে `swagger-petstore_adjudication.csv`-এ, আগের note সংরক্ষিত।
- C005 (SPEC → UNDECIDABLE) এখনো Claude-এর provisional same-class সিদ্ধান্ত। সেটা শুধু `final_labels_baseline_s1_v06.csv`-এ আছে।
- **P014 IMPL → SPEC** (supervisor-delegated, Claude, 2026-11-15): upstream developer commit `9fb97b1` (2025-08-04) spec-এ `status` required করেছে, আর guard রেখে দিয়েছে। প্রমাণ T41 (`E4_triage/future_oracle/`)।

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
| swagger-petstore | 43 | 5 | 0 | 6 | 7 | 20 | 5 | 0 |
| market | 13 | 4 | 0 | 2 | 6 | 1 | 0 | 0 |
| cwa-verification | 6 | 1 | 1 | 0 | 0 | 4 | 0 | 0 |
| **মোট** | **161** | **41** | **1** | **40** | **30** | **26** | **23** | **0** |

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
- **Decidable defect** (SPEC + SPEC_PARTIAL + IMPL + BOTH) মোট 112টি (2026-11-14-এ ছিল 115):
  - SPEC-দিক: 42 (37.5%)।
  - IMPL: 40 (35.7%)।
  - BOTH: 30 (27%)।
- ⚠️ [H] চার SUT-এর baseline-এ প্রতি চারটি নির্ণয়যোগ্য অমিলের একটিতে spec আর code দুটোই বদলাতে হয়। তাই শুধু "spec নাকি code" — এই এক-কথার attribution অপর্যাপ্ত। এটা R1-এর একটি প্রধান empirical দাবির প্রার্থী।
- **TEST 26টি (16%)** আমাদের নিজেদের tooling-এর সীমা: checker-এর coverage, int64 format, fuzzer-এর probe। এটা পরিমাপের নির্ভরযোগ্যতার একটা আলাদা ফল।
- **UNDECIDABLE 23টি (14%)** প্রায় সবই policy-ambiguous: open schema বনাম কঠোর binding, container policy, আর guard-only intent।
- **Stateful fault** (petstore user, #952): একটি root cause পাঁচটি operation-এ ছড়িয়ে আছে। Per-operation attribution-এর একটা সীমা।

## সীমা
- একক হলো **fingerprint**, root cause নয়। scout-এর 99টি fingerprint মাত্র ~8–18টি root cause থেকে আসে, তাই root-cause স্তরে অনুপাত ভিন্ন হতে পারে।
- চারটিই Java SUT; একটি fuzzer; seed 1।
- দুই labeller-ই LLM, আর adjudication একজন মানুষের। এটা মানব inter-rater reliability নয়।
- 11টি "rule-applied" label supervisor item ধরে দেখেননি।
