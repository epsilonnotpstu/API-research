# P002 — Testing RESTful APIs: A Survey

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references তালিকা শুধু গণনা — ১৭২টি) · **উৎস:** `03_papers_markdown/P002.md` = **arXiv 2212.14604v1 (৩০ Dec 2022)**, ৩৯ পৃষ্ঠা; TOSEM 2023 published version-এর সঙ্গে পার্থক্য থাকতে পারে · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Amid Golmohammadi, Man Zhang, Andrea Arcuri (Kristiania University College; Oslo Metropolitan University)
- **Venue/Year:** ACM TOSEM 2023, DOI 10.1145/3617175 (পঠিত: arXiv v1)
- **Cluster:** T1 (survey)
- **ধরন:** Systematic literature review (৯২টি article)

## B. Research motivation
- REST API ব্যাপক ব্যবহৃত; পরীক্ষা কঠিন কারণ network message + database setup + external service mocking লাগে (p.1 L36–39)।
- ২০১৭-এর পর গবেষণা বিস্ফোরণ, কিন্তু পূর্ববর্তী web-service survey পুরোনো (২০০৯, ২০১৩); একমাত্র সাম্প্রতিক survey (Applied Sciences 2022) মাত্র ১৬টি article (p.4 L301–323)।

## C. Research questions (১২টি; p.5 L333–351)
- **Publication status:** RQ1 প্রতি বছর কত paper; RQ2 venue; RQ3 contribution ধরন।
- **Approaches:** RQ4 metrics; RQ5 techniques; RQ6 testing type; RQ7 evaluation artifact।
- **Tools:** RQ8 open-source research tool; RQ9 non-research tool; RQ10 feature।
- **Challenges:** RQ11 addressed; RQ12 open।

## D. Main contributions
- ৯২টি article-এর শ্রেণিবিন্যাস: metrics taxonomy (Figure 5), technique taxonomy (Table 5), testing type (Table 6), artifact (Figure 7), ১৬টি open-source tool (Table 7), ২০টি non-research tool (Table 8), tool feature (Table 9), addressed challenges (Table 10), open challenges (Table 11)।
- নিজেদের দাবি: পূর্ববর্তী survey-র চেয়ে অনেক বড় (৯২ বনাম ১৬) ও বেশি দৃষ্টিকোণ (p.5 L320–323)।

## E. Methodology (SLR)
- **Databases (Table 1, p.6):** IEEE (৮৫), ACM (১৮), ScienceDirect (১৭), Wiley (২), Web of Science (১২), MIT Libraries (১৯), Springer (৯০); search তারিখ **১ March 2022** (p.5 L368–369)।
- Provider-ভিত্তিক সীমা (Springer-এ advanced query নেই; ScienceDirect-এ ≤৮ boolean, wildcard নেই) (p.6 L445–452)।
- **Inclusion (Table 2, p.7):** ইংরেজি; testing-সম্পর্কিত; REST-সম্পর্কিত (একচেটিয়া নয়); thesis নয়; survey নয়।
- **Snowballing:** forward ও backward, **১৪ June 2022**, Google Scholar দিয়ে; ৪০টি search থেকে + ৫২টি snowballing থেকে = ৯২ (p.7 L488–509)।
- **Data extraction:** দুই লেখক ভাগ করে, অন্যজন double-check, মতভেদে তৃতীয় লেখক (p.7 L523–525)।
- ⚠️ Quality assessment (paper-এর মান যাচাই) ধাপ উল্লেখ নেই।

## F. Dataset
- ৯২টি article (২০০৯–জুন ২০২২)। Search query-গুলো Table 1-এ পুনরুৎপাদনযোগ্যভাবে দেওয়া।

## G. Evaluation / synthesis method
- Descriptive frequency analysis; statistical synthesis নেই (survey-র জন্য স্বাভাবিক)।

