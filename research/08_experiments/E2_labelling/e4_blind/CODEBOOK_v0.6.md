# R1 Triage Codebook — v0.6 (labeller copy)

**তারিখ:** 2026-11-09 · **উদ্দেশ্য:** OpenAPI conformance failure-কে **উৎস (attribution)** অনুযায়ী label করার নিয়ম।
- Manual labelling (বাস্তব failure) ও injected ground truth (§5) — দুটোতেই একই scheme।

**অবস্থা:** খসড়া।
- v0.2-এ P001-এর ১৪৭টি confirmed fault-এর বিশ্লেষণ থেকে সংযোজন (§8; `E1_pilot/P001_empirical_findings.md`)।
- Pilot labelling (roadmap E2)-এর পরে আবার সংশোধন হবে।

⚠️ **নতুনত্ব:** এই scheme আমাদের প্রস্তাব। নিচের উৎসগুলোর কোনোটিই spec defect বনাম implementation fault আলাদা করেনি।
- **P001:** oracle category।
- **2504.08113:** “API Bug Exposed” = যেকোনো অমিল।
- **RESTifAI:** Bug / Enhancement / Invalid।

---

## 1. মৌলিক সংজ্ঞা

- **Conformance failure:** একটি request-response জোড়া, যেখানে observed আচরণ OpenAPI spec-এর সাথে মেলে না। উদাহরণ:
  - Response schema লঙ্ঘন।
  - Undocumented status code।
  - Spec-অনুযায়ী অবৈধ input-এ 2xx।
  - Spec-অনুযায়ী বৈধ input-এ 4xx।
  - এগুলো P001-এর F_OAS, F_2XXP/D, F_400-এর সমতুল্য।
- **Intended behaviour:** API-র প্রকৃত উদ্দেশ্য। এটি spec বা code — কোনোটিই স্বয়ংক্রিয়ভাবে নয়। প্রমাণ থেকে অনুমান করতে হয় (§3)।

## 2. Label (Level 1 — attribution)

| Label | সংজ্ঞা | উদাহরণ |
|---|---|---|
| **SPEC** | Implementation-ই intended আচরণ করছে; spec ভুল বা অসম্পূর্ণ | Response-এ `nickname` field আছে, spec-এ নেই এবং `additionalProperties: false` |
| **IMPL** | Spec-ই intended আচরণ বর্ণনা করে; implementation ভুল | Spec বলছে `limit ≤ 100`; `limit=500`-এ 2xx এবং ভুল data |
| **BOTH** | দুটোই intended আচরণ থেকে বিচ্যুত | Spec বলে 404; code দেয় 500; intended হলো 400 |
| **TEST** | Failure-টি test বা tool-এর সৃষ্টি: ভুল oracle, ভুল fixture, অসম্ভব data অনুমান | Tool ধরে নিয়েছে ID 9999 অস্তিত্বহীন (2504.08113-এর “Missing Information”) |
| **ENV** | Non-determinism বা পরিবেশ: rate limit, timeout, outage, quota, clock | 429 বা 503 (P001-এ DHL ban, Ohsome outage) |
| **UNDECIDABLE** | প্রমাণ অপর্যাপ্ত | Spec ও code পরস্পরবিরোধী, অন্য কোনো প্রমাণ নেই |

## 3. প্রমাণের উৎস ও অগ্রাধিকার (intended behaviour নির্ধারণ)

ক্রমানুসারে শক্তিশালী থেকে দুর্বল। একাধিক উৎস মিললে আস্থা বাড়ে।

1. **E-DEV:** developer-এর নিশ্চিতকরণ বা fix।
   - Issue বা commit; P001-এর `bugs_reported.csv`-এর `confirmed` ও `fixed` কলাম।
   - Fix code-এ হলে → IMPL। Fix spec-এ হলে → SPEC।
2. **E-DOC:** spec-এর বাইরের prose documentation বা README।
   - এটি সাধারণত spec-এর চেয়ে মানুষের উদ্দেশ্য বেশি প্রতিফলিত করে।
   - SpecFix (P032)-এর তুলনা-উৎস।
3. **E-CODE-INTENT:** code-এ স্পষ্ট উদ্দেশ্যের চিহ্ন।
   - Validation annotation (`@Valid`, `@Max`)।
   - Explicit exception handler।
   - Code-derived spec (Respector P018, RestPi P019)।
   - Code-এ ইচ্ছাকৃত আচরণ → SPEC-এর দিকে ঝোঁক।
   - Unhandled exception বা 5xx → IMPL-এর দিকে।
