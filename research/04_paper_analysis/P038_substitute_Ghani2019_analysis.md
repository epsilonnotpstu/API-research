# P038 — ⚠️ IDENTITY MISMATCH: প্রদত্ত PDF নির্বাচিত paper নয়

> **গুরুত্বপূর্ণ:** `final_papers.csv`-এ P038 = *Microservices testing: A systematic literature review* — Francisco Ponce, Roberto Verdecchia, Breno Miranda, Jacopo Soldani, **Information and Software Technology 2025**, DOI 10.1016/j.infsof.2025.107870 (৭৪টি study, SWEBOK শ্রেণিবিন্যাস)।
> কিন্তু supervisor-প্রদত্ত `paper/P038.pdf` (sha256 9a04aa1e…6184, ১৬ পৃষ্ঠা) আসলে **ভিন্ন paper**: *Microservice Testing Approaches: A Systematic Literature Review* — Israr Ghani, Wan M.N. Wan-Kadir, Ahmad Mustafa, Muhammad Imran …, **International Journal of Integrated Engineering 11(8), 2019, pp. 65–80**, DOI 10.30880/ijie.2019.11.08.008 (p.1 L5–31)।
> যাচাই: প্রথম লেখকের surname “Ponce” Markdown-এর প্রথম ৬,০০০ অক্ষরে নেই; বাকি ৩৭টি paper এই পরীক্ষায় মিলেছে।
> **সিদ্ধান্ত:** নিচের বিশ্লেষণ কেবল প্রদত্ত document-এর (Ghani et al. 2019) — **substitute হিসেবে, Ponce et al. 2025-এর প্রমাণ হিসেবে নয়।** Ponce 2025-এর কোনো দাবি এখানে বা synthesis-এ ব্যবহার করা হয়নি (full text পড়া হয়নি)। সঠিক PDF পাওয়া গেলে P038 পুনর্বিশ্লেষণ প্রয়োজন।

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references বাদ) · **উৎস:** supervisor-provided copy, ১৬ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity (প্রদত্ত document)
- **Authors:** Israr Ghani, Wan M.N. Wan-Kadir (corresponding), Ahmad Mustafa, Muhammad Imran ও অন্যান্য (Universiti Teknologi Malaysia; Army Public College of Management and Science, Rawalpindi) (p.1 L20–28)
- **Venue:** International Journal of Integrated Engineering (Penerbit UTHM), Vol. 11 No. 8 (2019) 65–80; DOI 10.30880/ijie.2019.11.08.008
- **Cluster:** T9 (secondary: T1 — API/contract/integration testing level)
- **ধরন:** Systematic literature review (১৫টি primary study)

## B. Motivation
- Microservice testing কঠিন; security, performance, traceability, compatibility, complexity, effectiveness, scalability — এই সাতটি quality concern-এ testing approach কেমন, তা পূর্ববর্তী গবেষণা address করেনি বলে দাবি (p.1 L43–47; p.2 L79–83)।
- বিদ্যমান tool/model/framework-এর overhead ও platform-portability সমস্যা; NFR testing অবহেলিত (p.2 L94–109)।

## C. Research questions (Table 1, p.2 L116–134)
- **RQ1:** Microservice testing-এ issue কী? (gap চিহ্নিত করা)
- **RQ2:** Testing-এর quality-related aspect ও concern কী?
- **RQ3:** Issue সমাধানে বিদ্যমান solution কী?

## D. Contributions (p.2 L85–91)
- ১৫টি primary study-র বিশ্লেষণ — মূল issue, quality attribute ও বিদ্যমান solution/gap।
- সাতটি parameter-এর বিপরীতে ✓/x matrix (Table 6) এবং primary study-র “quality” তুলনা (Table 8)।
- Testing level-এর বর্ণনা (unit, component, integration, contract, E2E)।

## E. Methodology
- Petersen et al.-এর guideline অনুসরণের দাবি (p.2 L112–113); ৭টি database (ACM, IEEE Xplore, ISI WoS, Springer, ScienceDirect, Wiley, Scopus) + Google Scholar manual search (p.3 L193–223)।
- Search string title/abstract/keyword-এ (Table 4, p.4 L253–293)।
- Selection: **৪৬৫ → ১৭৩ (title) → ৪৯ (abstract + duplicate removal) → ১৫ (full text)** (p.3 L232–234)।
- Data extraction: source, title, method, pros/cons, supportive facts ইত্যাদি (p.4–5 L338–367); ✓ (“Existing”) / x (“Lacking”) coding (p.8 L578–579)।

