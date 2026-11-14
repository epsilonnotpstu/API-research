# T25 রিপোর্ট — E5 replacement mutation sites

## কাজ ও ফল

`sites.json`-এ `market-response-field-v2` এবং `petstore-reject-valid-v2` append করা হয়েছে; দুটিই `pilot: true`। আগের ২০টি entry ও catalogue metadata অপরিবর্তিত, মোট entry ২২। `codemut.py` বদলানোর প্রয়োজন হয়নি। নতুন site দুটির exact source-copy application, hash/anchor পরীক্ষা ও refusal tests দেওয়া হয়েছে। প্রথমে existing ১১৭/১১৭, পরে মোট ১২৪/১২৪ tests PASS; failure/error/skip শূন্য। সব পুরোনো ২২টি codemut test method-এর AST অপরিবর্তিত; fixture-এর temporary directory শুধু T25 scratch-এ নেওয়া হয়েছে। প্রমাণ: `08_experiments/E5_codemut/sites.json:520,549`; `test_codemut.py:218–327` একই directory-তে; `09_collab/logs/T25_scratch/baseline_tests.txt` শেষ তিন লাইন; `tests.txt` শেষ চার লাইন; `verification.json`-এর `old_entries_preserved`, `original_test_methods_preserved`, `tests`।

এটি write-only design ও Python verification। Java/Maven/Docker/network/build/SUT execution করা হয়নি; source copies সাধারণ data হিসেবে লেখা হয়েছে। `harness_v2/`, `tools/`, `_external/`, `E1_pilot/runs/`, `E5_codemut/work/`-এ write করা হয়নি; blind package/key খোলা হয়নি। শুরুতে snapshot করা ১৯৮টি protected file (এর মধ্যে `codemut.py`) ও selection audit-এর ১৩১টি input hash অপরিবর্তিত। এই hash count পুরো forbidden directory tree-র exhaustive snapshot দাবি করে না। প্রমাণ: `09_collab/tasks/T25.md`, Write scope; `09_collab/logs/T25_scratch/before_sha256.json`, `input_sha256.json`, `verification.json:1–20`; execution record `09_collab/logs/T25.log`।

## Market নির্বাচন ও compile dependency evidence

নতুন anchor: `08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market/market-rest/src/main/java/market/RestConfig.java:13`, `public class RestConfig {`। একই file-এর একটিমাত্র edit-এ `Jackson2ObjectMapperBuilderCustomizer` bean ও nested abstract mix-in যোগ হয়; mix-in-এর `getPrice()`-এ FQ `@JsonProperty(access = WRITE_ONLY)` থাকে। Builder শুধু `ProductDTO`-র জন্য mix-in register করে। Exact `before`/`after`, original hash এবং patch: `08_experiments/E5_codemut/sites.json`, `site_id=market-response-field-v2`; `09_collab/logs/T25_scratch/source_proofs/market-response-field-v2/patch.diff:1–19`।

`market-rest`-এ Jackson compile dependency-র POM path নিচে; dependency-গুলিতে `optional=true` নেই। Explicit scope না থাকলে Maven-এর default compile scope ব্যবহৃত হয়েছে। Cached POM data-র byte-identical snapshot scratch-এ রাখা হয়েছে, কোনো Maven command চালানো হয়নি; original location ও SHA-256 আছে `09_collab/logs/T25_scratch/pom_evidence.json`-এর ছয়টি entry-তে।

| Dependency edge / version | File evidence |
|---|---|
| market-rest → spring-boot-starter-web; parent imports Boot dependency management 2.4.3 | `08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market/market-rest/pom.xml:60–63`; `08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market/pom.xml:44–49` |
| starter-web 2.4.3 → starter-json 2.4.3, explicit compile | `09_collab/logs/T25_scratch/poms/spring-boot-starter-web-2.4.3.pom:50–54` |
| starter-json 2.4.3 → jackson-databind 2.11.4, explicit compile | `09_collab/logs/T25_scratch/poms/spring-boot-starter-json-2.4.3.pom:56–60` |
| jackson-databind → jackson-annotations, default compile | `09_collab/logs/T25_scratch/poms/jackson-databind-2.11.4.pom:60–67` |
| Boot BOM → Jackson BOM 2.11.4; annotations version 2.11.4 | `09_collab/logs/T25_scratch/poms/spring-boot-dependencies-2.4.3.pom:78,2610–2616`; `09_collab/logs/T25_scratch/poms/jackson-bom-2.11.4.pom:52,60,85–88` |
| starter-web → starter 2.4.3 → spring-boot-autoconfigure 2.4.3, explicit compile; customizer interface-এর dependency path | `09_collab/logs/T25_scratch/poms/spring-boot-starter-web-2.4.3.pom:44–48`; `09_collab/logs/T25_scratch/poms/spring-boot-starter-2.4.3.pom:50–54` |

⚠️ POM graph অনুযায়ী `market-rest`-এর compile classpath-এ annotation ও customizer dependency থাকার যুক্তি পাওয়া যায়; এটি নতুন mutant-এর successful compilation নয়। আগের `market-core` failure-এর exact root cause নতুন করে প্রমাণ করা হয়নি। আগের BUILD-INVALID record অপরিবর্তিত: `08_experiments/E5_codemut/COORDINATOR_NOTES.md:24–30`; নতুন manifest-এ `validation.java_compile=not_run`।

