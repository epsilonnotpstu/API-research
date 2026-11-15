# T34 — Controlled cells, same-seed reference ও trajectory review

Review: Codex; 2026-11-15। **গণনার ফল পুনরুৎপাদিত; reference বাছাই ও fresh≈replay ব্যাখ্যা সংশোধন প্রয়োজন।** Findings: ১টি P1 ও ৪টি P2। CSV-only recount-এ 966 assertion, Claude stdout-এর 35টি group/total এবং তিনটি raw-row spot-check-এর 42 assertion পাস করেছে (`09_collab/logs/T34_scratch/codex/verification.json:2`)।

নিচের evidence-এ path সংক্ষিপ্ত করতে `P/` = `08_experiments/E1_pilot/pilot_results/`, `C/` = `09_collab/logs/T34_scratch/codex/`, `H/` = `08_experiments/E1_pilot/harness_v2/`, `T/` = `08_experiments/tools/`। সব `:line` physical file line; CSV header line 1। ⚠️ চিহ্নিত বক্তব্য inference বা সম্ভাব্য প্রভাব।

**F1 — P1: Traffic divergence থেকে উপযুক্ত null reference নির্ধারণ এবং ORACLE fresh≈replay সিদ্ধান্ত প্রতিষ্ঠিত নয়।**

Evidence: `P/fuzzer_trajectory_overlap.py:4–10` প্রায় deterministic fixed-seed traffic থেকে near-identical→same-seed, diverged→cross-seed reference-এর যুক্তি দেয়। `P/PILOT_SUMMARY.md:141–144` সেটিকে প্রয়োজনীয় reference selection ও ORACLE fresh কার্যত replay হিসেবে উপস্থাপন করেছে। `P/FUZZER_COMPARE.md:100–105` আরও বলে same-seed reference noise কম দেখায় এবং ORACLE-এ reference 0 হওয়ায় 11/12 সংকেত noise নয়। অথচ saved scout ORACLE s2-এর positional identity **0.198**, Jaccard **0.105** (`P/fuzzer_trajectory_overlap.csv:66`); তার baseline replicate-ও **0.199/0.105** (`09_collab/logs/T34_scratch/claude_run_traj.log:127`)। cwa-র ফল দিয়ে সব SUT-এর determinism প্রতিষ্ঠা হয় না।

⚠️ Mutation-পরবর্তী divergence treatment-এর ফলও হতে পারে; শুধু ওই overlap দেখে cross-seed baselines mutated run-এর no-mutation counterfactual-এর ভালো estimator বলা যায় না। এক replicate-এ noise zero পাওয়া থেকেও অতিরিক্ত NEW-কে noise নয় বলা যায় না। একই requests হলেও stateful SUT-এর response headers/body বদলাতে পারে; বর্তমান key এসব response detail দেখে না (`P/fuzzer_trajectory_overlap.py:31–32`)। তাই high overlap থেকে fresh attribution-কে replay attribution বলা যায় না। তিনটি spot-check-এর দুটো ORACLE-এ counts সমান পাওয়া equivalence-এর সাধারণ প্রমাণ নয় (`C/spot_check.json:16`, `C/spot_check.json:87`)।

Suggested fix: fault-class-dependent reference selection-কে **⚠️ hypothesis** হিসেবে লিখুন। একই seed/settings-এর unchanged-input replicate-কে primary observed reference, cross-seed-কে আলাদা sensitivity reference হিসেবে পাশাপাশি দিন। `beyond_both = NEW > max(refs)` দুই observed threshold-এর conjunction হিসেবে সঠিক এবং প্রত্যেকটি threshold-এর তুলনায় কঠোর; এটি causal attribution, calibrated statistical test বা noise upper bound নয় (`P/fuzzer_trajectory_overlap.py:69–78`)। Schemathesis-এ same reference অনুপস্থিত থাকলেও `beyond_both` populated—`refs_available` যোগ করে `beyond_available_refs` বলুন, অথবা দুই reference না থাকলে `beyond_both=NA` দিন (`P/fuzzer_trajectory_overlap.csv:47`)।

**F2 — P2: Request key literal request identity নির্ভরযোগ্যভাবে মাপে না।**

Evidence: `P/fuzzer_trajectory_overlap.py:31–32`-এ `str(rq['body'])[:2000]` ও **response status** আছে; request headers ও origin নেই। Logger-এর body string নয়, `text/truncated/size/base64/decode_error`-সহ dict (`T/mitm_fulllog.py:23–32`); origin, headers ও duplicate query values-ও capture হয় (`T/mitm_fulllog.py:43–47`)। `Content-Type` checker-এর request interpretation-এ ব্যবহৃত হয় (`T/conformance.py:372`)।

