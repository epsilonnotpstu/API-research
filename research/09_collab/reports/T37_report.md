# T37 — REQUEST_STRICT keyword ablation knob

`specmut --strict-keywords` এবং harness `STRICT_KEYWORDS` সরাসরি implement করা হয়েছে। Default compatibility-এর ১৬টি pre-edit CLI golden case, ১৪৪টি existing real-spec property case, নতুন ১০টি specmut regression test, harness-এর ৩৯টি test এবং static validation PASS। Market-এর ছয়টি offline variant-এ আগের sampling এবং প্রত্যাশিত keyword subset মিলেছে। Seed 1-এর পুরোনো selected-but-unedited operation saved manifest-এ অনুপস্থিত ছিল; নিচে সেই পার্থক্য আলাদা করে দেখানো হয়েছে। [Evidence: `09_collab/logs/T37_scratch/test_specmut.txt:1–15,161`; `test_fuzzer_args.txt:42–44`; `static_validate.txt:89`; `sanity.json`, `rows[seed=1..3]`, `all_checks_passed`। এই report-এ সংক্ষিপ্ত log filename-গুলো `09_collab/logs/T37_scratch/`-এর অধীনে।]

Code locator-এ `specmut.py` ও `test_specmut.py` হলো `08_experiments/tools/`-এর file; অন্য সংক্ষিপ্ত harness source filename-গুলো `08_experiments/E1_pilot/harness_v2/`-এর file।

## 1. Implementation ও selection

- `maximum`, `maxLength`, `required`, `param_required` চারটি family অনুমোদিত। `required` শুধু object-এর required-list বদলায়; `param_required` শুধু query/header parameter-এর flag flip করে। CLI option absent থাকলে পুরোনো mutator path ব্যবহৃত হয়। Option অন্য fault-এর সঙ্গে, empty list, unknown name, whitespace বা duplicate দিলে exit 2; output তৈরি হওয়ার আগেই validation হয়। [Evidence: `08_experiments/tools/specmut.py:24,152–173,250–275,302–313`; `test_specmut.py:354–375`।]
- Candidate pool-এ সম্ভাব্য STRICT edit থাকার শর্ত **আগেও ছিল না**: path exclusion ও optional `only` pool-এর পরে sorted operations থেকে `Random(f'{seed}:{fault}')`, একই rounding এবং একই sample নেওয়া হয়। এই algorithm `select_operations()`-এ আলাদা করা হয়েছে; sampling-এর পরে keyword family filter হয়। ফলে keyword-specific eligibility বা resampling নেই। [Evidence: `specmut.before.py:230–245`; `08_experiments/tools/specmut.py:233–247,266–277`; `test_specmut.py:241–288`।]
- Retained edit শূন্য হলে `$ref` inlining/path-level parameter copying-সহ operation-এর side effect undo হয়। Operation `mutations`-এ যায় না। Explicit option-এ manifest-এ sorted `strict_keywords` এবং sorted `selected_no_edit` যোগ হয়; দুটো list-এর operation union হলো original sample। Option absent থাকলে এই দুই field-ই অনুপস্থিত। Python `mutate()`-এর পুরোনো triple return বজায় আছে। [Evidence: `08_experiments/tools/specmut.py:277–289,328–332`; `test_specmut.py:265–319,346–352`; `test_specmut.txt:1–15`।]
- Selected operation-এর retained edit থাকলে প্রয়োজনীয় structural inlining manifest-এ আগের `document_edits()` দিয়ে record হয়। তাই literal document patch-এর কোনো schema replacement-এ একাধিক nested constraint থাকতে পারে; ablation যাচাই করা হয়েছে **semantic keyword edits-এর subset** এবং reconstructed document দুটোতেই। বাদ দেওয়া family-এর নতুন constraint এতে ঢোকে না; original spec-এর আগে থেকেই থাকা constraint বজায় থাকে। [Evidence: `08_experiments/tools/specmut.py:210–230,280–287`; `test_specmut.py:221–239,321–344`; `sanity.py:61–116`; `sanity.json`, প্রতিটি variant-এর `semantic_edits`, `output_equals_independent_old_mutator_edit_subset`, `manifest_equals_expected_structural_patch`।]