`RestApplication`-এর `@Import`-এ `RestConfig` আছে এবং auto-configuration enabled: `08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market/market-rest/src/main/java/market/RestApplication.java:9–12`। Product list/detail-এ assembler থেকে `ProductDTO` যায়: একই market root-এর `market-rest/src/main/java/market/rest/ProductsRestController.java:37–42,56–60`; price mapping আছে `market-core/src/main/java/market/dto/assembler/ProductDtoAssembler.java:21`। Saved spec-এ শুধু GET `/products` এবং GET `/products/{productId}`-এর response schema-য় ProductDTO আছে; `ProductDTO.required`-এ `price`: `08_experiments/_external/emb/openapi-swagger/market.json`, `#/definitions/ProductDTO/required`, `#/paths/~1products/get/responses`, `#/paths/~1products~1{productId}/get/responses`। তাই affected-operation list-এ ওই দুই GET রাখা হয়েছে।

⚠️ [H] সক্রিয় MVC ObjectMapper customizer গ্রহণ করলে JSON output থেকে `price` বাদ যাবে, setter binding থাকবে এবং `RESPONSE_SCHEMA` / `I-RESP-CONTRACT` পাওয়া উচিত। Control-এর nonempty product JSON, mutant-এর missing-price JSON এবং unchanged spec দিয়ে identical-request witness প্রয়োজন; HATEOAS mapper/mix-in integration runtime-এ যাচাই বাকি। Injection label `expected_L1=IMPL` স্বাধীন attribution prediction নয় (`sites.json`, নতুন Market entry-র `conditions` ও `witness_plan`)।

Python oracle model-এ saved control `08_experiments/E1_pilot/runs/market/20261114T130729Z_618104_e5_market-wrong-status_control_s1/exchanges.jsonl:1002`-এর ১১টি product-এর price key counterfactually বাদ দিলে ১১টি required-price diagnostic পাওয়া যায়, pointer `/items/required`, একই normalized fingerprint; ওই exact control response-এ baseline checker diagnostic ছিল শূন্য। এটি Python-এ body transformation, Java/Jackson execution নয়; অন্য response-এর pre-existing `_links` সমস্যা আলাদা রাখতে হবে। প্রমাণ: `09_collab/logs/T25_scratch/oracle_models.json`, `market_counterfactual_price_removal`; `verification.json`, `market_model`।

## Petstore নির্বাচন, exposure ও noise floor

নতুন site `08_experiments/_external/emb/jdk_8_maven/cs/rest/original/swagger-petstore/src/main/java/io/swagger/petstore/controller/UserController.java:103`-এ `loginUser`-এর শুরুতে `username == null` হলে `BadRequestException` যোগ করে। Saved OAS-এ username/password দুটোই optional string; পুরোনো handler parameter presence পরীক্ষা না করে response তৈরি করে। প্রমাণ: ওই source `:103–110`; `08_experiments/_external/emb/openapi-swagger/swagger-petstore.json`, `#/paths/~1user~1login/get/parameters`; `09_collab/logs/T25_scratch/source_proofs/petstore-reject-valid-v2/patch.diff:1–10`।

দুটি timestamped saved bundle-এর প্রয়োজনীয় saved evidence পড়া হয়েছে: `08_experiments/E5_codemut/work/petstore-reject-valid_20261114T114156Z/` এবং `08_experiments/E5_codemut/work/petstore-response-field_20261114T113954Z/`। প্রতিটিতে seeds ১–৩-এর `analysis-s*-default/attribution.csv` ও `noise-analysis-s*-default/attribution.csv`, তাদের `analysis.json`-এ pointed run-এর `exchanges.jsonl`, saved role-specific violations পড়া হয়েছে। মোট ১২টি analysis ও ২৪টি role-run; full per-operation count ৪৮০ row। প্রমাণ: `09_collab/logs/T25_scratch/input_sha256.json` path/hash rows; `petstore_operation_counts.csv:P0001–P0480`; `audit_selection.py:39–158`।

Count-এর একক captured exchange। `analysis.json` থেকে mutant pair-এর C=control, M=mutant এবং noise pair-এর N=control, R=control_repeat আলাদা রাখা হয়েছে; N ও C একই role-এর হলেও আলাদা run। Template matching-এ বর্তমান own `conformance.Spec.match` এবং request validity-তে `request_problems` ব্যবহার করা হয়েছে, T24-এর int32/int64 checking enabled। Saved `VALID_REJECTED` count পূর্বের saved violations/attribution থেকেই নেওয়া; পুরোনো analysis silently regenerate করা হয়নি। JSONL line locators physical ১-based line; saved violation `exchange` index ০-based। প্রমাণ: `09_collab/logs/T25_scratch/audit_selection.py:50–136`; `08_experiments/tools/conformance.py:45–66,182–219,292–401`।

নির্বাচিত GET `/user/login`-এর নিচের প্রতিটি cell-এ `200×2`, request-valid ২, optional username absent ২; 400=0, 422=0, saved VALID_REJECTED=0। Cell-এ CSV row ID দেওয়া আছে; ওই row-এর `exchanges` ও `lines` সরাসরি original file/line evidence। Source: `09_collab/logs/T25_scratch/petstore_operation_counts.csv`, নিচের IDs; প্রত্যেক individual request: `petstore_login_witnesses.json`, ৪৮টি file/line record।

