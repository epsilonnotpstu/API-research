# T50 — নতুন repositories, frozen pool3 ও পৃথক Q-package

এই report-এ সংক্ষিপ্ত script/CSV/JSON ও `key/` path-এর ভিত্তি `08_experiments/E7_mining/`; audit/test summary-এর ভিত্তি `09_collab/logs/T50_scratch/`। Function, JSON field ও repo-named CSV row evidence locator হিসেবে দেওয়া হয়েছে। কোনো per-item direction বা fix identifier এখানে নেই।

## T50b continuation

Supervisor amendment `09_collab/tasks/T50b.md` অনুযায়ী আগের দুই round-এর পর **একই frozen pool3-এর rank 3** থেকে continuation হয়েছে। Budget stop প্রত্যাহার করা হয়েছে; usage-reset continuation-এ record পুনরায় শুরু বা pool পুনর্নির্মাণ করা হয়নি। আগের ৪০ final decisions, ২০৮ preview events, ৮ items ও cap records byte-identical আছে। Decision CSV-এর original byte prefix অক্ষত রেখে append করা হয়েছে; final decision এবং preview record প্রতি candidate শেষে flush হয়েছে। প্রতি সম্পূর্ণ round শেষে yield checkpoint লেখা হয়েছে। Evidence: `review_t50b.py:continuation_guard,private_json,append_csv_records,checkpoint`; `key/t50_superseded_round2/manifest.json`; `key/t50b_round_checkpoints/`; `finalize_t50b.py:audit`; `test_t50b.py:ContinuationTests`।

**Final: ৯৪৭ reviewed candidates / ৪২ accepted candidates / ৬১ accepted items।** Continuation-এ নতুন ৯০৭ candidates reviewed এবং ৫৩ items যোগ হয়েছে। **৫১টি পূর্ণ round** শেষ হয়েছে; ৫২তম round-এর current candidate-এর final decision-এ total ৫৯ থেকে ৬১ হওয়ায় সঙ্গে সঙ্গে review থেমেছে। Target ≥৬০ পূরণই stopping reason; বাকি round review করা হয়নি। চারটি repo exhausted, কোনো repo ১০-item cap-এ পৌঁছায়নি। Evidence: `summary_t50b.json:reviewed,accepted_candidates,accepted_items,continuation_reviewed,continuation_items,completed_round,current_round,current_round_complete,stopping_reason`; `yield_t50.csv`।

পুরোনো unused `key/e13_key.csv`, `key/accepted_full_t50.csv` ও সম্পূর্ণ ৮-item `e13_blind/` directory unmodified অবস্থায় `key/t50_superseded_round2/`-এ move করা হয়েছিল। Archive-এর ৫২ package files এবং দুই CSV-এর hashes মেলে। তারপর সব accepted item দিয়ে তিনটি output নতুনভাবে তৈরি হয়েছে। **Existing `key/e13_shuffle_salt.txt`-ই পুনর্ব্যবহৃত**; পুরোনো mapping/build log এবং historical stopping marker অক্ষত আছে। নতুন mapping/log-এ `_t50b` suffix দেওয়া হয়েছে। Evidence: `key/t50_superseded_round2/manifest.json`; `finalize_t50b.py:archived_hashes`; `build_t50b.py:main,publish`; `key/e13_shuffle_mapping_t50b.csv`; `test_t50b.py`।

## Retrieval ও review

২০টি selected নতুন bare clone পাওয়া গেছে। Review-এর আগে **১২,৮৩২-candidate pool3 freeze** হয়েছে। T46 pool2-এর correction-cue AND (contract path OR behaviour path), exclusions, এবং `10 × cue_strength + operation_path_bit` score অপরিবর্তিত। Contract definition-এ শুধু checked-in document-এর সঙ্গে থাকা Go `// @Router` ও `// swagger:route` annotation sources যোগ হয়েছে; প্রত্যেক repo-তে একই rule। Repo-র মধ্যে score descending, SHA ascending; repo-গুলোর review order `selected.tsv:clone_name` অনুযায়ী rank 1, rank 2, ইত্যাদি round-robin। আগের ৩৪ repository থেকে candidate নেওয়া হয়নি। Evidence: `mine3.py:classify,discover,main`; `mine2.py`; `mine.py:rank_candidate`; `freeze3.json`; `pool3_inventory.json`; `t50_repo_selection/selected.tsv`; `test_t50.py:Pool3Tests,ReviewTests`।

