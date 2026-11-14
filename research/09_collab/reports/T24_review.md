**T24 — int32/int64 format enforcement-এর independent review**

রায়: Python `int`-এর signed bounds এবং E014-এ বর্ণিত path overflow-এর fix সঠিক; তবে পূর্ণ integer-format enforcement হিসেবে গ্রহণের আগে OAS 3.1-এর integral-float bypass এবং REQUEST_LOOSE pool-এর অসঙ্গতি সমাধানের সুপারিশ করছি। Legacy CLI output পুনরুৎপাদিত হয়েছে, কিন্তু existing pipeline দিয়ে historical analysis চালানোর ব্যবস্থা এই switch একা দেয় না। প্রমাণ: `08_experiments/tools/conformance.py:44–58,107–110,267–270,480–482`; `08_experiments/tools/eligible_ops.py:22–32`; নিচের F1–F3 ও audit rows T24-PROBE/T24-BYTES। E014 সম্পর্কে motivation শুধু task-এর বিবরণ থেকে নেওয়া; blind package স্বাধীনভাবে যাচাই করা হয়নি (`09_collab/tasks/T24.md:7,36`)।

**পরিধি ও execution record**

Protocol ও task অনুযায়ী implementation সম্পাদনা করা হয়নি; স্থায়ী output এই report ও board-এর একটি Log line। `/usr/bin/python3 -I -B` দিয়ে own Python tests/probes চালানো হয়েছে; Docker, Java, Maven, network বা third-party project code চালানো হয়নি; নিষিদ্ধ `E2_labelling/e5_blind*` ও `E5_codemut/blind_key*` খোলা হয়নি। Constraints: `09_collab/PROTOCOL.md:4–15`; `09_collab/tasks/T24.md:32–37`। নিচের audit rows এই review-এর সরাসরি পর্যবেক্ষণ; `/tmp` artifacts সাময়িক, তাই গুরুত্বপূর্ণ output এখানেই সংরক্ষিত।

| Audit row | সংরক্ষিত পর্যবেক্ষণ |
|---|---|
| T24-ENV | `/usr/bin/python3`: 3.14.7; installed `jsonschema`: 4.26.0। |
| T24-SOURCE | Reviewed `conformance.py` Git blob `bc3d58359ccc80927787ede87000ebb96eb960d6`। Review base Git blob prefix `98d8ac5`, diff-এ উল্লিখিত একই base (`09_collab/logs/T24_change.diff:1–4`)। |
| T24-UNIT | `test_review_fixes`: **31/31**; `test_only_ops`: **6/6**; `test_triage`: **61/61**; মোট **98**, failures/errors/skips **0**। Source entry points: `08_experiments/tools/test_review_fixes.py:404`, `test_only_ops.py:104`, `test_triage.py:574`। |
| T24-CORPUS | `test_specmut.py 08_experiments/_external/emb/openapi-swagger`: **144 passed, 0 failed**। এটি unittest suite নয়; তার `main()` চালানো হয়েছে (`08_experiments/tools/test_specmut.py:90–108`)। |
| T24-PIPELINE | একই corpus-এ replay check **PASS**, unexplained **0**। `REQUEST_LOOSE`: mutated ops 419, NEW 0, VANISHED 31; `REQUEST_STRICT`: 569/2052/0; `RESPONSE_ORACLE`: 465/2972/0; `METHOD_SEM`: 407/406/582। Check-এর অর্থ locality, SUT correctness নয় (`08_experiments/tools/test_pipeline.py:109–146`)। |
| T24-PROBE | `/tmp/T24_review/probe.py`: **32 observation records**, parameter boundaries-এর **176** assertions এবং JSON request/response boundaries-এর **60** assertions pass; float, number, nullable, arrays, forms, pool ও cached-global probes-ও pass। এখানে pass মানে নথিবদ্ধ আচরণ reproduce হয়েছে; F1/F2 ঠিক হয়েছে এমন নয়। |
| T24-WRITES | প্রথম verification-এ snapshotted **41/41** own tool/E5 Python/harness files অপরিবর্তিত ছিল। Final verification-এ **40/41** অপরিবর্তিত; শুধু unrelated `08_experiments/E5_codemut/test_codemut.py`-এর concurrent hash change দেখা গেছে, এই review সেটি edit/run করেনি। Reviewed `conformance.py`, `test_review_fixes.py` এবং harness sources অপরিবর্তিত। `test_review_fixes.py:65,378`-এর hard-coded `T10_scratch` temp directory runtime `unittest.mock.patch` দিয়ে `/tmp/T24_review`-এ সরানো হয়েছে; repository test source অপরিবর্তিত। |

