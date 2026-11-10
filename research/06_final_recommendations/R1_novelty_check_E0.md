# R1 Novelty Check — Roadmap ধাপ E0

**তারিখ:** 2026-11-09 · **লক্ষ্য:** R1 (“Spec or Bug?”)-এর novelty যাচাই। এই যাচাইয়ের উপর গোটা সুপারিশ নির্ভর করে (`ranked_research_topics.md` §3)।
**পদ্ধতি:**
- দুটি প্রতিদ্বন্দ্বী কাজের **পূর্ণ পাঠ:** 2607.12101 ও RESTifAI 2512.08706।
- P032-এর version যাচাই।
- P001 ও 2607.12101-এর Zenodo package-এর বিষয়বস্তু পরিদর্শন। P001-এর ২.৭ GB zip পুরো না নামিয়ে HTTP range request দিয়ে।
- ৩টি নতুন search (GV18–GV20)।

**লেবেল:** ⚠️ = অনুমান।
**সতর্কতা:** GV18–GV20-এর বাকি ফল কেবল snippet-স্তরের।

---

## 1. সিদ্ধান্ত (সংক্ষেপে)

**✅ GO — R1 বহাল থাকছে।** তবে নকশায় তিনটি পরিবর্তন সুপারিশ করা হচ্ছে (§4)।

- **Triage অংশ (spec defect বনাম implementation fault):**
  - কোনো স্বয়ংক্রিয় research পদ্ধতি পাওয়া যায়নি।
  - সবচেয়ে কাছের কাজগুলোতেও (RESTifAI, 2504.08113) classification **মানুষ হাতে** করেছে।
  - P001-এর লেখকরা এটিকে স্পষ্টভাবে future research বলেছেন — **Class A প্রমাণ**।
- **Repair অংশ:**
  - Research-এ runtime-ভিত্তিক OpenAPI repair পাওয়া যায়নি। SpecFix এখনো static-only।
  - তবে **commercial বা practitioner tool** (traffic থেকে drift detection, patch প্রস্তাব) বিদ্যমান।
  - ⇒ Repair-কে নতুন “tool” হিসেবে নয়, **মূল্যায়িত নির্ভুলতা ও triage-নির্ভর repair** হিসেবে উপস্থাপন করতে হবে।
- **R2-এর novelty কমেছে।** 2607.12101 spec-এর ত্রুটি fuzzer-কে কতটা প্রভাবিত করে তা ইতিমধ্যে নিয়ন্ত্রিতভাবে মেপেছে।

## 2. প্রমাণ

### 2.1 2607.12101 — *Fault Injection in OpenAPI Specifications for Evaluating Black-Box Testing Effectiveness*

**পরিচয়:**
- Mazhar, Wang, Mäntylä (University of Helsinki)।
- ISSRE 2026-এ accepted (Zenodo বিবরণ অনুযায়ী)।
- arXiv v1, 13 Jul 2026।
- পূর্ণ পাঠ।

**কী করে:**
- ৬টি spec fault class: REQUEST_STRICT, REQUEST_LOOSE, METHOD_SEM, RESPONSE_ORACLE, PARSE_BROKEN_REF, COMPOSITE।
- ৫টি severity level।
- TrainTicket (২১১ operation) ও SocialNetwork (৬ operation)।
- EvoMaster, RESTler ও Schemathesis দিয়ে মোট ৪৫০+ run।
- Metric: code coverage, spec coverage, request/response quality, behavioural diversity।

**কী করে না:**
- Spec-এর ত্রুটি **শনাক্ত, triage বা repair** করে না।
- Implementation অপরিবর্তিত রাখে — অর্থাৎ implementation fault বনাম spec fault-এর পৃথকীকরণের প্রশ্ন তোলেই না।

**R1-এর পক্ষে প্রমাণ:**
- উপসংহারে লেখকরা বলেছেন practitioner-দের spec-কে “testable artifact” হিসেবে দেখতে হবে এবং “appropriate repair strategies” বেছে নিতে হবে।
- METHOD_SEM-ধরনের ত্রুটি “must be fixed at the specification source”।
- ⇒ Repair ও শনাক্তকরণ তাদের পরিধির বাইরে, এবং প্রয়োজনীয় হিসেবে উল্লিখিত।

