# Schemathesis বনাম EvoMaster: spec mutation-এ mapped fingerprint পরিবর্তন (2026-11-15, Claude; T29 আর T34 review-এর পর সংশোধিত, scout আর same-seed reference যোগ করা হয়েছে)

**Scripts** (সব offline; বিদ্যমান run বর্তমান checker দিয়ে আবার check করা — int format চালু, default oracle 400/422):
1. `fuzzer_compare.py` → `fuzzer_compare.csv`
2. `fuzzer_noise_cross_seed.py` → `fuzzer_noise_cross_seed.csv`
3. `fuzzer_controlled_cells.py` → `fuzzer_controlled_cells.csv`
4. `fuzzer_noise_same_seed.py` → `fuzzer_noise_same_seed.csv`
5. `fuzzer_trajectory_overlap.py` → `fuzzer_trajectory_overlap.csv`
6. `schemathesis_replicate_overlap.py` → `schemathesis_replicate_overlap.csv`

**Review:**
- Codex T29 (`09_collab/reports/T29_review.md`) script 1–2 দেখেছে। ৬টি finding-ই গ্রহণ করা হয়েছে।
- Codex T34 (`09_collab/reports/T34_review.md`) script 3–5 দেখেছে। ৫টি finding-ই গ্রহণ করা হয়েছে (F1 P1; F2–F5 P2)।
  - স্বাধীন recount সব total পুনরুৎপাদন করেছে।
  - নিচের সংখ্যা সংশোধনের পরের।
- Run log: `09_collab/logs/T34_scratch/claude_rerun_*.log`; সংশোধনের আগের log `claude_run_*.log`।
- Script 6 (`schemathesis_replicate_overlap.py`) T34 launch-এর পরে লেখা, তাই review হয়নি।

## Run
- **EvoMaster v6.2.0 black-box** (T27 harness):
  - budget 300 s, `--schemaOracles true`।
  - প্রতিটি SUT-এ baseline + 4 fault × seed 1–3, SEVERITY 30, ORACLE_POOL=baseline, LOOSE_POOL=spec। প্রতিটিতে 12টি mutated run, সবগুলো `complete`।
  - Generator input: petstore, market আর cwa-তে মূল `spec.test.json`; scout-এ derecursed (§Scout)।
- **EvoMaster same-seed replicate:**
  - প্রতিটি SUT-এ baseline-only batch (`FAULTS=" "`), seed 1–3, মূল batch-এর মতো একই settings।
  - মোট 12টি baseline, সবগুলো exit 0।
- **Schemathesis:** বিদ্যমান `DATA_GEN=all` run, max-examples 100।
  - REQUEST_LOOSE-এর কিছু run p100।
  - petstore LOOSE p30 s1 দুটো আলাদা batch-এ আছে। ওই অতিরিক্ত repeat-টা স্বাধীন চতুর্থ seed নয়।

## মাপকাঠি
- **সংকেত:** mutated op-এ fresh NEW fingerprint। এটা "mapped fingerprint পরিবর্তন", fault detection-এর প্রমাণ নয়।
  - Fresh attribution সব NEW-কে `NEEDS_MANUAL` দেয়। Cause প্রতিষ্ঠার জন্য labelling দরকার।
  - **`*_UNCHECKABLE` kind বাদ** (T29 F3): checker-এর অক্ষমতাকে fault-এর সংকেত ধরা হয় না। একই filter সংকেত আর reference, দুই দিকেই।
