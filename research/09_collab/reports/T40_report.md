# T40 — E4 blind package ও hidden key সম্পন্ন

**অবস্থা: DONE।** Offline production build একবার চালিয়ে `08_experiments/E2_labelling/e4_blind/`-এ **৫০টি item: ২৮ injected + ২২ decoy** তৈরি হয়েছে। `08_experiments/E4_triage/`-এ requested `e4_key.csv`, `e4_manifest.json`, `build_log.json` আছে। দুইটি task draft ও unchanged codebook package-এ আছে। **কোনো labeller launch বা manual labelling করা হয়নি।** [Evidence: `08_experiments/E4_triage/build_log.json`: `items`, `roles`, `package_file_sha256`; `09_collab/logs/T40_scratch/production_verification.json`: `production_build_count`, `task_draft_copy_identity_passed`, `labellers_launched`।]

## অনুমোদিত omission ও source re-scan

Coordinator-এর supervisor-delegated continuation অনুযায়ী exact ও near-equivalent specification artifact বাদ দেওয়ার অনুমতি প্রয়োগ করা হয়েছে। প্রতিটি omission explicit list-এ থাকতে হয়, file-টিকে JSON/YAML top-level `swagger`/`openapi` document হতে হয় এবং audited justification মিলতে হয়। Near-equivalent-এর জন্য nonempty path set একই এবং অন্তত একটি path document পুরোপুরি identical হতে হয়। Known filename-এ path-set drift বা equivalence evidence হারালেও build fail করে। Arbitrary source file, manual config bypass এবং নতুন unapproved spec-like source file reject হয়। [Evidence: `09_collab/COLLAB_BOARD.md`, Claude T40 decision, 2026-11-15 11:26; `08_experiments/E4_triage/build_e4_blind.py:487`, `:502`, `:552`; `08_experiments/E4_triage/test_build_e4_blind.py:391`, `:405`, `:426`।]

| SUT | source থেকে বাদ দেওয়া file | justification | same path set | identical path documents |
|---|---|---|---|---:|
| cwa-verification | `api-docs.json` | `exact_byte_copy`; original EMB spec-এর সঙ্গে byte-identical | true; ৫/৫ paths | ৫/৫ |
| swagger-petstore | `src/main/webapp/openapi.yaml` | `semantic_near_equivalent_same_path_set`; bytes/document সমান নয় | true; ১৩/১৩ paths | ৭/১৩; ভিন্ন ৬ |

প্রতি file-এর SHA-256, original SHA-256, byte/document equality, path-set equality, identical/different path counts, identical path list এবং justification hidden log-এ আছে। Full upstream tree hash, retained tree hash ও copied tree hash-ও আছে। Retained **৫৫৬টি source file** byte-identical: scout ১৯২, petstore ৩৬, market ২৩৭, CWA ৯১। বাদ দেওয়া দুইটি upstream file অপরিবর্তিত আছে। [Evidence: `08_experiments/E4_triage/build_log.json`: `source_audit`, `source_spec_scan`, `source_spec_approvals`; `09_collab/logs/T40_scratch/production_verification.json`: `source_files_verified`, `suts.*.source_identity_passed`।]

Copy-eligible চার source tree-র **৩১টি JSON/YAML file** scan হয়েছে: scout ৯, petstore ২, market ৭, CWA ১৩। অনুমোদিত দুইটি ছাড়া অন্য spec-like source file নেই। তিনটি existing config YAML parse হয় না; তাদের নাম audit-এ আছে, content/error text print করা হয়নি, এবং spec-like top-level indicator পাওয়া যায়নি। নতুন spec-looking unparseable file-এ scanner fail করে। Package-এর retained source trees পুনরায় scan করে spec-like document **শূন্য** পাওয়া গেছে। [Evidence: `09_collab/logs/T40_scratch/approved_spec_source_audit.json`, প্রতি SUT-এর `scanned_json_yaml`, `parse_error_files`, `spec_like`; `09_collab/logs/T40_scratch/production_verification.json`: `package_spec_like_source_files`; `08_experiments/E4_triage/test_build_e4_blind.py:435`।]

