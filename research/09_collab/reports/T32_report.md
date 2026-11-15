# T32 — EvoMaster কি REQUEST_STRICT constraint ভাঙে?

**ফল: হ্যাঁ।** Controlled REQUEST_STRICT-এর EvoMaster fresh traffic-এ ৯টি SUT–seed cell-এর ৮টিতে original-valid edited location নতুন constraint ভেঙেছে। Market seed 1/2/3-এ যথাক্রমে **392 / 0 / 361**টি এমন request; ওই 753টির প্রতিটির response **500**, `2xx` একটিও নয়। তাই [H] “EvoMaster stricter spec পেয়ে added constraint কখনো ভাঙে না”—এই সাধারণ দাবিটি এবং market-এর seed 1/3-এ দাবিটি সরাসরি খণ্ডিত। Seed 2-এর checkable edited location-এ কোনো added-constraint breach পাওয়া যায়নি। (Evidence: `08_experiments/E1_pilot/pilot_results/strict_exposure.csv`, `row_type=run`, `fuzzer=evomaster`; market row IDs `market.s1.evomaster`–`market.s3.evomaster`।)

Market-এর EvoMaster paired baseline-এ mutant spec প্রয়োগ করলে eligible violation **1331 / 1642 / 1488**, যার `2xx` **81 / 280 / 667**। Schemathesis fresh-এ একই seed-গুলিতে eligible violation **221 / 192 / 296**, যার `2xx` **2 / 65 / 198**। অর্থাৎ “fresh accepted strict violation নেই” পর্যবেক্ষণটি market EvoMaster-এর ক্ষেত্রে সত্য; “fresh request constraint ভাঙে না” কথাটি সত্য নয়। এগুলো request-occurrence count; আগের replay NEW **5–11** হলো fingerprint count, তাই এক সংখ্যা হিসেবে তুলনা করা যাবে না। (Evidence: CSV `market.s{1,2,3}.{evomaster,schemathesis}`; `FUZZER_COMPARE.md:74–76`; fingerprint/acceptance rule `08_experiments/tools/conformance.py:417–424,465–471`।)

## পদ্ধতি ও গণনার সংজ্ঞা

`fuzzer_controlled_cells.csv`-এর `controlled=True`, `fault=REQUEST_STRICT` থেকে শুধু market, swagger-petstore, cwa-verification-এর seed 1–3 নেওয়া হয়েছে: ৯টি paired cell, ১৮টি mutated run। Paired baseline নিজে অনুমান না করে প্রত্যেক run-এর `analysis-*/inputs.txt` থেকে নেওয়া হয়েছে; একই run-এর applicable input file-গুলিতে baseline এক হতে হয়েছে। প্রতিটি pair-এর `complete`, seed, fuzzer, baseline/original spec equality, manifest-এর literal before/after এবং দুই fuzzer-এর manifest equality assert করা হয়েছে। Fresh exchange count-ও controlled-cell CSV-এর সঙ্গে মিলেছে। কোনো scout run খোলা হয়নি। (Evidence: `strict_exposure.py:128,316`; `09_collab/logs/T32_scratch/audit.json:inputs_sha256`; controlled CSV-এর নয়টি REQUEST_STRICT row।)

Template matching সরাসরি `conformance.Spec.match()`; method, base/server origin, concrete-route precedence, optional trailing slash এবং percent-decoded path parameter checker-এরই policy। Deployment origin হলো `http://sut-<sut>:8080`। `INT_FORMATS=True`; response-এর strict-additional policy এই request-side পরিমাপে প্রযোজ্য নয়। (Evidence: `08_experiments/tools/conformance.py:182–239,257–258`; `strict_exposure.py:252–257,326,374`।)

