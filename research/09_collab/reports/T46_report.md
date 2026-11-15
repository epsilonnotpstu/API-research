# T46 — Offline corpus continuation ও parent-state package

T46-এ **২৯টি নতুন item** গৃহীত হয়েছে; T45-এর ১৬টি মিলিয়ে নতুন set **৪৫টি**। নতুন ২৯টি item এসেছে **২১টি candidate** থেকে এবং **২৬টি পৃথক repo–operation** জুড়ে। নতুন set ও আগের ২৫টি exploratory item মিশিয়ে **৭০-item blind package** পুনর্নির্মিত হয়েছে। Evidence: `08_experiments/E7_mining/summary2.json` (`accepted_T46`, `accepted_combined_new`); `key/new_accepted2.json`; `verification2.json` (`sets`, `source_tasks`)। এখানে ও নিচের সংক্ষিপ্ত `key/`, `yield2.csv`, `freeze2.json` ইত্যাদি path-এর base হলো `08_experiments/E7_mining/`।

## Frozen retrieval ও review

Final pool2-তে **১২,৬৩৭ candidate**, **৩৪ repo**। Correction cue এবং contract অথবা production behaviour surface—দুটির conjunction অপরিবর্তিত। Score `10 × cue_strength + operation_path_bit`; repo, score descending এবং SHA ascending-এ ranking হয়েছে। কোনও direction bonus বা direction balancing নেই। T42/T43/T45-এ accepted/rejected/deferred হওয়া **১,১১২টি repo–commit pair** বাদ গেছে। Evidence: `freeze2.json`; `mine2.py` (`reviewed`, `main`); `test_review2.py::test_ranking_and_prior_exclusions`।

Contract retrieval-এ extension-ভিত্তিক proxy ব্যবহার হয়নি। JSON root অথবা column-zero YAML mapping-এ OpenAPI/Swagger version scalar যাচাই করা হয়েছে; parent বা child-এ root থাকলেই যথেষ্ট। Root থেকে local `$ref` closure-এ পৌঁছানো fragment-ও contract surface। JVM source-এ Swagger/springdoc/springfox/Javalin OpenAPI imports ও সংশ্লিষ্ট annotation use যাচাই হয়েছে; Maven `@Parameter` এবং Spring-only `@RequestBody` যথেষ্ট নয়। Behaviour surface Java/Kotlin/Go production handler/controller/resource/route/model/DTO/validator/serializer/error-mapping paths। CI, `.github`, helm/k8s/docker/deploy/terraform, test/generated-client paths এবং configuration-only YAML বাদ দেওয়া হয়েছে। Spark instrumentation, operator/CLI/serde ও পরিচিত generated HTTP-client modules behaviour surface হয়নি। Docs-site source বাদ; content-verified OpenAPI document ও তার local references ব্যতিক্রম। Evidence: `mine2.py:22`–`classify`, `reachable`, `production`; `test_pool2.py`।

⚠️ Retrieval preflight-এ candidate preview এবং কিছু provisional parent evidence দেখা হয়েছিল। প্রথম filter-এ library/client paths, annotation-name collision ও configuration-এর `swagger` section false positive ছিল; সংশোধনের পর final pool2-তে review পুনরারম্ভ হয়েছে। Preliminary artefacts ও correction audit মুছে ফেলা হয়নি: `key/pool2_preflight/`, `key/pool2_preflight2/`, `key/pool2_content_validation/`, `key/retrieval_corrections.json`। সুতরাং final freeze-কে সম্পূর্ণ outcome-naive preregistration বলা যায় না। Usage reset-এর পর **কোনও re-freeze হয়নি**: pool, frozen sources ও freeze file-এর continuation hashes অপরিবর্তিত—`key/freeze2_continuation_guard.json`; `test_review2.py::test_frozen_bytes_unchanged_on_continuation`।

