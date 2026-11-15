# T44 — blind package builder: সমাপ্তির প্রতিবেদন

Production build **একবার সফলভাবে** চালানো হয়েছে। ২৫টি input থেকে cross-item leakage rule প্রয়োগের পরে **১৮টি scored item: IMPL ১০ / SPEC ৮**, ১১টি repository। বাদ পড়া item-এর package রাখা হয়নি; reserved K IDs অপরিবর্তিত। কোনো item label করা হয়নি এবং কোনো labeller launch হয়নি। Evidence: `08_experiments/E6_realfix/e6_build_log.json:summary,excluded_items`; `09_collab/logs/T44_scratch/production_stdout.jsonl`-এর শেষ row।

Builder ও tests: `08_experiments/E6_realfix/build_e6_blind.py`, `test_build_e6_blind.py`; ব্যবহার ও inclusion rule: `T44_BUILDER.md`। Hidden key-এর columns ঠিক নির্দেশিত নয়টি; blind manifest-এর পাঁচটি columns-এ শুধু item/package/operation/verbatim proposition/contract path আছে। Key-তে নতুন judgment যোগ করা হয়নি; accepted manifest-এর truth metadata কপি হয়েছে। Evidence: `build_e6_blind.py:34,80,642,718`; `e6_key.csv:item_id`; `08_experiments/E2_labelling/e6_blind/items.csv:item_id`।

Parent-side evidence-এ থাকা handler/DTO/validator/exception module-এর পুরো `src/`, তার tests/resources, local Java/Kotlin imports-এর module closure, local contract `$ref` closure, module descriptors ও README/docs এবং root README/docs রাখা হয়েছে। `.git`, build/dependency output, symlink/submodule, archive ও সব binary বাদ; সব file-এর জন্য 2 MiB cap-ও আছে। Contract কেবল `source/`-এ; আলাদা duplicate নেই। Attribution ও credential value redaction physical line count ধরে রাখে; অন্য content parent blob থেকে আসে। প্রতিটি retained path-এর parent Git object, parent SHA-256, delivered SHA-256 ও bytes hidden log-এ আছে। Evidence: `build_e6_blind.py:265,400,415,480`; `e6_build_log.json:inclusion_rule,items[].files,items[].redactions`।

Salt আগে স্থির করে `HMAC-SHA256(salt, original item_id)` অনুযায়ী K01–K25 reserve করা হয়েছে; input CSV row order এতে প্রভাব ফেলে না। “Later-sorted” = বড় K ID, chronological parent নয়। সব parent evidence path এবং local contract references protected ধরা হয়েছে, যাতে unrelated path বাদ দিতে গিয়ে প্রয়োজনীয় evidence না হারায়। Balance দেখে salt বদলানো হয়নি। Evidence: `build_e6_blind.py:33,400,516,642`; `e6_build_log.json:salt,ordering`; `test_build_e6_blind.py:test_salt_changes_mapping_and_row_order_does_not`।

১৯টি potential cross-item pair-এর সবগুলো নিচে আছে। ৭টিতে বড় K item drop, ৮টিতে optional path exclusion, ৪টিতে endpoint আগেই excluded ছিল। Final scored packages-এ মোট ১৫টি optional path এই কারণে বাদ গেছে; একটি exclusion decision-এর ৪টি path-সহ package পরে drop হয়েছে। পূর্ণ path list এবং protected-path কারণ log-এর প্রতিটি pair-এ আছে। Evidence: `e6_build_log.json:cross_item_pairs,items[].omissions`।

| A: resolution-এর item | B: যে snapshot-এ path ছিল | Overlap paths | B-তে protected | সিদ্ধান্ত |
|---|---|---:|---:|---|
| K01 | K05 | 5 | 1 | Drop K05 |
| K01 | K24 | 5 | 1 | Drop K24 |
| K03 | K02 | 1 | 1 | Drop K03 |
| K06 | K07 | 4 | 0 | B থেকে optional paths বাদ |
| K06 | K09 | 4 | 0 | B থেকে optional paths বাদ |
| K06 | K10 | 4 | 0 | B থেকে optional paths বাদ |
| K06 | K19 | 2 | 0 | B থেকে optional paths বাদ |
| K07 | K10 | 2 | 1 | Drop K10 |
| K09 | K07 | 1 | 0 | B থেকে optional paths বাদ |
| K09 | K10 | 2 | 1 | Endpoint আগেই excluded |
| K09 | K19 | 1 | 0 | B থেকে optional paths বাদ |
| K12 | K04 | 1 | 0 | B থেকে optional paths বাদ |
| K16 | K15 | 1 | 1 | Drop K16 |
| K17 | K02 | 1 | 1 | Drop K17 |
| K17 | K03 | 1 | 1 | Endpoint আগেই excluded |
| K18 | K14 | 1 | 1 | Drop K18 |
| K20 | K15 | 2 | 0 | B থেকে optional paths বাদ |
| K20 | K16 | 2 | 0 | Endpoint আগেই excluded |
| K24 | K05 | 4 | 0 | Endpoint আগেই excluded |

