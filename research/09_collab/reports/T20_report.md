# T20 — E5 run, validation ও fresh-analysis scripts

T20-এর write-only deliverables সম্পন্ন: `run_pair.sh`, `validate_pair.py`, `analyse_pair.sh`, `summarise_e5.py`, shared helpers, synthetic tests ও execution guide তৈরি হয়েছে। **৭৪/৭৪ tests PASS**: ৫২টি নতুন pipeline test এবং আগের ২২টি codemut test। কোনো Docker/Maven/Java/harness/SUT চালানো হয়নি (`08_experiments/E5_codemut/PIPELINE.md`, “Commands for Claude”, “Synthetic verification”; `09_collab/logs/T20_scratch/tests.txt`, final unittest summary)।

এই report-এ script basename ও `PIPELINE.md` বলতে `08_experiments/E5_codemut/`-এর ফাইল বোঝানো হয়েছে। T20 scratch evidence থাকে `09_collab/logs/T20_scratch/`-এ। Build inputs-এর coordinator সিদ্ধান্ত `08_experiments/E5_codemut/COORDINATOR_NOTES.md`, Maven build images; current applied harness patch সরাসরি `08_experiments/E1_pilot/harness_v2/run_pilot.sh:54–71,123–144`-এ দেখা যায়। এগুলো T20 edit করা হয়নি।

## Deliverables ও ব্যবহার

| Entry point | কাজ ও output |
|---|---|
| `run_pair.sh MUT_DIR [SEEDS…]` | Default 1/2/3; control তারপর mutant; budget 300 s, DATA_GEN=all, response_headers_conformance। Preflight ও frozen plan, run শুরুর আগে ledger row, exit/status update; failure বা validation FAIL-এ stop (`e5_pipeline.py`, `run_pair`; `e5_common.py:16,79–108`)। |
| `validate_pair.py CONTROL_RUN MUTANT_RUN MUT_DIR` | Named checks-সহ `pair-validation-s<seed>.json`; কোনো FAIL হলে nonzero exit। Missing evidence fail; invalid control seed হলে `sunknown` report (`validate_pair.py`, `Checks`, `validate`, `main`)। |
| `analyse_pair.sh MUT_DIR` | প্রতিটি complete paired seed revalidate করে `analysis-s<seed>-default/` ও `analysis-s<seed>-sut/`; original spec, deploy-origin এবং code manifest দিয়ে fresh attribution (`e5_pipeline.py`, `analyse_pair`)। |
| `summarise_e5.py` | Pair × seed × oracle CSV; default output `e5_summary.csv`; stale/missing evidence-এ blank metrics/error, fabricated zero নয় (`summarise_e5.py`, `summarise`, `main`)। |

Exact commands, validation coverage table এবং failure rules `PIPELINE.md`-এ আছে; মূল README-তে নতুন workflow-এর link যোগ করা হয়েছে। Live `build_pair.sh`, coordinator notes, `work/`, harness, tools, external source বা captured runs edit করা হয়নি (`08_experiments/E5_codemut/README.md`, “T20 executable workflow”; `09_collab/logs/T20_scratch/static_checks.json`, `protected_files`; `09_collab/tasks/T20.md`, Constraints)।

Launcher mutable tag-এর বদলে saved immutable build image ID পাঠায়; role-specific source digest/JAR/code manifest আলাদা রাখে। SIGINT/SIGTERM harness-এ forward করে cleanup-এর জন্য অপেক্ষা করে এবং interruption ledger-এ রাখে। Existing ledger বা analysis directory স্বয়ংক্রিয় overwrite/resume হয় না। পরের seed fail হলেও আগের complete seed analyse করা যায়; planned কিন্তু unattempted seeds summary-তে error row হয় (`e5_pipeline.py`, `harness_process`, `run_pair`, `analyse_pair`; `summarise_e5.py:91–127`; `PIPELINE.md`, failure handling)।

## Validation কী পরীক্ষা করে

