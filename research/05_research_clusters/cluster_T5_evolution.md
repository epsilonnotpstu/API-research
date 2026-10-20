# Cluster T5 — API Evolution & Breaking Changes

**Primary:** P020, P021, P022, P023, P024, P025 · **Secondary:** P030, P031, P034, P035
⚠️ = অনুমান। [H] = hypothesis।

## 1. ID ও নাম
T5 — API পরিবর্তন, breaking change, deprecation এবং তাদের consumer-প্রভাব। Consumer হতে পারে মানুষ-লিখিত client, microservice বা LLM।

## 2. Problem ও motivation
- API পরিবর্তন client ভাঙে।
- Library-তে semver প্রায়ই লঙ্ঘিত হয় (P023)।
- Microservice-এ consumer অজানা (P020)।
- REST-এ behavioural regression schema-তে দেখা যায় না (P025)।
- নতুন consumer হিসেবে LLM পুরোনো বা deprecated API ব্যবহার করে (P022, P024)।

## 3. Core RQ
- Breaking change কত ঘন ঘন ঘটে, এবং কতটা প্রভাব ফেলে (P023)?
- Practitioner-রা কীভাবে evolution পরিচালনা করেন (P020)?
- Version-এর মধ্যে regression কীভাবে ধরা যায় (P025)?
- LLM কি deprecated API ব্যবহার করে, এবং কীভাবে তা ঠিক করা যায় (P024)?
- পরিবর্তনশীল tool-এ agent কীভাবে মানিয়ে নেয় (P022)?

## 4. Paper
| ID | ধরন | পরিধি |
|---|---|---|
| P021 (CSUR 2021) | SLR | API evolution-এর সামগ্রিক চিত্র |
| P025 (ISSTA 2020) | Technique | REST differential regression (Azure) |
| P023 (EMSE 2022) | Replication | Maven Central semver |
| P020 (JSS 2024) | Interview | ১৭ জন microservice practitioner |
| P024 (ICSE 2025) | Empirical + fix | LLM completion-এ deprecated usage (Python) |
| P022 (ICLR 2025) | Technique + benchmark | ToolEVO (MCTS, self-reflection) |

## 5. ঐতিহাসিক অবদান
- **P021:** ক্ষেত্রের মানচিত্র ও open challenge-এর তালিকা।
- **P025:** REST-এ differential regression-এর প্রথম পদ্ধতি।

## 6. সাম্প্রতিক উন্নয়ন
- LLM consumer-এর দিকে মোড় (P022, P024; corpus-এর বাইরে GV11-এ evolving-agent benchmark)।
- **REST evolution dataset (GV07):**
  - GitHub-sourced OpenAPI dataset (ICWE 2024)।
  - RADA deprecation study (ICSME 2020)।

## 7. Methodology
- Mining (P023)।
- Differential testing (P025)।
- Qualitative interview (P020)।
- Benchmark + prompting/editing (P024)।
- Synthetic tool modification + MCTS training (P022)।

## 8. Tool
- Maracas (P023)।
- RESTler-generated test suite + response-log diffing (P025)।
- REPLACEAPI / INSERTPROMPT (P024)।
- ToolEVO (P022)।

## 9. Dataset
- **P023:** Maven Central corpus।
- **P025:** Azure version।
- **P024:** ১৪৫টি mapping ও ২৮,১২৫টি prompt।
- **P022:** ToolQA-D।
- **P020:** interview transcript (গোপন)।

## 10. মূল্যায়ন
- Breaking-এর হার ও client প্রভাব (P023)।
- Confirmed regression (P025)।
- DUR/AUP ও Fixed Rate (P024)।
- Task success (P022)।

## 11. প্রতিষ্ঠিত ফলাফল
- **Library (P023):**
  - Non-major upgrade-এর ২০.১% breaking।
  - কিন্তু মাত্র ৭.৯% client প্রভাবিত।
  - Non-major breaking-এর হার ২০০৫-এর ৬৭.৭% থেকে ২০১৮-তে ১৬.০%-এ নেমেছে।
- **Microservice অনুশীলন (P020):**
  - মাত্র ৫/১৭ behavioural পরিবর্তনকে breaking ধরে।
  - ১২/১৭-এ consumer পুরোনো version-এ আটকে থাকে।
  - Event-driven API ১৩/১৭-এ ব্যবহৃত, কিন্তু documented মাত্র ৩/১৭-এ।
