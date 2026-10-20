# P028 — Automatic Detection of Five API Documentation Smells: Practitioners' Perspectives

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references বাদ) · **উৎস:** arXiv 2102.08486 / SANER 2021 version, ১২ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Junaed Younus Khan, Md. Tawkat Islam Khondaker, Gias Uddin, Anindya Iqbal (BUET; University of Calgary)
- **Venue:** IEEE SANER 2021, DOI 10.1109/saner50967.2021.00037
- **Cluster:** T6 (secondary: T7 — documentation-জনিত API misuse-এর পূর্বশর্ত)
- **ধরন:** Smell catalog + benchmark + practitioner survey + ML detection

## B. Motivation
- API documentation নিজেই একটি software product; খারাপ documentation adoption ক্ষতিগ্রস্ত করে (p.1 L45–52)।
- গবেষণা মূলত “**what**” সমস্যায় (code-comment inconsistency, obsolete doc, summary generation) — “**how**” (presentation/design) সমস্যার স্বয়ংক্রিয় শনাক্তকরণে কোনো কাজ নেই (p.1 L53–86)।

## C. Research questions
- RQ1: developer কি catalog ও উদাহরণের সঙ্গে একমত? RQ2: smell-এর প্রভাব কীভাবে অনুভূত? (p.5 L401–403)
- RQ3: rule-based classifier কতটা নির্ভুল? RQ4: shallow ML কি rule-কে ছাড়িয়ে যায়? RQ5: deep ML কি shallow-কে ছাড়িয়ে যায়? (p.7 L560–564)

## D. Contributions
- পাঁচটি API documentation smell-এর catalog: **Bloated, Excess Structural Information, Tangled, Fragmented** (Uddin & Robillard-এর IBM study থেকে) + **Lazy** (অপর্যাপ্ত বর্ণনা) (p.1 L88–98; p.2 L204–225)।
- ১,০০০ unit-এর প্রথম real-world benchmark; ২১ জন developer survey; rule-based, shallow ও deep classifier suite; replication package (disa-lab/SANER2021-DocSmell) (p.2 L107–135)।

## E. Methodology
- **Benchmark:** Java SE online API documentation crawl — ২১৭ package, ৪K+ class, **২৯K+ method**; focus group-এ ৫০টি labeled unit; তারপর random ৯৫০ — প্রথম দুই লেখক ৫০-এর batch-এ স্বাধীন label, তিন iteration-এ **Cohen's κ = ০.৮৩**; coding guideline দিয়ে **১৭ জন undergraduate** বাকি ৮০০ label করে (লেখকদের সঙ্গে পরামর্শ সহ) — মোট **১,০০০**, multi-label (p.3 L258–302)।
- **Survey:** ব্যক্তিগত যোগাযোগে ২১ জন professional (১৪ জনের <৫ বছর অভিজ্ঞতা); প্রতি smell-এ ২টি Javadoc উদাহরণ — সম্মতি (Likert), গত তিন মাসে frequency, severity (Blocker/Severe/Moderate) (p.5–6 L435–528)।
- **Rule-based:** ৬টি metric — documentation length, Flesch readability, acronym/jargon সংখ্যা, URL সংখ্যা, function/class/package নাম সংখ্যা, documentation ও method prototype-এর Levenshtein distance; percentile threshold (p.7 L619–639)।
- **Shallow:** OVR-, LPS-, CC-SVM (linear kernel), ML-kNN; feature: rule metric বা bag-of-words; permutation feature importance (p.8 L840–905)।
- **Deep:** Bi-LSTM (GloVe ১০০-d), **BERT-base** (১০ epoch, early stop, max ২৫৬ token); **৫-fold iterative stratified CV** (multi-label-এর জন্য) (p.7 L566–586; p.9 L1227–1247)।

## F. Dataset
- উপরে E — Java SE official reference documentation।

## G. Evaluation
- Accuracy, precision, recall, F1 per smell; survey-এর বর্ণনামূলক শতাংশ।

