"""Render the Bengali T25 report from reviewed text and saved count rows."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
rows = json.loads((OUT / "petstore_operation_counts.json").read_text())
verification = json.loads((OUT / "verification.json").read_text())

report = """# T25 রিপোর্ট — E5 replacement mutation sites

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
"""

pairs = sorted({r["pair"] for r in rows})
roles = (("mutant", "control"), ("mutant", "mutant"), ("noise", "control"), ("noise", "control_repeat"))
index = {(r["pair"], r["seed"], r["method"], r["template"], r["kind"], r["role"]): r for r in rows}
for pair in pairs:
    for seed in (1, 2, 3):
        cells = [index[(pair, seed, "GET", "/user/login", kind, role)]["row_id"] + ": 200×2" for kind, role in roles]
        report += "| " + " | ".join([pair, str(seed)] + cells) + " |\n"

report += """
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

"""
for pair in pairs:
    for seed in (1, 2, 3):
        report += f"### {pair} — seed {seed}\n\n"
        report += "| Operation/path | C: pair control | M: historical mutant | N: noise control | R: control_repeat |\n|---|---|---|---|---|\n"
        operations = sorted({(r["method"], r["template"]) for r in rows if r["pair"] == pair and r["seed"] == seed})
        assert len(operations) == 20
        for method, template in operations:
            cells = []
            for kind, role in roles:
                row = index[(pair, seed, method, template, kind, role)]
                counts = "; ".join(f"{status}×{count}" for status, count in row["statuses"].items())
                cells.append(row["row_id"] + ": " + counts)
            report += "| " + " | ".join([f"`{method} {template}`"] + cells) + " |\n"
        report += "\n"

(ROOT / "09_collab/reports/T25_report.md").write_text(report)
print("report written; 480 counted status cells")
