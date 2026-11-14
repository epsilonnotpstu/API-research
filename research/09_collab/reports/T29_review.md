# T29 — fuzzer comparison review

তারিখ: 2026-11-15। Review only; implementation, CSV ও মূল doc সংশোধন করা হয়নি। এই report-এ `P/` = `08_experiments/E1_pilot/pilot_results/`, `R/` = `08_experiments/E1_pilot/runs/`, `S/` = `09_collab/logs/T29_scratch/`। এগুলো নিচের evidence locator-এর path prefix।

**ফল:** detection table-এর সব 26টি অনুপাত, বন্ধনীর p100 ফলসহ, পুনরুৎপাদিত হয়েছে; matched-cell totals **23/33 ও 23/34 সঠিক**। তবে এগুলো বর্তমান raw-fingerprint threshold-এর হিসাব। Cross-seed ফলকে নিশ্চিত upper bound, দুই fuzzer-কে একই mutations-এর comparison, এবং সমস্ত NEW-কে fault detection বলা সমর্থিত নয়। ছয়টি finding নিচে দেওয়া হলো। Evidence: `S/recount.py:143–170`, `S/recount.json:255–264`, `P/FUZZER_COMPARE.md:14–37`; বিস্তারিত F1–F6।

## Findings

### F1 — P1: Cross-seed maximum, same-input noise-এর upper bound নয়

**Evidence:** `P/fuzzer_noise_cross_seed.py:9–10` এবং `P/FUZZER_COMPARE.md:14–18,68` অন্য seed-এ traffic বেশি আলাদা হবে ধরে তাকে conservative upper bound বলেছে। কিন্তু একই saved corpus-এ petstore REQUEST_STRICT s3-এর **same-seed max NEW=3**, cross-seed max **0** (`P/noise_floor_spec.csv:59`; `P/fuzzer_noise_cross_seed.csv:83`)। RESPONSE_ORACLE s3-তেও যথাক্রমে **1 ও 0** (`P/noise_floor_spec.csv:62`; `P/fuzzer_noise_cross_seed.csv:86`)। Independent join আরও দুই scout counterexample পেয়েছে (`S/noise_counterexamples.json:1`; join: `S/recount.py:170`)। Same-input replicate provenance-এর পূর্বের বিবরণ আছে `P/NOISE_FLOOR_SPEC.md:6–17,53–55`-এ; এই review-তে সেই replicate-গুলোর raw traffic আবার scan করা হয়নি।

NEW হলো directional set difference, traffic distance নয় (`08_experiments/tools/attribute.py:24–39`)। বেশি traffic difference থেকে বেশি NEW হওয়ার নিশ্চয়তা নেই। একই batch-এর সর্বোচ্চ দুই peer-ও population upper bound বা error rate নির্ধারণ করে না (`P/fuzzer_noise_cross_seed.py:55–70`)।

**Suggested fix:** “observed cross-seed reference maximum” বলুন। `beyond_noise_NEW`-এর অর্থ রাখুন “এই finite sample-এর maximum-এর চেয়ে বেশি”; statistical significance বা same-input noise অতিক্রমের প্রমাণ বলবেন না। Schemathesis-এর same-seed ফল আলাদা দিন; EvoMaster-এর same-seed replicate ছাড়া তার upper-bound দাবি প্রত্যাহার করুন। ⚠️ Same-seed EvoMaster noise-এর প্রকৃত মাত্রা বর্তমান data থেকে অজানা।

### F2 — P1: Matched cells-এর mutations প্রায়ই এক নয়; fuzzer comparison-এ confounding আছে

**Evidence:** doc-এর title “একই spec mutation” এবং “পরিপূরক” inference (`P/FUZZER_COMPARE.md:1,37,47,53–55`) case matching-এর চেয়ে শক্ত দাবি। Independent manifest comparison-এ p30/seed-matched METHOD_SEM **9/9**, STRICT **9/9** mutations এক; LOOSE **0/7**, ORACLE **2/9** এক। LOOSE-এর সাতটি comparison-এ petstore s1-এর দুই batch অন্তর্ভুক্ত (`S/recount.json`, `manifest_matching`; `S/manifest_pairs.json:1`; code `S/recount.py:137–152`)।

নির্দিষ্ট উদাহরণ: cwa ORACLE s1-এ Schemathesis mutation হলো `POST /version/v1/tan/teletan`, EvoMaster mutation `POST /version/v1/testresult`:

- `R/cwa-verification/20261114T103253Z_batch_321562_mutated_RESPONSE_ORACLE_p30_s1/manifest.json:8–24`;
- `R/cwa-verification/20261114T200712Z_batch_962064_mutated_RESPONSE_ORACLE_p30_s1/manifest.json:8–24`।