Synthetic reproduction: identical request-এর response status বদলালে key বদলায়; Content-Type বা origin বদলালে বদলায় না; body-র 2501তম character বদলালেও key মিলে যায়; একই body dict-এর metadata key-order বদলালে key বদলায় (`C/key_probes.py:35–56`; `C/key_probes.json:2–7`)। Real market STRICT s2-তে full-request Jaccard **0.029**, reviewed key-তে **0.027**; 612 mutated request-এর body representation 2000 character ছাড়ায় (`C/spot_check.json:182–188`, `C/spot_check.json:210–214`)। এই তিন-row sample-এ within-run distinct-body collision পাওয়া যায়নি; synthetic collision-কে observed corpus collision বলা হচ্ছে না।

আরও সীমা: `min(len)` denominator এবং set-Jaccard tail length, multiplicity ও order পুরো বোঝায় না। এক request বনাম সেটির 100 repeat-এ দুটো score-ই 1.0 (`P/fuzzer_trajectory_overlap.py:36–41`; `C/key_probes.json:8–11`)। Logger-এর top-level `ts` key-তে নেই—এটি উপযুক্ত; body/path/query-র generated IDs বা timestamps কিন্তু literal পার্থক্য ঘটাবে। ⚠️ তাই low literal overlap একা structurally নতুন search strategy প্রমাণ করে না।

Suggested fix: পূর্ণ captured body bytes-এর digest, method/path/query, origin ও আচরণে প্রাসঙ্গিক request headers দিয়ে canonical request key করুন; response status আলাদা outcome metric হোক। Capture truncation/decode flags জানান। Auth identity metadata role/fixture equality দিয়ে যাচাই করুন; secret প্রকাশ করবেন না। Literal এবং আগেই নির্ধারিত schema-aware volatile-field normalization-এর score আলাদা দিন; নির্বিচারে IDs বাদ দেবেন না। `len_base/len_mut`, length ratio, multiplicity-sensitive overlap এবং alignment metric যোগ করুন। Replay equivalence দাবি করতে response-ও আলাদাভাবে যাচাই প্রয়োজন।

**F3 — P2: Summary-র median বাস্তবে upper-middle order statistic।**

Evidence: `P/fuzzer_trajectory_overlap.py:91`-এ `sorted(xs)[len(xs)//2]`। 12টি value-তে ষষ্ঠ ও সপ্তমটির average প্রয়োজন, কিন্তু সপ্তমটি নেয়। ফলে EvoMaster ORACLE-এর printed positional/Jaccard median **0.996/0.993** (`09_collab/logs/T34_scratch/claude_run_traj.log:114`), CSV থেকে সঠিক median **0.966/0.9875** (`C/recount.json:342–346`)। এই ভুল 0.996-কে narrative-তেও নিয়েছে (`P/PILOT_SUMMARY.md:143`)।

Suggested fix: `statistics.median` ব্যবহার করুন; rounding aggregation-এর পরে করুন। Upper quantile ইচ্ছাকৃত হলে সেভাবেই label দিন। এই সংশোধনে `beyond_*` counts বদলায় না; সেগুলো row-wise threshold comparison (`P/fuzzer_trajectory_overlap.py:76–78`)।

**F4 — P2: Cartesian pairing pair-instance গোনে; unique seed/cell বা independent EvoMaster replicate নয়।**

Evidence: nested `evo × sch` loop (`P/fuzzer_controlled_cells.py:25–26`) এবং প্রত্যেক pair-কে সমান ওজন দেওয়া (`P/fuzzer_controlled_cells.py:44–49`)। `P/fuzzer_controlled_cells.csv:38–39`-এ একই petstore LOOSE p30 s1 EvoMaster run দুটো Schemathesis batch-এর সঙ্গে আছে। ফলে ওই group **E 1/4, S 0/4**, যদিও unique seed তিনটি এবং unique EvoMaster run-ও তিনটি। Manifest-differs total **13/20 বনাম 11/20**-এ unique EvoMaster run **19**; repeated run দুবারই signal=False (`C/recount.json:153–162`; `P/fuzzer_controlled_cells.csv:38–41`)।

Controlled 26 pair-এ এই duplication নেই (`C/recount.json:148–153`)। Narrative duplicate থাকার কথা জানিয়েছে (`P/FUZZER_COMPARE.md:26`, `P/FUZZER_COMPARE.md:65`), কিন্তু CSV/stdout-এর denominator এখনও pair-instance।

