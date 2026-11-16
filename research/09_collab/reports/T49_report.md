# T49 — frozen pool2 continuation ও পৃথক U-package

Evidence paths: নিচে সংক্ষিপ্ত script/JSON/CSV নাম এবং `key/`-এর ভিত্তি `08_experiments/E7_mining/`; `final_audit.json` ও test summaries-এর ভিত্তি `09_collab/logs/T49_scratch/`। `E2_labelling/`-এর ভিত্তি `08_experiments/`। Function name, JSON field ও CSV repo row দিয়ে সংশ্লিষ্ট evidence চিহ্নিত করা হয়েছে।

T49 সম্পন্ন: **949 candidates**-এর final decision থেকে **24 accepted candidates / 36 items** পাওয়া গেছে। 40-এর আগে থামার কারণ: প্রতিটি eligible repo capped অথবা exhausted। Frozen pool2-তে 34 repo / 12,637 candidates আছে; এই continuation-এ ছয় repo-তে নতুন review হয়েছে। শেষে সব repo মিলিয়ে 14 capped এবং 20 exhausted। Evidence: `08_experiments/E7_mining/summary_t49.json` (`reviewed`, `accepted_candidates`, `accepted_T49`, `stopping_reason`); `08_experiments/E7_mining/yield_t49.csv` (repo rows)।

`yield_t48.csv:last_reviewed_rank + 1` থেকে একই repo order-এ rank অনুযায়ী review হয়েছে; নতুন rank limit বা retrieval চালানো হয়নি। Combined T45–T49 cap 10। প্রতিটি accepted candidate-এর সব প্রতিষ্ঠিত operation-এর `METHOD path` UTF-8/plain byte order-এ সাজিয়ে প্রথম দুইটি রাখা হয়েছে; repo-তে কম slot থাকলে সেই prefix আরও ছোট হতো। Selection function direction, confidence বা অন্য item property পড়ে না। প্রতিটি candidate-এর final decision পরবর্তী candidate খোলার আগে লেখা হয়েছে। ⚠️ এটি static parent contract/implementation ও resolving patch comparison; runtime execution হয়নি। Evidence: `09_collab/tasks/T49.md` requirements 1–4; `08_experiments/E7_mining/review_t49.py:plan`, `select_operations`, `require_current`; `finalize_t49.py:audit`।

নিচে সব repo দেখানো হয়েছে; `reviewed_T49` শূন্য হলে পূর্বের cap বা exhaustion-এর কারণে নতুন review হয়নি। প্রতিটি row-এর সরাসরি evidence `08_experiments/E7_mining/yield_t49.csv:repo`।

