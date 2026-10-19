# P018 — Generating REST API Specifications through Static Analysis (Respector)

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (related work বাদ, references বাদ) · **উৎস:** ICSE 2024 (CC-BY-SA), ১৩ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Ruikai Huang, Manish Motwani, Idel Martinez, Alessandro Orso (Georgia Tech; Oregon State)
- **Venue:** ICSE 2024, DOI 10.1145/3597503.3639137
- **Cluster:** T4 (secondary: T1 — enhanced spec for testing; T6 — documentation inconsistency)
- **ধরন:** Static + symbolic analysis technique + empirical evaluation

## B. Motivation
- Developer প্রায়ই spec লেখে/রক্ষা করে না; production API spec থেকে ভিন্ন (p.1 L75–77)।
- বিদ্যমান generator (AppMap, Swagger Inspector, ExpressO, Springfox, springdoc, ApiCarv) annotation বা deployment/test-execution চায় এবং সরল spec দেয় — ApiCarv শুধু method ও path (p.1 L78–85)।

## C. Research questions (p.2 L120–133)
- RQ1: Respector কি নির্ভুল spec তৈরি করে? RQ2: developer spec-এর তুলনায়? RQ3: বিদ্যমান technique-এর তুলনায়?

## D. Contributions (p.2 L134–146)
- **প্রথম static/symbolic-analysis-ভিত্তিক OAS generator**; Spring Boot ও Jersey prototype; ১৫টি API-তে মূল্যায়ন; replication package (Software Heritage)।
- Enhanced OAS extension: `x-endpoint-constraints` (OpenAPI-তে অপ্রকাশযোগ্য constraint SMT-LIB-এ), `x-global-variables-info`, **`x-endpoint-interdependence`** (global variable read/write-ভিত্তিক dependency) (p.3 L489–502)।

## E. Methodology
- **Framework database (একবারের):** ২ class, ১৪ method, ১১ parameter annotation, ৩৩ library method, ১০১ response object, ৩ body-access method — দুই দিনের কম শ্রম (p.4 L592–610)।
- **Step 1 (Alg.1):** controller class, endpoint method (path, HTTP method, return type, status code), parameter (annotation, framework request object call-site, user-defined body class deserialization, controller class field), response schema (recursive getSchema); **sub-resource/indirect path** (Alg.2) (p.4–5 L611–866)।
- **Step 2 (Alg.3):** Soot ICFG-তে DFS symbolic traversal; Z3 দিয়ে feasible branch; return/throw-এ status code থেকে ValidPC/InvalidPC; global read/write রেকর্ড; loop একবার unroll, recursion বাদ, **প্রতি endpoint ৫,০০০ path threshold** (p.5–6 L867–1032)।
- **Step 3 (Alg.4):** ValidPC-এর প্রতি-variable constraint-এর disjunction Z3 দিয়ে conjunction-এ সরল (p.6–7 L1033–1123)।
- **Step 4–5:** pattern matching দিয়ে OpenAPI keyword-এ রূপান্তর — ১৫টির মধ্যে **৮টি constraint type** (min/max, exclusive, required, min/maxLength, multipleOf); pattern, items, enum ইত্যাদি সমর্থিত নয়; বাকিগুলো extension-এ (p.7 L1128–1209)।

## F. Dataset ও setup
- **১৫টি open-source Java API** (১K–১১৯K SLOC): GitHub search (Spring Boot/Jersey, developer spec আছে, ≥৫ star, compile হয়) থেকে ৮টি (Digdag, enviroCar, Gravitee, Kafka, cassandra, Quartz, Senzing, Ur-Codebin) + পূর্ববর্তী গবেষণা (EMB ইত্যাদি) থেকে ৭টি (p.8 L1223–1229)।
- **Ground truth:** একাধিক লেখক স্বাধীনভাবে source code ও developer spec বিশ্লেষণ করে reconcile (p.8 L1230–1241)।
- Runtime গড় ২২ মিনিট/API, median ১৫.৯৭ s (p.8 L1242–1243)।
- Baselines: AppMap (test execution), Swagger Core (Jersey), springdoc-openapi ও SpringFox (Spring Boot) — সবই API বা test চালানো দরকার (p.8 L1247–1253, L1362–1366)।

## G. Evaluation
- Precision/recall (৪ মাত্রা) + interdependency manual যাচাই; developer spec-এর সঙ্গে diff; baseline coverage (Respector-detected entity-র শতাংশ)।