## F. Dataset
- ১৫টি primary study (২০১৩–২০১৮; conference, journal, book chapter) (p.4 L246–248)। Table 5/6/7/8-এর সারি column-split — পূর্ণ তালিকা Markdown থেকে নির্ভরযোগ্যভাবে পুনর্গঠনযোগ্য নয়।

## G. Evaluation
- বর্ণনামূলক count ও শতাংশ; কোনো formal quality-assessment score বা inter-rater agreement রিপোর্ট নেই।

## H. Results (author-reported)
- **Parameter coverage (Fig 4):** security-তে ৭টি, performance-এ ৯টি, complexity-তে ১০টি study (১৫-এর মধ্যে); traceability, compatibility, effectiveness, scalability-তে আরও মনোযোগ দরকার (p.9 L858–864)।
- **Testing level (Fig 7):** unit testing ≈৭৫%, integration ১০%, component/contract/E2E প্রতিটি ৫% (p.11 L991–997)।
- **Study quality (Table 8/Fig 8):** ৬টি inclusive related work; ১০টি approach প্রস্তাব করে; ১০টি experiment চালায়, ৭টি outcome উপস্থাপন করে; **মাত্র ১টি পূর্ববর্তী study-র সাথে তুলনা করে**; ৭টি improvement দাবি করে; ১২টি knowledge contribution করে (p.12 L1081–1089)।
- **Challenge (RQ1):** tester–consumer ব্যবধান; **API-র সংখ্যা বৃদ্ধি** (প্রতিটি service-এর আলাদা API); service upgrade/maintenance — সব user upgrade করে না (p.11–12 L1022–1036)।
- **Future need:** test frequency নির্ধারণ; stakeholder-ভিত্তিক (Developer, Provider, Integrator, Third Party, End User) testing level; integrator/third-party testing approach (p.12 L1040–1047)।
- **উপসংহার:** “৭০% microservice testing approach-based”; interoperability, auditability, reliability, integrity, inconsistency ভবিষ্যৎ কাজ (p.14 L1325–1336)।

## I. Strengths
- Microservice testing-এর প্রাথমিক (২০১৯) সারসংক্ষেপ; testing level ও NFR concern-এর তালিকা।
- Primary study-গুলোর **তুলনা ও evaluation-এর অভাব** স্পষ্টভাবে দেখায় (১/১৫ পূর্ববর্তী কাজের সাথে তুলনা) — benchmark-gap-এর পুরনো প্রমাণ।
- **Consumer-driven contract test** ও API সংখ্যা বৃদ্ধিকে challenge হিসেবে চিহ্নিত — T5 (breaking change)-এর সাথে সংযোগ।

## J. Explicit limitations (p.14 L1303–1317; p.14 L1333–1336)
- Primary study selection ও analysis-এ bias-এর সম্ভাবনা; gray literature-এর কারণে study বাদ পড়তে পারে।
- আরও study ও সব database কভার করে উন্নত করা যায়; interoperability, auditability, integrity, inconsistency বাকি।