- **দুই রকম reference:** কোনোটাই upper bound নয়। "ছাড়ায়" মানে সসীম peer-সেটের maximum-এর চেয়ে বেশি; কোনো significance দাবি নেই।
  - **Cross-seed:** B (seed s) বনাম একই batch-এর অন্য seed-এর baseline B' (base spec, একই manifest)। প্রতিটি row-এ 2টি peer।
  - **Same-seed (শুধু EvoMaster):** B বনাম পরের batch-এর একই seed-এর baseline।
    - পূর্ণ provenance মিলতে হবে (T34 F5): input mode, schemaOracles, budget, argv, original/generator-input digest, SUT JAR, image ID, SUT config, auth fixture digest, timeout, EMB commit।
    - Harness drift আলাদা column-এ জানানো হয়, filter হিসেবে নয়।
      - 48 row-এর 36টিতে (petstore, market, cwa) drift: `fuzzer_args.sh`, `run_metadata.py`, `run_pilot.sh`। এগুলো T28/T31-এর knob, যোগ হয়েছে মূল batch-এর পরে।
      - Default-এ argv byte-identical (golden test)। Recorded argv-ও দুই run-এ সমান।
      - Scout-এ drift নেই।
    - প্রতিটি row-এ মাত্র **1টি** replicate। একই baseline–replicate জোড়া চার fault-এ পুনর্ব্যবহৃত, তাই 48 row মানে 48টি স্বাধীন replicate নয়। এটা **observed same-seed replicate reference**।
  - **`beyond_both`:** checkable NEW > max(cross, same), শুধু যখন দুটো reference-ই আছে। এটা দুই observed threshold-এর conjunction; কোনো test নয়।
- **Controlled ঘর (T29 F2):** একই sut × fault × severity × seed, যেখানে দুই fuzzer-এর mutation set (operation + edit) হুবহু এক (`manifest_sig`)।
  - ORACLE-এর pool baseline-নির্ভর, আর LOOSE-এর pool পুরোনো Schemathesis run-এ legacy format-নিয়মে তৈরি। তাই এই দুই fault-এ manifest প্রায়ই আলাদা।
- **সংকেতের সংজ্ঞা:** নিচের সারণিতে cross-seed reference ব্যবহার করা হয়েছে। EvoMaster-এ `beyond_both` প্রতিটি ঘরে এর সমান (§Same-seed)।

## ফল ১: Controlled ঘর (একই mutation, p30)

| SUT | Fault | EvoMaster | Schemathesis |
|---|---|---|---|
| petstore | METHOD_SEM | 3/3 | **0/3** checkable threshold-এ। raw NEW-এ বেশিরভাগ `REQUEST_UNCHECKABLE`, আর s1-এ VALID_REJECTED 1, s3-এ SERVER_ERROR 1। Expected-kind threshold-এ 1/3 (ফল ৩)। |
| petstore | REQUEST_STRICT | 3/3 | 3/3 |
| petstore | RESPONSE_ORACLE | 1/1 | 1/1 |
| market | METHOD_SEM | 3/3 | 3/3 |
| market | REQUEST_STRICT | **0/3** | 3/3 |
| cwa | METHOD_SEM | 3/3 | 3/3 |
| cwa | REQUEST_STRICT | 1/3 | 0/3 |
| cwa | RESPONSE_ORACLE | 0/1 | 0/1 |
| scout ⚠️ | METHOD_SEM | 3/3 | 3/3 |
| scout ⚠️ | REQUEST_STRICT | 3/3 | 3/3 |
| **মোট** | | **20/26** | **19/26** |
| মোট, scout বাদে | | 14/20 | 13/20 |

⚠️ Scout-এ EvoMaster-এর generator input derecursed; Schemathesis-ও derecursed input পায়। Mutation set (`manifest_sig`) দুই দিকে এক।

## ফল ২: Manifest আলাদা (শুধু বর্ণনামূলক, p30)

| SUT | Fault | EvoMaster | Schemathesis |
|---|---|---|---|
| petstore | REQUEST_LOOSE | 1/3 | 0/3 |
| petstore | RESPONSE_ORACLE | 2/2 | 2/2 |
| market | REQUEST_LOOSE | 1/3 | 1/3 |
| market | RESPONSE_ORACLE | 3/3 | 3/3 |
| cwa | RESPONSE_ORACLE | 2/2 | 1/2 |
| scout | REQUEST_LOOSE | 1/3 | 2/3 |
| scout | RESPONSE_ORACLE | 3/3 | 2/3 |
| **মোট** (unique ঘর) | | 13/19 | 11/19 |

