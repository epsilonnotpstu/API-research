# P030 — A Systematic Evaluation of Static API-Misuse Detectors

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (detector survey §4-এর বিস্তারিত ও per-detector table skim; references বাদ) · **উৎস:** arXiv 1712.00242 (“Accepted for publication in IEEE TSE, 2018”), ১৯ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Sven Amann, Hoan Anh Nguyen, Sarah Nadi, Tien N. Nguyen, Mira Mezini (TU Darmstadt; Iowa State; Alberta; UT Dallas)
- **Venue:** IEEE Transactions on Software Engineering 45(12), 2019, DOI 10.1109/tse.2018.2827384
- **Cluster:** T7 (secondary: T5 — misuse-এর evolution/bug fix data; T6 — documentation অপর্যাপ্ততা)
- **ধরন:** Taxonomy + qualitative survey + automated benchmark + empirical evaluation

## B. Motivation
- API misuse (usage constraint লঙ্ঘন — যেমন `hasNext()` না দেখে `next()`) bug, crash, vulnerability-র প্রধান কারণ; documentation যথেষ্ট নয় — ConcurrentModificationException-এর StackOverflow thread-এর শীর্ষ ৫%-এর ৫৭% একই misuse-এর সমাধান চায় (p.1 L36–54)।
- দুই দশকের detector গবেষণা সত্ত্বেও misuse প্রচলিত; detector-গুলোর তুলনামূলক ক্ষমতা ও সীমা অজানা (p.1 L81–92)।

## C. Research questions
- ⚠️ আনুষ্ঠানিক RQ নেই; তিনটি experiment: **P** (per-project precision), **RUB** (crafted correct usage দিয়ে recall upper bound), **R** (বাস্তব setting-এ recall) (p.2 L130–139)।

## D. Contributions (p.2 L164–176)
- **MUC** — API misuse taxonomy (API-usage element × violation type)।
- ১২টি static detector-এর qualitative survey ও MUC-ভিত্তিক তুলনা (original লেখকদের দিয়ে যাচাই)।
- **MUBenchPipe** — প্রথম automated benchmark pipeline (public)।
- ৪টি detector-এর precision ও recall-এর প্রথম তুলনা; FP/FN-এর root-cause বিশ্লেষণ।

## E. Methodology
- **Dataset:** MUBench (পূর্ববর্তী কাজ) — ২১টি project-এর ১,২০০+ bug report ও developer survey থেকে **৯০টি Java misuse** (৭৩ বাস্তব + ১৭ survey) + API-usage directive গবেষণা থেকে ১০টি hand-crafted → **১০০** (p.2 L227–233; p.3 L447–452)।
- **MUC:** grounded theory-র রূপ — প্রথম লেখক label, সব লেখক iterative unification; element: method call, condition (null check, value/state, synchronization, context), iteration, exception handling; violation: **missing** ও **redundant** (Table 2) (p.3–4 L240–487)।
- **Survey:** ১২টি detector (JADET, GROUMINER, TIKANGA, DMMC, CAR-Miner, Alattin ইত্যাদি) — মূল evaluation-এর precision সাধারণত কম (JADET ৬.৫%, TIKANGA ৯.৯%, GROUMINER ৫.৪% ইত্যাদি), **কোনো মূল evaluation recall মাপেনি** (p.7–8 L887–1137)।
- **Empirical:** ৪টি Java detector (বাকি ৮টি Google Code Search বন্ধ, C/C++, বা Dalvik-নির্ভর); ২৯টি বাস্তব project + ২৫টি hand-crafted; প্রকাশিত optimal configuration; project version-এর ৪৭% compile হয়নি (p.2 L124–129; p.9 L1171–1177)।
- **Exp P:** প্রতি project-এ detector চালিয়ে top-২০ finding হাতে review (দুই reviewer, κ)।
- **Exp RUB:** crafted correct usage দিয়ে pattern mining → empirical বনাম conceptual (MUC-ভিত্তিক) recall upper bound।
- **Exp R:** MUBench-এর ৬৪টি + Exp P-এ পাওয়া ১৪টি misuse — বাস্তব setting-এ recall (p.10–11 L1539–1644)।

