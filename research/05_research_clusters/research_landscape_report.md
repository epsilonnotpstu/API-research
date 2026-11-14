# Research Landscape Report — PHASE D

> **হালনাগাদ 2026-11-13 — P038 সমস্যার সমাধান:** সঠিক paper (Ponce et al. 2025, IST 188:107870, author-hosted copy) এখন `paper/P038.pdf`-এ আছে। এর বিশ্লেষণ `04_paper_analysis/P038_analysis.md`-এ (৭৪টি study, confidence High)। এই নথিতে যেখানে P038-কে “substitute”, “P038*” বা “Ghani 2019” বলা হয়েছে, তা ঐতিহাসিক — সেগুলো এখন আর প্রযোজ্য নয়। T9-এর evidence strength এখন **মাঝারি** (`05_research_clusters/cluster_T9_microservices.md`)।


**তারিখ:** 2026-10-19 · **Corpus:** ৩৮টি paper (P001–P038; P038 substitute) · **ভিত্তি:** PHASE C analysis, `cross_paper_synthesis.md`, ৯টি cluster report, gap validation (GV01–GV17)
⚠️ = অনুমান। [H] = hypothesis।

## 1. সারসংক্ষেপ
API গবেষণার এই corpus ৯টি প্রমাণ-ভিত্তিক cluster-এ বিভক্ত।

**কেন্দ্র (সবচেয়ে পরিণত ও ঘন):** T1 REST testing।
- তার চারপাশে তিনটি সহায়ক অক্ষ:
  - T4 spec inference।
  - T6 documentation ও design।
  - T5 evolution।
- নতুন consumer হিসেবে **T8 LLM agent/MCP** দ্রুত বাড়ছে। এটি পুরোনো সমস্যাগুলোকে নতুন রূপে ফিরিয়ে আনছে।

**তিনটি সর্বজনীন সত্য:**
1. **Spec-এর মান** প্রায় প্রতিটি স্বয়ংক্রিয় পদ্ধতির bottleneck।
2. **Oracle ও মূল্যায়ন-পদ্ধতি** দুর্বল: 5xx, self-evaluation, seeded fault, proxy metric।
3. **Behavioural (অর্থগত) আচরণ** — পরিবর্তন, fault বা policy যাই হোক — syntactic আচরণের তুলনায় অনেক কম অধ্যয়িত।

## 2. Cluster গঠন-পদ্ধতি (D1)

- **ভিত্তি:**
  - PHASE A taxonomy (T1–T10) প্রাথমিক কাঠামো দেয়।
  - কিন্তু প্রতিটি paper-এর primary cluster নির্ধারিত হয়েছে তার **research objective, method ও result** থেকে, keyword থেকে নয়।
  - Secondary cluster এসেছে paper-এর §O সম্পর্ক ও limitation থেকে।
- **পরিবর্তন:**
  - T10 (API recommendation) PHASE B-তে বাদ গিয়েছিল। তাই cluster ৯টি।
- **বিবেচিত কিন্তু গ্রহণ না-করা একীকরণ:**
  - **T2 → T1:** P011 পদ্ধতিগতভাবে T1, কিন্তু P009/P010-এর সমস্যা (GraphQL ecosystem, cost/DoS) ভিন্ন। তাই আলাদা রাখা হয়েছে, “ছোট ও বৈচিত্র্যময়” সতর্কতাসহ।
  - **T9 → T1:** P037-এর মূল অবদান observability dataset, testing নয়। তাই আলাদা রাখা হয়েছে, evidence “নিম্ন”।
- **Primary সংখ্যা:** T1 ৮, T5 ৬, T8 ৫, T3 ৪, T4 ৪, T2 ৩, T6 ৩, T7 ৩, T9 ২।

## 3. সময়রেখা ও প্রবণতা
- **২০১৮–২০২১ (ভিত্তি):**
  - RESTler (P006)।
  - GraphQL cost (P010)।
  - Web-to-mobile (P013)।
  - Misuse detector-এর মূল্যায়ন (P030)।
  - Evolution SLR (P021)।
  - Doc smell (P028)।
  - Differential regression (P025)।