প্রতি candidate-এর final decision-এর আগে পরের candidate খোলা হয়নি। Record-এ review_status, একটি reason_code এবং সর্বোচ্চ ২৫-word candidate-specific reason আছে। Acceptance-এ existing operation, exact parent contract/implementation locators, resolving patch, confidence, family ও neutral proposition আছে: `METHOD path: contract says X; implementation does Y`। IMPL acceptance-এ parent contract-এ corrected behaviour থাকা আবশ্যক। Dedup T45–T49 এবং ২৫ exploratory item-সহ repo–operation–fix_family identity-তে হয়েছে; direction বা অন্য property target/balance করা হয়নি। Evidence: `review_t50.py:require_current,record_preview,accept,finish_accept`; `review_t50b.py`; `finalize_t50b.py:audit`; `key/accepted_full_t50.csv:proposition_check,evidence,confidence,inference_notes`; `key/review_decisions_t50.csv`।

প্রতি repo-র ফল; row evidence `yield_t50.csv:repo`। Accepted candidates ও items আলাদা। `exhausted` মানে সেই repo-র frozen list শেষ; অন্য repo-গুলোর stop `target reached`।

| Repo | Pool3 | Reviewed | Accepted candidates | Items | Last rank | Stop |
|---|---:|---:|---:|---:|---:|---|
| traccar | 274 | 52 | 3 | 5 | 52 | target reached |
| flagr | 41 | 41 | 5 | 8 | 41 | exhausted |
| datarhei-core | 105 | 52 | 4 | 6 | 52 | target reached |
| spring-petclinic-rest | 13 | 13 | 0 | 0 | 13 | exhausted |
| apigee-registry | 18 | 18 | 0 | 0 | 18 | exhausted |
| fess | 885 | 52 | 3 | 5 | 52 | target reached |
| gitea | 3847 | 52 | 0 | 0 | 52 | target reached |
| authelia | 250 | 52 | 2 | 3 | 52 | target reached |
| argo-cd | 874 | 52 | 0 | 0 | 52 | target reached |
| dependency-track | 480 | 52 | 4 | 4 | 52 | target reached |
| halo | 309 | 52 | 1 | 1 | 52 | target reached |
| vikunja | 1497 | 52 | 0 | 0 | 52 | target reached |
| harness | 610 | 52 | 1 | 2 | 52 | target reached |
| tyk | 419 | 51 | 2 | 3 | 51 | target reached |
| casdoor | 697 | 51 | 1 | 1 | 51 | target reached |
| photoprism | 90 | 51 | 2 | 3 | 51 | target reached |
| answer | 209 | 51 | 3 | 4 | 51 | target reached |
| keto | 49 | 49 | 6 | 9 | 49 | exhausted |
| keycloak | 1422 | 51 | 1 | 2 | 51 | target reached |
| nifi | 743 | 51 | 4 | 5 | 51 | target reached |

## Candidate caps, licence ও aggregate ফল

৪২ accepted candidates-এর মধ্যে **২৩টি থেকে একটি করে** এবং **১৯টি থেকে দুটি করে** item রাখা হয়েছে। Cap-এর আগে প্রতিষ্ঠিত valid operation histogram নিচে। `METHOD path` plain byte order-এ সাজিয়ে প্রতি fix-এর প্রথম দুটি রাখা হয়েছে; repo-তে বাকি slot কম হলে তার সীমাও প্রযোজ্য। **FIX_CAP exclusions ৬০; REPO_CAP exclusions ০।** তাই valid operations ১২১, delivered items ৬১। Candidate final rows ৯৪৭ এবং accepted_capped rows ৬০ মিলিয়ে private decision table-এ ১,০০৭ rows। Patch-এর অন্য edits-এ parent mismatch প্রতিষ্ঠা না হলে সেগুলো valid operation হিসেবে গণনা করা হয়নি। Evidence: `summary_t50b.json:items_per_accepted_candidate,valid_operations_per_candidate,FIX_CAP_exclusions,REPO_CAP_exclusions`; `review_t50.py:select_operations`; `key/review_decisions_t50.csv`; `test_t50.py:test_caps_only_read_operation_and_use_plain_bytes`।

