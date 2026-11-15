# T36 — Codebook v0.6 §11.4 non-blind baseline pilot

২৮টি pre-specified item-এ pilot সম্পন্ন: ২৪টি search, ৪টি rule exemption, ১৫২টি raw hit review এবং ৯১টি manual/context record। Final labels-এর সঙ্গে exact agreement **১৭/২৮ (৬০.৭%)**। ছয়টি final BOTH item-এ labeller-এর অনুমোদিত primary IMPL + `both_candidate=true` থাকার কারণে exact mismatch; ওই কর্তৃত্বগত পার্থক্য আলাদা করলে compatibility **২৩/২৮ (৮২.১%)**। **পাঁচটি substantive review proposal** এসেছে; কোনো final label পরিবর্তন করা হয়নি। এগুলো accuracy বা ground-truth ফল নয়। প্রমাণ: `09_collab/logs/T36_scratch/comparison_summary.json:$.per_stratum`, `09_collab/logs/T36_scratch/verification.json:1`; adjudication-এর অর্থ: `08_experiments/E2_labelling/FINAL_LABELS.md:3-16,34-35`।

**গুরুত্বপূর্ণ boundary incident:** একটি অসুরক্ষিত manual source-window printer market-এর demo Basic-auth value terminal-এ ছাপিয়েছে; এখানে value পুনরাবৃত্তি করা হয়নি। আর Scout source-এ top-level README/CHANGELOG না থাকায় empty path-list-সহ fallback `rg` workspace root scan করেছে। তার matches-এ ২৮টি E5 path ছিল; discarded output-এর কোনো E5 match content মডেলকে দেখানো হয়নি—শুধু প্রথম পাঁচটি non-blind board/watch line দেখা হয়েছিল। তারপর সমগ্র contaminated scratch output মুছে শুধু hash/count/scope metadata রাখা হয়েছে এবং empty-path guard যোগ করা হয়েছে। ফলে “forbidden material কখনো access হয়নি” দাবি করা যাবে না। ভবিষ্যৎ E5 blind assignment-এর আগে coordinator-কে এই access incident মূল্যায়ন করতে হবে। প্রমাণ: `09_collab/logs/T36_scratch/incident.json:1`, `09_collab/logs/T36_scratch/fallback_manifest.json:1`, `09_collab/logs/T36_scratch/fallback.py:17-25`।

**Sample ও decision sequence।** Population ১৬১টি baseline row; B065/M003/M005/M007/M012 বাদ। `random.Random(20261115)` দিয়ে sorted strata থেকে SPEC → SPEC_PARTIAL → UNDECIDABLE → BOTH → IMPL ক্রমে ৬/৪/৬/৬/৬টি draw হয়েছে। সব চারটি SPEC_PARTIAL-ও `rng.sample(pool, 4)` দিয়ে নেওয়ায় RNG consumption স্পষ্ট। Non-scout replacement দরকার হয়নি; প্রতিটি stratum-এ অন্তত একটি non-scout আছে। TEST stratum নেওয়া হয়নি। Script ও output evidence search-এর আগে তৈরি; স্বাধীন পুনর্গণনায় একই ২৮টি ID। প্রমাণ: `09_collab/logs/T36_scratch/sample.py:1`, `09_collab/logs/T36_scratch/sample.json:1`, `09_collab/logs/T36_scratch/verify.py:47-61`।

Working sheet-এ `final_L1`, `A_L1`, `B_L1`, `note` এবং source/adjudication-origin column লুকানো হয়েছে। Blind sheets, পূর্বের নিজের label sheet-এর **শুধু locators**, পুরোনো neutral exchange maps এবং raw runs থেকে evidence নেওয়া হয়েছে। পুরোনো সিদ্ধান্ত/rationale extraction script-এ ব্যবহার করা হয়নি। 28টি decision এবং review 2026-11-15 02:11:25 UTC-তে freeze; final join 02:12:03 UTC-তে। Join-এর পরে frozen L1 ও original review hash মেলানো হয়েছে। C002-এ পরে পাওয়া explanatory branch-count ভুলের জন্য আলাদা immutable amendment আছে; original record অক্ষত, L1 অপরিবর্তিত, তিনটি CSV annotation cell-এর old/new value সংরক্ষিত। প্রমাণ: `09_collab/logs/T36_scratch/prepare.py:48-65`, `09_collab/logs/T36_scratch/working_sheet.csv:1`, `09_collab/logs/T36_scratch/decision_freeze.json:1`, `09_collab/logs/T36_scratch/comparison_summary.json:$.joined_utc`, `09_collab/logs/T36_scratch/verification.json:1`।

