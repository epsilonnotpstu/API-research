# 08_experiments — R1 (“Spec or Bug?”) experiment workspace

**তারিখ:** 2026-11-09 · **সংশ্লিষ্ট:** `06_final_recommendations/research_execution_roadmap.md` (E1–E6), `R1_novelty_check_E0.md`, `R1_triage_codebook.md`

## গঠন

| পথ | বিষয়বস্তু | Git |
|---|---|---|
| `tools/specmut.py` | নিজস্ব spec-mutation tool: Swagger 2.0 ও OpenAPI 3.x, ground-truth manifest সহ | ✅ |
| `tools/test_specmut.py` | Property check: serialisation, locality, manifest fidelity, determinism | ✅ |
| `tools/conformance.py` | Logged exchange → violation + fingerprint। Swagger 2 ও OAS3; strict mode ঐচ্ছিক | ✅ |
| `tools/attribute.py` | Baseline বনাম mutated violation-এর diff + manifest-ভিত্তিক label (NEW / VANISHED / PERSISTENT) | ✅ |
| `tools/mitm_fulllog.py` | mitmproxy addon: পূর্ণ request/response JSONL (EMB-এর `minlog.py`-এর বিকল্প) | ✅ (এখনো চালানো হয়নি) |
| `tools/test_pipeline.py` | Replay-mode end-to-end test: specmut → conformance → attribute | ✅ |
| `E1_pilot/p001_oas_analysis.py`, `E1_pilot/P001_empirical_findings.md`, `E1_pilot/p001_results/` | P001-এর ১৪৭টি confirmed fault-এর বিশ্লেষণ ও replay | ✅ |
| `R1_triage_codebook.md` | Failure attribution label scheme v0.2 | ✅ |
| `E1_pilot/spec_mutability.txt` | ৩৬টি EMB spec-এর mutability ও dependency তালিকা | ✅ |
| `_external/p001/` | P001 Zenodo থেকে নামানো ফাইল (~৬০ MB) ও ১৩টি spec | ❌ (`.gitignore`) |
| `_external/emb/` | EMB sparse clone: commit `915859080da0…`, শুধু `openapi-swagger/`, `dockerfiles/`, features-service source | ❌ (`.gitignore`) |

## E1 অগ্রগতি

### ✅ সম্পন্ন

1. **`specmut`:** 2607.12101-এর fault taxonomy-র স্বাধীন পুনর্বাস্তবায়ন (CC-BY 4.0 উৎস উল্লেখসহ)। চারটি class: REQUEST_LOOSE, REQUEST_STRICT, RESPONSE_ORACLE, METHOD_SEM।
   - **মূল সংযোজন:** প্রতিটি edit-এর manifest — operation, JSON pointer, before/after, প্রত্যাশিত triage label (codebook §5)।
   - **Locality নিশ্চিতকরণ:** `$ref` ও path-level parameter শুধু বাছাই করা operation-এর ভেতরে inline হয়; no-op হলে সব পার্শ্ব-প্রতিক্রিয়া ফিরিয়ে নেওয়া হয়।
2. **যাচাই:** EMB-এর ৩৬টি spec (১৯টি Swagger 2 + ১৭টি OAS3) × ৪টি class = **১৪৪/১৪৪ check পাস**।
   ```
   cd tools && python3 test_specmut.py ../_external/emb/openapi-swagger
   ```
   - প্রথম run-এ ৩০টি locality ব্যর্থতা ধরা পড়েছিল। কারণ: no-op mutation-এর `$ref` inlining রয়ে যাচ্ছিল। এটি সংশোধিত হয়েছে।
3. **SUT নির্বাচনের তথ্য (`E1_pilot/spec_mutability.txt`):**
   - Severity ১০০%-এ প্রতিটি class কত শতাংশ operation-এ প্রয়োগযোগ্য, তার হিসাব।
   - **পর্যবেক্ষণ:** EMB spec-গুলোর মান খুব অসমান। উদাহরণ: features-service-এ constraint প্রায় নেই এবং definition খালি object — LOOSE ৬%, ORACLE ২২%।
   - ⇒ R1-এর SUT বাছাইয়ে spec-এর “mutability” একটি মানদণ্ড হওয়া উচিত।
     - ⚠️ এতে নির্বাচন-পক্ষপাত ঢোকে। Threats to validity-তে লিখতে হবে।

4. **Pipeline (2026-11-09):** `conformance.py` + `attribute.py` + `mitm_fulllog.py`।
   - Replay-mode test (`test_pipeline.py`): ৩৬টি spec × ৪টি class-এ unexplained diff = ০।
   - REQUEST_LOOSE নতুন violation তৈরি করে না, কিন্তু ৩০টি বিদ্যমান violation **লুকিয়ে ফেলে** (masking)। এটি 2607.12101-এর “hidden degradation”-এর oracle-পক্ষীয় রূপ।
5. **বাস্তব data-তে instrument যাচাই (P001):** আমাদের checker P001-এর verdict পুনরুৎপাদন করে —
   - F_OAS ৮৫% (strict mode-এ ৯৭%)।
   - F_400 ১৫/১৬, 5xx ৬/৬।
   - Inter-parameter dependency ০/৮ (OpenAPI-তে অপ্রকাশযোগ্য — প্রত্যাশিত)।
   - বিস্তারিত: `E1_pilot/P001_empirical_findings.md`।

### প্রস্তাবিত pilot SUT
শর্ত: অতিরিক্ত container নেই, এবং চারটি class-ই প্রয়োগযোগ্য।