**গুরুত্বপূর্ণ ফল:**
- REQUEST_LOOSE (constraint শিথিল) coverage-এ কোনো প্রভাব দেখায় না, কিন্তু request/response quality ব্যাপকভাবে কমায় — “hidden degradation”।
- ⇒ Coverage-only মূল্যায়ন spec-ত্রুটির প্রভাব কম দেখায়।

**কাজে লাগবে:** replication package (Zenodo 10.5281/zenodo.21342161, CC-BY 4.0, ০.৬ MB)।
- Baseline spec, fault injector script ও injection catalog।
- Mutated spec — “regenerates exactly”।
- ⇒ **R1-এর জন্য নিয়ন্ত্রিত ground truth-এর তৈরি উৎস।**

**নোট:** লেখক Yuqing Wang ও Mäntylä P037 (LO2)-এর সহ-লেখক — একই গবেষণা-ধারা।

### 2.2 P032 (SpecFix) — version যাচাই

- arXiv-এ ৪টি version আছে। আমাদের corpus-এ যেটি পড়া হয়েছে সেটিই সর্বশেষ: **v4 (6 Apr 2026)**। নতুন version নেই।
- SpecFix-এর ত্রুটির ধরন A–C:
  - Authentication।
  - Base URL।
  - Undocumented runtime header বা prefix।
- এগুলো documentation-এর সাথে তুলনা করে খুঁজে পায়। লেখকরা runtime-only ত্রুটি বাদ দিয়েছেন।
- **R1-এর সাথে overlap অপরিবর্তিত** — শুধু আংশিক, এবং static।

### 2.3 RESTifAI (arXiv 2512.08706, Dec 2025) — পূর্ণ পাঠ

- LLM দিয়ে happy-path ও negative test তৈরি।
- ব্যর্থ test-কে **domain expert-রা** Bug, Enhancement বা Invalid-এ ভাগ করেছেন (Table 4)।
- “Invalid”-এর একটি কারণ: business rule API contract-এ অনুপস্থিত, অর্থাৎ spec-এর ঘাটতি।
- **⇒ Triage স্বয়ংক্রিয় নয়।** কাজটি দেখায় বাস্তবে এই পৃথকীকরণ প্রয়োজন এবং manual — R1-কে সমর্থন করে।

### 2.4 P001 Zenodo (10.5281/zenodo.6941292) — বিষয়বস্তু

**Package:** ২.৭ GB zip, ১৬,১০৮টি entry, CC-BY 4.0। Range request দিয়ে তালিকা ও ৪টি ছোট ফাইল পড়া হয়েছে।

**`results-all/testsWithFaultClusters*_<api>.csv`:**
- প্রতিটি test case-এর `passed`, `failReasonCategory`, `bot`, `faultClusterIndex` আছে।
- উদাহরণ OMDb:
  - ৫৮,৫২৫টি test।
  - ২,৫০৩টি “OAS disconformity”।
  - ১,৭১০টি inter-parameter dependency।
  - ১,৬৭৪টি individual constraint।
  - ৫৮৮টি 5XX-invalid।

**অন্যান্য ফাইল:**
- **`additional/bugs_reported.csv`:** ২৫৩টি report-করা test case, `confirmed` ও `fixed` কলামসহ।
  - ৪৫টি confirmed — এর মধ্যে ১৪টি fixed।
  - ৬টি confirmed না হয়েও fixed।
  - ১২টি false।
  - বাকিগুলো অনিশ্চিত।
- **`results-replication/resources/taas_eval/<API>/openapi.yaml`:** প্রতিটি API-র spec।
- **`DOC/OPPORTUNITIES.md` Scenario 1:** “Automated classification of failures into faults … using machine learning”।
  - ⇒ লেখকদের স্পষ্ট আমন্ত্রণ: **Class A।**