| Saved bundle | Seed | C: pair control | M: historical mutant | N: noise control | R: noise control_repeat |
|---|---|---|---|---|---|
| petstore-reject-valid_20261114T114156Z | 1 | P0010: 200×2 | P0030: 200×2 | P0150: 200×2 | P0130: 200×2 |
| petstore-reject-valid_20261114T114156Z | 2 | P0050: 200×2 | P0070: 200×2 | P0190: 200×2 | P0170: 200×2 |
| petstore-reject-valid_20261114T114156Z | 3 | P0090: 200×2 | P0110: 200×2 | P0230: 200×2 | P0210: 200×2 |
| petstore-response-field_20261114T113954Z | 1 | P0250: 200×2 | P0270: 200×2 | P0390: 200×2 | P0370: 200×2 |
| petstore-response-field_20261114T113954Z | 2 | P0290: 200×2 | P0310: 200×2 | P0430: 200×2 | P0410: 200×2 |
| petstore-response-field_20261114T113954Z | 3 | P0330: 200×2 | P0350: 200×2 | P0470: 200×2 | P0450: 200×2 |

মোট ৪৮/৪৮ request-valid login request-এ 200; এর ৩৬টি C/N/R controls থেকে, ১২টি পুরোনো অন্য-site mutants থেকে। সব ৪৮টি empty query, ফলে নতুন null-username guard-এর condition পূরণ করে। প্রতি run মাত্র ২টি request এবং একটিই query shape—৪৮টি independent input shape বা high-volume per-run coverage দাবি করছি না। Task-এর “many valid requests” criterion এখানে corpus জুড়ে ৩৬টি control witness/৪৮টি মোট repeated witness হিসেবে পূরণ করা হয়েছে; চাইলে coordinator অতিরিক্ত directed repetitions দিয়ে exposure বাড়াতে পারবেন। প্রমাণ: `09_collab/logs/T25_scratch/selection_summary.json`; `petstore_login_witnesses.json`-এর `request_valid`, `query`, `guard_hit`, `status`।

Candidate screening-এ GET `/store/inventory` বাদ: সব run-এ 400 ছিল (seed ১: 200×15+400×8; seed ২: 200×15+400×3; seed ৩: 200×17+400×1)। GET `/user/logout`-ও 400/422-মুক্ত, কিন্তু প্রতি run ১টি request; login-এ ২টি। বাকি captured declared operations-এর corpus-এ 400 আছে। Attribution-এ VALID_REJECTED না থাকা একা যথেষ্ট ধরা হয়নি; raw statuses-ও পরীক্ষা করা হয়েছে। প্রমাণ: `09_collab/logs/T25_scratch/petstore_operation_counts.csv`, method/template rows; নিচের পূর্ণ count tables।

⚠️ [H] নতুন login guard-এর 400 হলে expected fingerprint হবে `["GET","/user/login","400","VALID_REJECTED","","","",""]`। এই op-এ saved controls, control_repeats ও historical mutants কোথাও 400/422 বা VALID_REJECTED নেই; তাই expected fingerprint শুধু existing fingerprint-এর INCREASED count হওয়ার কথা নয়, NEW হওয়ার ভিত্তি আছে। Python counterfactual-এ একই ৪৮টি valid request-এর শুধু response status 400 করলে প্রত্যেকটিতে ওই fingerprint পাওয়া গেছে। এটি checker capability model, actual mutant result নয়। প্রমাণ: `09_collab/logs/T25_scratch/oracle_models.json`, `login_counterfactual_400`; `petstore_saved_valid_rejected.json`-এ GET `/user/login` row অনুপস্থিত; `08_experiments/E5_codemut/summarise_e5.py`, `EXPECTED_CHANGED_FP_ABSENT_BOTH_NOISE_RUNS_V1` rule।

Saved login 200 response-এ বর্তমান checker `RESPONSE_PARSE` দেয়: body raw session text, JSON quoted string নয়। তাই “request-valid” ও “response-conformant” এক করা হয়নি; pre-existing parse signal আলাদা, expected signal শুধু valid-request rejection। প্রমাণ: `09_collab/logs/T25_scratch/petstore_login_witnesses.json`, সব `saved_response_kinds=["RESPONSE_PARSE"]`; একই file-এর exact source exchange line locators।

## Tests ও reviewable artifacts

| পরীক্ষা | ফল ও evidence |
|---|---|
| Existing suite | 117/117 PASS; `09_collab/logs/T25_scratch/baseline_tests.txt`, শেষ summary |
| New source-copy tests সহ suite | 124/124 PASS, 0 skipped; `09_collab/logs/T25_scratch/tests.txt`, শেষ summary; `test_results.json` |
| Pinned source hash, একটিমাত্র anchor ও এক changed file | `08_experiments/E5_codemut/test_codemut.py:237–268`; দুটো source proof-এর `manifest.json`, `source_files`, `source_sha256`, `mutated_file_sha256` |
| Hash drift refusal, ambiguous/missing anchor refusal | `08_experiments/E5_codemut/test_codemut.py:280–308`; `tests.txt`, সংশ্লিষ্ট test method rows |
| Existing output ও already-mutated tree reapply refusal | `08_experiments/E5_codemut/test_codemut.py:310–324`; `tests.txt`, সংশ্লিষ্ট test method row |
| Original entries/test methods অক্ষত; selected protected inputs অক্ষত | `09_collab/logs/T25_scratch/verify_delivery.py:26–42,113–132`; `verification.json` |

Persistent review copies ও manifest/patch: `09_collab/logs/T25_scratch/source_proofs/market-response-field-v2/` এবং `source_proofs/petstore-reject-valid-v2/` একই scratch root-এ। Market copy-তে ২৩৭টি retained source/resource file, Petstore-এ ৩৭টি; প্রত্যেকটিতে এক Java file ছাড়া সব byte/mode digest অপরিবর্তিত। এই source copies build করা হয়নি। প্রমাণ: `09_collab/logs/T25_scratch/verification.json`, `source_proofs`; দুই proof-এর manifest `source_files`, `source_tree_sha256`, `mutated_tree_sha256`।

