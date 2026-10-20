# Research Gap Validation — PHASE D3

**তারিখ:** 2026-10-19 · **Register:** `research_gap_register.csv` (G1–G14) · **Search log:** `00_protocol/search_log.csv` GV01–GV17 (WebSearch; snippet-স্তর, full text পড়া হয়নি)

**শ্রেণি:**
- **A** — লেখকরা স্পষ্টভাবে উল্লেখ করেছেন।
- **B** — একাধিক paper-এর evidence synthesis দ্বারা সমর্থিত।
- **C** — অস্থায়ী hypothesis; আরও যাচাই দরকার।

**নিয়ম:** Class C কে কখনো প্রতিষ্ঠিত সমস্যা হিসেবে উপস্থাপন করা হয়নি।
**সতর্কতা:** বাইরের search-এর কাজগুলো (২০২৫–২০২৬ preprint সহ) কেবল শিরোনাম বা snippet স্তরে দেখা। তাদের দাবি যাচাই হয়নি। এগুলো শুধু **gap দুর্বল করার সংকেত** হিসেবে ব্যবহৃত।

## 1. সারসংক্ষেপ

| Gap | শ্রেণি | Search-এর পর অবস্থা | সুপারিশে ব্যবহারযোগ্য? |
|---|---|---|---|
| G1 REST evolution benchmark (behavioural label) | A+B | Supported (narrowed) | ✅ |
| G2 Behavioural breaking-change detection (REST) | B | Supported | ✅ |
| G3 MCP/REST-wrapper authorization testing | B → C (narrowed) | Partially weakened | ⚠️ সতর্কভাবে |
| G4 Spec quality → agent reliability (causal) | B/C | Partially weakened | ⚠️ overlap যাচাইসহ |
| G5 Real REST security benchmark | A+B | Supported | ✅ (ব্যয়বহুল) |
| G6 Semantic REST oracle | A | **Weakened** | ❌ প্রধান novelty হিসেবে নয় |
| G7 API hallucination benchmark | A | **Weakened** | ❌ (কেবল residual) |
| G8 LLM security API misuse | A | **Weakened** | ❌ |
| G9 Inferred spec-এর downstream মূল্যায়ন | B | Supported | ✅ |
| G10 Independent LLM REST tool তুলনা | B | Supported | ✅ (মাঝারি novelty) |
| G11 GraphQL/RPC testing | A | **Weakened** | ❌ |
| G12 AsyncAPI evolution | A (একটি উৎস) | Supported, দুর্বল প্রমাণ | ⚠️ exploratory |
| G13 Observability oracle | C | Partially weakened | ⚠️ |
| G14 Spec-vs-impl runtime triage ও repair | B | Supported | ✅ |

## 2. বিস্তারিত যাচাই (প্রধান gap)

### G1 + G2 — REST/OpenAPI behavioural breaking changes (benchmark + detection)

- **সমস্যার প্রমাণ:**
  - P020: মাত্র ৫/১৭ প্রতিষ্ঠান behavioural পরিবর্তনকে breaking ধরে; impact analysis manual।
  - P025: ১৪টির মধ্যে ৯টি regression service-side।
  - P023: ২০.১% non-major upgrade breaking (Java)।
  - P021: uniform benchmark-এর অভাব একটি open challenge।
- **আগের সমাধান-প্রচেষ্টা:**
  - P025 (Azure-নির্দিষ্ট, manual triage, open history নেই)।
  - Library-স্তরে BBC detection (GV10: TOSEM 10.1145/3643782, Sembid)।
  - oasdiff (schema-only)।
- **যা বাকি:**
  - REST-এ behavioural label-সহ benchmark।
  - Cross-version semantic oracle।
