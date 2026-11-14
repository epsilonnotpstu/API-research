# Cluster Comparison — PHASE D4

> **হালনাগাদ 2026-11-13 — P038 সমস্যার সমাধান:** সঠিক paper (Ponce et al. 2025, IST 188:107870, author-hosted copy) এখন `paper/P038.pdf`-এ আছে। এর বিশ্লেষণ `04_paper_analysis/P038_analysis.md`-এ (৭৪টি study, confidence High)। এই নথিতে যেখানে P038-কে “substitute”, “P038*” বা “Ghani 2019” বলা হয়েছে, তা ঐতিহাসিক — সেগুলো এখন আর প্রযোজ্য নয়। T9-এর evidence strength এখন **মাঝারি** (`05_research_clusters/cluster_T9_microservices.md`)।


**তারিখ:** 2026-10-19 · বিস্তারিত: `cluster_T*.md`; gap: `research_gap_register.csv`, `gap_validation.md`; paper-স্তরের final table: `final_paper_cluster_table.md`
⚠️ = অনুমান। Difficulty ও Evidence Strength বিশ্লেষকের মূল্যায়ন (নিচে মানদণ্ড)।

## 1. তুলনামূলক টেবিল

| Cluster | Existing Work | Methods | Key Limitations | Evidence-Backed Gaps | Possible Research | Dataset/Tools | Difficulty | Evidence Strength |
|---|---|---|---|---|---|---|---|---|
| **T1** REST testing/fuzzing | P001–P008 (+৯ secondary) | Search-based, RL, LLM input, invariant oracle | Coverage ছাদ (<৬০%); 5xx oracle; self-evaluation; অসম budget | G10, G14, G9 (G6 weakened) | Neutral LLM tool তুলনা; failure triage ও spec repair | EMB, EvoMaster, Schemathesis, RESTler, P001 dataset | মাঝারি | **উচ্চ** |
| **T2** GraphQL/RPC | P009–P011 | Mapping, formal cost analysis, WB fuzzing | Corpus পুরোনো; industrial data গোপন | G11 weakened; GraphQL authz (C) | Cost-aware fuzzing; agent query cost | EvoMaster, P010 corpus | মাঝারি-উচ্চ | মাঝারি |
| **T3** Security/authz | P012–P015 (+৪) | Black-box inference, CPN, oracle fuzzing | Seeded benchmark; ownership অনুমান; low precision (P014 V2) | G5; G3 (narrowed C); G13 | Real benchmark; MCP access-policy fuzzing | VAmPI, crAPI, Juice Shop, EMB | উচ্চ | মাঝারি-উচ্চ |
| **T4** Spec inference | P016–P019 (+৯) | Static analysis, type inference, LLM, IDL/CSP | Downstream মূল্যায়ন নেই; ভাষা-নির্দিষ্ট; constraint recall কম | G9, G14, G4 | Spec-completeness ablation | Respector, RestPi, OOPS, IDL | মাঝারি | উচ্চ |
| **T5** Evolution | P020–P025 (+৪) | Mining, differential, interview, LLM benchmark | REST-এ open history নেই; behavioural অবহেলিত; synthetic tool পরিবর্তন | G1, G2, G12 | Behavioural BC benchmark ও detector | oasdiff, Maracas, GitHub OpenAPI history | মাঝারি-উচ্চ | **উচ্চ** |
| **T6** Docs/design | P026–P028 (+১১) | Controlled experiment, linting, ML classifier | LLM consumer অপরীক্ষিত; Java-কেন্দ্রিক smell | G4 | LLM-as-consumer design-rule experiment | RESTRuler, APIs.guru, P026 material | নিম্ন-মাঝারি | মাঝারি-উচ্চ |
| **T7** API misuse | P029–P031 (+৫) | Pattern mining, SLR, LLM taxonomy, repair | Precision <১২%; web client অনুপস্থিত | G8 weakened; REST client misuse (C) | Spec-constrained client check | MUBench, Dr.Fix | মাঝারি | উচ্চ (ভেতরে), novelty কম |
| **T8** LLM tool/MCP | P032–P036 (+৬) | Fine-tuning, RAG, mining, generation + repair | Execution মূল্যায়ন বিরল; সংখ্যায় অসঙ্গতি; preprint | G4, G3 (C); G7 weakened | Spec-mutation agent testbed; MCP authz | ToolBench, APIBench, CloudAPIBench, MCP SDK | মাঝারি | মাঝারি |
| **T9** Microservices | P037, P038 (+৪) | SLR (৭৪ study), dataset, ML anomaly detection | Lab-only TRL ৩–৪; security testing অনুপস্থিত; anomaly = 4xx | G13 (C), G2 (ভাগ করা), MSA security (A) | Spec-aware log oracle; R1-এর TrainTicket সম্প্রসারণ | LO2, LogLead, TrainTicket | উচ্চ (infra) | **মাঝারি** |

