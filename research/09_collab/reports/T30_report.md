# T30 — Run-time provenance ও analysis-time drift

## Design (implementation-এর আগে)

সমস্যা: validator current `tools/*.py` এবং current harness inventory/hash-কে প্রত্যেক run-এর recorded inventory/hash-এর সমান চায়; summary saved analysis-এর tool inventory-তেও current bytes চায় (`08_experiments/E5_codemut/validate_pair.py`, `artifacts()`; `summarise_e5.py`, `verify_analysis()`)।

নির্বাচিত design: pair-এর দুই সদস্যের nonempty, safe-path, SHA-256 inventories validate হবে; প্রয়োজনীয় core tool/harness entries থাকতে হবে। Recorded `tool_sha256` এবং `harness_sha256` সম্পূর্ণ dictionary হিসেবে pair-এ identical থাকা বাধ্যতামূলক। Run artefacts-এর actual bytes, build/source/image chain, non-JAR equality, argv, scenario এবং JUnit exclusions-এর checks থাকবে। Current checkout-এ পুরোনো code bytes থাকা আবশ্যক হবে না। ⚠️ `accepted_harness_epochs` registry যোগ করলে একই recorded identity-এর পাশাপাশি manual approval state রাখতে হয়; এই task-এর provenance প্রশ্নে তার প্রয়োজন নেই। Snapshot identity historical code-এর correctness/security approval নয়।

Summary historical analysis-এর identity, output hashes, exclusions এবং saved violations→attribution consistency আগে যাচাই করবে। এরপর saved raw run exchanges থেকে **CURRENT conformance + attribute** দিয়ে metrics পুনর্গণনা করবে। পুরোনো analysis directory overwrite হবে না। পুরোনো validation JSONs-ও বদলানোর প্রয়োজন না থাকলে সংরক্ষিত থাকবে; before/after hashes audit হবে। Historical output-কে current-checker output বলে উপস্থাপন করা হবে না।

প্রত্যেক summary row-তে analysis tool inventory digest, analysis pipeline digest, recorded run snapshot digest, `analysis_tools_drift=none|changed` এবং harness drift থাকবে; incomplete provenance-এ drift `unknown` হবে। Tool drift comparison-এ filename additions/deletions-ও ধরা হবে। Hashes পুরো tool inventory-র, শুধু checker-এর নয়। Runtime snapshot comparison pair ও noise bridge-এ একই strict rule মানবে।

Historical analysis-এর `pipeline_sha256`-এ tools/harness bytes বদলালে সেই entries-কে historical identity হিসেবে যাচাই করা হবে; arbitrary E5 code changes-এর পুরোনো নিষেধ বজায় থাকবে। নতুন pipeline analysis record-এ execution-time current tool hashes থাকবে এবং analysis শেষে সেগুলো অপরিবর্তিত কি না যাচাই হবে।

সীমা: ⚠️ hash inventories recording-এর attestation; সংরক্ষিত historical source bytes/signature ছাড়া প্রতিটি পুরোনো harness-এর implementation পুনরুদ্ধার বা metadata forgery অস্বীকার করা যায় না। Artefact hashes ও pair equality integrity দেখায়, historical code review বা causal kill প্রমাণ করে না। Existing EMB config/auth/JaCoCo checks এই task-এ অপরিবর্তিত থাকবে। কোনো Docker/Java/Maven/network/external code execution হবে না।

## ফলাফল

### Implementation

`e5_common.py:63-85` recorded hash inventory ও current inventory আলাদা করেছে; `validate_pair.py:263-265` historical identities validate করে। Complete metadata dictionary comparison-এ `tool_sha256`/`harness_sha256` allowlist-এ নেই, তাই pair mismatch এখনও FAIL (`validate_pair.py`, `pair_metadata()`)। Required run artefacts-এর byte checks এবং build chain অপরিবর্তিত।