SHA record:

```text
reviewed Git blob: bc3d58359ccc80927787ede87000ebb96eb960d6
T24_change.diff SHA-256: 431df1689524ee77923af9e406c37652460508baeabeecfe497cbd1f8029e6a6
reviewed conformance.py SHA-256: 1398afb883f2d6f8c7965168d9eec3c305b5e9b37637ab0f154a5a4f1297528b
base 98d8ac5 source SHA-256: 405a40dc742a6eb7cbde90d72dd79a4932c1c49da3f7e7bf5e0358207612a032
/tmp/T24_review/probe.py SHA-256: c5b5b7466541e60820b5a41eca1980309c1e9c976d874522d6955a4903335f9f
/tmp/T24_review/probes.json SHA-256: 02108cb5a4252e66883c4182c03cb662fcda2f23ac33fcc237b8b61cda688a2a
/tmp/T24_review/compare.py SHA-256: 0fe266f196a5e5532429bcccb7533af5a1cb8513103e061c3a863f69f967c015
/tmp/T24_review/comparison.json SHA-256: 6106889ab76daf958c220caac613ca99623896524a3edcd763d52575151ed9d5
/tmp/T24_review/tests.json SHA-256: b6bff6412ade8bc7dd58489c2582bf3796cb84eb0a99192960573d347b171cf9
concurrent test_codemut.py SHA-256 before: c8ff181a9ec805bebbb7543b8bb57101e72016284c59ce03d54f3bc0a9bb4996
concurrent test_codemut.py SHA-256 observed after: 9d4170e60786393fdd74fb0afb93c9a3eaf0f9d83d49cb7644dbdf226f0d473c
```

**1. প্রতিটি validation site-এর correctness**

সব schema validation `Spec.errors()` → `validator()` দিয়ে যায়; `format_checker=FORMAT_CHECKER` উভয় validator class-এই সরাসরি দেওয়া হয়। `format` normalization-এ বাদ যায় না। Request validity, response schema errors ও nested array items তাই একই checker ব্যবহার করে (`08_experiments/tools/conformance.py:65–104,107–139,246–254,292–296`)।