**কেন location-ভিত্তিক dual validation:** `conformance.request_problems()` original ও mutated spec-এ প্রতিটি edited parameter অথবা selected request-body media/schema আলাদাভাবে পরীক্ষা করে। পুরো request original-valid হওয়া বাধ্যতামূলক করলে অন্য একটি invalid parameter সত্যিকারের strict exposure আড়াল করতে পারে। এখানে body edit-এর জন্য **সম্পূর্ণ original body schema**, parameter edit-এর জন্য **সম্পূর্ণ original parameter** valid হতে হয়; শুধু changed scalar keyword pass করলেই যথেষ্ট নয়। তারপর mutated error-এর exact schema pointer ও keyword-কে semantic edit-এর সঙ্গে মেলানো হয়। `required`-এর ক্ষেত্রে কেবল নতুন required property-এর error নেওয়া হয়। (Evidence: `strict_exposure.py:81–125,230–247,269–283`; checker `conformance.py:323–402`; synthetic gate checks `09_collab/logs/T32_scratch/test_strict_exposure.py:test_union_response_classes_and_location_gate,test_body_gate_ref_expansion_and_array_unique_requests`।)

Manifest-এ `$ref` remove, `properties` add, description/type/XML metadata add-ও আছে। এগুলো আলাদা strict constraint নয়। Original ও mutated local reference resolve করে mutator-এর তিনটি পরিবর্তন—`maximum`, `maxLength`, `required`—বের করা হয়েছে। Nested semantic edit তার সবচেয়ে নির্দিষ্ট enclosing literal manifest edit-এর অধীনে আছে। ফলে ref expansion-কে constraint failure ধরা হয়নি, আবার added `properties`-এর ভেতরের nested constraint-ও বাদ যায়নি। (Evidence: `08_experiments/tools/specmut.py:48–73,108–123,151–170`; `strict_exposure.py:59–125,189–224`।)

নিচের table-এ `N` = mutated operation-এ request, `V` = ঐ edited location original-valid এবং added constraint-এ invalid এমন unique request। `A` = V × `2xx`, `R` = V × `4xx`, `O` = V × অন্য status। এই corpus-এ সব O হলো `500`; `V=A+R+O`। A-তে mutant checker `INVALID_ACCEPTED` দিতে পারে; R-তে accepted-invalid fault নেই। ⚠️ `401`/`404`/`406` দেখে নির্দিষ্ট added constraint server enforce করেছে বলা যায় না—এটি response-class হিসাব। একই request একাধিক edit ভাঙলেও run/operation/literal-edit row-এ একবার গণনা হয়েছে। (Evidence: CSV `*_violating_status_counts`; `09_collab/logs/T32_scratch/verification.json:eligible_response_statuses`; `conformance.py:465–471`।)

## প্রতি run: fresh mutated traffic

প্রতিটি row-এর পূর্ণ run name CSV-এর `run` column-এ; table-এর ID CSV-এর exact `row_id`।

| row_id | N | V | A: 2xx | R: 4xx | O: 500 |
|---|---:|---:|---:|---:|---:|
| `market.s1.evomaster` | 1239 | 392 | 0 | 0 | 392 |
| `market.s2.evomaster` | 1619 | 0 | 0 | 0 | 0 |
| `market.s3.evomaster` | 1326 | 361 | 0 | 0 | 361 |
| `market.s1.schemathesis` | 300 | 221 | 2 | 64 | 155 |
| `market.s2.schemathesis` | 400 | 192 | 65 | 66 | 61 |
| `market.s3.schemathesis` | 400 | 296 | 198 | 13 | 85 |
| `swagger-petstore.s1.evomaster` | 10239 | 2876 | 2457 | 191 | 228 |
| `swagger-petstore.s2.evomaster` | 19708 | 2622 | 1405 | 0 | 1217 |
| `swagger-petstore.s3.evomaster` | 35303 | 5543 | 2440 | 0 | 3103 |
| `swagger-petstore.s1.schemathesis` | 283 | 78 | 22 | 56 | 0 |
| `swagger-petstore.s2.schemathesis` | 443 | 157 | 10 | 79 | 68 |
| `swagger-petstore.s3.schemathesis` | 373 | 29 | 4 | 20 | 5 |
| `cwa-verification.s1.evomaster` | 2042 | 1013 | 0 | 1013 | 0 |
| `cwa-verification.s2.evomaster` | 1967 | 1967 | 19 | 1948 | 0 |
| `cwa-verification.s3.evomaster` | 1995 | 927 | 0 | 927 | 0 |
| `cwa-verification.s1.schemathesis` | 189 | 0 | 0 | 0 | 0 |
| `cwa-verification.s2.schemathesis` | 8 | 8 | 0 | 8 | 0 |
| `cwa-verification.s3.schemathesis` | 156 | 9 | 0 | 9 | 0 |

