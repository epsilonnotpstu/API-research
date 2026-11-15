# T39 — expected-kind signal ও market STRICT ablation review

**ফল:** CSV arithmetic ও নতুন noise-floor addendum সঠিক। Controlled expected-kind **20/26 বনাম 20/26**, manifest-differs **10/19 বনাম 8/19**; Schemathesis noise floor **34/61 expected, 44/61 checkable**। তবে Schemathesis ablation-এ অঘোষিত `schema_checks` পরিবর্তন আছে; `METHOD_SEM` whitelist সম্পূর্ণ mechanism coverage নয়; kind membership থেকে causal attribution করা যায় না। Findings: **F1 P1, F2–F3 P2, F4 P3**। [Evidence: `S/recount.json:7–75`; F1–F4 নিচে।]

এই report-এ `P` = `08_experiments/E1_pilot/pilot_results/`, `R` = `08_experiments/E1_pilot/runs/`, `T` = `08_experiments/tools/`, `S` = `09_collab/logs/T39_scratch/`। CSV locator-এ header line 1; JSON key/array predicate-ও locator হিসেবে ব্যবহৃত।

## Findings

### F1 — P1: Schemathesis full ও ablation-এর runtime oracle আলাদা; keyword-only causal comparison নয়

**Evidence:** original Schemathesis full s1 `schema_checks=response_headers_conformance`, required-only s1 ও no-required s1 `schema_checks=all`; recorded argv-তেও একই পার্থক্য আছে। এটি তিন seed-এই ঘটে (`R/market/20261114T104059Z_batch_339514_mutated_REQUEST_STRICT_p30_s1/run.json:30`; `R/market/20261115T025622Z_batch_1086844_mutated_REQUEST_STRICT_p30_s1/run.json:32`; `R/market/20261115T025922Z_batch_1095053_mutated_REQUEST_STRICT_p30_s1/run.json:32`; `S/recount.json`, `ablation.metadata[fuzzer=schemathesis]`)। Harness নিজেই বলে Schemathesis প্রথম failed check-এ ওই operation abandon করে; তাই `SCHEMA_CHECKS` generation-এ প্রভাব ফেলে (`08_experiments/E1_pilot/harness_v2/run_pilot.sh:56–58`)। Full-এর exchange সংখ্যা s1–s3 **1202/1154/1164**, required **117/89/104**, no-required **111/91/110** (`P/strict_ablation.csv:2–4,11–16`)। ⚠️ এই কম traffic-এর কতটা keyword change আর কতটা runtime checks-এর প্রভাব, বর্তমান তুলনা থেকে আলাদা করা যায় না।

`STRICT_ABLATION.md:25`-এর “সবগুলো exit 0” শুধু **harness exit** হিসেবে সত্য। ছয় Schemathesis ablation-এর প্রতিটির `schemathesis_exit=1`; full s2/s3-ও 1। Required s1-এ `GET /customer` runtime error `bad escape \\p at position 2` এবং 1 passed/11 failed/1 errored আছে (`R/market/20261115T025622Z_batch_1086844_mutated_REQUEST_STRICT_p30_s1/run.json:19–24`; একই run-এর `schemathesis.log:26–30,236`; `S/recount.json`, সংশ্লিষ্ট metadata)। Harness test-failure exit 1 অনুমোদন করে, তাই `complete=True` নিজে defect নয় (`08_experiments/E1_pilot/harness_v2/run_pilot.sh:328–335`)।

**প্রভাব:** baseline pairing ঠিক থাকলেও cross-variant generation settings নিয়ন্ত্রিত নয়। HAL-path evidence ও required-only collateral NEW বাস্তব; কিন্তু Schemathesis-এর variant difference-কে শুধু keyword ablation-এর ফল বলা যাবে না। EvoMaster-এর এই `SCHEMA_CHECKS` confound নেই; তার no-required result আলাদাভাবে রাখা যায় (`S/recount.json`, `ablation.metadata`; `S/market.json`, `HAL_examples`, `evo_noreq`)।

**Suggested fix:** document/table-এ runtime `schema_checks`, fuzzer exit ও harness exit পৃথকভাবে দিন; এখনকার Schemathesis comparison-কে settings-confounded descriptive result বলুন। ভবিষ্যৎ controlled ablation-এ full/required/no-required ও তাদের baselines-এ একই checks/argv রাখুন। এই review-তে rerun বা harness edit করা হয়নি।

### F2 — P2: METHOD_SEM-এর whitelist canonical subset; সব mechanically possible method-contract mismatch ধরে না