Supplemental whole-tree scan-এ build artifacts-সহ **৮৩টি JSON/YAML file** দেখা হয়েছে: scout ১৬, petstore ৩৩, market ৯, CWA ২৫। সেখানে petstore-এর `target/classes/webapp/openapi.yaml`-এ একই ১৩-path / ৭-identical-path generated copy আছে। এটি original task-এর pre-approved `target/` directory exclusion-এর আওতায়; নতুন source omission যোগ করা হয়নি। এই excluded build copy-সহ তিনটি spec-like file-এর finding report করা হলো; copy-eligible source-এ নতুন unapproved artifact পাওয়া যায়নি। Whole-tree scan-এর পাঁচটি parse-error path-ও evidence-এ আছে। [Evidence: `09_collab/logs/T40_scratch/spec_source_rescan.json`, চার SUT object এবং petstore `under_excluded_directory: true`; `09_collab/tasks/T40.md`, source copy থেকে `target/` বাদ দেওয়ার নির্দেশ।]

## Composite ও replay selection

Seed `20261115`; salt `blind-contract-20261115-v1`। প্রতি class-এ cap = `min(3, floor(clean_exercised_ops/4))`: scout/petstore/market-এ ৩, CWA-তে ১। এতে CWA-র পাঁচটি operation-এর মধ্যেও চার class disjoint রাখা যায়। Repository `specmut.select_operations` ও `specmut.mutate(..., only=...)` ব্যবহার হয়েছে; mutation logic আবার লেখা হয়নি। Mutator edit করতে পারে কি না এবং baseline traffic exposure দিয়ে eligibility নির্ধারিত; scarce class আগে reserve করে, পরে round-robin। LOOSE-এ 400/422 এবং STRICT/ORACLE-এ 2xx exposure prefer করা হয়েছে। Replay NEW outcomes দিয়ে operation বাছা হয়নি। [Evidence: `08_experiments/E4_triage/build_e4_blind.py:241`; `08_experiments/E4_triage/e4_manifest.json`: প্রতি SUT-এর `cap_operations_per_class`, `selection`, `assignments`; `08_experiments/E4_triage/build_log.json`: `selection_policy`।]

METHOD_SEM প্রথম apply হয়েছে; original ও destination verb দুটো occupied রাখা হয়েছে। পরের class শুধু পূর্বনির্ধারিত original operations পেয়েছে। প্রতি stage checker-এ parse হয়েছে; original operation counts অপরিবর্তিত: scout ৪৯, petstore ১৯, market ১৩, CWA ৫। Complete edit records থেকে চার composite-ই স্বাধীনভাবে reconstruct হয়েছে: scout ১২ edited operation/৪১ edit; petstore ১২/৭২; market ১২/৩৩; CWA ৪/১৬। নতুন `x-` extension signature যোগ হয়নি। [Evidence: `08_experiments/E4_triage/e4_manifest.json`: `stages`, `mutations`; `09_collab/logs/T40_scratch/real_composite_checks.json`; `09_collab/logs/T40_scratch/production_verification.json`: `suts.*.composite_patch_reconstruction_passed`, `disjoint_operation_sets_passed`।]

একই ৭,৭৯৩ baseline exchange original ও composite spec-এ check হয়েছে: `INT_FORMATS=True`, `strict_additional=False`, default rejection oracle 400/422; এরপর `attribute(..., 'replay')`। Canonical `EXPECTED_KINDS` existing `fuzzer_compare.py`-এর AST literal থেকে পড়া হয়েছে; analysis script execute হয়নি। Injected item কেবল NEW + mutated operation + canonical expected kind; প্রতি SUT×fault সর্বোচ্চ তিনটি, আলাদা edit-pointer group prefer করে। Complete operation edit pointers key-তে আছে; diversity ranking আলাদা causal adjudication নয়। [Evidence: `08_experiments/E4_triage/build_log.json`: `checker`, `replay`, `expected_kinds`; `08_experiments/E4_triage/build_e4_blind.py:382`; `08_experiments/E1_pilot/pilot_results/fuzzer_compare.py:35`; `08_experiments/E4_triage/e4_key.csv`: injected rows।]

