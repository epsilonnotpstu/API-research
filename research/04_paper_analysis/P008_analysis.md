# P008 — AGORA: Automated Generation of Test Oracles for REST APIs

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references ৮৪) · **উৎস:** supervisor-প্রদত্ত কপি (ISSTA 2023 published layout, pp.1018–1030), ১৩ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Juan C. Alonso, Sergio Segura, Antonio Ruiz-Cortés (SCORE Lab, Universidad de Sevilla)
- **Venue:** ISSTA 2023, DOI 10.1145/3597926.3598114 (ACM SIGSOFT Distinguished Artifact — PHASE B search অনুযায়ী)
- **Cluster:** T1 (oracle sub-problem; secondary: T6 — documentation/spec অসামঞ্জস্য ধরা পড়ে)
- **ধরন:** Original technique

## B. Motivation
- REST test generation tool-এর input generation উন্নত, কিন্তু **oracle সরল** — শুধু crash (5xx), spec-অমিল, regression ও best-practice লঙ্ঘন ধরে (p.1 L72–80)।
- Spec-conformant কিন্তু ভুল response (ভুল length/format, সংখ্যাগত সীমা, array সম্পর্ক) অধরা থাকে; surveys ও tool comparisons oracle-কে প্রধান চ্যালেঞ্জ বলেছে (p.1 L81–89)।

## C. Research questions (p.6–7 L1150–1202)
- RQ1: oracle তৈরিতে কার্যকারিতা (precision; baseline default Daikon)।
- RQ2: input dataset-এর আকারের প্রভাব।
- RQ3: তৈরি oracle কতটা failure ধরে?

## D. Contributions (p.2 L161–176)
- AGORA (black-box, OAS + পূর্ববর্তী request/response থেকে); **Beet** (OAS→Daikon instrumenter, open-source); **১০৫ ধরনের invariant**-সহ customized Daikon; empirical মূল্যায়ন ও ১১টি বাস্তব bug; replication package + VM।
- দাবি: REST API-তে likely-invariant detection-এর “first approach” (p.3 L421–423)।

## E. Methodology
- **Pipeline (Figure 1):** OAS + API request/response (CSV) → Beet → declaration file + data trace → customized Daikon → likely invariants → (developer নিশ্চিত করলে) oracle।
- **Beet (p.4–6):** প্রতি operation ENTER/EXIT program point; nested JSON object flatten; **array of objects-এর জন্য recursive নতুন nesting level (EXIT2…)** যাতে array element-এর property-তে invariant পাওয়া যায়।
- **Invariant নকশা (p.6 L1119–1140):** RapidAPI-র ৪০টি API (৭০২ operation) বিশ্লেষণ করে — **২২টি নতুন invariant**, ৩৬টি default বাদ, ৯টি নিষ্ক্রিয় সক্রিয়। পাঁচ শ্রেণি: arithmetic comparison (৪৮), array property (২৩), specific format (২২ — URL, date, length), specific value (৯), string comparison (৩)।
- **সীমা:** শুধু operation-level (sequence নয়), শুধু JSON (p.4 L570–575)।

## F. Dataset ও setup
- **১১টি operation, ৭টি industrial API (Table 2):** Amadeus Hotel, GitHub (২), Marvel, OMDb (২), Spotify (৩), Yelp, YouTube।
- Spec: অফিসিয়াল; OMDb ও Yelp-এর spec **manually তৈরি**; Spotify/YouTube APIs.guru থেকে নিয়ে হালনাগাদ; ভুল/অসম্পূর্ণ spec হাতে সংশোধন (p.7 L1208–1218)।
- **RESTest দিয়ে প্রতি operation ১০K valid (2xx) call** (মোট ১১০K); ≥৯০% response-এ ফল থাকা নিশ্চিত; **diversity-র জন্য হাতে বানানো data dictionary** (p.7 L1219–1240)।
- Laptop (i7, 32GB) (p.7 L1191–1193)।

## G. Evaluation
- **RQ1/RQ2:** ৫০, ১০০, ৫০০, ১K, ১০K request-এর random subset; invariant-গুলো **লেখকরা হাতে true/false positive শ্রেণিবদ্ধ করেছেন** (প্রতিটি ≥২ লেখক; মতভেদে docs বা developer); ENTER (input-only) invariant precision-গণনার বাইরে (p.7 L1165–1182; p.10 L2001–2005)।
- Baseline: default Daikon (Beet-সহ; combinatorial explosion-কারী ১৩টি invariant বাদ দিয়ে) — **তুলনীয় অন্য কোনো approach নেই** (p.7 L1183–1190)।
- **RQ3:** JSONMutator দিয়ে **response-এ** single error seed (১২টি operator: Boolean/number/string পরিবর্তন, array element বাদ/ক্রম বদল); **শুধু spec-conformant mutant** (syntactic mutant ও null বাদ); ৫০-request-এর oracle → ৭২৪টি Java assertion; প্রতি operation ১K response × ১০০ repetition = **১.১M seeded error**; FDR = কোনো assertion লঙ্ঘিত হলে detected (p.8–9 L1435–1908)।

