# P009 — GraphQL: A Systematic Mapping Study

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references বাদ) · **উৎস:** ACM Comput. Surv. 55(10) Article 202, ৩৫ পৃষ্ঠা (CC-BY) · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Antonio Quiña-Mera, Pablo Fernandez, José María García, Antonio Ruiz-Cortés (Universidad Técnica del Norte; SCORE Lab, Universidad de Sevilla)
- **Venue:** ACM Computing Surveys 55(10), 2023, DOI 10.1145/3561818
- **Cluster:** T2 (secondary: T6 — governance/SLA/pricing roadmap)
- **ধরন:** Systematic mapping study (SMS) + GraphQL-এর conceptual framework

## B. Motivation
- REST-এর data-access সমস্যা: query complexity, over-fetching, under-fetching (n+1) (p.2 L70–77)।
- GraphQL-এর জনপ্রিয়তা বাড়ছে কিন্তু কোনো SLR/SMS নেই — গবেষকদের জন্য বৈশ্বিক দৃষ্টিভঙ্গির অভাব (p.3 L108–110; p.10 L361–365)।

## C. Research questions (p.11–12 L415–444; Kipling 5W+1H)
- RQ1 Who (লেখক/প্রতিষ্ঠান), RQ2 Where (venue), RQ3 What (empirical maturity), RQ4 When, RQ5 Why (setting/domain/SWEBOK), RQ6 How (contribution domain/type, components, public API), RQ7 frontiers (advantages, disadvantages, limitations, challenges)।

## D. Contributions
- GraphQL paradigm-এর conceptual framework — ৪টি উচ্চ-স্তরের ও ১৭টি নির্দিষ্ট component (p.4 L144–161; §2.2)।
- ৮৪টি primary study-র SMS, topic-independent ও topic-specific classification; supplementary dataset [45] (p.33 L1885–1888)।

## E. Methodology
- Petersen 2008/2015 ও Kuhrmann 2017 guideline (p.11 L402–404)।
- **Search string:** শুধু “graphql”; ACM DL, SpringerLink, IEEE Xplore, Scopus, DBLP, Google Scholar; ২০১৫ – ৩০ জুন ২০২১ (p.13 L468–472)।
- **Funnel:** ৩,১৮৫ → automatic filter ২৫৪ → duplicate বাদে ১৩৫ → inclusion/exclusion ৮০ → manual search +৪ = **৮৪** (p.13 L472–502; Fig.14)। Snowballing pilot করে নতুন কিছু পায়নি (L464–466)।
- **Inclusion:** peer-reviewed + **gray literature (Bachelor/Master/PhD thesis)**; **Exclusion:** non-peer-reviewed (NPREV) — ⚠️ thesis অন্তর্ভুক্তির সঙ্গে আপাত-বিরোধ (L479–489)।
- Quality assessment ইচ্ছাকৃতভাবে করা হয়নি (low stringency, SMS-এর রীতি) (p.13–14 L503–534)।
- Classification: Wieringa research type (Table 2 decision table), research method, setting, SWEBOK area, contribution domain (Provider/Client), contribution type, GraphQL component, public API (p.14–16)।
- Bias প্রশমন: প্রথম গবেষক mapping, দ্বিতীয় জন review, মতভেদ consensus-এ (p.17 L885–889); RQ6 classification একজন GraphQL expert দুবার করেছেন (p.23 L1390–1391)।

## F. Dataset
- ৮৪টি study (S01–S84), supplementary material [45]-এ; ২৯৮ authorship, ২৭০ গবেষক, ৮৬ প্রতিষ্ঠান, ৩৩ দেশ (p.18 L929–936)।

## G. Evaluation
- Descriptive frequency/percentage; কোনো inferential বা synthesis পদ্ধতি নেই (SMS-এর প্রত্যাশিত)।

