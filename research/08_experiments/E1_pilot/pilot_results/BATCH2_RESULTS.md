# Pilot Batch 2 — scout-api, পূর্ণ traffic (2026-11-14)

**Batch 1 থেকে পার্থক্য:** `SCHEMA_CHECKS=response_headers_conformance`।
- Schemathesis কোনো check ব্যর্থ হলে সেই operation ছেড়ে দেয়। Batch 1-এ তাই ৩৫টি operation মাত্র ২টি করে request পেয়েছিল।
- আমাদের oracle `tools/conformance.py`, তাই generator-এর check বদলালে মাপ বদলায় না।

**Setup:**
- ১৫/১৫ run সম্পূর্ণ; প্রতিটিতে **৪,৭০৩টি exchange**, ৪৯/৪৯ operation।
- Data: `../runs/scout-api/` · সারাংশ: `batch2_attribution_summary.csv`, `batch2_baseline_s1_violations_prelim.csv`।

⚠️ = অনুমান। একটি SUT — pilot পর্যবেক্ষণ।

## 1. Baseline (seed 1)
- ৪,৮৯৮টি violation occurrence, **৯৯টি অনন্য fingerprint** (Batch 1-এ ৫৩)। Seed ২ ও ৩-এ ৯৬টি করে।

| ধরন | অনন্য | প্রাথমিক label (rule; এখনো code দেখে যাচাই হয়নি) |
|---|---|---|
| SERVER_ERROR (500) | ৩৩ | IMPL / I-CRASH (codebook R1) |
| UNDOCUMENTED_STATUS 500 | ১৬ | IMPL — উপরেরগুলোরই দ্বিতীয় রূপ |
| VALID_REJECTED (400) | ২০ | UNDECIDABLE → ⚠️ সম্ভাব্য **S-REQ-LOOSE**: spec-বৈধ body server প্রত্যাখ্যান করছে (যেমন `POST /v2/activities` ৯২ বার) |
| UNDOCUMENTED_STATUS 400/404/403 | ২৬ | SPEC / S-STATUS (confidence ১) |
| INVALID_ACCEPTED | ৩ | UNDECIDABLE — `/v1/users/profile`, `/v1/favourites`-এ “required path id”। ⚠️ spec-এর path-level parameter নাকি checker-এর path matching — যাচাই দরকার |
| UNDOCUMENTED_OPERATION | ১ | UNDECIDABLE |

- ⇒ প্রাথমিক: IMPL ৪৯, SPEC ২৬, UNDECIDABLE ২৪।
- **একটি বাস্তব SUT-এ SPEC ও IMPL দুই ধরনই প্রচুর** — R1-এর সমস্যাটি বাস্তব data-তে উপস্থিত।

## 2. Injected spec fault (৩০%, seed ১/২/৩)

| Fault | Replay NEW | Fresh NEW | Replay VANISHED | Fresh VANISHED |
|---|---|---|---|---|
| REQUEST_STRICT | ২৮ / ২০ / ৬১ | **০ / ২ / ০** | ২ / ৫ / ৬ | ০ / ২ / ১ |
| REQUEST_LOOSE | ০ / ০ / ০ | ০ / ২ / ১ | ০ / ০ / ০ | ০ / ১ / ১ |
| RESPONSE_ORACLE | ৯০ / ০ / ০ | ৯০ / ০ / ০ | ০ | ০ |
| METHOD_SEM | ৫ / ১১ / ১৫ | ২ / ২ / ৪ | ৫ / ১০ / ১৪ | ৫ / ১০ / ১৪ |

- সব analysis-এ unexplained = ০।

## 3. পর্যবেক্ষণ
1. **REQUEST_STRICT:** পূর্ণ traffic-এও একই চিত্র, আরও স্পষ্ট।
   - Replay-এ ২০–৬১টি নতুন violation, fresh fuzzing-এ ০–২টি।
   - ⇒ Spec-চালিত fuzzer অতিরিক্ত-কঠোর spec প্রায় ধরতে পারে না। ⚠️ একটি SUT ও একটি fuzzer-এ দেখা।
2. **RESPONSE_ORACLE-এর seed-নির্ভরতা ব্যাখ্যাত:**
   - Mutation কেবল 2xx body-সহ response-এ ধরা পড়ে।
   - scout-api-র লেখার operation-গুলো প্রায় সবসময় 4xx/5xx দেয় (POST-এ ২xx মাত্র ২৪/১,০০০)।
   - Seed ১-এ ঘটনাক্রমে `POST activities` (২xx দেয়) বাছা হয়েছিল।
   - ⇒ Response-side fault মূল্যায়নে “2xx body পাওয়া operation” থেকে নমুনা নিতে হবে (stratified selection)। এটি specmut-এর জন্য উন্নতির প্রস্তাব।
3. **REQUEST_LOOSE:** এই spec-এ constraint কম, তাই প্রভাব নগণ্য (Batch 1-এর মতোই)।
4. **Baseline-এ VALID_REJECTED ২০টি:** আসল spec নিজেই সম্ভবত অতিরিক্ত-শিথিল — বাস্তব S-REQ-LOOSE-এর প্রার্থী। Code দেখে নিশ্চিত করতে হবে।

## 4. পরের ধাপ
1. scout-api-র source দেখে ৯৯টি fingerprint-এর label (E-CODE-INTENT) → প্রথম open-source ground truth।
2. `INVALID_ACCEPTED … path/id/required`: checker bug নাকি spec defect, নির্ণয়।
3. specmut-এ stratified operation selection।
4. petstore ও market-এ একই batch (harness_v2, Codex T14)।