প্রতি repo-তে final rank-এর ধারাবাহিক prefix review হয়েছে। প্রত্যেক candidate-এর আলাদা status, একটি reason_code, সর্বোচ্চ ২৫-word নির্দিষ্ট reason, full sanitized patch path ও patch hash আছে। অনেক reason-এর rendering-এ সেই candidate-এর filename, title ও পৃথক source delta ব্যবহার হয়েছে; scope code ও investigated exceptions আলাদাভাবে নথিভুক্ত। **Range-level reason নেই।** Acceptance-এর জন্য neutral proposition, parent-only contract/implementation locators, resolving patch, confidence, contract kind এবং family রেকর্ড করা হয়েছে। IMPL acceptance-এ প্রত্যাশিত behaviour parent contract-এই থাকতে হয়েছে। Dedup হয়েছে exploratory ও T45 set-এর repo–operation–family অনুযায়ী; একই operation-এর আগের proposition-ও তুলনা করা হয়েছে। Evidence: `key/review_decisions2.csv` (১,২৫৯ data rows); `key/decide2.py`; `key/review2_notes.tsv`; `key/curate2.py`; `key/accepted_full.csv`; `test_review2.py`।

## Per-repo ফল

নিচে reviewed হলো T46 individual patch-screen count; accepted হলো item count, candidate count নয়। T45 column কেবল নতুন set-এর পূর্ববর্তী contribution। প্রতিটি row-এর evidence `yield2.csv`-এর নির্দেশিত data row এবং একই repo-র `pool2_inventory.json` record।

| Repo | pool2 | Reviewed | T46 accepted | T45 accepted | Combined new | CSV row |
|---|---:|---:|---:|---:|---:|---:|
| FAAAST-Service | 149 | 60 | 0 | 0 | 0 | 2 |
| Iced-Latte | 292 | 60 | 3 | 0 | 3 | 3 |
| OpenLineage | 3 | 3 | 0 | 0 | 0 | 4 |
| allure-server | 0 | 0 | 0 | 0 | 0 | 5 |
| apicurio-registry | 222 | 60 | 3 | 0 | 3 | 6 |
| basyx-java-server-sdk | 21 | 21 | 0 | 5 | 5 | 7 |
| bibliothek | 0 | 0 | 0 | 0 | 0 | 8 |
| catwatch | 5 | 5 | 0 | 0 | 0 | 9 |
| cwms-data-api | 177 | 50 | 4 | 2 | 6 | 10 |
| ditto | 906 | 60 | 0 | 1 | 1 | 11 |
| dockstore | 228 | 60 | 0 | 0 | 0 | 12 |
| eudi-srv-verifier-endpoint | 3 | 3 | 0 | 1 | 1 | 13 |
| fineract | 490 | 60 | 4 | 1 | 5 | 14 |
| genome-nexus | 4 | 4 | 0 | 0 | 0 | 15 |
| gravitee-api-management | 6564 | 60 | 1 | 1 | 2 | 16 |
| harbor | 711 | 60 | 0 | 0 | 0 | 17 |
| hivemq-edge | 125 | 60 | 0 | 0 | 0 | 18 |
| hydra | 182 | 60 | 0 | 0 | 0 | 19 |
| kapua | 1018 | 60 | 1 | 2 | 3 | 20 |
| kratos | 323 | 60 | 2 | 0 | 2 | 21 |
| microcks | 98 | 60 | 1 | 0 | 1 | 22 |
| nessie | 63 | 60 | 4 | 1 | 5 | 23 |
| ohsome-api | 19 | 19 | 0 | 0 | 0 | 24 |
| open-banking-gateway | 172 | 60 | 0 | 0 | 0 | 25 |
| pay-publicapi | 47 | 47 | 2 | 1 | 3 | 26 |
| polaris | 37 | 37 | 2 | 0 | 2 | 27 |
| quartz-manager | 9 | 9 | 0 | 0 | 0 | 28 |
| rhsm-subscriptions | 152 | 60 | 0 | 0 | 0 | 29 |
| service-api | 514 | 60 | 0 | 0 | 0 | 30 |
| session-service | 0 | 0 | 0 | 0 | 0 | 31 |
| sldt-digital-twin-registry | 9 | 9 | 0 | 0 | 0 | 32 |
| spring-batch-rest | 0 | 0 | 0 | 0 | 0 | 33 |
| strimzi-kafka-bridge | 50 | 32 | 2 | 1 | 3 | 34 |
| tiltaksgjennomforing-api | 44 | 0 | 0 | 0 | 0 | 35 |

**Stopping reason:** নতুন set-এর count ৪৫ হওয়ায় `strimzi-kafka-bridge`-এর rank ৩২-এর পরে review থেমেছে। `cwms-data-api` rank ৫০-এ combined ছয়-item cap ছুঁয়েছে। অন্য আগের repo-গুলি top ৬০ অথবা ছোট pool exhaustion পর্যন্ত গেছে; পরের `tiltaksgjennomforing-api`-তে review শুরু হয়নি। কোনও repo combined cap ছাড়ায়নি। Evidence: `yield2.csv:10`, `yield2.csv:34`, `yield2.csv:35`; `summary2.json`; `test_review2.py::test_stopping_caps_and_dedup`।