- **Denominator (T34 F4):**
  - Primary: প্রতি ঘরে একটি জোড়া, প্রতিটি fuzzer-এর সবচেয়ে আগের run নিয়ে।
  - একমাত্র duplicate ঘর petstore LOOSE p30 s1 (দুটো Schemathesis batch)। সব pair-instance গুনলে 13/20 বনাম 11/20 (`primary` column)।
  - Controlled ঘরে কোনো duplicate নেই (26 = 26)।
- cwa REQUEST_LOOSE-এর তুলনা হয়নি: Schemathesis শুধু p100-এ আছে (সেখানে 3/3), আর EvoMaster p30-এ (2/3)।

## ফল ৩: প্রত্যাশিত-kind (canonical, mechanism-compatible) সংকেত (2026-11-15; T39-এ সংশোধিত)
- ⚠️ এটা causal adjudication নয় (T39 F3)। Filter-এর বাইরের NEW মানেই "collateral" নয়। Trace দিয়ে নিশ্চিত collateral আছে কেবল market STRICT required-only-এ (T35 HAL path)। METHOD_SEM-এর set একটা canonical subset (T39 F2)। `34/61` বা ঘরের সংখ্যাগুলো ঘোষিত filter অনুযায়ী observed count, detection rate নয়।
- **নিয়ম:** `fuzzer_compare.EXPECTED_KINDS`। এটা mechanism থেকে আগে ঠিক করা, per-kind ফল দেখার আগে।

  | Fault | প্রত্যাশিত kind |
  |---|---|
  | LOOSE | VALID_REJECTED |
  | STRICT | INVALID_ACCEPTED |
  | ORACLE | RESPONSE_SCHEMA, UNDOCUMENTED_STATUS |
  | METHOD_SEM | UNDOCUMENTED_OPERATION, UNDOCUMENTED_STATUS, VALID_REJECTED |

  Cross-seed reference-এও একই filter।
- **Controlled ঘর (primary): EvoMaster 20/26, Schemathesis 20/26।** Checkable নিয়মে ছিল 20/26 বনাম 19/26।
  - একমাত্র বদল petstore METHOD_SEM-এ Schemathesis 0/3 থেকে 1/3। s1-এ একটা VALID_REJECTED আছে, আর expected-kind reference 0।
  - বাকি সব ঘর অপরিবর্তিত।
- **Manifest আলাদা (primary): EvoMaster 10/19, Schemathesis 8/19।** Checkable নিয়মে ছিল 13/19 বনাম 11/19।
  - **REQUEST_LOOSE-এর সব ঘর 0।** petstore, market আর scout, দুই fuzzer-এই।
  - আগের LOOSE "সংকেত" filter-এর বাইরের kind ছিল: RESPONSE_SCHEMA (petstore), INVALID_ACCEPTED (scout Schemathesis), UNDOCUMENTED_STATUS আর SERVER_ERROR (market/scout EvoMaster)।
    - T39 আসল data স্বাধীনভাবে যাচাই করেছে: scout/petstore-এর 13টি NEW-এর একটিরও VANISHED partner নেই। এগুলো বদলানো negative traffic-এ টিকে থাকা constraint-এর (type/required/enum) লঙ্ঘনের সঙ্গে সঙ্গত, pointer-shift artifact নয়।
    - ⚠️ Cause (spec নাকি impl) চূড়ান্ত নয়।
  - প্রত্যাশিত VALID_REJECTED এসেছে শুধু cwa LOOSE-এ: Schemathesis p100 3/3, EvoMaster p30 2/3। cwa এই তুলনার বাইরে, কারণ severity আলাদা।
  - ORACLE অপরিবর্তিত।
- **উপসংহার:**
  - দুই fuzzer-এর তুলনা (controlled) kind filter-এ প্রায় অপরিবর্তিত।
  - কিন্তু REQUEST_LOOSE-এর fresh সংকেত প্রায় পুরোটাই প্রত্যাশিত kind-এর বাইরে ছিল।
  - Kind-নিরপেক্ষ mapped-fingerprint মাপ fault class-এর detection বাড়িয়ে দেখায়, বিশেষত যখন mutation generator-এর trajectory বদলায়।
- Per-run kind-বণ্টন: `fuzzer_compare.csv` (`fresh_mut_kinds`)। Run log: `09_collab/logs/kindfilter/`।