| Site | ফল ও সীমা | file:line evidence |
|---|---|---|
| Query/path/header/cookie | `type: integer`-এর captured decimal string `int()` হয়; int32/int64-এর `lo-1`, `lo`, `hi`, `hi+1` সঠিকভাবে reject/accept হয়। OAS 3.0/3.1-এর চার location এবং Swagger 2-এর query/path/header, উভয় format ও HTTP 200/400 মিলিয়ে 176 assertions pass (T24-PROBE)। Cookie `<redacted>` হলে range পরীক্ষা হয় না; `REQUEST_UNCHECKABLE` হয়। | `08_experiments/tools/conformance.py:257–274,319–362,457–463` |
| Swagger 2 parameter-level `type`/`format` | `schema` না থাকলে `PARAM_SCHEMA_KEYS` দিয়ে parameter থেকেই দুটো key নেওয়া হয়; সুতরাং একই enforcement কার্যকর। Swagger 2 boundary probes-এ এটি সরাসরি যাচাই হয়েছে। | `08_experiments/tools/conformance.py:142–143,321,354–360` |
| JSON request body | JSON decode হওয়া Python `int`-এ bounds কার্যকর; invalid body-সহ 2xx-এ `INVALID_ACCEPTED`, 400-এ `VALID_REJECTED` হয় না। Swagger 2 body parameter ও OAS 3 requestBody উভয় route পরীক্ষা হয়েছে। Float ব্যতিক্রম F1-এ। | `08_experiments/tools/conformance.py:299–305,365–393,460–463` |
| JSON response body | একই range error `RESPONSE_SCHEMA`, keyword `format` দেয়; response type error আলাদা থাকে। তিন dialect-এর request/response, দুই format, চার bound ও 1001-digit integer মিলিয়ে 60 assertions pass। | `08_experiments/tools/conformance.py:233–237,438–456`; T24-PROBE |
| OAS 3 form body | `application/x-www-form-urlencoded` এবং multipart-এর decoder নেই; schema থাকলে unsupported encoding → `REQUEST_UNCHECKABLE`। Probe-এ urlencoded form-এর 400-এ এই output এসেছে। এটি নতুন format change-এর regression নয়, বিদ্যমান coverage limit। | `08_experiments/tools/conformance.py:299–305,382–393,458–463` |
| Swagger 2 `formData` | Supported parameter locations-এর বাইরে; probe-এ `unsupported parameter location: formData` → `REQUEST_UNCHECKABLE`। নতুন checker form values পর্যন্ত পৌঁছায় না। | `08_experiments/tools/conformance.py:320–344` |
| OAS 3.1 | **হ্যাঁ, `format` assert হচ্ছে**: `Draft202012Validator`-কেও explicit checker দেওয়া হয়। Plain out-of-range Python int-এ `format` error reproduce হয়েছে। তবে সেই validator-এর integral-float integer support-এর সঙ্গে `_int_format()` অসঙ্গত; F1 দেখুন। | `08_experiments/tools/conformance.py:50–54,61–62,107–110`; T24-PROBE |

⚠️ Unsupported/redacted captures ও unsupported parameter serialization-এ পুরো request validity স্থির করা যায় না; সেই অবস্থায় `VALID_REJECTED` না দেওয়া checker-এর explicit guard-এর সঙ্গে সামঞ্জস্যপূর্ণ। `$ref`-সহ scalar parameter serialization-ও uncheckable branch-এ পড়ে; এই change তার coverage বাড়ায় না (`08_experiments/tools/conformance.py:335–352,458–463`)।

**2. Edge cases ও F1 — P1: OAS 3.1 integral-float range bypass**

`_int_format()` শুধু `isinstance(value, int)` হলে bounds দেখে। OAS 3.1 validator integer-valued Python `float`-ও `integer` হিসেবে গ্রহণ করেছে; ফলে একই mathematical overflow JSON-এ integer বা decimal/exponent representation অনুযায়ী আলাদা ফল দেয়। Request-এর 400 ভুলভাবে `VALID_REJECTED` হতে পারে এবং response-এর overflow বাদ পড়ে। এটি সরাসরি end-to-end reproduction, hypothesis নয় (`08_experiments/tools/conformance.py:50–53,108–110,302,453–463`; T24-PROBE `float_json`)।

| Schema ও input | পর্যবেক্ষণ |
|---|---|
| OAS 3.1 `integer/int64`, JSON `9223372036854775808` | `format` error; request 400-এ `VALID_REJECTED` নেই; response 200-এ `RESPONSE_SCHEMA`। |
| একই schema, JSON `9223372036854775808.0`, `1e100`, `-1e100` | Request 400-এ **`VALID_REJECTED`**, response 200-এ **কোনো violation নেই**। |
| একই schema, JSON `1.0` | Valid: request 400-এ `VALID_REJECTED`, response 200-এ violation নেই। এটি range-এর ভেতরে থাকা integral float-এর positive control। |
| Swagger 2/OAS 3.0 `integer/int64`, JSON `1.0` বা উপরোক্ত বড় floats | Draft4 type check-এই invalid; response-এ `RESPONSE_SCHEMA` keyword `type`। এটি আগে থেকেই ব্যবহৃত dialect behavior, নতুন range check-এর ফল নয়। |
| `number/int64`, Python int `2**63` বনাম `float(2**63)` | প্রথমটিতে `format`, দ্বিতীয়টিতে error নেই। `0.5`-ও format checker পার হয়। `type: number` parameter-এর চার location-এই `coerce()` float বানায়; `2**63` পাঠিয়ে 400 পেলে `VALID_REJECTED` থাকে। |