Original source SHA-256:

| Site | SHA-256 |
|---|---|
| market-response-field-v2 | `6923166ab53103be941c9828ffcf199f3d6219e6d707c6b9e1322cbc2e044e21` |
| petstore-reject-valid-v2 | `257a89219d5dadc1fa10006098d0fdb95a7e6668f0de7d43040a3d9ec4ede58e` |

Source: `09_collab/logs/T25_scratch/verification.json`, `source_proofs`-এর দুই `source_sha256`; `08_experiments/E5_codemut/sites.json`, শেষ দুই entry।

## সীমাবদ্ধতা ও খোলা প্রশ্ন

১. নতুন Market mutant compile করে কি না, MVC/HATEOAS ObjectMapper mix-in কার্যকর হয় কি না এবং setter binding বজায় থাকে কি না—সবই runtime verification বাকি। Static POM/source review ও Python oracle model-কে successful Java build বা serialization result বলা হয়নি (`sites.json`, Market v2 `conditions`; `verification.json`, `java_compile=not_run`, `runtime=not_run`)।

২. Login-এর exposure repeated ও ছোট; single empty-query shape-এর বাইরে generalization দাবি নেই। ⚠️ Saved no-rejection noise floor ভবিষ্যৎ no-noise guarantee নয়। Fresh v2 controls/noise, তিন seed ও identical valid request-এ control 200 বনাম mutant 400 প্রয়োজন; তখনই noise rule ও causal kill গণনা করা যাবে (`selection_summary.json`, `limitation`; `sites.json`, Petstore v2 `witness_plan`; `08_experiments/E5_codemut/PIPELINE.md`, control-vs-control noise section)।

৩. `pilot: true` নতুন entries নির্বাচনযোগ্য করে, পুরোনো entries মুছে না। এখন সংশ্লিষ্ট দুই SUT/operator pool-এ দুটি করে site; seed-only selection পুরোনো site-ও বেছে নিতে পারে। Claude-কে explicit `--site market-response-field-v2` / `--site petstore-reject-valid-v2` দিয়ে fresh bundle বানাতে হবে; পুরোনো build-invalid/noise result রয়ে যাবে (`08_experiments/E5_codemut/codemut.py:102–119`; `README.md`, T25 v2 sites)।

৪. Experimental kill ও independent attribution এই task-এ মাপা হয়নি। `expected_L1/L2` injection intent; source count, Python model বা পুরোনো mutant traffic নতুন causal outcome নয় (`08_experiments/E5_codemut/sites.json`, দুই v2 entry; `codemut.py:224–234`)।

## পরিশিষ্ট — সব operation-এর seed/role status counts

নিচে দুই saved bundle-এর প্রত্যেক seed-এ C/M/N/R আলাদা count আছে: ২০টি captured operation/path × ৩ seed × ২ bundle × ৪ role = ৪৮০ row। এর ১৯টি declared operation; GET `/api/v3` readiness/unmapped path-টিও বাদ দেওয়া হয়নি। প্রতিটি cell `row_id: HTTP-status×occurrences`; omitted status-এর count শূন্য। একই cell-এর counts যোগ করলে সংশ্লিষ্ট operation-এর total captured exchanges পাওয়া যায়। প্রতিটি row ID সরাসরি `09_collab/logs/T25_scratch/petstore_operation_counts.csv`-এ resolves, যেখানে original `exchanges` path, physical `lines`, এবং analysis `attribution` path আছে; JSON সংস্করণ `petstore_operation_counts.json`।

### petstore-reject-valid_20261114T114156Z — seed 1

