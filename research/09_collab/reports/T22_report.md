# T22 — E5 control-vs-control noise floor (write only)

কাজ সম্পন্ন: `run_noise.sh`, `analyse_noise.sh`, noise validation, `kind=noise` summary এবং `signal_exceeds_noise` rule দেওয়া হয়েছে। সব E5 test **117/117 PASS**; এর মধ্যে নতুন noise test 27টি। বাস্তব noise run চালানো হয়নি—এটি task-এর write-only delivery। প্রমাণ: `08_experiments/E5_codemut/run_noise.sh:6`, `analyse_noise.sh:6`, `test_e5_noise.py:58`; `09_collab/logs/T22_scratch/tests.txt:121–123`, `execution_audit.json:2–6`; scope: `09_collab/tasks/T22.md:9–24`।

## কী পরিবর্তন হয়েছে

- Shared launcher-এর `kind=noise` একই seed-এ control image দুবার নেয়। Ledger role `control`/`control_repeat`, কিন্তু দুবারই harness-এ `CODE_ROLE=control`, একই immutable control image ID, control JAR ও original source digest যায়। Run ID আলাদা; budget 300 s, DATA_GEN=all, 100 examples, response_headers_conformance, timeout 10000 ms ও body limit 65536—সব pair mode-এর একই code path। প্রমাণ: `08_experiments/E5_codemut/e5_pipeline.py:62–124`; exact mocked-launch assertions: `test_e5_noise.py:139–161`।
- `noise-runs.tsv`, `noise-run-plan.json`, preflight/log এবং `noise-pair-validation-s<seed>.json` আলাদা; existing pair ledger/report overwrite হয় না। Standalone validator-এ `--kind noise` আছে। দুপাশের image/JAR/source chain control build-এর সঙ্গে মেলাতে হয়; metadata, snapshot, runtime, Env multiset, Binds set ও T20c JUnit/exclusion rules একই থাকে। Manifest-mapped operation-এ asymmetric JUnit error noise mode-এও FAIL। প্রমাণ: `e5_common.py:20–24,85–116`; `e5_pipeline.py:62–124`; `validate_pair.py:214–378,380–402`; tests: `test_e5_noise.py:64–137`—সব code path `08_experiments/E5_codemut/`-এর অধীনে।
- Noise analysis baseline হিসেবে control এবং treatment হিসেবে control_repeat নিয়ে দুই oracle-এ fresh attribution করে। Output `noise-analysis-s<seed>-<oracle>/`; raw/scoped violations দুটিই থাকে। Exclusions দুই role-এ একইভাবে filter হয়; provenance/hash chain এবং current evidence পুনরায় যাচাই হয়। প্রমাণ: `08_experiments/E5_codemut/e5_pipeline.py:144–190`; exclusion integration test: `test_e5_noise.py:108–123`; separate-file test: `test_e5_noise.py:181–190`।
- Summary দুই kind-এর ledger/plan discover করে। Noise-এর `mutated_*` columns **manifest-mapped operation stratum** বোঝায়; বাস্তবে control code পরিবর্তিত নয়। Noise NEW/INCREASED/DECREASED/VANISHED একই fingerprint/occurrence definitions-এ মাপে। Legacy `mutated_occurrences` এবং `expected_signal_present_mutant` নাম noise row-এ control_repeat treatment বোঝায়; এগুলো causal IMPL prediction নয়। প্রমাণ: `08_experiments/E5_codemut/summarise_e5.py:20–25,81–155,240–257`; metric integration tests: `test_e5_noise.py:181–202`; documentation: `PIPELINE.md:205`।

## `signal_exceeds_noise` rule

Rule ID: `EXPECTED_CHANGED_FP_ABSENT_BOTH_NOISE_RUNS_V1`। একই MUT_DIR × seed × oracle-এর validated pair/noise analysis লাগে। Pair control বনাম noise control-কে noise validator দিয়ে আবার মিলিয়ে cross-comparison build/scenario যাচাই করা হয়। চার run directory, Compose project ও প্রত্যেক service-এর container ID আলাদা হতে হবে; proxy volume shared হওয়া চলবে না। প্রমাণ: `08_experiments/E5_codemut/summarise_e5.py:182–203`; reuse/scenario tests: `test_e5_noise.py:241–265,273–277`।

`True` তখনই, যখন mutant comparison-এর manifest-mapped operation-এ expected-kind NEW/INCREASED fingerprint আছে, operation চার capture-এই পাওয়া গেছে, এবং ওই fingerprint **উভয় noise run-এই অনুপস্থিত**। Noise fingerprint union-এ VANISHED ও unchanged/PERSISTENT-ও ধরা হয়। Valid matched noise থাকলে candidate না থাকা, অথবা সব covered candidate noise-এ থাকা মানে `False`। Missing/invalid/wrong-seed/wrong-oracle noise, scenario mismatch বা ফল বদলাতে পারে এমন missing operation exposure হলে `UNKNOWN`; noise row-এ `NOT_APPLICABLE`। Detail column reason বা qualifying fingerprint রাখে। প্রমাণ: `08_experiments/E5_codemut/summarise_e5.py:159–228`; positive/negative/unknown tests: `test_e5_noise.py:204–239,267–288`।