Baseline-dependent ORACLE pool harness-এই নির্ধারিত (`08_experiments/E1_pilot/harness_v2/run_batch.sh:45–58`)। প্রতিটি run-এর **নিজের** manifest attribution-এ সঠিকভাবে দেওয়া হয়েছে (`P/fuzzer_compare.py:82–88`); সমস্যা হলো ভিন্ন manifests-কে একই comparison cell-এ ধরে ব্যাখ্যা করা।

**Suggested fix:** বর্তমান totals-কে fault-class/severity-level descriptive totals বলুন এবং manifest/pool mismatch স্পষ্ট করুন। Controlled comparison-এর জন্য একই saved mutated spec/manifest দুই fuzzer-এ দিন, অথবা identical `mutations` subset আলাদা report করুন। Market STRICT-এর observed 0/3 বনাম 3/3 রাখা যায়, কারণ তার mutations মেলে; cwa ORACLE superiority ও overall complementarity-কে ⚠️ exploratory inference হিসেবে লিখুন। অতিরিক্ত petstore LOOSE s1 repeat-কে স্বাধীন চতুর্থ seed বলবেন না (`P/fuzzer_compare.csv:71–74`)।

### F3 — P2: NEW signal-এর মধ্যে checker inability আছে; “detection” নামটি অতিরিক্ত শক্ত

**Evidence:** `counts()` kind filter ছাড়াই প্রতিটি NEW গোনে (`P/fuzzer_compare.py:54–64`); checker `REQUEST_UNCHECKABLE`/`RESPONSE_UNCHECKABLE`-ও emit করে (`08_experiments/tools/conformance.py:448–467`)। Independent CURRENT-checker spot check-এ cwa LOOSE s1-এর fresh NEW=3-এর একটি `REQUEST_UNCHECKABLE`, দুটি `VALID_REJECTED` (`S/spot_check.json:8–43`)। অর্থাৎ checker inability বাস্তবেই এই metric-এ মিশেছে।

আরও একটি গুরুত্বপূর্ণ saved example: petstore METHOD_SEM Schemathesis s2-এর **একমাত্র** mapped NEW হলো `REQUEST_UNCHECKABLE`, occurrence 32 (`R/swagger-petstore/20261114T105422Z_batch_356033_mutated_METHOD_SEM_p30_s2/analysis-both/fresh.attributed.csv:11`)। Latest CSV-তেও সেই run NEW=1, noise max=0, beyond=True (`P/fuzzer_noise_cross_seed.csv:79`)। ⚠️ এই run-এর saved attribution পুরোনো checker hash-এর; চার-run সীমার কারণে current checker-এ raw rescan করা হয়নি। তাই latest NEW-টির kind একই আছে ধরে corrected 2/3 বা corrected total ঘোষণা করছি না।

এছাড়া fresh attribution ইচ্ছাকৃতভাবে `NEEDS_MANUAL` দেয়—mapped NEW মানেই injected fault-এর cause প্রতিষ্ঠিত নয় (`08_experiments/tools/attribute.py:1–7,38–50`)। বর্তমান threshold সেই causal যাচাই করে না (`P/fuzzer_noise_cross_seed.py:61–70`)।

**Suggested fix:** raw NEW-এর নাম “mapped fingerprint change” রাখুন। Fault-detection metric চাইলে uncheckable kinds আলাদা দিন, signal ও noise উভয় দিকে একই filter ব্যবহার করুন, এবং expected kind/manual attribution স্পষ্ট করুন। Latest checker-এ petstore METHOD_SEM s2 পুনরায় যাচাই করে তারপর detection table সংশোধন করুন।

### F4 — P2: “LOOSE replay NEW সবসময় 0” দাবি ভুল; replay-তেই VALID_REJECTED তৈরি হয়

**Evidence:** `P/FUZZER_COMPARE.md:60–62`-এর দাবির বিপরীতে CSV-তে **সাতটি** LOOSE row-এর replay NEW nonzero: cwa p100 seeds 1–3-এ প্রতিটিতে 2; scout p100 seeds 1–3-এ প্রতিটিতে 1; petstore p30 দ্বিতীয় s1 batch-এ 2 (`P/fuzzer_compare.csv:2–4,59–61,72`; independent list `S/recount.json`, `nonzero_LOOSE_replay`)।