| Operation/path | C: pair control | M: historical mutant | N: noise control | R: control_repeat |
|---|---|---|---|---|
| `DELETE /pet/{petId}` | P0001: 200×39; 400×45 | P0021: 200×41; 400×42 | P0141: 200×40; 400×42 | P0121: 200×40; 400×42 |
| `DELETE /store/order/{orderId}` | P0002: 200×47; 400×53 | P0022: 200×44; 400×56 | P0142: 200×51; 400×49 | P0122: 200×51; 400×49 |
| `DELETE /user/{username}` | P0003: 400×2; 500×98 | P0023: 400×2; 500×98 | P0143: 400×2; 500×98 | P0123: 400×2; 500×98 |
| `GET /api/v3` | P0004: 400×1 | P0024: 400×1 | P0144: 400×1 | P0124: 400×1 |
| `GET /pet/findByStatus` | P0005: 200×12; 400×88 | P0025: 200×12; 400×88 | P0145: 200×12; 400×88 | P0125: 200×12; 400×88 |
| `GET /pet/findByTags` | P0006: 200×86; 400×14 | P0026: 200×78; 400×22 | P0146: 200×86; 400×14 | P0126: 200×85; 400×15 |
| `GET /pet/{petId}` | P0007: 400×17; 404×40 | P0027: 200×1; 400×17; 404×27; 500×12 | P0147: 200×1; 400×19; 404×39 | P0127: 400×19; 404×40 |
| `GET /store/inventory` | P0008: 200×15; 400×8 | P0028: 200×15; 400×8 | P0148: 200×15; 400×8 | P0128: 200×15; 400×8 |
| `GET /store/order/{orderId}` | P0009: 200×1; 400×53; 404×46 | P0029: 200×1; 400×56; 404×43 | P0149: 200×1; 400×49; 404×50 | P0129: 200×1; 400×49; 404×50 |
| `GET /user/login` | P0010: 200×2 | P0030: 200×2 | P0150: 200×2 | P0130: 200×2 |
| `GET /user/logout` | P0011: 200×1 | P0031: 200×1 | P0151: 200×1 | P0131: 200×1 |
| `GET /user/{username}` | P0012: 400×2; 500×98 | P0032: 400×2; 500×98 | P0152: 400×2; 500×98 | P0132: 400×2; 500×98 |
| `POST /pet` | P0013: 200×17; 400×30; 500×56 | P0033: 200×13; 400×41; 500×49 | P0153: 200×13; 400×41; 500×49 | P0133: 200×17; 400×32; 500×54 |
| `POST /pet/{petId}` | P0014: 400×72; 404×28 | P0034: 400×72; 404×28 | P0154: 400×78; 404×22 | P0134: 400×78; 404×22 |
| `POST /pet/{petId}/uploadImage` | P0015: 400×71; 404×29 | P0035: 400×73; 404×27 | P0155: 400×72; 404×28 | P0135: 400×72; 404×28 |
| `POST /store/order` | P0016: 200×27; 400×64; 500×12 | P0036: 200×35; 400×44; 500×24 | P0156: 200×18; 400×67; 500×18 | P0136: 200×15; 400×54; 500×34 |
| `POST /user` | P0017: 200×4; 400×45; 500×54 | P0037: 200×4; 400×45; 500×54 | P0157: 200×4; 400×61; 500×38 | P0137: 200×4; 400×48; 500×51 |
| `POST /user/createWithList` | P0018: 400×57; 500×44 | P0038: 400×50; 500×51 | P0158: 400×59; 500×42 | P0138: 400×54; 500×47 |
| `PUT /pet` | P0019: 200×3; 400×30; 404×14; 500×56 | P0039: 200×3; 400×41; 404×10; 500×49 | P0159: 200×3; 400×41; 404×10; 500×49 | P0139: 200×3; 400×32; 404×14; 500×54 |
| `PUT /user/{username}` | P0020: 400×50; 500×53 | P0040: 400×50; 500×53 | P0160: 400×50; 500×53 | P0140: 400×50; 500×53 |

### petstore-reject-valid_20261114T114156Z — seed 2

| Operation/path | C: pair control | M: historical mutant | N: noise control | R: control_repeat |
|---|---|---|---|---|
| `DELETE /pet/{petId}` | P0041: 200×37; 400×34 | P0061: 200×44; 400×31 | P0181: 200×37; 400×34 | P0161: 200×48; 400×29 |
| `DELETE /store/order/{orderId}` | P0042: 200×53; 400×47 | P0062: 200×50; 400×50 | P0182: 200×53; 400×47 | P0162: 200×53; 400×47 |
| `DELETE /user/{username}` | P0043: 500×100 | P0063: 500×100 | P0183: 500×100 | P0163: 500×100 |
| `GET /api/v3` | P0044: 400×1 | P0064: 400×1 | P0184: 400×1 | P0164: 400×1 |
| `GET /pet/findByStatus` | P0045: 200×5; 400×95 | P0065: 200×5; 400×95 | P0185: 200×5; 400×95 | P0165: 200×5; 400×95 |
| `GET /pet/findByTags` | P0046: 200×83; 400×17 | P0066: 200×86; 400×14 | P0186: 200×82; 400×18 | P0166: 200×86; 400×14 |
| `GET /pet/{petId}` | P0047: 400×25; 404×22 | P0067: 400×25; 404×11; 500×10 | P0187: 200×3; 400×25; 404×19 | P0167: 400×27; 404×21 |
| `GET /store/inventory` | P0048: 200×15; 400×3 | P0068: 200×15; 400×3 | P0188: 200×15; 400×3 | P0168: 200×15; 400×3 |
| `GET /store/order/{orderId}` | P0049: 200×1; 400×47; 404×52 | P0069: 200×1; 400×50; 404×49 | P0189: 200×1; 400×47; 404×52 | P0169: 200×1; 400×47; 404×52 |
| `GET /user/login` | P0050: 200×2 | P0070: 200×2 | P0190: 200×2 | P0170: 200×2 |
| `GET /user/logout` | P0051: 200×1 | P0071: 200×1 | P0191: 200×1 | P0171: 200×1 |
| `GET /user/{username}` | P0052: 500×100 | P0072: 500×100 | P0192: 500×100 | P0172: 500×100 |
| `POST /pet` | P0053: 200×12; 400×44; 500×47 | P0073: 200×12; 400×39; 500×52 | P0193: 200×17; 400×41; 500×45 | P0173: 200×12; 400×44; 500×47 |
| `POST /pet/{petId}` | P0054: 200×1; 400×74; 404×25 | P0074: 400×77; 404×23 | P0194: 200×1; 400×74; 404×25 | P0174: 400×80; 404×20 |
| `POST /pet/{petId}/uploadImage` | P0055: 400×78; 404×22 | P0075: 400×80; 404×20 | P0195: 400×73; 404×27 | P0175: 400×79; 404×21 |
| `POST /store/order` | P0056: 200×24; 400×55; 500×24 | P0076: 200×34; 400×57; 500×12 | P0196: 200×24; 400×60; 500×19 | P0176: 200×15; 400×58; 500×30 |
| `POST /user` | P0057: 200×4; 400×54; 500×45 | P0077: 200×4; 400×56; 500×43 | P0197: 200×4; 400×39; 500×60 | P0177: 200×4; 400×47; 500×52 |
| `POST /user/createWithList` | P0058: 400×54; 500×47 | P0078: 400×57; 500×44 | P0198: 400×60; 500×41 | P0178: 400×66; 500×35 |
| `PUT /pet` | P0059: 200×6; 400×44; 404×6; 500×47 | P0079: 200×6; 400×39; 404×6; 500×52 | P0199: 200×6; 400×41; 404×11; 500×45 | P0179: 200×6; 400×44; 404×6; 500×47 |
| `PUT /user/{username}` | P0060: 400×50; 500×53 | P0080: 400×50; 500×53 | P0200: 400×50; 500×53 | P0180: 400×50; 500×53 |

