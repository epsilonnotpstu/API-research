# Spec mutation-এর fresh-mode noise floor (2026-11-14, Claude)

**Script:** `noise_floor_spec.py` → `noise_floor_spec.csv`। নতুন কোনো run চালানো হয়নি।

## নকশা
- **উৎস:** negative-data batch-গুলোতে প্রতিটি SUT × seed-এর জন্য একই execution input-এ 2–5টি সম্পূর্ণ baseline আছে।
- **যাচাই করা হয়েছে যে এগুলো সত্যিই replicate:**
  - SUT jar-এর sha, image, আর Schemathesis argv (run id বাদে) সব এক।
  - `run_pilot.sh`, `common.sh`, `mitm_fulllog.py` অপরিবর্তিত।
  - পার্থক্য শুধু `analyse_run.sh`, `run_batch.sh`, `market.env` (oracle) আর README-তে। এগুলো run-এর আচরণে প্রভাব ফেলে না।
- **সংকেত:** fresh attribution(জোড়া baseline @ base spec, mutated run @ mutated spec, manifest)।
- **Noise:** fresh attribution(জোড়া baseline, অন্য replicate @ base spec, একই manifest)।
  - এখানে manifest শুধু op-এর স্তর নির্ধারণ করে।
  - মাপা হয়েছে সব replicate-এর ওপর। "max" মানে সবচেয়ে প্রতিকূল replicate।
- **Checker:** বর্তমানটা (int format চালু), default oracle 400/422।
- **নিয়ম:** সংকেত noise ছাড়ায় যদি mutated op-এ NEW > noise max NEW (একই op-এ)। দ্বিতীয় নিয়ম: NEW **বা** INCREASED, noise max-এর চেয়ে বেশি।
- এটা finite-sample পর্যবেক্ষণ, কোনো statistical test নয়।

## ফল (61টি mutated run)
| Fault | SUT | NEW > noise | NEW বা INCREASED > noise |
|---|---|---|---|
| METHOD_SEM | সব 4টি | 12/12 | 12/12 |
| REQUEST_STRICT | scout, petstore, market | 9/9 | 9/9 |
| REQUEST_STRICT | cwa | 0/3 | 0/3 |
| RESPONSE_ORACLE | petstore, market | 6/6 | 6/6 |
| RESPONSE_ORACLE | scout | 2/3 | 2/3 |
| RESPONSE_ORACLE | cwa | 1/3 | 1/3 |
| REQUEST_LOOSE | cwa | 3/3 | 3/3 |
| REQUEST_LOOSE | petstore | 6/7 | 6/7 |
| REQUEST_LOOSE | scout | 5/6 | 5/6 |
| REQUEST_LOOSE | market | **1/9** | **7/9** |
| **মোট** | | **45/61** | **51/61** |

- **Noise-এর মাপ (mapped স্তরে NEW, সবচেয়ে বেশি):** scout 4, petstore 3, market 0, cwa 0।
- **অপরিবর্তিত op-এ noise (max):**
  - scout: NEW ≤9, I ≤51, D ≤53।
  - petstore: ≤3 / 12 / 11।
  - market: 0 / 10 / 11।
  - cwa: 0 / 4 / 3।

## ব্যাখ্যা
1. **Fresh fuzzing-এ spec mutation-এর সংকেত বেশিরভাগ ক্ষেত্রেই noise ছাড়ায়** (51/61), negative data দিলে।
   - এতে PILOT_SUMMARY-র সংশোধিত H1 সমর্থন পায়।
   - তবে ব্যতিক্রমগুলো নির্দিষ্ট:
     - cwa-র STRICT আর ORACLE: fresh-এ mutated op-এ প্রায় কোনো NEW-ই নেই।
     - market-এর LOOSE: সংকেত আসে শুধু occurrence বাড়া হিসেবে, যা §6-এর "occurrence-স্তরের metric লাগে" কথার সাথে মেলে।
2. **Mutated run-এর অপরিবর্তিত op-এর বড় পরিবর্তন প্রায় পুরোটাই noise।**
   - Unmut NEW noise max ছাড়িয়েছে মাত্র 11/61 run-এ, আর I+D ছাড়িয়েছে 9/61-এ।
   - ⚠️ [H] বাকি ব্যতিক্রমগুলো mutation-এর কারণে generator-এর পরোক্ষ পরিবর্তন হতে পারে, যেমন spec বদলালে অন্য op-এর জন্য তৈরি request বা state বদলে যায়।
   - এটা E5-এর code-mutation noise floor-এর ফলের সাথে মেলে (E5_RESULTS §3b)।