বাদ পড়া item-গুলো scored key ও blind directory-তে নেই। নিচের mapping শুধু coordinator report/log-এর জন্য; labeller task/manifest-এ নেই। Evidence: `e6_build_log.json:items[status=excluded],excluded_items`।

| Reserved ID | Accepted ID | Repository | পূর্বনির্ধারিত truth |
|---|---|---|---|
| K03 | R006 | microcks | SPEC |
| K05 | T43R001 | strimzi-kafka-bridge | IMPL |
| K10 | R012 | pay-publicapi | IMPL |
| K16 | R003 | cwa-verification-server | SPEC |
| K17 | R005 | microcks | SPEC |
| K18 | T43R004 | dockstore | IMPL |
| K24 | T43R002 | strimzi-kafka-bridge | IMPL |

Blind payload মোট **53,151,789 bytes (50.6895 MiB)**: source **53,104,960 bytes / 11,432 files**, এবং manifest, দুইটি task ও unchanged codebook মিলিয়ে আরও ৪টি file। মোট 11,436 files। Hidden key 2,157 bytes; hidden build log 9,223,308 bytes। নিচে প্রতি package-এর source payload; filesystem allocation size আলাদা হতে পারে। Evidence: `e6_build_log.json:summary,items[].bytes,items[].files`; hidden output file sizes।

| Package | Source files | Source bytes |
|---|---:|---:|
| K01 | 84 | 622407 |
| K02 | 739 | 5391828 |
| K04 | 2952 | 12363783 |
| K06 | 198 | 747938 |
| K07 | 322 | 1265848 |
| K08 | 863 | 3656269 |
| K09 | 271 | 1025480 |
| K11 | 502 | 1834212 |
| K12 | 2895 | 12132791 |
| K13 | 37 | 119399 |
| K14 | 799 | 5749287 |
| K15 | 74 | 364734 |
| K19 | 425 | 1514734 |
| K20 | 53 | 260615 |
| K21 | 27 | 90666 |
| K22 | 676 | 4789951 |
| K23 | 119 | 365301 |
| K25 | 396 | 809717 |

`TASK_M1.md` ও `TASK_M2.md` parent source + contract + proposition থেকে intended behaviour বিচার করতে বলে; runtime exchange নেই। দুটিতে launch authorization paragraph verbatim, explicit-path search, redaction ও “do not compare files across packages” rule এবং নিজস্ব output filenames আছে। M2-তে intent tool allowed, `history_scope=unavailable`, outside history নিষিদ্ধ, এবং review/search records রাখা বাধ্যতামূলক। Codebook অপরিবর্তিত; SHA-256 `fee70f11ed3817c014af0da32f8160117417663ea18d374cbc4f8bc4726ad9b8`। Evidence: `build_e6_blind.py:554`; `e6_blind/TASK_M1.md`, `TASK_M2.md`; `e6_build_log.json:package_hashes.CODEBOOK_v0.6.md`।

২৫টি synthetic test PASS। Tests stdlib দিয়ে loose Git objects তৈরি করে; `git init/add/commit/checkout` চালায় না। Determinism, row-order independence, salt allocation, child-version copy under another path, parent-identical mode-only exception, cross-item optional exclusion/protected drop, same-parent non-leak, actual future-reference rejection, credential examples, structured contract validity, long fixture scan এবং refusal-to-overwrite covered। Evidence: `09_collab/logs/T44_scratch/tests.txt:1`; `test_build_e6_blind.py`।

