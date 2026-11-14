# Checker-এ int32/int64 format যাচাই (2026-11-14, Claude)

## কেন
- **E5 blind v2-এর item E014:** petstore `GET /pet/{petId}`-এ 2^63-এর বেশি একটা ID গিয়েছিল। Spec বলে `integer/int64`, আর SUT 400 দিয়েছে (Java `Long`-এ রূপান্তর ব্যর্থ)।
- Draft4-এর format checker int32/int64 উপেক্ষা করে। তাই checker request-টাকে বৈধ ধরে **ভুয়া VALID_REJECTED** দিত।
- চারজন blind labeller-ই এটাকে TEST (checker-এর ফাঁক) বলেছিল।

## পরিবর্তন
- `tools/conformance.py`:
  - `FORMAT_CHECKER` এখন Python int-এর জন্য int32/int64-এর সীমা যাচাই করে। Bool আর int নয় এমন মান পাস করে।
  - `INT_FORMATS=False` (CLI `--no-int-formats`) দিলে আগের আচরণ ফিরে আসে, পুরোনো analysis পুনরুৎপাদনের জন্য।
- **Test:** `test_review_fixes.py` R10d।
  - Request: query int64/int32 সীমা, ভেতরে ও বাইরে।
  - Response body, legacy switch।
  - সব suite পাস: review-fixes 31, specmut 144/144, pipeline, triage, only-ops।
- **স্বাধীন review:** Codex T24 (`09_collab/reports/T24_review.md`)। Review-এর পর যা বদলেছে:
  - **F1, ঠিক করা হয়েছে:** OAS 3.1-এ পূর্ণসংখ্যার মানওয়ালা float (`9223372036854775808.0`, `1e100`) আগে range check এড়িয়ে যেত। এখন `int()` দিয়ে নিখুঁত তুলনা হয়। Fraction-ওয়ালা মানের বিচার করে `type`, format নয়। `type: number` + `format: int32/int64` হলে শুধু পূর্ণসংখ্যার মানের range যাচাই হয়। এটা নীতি হিসেবে নথিভুক্ত।
    - সংরক্ষিত run-এ প্রভাব নেই, impact CSV byte-সমান।
  - **F2, ঠিক করা হয়েছে:** `eligible_ops` এখন checker যে format-গুলো সত্যিই যাচাই করে (`date`, `date-time`, `int32`, `int64`), সেগুলোর অপসারণকে LOOSE-এর ক্ষেত্রে কার্যকর ধরে। `uuid`/`email`-এর মতো format এখনো বাদ।
    - `--legacy-formats` দিলে পুরোনো pool হুবহু ফেরে।
    - ⚠️ ভবিষ্যতের REQUEST_LOOSE spec-pool আগের চেয়ে বড় হতে পারে। আগের LOOSE ফল পুরোনো pool-এর।
  - **F3, সীমা হিসেবে রাখা হয়েছে:** `analyse_run.sh` আর E5 pipeline `--no-int-formats` পাঠায় না। Tool-hash guard ইচ্ছাকৃতভাবে পুরোনো collection-এ নতুন checker চালানো আটকায়।
    - পুরোনো analysis পুনরুৎপাদন করতে হলে standalone CLI-তে `--no-int-formats` দিতে হবে। T24 চারটি baseline-এ যাচাই করেছে যে এতে আগের output byte-সমান আসে।
    - নতুন analysis নতুন নিয়মেই চলবে।
  - Test: R10d-তে float, `number` আর OAS 3.1-এর case যোগ হয়েছে। `test_only_ops`-এ নতুন আর legacy pool আছে। সব suite পাস।

## সংরক্ষিত run-এ প্রভাব (`int_format_impact.py` → `int_format_impact.csv`)
- 265টি সম্পূর্ণ run আবার যাচাই করা হয়েছে (spec.original, default oracle), পুরোনো আর নতুন দুই নিয়মে।

| SUT | Run | পরিবর্তিত run | পরিবর্তন |
|---|---|---|---|
| scout-api | 86 | 86 | VALID_REJECTED occurrence −3052 |
| swagger-petstore | 67 | 67 | VALID_REJECTED occurrence −1171 |
| market | 64 | 0 | — |
| cwa-verification | 48 | 0 | — |

- **শুধু VALID_REJECTED কমেছে।** কোনো নতুন INVALID_ACCEPTED আসেনি: সীমা ছাড়ানো int কোনো SUT 2xx দিয়ে গ্রহণ করেনি।
- **E2-এর চূড়ান্ত label:**
  - P016 (`DELETE /pet/{petId}`) আর P017 (`GET /pet/{petId}`) পুরো মুছে যায়। দুটোরই চূড়ান্ত label ছিল TEST, অর্থাৎ checker-এর ফাঁক, যা এই পরিবর্তনের সাথে মেলে।
  - আরও 8টি item 1–3টি করে occurrence হারায়। **কোনো label বদলায় না।**
- **E5:**
  - Mapped op-এ প্রভাব পড়েছে শুধু petstore-reject-valid আর petstore-response-field-এ (`GET /pet/{petId}` VALID_REJECTED)।
  - response-field-এর প্রত্যাশিত kind (RESPONSE_SCHEMA) অপরিবর্তিত। অন্য 7টি mutant-এর ফলও অপরিবর্তিত।
  - **petstore-reject-valid** (mapped op-এ VALID_REJECTED occurrence, পুরোনো → নতুন):

| seed | control | mutant | noise control | control_repeat |
|---|---|---|---|---|
| s1 | 6→5 | 6→5 | 6→5 | 6→5 |
| s2 | 2→0 | 4→1 | 2→0 | 1→0 |
| s3 | 4→1 | 4→1 | 3→2 | 4→1 |

  - অর্থাৎ নতুন checker-এ s2-তে একটা দুর্বল সংকেত (1 বনাম 0/0/0) noise ছাড়ায়। s1 আর s3-এ কিছু নেই।
  - বাকি baseline 400-গুলোর উৎস অন্য, যেমন header-এ control byte।
  - তাই বিকল্প site (T25) এখনো দরকার।
- ⚠️ পুরোনো analysis ফোল্ডারগুলো আগের checker hash নিয়ে অপরিবর্তিত আছে। আগের ফলের নথিতে (BATCH2, PETSTORE, LOOSE, E5) উল্লেখ করা VALID_REJECTED সংখ্যা আগের checker-এর।
