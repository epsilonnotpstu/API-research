# Batch-2 baseline (scout-api, s1): labeller A বনাম B — agreement ও adjudication (2026-11-14)

- **A** = Claude, source-ভিত্তিক: `../E1_pilot/pilot_results/batch2_baseline_s1_labels_code.csv`।
- **B** = Codex T15, blind: `batch2_baseline_s1_labels_codex.csv`, root causes `batch2_root_causes_codex.csv`, report `../../09_collab/reports/T15_report.md`।
- **Adjudication sheet:** `batch2_adjudication.csv`। 99টি সারি; দুজনের label, evidence ও rationale পাশাপাশি। খালি column `supervisor_L1`, `supervisor_L2`, `supervisor_note`।
- **Protocol:** দুটি LLM labeller + মানব (supervisor) adjudication। এটি মানব inter-rater reliability নয়।

## Agreement
| মাপ | মান |
|---|---|
| L1 agreement | 81/99 = 81.8%, Cohen's κ = 0.697 |
| L2, যেখানে L1 মেলে | 80/81 (একমাত্র পার্থক্য: probe-এর L2 — A `T-PROBE`, B নতুন code প্রস্তাব করেছে `T-PROBE-CONTAMINATION`) |
| IMPL | A 49, B 49 — সব একই item |
| BOTH প্রার্থী | A 17, B 21, দুজনেই 13 |

## মতভেদ
1. **18টি item — একটিই প্রশ্ন।** অঘোষিত property-সহ JSON body-তে server 400 ("Unable to process JSON") দেয়, অথচ schema খোলা (`additionalProperties` উল্লেখ নেই)।
   - A: SPEC / S-REQ-LOOSE, confidence 2 — spec-এর শিথিলতা।
   - B: UNDECIDABLE, confidence 1 — খোলা schema আর কঠোর binding দুটোই default। কোনো পক্ষেই ইচ্ছার (intent) স্পষ্ট প্রমাণ নেই।
   - ⚠️ A-র নিজস্ব পুনর্মূল্যায়ন: A-র প্রমাণ ছিল কেবল E-OBS। Project code-এ কঠোরতার স্পষ্ট সিদ্ধান্ত A খুঁজে পায়নি। Codebook-এর নিয়মে B-র অবস্থান দুর্বল নয়।
2. **BOTH প্রার্থীতে 12টি পার্থক্য।**
   - কেবল A: `POST /v1|v2/activities` 500 (4টি)।
   - কেবল B: rating POST, tag/category/user PUT 500 (8টি)। B-র root cause RC08/RC09: required field-এর validation নেই; client-এর দেওয়া id দিয়ে update।

## B যা আলাদাভাবে ধরেছে (A-র ঘাটতি)
- **Root cause-এর সংখ্যা:** B 18টি, A ~8টি।
- **RC12:** `GET /v1|v2/activities`-এ খালি `name` token-এ `charAt(0)` ব্যর্থ হয়। A এই 500-গুলোকে `my_favourites`-এর সাথে এক কারণে ফেলেছিল — **ভুল**। Fingerprint এক হলেও কারণ দুটি।
- **RC09:** client-এর দেওয়া generated id অস্তিত্বহীন row-এর update হিসেবে persist পর্যন্ত পৌঁছায়।
- ⚠️ শিক্ষা: fingerprint-level label একই হলেও root-cause স্তরে labeller-দের পার্থক্য বড়। R1-এর মূল্যায়নে দুই স্তরই রিপোর্ট করা দরকার।

## Blinding
- Board-এর একটি পুরোনো log লাইনে rule-prelabel-এর মোট সংখ্যা ছিল (IMPL 49, SPEC 26, UNDECIDABLE 24)। B সেটা পড়েছে এবং নিজেই প্রকাশ করেছে (T15 report §1)।
- A-র কোনো item-level label B দেখেনি।
- Task-এর নিষিদ্ধ-substring নিয়ম `labels_code` B-র নিজের অনুমোদিত output (`labels_codex`)-এর নামের সাথেও মিলে যায়। এটা task লেখার ত্রুটি (A-র), leak নয়।

## Supervisor adjudication
- **2026-11-14 — 18টি open-schema item: UNDECIDABLE** (B-র অবস্থান গৃহীত)। এগুলো "policy-ambiguous" উদাহরণ হিসেবে রিপোর্ট হবে।
  - এর ফলে L1 বণ্টন: IMPL 49, SPEC 31, UNDECIDABLE 18, TEST 1।
- **BOTH-এর 12টি পার্থক্য:** supervisor `batch2_adjudication.csv`-এর `supervisor_L1/L2/note` column পূরণ করবেন। Item: B015, B016, B079, B080 (কেবল A); B020, B044, B045, B054, B055, B084, B087, B088 (কেবল B)।
- বাকি 69টি item, যেখানে দুজন একমত: supervisor-এর নমুনা-যাচাই বাকি।