| Repo | T48 শেষ rank | T49 reviewed | শেষ rank | আগের items | T49 items | Combined | Stop |
|---|---:|---:|---:|---:|---:|---:|---|
| FAAAST-Service | 149 | 0 | 149 | 0 | 0 | 0 | available pool exhausted |
| Iced-Latte | 194 | 0 | 194 | 10 | 0 | 10 | combined repo cap |
| OpenLineage | 3 | 0 | 3 | 0 | 0 | 0 | available pool exhausted |
| allure-server | 0 | 0 | 0 | 0 | 0 | 0 | available pool exhausted |
| apicurio-registry | 155 | 0 | 155 | 10 | 0 | 10 | combined repo cap |
| basyx-java-server-sdk | 21 | 0 | 21 | 5 | 0 | 5 | available pool exhausted |
| bibliothek | 0 | 0 | 0 | 0 | 0 | 0 | available pool exhausted |
| catwatch | 5 | 0 | 5 | 0 | 0 | 0 | available pool exhausted |
| cwms-data-api | 146 | 0 | 146 | 10 | 0 | 10 | combined repo cap |
| ditto | 150 | 491 | 641 | 1 | 9 | 10 | combined repo cap |
| dockstore | 150 | 73 | 223 | 5 | 5 | 10 | combined repo cap |
| eudi-srv-verifier-endpoint | 3 | 0 | 3 | 1 | 0 | 1 | available pool exhausted |
| fineract | 80 | 0 | 80 | 10 | 0 | 10 | combined repo cap |
| genome-nexus | 4 | 0 | 4 | 0 | 0 | 0 | available pool exhausted |
| gravitee-api-management | 150 | 50 | 200 | 6 | 4 | 10 | combined repo cap |
| harbor | 150 | 28 | 178 | 4 | 6 | 10 | combined repo cap |
| hivemq-edge | 125 | 0 | 125 | 0 | 0 | 0 | available pool exhausted |
| hydra | 107 | 0 | 107 | 10 | 0 | 10 | combined repo cap |
| kapua | 114 | 0 | 114 | 10 | 0 | 10 | combined repo cap |
| kratos | 121 | 0 | 121 | 10 | 0 | 10 | combined repo cap |
| microcks | 98 | 0 | 98 | 1 | 0 | 1 | available pool exhausted |
| nessie | 63 | 0 | 63 | 5 | 0 | 5 | available pool exhausted |
| ohsome-api | 19 | 0 | 19 | 0 | 0 | 0 | available pool exhausted |
| open-banking-gateway | 150 | 22 | 172 | 3 | 2 | 5 | available pool exhausted |
| pay-publicapi | 47 | 0 | 47 | 3 | 0 | 3 | available pool exhausted |
| polaris | 37 | 0 | 37 | 2 | 0 | 2 | available pool exhausted |
| quartz-manager | 9 | 0 | 9 | 0 | 0 | 0 | available pool exhausted |
| rhsm-subscriptions | 104 | 0 | 104 | 10 | 0 | 10 | combined repo cap |
| service-api | 150 | 285 | 435 | 0 | 10 | 10 | combined repo cap |
| session-service | 0 | 0 | 0 | 0 | 0 | 0 | available pool exhausted |
| sldt-digital-twin-registry | 9 | 0 | 9 | 0 | 0 | 0 | available pool exhausted |
| spring-batch-rest | 0 | 0 | 0 | 0 | 0 | 0 | available pool exhausted |
| strimzi-kafka-bridge | 45 | 0 | 45 | 10 | 0 | 10 | combined repo cap |
| tiltaksgjennomforing-api | 44 | 0 | 44 | 0 | 0 | 0 | available pool exhausted |

Accepted candidates-এর মধ্যে 12টি থেকে একটি করে এবং 12টি থেকে দুইটি করে item রাখা হয়েছে। Cap-এর আগে valid operations-এর histogram: 12 candidates × 1, 6 × 2, 2 × 3, 2 × 4, 1 × 6, 1 × 37 = 81 operations। অতিরিক্ত **45 operations**-এ `review_status=accepted_capped`, `reason_code=FIX_CAP`; `REPO_CAP` exclusions 0। Candidate final rows 949 এবং cap-exclusion rows 45—মোট 994 rows private decision CSV-তে আছে। Evidence: `summary_t49.json:items_per_accepted_candidate`, `valid_operations_per_accepted_candidate`, `FIX_CAP_exclusions`; `key/review_decisions_t49.csv:review_status,reason_code`; `finalize_t49.py:audit`।

Candidate-level `reason_code` distribution নিচে; `ACCEPT` candidates গণনা করে, items নয়। Cap exclusions আলাদাভাবে উপরে দেওয়া হয়েছে। Evidence: `summary_t49.json:reason_code_counts,review_status_counts`; candidate statuses: accepted 24, rejected 818, deferred 107।

| reason_code | Candidates |
|---|---:|
| ACCEPT | 24 |
| BOTH_CHANGED_TO_NEW_BEHAVIOUR | 13 |
| GENERATED_OR_DOCS_ONLY_CHURN | 66 |
| NEW_FEATURE_OR_ENDPOINT | 16 |
| NOT_CONTRACT_RELATED | 649 |
| NO_PARENT_MISMATCH | 87 |
| OTHER | 30 |
| REFACTOR_OR_RENAME | 43 |
| TEST_OR_CLIENT_ONLY | 1 |
| TOO_LARGE_TO_ESTABLISH | 20 |

