# T14 — Multi-SUT harness v2: হস্তান্তর প্রতিবেদন

## কাজের পরিধি ও অবস্থা

T14-এর write-only deliverable প্রস্তুত: `scout-api`, `swagger-petstore`, ও `market`-এর জন্য নতুন `harness_v2/`, per-SUT config, generalized preparation/run/batch/analysis, OpenAPI 3 derecursion ও unit tests, exact execution commands এবং প্রথম execution-এর যাচাইতালিকা। এটি script/static-validation পর্যায়ের সমাপ্তি; নতুন SUT execution-এর ফল দাবি করা হচ্ছে না। প্রমাণ: `09_collab/tasks/T14.md:1–20`; `08_experiments/E1_pilot/harness_v2/README.md:1–97`; `08_experiments/E1_pilot/harness_v2/static_checks.txt:2–39`।

বর্তমান `harness/`-এর দশটি non-hidden file-এর SHA-256 শুরুতে সংরক্ষণ করে পরে মিলিয়ে দেখা হয়েছে—সব অপরিবর্তিত। Docker, Compose, Java, Schemathesis, SUT, network download, dependency installation বা tool pipeline চালানো হয়নি। প্রমাণ: `08_experiments/E1_pilot/harness_v2/source-harness-sha256.json:1–12`; `08_experiments/E1_pilot/harness_v2/static_checks.txt:17,39`।

## কী করা হয়েছে

### ১. SUT configuration ও preparation

প্রতিটি non-secret `suts/<sut>.env`-এ built jar source, Compose/Dockerfile path, service, internal port, readiness/base path, auth role/source, spec source ও নির্দিষ্ট image tag আছে। Common loader শুধু তিনটি অনুমোদিত নাম গ্রহণ করে। প্রমাণ: `08_experiments/E1_pilot/harness_v2/common.sh:3–15`; `08_experiments/E1_pilot/harness_v2/suts/scout-api.env:2–14`; `08_experiments/E1_pilot/harness_v2/suts/swagger-petstore.env:2–14`; `08_experiments/E1_pilot/harness_v2/suts/market.env:2–14`।

| SUT | Config-এর default | Static spec পর্যবেক্ষণ | প্রমাণ |
|---|---|---|---|
| scout-api | internal 8080; base `/api`; ⚠️ health `/admin/healthcheck`; role `administrator`; image `r1-scout-api-sut:pilot` | Swagger 2.0; 49 declared operations | `harness_v2/suts/scout-api.env:2–14`; `harness_v2/static_checks.txt:13` |
| swagger-petstore | internal 8080; ⚠️ base `/api/v3`; ⚠️ health `/api/v3/openapi.json`; role `none`; image `r1-swagger-petstore-sut:pilot` | OpenAPI 3.0.4; 19 declared operations | `harness_v2/suts/swagger-petstore.env:2–14`; `harness_v2/static_checks.txt:14` |
| market | internal 8080; base `/`; ⚠️ health `/v2/api-docs`; role `user`; image `r1-market-sut:pilot` | Swagger 2.0; 13 declared operations | `harness_v2/suts/market.env:2–14`; `harness_v2/static_checks.txt:15` |

সারণির `harness_v2/` prefix-এর পূর্ণ path হলো `08_experiments/E1_pilot/harness_v2/`; operation সংখ্যা spec-এর declaration গণনা, runtime coverage নয়। গণনার implementation: `08_experiments/E1_pilot/harness_v2/static_validate.py:76–78`।

`prepare_dist.sh <sut>` নির্বাচিত built jar-টি `EMB/dist/`-এ পরিবর্তিত হলে copy করে; JaCoCo 0.8.12 agent/CLI-এর HTTPS download ও Maven SHA-1 verification রেখে দেওয়া হয়েছে। Execution হলে preparation ও run একই v2 lock ব্যবহার করবে; পুরোনো harness-এর বিদ্যমান lock file read-only খুলে তার lock-ও নেবে। T14-তে এসব operational action চালানো হয়নি। প্রমাণ: `08_experiments/E1_pilot/harness_v2/prepare_dist.sh:5–51`; `08_experiments/E1_pilot/harness_v2/common.sh:17–25`; `08_experiments/E1_pilot/harness_v2/static_checks.txt:39`।