4. **E-CONSIST:** একই operation-এ বহু request-এর সামঞ্জস্য।
   - একটি field সব response-এ উপস্থিত থাকলে তা ইচ্ছাকৃত (→ SPEC)।
   - বিক্ষিপ্তভাবে থাকলে implementation-এর অনিয়ম হতে পারে।
5. **E-CROSS:** একই API-র অন্য operation বা পুরোনো version-এর আচরণ।
   - P025-ধাঁচের version diff।
6. **E-CONV:** HTTP বা REST convention।
   - উদাহরণ: অবৈধ input-এ 5xx প্রায় সবসময় IMPL (P001-এর F_5XXI)।
   - P026/P027-এর design rule।

**Tie-break নিয়ম:**
- **R1:** 5xx response সর্বদা অন্তত IMPL — হয় IMPL নয়তো BOTH।
- **R2:** Response-এ অতিরিক্ত field যা সব request-এ সামঞ্জস্যপূর্ণ (E-CONSIST) এবং code-এ ইচ্ছাকৃত → SPEC।
- **R3:** Spec-অনুযায়ী অবৈধ input-এ 2xx:
  - Code-এ সেই constraint-এর কোনো চিহ্ন না থাকলে, এবং documentation-ও constraint না বললে → **SPEC** (spec অতিরিক্ত কঠোর; 2607.12101-এর REQUEST_STRICT-এর বাস্তব রূপ)।
  - Documentation constraint বললে → **IMPL** (P001-এর F_2XXP/D-এর “invalid input accepted”)।
- **R4:** 429, 503 বা timeout → ENV। তবে একই input-এ ধারাবাহিকভাবে পুনরুৎপাদনযোগ্য হলে পুনর্বিবেচনা।
- **R5:** কোনো উৎসই সিদ্ধান্ত না দিলে → UNDECIDABLE। এটি অনুমান দিয়ে পূরণ করা যাবে না।

## 4. Level 2 — ত্রুটির ধরন (locus)

### SPEC-এর উপধরন
2607.12101-এর fault class, P032-এর A–C এবং P018/P019-এর পর্যবেক্ষণ থেকে।

| কোড | ধরন | সংশ্লিষ্ট উৎস |
|---|---|---|
| S-RESP-MISSING | Response-এ undocumented property, বা `required` অতিরিক্ত | P025 (unspecified properties), P019 |
| S-RESP-TYPE | Response property-র type বা format ভুল (যেমন nullable অনুপস্থিত) | P001 F_OAS |
| S-STATUS | Undocumented status code (বিশেষত non-200) | P019 (+১২৯% non-200), RESPONSE_ORACLE |
| S-REQ-STRICT | Spec-এর request constraint implementation-এর চেয়ে কঠোর | REQUEST_STRICT |
| S-REQ-LOOSE | Spec-এর constraint শিথিল বা অনুপস্থিত (implementation বেশি কঠোর → বৈধ-দেখানো input-এ 4xx) | REQUEST_LOOSE, P018 (constraint recall ৫০%) |
| S-METHOD | Method বা path semantics ভুল | METHOD_SEM |
| S-CONFIG | Auth, base URL, header বা prefix | P032 SpecFix A–C |
| S-STRUCT | `$ref` বা structural ত্রুটি | PARSE_BROKEN_REF |

### IMPL-এর উপধরন

| কোড | ধরন | সংশ্লিষ্ট উৎস |
|---|---|---|
| I-CRASH | 5xx (valid বা invalid input-এ) | P001 F_5XXV/F_5XXI, EvoMaster |
| I-ACCEPT-INVALID | অবৈধ input গ্রহণ (2xx যেখানে 4xx প্রত্যাশিত) | P001 F_2XXP/D |
| I-REJECT-VALID | বৈধ input প্রত্যাখ্যান (4xx যেখানে 2xx প্রত্যাশিত) | P001 F_400 |
| I-RESP-CONTRACT | Documented response contract লঙ্ঘন, যেখানে spec authoritative | P001 F_OAS (IMPL অংশ) |
| I-SEMANTIC | Contract-এর মধ্যে থেকেও ভুল data বা business logic | RESTifAI (200 কিন্তু ভুল), সাধারণত conformance-এর বাইরে |

