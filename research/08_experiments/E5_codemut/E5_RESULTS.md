# E5 — প্রথম code-mutation pilot-এর ফল (2026-11-14, Claude)

**নকশা:** Codex T19, T20, T20b, T20c। Build, execution আর review: Claude।
**উৎস:**
- `e5_summary.csv` (`summarise_e5.py`)।
- `work/<pair>/pair-validation-s*.json`, `work/<pair>/analysis-s*-*`।
- `COORDINATOR_NOTES.md`।

## 1. কী চালানো হয়েছে
- **10টি mutant:** 5টি operator × 4টি SUT।
  - 1টি BUILD-INVALID: `market-response-field`। javac crash; Jackson `market-core`-এর classpath-এ নেই [H]।
- **প্রতিটি mutant-এর তুলনা একটা control-এর সাথে:** একই source copy, একই Maven image আর runtime base থেকে আবার build করা। Resolved Maven artifact দুই দিকে সমান।
- **Run:**
  - Harness_v2, baseline/NONE/0 (spec অপরিবর্তিত)।
  - `DATA_GEN=all`, 300 s, seed 1–3।
  - Fresh-mode attribution। Oracle: default, আর market-এ SUT oracle-ও।
- **জোড়া-যাচাই:** 14টি provenance check। দুই দিকের খরচ, runtime, dependency আর tool সমান।

## 2. Validation-এর হিসাব
- **বৈধ জোড়া-seed: 22।**
  - scout 9, petstore 6, market 4 (drop-null-এ শুধু s1, ledger-এর নিয়মে), cwa 3।
  - এর মধ্যে 1টি `PASS_WITH_EXCLUSION` (cwa-drop-null s2)।
- **বাদ পড়েছে:**
  - cwa-drop-validation s2: অসমতা mutated op-এ, তাই FAIL।
  - cwa-র দুটো জোড়ার s3: কখনো চলেনি, কারণ s2-এ launcher থেমে গিয়েছিল।

## 3. ফল (default oracle; মান = seed অনুযায়ী)
| Mutant (operator) | Expected | Mutated op-এ N/V/I/D | প্রত্যাশিত kind দেখা গেছে | অপরিবর্তিত op-এ N / I / D (noise) |
|---|---|---|---|---|
| scout-wrong-status (WRONG_STATUS) | UNDOCUMENTED_STATUS | N 1/1/1 | 3/3 | N 9/0/4, I 45–52, D 31–45 |
| scout-drop-null (DROP_NULL_CHECK) | SERVER_ERROR | N 1/1/1 | 3/3 | N 2/6/2, I 37–48, D 27–45 |
| scout-reject-valid (REJECT_VALID) | VALID_REJECTED | N 1/1/1 | 3/3 | N 2/3/3, I 38–48, D 31–47 |
| petstore-response-field (RESP_FIELD) | RESPONSE_SCHEMA | N 2/1/1 (+I/D) | 3/3 | N 3/4/1, I 8–15, D 9–15 |
| petstore-reject-valid (REJECT_VALID) | VALID_REJECTED | N 2/1/1 | **1/3** | N 2/0/5, I 9–10, D 7–14 |
| market-wrong-status (WRONG_STATUS) | UNDOCUMENTED_STATUS | N 1/1/1 | 3/3 | N 0, I 5–10, D 4–10 |
| market-drop-null (DROP_NULL_CHECK) | SERVER_ERROR | I 2 (s1) | 1/1 | N 0, I 6, D 9 |
| cwa-drop-null (DROP_NULL_CHECK) | SERVER_ERROR | N 1/1, V 1/1 | 2/2 | N 0, I 0–2, D 0–2 |
| cwa-drop-validation (DROP_VALIDATION) | INVALID_ACCEPTED / SERVER_ERROR | N 1, V 1 (s1) | 1/1 | N 0, I 3 |