## Reason-code distribution

এটি candidate-level distribution; ACCEPT-এর ২১ candidate থেকে ২৯ item এসেছে। Evidence: `summary2.json` (`reason_code_counts`, `review_status_counts`); `key/review_decisions2.csv`।

| reason_code | Candidates |
|---|---:|
| ACCEPT | 21 |
| NOT_CONTRACT_RELATED | 375 |
| NEW_FEATURE_OR_ENDPOINT | 43 |
| REFACTOR_OR_RENAME | 389 |
| GENERATED_OR_DOCS_ONLY_CHURN | 142 |
| BOTH_CHANGED_TO_NEW_BEHAVIOUR | 109 |
| NO_PARENT_MISMATCH | 161 |
| TEST_OR_CLIENT_ONLY | 0 |
| TOO_LARGE_TO_ESTABLISH | 18 |
| OTHER | 1 |

Status totals: accepted **২১**, rejected **১,০৫৯**, deferred **১৭৯**। Deferred মানে mismatch অপ্রমাণিত বা bounded review-এ অতিরিক্ত বড়; negative ground truth নয়। সমস্ত rejected candidate-এর পূর্ণ parent pair তুলনা করা হয়েছে—এমন দাবি করা হচ্ছে না। Exact-parent gate acceptance-এর জন্য; অন্যগুলি individual patch triage। Evidence: `summary2.json`; `key/review_decisions2.csv` (`review_depth`)।

## কেবল aggregate direction counts

| Set | SPEC | IMPL | BOTH | Total |
|---|---:|---:|---:|---:|
| T46 new | 18 | 11 | 0 | 29 |
| T45 + T46 new | 26 | 18 | 1 | 45 |

Evidence: `summary2.json` (`T46_direction_counts`, `combined_new_direction_counts`)। কোনও item-wise direction বা history identifier এই report-এ নেই।

## Key, replacement ও verification

`set=new` রেখেই T46 rows যোগ হয়েছে; `source_task` column নতুন rows-এর T45/T46 উৎস আলাদা করে। **T45-এর ১৬টি source row byte-identical আছে**, এবং পুরোনো package key-এর **৪১টি logical row-এর সব পূর্ববর্তী column value** `key/corpus_key.csv`-এ অক্ষুণ্ণ আছে। Fresh shuffle-এর package IDs ও recomputed cross-item flags `key/e7_key.csv`-এ; `key/shuffle_mapping.csv` stable corpus IDs-কে নতুন package IDs-এর সঙ্গে যুক্ত করে। পুরোনো key, full rows, salt ও manifest-এর snapshot `key/t45_snapshot/`-এ। Evidence: `key/preservation_audit2.json`; `key/preserve_sources2.py`; `test_review2.py::test_T45_source_bytes_preserved`।

`build.py --replace` দিয়ে পুরোনো package প্রতিস্থাপিত হয়েছে। নতুন salt কেবল key directory-তে; old salt থেকে পার্থক্য এবং fresh X-shuffle যাচাই হয়েছে। `key/build_log.json.replacement_history`-তে explicit replace flag, **old package hash**, old build-log hash এবং new package hash আছে। পুরোনো package hash snapshot manifest-এর সঙ্গে মেলানো হয়েছে। Evidence: `09_collab/logs/T46_scratch/build_replace.txt`; `key/build_log.json` (`replacement_history`); `key/preservation_audit2.json`।

Final package: **৭০ item, ৪৯৮ file, ৬,৮৩৫,৬১৯ bytes**; **২৬২ contract file**, **২৩৪ implementation file**, সঙ্গে table ও README। Implementation locator files whole parent files; প্রতি item-এ সর্বোচ্চ আটটি implementation file। **৩টি** বড় specification projected; operation ও transitive local reference closure রাখা হয়েছে। **৪৩৬টি** delivered source file privacy redaction পেয়েছে। Parent locators, parent provenance, নিজের corresponding child content exclusion, message/history literals, verbatim proposition, forbidden words, reference projection এবং privacy/auth-fixture scans পাস করেছে। ১৫টি auth fixture-এর ৫৪ value variant scan হয়েছে। Published disk bytes deterministic parent reconstruction-এর সঙ্গে হুবহু মিলেছে। Evidence: `verification2.json`; `key/build_log.json` (`summary`, `assertions`, per-file hashes) ।