## 2. Harness policy ও ব্যবহার

`build_strict_args()` shared validation করে: unset/empty হলে empty array; অন্যথায় চার নামের distinct comma-list এবং `fault=REQUEST_STRICT` দরকার। Invalid value error message-এ echo হয় না। `run_pilot.sh` Docker/tool checks এবং run-directory creation-এর আগে validate করে। Oracle mutation ও derecursed generator-input mutation দুটোই একই `strict_args` array নেয়। Schemathesis, EvoMaster spec input এবং EvoMaster derecursed input-এর shell routing/actual specmut argv offline tests-এ পরীক্ষা করা হয়েছে। [Evidence: `08_experiments/E1_pilot/harness_v2/fuzzer_args.sh:4–18`; `run_pilot.sh:41–43,188–189,230–231`; `test_fuzzer_args.py:477–508,551–621`; `test_fuzzer_args.txt:35–44`।]

**Batch policy:** non-empty `STRICT_KEYWORDS` থাকলে `FAULTS`-এ ঠিক একবার `REQUEST_STRICT` থাকতে হবে। Default/all-fault batch, mixed fault, empty/whitespace-only list বা duplicate fault exit 2 দেয়, batch output তৈরির আগে। Comparison baseline-এর child process-এ knob empty করা হয়; mutated child original keyword value পায়। Direct baseline run-এ non-empty knob নিষিদ্ধ। `run_metadata.py` কেবল non-empty knob-এ sorted `strict_keywords` লিখে; baseline/unset/empty run-এ field নেই। [Evidence: `08_experiments/E1_pilot/harness_v2/run_batch.sh:24–35,48–52`; `run_metadata.py:81–82`; `test_fuzzer_args.py:460–467,489–549`।]

Claude-এর runtime smoke-এর জন্য নিচের invocation ব্যবহার করা যাবে; এখানে এগুলো চালানো হয়নি। Schemathesis-এর জন্য `FUZZER=schemathesis`; EvoMaster-এর জন্য নিচের মতো `FUZZER=evomaster`। Derecursed EvoMaster চাইলে `EVOMASTER_INPUT=derecursed` যোগ করতে হবে। [Evidence: `08_experiments/E1_pilot/harness_v2/run_pilot.sh:24–37`; `run_batch.sh:24–35,45–52`; execution record `verification.json`, `execution_boundary`।]

```bash
STRICT_KEYWORDS=required FAULTS=REQUEST_STRICT FUZZER=evomaster \
  08_experiments/E1_pilot/harness_v2/run_batch.sh market 1 2 3

STRICT_KEYWORDS=maximum,maxLength FAULTS=REQUEST_STRICT FUZZER=evomaster \
  08_experiments/E1_pilot/harness_v2/run_batch.sh market 1 2 3
```

## 3. Default compatibility ও tests

চারটি EMB spec—`market`, `scout-api`, `swagger-petstore`, `cwa-verification`—প্রত্যেকটির চার fault-এর pre-edit output থেকে golden নেওয়া হয়েছে (`severity=30`, `seed=7`)। Serialized spec, serialized manifest ও stdout-এর **৪৮টি SHA-256** test code-এ pin করা আছে; বর্তমান absent-option output সবগুলোতে byte-identical। Explicit all-four option-এ spec/stdout এবং mutation records default-এর সমান; শুধু opt-in metadata যোগ হয়। [Evidence: `default_goldens.json`, চার spec-এর চার fault row; `08_experiments/tools/test_specmut.py:113–162,205–219,307–319`; `test_specmut.txt:1–15`।]

