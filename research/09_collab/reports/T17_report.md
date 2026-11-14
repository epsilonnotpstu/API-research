# T17 — চতুর্থ SUT: cwa-verification

## কী করা হয়েছে

`harness_v2`-এ `cwa-verification` config, Compose override ও allowlist entry যোগ করা হয়েছে। Fixed image tag `r1-cwa-verification-sut:pilot`; internal HTTP port 8080; credential injection বন্ধ। README-তে source review, missing dependency, exact smoke/batch commands এবং runtime review-এর প্রশ্ন যুক্ত হয়েছে। প্রমাণ: `08_experiments/E1_pilot/harness_v2/suts/cwa-verification.env:1–19`; `08_experiments/E1_pilot/harness_v2/compose.override.cwa-verification.yaml:1–32`; `08_experiments/E1_pilot/harness_v2/common.sh:4`; `08_experiments/E1_pilot/harness_v2/README.md:221–370`।

Docker, Java, Maven, SUT বা Schemathesis চালানো হয়নি। Source/static inspection, একটি jar-এর ZIP metadata read, আমাদের checker-এর route-matching model check ও অনুমোদিত static validator/unittest চালানো হয়েছে। Jar build coordinator-এর কাজ; T17 সেই build শুরু বা পরিবর্তন করেনি। প্রমাণ: `09_collab/tasks/T17.md:19–21,45–48`; `09_collab/logs/T17_scratch/jar_evidence.json:2–12`; `09_collab/logs/T17_scratch/origin_check.json:2–24`; `08_experiments/E1_pilot/harness_v2/static_checks.txt`, `NOT EXECUTED` row।

## Jar-এর exact নাম

POM-এর artifactId `cwa-verification-server`, version `1.5.0-SNAPSHOT`; কিন্তু Spring Boot repackage execution-এ `finalName=cwa-verification` ও classifier `sut` দেওয়া আছে। তাই এই checkout-এর exact local source jar হলো:

```text
jdk_11_maven/cs/rest/cwa-verification-server/target/cwa-verification-sut.jar
```