## K. Inferred limitations (⚠️ অনুমান)
- **Identity:** এটি নির্বাচিত P038 নয় — corpus-এর T9 coverage-এ ২০২৫-এর ৭৪-study SLR-এর বদলে ২০১৯-এর ১৫-study review; recency ও breadth উভয়ই কম।
- **অভ্যন্তরীণ অসঙ্গতি:** inclusion criteria ২০১০–২০১৮ (Table 2, p.3 L176) বনাম search ২০১৩–২০১৮ (p.3 L222); “Available online 15 Sep 2019” কিন্তু “Accepted 27 Sep 2019” (p.1 L32); “৭০% approach-based” (উপসংহার) ফলাফল অংশে প্রতিষ্ঠিত নয়।
- **Methodological rigor দুর্বল:** কোনো quality-assessment checklist, দ্বিতীয় reviewer বা agreement নেই; search string অস্পষ্ট ও অসমঞ্জস (Table 4); Petersen (mapping study guideline) ও Cochrane handbook-এর দাবি কিন্তু প্রয়োগের বিবরণ নেই।
- **অসমর্থিত ব্যাখ্যা:** unit testing ৭৫% “কারণ tester-রা data sensitivity-র জন্য manual testing পছন্দ করেন” (p.11 L993–994) — প্রমাণ উপস্থাপিত হয়নি; “Relatively easy … but difficult to use” স্ববিরোধী (p.11 L1001)।
- **সাতটি parameter-এর সংজ্ঞা নেই** (যেমন “effectiveness”, “complexity” testing-এর quality attribute হিসেবে কীভাবে কোড করা হয়েছে) — ✓/x coding-এর construct validity অস্পষ্ট।
- ১৫টি study-র ক্ষুদ্র নমুনায় শতাংশ (৫%, ১০%) — প্রতি ৫% ≈ ০.৭৫ study, অর্থাৎ শতাংশ-ভিত্তিক পরিসংখ্যান অর্থবহ নয়।
- API-নির্দিষ্ট testing (OpenAPI-ভিত্তিক REST fuzzing, contract test tooling) প্রায় অনুপস্থিত।

## L. Threats to validity
- উপরে J; inferable: construct (parameter সংজ্ঞা), internal (একক coder), external (২০১৮ পর্যন্ত, ১৫ study), reliability (অস্পষ্ট search string)।

## M. Reproducibility
- **নিম্ন:** search string ও selection-এর বিবরণ অসম্পূর্ণ; extraction form/data প্রকাশিত নয়; table column-split।

## N. Opportunities (hypothesis)
- **হালনাগাদ, API-কেন্দ্রিক microservice testing mapping:** ২০১৯-এর পর REST fuzzer (P001–P008), contract testing ও observability-ভিত্তিক oracle (P037) একত্রে — সঠিক P038 (Ponce 2025) এই gap আংশিক পূরণ করতে পারে; পূর্ণ পাঠের পর যাচাই প্রয়োজন।
- **Consumer-driven contract test + breaking change detection** (T5: P020, P023, P025) — microservice API evolution-এ স্বয়ংক্রিয় contract synthesis।
- **Multi-service (system-level) REST testing benchmark** — ১/১৫ study তুলনা করেছে; P011 (EvoMaster microservice) ও P037 (LO2) এর সাথে সমন্বিত benchmark।

## O. Relationships
- **T9 cluster:** P037 (LO2 observability dataset), P011 (microservice API testing), P020 (industrial microservice API evolution)।
- **T1-এর সাথে:** integration/contract testing level — REST API testing tool-গুলো এখানে প্রায় অনুপস্থিত।
- **T5-এর সাথে:** consumer-driven contract test-এর breaking-change উদ্দেশ্য।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Title, authors, venue, DOI | p.1 L5–31 |
| Abstract — সাত parameter | p.1 L33–47 |
| ১৫ study, ৪৬৫ initial | p.2 L85–91 |
| Motivation | p.2 L94–113 |
| RQ (Table 1) | p.2 L116–134 |
| Inclusion criteria ২০১০–২০১৮ | p.3 L159–190 |
| Database, search ২০১৩–২০১৮ | p.3 L193–226 |
| Selection ৪৬৫→১৭৩→৪৯→১৫ | p.3 L232–234 |
| Data extraction | p.4–5 L338–367 |
| Parameter coverage (Fig 4) | p.9 L858–868 |
| Testing level | p.10–11 L915–983 |
| Unit ৭৫% ইত্যাদি (Fig 7) | p.11 L986–997 |
| Challenges | p.11–12 L1017–1050 |
| Study quality (Table 8) | p.12 L1062–1105 |
| Implications | p.14 L1290–1300 |
| Threats | p.14 L1303–1317 |
| Conclusion, ৭০% | p.14 L1319–1336 |

**Document integrity:** **IDENTITY MISMATCH** (নির্বাচিত paper নয়)। Body সম্পূর্ণ; Table 2–8 column-split (Table 5–8-এর সারি পুনর্গঠন অনির্ভরযোগ্য); Fig 1, 4–8 অনুপস্থিত; Markdown-এ references section একাধিকবার (L372, L875, L1338)।