## H. Results (author-reported)
- **RQ1 (Table 2, ১০K):** AGORA precision **৮১.২%** (৯৪৮টির ৭৭০ বৈধ) বনাম default Daikon ৫১.৪% (৭০৬-এর ৩৬৩); সব operation-এ AGORA ভালো; operation-ভেদে ৫০% (Yelp) থেকে ১০০% (Spotify createPlaylist); invariant সংখ্যা ও response field সংখ্যার Spearman ~০.৯ (p.7 L1254–1282)।
- **False positive-এর ৭৫.৮% arithmetic comparison** থেকে (যেমন duration_ms > artists সংখ্যা); এগুলো বাদ দিলে precision **৯৩.৬%** (p.8 L1283–1290)।
- **RQ2:** ৫০ request-এই **৭৩.২%** (arithmetic বাদে ৮৭.৬%); বৃদ্ধি সীমিত; ৫০ request সেরা খরচ-লাভ (p.8 L1292–1420)।
- রানটাইম: Beet ০.৩–৪৯.৯s, Daikon ০.২–১৫.৬s; ১০K-এ ~১ মিনিট (p.8 L1387–1392)।
- **RQ3 (Table 3):** **FDR ৫৭.৩%** (২০.৮% OMDb bySearch থেকে ৯২.৩% GitHub createRepo); অধরা মূলত unique string-এ পরিবর্তন (যেমন movie title) (p.9 L1909–1918)।
- **বাস্তব bug (p.9–10):** ৫টি API-র ৭টি operation-এ **১১টি domain-specific bug** (৪টি confirmed, ২টি fixed) — Amadeus-এ শূন্য-bed রুম (fixed), GitHub-এ ভুল license (confirmed) ও documentation update, Marvel-এ ০ পৃষ্ঠার comic ও ভুল code, OMDb-তে undocumented “game” মান, YouTube-এ অঞ্চলে অনুপলব্ধ video (confirmed)।
- Invariant-এর **দ্বৈত ভূমিকা:** অবৈধ invariant (manual inspection) learning-কালীন fault প্রকাশ করে; বৈধ invariant-এর লঙ্ঘন production fault ধরে (p.10 L1940–1947)।

## I. Strengths
- **Oracle problem-এ সরাসরি অবদান** — P001/P002/P003-এর চিহ্নিত মৌলিক দুর্বলতা।
- Black-box, tool-agnostic (OAS + traffic) — যেকোনো generator-এর সঙ্গে যুক্তযোগ্য; কম data-য় (৫০ request) কার্যকর; দ্রুত।
- বাস্তব, developer-স্বীকৃত semantic bug — যা 5xx/spec oracle কখনো ধরত না।
- Open-source Beet, replication package, VM।

## J. Explicit limitations (p.10 L1983–2022)
- OMDb/Yelp spec হাতে তৈরি — ভুলের সম্ভাবনা (≥২ লেখক পর্যালোচনা)।
- Input diversity হাতে বানানো dictionary-নির্ভর — “naive and conservative”; adaptive random testing ভালো হতে পারে।
- Invariant শ্রেণিবিন্যাসে মানব-পক্ষপাত (≥২ লেখক)।
- Random subset একবারই — **পুনরাবৃত্তি নেই** (manual শ্রেণিবিন্যাসের খরচে)।
- ১১টি operation-এ সাধারণীকরণ সীমিত; invariant-তালিকা সম্পূর্ণ নয়।
- Future: invariant থেকে স্বয়ংক্রিয় assertion, Web API হিসেবে deploy; sequence-level invariant (p.4)।