- **২০২২–২০২৩ (পরিণতি):**
  - Tool তুলনা (P003, P004)।
  - Online testing (P001)।
  - AGORA (P008)।
  - IDL (P016)।
  - Mass assignment (P012)।
  - Survey (P002, P009)।
- **২০২৪–২০২৬ (LLM মোড়):**
  - LLM testing (P005, P007)।
  - LLM spec (P017)।
  - Tool use (P033, P034)।
  - Hallucination (P035)।
  - Evolving tools (P022)।
  - Deprecated usage (P024)।
  - MCP (P032, P036)।
  - LLM misuse (P031)।
  - Security oracle (P014, P015)।
- **Corpus-এর বাইরে (gap validation):** ২০২৫–২০২৬-এ semantic oracle, GraphQL fuzzing, hallucination benchmark ও MCP security-তে উল্লেখযোগ্য নতুন কাজ। ⇒ এসব এলাকায় corpus-ভিত্তিক gap দ্রুত পুরোনো হচ্ছে।

## 4. প্রতিষ্ঠিত জ্ঞান (একাধিক independent প্রমাণ)

| দাবি | প্রমাণ |
|---|---|
| REST fuzzer-এর line coverage সাধারণত ৬০%-এর নিচে | P003, P004, P007, P011 |
| Spec-implementation অমিল ব্যাপক | P001, P004, P018, P019, P025, P013 |
| Status-code oracle বেশিরভাগ অর্থগত fault মিস করে বা noise দেয় | P001, P015, P002 |
| Breaking change সাধারণ, কিন্তু প্রভাব usage-নির্ভর | P023, P020 |
| LLM context বা documentation অনুসরণ করে; outdated context ক্ষতিকর | P024, P035, P034 |
| Model-এর আকার বড় করলেই API-ভুল কমে না | P024, P034 |
| MCP server-গুলো মূলত REST-এর পাতলা wrapper | P032 (preprint), P036 |

## 5. Gap-এর চূড়ান্ত চিত্র (D3-এর পর)

- **শক্তিশালী (Supported):**
  - G1/G2 REST behavioural breaking changes।
  - G14 spec-vs-impl runtime triage।
  - G9 inferred spec-এর downstream মূল্যায়ন।
  - G10 neutral LLM tool তুলনা।
  - G5 real security benchmark।
- **সতর্ক (Partially weakened / Class C):**
  - G4 spec-quality → agent।
  - G3 MCP authorization (narrowed)।
  - G13 observability oracle।
  - G12 AsyncAPI।
- **দুর্বল বা বাতিল:**
  - G6 semantic oracle।
  - G7 hallucination benchmark।
  - G8 LLM security misuse।
  - G11 GraphQL testing।

## 6. Landscape-এর সীমাবদ্ধতা
- **Corpus মাত্র ৩৮টি paper** এবং নির্বাচন T1-ঘন। এটি T1-এর প্রাধান্যকে আংশিকভাবে প্রতিফলিত করতে পারে।
- **P038 substitute** — T9 প্রায় শূন্য-প্রমাণ।
- **২৪টি preprint version পড়া হয়েছে;** published version-এর সাথে পার্থক্য যাচাই হয়নি।
- **Gap validation search** WebSearch snippet-স্তরে। Scholarly database-এর পূর্ণ query নয়।
- **Research-group concentration:**
  - EvoMaster: P003, P011, P015।
  - LlamaRestTest ও AutoRestTest: P005, P007।
  - Sevilla গোষ্ঠী: P001, P008, P016।
  - এরা ক্ষেত্রের মূল প্রবাহ, কিন্তু দৃষ্টিভঙ্গি-পক্ষপাতের ঝুঁকি আছে ⚠️।

## 7. PHASE E-র জন্য ইনপুট
**সুপারিশযোগ্য gap:** G14, G9, G1/G2, G10, G4, G3 (narrowed), G5।
- প্রতিটির জন্য candidate গবেষণা প্রস্তাব, weighted scoring ও Option A/B/C।
