# T27 — EvoMaster proposal; E5 integration BLOCKED

## অবস্থা ও blocker

Harness-এর review-only proposal প্রস্তুত ও offline checks PASS। কিন্তু সম্পূর্ণ T27 **BLOCKED**: বর্তমান E5 wrapper বাধ্যতামূলকভাবে `DATA_GEN=all` বসায়; proposal-এর required unsupported-option rejection-এ EvoMaster collection শুরুর আগেই থামবে। E5 validator-ও Schemathesis-specific argv/JUnit/artifacts চায়। অথচ T27-এ `E5_codemut/` পরিবর্তন নিষিদ্ধ। তাই এই ফলকে সম্পূর্ণ E5 support বা T27 DONE বলা হচ্ছে না। Protocol অনুযায়ী blocker report/board-এ লিখে কাজ থামানো হচ্ছে। Evidence: `08_experiments/E5_codemut/e5_pipeline.py:94–106`; `validate_pair.py:146–161,241–255,351`; `09_collab/tasks/T27.md` Goal/Constraints; `09_collab/PROTOCOL.md:15`।

## কী করা হয়েছে

`08_experiments/E1_pilot/harness_v2/proposals/harness.evomaster.proposed.diff`, `harness.evomaster.base-sha256.json` এবং `README.md` লেখা হয়েছে। Diff-এর paths `08_experiments/` থেকে `patch -p1`-এর উপযোগী; তিনটি existing file-এর base SHA-256 সংরক্ষিত। Patch-এ চারটি new file ও তিনটি modified file আছে; production harness-এ apply করা হয়নি। Evidence: `09_collab/logs/T27_scratch/build_and_validate.py:24–53`; `patch-apply.txt:1–7`; `validation.json:3–11`; proposal-এর `harness.evomaster.base-sha256.json:2–4`।

Staged implementation-এ `FUZZER=evomaster` black-box REST argv, immutable local image, `SEED`, `--maxTime ${budget}s`, generated Java source ও CSV statistics যুক্ত করেছে। Task-supplied version `6.2.0` record হয়; image-এর version runtime-এ নতুনভাবে যাচাই করা হয়নি। EvoMaster branch image pull/help চালায় না। Evidence: `09_collab/tasks/T27.md:12–15`; `09_collab/logs/T27_scratch/staged/harness_v2/run_pilot.sh:34–40,186–190`; `fuzzer_args.sh:16–22`।

EvoMaster-এর saved help অনুযায়ী `--base`-এ API path দেওয়া যাবে না; সেই path schema থেকে আসে। তাই `--base http://mitmproxy:8080`, same compose network ও schema/`BASE_PATH` consistency guard রাখা হয়েছে। Run-এর অপরিবর্তিত `spec.test.json` আলাদাভাবে read-only mount হয় এবং সেটিই `--schema`; path/server ambiguity fail করে। চার SUT-এর বর্তমান schema/config এই guard-এ PASS। Evidence: `09_collab/logs/T27_scratch/evomaster_help.txt:177–190,1531–1540`; staged `evomaster_guard.py:19–53`; `run_pilot.sh:282–285`; `static-tests.txt:54–61`। ⚠️ Actual Docker routing, absolute-server authority replacement ও read-only mount-এর runtime আচরণ যাচাই হয়নি।

Auth resolution আগের fixture/runtime source-ই ব্যবহার করে; EvoMaster argv-এ `--header0` বসে। Saved argv-এ value-এর জায়গায় `<redacted>`; streaming log ও generated artifacts-এর final recursive redaction আগের redactor দিয়ে হয়। `run.json`-এ fuzzer, image digest, version, redacted argv/file, exit ও nested output hashes যোগ হয়েছে। Evidence: staged `run_pilot.sh:49–70,275,285`; `fuzzer_args.sh:25–31`; `run_metadata.py:78–96`; `test_fuzzer_args.py:205–283`; `static-tests.txt:65–68`।

Existing exit policy-এর মতো `0|1` কেবল required output থাকলে গ্রহণ করা হয়; EvoMaster-এর ক্ষেত্রে nonempty statistics ও generated Java source লাগে। `124|137` incomplete, অন্য exit propagate করে। Search-এর `maxTime` ঠিক budget; outer watchdog `budget+120` seconds, তারপর existing 20-second kill grace। Cleanup/coverage ও nonempty-exchanges completion gates আগের মতো আছে। Evidence: staged `run_pilot.sh:111–140,279–312`; `evomaster_guard.py:56–63`; original `08_experiments/E1_pilot/harness_v2/run_pilot.sh:278–284`। ⚠️ EvoMaster exit `1`-এর actual failure modes এই offline task-এ observed নয়; output gate-টি বর্তমান harness semantics অনুসরণ করে।