## H. Results (author-reported)
- **RQ1:** endpoint P **১০০%** / R **৯৮.৬%** (৯৫২-এর ৯৪৬; dynamic URI factory-তে ৬টি মিস); parameter ১০০/৯৪.৪% (৮,০৩৭-এর ৭,৯৭৭); **constraint ৯৫.৬/৫০%** (গড়) — কিন্তু মোট **১১১-এর মাত্র ৩১টি (২৭.৯৩%)**; response ১০০/৯২.৬% (১,১২০-এর ১,০৩৮; async response মিস); ৪২৫টি method ৩৯৩টি global variable ব্যবহার করে, ১০০টি method-এ **৪,৮০৬ interdependency** (p.8–9 L1379–1756)।
- Constraint মিসের কারণ: ৫৮টি Ohsome-এর `required` — Z3 `splitParamOnComma` বোঝে না; ২২টি reflection/lambda/runtime validation (Jersey bean validation); ৩টি ভুল — Senzing-এ path threshold অতিক্রম (p.9 L1391–1741)।
- **RQ2:** developer spec-এ অনুপস্থিত — **২২৮ endpoint, ২,৭৯৫ parameter, ১৫ constraint, ৫০২ response**; **৪টি constraint অসঙ্গতি — developer-স্বীকৃত** (Senzing `buildOut` int8 বনাম int32, অনুপস্থিত maximum ১০০) (p.3 L371–382; p.9–10 L1941–1967)।
- **RQ3:** AppMap ৭টি API-তে ব্যর্থ; বাকিতে ৩৬.৩% endpoint, ৩.৫% parameter, কোনো constraint/response নেই; ৮টি API deploy-ই করা যায়নি (DB, auth, config সমস্যা); baseline-গুলো গড়ে Respector-detected entity-র **৭৫.৪৩% endpoint, ৬৬.২৮% parameter, ১৮.৩৫% constraint, ৬৩.৯৭% response** পেয়েছে (p.10 L1968–2015)।

## I. Strengths
- **Deployment-মুক্ত** — API চালানো লাগে না (baseline-এর ৮/১৫ deploy ব্যর্থতা বিপরীতে এর ব্যবহারিক সুবিধা স্পষ্ট)।
- **Developer-confirmed অসঙ্গতি** — spec-implementation mismatch-এর বাস্তব প্রমাণ (P001/P004-এর সঙ্গে সামঞ্জস্যপূর্ণ)।
- Success/error-এর path condition ও endpoint interdependency — testing tool-এর জন্য মূল্যবান অতিরিক্ত তথ্য।
- Failure-এর কারণ বিশ্লেষণ সৎ; artifact Software Heritage-এ স্থায়ী।

## J. Explicit limitations (p.10 §4.3)
- Static analysis-এর সীমা: path explosion (Senzing >২২০ path), dynamic endpoint handling।
- Type erasure/interface-এ precision কমে।
- Z3/Soot-এর সমর্থনসীমা; **external library analysis নেই**; configuration file (SpringFox runtime parameter) পড়ে না।
- শুধু Spring Boot ও Jersey; bytecode প্রয়োজন।
- External validity: ১৫টি API; REST case study জোগাড় কঠিন।

## K. Inferred limitations (⚠️ অনুমান)
- **Constraint recall-এর উপস্থাপনা বিভ্রান্তিকর:** abstract/RQ1-এ “৫০% recall” (per-API গড়, NA বাদ), অথচ pooled হিসাবে **২৭.৯৩%** — অর্থাৎ constraint inference আসলে দুর্বল; একটি API (Ohsome) ৫৮/৮০ মিসের কারণ।
- **Ground truth লেখকদেরই তৈরি** — inter-rater agreement সংখ্যা নেই; ground truth নিজেই source-code reading-ভিত্তিক — Respector-এর মতো একই দৃষ্টিভঙ্গি (shared blind spot, যেমন runtime-configured parameter)।
- **Precision ১০০% প্রায় সর্বত্র** — static analysis false positive কম দেয়, কিন্তু ground truth যদি tool-output দেখে reconcile করা হয় তবে anchoring bias সম্ভব।
- **Interdependency (৪,৮০৬)-এর উপযোগিতা অপরীক্ষিত:** global variable-শেয়ারিং-ভিত্তিক dependency অত্যন্ত coarse (যেমন shared FACTORY singleton) — অনেকগুলো অর্থহীন হতে পারে; testing-এ কাজে লাগে কিনা (sequence generation) পরিমাপ হয়নি; DB-মাধ্যম dependency (সবচেয়ে সাধারণ) ধরা পড়ে না।
- **Downstream testing benefit অপরীক্ষিত** — enhanced spec দিয়ে RESTler/EvoMaster-এর coverage বাড়ে কিনা দেখানো হয়নি (motivation-এ দাবি করা হয়েছে)।
- Baseline তুলনা আংশিক — বেশিরভাগ baseline অর্ধেক API-তেই চলেনি; তুলনা “Respector-detected entity”-কে denominator ধরে, ground truth নয় — Respector-এর মিস করা entity baseline পেলে তা গণনায় আসে না।
- ২২ মিনিট গড় কিন্তু median ১৬ s — কিছু API-তে বিশাল সময় (সম্ভবত Senzing/Kafka); scalability-র বিস্তারিত নেই।