## Same-seed reference আর traffic trajectory (2026-11-15; T34 সংশোধিত)

এই অংশ শুধু বর্ণনামূলক।
- Request key (T34 F2): method, origin, path, query, request content-type, পূর্ণ captured body object-এর sha256। Response status key-তে নেই; সেটা আলাদা metric `pos+status`।
- Volatile field (generated ID, timestamp) normalize করা হয়নি। তাই literal overlap গঠনগত মিলের নিম্নসীমা মাত্র।
- Median = `statistics.median` (T34 F3)।

### ১. Same-seed reference প্রায় শূন্য
- 48টি EvoMaster row-এর মধ্যে 45টিতে same-seed checkable NEW 0। বাকি 3টি scout s2-এ: METHOD_SEM 1, LOOSE 1, STRICT 2।
- দেখা গেছে, **একই seed-এ EvoMaster প্রায় একই request sequence পুনরাবৃত্তি করে।** প্রতিটি seed-এ 1টি replicate মাপা হয়েছে, তাই এটা পর্যবেক্ষণ, determinism-এর প্রমাণ নয়।

  | SUT | Positional identity | Multiset Jaccard |
  |---|---|---|
  | cwa | 1.000 (তিন seed-এই captured request sequence হুবহু এক) | 1.000 |
  | petstore | 0.996–0.997 | 0.94–0.99 |
  | market | 0.90–0.93 | 0.98–0.99 |
  | scout | 0.88 / **0.20** / 0.88 | 0.74 / 0.36 / 0.81 |

  - Scout s2-এর trajectory আলাদা হয়ে গেছে। ⚠️ সম্ভবত time-budgeted search-এ সময়ের সামান্য পার্থক্য থেকে; যাচাই হয়নি।

### ২. Mutated run বনাম paired baseline (median, প্রতিটি fault-এ 12টি EvoMaster run)

| Fault | Positional | Pos+status | Jaccard | Multiset Jaccard | beyond cross | beyond same | beyond both |
|---|---|---|---|---|---|---|---|
| METHOD_SEM | 0.015 | 0.011 | 0.043 | 0.168 | 12/12 | 12/12 | 12/12 |
| REQUEST_LOOSE | 0.016 | 0.015 | 0.034 | 0.220 | 5/12 | 7/12 | 5/12 |
| REQUEST_STRICT | 0.011 | 0.010 | 0.025 | 0.174 | 7/12 | 7/12 | 7/12 |
| RESPONSE_ORACLE | **0.966** | **0.966** | **0.987** | **0.990** | 11/12 | 11/12 | 11/12 |

- **পর্যবেক্ষণ:**
  - Request-side mutation-এর (METHOD_SEM, LOOSE, STRICT) পরে EvoMaster-এর literal request sequence baseline থেকে প্রায় পুরোপুরি আলাদা। RESPONSE_ORACLE-এ প্রায় একই।
  - তবে ব্যতিক্রম আছে: scout ORACLE s2-এ 0.20, ঠিক তার replicate-এর মতো।
- EvoMaster-এ `beyond_both` প্রতিটি row-এ `beyond_cross`-এর সমান।
  - শুধু petstore LOOSE-এ same-seed নিয়ম 3/3 দিত, cross নিয়ম দেয় 1/3।
  - s1 আর s2-এ fresh 1, cross ref 1, same ref 0।
- **⚠️ Hypothesis (T34 F1), প্রতিষ্ঠিত নয়:**
  - Request-side mutation generator input বদলায় বলে trajectory সরে যায়। তাই সেখানে unchanged-input same-seed replicate হয়তো noise কম দেখায়, আর cross-seed reference একটা sensitivity তুলনা দেয়।
  - ORACLE-এ traffic প্রায় এক, তাই fresh সংকেত মূলত একই traffic-এ oracle পরিবর্তনের প্রভাব হতে পারে।
  - কিন্তু এগুলো প্রতিষ্ঠিত নয়:
    - divergence নিজেই treatment-এর ফল হতে পারে;
    - একই request হলেও stateful SUT-এর response বদলাতে পারে;
    - একটা replicate-এ শূন্য noise দেখে অতিরিক্ত NEW-কে "noise নয়" বলা যায় না।
  - তাই প্রাথমিক observed reference হলো same-seed replicate, আর cross-seed হলো sensitivity reference। দুটোই পাশাপাশি দেওয়া হয়েছে।
  - T34-এর spot-check: cwa ORACLE s1-এ fresh 6 = replay 6, market ORACLE s2-এ 7 = 7। দুটো row equivalence-এর সাধারণ প্রমাণ নয়।
