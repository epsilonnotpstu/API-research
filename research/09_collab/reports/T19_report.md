# T19 — E5 code-mutation design ও tool

T19-এর write-only কাজ সম্পন্ন: চার SUT-এর জন্য পাঁচ operator family, ২০টি reviewed source site, copy-only `codemut.py`, synthetic tests, দশটি প্রথম-batch proposal এবং ভবিষ্যৎ build/run/analysis plan দেওয়া হয়েছে। কোনো real mutant compile/run বা kill দাবি করা হচ্ছে না। সব runtime expectation **[H]**। প্রমাণ: `08_experiments/E5_codemut/OPERATORS.md:1–29`, `sites.json` (`site_id` rows), `09_collab/logs/T19_scratch/validation.json` (`catalogue`, `execution`, `status`)।

এই report-এ `sites.json`, `OPERATORS.md`, `README.md`, `codemut.py`, `test_codemut.py` বলতে `08_experiments/E5_codemut/`-এর ফাইল; `validation.json`, `validate.py`, `protected_before.json` বলতে `09_collab/logs/T19_scratch/`-এর ফাইল বোঝানো হয়েছে।

## কী তৈরি হয়েছে

- `08_experiments/E5_codemut/OPERATORS.md`: `DROP_VALIDATION`, `WRONG_STATUS`, `DROP_NULL_CHECK`, `RESP_FIELD`, `REJECT_VALID`-এর expected IMPL/L2 ও checker signal; প্রতি family-তে চার SUT-এর একটি করে site। প্রতিটি site-এর source `file:line`, original contract locator, affected operation, captured exposure, condition এবং witness plan আছে। তালিকাটি source/spec পড়ে তৈরি; arbitrary Java AST mutation নয় (`OPERATORS.md:1–41`; `sites.json`, সব ২০ `site_id`; `validation.json`, `catalogue.per_operator`, `catalogue.rows`)।
- `08_experiments/E5_codemut/codemut.py`: reviewed file SHA-256, unique exact anchor ও line যাচাই করে আলাদা source copy-তে একটিমাত্র Java edit; `<out>/source/`, `patch.diff`, `manifest.json` তৈরি করে। Manifest-এ snippets, operation mapping, expected labels/signals, original/mutated file/tree hashes, patch/catalogue/site hashes এবং selection provenance থাকে। `mutations` operation records existing `attribute.py`-compatible; `operations_mutated` measured coverage নয় (`codemut.py:121–237`; `08_experiments/tools/attribute.py:25–31`)।
- `08_experiments/E5_codemut/README.md`: চার SUT-এর Maven module/JAR commands, original/control copy, distinct image tags, frozen runtime base, dependency/source verification, paired harness commands, fresh analysis ও independent triage-এর plan। Exact proposed harness diff README-তে embedded এবং আলাদা `harness.proposed.diff`-এও আছে; live harness-এ apply করা হয়নি (`README.md`, “Future build commands for Claude”, “Proposed harness changes”, “Future paired harness runs”; `validation.json`, `static.embedded_diff_exact`, `protected_files`)।

Tool existing output overwrite করে না; source/output overlap, EMB-এর মধ্যে output, retained symlink/nonregular file, unsafe site path এবং source/hash/line drift প্রত্যাখ্যান করে। Build/VCS/cache directories বাদ যায়; resource bytes ও modes রাখা হয়। Copy শেষে original inventory পুনরায় যাচাই হয়। Copy/I/O failure-এ incomplete output থেকে যেতে পারে, যা নতুন invocation reuse করে না। এটি concurrent hostile filesystem-এর security boundary নয় (`codemut.py:47–56,121–200`; `README.md:44–52`; `test_codemut.py:92–195`)।

Seed selection হলো sorted candidate pool-এ `sha256(sut:operator:seed) mod count`; explicit `--site`-কে একই SUT/operator-এর হতে হয়। বর্তমান registry-তে প্রতিটি SUT/operator-এর একটি site হওয়ায় seed বদলালে site বদলাবে না; synthetic multi-site test selection ও ordering যাচাই করে (`codemut.py:103–118`; `test_codemut.py:77–84`; `sites.json`, সব rows)।

## কোন traffic দেখে নির্বাচন

`exposure.json`-এ inspection-এর সময় নির্বাচিত latest complete seed-1 baseline প্রতি SUT-এ freeze করা হয়েছে; run metadata ও exchange hashes রাখা আছে। এগুলো নতুন E5 matched control নয়। Method/path অনুযায়ী matched captured requests-এর পুনর্গণনা:

| SUT | Operation rows | Matched captured requests |
|---|---:|---:|
| scout-api | 49 | 4702 |
| swagger-petstore | 19 | 1582 |
| market | 13 | 1138 |
| cwa-verification | 5 | 368 |

প্রমাণ: `08_experiments/E5_codemut/exposure.json`, `runs.<sut>` ও `operations.evidence_id`; `09_collab/logs/T19_scratch/validation.json:186–211`। সব ৮৬ row-এর status count এবং ২৪৮ exchange locator যাচাই হয়েছে; physical JSONL lines দিয়ে parse করা হয়েছে। ⚠️ HTTP operation reached হওয়া edited branch বা bytecode coverage প্রমাণ করে না (`validation.json:186–211`; `09_collab/logs/T19_scratch/validate.py`, exposure loop; `OPERATORS.md:32–41`)।

## প্রথম batch-এর দশটি proposal

সবগুলো **[H]**: compilation এবং same-state control/mutant witness লাগবে। নিচের row IDs সরাসরি `--site`-এ দেওয়া যায় (`sites.json`, উল্লিখিত rows; `OPERATORS.md`, “First E5 batch” table)।

| SUT | প্রস্তাবিত sites | নির্বাচনের কারণ ও exposure gate |
|---|---|---|
| scout-api | `scout-wrong-status`, `scout-drop-null`, `scout-reject-valid` | roles-এ 200 এবং tags-এ 95টি 200 পাওয়া গেছে; optional query অনুপস্থিত successful witness আছে। [H] status/crash/rejection আলাদাভাবে পরীক্ষা করা যাবে (`exposure.json`, `scout-api:GET /v1/system/roles`, `scout-api:GET /v2/tags`)। |
| swagger-petstore | `petstore-response-field`, `petstore-reject-valid` | findByStatus-এর nonempty 200-তে required `name` আছে। নির্বাচিত traffic-এ getPetById-এর 200 নেই; reject-valid বলার আগে clean seeded pet-এর control 200 আবশ্যক (`exposure.json`, `swagger-petstore:GET /pet/findByStatus`, `swagger-petstore:GET /pet/{petId}`; `sites.json`, দুই site-এর `conditions`)। |
| market | `market-wrong-status`, `market-drop-null`, `market-response-field` | listing-এর nonempty 200-তে `price`; detail-এ 44টি 404। [H] নতুন 418, absence-path 500 ও required-price diagnostic দেখার সুযোগ আছে; existing schema/crash fingerprint আলাদা করতে হবে (`exposure.json`, `market:GET /products`, `market:GET /products/{productId}`; `sites.json`, তিন rows)। |
| cwa-verification | `cwa-drop-validation`, `cwa-drop-null` | registration binding 400 এবং absent TAN 404 দেখা গেছে। [H] এই witness-এ missing test-result backend লাগে না। token-success traffic নেই বলে wrong-status/response-field প্রথম batch-এ নেই (`exposure.json`, `cwa-verification:POST /version/v1/registrationToken`, `cwa-verification:POST /version/v1/tan/verify`; `sites.json`, দুই pilot rows)। |

তিনটি catalogue candidate-এ current conformance signal ইচ্ছাকৃতভাবে empty: `scout-drop-validation`-এর intended numeric rule spec-এ string; `scout-response-field` optional field; `petstore-wrong-status` schema-free default-এর মধ্যে পড়ে। এগুলো oracle-blind/semantic negative control, detector miss বা সফল kill বলে দাবি করা যাবে না। Original contract locators সংশ্লিষ্ট `OPERATORS.md` site section-এ আছে (`sites.json`, ওই তিন row-এর `expected_conformance_signal`, `conditions`; `08_experiments/tools/conformance.py:399–442`)।

## Attribution-এর সীমা

Existing fresh `attribute.py` mapped operation-এর NEW-কে `NEEDS_MANUAL`, off-operation NEW-কে `UNEXPLAINED` রাখে; manifest-এর expected IMPL একটি expectation মাত্র। Synthetic interoperability probe-ও ঠিক এই ফল দিয়েছে। E5-তে replay mode ব্যবহার করা যাবে না: অপরিবর্তিত spec/exchanges replay executable mutation পর্যবেক্ষণ করে না; manifest label বসালে evaluation circular হবে (`08_experiments/tools/attribute.py:1–7,25–57`; `validation.json:225–228`; `README.md`, “Pair validation, fresh analysis and independent attribution”)।