## 5. Injected ground truth-এর সাথে মানচিত্র (দ্বিমুখী injection, E0 §4)

| Injection | প্রত্যাশিত Level 1 | প্রত্যাশিত Level 2 |
|---|---|---|
| Spec mutation: SCHEMA_LOOSE / REQUEST_LOOSE | SPEC | S-REQ-LOOSE |
| Spec mutation: REQUEST_STRICT | SPEC | S-REQ-STRICT |
| Spec mutation: RESPONSE_ORACLE (500 মুছে ফেলা, 2xx schema কঠোর করা) | SPEC | S-STATUS / S-RESP-TYPE |
| Spec mutation: METHOD_SEM | SPEC | S-METHOD |
| Code mutation: validation সরানো | IMPL | I-ACCEPT-INVALID |
| Code mutation: exception বা null path | IMPL | I-CRASH |
| Code mutation: response mapping পরিবর্তন | IMPL | I-RESP-CONTRACT |

**সতর্কতা:**
- Injection-এর আগেই baseline-এ কিছু failure থাকে (বাস্তব অমিল)। এগুলো injection-এর label পাবে না।
- এদের আলাদা করার নিয়ম: baseline run-এর failure set থেকে বিয়োগ (set difference) এবং fingerprint মেলানো (operation + status + violation path)।

## 6. Labelling প্রক্রিয়া

1. **Unit:** একটি failure cluster। Fingerprint = operation + status code + violation JSON path + oracle type। P001-এর clustering-এর অনুরূপ। প্রতিটি cluster থেকে একটি প্রতিনিধি request।
2. **Labeller:** দুইজন, স্বাধীনভাবে। প্রতিটি label-এর সাথে ব্যবহৃত প্রমাণ-কোড (E-DEV … E-CONV) রেকর্ড করতে হবে।
3. **Pilot:** ৫০টি cluster → Cohen's κ (লক্ষ্য ≥ ০.৭) → মতভেদ আলোচনা করে codebook v0.2।
4. **পূর্ণ labelling:** বাকিগুলো; মতভেদে তৃতীয় ব্যক্তি বা supervisor চূড়ান্ত সিদ্ধান্ত নেবেন।
5. **রেকর্ড:** CSV — `cluster_id, op, status, violation_path, label_L1, label_L2, evidence_codes, labeller, confidence(1-3), note`।

## 7. খোলা প্রশ্ন (pilot-এ যাচাই)

- BOTH কি যথেষ্ট ঘন ঘন আসবে যে আলাদা শ্রেণি দরকার, নাকি Level 2-তে একীভূত করা যায়?
- I-SEMANTIC conformance failure নয় — R1-এর পরিধি থেকে বাদ রাখা উচিত কি?
- P001-এর বাস্তব API-তে (closed source) E-CODE-INTENT অনুপস্থিত। তখন label-এর আস্থা কীভাবে কমানো হবে?

## 8. v0.2 সংযোজন (P001 বিশ্লেষণ থেকে, 2026-11-09)

1. **Strictness চিহ্ন — `STRICT_ONLY`:**
   - Violation যদি কেবল OpenAPI-র ডিফল্টের চেয়ে কঠোর validator-এ ঘটে, তবে আলাদা চিহ্ন দিতে হবে। যেমন undeclared property, যখন `additionalProperties` উল্লেখ নেই।
   - এমন ক্ষেত্রে default L1 = SPEC (S-RESP-MISSING)। কারণ implementation OpenAPI semantics লঙ্ঘন করছে না।
   - তবে label-এর পাশে `STRICT_ONLY=true` রাখতে হবে।
   - P001-এ F_OAS-এর ৯/৭৩ (১২%) এই শ্রেণির।
2. **সহায়ক constraint-উৎস — প্রমাণ-কোড `E-AUX`:**
   - Constraint OpenAPI-তে না থেকে IDL, test configuration বা prose-এ থাকতে পারে।
   - P001-এ F_2XXD-এর ৮/৮টি এবং F_2XXP-এর অন্তত কয়েকটি এমন।
   - তখন request-side failure-এর label নির্ভর করবে সেই উৎসের কর্তৃত্বের উপর:
     - উৎস developer-প্রকাশিত হলে → IMPL হতে পারে, আর spec-এ constraint যোগ করা উচিত (S-REQ-LOOSE)।
     - উৎস tester-নির্মিত হলে → TEST হতে পারে।
