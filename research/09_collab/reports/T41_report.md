**T41 — Future-version oracle: upstream SPEC বদলেছে, না CODE?**

৬২টি baseline item-এর মধ্যে **৩টিতে developer direction পাওয়া গেছে: সবই `spec_changed_to_match_code`**, দুটি upstream commit থেকে। P014-এর একটি witness সম্পূর্ণভাবে এই পরিবর্তনের আওতায়; P015 ও C002-তে cluster-এর কেবল অংশের জন্য evidence আছে। `code_changed_to_match_spec` বা `both_changed` পাওয়া যায়নি। এই তিনটির direction বনাম বর্তমান `final_L1` মিল **২/৩**; একমাত্র disagreement **P014: developer SPEC দিকে পরিবর্তন করেছে, final label IMPL**। Labels অপরিবর্তিত; শুধু review proposal লেখা হয়েছে। সূত্র: `08_experiments/E4_triage/future_oracle/{summary.json,agreement.csv,review_proposals.csv}`, item P014/P015/C002।

⚠️ এখানে “future” মানে **EMB source anchor-এর পরের upstream history**। Fix-দুটি 2021 ও 2025-এর, baseline experiment November 2026-এর; এটি experiment-এর পরে developer-এর প্রতিক্রিয়া নয়। Analysis non-blind: final labels ও adjudication থেকে mismatch proposition নেওয়া হয়েছে। Patch কে কোন report-এর প্রতিক্রিয়ায় করেছে, তার প্রমাণ নেই। সূত্র: `future_oracle/anchors.json`-এর commit dates; `future_oracle/candidate_witnesses.json`-এর baseline run locators; `future_oracle/*_all_descendant_history.json`-এর দুই fix commit। এই report-এ `future_oracle/` বলতে `08_experiments/E4_triage/future_oracle/` বোঝানো হয়েছে।

**কাজের পদ্ধতি ও anchor**

প্রতি EMB file-এর `SHA1("blob " + byte_length + NUL + content)` upstream `ls-tree` blob-এর সঙ্গে মিলিয়েছি। Denominator: `src/`-এর Java, JSON, YAML, XML, properties ও SQL; root/module `pom.xml`, `api-docs.json`, `inflector.yaml`। `target/`, `.git/`, `node_modules/`, generated build output বাদ। সব local ref-এর সব commit score করা হয়েছে; default HEAD-এর ancestor-গুলির সর্বোচ্চ match থেকে anchor নিয়েছি। Tie-গুলিও সংরক্ষিত; primary anchor tie traversal-এর পুরোনো প্রান্তে, যাতে সমান source-এর মাঝের কোনো change বাদ না পড়ে। এটি exact original import commit শনাক্ত করার দাবি নয়। সূত্র: `future_oracle/mine_history.py:relevant,main`, `future_oracle/anchor_scores.csv`, `future_oracle/anchors.json`।

| SUT | anchor, author date | relevant exact match | Java exact match | tied best |
|---|---|---:|---:|---:|
| swagger-petstore | `f1ed336a08b18ba4a86c496147c4f546ae965a7b`, 2025-03-19 | 24/27 = **88.9%** | 22/23 | 2 |
| cwa-verification | `a02110fb8dd960a66f4d359d99c62454b8bc0b79`, 2021-09-07 | 67/71 = **94.4%** | 55/57 | 1 |
| market | `2b690750752a848ed5fdb48006bc2d5e8db97bf1`, 2022-02-06 | 135/139 = **97.1%** | 124/124 | 3 |

Table-এর evidence: `future_oracle/anchors.json`, সংশ্লিষ্ট SUT-এর `matches`, `denominator`, `java_matches`, `java_total`, `tied_best_commits`; সব score `anchor_scores.csv`-এ। কোনো SUT 80%-এর নিচে নয়। Market-এর প্রাথমিক 97.8% হিসাবটিতে SQL ছিল না; final 97.1% scope-এ SQL-ও আছে।