## 6. Baseline অমিলের code-ভিত্তিক label (seed 1, ৯৯টি fingerprint)

**Labeller:** Claude একা, scout-api source ও SUT log দেখে। এটি এখনো ground truth নয়; দ্বিতীয় labeller দরকার।
**ফাইল:** `batch2_baseline_s1_labels_code.csv` (প্রতিটি সারিতে evidence locator); নিয়ম: `../label_batch2_baseline.py`।

| L1 | L2 | Fingerprint | মূল কারণ (source) |
|---|---|---|---|
| IMPL | I-CRASH | 49 (এর 16টি একই 500-এর UNDOCUMENTED_STATUS রূপ) | নিচে |
| SPEC | S-STATUS | 26 | Spec-এ শুধু `200`; বাস্তবে 400 (13), 404 (12), 403 (1) |
| SPEC | S-REQ-LOOSE | 20 | Spec শিথিল, code কঠোর |
| SPEC | S-STRUCT | 3 | Template ছাড়া path-এ required path parameter |
| TEST | T-PROBE (নতুন code, প্রস্তাবিত) | 1 | Schemathesis-এর NUL-byte probe |

প্রাথমিক নিয়ম-label থেকে পরিবর্তন: UNDECIDABLE 24 → SPEC 23, TEST 1। IMPL 49 ও SPEC 26 অপরিবর্তিত। **UNDECIDABLE এখন 0** — source থাকলে এই SUT-এ সব অমিল নির্ণয়যোগ্য।

### মূল কারণগুলো (৯৯টি fingerprint আসলে ~৮টি root cause)
1. **Null check নেই (IMPL).** `dao.read(id)`-এর ফল যাচাই ছাড়া ব্যবহার → অস্তিত্বহীন id-তে 404-এর বদলে 500।
   - `ActivityResource.java:76,94,102,119,133,144`; `ActivityRating.java:90`; `ActivityDao.java:167,219`; `MediaFileResource.java:260`।
   - Log: `NullPointerException` 1,315 বার; `IllegalArgumentException: attempt to create delete event with null entity` 498 বার।
2. **Create-এ input validation নেই (IMPL, confidence 2).** `{}` body persistence পর্যন্ত পৌঁছে `JdbcSQLException: NULL not allowed` দেয়।
   - ⚠️ [H] Spec-এও `required` নেই, তাই এগুলো BOTH হওয়ার প্রার্থী।
3. **`my_favourites` (IMPL).** `ActivityResourceV1.java:74-76`, `ActivityResourceV2.java:76-78`: status ছাড়া `WebApplicationException` → 500। Spec parameter-টি ঘোষণা করে, code বলে "currently does not support"।
   - ⚠️ [H] BOTH প্রার্থী।
4. **`POST /v1/favourites` (IMPL).** `FavouritesResourceV1.java:58,66`: `{}` body-তে id list null → NPE।
5. **Undeclared property প্রত্যাখ্যান (SPEC / S-REQ-LOOSE, confidence 2).** 1,131টি প্রত্যাখ্যাত body-র 1,054টিতে top-level অঘোষিত property; বাকি 77টিতে nested অঘোষিত property বা সীমার বাইরের মান। Schema-তে `additionalProperties: false` নেই।
   - Confidence 2, কারণ কঠোরতা framework-এর default থেকে আসে; project code-এ স্পষ্ট সিদ্ধান্ত নেই।
6. **Query parameter-এর type (SPEC / S-REQ-LOOSE, confidence 3).** `ActivityResource.java:47-55`: `participants`, `age_*`, `time_*`, `categories`, `id` spec-এ `string`, কিন্তু code comma-separated integer হিসেবে parse করে এবং স্পষ্ট 400 দেয়।
7. **ভুল path parameter (SPEC / S-STRUCT).** `UserResource.java:81-84` (`/v1/users/profile`) ও `FavouritesResourceV1.java:46,55`: `@Path`-এ `{id}` নেই, অথচ method-এ `@PathParam("id")`। Generated spec তাই অপূরণীয় required parameter ঘোষণা করে।
   - **আগের প্রশ্নের উত্তর:** এটি `conformance.py`-র bug নয়; checker ঠিক ধরেছে। সংশোধনের জায়গা code annotation।
8. **Undocumented status (SPEC / S-STATUS).** 49টি operation-এর 19টি শুধু `200` ঘোষণা করে, 30টি শুধু `default`। `default`-ওয়ালা operation-এ কোনো status-ই undocumented ধরা পড়ে না — DELETE-এর 500-গুলো তাই শুধু SERVER_ERROR হিসেবে আসে।

### R1-এর জন্য তাৎপর্য
- একই SUT-এ SPEC 49 ও IMPL 49 — প্রায় সমান। ⚠️ এটি fingerprint গণনা; root cause ধরলে IMPL ৪টি, SPEC ৪টি।
- Fingerprint ≠ fault: ৯৯টি fingerprint ~৮টি কারণে নেমে আসে। Attribution-এর মূল্যায়নে root-cause clustering লাগবে।
- BOTH প্রার্থী (কারণ 2, 3, 4) codebook-এর খোলা প্রশ্নটির (BOTH আলাদা শ্রেণি দরকার কিনা) প্রথম বাস্তব উদাহরণ।
- সীমা: একজন labeller, একটি SUT, একটি seed; spec code থেকে generated, তাই "spec defect"-এর অনেকগুলোর সংশোধনের জায়গা code annotation।
