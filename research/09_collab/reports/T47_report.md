# T47 — Frozen pool2 continuation ও পৃথক W package

T47-এ **৮৫৩টি candidate-এর individual review থেকে ৪১টি নতুন item** গৃহীত হয়েছে; accepted candidate **২৬টি**। T45/T46-এর ৪৫টি মিলিয়ে নতুন corpus এখন **৮৬টি item**। T47-এর জন্য পৃথক **W01–W41** package তৈরি হয়েছে। Evidence: `08_experiments/E7_mining/summary_t47.json` (`reviewed`, `accepted_T47`, `accepted_candidates`, `accepted_combined_new`); `08_experiments/E7_mining/verification_t47.json` (`summary.items`)। নিচের সংক্ষিপ্ত path-গুলোর base হলো `08_experiments/E7_mining/`।

Frozen pool2 **পুনরায় freeze করা হয়নি**। Task শুরুর baseline ও final comparison-এ `pool2.json`, `freeze2.json`, `mine2.py` এবং private frozen source-এর bytes অপরিবর্তিত। বিদ্যমান `key/`-এর **৪,৩৬৩টি file** একই SHA-256 রেখেছে; এর মধ্যে `e7_key.csv`, `corpus_key.csv`, `accepted_full.csv` আছে। নতুন salt, mapping, decisions ও accepted rows কেবল নতুন private file-এ লেখা হয়েছে। Evidence: `key/preservation_t47_start.json`; `key/preservation_t47_final.json` (`unchanged`, `existing_key_files`, `hashes`); `test_t47.py::ContinuationTests.test_every_preexisting_private_file_and_frozen_file_is_preserved`।

প্রতি repo-তে T46-এর প্রথম unreviewed pool2 rank থেকে ধারাবাহিক final decision হয়েছে। Acceptance gate অপরিবর্তিত: existing operation, parent-only contract ও implementation locators, resolving patch, confidence, contract kind, mismatch/family এবং neutral proposition। Proposition-এর রূপ `<METHOD> <path>: contract says <X>; implementation does <Y>`; published table-এ তা verbatim আছে। IMPL acceptance-এর প্রত্যাশিত আচরণ parent contract-এ প্রতিষ্ঠা করা হয়েছে। Dedup identity হলো repo + operation + fix family; exploratory set এবং সব T45/T46 item-ও তুলনায় আছে। Direction বা অন্য property অনুযায়ী quota/balancing নেই। Evidence: `review_t47.py::accept`; `finalize_t47.py::audit`; `key/review_decisions_t47.csv`; `key/accepted_full_t47.csv`; `verification_t47.json` (`checks.verbatim_propositions`)।

প্রতি candidate-এর নিজস্ব `review_status`, `reason_code`, সর্বোচ্চ ২৫-word specific reason, sanitized patch path, patch hash এবং review-depth record আছে। Range দিয়ে CLI-তে কিছু code দেওয়া হলেও output-এ প্রত্যেক candidate-এর আলাদা filename/title/source-delta-ভিত্তিক reason তৈরি হয়েছে; range-level decision row নেই। Acceptance-এর জন্য বিস্তারিত parent comparison, অন্যগুলোর জন্য bounded individual patch screen হয়েছে। Evidence: `review_t47.py::decide`; `key/review_decisions_t47.csv` (৮৫৩ data row); `test_t47.py::ContinuationTests.test_rank_order_stopping_reasons_caps_and_dedup`।

Per-repo table-এ reviewed হলো **T47 candidate count**, accepted হলো **T47 item count**। পূর্বের column কেবল T45/T46 accepted item; শেষ rank-এ আগের T46 prefix-ও অন্তর্ভুক্ত। প্রতিটি row-এর evidence `yield_t47.csv`-এর নির্দেশিত line।

