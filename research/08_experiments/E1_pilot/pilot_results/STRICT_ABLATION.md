# Market REQUEST_STRICT keyword ablation (2026-11-15, Claude; supervisor-delegated)

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
- **Script:**
  - `strict_ablation.py` → `strict_ablation.csv`;
  - `strict_ablation_kinds.py` → `strict_ablation_kinds.csv`।
  - Checker বর্তমানটা (int format চালু)। `*_UNCHECKABLE` বাদ।
- **সংকেত দুই স্তরে:**
  - (i) mutated op-এ fresh checkable NEW > observed cross-seed reference;
  - (ii) সেই NEW-এর **kind** STRICT-এর প্রত্যাশিত `INVALID_ACCEPTED` কিনা। অন্য যেকোনো kind = collateral।
- **Run:** 18টি mutated run (6 batch × 3) আর তাদের baseline, সবগুলো exit 0।
  - EvoMaster no-required batch প্রথমবার Claude-এর process ভুলে আটকে গিয়েছিল (batch চলাকালীন T38 tool edit)। পরে পুরোটা আবার চালানো হয়েছে।

## ফল
| Fuzzer | Variant | Fresh NEW > ref | যার মধ্যে INVALID_ACCEPTED | শুধু collateral NEW | Replay NEW>0 | `_links`-সহ contacts PUT (500) |
|---|---|---|---|---|---|---|
| EvoMaster | full | 0/3 | 0/3 | 0/3 | 3/3 | 2100 (2100) |
| EvoMaster | required | 0/3 | 0/3 | 0/3 | 3/3 | 2298 (2298) |
| EvoMaster | maximum,maxLength,param_required | **2/3** | **2/3** | 0/3 | 3/3 | 1370 (1370) |
| Schemathesis | full | 3/3 | 3/3 | 0/3 | 2/3 | 36 (32) |
| Schemathesis | required | 3/3 | **0/3** | **3/3** (SERVER_ERROR + UNDOCUMENTED 500) | 0/3 | 4 (4) |
| Schemathesis | maximum,maxLength,param_required | 2/3 | 2/3 | 0/3 | 2/3 | 0 (0) |

- **EvoMaster-এর no-required variant:** সংকেতটা `PUT /customer/contacts`-এ phone/address `maxLength`-এর INVALID_ACCEPTED। এটা ঠিক সেই constraint, যা full STRICT-এ ঢাকা পড়ে ছিল।
- **Schemathesis-এর no-required variant:** সংকেত query `name` required-এর (`param_required`) INVALID_ACCEPTED, `GET /customer/{cart,contacts,orders}`-এ।

## ব্যাখ্যা
1. **T35-এর causal ব্যাখ্যা সমর্থিত।**
   - Required edit সরালে EvoMaster-এর প্রত্যাশিত সংকেত 0/3 থেকে 2/3-এ ফেরে।
   - শুধু required রাখলে 0/3 থাকে, আর contacts PUT-এর সবগুলোই 500।
   - ⚠️ No-required variant-এও EvoMaster ~450টি PUT-এ optional `_links` পাঠায়, সব 500। যে request-গুলো `_links` বাদ দেয়, সেগুলো 2xx পায়, আর তাতেই INVALID_ACCEPTED আসে।
2. **নতুন পদ্ধতিগত শিক্ষা: collateral exposure।**
   - Schemathesis-এর required-only run mapped-fingerprint মাপকাঠিতে 3/3 "সংকেত" দেখায়। কিন্তু সব NEW হলো 500, যা SUT-এর **আগে থেকে থাকা** HAL `_links` defect থেকে আসে।
   - এগুলো আসে কারণ mutated spec generator-কে সেই পথে ঠেলে দেয়। Spec mutation-এর প্রত্যাশিত প্রভাব (INVALID_ACCEPTED) এটা নয়।
   - তাই **fresh mode-এর "mapped fingerprint পরিবর্তন" kind-নিরপেক্ষভাবে গুনলে collateral defect-কে mutation-এর detection হিসেবে গোনা হয়।**
   - R1-এর মূল্যায়নে fault class-এর প্রত্যাশিত kind দিয়ে আলাদা করা দরকার। FUZZER_COMPARE-এর controlled ঘরে market STRICT-এর Schemathesis 3/3 ছিল full variant, সেখানে সব NEW-ই INVALID_ACCEPTED, তাই আগের ফল অপরিবর্তিত।
3. **Multi-keyword STRICT edit।**
   - একই spec mutation একই সঙ্গে প্রত্যাশিত সংকেত তৈরি করতে পারে (maxLength) আর generator-এর মাধ্যমে সেটা দমাতেও পারে (required → 500-পথ)।
   - তাই STRICT-এর ফলাফল একক constraint-এর detection হিসেবে পড়া যাবে না। R1 protocol-এ STRICT-কে keyword family অনুযায়ী আলাদা করে চালানো, অথবা অন্তত kind অনুযায়ী জানানো উচিত।

## সীমা
- একটি SUT, n=3 seed, একটি budget। কোনো statistical test নেই।
- Ablation run আর full run আলাদা batch আর দিনে চলেছে, প্রত্যেকটি নিজের baseline-সহ। ফলে cross-variant তুলনায় baseline-এর পার্থক্যও মিশে আছে।
- Cross-seed reference observed max, upper bound নয়।
- Collateral NEW-এর cause (HAL defect) T35-এর trace থেকে অনুমিত। ⚠️ এই run-গুলোর প্রতিটি 500 আলাদা করে trace করা হয়নি।
