# P003 — Open Problems in Fuzzing RESTful APIs: A Comparison of Tools

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references গণনা: ৭২) · **উৎস:** `03_papers_markdown/P003.md` = **arXiv 2205.05325v2 (৭ Jul 2022)**, ৩৩ পৃষ্ঠা · ⚠️ Published TOSEM 2023 version-এর abstract-এ “18 open-source—1 industrial and 1 artificial” (মোট ২০) বলা; পঠিত arXiv v2-তে ১৯টি API — version-পার্থক্য · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Man Zhang, Andrea Arcuri (Kristiania University College)
- **Venue/Year:** ACM TOSEM 2023, DOI 10.1145/3597205 (পঠিত: arXiv v2)
- **Cluster:** T1 (secondary: T4 — underspecified schema)
- **ধরন:** Empirical tool comparison + source-code-level qualitative analysis

## B. Research motivation
- বেশিরভাগ fuzzer black-box, remote API-তে প্রয়োগ — **code coverage রিপোর্ট হয় না**, তাই কোন কোড অপরীক্ষিত থাকে জানা যায় না; ধরা পড়া fault হয়তো শুধু input-validation-এর প্রথম স্তরে (p.1 L43–51)।
- সীমাবদ্ধতা না বুঝলে নতুন কৌশল নকশা সম্ভব নয়।

## C. Research questions (p.4 L201–204)
- **RQ1:** সাতটি black-box fuzzer line coverage-এ কেমন?
- **RQ2:** white-box fuzzing-এ coverage ও fault detection কত?
- **RQ3:** ফল আটকে রাখা মূল open problem কী কী?

## D. Main contributions (p.2 L69–73)
1. তাদের মতে বৃহত্তম ও বৈচিত্র্যময় REST fuzzer তুলনা।
2. Black-box metric নয়, **প্রকৃত line coverage** (JaCoCo/c8)।
3. প্রতিটি SUT-এর source code বিশ্লেষণ করে open problem-এর গভীর তালিকা।

## E. Technical methodology
- **Tools (version, ২৩ May 2022):** bBOXRT (commit 7c894247), EvoMaster 1.5.0 (লেখকদের নিজস্ব), RESTest 1.2.0, RestCT 1.0, RESTler v8.5.0, RestTestGen v22.01, Schemathesis 3.15.2 (p.2–3 L102–135)। Morest বাদ: open-source নয়, replication package expired (p.2 L92–93; footnote L117)।
- **Black-box (RQ1):** ৭ tool × ১৯ SUT × ১০ রান = ১,৩৩০ রান, প্রতিটি **১ ঘণ্টা** (৫৫.৪ দিন compute); tool শেষ হয়ে গেলে loop-এ পুনরায় চালানো; coverage HTTP call চলাকালীন মাপা (generated test নয়) (p.5 L376–407)।
- **White-box (RQ2):** EvoMaster white-box বনাম grey-box (একই instrumentation, random sampling) — ১০+১০ রান × ১৯ = ৩৮০ রান (১৫.৮ দিন); coverage EvoMaster-এর নিজস্ব instrumentation দিয়ে, তাই Table 2-এর সঙ্গে সরাসরি তুলনীয় নয় (p.10 L928–947; p.13 L1311–1321)।
- **RQ3:** tool log বিশ্লেষণ + সেরা test suite (EvoMaster) IDE-তে চালিয়ে প্রতিটি অপ্রাপ্ত branch-এর হাতে-কলমে বিশ্লেষণ (p.13 L1304–1310)।
- **Schema মেরামত:** প্রথম রানে শুধু ৩টি tool HTTP call করতে পেরেছিল; YAML/JSON রূপান্তর, OpenAPI v2→v3, scheme/host/server তথ্য যোগ করার utility দিয়ে সব tool চালানো হয় (p.6–7 L449–483)।

## F. Dataset ও experimental setup
- **১৯টি SUT (Table 1, p.4):** ৬টি NodeJS (JS/TS) + ১৩টি JVM (Java/Kotlin), এর একটি industrial (ind0); মোট ~২৮৫K file LOC, ৭৬K coverage-target line। বড়গুলো: languagetool (১৭৪K LOC), ocvn-rest (৪৫K)। EMB corpus থেকে।
- Authentication: ৫টি API-তে; ocvn-rest ও realworld-app-এর form-login dynamic token **কনফিগার করা হয়নি** (p.7 L491–500)।
- Hardware: Windows 10, Xeon 24 core, 192GB RAM (p.5 L389–390)।