### petstore-reject-valid_20261114T114156Z — seed 3

| Operation/path | C: pair control | M: historical mutant | N: noise control | R: control_repeat |
|---|---|---|---|---|
| `DELETE /pet/{petId}` | P0081: 200×29; 400×53 | P0101: 200×29; 400×53 | P0221: 200×29; 400×53 | P0201: 200×36; 400×46 |
| `DELETE /store/order/{orderId}` | P0082: 200×44; 400×56 | P0102: 200×44; 400×56 | P0222: 200×40; 400×60 | P0202: 200×48; 400×52 |
| `DELETE /user/{username}` | P0083: 400×2; 500×98 | P0103: 400×2; 500×98 | P0223: 400×2; 500×98 | P0203: 400×2; 500×98 |
| `GET /api/v3` | P0084: 400×1 | P0104: 400×1 | P0224: 400×1 | P0204: 400×1 |
| `GET /pet/findByStatus` | P0085: 200×4; 400×96 | P0105: 200×4; 400×96 | P0225: 200×4; 400×96 | P0205: 200×4; 400×96 |
| `GET /pet/findByTags` | P0086: 200×77; 400×23 | P0106: 400×12; 500×88 | P0226: 200×88; 400×12 | P0206: 200×88; 400×12 |
| `GET /pet/{petId}` | P0087: 200×5; 400×35; 404×20 | P0107: 400×35; 404×14; 500×11 | P0227: 200×3; 400×31; 404×18 | P0207: 200×5; 400×34; 404×20 |
| `GET /store/inventory` | P0088: 200×17; 400×1 | P0108: 200×17; 400×1 | P0228: 200×17; 400×1 | P0208: 200×17; 400×1 |
| `GET /store/order/{orderId}` | P0089: 200×1; 400×56; 404×43 | P0109: 200×1; 400×56; 404×43 | P0229: 200×1; 400×60; 404×39 | P0209: 200×1; 400×52; 404×47 |
| `GET /user/login` | P0090: 200×2 | P0110: 200×2 | P0230: 200×2 | P0210: 200×2 |
| `GET /user/logout` | P0091: 200×1 | P0111: 200×1 | P0231: 200×1 | P0211: 200×1 |
| `GET /user/{username}` | P0092: 400×2; 500×98 | P0112: 400×2; 500×98 | P0232: 400×2; 500×98 | P0212: 400×2; 500×98 |
| `POST /pet` | P0093: 200×16; 400×41; 500×46 | P0113: 200×12; 400×35; 500×56 | P0233: 200×16; 400×38; 500×49 | P0213: 200×24; 400×26; 500×53 |
| `POST /pet/{petId}` | P0094: 400×81; 404×19 | P0114: 400×81; 404×19 | P0234: 200×1; 400×83; 404×16 | P0214: 400×84; 404×16 |
| `POST /pet/{petId}/uploadImage` | P0095: 400×51; 404×49 | P0115: 400×51; 404×49 | P0235: 200×1; 400×56; 404×43 | P0215: 400×51; 404×49 |
| `POST /store/order` | P0096: 200×28; 400×51; 500×24 | P0116: 200×28; 400×51; 500×24 | P0236: 200×28; 400×51; 500×24 | P0216: 200×24; 400×53; 500×26 |
| `POST /user` | P0097: 200×4; 400×47; 500×52 | P0117: 200×4; 400×57; 500×42 | P0237: 200×4; 400×71; 500×28 | P0217: 200×4; 400×57; 500×42 |
| `POST /user/createWithList` | P0098: 400×53; 500×48 | P0118: 400×69; 500×32 | P0238: 400×79; 500×22 | P0218: 400×62; 500×39 |
| `PUT /pet` | P0099: 200×5; 400×41; 404×11; 500×46 | P0119: 200×4; 400×35; 404×8; 500×56 | P0239: 200×3; 400×38; 404×13; 500×49 | P0219: 200×3; 400×26; 404×21; 500×53 |
| `PUT /user/{username}` | P0100: 400×59; 500×44 | P0120: 400×59; 500×44 | P0240: 400×59; 500×44 | P0220: 400×59; 500×44 |

### petstore-response-field_20261114T113954Z — seed 1