**মোট:**
- **Mutated op-এ সংকেত (N বা I):** 22/22।
- **প্রত্যাশিত violation kind:** 20/22।

## 3b. Noise floor (control বনাম control, T22; 2026-11-14)
- **নকশা:** প্রতিটি বৈধ জোড়া-seed-এর জন্য একই control image দুবার চালানো হয়েছে (control, control_repeat)।
  - Seed, 300 s, `DATA_GEN=all` সব একই।
  - মোট 44টি run। সব noise জোড়া validate হয়েছে (21 PASS, 1 PASS_WITH_EXCLUSION)।
- **নিয়ম** `EXPECTED_CHANGED_FP_ABSENT_BOTH_NOISE_RUNS_V1` (PIPELINE.md):
  - সংকেত noise ছাড়ায় যদি mutated op-এর প্রত্যাশিত-kind NEW/INCREASED fingerprint দুই noise capture-এর কোনোটিতেই না থাকে।
  - এটা রক্ষণশীল পর্যবেক্ষণ, কোনো statistical test নয়।

| Mutant | Signal > noise (seed অনুযায়ী) | মন্তব্য |
|---|---|---|
| scout-wrong-status, scout-drop-null, scout-reject-valid | 3/3, 3/3, 3/3 | |
| petstore-response-field | 3/3 | |
| market-wrong-status | 3/3 | |
| cwa-drop-null, cwa-drop-validation | 2/2, 1/1 | |
| **market-drop-null** | **0/1** | সংকেত শুধু INCREASED (2)। Noise-এও ঠিক একই op-এ INCREASED 2, আর fingerprint control-এই আছে। ফলে noise থেকে আলাদা করা যায় না। |
| **petstore-reject-valid** | **0/3** | s1, s3-এ প্রত্যাশিত kind-ই নেই। s2-এর fingerprint noise-এও দেখা যায়। |

**মোট:**
- **Noise ছাড়ানো সংকেত:** 18/22 জোড়া-seed। Mutant হিসেবে 7/9 সব বৈধ seed-এ।
- **Noise-এ কাকতালীয় "প্রত্যাশিত kind":** mapped op-এ 3/22 noise run-এ (market-drop-null, petstore-reject-valid s3, petstore-response-field s3)। শুধু kind মিলিয়ে mutant ধরা নিরাপদ নয়।
- **অপরিবর্তিত op (default oracle; min–max):**

| SUT | Mutant জোড়া: NEW / I / D | Noise জোড়া: NEW / I / D |
|---|---|---|
| scout | 0–9 / 37–52 / 27–47 | 0–3 / 28–60 / 31–53 |
| petstore | 0–5 / 8–15 / 7–15 | 0–3 / 4–15 / 5–10 |
| market | 0 / 5–10 / 4–10 | 0 / 5–10 / 5–11 |
| cwa | 0 / 0–3 / 0–2 | 0 / 0–2 / 0–3 |

- Occurrence-স্তরের I/D পরিবর্তন mutant আর noise-এ প্রায় সমান, তাই এগুলো fuzzing-এর অনির্দেশ্যতা থেকে আসে, mutation থেকে নয়।
- NEW-এর সংখ্যা mutant জোড়ায় কিছুটা বেশি (scout সর্বোচ্চ 9 বনাম 3)।
  - ⚠️ [H] এটা mutation-এর পরোক্ষ প্রভাব হতে পারে, যেমন বদলে যাওয়া state-এর কারণে পরের request-এর আচরণ পাল্টানো।
  - আবার n ছোট হওয়ার কারণেও হতে পারে। এখান থেকে সিদ্ধান্ত টানা যায় না।

## 3c. বিকল্প site (T25; 2026-11-14)
Build আর run করেছে Claude। প্রতিটির জন্য 3টি seed + noise floor। সব জোড়া PASS। Checker নতুনটা (int format চালু)।

