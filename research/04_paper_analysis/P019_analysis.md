# P019 — RestPi: Path-Sensitive Type Inference for REST APIs

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (related work ও per-endpoint appendix table skim, references বাদ) · **উৎস:** PACMPL OOPSLA2 2025 (CC-BY-ND), ২২ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Mark W. Aldrich, Kyla H. Levin, Michael Coblenz, Jeffrey S. Foster (Tufts; UMass Amherst; UC San Diego)
- **Venue:** Proc. ACM Program. Lang. 9 (OOPSLA2), Article 277, 2025, DOI 10.1145/3763055
- **Cluster:** T4 (secondary: T6 — documentation completeness)
- **ধরন:** Type-system theory + Ruby implementation + empirical evaluation

## B. Motivation
- REST client-কে সব response type (status + JSON shape) জানতে হয়; বিভিন্ন API সাফল্য/ব্যর্থতা ভিন্নভাবে প্রকাশ করে (p.1 L31–38)।
- Proxy/test-traffic-ভিত্তিক spec (rswag, rspec-openapi): slowdown, privacy ঝুঁকি, মূলত সফল interaction দেখে, **perfect coverage না থাকলে অসম্পূর্ণ** (p.1–2 L39–63); NL/annotation-ভিত্তিক পদ্ধতির পূর্বশর্ত documentation (L64–66)।
- **Discourse উদাহরণ:** rswag-generated spec — invite-only সেটিংয়ে `POST /users.json` 403 + খালি body দেয় (spec-এ নেই); `user_found` field site configuration-নির্ভর; private profile/নিজের profile-এ field ভিন্ন (p.2–3 L94–160)।

## C. Research questions (p.12–13 L810–849)
- RQ1: path-sensitive type inference কি control-flow-নির্ভর response type enumerate করতে কার্যকর? RQ2: performance? RQ3: dynamic proxy-ভিত্তিক spec-এর তুলনায়?

## D. Contributions (p.2 L82–87)
- Path-sensitive type inference system — function-এর ভিন্ন ভিন্ন return type ও তাদের path condition enumerate করে।
- RESTπ — Ruby-র জন্য open-source implementation (RDL-এর উপর)।
- ৫টি Rails API-তে মূল্যায়ন।

## E. Methodology
- **Formal core (Fig.4–5):** ছোট imperative ভাষা; path condition = syntactic branch label ℓ-এর বুলিয়ান সমন্বয় (**guard interpret করা হয় না**); **path type** (φ₁:τ₁, φ₂:τ₂); if-এ type environment duplicate, join-এ path type তৈরি; flow-sensitive (p.5–7 L316–451)।
- **Singleton types:** literal (404, `{success: "OK"}`) type-এ তুলে রাখা → `HTTPResponse<200, {success: "OK"}>` (p.7–8 L468–525)।
- **Computed types:** `Hash#merge`, `ActiveRecord::Base#as_json` (DB schema থেকে column type) inference-কালে গণনা (p.8–9 L527–573)।
- **Layered inference:** before_action (auth) → controller → rescue_from → serializer — layer-ক্রমে context প্রবাহ; প্রতিটি render একটি path-sensitive constraint τ ≤φ α (p.9–10 L574–660)।
- **Path-explosion প্রশমন:** (১) **path-type merging** — hash-এর key-wise merge (symbolic execution-এর value merging-এর type-theoretic রূপ); (২) library/ORM/helper call path-insensitive (path type-কে union হিসেবে) (p.10–12 L662–804)।

## F. Dataset ও setup
- **৫টি Ruby on Rails API:** Code.org, Discourse, Journey (পূর্ববর্তী RDL কাজ থেকে) + Canvas, OpenFarm (GitHub star-ক্রমে, ≥১০ endpoint-এ একাধিক `render`, ORM, কার্যকর test suite) (p.13 L855–866)।
- **Endpoint নির্বাচন:** শুধু যেগুলো একই function-এ একাধিকবার `render` করে (control-flow-সমৃদ্ধ); Canvas-এ শুধু course assignment — মোট **১৩২ endpoint** (p.13 L861–866)।
- **Dynamic baseline spec:** Discourse-এ rswag official docs; Canvas/OpenFarm-এ rspec-openapi; Code.org/Journey-তে test suite instrument করে HAR → har-to-openapi (p.13 L867–874)।
- Hardware: consumer desktop i7-3770, 16GB (L875)।