Independent raw replay-এ cwa s1-এর **একই baseline traffic** mutated spec-এ check করে `VALID_REJECTED` NEW=2, occurrences **9 ও 5**, পুনরুৎপাদিত (`S/spot_check.json:46–72`)। Checker request-এ আর validation problem না পেলে, আগের 400/422 response-কে `VALID_REJECTED` বলে (`08_experiments/tools/conformance.py:465–471`)। Request loosening সেই পরিবর্তন baseline replay-তেও ঘটাতে পারে; fresh-only mechanism নয়।

**Suggested fix:** “সবসময় 0” ও “শুধু fresh” বাদ দিন; observed nonzero rows উল্লেখ করুন। ব্যাখ্যায় বলুন: loosened spec-এ valid হওয়া request-কে SUT reject করলে এই kind আসে। Doc-এর “SUT loosened constraint মানলেও” কথাটিও এই rejection mechanism অনুযায়ী সংশোধন করুন।

### F5 — P2: Noise extrema doc-এ ভুল

**Evidence:** `P/FUZZER_COMPARE.md:49–50` বলে EvoMaster petstore mapped NEW noise সর্বোচ্চ **1**, Schemathesis সর্বোচ্চ প্রায় **1.7**, scout-এ। Actual:

- EvoMaster petstore ORACLE s2: `noise_max_mut_NEW=2`, `noise_mean_mut_NEW=2.0` (`P/fuzzer_noise_cross_seed.csv:97`)। Market ও cwa-এর 0 দাবিটি মেলে।
- Schemathesis: maximum `noise_max_mut_NEW=3`; maximum per-row `noise_mean_mut_NEW=2.5`, scout LOOSE p100 s1-এ (`P/fuzzer_noise_cross_seed.csv:59`)। Scout STRICT s1-তেও max=3 (`P/fuzzer_noise_cross_seed.csv:65`)।

Independent extrema: `S/recount.json`, `noise_extrema`; calculation `S/recount.py:181–183`। এটি max বনাম mean বদলালেও doc-এর 1/1.7 উদ্ধারের উপায় নয়।

**Suggested fix:** maximum-of-pair counts এবং maximum-of-row means আলাদা নামে CSV থেকে generate করুন। সংখ্যা যথাক্রমে EvoMaster **2/2.0**, Schemathesis **3/2.5** লিখুন।

### F6 — P2: “নতুন violation মানে baseline-এ ওই input ছিলই না”—inference প্রতিষ্ঠিত নয়

**Evidence:** `P/FUZZER_COMPARE.md:63`-এ cwa STRICT s2 fresh NEW=2, replay NEW=0 থেকে baseline input অনুপস্থিত বলা হয়েছে। CSV-র **2/0 সঠিক** (`P/fuzzer_compare.csv:21`), কিন্তু `attribute()` শুধু fingerprint counts তুলনা করে; request input বা sequence তুলনা করে না (`08_experiments/tools/attribute.py:24–27,35–53`)। Fingerprint-এ HTTP status, kind, schema pointer আছে; সম্পূর্ণ input নেই (`08_experiments/tools/conformance.py:419–425`)। একই input হলেও response/state/status আলাদা হলে fingerprint বদলাতে পারে। ⚠️ এই সম্ভাবনাগুলো current CSV পৃথক করতে পারে না।

**Suggested fix:** “baseline replay-তে ওই violation দেখা যায়নি” বলুন। Input অনুপস্থিতির দাবিকে ⚠️ hypothesis রাখুন এবং raw request/body + response + sequence comparison ছাড়া নিশ্চিত করবেন না। Market STRICT-এর spec-following explanation-এ ⚠️ আছে (`P/FUZZER_COMPARE.md:57–58`); সেখানেও causal বাক্যের শুরুতেই inference marker দিন।

## Pairing, classification ও semantics যাচাই

`S/recount.py` target scripts import না করে CSV recount এবং সব selected run-এর metadata/spec/manifest audit করে। মোট **97 row = 36 EvoMaster + 61 Schemathesis**, compare/noise দুটিতেই; duplicate run নেই। সব 97-এর copied fields এবং `fresh_mut_NEW > noise_max_mut_NEW` boolean মেলে (`S/recount.json:1`; `S/recount.py:44–54,84–135`)।

