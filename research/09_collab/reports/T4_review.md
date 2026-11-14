# T4 — R1 tools-এর স্বাধীন code review

তারিখ: 2026-11-13 · Reviewer: Codex · Scope: `09_collab/tasks/T4.md:1`-এ নির্ধারিত সাতটি Python file এবং P001 ফলাফল।

⚠️ **মূল মূল্যায়ন:** সংরক্ষিত P001 সংখ্যা পুনরুৎপাদনযোগ্য, কিন্তু বর্তমান checker/attribution থেকে নির্ভরযোগ্য causal ground truth বা সম্পূর্ণ OpenAPI conformance দাবি করা যায় না। নিচের R01–R15-এর ত্রুটিগুলো সংশ্লিষ্ট input-এ ফলের অর্থ বদলে দেয়; সেগুলো ঠিক করে validation পুনরায় করা উচিত। প্রমাণ: R01–R15-এর reproduction এবং `08_experiments/E1_pilot/P001_empirical_findings.md:85`।

এই review-তে production file সম্পাদনা করা হয়নি। Reproduction, test output এবং replay output কেবল `09_collab/logs/T4_scratch/`-এ লেখা হয়েছে; external SUT/tool build, package install বা external project code execution করা হয়নি। Logger-এর জন্য প্রকৃত mitmproxy-এর বদলে একটি local mock ব্যবহৃত হয়েছে (`09_collab/logs/T4_scratch/reproduce.py:311`)।

## পরীক্ষা ও evidence পড়ার নিয়ম

- **E[id]** = `09_collab/logs/T4_scratch/reproductions.jsonl`-এর `id` field; executable fixture: `09_collab/logs/T4_scratch/reproduce.py`। প্রতিটি record-এ concrete input, expected, actual আছে।
- **A[id]** = `09_collab/logs/T4_scratch/p001_audit.jsonl`-এর `id` field; audit script: `09_collab/logs/T4_scratch/audit_p001.py`। একই id-র একাধিক record হলে `testCaseId` দিয়ে নির্বাচন করতে হবে।
- Severity: **P1** = সংশ্লিষ্ট experiment/ground-truth inference-এর আগে সংশোধন দরকার; **P2** = coverage, robustness বা fidelity-এর সীমা, support দাবি করার আগে সংশোধন দরকার। এটি reviewer-এর অগ্রাধিকার, মাপা empirical frequency নয়।
- Reproduction-এর assertions **বর্তমান ভুল আচরণ ঘটেছে** তা যাচাই করে; এগুলো production correctness-এর pass নয় (`09_collab/logs/T4_scratch/reproduce.py:1`)।

| পরীক্ষা | ফল | Evidence |
|---|---|---|
| Synthetic defect observations | 48টি assertion পাস; 8টি positive-control group পাস | E-এর শেষ `summary` record |
| বিদ্যমান `test_specmut` | 144 passed, 0 failed | `09_collab/logs/T4_scratch/test_specmut.txt:146` |
| বিদ্যমান `test_pipeline` | PASS; unexplained = 0 | `09_collab/logs/T4_scratch/test_pipeline.txt:2` |
| একই pipeline আবার চালানো | প্রথম output-এর সঙ্গে byte-identical | A[A12_verification] |
| P001 script rerun | চারটি ফলাফল file-ই সংরক্ষিত file-এর সঙ্গে byte-identical | A[A08_artifact_equality] |
| বর্তমান P001 coverage/join | 147 fault row; missing spec = 0; উভয় table-এ duplicate `testCaseId` = 0; joined row = 147 | A[A01_coverage], A[A07_join] |

P001-এর headline অপরিবর্তিত: F_OAS 62/73 default, 71/73 strict; F_400 15/16; 5xx 6/6; F_2XXP 30/44; F_2XXD 0/8। Evidence: `09_collab/logs/T4_scratch/p001_rerun/summary.json`, `replay_reproduced_by_oracle` rows; A[A08_artifact_equality]।

নতুন pipeline run-এ `REQUEST_STRICT NEW=2012`, `METHOD_SEM VANISHED=472`; আগের artifact-এ যথাক্রমে 1359 ও 474। দুটোই PASS হলেও সংখ্যা মেলেনি (`09_collab/logs/T4_scratch/test_pipeline.txt:4`, `08_experiments/E1_pilot/pipeline_replay_test.txt:4`)। ⚠️ আগের run-এর input/dependency/source hashes না থাকায় পার্থক্যের কারণ নির্ধারণ করা যায়নি; একই বর্তমান পরিবেশে দুবার output মেলায় এটিকে mutation nondeterminism-এর প্রমাণ বলা হচ্ছে না। বর্তমান Python/dependency versions এবং source/data SHA-256: A[A11_provenance]।

## Confirmed (reproduced) — severity অনুযায়ী