Harness-এর existing fuzzer argv golden file অপরিবর্তিত আছে। দুই mutation command-এর actual argv unset ও empty knob-এ পুরোনো argument sequence-ই দেয়; non-empty knob-এ শুধু `--strict-keywords VALUE` যোগ হয়। আগে pin করা shell fragment hash যাচাইয়ে শুধু empty-array expansion-এর নতুন source text সরিয়ে পুরোনো bytes-এর সঙ্গে তুলনা করা হয়; বাকিগুলো আগের মতো pinned। `run.json`-এর current code provenance hashes স্বাভাবিকভাবেই নতুন source hash record করবে; default-এ নতুন keyword metadata field যোগ হয় না। [Evidence: `08_experiments/E1_pilot/harness_v2/test_fuzzer_args.py:212–223,460–486,551–621`; `run_metadata.py:66–69,81–82`; `freeze.json`, `before`/`after`-এর `fuzzer-golden.json` entry।]

| Check | ফল | Evidence |
|---|---|---|
| `bash -n`, সব ৬টি harness_v2 shell file | PASS | `bash_n.txt:1–6` |
| `static_validate.py` | PASS; embedded derecurse 13 ও fuzzer 39 test | `static_validate.txt:41–43,86–89` |
| `test_specmut.py EMB/openapi-swagger` | নতুন 10 unit test + existing 144 property case PASS | `test_specmut.txt:13–15,161` |
| `test_pipeline.py EMB/openapi-swagger` | PASS; প্রতিটি fault-এ unexplained attribution 0 | `test_pipeline.txt:1–7` |
| `test_fuzzer_args.py` | 39/39 PASS | `test_fuzzer_args.txt:42–44` |
| `test_derecurse.py` | 13/13 PASS | `test_derecurse.txt:16–18` |
| অন্যান্য existing tool tests | review fixes 31, triage 61, intent evidence 52, only_ops 6; সব PASS | `test_review_fixes.txt:34–36`; `test_triage.txt:64–66`; `test_intent_evidence.txt:3–5`; `test_only_ops.txt:3–5` |

নতুন regression coverage-এ singleton keyword filtering, exact manifest reconstruction, seed/severity/exclude/only-ops selection invariance, original no-op candidate retention, empty pool/zero retained edits, object-list বনাম parameter flag, Swagger/OAS3 refs/path parameters, explicit-all parity এবং invalid CLI/env/fault combinations আছে। Harness tests real error-only preflight ও extracted pure shell fragments চালায়; complete runtime orchestration চালায় না। [Evidence: `08_experiments/tools/test_specmut.py:205–375`; `08_experiments/E1_pilot/harness_v2/test_fuzzer_args.py:477–621`; `verification.json`, `execution_boundary`।]

## 4. Market offline sanity: seeds 1–3

Input `08_experiments/_external/emb/openapi-swagger/market.json`, REQUEST_STRICT p30। প্রতিটি seed-এ frozen pre-edit mutator-এর full mutation records saved run manifest-এর সঙ্গে হুবহু মিলে গেছে। আলাদাভাবে পুরোনো RNG algorithm দিয়ে sample reconstruct করা হয়েছে; নতুন দুই variant-এর `mutations ∪ selected_no_edit` তার সমান। Expected output তৈরিতে pre-edit mutator-এর raw STRICT edits থেকে শুধু সংশ্লিষ্ট family রেখে প্রয়োগ করা হয়েছে; output document ও structural patch—দুটিই match করেছে। [Evidence: `sanity.py:45–116`; `sanity.json`, `rows[seed=1..3].default_mutations_equal_saved`, প্রতিটি variant-এর তিনটি equality field; saved paths প্রতিটি row-এর `saved_manifest`।]

| Seed | Original sample | Saved mutated ops | required-only mutated / no-edit | maximum,maxLength mutated / no-edit | Retained semantic edits: required / maximum,maxLength |
|---|---:|---:|---:|---:|---|
| 1 | 4 | 3 | 2 / 2 | 3 / 1 | required 3 / maximum 1, maxLength 13 |
| 2 | 4 | 4 | 1 / 3 | 4 / 0 | required 2 / maximum 4, maxLength 11 |
| 3 | 4 | 4 | 1 / 3 | 4 / 0 | required 2 / maximum 0, maxLength 14 |