Decoy-তে blind-sheet fingerprint canonicalization, item_id/adjudication/final-sheet join এবং method/template/status/kind consistency check আছে। শুধু original/composite উভয় spec-এ PERSISTENT mapped fingerprint নেওয়া হয়েছে; final_L1 stratum অনুযায়ী deterministic round-robin-এ সর্বোচ্চ ছয়টি। কোনো final label পরিবর্তন বা নতুন label adjudicate করা হয়নি। [Evidence: `08_experiments/E4_triage/build_e4_blind.py:336`, `:382`; `08_experiments/E4_triage/e4_key.csv`: decoy rows-এর `baseline_item_id`, `final_L1`; `09_collab/logs/T40_scratch/production_verification.json`: `suts.*.all_item_joins_passed`।]

## Production counts

প্রতি fault cell-এ **eligible NEW / selected**। সব zero cell দেখানো হয়েছে। Petstore METHOD_SEM-এর ৬টি eligible fingerprint-এর মধ্যে পাঁচটিতে transport-clean representative আছে; সেখান থেকে তিনটি নেওয়া হয়েছে। [Evidence: `08_experiments/E4_triage/build_log.json`: `counts.*.{fault}.eligible_fingerprints`, `transport_clean_candidates`, `selected`।]

| SUT | REQUEST_LOOSE | REQUEST_STRICT | RESPONSE_ORACLE | METHOD_SEM | injected | decoy |
|---|---:|---:|---:|---:|---:|---:|
| scout-api | 0 / 0 | 11 / 3 | 44 / 3 | 5 / 3 | 9 | 6 |
| swagger-petstore | 0 / 0 | 8 / 3 | 11 / 3 | 6 / 3 | 9 | 6 |
| market | 0 / 0 | 6 / 3 | 4 / 3 | 6 / 3 | 9 | 6 |
| cwa-verification | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 1 | 4 |
| মোট | 0 / 0 | 25 / 9 | 59 / 9 | 18 / 10 | **28** | **22** |

Decoy strata: scout BOTH=2, IMPL=2, SPEC=1, UNDECIDABLE=1; petstore BOTH=2, IMPL=1, SPEC=1, TEST=1, UNDECIDABLE=1; market BOTH=2, IMPL=2, SPEC=2; CWA SPEC=1, SPEC_PARTIAL=1, TEST=2। CWA-তে পাঁচটি mapped PERSISTENT candidate-এর মধ্যে চারটিতে clean representative পাওয়া গেছে। Production counts পূর্বের preflight counts-এর সঙ্গে পুরোপুরি মিলে গেছে। [Evidence: `08_experiments/E4_triage/build_log.json`: `counts.*.decoy`; `09_collab/logs/T40_scratch/verify_production.py`, preflight/production equality assertion; `09_collab/logs/T40_scratch/replay_preflight_counts.json`।]

## Blinding, credentials ও package assertions

Transport-clean example selection literal এবং percent-decoded control bytes reject করে; path, nested query, request/response header names ও values check হয়। Authorization/Cookie/Set-Cookie values redact হয়। Input-header ও fixture values literal/JSON-escaped/URL-escaped spellings-এ source-সহ পুরো package scan হয়েছে। Credential hit নেই; কোনো auth value print করা হয়নি। Redaction-এর আগে ও পরে প্রতি exchange-এর checker fingerprint multiset একই, original ও composite দুটিতেই। [Evidence: `08_experiments/E4_triage/build_e4_blind.py:444`, `:641`; `08_experiments/E4_triage/build_log.json`: `credential_checks_passed`, `replay.*.redaction_preserves_all_checker_fingerprints`; `09_collab/logs/T40_scratch/production_verification.json`: `credential_checks_passed`।]

Generated items/spec/tasks-এ নিষিদ্ধ keyword hit নেই। Traffic/log copies-তে **৬৪টি legitimate inherited hit** পাওয়া গেছে; input provenance যাচাই করে অপরিবর্তিত রাখা হয়েছে:

| package file | token | count |
|---|---|---:|
| `K01/r1/compose.log` | `E4` | ১৩ |
| `K01/r1/compose.log` | `E5` | ৬ |
| `K01/r1/compose.log` | `inject` | ২৫ |
| `K04/r1/exchanges.jsonl` | `E4` | ১৫ |
| `K04/r1/exchanges.jsonl` | `E5` | ৫ |

এগুলো SUT traffic/log text থেকে এসেছে; experiment metadata ঢোকানো হয়নি। Hidden build log-এ সব hit আছে। Supplementary provenance file-এ physical LF line numbers আছে; এই LF locators ব্যবহার করতে হবে, কারণ builder string scanner Unicode separator-ও line হিসেবে গোনে। Source trees string check থেকে আগের অনুমোদন অনুযায়ী exempt। [Evidence: `08_experiments/E4_triage/build_log.json`: `legitimate_traffic_keyword_hits`; `09_collab/logs/T40_scratch/traffic_keyword_provenance.json`: `physical_line`, `input_provenance_verified`; `09_collab/logs/T40_scratch/verify_production.py`, input-to-copy equality checks।]

Supplied `CODEBOOK_v0.6.md` unchanged আছে; SHA-256 `fee70f11ed3817c014af0da32f8160117417663ea18d374cbc4f8bc4726ad9b8`। Coordinator-approved `--allow-inherited-codebook-keywords` exception-এর অধীনে original codebook-এর 102–108 লাইনের সাতটি `mutation` hit নথিভুক্ত হয়েছে। অন্য generated file-এ এই exception প্রযোজ্য নয়; বদলানো codebook copy-ও reject হয়। [Evidence: `08_experiments/E4_triage/build_log.json`: `inherited_codebook_keyword_exception`, `inherited_codebook_keyword_hits`, `input_sha256`; `09_collab/logs/T40_scratch/production_verification.json`: `codebook_byte_identity_passed`; `08_experiments/E4_triage/test_build_e4_blind.py:301`।]

Package-এ original বা near-equivalent spec source copy নেই; প্রত্যেক deployment-এ শুধু composite `spec.json` আছে। Package-এর **৫৭২টি file hash** স্বাধীনভাবে verify হয়েছে; মোট size **৫৩,০৯৫,৬১০ bytes**। Input log-এ ৩৮টি file hash ও পৃথক source inventory আছে। আগের freeze-এর ৩৭টি protected tool/run/spec/sheet/task/codebook/fixture input অপরিবর্তিত। Requested root hidden files ও `build_evidence/` copies byte-identical। Existing production output-এ overwrite attempt reject হয়েছে এবং package hashes অপরিবর্তিত থেকেছে। [Evidence: `08_experiments/E4_triage/build_log.json`: `input_sha256`, `package_file_sha256`; `09_collab/logs/T40_scratch/production_verification.json`: `package_file_hashes_verified`, `package_bytes`, `protected_inputs_unchanged`, `overwrite_refusal_passed`; `09_collab/logs/T40_scratch/verify_production.py`।]

## Tests, task files ও execution

`/usr/bin/python3 -I -B 08_experiments/E4_triage/test_build_e4_blind.py` → **২৬/২৬ PASS**, zero skips। Tests real repository mutator/checker/attribution APIs চালায়। দুইটি default synthetic complete build-এর outputs byte-identical; exact+near-equivalent omissions ও inherited-codebook policy-সহ দুইটি additional complete temporary build-ও byte-identical। Production package একবারই তৈরি হয়েছে। [Evidence: `09_collab/logs/T40_scratch/tests.txt`, শেষ summary; `08_experiments/E4_triage/test_build_e4_blind.py:132`, `:347`; `09_collab/logs/T40_scratch/production_verification.json`: `production_build_count`।]