### ২. Batch 1-এর প্রয়োজনীয় fixes সংরক্ষণ

- তিন Compose override-এ সরাসরি `mitmdump` entrypoint, সঠিক SUT upstream, host UID/GID ও full logger mount আছে। Original Compose-এর port interpolation-এ host binding `127.0.0.1:18080` ও `127.0.0.1:16300` দেওয়া হয়। প্রমাণ: `08_experiments/E1_pilot/harness_v2/compose.override.scout-api.yaml:1–34`; `08_experiments/E1_pilot/harness_v2/compose.override.swagger-petstore.yaml:1–34`; `08_experiments/E1_pilot/harness_v2/compose.override.market.yaml:1–34`; `08_experiments/E1_pilot/harness_v2/common.sh:13–14`।
- SUT-এর fixed tag থাকলে `--no-build`, না থাকলে প্রথম build; pinned Schemathesis 3.39.16, configurable `SCHEMA_CHECKS`, default request timeout 10000 ms, এবং `explicit,generate` phases রেখে shrinking বন্ধ রাখা হয়েছে। প্রমাণ: `08_experiments/E1_pilot/harness_v2/run_pilot.sh:24–32,127–141,170–173`।
- Oracle spec-এর snapshot আলাদা থাকে। Baseline generator input `derecurse(original)`; mutated generator input `specmut(derecurse(original))`; দুই mutation manifest-এর `(path, method)` list সমান না হলে abort। একই snapshotted original থেকে দুই pass চালানো হয়। প্রমাণ: `08_experiments/E1_pilot/harness_v2/run_pilot.sh:111–125,176–191`।
- `flock`, unique Compose project, exclusive run directory, readiness traffic quarantine, JVM বন্ধের আগে JaCoCo dump ও scoped cleanup রাখা হয়েছে। ব্যর্থ/অসম্পূর্ণ run-এর জায়গায় নতুন run লেখা হয় না। প্রমাণ: `08_experiments/E1_pilot/harness_v2/common.sh:17–25`; `08_experiments/E1_pilot/harness_v2/run_pilot.sh:57–108,150–168,208–214`।

### ৩. Authentication ও provenance

Scout ও market-এর fixed Authorization header execution-এর সময় EMB YAML থেকে নির্বাচিত role অনুযায়ী পড়া হবে; parser error-এ credential content echo করা হয় না। Petstore-এর জন্য কোনো header যোগ হয় না। `run.json`-এ role/source/digest লেখা হয়; header value লেখা হয় না। Non-secret config snapshot ও provenance-এ public role identifiers অক্ষত রাখার জন্য redactor-এর explicit exclusion আছে। প্রমাণ: `08_experiments/E1_pilot/harness_v2/auth_header.py:8–30`; `08_experiments/E1_pilot/harness_v2/run_pilot.sh:33–52,192–202`; `08_experiments/E1_pilot/harness_v2/redact_auth.py:25–39`; `08_experiments/E1_pilot/harness_v2/run_metadata.py:43–53`।

Market-এ default `user` বাছাইয়ের source-level কারণ `/customer**`-এ `ROLE_USER` requirement। ⚠️ এটি fixture সফলভাবে authenticate হওয়ার runtime প্রমাণ নয়। প্রমাণ: `08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market/market-rest/src/main/java/market/RestSecurityConfig.java:9–17`; `08_experiments/E1_pilot/harness_v2/suts/market.env:11–12`।

Provenance-এ image IDs/digests, EMB commit/status, jar/agent/CLI hashes, check choice, timeout/phases, recursive harness/config hashes ও artifact hashes আছে। Analysis incomplete বা incompatible pair, ভিন্ন image/check/config, বদলানো input এবং current tool/harness drift প্রত্যাখ্যান করে। প্রমাণ: `08_experiments/E1_pilot/harness_v2/run_metadata.py:20–74`; `08_experiments/E1_pilot/harness_v2/analyse_run.sh:13–50`।

### ৪. Batch ও analysis interface

`run_batch.sh <sut> [seeds…]` default-এ seeds 1,2,3 নেয়; প্রত্যেকটির baseline ও চার fault class চালানোর script প্রস্তুত। Budget, severity, maximum examples ও checks environment থেকে নেওয়া যায়। Pairing-এর জন্য এই batch-এর exact run IDs ব্যবহার হয়; আগের directory glob থেকে baseline/mutant বাছাই হয় না। ব্যর্থ run বা analysis-এ batch থামে। প্রমাণ: `08_experiments/E1_pilot/harness_v2/run_batch.sh:3–47`।