| Mutant | Mutated op-এ সংকেত | প্রত্যাশিত kind | Noise ছাড়ায় | মন্তব্য |
|---|---|---|---|---|
| market-response-field-v2 (`market-rest` Jackson mix-in, `price` WRITE_ONLY) | N 1/1/1 | **3/3** (RESPONSE_SCHEMA `/items/required` price, GET `/products`) | **3/3** | v1 (`market-core`) build-invalid ছিল; v2 compile হয় আর কাজ করে |
| petstore-reject-valid-v2 (GET `/user/login`, `username == null` guard) | N 1/1/1 (SERVER_ERROR 500) | **0/3** | (সংকেত আছে; noise-এ mapped স্তরের NEW 0) | `throw new BadRequestException` inflector-এ 400 হয় না, 500 হয় |
| petstore-reject-valid-v3 (একই guard, codebase-এর নিজস্ব `ResponseContext().status(BAD_REQUEST)`; T25b, run 2026-11-15) | N 1/1/1 | **3/3** (VALID_REJECTED 400, GET `/user/login`) | **3/3** (noise-এ fingerprint দুই repeat-এই অনুপস্থিত) | Operator-এর ত্রুটি ঠিক হয়েছে; এখন প্রত্যাশিত kind আসে |

- **petstore-reject-valid-v2-এর শিক্ষা:**
  - Fault ঢুকেছে, আর fuzzing সেটা ধরেছেও। কিন্তু operator-এর বাস্তবায়ন এই codebase-এর status ব্যবস্থার সাথে মেলেনি। Codebase 400 দেয় `ResponseContext().status(BAD_REQUEST)` দিয়ে।
  - তাই REJECT_VALID এখানে কার্যত crash (I-CRASH) হয়ে গেছে।
  - Ground truth L1 তবুও IMPL।
  - v3 site (একই condition, codebase-এর নিজের 400 পদ্ধতিতে) T25b হিসেবে Codex-এর কাছে।
- **E5-এর হিসাব এখন (v3 সহ, 2026-11-15):**
  - 12টি build-valid mutant, 31টি বৈধ জোড়া-seed।
  - Mutated op-এ সংকেত 31/31।
  - প্রত্যাশিত kind 26/31।
  - Noise ছাড়ায় **25/31** (§3b-এর নিয়মে)।
    - petstore-reject-valid-v2-এর 3টি নিয়মের সংজ্ঞায় False, কারণ kind প্রত্যাশিত নয়।
    - নতুন checker-এ petstore-reject-valid s2 এখন True: mutant-এ 1, noise-এ 0/0, আগে 24 ছিল।
  - v2 আর v3 একই ত্রুটি-site-এর দুই বাস্তবায়ন। Site-প্রতি একটা গুনলে (v3 রেখে v2 বাদ দিলে): 11 mutant, 28 জোড়া-seed, প্রত্যাশিত kind 26/28, noise ছাড়ায় 25/28।
- **Validator সংশোধন (T30, 2026-11-15):**
  - আগে `validate_pair` run-এর সময়ের tools/ আর harness snapshot-কে বর্তমান ফাইলের সঙ্গে হুবহু মেলাত। ফলে যেকোনো পরে-আসা tool পরিবর্তনে পুরোনো সব run "stale" FAIL হতো।
  - এখন run-time provenance কঠোর: জোড়ার দুই run-এর recorded snapshot হুবহু এক হতে হবে।
  - Metric গোনা হয় **বর্তমান checker** দিয়ে, raw capture থেকে। Summary-তে drift column আছে: `analysis_tools_drift` none 12 / changed 112 / unknown 6।
  - Legacy checker (`INT_FORMATS=False`) দিয়ে HEAD-এর 88/88 row হুবহু পুনরুৎপাদিত হয়েছে। তাই উপরের সব পরিবর্তন শুধু int-format নীতির ফল (24 row / 66 cell; `09_collab/logs/T30_scratch/metric_changes.csv`)।
  - `e5_summary.csv`: 130 row = 120 PASS + 4 PASS_WITH_EXCLUSION + 6 FAIL। এই 6টি পুরোনো, ঐতিহাসিক cwa-র অসম্পূর্ণ seed।