**মানদণ্ড:**
- **Difficulty:** infrastructure, ground-truth খরচ ও প্রয়োজনীয় দক্ষতার সমন্বিত বিচার।
- **Evidence Strength:**
  - Peer-reviewed primary paper-এর সংখ্যা ও মান।
  - Independent মূল্যায়ন।
  - Artifact।
  - Corpus-এর বাইরের যাচাই।

## 2. Cluster-ভিত্তিক বিশ্লেষণ

### T1 — সবচেয়ে পরিণত, তবে oracle ও মূল্যায়নের সংকট
- প্রমাণ সবচেয়ে ঘন: ৮টি primary, দুটি independent তুলনা (P003, P004)।
- Coverage ছাদ ও এর কারণ সুপ্রতিষ্ঠিত।
- LLM-যুগে নতুন tool এসেছে, কিন্তু তাদের neutral তুলনা নেই (G10)।
- Semantic oracle সক্রিয় প্রতিযোগিতার এলাকা (G6 weakened)। তাই নতুন গবেষকের জন্য এটি ঝুঁকিপূর্ণ।
- **সবচেয়ে কম প্রতিযোগিতাপূর্ণ সুযোগ:** spec ও implementation-এর অমিলের triage (G14)। এখানে P001-এর public dataset তাৎক্ষণিক ভিত্তি দেয়।

### T4 + T6 — “Spec-এর মান” অক্ষ
- দুটি cluster মিলে দেখায়:
  - Spec ও documentation-এর মান ব্যাপকভাবে খারাপ (P004, P018, P027, P028)।
  - এটি মানুষের বোঝাপড়া ক্ষতিগ্রস্ত করে (P026)।
- কিন্তু **কোনো paper spec উন্নতির downstream প্রভাব নিয়ন্ত্রিতভাবে মাপেনি** (G9, G4)।
- Tool সহজলভ্য ও খরচ কম। তাই feasibility উচ্চ।

### T5 — স্পষ্ট লেখক-স্বীকৃত gap
- **G1/G2** তিনজন ভিন্ন লেখক-গোষ্ঠীর উল্লেখে সমর্থিত: P021, P023, P025 + P020-এর practitioner প্রমাণ।
- Search-এ syntactic dataset পাওয়া গেছে, কিন্তু behavioural label পাওয়া যায়নি।
- এটি **corpus-এর সবচেয়ে শক্তিশালীভাবে সমর্থিত gap।**

### T3 — গুরুত্বপূর্ণ, কিন্তু ব্যয়বহুল
- Security oracle-এর technique শক্তিশালী।
- কিন্তু বাস্তব benchmark-এর অভাব (G5) পূরণে নৈতিক ও manual খরচ বেশি।
- MCP security দ্রুত ভিড় জমাচ্ছে।

### T8 — উচ্চ প্রাসঙ্গিকতা, উচ্চ novelty-ঝুঁকি
- LLM agent এখন API-র নতুন consumer। T1, T4, T5, T6-এর জ্ঞান এখানে স্থানান্তরযোগ্য।
- কিন্তু ২০২৫–২০২৬-এ প্রকাশনার গতি অত্যন্ত দ্রুত (GV01, GV03, GV09)।
- তাই novelty দাবিতে বারবার যাচাই প্রয়োজন।

### T2, T7, T9 — সুপারিশের জন্য দুর্বল ভিত্তি
- **T2 ও T7:** corpus-এর gap বাইরের সাহিত্যে দ্রুত পূরণ হচ্ছে।
- **T9:** primary প্রমাণ দুর্বল (P038 substitute)।

## 3. পর্যবেক্ষিত মেটা-প্যাটার্ন
1. **Spec কেন্দ্রীয় সংযোগবিন্দু:** ৯টি cluster-এর মধ্যে ৬টিতে spec-এর মান সীমাবদ্ধতা হিসেবে এসেছে (T1, T3, T4, T5, T6, T8)।
2. **মূল্যায়ন-সংকট সর্বজনীন:**
   - Self-evaluation।
   - Seeded fault।
   - Live API।
   - Proxy metric (5xx, error-free invocation, AST match)।
3. **নতুন consumer হিসেবে LLM** পুরোনো gap-গুলোকে নতুন রূপে ফিরিয়ে আনছে:
   - Evolution → agent robustness।
   - Documentation → hallucination।
   - Security → MCP।