Evidence: `08_experiments/E1_pilot/pilot_results/strict_exposure.csv`, `row_type=run`, `fresh_*` columns, উপরের exact row IDs।

## প্রতি run: paired baseline traffic @ mutated spec (replay view)

এখানে একই baseline request-কে original spec-এর location-validity gate ও mutated spec-এর added constraint দিয়ে পরীক্ষা করা হয়েছে। নতুন HTTP request replay/execute করা হয়নি। Baseline run name CSV-এর `baseline_run` column-এ।

| row_id | N | V | A: 2xx | R: 4xx | O: 500 |
|---|---:|---:|---:|---:|---:|
| `market.s1.evomaster` | 1354 | 1331 | 81 | 628 | 622 |
| `market.s2.evomaster` | 1664 | 1642 | 280 | 836 | 526 |
| `market.s3.evomaster` | 1514 | 1488 | 667 | 282 | 539 |
| `market.s1.schemathesis` | 300 | 209 | 0 | 144 | 65 |
| `market.s2.schemathesis` | 400 | 283 | 67 | 152 | 64 |
| `market.s3.schemathesis` | 400 | 350 | 252 | 60 | 38 |
| `swagger-petstore.s1.evomaster` | 8956 | 6462 | 2636 | 722 | 3104 |
| `swagger-petstore.s2.evomaster` | 18149 | 16090 | 1414 | 4610 | 10066 |
| `swagger-petstore.s3.evomaster` | 30598 | 10450 | 1835 | 925 | 7690 |
| `swagger-petstore.s1.schemathesis` | 287 | 133 | 40 | 70 | 23 |
| `swagger-petstore.s2.schemathesis` | 422 | 280 | 41 | 134 | 105 |
| `swagger-petstore.s3.schemathesis` | 360 | 93 | 19 | 8 | 66 |
| `cwa-verification.s1.evomaster` | 2013 | 983 | 0 | 983 | 0 |
| `cwa-verification.s2.evomaster` | 1907 | 1907 | 0 | 1907 | 0 |
| `cwa-verification.s3.evomaster` | 1956 | 1947 | 0 | 1947 | 0 |
| `cwa-verification.s1.schemathesis` | 196 | 56 | 0 | 56 | 0 |
| `cwa-verification.s2.schemathesis` | 166 | 148 | 0 | 148 | 0 |
| `cwa-verification.s3.schemathesis` | 130 | 59 | 0 | 59 | 0 |

Evidence: একই CSV, `row_type=run`, `baseline_*` columns, উপরের exact row IDs।

## Per-edit detail ও market hypothesis-এর নির্দিষ্ট উত্তর

CSV-তে **822টি data row**: 18 `run`, 62 `operation`, 324 `manifest_edit`, 418 `constraint`। `manifest_edit`-এ প্রত্যেক literal operation + JSON pointer + before/after/existence flag আছে; `constraint`-এ resolved before/after, body media/parameter location, `error_pointer` এবং `parent_manifest_edit` আছে। প্রত্যেক স্তরে fresh ও baseline-এর N/V/A/R/O রয়েছে। `structural_or_annotation` row-এ V=0 মানে ঐ literal edit-এর নিজস্ব semantic strict change নেই; request compliance-এর দাবি নয়। Per-edit সংখ্যাগুলো যোগ করে run-total করা যাবে না। (Evidence: CSV `row_type`, `edit_role`, `semantic_constraints`, `parent_manifest_edit`; `09_collab/logs/T32_scratch/audit.json:row_counts`।)