3. **TYPE_NULL নিয়ম:**
   - Response-এ `null`, অথচ spec-এ `nullable` বা `x-nullable` নেই।
   - একই field অন্য response-এ null ও non-null দুটোই হলে (E-CONSIST) → SPEC / S-RESP-TYPE (nullable বাদ পড়েছে)।
   - সবসময় null হলে → field-এর অস্তিত্ব নিয়ে প্রশ্ন; তখন UNDECIDABLE বা IMPL।
   - P001-এ ১৯টি fault, যার একটিতেও developer উত্তর দেননি।
4. **Spec-এর নিজস্ব গঠনগত ত্রুটি:**
   - Pattern-এর double-escape (Amadeus), Java-only regex (`\p{L}`), অসঙ্গত `oneOf`।
   - এদের SPEC / S-RESP-TYPE বা S-STRUCT হিসেবে label দিতে হবে।
   - পরীক্ষা: সঠিক-দেখানো মান কি pattern-এর সাথে **কোনোভাবেই** মেলা সম্ভব?
5. **COMPOSITION (oneOf/allOf/anyOf ব্যর্থতা):**
   - প্রথমে যাচাই করতে হবে schema-টি নিজে satisfiable কিনা। যেমন `oneOf`-এর দুটি শাখা একই instance-এ মিলে যায় কিনা।
   - Satisfiable না হলে → SPEC।

## 9. v0.3 পরিবর্তন (2026-11-13)

**উৎস:** তিনটি label-সেটের তুলনা — rule baseline, T2 triage, T3 blind LLM labeller (`E2_labelling/comparison_rule_triage_codex.csv`) — এবং Codex-এর T3 প্রস্তাব।
মতভেদের বড় অংশ এসেছে নিচের তিনটি অস্পষ্টতা থেকে।

### 9.1 Label-এর একক: message-স্তর → cluster-স্তর (aggregation)
- **প্রথমে message-স্তরে label:** প্রতিটি violation message আলাদা L1/L2 পায়।
- **Cluster-এর L1 নির্ণয়ের নিয়ম:**

| Message-স্তরের ফল | Cluster L1 |
|---|---|
| সব message একই L1 (SPEC / IMPL / ENV / TEST) | সেই L1 |
| কিছু SPEC, বাকি UNDECIDABLE | **SPEC_PARTIAL** |
| কিছু IMPL, বাকি UNDECIDABLE | **IMPL_PARTIAL** |
| SPEC ও IMPL দুটোই প্রমাণিত | **BOTH** — প্রতিটি দিক আলাদা প্রমাণসহ |
| কোনো message-এ সিদ্ধান্ত নেই | UNDECIDABLE |

- **মূল্যায়নে:**
  - Strict scoring-এ `*_PARTIAL` = UNDECIDABLE।
  - Lenient scoring-এ `*_PARTIAL` = সংশ্লিষ্ট L1।
  - দুটোই রিপোর্ট করতে হবে।
- ⇒ কোনো “decisive” ব্যতিক্রম নেই। যেমন Amadeus F004–F006-এ double-escape SPEC, কিন্তু missing `fax` UNDECIDABLE → cluster = **SPEC_PARTIAL**।

### 9.2 Strict-only violation = oracle policy, SPEC নয়
- §8.1 সংশোধিত হলো। যে message কেবল OpenAPI-র ডিফল্টের চেয়ে কঠোর validator-এ violation (undeclared property, যখন `additionalProperties` অনুল্লিখিত), তার L1 = **TEST**, L2 = **T-ORACLE-STRICT**।
- কারণ: OpenAPI semantics-এ implementation বা spec কোনোটিই লঙ্ঘন করেনি — oracle-এর নীতি কঠোর।
- **Documentation completeness আলাদা attribute:** `doc_gap=true`, যদি field-টি public documentation-এ থাকে কিন্তু schema-তে না থাকে।
- P001-এ এর প্রভাব:
  - ৯টি পুরোপুরি strict-only fault → TEST।
  - বাকি ১৮টিতে undeclared-property message TEST, আর cluster aggregation §9.1 অনুযায়ী।