⚠️ এটি practically blind নয়: prescribed stratum order ও block sizes থেকেও label উদ্ধার করা সম্ভব; পুরোনো T15/T16/T18 baseline labelling-এর exposure আছে; B005-এর final label population header/প্রথম কয়েকটি row দেখার সময়ে সরাসরি দেখা হয়েছে। বাকি item-এর specific final label আগে মনে ছিল না, কিন্তু আগের final exposure অস্বীকার করা হয়নি। প্রতিটি row-তে `prior_exposure`, এবং review record-এ বিস্তারিত আছে। তাই পাঁচটি proposal-ও independent replication নয়। প্রমাণ: `08_experiments/E2_labelling/pilot_v06/T36_pilot_labels.csv:item_id=B005`, `08_experiments/E2_labelling/pilot_v06/review/B005.json:$.prior_exposure`, `09_collab/logs/T36_scratch/sample.json:1`।

Procedure-এ প্রথমে actual message/constraint ও observed branch নির্দিষ্ট করেছি; তারপর mandatory gate, repository tool, HANDLER → E-TEST → E-DOC → E-CONSIST → E-HISTORY review, directed fallback, এবং label। প্রতিটি mandatory run-এর exact argv, source/spec/tool hash, representative exchange, stdout JSON, stderr, exit code, scan ও history metadata আছে। কোনো search reuse করা হয়নি। Raw string থেকে label করা হয়নি: `supports_spec` spec-এর আচরণের পক্ষে candidate; SPEC defect নয়। পুরোনো accepted Scout framework precedent প্রয়োগ করার সঙ্গে নতুন independent evidence discovery আলাদা রাখা হয়েছে। প্রমাণ: `09_collab/logs/T36_scratch/run_searches.py:1`, `09_collab/logs/T36_scratch/search/B005.manifest.json:1`, codebook `08_experiments/R1_triage_codebook.md:289-298`।

B066/B023/B071-এর non-gateway 500-এ R1/§9.3 এবং P035-এর malformed documented JSON-এ §9.3/§10.7 যথেষ্ট; চারটিতে `intent_search_status=not_run`, verdict `NA`, exemption rule ও placeholder raw/manifest locator দেওয়া হয়েছে। 5xx cluster-এর আলাদা সম্ভাব্য SPEC component থাকলে gate এড়ানো হয়নি: M002/M013/B094/B040/B098/B087-এ search চালানো হয়েছে। প্রমাণ: `09_collab/logs/T36_scratch/search_summary.json:1`, `09_collab/logs/T36_scratch/search/B066.manifest.json:1`, `09_collab/logs/T36_scratch/search/P035.manifest.json:1`, `09_collab/logs/T36_scratch/run_searches.py:23-33`।

**Per-stratum agreement।** Exact column সরাসরি `L1 == final_L1_joined`; compatibility column শুধু final BOTH ↔ primary IMPL+flag-এর কর্তৃত্বগত reconciliation। এটি নতুন adjudicated label বা accuracy score নয়। প্রমাণ: `09_collab/logs/T36_scratch/join_final.py:29-42`, `08_experiments/R1_triage_codebook.md:217-219`।

| Final stratum | n | Non-scout | Exact agreement | Primary+flag compatible |
|---|---:|---:|---:|---:|
| SPEC | 6 | 1 | 5/6 (83.3%) | 5/6 |
| SPEC_PARTIAL | 4 | 4 | 1/4 (25.0%) | 1/4 |
| UNDECIDABLE | 6 | 1 | 6/6 (100.0%) | 6/6 |
| BOTH | 6 | 3 | 0/6 (0.0%) | 6/6 |
| IMPL | 6 | 2 | 5/6 (83.3%) | 5/6 |