প্রতিটি সংখ্যার evidence: `sanity.json`, সংশ্লিষ্ট `rows[seed]`-এর `selected_operations`, `saved_mutated_operations`, `variants[].mutated_operations`, `selected_no_edit`, `semantic_edits_by_keyword`; সহজে পড়ার summary: `sanity_summary.txt:1–101`। Semantic edit count ও serialized document patch count এক নয়; দুটো count-ই JSON-এ রাখা হয়েছে।

**Saved manifest-এর সীমা:** seed 1-এর sample-এ `GET /products` আছে, কিন্তু full STRICT edit-ও সেখানে শূন্য। পুরোনো manifest শুধু অন্য তিনটি mutated operation record করেছিল। নতুন দুই variant-এ সেটি `selected_no_edit`-এ আছে। Seed 2/3-এর চার sample-ই পুরোনো manifest-এ mutated ছিল। তাই full sample বনাম saved mutated-list-এর literal equality seed 1-এ **false**; এটি `sanity.json`-এ স্পষ্ট record করা হয়েছে। Original no-op বাদ দিলে তিন seed-এই full-edit-capable selected set saved manifest-এর সমান। ⚠️ “selected operations = saved manifests” যাচাইকে এই historical manifest সীমার মধ্যে পড়তে হবে; তিনটি record-এর সঙ্গে sample মেলানোর জন্য eligibility বদলালে মূল identical-selection requirement ভাঙত। [Evidence: `sanity.json`, `rows[seed=1].legacy_selected_no_edit`, `literal_sample_equals_saved_mutated_list`, এবং ছয় variant-এর `full_edit_capable_selection_equals_saved_mutations`; `specmut.before.py:243–255`।]

## 5. Freeze, সীমা ও handoff

`freeze.json`-এ tools/, harness_v2/ ও requested `E1_pilot/run_batch.sh` entry-এর before/after SHA-256 আছে। Intended আটটি file-ই বদলেছে; বাকি **৪২টি protected entry অপরিবর্তিত**—৪১টি existing file এবং একটি absent path। `08_experiments/E1_pilot/run_batch.sh` আগে/পরেও নেই; আসল batch script `harness_v2/run_batch.sh` বদলানো হয়েছে। `conformance.py`, `attribute.py`, existing golden ও bytecode file-গুলোর before/after digest একই। [Evidence: `freeze.json`, `changed_intended`, `protected_entries`, `protected_present_files`, `unexpected_changes`, `unexpected_new_files`, `all_protected_unchanged`, সংশ্লিষ্ট `before`/`after` entries; `verification.json`, `freeze`।]

Docker, Java, Maven, network, fuzzer বা SUT চালানো হয়নি। Saved runs-এ কোনো output লেখা হয়নি; offline mutation artifacts scratch-এর মধ্যে আছে। Runtime smoke ও actual detection/500-rate outcome Claude-এর বাকি কাজ। ⚠️ Required-only বা length-only runtime-এ কোন response distribution হবে, এই offline result থেকে নির্ধারণ করা যায় না। আর সব selected operation-এর retained edits শূন্য হলে specmut manifest ঠিকই লেখে, তবে harness-এর আগের `operations_mutated > 0` guard সেই run থামাবে; সেই default guard বজায় আছে। [Evidence: `verification.json`, `execution_boundary`; `sanity.json`, প্রতিটি variant-এর `manifest_path`; `08_experiments/E1_pilot/harness_v2/run_pilot.sh:195`; `test_specmut.py:290–305`; task runtime boundary `09_collab/tasks/T37.md`, Constraints।]

Offline sanity ও freeze summary পুনরুৎপাদন:

```bash
/usr/bin/python3 -I -B 09_collab/logs/T37_scratch/sanity.py
/usr/bin/python3 -I -B 09_collab/logs/T37_scratch/verify.py
```

সব check-এর exit code, test count ও log digest `verification.json`-এ আছে; raw auth value print বা output-এ copy করা হয়নি। [Evidence: `verification.json`; `static_validate.txt:24`; `artifact_scan.json`।]
