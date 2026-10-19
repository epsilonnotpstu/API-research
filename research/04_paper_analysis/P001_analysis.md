# P001 — Online Testing of RESTful APIs: Promises and Challenges

**পাঠের অবস্থা:** সম্পূর্ণ পাঠ (body, tables-এর পাঠযোগ্য অংশ, references) · **উৎস:** `03_papers_markdown/P001.md` (idUS repository copy, ১৩ পৃষ্ঠা) · **বিশ্লেষক:** Claude · **তারিখ:** 2026-10-19
**Evidence location রীতি:** `p.N` = PDF পৃষ্ঠা, `L` = Markdown লাইন।

---

## A. Bibliographic identity
- **Authors:** Alberto Martin-Lopez, Sergio Segura, Antonio Ruiz-Cortés (SCORE Lab, Universidad de Sevilla)
- **Venue/Year:** ESEC/FSE 2022 (pp. 408–420), DOI 10.1145/3540250.3549144
- **Cluster:** T1 — REST/Web API testing & fuzzing (secondary: T6 spec–implementation consistency)
- **ধরন:** Original empirical study (industrial-scale, online testing)

## B. Research motivation
- শিল্পে **online testing** (production-এ API-কে ২৪/৭ পরীক্ষা) জনপ্রিয় হচ্ছে (Datadog, RapidAPI Testing, Sauce Labs), কিন্তু এসব প্ল্যাটফর্ম test *execution* স্বয়ংক্রিয় করে, test *generation* এখনো manual (p.1 L72–85)।
- গবেষণার test-generation tool-গুলো ল্যাবে মূল্যায়িত: অল্প কিছু open-source API, কয়েক হাজার test case, কয়েক ঘণ্টা, বা একটি প্রতিষ্ঠানের ভেতরে (p.2 L121–131; L186–191)।
- লেখকদের ভাষায় “clear gap between industrial solutions… and research approaches… limited to lab settings” (p.2 L128–131)।

## C. Research questions (p.3 L381–390)
- **RQ1:** Online testing-এর failure detection capability কত (সময়ের সঙ্গে)?
- **RQ2:** Fault detection capability কত (unique fault)?
- **RQ3:** বিভিন্ন test data ও test case generation কৌশলের মধ্যে পার্থক্য কী এবং তারা কীভাবে পরিপূরক?

## D. Main contributions (p.2 L109–114, L202–205)
1. Online testing-এর failure/fault detection capability-র মূল্যায়ন।
2. Test data ও test case generation কৌশলের তুলনা (online প্রেক্ষাপটে)।
3. ১৩টি industrial API-তে ২৫৪টি reproducible bug।
4. Online testing গ্রহণের ৫টি চ্যালেঞ্জ।
5. Multi-bot architecture-এর open implementation ও ১M+ test case / ৩৯০K failure-এর dataset (Zenodo 10.5281/zenodo.6941292)।
- **Novelty দাবি:** “first empirical study on the use of automated test case generation techniques for online testing of RESTful APIs in industrial-like settings” (p.3 L255–256)।