Cross-item check-এ **১৮ item flagged**। **৩৪টি locator-overlap incidence** নিজের locator হওয়ায় retained; এটি distinct-file count নয়। Actual package-এ optional cross-overlap file exclusion **০**; synthetic test-এ optional exclusion ও own-locator retention—দুই branch যাচাই হয়েছে। Eight-file cap-এর বাইরে **৮টি suggested helper occurrence** বাদ গেছে; required locator বাদ যায়নি। Remote `$ref` **০**। Evidence: `key/build_log.json` (`cross_item_pairs`, `omitted_helpers`, `remote_refs`); `verification2.json` (`summary`)।

**২৬টি test পাস**: পুরোনো ১৩টি build/leakage test, আটটি pool2/replacement/privacy test এবং পাঁচটি frozen-review/preservation audit test। CI/config YAML exclusion, OpenAPI inclusion, generated-client exclusion, annotation import verification, explicit replacement hash, determinism, parent-only provenance, forbidden words, overwrite refusal, cross-item rules ও T45 preservation অন্তর্ভুক্ত। Derived display-privacy correction-এর পর review audit আবার পাস করেছে; package bytes বদলায়নি। Evidence: `09_collab/logs/T46_scratch/test_results.txt`; `09_collab/logs/T46_scratch/test_review2.txt`; `test_build.py`; `test_pool2.py`; `test_review2.py`।

## Threats ও boundary

⚠️ Correction-cue vocabulary, static server-module/path heuristics এবং bounded prefix sampling coverage সীমিত করে। Root discovery cue-history ও current-tip roots ব্যবহার করেছে; পুরোনো, আর tip-এ নেই এবং কোনও cue edit-এ আসেনি—এমন root বাদ পড়তে পারে। API annotations-এর schema defaults, inherited Bean Validation, serialization ও exception behaviour static inference; runtime request চালানো হয়নি। Per-item confidence ও inference notes key-তে আছে। Full parent analysis না-করা rejection codes search triage হিসেবে পড়তে হবে। Evidence: `mine2.py`; `key/accepted_full.csv`; `key/review_decisions2.csv`।

⚠️ Item count স্বাধীন observations-এর count নয়: একই candidate একাধিক operation বা আলাদা mismatch facet দিতে পারে; একই parent file বিভিন্ন item-এ পুনরাবৃত্ত। New ৪৫ মানে ৪৫টি স্বাধীন history event নয়। Cross-item locator retention-ও item independence নিশ্চিত করে না। কিছু generated runtime interface বা dependency source clone-এ নেই; এ ধরনের incomplete pair defer করা হয়েছে। Salt shuffle repository/model memorisation দূর করে না; আট-file cap context সীমিত করে। Lexical privacy scan সব personal name বা semantic leakage শনাক্ত করার নিশ্চয়তা দেয় না। Evidence: `key/new_accepted2.json`; `key/accepted_full.csv`; `key/build_log.json`; `key/review2_overrides.json`।

একটি পুরোনো title-এর attribution handle screen-এ বেরিয়েছিল। Title display filter সংশোধিত; derived reason ও saved screen headings sanitize হয়েছে। Frozen source metadata পরিবর্তন করা হয়নি, তাই তার hash অক্ষুণ্ণ। Package-এ title/message নেই; OpenAPI contact metadata-ও line-preserving ভাবে redact করা হয়েছে। Evidence: `key/display_privacy_audit2.json`; `inspect2.py`; `draft2.py`; `build.py::sanitize`; `test_pool2.py`।

কাজ সম্পূর্ণ offline। Upstream থেকে শুধু read-only Git object/history পড়া হয়েছে; checkout, build, upstream-code execution বা network ব্যবহার হয়নি। শুধু project-owned Python ও standard-library tests চলেছে; synthetic Git writes অস্থায়ী artificial test repos-এ সীমিত। Board পড়া হয়নি; task শেষে একটিমাত্র Log line shell append করা হয়েছে। Evidence: `mine.py::git`; `mine2.py::objects`; `build.py`; `test_build.py::ArtificialRepo`; `09_collab/logs/T46_scratch/completion.json`।