মূল T19 plan-এর checks এখন concrete saved-evidence checks: completion/exit/JUnit, unchanged original/test spec, generator-input/cuts/argv ও DATA_GEN, seed/budget/checks/timeout/auth, all listed artifact hashes, complete current tool/harness inventory, EMB config এবং JaCoCo provenance। Narrow allowlist ছাড়া metadata difference fail করে। JUnit execution error বা zero test cases reject হয়; ordinary test failures manual review-এর জন্য থাকে (`validate_pair.py`, `generator_argv`, `validate`; `PIPELINE.md`, “Pair validation contract”)।

Build chain-ও যাচাই হয়: original/mutant retained source inventory ও exact edit/patch; actual Maven-cache JAR/POM hashes বনাম saved resolved-artifact inventory; context checksum inventory ও সব non-JAR runtime input; built/staged JAR; image labels; runtime-base layer prefix/digest; collected image ID এবং actual SUT container image। Container Config/HostConfig/mount/entrypoint/args সমান হতে হয়, কেবল Docker identity/network/known Compose bookkeeping বাদ যায়। SUT mount বা persistent volume গ্রহণ করা হয় না; দুই role-এর container/project/proxy volume পৃথক হতে হয় (`validate_pair.py:39–131,160–192`, `treatment`, `pair_metadata`)।

Existing metadata glob `compose.code-image.json`-কেও image inspection হিসেবে পড়ে এবং inspection_error রাখে। Validator এই পরিচিত entry-কে একই থাকলে গ্রহণ করে, কিন্তু Compose JSON-তে immutable override সরাসরি পরীক্ষা করে; অন্য অজানা image entry fail করে। Live metadata writer বদলানো হয়নি (`08_experiments/E1_pilot/harness_v2/run_metadata.py:22–29`; `validate_pair.py`, `treatment`, `pair_metadata`; `test_e5_pipeline.py`, `test_known_compose_json_metadata_glob_entry_is_accepted`, `test_unknown_collected_image_entry_fails`)।

## Analysis ও summary-এর অর্থ

Default oracle 400/422; market-এর SUT oracle 400/406/422। দুটোতেই `conformance.py --deploy-origin http://$SUT_SERVICE:$INTERNAL_PORT` এবং `attribute.py --mode fresh` চলে। Output/input/tool/pipeline/validation hashes ও COMPLETE/FAIL status `analysis.json`-এ থাকে। Summary আবার pair validate করে, hash chain দেখে এবং saved violations থেকে fresh attribution recompute করে CSV মেলায় (`e5_pipeline.py`, `tool`, `analyse_pair`; `summarise_e5.py:26–59`; `08_experiments/R1_triage_codebook.md:251–259`)।

- Mutated ও non-mutated operations-এর জন্য আলাদা NEW, VANISHED, INCREASED, DECREASED columns। Count-এর unit fingerprint; INCREASED/DECREASED শুধু PERSISTENT-এর occurrence delta, NEW/VANISHED আবার গণনা হয় না (`summarise_e5.py:62–88`; `test_e5_pipeline.py`, `test_all_eight_metrics_are_separate_and_do_not_double_count`)।
- `expected_signal_observed` মানে mapped operation-এ expected kind NEW অথবা INCREASED। `expected_signal_present_mutant` pre-existing unchanged presence-ও ধরে। এটি causal kill বা সঠিক IMPL attribution-এর দাবি নয় (`summarise_e5.py:62–88`; `PIPELINE.md`, “Summary meanings”)।
- Current `triage.py` P001 sheet/directory input চায়; E5 JSONL adapter নেই। তাই `triage_status=NOT_APPLICABLE_P001_CLI`, triage L1 blank; fresh attribution-এর L1 counts আলাদা column-এ থাকে। Manifest expectation থেকে কৃত্রিম IMPL prediction বানানো হয়নি (`08_experiments/tools/triage.py:852–864`; `summarise_e5.py:84–88`)।

বর্তমান `e5_summary.csv` **header-only, zero empirical rows**: inspection-এ কোনো E5 `runs.tsv` ছিল না। এটি script/output প্রস্তুত থাকার প্রমাণ; real E5 run/detection result নয় (`08_experiments/E5_codemut/e5_summary.csv:1`; `09_collab/logs/T20_scratch/static_checks.json`, `summary`; `summarise_e5.py`, `main`)।

