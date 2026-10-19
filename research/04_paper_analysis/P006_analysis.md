# P006 — RESTler: Stateful REST API Fuzzing

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references ৪৩) · **উৎস:** Microsoft Research-hosted PDF (প্রথম পৃষ্ঠার শিরোনাম ICSE 2019 version-এর সঙ্গে মেলে; ১১ পৃষ্ঠা) · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Vaggelis Atlidakis (Columbia; কাজ মূলত MSR-এ), Patrice Godefroid, Marina Polishchuk (Microsoft Research)
- **Venue:** ICSE 2019, DOI 10.1109/icse.2019.00083
- **Cluster:** T1 (foundational)
- **ধরন:** Original technique + case studies

## B. Motivation
- Cloud service REST API-দিয়ে প্রবেশযোগ্য; বিদ্যমান tool মূলত live traffic capture/replay fuzzer (Burp, AppSpider প্রভৃতি) — কার্যকারিতা অজানা (p.1 L44–54)।
- কোনো tool spec থেকে **stateful** (একাধিক request-এর ক্রম) test তৈরি করে না।

## C. Research questions (p.4 L469–475)
- Q1: dependency inference ও dynamic feedback — দুটোই কি দরকার?
- Q2: sequence length বাড়লে কি গভীর service logic অনুশীলিত হয়?
- Q3: তিনটি search strategy (BFS, BFS-Fast, RandomWalk) তুলনায় কেমন?

## D. Contributions (p.1 L91–106)
- “প্রথম” স্বয়ংক্রিয় stateful REST fuzzer; কৌশল-আবশ্যকতার প্রমাণ; তিনটি search strategy তুলনা; GitLab case study; Azure/Office365 অভিজ্ঞতা।

## E. Methodology
- **Spec processing (p.2):** Swagger থেকে স্বয়ংক্রিয়ভাবে Python test-generation grammar; `restler_static` ও `restler_fuzzable` (dictionary থেকে value); response parser dynamic object (যেমন id) সংগ্রহ করে।
- **Algorithm (Figure 3, p.3):** length n পর্যন্ত sequence; EXTEND — যে request-এর consumed object আগের sequence produce করেছে শুধু সেগুলো যোগ (producer–consumer dependency); RENDER — dictionary-র সব combination concretize, execute, **শুধু 2xx sequence রাখা** (dynamic feedback pruning)। ডিফল্ট BFS।
- **BFS-Fast:** প্রতিটি request সর্বোচ্চ একটি sequence-এ যোগ — পূর্ণ grammar coverage, কম sequence; **RandomWalk:** একটি random extension, ব্যর্থ হলে restart (p.3–4 L398–424)।
- **Implementation:** ৩,১৫১ LOC Python; garbage collector; **bug = 500 status code** (p.4 L426–453)।
- **Production সংযোজন (p.9):** GC (resource quota), auth token refresh hook, annotation ও resource-specific mutation (অসম্পূর্ণ spec/non-REST naming)।

## F. Dataset ও setup
- Q1: ১৮৯ LOC Python Flask **blog-posts service** (৫টি request type, **planted bug** — checksum মিললে uncaught exception) (p.4 L484–502)।
- Q2/Q3: **GitLab** (৩৭৬K+ LOC Ruby), ছয়টি API group (Commits ১১, Branches ৭, Issues ২২, Repos ১০, Groups ৫০, Projects ৪৮ request type); প্রতি পরীক্ষা ৫ ঘণ্টা, ≤১,০০০ combination/request; ক্ষুদ্র dictionary (string: “sampleString”, ""; integer: 0, 1; bool) (p.4–5 L503–523)।
- Azure VM: ৮ core, 56GB (p.5 L524–526)।
- Production: ৩টি Azure + ১টি Office365 service (বিস্তারিত গোপন) (p.9)।

## G. Evaluation
- Code coverage (Ruby TracePoint, boot-coverage ১৬,৮৩৬ লাইন বাদ), HTTP status code distribution, sequence/test/dynamic object সংখ্যা, bug bucket (suffix-ভিত্তিক)।
- ⚠️ **বাইরের কোনো tool-এর সঙ্গে তুলনা নেই** (শুধু নিজের ablation ও strategy); একক রান (repetition বা statistics নেই)।

## H. Results (author-reported)
- **Q1 (blog service, Figure 4):** dependency ছাড়া coverage ≤১৩০ লাইন, planted bug অধরা; feedback ছাড়া ৪,৬০০+ test, ১,৭৫০s, ~১৫০ লাইন; দুটো সহ **<৮০০ test, ১৭৯s-এ একই ~১৫০ লাইন** এবং bug পাওয়া; 40X অনুপাত ৬০% → ২০% (p.5 L552–605)।
- **Q2 (Table I):** দীর্ঘ sequence → বেশি coverage (যেমন Commits ৫৯৮→১,১০৮→১,১৯৬ লাইন, দৈর্ঘ্য ১–৩); BFS-এ search space দ্রুত বিস্ফোরিত (Commits-এ seqSet ২০,৬৭৯; brute force-এ ১৬৪M+) (p.6–7 L984–1250)।
- **Q3 (Table II, III):** BFS ছোট API-তে বেশি coverage; BFS-Fast/RandomWalk বড় API-তে গভীরে যায়; **RandomWalk সবচেয়ে বেশি bug (২১) যদিও প্রায়ই কম coverage**; BFS ১৬, BFS-Fast ১৩; মোট ২২টি unique bug বিভিন্ন strategy-তে, ৯টি সবার মধ্যে সাধারণ (p.8 L1360–1428)।
- **মোট:** GitLab-এ ২৮টি নতুন bug (confirmed ও fixed); Azure/Office365-এ প্রতিটিতে কয়েকটি (p.8 L1430–1436; p.9)।
- Bug pattern: (১) গভীর valid state-এ পৌঁছানো + (২) অপ্রত্যাশিত মান বা কাজ (যেমন deleted project-এর branch edit — foreign key violation) (p.9 L1468–1475)।