Runs-এর location `E1_pilot/runs/<sut>/`; batch index `batches/<batch_id>/runs.tsv`। `analyse_run.sh MUTATED_RUN BASELINE_RUN [--mode both|fresh|replay]` metadata থেকে allowlisted SUT শনাক্ত করে এবং mode-specific output overwrite করে না। Fresh ও replay উভয় ক্ষেত্রেই conformance checker `spec.test.*` ব্যবহার করে। প্রমাণ: `08_experiments/E1_pilot/harness_v2/run_batch.sh:24–37`; `08_experiments/E1_pilot/harness_v2/analyse_run.sh:5–11,59–75`।

### ৫. OpenAPI 3 derecursion ও tests

আগের helper basename দিয়ে ref শনাক্ত করত এবং `definitions` অথবা `components/schemas`-এর একটিকে নিত। নতুন helper দুই namespace একসঙ্গে, পূর্ণ escaped pointer দিয়ে শনাক্ত করে; deterministic DFS-এ back edge কাটে; input deep-copy করে এবং cut-এর নির্দিষ্ট pointer সংরক্ষণ করে। Object replacement policy আগের মতো রাখা হয়েছে। প্রমাণ: `08_experiments/E1_pilot/harness/derecurse.py:19–64`; `08_experiments/E1_pilot/harness_v2/derecurse.py:13–64`।

১৩টি stdlib unittest সফল: Swagger self-cycle, OpenAPI mutual/multi-node cycle, shared acyclic refs, escaped names, namespace collision ও independent cycles, ref siblings, external/dangling refs, empty schemas, এবং তিন actual SUT spec-এর static transform। Input অপরিবর্তিত থাকা, deterministic result ও দ্বিতীয় pass-এ নতুন cut না হওয়ার assertions আছে। প্রমাণ: `08_experiments/E1_pilot/harness_v2/test_derecurse.py:22–117`; `08_experiments/E1_pilot/harness_v2/static_checks.txt:20–38`।

## যাচাইয়ের ফল

| যাচাই | ফল | প্রমাণ |
|---|---|---|
| পাঁচ shell file-এর পৃথক `bash -n`, inline Python AST | PASS | `08_experiments/E1_pilot/harness_v2/static_checks.txt:2–6` |
| ছয় Python file-এর AST | PASS | `08_experiments/E1_pilot/harness_v2/static_checks.txt:7–12` |
| তিন config-এর jar/source path, YAML/proxy/port interpolation, auth fixture shape | PASS | `08_experiments/E1_pilot/harness_v2/static_checks.txt:13–15` |
| Required-fix markers এবং original harness-এর দশটি digest | PASS | `08_experiments/E1_pilot/harness_v2/static_checks.txt:16–17` |
| Full fixture header ও non-role token অনুপস্থিতির scan; public role identifiers অনুমোদিত | PASS | `08_experiments/E1_pilot/harness_v2/static_checks.txt:18`; `08_experiments/E1_pilot/harness_v2/static_validate.py:117–129` |
| Derecursion unittest | 13/13 PASS | `08_experiments/E1_pilot/harness_v2/static_checks.txt:35–38` |

পূর্ণ static validation পুনরুৎপাদনের command: `/usr/bin/python3 -I -B 08_experiments/E1_pilot/harness_v2/static_validate.py`। Validator-এর subprocess execution শুধু `bash -n` ও অনুমোদিত own unittest-এ সীমিত। প্রমাণ: `08_experiments/E1_pilot/harness_v2/static_validate.py:30–44`; `08_experiments/E1_pilot/harness_v2/static_validate.py:130–132`।

## সীমাবদ্ধতা ও খোলা প্রশ্ন