## E. Technical methodology
- **Tool:** RESTest (open-source, black-box, OAS-ভিত্তিক) — কিন্তু monolithic নকশা scale করেনি, তাই Facebook WES দ্বারা অনুপ্রাণিত **multi-bot architecture** (p.4 L594–608; Figure 1)।
- **Bot taxonomy (Table 2, p.4):** তিনটি মাত্রা — (১) write-safety: R (read-only) / RW; (২) test data: FD (fuzzing dictionaries), CDG (customized data generators), DP (data perturbation), SD (semantic data from DBpedia), CD (contextual data); (৩) test case: RT (random), CBT (constraint-based, inter-parameter dependency সন্তুষ্ট করে), ART (adaptive random)। মোট ৩১ ধরনের input bot সম্ভব (p.4 L587–588)।
- **নির্বাচিত:** ৭৫ test bot + ৩ garbage collector + ৭৫ test reporter (Allure) + ৭৫ coverage computer = **২২৮ bot** (p.5 L637–639)।
- **Configuration:** ১৫ দিন (৩৭৮ ঘণ্টা) নিরবচ্ছিন্ন; API quota মেনে iteration-ভিত্তিক; FD ও DP bot চারগুণ বেশি sleep করে (কম test budget) (p.5 L649–663)।
- **Test oracles (৬টি, p.5 L694–711):** F_5XXV (valid request-এ 5xx), F_5XXI (invalid request-এ 5xx), F_2XXP (parameter constraint লঙ্ঘনে 2xx), F_2XXD (inter-parameter dependency লঙ্ঘনে 2xx), F_400 (valid request-এ 400), F_OAS (response বনাম spec অমিল)।
- **Failure → fault clustering (p.5 L720–738; Table 3 p.6):** একই oracle + একই operation + একই status code ও content-type + normalized Levenshtein distance (NLD) threshold (যেমন response NLD < 0.5); F_OAS-এর জন্য dynamic value wildcard করে error log তুলনা। তারপর manual confirm/discard।
- **Input:** OAS spec (APIs.guru বা API website; Foursquare, RESTCountries, Yelp-এর spec লেখকদের পূর্ববর্তী কাজ থেকে) (p.3 L406–410)। **Output:** test report, coverage, fault cluster।

## F. Dataset ও experimental setup
- **১৩টি API (Table 1, p.3):** Amadeus, DHL, FDIC, Foursquare, LanguageTool, Marvel, Ohsome, OMDb, RESTCountries, Spotify, Stripe, Yelp, YouTube (Comments ও Search আলাদা) — মোট **১৮৯ operation, ১,৬৯৪ parameter**। বেশিরভাগ read-only।
- Ohsome-এর জন্য developers production-সমান instance দিয়েছিলেন (footnote, p.3 L425–430)।
- **Infrastructure:** একক VM — 512GB RAM, 32 CPU core, 2TB HDD (p.4 L577–580)।
- ⚠️ Table 1-এর কলাম pdftotext-এ ভেঙে গেছে (p.3 L263–379); totals (১৮৯/১,৬৯৪) body text থেকে নিশ্চিত।

## G. Evaluation
- **Metrics (p.5 L669–692):** failure/fault সংখ্যা (oracle-ভেদে), FDR ও FtDR, APFD, API test coverage (black-box coverage criteria [89]; সংশোধন: শুধু সফল response পাওয়া request-এর input element গণ্য)।
- **Baselines:** কোনো বাইরের tool নয় — তুলনা bot-কৌশলগুলোর মধ্যে (RQ3)। লেখকরা স্পষ্ট বলেছেন “we do not aim at doing a rigorous comparison of testing techniques” (p.4 L622–625)।
- **Statistical test:** নেই (descriptive)।

## H. Actual results (author-reported)
- **RQ1:** মোট **১,১০১,৮৪৬ test case** (Table 4 total, p.7 L1146), **৩৮৯,২১৬ failure** (≈১/৩); **২৪৩,৩৯৪ (৬৩%) F_OAS** — “API specifications poorly reflect the actual API implementation” (p.6 L795–797, L825–833)। FDR ০.০৪ (RESTCountries) থেকে ০.৭৯ (LanguageTool)। DHL ব্যান (quota মেনেও), Ohsome ও Yelp-এ outage (p.6 L772–781)।
- **RQ2 (FDIC, Ohsome বাদে ১১ API):** ২১৮,৪১৯ failure → ৫০২ potential fault → manual-এ **১৩৯ reproducible** + reporter থেকে ৮ = **১৪৭ fault**; ৭৩ (৫০%) F_OAS, ৫২ invalid-input-as-valid (F_2XXP/D), মাত্র ৬টি 5xx; ৮৭% fault প্রথম ৩ দিনে, ১০ দিনে সব (p.6 L839–855; p.8 L1944–1952)।
- **RQ3:** valid ও invalid data প্রায় সমান unique bug (৭৬ বনাম ৮১, ১০টি উভয়ে); **DP সবচেয়ে বেশি unique bug (৫৫)**, তারপর CDG (২৭); SD-ই একমাত্র কৌশল যা কিছু যোগ করেনি; CBT RT-এর চেয়ে cost-effective (YouTubeSearch-এ ~৫০ বনাম ~৭০০ test-এ সমান coverage); ART কোনো উন্নতি দেয়নি (Amadeus ছাড়া) (p.8–9 L1963–2015)।
- **সামগ্রিক:** ২৫৪ reproducible bug (২০৯ cluster থেকে, ৪৪ report থেকে, ১ garbage collector থেকে); ৬৫টি developer-স্বীকৃত/fixed; YouTube ও Amadeus-এ doc ও implementation fix (p.9 L2067–2078)।
- **Cost:** ৭৫ bot configure করতে ~২৬K LOC (৯৫% copy-paste); ৫০টি data dictionary, ৫২,০৮৪ value; RAM ও disk ১৫ দিনে ক্রমাগত বৃদ্ধি (p.10 L2158–2182)।
- ⚠️ **অভ্যন্তরীণ অসামঞ্জস্য:** p.6 L853 “147 faults in 12 APIs” বনাম p.8 L1945 “147 faults in 11 APIs” — PDF-এ মিলিয়ে দেখা দরকার।