- **Baseline:** সব eligible `analysis-*/inputs.txt` একই baseline-এ নির্দেশ করে; 94 run-এ শুধু `analysis-both`, তিনটিতে `analysis-both` ও `analysis-both-default` একই pair। Baseline complete/mode/seed/SUT/fuzzer এবং paired image/JAR/auth/budget/tool/harness metadata checks pass। প্রতিটি spec glob-এ একটিমাত্র file; baseline `spec.original`, baseline `spec.test`, mutated run-এর `spec.original` hash এক। Mutated spec ও manifest metadata hashes মেলে (`S/provenance.json`, selected run id; assertions `S/recount.py:89–115`)। অতএব CURRENT corpus-এ `inputs[0]` থেকে ভুল pair পাওয়ার evidence নেই।
- **`-sut` exclusion:** custom rejection oracle-এর metrics-এর সঙ্গে default 400/422 মিশ্রণ এড়ানো সঠিক; default oracle checker default-ই (`08_experiments/E1_pilot/harness_v2/analyse_run.sh:61–65`; `08_experiments/tools/conformance.py:182–186`)। Pair নির্বাচন আর oracle পুনরায় check করা আলাদা কাজ; বাদ দেওয়াটা একমাত্র pairing correctness gate নয়। বর্তমান eligible alternatives-এ ambiguity নেই (`S/provenance.json`)।
- **Fresh/replay specs:** baseline/base spec; mutated traffic/mutated spec; replay baseline traffic/mutated spec—সঠিক (`P/fuzzer_compare.py:83–88`)। Manifest METHOD_SEM-এ old ও replacement method দুটোই stratum হিসেবে ধরা হয় (`08_experiments/tools/attribute.py:28–33`)। `mutated_ops=len(mutations)` original mutation entries-এর সংখ্যা, দুই method মিলে mapped keys-এর সংখ্যা নয় (`P/fuzzer_compare.py:90`)।
- **Classification:** স্বাধীন exact-token argv parsing-এ selected 61 Schemathesis run-এর সবগুলো `--data-generation-method all`; 36 EvoMaster `run.json` দিয়ে চিহ্নিত। বর্তমান inclusion-এ misclassification পাওয়া যায়নি (`S/recount.py:28–40,89`; `S/recount.json`, selected_classifications)। দুই complete negative-data run-এর analysis inputs নেই, তাই বাদ গেছে: `20261114T081833Z_batch_109065_mutated_REQUEST_LOOSE_p30_s1`, `20261114T082035Z_batch_111783_mutated_REQUEST_LOOSE_p30_s1` (`S/provenance.json`, excluded run id)। এগুলো verified pair ছাড়া নিজে থেকে যোগ করা উচিত নয়; coverage-এ “paired analyses available” শর্ত লিখুন। Positive-only ও incomplete run বাদ পড়া scope অনুযায়ী সঠিক (`P/fuzzer_compare.py:30–36,73–81`; inventory `S/provenance.json`)।
- **Same-batch peers:** CURRENT rows-এ নামের batch prefix দিয়ে পাওয়া peer-এর seed আলাদা; spec, fuzzer এবং execution metadata মেলে। 96 row-এ দুই peer; পুরোনো petstore LOOSE s1 row-তে এক complete peer (`P/fuzzer_noise_cross_seed.csv:71`; audit `S/provenance.json`)। আলাদা fuzzer/configuration একসঙ্গে noise হিসেবে নেওয়ার চেয়ে batch restriction যথাযথ; এটি F1-এর upper-bound দাবি প্রতিষ্ঠা করে না।
- **`counts()`:** NEW হলো baseline-এ অনুপস্থিত fingerprint; INCREASED/DECREASED শুধু PERSISTENT fingerprint-এর occurrence তুলনা, occurrence delta-র যোগফল নয়। `attribute.py` এবং `noise_floor_spec.py`-এর shared metrics-এর সঙ্গে মেলে। পার্থক্য: নতুন script **VANISHED বাদ দেয়**, পুরোনো script আলাদা VANISHED counter রাখে; VANISHED-কে DECREASED ধরা হয় না (`P/fuzzer_compare.py:54–64`; `P/noise_floor_spec.py:53–63`; `08_experiments/tools/attribute.py:38–53`; synthetic evidence `S/semantics_check.json:1`)। তাই `replay_unmut_changes=0`-কে সব ধরনের পরিবর্তন অনুপস্থিত বলা যাবে না: এই column-এ VANISHED নেই (`P/fuzzer_compare.py:95`)।

## Table recount

Detection table-এর 26টি ratio programmatically parse করে CSV grouping-এর সঙ্গে assert করা হয়েছে (`S/recount.py:153–169`)। Cwa LOOSE বাদ দিয়ে p30-তে totals **EvoMaster 23/33**, **Schemathesis 23/34**; Schemathesis-এর denominator-এ petstore LOOSE s1 repeat আছে (`S/recount.json:255–264`; `P/fuzzer_compare.csv:71–74`)। Severity না মিশিয়ে এই হিসাব করা জরুরি: comparison script-এর stdout summary-তে severity group key নেই, যদিও CSV-তে আছে (`P/fuzzer_compare.py:104–115`)।