### 9.3 প্রমাণের নিয়ম
- **E-DOC (web):** বর্তমান public documentation গ্রহণযোগ্য, তবে confidence ≤ ২। Retrieval তারিখ ও URL বাধ্যতামূলক। Documentation পরে বদলে থাকতে পারে — ঐতিহাসিক অমিলের ঝুঁকি।
- **Developer evidence-এর দিক:** `confirmed` বা `fixed` একা attribution নয়। Fix কোথায় হয়েছে — spec, code বা documentation — তার URL বা commit না থাকলে কেবল “সমস্যা স্বীকৃত” অর্থে ব্যবহার করতে হবে।
- **R1 বনাম R4-এর অগ্রাধিকার:**
  - 429, 502, 503, 504 এবং gateway বা timeout body → **ENV** (R4 অগ্রাধিকার পায়)।
  - অন্য সব 5xx → IMPL (R1)।
- **R3 (closed-source):** code না দেখে “code-এ constraint নেই” ধরা যাবে না। Closed-source API-তে R3 প্রযোজ্য নয়।
- **Malformed JSON body:** documented JSON response-এর body syntactically invalid হলে → **IMPL / I-RESP-CONTRACT** (P001 F047)।

### 9.4 নতুন Level-2 code
- `S-MEDIA` — Content-Type বা media type undocumented।
- `S-RESP-VALUE` — enum বা range অসম্পূর্ণ।
- `T-ORACLE-STRICT` — §9.2।

### 9.5 Composition (oneOf/allOf/anyOf) — তিনটি পরীক্ষা আলাদা করতে হবে
1. Schema কি globally unsatisfiable?
2. Representative instance কি একাধিক branch-এ match করে (oneOf ভঙ্গ)?
3. Converter বা validator-এর সমস্যা কিনা (যেমন nullable parent-এ `type` না থাকা)?

প্রতিটির witness রেকর্ড করতে হবে। Branch-এর নাম দেখে সিদ্ধান্ত দেওয়া যাবে না।

### 9.6 তিন label-সেটের তুলনা (v0.2 দিয়ে labelled; ভিত্তি-চিত্র)
| তুলনা | মিল | Cohen's κ |
|---|---|---|
| T3 LLM বনাম rule baseline | ৪৯.৩% | ০.১০ |
| T3 LLM বনাম T2 triage | ৬১.৬% | ০.৩৫ |

⚠️ কোনোটিই ground truth নয়। মানব labeller-এর label এখনো বাকি।

## 10. v0.4 সংযোজন — supervisor adjudication থেকে নিয়ম (2026-11-14)
উৎস: `E2_labelling/batch2_AB_agreement.md` (scout, T15) এবং `E2_labelling/petstore_market_AB_agreement.md` (petstore/market, T16)।

### 10.1 BOTH-এর রীতি (Q1)
- Labeller সবসময় একটি **প্রাথমিক L1** দেবে (যেমন 5xx → IMPL, R1 অনুযায়ী) এবং আলাদা `both_candidate` flag দেবে। প্রতিটি দিকের প্রমাণ আলাদা থাকবে।
- **চূড়ান্ত L1 = BOTH কেবল supervisor-এর adjudication-এ** নির্ধারিত হবে। Labeller সরাসরি BOTH লিখবে না।

### 10.2 Open-schema বনাম কঠোর binding (T15)
- Schema খোলা (`additionalProperties` অনুল্লিখিত), অথচ server অঘোষিত property প্রত্যাখ্যান করে, আর কোনো পক্ষেই intent-এর স্পষ্ট প্রমাণ নেই → **UNDECIDABLE** (policy-ambiguous)।

### 10.3 Container বা framework policy বনাম খোলা spec (Q3)
- বৈধ কিন্তু container-এর default নিরাপত্তা নীতিতে আটকানো input (যেমন Tomcat-এ `%5C`), যেখানে spec কোনো বাধা দেয় না → **UNDECIDABLE**।
- কিন্তু সত্যিই অবৈধ HTTP (যেমন header-এ control character) → **TEST**।