**Evidence:** mutator শুধু verb rename করে না, **পুরো request ও response contract** target verb-এ সরায় (`T/specmut.py:194–200`)। Checker original verb অনুপস্থিত হলে early-return `UNDOCUMENTED_OPERATION` দেয়; replay-তে এটি যথার্থ। Fresh target verb-এ operation পাওয়া গেলে checker status, response content/schema/parse ও request validity সবই পরীক্ষা করে (`T/conformance.py:427–471`; `T/attribute.py:27–32`)।

Synthetic `GET → POST` case-এ inherited integer request/response schema রেখে POST-এর 200 response-এ string দিলে **RESPONSE_SCHEMA ও INVALID_ACCEPTED NEW** হয়। আলাদা case-এ inherited JSON media-এর বদলে text response-এ **RESPONSE_CONTENT_TYPE NEW** হয়। এগুলো বর্তমান METHOD whitelist-এ নেই (`P/fuzzer_compare.py:36`; `S/mechanisms.json`, `cases[case=method_response_and_request_contract]`, `cases[case=method_documented_error_and_bad_response_media]`)। ⚠️ একটি target-method handler ভিন্ন contract অনুসরণ করলে এমন mismatch wrong-method specification-এর সরাসরি প্রকাশও হতে পারে; শুধু kind দিয়ে collateral বলা যায় না। Synthetic response-গুলো checker/mutator mechanism পরীক্ষা করে; কোনো বাস্তব SUT execution বা বর্তমান corpus-এ এই causal scenario ঘটেছে—এমন দাবি নয়।

**Suggested fix:** বর্তমান pre-specified mapping ও তার totals সংরক্ষণ করুন, কিন্তু METHOD-এর metric-কে **selected/canonical expected-kind signal** বলুন। Replay-এর old-verb `UNDOCUMENTED_OPERATION` ও fresh-এর target-verb contract mismatch আলাদা ব্যাখ্যা করুন। সম্পূর্ণ method-contract coverage চাইলে outcome না দেখে response/request mismatch-এর secondary mechanism-compatible set সংজ্ঞায়িত করুন; নতুন mapping version দিয়ে পুনর্গণনা হবে। শুধু বর্তমান ফল বাড়াতে whitelist প্রসারিত করা উচিত নয়।

### F3 — P2: expected-kind filter causal adjudication নয়; complement-কে স্বয়ংক্রিয়ভাবে collateral বলা অতিরিক্ত দাবি

**Evidence:** code comment বলে যেকোনো অন্য kind “collateral”; doc heading-এ “collateral exposure বাদ” বলা আছে (`P/fuzzer_compare.py:29–36`; `P/strict_ablation_kinds.py:2–4`; `P/FUZZER_COMPARE.md:87–109`; `P/NOISE_FLOOR_SPEC.md:56–70`)। অথচ `counts()` শুধু NEW-এর kind membership পরীক্ষা করে—edited constraint identity, একই exchange-এর original-spec validity বা source-level cause পরীক্ষা করে না (`P/fuzzer_compare.py:64–73`)। Fresh attribution নিজেও `NEEDS_MANUAL` রাখে (`T/attribute.py:34–39`)। Cross-seed baseline-only comparisons-এও expected kinds পাওয়া সম্ভব, যা reference subtraction-এর প্রয়োজনের সঙ্গেই সামঞ্জস্যপূর্ণ (`P/fuzzer_noise_cross_seed.py:59–75`)।

Kind-level set causal অর্থে over-inclusive-ও হতে পারে: ORACLE শুধু 5xx response entry সরায়, কিন্তু whitelist-এর UNDOCUMENTED_STATUS যেকোনো status-এর NEW-ই নেয়; fresh-এর নতুন undocumented 404 সরাসরি ওই removal-এর ফল নয়। একইভাবে STRICT-এর untouched constraint-এর INVALID_ACCEPTED-ও kind মিলে যায়। এই code-level সীমা দেখানো হয়েছে; বর্তমান totals-এ এমন row-এর প্রভাব নতুন করে মাপা হয়নি (`T/specmut.py:152–179`; `T/conformance.py:437–439,468–469`; `P/fuzzer_compare.py:72–73`)।