**সীমা:**
- Label হলো failure → fault cluster ও confirmed bug। **Spec-defect বনাম implementation-fault label নেই।** তাই R1-কে নিজের label তৈরি করতে হবে।
- কাঁচা request/response body আলাদা archive-এ আছে (`restest.us.es/fse2022/test-data.zip`)। লেখকদের মতে এটি প্রক্রিয়া করতে ১২৮ GB RAM লাগে।
  - 2026-11-09-এ সার্ভারের TLS certificate chain যাচাই ব্যর্থ হয়েছে।
  - নিরাপত্তা check bypass করা হয়নি — **প্রাপ্যতা যাচাই হয়নি।**

### 2.5 নতুন search (GV18–GV20; snippet-স্তর)

| ID | পাওয়া কাজ | R1-এর উপর প্রভাব |
|---|---|---|
| GV18 | RESTifAI (2512.08706, পূর্ণ পাঠ §2.3); 2504.08113 (LLM test amplification — failure manually labelled, যার মধ্যে “API Bug Exposed”); TOSEM 10.1145/3491038 (spec-SUT discrepancy প্রায় সব সিস্টেমে) | Triage-এর **প্রয়োজন সমর্থিত**; স্বয়ংক্রিয় পদ্ধতি পাওয়া যায়নি |
| GV19 | APISensor (2603.23852) ও MRG (2604.19471) — traffic থেকে API discovery বা spec generation, repair নয়; practitioner tool (Beeceptor patch প্রস্তাব, api-drift-detector, API Sentinel) | Repair অংশ: **engineering practice আছে** → research অবদান হতে হবে মূল্যায়িত নির্ভুলতা ও triage-ভিত্তিক সিদ্ধান্ত |
| GV20 | RESTest follow-up (2309.04230, 2410.12547 — healthcare IoT; duplicate failure-এর সমস্যা উল্লেখিত) | P001 Scenario 1-এর ML follow-up পাওয়া যায়নি |

## 3. Score হালনাগাদ

| পরিবর্তন | কারণ |
|---|---|
| **R2 novelty ৩ → ২.৫** | 2607.12101 spec-ত্রুটির downstream প্রভাব নিয়ন্ত্রিতভাবে মেপেছে। R2-এর অবশিষ্ট অবদান কেবল “বাস্তব inferred spec” |
| R1 novelty ৪ (অপরিবর্তিত) | Triage অংশ শক্তভাবে সমর্থিত। Repair-এর tool-স্তরের overlap §4-এর নকশা দিয়ে সামলানো হবে |

**ফল** (`_scoring_e0.json`):
- **Base weighting:** R1 ৪.০০, R2 ৩.৮২৫, R4 ৩.৮২৫, R3 ৩.৮০।
- **R1-এর novelty ৩.৫ ধরলেও:** ৩.৮৭৫, এবং **R1 প্রথমই থাকে**।
  - E0-এর আগে novelty ৩ হলেই R1 পঞ্চম স্থানে নামত।
- ⇒ সুপারিশের robustness বেড়েছে।
- **অন্যান্য weighting:**
  - Importance-heavy: R3 ১ম (৪.০৫), R1 ২য়।
  - Feasibility-heavy: R2 ১ম (৪.১৭৫), R1 ৩য়।

## 4. R1-এর নকশায় সুপারিশকৃত পরিবর্তন

1. **দ্বিমুখী fault injection — manual label ছাড়াই ground truth:**
   - **Spec দিক:** 2607.12101-এর injector দিয়ে spec-এ ত্রুটি (REQUEST_LOOSE/STRICT, RESPONSE_ORACLE, METHOD_SEM)। Implementation অপরিবর্তিত।
     - ⇒ এর ফলে যে failure হয়, তার label = **spec defect**।
   - **Implementation দিক:** code mutation (Java-তে PIT/Major) বা জানা bug। Spec অপরিবর্তিত।
     - ⇒ এর ফলে যে failure হয়, তার label = **implementation fault**।
   - দুটি একসাথে → triage classifier-এর নিয়ন্ত্রিত মূল্যায়ন।
   - Manual labelling থাকবে কেবল বাস্তব (non-injected) failure-এর জন্য।
   - ⚠️ এই নকশা এখানে প্রস্তাবিত; প্রকাশিত কাজে পাওয়া যায়নি (snippet-স্তরের search)।