১. ⚠️ Readiness ও runtime routing যাচাই বাকি। বিশেষ করে petstore spec-এর `/api/v3` বনাম servlet `/api/*` ও Inflector `rootPath: /api` একসঙ্গে বাস্তবে কী route দেয়, তা source দেখে নিশ্চিত করা যায়নি। Default spec routing রাখা হয়েছে; path পাল্টালে unchanged oracle-এর route matching আলাদা করে পর্যালোচনা করতে হবে। প্রমাণ: `08_experiments/_external/emb/openapi-swagger/swagger-petstore.json#/servers`; `08_experiments/_external/emb/jdk_8_maven/cs/rest/original/swagger-petstore/README.md:40`; `08_experiments/_external/emb/jdk_8_maven/cs/rest/original/swagger-petstore/src/main/java/io/swagger/petstore/Main.java:54–65`; `08_experiments/_external/emb/scripts/dockerize/data/additional_files/swagger-petstore/inflector.yaml:16`; `08_experiments/tools/conformance.py:157–176`।

২. ⚠️ Market-এর `/v2/api-docs` health path Springfox Swagger 2 configuration থেকে inference; scout-এর health path Dropwizard server configuration থেকে নেওয়া। Auth fixture validity, protected-operation coverage, petstore-এর unauthenticated coverage, fresh-JVM state reset ও JaCoCo integration প্রথম execution-এ Claude-কে যাচাই করতে হবে। প্রমাণ: `08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market/market-rest/src/main/java/market/RestConfig.java:15–21`; `08_experiments/_external/emb/scripts/dockerize/data/additional_files/scout-api/scout_api_evomaster.yml:1–9`; `08_experiments/E1_pilot/harness_v2/README.md:153–199`।

৩. ⚠️ Generator input এবং oracle এক নয়। সমান mutation operation set থেকে সমান edits/constraints বা সমান generated traffic অনুসরণ করে না। Object replacement-এর semantic effect আছে; external refs, অন্য component group ও subschema-pointer/anchor cycle এই helper কাটে না। ফলে এটি general schema-repair ব্যবস্থা নয়। প্রমাণ: `08_experiments/E1_pilot/pilot_results/BATCH1_RESULTS.md:46–51`; `08_experiments/E1_pilot/harness_v2/derecurse.py:20–38`; `08_experiments/E1_pilot/harness_v2/run_metadata.py:66–70`।

৪. Fixed image tag থাকলে jar পরিবর্তন হলেও automatic rebuild নেই; প্রথম run-এর আগে tag-এর ভেতরের jar identity যাচাই প্রয়োজন। Scout v2 tag `r1-scout-api-sut:pilot`, v1 tag `r1-scout-sut:pilot` থেকে আলাদা। পুরোনো lock file অনুপস্থিত হলে cross-version lock race এড়াতে v1 ও v2 একসঙ্গে launch করা যাবে না। প্রমাণ: `08_experiments/E1_pilot/harness_v2/run_pilot.sh:137–141`; `08_experiments/E1_pilot/harness_v2/suts/scout-api.env:13`; `08_experiments/E1_pilot/harness/compose.override.scout-api.yaml:5`; `08_experiments/E1_pilot/harness_v2/common.sh:17–25`।

৫. Existing logger-এ response hook আছে; transport-error hook নেই। ⚠️ তাই exchange count থেকে সব attempted request সফলভাবে নথিভুক্ত হওয়ার সিদ্ধান্ত নেওয়া যাবে না। Fresh comparison observational; replay একই baseline exchange-এ oracle বদলায়। `complete=true` operation বা mutation exposure-এর প্রমাণ নয়; log/JUnit/coverage দেখে review লাগবে। প্রমাণ: `08_experiments/tools/mitm_fulllog.py:40–55`; `08_experiments/E1_pilot/harness_v2/analyse_run.sh:63–72`; `08_experiments/E1_pilot/harness_v2/run_pilot.sh:80–104,208–214`।

৬. Docker Compose merge, pinned-image runtime flags, UID/GID permissions, image/JVM compatibility, credentials-এর runtime sanitization ও cleanup-এর integration পরীক্ষা T14-এর বাইরে। SIGKILL/host loss cleanup এড়িয়ে যেতে পারে। Exact per-SUT execution commands ও ছয়টি first-execution assumption group README-তে দেওয়া আছে; runtime blocker শনাক্ত হয়েছে বলে দাবি করা হচ্ছে না। প্রমাণ: `08_experiments/E1_pilot/harness_v2/static_checks.txt:39`; `08_experiments/E1_pilot/harness_v2/README.md:39–97,146–199`।