### R01 · P1 — P001-এর broad oracle hit-কে নির্দিষ্ট failure reproduction বলা হচ্ছে

- **স্থান:** `08_experiments/E1_pilot/p001_oas_analysis.py:55`, `:137`, `:142`, `:150`; দাবি: `08_experiments/E1_pilot/P001_empirical_findings.md:85`, `:89`।
- **Concrete input:** LanguageTool `test_qhsvno15ea0l_check`-এর source types `ADDITIONAL_PROPERTIES;MISSING_REQUIRED`; default checker কেবল missing `sentence` পায়। তবুও `RESPONSE_SCHEMA` থাকলেই `reproduced_default=True` হয়।
- **Expected বনাম actual:** source-এর নির্দিষ্ট constraint/message-এ agreement আলাদা মাপা দরকার। Actual: ADDITIONAL_PROPERTIES group-এর 27টির মধ্যে 18টি broad hit; ওই 18টির কোনোটিতেই emitted default violation-এর pointer `/additionalProperties` দিয়ে শেষ হয় না। Direct additional-property error record default **0/27**, strict **27/27**। এটি emitted keyword-এর audit; composition error-এর সব nested cause-এর পূর্ণ equivalence metric নয়। Evidence: A[A04_additional_not_reproduced], LanguageTool row; A[A05_message_audit_counts]; E[C19_broad_agreement]।
- **প্রভাব:** 62/73 এবং 71/73 বৈধ **category-level re-detection count**, constraint-level agreement বা accuracy নয়। 18/27-কে additional-property failure reproduction বলা ভুল। 9টি strict-only broad hit মানে পুরো 27টির মধ্যে মাত্র 9টিতে strict policy প্রাসঙ্গিক—এ সিদ্ধান্তও সমর্থিত নয়।
- **Suggested fix:** oracle category, validator keyword, instance location এবং source message-এর matched cause আলাদা column করুন। Positive representative fault ছাড়াও conforming negative controls দিন; false-positive rate মাপুন। 5XXI ও 5XXV-র জন্য শুধু `SERVER_ERROR` পাওয়া request validity পুনরুৎপাদন করে না (`p001_oas_analysis.py:57`)।

### R02 · P1 — fingerprint collision নতুন missing-property failure-কে PERSISTENT বানায়

- **স্থান:** `08_experiments/tools/conformance.py:229`, `:257`; `08_experiments/tools/attribute.py:29`, `:47`।
- **Input:** response schema-তে properties `a,b`, baseline `required:[a]`, body `{}`; `RESPONSE_ORACLE` mutation-এর পরে `required:[a,b]`। একই exchange দুবার check।
- **Expected:** আগের missing `a` PERSISTENT, নতুন missing `b` NEW। **Actual:** baseline-এ 1টি error, mutated-এ 2টি; দুটোরই pointer `/required` এবং একই fingerprint। Dict conversion-এর পরে একটিমাত্র PERSISTENT row থাকে; missing `b` হারায়। Evidence: E[C14_required_fingerprint]।
- **Suggested fix:** stable error identity-তে keyword-এর সঙ্গে missing/extra property name এবং প্রয়োজনমতো normalized instance location রাখুন; occurrence/count আলাদা রাখুন। শুধু পুরো error message hash করলে library version বা concrete value বদলে অস্থিতিশীলতা আসতে পারে—এটি design tradeoff।

### R03 · P1 — mutated operation-এ যেকোনো NEW error-কে injected SPEC defect ধরা হয়

- **স্থান:** `08_experiments/tools/attribute.py:3`, `:12`, `:33`, `:42`।
- **Input:** REQUEST_STRICT manifest; baseline `GET /x?q=0 -> 200`, mutated run-এ একই operation `->500`। Mutation শুধু request constraint/required flag বদলায়।
- **Expected:** নতুন SERVER_ERROR-এর কারণ অতিরিক্ত evidence ছাড়া অজানা। **Actual:** NEW SERVER_ERROR এবং UNDOCUMENTED_STATUS দুটোই manifest-এর `SPEC/S-REQ-STRICT` পায়। Evidence: E[C15_causal_overclaim]।
- **প্রভাব:** একই SUT build যথেষ্ট causal control নয়; generator-এর traffic, state বা nondeterminism বদলাতে পারে। Docstring-এ traffic confounding স্বীকার করা হলেও output label-এ অনিশ্চয়তা নেই (`attribute.py:12`)।
- **Suggested fix:** observational delta ও causal label পৃথক করুন; exchange pairing/replay mode, changed constraint-এর সঙ্গে error dependency এবং coverage evidence ছাড়া NEW-কে `NEEDS_MANUAL` রাখুন। VANISHED-ও missed coverage থেকে হতে পারে; mutation-related disappearance প্রমাণ হলে তবেই MASKED।

### R04 · P1 — response body `null` সম্পূর্ণ schema validation এড়ায়

