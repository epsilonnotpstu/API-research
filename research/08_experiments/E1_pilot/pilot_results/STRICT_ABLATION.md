# Market REQUEST_STRICT keyword ablation (2026-11-15, Claude; supervisor-delegated; T39 review-এর পর সংশোধিত)

**প্রশ্ন (T35-এর পরে):**
- Market STRICT-এ EvoMaster-এর সংকেত 0/3। এটা কি required `_links` edit-এর কারণে? T35-এর ব্যাখ্যা: required `_links` → HAL parse → 500।
- STRICT-এর একাধিক keyword-এর edit একক constraint-এর প্রভাব হিসেবে পড়া যায় কি?

## পদ্ধতি
- **Knob:** T37-এর `STRICT_KEYWORDS`।
  - Operation selection একই থাকে, আর selected-but-unedited op আলাদা নথিভুক্ত হয়।
  - Default-এ আচরণ byte-identical।
- **Variant:**
  - `full`: পুরোনো STRICT run;
  - `required`: শুধু object-level required list;
  - `maximum,maxLength,param_required`: required ছাড়া বাকি সব।
  - শেষ দুটো মিলে full হয়।
- **Fuzzer:** EvoMaster v6.2.0 (spec input, schemaOracles true) আর Schemathesis (`DATA_GEN=all`)। Seed 1–3, severity 30, budget 300 s।
  - প্রতিটি ablation batch নিজের baseline চালায়। Baseline-এর child process-এ knob ফাঁকা থাকে।
- **Schemathesis-এর runtime checks (T39 F1):**
  - মূল full run চলেছিল `SCHEMA_CHECKS=response_headers_conformance`-এ।
  - প্রথম ablation run ভুলবশত default `all`-এ চলেছিল। এটা generation-এ প্রভাব ফেলে: প্রথম failed check-এ Schemathesis ওই operation ছেড়ে দেয়, ফলে exchange সংখ্যা প্রায় 100 বনাম প্রায় 1200।
  - তাই মিলানো settings-এ দুই variant **আবার চালানো হয়েছে**। নিচে primary হলো মিলানো run। `[checks=all]` run শুধু secondary।
- **Script:**
  - `strict_ablation.py` → `strict_ablation.csv`;
  - `strict_ablation_kinds.py` → `strict_ablation_kinds.csv`।
  - Checker বর্তমানটা (int format চালু)। `*_UNCHECKABLE` বাদ।
- **সংকেত দুই স্তরে:**
  - (i) mutated op-এ fresh checkable NEW > observed cross-seed reference;
  - (ii) সেই NEW-এর **kind** STRICT-এর canonical `INVALID_ACCEPTED` কিনা।
- **Exit:**
  - সব run-এ harness exit 0।
  - Fuzzer exit আলাদা ব্যাপার: Schemathesis-এর exit 1 মানে test-failure, যা harness অনুমোদন করে। বিস্তারিত `strict_ablation.csv`-এর `fuzzer_exit` column-এ। Full s2/s3-ও 1।
  - EvoMaster no-required batch প্রথমবার Claude-এর process ভুলে আটকে গিয়েছিল (batch চলাকালীন T38 tool edit), পরে পুরোটা আবার চালানো হয়েছে।

## ফল (primary: মিলানো settings)
| Fuzzer | Variant | Fresh NEW > ref | যার মধ্যে INVALID_ACCEPTED | Filter-এর বাইরের NEW-ই শুধু | Replay NEW>0 | `_links`-সহ contacts PUT (500) | Mean exchanges |
|---|---|---|---|---|---|---|---|
| EvoMaster | full | 0/3 | 0/3 | 0/3 | 3/3 | 2100 (2100) | ~4.17k |
| EvoMaster | required | 0/3 | 0/3 | 0/3 | 3/3 | 2298 (2298) | ~4.15k |
| EvoMaster | maximum,maxLength,param_required | **2/3** | **2/3** | 0/3 | 3/3 | 1370 (1370) | ~4.05k |
| Schemathesis | full | 3/3 | 3/3 | 0/3 | 2/3 | 36 (32) | ~1.17k |
| Schemathesis | required | **0/3** | 0/3 | 0/3 | 0/3 | 177 (172) | ~1.19k |
| Schemathesis | maximum,maxLength,param_required | **3/3** | 3/3 | 0/3 | 2/3 | 71 (69) | ~1.17k |