| Repo | T47 reviewed | T47 accepted | পূর্বের accepted | Combined | শেষ pool2 rank | CSV line |
|---|---:|---:|---:|---:|---:|---:|
| FAAAST-Service | 89 | 0 | 0 | 0 | 149 | 2 |
| Iced-Latte | 90 | 5 | 3 | 8 | 150 | 3 |
| OpenLineage | 0 | 0 | 0 | 0 | 3 | 4 |
| allure-server | 0 | 0 | 0 | 0 | 0 | 5 |
| apicurio-registry | 90 | 5 | 3 | 8 | 150 | 6 |
| basyx-java-server-sdk | 0 | 0 | 5 | 5 | 21 | 7 |
| bibliothek | 0 | 0 | 0 | 0 | 0 | 8 |
| catwatch | 0 | 0 | 0 | 0 | 5 | 9 |
| cwms-data-api | 96 | 4 | 6 | 10 | 146 | 10 |
| ditto | 90 | 0 | 1 | 1 | 150 | 11 |
| dockstore | 90 | 5 | 0 | 5 | 150 | 12 |
| eudi-srv-verifier-endpoint | 0 | 0 | 1 | 1 | 3 | 13 |
| fineract | 20 | 5 | 5 | 10 | 80 | 14 |
| genome-nexus | 0 | 0 | 0 | 0 | 4 | 15 |
| gravitee-api-management | 90 | 4 | 2 | 6 | 150 | 16 |
| harbor | 90 | 4 | 0 | 4 | 150 | 17 |
| hivemq-edge | 65 | 0 | 0 | 0 | 125 | 18 |
| hydra | 43 | 9 | 0 | 9 | 103 | 19 |
| kapua | 0 | 0 | 3 | 3 | 60 | 20 |
| kratos | 0 | 0 | 2 | 2 | 60 | 21 |
| microcks | 0 | 0 | 1 | 1 | 60 | 22 |
| nessie | 0 | 0 | 5 | 5 | 60 | 23 |
| ohsome-api | 0 | 0 | 0 | 0 | 19 | 24 |
| open-banking-gateway | 0 | 0 | 0 | 0 | 60 | 25 |
| pay-publicapi | 0 | 0 | 3 | 3 | 47 | 26 |
| polaris | 0 | 0 | 2 | 2 | 37 | 27 |
| quartz-manager | 0 | 0 | 0 | 0 | 9 | 28 |
| rhsm-subscriptions | 0 | 0 | 0 | 0 | 60 | 29 |
| service-api | 0 | 0 | 0 | 0 | 60 | 30 |
| session-service | 0 | 0 | 0 | 0 | 0 | 31 |
| sldt-digital-twin-registry | 0 | 0 | 0 | 0 | 9 | 32 |
| spring-batch-rest | 0 | 0 | 0 | 0 | 0 | 33 |
| strimzi-kafka-bridge | 0 | 0 | 3 | 3 | 32 | 34 |
| tiltaksgjennomforing-api | 0 | 0 | 0 | 0 | 0 | 35 |

**Stopping reason:** hydra-র rank **১০৩**-এর candidate review সম্পূর্ণ হওয়ার পরে T47 count **৪১**, অর্থাৎ ≥৪০। সেই candidate থেকে তিনটি related operation-এর proposition গৃহীত হওয়ায় threshold অতিক্রম করেছে। পরবর্তী repo-তে T47 review শুরু হয়নি। CWMS rank ১৪৬ এবং Fineract rank ৮০-তে combined ten-item cap ছুঁয়েছে; অন্য preceding repo-গুলি rank ১৫০ বা ছোট pool exhaustion পর্যন্ত গেছে। Evidence: `summary_t47.json` (`stopping_reason`, `final_repo`, `final_rank`); `yield_t47.csv:10`, `yield_t47.csv:14`, `yield_t47.csv:19`; `finalize_t47.py::audit`।

Reason-code distribution candidate-level; ACCEPT-এর ২৬ candidate থেকে ৪১ item এসেছে। Evidence: `summary_t47.json` (`reason_code_counts`, `review_status_counts`)।

