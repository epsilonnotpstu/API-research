# T35 — Market REQUEST_STRICT-এর 500: `_links` deserialization-এ আটকে যাওয়া

**ফল:** EvoMaster s1/s3-এর 392/361টি eligible violating request সবই `PUT /customer/contacts`; প্রতিটির body-তে `_links` **array**, এবং প্রতিটি 500 response-এ `Expected relation name` ও `ContactsDTO["_links"]` reference chain আছে। Saved stack trace-এ Spring HATEOAS HAL deserializer-এর `JsonParseException`; market-এর generic exception handler সেটিকে **500** করে। ⚠️ Code ও traffic মিলিয়ে failure-এর কারণ হলো co-occurring `_links` representation; breaching `phone/address.maxLength` value এই exception-এর কারণ নয়। [Evidence: নিচের `E1:6`, `E3:6`; `F:1–2`; `E1/compose.log:321–324`, `E3/compose.log:170–173`; `R/rest/exception/RestExceptionHandler.java:37–42`।]

STRICT edit-এর গুরুত্বপূর্ণ interaction: আগে optional `_links` এখন **required**। Fresh eligible body-গুলোর সবটিতে সেটি আছে; একই PUT-এর baseline 2xx body-গুলোর কোনোটিতে নেই। তবে Schemathesis-এর 2/65/198টি accepted violation **এই PUT-এ নয়**; অন্য operation-এ। ফলে “একই phone/address breach এক fuzzer-এ 500, অন্যটিতে 2xx”—এমন matched comparison এই corpus দেয় না। [Evidence: `E1/manifest.json:180–190`, `E3/manifest.json:158–168`; `F:1–5`।]

## Evidence locator ও scope

সব capture-এর prefix `08_experiments/E1_pilot/runs/market/`। নিচের alias-এর পরে `:N` মানে সেই run-এর **`exchanges.jsonl`-এর 1-based physical line N**; `/filename:N` দিলে সেই file-এর line। Seed suffix `{s}` = 1, 2, 3।

| Alias | Run directory |
|---|---|
| `E{s}` | `20261114T183929Z_batch_940129_mutated_REQUEST_STRICT_p30_s{s}` |
| `B{s}` | `20261114T183929Z_batch_940129_baseline_NONE_p0_s{s}` |
| `S{s}` | `20261114T104059Z_batch_339514_mutated_REQUEST_STRICT_p30_s{s}` |
| `SB{s}` | `20261114T104059Z_batch_339514_baseline_NONE_p0_s{s}` |

Source alias `M` = `08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market`; `R` = `M/market-rest/src/main/java/market`; `C` = `M/market-core/src/main/java/market`। Scratch alias `F` = `09_collab/logs/T35_scratch/findings.jsonl`; `P` = `09_collab/logs/T35_scratch/provenance.json`। নিচে bare scratch filenames ওই scratch directory-তে; `harness_v2/…` = `08_experiments/E1_pilot/harness_v2/…`, bare result CSV = `08_experiments/E1_pilot/pilot_results/…`, এবং bare `specmut.py` = `08_experiments/tools/specmut.py`। `F:1/2` যথাক্রমে s1/s3 comparison, `F:3/4/5` Schemathesis s1/s2/s3, `F:6` EvoMaster s2 control। Full per-request derived locators `contacts.jsonl` ও `eligible.jsonl`-এর `run,line` field-এ রাখা হয়েছে। [Evidence: `09_collab/logs/T35_scratch/analyse.py`, `evidence.py`; `F:1–6`।]

T32-এর location-level eligibility বজায় রাখা হয়েছে: edited location original-valid হতে হবে এবং নতুন semantic constraint ভাঙতে হবে; অন্য location invalid থাকলেও তার পৃথক valid location-এর exposure গণনা হয়। তাই baseline-এর overall eligible count-কে “পুরো body original-valid” বলা হয়নি। এই task-এ ছয়টি controlled STRICT run ও তাদের ছয়টি recorded baseline-এর **32,206 exchange** পড়া হয়েছে। [Evidence: `08_experiments/E1_pilot/pilot_results/strict_exposure.py:230–283`; `09_collab/logs/T35_scratch/verification.json`, `total_exchanges`; `traffic_summary.json`-এর 12টি `id`।]