| Operation/path | C: pair control | M: historical mutant | N: noise control | R: control_repeat |
|---|---|---|---|---|
| `DELETE /pet/{petId}` | P0241: 200×38; 400×45 | P0261: 200×41; 400×42 | P0381: 200×40; 400×42 | P0361: 200×40; 400×42 |
| `DELETE /store/order/{orderId}` | P0242: 200×45; 400×55 | P0262: 200×44; 400×56 | P0382: 200×51; 400×49 | P0362: 200×51; 400×49 |
| `DELETE /user/{username}` | P0243: 400×2; 500×98 | P0263: 400×2; 500×98 | P0383: 400×2; 500×98 | P0363: 400×2; 500×98 |
| `GET /api/v3` | P0244: 400×1 | P0264: 400×1 | P0384: 400×1 | P0364: 400×1 |
| `GET /pet/findByStatus` | P0245: 200×12; 400×88 | P0265: 200×12; 400×88 | P0385: 200×12; 400×88 | P0365: 200×12; 400×88 |
| `GET /pet/findByTags` | P0246: 200×79; 400×21 | P0266: 200×86; 400×14 | P0386: 200×74; 400×26 | P0366: 200×86; 400×14 |
| `GET /pet/{petId}` | P0247: 400×17; 404×40 | P0267: 200×1; 400×17; 404×39 | P0387: 200×1; 400×19; 404×39 | P0367: 200×1; 400×19; 404×39 |
| `GET /store/inventory` | P0248: 200×15; 400×8 | P0268: 200×15; 400×8 | P0388: 200×15; 400×8 | P0368: 200×15; 400×8 |
| `GET /store/order/{orderId}` | P0249: 200×1; 400×55; 404×44 | P0269: 200×1; 400×56; 404×43 | P0389: 200×1; 400×49; 404×50 | P0369: 200×1; 400×49; 404×50 |
| `GET /user/login` | P0250: 200×2 | P0270: 200×2 | P0390: 200×2 | P0370: 200×2 |
| `GET /user/logout` | P0251: 200×1 | P0271: 200×1 | P0391: 200×1 | P0371: 200×1 |
| `GET /user/{username}` | P0252: 400×2; 500×98 | P0272: 400×2; 500×98 | P0392: 400×2; 500×98 | P0372: 400×2; 500×98 |
| `POST /pet` | P0253: 200×17; 400×32; 500×54 | P0273: 200×13; 400×41; 500×49 | P0393: 200×13; 400×41; 500×49 | P0373: 200×13; 400×41; 500×49 |
| `POST /pet/{petId}` | P0254: 400×75; 404×25 | P0274: 400×72; 404×28 | P0394: 400×78; 404×22 | P0374: 400×78; 404×22 |
| `POST /pet/{petId}/uploadImage` | P0255: 400×69; 404×31 | P0275: 400×73; 404×27 | P0395: 400×74; 404×26 | P0375: 400×74; 404×26 |
| `POST /store/order` | P0256: 200×15; 400×57; 500×31 | P0276: 200×21; 400×58; 500×24 | P0396: 200×29; 400×54; 500×20 | P0376: 200×23; 400×60; 500×20 |
| `POST /user` | P0257: 200×4; 400×45; 500×54 | P0277: 200×4; 400×41; 500×58 | P0397: 200×4; 400×41; 500×58 | P0377: 200×4; 400×51; 500×48 |
| `POST /user/createWithList` | P0258: 400×45; 500×56 | P0278: 400×59; 500×42 | P0398: 400×59; 500×42 | P0378: 400×58; 500×43 |
| `PUT /pet` | P0259: 200×3; 400×32; 404×14; 500×54 | P0279: 200×3; 400×41; 404×10; 500×49 | P0399: 200×3; 400×41; 404×10; 500×49 | P0379: 200×3; 400×41; 404×10; 500×49 |
| `PUT /user/{username}` | P0260: 400×50; 500×53 | P0280: 400×50; 500×53 | P0400: 400×50; 500×53 | P0380: 400×50; 500×53 |

### petstore-response-field_20261114T113954Z — seed 2

| Operation/path | C: pair control | M: historical mutant | N: noise control | R: control_repeat |
|---|---|---|---|---|
| `DELETE /pet/{petId}` | P0281: 200×39; 400×35 | P0301: 200×37; 400×34 | P0421: 200×37; 400×34 | P0401: 200×48; 400×29 |
| `DELETE /store/order/{orderId}` | P0282: 200×48; 400×52 | P0302: 200×53; 400×47 | P0422: 200×53; 400×47 | P0402: 200×53; 400×47 |
| `DELETE /user/{username}` | P0283: 500×100 | P0303: 500×100 | P0423: 500×100 | P0403: 500×100 |
| `GET /api/v3` | P0284: 400×1 | P0304: 400×1 | P0424: 400×1 | P0404: 400×1 |
| `GET /pet/findByStatus` | P0285: 200×5; 400×95 | P0305: 200×5; 400×95 | P0425: 200×5; 400×95 | P0405: 200×5; 400×95 |
| `GET /pet/findByTags` | P0286: 400×17; 500×83 | P0306: 200×82; 400×18 | P0426: 400×25; 500×75 | P0406: 200×82; 400×18 |
| `GET /pet/{petId}` | P0287: 200×1; 400×25; 404×20 | P0307: 200×3; 400×25; 404×19 | P0427: 400×25; 404×22 | P0407: 400×27; 404×21 |
| `GET /store/inventory` | P0288: 200×15; 400×3 | P0308: 200×15; 400×3 | P0428: 200×15; 400×3 | P0408: 200×15; 400×3 |
| `GET /store/order/{orderId}` | P0289: 200×1; 400×52; 404×47 | P0309: 200×1; 400×47; 404×52 | P0429: 200×1; 400×47; 404×52 | P0409: 200×1; 400×47; 404×52 |
| `GET /user/login` | P0290: 200×2 | P0310: 200×2 | P0430: 200×2 | P0410: 200×2 |
| `GET /user/logout` | P0291: 200×1 | P0311: 200×1 | P0431: 200×1 | P0411: 200×1 |
| `GET /user/{username}` | P0292: 500×100 | P0312: 500×100 | P0432: 500×100 | P0412: 500×100 |
| `POST /pet` | P0293: 200×19; 400×39; 500×45 | P0313: 200×18; 400×54; 500×31 | P0433: 200×15; 400×46; 500×42 | P0413: 200×12; 400×40; 500×51 |
| `POST /pet/{petId}` | P0294: 400×78; 404×22 | P0314: 200×1; 400×74; 404×25 | P0434: 200×1; 400×74; 404×25 | P0414: 400×80; 404×20 |
| `POST /pet/{petId}/uploadImage` | P0295: 200×1; 400×72; 404×27 | P0315: 400×78; 404×22 | P0435: 400×78; 404×22 | P0415: 400×79; 404×21 |
| `POST /store/order` | P0296: 200×22; 400×69; 500×12 | P0316: 200×32; 400×57; 500×14 | P0436: 200×34; 400×57; 500×12 | P0416: 200×26; 400×65; 500×12 |
| `POST /user` | P0297: 200×4; 400×37; 500×62 | P0317: 200×4; 400×61; 500×38 | P0437: 200×4; 400×44; 500×55 | P0417: 200×4; 400×44; 500×55 |
| `POST /user/createWithList` | P0298: 400×62; 500×39 | P0318: 400×52; 500×49 | P0438: 400×63; 500×38 | P0418: 400×53; 500×48 |
| `PUT /pet` | P0299: 200×5; 400×39; 404×14; 500×45 | P0319: 200×5; 400×54; 404×13; 500×31 | P0439: 200×5; 400×46; 404×10; 500×42 | P0419: 200×6; 400×40; 404×6; 500×51 |
| `PUT /user/{username}` | P0300: 400×50; 500×53 | P0320: 400×50; 500×53 | P0440: 400×50; 500×53 | P0420: 400×50; 500×53 |

