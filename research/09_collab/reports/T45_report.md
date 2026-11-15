# T45 — offline mining ও parent-state excerpt package

নতুন **১৬টি** real contract-alignment item গৃহীত হয়েছে। আগের exploratory **২৫টি** item-সহ প্রকাশিত excerpt package-এ **৪১টি** item আছে। নতুন set-এর aggregate direction: **SPEC ৮ / IMPL ৭ / BOTH ১**। ৪৫টি নতুন acceptance-এর threshold পূরণ হয়নি; নির্ধারিত review-depth stopping rule-এ এই run শেষ হয়েছে। Evidence: `08_experiments/E7_mining/summary.json` এবং `verification.json`-এর `sets`, `new_direction_counts`। কোনো per-item direction বা history identifier এই report-এ দেওয়া হয়নি।

শুধু অনুমোদিত protocol, task, pipeline, metadata ও input CSV পড়া হয়েছে; board পড়া হয়নি। ১২টি নতুন bare clone-এর সবগুলো পাওয়া গেছে। Mining-এর scope-এ ছিল ওই ১২টি এবং আগে ব্যবহৃত ২২টি bare repo, মোট ৩৪টি। Working-clone-ভিত্তিক exploratory item-এর source প্রয়োজনমতো শুধু recorded parent থেকে নেওয়া হয়েছে। Evidence: `09_collab/tasks/T45.md`; `08_experiments/E7_mining/inventory.json`; `mine.py:59`; private build provenance।

Retrieval-এ correction cue এবং সম্ভাব্য contract/behaviour path ব্যবহার করা হয়েছে। Score হলো `10 × cue_strength + operation_path_bit`; strong alignment/error cue-এর strength ৩, correction cue-এর ২, missing/match-এর ১। Contract-only, behaviour-only অথবা mixed edit-এর জন্য আলাদা bonus নেই। Sort হলো repo, score descending, SHA ascending। YAML/JSON path screen ইচ্ছাকৃতভাবে broad: workflow/configuration-ও false positive হিসেবে আসতে পারে; সেগুলো screen-এ বাদ দেওয়া হয়েছে। তাই frozen pool-কে verified mismatch set বলা যায় না। Evidence: `mine.py:26`, `mine.py:59`; `candidate_pool.json`; `freeze.json`।

Pool-এ **২০,১৯৯** candidate ছিল। Review-এর আগে pool freeze করা হয়েছে; পরের audit-এ pool hash, membership/order এবং পূর্বে accepted/rejected/deferred candidate বাদ পড়া যাচাই হয়েছে। Ranked title/path/delta screen-এর সঙ্গে পূর্ণ sanitized patch private evidence-এ সংরক্ষিত আছে। Acceptance-এর জন্য আলাদা exact-parent gate প্রয়োগ করা হয়েছে: neutral proposition, parent-only contract ও implementation locators, corresponding developer patch, confidence, contract kind, mismatch/family এবং existing-operation check। IMPL item-এ parent contract-এর সমর্থন প্রয়োজন হয়েছে। Dedup identity ছিল repo + operation + fix family। Evidence: `freeze.json`; `finalize_review.py:56`; `key/review_decisions.csv`; `key/accepted_full.csv`।

মোট **৮৯২টি candidate** reviewed: **১৫টি accepted candidate থেকে ১৬টি item**, **৬৭৪টি rejected**, **২০৩টি deferred**। একই candidate-এর দুইটি আলাদা operation থাকায় candidate ও item count আলাদা। Deferred অর্থ পূর্ণ parent mismatch evidence প্রতিষ্ঠিত হয়নি; এগুলো negative ground truth নয়। Review ছিল bounded patch screening; accepted item-গুলোর exact-parent evidence অতিরিক্তভাবে পড়া হয়েছে। Evidence: `summary.json:5`; `key/review_decisions.csv`; `key/accepted_full.csv`।