## 1. কোন source tree ও jar?

Harness-এর `JAR_SOURCE` সরাসরি **`jdk_11_maven/cs/rest-gui/market/market-rest/target/market-sut.jar`**। `prepare_dist.sh` সেটি `emb/dist/market-sut.jar`-এ copy করে; recorded `emb_config_sha256`-এর Dockerfile হলো `emb/dockerfiles/market.dockerfile`, যার line 3 ওই dist jar copy করে। `market-rest/pom.xml`-এ packaged entry class `market.RestApplication`। [Evidence: `08_experiments/E1_pilot/harness_v2/suts/market.env:3–5`; `harness_v2/prepare_dist.sh:10–12,45–47`; `08_experiments/_external/emb/dockerfiles/market.dockerfile:3`; `M/market-rest/pom.xml:35–40`; `E1/run.json:168–171`।]

১২টি run-এর `sut_jar_sha256`, বর্তমান target jar ও dist jar—সবগুলোর SHA-256:

```text
527b06a6fb8d45cc5371af2862b8fb881d42441c7b022f4bfd4d3714dd737f95
```

সব run-এ `code_mutation=null`; Dockerfile ও compose file-এর current hash-ও ১২টি recorded `emb_config_sha256`-এর সঙ্গে মেলে। Jar-এর controller, handler, error response, ContactsDTO ও contacts service-এর পাঁচটি class বর্তমান এই tree-এর `target/classes`-এর সঙ্গে byte-identical; class debug metadata-র source filename/line table-ও সংরক্ষিত। সুতরাং trace-এর জন্য এই **REST/core source tree** ব্যবহার করা হয়েছে। [Evidence: `E1/run.json:41–42`; `P:1–364`, keys `all_12_recorded_jars_match`, `all_12_code_mutation_null`, `config_hashes`, `classes`; `evidence.py:128–180`।]

`source_spec` হলো `emb/openapi-swagger/market.json`—এটি specification-এর provenance, Java source tree-এর নাম নয়। এর hash `cf51a9d511b970fd51bce1206eb9429024c11eb180ada58b43193bcb5883c3cd`, সব run-এর recorded source hash-এর সঙ্গে মেলে। ⚠️ এই E1 metadata-তে original Java source-tree digest/reproducible build proof নেই; jar/hash/class correspondence source attribution-এর শক্ত evidence, সম্পূর্ণ build attestation নয়। [Evidence: `E1/run.json:5–6,42`; `P:8–9,20–364`, keys `source_spec_sha256`, `all_12_source_spec_matches`, `classes`; `harness_v2/run_metadata.py:38–39,61–65`।]

## 2. s1/s3-এর failing request বনাম baseline accepted request

নিচের fresh column-গুলো শুধু T32-eligible violating request-এর; baseline column একই PUT-এর 2xx violating request-এর। Phone/address count overlap করে—যোগ করে unique request count করা যাবে না। [Evidence: `F:1–2`, `fresh_phone_breach`, `fresh_address_breach`; `strict_exposure.csv`, rows `market.s1.evomaster.o2`, `market.s3.evomaster.o3`।]

| বৈশিষ্ট্য | E1 fresh | E3 fresh | B1 একই PUT 2xx | B3 একই PUT 2xx |
|---|---:|---:|---:|---:|
| Request / response | 392 / সব 500 | 361 / সব 500 | 81 / সব 200 | 74 / সব 200 |
| `phone.maxLength:20→1` breach | 392 | 361 | 81 | 74 |
| `address.maxLength:100→1` breach | 148 | 128 | 62 | 17 |
| Phone length range | 12–20 | 12–19 | 13–19 | 12–19 |
| Address length 0 / 1 / 2 | 121 / 123 / 148 | 109 / 124 / 128 | 0 / 19 / 62 | 0 / 57 / 17 |
| Body keys | `_links,address,phone` | একই | `address,phone` | একই |
| `_links` | array, length 0–5 | array, length 0–5 | absent | absent |
| Empty `_links:[]` | 70 | 61 | 0 | 0 |
| `Content-Type` / `Accept` | `application/json` / `*/*` | একই | একই | একই |