| reason_code | Candidates |
|---|---:|
| ACCEPT | 26 |
| NOT_CONTRACT_RELATED | 69 |
| NEW_FEATURE_OR_ENDPOINT | 45 |
| REFACTOR_OR_RENAME | 139 |
| GENERATED_OR_DOCS_ONLY_CHURN | 69 |
| BOTH_CHANGED_TO_NEW_BEHAVIOUR | 27 |
| NO_PARENT_MISMATCH | 431 |
| TEST_OR_CLIENT_ONLY | 7 |
| TOO_LARGE_TO_ESTABLISH | 39 |
| OTHER | 1 |

Status totals: accepted **২৬**, rejected **৩৫৭**, deferred **৪৭০**। Deferred-এর অর্থ bounded review-এ parent discrepancy প্রতিষ্ঠিত হয়নি; এগুলো negative ground truth নয়। Evidence: `summary_t47.json` (`review_status_counts`); `key/review_decisions_t47.csv` (`review_depth`)।

কেবল aggregate direction counts নিচে দেওয়া হলো। Evidence: `summary_t47.json` (`T47_direction_counts`, `combined_new_direction_counts`)।

| Set | SPEC | IMPL | BOTH | Total |
|---|---:|---:|---:|---:|
| T47 new | 23 | 18 | 0 | 41 |
| T45 + T46 + T47 new | 49 | 36 | 1 | 86 |

নতুন package হলো `08_experiments/E2_labelling/e8b_blind/`। এতে শুধু W01–W41, `items.csv`-এর চারটি column `item_id,repo,operation,proposition`, প্রতি item-এর `contract/` ও `impl/`, এবং README আছে। `key/e8b_key.csv`-তে পুরোনো package-key schema, `set=new`, `source_task=T47`; full evidence `key/accepted_full_t47.csv`-তে। Fresh salt ও stable-source-to-W mapping শুধু private directory-তে আছে। নতুন publisher existing destination বা key file পেলে overwrite প্রত্যাখ্যান করে। `e7_blind/` খোলা, rebuild বা replace করা হয়নি। Evidence: `build_t47.py:17`, `build_t47.py::w_order`, `build_t47.py::publish`; `test_t47.py::ContinuationTests.test_real_package_contains_only_new_W_rows`; `test_t47.py::SyntheticSeparationTests.test_new_publisher_refuses_overwrite_and_preserves_old_key_sentinels`।

Package size **৪১ item, ২৩৪ file, ৬,১৯৩,৫৬৪ bytes**: **৫১ contract file**, **১৮১ implementation file**, table ও README। **১৬০টি source file** privacy/history redaction পেয়েছে; projection **০**, remote `$ref` **০**। Implementation files whole parent files; সর্বোচ্চ আটটি implementation file-এর cap বজায় আছে। ওই cap-এর বাইরে **৩২টি suggested helper occurrence** বাদ গেছে; required locator বাদ যায়নি। Parent reconstruction-এর সঙ্গে published disk bytes ও নতুন key/full/mapping হুবহু মিলে গেছে। Evidence: `verification_t47.json` (`summary`, `checks`); `key/e8b_build_log.json` (`items.files`, `items.omitted_helpers`, `items.remote_refs`, `package_hashes`); `build_t47.py:116`।

Cross-item check-এ exploratory ২৫ + T45/T46 ৪৫ + T47 ৪১, মোট **১১১টি item** ছিল। নতুন package-এর **১০টি W item flagged**; **১৪টি own-locator overlap incidence** retained, optional overlapping file exclusion **০**। Actual delivered manifests-এর independent all-pairs audit-এ মোট **৫৭ pair incidence**, **৩৩ flagged item**; নতুন item থেকে পুরোনো **৬টি item**-এ **১০টি incoming overlap incidence**, যার মধ্যে পুরোনো frozen flags-এর অতিরিক্ত **৫টি item** flagged হয়। এই নতুন সম্পর্কগুলি শুধু নতুন private audit-এ আছে; পুরোনো key বা package বদলানো হয়নি। Evidence: `verification_t47.json` (`summary`); `key/e8b_build_log.json` (`cross_item_pairs`); `key/e8b_cross_item_all.json` (`all_pairs`, `newly_affected_prior_items`, `summary`); `cross_audit_t47.py::main`।