- **Schemathesis (median, mutated বনাম baseline):** positional 0.26–0.51; ORACLE 0.40।
  - Same-seed replicate-এর তুলনা (`schemathesis_replicate_overlap.py`): `noise_floor_spec.py`-এর replicate থেকে 52 জোড়া।

    | SUT | Positional (min / median / max) | Multiset Jaccard (median) |
    |---|---|---|
    | cwa | 0.16 / 0.26 / 0.28 | 0.30 |
    | petstore | 0.14 / 0.31 / 0.82 | 0.57 |
    | scout | 0.37 / 0.46 / 0.73 | 0.53 |
    | market | 0.56 / 0.72 / 0.84 | 0.69 |

  - Schemathesis-এর same-seed replicate-ও একে অপরের থেকে mutated run-এর মতোই সরে যায়। তাই তার জন্য same-seed noise floor (`NOISE_FLOOR_SPEC.md`) EvoMaster-এর তুলনায় বেশি তুলনীয় reference দেখায়।
  - ⚠️ Schemathesis-এর অনির্দেশ্যতার উৎস (worker ক্রম, SUT state, নাকি Hypothesis database) যাচাই হয়নি।

## Traffic আর reference-এর মাপ
- **Mutated run-এ exchange সংখ্যা** (all-row mean, `fuzzer_compare.csv`):

  | SUT | EvoMaster | Schemathesis |
  |---|---|---|
  | petstore | ~73k | ~1.6k |
  | market | ~4.2k | ~1.2k |
  | cwa | ~9.7k (run ভেদে 4.9–57k) | ~350 |
  | scout | ~70k | ~4.7k |

  - EvoMaster প্রায় 4–46 গুণ বেশি request পাঠায়, তবু controlled ঘরে সংকেতের হার প্রায় সমান।
- **Cross-seed reference-এর চরম মান:**
  - EvoMaster: max NEW 4, সর্বোচ্চ row-mean 3.5 (scout STRICT s3)। Scout বাদে 2 / 2.0 (petstore); market আর cwa-তে 0।
  - Schemathesis: max NEW 3, সর্বোচ্চ row-mean 2.5 (scout LOOSE p100 s1)।