Suggested fix: primary analysis-এ আগে থেকে নির্ধারিত একটি Schemathesis batch প্রতি sut×fault×severity×seed নিন, অথবা প্রতিটি seed/cell-এর মধ্যে replicate average করে cell-কে এক ওজন দিন; সব pair secondary table-এ রাখুন। দুটো source run id, batch id ও `pair_instance`/`unique_cell` denominator আলাদা প্রকাশ করুন। ⚠️ শুধু duplicate False EvoMaster row বাদ দিলে descriptive EvoMaster fraction 13/19 হয়; এটিকে নতুন paired fuzzer comparison ধরা যাবে না—Schemathesis repeat policy-ও একই সঙ্গে নির্ধারণ করতে হবে।

**F5 — P2: `settings()` পর্যাপ্ত provenance identity নয়; বর্তমান matches-এ ভুল input বা incomplete run পাওয়া যায়নি।**

Evidence: `P/fuzzer_noise_same_seed.py:31–33` শুধু input mode, schemaOracles, budget ও EvoMaster image মেলায়। Original/generator spec hash, SUT immutable image ID/JAR, timeout, auth fixture, runtime config এবং collection harness/logger identity বাদ পড়ে। এগুলোর অনেকটাই metadata-তে আছে (`H/run_metadata.py:35–39`, `H/run_metadata.py:48–74`)। Current 48 row-এর 36টিতে original ও replicate-এর recorded harness hashes আলাদা; বদলানো files-এর মধ্যে `run_pilot.sh`, `fuzzer_args.sh`, `run_metadata.py` আছে (`C/metadata_summary.json:42–43`, `C/metadata_summary.json`, `unique_replicate_pairs` → `harness_changed_files`)। `harness_version=2` একা এই drift প্রকাশ করে না।

Counter-check: 48/48 row-তে এক replicate; 12 distinct baseline–replicate pair। Actual original/generator inputs, recorded argv, image IDs, SUT JAR ও checked runtime knobs মিলেছে। Scout সব selected pair-এ `derecursed/true`; বাকিতে `spec/true`; selected baseline/replicate complete এবং recorded generator/harness/coverage exit 0। Self-match শূন্য, mutated-vs-baseline settings mismatch-ও শূন্য (`C/metadata_summary.json:18–43`; `C/replicate_matches.json`, প্রত্যেক `settings`, `baseline_exit`, `replicate_exit`)। তাই বর্তমান data-তে ভুল replicate match প্রমাণিত নয়। ⚠️ Harness drift-এর ফলে ফল বদলেছে—এমন দাবিও এই audit সমর্থন করে না।

Suggested fix: effective argv, original/generator-input digest, SUT image ID/JAR, relevant config ও auth-fixture equality validate করুন; relevant harness/logger drift report করুন। Documentation/test-file hash drift-কে অন্ধভাবে collection mismatch করবেন না। Selected **baseline এবং replicate run IDs**, settings digest ও mismatch diagnostics output-এ রাখুন; এখন CSV-তে শুধু replicate count/max আছে (`P/fuzzer_noise_same_seed.py:68–72`)। Summary-র replicate-overlap loop-ও একই selector reuse করুক—ওটি budget/image যাচাই করে না (`P/fuzzer_trajectory_overlap.py:109–114`)। EvoMaster-এ DATA_GEN সরাসরি সমর্থিত নয় (`H/evomaster_guard.py:8–10`); তাই তার বিকল্প generator options audit করার উপায় effective argv ও input digest, Schemathesis-এর DATA_GEN field কপি করা নয়।

**Controlled identity ও attribution direction-এর যাচাই**

`manifest_signature()` operation/path/method/fault এবং সম্পূর্ণ edits serialize করে; edit-এর nested before/after/existence/move value-ও এর মধ্যে থাকে (`P/fuzzer_compare.py:70–74`; `T/specmut.py:204–227`, `T/specmut.py:255–263`)। বর্তমান 26 controlled pair-এ severity, literal edit-set, original source hash এবং original/mutated oracle file bytes সব সমান—false selected-edit match পাওয়া যায়নি (`C/metadata_summary.json:2–17`)।

এটি **same selected patch, conditional on same original spec**-এর ভালো identity; source identity বা candidate pool-এর নিশ্চয়তা নয়। ভবিষ্যতের জন্য source hash ও oracle identity assert করা উচিত। Concrete exception: petstore RESPONSE_ORACLE s3, controlled CSV line 47—দুই pool-এর size 9 হলেও EvoMaster-এ `POST /pet/{petId}`, Schemathesis-এ তার জায়গায় `POST /pet/{petId}/uploadImage`; selected edits/test specs তবু সমান (`P/fuzzer_controlled_cells.csv:47`; `C/manifest_pairs.json`, `csv_line=47`)। তাই একে mutation-controlled বলা যায়; pool-controlled বলা যায় না। cwa ORACLE s2-এ only-ops **file hash** আলাদা, কিন্তু actual operation list সমান—metadata-সহ whole-file hash-কে pool-set inequality ভাবা ভুল (`C/manifest_pairs.json`, `csv_line=9`)।

