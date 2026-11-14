# Schemathesis বনাম EvoMaster: spec mutation-এ mapped fingerprint পরিবর্তন (2026-11-15, Claude; T29 review-এর পর সংশোধিত)

**Scripts** (সব offline; বিদ্যমান run বর্তমান checker দিয়ে আবার check করা — int format চালু, default oracle 400/422):
1. `fuzzer_compare.py` → `fuzzer_compare.csv`
2. `fuzzer_noise_cross_seed.py` → `fuzzer_noise_cross_seed.csv`
3. `fuzzer_controlled_cells.py` → `fuzzer_controlled_cells.csv`

Review: Codex T29 (`09_collab/reports/T29_review.md`)। ৬টি finding-ই গ্রহণ করা হয়েছে, আর নিচের সব সংখ্যা সংশোধনের পরের।

## Run
- **EvoMaster v6.2.0 black-box** (T27 harness):
  - `--schemaOracles true`, input = মূল `spec.test.json`, budget 300 s।
  - petstore, market, cwa: baseline + 4 fault × seed 1–3, SEVERITY 30, ORACLE_POOL=baseline, LOOSE_POOL=spec।
  - প্রতিটি SUT-এ 12টি mutated run, সবগুলো `complete`।
- **Scout (EvoMaster):** দুইবার s1 REQUEST_LOOSE-এ আটকে গেছে (watchdog exit 124)। কারণ এবং সমাধান §Scout-এ।
- **Schemathesis:** বিদ্যমান `DATA_GEN=all` run, max-examples 100।
  - REQUEST_LOOSE-এর কিছু run p100।
  - petstore LOOSE p30 s1 দুটো আলাদা batch-এ আছে। ওই অতিরিক্ত repeat-টা স্বাধীন চতুর্থ seed নয়।

## মাপকাঠি
- **সংকেত:** mutated op-এ fresh NEW fingerprint। এটা "mapped fingerprint পরিবর্তন", fault detection-এর প্রমাণ নয়।
  - Fresh attribution সব NEW-কে `NEEDS_MANUAL` দেয়। Cause প্রতিষ্ঠার জন্য labelling দরকার।
  - **`*_UNCHECKABLE` kind বাদ** (T29 F3): checker-এর অক্ষমতাকে fault-এর সংকেত ধরা হয় না। একই filter সংকেত আর reference, দুই দিকেই।
- **Reference (T29 F1):**
  - EvoMaster-এ একই seed-এর replicate নেই। তাই B (seed s) বনাম একই batch-এর অন্য seed-এর baseline B' (base spec, একই manifest) মাপা হয়েছে।
  - এটা **observed cross-seed reference**। Same-input noise-এর upper bound **নয়**: petstore STRICT/ORACLE s3-এ same-seed max NEW 3/1, অথচ cross-seed max 0।
  - "Reference ছাড়ায়" মানে এই সসীম peer-সেটের maximum-এর চেয়ে বেশি। কোনো significance দাবি নেই।
- **Controlled ঘর (T29 F2):** একই sut × fault × severity × seed, যেখানে দুই fuzzer-এর mutation set (operation + edit) হুবহু এক (`manifest_sig`)।
  - ORACLE-এর pool baseline-নির্ভর, আর LOOSE-এর pool পুরোনো Schemathesis run-এ legacy format-নিয়মে তৈরি। তাই এই দুই fault-এ manifest প্রায়ই আলাদা।

## ফল ১: Controlled ঘর (একই mutation, p30)

| SUT | Fault | EvoMaster | Schemathesis |
|---|---|---|---|
| petstore | METHOD_SEM | 3/3 | **0/3** (raw NEW সবই `REQUEST_UNCHECKABLE`) |
| petstore | REQUEST_STRICT | 3/3 | 3/3 |
| petstore | RESPONSE_ORACLE | 1/1 | 1/1 |
| market | METHOD_SEM | 3/3 | 3/3 |
| market | REQUEST_STRICT | **0/3** | 3/3 |
| cwa | METHOD_SEM | 3/3 | 3/3 |
| cwa | REQUEST_STRICT | 1/3 | 0/3 |
| cwa | RESPONSE_ORACLE | 0/1 | 0/1 |
| **মোট** | | **14/20** | **13/20** |

## ফল ২: Manifest আলাদা (শুধু বর্ণনামূলক, p30)

| SUT | Fault | EvoMaster | Schemathesis |
|---|---|---|---|
| petstore | REQUEST_LOOSE | 1/4 | 0/4 (s1 দুইবার গোনা) |
| petstore | RESPONSE_ORACLE | 2/2 | 2/2 |
| market | REQUEST_LOOSE | 1/3 | 1/3 |
| market | RESPONSE_ORACLE | 3/3 | 3/3 |
| cwa | RESPONSE_ORACLE | 2/2 | 1/2 |
| **মোট** | | 9/14 | 7/14 |

- cwa REQUEST_LOOSE-এর তুলনা হয়নি: Schemathesis শুধু p100-এ আছে (সেখানে 3/3), আর EvoMaster p30-এ (2/3)।