## F. Dataset
- উপরে E (Table 1)।

## G. Evaluation
- Precision, recall (upper bound ও বাস্তব), Cohen's κ, root-cause frequency; ১৫টি observation (O1–O15)।

## H. Results (author-reported)
- **O1 (Exp P):** সব detector-এর **precision <১২%** — TIKANGA ১১.৪%, JADET ১০.৩%, DMMC ৯.৯%, GROUMINER কেবল false positive; মোট মাত্র **১৪টি নিশ্চিত misuse**, সবগুলো missing value/state condition বা missing call ধরনের (O2) (p.12 L1756–1789)।
- **FP root cause (O3–O8):** অস্বাভাবিক কিন্তু বৈধ usage (৭৩, ৩৪.৩%) — “most-frequent = correct” অনুমানের ব্যর্থতা; static analysis-এর অনির্ভুলতা (৫১, ২৩.৯%); বিকল্প pattern (৪১, ১৯.২%); class-এর নিজস্ব partial implementation (১২.২%); object state-এর implicit dependency (৬.৬%); একাধিকবার call বৈধ (১.৪%) (p.13–15 L1908–2145)।
- **O9 (Exp RUB):** correct usage দিলেও **empirical recall upper bound conceptual upper bound-এর চেয়ে অনেক কম**; GROUMINER সর্বোচ্চ (graph representation কার্যকর); FN কারণ — পার্থক্য ধরার মতো বিস্তারিত না রাখা (O10), pattern-matching কঠোরতা (O11, ৩১.৩%), analysis imprecision (O12, ১৮.৮%), implementation bug (p.15–17 L2160–2462)।
- **Exp R:** বাস্তবে recall অত্যন্ত কম — JADET কেবল আগে পাওয়া ৩টি, GROUMINER শূন্য, TIKANGA ৭, **DMMC সেরা** (MUBench-এর ২টি + নিজের ৮টি + ১টি); সত্যিকারের misuse ranking-এ অনেক নিচে (DMMC-তে rank ৩০৯ ও ৬১৩) (O14) (p.17–18 L2583–2658)।
- **O15:** কম recall-এর মূল কারণ target project-এ **correct usage example-এর অভাব** → cross-project mining ও code search প্রয়োজন (p.18 L2603–2658)।
- **মূল বার্তা:** detector-কে “frequency থেকে বিচ্যুতি = misuse” অনুমান ছাড়তে হবে (probabilistic/context model), বেশি usage example ও program semantics (type hierarchy, implicit dependency) লাগবে (p.2 L146–160)।

## I. Strengths
- **Recall মাপার প্রথম কাজ** — মাঠের একটি পদ্ধতিগত অন্ধবিন্দু উন্মোচন।
- Conceptual (MUC) + empirical (৩ experiment) দ্বিস্তর মূল্যায়ন; RUB দিয়ে training-data সমস্যা আলাদা করা — চতুর experimental design।
- Original লেখকদের দিয়ে qualitative assessment যাচাই; reviewer κ রিপোর্ট।
- Root-cause-ভিত্তিক actionable observation; সম্পূর্ণ tooling ও dataset public।

## J. Explicit limitations (p.18–19 Threats)
- Construct: configuration-নির্ভর performance — প্রকাশিত optimal configuration ব্যবহার, বিকল্প পরীক্ষিত নয়; শুধু static detector — dynamic approach ভিন্নভাবে করতে পারে (executable code প্রয়োজন)।
- Java-only; MUBench-এর প্রতিনিধিত্বশীলতা; top-২০ review (ব্যয়ের কারণে)।