LOOSE-এর একটি ছোট **OpenAPI 3.1 synthetic** counterexample-এ `$ref` sibling resolution surviving `type` constraint-এর pointer `/requestBody/properties/name/type` থেকে `/requestBody/properties/name/allOf/0/type` করে। একই 200 exchange-এই `INVALID_ACCEPTED` NEW+VANISHED হয়; নতুন traffic বা নতুন implementation defect লাগে না (`T/specmut.py:57–67,141–149`; fingerprint pointer: `T/conformance.py:419–425`; `S/mechanisms.json`, `cases[case=loose_replay_identity_shift]`)। এটি `VALID_REJECTED` whitelist-এ INVALID_ACCEPTED যোগ করার যুক্তি নয়—identity artifact আলাদাভাবে ধরার উদাহরণ।

**বাস্তব LOOSE যাচাই:** supervisor-এর resume note/Claude board line-কে প্রমাণ হিসেবে ব্যবহার না করে সাত Schemathesis p30 scout/petstore run-এর saved fresh attribution, baseline ও fresh violation identities স্বাধীনভাবে join করেছি। Mutated-op **raw NEW=14**, কিন্তু INVALID_ACCEPTED/RESPONSE_SCHEMA **13টি**, বাকি 1টি REQUEST_UNCHECKABLE। এই 13টির **0টির** same-kind/same-op VANISHED partner আছে; same-status শর্ত দিলেও 0। Scout-এর 9টি এবং petstore-এর 1টি INVALID_ACCEPTED সব `type`; petstore-এর 3টি RESPONSE_SCHEMA হলো response required/enum। ফলে synthetic pointer-shift উদাহরণটি এই observed LOOSE ফলের explanation নয় (`P/fuzzer_compare.csv:56–58,83–86`; `S/loose_real_data.json:1–7`, `records`; প্রতিটি record-এ source analysis locator ও hash)। ⚠️ এগুলো changed traffic-এ surviving constraint failures-এর সঙ্গে সামঞ্জস্যপূর্ণ; শুধু partner না থাকা থেকে implementation-versus-spec cause চূড়ান্ত হয় না।

**Suggested fix:** “filter-এর বাইরে” এবং “trace-confirmed collateral” আলাদা শব্দে লিখুন; expected-kind match-কে mechanism-compatible signal বলুন। বর্তমান LOOSE p30 observations ও required-only HAL trace-এর সীমিত collateral interpretation রাখুন। সব future NEW-এর জন্য causal verdict, অথবা “kind filter collateral পুরো বাদ দিয়েছে”—এমন দাবি করবেন না। `34/61` causal detection rate নয়, ঘোষিত filter অনুযায়ী observed count।

### F4 — P3: কয়েকটি prose claim নতুন CSV-এর চেয়ে বেশি শক্ত বা পুরোনো

**Evidence ও suggested fixes:**

- `STRICT_ABLATION.md:50` বলে Schemathesis full-এর “সব NEW-ই INVALID_ACCEPTED”। Full s2-তে **INVALID_ACCEPTED:3; UNDOCUMENTED_STATUS:1** আছে (`P/strict_ablation_kinds.csv:3`)। লিখুন **তিন seed-এই INVALID_ACCEPTED NEW আছে**; 3/3 result সত্য, সব NEW একই kind নয়।
- `FUZZER_COMPARE.md:53,204` বলে petstore METHOD_SEM raw NEW সব/শুধু REQUEST_UNCHECKABLE। s1-এ VALID_REJECTED:1, s3-এ SERVER_ERROR:1 আছে (`P/fuzzer_compare.csv:90–92`)। “checkable threshold ছাড়ায় 0/3; expected-kind threshold ছাড়ায় 1/3”—এভাবে metric আলাদা করে লিখুন।
- `STRICT_ABLATION.md:45`-এর “যে request-গুলো `_links` বাদ দেয়, সেগুলো 2xx পায়” সর্বজনীন নয়। EvoMaster no-required contacts PUT-এর valid JSON object-এ `_links` absent অবস্থায় 200 **40/77/50**, 406 **251/321/280** আছে; আলাদা malformed JSON 500 **249/282/233**-কে absence হিসেবে ধরা হয়নি (`S/market.json`, `traffic[fuzzer=evomaster,variant=maxLength+maximum+param_required].contacts_status_by_JSON_state`)। লিখুন **NEW INVALID_ACCEPTED-সৃষ্টিকারী accepted subset-এ `_links` অনুপস্থিত**; এই সংকীর্ণ দাবিটি স্বাধীন checker-এ সত্য।

## Mapping-এর mechanism verdict