- **স্থান:** `08_experiments/tools/conformance.py:250`, `:254`, `:256`।
- **Input:** OAS3 response schema `{type:object}`, status 200, `Content-Type: application/json`, body `null`।
- **Expected:** RESPONSE_SCHEMA type violation। **Actual:** `json.loads` থেকে `None`; parse failure-এর sentinel-ও `None`, ফলে কোনো violation নেই। Evidence: E[C01_response_null]।
- **Suggested fix:** parse success আলাদা boolean/sentinel-এ রাখুন এবং সফল parse-এর সব JSON value validate করুন। Nullable schema-র বৈধ null-ও একই পথ দিয়ে validator-এ যেতে হবে।

### R05 · P1 — missing/malformed/null request body-কে conforming ধরা হয়

- **স্থান:** `08_experiments/tools/conformance.py:197`, `:203`, `:209`, `:262`।
- **Input:** `requestBody.required:true`, JSON object schema; body যথাক্রমে absent, `{`, এবং `null`; response 200। আরও একটি case: truncated body `{"a":`, response 400।
- **Expected:** প্রথম তিনটিতে INVALID_ACCEPTED; truncated evidence-এ পূর্ণ validity verdict অনির্ধারিত। **Actual:** প্রথম তিনটিতে violation নেই; শেষটিতে VALID_REJECTED আসে। Request-body truncation flag পরীক্ষা করা হয় না। Evidence: E[C01_request_missing], E[C01_request_malformed], E[C01_request_null], E[C01_truncated_request]।
- **Suggested fix:** required-body presence, parser error, JSON null এবং incomplete capture পৃথক করুন; `valid / invalid / uncheckable` ফল দিন। Request media type নির্বাচনও R09-এর মতো করুন।

### R06 · P1 — OpenAPI 3.1-এ Draft4 চালানো এবং `$ref` siblings হারানো