### 10.4 Aggregation: SPEC + TEST মিশ্রণ (Q2)
- §9.1-এর টেবিলে নতুন সারি: **কিছু SPEC, বাকি TEST (checker বা generator-এর false positive) → SPEC_PARTIAL**।
- Strict scoring-এ এটি UNDECIDABLE, lenient scoring-এ SPEC।
- ⚠️ [H] প্রতিসম নিয়ম "কিছু IMPL, বাকি TEST → IMPL_PARTIAL" প্রস্তাবিত, এখনো সিদ্ধান্ত হয়নি।

### 10.5 প্রস্তাবিত TEST L2 code (দুই labeller-ই স্বাধীনভাবে প্রস্তাব করেছে; চূড়ান্ত নাম বাকি)
- `T-ORACLE-COVERAGE`: checker request body validate করতে পারেনি (XML, form, binary)।
- `T-ORACLE-FORMAT`: checker int32/int64 format-এর সীমা enforce করে না, তাই অবৈধ input-কে বৈধ ধরে। B-র নাম `T-ORACLE-NUMERIC-FORMAT`।
- `T-PROBE`: fuzzer-এর capability probe traffic। B-র নাম `T-PROBE-CONTAMINATION`।
- `T-GEN-INVALID-HTTP`: generator অবৈধ HTTP পাঠিয়েছে। B-র নাম `T-TRANSPORT-INPUT`।

### 10.6 চূড়ান্ত BOTH-এর নিয়ম (supervisor-অনুমোদিত, 2026-11-14)
- **Spec-এ ঐচ্ছিক, অথচ অনুপস্থিত হলে code crash:**
  - অনুপস্থিত জিনিসটি resource-এর key, create-এর body বা NOT NULL persistent field হলে → **BOTH** (spec-এরও required বলা উচিত ছিল)।
  - Resource অস্তিত্বহীন বলে crash (404 প্রত্যাশিত), বা অনুপস্থিত মান server নিজে সামলাতে পারত (যেমন create-এ id তৈরি) → **IMPL**।
- **Spec-এর type বা structure ভুল, আর code সেই ভুলকে 5xx-এ পরিণত করে** (যেমন market-এর `_links`) → **BOTH**।
- **Spec নিজের ভেতরেই অসংগত** (request parameter-এ enum নেই, model-এ আছে), আর code অবৈধ মান সংরক্ষণ করে → **BOTH** (প্রাথমিক L1: IMPL)।

### 10.7 BOTH নয় এমন ক্ষেত্র
- Code ইচ্ছাকৃতভাবে একটি status দেয় যা spec ঘোষণা করে না, কিন্তু status-টি HTTP-অর্থে অনুপযুক্ত (যেমন validation-এ 406) → **SPEC / S-STATUS**। HTTP-অর্থের সমস্যা আলাদা note-এ থাকবে; code-ত্রুটি হিসেবে গণনা হবে না।
- এক দিক ঠিক করলেই সমস্যা মেটে (যেমন JSON বলে plain text ফেরত: code-এ quote, অথবা spec-এ `text/plain`) → **IMPL** (§9.3)।
- Spec-এর documented `default` server-এর প্রতিশ্রুতি; code সেটা না মানলে → **IMPL / I-REJECT-VALID**।

### 10.8 SUT-ভিত্তিক rejection status (oracle variant; supervisor-এর সিদ্ধান্ত, 2026-11-14)
- **Default oracle:** VALID_REJECTED জ্বলে কেবল 400/422-এ।
- **SUT oracle:** code-এ স্পষ্ট প্রমাণ থাকলে (explicit validation handler) সেই SUT-এর জন্য অতিরিক্ত rejection status মানা যায়।
  - যেমন market: 400, 406, 422 (`RestExceptionHandler.java:63-64,73-74`)।
  - Config: `harness_v2/suts/<sut>.env`-এর `REJECT_STATUSES_DEFAULT`।
- **রিপোর্টিং:** দুটো oracle-এর ফলই পাশাপাশি রিপোর্ট হবে।
  - `analyse_run.sh`-এর default হলো SUT oracle।
  - `ORACLE=default` দিলে analysis চলে generic oracle দিয়ে; output যায় `analysis-<mode>-default`-এ।
- **আগের সংস্করণ:** 2026-11-14-এর আগের সব analysis (আর চূড়ান্ত label) default oracle দিয়ে করা।

## 11. v0.5 সংশোধন (supervisor-এর সিদ্ধান্ত, 2026-11-14)