## G. Evaluation
- RQ1: inferred unique response type সংখ্যা; RQ2: ১০ রানের median সময় বনাম control-flow split সংখ্যা, merging চালু/বন্ধ; RQ3: dynamic spec-এর সঙ্গে status code, অতিরিক্ত field, “required” field ভুল সংখ্যা (Table 3)।

## H. Results (author-reported)
- **RQ1:** ১৩২ endpoint-এ **৫৪৫টি unique response type** — ১৬৬টি HTTP 200, ৩৭৯টি অন্যান্য status (p.13 L881–888)।
- **RQ2:** গড় **১.৩৫৩ s/endpoint** (merging সহ); control-flow split সর্বোচ্চ ১০০ (Canvas); merging বন্ধ থাকলে ৫টি endpoint timeout-এ শেষ হয়নি; CI-তে ব্যবহারযোগ্য বলে দাবি (p.15 L1175–1187)।
- **RQ3:** ১৩২-এর মধ্যে মাত্র **৭৬টি test suite-এ invoke হয়েছিল**; dynamic spec-এ ১৩২ response type (৬০টি 200, ৭২টি অন্য) বনাম RESTπ **২২৭ (+৭১.৯৭%)** — ৬২ (+৩.৩৩%) 200 এবং **১৬৫ (+১২৯.১৭%) non-200**; RESTπ dynamic-এ দেখা সব status ও field-এর over-approximation বলে হাতে যাচাই (p.16 L1549–1555)।
- দুটি endpoint-এ test suite কখনো সফল হয়নি কিন্তু RESTπ 200-path খুঁজে পেয়েছে; Canvas-এ serialization format (assignment/quiz/calendar event) ভেদে field; Discourse-এ access-control-স্তর ভেদে field; Code.org-এ dynamic spec `{2378: T}` বনাম আসল `Hash<Integer, T>` — dynamic inference-এর সাধারণীকরণ-সমস্যা (p.17 L1556–1594)।

## I. Strengths
- **নতুন তাত্ত্বিক অবদান:** symbolic execution-এর path sensitivity type system-এ — formal rule সহ; value merging-এর type-theoretic অনুবাদ।
- **Error response-কেন্দ্রিক** — P017/P018 মূলত 2xx-এ সীমিত; এখানে non-200 response +১২৯% — testing oracle ও client robustness-এর জন্য গুরুত্বপূর্ণ।
- Ruby (dynamic language)-এ কাজ — Java-কেন্দ্রিক static tool (P018) থেকে ভিন্ন ecosystem।
- Test-suite ছাড়াই কাজ করে; dynamic spec-এর coverage-নির্ভরতা স্পষ্টভাবে প্রদর্শিত (১৩২-এর মাত্র ৭৬ tested)।
- Open-source; Discourse-এর মতো বড় বাস্তব প্রকল্প।

## J. Explicit limitations (p.17 §Threats)
- **Ruby on Rails-নির্ভর:** DB schema ও Rails serialization-এর সুবিধা; অন্য framework-এ অতিরিক্ত modelling লাগবে।
- **Loop-এর type rule নেই:** higher-order iteration path-insensitive (sound); language-level while/for একবার বিশ্লেষণ (unsound) — মূল্যায়নের endpoint-এ ছিল না।

## K. Inferred limitations (⚠️ অনুমান)
- **Precision অপরিমাপিত:** path condition syntactic label — guard interpret না করায় **infeasible path থেকে অস্তিত্বহীন response type** আসতে পারে; লেখকরা কেবল over-approximation (superset) যাচাই করেছেন, অতিরিক্ত ৯৫টি response type-এর কতগুলো বাস্তবে সম্ভব তা যাচাই হয়নি (developer confirmation বা targeted test নেই)।
- **Endpoint নির্বাচন পক্ষপাতী:** শুধু “একাধিক render”-যুক্ত endpoint — RESTπ-এর সুবিধা দেখানোর জন্য সবচেয়ে অনুকূল উপসেট; সাধারণ CRUD endpoint-এ বাড়তি মূল্য কম হতে পারে (লেখকরা নিজেরাই স্বীকার করেন)।
- **Baseline দুর্বল:** test-suite-এর proxy spec — অন্য static tool (Respector-এর Ruby সমতুল্য নেই) বা LLM (P017) তুলনা নেই; dynamic spec-এর মান test suite-এর মানের উপর নির্ভরশীল।
- **Request side অনুপস্থিত:** শুধু response type; parameter, constraint, inter-parameter dependency inference নেই — পূর্ণ OAS generator নয়।
- **Path condition-এর ব্যবহারযোগ্যতা:** `logged_in ∧ Post.find` ধরনের condition মানুষের বোধগম্য, কিন্তু OpenAPI-তে প্রকাশের পদ্ধতি (বা client codegen-এ ব্যবহার) দেখানো হয়নি।
- Single consumer desktop, ১০ রান — performance ঠিক আছে কিন্তু বড় codebase (Canvas পুরো API)-এ স্কেল অপরীক্ষিত।