- **স্থান:** `08_experiments/tools/specmut.py:40`, `:53`; `08_experiments/tools/conformance.py:43`, `:61`।
- **Input:** 3.1 schemas `{type:number,exclusiveMinimum:5}`-এ body `3`; `{const:5}`-এ `3`; schema `false`-এ `{}`; `$ref:N` plus sibling `maximum:5`, N=`{type:number}`, body `8`।
- **Expected:** প্রতিটিতে RESPONSE_SCHEMA। **Actual:** সব case-এ কোনো violation নেই। Draft4 numeric-exclusive bound/const বোঝে না, false schema truthiness guard-এ বাদ পড়ে, আর resolver sibling মুছে দেয়। Evidence: E[C02_exclusive], E[C02_const], E[C02_false], E[C04_ref_sibling]।
- **Suggested fix:** OAS2/OAS3.0/OAS3.1 ও declared dialect আলাদা dispatch করুন; 3.1-এ যথাযথ 2020-12 support এবং boolean schema handling দিন; schema `$ref`-এর sibling বজায় রাখুন। Normative ভিত্তি: [OAS3.1 Schema Object](https://spec.openapis.org/oas/v3.1.0.html#schema-object)।

### R07 · P1 — schema normalization সাধারণ property name মুছে দেয়

- **স্থান:** `08_experiments/tools/conformance.py:59`, `:61`, `:65`, `:74`।
- **Input:** `{type:object,properties:{readOnly:{type:integer},nullable:{type:integer}}}`। এগুলো data property-এর নাম।
- **Expected:** property schema দুটি অক্ষত থাকবে। **Actual:** normalization-এর পরে `properties:{}`; recursive `fix` properties map-কেও Schema Object মনে করে keys pop করে। Evidence: E[C03_property_names]।
- **Suggested fix:** schema-aware traversal করুন; `properties`/`$defs`-এর values এবং composition children visit করুন, arbitrary map/enum/example data-র keys-এ keyword transformation চালাবেন না।

### R08 · P1 — readOnly/writeOnly বাদ দেওয়ায় required-এর direction হারায়

- **স্থান:** `08_experiments/tools/conformance.py:65`, `:210`, `:257`।
- **Input:** object `required:[id]`; `id` readOnly integer; request body `{}`। বিপরীত case-এ `id` writeOnly integer; response `{}`।
- **Expected:** request-এ readOnly required এবং response-এ writeOnly required প্রযোজ্য নয়। **Actual:** যথাক্রমে INVALID_ACCEPTED এবং RESPONSE_SCHEMA। Evidence: E[C03_readonly_required], E[C03_writeonly_required]।
- **Suggested fix:** request/response direction অনুযায়ী required projection তৈরি করুন; annotation মুছে দিয়ে একই schema দুদিকে validate করবেন না। Normative ভিত্তি: [OAS3.0 Schema Object](https://spec.openapis.org/oas/v3.0.3.html#schema-object)।

### R09 · P1 — content negotiation-এ সবসময় application/json/প্রথম schema নেওয়া হয়

- **স্থান:** `08_experiments/tools/conformance.py:123`, `:128`, `:198`, `:250`।
- **Input:** একটি response-এ JSON object ও `text/plain` string documented; actual body `hello`, media `text/plain`। অন্য case-এ JSON string ও `application/problem+json` object documented; actual problem+json body `{}`।
- **Expected:** actual media-র schema দিয়ে দুটোই conforming। **Actual:** যথাক্রমে RESPONSE_PARSE এবং RESPONSE_SCHEMA; media allowed হলেও ভুল schema ব্যবহৃত। Evidence: E[C05_plain_response], E[C05_json_variant]।
- **Suggested fix:** actual Content-Type অনুযায়ী exact/wildcard specificity-তে schema নির্বাচন করুন; media অনুযায়ী parse করুন। Request path-এও একই rule এবং unsupported encoding-এর explicit uncheckable verdict দরকার।

### R10 · P1 — servers variables/scopes/alternatives ভুলভাবে route হয়

- **স্থান:** `08_experiments/tools/conformance.py:88`, `:90`, `:95`, `:104`।
- **Input:** server `https://example.test/{version}` default `v1`, route `/x/{id}`, request `/v1/x/7`; root `/api` কিন্তু operation server `/custom`; অথবা second server `/v2`।
- **Expected:** variable expansion, operation override এবং second documented server অনুযায়ী route match। **Actual:** variable base-কে path wildcard বানানো হলেও `len(self.base)` দিয়ে parameter extraction ভুল হয়; অন্য দুই case UNDOCUMENTED_OPERATION। Evidence: E[C06_server_variable], E[C06_operation_server], E[C06_second_server]।
- **Suggested fix:** expanded server candidates ও per-operation effective server ব্যবহার করুন; regex captures থেকেই path parameters নিন। Log-এ origin/server নির্বাচনও রাখতে হবে। Normative ভিত্তি: [OAS3.0 Server Object](https://spec.openapis.org/oas/v3.0.3.html#server-object)।

### R11 · P1 — path-level parameter `$ref` resolve-এর আগে dedup হওয়ায় mutation বাদ যায়

- **স্থান:** `08_experiments/tools/specmut.py:75`, `:77`, `:80`।
- **Input:** operation parameter `$ref:Q`, path-level parameter `$ref:R`; Q ও R আলাদা query integer। REQUEST_STRICT 100%।
- **Expected:** inherited R-ও operation-local copy-তে আসবে এবং tightening পাবে। **Actual:** unresolved ref দুটোর key `(None,None)` হওয়ায় R copy হয় না; শুধু Q বদলায়। R path-level declaration-এ থাকে, কিন্তু mutation পায় না। Evidence: E[C09_path_ref_dedup]।
- **Suggested fix:** identity বের করার আগে parameter reference resolve করুন; operation-level override precedence বজায় রাখুন। Conformance-এর `operation()`-এ ইতিমধ্যে আগে resolve হয় (`conformance.py:115`); bugটি mutator-এর আলাদা implementation-এ।

### R12 · P1 — REQUEST_STRICT কখনো constraint শিথিল করে, কখনো no-op-ও mutation গোনে

- **স্থান:** `08_experiments/tools/specmut.py:139`, `:144`, `:199`।
- **Input:** required query string `maxLength:0`; strict mutation। অন্য input: required integer `maximum:-2`।
- **Expected:** STRICT-এ accepted set বাড়বে না; unchanged edit mutated operation হিসেবে গণনা হবে না। **Actual:** `maxLength` 1 হয়, আগে অবৈধ `a` বৈধ হয়। Numeric case-এ `before=-2,after=-2` edit রেকর্ড হয়; spec অপরিবর্তিত হলেও `operations_mutated` বাড়ে। Evidence: E[C10_strict_widens], E[C10_noop_manifest]।
- **Suggested fix:** existing bound-এর সঙ্গে monotonic tightening করুন, before==after বাদ দিন এবং satisfiability/semantic-direction যাচাই করুন। `required=sorted(properties)`-ও existing required নাম অক্ষত রেখে union করা উচিত (`specmut.py:147`)।

### R13 · P1 — manifest পুরো mutation ব্যাখ্যা করে না; JSON Pointer escaping-ও ভাঙা

- **স্থান:** `08_experiments/tools/specmut.py:76`, `:80`, `:87`, `:109`, `:195`; `08_experiments/tools/test_specmut.py:47`।
- **Input A:** parameter কেবল `$ref:Q`; Q-এর `minimum`/required মুছুন। **Expected:** structural inlining/copy edit এবং সত্য before location থাকবে। **Actual:** manifest সরাসরি `/parameters/0/schema/minimum`-এর before দাবি করে, অথচ মূল document-এ ওই pointer নেই; ref replacement-এর edit নেই। Evidence: E[C13_unlogged_structure]।
- **Input B:** property names `a/b`, `t~n`-এর maxLength মুছুন। **Expected:** pointer segments `a~1b`, `t~0n`। **Actual:** raw নাম ব্যবহৃত হয়; pointer অন্য/অনুপস্থিত node নির্দেশ করে। `test_specmut.check` এমন deletion-কেও PASS দেয়, কারণ যেকোনো missing pointer + after=None গ্রহণ করে। Evidence: E[C12_pointer_escaping], E[C21_bad_pointer_test_pass]।
- **Suggested fix:** normalization আর mutation-এর আলাদা auditable patch দিন, অথবা normalization-এর পরের base hash/pointer context সংরক্ষণ করুন। Explicit add/remove/replace/move, before-exists, before-value এবং সম্পূর্ণ diff coverage পরীক্ষা করুন। Pointer encoding-এর ভিত্তি: [RFC6901 §3](https://www.rfc-editor.org/rfc/rfc6901.html#section-3)।

### R14 · P1 — array explode এবং nullable numeric coercion থেকে false INVALID_ACCEPTED

- **স্থান:** `08_experiments/tools/conformance.py:142`, `:150`, `:188`, `:194`।
- **Input A:** OAS3 query array, `style:form,explode:true,maxItems:1`, items string; decoded query list `q:["a,b"]`। **Expected:** একটি string item; valid। **Actual:** comma দিয়ে দুই item বানায়; INVALID_ACCEPTED। `explode` পড়াই হয় না। Evidence: E[C08_single_exploded_value], E[C08_comma_enum]।
- **Input B:** query schema `{type:integer,nullable:true}`, `q=7`। **Expected:** integer 7 valid। **Actual:** normalized type list হওয়ায় coercer string `7` রেখে দেয়; INVALID_ACCEPTED। Evidence: E[C22_nullable_parameter]।
- **Suggested fix:** dialect/location/style/explode/collectionFormat অনুযায়ী deserialization করুন; union/nullable schema-র non-null type অনুযায়ী primitive coercion করুন।

### R15 · P1 — P001 reconstruction encoded slash decode করে বাস্তব replay miss তৈরি করে

- **স্থান:** `08_experiments/E1_pilot/p001_oas_analysis.py:68`, `:74`, `:80`; ব্যাখ্যা: `08_experiments/E1_pilot/P001_empirical_findings.md:103`।
- **Concrete input:** Marvel `test_1ib99qn5h0sog_getCharacterStoryCollection`; `characterId=-b%7D%3C2%2FH%3F%5D**%29DsuC;`।
- **Expected:** path substitution-এ parameter-এর encoded slash route separator হয়ে যাবে না। **Actual:** `%2F` → `/`, `%3F` → `?`; reconstructed path আর template মেলে না, UNDOCUMENTED_OPERATION। একই row-তে encoded representation বজায় রাখলে strict checker UNDOCUMENTED_STATUS পায়, অর্থাৎ F_OAS broad hit ফিরে আসে। Evidence: A[A03_unmatched_path], A[A03_preserved_encoding]; E[C18_path_unescape]।
- **আরও fidelity সমস্যা:** `kv('q=a;q=b;token=A+B')`-এ duplicate q হারিয়ে শুধু b থাকে এবং plus space হয়। Duplicate loss reproduced; বর্তমান 147 row-তে duplicate key নেই, তাই বর্তমান headline-এ এর প্রভাব দাবি করা হচ্ছে না। Evidence: E[C18_kv_loss], A[A06_serialization_risks]।
- **Suggested fix:** raw transport representation ও decoded semantic value পৃথক রাখুন; source encoding যাচাই করে substitution/re-encoding এবং multimap ব্যবহার করুন। CSV reconstruction-কে captured HTTP replay হিসেবে বর্ণনা করবেন না।

### R16 · P2 — `$ref` depth cap নিঃশব্দে constraints মুছে দেয়

- **স্থান:** `08_experiments/tools/specmut.py:48`, `:50`; `08_experiments/tools/conformance.py:117`।
- **Input:** recursive Node `{value:integer,next:$ref Node}`; 12টি next-এর পরে value=`"BAD"`।
- **Expected:** leaf type error, অথবা explicit validation-depth limitation। **Actual:** depth cap-এর পরে `{}` হয়ে leaf constraint হারায়; কোনো response violation নেই। Mutator-এ inlining হলে একই কাটাছেঁড়া manifest-বহির্ভূত semantic change-ও হতে পারে। Evidence: E[C04_recursive_ref]; structural issue-এর জন্য R13।
- **Suggested fix:** validator-এর reference registry ব্যবহার করুন; cycle-aware graph রাখুন। Safety bound লাগলে uncheckable reason দিন; unconstrained `{}` দিয়ে silently success নয়।

### R17 · P2 — mixed literal/template segment এবং percent-encoded path value ভুল extract হয়

- **স্থান:** `08_experiments/tools/conformance.py:95`, `:104`, `:106`।
- **Input:** `/files/{id}.json`, request `/files/7.json`, id integer। অন্য case `/x/{id}`-এ `/x/%31`।
- **Expected:** parameter id যথাক্রমে `7`, `1`। **Actual:** প্রথমটিতে key `id}.jso`, value `7.json`; দ্বিতীয়টিতে raw `%31` validate হয়ে INVALID_ACCEPTED। Evidence: E[C07_mixed_segment], E[C07_encoded_path]।
- **Suggested fix:** named regex capture দিয়ে template variable ধরুন; path segment boundary match করার পরে একবার decode করুন। Encoded slash-এর route matching এবং decoded parameter validation পৃথক রাখুন।

### R18 · P2 — required parameter schema ফাঁকা হলে এবং cookie-তে থাকলে বাদ পড়ে

- **স্থান:** `08_experiments/tools/conformance.py:170`, `:171`, `:182`।
- **Input:** missing required query q with `schema:{}`; missing required cookie session with string schema; response 200।
- **Expected:** দুটোতেই INVALID_ACCEPTED। **Actual:** কোনো problem নেই—প্রথমটি falsy-schema guard-এ, দ্বিতীয়টি unsupported location branch-এ বাদ। Evidence: E[C08_empty_schema_required], E[C08_required_cookie]।
- **Suggested fix:** presence/required validation schema-এর truthiness থেকে আলাদা করুন; cookie support দিন। Unsupported parameter/form/content encoding থাকলে complete request validity দাবি না করে explicit scope দিন।

### R19 · P2 — composition branch-এ request mutation পৌঁছায় না

- **স্থান:** `08_experiments/tools/specmut.py:104`, `:109`, `:111`।
- **Input:** optional query schema `allOf:[{type:integer,minimum:2}]`; অন্য case একই oneOf wrapper; REQUEST_LOOSE 100%।
- **Expected:** nested minimum mutation candidate হবে। **Actual:** শুধু properties/items traverse হওয়ায় spec অপরিবর্তিত, manifest empty। Evidence: E[C11_unvisited_allOf], E[C11_unvisited_oneOf]।
- **Suggested fix:** composition-aware traversal এবং pointer দিন। ⚠️ oneOf branch ঢিলে করলেই whole schema ঢিলে হবে এমন নয়; একাধিক branch match হয়ে exclusive choice ব্যর্থ হতে পারে। তাই branch mutation-এর semantic direction আলাদাভাবে যাচাই করতে হবে। Ordinary allOf/oneOf validation-এর positive controls পাস করেছে; সব composition validation ভাঙা বলা হচ্ছে না (E-এর positive controls)।

### R20 · P2 — date/date-time format checker RFC3339-এর চেয়ে বেশি permissive

- **স্থান:** `08_experiments/tools/conformance.py:33`, `:38`।
- **Input:** date=`20260101`; date-time=`2026-01-01`; অথবা date-time=`2026-01-01T12:00:00`।
- **Expected:** ঘোষিত format-এ error। **Actual:** Python `fromisoformat` সবগুলো গ্রহণ করে; error list empty। Evidence: E[C16_20260101], E[C16_2026-01-01], E[C16_2026-01-01T12:00:00]।
- **Suggested fix:** RFC3339-aware format validation দিন; full-date এবং offset-সহ full-time grammar পরীক্ষা করুন। ভিত্তি: [RFC3339 §5.6](https://www.rfc-editor.org/rfc/rfc3339.html#section-5.6)।

### R21 · P2 — test harness pass শক্ত correctness evidence নয়; valid input-এ crash/zero coverage আছে

- **স্থান:** `08_experiments/tools/test_pipeline.py:29`, `:80`, `:83`, `:107`, `:115`; `08_experiments/tools/test_specmut.py:42`, `:52`, `:59`।
- **Inputs/actual:** `responses:{2XX:{description:ok}}`-এ `int('2XX')` ValueError; শুধু default response-এ zero exchanges; allOf-তে required a এবং required b থাকলে generator শুধু a তৈরি করে; empty spec directory-তে উভয় test entry point exit 0/PASS। Evidence: E[C17_range_test_crash], E[C17_default_not_tested], E[C17_invalid_generated_instance], E[C25_empty_corpus_passes]।
- **Expected:** supported response entry থেকে representative status; generated instance-এর validity যাচাই; nonzero corpus/coverage requirement।
- **Suggested fix:** range/default case ও expected error/fingerprint assertions যোগ করুন; generated instance validate না হলে unsupported/skip reason গুনুন; zero input fail করুন। Existing locality test একই ভুল দুই checker-এ থাকলে ধরবে না। `test_specmut` before/full diff বা mutated document determinism পরীক্ষা করে না; শুধু recorded after এবং manifest equality দেখে। R13-এ invalid deletion pointer-ও pass করেছে।

### R22 · P2 — logger-এর binary body lossless নয়

- **স্থান:** `08_experiments/tools/mitm_fulllog.py:22`, `:24`।
- **Input:** mock message bytes hex `ff00`।
- **Expected:** binary response replay-এর জন্য original bytes বা explicit unsupported encoding। **Actual:** UTF-8 replacement text লেখা হয়; text re-encode করে original bytes ফেরত পাওয়া যায় না। Evidence: E[C20_binary_log]।
- **Suggested fix:** raw bytes-এর base64/encoding রাখুন এবং text decoding আলাদা view করুন। এটি live mitmproxy integration test নয়; addon-এর নিজস্ব conversion function-এর confirmed fidelity limitation।

### R23 · P2 — operation denominator-এ TRACE নেই; zero severity-তেও mutation হয়

- **স্থান:** `08_experiments/tools/specmut.py:22`, `:67`, `:189`; `08_experiments/tools/test_pipeline.py:69`।
- **Input:** একটি valid OAS3 TRACE operation; আলাদা case-এ এক GET operation, METHOD_SEM severity=0।
- **Expected:** total operations=1; zero percent-এ zero mutation অথবা documented rejection। **Actual:** TRACE total=0; severity=0-তেও একটি method swap। Evidence: E[C23_trace_not_enumerated], E[C24_zero_severity]।
- **Suggested fix:** version অনুযায়ী supported HTTP methods নির্ধারণ করুন; severity range validate করুন, zero-এর আচরণ নির্ধারণ করুন; candidate/selected/effectively-mutated counts পৃথক রাখুন। OAS3 Path Item-এ TRACE আছে: [Path Item Object](https://spec.openapis.org/oas/v3.0.3.html#path-item-object)।

### R24 · P2 — P001 developer join global id uniqueness-এর ওপর নির্ভরশীল

- **স্থান:** `08_experiments/E1_pilot/p001_oas_analysis.py:114`, `:118`।
- **Input:** API A ও B-তে একই `testCaseId=shared`, উভয় table-এ একটি করে matching row।
- **Expected:** API+testCaseId দিয়ে 2টি match। **Actual:** শুধু testCaseId merge করে 4টি row; confirmation count-ও double হয়। Evidence: A[A09_cross_api_join_fixture]।
- **Suggested fix:** canonical API id-সহ composite join এবং pandas `validate`/uniqueness assertions দিন। **বর্তমান data-য় এই inflation ঘটেনি**: দুই table-এর ids unique, join 147→147; A[A01_coverage], A[A07_join]।

## Suspected / এখনো পূর্ণ reproduction হয়নি

### S01 · P1 — Amadeus pattern mismatch থেকে “Implementation সঠিক” সিদ্ধান্ত অতিরিক্ত শক্ত

**স্থান:** `08_experiments/E1_pilot/P001_empirical_findings.md:57`, `:64`, `:67`, `:125`। **Input:** double-escaped numeric-looking regex এবং price string `399.00`। **Expected evidence:** authoritative intended price format এবং spec transformation provenance। **Actual report:** regex mismatch-এর পরে implementation correct ও SPEC attribution বলেছে, যদিও একই report-এ transformation origin অজানা এবং internal code evidence অনুপস্থিত বলা আছে। ⚠️ pattern-এর apparent intent SPEC hypothesis-কে সমর্থন করে; একে implementation correctness-এর স্বাধীন প্রমাণ বলা যায় না। **Suggested fix:** intended behavior-এর E-DOC/provenance না পাওয়া পর্যন্ত hypothesis/uncertainty স্পষ্ট করুন। এই review নতুন root-cause adjudication বা developer-label correctness দাবি করছে না।

### S02 · P2 — missing spec silent skip ভবিষ্যৎ replay denominator কমিয়ে দিতে পারে

**স্থান:** `08_experiments/E1_pilot/p001_oas_analysis.py:128`, `:147`। **Failing-input candidate:** corpus-এ একটি fault API যার matching spec নেই। **Expected:** explicit skipped/error row ও original denominator। **Source থেকে actual-এর অনুমান:** `continue`-এর কারণে replay table ও denominator থেকে row বাদ পড়বে; A[A10_missing_spec_fixture] source-derived prediction, end-to-end missing-spec run নয়। **Suggested fix:** coverage ledger ও missing count সংরক্ষণ, skip থাকলে incomplete verdict। বর্তমান corpus-এ missing spec নেই, ফলে বর্তমান 147 denominator-এর বিরুদ্ধে অভিযোগ নয়; A[A01_coverage]।

### S03 · P2 — logger transport failure capture করে না বলে coverage bias হতে পারে

**স্থান:** `08_experiments/tools/mitm_fulllog.py:32`। **Failing-input candidate:** upstream reset/timeout, যেখানে HTTP response event নেই। **Expected:** request, transport error এবং correlation id record। **Source থেকে অনুমান:** কেবল `response` hook আছে; dedicated error hook নেই। প্রকৃত mitmproxy চালানো হয়নি, তাই runtime behavior/integration impact unconfirmed। **Suggested fix:** permitted integration phase-এ error hook ও failed-flow fixture পরীক্ষা করুন; missing exchange-কে VANISHED mismatch ভাবা বন্ধ করতে run coverage ledger রাখুন (`attribute.py:45`)।

## যা যাচাই হয়েছে এবং সীমাবদ্ধতা

Concrete path `/pets/mine` templated counterpart-এর আগে match করে; ordinary Swagger2 `basePath` কাজ করে; exact response→`2XX`→`default` precedence কাজ করে; ordinary OAS3.0 nullable value validator-এ গ্রহণযোগ্য; conformance-এ operation parameter path-level parameter override করে; same-input/same-seed mutation result মেলে; METHOD_SEM-এর নতুন method attribution alias আছে। Ordinary allOf/oneOf validation-ও control-এ কাজ করে। Evidence: `09_collab/logs/T4_scratch/reproduce.py`, শেষ positive-control block। Ambiguous templates-এর tooling choice-কে confirmed precedence bug হিসেবে ধরা হয়নি; normative background: [OAS3.0 Path Matching](https://spec.openapis.org/oas/v3.0.3.html#path-templating-matching)।

P001 sample-এ কেবল fault representative আছে; true-negative population নেই (`08_experiments/E1_pilot/P001_empirical_findings.md:6`, `:123`)। ⚠️ তাই broad re-detection rate থেকে specificity, false-positive rate বা অন্য SUT-এ instrument reliability নির্ণয় করা যায় না। Strict mode নিজেই default-এর বাইরে policy প্রয়োগ করে (`08_experiments/tools/conformance.py:54`); strict-এ hit বাড়া independent correctness evidence নয়।

External data-কে data হিসেবে পড়া হয়েছে; external tools/SUT execute করা হয়নি। Logger পরীক্ষা mock-ভিত্তিক; real request serialization, auth/state effects, TLS/network errors, external `$ref` retrieval এবং সম্পূর্ণ OpenAPI compliance এই review-তে certify করা হয়নি। বর্তমান source ও data পুনরায় চিহ্নিত করতে A[A11_provenance]-এর hashes ব্যবহার করা যাবে।

## খোলা প্রশ্ন ও integration-এর জন্য প্রস্তাব

1. **Fingerprint-এর unit কী হবে—constraint fault, instance failure, নাকি occurrence?** R02-এর collision মেটাতে property identity ও instance normalization policy লিখতে হবে (`conformance.py:232`, `attribute.py:29`)।
2. **Ground truth কখন causal?** Identical exchange replay বনাম fresh generated traffic আলাদা mode ও label confidence চাই; R03-এর automatic expected-label assignment সীমিত করতে হবে (`attribute.py:12`, `:44`)।
3. **প্রথম pilot-এর supported subset কোনটি?** R04–R20 অনুযায়ী request/response encoding, dialect, refs এবং uncheckable verdict নির্ধারণ করতে হবে; silently unsupported feature গ্রহণ করলে VALID_REJECTED-এর অর্থ বদলে যায় (`conformance.py:262`)।
4. **P001 result-এর নাম/ব্যাখ্যা কী হবে?** Category-level re-detection headline রাখা যায়; R01 অনুযায়ী additional-property সংখ্যা ও reliability দাবি সংশোধন, R15 অনুযায়ী reconstruction audit এবং negative-control validation দরকার (`p001_oas_analysis.py:142`, `P001_empirical_findings.md:85`)।
5. **আগের pipeline সংখ্যা কোন inputs/environment-এর?** বর্তমান repeatable run ও পুরোনো artifact-এর delta ব্যাখ্যার জন্য আগের provenance দরকার; বর্তমান snapshot A[A11_provenance], তুলনা `pipeline_replay_test.txt:4` বনাম `09_collab/logs/T4_scratch/test_pipeline.txt:4`।

পুনরায় চালানোর command (workspace root থেকে; সব output T4 scratch-এ):

```sh
/usr/bin/python3 -I -B 09_collab/logs/T4_scratch/reproduce.py > 09_collab/logs/T4_scratch/reproductions.jsonl
/usr/bin/python3 -I -B 08_experiments/E1_pilot/p001_oas_analysis.py 08_experiments/_external/p001 09_collab/logs/T4_scratch/p001_rerun > 09_collab/logs/T4_scratch/p001_rerun_stdout.json
/usr/bin/python3 -I -B 09_collab/logs/T4_scratch/audit_p001.py > 09_collab/logs/T4_scratch/p001_audit.jsonl
```