উৎস: `09_collab/logs/T36_scratch/comparison_summary.json:$.per_stratum`। Pilot L1 distribution: SPEC ৫, SPEC_PARTIAL ১, UNDECIDABLE ১১, IMPL ১১; labeller সরাসরি BOTH দেয়নি। প্রমাণ: একই file `$.pilot_L1_counts`; output `08_experiments/E2_labelling/pilot_v06/T36_pilot_labels.csv:1`।

C002-এর explanatory count correction final join-এর পরে হয়েছে: ৬২টি non-header rejection-কে মূল record ভুল করে সব missing-input বলেছিল। মূল review/decision freeze রাখা হয়েছে; `review_amendments/C002.json`-এ সঠিক ৪৯/১১/২/৭ split, নতুন test/call-chain evidence, এবং তিনটি annotation cell-এর exact before/after আছে। Label, confidence, agreement ও comparison denominator বদলায়নি। এই supplemental evidence review-ও non-blind। প্রমাণ: `08_experiments/E2_labelling/pilot_v06/review_amendments/C002.json:1`, `09_collab/logs/T36_scratch/comparison_summary_initial.json:1`, `09_collab/logs/T36_scratch/verification.json:$.post_join_annotation_amendment`।

**সব label disagreement-এর review proposal।** নিচের প্রথম পাঁচটিতে v0.6-এর independence gate পুরোনো adjudication আবার দেখতে বলছে। Final file অপরিবর্তিত; ⚠️ proposal-এর evidence interpretation labeller-এর inference।

| Item | Existing final → pilot | Evidence ও review proposal |
|---|---|---|
| C005 | SPEC → UNDECIDABLE | আসল message হলো documented 404 object body অনুপস্থিত। `InternalTanController.java:103-122` ও exception mapper bodyless response ব্যাখ্যা করে; test `VerificationApplicationInternalTest.java:156-170` এবং architecture guide `:243-253` শুধু 404 নিশ্চিত করে, empty body নয়। একই exception-handler class-এর binding/validation/verification methods-এর policy independence Claude provisional decision-এর জন্য দিন; `adjudication_flag=same_class_policy`। সব expanded locator ও unresolved checklist: `08_experiments/E2_labelling/pilot_v06/review/C005.json:$.manual_additions`। |
| P043 | SPEC_PARTIAL → UNDECIDABLE | ৩৪টি absent-body rejection-এর ভিত্তি একটিমাত্র `UserController.java:146-149` guard; স্বাধীন body-required test/doc নেই। অন্য একটি exchange-এ `userStatus` int32 overflow, TEST। আগের SPEC component এখন unsupported; UNDECIDABLE+TEST-এর conservative abstention review করুন। প্রত্যেক captured line ও source: `08_experiments/E2_labelling/pilot_v06/review/P043.json:$.decision.message_decisions`, একই file `$.manual_additions`। |
| P021 | SPEC_PARTIAL → UNDECIDABLE | ৬০টি no-file rejection শুধু `PetController.java:157-159` guard-এ; স্বাধীন required-file evidence নেই। দুইটি petId int64 overflow TEST। SPEC_PARTIAL বজায় রাখার positive SPEC basis পর্যালোচনা করুন। প্রমাণ: `08_experiments/E2_labelling/pilot_v06/review/P021.json:$.decision.message_decisions`, একই file `$.manual_additions`। |
| P019 | SPEC_PARTIAL → UNDECIDABLE | ৬৩টি optional-name rejection-এর ভিত্তি `PetController.java:99-103`; README incidental, test class খালি। তিনটি petId overflow TEST। Missing-name guard-এর বাইরে স্বাধীন intent ছাড়া SPEC component গ্রহণ না করার proposal। প্রমাণ: `08_experiments/E2_labelling/pilot_v06/review/P019.json:$.hits`, একই file `$.manual_additions`, `$.decision.message_decisions`। |
| P013 | IMPL → UNDECIDABLE | Exchange 211-এর সপ্তম Pet, id 22176, required photoUrls ছাড়া আসে। `Pet.java:32-70` default/setter/XML annotations ও `PetData.java:115-135` data flow ব্যাখ্যা করে; JSON field-presence intent-এর স্বাধীন test/doc নেই। §11.2 অনুযায়ী code-only attribution abstain করার proposal। প্রমাণ: `08_experiments/E2_labelling/pilot_v06/review/P013.json:$.target`, একই file `$.manual_additions`। |