Market EvoMaster-এর fresh-এ nonzero eligible strict edit কেবল `PUT /customer/contacts` body-এর `address.maxLength` ও `phone.maxLength`। Original-এ address maxLength=100, phone maxLength=20; mutant-এ উভয়টিই 1। সুনির্দিষ্ট expanded pointer হলো `/paths/~1customer~1contacts/put/parameters/0/schema/properties/{address,phone}/maxLength`। (Evidence: নিচের exact constraint row IDs-এর `before`/`after` columns।)

| Seed | Edited field | V fresh | A fresh | R fresh | 500 fresh | exact constraint row_id |
|---|---|---:|---:|---:|---:|---|
| 1 | `address.maxLength` | 148 | 0 | 0 | 148 | `market.s1.evomaster.o2.l3.c11` |
| 1 | `phone.maxLength` | 392 | 0 | 0 | 392 | `market.s1.evomaster.o2.l3.c12` |
| 3 | `address.maxLength` | 128 | 0 | 0 | 128 | `market.s3.evomaster.o3.l3.c11` |
| 3 | `phone.maxLength` | 361 | 0 | 0 | 361 | `market.s3.evomaster.o3.l3.c12` |

উপরের সংখ্যায় address violation-গুলো phone violation-এর subset: s1-এ union=392; s3-এ union=361। Query `name.required`/`name.maxLength`, path ID-এর `maximum` এবং অন্য edited body constraint-এ market EvoMaster fresh-এ কোনো breach নেই; seed 2-এর সব edited location checkable এবং V=0। (Evidence: CSV-এর market EvoMaster সব `constraint` row-এর `fresh_constraint_breaches`; operation row `market.s1.evomaster.o2`, `market.s3.evomaster.o3`; run row `market.s2.evomaster`।)

সরাসরি example: market s1 fresh `exchanges.jsonl:6`, `PUT /customer/contacts`, phone-এর length=16, address-এর length=0। পুরো request original checker-এ request-valid; mutated checker-এ phone `maxLength` error। Response=500, তাই উভয় spec-এ `SERVER_ERROR` + `UNDOCUMENTED_STATUS`, mutant-এ `INVALID_ACCEPTED` নয়। Seed 3-এর line 6-এ একই ফল, phone length=15। (Evidence: `08_experiments/E1_pilot/runs/market/20261114T183929Z_batch_940129_mutated_REQUEST_STRICT_p30_s1/exchanges.jsonl:6`; একই batch-এর `..._s3/exchanges.jsonl:6`; `09_collab/logs/T32_scratch/spot_checks.json`, row IDs `market.s1.evomaster`, `market.s3.evomaster`, `side=fresh`।)

⚠️ **ব্যাখ্যা:** 0 fresh checkable NEW থেকে “constraint exercise হয়নি” সিদ্ধান্ত নেওয়া ভুল। এখানে কিছু constraint-এ exposure সত্যিই শূন্য, কিন্তু phone/address-এ exposure আছে এবং সব response 500। Accepted-invalid route না পাওয়া এবং আগে থেকেই থাকা server-error fingerprint-এ পড়া observed 0 NEW-এর সঙ্গে সঙ্গতিপূর্ণ। Generator কেন ঐ input বেছে নেয়, অথবা 500-এর code-level cause কী—এই offline measurement তা প্রমাণ করে না। `FUZZER_COMPARE.md:75`-এর blanket no-breach বাক্যটি সংশোধনযোগ্য; T32-এর write scope অনুযায়ী ওই existing file বদলানো হয়নি। (Evidence: CSV market rows; `spot_checks.json`; `FUZZER_COMPARE.md:74–76`।)