NEW ছাড়াও PERSISTENT fingerprint-এর occurrence বৃদ্ধি দেখতে হবে। Stateful off-operation failure, pre-existing/BOTH/TEST diagnostics এবং একই fingerprint-এ মিশে যাওয়া field failure manual review করতে হবে। বর্তমান pilot evidence-ও occurrence ও state-propagation সীমা দেখায়; সেটি E5 result নয় (`08_experiments/E1_pilot/pilot_results/PILOT_SUMMARY.md:79–100`; `08_experiments/E2_labelling/FINAL_LABELS.md:18–24`; `README.md`, final analysis paragraphs)।

`triage.py`-এর CLI P001 sheet/messages-এর জন্য; E5 violation JSONL সরাসরি input হিসেবে নেওয়ার adapter নেই। Plan-এ independent blinded source/log/request review, অথবা আলাদা reviewed adapter-এর কথা বলা হয়েছে। Predictor/label freeze-এর পরে manifest join হবে। Market-এর 406-এর জন্য default ও SUT oracle দুটো পাশাপাশি report করার commands আছে (`08_experiments/tools/triage.py:852–864`; `08_experiments/R1_triage_codebook.md:251–259`; `README.md`, analysis commands ও triage paragraph)।

## যাচাই ও execution boundary

- **২২/২২ synthetic tests PASS**: পাঁচ operator, full copy/patch/manifest, selection, no overwrite/overlap/EMB write, symlink/path/drift rejection, resources/modes, CRLF/EOF ও own CLI। কোনো real SUT build fixture নেই (`09_collab/logs/T19_scratch/tests.txt:1–27`; `08_experiments/E5_codemut/test_codemut.py:1–217`)।
- **২০/২০ source anchors PASS**: exact hash/line/unique anchor যাচাই; edits শুধু memory-তে; সব mapped operation original spec-এ আছে (`validation.json`, `catalogue.rows`; `validate.py`, catalogue loop)।
- **Static PASS**: আটটি own/staged Python file, README-এর ছয় Bash block, পাঁচ inline Python block, চার proposed diff hunk; embedded diff exact (`validation.json:212–224`)। Static syntax check runtime integration প্রমাণ করে না।
- শুরুতে snapshot নেওয়া **৩৩টি harness/tool regular file-এর hash অপরিবর্তিত**; hidden/cache paths এই গণনার বাইরে। Site source hashes-ও মিলেছে। Live harness/tools/external/runs-এ এই task কোনো write করেনি; Maven/Java/Docker/SUT/Schemathesis execute হয়নি (`validation.json:229–240`; `protected_before.json`, path-keyed digests; `09_collab/tasks/T19.md`, Allowed write paths/Constraints)।

নিজস্ব Python `/usr/bin/python3 -I -B` এবং Bash syntax parsing-ই চালানো হয়েছে। Shell-plan validation-এ parameter expansion-এর একটি quoting error ধরা পড়ে ঠিক করা হয়েছে; final shell checks PASS (`09_collab/logs/T19_scratch/validate.py`, static checks; `validation.json:212–224,234–240`)।

## অবশিষ্ট প্রশ্ন ও পরবর্তী execution gate

1. Original Java8/Java11 Maven build image IDs/digests এই task-এর evidence-এ নির্ধারিত নয়। User-কে জিজ্ঞাসা করা হয়েছে; উত্তর ছাড়া guessed tag বসানো হয়নি। README-তে surviving original container থেকে immutable ID উদ্ধারের commands এবং mandatory variables আছে; coordinator-কে প্রত্যেক SUT-এর original build identity মিলিয়ে নিতে হবে। Original argv-ও দাবি করা হয়নি—এগুলো proposed package commands (`README.md:60–73`, “Future build commands for Claude”)।
2. সব real edit compile-valid কি না, WRITE_ONLY বাস্তব serializer-এ কার্যকর কি না, guard/binding/exception mapping ও readiness টিকে থাকে কি না—সবই **[H]**। Compile-invalid, oracle-blind, unexposed, surviving exposed, causally killed এবং flaky ফল আলাদা রাখতে হবে (`sites.json`, `conditions`; `OPERATORS.md`, final paragraph; `README.md`, final evaluation paragraph)।
3. Live batch শেষ হলে Claude exact proposed diff review/rebase করবেন; তারপর supervisor-authorized execution। পুরোনো control পুনর্ব্যবহার বা `analyse_run.sh`-এর image/JAR compatibility guard দুর্বল করার প্রস্তাব নেই। নতুন matched controls, frozen provenance ও repeated baseline noise floor লাগবে (`README.md`, “Proposed harness changes”, “Future paired harness runs”, “Pair validation”; `09_collab/PROTOCOL.md:12–14`)।