অবশিষ্ট ছয়টি exact mismatch-এর proposal হলো existing final BOTH বজায় রাখার evidence/flag adjudicator-কে দেখানো; primary IMPL-কে final BOTH-এর replacement হিসেবে নেওয়া নয়। §10.1-এর authority rule এবং §10.6-এর specific exceptions ব্যবহার হয়েছে। প্রমাণ: `08_experiments/R1_triage_codebook.md:217-219,239-244`, `09_collab/logs/T36_scratch/comparison_summary.json:$.disagreements`।

| Item | Existing final → pilot | Adjudication review evidence |
|---|---|---|
| M002 | BOTH → IMPL + both_candidate | Array `_links`-এ HAL parse failure → generic 500; saved request schema-এ array shape। Existing market-specific §10.6 candidate পুনরায় উপস্থাপন। Full source/spec/exchange: `08_experiments/E2_labelling/pilot_v06/review/M002.json:$.manual_additions`। |
| B094 | BOTH → IMPL + both_candidate | Optional create body এবং required-list ছাড়া Tag schema; saved SQL NOT NULL GRP failure ও null-body crash। §10.6 candidate। প্রমাণ: `08_experiments/E2_labelling/pilot_v06/review/B094.json:$.manual_additions`। |
| B040 | BOTH → IMPL + both_candidate | Optional create body/KEY/VALUE requirements বাদ, persistence-এ NOT NULL/null-body crash। §10.6 candidate। প্রমাণ: `08_experiments/E2_labelling/pilot_v06/review/B040.json:$.manual_additions`। |
| B098 | BOTH → IMPL + both_candidate | Missing id list dereference; অতিরিক্ত structural witness: template-এ `{id}` নেই কিন্তু required path id ঘোষিত। Success-list tests missing-list intent নয়। প্রমাণ: `08_experiments/E2_labelling/pilot_v06/review/B098.json:$.manual_additions`, একই file `$.decision.message_decisions`। |
| P018 | BOTH → IMPL + both_candidate | Query status enum-হীন; response model enum আছে; একই invalid value persist/return। Specific §10.6 internal-inconsistency rule প্রযোজ্য; annotation নিজের generated spec-এর স্বাধীন evidence নয়। প্রমাণ: `08_experiments/E2_labelling/pilot_v06/review/P018.json:$.manual_additions`। |
| M013 | BOTH → IMPL + both_candidate | `_links` array → HAL failure → generic 500; §10.6। Registration guide-এর 406 validation example pre-validation HAL parser branch-এর intent বলে গ্রহণ করা হয়নি। প্রমাণ: `08_experiments/E2_labelling/pilot_v06/review/M013.json:$.hits`, একই file `$.manual_additions`। |

আরেকটি flag-only review signal: B087-এর primary IMPL আগের final-এর সঙ্গে মেলে, কিন্তু exchange 4135-এর SQL NOT NULL GRP branch-এর জন্য `both_candidate=true`; প্রথম missing-target/null-dereference branch থেকে আলাদা। ⚠️ §10.6-এর প্রয়োগ adjudicator দেখবেন; final L1 পরিবর্তনের দাবি নয়। প্রমাণ: `08_experiments/E2_labelling/pilot_v06/review/B087.json:$.decision.message_decisions`, একই file `$.manual_additions`।

