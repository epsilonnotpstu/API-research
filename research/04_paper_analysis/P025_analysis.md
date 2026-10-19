# P025 — Differential Regression Testing for REST APIs

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (related work বাদ, references বাদ) · **উৎস:** ISSTA 2020 ACM version, ১২ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Patrice Godefroid, Daniel Lehmann, Marina Polishchuk (Microsoft Research; Lehmann তখন MSR-এ)
- **Venue:** ISSTA 2020, DOI 10.1145/3395363.3397374
- **Cluster:** T5 (secondary: T1 — RESTler-ভিত্তিক automated testing; T6 — spec/example quality)
- **ধরন:** নতুন testing technique + historical case study (industrial)

## B. Motivation
- Cloud REST API ঘন ঘন বদলায় (Azure-এ প্রায় মাসিক; Network API-র median interval ৬১ দিন); breaking change প্রধান সমস্যা — Azure-এর ১১২টি high-severity incident-এর অনেকগুলো software update-জনিত (p.1 L80–88; p.8 L1107–1110)।
- বর্তমান পদ্ধতি: হাতে-লেখা/রেকর্ড করা request দিয়ে pre-deployment testing (শ্রমসাধ্য), spec পরিবর্তন চোখে দেখা, staged rollout ও incident-নির্ভর শনাক্তকরণ (ব্যয়বহুল) (p.1 L89–107)।

## C. Research questions
- ⚠️ আনুষ্ঠানিক RQ নেই; মূল্যায়নের প্রশ্ন: কতগুলো regression পাওয়া যায়, কোন ধরনের; stateful বনাম stateless diffing; upper-triangular বনাম diagonal-only strategy; runtime ও manual effort।

## D. Contributions (p.2 L143–151)
- REST API-র জন্য differential regression testing; **service regression** ও **specification regression**-এর মৌলিক পার্থক্য; জটিলতা বিশ্লেষণ।
- Network log-এর stateful ও stateless diffing।
- Azure Networking-এর (৩০+ API) ১৭ version-এর ঐতিহাসিক বিশ্লেষণ — ১৪টি regression।

## E. Methodology
- **Client/service version matrix:** spec version i থেকে তৈরি client cᵢ, service sⱼ; (cₙ, sₙ) বনাম (cₙ, sₙ₊₁) → **service regression**; (cₙ, sₙ₊₁) বনাম (cₙ₊₁, sₙ₊₁) → **specification regression**; diagonal তুলনা (cₙ,sₙ বনাম cₙ₊₁,sₙ₊₁) এড়ানো — rename ধরতে পারে না (p.3–4 L299–510)।
- **জটিলতা:** upper-triangular matrix-এ T(N) = N(N+1)/2 configuration, D(N) = N(N−1) diff; **diagonal-only strategy**-তে ২(N−১) configuration ও ২(N−১) diff — backward-compatibility transitivity, deterministic test generation ও deterministic response ধরে নিলে সমান নির্ভুল (p.4–5 L446–590)।
- **Input generation:** RESTler (P006) — spec থেকে stateful sequence; client = RESTler-generated suite; `api-version` query parameter দিয়ে service version নির্বাচন (p.5 L595–608; p.8 L1130–1135)।
- **Log abstraction:** Date, Etag, x-request-id, Authorization, Content-Length, RESTler-এর random id (regex), service-নির্দিষ্ট non-deterministic মান প্রতিস্থাপন (p.6 L735–772)।
- **Stateful diff:** sequence-এর recursive bottom-up তুলনা (Myers diff string-এ) — service update-এর জন্য (body পরিবর্তন ধরে); **Stateless diff:** request type (method, abstracted path, header+body hash) অনুযায়ী group, শুধু status code, নতুন যোগ করা request বাদ — spec update-এর জন্য (ordering ও global state noise এড়ায়) (p.6–7 L774–1002)।
- Implementation ~২,২০০ LoC।

## F. Dataset ও setup
- Azure DNS API (৪ version, সর্বশেষ ৬০ file/৪,১৪২ লাইন JSON) ও Network APIs (২৩ version, সর্বশেষ ৪৩৫ file/৫৮,৪১৯ লাইন, ~৪০% example) — example-যুক্ত version নির্বাচন: DNS ৩, Network **১৭** (২০১৬-১২-০১ → ২০১৯-০৪-০১); request সংখ্যা ১৩২ → ৩৭২; মোট >৬০০,০০০ লাইন Swagger (p.7–8 L1008–1124)।
- DNS-এ ৬ log, Network-এ ১৫৩ log; ২৭৮টি diff (৬ + ২৭২) (p.8 L1137–1176)।