আরও একটি constraint interaction আছে: original market phone regex-এ অন্তত 12 character লাগে, mutant-এ required phone-এর `maxLength=1`; cwa-এর required UUID `tan`/`registrationToken` pattern-এ 36 character লাগে অথচ mutant `maxLength=1`। তাই ঐ string location-এ দুই constraint একসঙ্গে মেনে original-valid value তৈরি করা অসম্ভব। ⚠️ EvoMaster pattern-কে length bound-এর চেয়ে অগ্রাধিকার দেয়—এই causal hypothesis সংখ্যাগুলো দিয়ে একা প্রতিষ্ঠা করা যায় না। (Evidence: market s1 mutant `spec.test.json`, `/paths/~1customer~1contacts/put/parameters/0/schema/properties/phone`; cwa s2 mutant `spec.test.json`, `/paths/~1version~1v1~1tan/post/requestBody/content/application~1json/schema/properties/registrationToken`; corresponding CSV `constraint` rows; original regex preserved in mutant schemas।)

## অন্য controlled STRICT cell

Petstore EvoMaster fresh-এ seed 1/2/3-এর V **2876 / 2622 / 5543**, A **2457 / 1405 / 2440**; মোট A=**6302**। এখানে “stricter spec-এর added constraint কখনো ভাঙে না” অনুমানের সরাসরি counterexample তিন seed-এই রয়েছে। Schemathesis-এর একই seed-এ A **22 / 10 / 4**। এগুলো occurrence count; fuzzer ranking বা unique defect count নয়। (Evidence: CSV `swagger-petstore.s{1,2,3}.{evomaster,schemathesis}`, `row_type=run`।)

Cwa EvoMaster fresh V **1013 / 1967 / 927**; A **0 / 19 / 0**। Seed 2-এ 19 accepted request দুটি operation-এ ভাগ: `POST /version/v1/tan`-এ 9টি `201`, `POST /version/v1/testresult`-এ 10টি `200`; উভয় ক্ষেত্রে 36-character original-valid `registrationToken` mutant-এর `maxLength=1` ভাঙে। Example fresh line 290-এ original checker-এ কোনো request error নেই, mutant-এ `INVALID_ACCEPTED` আছে। Schemathesis fresh V **0 / 8 / 9**, A সব seed-এ 0। (Evidence: CSV `cwa-verification.s{1,2,3}.{evomaster,schemathesis}`; constraint rows `cwa-verification.s2.evomaster.o1.l2.c2`, `cwa-verification.s2.evomaster.o2.l4.c2`; `08_experiments/E1_pilot/runs/cwa-verification/20261114T200712Z_batch_962064_mutated_REQUEST_STRICT_p30_s2/exchanges.jsonl:290`; `spot_checks.json`।)

⚠️ এই sample-এ EvoMaster “সবসময় strictly compliant generator” নয়। Market-এর নির্দিষ্ট `name`/ID edit ও seed 2-এ no-breach observation আংশিক generator sensitivity-এর সঙ্গে সঙ্গতিপূর্ণ; এটিকে সব edit, operation বা SUT-এ সাধারণীকরণ করা যাবে না। (Evidence: উপরোক্ত market/Cwa/Petstore CSV rows।)

## Validity gate ও অসম্পূর্ণ evidence

মূল V-এর পাশে CSV-তে `constraint_breaches` রাখা হয়েছে: mutant-এর নতুন constraint error পাওয়া গেছে, কিন্তু একই original location আগে থেকেই invalid হলেও এটি গণনা করে। তাই এই supplementary সংখ্যা main V-এর সমান হওয়া বাধ্যতামূলক নয়। উদাহরণ: Cwa Schemathesis s1 fresh-এ নতুন-constraint breach=17, eligible V=0; original body/location-invalid input-কে original-valid বলা হয়নি। Cwa Schemathesis s2 fresh-এর সব 8 request-এ অন্তত একটি edited location original-invalid, তবু আলাদা original-valid header location-এ strict violation আছে; run-level `original_invalid_requests` তাই V-এর সঙ্গে overlap করতে পারে। (Evidence: CSV `cwa-verification.s1.schemathesis`, `cwa-verification.s2.schemathesis`; `strict_exposure.py:269–283`।)