### petstore-response-field_20261114T113954Z — seed 3

| Operation/path | C: pair control | M: historical mutant | N: noise control | R: control_repeat |
|---|---|---|---|---|
| `DELETE /pet/{petId}` | P0321: 200×29; 400×53 | P0341: 200×36; 400×46 | P0461: 200×36; 400×46 | P0441: 200×29; 400×53 |
| `DELETE /store/order/{orderId}` | P0322: 200×44; 400×56 | P0342: 200×48; 400×52 | P0462: 200×48; 400×52 | P0442: 200×44; 400×56 |
| `DELETE /user/{username}` | P0323: 400×2; 500×98 | P0343: 400×2; 500×98 | P0463: 400×2; 500×98 | P0443: 400×2; 500×98 |
| `GET /api/v3` | P0324: 400×1 | P0344: 400×1 | P0464: 400×1 | P0444: 400×1 |
| `GET /pet/findByStatus` | P0325: 200×4; 400×96 | P0345: 200×4; 400×96 | P0465: 200×4; 400×96 | P0445: 200×4; 400×96 |
| `GET /pet/findByTags` | P0326: 200×81; 400×19 | P0346: 200×88; 400×12 | P0466: 200×88; 400×12 | P0446: 200×75; 400×25 |
| `GET /pet/{petId}` | P0327: 200×5; 400×35; 404×20 | P0347: 200×5; 400×34; 404×20 | P0467: 200×5; 400×34; 404×20 | P0447: 200×4; 400×35; 404×20 |
| `GET /store/inventory` | P0328: 200×17; 400×1 | P0348: 200×17; 400×1 | P0468: 200×17; 400×1 | P0448: 200×17; 400×1 |
| `GET /store/order/{orderId}` | P0329: 200×1; 400×56; 404×43 | P0349: 200×1; 400×52; 404×47 | P0469: 200×1; 400×52; 404×47 | P0449: 200×1; 400×56; 404×43 |
| `GET /user/login` | P0330: 200×2 | P0350: 200×2 | P0470: 200×2 | P0450: 200×2 |
| `GET /user/logout` | P0331: 200×1 | P0351: 200×1 | P0471: 200×1 | P0451: 200×1 |
| `GET /user/{username}` | P0332: 400×2; 500×98 | P0352: 400×2; 500×98 | P0472: 400×2; 500×98 | P0452: 400×2; 500×98 |
| `POST /pet` | P0333: 200×24; 400×30; 500×49 | P0353: 200×16; 400×47; 500×40 | P0473: 200×15; 400×41; 500×47 | P0453: 200×13; 400×37; 500×53 |
| `POST /pet/{petId}` | P0334: 400×81; 404×19 | P0354: 400×84; 404×16 | P0474: 400×84; 404×16 | P0454: 200×1; 400×82; 404×17 |
| `POST /pet/{petId}/uploadImage` | P0335: 400×51; 404×49 | P0355: 400×51; 404×49 | P0475: 400×51; 404×49 | P0455: 400×52; 404×48 |
| `POST /store/order` | P0336: 200×18; 400×54; 500×31 | P0356: 200×28; 400×51; 500×24 | P0476: 200×28; 400×51; 500×24 | P0456: 200×28; 400×51; 500×24 |
| `POST /user` | P0337: 200×4; 400×43; 500×56 | P0357: 200×4; 400×57; 500×42 | P0477: 200×4; 400×57; 500×42 | P0457: 200×4; 400×49; 500×50 |
| `POST /user/createWithList` | P0338: 400×64; 500×37 | P0358: 400×60; 500×41 | P0478: 400×70; 500×31 | P0458: 400×58; 500×43 |
| `PUT /pet` | P0339: 200×3; 400×30; 404×21; 500×49 | P0359: 200×6; 400×47; 404×10; 500×40 | P0479: 200×3; 400×41; 404×12; 500×47 | P0459: 200×5; 400×37; 404×8; 500×53 |
| `PUT /user/{username}` | P0340: 400×59; 500×44 | P0360: 400×59; 500×44 | P0480: 400×59; 500×44 | P0460: 400×59; 500×44 |