প্রতি repo-র yield নিচে দেওয়া হলো। সব সংখ্যার source হলো `08_experiments/E7_mining/yield.csv:2` থেকে repo-নামযুক্ত সংশ্লিষ্ট row। `reviewed` হলো candidate count; `accepted` হলো নতুন item count। কোনো repo ৬-item cap-এ পৌঁছায়নি। ছোট pool-এ সব available candidate, অন্যগুলোতে top ৩০ reviewed হওয়ায় stopping rule পূরণ হয়েছে। পুরো frozen pool exhaust করা হয়নি।

| Repo | Pool | Reviewed | Accepted |
|---|---:|---:|---:|
| FAAAST-Service | 188 | 30 | 0 |
| Iced-Latte | 394 | 30 | 0 |
| OpenLineage | 195 | 30 | 0 |
| allure-server | 18 | 18 | 0 |
| apicurio-registry | 737 | 30 | 0 |
| basyx-java-server-sdk | 76 | 30 | 5 |
| bibliothek | 2 | 2 | 0 |
| catwatch | 13 | 13 | 0 |
| cwms-data-api | 311 | 30 | 2 |
| ditto | 1104 | 30 | 1 |
| dockstore | 261 | 30 | 0 |
| eudi-srv-verifier-endpoint | 16 | 16 | 1 |
| fineract | 579 | 30 | 1 |
| genome-nexus | 29 | 29 | 0 |
| gravitee-api-management | 10022 | 30 | 1 |
| harbor | 1124 | 30 | 0 |
| hivemq-edge | 246 | 30 | 0 |
| hydra | 467 | 30 | 0 |
| kapua | 1305 | 30 | 2 |
| kratos | 626 | 30 | 0 |
| microcks | 273 | 30 | 0 |
| nessie | 254 | 30 | 1 |
| ohsome-api | 64 | 30 | 0 |
| open-banking-gateway | 399 | 30 | 0 |
| pay-publicapi | 85 | 30 | 1 |
| polaris | 156 | 30 | 0 |
| quartz-manager | 53 | 30 | 0 |
| rhsm-subscriptions | 314 | 30 | 0 |
| service-api | 624 | 30 | 0 |
| session-service | 2 | 2 | 0 |
| sldt-digital-twin-registry | 97 | 30 | 0 |
| spring-batch-rest | 2 | 2 | 0 |
| strimzi-kafka-bridge | 77 | 30 | 1 |
| tiltaksgjennomforing-api | 86 | 30 | 0 |

Package path: `08_experiments/E2_labelling/e7_blind/`। HMAC shuffle-এর salt শুধু private directory-তে আছে। `items.csv`-এর proposition অপরিবর্তিত; আলাদা provenance table-এ দুই set-এর পরিচয় আছে। Contract-এ সম্পূর্ণ parent file, অথবা ৩০০ KiB-এর বেশি spec-এর operation ও transitive local `$ref` closure রাখা হয়েছে। Annotation source সম্পূর্ণ রাখা হয়েছে। Implementation locator-এর সম্পূর্ণ parent file, selected direct helper ও routing evidence রাখা হয়েছে; সর্বোচ্চ ৮টি implementation file। একই annotated file দুই role-এ প্রয়োজন হলে উভয় directory-তে আছে। Evidence: `build.py:65`, `build.py:184`, `build.py:225`; `verification.json`।

Final package-এর আকার **৩,০৩৪,৬২৭ bytes**, **১৭২টি file**: **৪৪টি contract excerpt**, **১২৬টি implementation file**, এবং দুইটি সাধারণ file। দুইটি বড় specification projection করা হয়েছে; **১৩৬টি delivered source file**-এ privacy/history-literal redaction আছে। ছোট spec ও implementation-এর whole-file line count বজায় আছে; projection-এর line numbering মূল source-এর সমান নয়। Evidence: `verification.json:2`; private build file manifest।

Leakage audit-এ actual disk bytes deterministic parent reconstruction-এর সঙ্গে মিলে গেছে। Raw parent provenance, non-parent child-blob equality, actual output-এর message/reference scan, whole implementation locators, forbidden-word filter এবং key schema পাস করেছে। T44 credential/attribution scans-এর সঙ্গে **১৫টি auth fixture** থেকে **৫৪টি value variant** পরীক্ষা হয়েছে। Source-এর ISO date ও long hexadecimal history literal-ও redact/scan করা হয়েছে। Evidence: `verification.json`; `build.py:32`, `build.py:225`; `verify.py:14`।