Evidence: `F:1–2`, `fresh_eligible_contacts.counts`, `baseline_accepted_contacts.counts`; raw examples `E1:6,58`, `E3:6,85`, `B1:74`, `B3:112`; independent body-schema recount `verification.json:2–27`।

প্রতিটি fresh eligible request-এ `_links` প্রথম JSON property; nonempty array-এর প্রতিটি item-এর `rel` একটি object, এবং প্রতিটি Link property present। Link-এর string field-গুলোর length ≤1। Query `name`-ও সব fresh eligible request-এ present, length 0 বা 1: E1-এ 194/198, E3-এ 187/174। অর্থাৎ tightened required/name/Link constraints-এর সঙ্গে মেলে এমন systematic পরিবর্তন আছে, একই সঙ্গে phone/address length breach-ও আছে। Baseline accepted PUT-এ query `name` absent ছিল B1-এর 62/81 এবং B3-এর 16/74 request-এ; অন্যগুলোতে প্রায়ই length >1। [Evidence: `F:1–2`, counts `first_body_key`, `all_link_properties_present`, `all_link_strings_length_le_1`, `query_name_lengths`; `E1/spec.test.json:366–446`; `B1:74`, `B3:112`।]

**Auth/role:** metadata-তে সব ১২টি run-এর configured role `user`; controller-এ `@Secured({"ROLE_USER"})`। E1 eligible request-এর 391টিতে Authorization header present/redacted, একটিতে absent (`E1:2786`); E3-এর 361টিতেই present/redacted। B1/B3 accepted PUT-এ 81/74টিতেই present/redacted। এই চার group-এ Cookie header নেই। Header redaction-এর কারণে actual principal/value equality পুনরুদ্ধার করা যায় না। ⚠️ Auth identity একই ছিল—এমন দাবি করা যাচ্ছে না; তবে missing-header request-সহ একই parsing error এবং generic handler-এর source auth-কে এই uniform error-এর প্রয়োজনীয় ব্যাখ্যা করে না। [Evidence: `P:7`, `all_12_configured_auth_user`; `R/rest/ContactsRestController.java:24–26`; `F:1–2`, counts `auth_state`, `cookie_present`; `E1:2786`; redaction flow `harness_v2/run_pilot.sh:62–81`।]

**Path ID/state/order:** failing operation-এ কোনো path ID নেই। Contact update principal থেকে user login নেয়; cart/product/order ID নেয় না। দুই fresh run-এর প্রথম failure **line 6**, তার আগে DELETE নেই; line 5-এ `GET /customer/orders` 200। অন্যদিকে baseline success `B1:74`-এর আগে line 68-এ cart DELETE 200, এবং `B3:112`-এর আগে line 105-এ DELETE 200 আছে। ⚠️ Preceding DELETE/empty cart এই parsing failure-এর কারণ নয়: প্রথম failure-ই DELETE-পূর্ববর্তী এবং stack argument deserialization-এ; successful baseline contact update-ও DELETE-এর পরে পাওয়া যায়। [Evidence: `F:1–2`, `first_fresh_example`, `first_baseline_accepted_example`; `E1:5–6`, `E3:5–6`, `B1:68,74`, `B3:105,112`; `R/rest/ContactsRestController.java:49–54`; `C/service/impl/ContactsServiceImpl.java:24–38`।]

Baseline-এও array-valued `_links`-এর একই error আগে থেকেই ছিল: B1-এ **358**, B3-এ **303**টি PUT। Fresh run-এ সব PUT-এর ফল যথাক্রমে **885/789টি 500**; এর বাইরে থাকা 493/428টি request সম্পূর্ণ JSON হিসেবে parse করা যায়নি বলে eligible body-length group-এ ঢোকেনি। সব 500-কে 753টি original-valid body breach বলা হয়নি। [Evidence: `F:1–2`, `baseline_array_error_count`, `fresh_contacts_status`; `traffic_summary.json`, `id=market.s{1,3}.evomaster.fresh`, `contacts_groups`; `contacts.jsonl`, `body_json_parse_error`।]