## K. Inferred limitations (⚠️ অনুমান)
- **ছোট ও Java/library-কেন্দ্রিক dataset:** ১০০ misuse; ৪৭% project version compile-অযোগ্য — selection bias; web/REST API misuse (wrong HTTP method, missing auth header, pagination ignore) সম্পূর্ণ বাইরে।
- **মাত্র ৪টি detector, সবই ২০০৭–২০১৩-এর pattern-mining** — ML/DL-ভিত্তিক বা specification-ভিত্তিক (CogniCrypt/CrySL) detector তুলনায় নেই; ফলাফল “pattern-mining detector”-এর সীমা, সব detector-এর নয়।
- **Precision top-২০-এ সীমিত** — পূর্ণ precision অজানা; reviewer লেখকরা নিজেরাই।
- Self-built benchmark — একই গোষ্ঠী MUBench ও MuDetect (পরবর্তী detector) তৈরি করেছে; এই paper-এ নিজস্ব detector তুলনায় নেই কিন্তু ভবিষ্যৎ কাজে স্বার্থ-সংঘাতের সম্ভাবনা।
- ২০১৮-এর পূর্বের — LLM-যুগে (P031) misuse detection-এর ধারণা পাল্টেছে; তবু benchmark (MUBench) এখনো ব্যবহৃত।

## L. Threats to validity
- উপরে J; inferable: external (Java, ছোট নমুনা), construct (top-২০ precision)।

## M. Reproducibility
- MUBenchPipe ও dataset public [24], artifact web page [10] — **উচ্চ** (পুরোনো Java version/dependency পুনর্গঠন ঝুঁকি)।

## N. Opportunities (hypothesis)
- **Web/REST API misuse benchmark (MUBench-এর REST সমতুল্য):** client-side REST misuse (missing pagination, retry/idempotency ভুল, auth token handling, deprecated endpoint — P024/P022) বাস্তব bug-fix commit থেকে mining; P021-এর UC-1 ও P029-এর benchmark gap পূরণ।
- **LLM-based misuse detector বনাম pattern-mining:** MUBench-এ LLM-এর precision/recall — “frequency assumption”-এর বিকল্প হিসেবে LLM-এর API knowledge (P031 আংশিক উত্তর)।
- **Cross-project/code-search mining** (O15) + documentation/spec থেকে constraint (P016 IDL, P028) — correct usage example-এর অভাব পূরণ।
- **Ranking উন্নয়ন** (O14) — learning-to-rank finding।
- **Spec-driven misuse detection for web API clients:** OpenAPI + IDL দিয়ে client code static check (T4 → T7)।

## O. Relationships
- **Cited/used by P021** (Table 6-এ MUBench state-of-the-art benchmark) ও **P029** (generic misuse detector — security-নির্দিষ্টের বাইরে)।
- **Foundation for P031** (LLM API misuse taxonomy-র পূর্বসূরি ধারণা)।
- **Relates to P028** — documentation অপর্যাপ্ততা misuse-এর কারণ।
- **Contrasts with T1 oracle problem** — উভয়ই “সঠিক আচরণ কী” জানার সমস্যা (P008 invariant mining-ও frequency-ভিত্তিক — একই FP ঝুঁকি)।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract | p.1 L15–25 |
| Motivation, SO ৫৭% | p.1 L36–54 |
| Contributions | p.2 L164–176 |
| Experiments P/RUB/R সারাংশ | p.2 L124–160 |
| MUBench (৯০ → ১০০) | p.2–3 L227–233, L447–452 |
| MUC taxonomy (Table 2) | p.3–4 L240–487 |
| ১২ detector survey, মূল precision | p.7–8 L887–1137 |
| Compile সমস্যা (৪৭%) | p.9 L1171–1177 |
| Exp P design | p.10 L1188–1505 |
| Exp RUB design | p.10–11 L1539–1601 |
| Exp R design | p.11 L1621–1644 |
| O1–O2 precision (<১২%) | p.12 L1756–1789 |
| O3–O8 FP root cause | p.13–15 L1908–2145 |
| O9–O12 RUB | p.15–17 L2160–2462 |
| O13–O15 R | p.17–18 L2583–2658 |
| Threats | p.18–19 L2787– |
| Conclusions | p.19 L2877–2902 |

**Document integrity:** দুই-কলামের reading order মিশ্রিত (MUC section-এ দুটি কলামের লাইন জোড়া লেগেছে); Table 1–9 column-split — per-detector recall সংখ্যা text থেকে আংশিক; Fig.1–6 অনুপস্থিত; small-caps tool নাম letter-spaced (M U B ENCH)।