### 11.1 §10.7-এর সংশোধিত রূপ (আগের §10.7-এর প্রথম বুলেটের জায়গা নেবে)
"Code ইচ্ছাকৃতভাবে undocumented status দেয় → SPEC/S-STATUS" প্রযোজ্য হবে **কেবল যখন code-এর বাইরে বা একাধিক জায়গায় স্বাধীন intent-প্রমাণ থাকে**। এর অন্তত একটি থাকতে হবে:
- ওই status assert করে এমন test (unit বা integration);
- documentation, README বা API guide;
- commit message, issue বা changelog;
- একই নীতি একাধিক স্বাধীন জায়গায় (যেমন market-এর 406: দুটো আলাদা exception handler)।

একমাত্র প্রমাণ যদি ওই একটা code লাইন বা annotation হয় → **UNDECIDABLE**, `both_candidate=true`। কারণ code পড়ে ইচ্ছাকৃত নকশা আর ইচ্ছাকৃত-দেখতে ভুলকে আলাদা করা যায় না।

### 11.2 সাধারণীকরণ
একই যুক্তি অন্য explicit "ইচ্ছাকৃত-দেখতে" code-এও প্রযোজ্য (যেমন serialization annotation, explicit guard)। E-CODE-INTENT একা থাকলে confidence ≤ 2। Intent-ভিত্তিক SPEC label-এর জন্য উপরের স্বাধীন প্রমাণ লাগবে।

### 11.4 Intent-evidence search procedure (v0.6)
§11.1–11.2 বলে, কোনো intent-ভিত্তিক সিদ্ধান্তে code-এর বাইরের স্বাধীন প্রমাণ লাগে। §11.4 সেই প্রমাণ খোঁজার নিয়মবদ্ধ পদ্ধতি।

**11.4.1 কখন search বাধ্যতামূলক**
- **বাধ্যতামূলক:**
  - (a) intent-নির্ভর যেকোনো SPEC বা SPEC_PARTIAL candidate, বিশেষত S-STATUS, guard-নির্ভর S-REQ-STRICT/LOOSE আর serialization-নির্ভর S-RESP-*;
  - (b) code দেখে IMPL বনাম SPEC আলাদা করা যাচ্ছে না, অর্থাৎ UNDECIDABLE বা both_candidate;
  - (c) intent-নির্ভর IMPL candidate, যেখানে spec আর code বিরোধী আর test/doc সিদ্ধান্ত বদলাতে পারে। শুধু spec-কে authoritative ধরে IMPL দেওয়া এখানে যথেষ্ট নয়।
- **বাধ্যতামূলক নয়:** deterministic নিয়ম যখন intent না জেনেই message নির্ধারণ করে। যেমন:
  - global schema contradiction;
  - strict-only oracle failure;
  - malformed documented JSON;
  - নির্দিষ্ট ENV বা non-gateway 5xx নিয়ম।

  তখন `intent_search_status=not_run` দিন, সঙ্গে প্রযোজ্য নিয়মটা।
- **আগে target proposition লিখুন:** side (request/response), method + path template, scenario, status/field আর দিক (presence/absence, constraint আঁটসাঁট/শিথিল)। Status-only search দিয়ে body বা field-presence obligation-এর সিদ্ধান্ত নেওয়া যাবে না।

**11.4.2 Tool আর ক্রম**
- **Tool:** `/usr/bin/python3 -I -B ../../tools/intent_evidence.py K??/source K??/spec.json --method M --path TEMPLATE [--status OBSERVED] [--field F] --json`।
  - `--status`-এ দিন observed status, কাঙ্ক্ষিত status নয়।
  - Stdout JSON, stderr আর exit code নিজের `search/` folder-এ রাখুন।