## G. Evaluation
- Metric: line coverage (black-box), white-box-এ coverage + detected faults (EvoMaster-নিজস্ব গণনা)।
- **Fault detection black-box-এ মাপা হয়নি** — tool-ভেদে fault গণনার সংজ্ঞা ভিন্ন, stack-trace proxy (P004-এর পদ্ধতি) দুর্বল বলে যুক্তি (p.6 L408–426)।
- Statistics: Mann-Whitney-Wilcoxon U-test (EvoMaster বনাম প্রতিটি, ১১৪ তুলনা; Table 3), Vargha-Delaney Â12 (Table 4)।

## H. Actual results (author-reported)
- **RQ1 (Table 2, p.9):** গড় coverage — **EvoMaster BB ৫৬.৮%** (১৯-এর ১১টিতে সেরা), **Schemathesis ৫৪.৫%** (৭টিতে সেরা), RestTestGen ৪৫.৪%, bBOXRT ৪১.৯%, RestCT ৩৫.৪%, RESTler ৩৪.৬%, RESTest ৩৩.৬%। **কোনো tool ৬০%-এর বেশি নয়, সব ≥৩০%** (p.8 L554–562)। Ranking P004-এর সঙ্গে হুবহু মিলে যায় (p.7 L510–512)।
- রান-ভেদে বড় পার্থক্য: EvoMaster languagetool-এ ৯.১% (২৬.০–৩৫.১%), Schemathesis features-service-এ ১০.৫% (p.8 L539–545)।
- Industrial ind0-তে ৫টি tool ঠিক ৮.২% (p.7 L513–515)।
- **RQ2 (Table 4, p.11):** white-box গড় coverage ৪৫.৪% → **৫২.৯% (+৭.৫%)**, Â12 ০.৭৭; fault ৩৬.৫ → ৩৯.৯ (**+৩.৪, <১০% আপেক্ষিক**); ocvn-rest-এ white-box **খারাপ** (৩৫.৩% → ২৪.৮%) — fitness plateau (p.10–11 L948–1193)। প্রায় অর্ধেক SUT-এ এখনো ৫০%-এর নিচে।
- **RQ3 open problems (p.12–28):**
  1. **Schema-ত্রুটি:** ছয়টি SUT-এর schema-তে ভুল; বেশিরভাগ fuzzer crash করে (p.12 L1233–1240)।
  2. **JSON-এর বাইরে payload** (form-urlencoded) — শুধু EvoMaster সমর্থন করে (languagetool) (L1241–1246)।
  3. **Recursive (graph) object schema** (scout-api) (L1247–1253)।
  4. **HTTP execution bug** (RESTler-এর `//` double-slash; SSL) (L1254–1298)।
  5. **External services** (GitHub API কল আটকে থাকে; mocking নেই — WireMock) (p.14 L1363–1373)।
  6. **String length/regex constraint** (UUID ৩৬ char > EvoMaster-এর ১৬ char soft limit) (p.14–15 L1383–1452)।
  7. **Underspecified schema:** অনুপস্থিত header, field, endpoint, ভুল content-type (cwa-verification, cyclotron, languagetool, restcountries, proxyprint, ocvn-rest) (একাধিক স্থান)।
  8. **NoSQL (MongoDB) সমর্থন নেই**; NodeJS-এ SQL analysis নেই (p.15–17)।
  9. **Third-party validation (@Valid, javax.validation)-এ fitness gradient নেই** (ocvn-rest; ৩টি সমাধান-প্রস্তাব) (p.20–21 L1850–1915)।
  10. **Authentication/initial data setup** (proxyprint, spacex-api) (p.22, p.26)।
  11. **REST best-practice না মানা API** (location header নেই) — resource linking ব্যর্থ (p.26–27 L2271–2318)।
  12. **Integer equality sampling range tradeoff** (rest-ncs) (p.24 L2112–2121)।
- Discussion (p.27–28): prototype-গুলো ভঙ্গুর; schema-ত্রুটি black-box-এর জন্য “might not have a viable solution”; DB interaction; **কোনো fuzzer external service mocking করে না**।

## I. Strengths
- একমাত্র কাজ যা **প্রতিটি অপ্রাপ্ত branch-এর source-level কারণ** নথিভুক্ত করে — gap analysis-এর জন্য প্রাথমিক প্রমাণ।
- ১০ রান + statistical test + effect size; script ও SUT open (EMB, Zenodo)।
- লেখকরা নিজেদের bias খোলাখুলি স্বীকার করেছেন (p.3–4 L187–195)।

## J. Explicit limitations
- লেখকরা EvoMaster-এর নির্মাতা → bias সম্ভব (p.28 L2377–2380)।
- অন্য tool ভুল-কনফিগার হতে পারে (কম documentation) (L2372–2376)।
- ১৯টি API সাধারণীকরণযোগ্য না-ও হতে পারে; পরীক্ষা ব্যয়বহুল (৭১.২ দিন) (L2383–2390)।
- ১ ঘণ্টা budget “technically arbitrary” (p.5 L391–393)।
- Tool implementation তুলনা, technique নয় (p.27 L2330–2333)।