Traffic table-এর approximate সংখ্যাগুলো fault/severity cell mean বা all-row mean থেকে ব্যাখ্যা করা যায়। নিচে প্রতিটি SUT/fuzzer-এর all-row mean এবং cell-mean range দেওয়া হলো; এগুলো একক সংজ্ঞা নয়—doc-এ কোনটি ব্যবহার করা হয়েছে লিখলে পুনরুৎপাদন সহজ হবে (`P/FUZZER_COMPARE.md:39–45`; `S/recount.json:265–382`)।

| SUT | EvoMaster all-row mean; cell-mean range | Schemathesis all-row mean; cell-mean range |
|---|---|---|
| petstore | 73,051.17; 69,741.67–76,554.33 | 1,583.06; 1,575–1,607 |
| market | 4,236.67; 4,172–4,310.67 | 1,176.50; 1,149.67–1,202 |
| cwa | 9,741.33; 5,025–22,209 | 352.08; 344–365 |

Petstore-এর doc `~70–76k` হলো approximate cell-mean range; nearest-thousand rounding-এ **~70–77k** হবে। Cwa `5–22k` individual-run range নয়: individual max **56,546**, METHOD_SEM s3 (`P/fuzzer_compare.csv:16`)। “4–60 গুণ” descriptive approximation; exact rate/efficiency estimate হিসেবে ব্যবহার না করে aggregation লিখুন (`P/FUZZER_COMPARE.md:47`; উপরের mean/range)। Detection table-এ arithmetic mismatch নেই; অন্যান্য সংখ্যাগত ভুল F4/F5-এ।

## Cache, validation ও সীমা

Cache থেকে CURRENT immutable corpus-এ ভুল result হওয়ার evidence পাইনি। Compare cache key `(run,spec_path)`; `cache=False` পুরোনো entry return/store করে না, baseline-এর জন্য bounded cache রাখে—সর্বোচ্চ **5 entries**। Noise cache run-পিছু original-spec result রাখে, সর্বোচ্চ **7 entries** (`P/fuzzer_compare.py:39–51`; `P/fuzzer_noise_cross_seed.py:31–40`)। `attribute()` cached violation dict mutate করে না (`08_experiments/tools/attribute.py:24–53`)। Fake-exchange checks-এ bypass equality, repeated cache hit, eviction bounds ও input non-mutation pass (`S/semantics_check.py:25–70`; `S/semantics_check.json:1`)।

⚠️ Entry count bounded হলেও bytes bounded নয়: প্রতিটি cache value পূর্ণ violation list; বড় response/error volume-এ memory চাপ/OOM হতে পারে। Run/spec contents বা checker globals একই process-এ বদলালে cache invalidation নেই। Normal one-shot execution-এ INT_FORMATS loop-এর আগেই True এবং checker defaults অপরিবর্তিত, তাই এই stale-policy risk observed failure নয় (`P/fuzzer_compare.py:68–69`; `P/fuzzer_noise_cross_seed.py:44–45`)। ভবিষ্যৎ robustness-এর জন্য immutable input/policy hash, baseline agreement assertion, exact argv token/value parsing ও atomic output publication উপযোগী; এগুলোর অভাবে CURRENT CSV ভুল হয়েছে এমন দাবি করছি না।

চালানো হয়েছে শুধুই নিজস্ব offline Python, `/usr/bin/python3 -I -B` দিয়ে:

1. `09_collab/logs/T29_scratch/recount.py` — independent CSV/doc/provenance/manifest recount; PASS।
2. `09_collab/logs/T29_scratch/spot_check.py` — **চারটি unique raw run**; cwa fresh NEW/INC=3/1, replay NEW=2, এক cross-seed pair NEW/INC=0/4; market EvoMaster STRICT baseline replay NEW=5; asserted metrics PASS (`S/spot_check.json:1–88`)।
3. `09_collab/logs/T29_scratch/semantics_check.py` — synthetic semantics/cache checks; PASS (`S/semantics_check.json:1`)।

Reviewed source/doc/CSV hashes এবং scanned exchange hashes checks-এর আগে-পরে মেলানো হয়েছে (`S/reviewed_hashes.json:1`; `S/spot_check.json`, read_only_exchange_hashes)। Full 97-run checker rerun করা হয়নি; saved older attributions-এর সীমা F3-তে বলা আছে। Scout running batch read-only ছিল। Docker/Java/Maven/network/external code execution হয়নি। Deliverables ও write boundary: `09_collab/tasks/T29.md:25–37`।