- **Review-এর ক্রম:** HANDLER → E-TEST → E-DOC → E-CONSIST → E-HISTORY। প্রথম অনুকূল hit পেয়ে থামবেন না।
  1. **HANDLER** শুধু context, স্বাধীন প্রমাণ নয়। Return, annotation বা guard আচরণের অস্তিত্ব দেখায়, intent নয়।
  2. **E-TEST:** assertion-টা একই operation, method, scenario আর branch-এর status বা field assert করে কিনা দেখুন।
     - Helper prefix আর fixture resolve করুন।
     - একই route-এর success assertion error-branch-এর intent নয়।
     - Linkage-হীন অন্য module-এর test প্রমাণ নয়।
     - Positive test-এর অনুপস্থিতি implementation intent-এর প্রমাণ নয়।
  3. **E-DOC:** README, guide বা changelog-এর সংশ্লিষ্ট অনুচ্ছেদ পুরোটা পড়ুন।
     - শুধু কাছাকাছি থাকা hit প্রমাণ নয়: পাশের operation, success row-এর পাশে error row, incidental নাম বা সংখ্যা।
     - Handler-এর Javadoc বা `@ApiResponse` স্বাধীন ধরা হবে কেবল আলাদা normative উৎস থাকলে। প্রশ্নবিদ্ধ code বা spec-এর পুনরুক্তি স্বাধীন নয়, কারণ spec প্রায়ই annotation থেকেই তৈরি হয়।
  4. **E-CONSIST:** একই নীতি একাধিক স্বাধীন জায়গায়, প্রতিটির locator সহ।
     - Repeated traffic বা একই line-এর একাধিক hit স্বাধীনতা নয়।
     - একই class-এর ভেতরের একাধিক method-কে স্বাধীন ধরবেন কিনা অস্পষ্ট হলে: `L1=UNDECIDABLE`, `adjudication_flag=same_class_policy`।
  5. **E-HISTORY:** এই package-এ VCS history নেই, তাই `history_scope=unavailable`। এটা নিজে coverage gap নয়।
- **স্বাধীনতার checklist,** প্রতিটি accepted hit-এ:
  - (a) প্রত্যাশিত আচরণ স্পষ্ট?
  - (b) target scenario-র সঙ্গে linkage আছে?
  - (c) প্রশ্নবিদ্ধ line বা spec থেকে আলাদা ভিত্তি?
  - (d) প্রযোজ্য revision?
  - (e) বিপরীত প্রমাণ দেখা হয়েছে?

**11.4.3 Tool verdict থেকে label**
- Raw verdict কখনো নিজে label নয়।
- Tool-এর `independent=true` চিহ্ন একটা hypothesis। প্রতিটি hit review করুন: accept, reject, context বা unresolved, কারণ সহ।

| Raw verdict | অর্থ | Label action (review সাপেক্ষে) |
|---|---|---|
| `supports_code` | Candidate observed আচরণের সঙ্গে মেলে | যাচাই করা স্বাধীন প্রমাণ observed আচরণকে intended আর spec-কে ভুল দেখালে → SPEC হতে পারে |
| `supports_spec` | Candidate **spec-এর** আচরণ সমর্থন করে, observed-এর বিপরীতে | সেই scenario-তে যাচাই হলে → সাধারণত **IMPL**। Raw string থেকে SPEC কখনো নয়। |
| `conflicting` | দুই দিকেই support (প্রায়ই আলাদা branch থেকে) | Scenario filter করার পরও প্রকৃত conflict থাকলে → UNDECIDABLE + `both_candidate=true`। ভুল branch বা scenario-র hit বাতিল করে এক দিক টিকলে সেটা নিন, কারণ লিখে। |
| `none_found` | Decisive দিক পাওয়া যায়নি | Directed manual fallback শেষে স্বাধীন intent না পেলে → UNDECIDABLE। শুধু deliberate-looking code ভিত্তি হলে `both_candidate=true`, confidence ≤2। Absence থেকে SPEC বা IMPL নয়। অন্য decisive নিয়ম থাকলে সেটা প্রযোজ্য। |

- Search incomplete, parse error, অপঠনযোগ্য প্রাসঙ্গিক file বা unresolved route থাকলে তা `none_found` নয়। Manual-এ gap না মিটলে `intent_search_status=incomplete` আর `L1=DEFERRED`।
- **Aggregation:** intent-নির্ভর component unsupported আর বাকিটা শুধু TEST হলে → UNDECIDABLE (`components=UNDECIDABLE;TEST`)। Majority occurrence দিয়ে SPEC তৈরি করা যাবে না।
- `both_candidate` ≠ BOTH। Labeller কখনো BOTH লেখেন না (§10.1)।

**11.4.4 Retrieval boundary**
- Search command-এ সবসময় package-এর ভেতরের explicit path দিন। Empty path list নিয়ে `rg`/`grep` চালাবেন না।
- Source ছাপানোর সময় credential-এর মতো দেখতে লাইন (Authorization, password, token, Basic …) redact করুন।