⚠️ `_links` সরিয়ে দিলে সব fresh request 2xx হতো—এটিও বলা যায় না। উদাহরণস্বরূপ address empty থাকা 121/109টি request-এ DTO-র `@NotEmpty` validation পরবর্তী rejection ঘটাতে পারে; SUT-এর এই counterfactual চালানো হয়নি। Source-এর phone/address size যথাক্রমে 20/100; mutant spec-এর bound 1 application code-এ বসানো হয়নি। [Evidence: `F:1–2`; `C/dto/ContactsDTO.java:15–23`; `P:6`, `all_12_code_mutation_null`।]

## 3. Schemathesis-এর accepted violation কোথায়?

| Seed | Fresh accepted eligible violation | একই `PUT /customer/contacts`-এর সব response |
|---|---|---|
| s1 | `GET /products/{productId}`: **2** | 98×500, 2×406, **0×2xx** |
| s2 | `GET /customer/cart`: **63**; `GET /products/{productId}`: **2** | 59×500, 41×406, **0×2xx** |
| s3 | `GET /customer`, `GET /customer/contacts`, `GET /customer/orders`: **66 করে** | 87×500, 13×406, **0×2xx** |

Evidence: `F:3–5`, `accepted_by_operation`, `contacts_status`; raw accepted examples `S1:1021,1080`, `S2:106,1030,1032`, `S3:15,615,815`।

S1-এর দুই accepted product request-এই `productId=1`; S2-তে 6 ও 2। এগুলো নতুন `maximum=0` ভেঙেছে এবং 200 পেয়েছে—ঐ request-এর সময় ওই ID-তে resource পাওয়া গেছে। S2-এর accepted cart GET-এর 54টিতে required query `name` নেই, 9টিতে name length >1; S3-এর প্রতিটি GET-এর 40টিতে name absent, 26টিতে length >1। এসব request-এ failing ContactsDTO body নেই। তাই nonexistent product ID বা empty-cart checkout failure দিয়ে Schemathesis-এর 2xx বনাম EvoMaster-এর contacts-500 তুলনা ব্যাখ্যা করা ঠিক হবে না; তুলনীয় operation/body-ই আলাদা। [Evidence: `eligible.jsonl`, `run=S1/S2/S3` ও উল্লিখিত raw lines-এর `breaches,numeric_path_ids`; `F:3–5`, `accepted_breach_keywords_by_operation`; `strict_exposure.csv`, corresponding operation/constraint rows।]

EvoMaster baseline-এর **81/280/667** accepted violation-ও সব contacts PUT নয়। B1-এ 81টি ওই PUT; B2-এ cart GET 225 + cart PUT 48 + product GET 7; B3-এ contacts PUT **74** + orders GET 197 + contacts GET 204 + customer GET 192। তাই same-operation baseline comparison-এ s3-এর সংখ্যা 667 নয়, **74**। [Evidence: `F:1–2`, `baseline_all_eligible_accepted_ops`; `aggregates.json`, B2 run-এর `all_eligible_accepted_ops`; `eligible.jsonl`-এর সংশ্লিষ্ট run/status=200 rows।]

## 4. Response body থেকে code path

সব 753টি target response-এর short excerpt: **`JSON parse error: Expected relation name`**। Body-তে nested exception class `com.fasterxml.jackson.databind.JsonMappingException`, reference chain `market.dto.ContactsDTO["_links"]`; `fieldErrors=[]`, `entityName=null`। Body নিজে outer Java exception class বলে না; saved SUT log তা দেয়: `HttpMessageNotReadableException` → `JsonMappingException` → **`com.fasterxml.jackson.core.JsonParseException`**। [Evidence: `E1:6`, `E3:6`; `F:1–2`, `fresh_all_error_markers`, count `empty_field_errors`; `E1/compose.log:67,310,321`; `E3/compose.log:67,159,170`; `P:365–556`, `log_traces`।]