শেষ row-এর representation dependence-এর source: `08_experiments/tools/conformance.py:50–53,267–270`; বাকি rows-এর source: `:107–110,299–302` এবং audit T24-PROBE। **সুপারিশ:** ⚠️ OAS 3.1-এর finite integral floats-এও signed bounds পরীক্ষা করা উচিত; bool exemption রাখতে হবে। বড় integer-কে float-এ রূপান্তর করে তুলনা করা উচিত নয়, যাতে int64-এর শেষ valid value rounding-এ হারিয়ে না যায়। `type: number`-এ int format-কে integral numeric restriction হিসেবে নেওয়া হবে কি না explicit policy ও tests দিয়ে স্থির করা দরকার; বর্তমান Python representation-নির্ভর ফল এড়ানো উচিত। এই recommendation নতুন code edit নয়; কারণটি উপরের reproduced mismatch।

বাকি edge cases:

| Case | ফল | Evidence |
|---|---|---|
| Negative bounds | int32 `-2147483648`, int64 `-9223372036854775808` valid; প্রত্যেকটির এক কম invalid; positive maximum ও এক বেশি-ও ঠিক। | `08_experiments/tools/conformance.py:44,48–53`; T24-PROBE |
| Very large plain JSON integer | `10**1000` JSON round-trip-এর পরে Python int; দুই format ও তিন dialect-এই request invalid/response schema error। Decimal/exponent বড় সংখ্যার ফল F1-এ। | `08_experiments/tools/conformance.py:50–53,299–302`; T24-PROBE |
| `type: [integer, null]`, `format: int64` | JSON null valid; out-of-range int-এ `format`; bool-এ `type`। OAS 3.0 ও 3.1 validator probes-এ একই ফল; `coerce()` type list থেকে non-null type বেছে নেয়। | `08_experiments/tools/conformance.py:50–53,74–76,260–268`; T24-PROBE `nullable_bool` |
| Array of int32 | Query comma-separated values recursive `coerce()` পায়; `[1,2147483648]`-এ parameter error keyword `format`, JSON response-এ `RESPONSE_SCHEMA`; তিন dialect-এ reproduce। OAS 3 query probe-এ `explode=False` স্পষ্টভাবে দেওয়া হয়েছে। | `08_experiments/tools/conformance.py:263–265,355–360,453–454`; T24-PROBE `arrays` |
| Booleans | Direct format check True/False-কে range error দেয় না, কিন্তু `integer`/`number` schema-তে type check reject করে। Format-only schema হলে bool-এর উপর type restriction আসে না। | `08_experiments/tools/conformance.py:50–53,139`; T24-PROBE `nullable_bool`, `number_representation`, `format_nonints` |
| Non-numeric value | String/null/fractional float direct int-format checker পার হয়; schema-এর type/union independently সিদ্ধান্ত নেয়। Integer parameter-এ textual `1.0` `int()` conversion-এ fail করে string থাকে, JSON `1.0`-এর মতো float হয় না। | `08_experiments/tools/conformance.py:50–53,267–275`; T24-PROBE `format_nonints` |

**3. F2 — P2: `eligible_ops` এখন enforced format-only loosening বাদ দেয়**

`CHECKED_LOOSE_KEYS` এখনও blanket `format` বাদ দেয় এবং comment-এ int64 checker-ignored বলা আছে। অথচ `specmut.mutate_loose()` `format` সরায়। Required path parameter-এর `integer/int64` ছাড়া অন্য request constraint না থাকলে `eligible_ops.loose_effective()` False, যদিও overflow capture-এ base থেকে mutated spec-এ output `[]` → `['VALID_REJECTED']` হয়েছে (`08_experiments/tools/eligible_ops.py:22–32`; `08_experiments/tools/specmut.py:83–103,131–148`; T24-PROBE `format_only_pool`)।