## K. Independently inferred limitations (⚠️ অনুমান)
- **EMB-নির্ভরতা:** SUT-গুলো EvoMaster-এর নিজস্ব benchmark — EvoMaster আগে থেকেই এগুলোতে টিউন করা (লেখকরা স্বীকার: “EvoMaster did not crash on any of them”, L2371) — home-advantage।
- **Schema মেরামত পক্ষপাত:** লেখকরা অন্য tool-এর জন্য schema পরিবর্তন করেছেন — এটি তাদের সাহায্য করলেও, বাস্তবে এই tool-গুলোর ব্যর্থতা গোপন করে।
- **Coverage ≠ fault-finding:** black-box-এ fault মাপা হয়নি; ফলে “সেরা tool” দাবি শুধু coverage-ভিত্তিক।
- **Dynamic auth কনফিগার না করা** কিছু tool-কে অসুবিধায় ফেলে থাকতে পারে।
- **LLM-যুগের আগের ফল (২০২২):** open problem-গুলোর কয়েকটি (underspecified schema, string constraint) পরবর্তী LLM কাজ (P005, P007) লক্ষ্য করেছে — এখনো খোলা কিনা পুনর্মূল্যায়ন দরকার।

## L. Threats to validity
- **Stated:** internal (misconfiguration, author bias), external (API সংখ্যা)।
- **Inferable:** construct — white-box coverage EvoMaster-নিজস্ব মাপ, JaCoCo নয়; NodeJS-এ boot-time coverage বাদ (p.13 L1318–1321)।

## M. Reproducibility
- সব script EvoMaster repository-তে, Zenodo-তে সংরক্ষিত; SUT EMB-তে ✅ (ind0 বাদে — proprietary)।
- Compute ভারী (৭১.২ দিন sequential)।

## N. Opportunities (hypothesis)
- **Underspecified schema সমস্যা** → spec inference (T4: P016–P019) ও LLM-ভিত্তিক spec enrichment-এর সরাসরি প্রেরণা; black-box-এ “viable solution নাও থাকতে পারে” দাবিটি LLM/doc-mining দিয়ে চ্যালেঞ্জযোগ্য।
- **External service mocking** for fuzzers (কোনো tool করে না) — স্পষ্ট author-documented gap।
- **NoSQL/MongoDB-aware** test generation।
- Third-party validation constraint (@Valid) থেকে gradient — lightweight static extraction।
- Field-name-ভিত্তিক type inference (uri, date) — LLM দিয়ে সহজে পরীক্ষণযোগ্য (p.26 L2250–2256 লেখকদের প্রস্তাব)।

## O. Relationships
- **Corroborates:** P004 (ranking হুবহু এক — দুটি স্বাধীন study-র মিল, যদিও ১০টি API সাধারণ)।
- **Contrast:** P004 fault-proxy হিসেবে stack trace ব্যবহার করে; P003 এর সমালোচনা করে।
- **Motivates:** P005/P007 (LLM দিয়ে input/dependency), P016 (inter-parameter dependency), P017–P019 (spec inference), P008 (oracle)।
- **Same group:** P002, P011, P015 (EvoMaster); P037-এর মতো dataset নয় কিন্তু EMB corpus।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Motivation (coverage রিপোর্ট হয় না) | p.1 L43–51 |
| Tool ও version | p.2–3 L84–135 |
| Bias স্বীকার | p.3–4 L187–195 |
| RQs | p.4 L201–204 |
| SUT statistics | p.4 Table 1 L213–334 |
| Black-box setup | p.5 L376–407 |
| Fault metric না নেওয়ার যুক্তি | p.6 L408–426 |
| Schema মেরামত | p.6–7 L449–483 |
| RQ1 ফল | p.7–9 L501–562; Table 2 |
| U-test | p.10 Table 3 |
| RQ2 ফল | p.10–11 L928–1193; Table 4 |
| Log issues | p.12–13 L1229–1298 |
| Source-code issues | p.13–27 L1300–2318 |
| Discussion summary | p.27–28 L2322–2361 |
| Threats | p.28 L2365–2390 |

**Document integrity:** Table 1–4 কলাম-ভাঙা কিন্তু মান-ক্রম সংরক্ষিত (Table 2-এর কলাম-ক্রম bBOXRT, EvoMaster BB, RestCT, RESTler, RESTest, RestTestGen, Schemathesis — গড় সারি দিয়ে যাচাই সম্ভব); code-figure-গুলো letter-spaced (“r e g i s t r a t i o n T o k e n”) কিন্তু পাঠযোগ্য; arXiv v2 — TOSEM version-এ API সংখ্যা ভিন্ন (২০)।