Trace-এর ধাপগুলো:

1. **Body binding:** route `customer/contacts`-এর PUT argument হলো `@RequestBody @Valid ContactsDTO`; DTO extends `RepresentationModel<ContactsDTO>`। [Evidence: `R/rest/ContactsRestController.java:24,49–50`; `C/dto/ContactsDTO.java:3,13`।]
2. **HAL `_links` parsing:** jar-এর `spring-hateoas-1.2.4.jar`-এর `Jackson2HalModule$HalLinkListDeserializer.deserialize()` next token-এ `END_OBJECT` অথবা relation-এর `FIELD_NAME` প্রত্যাশা করে; অন্য token হলে line **597**-এ `JsonParseException("Expected relation name")` throw করে। এই method-এর constant-pool references, branch ও line-number table নিজস্ব Python দিয়ে jar-এর data হিসেবে পড়া হয়েছে; Java চালানো হয়নি। [Evidence: `P:634–748`, `hal_deserializer.methods[name=deserialize].prefix_data_disassembly`, PCs 8–44; `E1/compose.log:321–324`; `E3/compose.log:170–173`।]
3. **Array/object mismatch:** OAS request schema `_links`-কে array বলে, কিন্তু এই HAL deserializer relation-name keyed object-এর token stream চায়। Array-এর প্রথম item object হলেও তা `FIELD_NAME` নয়; empty array-এর `END_ARRAY`-ও প্রত্যাশিত `END_OBJECT` নয়। ⚠️ তাই `_links` array-তেই parser আটকে যায়, আগে থাকা এই property পার হয়ে phone/address validation-এ পৌঁছায় না। Empty-array natural examples-ও একই error দিয়েছে। [Evidence: `E1/spec.test.json:366–369`; `P:634–748`-এর উপরোক্ত bytecode; `E1:58`, `E3:85`; `F:1–2`, `first_empty_links_example`, `first_body_key`।]
4. **Spring wrapping:** saved frames-এ `AbstractJackson2HttpMessageConverter.readJavaType` এবং `RequestResponseBodyMethodProcessor.resolveArgument`; response-এর reference chain-ও `_links`-এ। ⚠️ এটি controller/service body চালুর আগের argument-reading failure-এর trace। Per-request trace ID নেই; representative saved stack ও সব response-এর একই exception signature মিলিয়ে এই reconstruction। [Evidence: `E1/compose.log:67–73,310–324`; `E3/compose.log:67–73,159–173`; `P:365–556`, `log_traces`; `F:1–2`।]
5. **কেন 500:** `@ControllerAdvice(basePackages="market.rest")`-এর `otherExceptions(Exception e, WebRequest request)`-এ `@ResponseStatus(INTERNAL_SERVER_ERROR)`; এটি `e.getMessage()` দিয়ে response বানায়। `HttpMessageNotReadableException`-এর পৃথক handler নেই। Bean validation-এর `MethodArgumentNotValidException` এবং domain `CustomNotValidException`-এর handler 406, কিন্তু এই parse exception সেই দুই class নয়। [Evidence: `R/rest/exception/RestExceptionHandler.java:23–25,37–42,63–81`; `R/rest/exception/RestErrorResponse.java:14–30`; `E1/compose.log:67`।]

## 5. Baseline → mutated trajectory কেন ফল বদলাল?

Original body schema-তে `_links,address,phone` কোনোটি required-list-এ ছিল না; STRICT mutation তিনটিকেই required করেছে। Nested Link object-এও সব property required; সব সাধারণ string-এর maxLength 1; query `name` required/maxLength 1। Mutator source-ও ঠিক এই recursive policy বাস্তবায়ন করে। `_links`-এর **array type আগে থেকেই ছিল**—mutant type বদলায়নি, optional incompatible representation-টিকে বাধ্যতামূলক করেছে। [Evidence: `B1/spec.test.json:662–685`; `E1/spec.test.json:362–446`; `E1/manifest.json:180–190`; `E3/manifest.json:158–168`; `08_experiments/tools/specmut.py:117–125,151–170`।]

