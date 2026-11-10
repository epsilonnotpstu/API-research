# R1 Triage Codebook — v0.2 (খসড়া)

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