Direction শুধু aggregate হিসেবে: T49 **SPEC 20, IMPL 16, BOTH 0**। T45–T49 নতুন set মিলিয়ে 162 items: SPEC 90, IMPL 71, BOTH 1। Direction target বা balancing করা হয়নি। Evidence: `summary_t49.json:T49_direction_counts,combined_new_direction_counts`; cap selection-এর regression tests `test_t49.py:CapRegressionTests`। Per-item direction, fix identifiers ও ID mapping কেবল `key/`-তে রাখা হয়েছে।

পৃথক package `08_experiments/E2_labelling/e12_blind/`-এ শুধু **U01–U36** আছে। `items.csv`-এর চারটি column `item_id,repo,operation,proposition`; propositions private accepted rows থেকে verbatim। প্রত্যেক item-এর `contract/` ও `impl/` আছে; README-এর bytes T48 builder-এর README-এর সমান। Fresh salt এবং mapping কেবল `key/e12_shuffle_salt.txt`, `key/e12_shuffle_mapping.csv`-তে। নতুন `key/e12_key.csv`-এর columns `e10_key.csv`-এর সমান; `key/accepted_full_t49.csv`-এর columns `accepted_full_t48.csv`-এর সমান এবং `candidate_id` আছে; সব নতুন row-এ `set=new`, `source_task=T49`। Evidence: `build_t49.py:prepare,full_bytes,publish`; `test_t49.py:ContinuationTests`।

Package size **197 files / 4,243,434 bytes (4.05 MiB)**: contract 54, implementation 141, table ও README 2 files। বড় spec-এর operation/reference projection 7 files; privacy/history/metadata redaction হয়েছে 178 files-এ। Implementation files সর্বোচ্চ আটটি/item; own parent locator files retained। কিছু generated spec path-এ API mount prefix expanded থাকায় একটিমাত্র literal suffix match পাওয়া গেলে সেই পূর্ণ spec path-এর operation project করা হয়েছে; ambiguous match reject হয়। Parent source phrase পরে commit subject হিসেবে ব্যবহৃত থাকলে phrase-টিও redacted; leakage scanner শিথিল করা হয়নি। Evidence: `verification_t49.json:summary,checks`; `build_t49.py:project_yaml,prepare`; `test_t49.py:SyntheticSeparationTests`।

Cross-item check exploratory 25 + T45–T48 126 + T49 36 = **187 items** জুড়ে হয়েছে। নতুন package-এ flagged items 16, excluded path incidents 22, retained own-locator overlap incidents 53। Actual manifests-এর independent audit-এ মোট pair incidents 158, U-তে incoming 43, U থেকে prior package-এ incidents 10; অতিরিক্ত prior-item flags 4। পুরোনো key না বদলে পূর্ণ side audit private `key/e12_cross_item_all.json`-এ আছে। Evidence: `verification_t49.json:summary`; `09_collab/logs/T49_scratch/final_audit.json:cross_item_audit`; `cross_audit_t49.py:main`।

Local contract file reference incidents 148; mandatory cross-item exclusions-এর ফলে 2 items-এ 24 references-এর target অনুপস্থিত। প্রতিটি missing target excluded cross-item path-এর মধ্যে পড়ে। Remote reference incidents 0। ⚠️ ফলে ওই excerpt closures সম্পূর্ণ self-contained নয়; blind reading-এ এই সীমাবদ্ধতা বিবেচ্য। Evidence: `key/e12_reference_audit.json:missing_references`; `final_audit.json:reference_audit`; `test_t49.py:test_all_generation_cross_flags_and_reference_exclusions`।

সব **73 tests pass**: earlier tests 52 + T49 tests 21; failures 0, errors 0। পুরোনো package tests T47/T48-এর isolated reconstruction-এ চলে; test process-এর audit hook অন্য labelling package-এ open/list/scandir আটকায়। Synthetic Git fixtures কেবল নিজেদের test directories-এ; upstream bare clones read-only। Independent reconstruction-এ delivered bytes, key, full CSV, mapping ও build log মিলে গেছে। Parent provenance, own-child exclusion, message/history scan, forbidden words, privacy, cross-item exclusion, verbatim propositions ও আট-file cap checks pass। Evidence: `09_collab/logs/T49_scratch/test_summary_02.json`; `verification_t49.json:checks`; `run_tests_t49.py:read_boundary`; raw diagnostics private `key/e12_test_run_*.txt`।