## H. Results (author-reported)
- **RQ1:** ইউরোপ ৬০.৭৪%; সর্বাধিক লেখক USA; Linköping University শীর্ষ প্রতিষ্ঠান; Olaf Hartig ৬টি প্রকাশনা (p.18 L930–937; Table 4)। কোনো প্রতিষ্ঠিত বিশেষায়িত গবেষণা-সম্প্রদায় নেই (p.29 L1750–1752)।
- **RQ2:** conference ৪৬.০৭% (Discussion-এ ৪৬.৪৩% — ⚠️ অমিল); peer-reviewed ৬৯.০৫%, gray ৩০.৯৫% (p.19 L991–992); ৩৯টির মধ্যে ১৯টি conference GGS-ranked; WWW ও ESEC/FSE শীর্ষ (p.20 L1158–1160)।
- **RQ3:** evaluation/validation ৬১.৯১%; বাকিগুলো empirical evaluation ছাড়া (solution proposal, experience, opinion); কোনো philosophical paper নেই; evaluation-এ case study, validation-এ experiment/prototyping প্রধান (p.21–22 L1323–1345)।
- **RQ4:** ধারাবাহিক বৃদ্ধি; ২০১৯-এ সর্বোচ্চ বৃদ্ধি (১৭.৮৬%) (p.22 L1352–1357)।
- **RQ5:** academic ৭১.৪৩%, বাকিটা industry, **government শূন্য**; domain: development ৫২.৩৮%, computing ২১.৪৩%; SWEBOK “construction” ৫৫.৯৫%; ১৫টির মধ্যে মাত্র ৭টি SWEBOK area; **Testing মাত্র ৪টি study** (S10, S39, S50, S63) (p.23 L1377–1386; Table 9 L1419–1420; p.30 L1786–1788)।
- **RQ6:** Provider ৫৪, উভয় ২৬, **Client মাত্র ৪** (p.24 L1446–1447); ৮৪ paper থেকে ১২৭টি contribution; Implementation-এর ৪৩/৫৬ GraphQL API implementation; Analysis-এর ৩৫/৪৭ comparison (বেশিরভাগ REST বনাম GraphQL) (p.25–26 L1530–1565)। সবচেয়ে কম অধ্যয়িত component: **directives, validation, subscriptions** (p.27 L1587–1590)। ১৫টি public API, GitHub ও APIs.guru সর্বাধিক (L1591–1600)।
- **RQ7 (Table 13):** সুবিধা — performance (জটিল query-তে ১৬× [S34] থেকে ১৮৭× [S67] দ্রুত), response size ছোট, request সংখ্যা ১৭–১,০০২ থেকে ১-এ (p.28 L1673–1688); versioning সহজ। অসুবিধা — সরল single-endpoint query-তে REST-এর চেয়ে ধীর (২.৫× পর্যন্ত, [S80]) (p.29 L1707–1710)। সীমাবদ্ধতা — schema-তে private field নেই; **২০৯৪টি API-র ৩৯.৭৩% schema-তে cycle** [S10]; excessive query → DoS; HTTP cache অনুসৃত হয় না; mutation-এ polymorphism নেই (L1711–1723)।
- **উপসংহার:** REST স্থির, স্বল্প-data query-তে উপযুক্ত; GraphQL dynamic, বড় dataset-এ শ্রেয় (p.31 L1836–1838)।
- **Roadmap (p.31 L1838–1853):** (i) industrial-scale experiment ও quality characteristic; (ii) caching/security/schema/mutation best practice; (iii) governance, hybrid REST-GraphQL, **GraphQL testing**, SLA; (iv) **pricing/rate limit** non-functional দিক — GraphQL market-এ অনুপস্থিত।

## I. Strengths
- Funnel ও classification স্বচ্ছ; decision table দিয়ে research type disambiguation; supplementary dataset প্রকাশিত।
- GraphQL component-স্তরের mapping (mentioned/exemplified/used) — কোন অংশ অনধ্যয়িত তা সূক্ষ্মভাবে দেখায়।
- Paradigm-এর বিস্তারিত tutorial-ধর্মী ব্যাখ্যা নতুন গবেষকের জন্য উপযোগী।
- ACM CSUR (Q1), CC-BY।

## J. Explicit limitations (p.16–18 L740–917)
- Manual classification থেকে study selection error-এর ঝুঁকি (internal validity)।
- Generalizability: Petersen guide ও official spec অনুসরণ করে প্রশমন।
- Interpretive bias: প্রথম লেখক + তিন সহ-লেখকের পৃথক review ও consensus।
- ⚠️ পৃথক “Limitations” section নেই; validity অংশটি মূলত প্রশমন-বিবরণ।