`uncheckable_requests`-কে valid/obeyed বলা হয়নি। Cwa s1-এর object-valued `Authorization` header checker-এর supported parameter serialization-এর বাইরে; Petstore-এর কিছু edited body XML/form-urlencoded। Selected edited media/body-তে unsupported encoding হলে তা explicit unknown। একটি request-এর অন্য checkable edited location থাকলে তার নিশ্চিত violation আলাদাভাবে গণনা করা যায়। নিচের U হলো অন্তত একটি edited location uncheckable থাকা unique request; raw structural edit-গুলোকে এর denominator করা হয়নি। (Evidence: `conformance.py:350–352,381–399`; `audit.json:runs[].examples`, metric `uncheckable_requests`; CSV `*_uncheckable_requests`।)

| SUT | Fuzzer | Fresh U (s1/s2/s3) | Baseline U (s1/s2/s3) |
|---|---|---|---|
| market | evomaster | 0 / 0 / 0 | 0 / 0 / 0 |
| market | schemathesis | 0 / 0 / 0 | 0 / 0 / 0 |
| swagger-petstore | evomaster | 2058 / 0 / 11016 | 2014 / 0 / 10787 |
| swagger-petstore | schemathesis | 72 / 0 / 122 | 51 / 0 / 89 |
| cwa-verification | evomaster | 1029 / 0 / 0 | 1030 / 0 / 0 |
| cwa-verification | schemathesis | 55 / 0 / 0 | 87 / 0 / 0 |

⚠️ Unsupported location বাদ থাকায় main V-কে সমগ্র traffic-এর exhaustive strict-exposure estimate বলা যাবে না। তবে market-এর সব edited location checkable ছিল, এবং তার zero/positive finding এই encoding সীমার ওপর নির্ভর করে না। (Evidence: CSV market `run` rows-এর fresh/baseline U=0; উপরের U table।)

## Verification, reproducibility ও সীমা

চারটি focused synthetic test PASS: location-level original-valid gate, unique-request union ও int64 overflow exclusion; body `$ref`/nested required/array/media/truncation; unsupported object header; concrete template precedence/path decoding/other response class। এরপর independent verifier `request_problems()` ব্যবহার না করে scalar/body extract করে original/mutated schema validator সরাসরি প্রয়োগ করেছে। ১৮টি run-এর fresh ও baseline মিলিয়ে **503733টি exchange line**, **77990টি fresh** এবং **70772টি baseline mutated-operation request** পড়েছে। CSV-র 822 row × 2 side × 10 metric = **16440 assertion**-এ exact agreement। 27টি representative full-checker spot check-এর capture path ও 1-based line সংরক্ষিত। (Evidence: `09_collab/logs/T32_scratch/tests.txt`; `verify_exposure.py`; `verification.txt`; `verification.json`; `audit.json:runs[].traffic`; `spot_checks.json`।)

চালানোর command:

```sh
nice -n 10 /usr/bin/python3 -I -B 08_experiments/E1_pilot/pilot_results/strict_exposure.py --audit-json 09_collab/logs/T32_scratch/audit.json
/usr/bin/python3 -I -B 09_collab/logs/T32_scratch/test_strict_exposure.py
nice -n 10 /usr/bin/python3 -I -B 09_collab/logs/T32_scratch/verify_exposure.py
```

Input provenance `audit.json:inputs_sha256`-এ 166টি permitted input/source path-এর SHA-256; script ফল প্রকাশের আগে সব hash আবার মিলিয়েছে। Run directory-তে কোনো write নেই; no Docker/Java/Maven/network/SUT/fuzzer execution। Protected existing pilot_results/tools/harness files-এর before/after freeze এবং exact output hash `09_collab/logs/T32_scratch/final_checks.json`-এ। Board-এ কেবল T32-এর একটি Log line যোগ করা হয়েছে।

সীমা: 300-second saved run, severity 30, তিন seed; request occurrence-কে independent trial বা defect বলা হয়নি। Same input-এর নতুন generation experiment চালানো হয়নি। ⚠️ Generator-internal choice, authentication/state-dependent response, এবং 500-এর code-level cause এখনও খোলা প্রশ্ন; বর্তমান result traffic exposure ও observed response class-এ সীমিত। (Evidence: selected run `run.json:budget_seconds,severity,seed`; CSV response counts; task execution boundary `09_collab/tasks/T32.md`।)