- **REST (P025):**
  - ১৪টি regression, যার ৯টি service-side।
  - Diagonal কৌশল ২৭৮-এর বদলে ৩৬টি diff দিয়েই সবগুলো পায়।
- **LLM consumer:**
  - Outdated context-এ deprecated usage (DUR) ৭০–৯০% (P024)।
  - Parameter পরিবর্তন সবচেয়ে ক্ষতিকর, এবং Static-SFT deprecated call পুনরাবৃত্তি করে (P022)।
- **গবেষণার মান (P021):**
  - ৬৩.৯% কেবল Java-তে।
  - ৭৪% empirical study-তে statistics নেই।

## 12. বিরোধ
- **P023:** breaking change সাধারণ হলেও প্রভাব কম।
- **P020:** practitioner-রা breaking change এড়াতে বড় খরচ করেন (একাধিক version রাখা)।
- ⇒ প্রভাব-মাপার পদ্ধতি (কোন declaration ব্যবহৃত) গুরুত্বপূর্ণ। REST-এ এর সমতুল্য পরিমাপ নেই ⚠️।

## 13. লেখক-স্বীকৃত সীমাবদ্ধতা
- **P023:** Java; syntactic।
- **P025:** log-সংগ্রহে ৩+ দিন; manual analysis প্রায় ১ সপ্তাহ।
- **P020:** ছোট নমুনা।
- **P024:** ছোট open model।
- **P022:** synthetic পরিবর্তন।

## 14. বিশ্লেষণী সীমাবদ্ধতা ⚠️
- REST-এ open version-history benchmark নেই (P025-এর Azure নির্দিষ্টতা)।
- P022-এর পরিবর্তন GPT-4-generated, বাস্তব নয়।
- P021-এ সংখ্যার অসঙ্গতি (৬৩.৯/৬৬/৭০.৪%)।

## 15. অপর্যাপ্ত প্রমাণ
- Behavioural breaking change-এর হার REST-এ কত?
- Consumer-impact analysis।
- AsyncAPI evolution।

## 16. Gap
- **G1:** behavioural label-সহ REST evolution benchmark (Class A+B, Supported, narrowed)।
- **G2:** REST behavioural breaking-change detection (Class B, Supported)।
- **G12:** AsyncAPI (single source, দুর্বল)।
- **T5×T8:** real API history-ভিত্তিক agent robustness — GV11-এ partially weakened।

## 17. Technical উন্নতি
- Cross-version invariant oracle: P008-এর invariant + P025-এর diff।
- Consumer-usage-weighted prioritisation।
- Triage স্বয়ংক্রিয়করণ।

## 18. নতুন approach [H]
- **Open-source REST service-এর (EMB, P004-এর ২০টি service) git history থেকে version pair তৈরি:**
  1. Schema diff (oasdiff)।
  2. Differential testing (P025)।
  3. Invariant diff (AGORA, P008)।
- এই তিনটির সমন্বয়ে behavioural breaking change শনাক্ত ও label করা।
- পাশাপাশি P023-ধাঁচের client-impact পরিমাপ।

## 19. দক্ষতা ও resource
- Git mining।
- Docker দিয়ে পুরোনো version build করা।
- oasdiff, EvoMaster/Schemathesis, Daikon/AGORA।

## 20. ঝুঁকি
- পুরোনো version build-এ ব্যর্থতা।
- Behavioural label-এর subjectivity।
- নমুনায় পর্যাপ্ত breaking change না-ও থাকতে পারে।

## 21. Baseline ও metric
- **Baseline:** oasdiff (schema-only), P025-এর diagonal diff।
- **Metric:** precision/recall বনাম manual label, false-alarm হার, triage সময়।

## 22. নতুন গবেষকের সুযোগ
- **G1+G2 সমন্বিত** — উচ্চ গুরুত্ব, মাঝারি feasibility।

## 23. প্রমাণের মান
**উচ্চ।**
- ছয়টি peer-reviewed paper।
- Gap-টি একাধিক লেখক স্পষ্টভাবে উল্লেখ করেছেন (P021, P023, P025)।