Cross-item ancestry/path check-এ **৯টি item flagged**, **১৩টি overlap** নিজস্ব locator হিসেবে রাখা হয়েছে; optional overlapping file বাদ দেওয়ার প্রয়োজন হয়নি। এটি task-এর own-locator exception; cross-item information সম্পূর্ণ অনুপস্থিত—এমন দাবি করা যাচ্ছে না। Blind reading-এ item-গুলোর মধ্যে তুলনা না করা প্রয়োজন। বিস্তারিত overlap শুধু private provenance-এ আছে। Evidence: `verification.json`-এর `cross_item_flagged`, `retained_cross_locators`, `excluded_cross_files`; `key/build_log.json`।

**১৩টি test পাস** করেছে: synthetic bare repo-তে parent-only content ও message exclusion, optional cross-file exclusion, own-locator retention/flag, deterministic shuffle, forbidden words, overwrite refusal, parent-locator enforcement, attribution/fixture-value redaction, contributor-header continuation, dual-role annotated source এবং JSON/YAML/multi-file reference closure। Production package একবার publish করা হয়েছে; final privacy correction-এর পরে reconstruction দিয়ে actual disk bytes যাচাই হয়েছে। Upstream checkout/build/execution/network ব্যবহার করা হয়নি। Synthetic Git object creation কেবল test-এর অস্থায়ী স্থানীয় directory-তে হয়েছে। Evidence: `test_build.py:45`; `09_collab/logs/T45_scratch/test_results.txt`; `verification.json`; `key/privacy_update.json`।

⚠️ Threats: direction-neutral score হলেও correction-cue vocabulary, broad path proxy ও মাত্র top-৩০ depth retrieval bias তৈরি করতে পারে। Bounded screen এবং ২০৩টি deferral থেকে অবশিষ্ট pool-এর সম্ভাব্য yield নির্ণয় করা যায় না; এই ফল ৪৫-item corpus অসম্ভব হওয়ার প্রমাণ নয়। Annotation drift, regenerated documentation, squash/cherry-pick history এবং feature-সদৃশ correction acceptance কঠিন করে। Runtime traffic ছাড়া framework serialization/exception semantics-এর কিছু সিদ্ধান্ত static inference; item-ভিত্তিক confidence ও inference note private evidence-এ আছে। Go repo-গুলোর reviewed অংশ থেকে নতুন acceptance নেই, ফলে Go coverage প্রতিষ্ঠিত হয়নি। Source excerpt পুরো module নয়; ৮-file cap-এর কারণে কিছু context অনুপস্থিত থাকতে পারে। Local reference closure সংরক্ষিত হলেও remote content network দিয়ে আনা হয়নি। Lexical privacy/reference scan semantic paraphrase বা সব personal name শনাক্ত করার নিশ্চয়তা দেয় না। Popular repo-র memorisation risk রয়ে গেছে; supplied stars private metadata-তে আছে। Evidence: `key/accepted_full.csv`; `key/build_log.json`; `yield.csv`; `09_collab/tasks/T45.md`।

Boundary incident: প্রথম screen output-এ embedded attribution trailer সম্পূর্ণ redact হয়নি। Filter সংশোধনের পর stored discovery metadata ও তখনকার patch evidence পুনরায় sanitize করা হয়েছে; frozen membership/ranking অপরিবর্তিত ছিল। অতিরিক্ত final scan-এ T44 filter-এর বাইরে থাকা comment credit block পাওয়া যায়; ১৪টি source file-এ শুধু line-preserving privacy correction করা হয়েছে। Item table ও key অপরিবর্তিত আছে, এবং final reconstruction/privacy scan পাস করেছে। ব্যক্তিগত attribution এখানে পুনরুৎপাদন করা হয়নি। Evidence: `key/sanitization_audit.json`; `key/privacy_update.json`; `mine.py:30`; `verification.json`।