## I. Strengths
- শিল্প-স্কেলের বিরল প্রমাণ: ১৩টি বাস্তব production API, ১.১M test, ১৫ দিন — ল্যাব-মূল্যায়নের সীমা সরাসরি চ্যালেঞ্জ করে।
- Developer-স্বীকৃত bug (৬৫) — false-positive সমস্যা আংশিক নিয়ন্ত্রিত।
- ৬ ধরনের oracle-এর স্পষ্ট সংজ্ঞা; F_OAS-এর আধিক্য একটি গুরুত্বপূর্ণ empirical তথ্য।
- Artifact (Zenodo) — উচ্চ reproducibility সম্ভাবনা।

## J. Explicit limitations (লেখকদের স্বীকৃত)
- Challenges (p.10 L2140–2210): **#1 Automated fault identification** — ৫০২ cluster-এর ৩৬৩টি ভুল-শ্রেণিকৃত, ৮টি bug cluster-এ ধরা পড়েনি; **#2 Effective human interaction** (active learning); **#3 Optimal testing-strategy selection** (open problem); **#4 Optimal test execution scheduling** (quota, খরচ); **#5 Computational resource optimization**।
- FDIC ও Ohsome-এর সব cluster manual বিশ্লেষণ সম্ভব হয়নি (sampling) (p.9 L2050–2065)।
- Threats (p.11 L2234–2276): RESTest-এ implementation-নির্ভরতা; clustering ত্রুটি; ১৩ API প্রতিনিধিত্বশীল না-ও হতে পারে।

## K. Independently inferred limitations (⚠️ বিশ্লেষকের অনুমান)
- **Oracle-এর সীমা:** ৬টি oracle-ই status code ও schema-নির্ভর — business-logic বা semantic ভুল (যেমন ভুল ডেটা ফেরত) ধরার উপায় নেই; ফলে “fault” সংখ্যা বাস্তব ভুলের নিম্নসীমা।
- **F_OAS-এর আধিক্য দ্ব্যর্থক:** spec ভুল নাকি implementation ভুল — আলাদা করা হয়নি; ৬৩% failure “spec দুর্বলতা” হিসেবেও পড়া যায়, যা T4 (spec inference)-এর গুরুত্ব নির্দেশ করে।
- **কৌশল-তুলনা confounded:** FD/DP bot-এর budget চারগুণ কম, এবং bot সংখ্যা কৌশলভেদে অসম (যেমন SD ৫টি, CDG ৩২টি) — RQ3-এর তুলনা কাঠামোগতভাবে পক্ষপাতদুষ্ট হতে পারে।
- **একক tool (RESTest) ও একই গবেষক-দল** — অন্য tool (EvoMaster, RESTler) online-এ কেমন করে তা অজানা।
- **Write-operation কম:** ১৩টির মধ্যে মাত্র ৪টিতে write — stateful/destructive online testing-এর ঝুঁকি (production data) সীমিতভাবে পরীক্ষিত।
- **Ethical/production impact:** production API-তে ১M+ request — API provider-এর সম্মতি (Ohsome ছাড়া) উল্লেখ নেই; DHL ban এর ইঙ্গিত দেয়।