**Tool hits ও fallback yield।** Raw verdict: supports_spec ৫, conflicting ২, none_found ১৭; ৪টি exemption-এ NA। ১৫২টি hit-এর মধ্যে HANDLER ৪৯, E-TEST ৩৯, E-DOC ৫৮, E-CONSIST ৩, E-HISTORY ৩। প্রতিটিতে disposition/reason এবং (a) expectation, (b) scenario linkage, (c) separate basis, (d) revision, (e) contrary-evidence review আছে। ১০৯টি context, ৪৩টি reject; target constraint-এর জন্য raw hit থেকে independent accept শূন্য। Tool-এর independent-marked ১০২ এবং directional-marked ৩৪টি hypothesis-কে label হিসেবে নেওয়া হয়নি। এটি tool precision শূন্যের estimate নয়—context retrieval, target propositions ও task mix আলাদা। প্রমাণ: `09_collab/logs/T36_scratch/review_stats.json:1`, `09_collab/logs/T36_scratch/verification.json:1`, প্রতিটি `08_experiments/E2_labelling/pilot_v06/review/<item_id>.json:$.hits`।

| Fallback outcome | Item | ফল |
|---|---|---|
| নতুন decisive independent evidence, tool miss | C002 | Helper constants resolve করে null key/keyType tests-এর 400 assertions পাওয়া গেছে। পরের semantic audit-এ missing input ৪৯, invalid GUID ১১, unissued short TeleTAN ২ এবং invalid header ৭টি আলাদা হয়েছে। Invalid-GUID/unknown-TeleTAN integration tests ও validator/service linkage supplement-এ আছে; ৬২টি SPEC component + সাতটি TEST → SPEC_PARTIAL। প্রমাণ: `08_experiments/E2_labelling/pilot_v06/review/C002.json:$.manual_additions`, `08_experiments/E2_labelling/pilot_v06/review_amendments/C002.json:$.message_decisions`। |
| Missed evidence উদ্ধার, target-এ decisive নয় | C005 | Unknown-TAN 404 test ও architecture description উদ্ধার; missing-body proposition assert করে না। `08_experiments/E2_labelling/pilot_v06/review/C005.json:$.manual_additions`। |
| নতুন discovery নয়, adopted precedent প্রয়োগ | B068/B005/B037/B042/B017 | §11.3 Scout framework-wide 400/404 precedent preserve। Tool-এর happy-path/auth assertions স্বাধীন error-intent নয়। `09_collab/logs/T36_scratch/review_stats.json:$.manual_accepted_adopted_precedent_items`; `08_experiments/R1_triage_codebook.md:276-280`। |

অতএব directed fallback-এ নতুন positive intent পাওয়া গেছে **১/২৪ searched item**-এ; সেটিই unambiguous decisive tool-miss case। পাঁচটি Scout precedent application-কে নতুন source recovery হিসেবে গোনা হয়নি। অন্য none_found result-কে “কোথাও evidence নেই” বলা হয়নি। Local git-এর তিনটি actual history hit-এর full message/file patch shallow EMB merge/import; behavior-specific fix নয়। প্রমাণ: `09_collab/logs/T36_scratch/review_stats.json:$.manual_new_independent_items`, `09_collab/logs/T36_scratch/fallback/patch_C002.txt:1-14`, `09_collab/logs/T36_scratch/fallback/patch_C005.txt:1-14`, `09_collab/logs/T36_scratch/fallback/patch_P018.txt:1-14`।

False scenario support-এর concrete witness: B068/B005/B017/B012-এর `ActivitiesIntegrationTest.java:146` আসলে GET favourites-এর success; `:216` valid-fixture PUT/PATCH success। M002-এ UI `GET /customer/new` test ও cart-payment 201 prose-ও target parse-error scenario নয়। C002/C005-এর raw conflicting মূলত success/error branches বা generated annotation echoes; positive-evidence majority vote ব্যবহার হয়নি। প্রমাণ: `08_experiments/E2_labelling/pilot_v06/review/B068.json:$.hits`, `08_experiments/E2_labelling/pilot_v06/review/B012.json:$.hits`, `08_experiments/E2_labelling/pilot_v06/review/M002.json:$.hits`, `08_experiments/E2_labelling/pilot_v06/review/C002.json:$.hits`, `08_experiments/E2_labelling/pilot_v06/review/C005.json:$.hits`।