Saved EvoMaster argv `spec.test.json` input নির্দেশ করে এবং recorded spec-test hash actual file-এর সঙ্গে মেলে। এই changed generator input-এর fresh eligible body-তে required `_links` সবসময় present; baseline-এর 155টি accepted contacts body-তে absent। ⚠️ Required edit-এ generator sensitivity পুরোনো array/HAL mismatch-এ traffic ঠেলে দিয়েছে—এটাই observed systematic difference-এর সবচেয়ে সরাসরি explanation। একক edit-এর ablation বা generator-internal trace ছাড়া inclusion-এর পুরো causal chain experimental isolation করা হয়নি। [Evidence: `P:557–588`, `generator_binding`; `F:1–2`; `E1/run.json`, `evomaster_argv,file_sha256`; `B1:74`, `B3:112`।]

Trajectory CSV-তে market STRICT EvoMaster s1/s2/s3-এর `pos_vs_base` **0.0069 / 0.0039 / 0.0044**; ছোট request overlap alone specific failure cause বলে না। এখানে cause attribution-এর বাড়তি evidence হলো changed requiredness + concrete body shape + response message + source/bytecode trace। Seed 2-তে contacts PUT edited operation নয়; তার fresh-এ 78টি contacts PUT 200, সবগুলোতে `_links` absent; edited-location eligible violation 0। [Evidence: `08_experiments/E1_pilot/pilot_results/fuzzer_trajectory_overlap.csv`, `sut=market,fault=REQUEST_STRICT,fuzzer=evomaster,seed=1/2/3`; `strict_exposure.csv`, `market.s2.evomaster` operation rows; `F:6`; `P:557–588`, `generator_binding`।]

**Unsatisfiability-ও বাস্তব, কিন্তু আলাদা স্তরে।** Required phone-এর retained regex-এ সর্বনিম্ন 12 character লাগে: `+` + অন্তত 1 country-code digit + 3+3+2+2 digit। Mutant `maxLength=1`, required body ও required phone একসঙ্গে কোনো valid contacts input অনুমোদন করে না। Fresh eligible phone-এর length 12–20/12–19 এই contradiction-এর সঙ্গে সঙ্গতিপূর্ণ; ⚠️ generator কোন internal priority দিয়ে regex/length সামলেছে, তা capture থেকে জানা যায় না। এই contradiction নিজে HAL-এর `Expected relation name` exception তৈরি করে না—তার code branch `_links` token পরীক্ষা করে। [Evidence: `E1/spec.test.json:362,427–440`; `E3/spec.test.json`, contacts PUT body-এর একই schema; `F:1–2`; `P:634–748`, HAL disassembly PCs 8–44; T32 `strict_exposure.csv` phone constraint rows।]

## 6. R1-এর implication — পাঁচটি সিদ্ধান্ত