Petstore-এ path alias জরুরি: EMB `src/main/webapp/openapi.yaml` upstream `src/main/resources/openapi.yaml`-এর **একই blob** `1882eca957c5cf17bb97b8d8754bb6f31cad1e5b`। Alias ছাড়া literal-path maximum 23/27 এবং অনেক পরের commit-ও tie হয়; alias দিলে spec-সহ 24/27-এর দুইটি candidate পাওয়া যায়। দ্বিতীয়টি `0f0761b71b849c96b0425ea3796b8fb3aaa129e6`; relevant state একই। তিন SUT-এর baseline run `spec.original.json` supplied deployed JSON-এর সঙ্গে semantic equality পাস করেছে। CWA deployed JSON ও anchored `api-docs.json` byte-identical। সূত্র: `future_oracle/{anchors.json,anchor_scores.csv,spec_provenance.json}`। Petstore-এর JSON/YAML-এর সম্পূর্ণ byte বা parsed-tree equality দাবি করা হয়নি; YAML relocation-এর blob equality ও item-specific constraint correspondence ব্যবহার করেছি।

EMB-local differences-এর সম্পূর্ণ hash-only inventory `future_oracle/*_file_inventory.json`-এ। Relevant patches `*_emb_local.diff`-এ; নিচের তালিকায় non-build inventory-এর সব non-exact path আছে। Market README/seed SQL-এর values প্রকাশ বা copy করা হয়নি। সূত্র: `future_oracle/{swagger-petstore,cwa-verification,market}_file_inventory.json`, `future_oracle/local_modification_audit.json`।

| SUT | modified upstream paths | EMB-only paths |
|---|---|---|
| petstore | `inflector.yaml`, `pom.xml` | `dependency-reduced-pom.xml`; `src/main/java/io/swagger/petstore/Main.java`; `src/main/webapp/swagger-ui-bundle.js`, `swagger-ui-standalone-preset.js`, `swagger-ui.css` |
| CWA | `pom.xml`; `src/main/java/app/coronawarn/verification/controller/InternalTestStateController.java`; `src/main/resources/db/changelog/v000-create-app-session-table.yml` | `src/main/java/app/coronawarn/verification/config/IdeConfig.java` |
| market | `README.adoc`; `market-core/src/main/resources/data.sql`; `market-rest/pom.xml`; `market-web/pom.xml`; `pom.xml` | `Project.xml`, `codeStyleConfig.xml`, `codeStyles/Project.xml`, `codeStyles/codeStyleConfig.xml` |

Petstore `inflector.yaml` নতুন webapp spec path ব্যবহার করে; EMB POM ও অতিরিক্ত `Main.java` Tomcat bootstrap/package layout বদলায়। CWA-তে internal test-state controller-এর profile নিষ্ক্রিয় করা, local config এবং packaging পরিবর্তন আছে; changelog-এর পার্থক্য **শুধু CRLF/LF**। Market Java files হুবহু মেলে, তবে packaging ও seed data মেলে না। ⚠️ তাই transport বা state-dependent behaviour-এর ক্ষেত্রে high overall match-কে deployed execution-এর সমতা ধরা হয়নি। সূত্র: `future_oracle/*_emb_local.diff`, `future_oracle/local_modification_audit.json`, EMB `jdk_8_maven/cs/rest/original/swagger-petstore/src/main/java/io/swagger/petstore/Main.java`।

**Deployed spec-এর উৎস ও generated-spec সীমা**

Petstore design-first YAML ব্যবহার করে: `inflector.yaml`-এর `swaggerUrl` তার source; controller/model annotations-কে আলাদা generated spec-এর authority হিসেবে ধরা হয়নি। CWA-তে checked-in `api-docs.json` আছে, কিন্তু Springdoc ও Java `@Schema`, validation annotations এবং `@ApiResponse` তার generated উৎসের অংশ। Market-এ Springfox `Docket(DocumentationType.SWAGGER_2)` route/DTO থেকে spec বানায়; deployed `market.json`-এর upstream checked-in counterpart anchor tree-তে পাওয়া যায়নি। সূত্র: `future_oracle/spec_origins.json`; petstore anchor `inflector.yaml:3`; CWA anchor `pom.xml:85`, `src/main/java/app/coronawarn/verification/model/RegistrationTokenRequest.java:35`; market anchor `market-rest/src/main/java/market/RestConfig.java:17`, `market-rest/pom.xml:42`। Full SHA-সহ marker `spec_origins.json:generator_markers`-এ।