Mapping per-kind outcome দেখার আগে fixed ছিল—এটি review-এর premise হিসেবে রাখা হয়েছে; temporal ordering নতুন করে স্বাধীনভাবে প্রমাণ করিনি। Mapping-কে outcome অনুযায়ী বিচার করিনি (`09_collab/tasks/T39.md:13`; mapping declaration `P/fuzzer_compare.py:29–37`)।

| Fault | Mechanism থেকে প্রত্যাশা | Review |
|---|---|---|
| REQUEST_LOOSE | Request bound/format/required বাদ গেলে আগে-invalid request valid হতে পারে; 400/422 পেলে VALID_REJECTED NEW | Direct monotone effect-এর জন্য যথাযথ। Fresh-এ অন্য negative traffic surviving constraint ভেঙে INVALID_ACCEPTED/response failure আনতে পারে; general identity-artifact caveat F3। |
| REQUEST_STRICT | নতুন maximum/maxLength/required লঙ্ঘন করে 2xx পেলে INVALID_ACCEPTED | যথাযথ canonical kind। নতুন schema unsatisfiable হলে signal না-ও হতে পারে; rejection বা 500 এই checker-এ INVALID_ACCEPTED নয়। |
| RESPONSE_ORACLE | 2xx response schema tightening → RESPONSE_SCHEMA; 5xx response entry removal → UNDOCUMENTED_STATUS, fallback না থাকলে | যথাযথ। SERVER_ERROR যোগ করার দরকার নেই: একই 500-তে baseline-এই SERVER_ERROR আছে। |
| METHOD_SEM | Replay old verb → UNDOCUMENTED_OPERATION; fresh target verb-এ undocumented response status বা valid rejected request → UNDOCUMENTED_STATUS/VALID_REJECTED | তিনটি justified, কিন্তু fresh target-method contract mismatches-এর পূর্ণ set নয়; F2। |

[Evidence: `T/specmut.py:141–200`; `T/conformance.py:237–245,427–471`; `S/mechanisms.json`, আটটি case, চার fault-class group।]

ORACLE spot check-এ documented 500-এর **SERVER_ERROR PERSISTENT**, **UNDOCUMENTED_STATUS NEW**; response schema tightening-এ RESPONSE_SCHEMA NEW। `default` response থাকলে removed explicit 500 fallback-এ covered থাকে এবং কোনো NEW হয় না। তাই “5xx removal সবসময় signal দেয়” বলাও ঠিক হবে না (`S/mechanisms.json`, `cases[case=oracle_500_and_response_schema]`, `cases[case=oracle_default_covers_removed_500]`; `T/conformance.py:237–245`)।

## স্বাধীন CSV recount ও noise-floor equivalence

Recount scripts কোনো production analysis module import করেনি। `recount.py` স্বাধীনভাবে kind strings যোগ করেছে, threshold inequality পরীক্ষা করেছে, cross-seed CSV-এর source columns join করেছে, unique-cell earliest-run pairing ও manifest equality পুনর্গঠন করেছে। **109 compare, 109 cross-seed, 46 pair-instance; 2971 checks PASS** (`S/recount.py`; `S/recount.json:2–35`, `checks`)।

| Comparison | Checkable EvoMaster / Schemathesis | Expected-kind EvoMaster / Schemathesis |
|---|---|---|
| Primary controlled | 20/26 / 19/26 | **20/26 / 20/26** |
| Primary manifest-differs | 13/19 / 11/19 | **10/19 / 8/19** |
| All pair-instances controlled | 20/26 / 19/26 | 20/26 / 20/26 |
| All pair-instances manifest-differs | 13/20 / 11/20 | 10/20 / 8/20 |

[Evidence: `S/recount.json:7–35`; production joins/filter `P/fuzzer_noise_cross_seed.py:62–75`, `P/fuzzer_controlled_cells.py:31–47`; totals log `09_collab/logs/kindfilter/fuzzer_controlled_cells.log`, PRIMARY/SECONDARY sections।] Signal আর reference-এ একই expected set ব্যবহারে বা exported `*_kinds` join-এ mismatch পাইনি। Subset counts বনাম subset reference দুটোই বদলায়; তাই checkable 19/26 থেকে expected 20/26 হওয়া arithmetic contradiction নয় (`P/FUZZER_COMPARE.md:98–99`; `S/recount.json:8–13`)।