## H. Results (author-reported)
- **Prevalence:** ১,০০০-এর **৭৭৮টি (≈৭৮%)** অন্তত একটি smell; ৫২৪টিতে একটি, ১৯টিতে চারটি; Lazy সর্বাধিক (২৭৫); smell-এর মধ্যে phi correlation দুর্বল (Bloated/Excess/Tangled +০.২–০.৪; Lazy অন্যগুলোর সঙ্গে −০.২–০.৩) — smell-গুলো প্রায় স্বতন্ত্র (p.4–5 L368–419)।
- **RQ1:** প্রতিটি উদাহরণে ≥৫০% সম্মতি; Bloated, Tangled, Excess-এ >৭৫% (p.6 L489–497)।
- **RQ2:** ২১-এর ২০ জন (**৯৫.২%**) বলেন smell productivity কমায়; Lazy সবচেয়ে ঘন ও ক্ষতিকর (৯০% severity), Tangled ৮৫%; >৯০% বলেন smell ঠিক করা উচিত (p.1 L33–35; p.6–7 L529–544; p.10 L1432–1434)।
- **RQ3 (rule):** Bloated F1 ০.৯০, Lazy ০.৯৫; কিন্তু Excess ০.৪২, Tangled ০.৪১, Fragmented ০.৪৭ (p.8 L833–838)।
- **RQ4 (shallow):** OVR-SVM শ্রেষ্ঠ; Lazy ছাড়া সব smell-এ rule-কে ছাড়ায়; Documentation Length permutation-এ Bloated F1 ০.৮৮ → ০.৪২ (p.8 L866–905)।
- **RQ5 (deep):** **BERT সব smell-এ শ্রেষ্ঠ, F1 ০.৭৫–০.৯৭**; সেরা shallow-এর তুলনায় বৃদ্ধি: Excess +৫২%, Fragmented +৩৬.৪%, Tangled +৩৬.১%, Lazy +৬.৬%, Bloated +৫.৭%; ভুল — Java object/method-কে structural info ধরা, অন্য doc-এ রেফারেন্স চেনা (p.9 L1248–1271)।

## I. Strengths
- “How” documentation সমস্যার স্বয়ংক্রিয় শনাক্তকরণে প্রথম কাজ — স্পষ্ট gap।
- Benchmark নির্মাণে iterative κ ও coding guideline; multi-label-উপযোগী iterative stratification — পদ্ধতিগতভাবে সঠিক।
- Rule → shallow → deep ক্রমিক তুলনা + feature importance — ব্যাখ্যাযোগ্যতা।
- Replication package উন্মুক্ত।

## J. Explicit limitations (p.10 Threats)
- Internal: লেখক bias — ১৭ coder ও co-author agreement এবং সাহিত্য দিয়ে প্রশমন; train-test overlap নেই।
- Construct: data খোঁজার কঠিনতা — ২৯K unit প্রক্রিয়াকরণ।
- External: smell সাহিত্যের সঙ্গে corroborate; catalog পাঁচটিতে সীমিত, ভবিষ্যতে সম্প্রসারণযোগ্য।

## K. Inferred limitations (⚠️ অনুমান)
- **Java SE reference doc-এ সীমিত — Web/REST API documentation নয়:** OpenAPI description, developer portal, tutorial-এ smell-এর রূপ ভিন্ন (যেমন “Excess structural info” Javadoc-নির্দিষ্ট)। এই project-এর REST কেন্দ্রবিন্দুতে প্রয়োগযোগ্যতা পরোক্ষ।
- **৮০০টি unit একক student-coder labeled** — দ্বিতীয় coder বা κ নেই; “consulted with authors” প্রক্রিয়া পরিমাপযোগ্য নয়; label noise BERT-এর F1-কে প্রভাবিত করতে পারে। κ = ০.৮৩-কে “perfect agreement” বলা অতিরঞ্জন (প্রচলিত ব্যাখ্যায় “almost perfect”)।
- **Survey দুর্বল:** ২১ জন, ব্যক্তিগত যোগাযোগ, অধিকাংশ নবীন; লেখকদের নির্বাচিত উদাহরণ দেখিয়ে সম্মতি চাওয়া — acquiescence/leading-question bias; productivity প্রভাব self-report।
- **Smell সংজ্ঞা বিষয়ভিত্তিক:** Bloated/Lazy-এর সীমা (কত দীর্ঘ = bloated?) — rule-based length threshold-এ উচ্চ F1 হয়তো label-ই length-ভিত্তিক হওয়ার প্রতিফলন (circularity)।
- **Smell সত্যিই ক্ষতিকর কিনা** objective task performance দিয়ে পরীক্ষিত নয় (P026-এর মতো controlled experiment নেই)।
- Fix বা remediation কৌশল নেই — শুধু detection; ২০২১-এর পরে LLM দিয়ে detection+rewrite সহজলভ্য।
- Class imbalance-এর প্রভাব per-smell সংখ্যা ছাড়া পুরোপুরি মূল্যায়নযোগ্য নয় (Table V column-split)।