## L. Threats to validity
- **Stated:** internal (tool bugs, clustering), external (API নির্বাচন) (p.11)।
- **Inferable:** construct validity — “fault” = cluster-নির্ভর সংজ্ঞা; NLD threshold heuristic (Table 3) যাচাই/সংবেদনশীলতা বিশ্লেষণ নেই। Time validity — API ২০২২-এ পরীক্ষিত; ফল সময়-নির্ভর (developer fix চলমান ছিল, p.6 L772)।

## M. Reproducibility
- Code, binaries, data, scripts — Zenodo [92] ✅।
- কিন্তু **production API সময়ের সঙ্গে বদলায়**, কিছু API-তে key/quota লাগে — হুবহু পুনরুৎপাদন অসম্ভব; dataset পুনর্বিশ্লেষণ সম্ভব।
- Hardware ভারী (512GB RAM VM)।

## N. Opportunities for improvement (hypothesis)
- Failure clustering-এ unsupervised ML / LLM-ভিত্তিক triage (Challenge #1) — dataset (৩৯০K failure) benchmark হিসেবে ব্যবহারযোগ্য।
- Quota-aware test scheduling ও strategy selection (Challenge #3, #4) — optimization সমস্যা হিসেবে formalize করা যায়।
- F_OAS failure থেকে স্বয়ংক্রিয় **spec repair** প্রস্তাব (T4 সংযোগ)।
- Online testing-এ semantic/metamorphic oracle (P008 AGORA-র সঙ্গে সংযোগ)।

## O. Relationships to other papers
- **Supports:** P003/P004-এর দাবি যে tool-গুলোর oracle মূলত 5xx/spec-ভিত্তিক; P008 (AGORA) এই oracle-দুর্বলতা সমাধানের চেষ্টা।
- **Extends:** RESTest (ISSTA 2021), ARTE — একই group।
- **Contrast:** P006 RESTler (Microsoft-এর ভেতরের সার্ভিস), P011 (industrial RPC) — “single organization” মূল্যায়নের উদাহরণ যা P001 সমালোচনা করে।
- **T4 সংযোগ:** spec–implementation inconsistency-র ব্যাপকতা P018 (Respector) ও P017 (OOPS)-এর motivation-কে সমর্থন করে।
- **T6:** spec/document অসামঞ্জস্য (YouTube doc fix) — documentation quality-র প্রমাণ।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| গবেষণা-শিল্প gap | p.2 L121–131 |
| RQ1–RQ3 | p.3 L381–390 |
| Bot taxonomy | p.4 Table 2 L442–566 |
| ৬টি oracle | p.5 L694–711 |
| Clustering heuristics | p.5 L720–738; p.6 Table 3 L750–767 |
| ৩৮৯,২১৬ failure, ৬৩% F_OAS | p.6 L792–833 |
| ১৪৭ fault, ৮৭% প্রথম ৩ দিনে | p.6 L839–855; p.8 L1944–1952 |
| RQ3 ফল | p.8–9 L1963–2015 |
| ২৫৪ bug, ৬৫ স্বীকৃত | p.9 L2067–2078 |
| Cost | p.10 L2158–2182 |
| ৫টি challenge | p.10–11 L2136–2210 |
| Threats | p.11 L2224–2276 |

**Document integrity:** Table 1, 2, 4 কলাম-ভাঙা (মান পড়া যায় কিন্তু সারি-কলাম মিলানো কঠিন — Table 4-এর per-bot সংখ্যা PDF-এ যাচাই প্রয়োজন); Figure 1, 3, 4, 5-এর বিষয়বস্তু অনুপস্থিত (শুধু caption); section ক্রম সামান্য এলোমেলো (p.2-এর contribution list দুই কলামে ভাগ); references সম্পূর্ণ (১০৩)।