Coverage: disjoint operations ও moved verb reservation; composite validity ও full patch reconstruction; canonical injected-kind filter; decoy strata; clean examples; redaction replay invariance; source identity; exact/near-equivalent spec leaks; credential detection; overwrite refusal; extension rejection; unchanged codebook; omission approval/equivalence checks; unexpected spec-like source stop; arbitrary omission bypass rejection; unparseable spec-looking input; task boundaries। [Evidence: `08_experiments/E4_triage/test_build_e4_blind.py`, `FullBuildTests` ও `AssertionTests` test methods; `09_collab/logs/T40_scratch/tests.txt`, ২৬টি named result।]

`e4_blind/TASK_M1.md` ও `TASK_M2.md` পূর্বপ্রস্তুত draft copies-এর সঙ্গে byte-identical। M1-এ শুধু পাঁচটি L1, confidence, evidence ও rationale; codebook ও intent tool নিষিদ্ধ। M2-তে supplied codebook, intent review procedure ও অনুমোদিত দুই tool আছে। উভয়টিতে package boundary, explicit-path searches, external execution prohibition ও incident reporting আছে। Board/task-file reading override coordinator-কে launch-এর আগে authorize করার draft instruction রাখা আছে। কোনো labeller চালানো হয়নি। [Evidence: `08_experiments/E2_labelling/e4_blind/TASK_M1.md`; `08_experiments/E2_labelling/e4_blind/TASK_M2.md`; `09_collab/logs/T40_scratch/production_verification.json`: `task_draft_copy_identity_passed`, `labellers_launched`।]

Production command সফল হয়েছে:

```sh
/usr/bin/python3 -I -B 08_experiments/E4_triage/build_e4_blind.py \
  --omit-source-original-spec cwa-verification:api-docs.json \
  --omit-source-original-spec swagger-petstore:src/main/webapp/openapi.yaml \
  --allow-inherited-codebook-keywords
```

Stdout/stderr `09_collab/logs/T40_scratch/production_build.txt`-এ আছে। Independent audit command: `/usr/bin/python3 -I -B 09_collab/logs/T40_scratch/verify_production.py`; result `production_verification.json`। Tools, harness, runs ও EMB sources edit করা হয়নি। Docker/Java/Maven/network/SUT execution হয়নি; সব execution নিজস্ব offline Python। [Evidence: `09_collab/logs/T40_scratch/production_build.txt`; `09_collab/logs/T40_scratch/production_verification.txt`; `09_collab/logs/T40_scratch/protected_inputs.json`; `09_collab/logs/T40_scratch/production_verification.json`।]

## সীমা ও পরবর্তী handoff

LOOSE-এর selected item চার SUT-এই শূন্য; CWA-তে শুধু METHOD_SEM থেকে একটি injected item আছে। ⚠️ Positive-only traffic-এ LOOSE-এর VALID_REJECTED signal কম হওয়া plan-এর পূর্বজ্ঞাত সীমার সঙ্গে সামঞ্জস্যপূর্ণ; এই package দিয়ে LOOSE recall একা মাপা যাবে না। Fixed small cap ও traffic-tier selection সব possible spec defect-এর প্রতিনিধিত্ব করে না। Decoy truth adjudicated, construction-based নয়। কোনো labeller result বা SPEC recall এখানে দাবি করা হচ্ছে না। [Evidence: `08_experiments/E4_triage/build_log.json`: `counts`; `08_experiments/E4_triage/E4_PLAN.md`, “পূর্বজ্ঞাত সীমা” এবং decoy truth note।]

Builder-এর কাজ সম্পন্ন। Coordinator-এর পরবর্তী কাজ pre-registration/package freeze ও আলাদা labeller launch authorization; T40-এ এগুলো চালানো হয়নি। Source copies K*/-এর মধ্যেই আছে; `.gitignore` পরিবর্তন করা হয়নি, কারণ user সেটি Claude-এর জন্য রেখেছেন। [Evidence: `09_collab/logs/T40_scratch/production_verification.json`: `labellers_launched`; `09_collab/tasks/T40.md`, final constraint; `08_experiments/E4_triage/E4_PLAN.md`, freeze-before-labelling instruction।]