**Secondary (Schemathesis `[checks=all]`, settings মেলেনি; শুধু বর্ণনামূলক):**
- required: NEW > ref 3/3, কিন্তু INVALID_ACCEPTED 0/3। সব NEW হলো SERVER_ERROR আর UNDOCUMENTED 500 (HAL path)।
- no-required: 2/3 INVALID_ACCEPTED।

**Kind-এর বিস্তারিত:**
- EvoMaster no-required-এর NEW হলো `PUT /customer/contacts`-এ phone/address `maxLength` INVALID_ACCEPTED।
- Schemathesis-এর NEW হলো query `name` required-এর INVALID_ACCEPTED, contacts body `maxLength`-সহ।
- Schemathesis full-এর NEW-এর মধ্যে তিন seed-এই INVALID_ACCEPTED আছে। s2-তে একটা UNDOCUMENTED_STATUS-ও আছে।

## ব্যাখ্যা
1. **T35-এর causal ব্যাখ্যা EvoMaster-এর জন্য সমর্থিত।**
   - Required edit সরালে EvoMaster-এর INVALID_ACCEPTED সংকেত 0/3 থেকে 2/3-এ ফেরে। শুধু required রাখলে 0/3, আর contacts PUT-এর সবগুলো 500।
   - No-required variant-এও EvoMaster ~450টি PUT-এ optional `_links` পাঠায়, সব 500।
   - **যে accepted subset-টা NEW INVALID_ACCEPTED তৈরি করে, তাতে `_links` অনুপস্থিত** (T39 যাচাই)।
     - ⚠️ উল্টোটা সর্বজনীন নয়: valid JSON-এ `_links` অনুপস্থিত থাকলে 200 পাওয়া যায় 40/77/50 বার, আর 406 পাওয়া যায় 251/321/280 বার।
2. **Schemathesis-এর জন্য required edit নিরপেক্ষ।**
   - সংকেত আসে বাকি keyword থেকে: no-required 3/3 = full 3/3।
   - Required-only মিলানো settings-এ 0/3। `_links`-সহ PUT 177টি, প্রায় সবই 500, কিন্তু baseline-এ এই 500-পথ আগে থেকেই আছে, তাই NEW হয় না।
   - সুতরাং generator-এর পার্থক্য (EvoMaster প্রতিটি contacts PUT-এ `_links` পাঠায়, Schemathesis কম) আর SUT-এর 500-পথ মিলে দুই fuzzer-এর ফারাক তৈরি করে।
3. **Collateral exposure নির্ভর করে baseline coverage-এর ওপর।**
   - Settings-অমিলের `[checks=all]` run-এ baseline ছোট ছিল, তাই তাতে HAL 500 প্রায় অনুপস্থিত। Mutated required run সেই পথে traffic ঠেলে দেওয়ায় mutated op-এ 3/3 নতুন 500 দেখা দিয়েছে। এগুলো SUT-এর আগে থেকে থাকা defect, T35-এর trace অনুযায়ী।
   - মিলানো settings-এ baseline বড়, তাই ওই 500 আগেই আছে, আর collateral NEW নেই।
   - **শিক্ষা:** kind-নিরপেক্ষ mapped-fingerprint সংকেত আগে থেকে থাকা defect-কে mutation-এর detection হিসেবে গুনতে পারে, বিশেষত যখন baseline সেই পথ ছোঁয় না।
   - তাই R1-এ canonical expected-kind filter (FUZZER_COMPARE ফল ৩) একটা যুক্তিসঙ্গত সুরক্ষা। তবে এটা causal adjudication নয় (T39 F3)।
4. **Multi-keyword STRICT edit।**
   - একই spec mutation একই সঙ্গে প্রত্যাশিত সংকেত তৈরি করতে পারে (maxLength) আর generator-এর মাধ্যমে সেটা দমাতেও পারে (EvoMaster-এ required → 500-পথ)।
   - এই দমন fuzzer-নির্ভর। তাই STRICT-কে keyword family অনুযায়ী চালানো, অথবা অন্তত kind অনুযায়ী জানানো উচিত।

## সীমা
- একটি SUT, n=3 seed, একটি budget। কোনো statistical test নেই।
- Ablation run আর full run আলাদা batch আর দিনে চলেছে, প্রত্যেকটি নিজের baseline-সহ।
- Cross-seed reference observed max, upper bound নয়।
- Collateral NEW-এর cause (HAL defect) T35-এর trace আর response message থেকে। ⚠️ প্রতিটি 500 আলাদা করে trace করা হয়নি।