## পর্যবেক্ষণ
1. **কোনো fuzzer একতরফা ভালো নয়:** controlled ঘরে মোট 20/26 বনাম 19/26। পার্থক্য আসে নির্দিষ্ট ঘরে:
   - **market REQUEST_STRICT:** Schemathesis 3/3, EvoMaster 0/3, যদিও EvoMaster-এর replay NEW 5–11।
     - **"Spec মেনে চলা generator" অনুমানটা খণ্ডিত** (T32, `strict_exposure.csv`; `09_collab/reports/T32_report.md`)।
       - EvoMaster-এর fresh traffic added constraint ভাঙে: s1–s3-এ 392/0/361টি request। কিন্তু **সবগুলোর উত্তর 500, 2xx একটাও নয়।**
       - Baseline-এ 500 fingerprint আগে থেকেই আছে, তাই NEW আসে না।
       - Schemathesis-এর ভাঙা request 2xx পায় (2/65/198), ফলে INVALID_ACCEPTED NEW হয়।
       - EvoMaster-এর **baseline** traffic-এর ভাঙা request 2xx পেয়েছিল (81/280/667); replay NEW সেখান থেকেই আসে।
     - তাই পার্থক্যটা "constraint ভাঙে কিনা" নয়, বরং ভাঙা request SUT-এর কোন পথে যায় (সফল 2xx নাকি 500)।
     - **500-এর code-level কারণ (T35, `09_collab/reports/T35_report.md`):**
       - EvoMaster-এর 753টি violating request সবই `PUT /customer/contacts`, আর প্রতিটির body-তে `_links` একটা **array**।
       - Market-এর HAL deserializer (Spring HATEOAS) এখানে `JsonParseException` ("Expected relation name") দেয়, আর generic `RestExceptionHandler` সেটাকে 500 বানায়।
       - STRICT mutation আগে-optional `_links`-কে **required** করেছে, তাই mutated spec থেকে EvoMaster প্রতিটি body-তে `_links` পাঠায়। Baseline-এর 2xx PUT-গুলোতে `_links` অনুপস্থিত (155/155)।
       - তাই phone/address-এর breach এই 500-এর কারণ নয়। কারণটা spec-এর array রূপ আর SUT-এর HAL-এর মধ্যে আগে থেকেই থাকা অমিল, যা baseline-এও array request-এ দেখা যায়। Required edit সেই পথে traffic ঠেলে দিয়েছে।
       - Schemathesis-এর 2xx violation অন্য operation-এ, তাই "একই breach, ভিন্ন status" এমন সরাসরি জোড়া এই corpus-এ নেই।
       - Claude-এর spot-check: s1-এ 392, s3-এ 361টি array-`_links` PUT, সব 500 + HAL message।
       - **Keyword ablation (`STRICT_ABLATION.md`):** required edit সরালে EvoMaster-এর INVALID_ACCEPTED সংকেত 0/3 থেকে 2/3-এ ফেরে; শুধু required রাখলে 0/3।
       - Schemathesis-এ required edit নিরপেক্ষ: মিলানো settings-এ required-only 0/3, no-required 3/3। আগের `[checks=all]` run-এ required-only-তে 3/3 **collateral** 500 এসেছিল, কারণ baseline ছোট ছিল (T39 F1)। তাই collateral exposure নির্ভর করে baseline coverage-এর ওপর, আর fresh সংকেত kind-নিরপেক্ষভাবে গোনা যায় না।
       - ⚠️ T32-এর আরেকটা পর্যবেক্ষণ: কিছু STRICT edit original pattern-এর সঙ্গে মিলিয়ে অসম্ভব (যেমন phone regex ≥12 char কিন্তু `maxLength=1`)। এর প্রভাব generator-ভেদে আলাদা হতে পারে; causal কারণ যাচাই হয়নি।
     - R1-এর জন্য তাৎপর্য: fresh-only মূল্যায়ন generator-এর পথ এবং SUT-এর আচরণের ওপর নির্ভর করে। Replay mode একই baseline traffic-এ oracle বদলায়, তাই এই নির্ভরতা থেকে মুক্ত।
   - **petstore METHOD_SEM:** EvoMaster 3/3; Schemathesis checkable threshold-এ 0/3, কারণ raw NEW-এ বেশিরভাগ `REQUEST_UNCHECKABLE`, আর বাকিগুলো reference ছাড়ায় না। Expected-kind threshold-এ 1/3।
     - ⚠️ এটা দেখায় raw NEW গুনলে ফল কতটা বিভ্রান্তিকর হয়।
   - **cwa REQUEST_STRICT:** EvoMaster 1/3 (s2: fresh 2, replay 0), Schemathesis 0/3।
     - ⚠️ Baseline replay-তে ওই violation দেখা যায়নি। এর মানে input অনুপস্থিত ছিল কিনা, তা fingerprint দিয়ে বলা যায় না (T29 F6)।
   - **scout:** METHOD_SEM আর STRICT দুই fuzzer-এই 3/3।
2. **REQUEST_LOOSE দুই fuzzer-এই দুর্বল (0–2/3–4); প্রত্যাশিত kind দিয়ে 0/3 প্রতিটি তুলনীয় ঘরে (ফল ৩)।**
   - এখানে সংকেত আসে তখনই, যখন loosened spec-এ বৈধ হয়ে যাওয়া request-কে SUT তবু reject করে (`VALID_REJECTED`)। সেটা ঘটে কেবল traffic ওই constraint ভাঙলে।
   - LOOSE-এর replay NEW সাধারণত 0, কিন্তু সবসময় নয় (T29 F4): cwa p100 s1–3 প্রতিটিতে 2, scout p100-এ 1, petstore-এর দ্বিতীয় s1 batch-এ 2।