⚠️ এই rule finite observed absence যাচাই করে; statistical significance, effect magnitude বা causal kill প্রতিষ্ঠা করে না। Noise-এ fingerprint একবার থাকলেও বড় mutant occurrence increase `False` হতে পারে। Captured operation মানে একই request body, branch coverage, business state বা request count নয়। এক seed-এ একটি noise pair সমর্থিত; অতিরিক্ত repeat-এর জন্য আলাদা fresh launch directory প্রয়োজন। প্রমাণ: `08_experiments/E5_codemut/PIPELINE.md:205` (T22 rule ও limitations); `summarise_e5.py:182–210`; `e5_pipeline.py:62–68`।

## যাচাই ও বর্তমান saved evidence

| যাচাই | ফল | প্রমাণ |
|---|---|---|
| সব E5 tests | 117 PASS; 90 পুরোনো + 27 নতুন | `09_collab/logs/T22_scratch/tests-initial.txt:94–96`; `tests.txt:121–123`; `08_experiments/E5_codemut/test_e5_noise.py:58–302` |
| Python AST / shell syntax | 5 Python module ও 4 wrapper PASS | `09_collab/logs/T22_scratch/static_checks.json:2–15` |
| Existing CSV compatibility | 50→50 rows; 44 COMPLETE, 6 পূর্বের FAIL; pipeline version marker ছাড়া পুরোনো সব column অপরিবর্তিত | `09_collab/logs/T22_scratch/summary_verification.json:2–19` |
| বাস্তব noise evidence | 0 noise row; সব 50 pair row-এ `signal_exceeds_noise=UNKNOWN` | `09_collab/logs/T22_scratch/summary_verification.json:8–13`; `execution_audit.json:5–6` |
| Protected hashes | 196,576 পূর্বের file অপরিবর্তিত | `09_collab/logs/T22_scratch/protected-verification.json:2–4` |

Summary command exit 1 প্রত্যাশিত: cwa-drop-null seed 3 এবং cwa-drop-validation seeds 2/3-এর দুই oracle মিলে ছয়টি পূর্বের failed/unattempted row আছে। এগুলো শূন্য metric বানানো হয়নি; error ও blank metric অক্ষুণ্ণ আছে। প্রমাণ: `09_collab/logs/T22_scratch/summary-run.txt:1`, `summary_verification.json:20–57`; `08_experiments/E5_codemut/summarise_e5.py:128–155`। Existing analysis hashes মেনে attribution recompute করা হয়েছে; complete rows-এ `PRIOR_E5_PIPELINE_RECOMPUTED` version marker আছে। প্রমাণ: একই verification file:14–18; `summarise_e5.py:38–78`।

External process boundary test-এ mock করা হয়েছে; বাস্তবে শুধু own Python/test/conformance/attribute এবং `bash -n` চালানো হয়েছে। Harness, tools, existing work, saved runs ও build_pair.sh-এর protected inventory অপরিবর্তিত। Blind package ও key পড়া/লেখা হয়নি; snapshot সেগুলো অন্তর্ভুক্তও করে না। প্রমাণ: `09_collab/logs/T22_scratch/execution_audit.json:2–16`, `protected-verification.json:2–4`; mock boundary: `08_experiments/E5_codemut/test_e5_noise.py:139–178`; task boundary: `09_collab/tasks/T22.md:21–24`।

## পরবর্তী ব্যবহার ও সীমা

Coordinator-এর future commands `08_experiments/E5_codemut/PIPELINE.md:220`-এ আছে: reviewed MUT_DIR-এ `run_noise.sh`, তারপর `analyse_noise.sh`, শেষে `summarise_e5.py`। কোনো harness change/proposed diff প্রয়োজন হয়নি; wrapper একই existing harness interface নেয়। প্রমাণ: `run_noise.sh:6`, `e5_pipeline.py:96–107`; full workflow: `PIPELINE.md:205`—সব path `08_experiments/E5_codemut/`-এর অধীনে।

Noise preflight ইচ্ছাকৃতভাবে পুরো T20 build bundle যাচাই করে; unused mutant bundle-ও valid থাকতে হবে। Build-invalid/incomplete directory দিয়ে এই version noise launch করবে না। Empirical noise floor বা causal conclusion এখনো পাওয়া যায়নি; বাস্তব repeat captures আসার পর নতুন rows ও comparison তৈরি হবে। Implementation blocker নেই। প্রমাণ: `08_experiments/E5_codemut/e5_pipeline.py:67–71`; `validate_pair.py:60–137`; `09_collab/logs/T22_scratch/summary_verification.json:8–13`।