`summarise_e5.py:38-71` current checker তার current `specmut` dependency-সহ load করে; `current_attribution()` original captures-এ current default policy চালায়। `verify_analysis()` historical identity/output hashes/exclusions যাচাই করে, কিন্তু summary metrics historical violations থেকে নেয় না। Historical attribution implementation unchanged থাকলে পুরোনো CSV-ও exact recomputation দিয়ে যাচাই হয়; implementation বদলালে historical schema current schema-র সমান হওয়ার দাবি করা হয় না (`summarise_e5.py:79-135`)।

নতুন analysis-এর `tool_sha256` collection metadata থেকে copy হয় না: actual analysis-time inventory record হয় এবং analysis শেষে পুনরায় compare হয় (`e5_pipeline.py`, `analyse_pair()`, `analysis_tools`)। Summary শুরু/শেষে executed tools/pipeline identity compare করে; মাঝখানে পরিবর্তন হলে output publish করে না। Harness execute হয় না: তার initial snapshot-এর digest `analysis_harness_sha256` ও initial drift record হয়; concurrent harness maintenance metrics invalidate করে না (`summarise_e5.py`, `summarise()`)।

### Tests

- `test_e5_pipeline.py`: **75/75 PASS** (`09_collab/logs/T30_scratch/test_e5_pipeline.txt:79-81`)। Recorded tool/harness mismatch, উভয় run-এ missing/empty/malformed/unsafe inventory, drift reporting, current checker-এ পরিবর্তিত metric, preserved historical files, analysis-time tool recording, attribution schema revision, mid-summary tool drift এবং unexecuted harness-এর concurrent edit covered।
- `test_e5_noise.py`: **29/29 PASS** (`09_collab/logs/T30_scratch/test_e5_noise.txt:32-34`)। Noise pair-এর snapshot mismatch/missing inventory এবং tool drift reporting-সহ existing noise/exclusion/exposure rules covered।
- `test_codemut.py`: **31/31 PASS** (`09_collab/logs/T30_scratch/test_codemut.txt:34-36`)। মোট **135 tests**, zero skips।

প্রথম pipeline test run-এ পুরোনো `pipeline_snapshot_status` string expectation-এর একটি failure হয়েছিল; expectation নতুন explicit status-এ update হয়েছে (`09_collab/logs/T30_scratch/test_pipeline_initial.txt`, `test_old_empty_exclusion_reports_and_prior_pipeline_are_recomputed`)। Final run উপরের সব test পাস করেছে। প্রথম summary attempt চলাকালে attribution-schema compatibility refinement করা হয়েছিল; সেই attempt interrupt করে final স্থির snapshot দিয়ে rerun করা হয়েছে (`09_collab/logs/T30_scratch/summary_attempt_interrupted.txt`; `run_summary.py`)।

পরবর্তী audit-এ ছয় harness file-এর concurrent change পাওয়া যায় (`09_collab/logs/T30_scratch/freeze_verification.json:protected_changed`)। তখন দ্বিতীয় attempt interrupt করে guard কেবল executed tools/pipeline-এ সীমিত এবং harness drift initial digest-সহ record করা হয়েছে (`summary_attempt_concurrent_harness.txt`; `summarise_e5.py`, `summarise()`)। Harness files T30 write scope-এ নেই; T30 patch সেগুলো edit করেনি। ⚠️ পরিবর্তনগুলো concurrent maintenance-এর; audit শুধু before/after byte difference প্রতিষ্ঠা করে, অন্য process-এর পরিচয় নয়।

### Regeneration ও সংখ্যাগত audit

Baseline সরাসরি `git show HEAD:./08_experiments/E5_codemut/e5_summary.csv` থেকে `09_collab/logs/T30_scratch/summary_HEAD.csv`-এ সংরক্ষিত; input working CSV আলাদা `summary_before.csv`। সরবরাহ করা `/tmp/claude-1000/.../scratchpad/` copies edit করা হয়নি।

`legacy_check.py` বর্তমান checker-এ শুধু documented `INT_FORMATS=False` switch প্রয়োগ করে HEAD-এর প্রত্যেক COMPLETE row-এর raw captures পুনরায় check করেছে। **88/88 row**-এর আট scoped fingerprint metric, expected-kind metrics এবং fresh L1 count HEAD-এর সঙ্গে মিলে গেছে (`09_collab/logs/T30_scratch/legacy_check.json`, `rows=88`, `rows_matching_HEAD=88`; `legacy_check.py:fields`)। এতে `signal_exceeds_noise` তুলনা করা হয়নি; তার current comparison final summary-তে হয়। Legacy switch কেবল এই diagnostic-এ ব্যবহৃত, published summary-তে নয়।