## 4. পর্যবেক্ষণ
1. **Detection নির্ভরযোগ্য।** প্রতিটি বৈধ জোড়া-seed-এ code fault mutated operation-এ নতুন violation বা বাড়তি occurrence তৈরি করে, আর প্রায় সবসময় প্রত্যাশিত kind-এ।
   - market-drop-null-এ সংকেত শুধু INCREASED, কারণ ওই fingerprint control-এই ছিল। এটা §6-এর "occurrence-স্তরের metric লাগে" কথার আরেকটা উদাহরণ।
2. **Fresh-এর noise বড়, বিশেষ করে scout-এ।** অপরিবর্তিত op-এ প্রতি seed-এ ≤9টি NEW, আর occurrence পরিবর্তন 27–52।
   - তাই মোট NEW গুনে mutant শনাক্ত করা যায় না। কাজ করে শুধু mutated op-এ প্রত্যাশিত kind-এর খোঁজ, যার জন্য আগে থেকে manifest জানা থাকতে হয়।
   - Noise floor পরে মাপা হয়েছে (§3b)। অপরিবর্তিত op-এর এই পরিবর্তনগুলো প্রায় পুরোটাই noise।
3. **R1-এর মূল প্রশ্নের উত্তর এখনো বাকি।** Fresh-mode attribution নতুন violation-কে label দেয় না (সব NEEDS_MANUAL)। আর `triage.py`-এর CLI P001-এর format-এর জন্য বানানো, তাই এখানে চলে না।
   - তাই "attribution কি code fault-কে IMPL বলে?" — এর উত্তর পেতে mutated op-এর NEW violation-গুলোকে A/B protocol-এ blind label করতে হবে।
   - **পরের ধাপ:** 22টি জোড়া-seed থেকে প্রায় 25টি item। Labeller-কে mutant/control পরিচয় জানানো হবে না।
4. **পার্শ্ব-ফল: আরও দুটো spec ত্রুটি**, যেগুলো generator-কে প্রভাবিত করে:
   - cwa `RegistrationTokenRequest.keyDob`-এ `"required": false` (অবৈধ JSON Schema)। এর ফলে Schemathesis negative mode-এ অনির্দেশ্য "Schema Error" দেয়।
   - market `UserDTOReq.name`-এর pattern `^[\pL '-]+$`। এটা Java regex, ECMA-262 নয়; Schemathesis compile করতে পারে না।
   - দুটোই E2-এর baseline labelling-এ ধরা পড়েনি, কারণ conformance violation হিসেবে আসে না। ⚠️ এটা আলাদা একটা ত্রুটি-শ্রেণি: spec-এর ত্রুটি যা testing tool-কে ভাঙে।

## 5. সীমা
- **নমুনা ছোট:** 9টি build-valid mutant, প্রতিটি একটি করে site।
- **Noise floor:** প্রতি জোড়া-seed-এ মাত্র একটি repeat। তাই "noise ছাড়ায়" একটা finite-sample পর্যবেক্ষণ, কোনো p-value নয়।
- **Detection-এর মানদণ্ড** ("mutated op-এ প্রত্যাশিত kind") manifest জানার ওপর নির্ভর করে। এটা oracle-এর ক্ষমতার upper bound, কোনো অন্ধ মূল্যায়ন নয়।
- **Directed witness** (নির্দিষ্ট request দিয়ে সরাসরি যাচাই, T19 README) করা হয়নি। এখানের "kill" fuzzing-এ ধরা পড়া।
- **Runtime base:** JDK 11-এর base image আবার pull করতে হয়েছে, তাই digest মূল pilot image-এর থেকে আলাদা। তবে control আর mutant দুটো একই base পেয়েছে।