## Verification results

- **৭৪ tests PASS**: ৫২টি নতুন fake build/run test-এ missing/tampered artifacts, source/dependency/image/base/runtime drift, malformed metadata, omitted hashes, JUnit errors, unsafe paths, privacy, failed/interrupted launch, later-seed failure, planned-unattempted rows, stale reports, changed CSV/labels, আট metrics ও expected-signal distinction যাচাই হয়েছে। Launcher process boundary mocked; কোনো executable harness fixture চালানো হয়নি। Integration test শুধু আমাদের conformance/attribute Python-কে synthetic exchanges দিয়েছে (`09_collab/logs/T20_scratch/tests.txt`, final summary; `test_e5_pipeline.py`, test method names)।
- Coordinator-এর completed **market-drop-null** build directory-এর পাঁচ build-bundle check read-only চালিয়ে PASS পাওয়া গেছে। Source/context/dependency/image evidence পড়া হয়েছে; build বা real run-pair validation চালানো হয়নি, `work/`-এ report-ও লেখা হয়নি (`09_collab/logs/T20_scratch/built_pair_readonly_check.json`, `scope`, `checks`)।
- Own Python AST, দুই shell wrapper ও guide-এর Bash syntax checks PASS; শুরুতে snapshot নেওয়া **৩৫টির মধ্যে ৩৪টি protected regular file অপরিবর্তিত**—৩৩টি harness/tool file ও coordinator-এর build script। বাকি `COORDINATOR_NOTES.md` Claude build-results update করেছেন; সেই পরিবর্তন before/current hash-সহ আলাদা record করা হয়েছে, overwrite করা হয়নি। Test temporary directories cleaned; final static evidence ও output hashes freeze করা হয়েছে (`09_collab/logs/T20_scratch/static_checks.json`; `protected_before.json`, path-keyed rows; `freeze.json`)।

## সীমা ও open questions

1. **[H]** Real harness/SUT execution-এ end-to-end integration এখনো coordinator-কে যাচাই করতে হবে। Synthetic tests এবং read-only build preflight real mutation kill, coverage বা attribution accuracy প্রমাণ করে না (`PIPELINE.md`, “Synthetic verification”, validation limitations; `built_pair_readonly_check.json`, `scope`)।
2. Fresh containers/no writable SUT mounts ব্যবসায়িক state সমান বা traffic deterministic প্রমাণ করে না। Generator container মুছে যায়, তাই তার settings-এর evidence হলো frozen harness ও saved argv। Shared saved Maven image/arguments/cache independent per-build process attestation নয়। Unknown historical scout build image এবং replacement JDK11 base-এর জন্য rebuilt control-ই comparison unit (`validate_pair.py`, report `limitations`; `COORDINATOR_NOTES.md`, Maven build images; `09_collab/tasks/T20.md`, Current state; `PIPELINE.md`, validation limits)।
3. Non-mutated-op counts observational noise estimate; state propagation-ও কারণ হতে পারে। Expected signal match-কে causal kill বলার আগে identical controlled request/state, stack/serialization witness ও independent source/triage review দরকার; repeated same-seed controls-ও বাকি। P001 triage থেকে E5 adapter আলাদা future work (`summarise_e5.py:84–88`; `PIPELINE.md`, “Summary meanings”; `08_experiments/E1_pilot/pilot_results/PILOT_SUMMARY.md`, §3b/§5)।

4. কাজ চলাকালে coordinator ৯/১০ pair build ও `market-response-field` BUILD-INVALID নথিভুক্ত করেছেন। এটি coordinator-reported build result; T20 নিজে javac চালায়নি বা mutant replacement করেনি। Ledger-বিহীন build-invalid selection coordinator notes-এ থাকে; empirical run-summary row তৈরি হয় না (`08_experiments/E5_codemut/COORDINATOR_NOTES.md`, “Build results”; `09_collab/COLLAB_BOARD.md`, Claude T19 E5 builds log; `summarise_e5.py`, discovery)।