- **⚠️ Generator effect প্রধান contributor:** নতুন required `_links` fresh eligible body-র 753/753টিতে আছে; baseline accepted same-PUT body-র 155/155টিতে absent। একই trajectory-তে অন্য tightened constraints মেনে ছোট query/Link strings-ও এসেছে। তাই no-acceptance-কে “constraint exercise হয়নি” বা “SUT maxlength enforce করেছে” বলা যাবে না। [Evidence: `F:1–2`; `E1/spec.test.json:409–446`।]
- **SUT parsing/error-mapping effect স্পষ্ট:** OAS array representation HAL parser-এর সঙ্গে অসামঞ্জস্যপূর্ণ; generic market handler readable-body exception-কে 500 বানায়। Baseline-এও array request-এর একই error ছিল, ফলে এটি নতুন mutant Java behaviour নয়। [Evidence: `P:634–748`, HAL disassembly; `R/rest/exception/RestExceptionHandler.java:37–42`; `F:1–2`, baseline array errors 358/303।]
- **⚠️ SUT state এই target 500-এর প্রয়োজনীয় কারণ নয়:** প্রথম failure DELETE-এর আগে; failing route-এ ID/cart lookup নেই এবং saved trace argument parsing-এ। অন্য operation-এর empty cart/nonexistent ID failure-কে এই 753টির কারণ হিসেবে মেশানো যাবে না। [Evidence: `E1:5–6`, `E3:5–6`; `R/rest/ContactsRestController.java:49–54`; `E1/compose.log:69–73,323`।]
- **Spec-edit unsatisfiability সহাবস্থান করছে:** required phone regex বনাম maxLength 1 অসাধ্য; পাশাপাশি required `_links` পুরোনো representation mismatch বাধ্যতামূলক করেছে। ⚠️ Multi-keyword STRICT edit-এর observed effect তাই single numeric/string bound-এর causal effect হিসেবে ব্যাখ্যা করা যাবে না। [Evidence: `E1/spec.test.json:366–440`; `specmut.py:151–170`; `F:1–2`।]
- **⚠️ Detection outcome-এ generator × existing SUT/spec interaction:** 500 response-এ checker `INVALID_ACCEPTED` বানায় না; baseline-এ same server-error path থাকায় fresh NEW শূন্য হওয়া exposure শূন্য বোঝায় না। Schemathesis-এর accepted violations অন্য operation/constraint-এ, এবং replay-এর baseline traffic-এ missing `_links`-সহ accepted PUT আছে। এটি fuzzer ranking-এর স্বাধীন trial বা একটি নতুন SUT defect count নয়। [Evidence: `08_experiments/tools/conformance.py:465–471`; `fuzzer_trajectory_overlap.csv`, উপরোক্ত তিন market STRICT row-এর `fresh_mut_NEW_checkable=0`; `F:1–5`; `strict_exposure.csv`, market run rows।]

## Verification, সীমা ও reproducibility

`analyse.py` ১২টি traffic side-এর eligible status distribution T32 CSV-এর সঙ্গে assert করে। আলাদা `verify.py` সরাসরি resolved original schema-তে `jsonschema.Draft4Validator` চালিয়ে s1/s3 fresh **392/361**, same-PUT baseline accepted **81/74** independently মিলিয়েছে; এটি `conformance.request_problems()` ব্যবহার করে না। Baseline-এর direct body-length-only count 368/291-কে T32-এর সব location-এর union count বলা হয়নি। [Evidence: `09_collab/logs/T35_scratch/analyse.py`, শেষের `expected` assertion; `verify.py:35–89`; `verification.json`।]

224টি protected input/source/tool/harness file-এর hash verification-এ পরিবর্তন নেই। Output-এ fixture header/token ও decoded credential components-এর in-memory exact-match scan-এ hit নেই। Raw header/body dump রাখা হয়নি; auth value/Cookie value/credential quote করা হয়নি। সব লেখা report/scratch ও একটি board Log line-এ সীমিত; SUT, fuzzer, Java, Docker, Maven, external code বা network চালানো হয়নি। Jar examination কেবল Python `zipfile` ও class-file data parsing। [Evidence: `verification.json:28–33`, `protected_sha256.json`; `verify.py:72–106`; `evidence.py:45–126`; task boundary `09_collab/tasks/T35.md:32–36`।]

Reproduce:

```sh
/usr/bin/python3 -I -B 09_collab/logs/T35_scratch/analyse.py > 09_collab/logs/T35_scratch/recount_stdout.json
/usr/bin/python3 -I -B 09_collab/logs/T35_scratch/evidence.py
/usr/bin/python3 -I -B 09_collab/logs/T35_scratch/verify.py
```

সীমা: saved 300-second run, তিন seed; exact auth identity redacted, no isolated `_links` removal replay, no one-edit-at-a-time generator experiment, no per-request controller-entry trace। ⚠️ Code-level parsing branch ও generic 500 mapping-এর evidence শক্ত; generator-এর internal priority এবং `_links` সরানোর পর প্রতিটি request-এর counterfactual status অমীমাংসিত। [Evidence: `E1/run.json`, `budget_seconds`; `F:1–2`; `P:365–556`, `log_traces`; `09_collab/tasks/T35.md`, execution constraints।]