Direction সঠিক: `attribute(B, B_rep, manifest, 'fresh')`-এর NEW হলো `FP(B_rep,S0) \ FP(B,S0)`; mutated fresh NEW হলো `FP(M,S_mut) \ FP(B,S0)`। দুটোর anchor একই B। Manifest শুধু prospective mutated-operation subset চিহ্নিত করে; no-mutation comparison-এ mutation ঘটেছে বলা হয় না (`T/attribute.py:24–40`, `T/attribute.py:48–53`; `P/fuzzer_noise_same_seed.py:63–67`)। উল্টো direction দিলে অন্য quantity—B-তে থাকা অথচ replicate-এ অনুপস্থিত fingerprint—মাপা হতো। Paired baseline-কে replicate থেকে resolved-path inequality দিয়ে বাদ দেওয়া হয়েছে (`P/fuzzer_noise_same_seed.py:38–41`, `P/fuzzer_noise_same_seed.py:58–59`); audit-এ self-match 0 (`C/metadata_summary.json:20`)।

**স্বাধীন CSV recount**

`C/recount.py:1` কোনো project analysis function import বা exchanges read করে না; CSV join ও threshold নিজেরা গণনা করে। Input row-count: compare 109, cross 109, controlled 46, same 48, trajectory 109 (`C/recount.json:2–8`)। নিচে controlled/descriptive-এ `(EvoMaster successes, Schemathesis successes)/pair-count`; same-এ `EvoMaster beyond/runs`। `—` = matching pair নেই। সব printed controlled/descriptive ও same-seed group/total Claude logs-এর সঙ্গে মেলে (`C/verify_logs.py:13–43`; `C/verification.json:2–3`)।

| SUT | Fault | Controlled (E,S)/n | Manifest differs (E,S)/n | Same-seed beyond | Same max checkable NEW |
|---|---|---:|---:|---:|---:|
| cwa | METHOD_SEM | (3,3)/3 | — | 3/3 | 0 |
| cwa | REQUEST_LOOSE | — | — | 2/3 | 0 |
| cwa | REQUEST_STRICT | (1,0)/3 | — | 1/3 | 0 |
| cwa | RESPONSE_ORACLE | (0,0)/1 | (2,1)/2 | 2/3 | 0 |
| market | METHOD_SEM | (3,3)/3 | — | 3/3 | 0 |
| market | REQUEST_LOOSE | — | (1,1)/3 | 1/3 | 0 |
| market | REQUEST_STRICT | (0,3)/3 | — | 0/3 | 0 |
| market | RESPONSE_ORACLE | — | (3,3)/3 | 3/3 | 0 |
| scout | METHOD_SEM | (3,3)/3 | — | 3/3 | 1 |
| scout | REQUEST_LOOSE | — | (1,2)/3 | 1/3 | 1 |
| scout | REQUEST_STRICT | (3,3)/3 | — | 3/3 | 2 |
| scout | RESPONSE_ORACLE | — | (3,2)/3 | 3/3 | 0 |
| petstore | METHOD_SEM | (3,0)/3 | — | 3/3 | 0 |
| petstore | REQUEST_LOOSE | — | (1,0)/4 | 3/3 | 0 |
| petstore | REQUEST_STRICT | (3,3)/3 | — | 3/3 | 0 |
| petstore | RESPONSE_ORACLE | (1,1)/1 | (2,2)/2 | 3/3 | 0 |
| মোট | | **(20,19)/26** | **(13,11)/20** | **37/48** | **2** |

Table evidence: `C/recount.json:10–164` এবং `C/recount.json:165–278`। cwa LOOSE Schemathesis p100 বনাম EvoMaster p30 হওয়ায় matched pair নেই; severity মিশিয়ে পূরণ করা হয়নি (`P/fuzzer_compare.csv:2`, `P/fuzzer_compare.csv:17`; `P/fuzzer_controlled_cells.py:20`)।

Trajectory-র EvoMaster `beyond_both`: METHOD **12/12**, LOOSE **5/12**, STRICT **7/12**, ORACLE **11/12**; মোট **35/48**। Same-seed-only মোট 37/48 থেকে দুটি petstore LOOSE row cross reference-এ আটকে যায়। Schemathesis-এর **36/61** `beyond_both` আসলে cross-only; same-seed denominator 0। সব boolean CSV arithmetic মেলে; F1/F2/F3 interpretation ও summary metric-এর সমস্যা (`C/recount.json`, `trajectory`; `09_collab/logs/T34_scratch/claude_run_traj.log:111–118`)।