## Traffic আর reference-এর মাপ
- **Mutated run-এ exchange সংখ্যা** (all-row mean, `fuzzer_compare.csv`):

  | SUT | EvoMaster | Schemathesis |
  |---|---|---|
  | petstore | ~73k | ~1.6k |
  | market | ~4.2k | ~1.2k |
  | cwa | ~9.7k (run ভেদে 4.9–57k) | ~350 |

  - EvoMaster 4–45 গুণ বেশি request পাঠায়, তবু controlled ঘরে সংকেতের হার প্রায় সমান।
- **Cross-seed reference-এর চরম মান** (T29 F5 সংশোধিত):
  - EvoMaster: max NEW 2, সর্বোচ্চ row-mean 2.0 (petstore ORACLE s2)। market আর cwa-তে 0।
  - Schemathesis: max NEW 3, সর্বোচ্চ row-mean 2.5 (scout LOOSE p100 s1)।

## পর্যবেক্ষণ
1. **কোনো fuzzer একতরফা ভালো নয়:** controlled ঘরে মোট 14/20 বনাম 13/20। পার্থক্য আসে নির্দিষ্ট ঘরে:
   - **market REQUEST_STRICT:** Schemathesis 3/3, EvoMaster 0/3, যদিও EvoMaster-এর replay NEW 5–11।
     - Baseline traffic stricter spec ভাঙে, কিন্তু fresh mutated run-এ EvoMaster-এর traffic তা ভাঙে না।
     - ⚠️ অনুমান: mutated spec পেয়ে EvoMaster সেই constraint মেনে request বানায়, তাই strict constraint-টা আর পরীক্ষাই হয় না। Schemathesis-এর negative data সেটা ভাঙে।
     - R1-এর জন্য তাৎপর্য: fresh-only মূল্যায়ন generator-নির্ভর। Replay mode এই নির্ভরতা থেকে মুক্ত।
   - **petstore METHOD_SEM:** EvoMaster 3/3; Schemathesis-এর সংকেত শুধু `REQUEST_UNCHECKABLE`, তাই checkable 0/3।
     - ⚠️ এটা দেখায় raw NEW গুনলে ফল কতটা বিভ্রান্তিকর হয়।
   - **cwa REQUEST_STRICT:** EvoMaster 1/3 (s2: fresh 2, replay 0), Schemathesis 0/3।
     - ⚠️ Baseline replay-তে ওই violation দেখা যায়নি। এর মানে input অনুপস্থিত ছিল কিনা, তা fingerprint দিয়ে বলা যায় না (T29 F6)।
2. **REQUEST_LOOSE দুই fuzzer-এই দুর্বল (0–1/3–4)।**
   - এখানে সংকেত আসে তখনই, যখন loosened spec-এ বৈধ হয়ে যাওয়া request-কে SUT তবু reject করে (`VALID_REJECTED`)। সেটা ঘটে কেবল traffic ওই constraint ভাঙলে।
   - LOOSE-এর replay NEW সাধারণত 0, কিন্তু সবসময় নয় (T29 F4): cwa p100 s1–3 প্রতিটিতে 2, scout p100-এ 1, petstore-এর দ্বিতীয় s1 batch-এ 2।
3. **RESPONSE_ORACLE দুই fuzzer-এই শক্তিশালী।** Response schema-র mutation যেকোনো 2xx body-তে ধরা পড়ে, generator-এর কৌশল যা-ই হোক।

## Scout: EvoMaster কেন আটকায়
- **প্রথম চেষ্টা:** `--schemaOracles true`, s1 REQUEST_LOOSE-এ stall।
- **দ্বিতীয় চেষ্টা:** `EVOMASTER_SCHEMA_ORACLES=false` (T28), আবার stall।
  - EvoMaster-এর log দেখায়, flag false থাকলেও RestSchemaOracle schema parse করে।
- **কারণ:** `tools/specmut.py:resolve()` mutated op-এ `$ref` depth 8 পর্যন্ত inline করে, আর scout-এর activity schema recursive।
  - Mutated spec: 650 KB, nesting depth 31। দুটো op একেকটা ~59 KB।
  - Baseline: 52 KB, depth 8।
- **সমাধান (T31):** `EVOMASTER_INPUT=derecursed`। Schemathesis-এর মতোই original derecurse করে তারপর একই mutation চালানো হয়, generator input হিসেবে।
  - এতে input হয় 67 KB, depth 14, একই 14টি op। Oracle অপরিবর্তিত।
  - Scout batch এই mode-এ চলছে।
- ⚠️ **তুলনার সীমা:** scout-এর EvoMaster input derecursed, বাকি তিন SUT-এর মূল spec। cwa-তে derecurse cut 0, অন্য দুটোর প্রভাব যাচাই হয়নি।

## সীমাবদ্ধতা
- এক budget (300 s), এক severity (30), তিনটি seed। Controlled ঘর মাত্র 20টি জোড়া। কোনো statistical test নেই।
- EvoMaster-এর same-seed noise-এর মাত্রা অজানা।
- Mapped fingerprint পরিবর্তন cause প্রমাণ করে না। Labelling ছাড়া এটা "detection" নয়।
- ⚠️ "Spec মেনে চলা generator" ব্যাখ্যাটা অনুমান। এটা যাচাই করতে EvoMaster-এর request-গুলোকে strict constraint-এর বিপরীতে সরাসরি পরীক্ষা করতে হবে।