| Valid operations per candidate | Accepted candidates |
|---:|---:|
| 1 | 23 |
| 2 | 8 |
| 3 | 2 |
| 4 | 3 |
| 5 | 1 |
| 6 | 1 |
| 10 | 2 |
| 11 | 1 |
| 22 | 1 |

**LICENCE rejections ২**, দুটিই parent licence class `UNKNOWN`; confirmed restrictive licence rejection ০। গ্রহণের আগে parent commit-এর root licence file read-only `git show` দিয়ে পড়া হয়েছে; path/hash/class audit-এ আছে এবং প্রত্যেক accepted item-এর `licence_at_parent` পূরণ করা হয়েছে। Restrictive/source-available/non-commercial grant `OTHER` + `LICENCE:` reason-এ বাদ যায়; অজানা class-ও সতর্কভাবে বাদ দেওয়া হয়েছে। Historical trademark-clause false positive acceptance-এর আগেই context review দিয়ে সংশোধিত হয়েছিল; original correction audit অক্ষত আছে। ⚠️ এটি static licence classification; অজানা licence বাদ দেওয়ায় অতিরিক্ত selection bias থাকতে পারে। Evidence: `review_t50.py:licence_class,parent_licence,licence_gate`; `key/t50_licences/`; `key/e13_licence_classifier_correction.json`; `test_t50.py` licence tests; `test_t50b.py:test_actual_licence_rejections_are_unknown_and_never_accepted`।

Candidate-level reason_code distribution; ACCEPT item নয়, candidate গণনা করে। FIX_CAP আলাদা operation-level exclusion। Evidence: `summary_t50b.json:reason_code_counts,review_status_counts`; `key/review_decisions_t50.csv`।

| reason_code | Candidates |
|---|---:|
| ACCEPT | 42 |
| BOTH_CHANGED_TO_NEW_BEHAVIOUR | 22 |
| GENERATED_OR_DOCS_ONLY_CHURN | 41 |
| NEW_FEATURE_OR_ENDPOINT | 56 |
| NOT_CONTRACT_RELATED | 444 |
| NO_PARENT_MISMATCH | 227 |
| OTHER | 28 |
| REFACTOR_OR_RENAME | 51 |
| TEST_OR_CLIENT_ONLY | 1 |
| TOO_LARGE_TO_ESTABLISH | 35 |

Final statuses: accepted 42, rejected 643, deferred 262। **Aggregate direction: SPEC 34, IMPL 27, BOTH 0।** Per-item directions, history identifiers ও mappings শুধু `key/`-তে। Evidence: `summary_t50b.json:aggregate_directions`; `key/e13_key.csv`; `key/e13_shuffle_mapping_t50b.csv`।

## Package ও checks

পৃথক `08_experiments/E2_labelling/e13_blind/`-এ শুধু **Q01–Q61**। `items.csv`-এর columns `item_id,repo,operation,proposition`, LF line endings এবং verbatim propositions যাচাই হয়েছে। প্রত্যেক item-এর contract/ ও impl/ directories আছে। README T49-এর একই build rules অনুসরণ করে এবং archived round-2 README-এর সঙ্গে byte-identical। অন্য package তৈরি, পড়া বা পরিবর্তন করা হয়নি; package path থাকলে publisher overwrite প্রত্যাখ্যান করে। Key columns `e12_key.csv`-এর সমান, set=new/source_task=T50; full table-এ `accepted_full_t49.csv`-এর columns-এর পরে শুধু licence_at_parent। Evidence: `build_t50.py:prepare,full_bytes`; `build_t50b.py:publish,main`; `test_t50.py:PackageTests,SyntheticPackageTests`; `test_t50b.py`।

Package **273 files / 7,363,650 bytes (7.02 MiB)**: contract 74, implementation 197, table/README ২। Projected large documents 6; redacted source files 170। Generated document বড় হলে operation ও transitive local $ref closure রাখা হয়েছে। Implementation পুরো parent file, privacy redaction ছাড়া; প্রতি item-এ সর্বোচ্চ আটটি। Parent provenance, own-child exclusion, history/message leakage, forbidden words, privacy এবং proposition checks pass। Evidence: `verification_t50b.json:summary,checks`; `key/e13_build_log_t50b.json:items,assertions`; `build.py:contract_files,helper_selection,prepare`।