`ONLY_OPS` mutation-candidate selection হিসেবেই থাকে; baseline EvoMaster run-এ reject হয়। Nonempty `DATA_GEN`-এর সব value EvoMaster-এ reject হয়; positive/negative/all-এর সমতুল্যতা অনুমান করা হয়নি। Evidence: staged `evomaster_guard.py:8–16`; `run_pilot.sh:19–29,167–175`; `static-tests.txt:56,62–63`।

## Default ও analysis compatibility

Default Schemathesis argv এবং saved redacted argv-এর ছয়টি golden case original, unmodified shell statements থেকে তৈরি; explicit default, custom base/check/seed/timeout, auth এবং DATA_GEN variants আছে। সাতটি original source fragment hash দিয়ে Docker argv, preflight, readiness, cleanup/coverage, mutation pool, de-recursion ও exit policy সংরক্ষণ যাচাই করা হয়েছে। Evidence: `09_collab/logs/T27_scratch/make_golden.py:16–63`; staged `fuzzer-golden.json`-এর `cases` ও `preserved_fragments`; `static-tests.txt:45–53`। নতুন `fuzzer` metadata field ও harness hashes ইচ্ছাকৃতভাবে বদলাবে; actual default fuzzer execution করা হয়নি।

`analyse_run.sh` পরিবর্তিত হয়নি। তার `schema-image.json`, `schemathesis_image` এবং `generator-input.json` contract রাখতে EvoMaster image-এর compatibility alias ও `spec.test.json`-এর byte-copy রাখা হয়েছে। `schemathesis_exit=not_started`; actual value `evomaster_exit`-এ থাকে। Existing provenance hash checks বজায় আছে। Evidence: original `08_experiments/E1_pilot/harness_v2/analyse_run.sh:22–56`; staged `run_pilot.sh:189–190,270–275`; `run_metadata.py:39,78–96`; `validation.json:48`। ⚠️ এটি source/metadata compatibility evidence; EvoMaster-generated `exchanges.jsonl` দিয়ে end-to-end conformance/attribute replay করা হয়নি।

## যাচাইয়ের ফল

একটি `/tmp/T27-patch-validation-*` copy-তে patch zero fuzz-এ apply করে প্রতিটি patched file-এর staged bytes মিলেছে। `static_validate.py` exit `0`; existing 13 এবং new 24 unit tests মিলিয়ে **37/37 PASS**; ছয়টি shell file-এর `bash -n` PASS। Live harness-এর original **22/22 file অপরিবর্তিত**। Evidence: `09_collab/logs/T27_scratch/patch-apply.txt:1–7`; `static-tests.txt:41–75`; `validation.json:12–73`।

Tests actual argv builders, original golden argv/redaction, shell metacharacter preservation, fuzzer selection, unsupported options, numeric bounds, four real schema paths, ambiguous server rejection, missing outputs, streaming/recursive auth redaction এবং metadata identity/exit/hashes যাচাই করে। Fixture-এ কেবল synthetic credentials আছে। Evidence: staged `test_fuzzer_args.py:1–288`; `static-tests.txt:45–73`।

কোনো Docker/Java/Maven/fuzzer/SUT/network বা external-code execution করা হয়নি। Temporary copy-তে EMB/v1 files existing static checks-এর read-only input হিসেবে symlink করা হয়েছে; fuzzer orchestration execute করা হয়নি। Evidence: `09_collab/logs/T27_scratch/build_and_validate.py:55–77`; `static-tests.txt:75`। Allowed proposal/scratch/report/board append ছাড়া implementation file-এ write করা হয়নি; initial/live harness digests মেলে। Evidence: `build_and_validate.py:24–53,77–88`; `validation.json:44–73`; `freeze.json`।

## সীমাবদ্ধতা ও পরবর্তী প্রয়োজন

প্রথম অনুমোদিত smoke run-এ proxy/base path, schema compatibility, non-root writable output directory, complete statistics/tests, auth sanitization, exchanges ও JaCoCo যাচাই প্রয়োজন; এখানে সেগুলির runtime success দাবি নেই। Generated Java tests compile/run করা হয়নি। `MAX_EXAMPLES`, `SCHEMA_CHECKS` ও Hypothesis phases EvoMaster control নয়; metadata compatibility-র legacy fields। Evidence: staged `fuzzer_args.sh:4–22`; `run_pilot.sh:282–285`; `static-tests.txt:75`।

Coordinator-এর জন্য নির্দিষ্ট open scope: E5 wrapper-এর generator-specific environment এবং validator-এর genuine EvoMaster argv/completion/artifact/paired-metadata handling-এর আলাদা task প্রয়োজন। Existing validator-এর জন্য Schemathesis JUnit/argv বানিয়ে দেওয়ার কোনো synthetic compatibility layer দেওয়া হয়নি। বর্তমান write scope-এ এই blocker সমাধান সম্ভব নয়; full E5 support অনিষ্পন্ন। Evidence: `08_experiments/E5_codemut/e5_pipeline.py:98–106`; `validate_pair.py:146–161,241–255,351`; `09_collab/tasks/T27.md` Constraints।