## I. Strengths
- Stateful dependency + feedback pruning ধারণা — পরবর্তী প্রায় সব tool-এর ভিত্তি (P002-এর হিসাবে RESTler ৮টি paper-এ ব্যবহৃত)।
- Production cloud-এ বাস্তব চ্যালেঞ্জ (quota, token, non-REST naming) এবং সমাধান — শিল্প-প্রাসঙ্গিক।
- Bug confirmed ও fixed।

## J. Explicit limitations (p.4 L454–465; p.10)
- Server-side redirect (301/303/307) সমর্থন নেই।
- **Oracle শুধু unexpected status code** — information exposure-এর মতো দুর্বলতা ধরা পড়ে না।
- Generalization অজানা; অন্য service ও property পরীক্ষা দরকার; REST API-র পেছনে কী security vulnerability থাকে “still unclear” (p.10 L1648–1661)।
- RandomWalk-এর ফল দীর্ঘ session বা অন্য API-তে সাধারণীকরণ অনিশ্চিত (p.8 L1422–1423)।

## K. Inferred limitations (⚠️ অনুমান)
- **Q1-এর প্রমাণ দুর্বল ভিত্তিতে:** ১৮৯ লাইনের খেলনা service, লেখকদের নিজের রোপিত bug — কৌশলের আবশ্যকতা দেখায়, কার্যকারিতা নয়।
- **বাইরের baseline ও repetition নেই**; RandomWalk random — একক রানে strategy তুলনা অস্থির।
- **ক্ষুদ্র dictionary** (২টি string, ২টি integer) — input-space অনুসন্ধান সীমিত; পরবর্তী গবেষণা (P004) এটিকে RESTler-এর দুর্বলতা হিসেবে চিহ্নিত করেছে।
- Production ফল গোপন — যাচাই অযোগ্য।
- পঠিত কপি MSR-hosted — ICSE published version-এর সঙ্গে পাঠ্য-সমতা পুরোপুরি যাচাই হয়নি।

## L. Threats to validity
- Paper-এ পৃথক threats section নেই। Inferable: construct (500 = bug), external (একটি open-source service), internal (single run)।

## M. Reproducibility
- RESTler পরে open-source হয় (GitHub, ২০২০ — P003 অনুযায়ী); paper-এর পরীক্ষার script/data প্রকাশের উল্লেখ নেই। GitLab version উল্লেখ নেই।

## N. Opportunities (hypothesis)
- Status-code-এর বাইরে **semantic/security oracle** (লেখকরা নিজেরাই পরবর্তীতে P025-এর সহচর security checkers প্রস্তাব করেছেন)।
- **Spec ছাড়া**: runtime traffic-এ ML বা code-এ static analysis দিয়ে spec inference (p.10 L1613–1616) — T4-এর পূর্বাভাস।
- Back-end log/assertion ব্যবহার করে oracle শক্তিশালীকরণ (p.10 L1628–1632)।
- Coverage বনাম bug-finding-এর strategy-নির্ভর সম্পর্ক অধ্যয়ন।

## O. Relationships
- **Foundation for:** P003, P004 (baseline), P025 (differential regression RESTler দিয়ে input তৈরি), P015 (access-policy oracle-এর পূর্বসূরি ধারণা)।
- **Evidence tension:** P004 coverage–error correlation ~০.৭৯ দেখায়; P006-এ RandomWalk কম coverage-এ বেশি bug — coverage-কে একমাত্র নির্দেশক ধরা নিয়ে প্রশ্ন।
- **T4 পূর্বাভাস:** অসম্পূর্ণ spec ও annotation-এর প্রয়োজন — P016–P019-এর সমস্যা।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Motivation | p.1 L44–54 |
| Contributions | p.1 L91–106 |
| Grammar generation | p.2 L162–221 |
| Algorithm | p.3 Figure 3 L244–335; L337–424 |
| Implementation, bug=500 | p.4 L426–453 |
| Limitations | p.4 L454–465 |
| RQs | p.4 L469–475 |
| Blog service + planted bug | p.4 L484–502 |
| GitLab setup, dictionaries | p.4–5 L503–526 |
| Q1 ফল | p.5 L527–605 |
| Q2 ফল | p.6–7 Table I L963–1250 |
| Q3 ফল | p.7–8 Table II–III L1224–1428 |
| GitLab ২৮টি bug | p.8–9 L1430–1475 |
| Production challenges | p.9 L1476–1544 |
| Future directions | p.10 L1606–1661 |

**Document integrity:** Figure 4 (coverage/status chart) সংখ্যা ছড়ানো — পাঠযোগ্য নয়; Table I–III কলাম-ভাঙা কিন্তু total সারি পাঠযোগ্য; algorithm (Figure 3) পাঠযোগ্য; threats section নেই (মূল paper-এর বৈশিষ্ট্য, conversion ত্রুটি নয়)।