## K. Inferred limitations (⚠️ অনুমান)
- **RQ3-এ construct-validity ঝুঁকি:** mutation operator (string length/format, number, array) এবং invariant শ্রেণি (length, format, numeric bound, array) প্রায় একই ধরনের — ফলে FDR আংশিকভাবে নকশাগতভাবে অনুকূল; **বাস্তব semantic fault-এর বণ্টন** (যেমন ভুল business logic, ভুল সম্পর্কিত resource) প্রতিনিধিত্ব পায় না।
- **Recall অজানা:** বাস্তব bug-এর কত অংশ AGORA ধরে, তা মাপা হয়নি (১১টি bug anecdotal)।
- **False positive-এর manual খরচ:** ৯৪৮টি invariant-এর ১৮.৮% ভুল — প্রতিটি নিশ্চিত করতে মানুষের সময় লাগে; বড় API-তে (GitHub-এ ১৯৮টি invariant) scalability প্রশ্ন।
- **Baseline দুর্বল:** default Daikon-ও লেখকদের Beet দিয়ে চালানো এবং কিছু invariant বাদ দিয়ে — অন্য oracle কৌশল (metamorphic, LLM-ভিত্তিক) তুলনায় নেই (২০২৩-এ LLM-oracle সীমিত ছিল)।
- **Training data তৈরিতে একই group-এর RESTest** — input distribution AGORA-র ফলকে প্রভাবিত করে।
- Stateful (write-heavy) API-তে প্রযোজ্যতা অপরীক্ষিত — বেশিরভাগ operation read।

## L. Threats to validity
- Stated: internal (spec, diversity, labeling, single split), external (operation সংখ্যা, invariant সাধারণতা)।
- Inferable: construct (output-mutation ≠ real faults), evaluator bias (লেখকরাই labeler)।

## M. Reproducibility
- Zenodo 10.5281/zenodo.7970822 (code, data, VM) ✅; Beet GitHub-এ; industrial API সময়ের সঙ্গে বদলায় — নতুন request দিলে invariant ভিন্ন হতে পারে।

## N. Opportunities (hypothesis)
- **Sequence-level / stateful invariant** (লেখকদের future work) — CRUD lifecycle-জুড়ে।
- **LLM দিয়ে invariant ফিল্টারিং বা ব্যাখ্যা** — false-positive পর্যালোচনার খরচ কমানো; বা documentation থেকে invariant প্রস্তাব।
- **বাস্তব fault-benchmark-এ মূল্যায়ন** (output-mutation-এর বদলে) — oracle গবেষণার মূল্যায়ন-ঘাটতি।
- Invariant-কে spec-এ ফেরত লেখা (spec enrichment: pattern, minLength, enum) — T4 সংযোগ।
- Online testing (P001)-এর সঙ্গে সমন্বয়।

## O. Relationships
- **Addresses gap stated by:** P001 (oracle সীমা), P002 (oracle problem ৫টি paper-এ; automated oracles open challenge), P003, P004।
- **Same group:** P001 (RESTest), P009, P016 (IDL)।
- **Extended by:** AGORA+ (TOSEM 2025, তালিকার বাইরে)।
- **Complementary to:** P015 (access-policy oracle), P012 (mass-assignment oracle) — semantic oracle-এর ভিন্ন রূপ।
- **T6 সংযোগ:** OMDb/GitHub documentation অসামঞ্জস্য ধরা — documentation quality-র প্রমাণ।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Oracle-সীমা motivation | p.1 L72–89 |
| Contributions | p.2 L161–176 |
| Workflow, Beet | p.4 Figure 1; p.4–6 L626–1075 |
| Operation-level/JSON সীমা | p.4 L570–575 |
| ১০৫ invariant, শ্রেণি | p.6 L1106–1140 |
| RQs | p.6–7 L1150–1202 |
| Dataset, spec সংশোধন, dictionary | p.7 L1206–1240 |
| Setup, labeling, baseline | p.7 L1165–1193 |
| RQ1 ফল (৮১.২%) | p.7–8 L1254–1290; Table 2 p.9 |
| RQ2 (৫০ request ৭৩.২%) | p.8 L1292–1420 |
| RQ3 সেটআপ | p.9 L1818–1908 |
| RQ3 ফল (৫৭.৩%) | p.9 Table 3; L1909–1918 |
| ১১টি bug | p.9–10 L1920–1981 |
| Threats | p.10 L1983–2022 |

**Document integrity:** Listing (Daikon file, JSON) পাঠযোগ্য; Table 2 কলাম-ভাঙা — TOTAL সারি পুনর্গঠনযোগ্য (৫০: Daikon ৪০.২%/AGORA ৭৩.২% … ১০K: ৫১.৪%/৮১.২%); Figure 2 (sunburst) ও Figure 3-এর মান আংশিক; abstract অংশে ACM reference text মিশে গেছে (conversion ক্রম)।