3. **Replay এখনো নিখুঁত** (0 unexplained)। Fresh-এর জন্য দরকার mutated-op স্তরে noise-এর তুলনা, আর occurrence-স্তরের metric।

## সীমা
- Replicate কম: cwa-তে প্রতি seed-এ 1টি, scout ও petstore-এর s2/s3-তে 2টি।
- Replicate-গুলো আলাদা সময়ের batch থেকে। SUT-এর ভেতরের state প্রতিবার নতুন container-এ শুরু হয়, তবে ⚠️ host-এর load আলাদা হতে পারে।
- NEW-এর হিসাব fingerprint স্তরে। একই op-এ ভিন্ন kind আলাদা গোনা হয়।

## সংযোজন (2026-11-15): প্রত্যাশিত-kind সংকেত (collateral exposure বাদ দিয়ে)
**কেন:** STRICT ablation (`STRICT_ABLATION.md`) দেখিয়েছে, mutated spec generator-কে SUT-এর **আগে থেকে থাকা** defect-এর পথে ঠেলে দিতে পারে। তখন mutated op-এ NEW আসে, কিন্তু kind spec mutation-এর প্রত্যাশিত kind নয়।

**নিয়ম:** fault-এর mechanism থেকে প্রত্যাশিত kind আগে থেকে ঠিক করা (`fuzzer_compare.EXPECTED_KINDS`; per-kind ফল দেখার আগে):

| Fault | প্রত্যাশিত kind |
|---|---|
| LOOSE | VALID_REJECTED |
| STRICT | INVALID_ACCEPTED |
| ORACLE | RESPONSE_SCHEMA, UNDOCUMENTED_STATUS |
| METHOD_SEM | UNDOCUMENTED_OPERATION, UNDOCUMENTED_STATUS, VALID_REJECTED |

একই filter সংকেত আর noise, দুই দিকেই। Run-সেট অপরিবর্তিত (61)। STRICT ablation run আর তাদের batch-এর baseline বাদ।

| Fault | SUT | NEW > noise (raw) | প্রত্যাশিত kind > noise |
|---|---|---|---|
| METHOD_SEM | cwa, market, scout | 9/9 | 9/9 |
| METHOD_SEM | petstore | 3/3 | **1/3** |
| REQUEST_STRICT | scout, petstore, market | 9/9 | 9/9 |
| REQUEST_STRICT | cwa | 0/3 | 0/3 |
| RESPONSE_ORACLE | সব | 9/12 | 9/12 |
| REQUEST_LOOSE | cwa | 3/3 | 3/3 |
| REQUEST_LOOSE | scout | 5/6 | **3/6** |
| REQUEST_LOOSE | petstore | 6/7 | **0/7** |
| REQUEST_LOOSE | market | 1/9 | **0/9** |
| **মোট** | | **45/61** | **34/61** |

- Checkable filter একা (`*_UNCHECKABLE` বাদ) দিলে: 44/61।
- **প্রায় সব পরিবর্তন REQUEST_LOOSE-এ।**
  - petstore আর scout-এর LOOSE-এ "সংকেত" ছিল মূলত RESPONSE_SCHEMA আর INVALID_ACCEPTED, অর্থাৎ generator-এর বদলানো traffic-এ অন্য constraint-এর লঙ্ঘন।
  - প্রত্যাশিত VALID_REJECTED এসেছে শুধু cwa-তে (3/3) আর scout p100-এ (3/3)।
- **petstore METHOD_SEM:** raw NEW-এর একটা বড় অংশ REQUEST_UNCHECKABLE বা SERVER_ERROR।
- **সংশোধিত উপসংহার:**
  - Fresh mode-এ STRICT, ORACLE আর METHOD_SEM-এর প্রত্যাশিত সংকেত বেশিরভাগ ক্ষেত্রে noise ছাড়ায়।
  - **REQUEST_LOOSE-এর ক্ষেত্রে ছাড়ায় না:** 6/25, মাত্র দুটো SUT-এ।
  - আগের "51/61" উপসংহার kind-নিরপেক্ষ ছিল। তাতে collateral exposure-ও গোনা হয়েছিল।