পুরোনো CSV-এর দেওয়া `/tmp/claude-1000/.../scratchpad/noise_floor_spec_before.csv` readable ছিল; fallback `git show` লাগেনি। **61 run ID হুবহু এক**, শুধু সংখ্যা নয়; সব পুরোনো column-এর প্রতিটি cell-ও একই। Metadata থেকে ablation batch বাদ দিয়ে baseline replicate selector পুনর্গঠন করেও একই 61 selected run ও প্রতি run-এর পুরোনো `n_replicates` মেলে (`S/recount.json:37–75`; `S/recount.py`, old CSV comparison ও metadata selector; production exclusion `P/noise_floor_spec.py:78–100`)।

| LOOSE | Raw NEW > noise | Expected-kind NEW > noise |
|---|---|---|
| cwa | 3/3 | 3/3 |
| scout | 5/6 | 3/6; সফলগুলো p100 |
| petstore | 6/7 | 0/7 |
| market | 1/9 | 0/9 |
| মোট | 15/25 | **6/25** |

সব fault মিলিয়ে **45/61 raw → 44/61 checkable → 34/61 expected**। Addendum-এর totals ও LOOSE breakdown মেলে (`P/NOISE_FLOOR_SPEC.md:74–92`; `S/recount.json:42–72`)। এটি CSV-level স্বাধীন recount; সব baseline-এর raw capture থেকে নতুন করে noise fingerprints চালানো হয়নি। তাই exported reference maxima-র প্রতিটি raw provenance পুনঃপরীক্ষিত—এমন দাবি করছি না।

## Ablation selection, traffic ও HAL evidence

18 selected mutated run = দুই fuzzer × তিন variant × তিন seed। প্রতিটিতে variant `run.json.strict_keywords` থেকেই এসেছে; paired baseline `analysis-*/inputs.txt`-এর একই baseline, একই seed/fuzzer/batch, complete ও empty `strict_keywords`; দুটি complete same-batch cross-seed peer আছে। Paired run/baseline-এর checked source/JAR/images/config/auth-fixture digest/budget/checks/tools/harness metadata মেলে। একাধিক inputs file থেকে conflicting baseline পাইনি। Aborted EvoMaster attempt এই selected set-এ নেই (`S/recount.json`, `ablation.variant_counts`, `ablation.metadata`; `S/recount.py`; selector `P/strict_ablation.py:36–38,64–85`)। এটি within-pair check; F1-এর cross-variant drift আলাদা।

`traffic()`-এর regex-এর বদলে স্বাধীন `conformance.Spec.match()` দিয়ে template এবং verb মিলিয়ে **18/18 row-এর mutated-op 2xx/4xx/5xx counts** পুনরুৎপাদন হয়েছে (`S/raw_audit.py`, `market_audit`; `S/market.json`, `traffic`; production `P/strict_ablation.py:41–58`)। Regex-এ literal escaping/trailing slash/server base নেই; বর্তমান market corpus-এ count error পাওয়া যায়নি। ভবিষ্যৎ reuse-এ checker-এর route matcher ব্যবহার করা ভালো (`T/conformance.py:196–226`)।

`contacts_put_with_links` হলো whole-run contacts PUT diagnostic, mutated-op-only metric নয়; এটি JSON parse না করে body-text substring খোঁজে (`P/strict_ablation.py:53–57`)। তাই seed 2-এর cart mutation ব্যাখ্যায় contacts count যথেষ্ট নয়। EvoMaster full/required/no-required-এর textual counts যথাক্রমে **2100/2298/1370**, কিন্তু সম্পূর্ণ JSON parse করে top-level `_links` উপস্থিত counts **1050/1127/982**; বাকি **1050/1171/388** body malformed JSON, capture truncation নয়। এগুলোকে `_links` অনুপস্থিত বলা যাবে না। প্রত্যেক textual-match response-এই HAL `Expected relation name` marker মিলেছে, ফলে এই corpus-এ textual diagnostic-এর HAL-path interpretation সমর্থিত; “valid JSON member count” হিসেবে label করা উচিত নয় (`S/market.json`, সংশ্লিষ্ট `traffic[].diagnostic_errors`, `JSON_links`, `CSV_links`)।

Required-only-এর তিন নির্বাচিত example নিচে। Prefix `A` = `R/market/20261115T025622Z_batch_1086844_mutated_REQUEST_STRICT_p30_`। প্রতিটিতে status 500, request-এ array `_links`, response-এ DTO reference-chain, এবং saved compose trace-এ HAL deserializer + `JsonParseException: Expected relation name` মেলে (`S/market.json`, `HAL_examples`)।