## L. Threats to validity
- উপরে J; inferable: single-coder labeling, survey bias, Java-only external validity।

## M. Reproducibility
- Benchmark, code, survey GitHub-এ — **উচ্চ**।

## N. Opportunities (hypothesis)
- **Web API documentation smell catalog ও detector:** OpenAPI `description`/`summary`, error documentation, example payload (P025-এ ভাঙা example #১–৪), developer portal — REST-নির্দিষ্ট smell (missing error semantics, undocumented constraints — P016 IDL-এর NL রূপ); RESTRuler (P027)-এর সঙ্গে design + documentation যৌথ linting।
- **LLM দিয়ে detection ও automatic rewriting** — BERT baseline-এর সঙ্গে তুলনা; rewrite-এর পর developer/LLM comprehension পরিমাপ।
- **Documentation smell × LLM tool-use সাফল্য:** tool/MCP description-এ Lazy/Tangled smell agent-এর ভুল tool call বাড়ায় কিনা (P033 ToolBench, P035 documentation-augmented generation, P036 MCP server) — T6↔T8 সেতু।
- **Documentation smell × API misuse** (T7): smell-যুক্ত API-তে misuse বেশি কিনা (P030/P031 dataset-এর সঙ্গে join)।
- Controlled experiment দিয়ে smell-এর objective প্রভাব (P026-এর পদ্ধতি অনুসরণে)।

## O. Relationships
- **Builds on** Uddin & Robillard (IBM survey) ও Aghajani et al. (documentation issue taxonomy)।
- **Complements P026/P027** — design rule (structure) বনাম documentation presentation (NL)।
- **Relates to P035** — documentation-এর মান LLM hallucination প্রশমনের কার্যকারিতা নির্ধারণ করে।
- **Relates to P020** — practitioner-রা OpenAPI-কে NL wiki দিয়ে সম্পূরক করেন; semantics প্রায়ই NL-এ বা অনুপস্থিত।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract (১,০০০ unit, ২১ dev, ৯৫.২%, F1 ০.৭৫–০.৯৭) | p.1 L13–40 |
| What বনাম how gap | p.1 L53–86 |
| পাঁচ smell উৎস | p.1 L88–98; p.2 L204–225 |
| Benchmark প্রক্রিয়া, κ ০.৮৩, ১৭ coder | p.3 L258–302 |
| Smell সংজ্ঞা ও উদাহরণ | p.3–4 L304–366 |
| Prevalence (৭৭৮), phi correlation | p.4–5 L368–419 |
| Survey পদ্ধতি | p.5 L435–453 |
| RQ1 সম্মতি | p.6 L489–497 |
| RQ2 severity/frequency | p.6–7 L498–544 |
| CV ও metric | p.7 L566–613 |
| Rule-based metric, RQ3 | p.7–8 L614–838 |
| Shallow ML, RQ4, feature importance | p.8 L839–905 |
| Deep ML, RQ5 | p.9 L906–1271 |
| Implications, ৯০% fix চায় | p.9–10 L1273–1434 |
| Threats | p.10 L1435–1451 |
| Conclusions | p.10 L1496–1507 |

**Document integrity:** Body সম্পূর্ণ; দুই-কলামের reading order কিছু জায়গায় মিশ্রিত (smell সংজ্ঞা অনুচ্ছেদ খণ্ডিত); **Table I–V column-split** — per-smell P/R/F1 সংখ্যা text-এ যা আছে তা-ই ব্যবহৃত; Fig.2–17 অনুপস্থিত।