Cross-item ancestry/path check **248 items** জুড়ে: পুরোনো ১৮৭ ও নতুন ৬১। New/prior repository overlap ০। নতুন items-এর মধ্যে flagged items 26, optional cross-file exclusions 0, retained own-locator overlap incidents 52। পূর্বের flags/keys বদলানো হয়নি। Delivered contract-এ missing local-file references ০ ও remote-file references ০; projected internal closures-ও যাচাই হয়েছে। Evidence: `key/e13_cross_item_audit_t50b.json`; `key/e13_reference_audit_t50b.json`; `key/e13_build_log_t50b.json:cross_item_pairs`; `final_audit_t50b.json`।

**সব 103 tests pass**: আগের 73 + updated T50 21 + T50b 9; failures/errors ০। Earlier suites isolated reconstructions-এ চলেছে; audit hook পুরোনো labelling packages access করতে দেয়নি। Pool3 order/score/frozen-source reconstruction ও selected repo-তে full discovery replay deterministic; Q-shuffle একই salt-এ input-order independent। Real round-robin prefix, target boundary, per-fix selection, licence-at-parent, append-only CSV/JSON, archive hashes, separation, leakage, eight-file cap, preview chronology/filter ও overwrite refusal পরীক্ষা হয়েছে। Disk package, key ও full CSV deterministic reconstruction-এর সঙ্গে byte-for-byte মেলে। Evidence: `run_tests_t50b.py`; `test_t50.py`; `test_t50b.py`; latest `test_summary_t50b_*.json`; `verification_t50b.json:checks.exact_disk_reconstruction`। Raw diagnostics কেবল `key/`-তে।

Execution coverage একাধিক run-এর সমন্বয়: প্রথম full run-এর ১০২ tests-এ আগের ৭৩টি pass, কিন্তু reason privacy scan-এর একটি prose false positive failure ছিল। সেটি যাচাই করে exact prose-only exception এবং নতুন regression test যোগ করার পর সব বর্তমান T50/T50b-এর ৩০টি tests আবার pass করেছে। ফলে ১০৩টি বর্তমান test method-এর pass evidence আছে; unresolved failure নেই। Evidence: `test_summary_t50b_01.json`, `test_summary_t50b_02.json:execution_parts,all_current_test_methods_executed`; `run_tests_t50b_final.py`।

Task শুরুর **১৪,১৫৮ pre-T50 key/pool/freeze files** before/after SHA-256-এ অপরিবর্তিত; changed ০। Pool3, freeze3, retrieval code ও selection-এর frozen hashes-ও মেলে। Superseded তিনটি output ছাড়া অনুমোদিত কোনো replacement করা হয়নি; original records, salt, mapping/build log ও archived outputs সংরক্ষিত। Evidence: `key/preservation_t50_start.json`; `key/preservation_t50b_after.json`; `freeze3.json`; `final_audit_t50b.json:existing_files_checked,changed_existing_files`; `review_t50b.py:continuation_guard`; `finalize_t50b.py:archived_hashes`।

## Preview record ও privacy

Preview ledger: **3151 events / 947 candidates**; outside-final-prefix ০, without-final-decision ০, lookahead-before-prior-decision ০। Chronological order-এ কোনো completed candidate পুনরায় খোলা হয়নি। Evidence: `summary_t50b.json:preview_record`; `key/t50_previews/`; `finalize_t48.py:validate_previews`; `finalize_t50b.py:audit`।

Original T50-তে একটি current-candidate test-path probe-এ credential-সদৃশ fixture literal বেরিয়েছিল; exact value report-এ পুনরাবৃত্তি হয়নি। Corrected filter sensitive keyword-সম্বলিত পুরো line, credential assignment ও long encoded literal suppress করে; probes test/fixture paths বাদ দেয়। Continuation-এ hex-byte literals, encoded checksums ও source-hosting attribution URLs-এর suppression যোগ হয়েছে। একটি template provenance comment-এর attribution URL filter এড়িয়ে একবার বেরিয়েছিল; incident নথিবদ্ধ করে filter সংশোধন এবং regression test যোগ হয়েছে। তাই preview privacy-কে ত্রুটিহীন বলা হচ্ছে না। Evidence: `key/e13_preview_privacy_incident.json`; `key/t50b_attribution_display_incident.json`; `review_t50.py:display,probe`; `review_t50b.py:display`; `peek_t50b.py`; display tests in `test_t50.py`, `test_t50b.py`।