| SUT | Format | Ops | LOOSE / STRICT / ORACLE / METHOD (% op) |
|---|---|---|---|
| market | Swagger 2 | ১৩ | ৫৪ / ৯২ / ১০০ / ৯২ |
| swagger-petstore | OAS 3 | ১৯ | ৬৮ / ৮৯ / ৬৩ / ৭৪ |
| scout-api | Swagger 2 | ৪৯ | ৯২ / ৯৬ / ৩৭ / ৩৩ |
| cwa-verification | OAS 3 | ৫ | ১০০ / ১০০ / ১০০ / ১০০ (sanity) |

### ⛔ আটকে আছে — supervisor-এর অনুমতি দরকার

- **কী আটকেছে:** Docker-এর ভেতরে EMB SUT build। Claude Code auto-mode classifier “Code from External” কারণে বাতিল করেছে।
  - **External code চালানো** — SUT build বা run, 2607.12101-এর injector, Schemathesis/EvoMaster — **সবই এই শ্রেণির।** তাই supervisor-এর সিদ্ধান্ত দরকার।
- **বিকল্প:**
  - **(ক) নিজে চালানো:** নিচের command-গুলো terminal-এ চালাও। অথবা Claude Code-এ `!` দিয়ে শুরু করে চালাও।
  - **(খ) Claude-কে অনুমতি দেওয়া:** settings-এ নির্দিষ্ট rule যোগ করা। যেমন `Bash(docker run --rm -v m2cache:/root/.m2:*)`, বা `/permissions` থেকে।
- **Build command** (একটি SUT-এর উদাহরণ; JDK 8 Maven container, host-এ কিছু install হয় না):
  ```
  cd research/08_experiments/_external/emb
  # source পথ (git tree থেকে যাচাইকৃত) ও JDK (EMB dockerfile-এর FROM অনুযায়ী):
  #   market            jdk_11_maven/cs/rest-gui/market           → JDK 11 (maven:3.8.8-eclipse-temurin-11)
  #   cwa-verification  jdk_11_maven/cs/rest/cwa-verification-server → JDK 11
  #   scout-api         jdk_8_maven/cs/rest/original/scout-api      → JDK 8  (maven:3.8.8-eclipse-temurin-8)
  #   swagger-petstore  jdk_8_maven/cs/rest/original/swagger-petstore → JDK 8
  git sparse-checkout add /jdk_8_maven/cs/rest/original/scout-api/
  docker run --rm -v m2cache:/root/.m2 -v "$PWD/jdk_8_maven/cs/rest/original/scout-api":/src -w /src \
      maven:3.8.8-eclipse-temurin-8 mvn -q -DskipTests package
  ```
  - ⚠️ কিছু SUT EMB-এর parent `pom.xml`-এর উপর নির্ভর করতে পারে। ব্যর্থ হলে `jdk_*_maven/pom.xml`-ও sparse-checkout-এ যোগ করতে হবে।
  - Dockerfile `dist/<sut>-sut.jar` আশা করে। Build-এর পর jar নাম বদলে `dist/`-এ রাখতে হবে, সঙ্গে `jacocoagent.jar`।
  - ⚠️ EMB-এর অফিশিয়াল পথ `scripts/dist-docker.py` সব SUT build করে। এটি ভারী, এবং disk-এ মাত্র প্রায় ৪১ GB খালি।


### Supervisor-এর build (2026-11-13)
- scout-api build সম্পন্ন: `_external/emb/jdk_8_maven/cs/rest/original/scout-api/api/target/scout-api-sut.jar` (৩৪.৭ MB, root-owned — Docker build থেকে)।
- Runtime ফাইল sparse-checkout-এ যোগ: `scripts/dockerize/data/additional_files/scout-api/` (`init_db.sql`, `scout_api_evomaster.yml`; H2 in-memory DB, port 8080)।
- Spec: Swagger 2.0, `basePath: /api`, auth নেই।
- বাকি: `dist/` layout + jacocoagent → harness (Codex T5) → execution (T7; supervisor allow rule-এর পরে)। সমন্বয়: `../09_collab/COLLAB_BOARD.md`।

### Pilot ফল (2026-11-14)
- `E1_pilot/pilot_results/BATCH1_RESULTS.md`, `BATCH2_RESULTS.md` (scout-api), `PETSTORE_RESULTS.md` (swagger-petstore)। Market চলমান।
- Harness: `E1_pilot/harness/` (v1, শুধু scout-api), `E1_pilot/harness_v2/` (scout-api, swagger-petstore, market)।
  - `run_batch.sh SUT [seeds]`, options `SCHEMA_CHECKS`, `BUDGET_SECONDS`, `ORACLE_POOL=baseline`।
- নতুন tool: `tools/eligible_ops.py` (baseline-এ body-সহ 2xx পাওয়া operation) → `specmut.py --only-ops`। Test: `tools/test_only_ops.py`।
- Labelling: `E2_labelling/batch2_baseline_s1_blind.csv` (labeller B-এর জন্য, label ছাড়া)।

## পরবর্তী ধাপ (অনুমতি পেলে)

1. Pilot SUT build → `dockerfiles/<sut>.yaml` দিয়ে চালানো। mitmproxy log ও JaCoCo সহ।
2. **Baseline run:** Schemathesis (`--checks all`) ও EvoMaster BB — মূল spec দিয়ে → baseline failure set।
3. **Mutated run:** `specmut` দিয়ে প্রতিটি class × severity {১৫, ৩০, ৪৫} × seed {১, ২, ৩} → একই tool।
4. **Failure diff:** fingerprint (operation + status + violation path)। Mutated − baseline = injected-spec failure → manifest-এর সাথে join করে label।
5. **Code-mutation দিক (IMPL label):** PIT-এর mutant বা হাতে-তৈরি validation removal। এটি E4-এর সাথে।