**৩৬টি test পাস**: পূর্বের ২৬টি এবং T47-এর ১০টি। Existing-key/freeze preservation, ranked prefix/caps/dedup, deterministic W shuffle, package separation, new overwrite refusal, synthetic earlier-item-to-W overlap exclusion, own-locator retention এবং forbidden-word/privacy assertions অন্তর্ভুক্ত। Production reconstruction-এ parent provenance, corresponding child-content exclusion, message/history-literal checks, verbatim propositions এবং whole implementation checks পাস করেছে। T44 scans-এ **১৫টি auth fixture-এর ৫৪টি value variant** ব্যবহৃত হয়েছে। Evidence: `09_collab/logs/T47_scratch/test_results_final_code.txt`; `test_t47.py`; `verification_t47.json` (`checks`, `auth_fixtures`, `auth_value_variants`)।

⚠️ Threats: frozen retrieval-এর correction-cue ও path heuristics, bounded prefix sampling এবং এই acceptance threshold coverage সীমিত করে। অন্য repo-তে T47 review না-হওয়া zero-yield evidence নয়। Annotation inference, date representation, validation inheritance, scoped-resource semantics এবং writer/exception behaviour static source comparison থেকে বোঝা হয়েছে; upstream request চালানো হয়নি। Field-specific schema correction বা একই patch-এর একাধিক operation স্বাধীন observation নয়; shared candidate/file context ও cross-item overlap রয়ে গেছে। Eight-file cap কিছু dependency context সীমিত করতে পারে। Evidence: `key/accepted_full_t47.csv` (`confidence`, `inference_notes`, `proposition_check`); `key/e8b_cross_item_all.json`; `yield_t47.csv`।

⚠️ Advance patch preview final decision prefix-এর বাইরে **৪১টি candidate**-ও দেখেছিল: CWMS ৪, Fineract ৩৫, hydra ২। এগুলোর final review/acceptance record নেই; final stopping audit কেবল নির্ধারিত contiguous prefix গুনেছে। সুতরাং final-prefix review-কে সম্পূর্ণ preview-free বলা যায় না। Frozen pool ও ranking বদলায়নি। Evidence: `summary_t47.json` (`previews_outside_final_decision_prefix`); `finalize_t47.py::audit`; `key/t47_evidence/`।

Privacy boundary incident: একটি পুরোনো title-এ attribution-সদৃশ wording screen-এ দেখা গিয়েছিল। Display filter সেই pattern-এর জন্য প্রসারিত করা হয়েছে; private frozen metadata বা পূর্বের file বদলানো হয়নি। ৮৫৩টি reason-এর T44 privacy check পাস করেছে; package-এ title/message নেই। ⚠️ Lexical scans সব personal name বা semantic leakage শনাক্ত করার নিশ্চয়তা দেয় না। Evidence: `review_t47.py::display`; `key/display_privacy_t47.json`; `verification_t47.json` (`checks.message_scan`, `checks.privacy_and_auth_fixture_values`)।

কাজ offline: upstream থেকে কেবল read-only `git --git-dir` object/history access; upstream checkout/build/execution ও network ব্যবহার হয়নি। নিজস্ব Python এবং synthetic bare-repo tests চলেছে। Board পড়া হয়নি; task-এর শেষে একটিমাত্র Log line `>>` দিয়ে append করা হয়েছে। কোনও per-item direction বা fix identifier report/package-এ রাখা হয়নি। Evidence: `mine.py::git`; `build.py::prepare`; `build_t47.py::publish`; `09_collab/logs/T47_scratch/completion.json`; `09_collab/tasks/T47.md`।