Exact probe edit: `/paths/~1x~1{q}/get/parameters/0/schema/format`, before `int64`, after null; `q=9223372036854775808`, HTTP 400। Required path flag অপরিবর্তিত থাকায় এখানে format removal-ই একমাত্র edit। ⚠️ ফলে spec-based REQUEST_LOOSE pool measurable operation বাদ দিতে পারে; বর্তমান pool-এর উপর নতুন checker দিয়ে গবেষণার ফল ব্যাখ্যা করলে এই selection mismatch জানাতে হবে (`08_experiments/tools/specmut.py:133–148`; `08_experiments/tools/eligible_ops.py:67–73`)।

সুপারিশ: ⚠️ selector ও checker-এর policy মিলিয়ে enforced format values বিবেচনা করুন; নতুন mode-এ অন্তত `int32`/`int64`, legacy mode-এ সেগুলো বাদ। `format` key নির্বিচারে যুক্ত করলে unknown/non-asserted formats-ও eligible হবে, তাই `edit.before`-এর format name ও schema/request checkability দেখা ভালো। ইতিমধ্যেই custom `date`/`date-time` checks আছে, তাই “checker ignores format” মন্তব্য সাধারণভাবেও ভুল (`08_experiments/tools/conformance.py:21–37,50–58`)। Current opposite-expectation test `test_format_only_and_structural_ops_are_not_eligible`-কেও policy-aware expectations-এ বদলাতে হবে; এখন সেটি 6/6 passing suite-এর মধ্যেই পুরনো exclusion lock করে (`08_experiments/tools/test_only_ops.py:89–101`; T24-UNIT)। কোনো implementation/test পরিবর্তন করা হয়নি।

**4. Reproducibility ও F3 — P2 integration limitation: CLI legacy mode আছে, pipeline forwarding নেই**

**একই runtime/input/options-এ immediate pre-change checker-এর violation JSONL পুনরুৎপাদনের জন্য switch কার্যকর।** `INT_FORMATS=False` হলে registered callbacks কোনো error তৈরি করে না, আর CLI `--no-int-formats` main-এর আগে flag সেট করে (`08_experiments/tools/conformance.py:50–53,476–491`)। Git base `98d8ac5` থেকে own previous source `/tmp`-এ রেখে subprocess CLI comparison করা হয়েছে; চারটি saved complete baseline run-এ পুরনো source বনাম নতুন source + switch stdout **byte-identical**। Synthetic path overflow-তেও old == legacy, default output empty; শুধু module mock পরীক্ষা করা হয়নি (audit T24-BYTES নিচে)।

| T24-BYTES row | Saved baseline run directory (`08_experiments/E1_pilot/runs/`-এর নিচে) | Exchanges | Old = legacy diagnostic lines | New default lines |
|---|---|---:|---:|---:|
| scout | `scout-api/20261114T025044Z_batch_1756007_baseline_NONE_p0_s1` | 4703 | 4898 | 4891 |
| petstore | `swagger-petstore/20261114T021642Z_baseline_NONE_p0_s1_1699769` | 1458 | 1118 | 1107 |
| market | `market/20261114T023117Z_baseline_NONE_p0_s1_1723021` | 1202 | 509 | 509 |
| cwa | `cwa-verification/20261114T084715Z_baseline_NONE_p0_s1_117308` | 430 | 430 | 430 |

প্রতি directory-র input `spec.test.json`, `exchanges.jsonl` এবং deployment metadata `run.json`; generic reject statuses `400,422` রাখা হয়েছে। এটি captured-data offline replay, নতুন SUT execution বা batch validity assessment নয়। তুলনা পুরো bytes-এর; শুধু line count নয়। Old/legacy output SHA-256:

```text
scout:    2e67522be800deae6185fa565ebb116893312122c30160dc26084e15f26bd867
petstore: 731955aae6f697a969ea42941f78d0693877b74eedd824b14382122f0415ea7b
market:   000576034f23f6134e10e0727537770b3f085d526d4ede8780c2a6ab95322916
cwa:      78112052bada057ce287bfeeb9b55b97182c34762393c0ed9474650b0c667c2f
```

**পুরো historical analysis byte-for-byte পুনরুৎপাদনের জন্য switch একা যথেষ্ট নয়।** Immediate base-এর সঙ্গে checker stdout equality-এর প্রমাণ আছে; পুরনো arbitrary checker versions, dependency versions, attribution/metadata artifacts বা সব recorded exchanges-এর equality দাবি করছি না। Source hash বদলেছে; উপরোক্ত চার run-এর recorded conformance hash-এর সঙ্গে current hash-ও মেলেনি (T24-BYTES)। Pipeline-specific evidence:

- `harness_v2/analyse_run.sh` current tools-এর hash collection hash-এর সঙ্গে মিলিয়ে **analysis তৈরির আগেই** থামে; conformance invocations-এ deploy-origin/reject-statuses আছে, `--no-int-formats` নেই; inputs record-এও integer policy নেই (`08_experiments/E1_pilot/harness_v2/analyse_run.sh:30–35,68–80`)। Older harness-এর invocations-এও forwarding নেই (`08_experiments/E1_pilot/harness/analyse_run.sh:46–58`)।
- E5 `analyse_pair()` আগে validation করে; validator current tool inventory/hashes যাচাই করে। তারপর conformance arguments-এ শুধু spec/exchanges/deploy-origin/reject-statuses দেয়; `analysis.json`-এ integer policy নেই। Post-analysis snapshot check-ও আছে (`08_experiments/E5_codemut/validate_pair.py:263–267`; `e5_common.py:56–61`; `e5_pipeline.py:155–180`)।
- ⚠️ তাই existing immutable collection-এ current checker ও switch দিয়ে এই pipeline অপরিবর্তিত অবস্থায় চালানো যাবে না; hash mismatch ইচ্ছাকৃত provenance guard। উপরের equality পরীক্ষা standalone offline CLI-তে হয়েছে। সুপারিশ: future reviewed integration-এ explicit integer policy forwarding ও recording যোগ করুন; historical data-র জন্য matching tools/dependencies-সহ isolated reconstruction অথবা আলাদা provenance-সহ offline reanalysis করুন, saved `run.json` hashes বদলে bypass করবেন না (একই source locations)।

**Module-global safety:** বর্তমান invocations-এ safe process isolation আছে: harness-এর প্রতিটি `pytool` এবং E5-এর প্রতিটি `tool()` আলাদা `/usr/bin/python3 -I -B` process তৈরি করে। একটি run/role-এর flag অন্য subprocess-এ leak করে না (`08_experiments/E1_pilot/harness_v2/analyse_run.sh:53–55`; `08_experiments/E5_codemut/e5_pipeline.py:127–132`)। কিন্তু parent process-এ `conformance.INT_FORMATS=False` করলেও child CLI legacy হয় না; environment variable পড়ার ব্যবস্থাও নেই (`08_experiments/tools/conformance.py:43,480–482`; একই subprocess callsites)।

একই process-এর library use-এ policy per-`Spec` নয়: cached validator-সহ একই `Spec`-এ global True → False → True করলে outputs `[]` → `['VALID_REJECTED']` → `[]` হয়েছে (T24-PROBE `cached_validator_global`; `08_experiments/tools/conformance.py:50–53,246–254`)। ⚠️ Mixed-policy concurrent/threaded library calls তাই safe নয়; ভবিষ্যৎ library API-তে instance-specific policy/format checker ব্যবহার করা ভালো। বর্তমান subprocess pipelines-এ এই concurrency defect দাবি করছি না।