Task শুরুর **8,853 existing key files** এবং ছয়টি recorded freeze/continuation input—মোট **8,859 files**—before/after SHA-256-এ byte-identical; changed files 0। `freeze2.json`-এর pool/source/code hashes-ও actual files-এর সঙ্গে মেলে। Old keys ও frozen pool2 বদলানো হয়নি; অন্য blind packages বা board পড়া হয়নি। Old keys পড়া হয়েছে authorized preservation/build/dedup কাজে। Board-এর কাজ কেবল task শেষে একটিমাত্র completion Log append (`>>`); board row edit করা হয়নি। Evidence: `key/preservation_t49_start.json`, `key/preservation_t49_after.json`; `final_audit.json:existing_files_checked,changed_existing_files,board_read`; `09_collab/logs/T49_scratch/completion.json`; `finalize_t49.py:audit`; `09_collab/tasks/T49.md` board override।

Preview ledger: **2,473 events / 949 candidates**; outside-final-prefix 0, without-final-decision 0, lookahead-before-prior-decision 0। Chronological sequence এবং final-prefix membership pass। 726 candidates conservative static triage-এর মাধ্যমে final হয়েছে; বাকি 223-এ অতিরিক্ত model patch review হয়েছে। Accepted candidates-এ exact parent locators ও resolving patch evidence private আছে। Stop-এর পরে পরের candidate evidence access Git read বা preview write-এর আগেই reject হয়। Evidence: `summary_t49.json:preview_record,conservative_static_triage,additional_model_patch_reviews`; `key/t49_previews/`; `finalize_t49.py:validate_previews`; `test_t49.py:test_real_preview_ledger_and_stopped_guard`।

একটি early legacy patch preview-তে credential-সদৃশ encoded literal দেখা গিয়েছিল। Display filter-এ long encoded quoted literals এবং credential assignments suppression যোগ হয়েছে; synthetic regression pass। Value এখানে পুনরাবৃত্তি করা হয়নি। অতিরিক্ত exact/decoded/escaped variant scan-এ delivered 197 files-এর কোনোটিতে observed value পাওয়া যায়নি (3 variants checked)। এই incident-এর কারণে preview privacy-কে ত্রুটিহীন বলা যায় না। Evidence: `key/e12_preview_privacy_incident_audit.json`; `final_audit.json:preview_privacy_incident`; `review_t49.py:display`; `test_t49.py:test_preview_display_suppresses_encoded_and_credential_literals`।

⚠️ Threats: correction-cue retrieval ও historical availability selection bias তৈরি করে; frozen pool বা byte-order cap direction না পড়লেও repo caps এবং method/path ordering sample composition বদলায়। 726 rule-triaged candidates পূর্ণ manual parent comparison পায়নি; deferred 107-এর মধ্যে missing/ambiguous contracts এবং বড় patches আছে। Generated external models অনুপস্থিত থাকলে acceptance করা হয়নি। Accepted conclusions static framework dispatch, validation, serialization ও persistence inference; কোনো runtime reproduction বা external-code execution হয়নি। একই candidate-এর একাধিক operation এবং shared helpers স্বাধীন observations নয়; per-fix cap দুই হলেও clustering রয়ে গেছে। Cross-item own-locator exceptions এবং missing references blind readers-কে প্রভাবিত করতে পারে। Privacy/metadata redaction source readability কমাতে পারে। Aggregate directions এই selected corpus-এর ফল; population prevalence বা independent-fix rate হিসেবে ব্যবহারযোগ্য নয়। Evidence: `summary_t49.json`; `verification_t49.json`; `key/e12_cross_item_all.json`; `key/e12_reference_audit.json`; `final_audit.json`; `09_collab/tasks/T49.md` constraints।

Required deliverables: `key/e12_key.csv`, `key/accepted_full_t49.csv`, `key/review_decisions_t49.csv`, `yield_t49.csv`, `E2_labelling/e12_blind/`, T49 scripts/tests, preservation/verification audits এবং এই report। কোনো blocker বাকি নেই; ভবিষ্যৎ runtime validation বা blind labelling এই task-এর বাইরে। Evidence: উল্লিখিত artifacts এবং passing test/audit records।