- **Research না engineering?** Research। Ground truth নির্মাণ ও detection-এর মূল্যায়ন দুটোই বৈজ্ঞানিক প্রশ্ন।
- **বিরোধী প্রমাণ:** GV07-এ syntactic OpenAPI evolution dataset (ICWE 2024) ও RADA (ICSME 2020) পাওয়া গেছে। তাই “কোনো dataset নেই” দাবি ভুল হবে — gap কেবল **behavioural label**-এ।
- **Measurable:** হ্যাঁ। Manual label-এর বিপরীতে precision/recall।
- **Dataset/baseline:**
  - GitHub OpenAPI history, EMB/P004 service।
  - Baseline: oasdiff, P025-ধাঁচের diff।
- **Novelty দাবির আগে আরও search:**
  - MSR/ICSME/ICSOC ২০২৫–২০২৬।
  - “OpenAPI breaking change dataset”, “cross-version REST regression”।

### G14 — Spec-implementation mismatch: runtime triage ও repair

- **প্রমাণ:**
  - P001-এ failure-এর ৬৩% ও fault-এর ৫০% spec-disconformity।
  - P015-এ ১২,৪১৩টি schema fault, যার severity প্রশ্নসাপেক্ষ।
  - P018-এ ৪টি developer-confirmed inconsistency।
  - P004-এ প্রায় ৯৯% spec-এ mismatch।
  - P032-এ spec defect tool failure ঘটায়।
- **আগের প্রচেষ্টা:**
  - P032 SpecFix — **কেবল static**; লেখকরা runtime-only defect বাদ দিয়েছেন।
  - P018/P019 static inference।
  - GV16: spec fault-injection study (2607.12101) — repair নয়।
- **যা বাকি:** failure-কে {spec defect, implementation fault, environment noise}-এ ভাগ করা এবং spec patch প্রস্তাব করা।
- **Research না engineering?** Research। Classification-এর ground truth ও repair-এর সঠিকতা পরিমাপযোগ্য।
- **বিরোধ:** নেই। তবে P001 নিজেই spec-repair-কে future work বলেছে (Class A উপাদান)।
- **Dataset:** P001-এর ৩৯০K failure (Zenodo); APIs.guru; P018-এর developer-confirmed inconsistency।
- **Baseline:** raw Schemathesis/EvoMaster report; SpecFix (static)।
- **আরও search:** “OpenAPI repair dynamic”, “specification drift detection REST”। এছাড়া 2607.12101 পূর্ণ পাঠ।

### G9 — Inferred spec-এর downstream মূল্যায়ন

- **প্রমাণ:** P017, P018, P019 কেবল spec-element accuracy মাপে। অন্যদিকে P003 ও P004 দেখায় underspecified spec fuzzer-কে আটকায়।
- **আগের প্রচেষ্টা:** GV13 — ICICL (2504.07250) improved example-এর প্রভাব fuzzing-এ দেখায় (আংশিক)।
- **বাকি:** developer বনাম inferred বনাম enriched spec দিয়ে একই fuzzer বা agent চালিয়ে তুলনা।
- **Research?** Empirical research। মাঝারি novelty, উচ্চ feasibility।
- **Baseline ও dataset:** Respector/RestPi/OOPS artifact; EMB; EvoMaster BB/Schemathesis।

### G10 — Independent, budget-equal LLM REST tool তুলনা

- **প্রমাণ:**
  - P005-এ budget অসম।
  - P005 ও P007 একই গোষ্ঠীর, একই ১২টি service-এ মূল্যায়িত।
  - শেষ independent তুলনা P004 (২০২২)।
- **বিরোধী প্রমাণ:** GV06 — RESTifAI ও APIPilot তুলনা করে, কিন্তু তারা নিজেরাই tool প্রস্তাবক। Neutral study পাওয়া যায়নি।
- **Research?** হ্যাঁ — P003/P004-এর ধারায় empirical SE। ঝুঁকি: “কেবল replication” হিসেবে দেখা হতে পারে। তাই নতুন বিশ্লেষণ যোগ করা উচিত, যেমন fault severity বা mutation score।

### G4 — Spec/documentation-এর মান → agent reliability