2. **বাস্তব যাচাই:**
   - P001-এর “OAS disconformity” failure + `bugs_reported.csv`-এর confirmed/fixed তথ্য + API spec।
   - এগুলো দিয়ে বাস্তব-বিশ্বের নমুনায় ছোট (যেমন ২০০টি) double-labelled set।
3. **RQ4-এর metric:** coverage-এর সাথে **request/response quality** ও behavioural diversity। কারণ 2607.12101-এর RQ3 অনুযায়ী coverage একা “hidden degradation” ধরে না।

**উপস্থাপন:** “নতুন drift tool” নয়, বরং **“failure-এর উৎস নির্ধারণ (attribution) এবং attribution-নির্ভর spec repair-এর প্রথম মূল্যায়িত পদ্ধতি”**। Novelty দাবি সীমিত রাখতে হবে snippet-স্তরের search-এর কারণে।

## 5. বাকি কাজ (E0-এর পর)

- **2504.08113 ও TOSEM 10.1145/3491038:** পূর্ণ পাঠ। Failure taxonomy পুনর্ব্যবহারযোগ্য কিনা দেখতে হবে।
- **`restest.us.es` archive:** supervisor-এর browser থেকে প্রাপ্যতা যাচাই।
- **Scholarly database (ACM DL, IEEE Xplore)-এ search:** “failure attribution OpenAPI”, “specification or implementation fault REST”।
- **2607.12101 package নামিয়ে** injector কোন SUT-এ প্রয়োগযোগ্য তা পরীক্ষা (roadmap E1-এর সাথে)।

## 6. E1 প্রস্তুতি — 2607.12101-এর injector পরীক্ষা (2026-11-09)

**উৎস ও পরিদর্শন:**
- Package নামানো হয়েছে Zenodo API link থেকে: `records/21342162/files/.../content`।
  - ⚠️ Record-page-এর `?download=1` link HTML ফেরত দেয়।
- কেবল পড়া হয়েছে, কোনো code চালানো হয়নি।
- ৫৬টি ফাইল আছে:
  - README।
  - প্রতিটি system-এর জন্য `baseline_spec.json`, `catalog.yaml`, `fault_injector.py` (৮৭২/৯৫১ লাইন)।
  - `mutated_specs/<class>/P15…P75`।

**পুনর্ব্যবহারযোগ্যতা:**
- `--base-spec`, `--catalog`, `--out-dir`, `--seed` argument আছে। Catalog-এ `global_operations_base`, `exclude_paths`, `selection_seed` এবং variant (family × level)।
- ⇒ **যেকোনো spec-এ প্রয়োগযোগ্য।**
- Dependency শুধু Python 3 + PyYAML। Network বা subprocess call নেই (import তালিকা পরীক্ষিত)।

**সীমা:**
- **Spec format:** কেবল **Swagger 2.0, JSON** (`load_json`)।
  - `structural_check` `swagger` field দাবি করে।
  - `PARSE_BROKEN_REF` `#/definitions/...` ব্যবহার করে।
- **OpenAPI 3.x spec-এর জন্য দুটি বিকল্প:**
  - (ক) spec-কে Swagger 2.0-তে রূপান্তর করা।
  - (খ) injector-কে `components/schemas` ও `requestBody/content` সমর্থনের জন্য পরিবর্তন করা।
- **Licence:** package CC-BY 4.0 — attribution দিয়ে পুনর্ব্যবহার করা যাবে।

**পরবর্তী:**
- E1-এ নির্বাচিত SUT-এর spec format তালিকা করা (EMB ও P018-এর API)।
- তারপর (ক) বা (খ) বেছে নেওয়া।