## K. Inferred limitations (⚠️ অনুমান)
- **সংখ্যাগত অসামঞ্জস্য:** abstract/intro-তে প্রকাশনার গড় বার্ষিক বৃদ্ধি **১৬.৬৭%** ও Google Trends **১৩.৬১%** (p.3 L105–107), কিন্তু §3.1-এ যথাক্রমে **৬৬%** ও **৯৮%** (p.10 L369, L374); conference ৪৬.০৭% বনাম ৪৬.৪৩%। “০.০২ গুণ দ্রুত” (L1676–1677) ও “০.৩৬ গুণ ধীর” (L1708) — অর্থ অস্পষ্ট।
- **Coverage cut-off জুন ২০২১:** GraphQL testing/security-র মূল কাজগুলো (যেমন EvoMaster GraphQL, P010-এর cost analysis-এর পরবর্তী কাজ, LLM-যুগ) এর বাইরে — বর্তমান অবস্থা প্রতিফলিত নয়।
- **Search string শুধু “graphql”** — abstract/title-এ শব্দটি না থাকলে বাদ; ৩,১৮৫ → ২৫৪ automatic filter (TI, TA, EO, NC, NA) অস্বচ্ছ।
- **Thesis অন্তর্ভুক্তি বনাম “NPREV” বর্জন** — gray literature-এর মান নিয়ন্ত্রণ নেই; ৩০.৯৫% gray literature ফলাফলের ভার পরিবর্তন করতে পারে।
- **Performance দাবিগুলো** (১৬×, ১৮৭×) primary study থেকে অনূদিত, কোনো quality appraisal ছাড়া — heterogeneous setup; meta-analysis বা effect-size synthesis নেই। এগুলো প্রমাণ হিসেবে দুর্বল।
- Inter-rater agreement (যেমন Cohen's κ) রিপোর্ট নেই।
- লেখক-গোষ্ঠী (SCORE Lab) API SLA/pricing নিয়ে কাজ করে — roadmap (iv)-এ নিজস্ব গবেষণা-আগ্রহের প্রতিফলন সম্ভব।

## L. Threats to validity
- Descriptive, theoretical, generalizability, interpretive, repeatability (p.16–18) — উপরে J।
- Inferable: publication bias (শুধু English; subscription-এ অপ্রাপ্য বাদ — AVA)।

## M. Reproducibility
- Supplementary [45]-এ identification, primary-study ও mapping dataset — ভালো। Search string সরল, পুনরাবৃত্তিযোগ্য; তবে automatic filter-এর বিস্তারিত Fig.14-এ (markdown-এ হারিয়েছে)।

## N. Opportunities (hypothesis)
- **GraphQL testing** — SMS-এ মাত্র ৪টি testing study (২০২১ পর্যন্ত); T1-এর REST testing কৌশল (oracle, dependency, LLM input) GraphQL-এ স্থানান্তরের সুযোগ — P011 (RPC/GraphQL EvoMaster)-এর সঙ্গে যাচাই প্রয়োজন।
- **Subscriptions, directives, validation** — অনধ্যয়িত component; বিশেষত subscription (stateful, long-running) testing।
- **GraphQL security:** query depth/cost → DoS (P010 এই দিকের উত্তর); authorization at field level (T3-এর সঙ্গে সংযোগ)।
- **Schema cycle (৩৯.৭৩%)** — cycle-aware cost/test generation।
- **Client-side/consumption** গবেষণা (মাত্র ৪টি study) — usability, learning, LLM-সহায়ক query তৈরি (T8)।
- **Hybrid REST↔GraphQL migration** ও wrapper — T5 (evolution)-এর সঙ্গে সংযোগ।
- এই SMS-এর ২০২১-পরবর্তী update (rapid review) — সংকীর্ণ কিন্তু বৈধ গবেষণা-কাজ।

## O. Relationships
- **Context for P010** (GraphQL cost analysis — DoS সমস্যার সমাধান) ও **P011** (EvoMaster-এর RPC/GraphQL সম্প্রসারণ)।
- **Complements P002** (REST testing survey) — GraphQL-এ testing গবেষণার স্বল্পতা দেখায়।
- **Links T6:** SLA, pricing, governance roadmap।
- **Links T3:** DoS ও private-field সীমাবদ্ধতা।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| REST over/under-fetching | p.2 L70–97 |
| বৃদ্ধি ১৬.৬৭%/১৩.৬১% (abstract-intro) | p.3 L105–107 |
| বৃদ্ধি ৬৬%/৯৮% (§3.1) | p.10 L369, L374 |
| RQ1–RQ7 | p.11–12 L415–444 |
| Search, funnel ৩১৮৫→৮৪ | p.13 L468–502 |
| Inclusion/exclusion | p.13 L478–498 |
| Validity | p.16–18 L740–917 |
| RQ1 ফল | p.18 L926–937 |
| RQ2 venue | p.19–20 L983–1160 |
| RQ3 maturity ৬১.৯১% | p.21–22 L1316–1345 |
| RQ5 setting, SWEBOK | p.23–24 L1377–1423 |
| RQ6 domain (৫৪/২৬/৪) | p.24 L1446–1447 |
| Component gap | p.27 L1587–1590 |
| Public API | p.27 L1591–1600 |
| RQ7 advantages/limitations | p.28–29 L1616–1740 |
| Roadmap (i)–(iv) | p.31 L1838–1853 |
| Conclusions | p.32–33 L1856–1884 |

**Document integrity:** Body সম্পূর্ণ; Table 1–13 column-split (Table 5–7 কঠিনভাবে বিচ্ছিন্ন, publication-ID মিলানো যায় না); Table 2 (decision table) ঘূর্ণিত header-এর কারণে ভাঙা; সব figure (Fig.11–29) অনুপস্থিত — percentage text-এ আছে। Table 10-এর bold চিহ্ন (উভয়-domain) হারিয়েছে। বিশ্লেষণে ব্যবহৃত সব সংখ্যা চলমান text থেকে নেওয়া।