**Coverage, deferral ও effort।** সব ২৪টি tool run exit 0 ও `scan.complete=true`; relevant local unreadable file, parse failure, timeout বা unavailable candidate patch পাওয়া যায়নি। Scanner-এর Scout skip হলো ১২টি bundled font/image এবং >2 MB swagger-ui.js; build/vendor output-ও বাদ। এগুলো scenario-specific normative intent source হিসেবে ব্যবহৃত হয়নি; tests/helpers/docs/config হাতে দেখা হয়েছে। চারটি source-এর git history shallow; remote/upstream change intent জানা নেই, local import-কে developer fix বলা হয়নি। এটি bounded local search completion; ইতিহাসের exhaustiveness নয়। প্রমাণ: `09_collab/logs/T36_scratch/search_summary.json:1`, `09_collab/logs/T36_scratch/coverage_inventory.json:1`, `09_collab/logs/T36_scratch/fallback/*_history_scope.txt:1-2`।

Coverage-এর কারণে `incomplete`/deferred item **০**। UNDECIDABLE **১১**টি evidence insufficiency/policy ambiguity, coverage deferral নয়। C005-এ একটি unresolved manual policy record আছে; তাই positive intent verdict দেওয়া হয়নি এবং same-class adjudication flag আছে। ⚠️ Shallow upstream history-কে কোন পরিস্থিতিতে “relevant missing history” ধরা হবে, codebook-এ আরও স্পষ্ট করা উচিত; এখানে কোনো নির্দিষ্ট অনুপস্থিত fix/patch-এর উপর সিদ্ধান্ত নির্ভর করেনি। প্রমাণ: `09_collab/logs/T36_scratch/comparison_summary.json:$.search_status_counts`, একই file `$.pilot_L1_counts`; `08_experiments/E2_labelling/pilot_v06/review/C005.json:$.manual_additions`, `09_collab/logs/T36_scratch/verification.json:$.unresolved_manual_policy_records`।

Tool subprocess সময়: মোট 13.898 s; median 0.773 s/item; range 0.179–0.883 s। Sample freeze থেকে decision freeze wall interval 912.4 s ≈ ১৫.২ min; ভাগ করলে 32.6 s/item, কিন্তু এতে setup, shared source review, incident correction ও output generation অন্তর্ভুক্ত। এটি individual active labelling time নয়। C002-এর অতিরিক্ত post-join evidence review এই original interval-এর বাইরে। Manual active time আলাদাভাবে instrument করা হয়নি; তাই per-item time-feasibility ফল আংশিক। নিচে প্রতিটি item-এর measured tool time ও review burden আছে। প্রমাণ: `09_collab/logs/T36_scratch/verification.json:$.search_seconds`, একই file `$.sample_to_decision_freeze_seconds`; প্রতিটি review-এর `$.effort`।

| Item | Tool seconds | Raw hits | Manual/context records |
|---|---:|---:|---:|
| B068 | 0.883 | 2 | 4 |
| B005 | 0.826 | 11 | 4 |
| C005 | 0.229 | 22 | 5 |
| B037 | 0.818 | 4 | 4 |
| B042 | 0.811 | 1 | 4 |
| B017 | 0.762 | 11 | 4 |
| P043 | 0.264 | 5 | 4 |
| P021 | 0.255 | 5 | 2 |
| C002 | 0.179 | 20 | 10 |
| P019 | 0.252 | 5 | 3 |
| B012 | 0.810 | 11 | 2 |
| B043 | 0.778 | 1 | 2 |
| B091 | 0.767 | 1 | 2 |
| B032 | 0.791 | 1 | 2 |
| B027 | 0.783 | 1 | 2 |
| P039 | 0.270 | 3 | 2 |
| M002 | 0.363 | 13 | 3 |
| B094 | 0.804 | 1 | 4 |
| B040 | 0.801 | 1 | 4 |
| B098 | 0.787 | 5 | 3 |
| P018 | 0.262 | 7 | 3 |
| M013 | 0.343 | 16 | 4 |
| B066 | not_run | 0 | 2 |
| P035 | not_run | 0 | 2 |
| B023 | not_run | 0 | 2 |
| B071 | not_run | 0 | 2 |
| B087 | 0.790 | 1 | 3 |
| P013 | 0.270 | 4 | 3 |

