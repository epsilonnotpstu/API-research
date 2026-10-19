# P011 — White-box Fuzzing RPC-based APIs with EvoMaster: An Industrial Case Study

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references বাদ; Fig.6 UML ও কোড-listing glyph-ভাঙা অংশ skim) · **উৎস:** arXiv 2208.12743v2 (৩ Feb 2023), ৩৮ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Man Zhang, Andrea Arcuri (Kristiania University College), Yonggang Li, Yang Liu, Kaiming Xue (Meituan)
- **Venue:** ACM TOSEM 2023, DOI 10.1145/3585009
- **Cluster:** T2 (secondary: T1 — search-based API fuzzing; T9 — microservices)
- **ধরন:** নতুন technique + tool + industrial case study

## B. Motivation
- Thrift, gRPC, Dubbo, SOFARPC-ভিত্তিক RPC API শিল্পে ব্যাপক (Meituan-এর Meituan Select-এ >১,০০০ web service), কিন্তু **আধুনিক RPC API-র automated testing-এর কোনো tool/গবেষণা নেই** (p.1 L49–57)।
- পূর্ববর্তী কাজে Meituan-এ EvoMaster প্রয়োগ করতে RPC-র উপর হাতে REST wrapper লিখতে হয়েছিল — সময়সাপেক্ষ, debugging কঠিন (p.2 L75–85)।

## C. Research questions (p.21 L1514–1517)
- RQ1: white-box fuzzing বনাম grey-box baseline; RQ2: code coverage; RQ3: industrial setting-এ বাস্তব fault।

## D. Contributions (p.2 L101–107)
- RPC API fuzzing-এর প্রথম পদ্ধতি; open-source tool (EvoMaster extension, >১০,০০০ LoC); ৫৪টি industrial RPC API (১,৪৮৯,৯৫৯ LoC) নিয়ে empirical study; ৪টির গভীর বিশ্লেষণ; lessons learned ও গবেষণা-চ্যালেঞ্জ।

## E. Methodology
- **RPC Schema specification (Fig.6):** RPCInterfaceSchemaDto, RPCActionDto, ParamDto (constraint: nullable, min/max size/value, precision/scale, pattern), TypeDto, ActionResponseDto, RPCExceptionInfoDto, CustomizedCallResultCode (p.10–12 L615–803)।
- **Schema extraction:** `.thrift`/`.proto` parse না করে **Java Reflection** দিয়ে RPCInterface (interface/abstract class) থেকে — framework-নিরপেক্ষ (JVM-এ)। ১৬টি `javax.validation` constraint ও Thrift metaDataMap থেকে constraint (p.12–15 L804–1019)।
- **Driver architecture:** core → JSON → driver (`/infoSUT`, `/newAction`) → প্রকৃত client library দিয়ে RPC call; latency বাড়ে কিন্তু configuration সহজ (p.12 L819–834; p.16 L1098–1112)।
- **Genotype:** RPC call-এর sequence; EvoMaster-এর ৮০+ gene পুনঃব্যবহার; নতুন BigDecimal/BigInteger gene, SeededGene (manual input/authentication) (p.15–16 L1021–1088)।
- **Result analysis:** HTTP status code-এর মতো কোনো standard নেই → ৭ ধরনের execution result (ER1 internal error … ER7 handled); exception category APPLICATION/TRANSPORT/USER/UNCLASSIFIED; Thrift-এর ২৪টি exception type (p.17 L1131–1178)।
- **Fitness (Table 1):** প্রতিটি function-এ Handled/Error, Success/Fail, null/non-null, empty/non-empty target; ER1 ও unexpected/declared exception-কে potential fault হিসেবে পুরস্কার; transport error পুরস্কারহীন (p.19)।
- **Search:** MIO (default) + taint analysis + adaptive hypermutation + SQL handling; প্রথম k = a×n test সব function×auth combination কভার করে (p.20)।
- **Output:** JUnit test; smart DB clean; flakiness keyword (date, token, time) assertion comment-out (p.20–21)।

## F. Dataset ও setup
- **Table 2:** thrift-ncs, thrift-scs (artificial, open-source) + CS1–CS4 (Meituan): মোট ২৬ interface, ১৬৭ function, ৭২ external service, ১৯৫,০৭২ LoC, ২২৯ SQL table (p.21)।
- Budget ১,০০,০০০ RPC call; **৩০ রান**; industrial রানে ৯.৪১–১৮.২৭ ঘণ্টা/রান, মোট **১২৯.১২ দিন** compute (p.23)।
- Industrial পরীক্ষা Meituan-এর প্রকৃত pipeline-এ, সব external service চালু; **খালি database** (p.22)।
- আরও ৫০টি API: Meituan নিজে (গবেষক ছাড়া) ১ রান × ১০ ঘণ্টা (p.22)।
- Baseline: EvoMaster-এর Random search (grey-box) ও Meituan-এর বিদ্যমান test (manual JUnit + replay)।

## G. Evaluation
- Line coverage, target coverage, fault (entry point + শেষ executed statement দিয়ে unique exception); Mann-Whitney U ও Vargha-Delaney Â12 (p.22–23)।