**5. Missing tests ও প্রস্তাবিত acceptance checks**

বর্তমান R10d মূলত OAS 3.0 query integer overflow, কয়েকটি boundary, int32 object response, direct bool/string format checks এবং mocked legacy flag cover করে। Path/header/cookie, Swagger 2, request JSON, OAS 3.1, float semantics, arrays/nullable, real CLI flag parsing ও pipeline propagation সেখানে নেই (`08_experiments/tools/test_review_fixes.py:234–251`)। ⚠️ নিচের regressions যোগ করা উপযুক্ত:

1. **F1:** OAS 3.1 request ও response-এ `integer/int32|int64`, JSON `1.0`, upper/lower overflow decimal এবং exponent; in-range float positive control রাখতে হবে। `number/int64`-এর int/float/fraction policy-ও test করুন (`conformance.py:50–53,107–110,267–270`; T24-PROBE float/number rows)।
2. **সব boundaries ও sites:** `lo-1`, `lo`, `hi`, `hi+1`, Python arbitrary-precision JSON int; path/query/header/cookie after coerce; Swagger 2 parameter-level format; JSON body ও response; nullable union, bool type errors, arrays এবং local-reference body schemas (`conformance.py:44,107–139,257–275,315–393,438–463`)।
3. **F2:** format-only path/body ops new mode-এ eligible; legacy mode-এ integer-only format অপসারণের কারণে eligible নয়; unknown formats বাদ; structural-only ops বাদ। Existing reverse assertion update দরকার (`eligible_ops.py:22–32`; `test_only_ops.py:89–101`)।
4. **Legacy CLI ও isolation:** subprocess-এ actual `--no-int-formats` parsing; base-source/golden output-এর byte comparison; flag ছাড়া পরের process-এ default পুনঃস্থাপন; response enforcement-ও legacy-তে বন্ধ হওয়া। Per-instance policy এলে cached validators ও concurrent mixed policy পরীক্ষা করুন (`conformance.py:246–254,476–491`; T24-BYTES)।
5. **Coverage guard ও provenance:** unsupported form/redacted cookie থেকে `VALID_REJECTED` যেন না হয়; pipeline policy forwarding/metadata test এবং historical hash mismatch rejection অক্ষুণ্ণ থাকে (`conformance.py:335–344,382–393,458–463`; `harness_v2/analyse_run.sh:30–35,68–80`; `e5_pipeline.py:164–180`)।

F1/F2-এর ছোট reproduction, repository না বদলে `/usr/bin/python3 -I -B`-তে চালানোর জন্য:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / '08_experiments/tools'))
import conformance as c
import eligible_ops as e
import test_review_fixes as t

schema = {'type': 'integer', 'format': 'int64'}
for value in (2**63, float(2**63), 1e100, 1.0):
    print(repr(value), [x.validator for x in
          c.validator(schema, '3.1.0').iter_errors(value)])
# ['format'], [], [], []

d = t.doc(params=[{'name': 'q', 'in': 'path', 'required': True,
                   'schema': schema}])
d['paths']['/x/{q}'] = d['paths'].pop('/x')
print(e.loose_effective(d, '/x/{q}', 'get'))
# False, যদিও format removal উপরের overflow-এর validation বদলায়।
```

**সীমাবদ্ধতা ও open questions:** Forms/multipart execution এবং external refs এই review-তে নতুন support পায়নি; no-network constraint-এ normative external format specification যাচাই করা হয়নি। `type: number`-এ integer-format applicability ও historical reanalysis provenance policy coordinator-কে স্থির করতে হবে। চার baseline-এর standalone byte equality full historical corpus-এর guarantee নয়; F1/F2-এর existence ও subprocess behavior সরাসরি code/probes-এ প্রতিষ্ঠিত, broader experiment impact এই review-তে হিসাব করা হয়নি (`09_collab/tasks/T24.md:32–37`; `08_experiments/tools/conformance.py:50–53,135–137,299–305`; T24-PROBE/T24-BYTES)।