| Seed/run | Exchange locator | Operation / DTO | compose.log locator |
|---|---|---|---|
| `A` + `s1` | `exchanges.jsonl:66` | PUT `/customer/contacts`, ContactsDTO | handler 409; DTO 410; JsonParseException 514 |
| `A` + `s2` | `exchanges.jsonl:18` | PUT `/customer/cart`, CartItemDTO | handler 273; DTO 276; JsonParseException 406 |
| `A` + `s3` | `exchanges.jsonl:51` | PUT `/customer/contacts`, ContactsDTO | handler 531; DTO 532; JsonParseException 636 |

প্রতিটি seed-এ দুটি occurrences থেকে একই দুই NEW fingerprint—SERVER_ERROR ও UNDOCUMENTED_STATUS—তৈরি হয়েছে; এগুলো দুটি স্বতন্ত্র defect নয় (`P/strict_ablation_kinds.csv:11–13`; `S/raw_audit.py`, required-new fingerprint/index join)। ⚠️ Saved trace অনুযায়ী observed required-only NEW-গুলো HAL-path collateral exposure হিসেবে পড়া সমর্থিত; source defect নতুন করে mutation তৈরি করেছে—এমন প্রমাণ নয়। এক SUT/n=3 থেকে সাধারণ causal rate অনুমানও নয়।

EvoMaster no-required-এর তিন ছোট market run-এ current checker স্বাধীনভাবে চালিয়ে সব NEW INVALID_ACCEPTED fingerprint মিলিয়েছি। Seeds 1/2/3-এ fingerprints **2/0/2**, violation occurrences **60/0/74**; সবই **PUT `/customer/contacts`, status 200, parsed body-তে `_links` absent**, phone/address `maxLength`। Seed 1-এ phone/address occurrences 40/20, seed 3-এ 50/24। একই request দুই constraint ভাঙতে পারে; 60/74 distinct request count নয় (`S/market.json`, `evo_noreq`; `S/raw_audit.py`, `ia_occurrences`, `ia_fps`; `P/strict_ablation_kinds.csv:17–19`)। ফলে no-required INVALID_ACCEPTED-এর সংকীর্ণ provenance claim সত্য।

## সীমা, প্রক্রিয়া ও artifacts

`STRICT_ABLATION.md:56–59`-এ single SUT, n=3, এক budget, different-day/batch baselines ও observed-max reference সতর্কতা যথাযথ। এগুলো রাখুন; F1-এর settings difference আরও যোগ করতে হবে। ⚠️ EvoMaster-এর 0/3→2/3 result T35-এর mechanism-এর সঙ্গে সামঞ্জস্যপূর্ণ, তবে different batches ও মাত্র তিন seed থেকে isolated effect size/general superiority বলা যায় না। Pooled controlled 26 cell-ও 26 independent seed replicate নয় (`P/FUZZER_COMPARE.md:43,232–236`; `P/STRICT_ABLATION.md:42–59`)।

প্রক্রিয়াগত সীমা প্রকাশ: pause-এর আগের এক metadata probe প্রতি seed-এ প্রথমটির পাশাপাশি duplicate দ্বিতীয় 500-এর summary-ও emit করেছিল—**মোট ছয় exchange locator**, user-এর ≤3 spot-check ceiling অতিক্রম হয়েছিল। Report-এ তিনটি representative example রাখা হয়েছে; অতিরিক্ত raw-body/header dump করা হয়নি। পরে market aggregates ও saved attribution join করা হয়েছে। LOOSE pointer-shift synthetic result দিয়ে বাস্তব corpus-এর ব্যাখ্যা দেওয়া হয়নি; resume note-এর দাবিও স্বাধীনভাবে যাচাই করা হয়েছে (`S/loose_real_data.json`)।

Artifacts: `S/recount.py`/`recount.json` (CSV ও metadata); `S/mechanisms.py`/`mechanisms.json` (চার fault-class synthetic group); `S/raw_audit.py`, `S/market.json`, `S/loose_real_data.json` (market aggregates, তিন representative trace locator, saved LOOSE pairing)। সব Python execution `/usr/bin/python3 -I -B`, offline; কোনো Docker/Java/Maven/network বা external project code execution হয়নি। Production script/CSV/doc/tool/harness/run edit করা হয়নি। খোলা প্রশ্ন: METHOD fresh metric-এর desired coverage এবং matching-settings Schemathesis ablation পুনরায় চালানোর সিদ্ধান্ত coordinator/supervisor-এর; এই review-তে নতুন experiment চালানো হয়নি।