**Procedure/format-এ পাওয়া সমস্যা ও প্রস্তাবিত সংশোধন।** এগুলো review proposal; codebook/tool/edit করা হয়নি।

1. **Target proposition স্পষ্ট করুন।** Status-only search C005-এর missing-body obligation মাপে না; field/XML hit P013-এর JSON presence obligationও মাপে না। Schema direction, presence/absence এবং request/response side mandatory structured fields করুন; status-only verdict-কে unrelated constraint-এ প্রযোজ্য বলা যাবে না। প্রমাণ: `09_collab/logs/T36_scratch/search/C005.json:$.field`, `08_experiments/E2_labelling/pilot_v06/review/C005.json:$.target`, `08_experiments/E2_labelling/pilot_v06/review/P013.json:$.manual_additions`।

2. **Raw polarity ও branch filtering-এর উদাহরণ বাড়ান।** `supports_spec` থেকে SPEC দেওয়া উল্টো attribution হবে; matched route-এর পাশের assertion method/branch না-ও মিলতে পারে। Full helper/call-chain resolution review বাধ্যতামূলক থাকুক। Positive test absence-কে positive implementation intent বলা যাবে না। প্রমাণ: `08_experiments/E2_labelling/pilot_v06/review/B068.json:$.hits`, `08_experiments/E2_labelling/pilot_v06/review/B012.json:$.hits`, `08_experiments/R1_triage_codebook.md:291`।

3. **Comparison schema-তে authority আলাদা রাখুন।** `primary_L1`, `both_candidate`, `adjudicated_L1` এবং exact-versus-compatible denominator ঘোষণা করলে ছয়টি BOTH mismatch substantive change বলে ভুল হবে না। প্রমাণ: `09_collab/logs/T36_scratch/comparison_summary.json:$.per_stratum.BOTH`, `08_experiments/R1_triage_codebook.md:217-219`।

4. **UNDECIDABLE+TEST aggregation নির্দিষ্ট করুন।** §10.4 কেবল SPEC+TEST নির্ধারণ করে। P043/P021/P019-এ unsupported SPEC বাদ দিলে অবশিষ্ট U+TEST কী হবে স্পষ্ট row দরকার। এই pilot conservative UNDECIDABLE দিয়েছে; majority occurrence দিয়ে SPEC তৈরি করেনি। Historic numeric-format false-positive component-এর checker revisionও manifest-এ আলাদা রাখা ভালো। প্রমাণ: `08_experiments/R1_triage_codebook.md:228-237`, `08_experiments/E2_labelling/pilot_v06/review/P019.json:$.decision.documented_exception`, `08_experiments/E2_labelling/pilot_v06/review/P043.json:$.decision.message_decisions`।

5. **Same-class authority handoff operational করুন।** Q3 অনুযায়ী Claude provisional decision কে/কোথায় দেবেন, অপেক্ষাকালীন L1/flag কী হবে এবং supervisor outcome কোথায় join হবে স্পষ্ট করুন। C005-এ source retrieval সম্পূর্ণ হলেও policy independence অনির্ধারিত; code-only positive SPEC দিয়ে ঘাটতি পূরণ করা হয়নি। প্রমাণ: `08_experiments/R1_triage_codebook.md:293`, `08_experiments/E2_labelling/pilot_v06/review/C005.json:$.decision.adjudication_flag`।