## G. Evaluation
- Regression সংখ্যা ও ধরন (manual inspection); diff আকার (stateful বনাম stateless, direction অনুযায়ী); strategy তুলনা; runtime।

## H. Results (author-reported)
- **১৪টি unique regression:** ৫টি specification regression (stateless diff), ৯টি service regression (stateful diff) — উভয় দিক প্রয়োজনীয় (p.8 L1187–1198)।
- **#১–৪: example payload ভাঙা** — যেমন publicIpAddress-এর example-এ `location` এক স্তর ওপরে সরানো → 200 থেকে 400; পরের version-এ ঠিক, আবার ২০১৮-১১-০১-এ একই ভুল (p.9 L1212–1278)।
- **#৫: endpoint rename/remove** (`interfaceEndpoints`) — GitHub issue-তে ব্যবহারকারীরা আগেই পেয়েছিল; owner “intentional, unannounced API” বলে গ্রহণযোগ্য বললেন, যদিও “-preview” suffix ছিল না (p.9 L1279–1293)।
- **#৬–১৪: response-এ unspecified property** (zoneType, ipTags, enableDdosProtection…) — Microsoft REST Guidelines অনুযায়ী নতুন response field-ও backward-incompatible; spec পরে আপডেট (p.9–10 L1294–1379)।
- ১৪টির মধ্যে ১২টি পরবর্তী version-এ fix বা অন্যভাবে নিশ্চিত (#৮, #৯ ছাড়া) (p.8 L1199–1203)।
- **Diff আকার:** stateful গড় ২.৭ MB/file বনাম stateless ৬ KB; spec-update-এ stateful ৬৭৮ MB (অব্যবহারযোগ্য) বনাম stateless ৫০৫ KB; service-update-এ stateless ৯৮% খালি (p.9 L1386–1410)।
- **Diagonal-only:** ২৭৮-এর বদলে ৩৬টি diff; stateful লাইন ৩৮৮,৭৫৭ → ৩৬,৬৩৭ (৯%); **তবু সব ১৪টি regression পাওয়া গেছে** (p.10 L1448–1471)।
- **খরচ:** Network API-র log সংগ্রহ ৩ দিন ৮ ঘণ্টা (৯২,৩৮১ request); diffing <১ ঘণ্টা; ২৭৮ diff হাতে বিশ্লেষণ ~১ সপ্তাহ (একজন PhD শিক্ষার্থী) (p.10 L1472–1488)।
- Continuous mode: DNS 2017-10-01 service revision-এ (৫ বনাম ১৯ May 2019) zoneType regression (p.10–11 L1519–1561)।

## I. Strengths
- **ধারণাগত স্বচ্ছতা:** service বনাম specification regression — REST evolution-এ দুই উপাদানের (client spec ও service) পৃথক বিবর্তন; P020-এর practitioner উদ্বেগের (structural/behavioral) tool-স্তরের উত্তর।
- **Industrial, বাস্তব, ঐতিহাসিক** মূল্যায়ন — production Azure service, public spec।
- Version matrix-এর জটিলতা বিশ্লেষণ ও **diagonal-only** strategy — ব্যবহারিক খরচ রৈখিক।
- Oracle-free (differential) — P003/P008-এর oracle সমস্যার একটি সমাধান-ধারা।
- Behavioral পরিবর্তন (response body) ধরে — শুধু structural spec diff নয়।

## J. Explicit limitations (p.10 Threats)
- RESTler-এর coverage-নির্ভর — কম exercise হলে regression মিস; input generator পরিবর্তনযোগ্য।
- Diffing implementation-এর কার্যকারিতা — উন্নত diff algorithm দিয়ে false positive কমানো ভবিষ্যৎ কাজ।
- ফল নির্দিষ্ট API ও bug-এর উপর নির্ভরশীল (Azure Networking)।
- Diagonal-only তিনটি assumption ভাঙলে (non-determinism ইত্যাদি) বেশি মিস করতে পারে (p.5)।

## K. Inferred limitations (⚠️ অনুমান)
- **Manual inspection-নির্ভর oracle:** diff স্বয়ংক্রিয়, কিন্তু regression সিদ্ধান্ত মানুষের — ২৭৮ diff-এ ~১ সপ্তাহ; **false positive/precision সংখ্যা রিপোর্ট নেই** (কতগুলো diff noise ছিল)।
- **Ground truth/recall অজানা:** ১৪টি “পাওয়া” — কতগুলো মিস হয়েছে তার মূল্যায়ন নেই; RESTler-এর অসম্পূর্ণ coverage স্বীকৃত।
- **একটি মাত্র কোম্পানির একটি service family** (Azure Networking, এক spec repository) — লেখকরা “distinct APIs” বলেন কিন্তু একই সংস্থার governance; অন্য provider-এ (date-version ছাড়া, multiple active version ছাড়া) প্রয়োগযোগ্যতা অপরীক্ষিত।
- **পুরোনো service version চালু থাকা আবশ্যক** — Azure সব version জীবিত রাখে; অধিকাংশ API পুরোনো version বন্ধ করে দেয় (P020) → historical diff অসম্ভব; continuous mode-এই সীমিত।
- Stateless diff শুধু status code — response body-র semantic regression spec-direction-এ মিস।
- Regression-এর severity/client impact মাপা হয়নি (P023-এর “BC ঘটে বনাম client ভাঙে” প্রশ্ন)।
- Tool উন্মুক্ত বলে উল্লেখ নেই (“plan to deploy widely”) — reproducibility সীমিত।

## L. Threats to validity
- উপরে J; inferable: construct (manual regression labeling), external (এক provider)।

## M. Reproducibility
- Azure spec GitHub-এ public, service version-গুলো Azure subscription দিয়ে প্রবেশযোগ্য; কিন্তু **diffing tool প্রকাশের উল্লেখ নেই**; RESTler পরে open-source — **মাঝারি-নিম্ন**।

## N. Opportunities (hypothesis)
- **Automated regression triage:** diff → regression classification (LLM/rule) — manual সপ্তাহব্যাপী effort কমানো; precision/recall benchmark তৈরি।
- **Differential + invariant oracle:** P008 AGORA invariant-কে version-জুড়ে তুলনা — semantic/behavioral regression (P020-এর ৫/১৭ সমস্যা) ধরা।
- **Open benchmark of REST API version histories** (P021 UC-1; P023-এর REST সমতুল্য) — এই পদ্ধতির পুনরাবৃত্তি ও তুলনা।
- **Consumer-impact weighting:** gateway log থেকে প্রকৃত ব্যবহৃত endpoint/field দিয়ে regression অগ্রাধিকার (P023-এর ধারণা REST-এ)।
- **Microservice CI integration** (P038, P037 সংযোগ) — service revision-স্তরের continuous differential testing; contract testing (Pact)-এর সঙ্গে তুলনা।
- **Agent-facing API regression:** MCP/tool schema version diff (P022/P036) — একই matrix ধারণা।

## O. Relationships
- **Built on P006 (RESTler)** — একই MSR group।
- **Cited by P020** (regression testing strategy-র tool সমাধান হিসেবে)।
- **Complements P023** (library BC, binary-স্তর) — এটি REST, runtime/behavioral স্তর।
- **Confirms P001/P004/P018:** spec ও service অসঙ্গতি (unspecified property ৯টি)।
- **Relates to P028** (documentation smell) — example payload ভুল = documentation quality।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract (১৭ version, ১৪ regression) | p.1 L25–49 |
| Motivation, incident উল্লেখ | p.1 L80–107 |
| Contributions | p.2 L143–151 |
| Service বনাম spec regression | p.3 L299–377 |
| Version matrix, T(N), D(N) | p.3–4 L391–534 |
| Diagonal-only strategy | p.4–5 L540–590 |
| RESTler ব্যবহার | p.5 L595–608 |
| Log abstraction | p.6 L735–772 |
| Stateful/stateless diffing | p.6–7 L774–1002 |
| Azure API dataset (Table 1, Fig.8) | p.7–8 L1008–1124 |
| Experimental procedure | p.8 L1130–1180 |
| Table 2 (১৪ regression) | p.8 L1045–1105, L1187–1203 |
| Regression উদাহরণ | p.9 L1212–1379 |
| Stateful vs stateless (Table 3) | p.9 L1386–1410 |
| Diagonal-only (Table 4–5) | p.10 L1448–1471 |
| Runtime, manual effort | p.10 L1472–1488 |
| Threats | p.10 L1492–1514 |
| Continuous mode | p.10–11 L1519–1561 |

**Document integrity:** Body সম্পূর্ণ; জটিলতা সূত্র (T(N) পূর্ণ রূপ) আংশিক হারিয়েছে; Table 1–5 column-split — Table 2-এর regression তালিকা আংশিক পাঠযোগ্য; Figure 1–4, 8–9 অনুপস্থিত; section 2-এর কিছু heading auto-detect হয়নি।
