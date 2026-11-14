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

## 4. পর্যবেক্ষণ
1. **Detection নির্ভরযোগ্য।** প্রতিটি বৈধ জোড়া-seed-এ code fault mutated operation-এ নতুন violation বা বাড়তি occurrence তৈরি করে, আর প্রায় সবসময় প্রত্যাশিত kind-এ।
   - market-drop-null-এ সংকেত শুধু INCREASED, কারণ ওই fingerprint control-এই ছিল। এটা §6-এর "occurrence-স্তরের metric লাগে" কথার আরেকটা উদাহরণ।
2. **Fresh-এর noise বড়, বিশেষ করে scout-এ।** অপরিবর্তিত op-এ প্রতি seed-এ ≤9টি NEW, আর occurrence পরিবর্তন 27–52।
   - তাই মোট NEW গুনে mutant শনাক্ত করা যায় না। কাজ করে শুধু mutated op-এ প্রত্যাশিত kind-এর খোঁজ, যার জন্য আগে থেকে manifest জানা থাকতে হয়।
   - ⚠️ Noise floor (একই seed-এ control বনাম control) এখনো মাপা হয়নি।
3. **R1-এর মূল প্রশ্নের উত্তর এখনো বাকি।** Fresh-mode attribution নতুন violation-কে label দেয় না (সব NEEDS_MANUAL)। আর `triage.py`-এর CLI P001-এর format-এর জন্য বানানো, তাই এখানে চলে না।
   - তাই "attribution কি code fault-কে IMPL বলে?" — এর উত্তর পেতে mutated op-এর NEW violation-গুলোকে A/B protocol-এ blind label করতে হবে।
   - **পরের ধাপ:** 22টি জোড়া-seed থেকে প্রায় 25টি item। Labeller-কে mutant/control পরিচয় জানানো হবে না।
4. **পার্শ্ব-ফল: আরও দুটো spec ত্রুটি**, যেগুলো generator-কে প্রভাবিত করে:
   - cwa `RegistrationTokenRequest.keyDob`-এ `"required": false` (অবৈধ JSON Schema)। এর ফলে Schemathesis negative mode-এ অনির্দেশ্য "Schema Error" দেয়।
   - market `UserDTOReq.name`-এর pattern `^[\pL '-]+$`। এটা Java regex, ECMA-262 নয়; Schemathesis compile করতে পারে না।
   - দুটোই E2-এর baseline labelling-এ ধরা পড়েনি, কারণ conformance violation হিসেবে আসে না। ⚠️ এটা আলাদা একটা ত্রুটি-শ্রেণি: spec-এর ত্রুটি যা testing tool-কে ভাঙে।

## 5. সীমা
- **নমুনা ছোট:** 9টি build-valid mutant, প্রতিটি একটি করে site।
- **Detection-এর মানদণ্ড** ("mutated op-এ প্রত্যাশিত kind") manifest জানার ওপর নির্ভর করে। এটা oracle-এর ক্ষমতার upper bound, কোনো অন্ধ মূল্যায়ন নয়।
- **Directed witness** (নির্দিষ্ট request দিয়ে সরাসরি যাচাই, T19 README) করা হয়নি। এখানের "kill" fuzzing-এ ধরা পড়া।
- **Runtime base:** JDK 11-এর base image আবার pull করতে হয়েছে, তাই digest মূল pilot image-এর থেকে আলাদা। তবে control আর mutant দুটো একই base পেয়েছে।