3. **RESPONSE_ORACLE দুই fuzzer-এই শক্তিশালী।** Response schema-র mutation যেকোনো 2xx body-তে ধরা পড়ে, generator-এর কৌশল যা-ই হোক।
   - EvoMaster-এ ORACLE run-এর literal request sequence প্রায় baseline-এর মতোই (positional median 0.966)। ⚠️ তাই সেখানে fresh সংকেত হয়তো মূলত একই traffic-এ oracle পরিবর্তন; replay equivalence যাচাই হয়নি।
4. **⚠️ Hypothesis: fresh mode-এর noise reference হয়তো fault class-নির্ভর হওয়া উচিত।**
   - Request-side mutation trajectory সরায়, ORACLE সরায় না।
   - তাই R1 protocol-এ same-seed আর cross-seed, দুটো observed reference-ই পাশাপাশি রিপোর্ট করার প্রস্তাব।
   - কোন reference "সঠিক", তা নির্ধারণে আরও replicate দরকার।

## Scout: EvoMaster কেন আটকায়, আর সমাধান
- **প্রথম চেষ্টা:** `--schemaOracles true`, s1 REQUEST_LOOSE-এ stall (watchdog exit 124)।
- **দ্বিতীয় চেষ্টা:** `EVOMASTER_SCHEMA_ORACLES=false` (T28), আবার stall।
  - EvoMaster-এর log দেখায়, flag false থাকলেও RestSchemaOracle schema parse করে।
- **কারণ:** `tools/specmut.py:resolve()` mutated op-এ `$ref` depth 8 পর্যন্ত inline করে, আর scout-এর activity schema recursive।
  - Mutated spec: 650 KB, nesting depth 31। দুটো op একেকটা ~59 KB।
  - Baseline: 52 KB, depth 8।
- **সমাধান (T31):** `EVOMASTER_INPUT=derecursed`। Schemathesis-এর মতোই original derecurse করে তারপর একই mutation চালানো হয়, generator input হিসেবে।
  - এতে input হয় 67 KB, depth 14, একই 14টি op। Oracle অপরিবর্তিত।
  - Runtime-এ যাচাই করা: scout batch 15/15 run exit 0 (schemaOracles default true)।
- ⚠️ **তুলনার সীমা:** scout-এর EvoMaster input derecursed, বাকি তিন SUT-এর মূল spec। cwa-তে derecurse cut 0, অন্য দুটোর প্রভাব যাচাই হয়নি।

## সীমাবদ্ধতা
- এক budget (300 s), এক severity (30), তিনটি seed। Controlled ঘর 26টি জোড়া। কোনো statistical test নেই।
- Same-seed reference-এ প্রতিটি seed-এ মাত্র 1টি replicate। Observed zero থেকে বলা যায় না যে আসল noise শূন্য, এমনকি যে এটা upper bound বা "noise floor জানা"।
- Trajectory metric literal। Volatile-field normalization নেই, আর response body তুলনা করা হয়নি।
- Schemathesis-এর same-seed replicate-এর trajectory মাপা হয়েছে। কিন্তু controlled ঘরের সংকেত-নিয়মে Schemathesis-এর জন্য cross-seed reference-ই রাখা হয়েছে, দুই fuzzer-কে একই নিয়মে তুলনা করতে।
- Mapped fingerprint পরিবর্তন cause প্রমাণ করে না। Labelling ছাড়া এটা "detection" নয়।
- "Spec মেনে চলা generator" ব্যাখ্যাটা T32-এ সরাসরি যাচাই করে খণ্ডিত হয়েছে।
- Market STRICT-এর 500-পথ T35-এ ব্যাখ্যা হয়েছে: required `_links` আর HAL parse 500। এখান থেকে একটা সাধারণ শিক্ষা: একাধিক keyword-এর STRICT edit (required + maxLength একসঙ্গে) একক constraint-এর causal প্রভাব হিসেবে পড়া যায় না।