- **প্রমাণ:**
  - P032: repair-এর পর ৭৬%→৯৪.২%, কিন্তু success = error-free invocation।
  - P035: spec-ই মূল উপাদান।
  - P026: মানুষের ক্ষেত্রে design লঙ্ঘন ক্ষতিকর।
- **আগের প্রচেষ্টা (GV03):**
  - SilentProbe (constraint publication → silent failure)।
  - 2605.14312 (agent-ready documentation; লেখকদের মতে agent benchmark নেই)।
  - 2504.15546।
- **বাকি:** নিয়ন্ত্রিত spec mutation × end-to-end agent task success। এই নির্দিষ্ট নকশা পাওয়া যায়নি।
- **ঝুঁকি:** খুব দ্রুত চলমান এলাকা। SilentProbe-এর পূর্ণ পাঠ ছাড়া novelty দাবি করা যাবে না।

### G3 — MCP/REST-wrapper authorization testing (narrowed)

- **প্রমাণ:**
  - P036: mcp-scan excessive permission মিস করে।
  - P032: wrapper auth বাদ দেয় এবং ৭৩.৬% সব tool expose করে।
- **বিরোধী প্রমাণ (GV01, GV12):** MCPSecBench, MCPXKIT, MCPTox, VIPER-MCP, MCP-38, privilege measurement (2507.06250)। ⇒ **Broad MCP security gap বাতিল।**
- **বাকি (Class C):** wrapped REST endpoint-এর access-policy (BOLA/BFLA) বা least-privilege-এর **dynamic** testing — agent-mediated।
- **আরও search:** “MCP authorization testing”, “agent confused deputy REST”। ২০২৬-এর সাম্প্রতিক কাজ।

### G5 — Real REST security benchmark

- **প্রমাণ:**
  - P015: real API-তে Missed-Check fault নেই।
  - P012/P014: seeded বা vulnerable-by-design SUT।
  - P029: ৫টি benchmark, সবই synthetic Java।
- **GV05:** survey-গুলোও real-world benchmark চায়। XBOW আছে, কিন্তু সেটি exploit-challenge।
- **Feasibility:** নিম্ন-মাঝারি। CVE বা fix-commit mining ও নৈতিক বাধা আছে।

## 3. দুর্বল বা বাতিল gap (নথিভুক্ত)

| Gap | কেন দুর্বল | Search |
|---|---|---|
| G6 Semantic oracle | MASTOR, RESTOR, SATORI, RBCTest, AGORA+ — ২০২৫–২০২৬-এ সক্রিয় | GV04 |
| G7 Hallucination benchmark | WAPIIBench (execution-based), constrained decoding | GV09 |
| G8 LLM security misuse | 2404.03823, 2607.11348, EMSE 2025, SLR 2610.15482 | GV17 |
| G11 GraphQL testing | EvoMaster GraphQL (TWEB 2024), PrediQL, SGAFuzzer, BenGQL | GV08 |

**মন্তব্য:** corpus-এর ভেতরের লেখকরা এগুলোকে future work বলেছিলেন (Class A)। কিন্তু পরবর্তী সাহিত্য সেগুলো সক্রিয়ভাবে সমাধান করছে।
- এটি দেখায় corpus-ভিত্তিক gap যাচাই ছাড়া অতিরঞ্জিত হতে পারে।

## 4. পদ্ধতিগত সীমাবদ্ধতা
- WebSearch-এর ফল US-কেন্দ্রিক ও relevance-ranked। Scholarly database-এর পূর্ণ query নয় (OpenAlex credit ও Semantic Scholar 429 আগেই নথিভুক্ত)।
- Snippet-এর সংখ্যা যাচাই হয়নি।
- কিছু arXiv ID ভবিষ্যৎ-তারিখের মতো দেখায় (যেমন 2610.x = অক্টোবর ২০২৬)। এগুলো বর্তমান তারিখের (2026-10-19) সাথে সামঞ্জস্যপূর্ণ, তবুও পূর্ণ পাঠে যাচাই করতে হবে।