## H. Results (author-reported)
- **RQ1:** সব ৬টি case-এ p ≤ ০.০০১, Â12 > ০.৮০; relative improvement artificial-এ সর্বোচ্চ **৪৭%**, industrial-এ **১১.১৫%** (p.23 L1691, L1733–1734)।
- **RQ2:** artificial-এ ৮৮.২% ও ৭১.৯% line coverage; industrial CS1/CS2 **২৬.৮১%/২৬.০২%**, CS3/CS4 **১৫.৮৯%/৯.১৫%** (p.27 L2166–2168)। বিদ্যমান test-এর চেয়ে বেশি (CS4-এ সমান ৮.৩১%); বিদ্যমান test-এর ≥৭৭.০২% কভার করে (p.26)।
- **নিম্ন coverage-এর কারণ:** external service mock/instrument না হওয়া; business-logic-স্তরের input validation (external service-এ অস্তিত্ব যাচাই); বিশাল DTO (একটি input-এ ২,০২৪ লাইন, ২৫ field-এর nested DTO); CS4-এ ১০/৫৫ function client দিয়ে অপ্রবেশযোগ্য; অব্যবহৃত auto-generated DB code (p.26–27)।
- **৫০ API:** ১,৪৪৪,০৪৫ LoC; গড় **১৭.৪৯%** (সর্বোচ্চ ৫৯.১৬%, সর্বনিম্ন ৪.৩%) line coverage; **৮,৩৭৭** potential fault (API #24 একাই ২,২৫০ — authentication API) (p.27–29; Table 6)।
- **RQ3 (Table 7):** best-run suite-এর ৫৩৪টি test হাতে review (প্রথম লেখক + ৮ বছর অভিজ্ঞ QA manager) → **১২৬টি real fault**: L1 ২৪ (fix হবে), L2 ১৭ (কম গুরুত্বপূর্ণ), L3 ৮৫ (সহনীয়)। **৪১টি (L1+L2) fixed**। Potential fault গড় CS1 ৪০.২, CS2 ২১.৮, CS3 ৫১.৬, CS4 ৯১.৮ (p.28–29)।
- Automated oracle misleading/unexpected response ধরতে পারে না — formal spec নেই (p.29)।
- **Lessons (p.30–32):** industrial SUT reset ব্যয়বহুল (খালি DB clean ৫.৩ s → smart clean ২৮৫ ms, >৯০% হ্রাস); composite primary key সমর্থন নেই; external service mocking; production historical data ব্যবহারের চাহিদা; CI-তে অন্তর্ভুক্তি (Meituan driver স্বয়ংক্রিয় তৈরি করে, ৩০টি API-র driver); flakiness ও readability (exception-যুক্ত test আলাদা ফাইলে)।

## I. Strengths
- **শিল্প-বাস্তবতা:** ৫৪টি প্রকৃত industrial API, প্রকৃত pipeline, শিল্প অংশীদারের সঙ্গে fault triage — বিরল মাত্রার বহিঃস্থ বৈধতা।
- কঠোর পরিসংখ্যান (৩০ রান, U-test, Â12) — T1-এর বহু paper-এর (P005, P007) বিপরীতে।
- Framework-নিরপেক্ষ schema extraction (reflection) — `.proto` না থাকলেও কাজ করে।
- Lessons learned অংশ সৎ ও বিস্তারিত — ব্যর্থতার কারণ বিশ্লেষণ।
- Daily CI-তে গৃহীত।

## J. Explicit limitations (p.32 Threats; p.26–31)
- **Conclusion:** budget কেবল ১,০০,০০০ call — বেশি budget-এ CS3/CS4-এ ফল ভালো হতে পারে; ব্যয়ের কারণে পরীক্ষা হয়নি।
- **Internal:** implementation-এ ত্রুটি থাকতে পারে; industrial ফল গোপনীয়।
- **External:** কেবল Thrift (artificial) ও এক কোম্পানির Thrift-ভিত্তিক নিজস্ব framework; অন্য framework/কোম্পানিতে সাধারণীকরণ অনিশ্চিত; **industrial ফল পুনরুৎপাদনযোগ্য নয়**; open-source RPC corpus প্রয়োজন।
- gRPC-র result analysis এখনো প্রযুক্তিগত সম্প্রসারণ বাকি (p.18)।
- MIO ছাড়া অন্য search algorithm তুলনা scope-এর বাইরে (p.20)।
- External service, input validation, বড় DTO, DB state, flakiness — খোলা চ্যালেঞ্জ।

## K. Inferred limitations (⚠️ অনুমান)
- **Baseline দুর্বল:** একমাত্র tool-baseline নিজস্ব Random search; “অন্য কোনো RPC tool নেই” সত্য হলেও REST-wrapper + অন্য REST fuzzer বা EvoSuite-এর মতো unit generator (লেখকরাই সম্ভাব্য বিকল্প হিসেবে উল্লেখ করেন, p.8) তুলনা হয়নি।
- **Fault গণনার অসঙ্গতি ঝুঁকি:** “potential fault” (exception-location-ভিত্তিক) হাজারে, কিন্তু প্রকৃত fault-এর হার ১২৬/(~২০৫ গড় potential) — এবং ৮,৩৭৭-এর triage অসম্পূর্ণ; abstract-এর “৪১ real faults” আসলে ১২৬-এর মধ্যে L1+L2 — উপস্থাপনা সংকীর্ণ কিন্তু সঠিক।
- **Self-evaluation bias:** EvoMaster লেখকরাই tool নির্মাতা ও মূল্যায়নকারী (P002/P003-এর মতো একই গোষ্ঠী)।
- Oracle শুধু exception/5xx-সমতুল্য — semantic/functional bug (misleading response) ধরা পড়ে না; P008-এর মতো invariant oracle-এর প্রয়োজন।
- খালি database ব্যবহার — বাস্তব business scenario অনাবৃত; coverage কম হওয়ার এক কারণ নিজেরাই স্বীকার করেন।
- **GraphQL বা gRPC-এর উপর কোনো মূল্যায়ন নেই** — T2 cluster-এ এটি RPC (Thrift)-কেন্দ্রিক; “modern RPC” দাবি Thrift-এ সীমিত।
- Replication link “anonymous-authorxyz” (review-এর জন্য) — স্থায়ী artifact Zenodo-তে বলা হলেও case-specific package-এর স্থায়িত্ব যাচাই প্রয়োজন।

## L. Threats to validity
- উপরে J; inferable: construct (unique fault-এর সংজ্ঞা), external (এক কোম্পানি, এক framework পরিবার)।

## M. Reproducibility
- EvoMaster open-source (v1.5.0 Zenodo); artificial case (thrift-ncs/scs) EMB-তে; **industrial ফল পুনরুৎপাদন অসম্ভব**; compute ব্যয় বিশাল (১২৯ দিন)।

## N. Opportunities (hypothesis)
- **Open-source RPC/gRPC benchmark** (EMB-এর সমতুল্য) — লেখকরাই প্রয়োজনীয় বলেন; কম-infrastructure কিন্তু উচ্চ-প্রভাব গবেষণা কাজ।
- **External service mocking/virtualization** search-এর অংশ হিসেবে (P003-এর চ্যালেঞ্জের সঙ্গে মিল; T9 সংযোগ)।
- **LLM দিয়ে জটিল DTO/business-constraint input তৈরি** — P005/P007-এর LLM value generation RPC-তে স্থানান্তর।
- **Production traffic/historical data seeding** — privacy-সংরক্ষণ সহ।
- RPC-র জন্য **semantic oracle** (P008 AGORA-ধাঁচের invariant) ও fault classification/triage automation (৮,৩৭৭ potential fault-এর সমস্যা)।
- gRPC/Dubbo ও non-JVM language-এ সম্প্রসারণ; black-box `.proto`-ভিত্তিক বিকল্প।

## O. Relationships
- **Extends** EvoMaster (P002/P003-এর লেখক-গোষ্ঠী) — REST ও GraphQL-এর পরে RPC।
- **Confirms P003:** external service ও database state — সব ধরনের web API-তে সাধারণ চ্যালেঞ্জ।
- **Links T9** (microservice, CI integration) ও P038 (microservices testing SLR)।
- **Complements P009:** GraphQL/RPC-এর মতো non-REST paradigm-এ testing গবেষণার স্বল্পতা।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| RPC testing tool নেই | p.1 L49–57 |
| REST wrapper অভিজ্ঞতা | p.2 L75–85 |
| Contributions | p.2 L101–107 |
| RPC schema spec | p.10–12 L615–803 |
| Reflection-ভিত্তিক extraction, constraint | p.12–15 L804–1019 |
| Genotype, SeededGene | p.15–16 L1021–1088 |
| ER1–ER7, exception category | p.17 L1131–1178 |
| Fitness targets (Table 1) | p.19 |
| MIO, sampling | p.20 |
| Table 2 case studies | p.21 |
| RQs, setup, ৩০ রান | p.21–22 L1514–1600 |
| RQ1 (Table 3) ৪৭%/১১.১৫% | p.23 L1640–1734 |
| RQ2 coverage, existing tests | p.24–27 L1964–2168 |
| Table 6 (৫০ API) | p.28 L2200–2260 |
| RQ3 Table 7 (১২৬ fault) | p.28–29 L2466–2560 |
| Lessons learned | p.30–32 |
| Threats | p.32 |

**Document integrity:** Body সম্পূর্ণ; **Fig.6 (UML) সম্পূর্ণ glyph-garbage** (L638–762) — field নাম text থেকে পুনর্গঠিত; code listing (Fig.2, 3, 7) letter-spaced কিন্তু পাঠযোগ্য; Table 3, 5, 6 column-split — মূল সংখ্যা text ও Table 7 থেকে যাচাই করা হয়েছে (১২৬ = ২৪+১৭+৮৫)। Text-এ “88.2% on thrift-scs and 71.9% on thrift-scs” — মূল paper-এর typo (একটি ncs হওয়ার কথা)।