## L. Threats to validity
- উপরে J; inferable: construct (over-approximation = সঠিকতা?), selection bias (endpoint নির্বাচন), external (Rails)।

## M. Reproducibility
- RESTπ open-source [3]; benchmark প্রকল্পগুলো public; dynamic spec তৈরির পদ্ধতি বর্ণিত — **উচ্চ**।

## N. Opportunities (hypothesis)
- **Feasibility-checked path types:** guard-কে SMT-এ interpret করে (Respector-ধাঁচে) বা targeted test generation দিয়ে infeasible response বাদ — precision পরিমাপযোগ্য করা।
- **Path condition → test oracle/test generation:** “এই condition-এ 403” তথ্য দিয়ে REST fuzzer-কে নির্দেশিত করা (T1) — error-path coverage; P015-এর access-policy oracle-এর সঙ্গে সমন্বয় (Discourse-এর access-level-নির্ভর field = সম্ভাব্য information exposure)।
- **Access-control-নির্ভর response type → BOLA/data exposure audit** (T3): কোন role-এ কোন field দেখা যায় তা স্বয়ংক্রিয়ভাবে নথিভুক্ত।
- **Multi-language path-sensitive inference** (Python/TypeScript gradual type system-এ) এবং LLM-সহায়ক summary (P017-এর সঙ্গে hybrid)।
- Configuration-dependent response (site setting) — spec-এ conditional response প্রকাশের OpenAPI extension (P016 IDL-এর response-side সমতুল্য)।
- CI-তে handwritten spec বনাম inferred type checking (লেখকদের প্রস্তাব) — T5/T6 drift detection।

## O. Relationships
- **Complements P018 (Respector)** — উভয় static; Respector Java, symbolic execution, request-side শক্তিশালী; RESTπ Ruby, type-theoretic, response-side শক্তিশালী।
- **Complements P017 (OOPS)** — LLM বনাম formal; OOPS 2xx-only।
- **Builds on** RDL (Foster group-এর পূর্ববর্তী Ruby type inference), computed types।
- **Confirms P001/P004/P018:** auto-generated/dynamic spec-ও অসম্পূর্ণ।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract (১৩২ endpoint, ৫ API) | p.1 L10–19 |
| Proxy-ভিত্তিক spec-এর সমস্যা | p.1–2 L39–66 |
| Contributions | p.2 L82–87 |
| Discourse motivating example | p.2–4 L94–237 |
| Formal language, path types, rules | p.5–7 L316–451 |
| Singleton types | p.7–8 L468–525 |
| Computed types, as_json | p.8–9 L527–573 |
| Layered inference | p.9–10 L574–660 |
| Path-type merging, path-insensitive library | p.10–12 L662–804 |
| RQ1–RQ3 | p.12–13 L810–849 |
| Benchmark ও endpoint নির্বাচন | p.13 L855–875 |
| RQ1 (৫৪৫ response type) | p.13 L881–888 |
| RQ2 (১.৩৫৩ s; timeout) | p.15 L1175–1187 |
| RQ3 (+৭১.৯৭%, +১২৯.১৭%) | p.16 L1549–1555 |
| Additional field/required issue | p.17 L1556–1594 |
| Threats | p.17 L1597–1615 |

**Document integrity:** Body সম্পূর্ণ; inference rule (Fig.5) ও গ্রিক/গাণিতিক প্রতীক (φ, Γ, ⊎, ≤φ) আংশিক বিকৃত কিন্তু পাঠযোগ্য; Table 1–3 ও appendix per-endpoint table column-split — মোট সংখ্যা text থেকে; Fig.9 (runtime plot) অনুপস্থিত; পৃথক “Conclusion” অনুচ্ছেদ markdown-এ শনাক্ত হয়নি (related work-এর মধ্যে বা অনুপস্থিত — PDF-এ যাচাই প্রয়োজন)।