`/usr/bin/python3 -I -B 09_collab/logs/T30_scratch/run_summary.py` progress-only wrapper থেকে **`summarise_e5.main()`** চালিয়ে `08_experiments/E5_codemut/e5_summary.csv` regenerate হয়েছে; wrapper calculation বদলায় না, শুধু progress ও initial inventory লিখে (`run_summary.py`; `summary_run.txt:125`)। Exit **1** expected: নিচের ছয় historical invalid/incomplete row আছে।

Final CSV: **130 rows = 120 PASS + 4 PASS_WITH_EXCLUSION + 6 FAIL**; analysis **124 COMPLETE + 6 FAIL**। Saved PASS/PASS_WITH_EXCLUSION-এর **62/62 comparison**, অর্থাৎ উভয় oracle-এ **124/124 row**, আবার validate ও recompute হয়েছে। Golden **petstore-reject-valid-v3-এর 12/12 row PASS/COMPLETE**, tool drift **none**, সব audited metrics আগের working CSV-এর সঙ্গে identical (`09_collab/logs/T30_scratch/verification.json`, `validation_counts`, `analysis_counts`, `restored_saved_pass_reports`, `golden_rows_unchanged`; `verify_results.py:37-40`)।

Baseline HEAD-এ **94 rows: 84 PASS + 4 PASS_WITH_EXCLUSION + 6 FAIL** ছিল। Common 94 row-এর validation/completion status অপরিবর্তিত; নতুন 36 row সব COMPLETE। Task শুরুতে পাওয়া working CSV-তে 12 COMPLETE, 118 FAIL ছিল; এখন 112 historical row পুনরুদ্ধার হয়েছে (`summary_HEAD.csv`; `summary_before.csv`; `verification.json:common_rows,status_changes_vs_HEAD`)। এটি prompt-এর আগের 124 FAIL snapshot-এর চেয়ে পরের capture।

Per-site counts নিচে **seed-comparison এককে**, দুই oracle দ্বিগুণ করা হয়নি। `EX` = PASS_WITH_EXCLUSION; `signal` = mapped operation-এ কোনো NEW/INCREASED fingerprint; `expected` = সেই পরিবর্তনে expected kind; `exceeds` = existing conservative noise rule পাস। `default` ও `sut` oracle-এ এই counts identical (`e5_summary.csv`, site_id/kind/seed/oracle row keys; `verification.json:sites_default,totals`)।

| Site | Pair PASS | Pair EX | Pair FAIL | Noise PASS | Noise EX | Signal | Expected | Exceeds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| cwa-drop-null | 1 | 1 | 1 | 2 | 0 | 2 | 2 | 2 |
| cwa-drop-validation | 1 | 0 | 2 | 1 | 0 | 1 | 1 | 1 |
| market-drop-null | 1 | 0 | 0 | 0 | 1 | 1 | 1 | 0 |
| market-response-field-v2 | 3 | 0 | 0 | 3 | 0 | 3 | 3 | 3 |
| market-wrong-status | 3 | 0 | 0 | 3 | 0 | 3 | 3 | 3 |
| petstore-reject-valid | 3 | 0 | 0 | 3 | 0 | 3 | 1 | 1 |
| petstore-reject-valid-v2 | 3 | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| petstore-reject-valid-v3 | 3 | 0 | 0 | 3 | 0 | 3 | 3 | 3 |
| petstore-response-field | 3 | 0 | 0 | 3 | 0 | 3 | 3 | 3 |
| scout-drop-null | 3 | 0 | 0 | 3 | 0 | 3 | 3 | 3 |
| scout-reject-valid | 3 | 0 | 0 | 3 | 0 | 3 | 3 | 3 |
| scout-wrong-status | 3 | 0 | 0 | 3 | 0 | 3 | 3 | 3 |
| **মোট** | **30** | **1** | **3** | **30** | **1** | **31** | **26** | **25** |