প্রমাণ: `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/pom.xml:7–8,270–284`; [Spring Boot 2.4.1 RepackageMojo target-file construction](https://github.com/spring-projects/spring-boot/blob/v2.4.1/spring-boot-project/spring-boot-tools/spring-boot-maven-plugin/src/main/java/org/springframework/boot/maven/RepackageMojo.java); `09_collab/logs/T17_scratch/jar_evidence.json:2–12`। Task-এর provisional `cwa-verification-server-*-sut.jar` glob ব্যবহার করা হয়নি।

Jar উপস্থিত; static read-এ 72,438,233 bytes, SHA-256 `be129f9754d2a127e38811cf6cb081ec8a74361d862c5045b7299936543fd2af`; `Start-Class=app.coronawarn.verification.VerificationApplication` এবং Spring Boot 2.4.1 পাওয়া গেছে। এগুলো executable startup-এর প্রমাণ নয়। প্রমাণ: `09_collab/logs/T17_scratch/jar_evidence.json:2–12`।

## Base path ও actual route

EMB spec OpenAPI 3.0.1; পাঁচটি POST operation আছে। Server URL `http://localhost:8080`-এর path অংশ ফাঁকা; spec-এর প্রতিটি operation path-এই `/version/v1` আছে। Controller-গুলোর class prefix-ও `/version/v1`। সুতরাং harness-এর `BASE_PATH_DEFAULT=/`; আবার `/version/v1` যোগ করলে path দ্বিগুণ হবে। প্রমাণ: `08_experiments/_external/emb/openapi-swagger/cwa-verification.json#/servers` এবং `#/paths`; `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/src/main/java/app/coronawarn/verification/controller/ExternalTokenController.java:43,51,76–81`; `08_experiments/E1_pilot/harness_v2/suts/cwa-verification.env:15`; `08_experiments/E1_pilot/harness_v2/static_checks.txt`, `CONFIG:cwa-verification` row।

**Authority-সংক্রান্ত অতিরিক্ত সীমাবদ্ধতা:** existing checker absolute server authority-ও মেলায়। আমাদের Python model check-এ একই POST route `http://localhost:8080` origin-এ মেলেছে, কিন্তু `http://mitmproxy:8080` ও `http://sut-cwa-verification:8080` origin-এ মেলেনি। এটি actual CWA traffic নয়; কোনো HTTP request পাঠানো হয়নি। প্রমাণ: `08_experiments/tools/conformance.py:125–137,157–180,381`; `09_collab/logs/T17_scratch/origin_check.json:2–24`।

⚠️ Generator Docker proxy-তে পাঠায়, এবং logger flow request-এর origin লেখে; ফলে actual origin একইভাবে আলাদা হলে সব route ভুলভাবে unmatched হতে পারে। প্রথম smoke-এর origin পরীক্ষা ও explicit deployment-authority calibration review ছাড়া conformance/attribution ফল গ্রহণ করা যাবে না। T17 source/oracle spec, exchange origin বা checker rewrite করেনি। প্রমাণ: `08_experiments/E1_pilot/harness_v2/run_pilot.sh:189–192`; `08_experiments/tools/mitm_fulllog.py:39–46`; `08_experiments/E1_pilot/harness_v2/README.md:328–341`; `09_collab/logs/T17_scratch/origin_check.json:8–22`।

## Auth ও filters

`SecurityConfig` `/version/**` permit করে এবং CSRF বন্ধ করে। Firewall-এর allowed methods GET/POST/HEAD; এটি authentication নয়। Default YAML-এ JWT validation disabled এবং `JwtService.isAuthorized()` সেই অবস্থায় সরাসরি true ফেরত দেয়। তাই config-এ role `none`, auth source ফাঁকা; কোনো EMB auth fixture বা dummy credential যোগ করা হয়নি। প্রমাণ: `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/src/main/java/app/coronawarn/verification/config/SecurityConfig.java:38–58`; একই source root-এর `src/main/resources/application.yml:24–26`; `src/main/java/app/coronawarn/verification/service/JwtService.java:89–99`; `08_experiments/E1_pilot/harness_v2/suts/cwa-verification.env:16–17`; `08_experiments/E1_pilot/harness_v2/static_validate.py:110–120`।

তবে `POST /version/v1/tan/teletan` method argument-এ Authorization header required। JWT disabled হওয়া header-binding requirement সরায় না: header না থাকলে method-এর আগে 400 হতে পারে। Header-টি spec-এর required operation parameter; harness-level role `none` মানে সব operation-এ ওই input optional নয়। প্রমাণ: `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/src/main/java/app/coronawarn/verification/controller/InternalTanController.java:138–154`; একই directory-র `VerificationExceptionHandler.java:64–70`; `08_experiments/_external/emb/openapi-swagger/cwa-verification.json#/paths/~1version~1v1~1tan~1teletan/post/parameters`।

`RequestSizeLimitFilter` request-size/chunking policy প্রয়োগ করে, credential check করে না। Body অতিরিক্ত বড় বা chunked হলে 406 সেট করে। প্রমাণ: `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/src/main/java/app/coronawarn/verification/config/RequestSizeLimitFilter.java:49–65`।

## Readiness এবং প্রয়োজনীয় minimal script change

Original Dockerfile `--management.server.port=-1` দেয়। YAML-এ health/probes enabled থাকলেও CLI management HTTP listener নিষ্ক্রিয় করে; `/actuator/health` readiness হিসেবে নেওয়া হয়নি। `/api/docs`-এর জন্য security secure channel চায়, অথচ Dockerfile HTTP চালায়। Public business routes পাঁচটিই POST; existing GET-only readiness যথেষ্ট নয়। প্রমাণ: `08_experiments/_external/emb/dockerfiles/cwa-verification.dockerfile:17`; `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/src/main/resources/application.yml:27–56`; একই source root-এর `src/main/java/app/coronawarn/verification/config/SecurityConfig.java:53–58`; `08_experiments/_external/emb/openapi-swagger/cwa-verification.json#/paths`।

⚠️ নতুন source-derived probe: **খালি body** দিয়ে `POST /version/v1/tan/verify`, `Content-Type: application/json`, প্রত্যাশিত status **ঠিক 400**। Required `@RequestBody` binding ব্যর্থ হয়ে handler 400 দেবে; operation body-তে গিয়ে TAN redeem/delete বা backend call করার প্রয়োজন নেই। এটি T17-তে runtime-verified নয়। প্রমাণ: `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/src/main/java/app/coronawarn/verification/controller/InternalTanController.java:100–107`; একই directory-র `VerificationExceptionHandler.java:64–70`; `08_experiments/E1_pilot/harness_v2/suts/cwa-verification.env:9–14`।

এই কারণে task-এর conditional exception অনুযায়ী `run_pilot.sh`-এ শুধু optional POST-readiness branch যোগ করা হয়েছে। Method/status-এর নতুন config field না থাকলে পূর্বের GET `curl --fail` branch-ই চলে; পুরোনো তিন SUT config বদলায়নি। POST probe-এ curl transport failure এবং 400 ছাড়া অন্য status গ্রহণ করা হয় না। আগের readiness-traffic quarantine অক্ষত; config snapshot ও harness hash-এ probe configuration ধরা থাকবে। প্রমাণ: `09_collab/tasks/T17.md:45–48`; `08_experiments/E1_pilot/harness_v2/run_pilot.sh:162–180`; `08_experiments/E1_pilot/harness_v2/run_metadata.py:30–31,59–63`; `09_collab/logs/T17_scratch/scope_verification.json`, `protected_files_unchanged` ও `run_pilot_change_review` fields।

`run_batch.sh`, পুরোনো তিন SUT config ও override, analysis/metadata/helper/test files T17-তে অপরিবর্তিত। Claude-এর `ONLY_OPS`, local-image fallback, `FAULTS`, `ORACLE_POOL=baseline` রক্ষিত। একই সময়ে coordinator-এর নতুন `DATA_GEN` block-ও রাখা হয়েছে; সেটি T17-এর edit নয়। Initial hash থেকে readiness ও DATA_GEN block বাদ দিয়ে original content মেলার check রেকর্ড করা হয়েছে। প্রমাণ: `09_collab/logs/T17_scratch/before_sha256.json`; `09_collab/logs/T17_scratch/scope_verification.json`, `run_pilot_change_review` field; `08_experiments/E1_pilot/harness_v2/static_validate.py:143–147`।

## অনুপস্থিত cwa-testresult-server: কোন operation ও কী ফল

Dockerfile backend URL `http://cwa-testresult-server:8088` দেয়; original Compose ও নতুন override-এ ওই service নেই। Single Feign method `POST /api/v1/app/result` পাঠায় এবং service wrapper exception translate/catch করে না। প্রমাণ: `08_experiments/_external/emb/dockerfiles/cwa-verification.dockerfile:17`; `08_experiments/_external/emb/dockerfiles/cwa-verification.yaml`, `services` mapping; `08_experiments/E1_pilot/harness_v2/compose.override.cwa-verification.yaml:1–32`; `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/src/main/java/app/coronawarn/verification/client/TestResultServerClient.java:33–49`; একই source root-এর `src/main/java/app/coronawarn/verification/service/TestResultServerService.java:48–49`।

নিচের source references-এ `C` prefix-এর পূর্ণ path হলো `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/src/main/java/app/coronawarn/verification/controller/`।

| Active operation | Backend call-এর শর্ত | প্রমাণ |
|---|---|---|
| POST `/version/v1/testresult` | Non-fake request; existing registration token-এর session source `HASHED_GUID`; DOB hash থাকলে দ্বিতীয় lookup-ও হতে পারে | `C/ExternalTestStateController.java:94–125` |
| POST `/version/v1/tan` | Non-fake request; existing GUID-backed session; TAN counter limit বাকি | `C/ExternalTanController.java:100–129` |

`cwa-fake: 1` branch ও teleTAN-backed session এই backend call এড়ায়। `registrationToken` operation local session তৈরি করে; teleTAN create/verify local TAN/JWT service ব্যবহার করে। `InternalTestStateController`-এ client call থাকলেও profile `REMOVED_DUE_TO_CONFLICTS`, তাই Dockerfile-এর `local,external,internal` profile-এ এটি active নয়; এটিকে তৃতীয় exposed operation গণনা করা হয়নি। প্রমাণ: `C/ExternalTestStateController.java:97–99,134–151`; `C/ExternalTanController.java:103–105,127–129`; `C/ExternalTokenController.java:91–120`; `C/InternalTanController.java:100–123,141–163`; `C/InternalTestStateController.java:38–41,83–91`; `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/src/main/java/app/coronawarn/verification/service/AppSessionService.java:86–110,120–136`।

⚠️ বর্তমান missing service/alias অবস্থায় সবচেয়ে প্রত্যাশিত transport failure হলো **DNS resolution failure**। Host resolve হলেও port-এ listener না থাকলে connection refused; blocked/slow peer হলে connect/read timeout হতে পারে। প্রতিটির configured timeout 5000 ms; DNS/retry/total wall time ঠিক পাঁচ সেকেন্ড হবে বলে দাবি করা যাচ্ছে না। প্রমাণ: `08_experiments/_external/emb/dockerfiles/cwa-verification.yaml`, `services` mapping; `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/src/main/resources/application.yml:17–23`; একই source root-এর `src/main/java/app/coronawarn/verification/client/TestResultServerClientConfig.java:69–82`।

Client failure controller পর্যন্ত unhandled exception হিসেবে পৌঁছালে generic handler **HTTP 500** দেয়। Dedicated 502/503/504 mapping নেই। তবে generator-এর 10000 ms timeout আগে শেষ হলে response record না-ও পাওয়া যেতে পারে। Invalid input বা unknown token-এর 400 backend call-এর আগেই হতে পারে; তাই path বা status দেখেই ENV label দেওয়া যাবে না। প্রমাণ: `C/VerificationExceptionHandler.java:52–55`; `C/ExternalTestStateController.java:149–151`; `C/ExternalTanController.java:150–155`; `08_experiments/E1_pilot/harness_v2/run_pilot.sh:30–32`।

**সুপারিশ:** প্রথম diagnostic baseline-এ declared setup রাখুন এবং request/log-এ missing backend নিশ্চিত হলে সংশ্লিষ্ট exchange-কে **ENV** হিসেবে বিবেচনা করুন। Coverage বাড়াতে deterministic stub পরে আলাদা documented condition হিসেবে review করা যায়; তার আলাদা controls/provenance প্রয়োজন। T17 কোনো stub service যোগ করেনি। এটি conditional call sites ও error propagation-এর ভিত্তিতে recommendation; observed runtime result নয়। প্রমাণ: উপরের operation table; `C/VerificationExceptionHandler.java:52–55`; `08_experiments/E1_pilot/harness_v2/compose.override.cwa-verification.yaml:1–32`।

## Validation ও ফল

নির্দেশিত command চালানো হয়েছে:

```bash
/usr/bin/python3 -I -B 08_experiments/E1_pilot/harness_v2/static_validate.py
```

পাঁচ shell file-এর syntax/inline AST, ছয় Python file-এর AST, চার SUT config-এর jar/path/YAML/proxy/auth shape, required fixes, original harness-এর দশটি digest ও secret-absence checks সফল। আগের ১৩টি stdlib unittest-ও সফল। নতুন CWA-specific static transform-এ operation paths অক্ষত, দ্বিতীয় pass idempotent, এবং cut সংখ্যা 0। প্রমাণ: `08_experiments/E1_pilot/harness_v2/static_checks.txt`, `SHELL/INLINE_AST`, `PYTHON_AST`, `CONFIG:*`, `CWA_SOURCE`, `PRESERVED_FIXES`, `SOURCE_HARNESS_UNCHANGED`, `SECRET_ABSENCE`, `Ran 13 tests` ও final PASS rows; `08_experiments/E1_pilot/harness_v2/static_validate.py:98–130`।

Validator এখন allowlist-এর সঙ্গে চার SUT-এর সেট মেলায় এবং CWA POM-derived jar, root base path, POST/400 readiness config, JWT setting ও absent auth fixture আলাদা করে পরীক্ষা করে। `CWA_ORIGIN` review row রেখে analysis limitation আড়াল করা হয়নি। প্রমাণ: `08_experiments/E1_pilot/harness_v2/static_validate.py:98–147`; `08_experiments/E1_pilot/harness_v2/static_checks.txt`, `CWA_ORIGIN` row।

## সীমাবদ্ধতা ও প্রথম execution-এর খোলা প্রশ্ন

১. ⚠️ Empty POST-এ ঠিক 400, required header binding, loopback/proxy integration, DB reset ও JaCoCo সংগ্রহ runtime-এ যাচাই বাকি। এই probe process/router readiness পরীক্ষা করবে; backend availability নয়। প্রমাণ: `08_experiments/E1_pilot/harness_v2/README.md:247–276,343–366`; `08_experiments/E1_pilot/harness_v2/static_checks.txt`, `NOT EXECUTED` row।

২. Actual exchange origin কী হবে এবং immutable original server URL-র সঙ্গে তার calibration কীভাবে হবে—এটি analysis গ্রহণের আগে coordinator-এর review দরকার। Model check-এ origin mismatch প্রতিষ্ঠিত, actual SUT capture এখনো নেই। Exact smoke commands প্রস্তুত আছে; source spec বা tool পরিবর্তন করা হয়নি। প্রমাণ: `09_collab/logs/T17_scratch/origin_check.json:8–22`; `08_experiments/E1_pilot/harness_v2/README.md:328–366`।

৩. Missing backend-এ কোনো valid GUID-backed token sequence কতটা পৌঁছাবে, exact exception/elapsed time কী হবে, এবং eligible RESPONSE_ORACLE pool যথেষ্ট হবে কি না—source reading থেকে runtime সংখ্যা দেওয়া যায় না। নতুন data সংগ্রহের আগে current harness/config স্থির রাখুন; old/new harness snapshots মিশিয়ে pair করবেন না। প্রমাণ: `08_experiments/E1_pilot/harness_v2/run_batch.sh:42–53`; `08_experiments/E1_pilot/harness_v2/analyse_run.sh:19–39`; `08_experiments/E1_pilot/harness_v2/README.md:357–370`।