**সর্বোচ্চ তিনটি row-এর raw spot-check**

এখানেই শুধু exchanges check করা হয়েছে; cwa/market-এর ছোট run নেওয়া হয়েছে। `C/spot_check.py` current own checker reuse করে, কিন্তু `attribute()`/`counts()` reuse না করে fingerprint-set difference ও occurrence counters নিজে গণনা করে (`C/spot_check.py:17–25`, `C/spot_check.py:77–91`)। তিন row-এর baseline/replicate/cross-peer share হওয়ায় মোট 11টি distinct raw file পড়েছে; নতুন কোনো চতুর্থ row যাচাই করা হয়নি (`C/verification.json:6–8`)।

| Row | B/M/B_rep exchanges | Fresh checkable NEW | Replay NEW | Same ref | Cross ref | Pos / Jaccard |
|---|---:|---:|---:|---:|---:|---:|
| cwa ORACLE s1 | 5142/5142/5142 | 6 | 6 | 0 | 0 | 1.000/1.000 |
| market ORACLE s2 | 4305/4304/4267 | 7 | 7 | 0 | 0 | 0.926/0.997 |
| market STRICT s2 | 4305/4148/4267 | 0 | 8 | 0 | 0 | 0.004/0.027 |

Evidence: `P/fuzzer_compare.csv:23`, `:51`, `:54`; `C/spot_check.json:5–223`। Selected cwa s1-এর full captured request sequence baseline ও replicate-এ সমান, শুধু lossy key নয় (`C/spot_check.json:50–54`)। অন্য cwa seeds-এর byte equality স্বাধীনভাবে recheck করা হয়নি। Market STRICT-এ fresh mutated-op INCREASED 2 থাকলেও NEW 0—এখানে ব্যবহৃত threshold NEW-only (`C/spot_check.json:160–167`; `P/fuzzer_controlled_cells.py:6`)।

**Framing, সীমা ও বাকি কাজ**

প্রতি seed-এ **একটি** replicate, প্রতি SUT-এ তিনটি baseline–replicate pair; একই baseline pair চার fault-এর operation subset-এ আবার ব্যবহৃত হয়েছে। তাই 48 row মানে 48 independent noise replicate নয় (`C/recount.json:279–282`; `C/metadata_summary.json:18–19`)। Same-seed script-এর “finite-sample observation, not a test” এবং narrative-এর “কোনোটাই upper bound নয়” framing যথাযথ (`P/fuzzer_noise_same_seed.py:12`; `P/FUZZER_COMPARE.md:32–36`)। ⚠️ Observed zero noise থেকে true noise zero, “noise floor জানা”, future maximum বা upper bound বলা যায় না; fixed seed-এ determinism-ও প্রতিষ্ঠা হয় না। একে **observed same-seed replicate reference** বলুন; `beyond_both`-কেও শুধু observed maxima ছাড়ানোর indicator হিসেবে রাখুন। F1-এর “noise নয়” বাক্য এই finite-sample সীমার সঙ্গে সঙ্গতিপূর্ণ নয়।

Open questions: primary Schemathesis repeat policy, literal বনাম normalized trajectory metric, এবং broader determinism/reference-fit দাবি যাচাইয়ের জন্য কতগুলো independent repeat লাগবে—এগুলো analysis plan-এ নির্ধারণ করতে হবে। Current data-র বাইরে নতুন run বা statistical calibration এই review-তে করা হয়নি। Task launch-এর পরে যোগ করা `schemathesis_replicate_overlap.py`/52-pair analysis এই review-এর scope-এ নেই; তার ফল স্বাধীনভাবে যাচাই করা হয়নি (`09_collab/COLLAB_BOARD.md`, Claude T29-F1 2026-11-15 07:20 Log entry; `P/FUZZER_COMPARE.md:108`)।

সব Python offline `/usr/bin/python3 -I -B` দিয়ে চালানো হয়েছে। Scripts/CSVs/docs-এর 12টি reviewed file-এর hashes অপরিবর্তিত; input hashes `C/reviewed_hashes.json` এবং `C/recount.json`-এ সংরক্ষিত (`C/verification.json:4–5`)। Writes কেবল এই report, `C/**`, এবং board-এর এক Log line-এ সীমিত। Docker/Java/Maven/network/external-project code execution হয়নি; runs-এ write এবং auth value output করা হয়নি।