## H. Actual results (author-reported)
- **RQ1:** ২০১৭-এর আগে ০–২/বছর; ২০১৮-এ ৮, **২০২১-এ সর্বোচ্চ ২৪** (p.8 L583–590)।
- **RQ2:** ৬৩টি venue; ৬৬ conference paper (৪৩টি “other conferences”), ২০ journal, ৬ arXiv; ICSE ৭, ICST ৬, TOSEM ৫ (p.9 L663–673)।
- **RQ3:** ৬৬% নতুন automated approach; ১৮% analysis approach; empirical comparison মাত্র ৩% (p.10 L803–812)।
- **RQ4:** fault detection সবচেয়ে বেশি ব্যবহৃত metric (5xx, schema violation, rule violation); তারপর coverage (schema ও code); **performance metric বিরল** (p.17 L1202–1207)। Figure 6-এর পাঠযোগ্য সংখ্যা: schema cov n=30, 5xx ১৭/১৬ প্রভৃতি (মান-কলাম অনিশ্চিত)।
- **RQ5:** ৬১/৬২টি approach-এর **৭৩% black-box**; white-box মূলত search-based, এবং **সব white-box কাজ EvoMaster platform-এর ওপর** (p.18 L1266–1268; p.20 L1378–1382)।
- **RQ6:** system testing ৭২/৯২; security ৮, integration ৮, unit ৫, robustness ৩, regression ২, architecture ১, acceptance ১ (Table 6, p.21)।
- **RQ7:** local open-source ৩০%, internet API ২৮%, artificial ১৬%, closed-source local ৭%, **কোনো case study নেই ১৪%**; EMB ১৭টি paper-এ ব্যবহৃত (p.22–23 L1548–1582)।
- **RQ8:** ১৬টি open-source tool, ৪৪টি paper; EvoMaster ১৯, RESTest ৮, RESTler ৮ (p.23 L1735–1750)।
- **RQ9:** ২০টি non-research tool; RestAssured ১২টি paper (p.24 L1795–1796)।
- **RQ10:** ১২/১৬ tool OpenAPI নেয়; authentication ৮টি tool-এ; DB reset ও code instrumentation শুধু EvoMaster (p.25 L1996–2009)।
- **RQ11 (Table 10):** resource dependency ৮, inter-parameter dependency ৬, **oracle problem ৫**, database ৩, white-box heuristics ৩, mocking ২, coverage criteria ২, instance identification ২।
- **RQ12 (Table 11):** tool support ২৫, **more REST case studies ১৩**, **security testing ১০**, resource handling ৪, classifying test results ৪, external services ৪, white-box heuristics ৪, database ৪, **automated oracles ৪**, performance ৩, non-functional ২, load ১, metamorphic ১, underspecified schemas ১ (p.28)।

## I. Strengths
- Search query সম্পূর্ণ প্রকাশিত; snowballing; double-check data extraction।
- Open challenge-এর গণনাভিত্তিক তালিকা (Table 11) — Class A gap-এর কাঠামোবদ্ধ উৎস।
- Tool-feature matrix (Table 9) — tool-নির্বাচনে কার্যকর।

## J. Explicit limitations
- কিছু প্রাসঙ্গিক article বাদ পড়তে পারে; manual নির্বাচন/extraction-এ ভুল সম্ভব (p.29 L2362–2381)।
- **লেখকরা ৯২টির ১৬টি article-এর লেখক** — নিজেদের কাজ সঠিক বোঝা গেলেও অন্যের কাজ ভুল বোঝার ঝুঁকি স্বীকৃত (p.29–30 L2372–2381)।
- Tool feature তথ্য অসম্পূর্ণ হতে পারে (p.23 L1730–1734; p.25 L1993–1995)।