প্রতি oracle-এ valid pair-seed মোট **31**: signal **31/31**, expected-kind **26/31**, exceeds-noise **25/31**; অন্য 6 comparison noise rule-এ False, valid comparison-এ UNKNOWN নেই। Noise pairs-এ mapped-op signal **5/31**, expected-kind change **2/31**; exceeds-noise সেখানে NOT_APPLICABLE। দুই oracle একত্রে pair-row totals যথাক্রমে **62, 52, 50**; এটি independent replication দ্বিগুণ হওয়ার দাবি নয় (`verification.json:totals`)।

ছয় FAIL row আগের মতোই: `cwa-drop-null/s3` incomplete/unattempted, `cwa-drop-validation/s2` mutated operation-এ asymmetric JUnit generator error, `cwa-drop-validation/s3` incomplete/unattempted; প্রতিটির default/sut দুই row। সব metric cell blank, zero নয় (`verification.json:errors`; `08_experiments/E5_codemut/work/cwa-drop-validation_20261114T114829Z/pair-validation-s2.json`, `pair.equal_junit_errors`)।

### HEAD-এর তুলনায় metric changes

Common COMPLETE 88 row-এর **24 row / 66 cell** বদলেছে; অন্য common row-এ audited metrics unchanged (`09_collab/logs/T30_scratch/metric_changes.csv`, পূর্ণ 66-cell তালিকা; `verification.json:metric_changed_rows,metric_changed_cells`)। নিচের প্রতিটি পরিবর্তন **default ও sut উভয় oracle-এ একই**; তাই 12 table row আসলে 24 CSV row। `m*` = mutated, `n*` = non_mutated; N/V/I/D = NEW/VANISHED/INCREASED/DECREASED; `e*` = expected_signal_*।

| Kind | Site / seed | HEAD → current |
|---|---|---|
| pair | petstore-reject-valid / 1 | nN 2→0 |
| pair | petstore-reject-valid / 2 | mN 1→2; mI 1→0; nD 13→12; eNEW 0→1; eINCREASED 1→0; fresh L1 NEEDS_MANUAL 1→2; exceeds-noise False→True |
| pair | petstore-reject-valid / 3 | nI 10→9 |
| pair | petstore-response-field / 2 | mV 1→2; mD 1→0; nN 4→2; nI 14→13 |
| pair | petstore-response-field / 3 | nI 15→13; nD 10→9 |
| pair | scout-drop-null / 2 | nI 37→38; nD 27→26 |
| pair | scout-reject-valid / 3 | nI 44→47; nD 38→35 |
| noise | petstore-reject-valid / 2 | mD 1→0; nD 8→7; expected_signal_present_mutant True→False |
| noise | petstore-reject-valid / 3 | mI 1→0; mD 0→1; nI 15→13; nD 10→9; expected_signal_observed True→False; eINCREASED 1→0 |
| noise | petstore-response-field / 1 | nD 5→4 |
| noise | petstore-response-field / 2 | mD 2→1 |
| noise | petstore-response-field / 3 | mV 0→1; mD 1→0; nD 8→6 |

`legacy_check.json`-এর 88/88 exact metric reproduction এবং একই current checker-এর INT_FORMATS=True ফলের এই পার্থক্য int-format policy change-কে বিচ্ছিন্ন করে। Request range যাচাইয়ে আগের false VALID_REJECTED occurrence বাদ যাওয়ায় fingerprint direction বদলাতে পারে; তাই কোনো INCREASED count বাড়লেই নতুন captured fault হয়েছে এমন নয়। Petstore original s2-এর weak expected fingerprint এখন mutant-এ থাকে, noise-এর দুই run-এ থাকে না—exceeds-noise তাই True; একই observed-absence rule অপরিবর্তিত (`08_experiments/E1_pilot/pilot_results/CHECKER_INT_FORMATS.md`, E5 table; `metric_changes.csv`, pair/petstore-reject-valid/2; `summarise_e5.py`, `compare_noise()`)। এটি statistical significance বা causal kill নয়।

### Snapshot identity

