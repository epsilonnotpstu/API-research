# REQUEST_LOOSE: কেন ধরা পড়ে না, আর কী করলে পড়ে (2026-11-14, Claude)

## 1. সমস্যা
আগের সব batch-এ (scout, petstore, market; seed 1–3; severity 30%) REQUEST_LOOSE-এর replay NEW আর VANISHED ছিল **সবসময় 0**।

## 2. নির্ণয় — তিনটি স্তরে বাধা
1. **Traffic শুধু positive।** Schemathesis default-এ বৈধ data পাঠায়। ফলে শিথিল করা constraint baseline traffic কখনো ভাঙেনি।
   - প্রতিকার: harness_v2-তে `DATA_GEN=all` (`--data-generation-method all`)।
   - শুধু এটুকু দিয়ে replay তখনো 0 ছিল। Batch: petstore `20261114T085904Z_batch_140345`, market `20261114T090354Z_batch_155277`, scout `20261114T090948Z_batch_172361`।
2. **শিথিল করার মতো constraint নেই।**
   - Spec-এ request constraint-এর সংখ্যা:

     | SUT | Operation | Constraint |
     |---|---|---|
     | scout | 49 | 18 |
     | petstore | 19 | 6 |
     | market | 13 | 51 |
     | cwa | 5 | 10 |

   - এলোমেলো 30% বাছাইয়ে এগুলো প্রায় বাদ পড়ে।
   - বাছাই হওয়া edit-এর প্রায় সবই কাঠামোগত (`$ref` inline করা) অথবা `format` সরানো। `conformance.py` `format` (int64) enforce করে না; দুই labeller এটাকেই `T-ORACLE-FORMAT` হিসেবে ধরেছিল।
   - চার SUT মিলিয়ে সত্যিকারের শিথিলকরণ মাত্র 4টি।
   - প্রতিকার: `tools/eligible_ops.py --fault REQUEST_LOOSE`। Pool-এ থাকে শুধু সেই operation, যেখানে checker-এর মূল্যায়িত অন্তত একটি constraint সরানো হয়। Pool: scout 9, petstore 4, market 4, cwa 5। সাথে `run_batch.sh LOOSE_POOL=spec`, আর pool-এর সব operation (`SEVERITY=100`)।
3. **Oracle প্রচলিত rejection status ধরে নেয়।** VALID_REJECTED জ্বলে কেবল 400 বা 422-এ (`conformance.py:438`)।
   - Market-এর শিথিল operation baseline-এ প্রত্যাখ্যান করেছে শুধু **406 বা 500** দিয়ে, কখনো 400 নয়।
   - ফলে market-এ শিথিলকরণ checker-এর চোখে অদৃশ্য থাকে। 406 যে ইচ্ছাকৃত, তা আগেই প্রমাণিত (`RestExceptionHandler.java:63-64,73-74`)।

## 3. Pool-সহ ফল
Settings: `LOOSE_POOL=spec SEVERITY=100 DATA_GEN=all`, seeds 1–3। প্রতিটি SUT-এর সর্বশেষ batch: petstore `20261114T092517Z_batch_184034`, market `…093050Z_batch_195691`, cwa `…093712Z_batch_219304`, scout `…094102Z_batch_237105`।

| SUT | Replay NEW (s1/s2/s3) | Replay VANISHED | Fresh NEW / VANISHED | Fresh unexplained (মোট) |
|---|---|---|---|---|
| scout-api | 1 / 1 / 1 (VALID_REJECTED) | 1 / 1 / 1 (INVALID_ACCEPTED, MASKED) | 5/2, 5/2, 5/2 | 6 |
| swagger-petstore | 0 / 0 / 0 | 0 / 0 / 1 | 5/3, 4/6, 1/1 | 8 |
| market | 0 / 0 / 0 | 0 / 0 / 0 | 0/0 সব seed | 0 |
| cwa-verification | 2 / 2 / 2 (VALID_REJECTED) | 0 | 3/1, 5/1, 5/1 | 0 |

## 4. সিদ্ধান্ত ও R1-এর জন্য তাৎপর্য
- REQUEST_LOOSE ধরা পড়ে তিনটি শর্ত একসাথে পূরণ হলে:
  - negative traffic,
  - checker-এর মূল্যায়িত constraint আছে এমন operation,
  - SUT প্রত্যাখ্যানে প্রচলিত status দেয়।
- এই শর্তে replay-এর সংকেত প্রতি run-এ মাত্র 1–2টি। এটা REQUEST_STRICT-এর (প্রতি run-এ 20–61টি) তুলনায় অনেক দুর্বল।
- ⚠️ [H] **"শিথিল spec"-এর ত্রুটি conformance testing-এ মৌলিকভাবে কম দৃশ্যমান।** এটা কেবল তখনই ধরা পড়ে যখন implementation নিজে কঠোর এবং প্রচলিত status দেয়। এর মানে S-REQ-LOOSE-শ্রেণির বাস্তব ত্রুটি (scout baseline-এ 20টি পাওয়া গেছে) সম্ভবত সাধারণভাবে কম রিপোর্ট হয়।
- Negative data-য় fresh unexplained বেড়েছে (petstore 8)। Fresh mode-এর nondeterminism বেশি, তাই এখানে replay-ই নির্ভরযোগ্য মাপ।