Delivered package-এর সব bytes-এ auth fixture needles এবং observed fixture literal-এর scanner variants পরীক্ষা করে occurrences ০; credential/attribution/history scans pass। Decision reasons-এর scan প্রথমে দুটি reviewer-generated English phrase-কে auth literal ধরেছিল। Exact prose-only exception দিয়ে সেগুলো আলাদা করে private audit রাখা হয়েছে; source/package scanner ও append-only reasons বদলায়নি। অন্য credential-shaped text এখনও test-এ ধরা পড়ে। ব্যক্তিগত attribution বা observed literal report/log-এ আর লেখা হয়নি। Evidence: `key/t50b_reason_privacy_prose_exceptions.json`; `final_audit_t50b.json:privacy_scan_passed,preview_privacy_incident`; `verification_t50b.json:auth_fixtures,auth_value_variants`; `audit_t50b.py:reason_privacy_scan`; `test_t50.py`, `test_t50b.py` privacy tests।

## Threats ও সীমাবদ্ধতা

⚠️ Frozen pool-এর ১১,৮৮৫ candidates unreviewed। Target stop, selected repositories, correction cues, path filters ও byte-order cap sample composition প্রভাবিত করে; corpus completeness বা population prevalence infer করা যাবে না। Conservative scope screens ও absent parent/generated evidence false negatives রাখতে পারে। একটি আগের rejection reason-এ placeholder rename বিষয়ে overstatement ধরা পড়েছিল; append-only final অপরিবর্তিত আছে এবং private limitation record রাখা হয়েছে। এটি missed-item risk; candidate পুনরায় খোলা হয়নি। Evidence: `summary_t50b.json`; `yield_t50.csv`; `key/review_decisions_t50.csv`; `key/t50b_placeholder_screen_limitation.json`; `triage_t50b.py`।

⚠️ Framework dispatch, validation, JSON serialization, persistence ও annotation-processor mapping static inference; upstream build, tests বা traffic reproduction হয়নি। Descriptive contract wording, missing declarations এবং optional-field semantics বিচারনির্ভর। Confidence ও inference notes private accepted evidence-এ আছে। একই operation-এর আলাদা field family পৃথক item হতে পারে; family granularity dedup composition প্রভাবিত করে। Evidence: `key/accepted_full_t50.csv:confidence,fix_family,proposition_check,inference_notes`; `review_t50.py:accept`; `finalize_t50b.py:audit`।

⚠️ Multiple operations from one fix এবং shared files স্বাধীন observation নয়। Per-fix cap দুই হলেও clustering আছে। Retained own-locator cross-item overlaps blind reading প্রভাবিত করতে পারে; eight-file cap সম্পূর্ণ runtime context নিশ্চিত করে না। Projection-এ document line numbers বদলায়; privacy redaction readability কমাতে পারে। Lexical privacy/leakage/licence scans সব semantic hint বা attribution শনাক্ত করার নিশ্চয়তা দেয় না; দুই preview incident বাস্তব সীমা দেখায়। Existing salt-এ full-set shuffle হওয়ায় archived round-2 Q-ID mapping বর্তমান package-এ প্রযোজ্য নয়। Evidence: `key/e13_build_log_t50b.json`; `key/e13_cross_item_audit_t50b.json`; `key/t50_superseded_round2/`; `key/e13_preview_privacy_incident.json`; `key/t50b_attribution_display_incident.json`।

কাজ সম্পূর্ণ offline: bare clones-এ read-only git --git-dir; network, checkout, upstream-content execution বা dependency install হয়নি। নিজস্ব Python ও synthetic tests চলেছে। Do-not-read তালিকা এবং board পড়া হয়নি; শেষে T50b-এর একটি Log line শুধু >> দিয়ে append করা হয়েছে। Evidence: `run_tests_t50b.py:read_boundary`; `final_audit_t50b.json:network_used,upstream_execution,board_read,prior_package_access`; `completion_t50b.json`।