Final summary শুরুর complete inventories `09_collab/logs/T30_scratch/analysis_identity_initial.json`-এ আছে। Canonical digest:

- Analysis tools: `016618381c3ed2263af1a614ec5016eec645a89490e57540fabd8670f18454c8`।
- Analysis pipeline: `ff640bd186f2f71a64c28f30eefd98aaedd087652c2150caa4456d2b5ad3e32c`।
- Local harness (initial, analysis-এ execute হয়নি): `bbe2ec04688af4645883ebf568bb6a9da8edcbbbe9aafdb27d902b1e762afd3e`।

Saved PASS/PASS_WITH_EXCLUSION report-এর 62 comparison-এ তিন recorded epoch পাওয়া গেছে (`09_collab/logs/T30_scratch/runtime_epochs.json`, complete inventories ও comparison report paths):

| Runtime digest prefix | Comparison | Tools | Harness files | Tool drift | Harness drift |
|---|---:|---:|---:|---|---|
| `4dd0c945becc` | 44 | 11 | 22 | changed | changed |
| `37e4380f0687` | 12 | 13 | 25 | changed | changed |
| `a000181defe6` | 6 | 13 | 29 | none | changed |

V3 শেষ epoch-এর: তার tools current tools-এর সমান। Task চলাকালে local harness-এ concurrent changes হওয়ায় **V3-এরও harness drift changed**; সেটি গোপন করে `none` করা হয়নি। Golden no-tool-drift condition ও metrics equality assertions পাস করেছে (`verification.json:golden_rows_unchanged`)। Harness snapshot identity point-in-time; final local checkout-এর দাবি নয় (`analysis_identity_initial.json`; `runtime_epochs.json`)।

### Hash audit, scope ও সীমা

Saved validation JSON **কোনোটিই regenerate বা hand-edit করা হয়নি**। মোট **63/63 report-এর before/after SHA-256 identical**—এর মধ্যে historical FAIL report-টিও আছে। প্রত্যেক path-এর পৃথক before/after hash `09_collab/logs/T30_scratch/before.json:validations` ও `after.json:validations`-এ আছে; aggregate check `freeze_verification.json:validation_count,validations_changed`। এতে পুরোনো analysis-এর `pair_validation_sha256` chain-ও অক্ষুণ্ণ থাকে।

Protected inventory-র **4501 file**-এর মধ্যে আগে বর্ণিত ছয় local harness file ছাড়া **4495-এর hash unchanged**; সব retained E5 run artefacts, analysis outputs এবং live tools unchanged। ছয় concurrent difference পৃথকভাবে প্রকাশিত (`freeze_verification.json:protected_count,protected_changed`; `before.json:protected`; `after.json:protected`)। Active scout batch directory scan/execute করা হয়নি; run artefact audit-এ শুধু E5 ledgers-এর recorded directories ব্যবহার হয়েছে (`audit.py:files()`)। Blind keys/packages ও T29 files খোলা বা edit করা হয়নি।

শুধু repo-owned Python analysis/tests, local git reads ও static AST/diff checks চালানো হয়েছে; Docker/Java/Maven/network/external project code execution হয়নি। Source parsing checks `static_checks.json`-এ; final `git diff --check` assigned implementation/CSV paths-এ clean। Published CSV digest ও initial analysis digests `verification.json:output_sha256,analysis_tool_sha256,analysis_pipeline_sha256,analysis_harness_sha256`-এ সংরক্ষিত।

**Open questions / সীমা:** T30-এর কোনো implementation blocker অবশিষ্ট নেই। Historical snapshots-এর source bytes/signature সংগ্রহ বা approved-epoch governance এই design করে না; ⚠️ ভবিষ্যতে historical code correctness/approval দাবি করতে হলে আলাদা evidence লাগবে। Recorded provenance, checker signal ও finite noise absence independent IMPL attribution বা causal kill নয় (`validate_pair.py`, returned `limitations`; `summarise_e5.py`, `causal_kill_status=NEEDS_INDEPENDENT_WITNESS`)। এই task-এর পরে coordinator `E5_RESULTS.md` update করতে পারেন; T30 সেটি edit করেনি।