Final production verification **PASS: 103,248 assertions**। Preflight ও published plan মেলে; সব 11,436 disk hash, 11,432 parent/child file comparison, 10 retained same-repo ancestry pair, চারটি delivered JSON contract এবং proposition/key/task/codebook invariants verified। Existing E4 credential function ও T43 leakage function AST থেকে অপরিবর্তিত চালানো হয়েছে, actual-output adapters দিয়ে; T43-তে 414 target-item/file scans, zero exact/issue hits। Original scanner entry point বা অন্য blind package/key load করা হয়নি। আগের **445 input file অপরিবর্তিত**, input drift শূন্য; build ও verification stderr দুটিই empty। Evidence: `09_collab/logs/T44_scratch/production_verification.json:passed,assertions,files_hashed,own_child_file_comparisons,retained_cross_ancestry_checks,json_contracts_parsed,existing_T43_item_file_scans,protected_inputs_unchanged,input_drift`; `verify_production.py:main`; `production_stderr.txt`, `verification_stderr.txt`।

১৫টি auth fixture-এর ৫৪টি literal/JSON/URL/payload variant checked। Actual selected prose scope ১৭১টি file; all-source full/short resolution SHA ও subject scan-ও চালানো হয়। প্রতিটি repository-র সব input target, excluded target-সহ, scan scope-এ থাকে। Scored source-এ ৬,৪০৪টি file-এ credential/attribution redaction হয়েছে; copyright headers-ও এর মধ্যে পড়ে। Evidence: `e6_build_log.json:summary,items[].redactions,assertions`; `build_e6_blind.py:198,224,336,369,642`।

প্রথম audit দীর্ঘ হওয়ায় থামানো হয়। ⚠️ দীর্ঘ fixture string-এ unbounded regex সম্ভাব্য কারণ; profiling করা হয়নি। Regex bounded করা হয়েছে এবং দীর্ঘ fixture-এর regression যোগ হয়েছে। আরেক audit YAML `Basic` type-এর পরের লাইনের শব্দকে auth header ধরেছিল; match যে newline পেরিয়েছিল তা content না দেখিয়ে diagnostic-এ নিশ্চিত হয়। সেটি horizontal whitespace-এ সীমিত করা হয়েছে। নতুন credential-method regression শেষ করতে একটি intermediate audit-ও থামানো হয়। Final audit সফল হওয়ার পরে production command একবার চালানো হয়। Upstream source line, credential value বা personal attribution এসব diagnostic-এ print করা হয়নি। Evidence: `09_collab/logs/T44_scratch/development_notes.json`; `test_build_e6_blind.py:test_multiline_auth_schema_is_not_an_auth_header,test_long_noncredential_fixture_has_bounded_scan`।

⚠️ সীমা: exact SHA/subject/issue scan paraphrase বা semantic preannouncement-এর অনুপস্থিতি প্রমাণ করে না। Lexical privacy scans সব personal name বা সব credential encoding ধরার নিশ্চয়তা নয়। Static module/import closure runtime completeness বা reproducibility প্রমাণ করে না; external references fetch করা হয়নি। Redaction-এর কারণে কিছু unrelated fixture detail অনুপস্থিত। এগুলো hidden log-এর limitations-এ আছে। Dataset এখন ১৮টি, confidence-3 subset ৯টি; পরিকল্পনার ≥৪০ লক্ষ্য পূরণ হয় না। Developer repair direction-ই copied truth; তার correctness পুনরায় adjudicate করা হয়নি। Evidence: `e6_build_log.json:limitations,items[].confidence`; `E6_PLAN.md:Item set,পূর্বজ্ঞাত সীমা`।

কোনো network, checkout, upstream-code execution, Docker, Java বা Maven চালানো হয়নি। Read-only Git interface command allowlist ব্যবহার করে এবং optional locks, hooks, fsmonitor, lazy fetch বন্ধ রাখে। অন্য blind package/key খোলা হয়নি; শুধু নির্দেশিত E4 TASK/CODEBOOK এবং existing builder/scanner source পড়া হয়েছে। আগের inputs-এর integrity ফল final verification-এ আছে। Coordinator-এর পরবর্তী কাজ হলো reduced scored set ধরে pre-registration freeze ও fresh labeller launch; এই task-এ কোনো pending approval বা blocking প্রশ্ন নেই। Evidence: `build_e6_blind.py:103`; `verify_production.py`; `production_verification.json:protected_inputs_unchanged,input_drift`।