## 5. পরের পদক্ষেপের প্রস্তাব
1. **Checker-এ SUT-ভিত্তিক rejection status।** যেমন market-এর জন্য `--reject-statuses 400,406,422`। প্রমাণ থাকলে (code-এ explicit validation handler) SUT config থেকে নেওয়া যায়। ⚠️ এতে oracle-এর অর্থ বদলায়, তাই আগে supervisor-এর সিদ্ধান্ত দরকার।
2. **`format` enforcement।** checker-এ int32/int64 সীমা যাচাই যোগ করলে `format` edit-গুলো অর্থবহ হবে, আর `T-ORACLE-FORMAT` শ্রেণির TEST label কমবে।
3. **সব fault class-এ একই protocol।** REQUEST_STRICT-এর জন্যও pool আর negative data নিয়ে মূল তুলনা পুনরায় করা দরকার, নইলে fault class-গুলোর তুলনা ন্যায্য হবে না।

## 6. হালনাগাদ (2026-11-14): SUT oracle আর occurrence-স্তরের metric
**SUT oracle (market 400/406/422, codebook §10.8):** batch `runs/market/batches/20261114T102244Z_batch_312698`। একই run-গুলোর default-oracle analysis আছে `analysis-both-default`-এ।

**নতুন নির্ণয় — fingerprint-স্তরের metric সংকেত লুকিয়ে ফেলে।**
- শিথিল spec-এ যে request বৈধ হয়ে প্রত্যাখ্যাত হয়, সেটা প্রায়ই baseline-এর **একই** VALID_REJECTED fingerprint-এ পড়ে, কারণ fingerprint = kind + method + template + status।
- ফলে fingerprint "PERSISTENT" থাকে, কেবল occurrence বাড়ে। NEW/VANISHED গুনলে এই প্রভাব চোখে পড়ে না।
- Market-এ এর প্রমাণ: শিথিল operation-এ মূল spec-এ অবৈধ কিন্তু শিথিল spec-এ বৈধ, আর 406 পাওয়া request — pay-তে 1টি, contacts-এ 3টি। অথচ NEW = 0।

**INCREASED metric:** mutated operation-এ PERSISTENT fingerprint-এর occurrence baseline-এর চেয়ে বেশি হলে INCREASED। হিসাব হয়েছে `replay.attributed.csv`-এর `baseline_occurrences`/`mutated_occurrences` থেকে।

| SUT | Replay NEW (s1/s2/s3) | Replay INCREASED (s1/s2/s3) | উদাহরণ (baseline → mutated occurrence) | অপরিবর্তিত op-এ পরিবর্তন |
|---|---|---|---|---|
| scout-api | 1/1/1 | 0/0/0 | — | 0 |
| swagger-petstore | 0/0/0 | **1/1/1** | `findByStatus` VALID_REJECTED 52→88, 47→95, 48→96 (enum সরানো) | 0 |
| cwa-verification | 2/2/2 | **2/3/2** | `/tan` 38→46; `/testresult` 38→46 | 0 |
| market (SUT oracle) | 0/0/0 | **2/1/2** | `/customer/contacts` 47→50; `/register` 28→31 | 0 |
| market (default oracle) | 0/0/0 | 0/0/0 | — | 0 |

**সিদ্ধান্ত:**
- NEW + INCREASED মিলিয়ে REQUEST_LOOSE **চার SUT-এর প্রতিটি seed-এ** ধরা পড়ে।
- সব পরিবর্তন mutated operation-এই; অপরিবর্তিত operation-এ কোনো পরিবর্তন নেই (specificity 100%)।
- আগের "replay-তে 0" আংশিকভাবে metric-এর সীমা ছিল।
- ⚠️ পরের ধাপ: সব fault class-এর পুরোনো batch-ও INCREASED/DECREASED দিয়ে পুনর্গণনা করা। বিশেষ করে REQUEST_STRICT-এর fresh-এ "VANISHED", যা IMPL ত্রুটি আড়াল হওয়ার ইঙ্গিত দিয়েছিল।
- ⚠️ সংশোধন: §4-এর hypothesis "শিথিল spec মৌলিকভাবে কম দৃশ্যমান" দুর্বল হলো। শিথিলতা দৃশ্যমান হয়, কিন্তু নতুন fingerprint হিসেবে নয়, পুরোনো fingerprint-এর বাড়তি occurrence হিসেবে। তাই সহজে দৃশ্যমান হয় না।