Generated spec-এ annotation edit হলে সেটি code file-এর **spec-facing change**; handler logic পরিবর্তন আলাদা করে দেখতে হবে। এই sample-এর C002 commit শুধু saved JSON বদলেছে: **spec artifact=true, annotations=false, matching handler logic=false**। সংশ্লিষ্ট `@NotNull` ও `@Pattern` আগেই ছিল। তাই এটিকে code fix বা BOTH বলা হয়নি। ⚠️ এটি stale generated artifact পুনরায় export করার incidental ফলও হতে পারে; developer issue-confirmation হিসেবে বাড়তি দাবি করিনি। Market HEAD-এর নতুন spec generate/export করিনি। সূত্র: `future_oracle/item_history.json:C002`; `history_diffs/cwa-verification/40bd3a829f42e50a1dd764b4fa657a427bf32ef6.diff`; anchor/HEAD `RegistrationTokenRequest.java` copies in `future_oracle/source_evidence/`।

**History coverage ও তিনটি usable direction**

| SUT | local refs-এ মোট commits | default HEAD-এ মোট | anchor-এর পরে default HEAD | সব ref-এ anchor descendants |
|---|---:|---:|---:|---:|
| petstore | 258 | 121 | 21 | 28 |
| CWA | 211 | 211 | 37 | 37 |
| market | 121 | 119 | 4 | 5 |

সব descendant-এর file touches ও relevant patches দেখা হয়েছে; প্রতিটি item-এর spec/handler/DTO/validation/exception/dependency path-এর candidate list `future_oracle/item_history.json:<item_id>`-এ। Default HEAD-এর বাইরে petstore-এর সাতটি descendant build/dependency changes; market-এর একটি PostgreSQL update। এগুলিতে targeted repair পাওয়া যায়নি। Petstore ও market-এর post-anchor descendant history-তে Java file touch শূন্য। সূত্র: `future_oracle/anchors.json`-এর history bounds/ref metadata; `future_oracle/*_all_descendant_history.json`-এর `selected_files`, `in_default_head`; `future_oracle/history_diffs/`।

**P014 — status অনুপস্থিত থাকলেও 400।** Deployed spec: `status` optional, default `available`; representative exchange 208-এ parameter অনুপস্থিত এবং response `No status provided`। Upstream commit **`9fb97b14d3c9d15d99aa8e3dbe323284cceb6bee`**, author 2025-08-01, committer **2025-08-04**, message: “Change status/tag to required param for findbystatus/findbytag endpoints”। YAML `required: false → true`; handler-এর null guard অপরিবর্তিত। Direction **SPEC**, confidence **3**; একমাত্র witness-এর proposition covered। HEAD-এও `required: true`, default `available` এবং সেই guard আছে। সূত্র: commit `src/main/resources/openapi.yaml:131`; HEAD `5cb909fc7780bc708151bce0014939acba8b212a:src/main/java/io/swagger/petstore/controller/PetController.java:51`; `future_oracle/candidate_witnesses.json:P014`; `future_oracle/future_oracle.csv:P014`।

**P015 — tags অনুপস্থিত/empty হলে 400।** একই commit-এর YAML `src/main/resources/openapi.yaml:173`-এ `tags` required হয়েছে। Existing guard null বা empty list-এ 400 দেয়। Direction **SPEC**, confidence **3** সম্পর্কে নিশ্চিত, কিন্তু **partial cluster evidence**: ৫ witness-এর ২টিতে parameter নেই; ৩টিতে parameter আছে, তবুও guard rejection। HEAD array-তে `minItems` যোগ হয়নি। ⚠️ `required` একাই present-empty serialization-এর বাকি তিনটি মেরামত করেছে বলা যায় না। সূত্র: একই full SHA-এর YAML line 173; HEAD `5cb909fc7780bc708151bce0014939acba8b212a:src/main/java/io/swagger/petstore/controller/PetController.java:234`; `future_oracle/candidate_witnesses.json:P015` (exchange 212, 213, 214, 220, 265)।