## L. Threats to validity
- উপরে J; inferable: construct (ground truth পদ্ধতি; constraint recall-এর গড় বনাম pooled), external (Java-only)।

## M. Reproducibility
- সব data, code, documentation Software Heritage-এ — **উচ্চ**; subject API-গুলো open-source।

## N. Opportunities (hypothesis)
- **Static + LLM hybrid:** Respector-এর precision (১০০%) + OOPS (P017)-এর generality ও constraint recall — LLM দিয়ে Z3-অবোধ্য function (`splitParamOnComma`), reflection, runtime validation annotation ব্যাখ্যা; LLM output-কে symbolic path দিয়ে যাচাই।
- **Bean validation/framework runtime constraint মডেলিং** — ২২টি মিস সরাসরি সমাধানযোগ্য।
- **Inter-parameter dependency (IDL, P016) static inference** — path condition-এ দুই parameter একসঙ্গে থাকলে IDL তৈরি।
- **DB-mediated endpoint dependency** — ORM entity read/write থেকে producer-consumer (RESTler-এর runtime inference-এর static বিকল্প)।
- **Continuous spec-drift CI check:** প্রতিটি commit-এ generated বনাম developer spec diff — T5 (breaking change) ও T6 (documentation smell) সংযোগ; পরে Lercher et al. (P020-এর লেখকগোষ্ঠী) breaking change detection-এ অনুরূপ পদ্ধতি ব্যবহার করেছেন (P017-এ উদ্ধৃত)।
- Enhanced spec-এর downstream testing মূল্যায়ন।

## O. Relationships
- **Baseline for P017 (OOPS)** — OOPS এটিকে technology-specific বলে সমালোচনা করে।
- **Same group as P005/P007** (Orso, Georgia Tech) — testing tool-এর spec চাহিদা থেকে উদ্ভূত।
- **Complements P019 (RestPi)** — উভয়ই static/type analysis; RestPi path-sensitive type inference।
- **Confirms P001/P004** — spec-implementation অসঙ্গতি ব্যাপক।
- **Relates to P016** — constraint আছে কিন্তু inter-parameter dependency language নেই।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract | p.1 L31–51 |
| বিদ্যমান tool-এর সীমা | p.1 L75–85 |
| RQ সারাংশ সংখ্যা | p.2 L120–133 |
| Senzing উদাহরণ, developer confirmation | p.2–3 L157–382 |
| Enhanced OAS extension | p.3 L436–502 |
| Framework database | p.4 L592–610 |
| Alg.1 (extraction), Alg.2 (sub-resource) | p.4–5 L611–866 |
| Alg.3 symbolic, ৫,০০০ threshold | p.5–6 L867–1032 |
| Alg.4 simplification | p.6–7 L1033–1123 |
| ৮/১৫ constraint type | p.7 L1142–1146 |
| Dataset, ground truth, procedure | p.8 L1223–1368 |
| RQ1 ফল | p.8–9 L1379–1756 |
| RQ2 ফল | p.9–10 L1941–1967 |
| RQ3 ফল | p.10 L1968–2015 |
| Discussion, limitations | p.10 L2017–2050 |
| Threats | p.11 L2386–2403 |

**Document integrity:** Body সম্পূর্ণ; algorithm-এর গাণিতিক italic অক্ষর (𝑀, 𝑃) আংশিক বিকৃত কিন্তু পাঠযোগ্য; JSON listing letter-spaced; **Figure 5–8 (per-API table-figure) column-split** — মোট সংখ্যা text থেকে যাচাইকৃত।