## K. Independently inferred limitations (⚠️ বিশ্লেষকের অনুমান)
- **সময়-সীমা:** search মার্চ ২০২২, snowballing জুন ২০২২ — **LLM-ভিত্তিক REST testing (P005, P007, ২০২৪–২৫) সম্পূর্ণ অনুপস্থিত**; ফলে “open challenges” LLM-যুগে কতটা খোলা আছে তা এই survey থেকে নির্ধারণ করা যায় না।
- **Quality appraisal নেই:** প্রতিটি article সমান ওজন — Table 11-এর গণনা “কতজন উল্লেখ করেছেন” মাপে, “কতটা গুরুত্বপূর্ণ” নয়।
- **Self-citation/group bias:** লেখক-দলের EvoMaster ১৯টি paper-এ; “সব white-box কাজ EvoMaster-ভিত্তিক” পর্যবেক্ষণ সঠিক হলেও survey-র দৃষ্টিভঙ্গি white-box-এর দিকে ঝুঁকতে পারে।
- **Venue quality বিশ্লেষণ নেই:** ৪৩টি “other conferences” — নিম্ন-মানের venue-র প্রভাব অজানা।
- Contribution শ্রেণির শতাংশে (৬৬%+১৮%+৩%+৮%+৪%=৯৯%) rounding; RQ5-এ “৬১ out of ৯২” বনাম Table 5 total ৬২ — ছোট অসামঞ্জস্য (p.17 L1197 বনাম p.17 L1213)।

## L. Threats to validity
- **Stated:** selection ও extraction bias, নিজেদের paper (p.29)।
- **Inferable:** construct — “open challenge” গণনা লেখকের future-work বাক্যের ওপর নির্ভরশীল (প্রায়ই রীতিমাফিক)।

## M. Reproducibility
- Query ও তারিখ প্রকাশিত ✅; extraction spreadsheet প্রকাশিত কিনা উল্লেখ নেই (⚠️ যাচাই হয়নি)।

## N. Opportunities (hypothesis)
- ২০২২–২০২৬ সময়ের (LLM-যুগ) update survey বা “challenge re-assessment” — Table 11-এর চ্যালেঞ্জগুলো নতুন tool-এ সমাধান হয়েছে কিনা তার মানচিত্র।
- **Performance/load testing** ও **classifying test results** অত্যন্ত কম আলোচিত (৩ ও ৪) — P001-এর Challenge #1-এর সঙ্গে মিল।

## O. Relationships
- **Supports:** P001 (oracle সীমা), P003 (open problems — একই লেখক দল), P004 (tool comparison)।
- **Context for:** P006 RESTler, P016 IDL (inter-parameter dependency), P008 AGORA (oracle problem), P025 (regression; Table 6-এ ২টি regression paper-এর একটি)।
- **Gap-সংযোগ:** security testing (১০টি paper-এ future work) → T3 cluster (P012–P015) এই চাহিদার প্রতিক্রিয়া।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| ১২টি RQ | p.5 L333–351 |
| Databases ও query | p.6 Table 1 L376–443 |
| Inclusion criteria | p.7 Table 2 L471–486 |
| Snowballing ও ৯২টি paper | p.7 L488–509 |
| Publication trend | p.8 L583–645 |
| Metrics summary | p.17 L1202–1207 |
| ৭৩% black-box; white-box = EvoMaster | p.17–20 L1222–1224, L1266–1268, L1378–1382 |
| Testing types | p.21 Table 6 |
| Artifacts (১৪% কোনো case study নেই) | p.22–23 L1543–1582 |
| Open-source tools | p.23 Table 7 L1592–1750 |
| Addressed challenges | p.27 Table 10 |
| Open challenges | p.28 Table 11 L2226–2356 |
| Threats (নিজেদের ১৬টি paper) | p.29–30 L2362–2381 |

**Document integrity:** Figure 1 (OpenAPI JSON) code হিসেবে পাঠযোগ্য; Figure 2, 3, 6-এর সংখ্যা ছড়িয়ে আছে (মান-লেবেল মিলানো অনিশ্চিত); Table 7, 8, 9 কলাম-ভাঙা কিন্তু বিষয়বস্তু পাঠযোগ্য; Figure 4, 5 (diagram) অনুপস্থিত; arXiv version — published TOSEM version-এর সংখ্যা ভিন্ন হতে পারে।