**C002 — registration request-এর constraints stale spec-এ নেই।** Commit **`40bd3a829f42e50a1dd764b4fa657a427bf32ef6`**, **2021-11-19**, message: “feat: update openAPI to match version 1.5.0 (#247)”। Saved JSON-এ `RegistrationTokenRequest.required=[key,keyType]` এবং `keyDob.pattern` যোগ হয়েছে; এগুলি আগের Java validation-এর সঙ্গে মেলে। Direction **SPEC**, confidence **2**, ⚠️ regeneration/partial coverage। Commit-এর `api-docs.json:384` required fields এবং line 394 pattern দেখায়; Java constraints anchor ও HEAD-এ একই। সূত্র: `future_oracle/cwa_spec_semantic_delta.json`-এর `/components/schemas/RegistrationTokenRequest` entries; `future_oracle/item_history.json:C002`; CWA HEAD `bbc28be761c89bdda30f761f79f3a190e4c3a7c6:src/main/java/app/coronawarn/verification/model/RegistrationTokenRequest.java:46` এবং `:52`।

C002-র ৬৯ witness-এর ৫৬টিতে required field অনুপস্থিত; null-only required case শূন্য। নতুন required/pattern predicate মিলিয়ে ৬১টিকে spec আগেই invalid বলতে পারত; এই ৬১টির মধ্যে সাতটিতে illegal header control-ও আছে। ফলে **৫৪/৬৯ transport-clean witness** নতুন predicate-এর আওতায়। বাকি আটটিতে required ও `keyDob` predicate যথেষ্ট নয়; conditional `key` validation spec-এ এখনও নেই। ⚠️ এগুলি static constraint checks, server rerun নয়; partial evidence থেকে পুরো cluster মেরামতের দাবি করা হয়নি। সূত্র: `future_oracle/candidate_witnesses.json:C002`, counts ও per-exchange boolean features; extraction `future_oracle/collect_evidence.py:candidates`।

**যেগুলিতে usable direction পাওয়া যায়নি**

| recorded direction | n | ব্যাখ্যা |
|---|---:|---|
| `unchanged_at_head` | 31 | target predicate/source-এ matching repair নেই; static HEAD state প্রতিটি CSV row-তে |
| `changed_unrelated` | 1 | C005: document/migration changes হয়েছে, exact 404 body mismatch রয়ে গেছে |
| `unclear` | 27 | 25টি original TEST item; আরও P037/P039-এর deployment-specific transport correspondence unresolved |
| `spec_changed_to_match_code` | 3 | উপরের P014/P015/C002 |
| `code_changed_to_match_spec` / `both_changed` | 0 / 0 | targeted evidence পাওয়া যায়নি |

Count evidence: `future_oracle/{summary.json,future_oracle.csv}`। **`unchanged_at_head` মানে observed source/artifact predicate unchanged; নতুন runtime-এ defect পুনরুৎপাদন হয়েছে নয়।** Dependency/container drift-এর প্রভাব চলমান server ছাড়া যাচাই করা হয়নি। প্রতিটি row-তে `HEAD <full_sha>` state ও source locator আছে; market-এ generated HEAD spec পাওয়া গেছে এমন দাবি করা হয়নি।

৩১টি unchanged item: petstore **P005/P006/P011/P012/P013/P018/P019/P021/P026/P027/P031/P032/P033/P034/P035/P036/P038/P042/P043**, market **M002–M013**। Photo URL omission, nullable-id/user data flow, arbitrary status, missing optional body/file/list, raw login JSON, HAL parse/overflow-to-500 এবং omitted validation-406—এই target-গুলির source অবস্থান অপরিবর্তিত। P013-এর operation-এ P014-এর spec edit ঘটলেও photoUrls response proposition মেরামত হয়নি। ⚠️ 500-এর কয়েকটি per-request throwing-site আগের labeller evidence থেকেই inferred; history দিয়ে নতুন stack trace বানানো হয়নি। সূত্র: `future_oracle/item_history.json` ও `future_oracle/future_oracle.csv`, উল্লিখিত item ids; anchored/HEAD text ও blobs `future_oracle/source_index.json`।

C005-এ `40bd3a8…` অন্য responses/headers refresh করেছে, কিন্তু `tan/verify`-এর **404 object schema অপরিবর্তিত**। `e8046d3a2a04475b95b8bf57d324ab8f8b0b4971` (2023-03-16, “Chore: Update CWA-Parent to 2.0.2 (#286)”) Jakarta/import/refactor touch করেছে; exception handler এখনও body ছাড়া response বানায়। তাই ⚠️ incidental touches-কে fix direction করিনি। HEAD locators: `bbc28be761c89bdda30f761f79f3a190e4c3a7c6:api-docs.json:183`, একই SHA `src/main/java/app/coronawarn/verification/controller/VerificationExceptionHandler.java:94`। Semantic 404 equality ও candidate patches: `future_oracle/item_history.json:C005`, `future_oracle/cwa_spec_semantic_delta.json`, `future_oracle/history_diffs/cwa-verification/`।

২৭ unclear item-কে “upstream defect unchanged” বলা হয়নি। Request-body coverage diagnostic **P002–P004/P007–P010/P020/P023–P025/P028–P030/P040–P041**, setup probe **P001/C001/M001**, int64-checker gap **P016/P017**, invalid transport **P022**, missing-session precondition **C003/C006**, header-serialization coverage **C004**—এই ২৫টি final TEST। **P037/P039**-এ EMB Tomcat ও upstream Jetty correspondence অযাচাইকৃত। সূত্র: `future_oracle/baseline_evidence.json`-এর সংশ্লিষ্ট adjudication/codex evidence; `future_oracle/future_oracle.csv`-এর proposition/notes।

**Final labels-এর সঙ্গে agreement ও review proposal**

| developer direction | final SPEC | final SPEC_PARTIAL | final IMPL | final BOTH | অন্য final | মোট |
|---|---:|---:|---:|---:|---:|---:|
| spec_changed_to_match_code | 1 | 1 | 1 | 0 | 0 | 3 |
| code_changed_to_match_spec | 0 | 0 | 0 | 0 | 0 | 0 |
| both_changed | 0 | 0 | 0 | 0 | 0 | 0 |

Mapping অনুযায়ী P015=SPEC ও C002=SPEC_PARTIAL agreement; P014=IMPL disagreement। `changed_unrelated`-এর কোনো SPEC/IMPL/BOTH mapping নেই, তাই C005 comparison denominator-এ নেই; unchanged/unclear-ও নেই। Evidence: `future_oracle/agreement.csv` rows P014/P015/C002; `future_oracle/assess_items.py:MAPPING`।

**একমাত্র review proposal: P014।** Upstream required parameter করে original missing-status behaviour-এর সঙ্গে spec মেলিয়েছে; তাই E-DEV/E-HISTORY direction SPEC। বর্তমান IMPL adjudication original optional parameter-এর documented default-কে server promise ধরেছে। ⚠️ দুটো বক্তব্য একই ইতিহাসে সম্ভব: developer spec-এর promise বদলে repair বেছে নিতে পারে, অথচ original implementation তখনও original promise ভেঙেছিল। ফলে স্বয়ংক্রিয় IMPL→SPEC relabel প্রস্তাব করছি না; original-contract attribution বনাম later repair-side distinction adjudication-এ লিখে direction-compatible view বিবেচনার প্রস্তাব। সূত্র: `08_experiments/E2_labelling/swagger-petstore_adjudication.csv:P014`, `future_oracle/review_proposals.csv:P014`, codebook `08_experiments/R1_triage_codebook.md:42–44` এবং targeted upstream YAML patch।

**Yield, E6 ও threats**

Primary usable-direction yield **3/62 = 4.84%**, কিন্তু স্বাধীন fix commit মাত্র **2**। Confidence-3 directional items দুইটি, একই petstore commit-এর; তার একটিতে partial cluster coverage। পুরো observed cluster-এর predicate cover করে একমাত্র P014: **1/62 = 1.61%**। কোনো usable IMPL/BOTH example নেই। ⚠️ তাই ২/৩ agreement-কে general accuracy, balanced ground truth বা triage-method ranking হিসেবে ব্যবহার করা যাবে না। সূত্র: `future_oracle/summary.json`, `future_oracle/agreement.csv`, `future_oracle/candidate_witnesses.json`।

⚠️ E6-তে এই oracle **supplementary historical evidence** হিসেবে scale করতে পারে; এই তিন repo দিয়ে standalone balanced evaluation পাওয়া যায়নি। Matching blobs, path aliases, JSON Pointer delta, annotation/handler separation এবং candidate path indexing automated করা যায়; exact proposition-to-patch linkage ও partial witness coverage-তে manual review দরকার। Task-এর স্বল্প yield এবং বর্তমান script-এর explicit manual assessment table এই সীমার প্রমাণ। সূত্র: `future_oracle/{mine_history.py,collect_evidence.py,assess_items.py,summary.json}`।

- **Survivorship / right censoring:** ⚠️ শুধু surviving clone ও merged/retained history থেকে fix দেখা যায়; unreported, unfixed বা branch-deleted defect বাদ পড়বে। 31 static unchanged-কে correct/incorrect label হিসেবে ব্যবহার করা যাবে না। এই sample-এ market default HEAD-এ মাত্র চার post-anchor commit এবং কোনো Java touch নেই। সূত্র: `future_oracle/anchors.json:market`, `market_all_descendant_history.json`।
- **Spec regeneration:** CWA refresh real saved-spec correction, কিন্তু annotation edit নয়; C005-এর একই refresh target mismatch রাখে। ⚠️ Generated file বদলকে code fix বা একসঙ্গে BOTH ধরলে false direction হবে। Runtime generator/dependency upgrade-এর প্রভাবও source-only analysis পুরো মাপে না। সূত্র: `history_diffs/cwa-verification/40bd3a829f42e50a1dd764b4fa657a427bf32ef6.diff`, `item_history.json:C002,C005`।
- **Squash/merge ও date:** ⚠️ এক commit এক defect নয়, আর author/committer dates আলাদা হতে পারে; petstore এক commit-এ দুই parameter ও whitespace বদলেছে। Search ancestry দিয়ে সীমাবদ্ধ, wall-clock date alone দিয়ে নয়; merge history ও alternate ref screening retained আছে। সূত্র: `swagger-petstore_all_descendant_history.json:9fb97b14…`, `history_diffs/swagger-petstore/9fb97b14d3c9d15d99aa8e3dbe323284cceb6bee.diff`, `anchors.json`।
- **Archived/inactive repos:** CWA local HEAD 2023-04-12, market default HEAD 2024-02-22। ⚠️ Maintenance বন্ধ থাকলে unchanged evidence-এর probability বাড়ে; archive status নিজে offline Git দিয়ে independently যাচাই হয়নি। Market-এর retained dependency branch 2026-এর হওয়াও default handler maintenance প্রমাণ করে না। সূত্র: `anchors.json`-এর HEAD dates/ref tips; `market_all_descendant_history.json:38ad764b99d8210fd90cd1d09388299a695422a3`।
- **Anchor/deployment ও construct validity:** EMB-local container/seed patches, runtime-generated HEAD spec না পাওয়া, original labels দেখা, এবং later repair-side বনাম original blame আলাদা হওয়া—সবই oracle-এর সীমা। ⚠️ E6-তে released-version interval, archived/censored status, operation-level proposition, cluster coverage এবং developer-confirmation strength আলাদা metadata রাখতে হবে; একই commit-এর items-কে স্বাধীন sample ধরা উচিত নয়। সূত্র: `*_file_inventory.json`, `local_modification_audit.json`, `candidate_witnesses.json`, `agreement.csv:P014`।

**Deliverables, যাচাই ও বাকি review**

`future_oracle.csv`-তে exact 62 item, requested নয়টি column; `anchors.json`, reproducible mining/collection/assessment/verification scripts, per-item search trails, inert source excerpts, patches, witness features, agreement ও proposal দেওয়া হয়েছে। পুনরায় চালানোর commands ও direction/confidence definitions `future_oracle/README.md`-এ। Input hashes, full-SHA locators, anchor maxima, positive predicate edits, unchanged Java trees, CWA annotation/404 semantics, coverage counts ও credential-output scan-এর ফল `future_oracle/verification.json` এবং `09_collab/logs/T41_scratch/`-এ।

কোনো external code, upstream script, Docker, Java, Maven, build বা network চালানো হয়নি; শুধু whitelist করা read-only Git verbs ও আমাদের `/usr/bin/python3 -I -B` scripts। Blind package/key content খোলা হয়নি। শুরুতে explicit `E2_labelling` path-এর filename-only discovery-তে forbidden child directory-র কয়েকটি filename surfaced হয়েছিল; তারপর exact baseline files-এ retrieval সীমাবদ্ধ ছিল। Filename exposure-কে content access বা evidence হিসেবে ব্যবহার করা হয়নি। Market README/HTML credential quote করা হয়নি; header values output হয়নি। Execution boundary: `mine_history.py:git`, script inputs ও output manifests; task constraint: `09_collab/tasks/T41.md`। একটি JSONL extraction bug ঠিক করা হয়েছে: Unicode line-separator ভাঙা ঠেকাতে `splitlines()`-এর বদলে `split("\n")`; পরে exact occurrence counts পাস করেছে (`collect_evidence.py:candidates`, `verification.json`)।

Outstanding review: (১) P014-এ original fault attribution এবং observed repair direction আলাদা annotation গ্রহণ করা হবে কি না; (২) E6 sampling unit পুরো fingerprint হবে, না independently repaired proposition/witness subset হবে। ⚠️ বর্তমান sparse/partial yield দ্বিতীয় unit-এর প্রয়োজন দেখায়, কিন্তু task-এর 62-row baseline labels কোনোটি পরিবর্তন করা হয়নি। সূত্র: `future_oracle/{review_proposals.csv,summary.json,candidate_witnesses.json}`।