6. **Complete বনাম unavailable-history ও deferral representation নির্দিষ্ট করুন।** “local shallow snapshot searched” এবং “relevant upstream fix unavailable” আলাদা reason code দরকার। Known relevant gap না মিটলে `incomplete` দিয়ে label deferred রাখার নিয়ম আছে, কিন্তু L1 sentinel (যেমন DEFERRED বনাম blank) ও agreement denominator নির্ধারিত নয়। এই zero-deferral pilot সেই stopping behavior empirically exercise করেনি; held-out run-এর আগে এটিকে format check করা দরকার। প্রমাণ: `08_experiments/E2_labelling/proposals/CODEBOOK_11_4_PROPOSAL.md:54-56,69-75`, `08_experiments/R1_triage_codebook.md:297-298`, `09_collab/logs/T36_scratch/comparison_summary.json:$.search_status_counts`।

7. **Effort ও bounded retrieval-এর recording উন্নত করুন।** Per-item review start/end এবং shared-source reuse আলাদা নিলে active effort মাপা যাবে। Empty-path fallback নিষিদ্ধ করা ও source-window printing-এ credential redaction প্রয়োজন—এই task-এর বাস্তব দুই incident দেখিয়েছে reporting validation একা execution boundary রক্ষা করে না। প্রমাণ: `08_experiments/E2_labelling/pilot_v06/review/C002.json:$.effort`, `09_collab/logs/T36_scratch/incident.json:1`, `09_collab/logs/T36_scratch/fallback.py:17-25`।

**Verification ও সীমাবদ্ধতা।** 4033টি audit assertion pass: sample regeneration, hidden columns, freeze-before-join, ২৮টি row ও review coverage, ১৫২টি exact hit index, five-part checklist, accepted-basis gates, text/JSON/CSV/spec locators, raw/spec/tool/review hashes এবং known demo credential-এর exact-value artifact scan। Deliverable-এ সেই demo value পাওয়া যায়নি; terminal transcript-এর আগের exposure ফেরত নেওয়া যায়নি। ৬০০টি protected hash-এর মধ্যে ৫৯৯টি অপরিবর্তিত; `08_experiments/tools/test_specmut.py`-এ drift ধরা পড়েছে। Source/spec/intent tool/final labels অপরিবর্তিত। T36 script ওই unrelated test file লেখে না; ⚠️ concurrent T37 কাজ এর সম্ভাব্য কারণ, এই pilot থেকে তা নিশ্চিত করা হয়নি। প্রমাণ: `09_collab/logs/T36_scratch/verification.json:1`, `09_collab/logs/T36_scratch/protected_before.json:1`, `09_collab/tasks/T36.md:65-73`।

⚠️ n=28, stratified selection, prior exposure, একই model-family-এর আগের labelling, correlated fingerprints/shared root causes, চারটি Java SUT এবং এক seed-এর adjudicated comparator—কোনোটিই representative accuracy benchmark বা human inter-rater reliability তৈরি করে না। ৫/২৮ substantive proposal-কে population change-rate হিসেবে extrapolate করা যাবে না। Independent source recovery সীমিত, local history shallow, per-item active time অপরিমাপিত এবং zero-deferral sample stopping-rule feasibility পরীক্ষা করে না। সবচেয়ে বড় execution limitation হলো উপরোক্ত boundary incidents; ভবিষ্যৎ E5 blind labelling-এ clean access history দাবি করা অনুচিত। কোনো SUT/external project code, Docker/Java/Maven বা network চালানো হয়নি। প্রমাণ: `09_collab/logs/T36_scratch/sample.json:1`, `08_experiments/E2_labelling/FINAL_LABELS.md:48-52`, `09_collab/logs/T36_scratch/verification.json:1`, `09_collab/logs/T36_scratch/incident.json:1`।

Deliverables: `08_experiments/E2_labelling/pilot_v06/T36_pilot_labels.csv`, `08_experiments/E2_labelling/pilot_v06/review/`-এর ২৮টি JSON, অতিরিক্ত immutable `review_amendments/C002.json`, এবং এই report। Raw artifacts/scripts/freeze/comparison/verification: `09_collab/logs/T36_scratch/`। C005-এর same-class decision এবং পাঁচটি substantive proposal adjudicator/supervisor-এর review-এর জন্য রইল; পুরোনো final labels বা codebook rewrite করা হয়নি।
