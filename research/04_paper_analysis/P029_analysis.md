# P029 — Detecting Misuse of Security APIs: A Systematic Review

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (security API বর্ণনা §4.1 ও misuse তালিকা §5 skim; references বাদ) · **উৎস:** ACM CSUR 2025 author version (arXiv 2306.08869), ৩৭ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Zahra Mousavi, Chadni Islam, Muhammad Ali Babar, Alsharif Abuadbba, Kristen Moore (CREST/Adelaide University; Edith Cowan; CSIRO Data61)
- **Venue:** ACM Computing Surveys, 2025, DOI 10.1145/3735968
- **Cluster:** T7 (secondary: T3 — security; OAuth/Spring Security authorization)
- **ধরন:** Systematic literature review (Kitchenham)

## B. Motivation
- Security API (crypto, SSL/TLS, OAuth) misuse গুরুতর vulnerability সৃষ্টি করে — Krüger et al.: ১০,০০০ Android app-এর ~৯৫%-এ অন্তত একটি crypto misuse; ২,০০০+ Java project-এর ৭২%-এ (p.2 L79–81)।
- কারণ: জটিল API design, দুর্বল documentation (OAuth documentation-এর code example-এই misuse), অনির্ভরযোগ্য forum, প্রশিক্ষণের অভাব (p.3 L148–157)।
- সাহিত্য বিচ্ছিন্ন — সমন্বিত সংশ্লেষণ নেই (p.2 L82–87)।

## C. Research questions (p.2 L90–93)
- RQ1: কোন security API অধ্যয়িত? RQ2: কোন misuse? RQ3: কোন detection কৌশল? RQ4: কোন evaluation কৌশল?

## D. Contributions (p.2 L95–99)
- ৬৯টি গবেষণার SLR; security API ও misuse-এর গভীর আলোচনা; detection approach-এর taxonomy; benchmark ও metric বিশ্লেষণ; ১৪টি open issue।

## E. Methodology
- **উৎস:** Scopus (প্রাথমিক), IEEE Xplore, ACM DL; চার category-র keyword (security, API, misuse, detection + synonym) AND (p.4 L181–206)।
- **Inclusion:** security API misuse detection (automated/manual/tool); **CORE বা Scimago-ranked venue**; English; **Exclusion:** security API-র অভ্যন্তরীণ vulnerability, **generic API misuse**, <৬ পৃষ্ঠা, book/thesis (Table 2, p.5 L235–245)।
- **Funnel (Nov 2022, কোনো বছর-সীমা নেই):** ১,৭১৩ → unique ১,১৮৬ (Scopus ৮৫৬ + IEEE ২৭১ + ACM ৫৯) → title/abstract ৬৮ → full text **২৭** → forward/backward snowballing → **৬৯** (p.5 L251–262)।
- Data extraction form (১৪–১৮ data item), ১২টি paper-এ pilot; thematic analysis; পাক্ষিক মিটিংয়ে মতভেদ নিষ্পত্তি (p.5–6 L271–295)।

## F. Dataset
- ৬৯টি primary study (২০১২–২০২২); ৫৮টি (৮৪%) conference; CCS ৯, S&P ৫ (p.6 L300–309)।

## G. Evaluation
- Descriptive statistics + thematic synthesis।

## H. Results (author-reported)
- **RQ1:** ৬টি API category — **crypto primitives (৩১ study)**, **SSL/TLS (১৪)**, উভয় ১২টি, OAuth ৯, Fingerprint/Spring Security/SafetyNet Attestation একটি করে; Java সর্বাধিক (crypto-র ৪৩-এর ৩৬টি JCA), C/C++ ৮, Python ৩, JavaScript ১, Go ১ (p.6–8 L320–487; Table 3)।
- **RQ2:** **৩০টি স্বতন্ত্র misuse** (M1–M30); সর্বাধিক রিপোর্টকৃত — insecure crypto algorithm, improper certificate validation (SSL), OAuth state parameter-এর অভাব/অপব্যবহার; মূলত Android app-এ (p.12 L715–724; p.34 L2136–2138)।
- **RQ3:** taxonomy — input (code, binary, log, network trace), heuristic- বা ML-based algorithm, output; **heuristic: static ৪২, dynamic ৯, hybrid ১৩; ML মাত্র ৩টি** (SO snippet-এ trained ইত্যাদি); hybrid-এ static candidate → dynamic MitM যাচাই (p.19–27 L1222–1674; p.34 L2140–2143)।
- **RQ4:** ১০/১১টি metric (accuracy ও efficiency গোষ্ঠী); **৯টি public benchmark, যার মাত্র ৫টি security API misuse-এর জন্য তৈরি — সবই Java crypto/SSL**; CryptoAPI-Bench (synthetic, static-কেন্দ্রিক), CryptoAPI-Bench* (dynamic), ApacheCryptoAPI-Bench (১০টি Apache project, বাস্তব); ৫টি study static tool-গুলোর তুলনামূলক মূল্যায়ন (p.27–29 L1678–1860)।
- **Open issues (১৪টি):** coverage — security context বৈচিত্র্যের অভাব, ML-based security API অনধ্যয়িত, **>৭০% study Java**, cross-language tool নেই, benchmark সীমিত (৩/৫ synthetic, static-কেন্দ্রিক, version/temporal drift); technical — **>৯৫% heuristic**, **LLM-এর প্রয়োগ অনধ্যয়িত**, **API evolution-এ model অভিযোজন** (compile error দেয় না এমন security evolution), standardized evaluation (spatial/temporal bias); human — developer প্রত্যাশা পূরণ হয় না (রিপোর্টকৃত misuse-এর ৭১%/৫২%/২০% স্বীকৃত; অ-সংবেদনশীল context-এ misuse অবজ্ঞা; exploit প্রদর্শন ছাড়া প্রত্যাখ্যান), মাত্র ৩টি study usability মূল্যায়ন করেছে, repair সমর্থনের অভাব (মাত্র ৪টি customized fix), API usability ও documentation দুর্বল, প্রশিক্ষণের অভাব (p.29–33 L1880–2075)।

## I. Strengths
- সংকীর্ণ ও স্পষ্ট scope (security API misuse) — গভীর taxonomy (API, misuse, technique, evaluation)।
- **Human-centric open issue** (developer feedback, false-positive context, repair) — tool গবেষণার জন্য বাস্তব অগ্রাধিকার।
- Benchmark-এর সমালোচনামূলক বিশ্লেষণ (synthetic বনাম বাস্তব, static বনাম dynamic)।
- Online appendix-এ study তালিকা ও extraction form।

## J. Explicit limitations (p.33 §9)
- প্রাসঙ্গিক study বাদ পড়ার ঝুঁকি — Scopus + ২টি DL + pilot search + snowballing দিয়ে প্রশমন।
- Selection-এ subjective bias — স্পষ্ট criteria ও সব লেখকের আলোচনা।
- Extraction/synthesis-এ মানব ত্রুটি — DEF ও পাক্ষিক মিটিং।

## K. Inferred limitations (⚠️ অনুমান)
- **Search cut-off Nov 2022, প্রকাশ ২০২৫:** আড়াই বছরের ফাঁক — LLM-ভিত্তিক misuse detection/generation (২০২৩–২০২৫-এর বিস্ফোরণ; P031) সম্পূর্ণ অনুপস্থিত, অথচ “LLM under-explored” বলে open issue — সংজ্ঞাগতভাবে পুরোনো।
- **Snowballing-নির্ভরতা:** database search থেকে মাত্র ২৭টি, snowballing থেকে ৪২টি — search string-এর recall দুর্বল ছিল বা snowballing-এর inclusion কম কঠোর; snowball stage-এর criteria প্রয়োগ বিস্তারিত নয়।
- **সংখ্যার অসামঞ্জস্য:** abstract “১০ performance measures”, conclusion “১১ metrics”; heuristic “৬৬ study” (L1361) বনাম ৪২+৯+১৩ = ৬৪।
- **Venue-ranking filter** (CORE/Scimago) — quality proxy, কিন্তু arXiv/workshop-এর নতুন কাজ বাদ; প্রকৃত study-স্তরের quality appraisal নেই।
- **Inter-rater agreement সংখ্যা নেই** — consensus মিটিং বর্ণিত কিন্তু κ নেই।
- **Web/REST API security misuse** (API key handling, JWT validation, CORS, rate-limit) প্রায় অনুপস্থিত — scope library-স্তরের security API; OAuth ছাড়া web API-স্তর কম (T3-এর সঙ্গে gap)।
- “Generic API misuse” বাদ — P030 (MUBench) ধরনের সাধারণ detector-এর সঙ্গে সংযোগ আলাদা থাকে।

## L. Threats to validity
- উপরে J; inferable: temporal staleness, snowball bias, agreement-এর অভাব।

## M. Reproducibility
- Online appendix-এ ৬৯টি study ও DEF [26] — **উচ্চ** (repository স্থায়িত্ব যাচাই প্রয়োজন)।

## N. Opportunities (hypothesis)
- **LLM × security API misuse (২০২৩–২০২৬) rapid review/empirical study:** LLM-generated code-এ crypto/OAuth misuse হার, LLM-ভিত্তিক detector বনাম CogniCrypt/CryptoGuard (P031-এর পদ্ধতি security API-তে) — এই SLR-এর open issue ৮.২.২ সরাসরি।
- **Web API security misuse taxonomy:** REST client-side misuse (JWT verification বাদ, token logging, TLS verification off, API key hard-coding — P013 WARDroid-এর hard-coded key) — T3↔T7 সেতু।
- **Context-aware triage:** security-relevant বনাম test/archived code পার্থক্য (developer প্রত্যাখ্যানের প্রধান কারণ) + exploit demonstration — false-positive হ্রাস।
- **Evolution-aware misuse detection:** deprecated insecure algorithm (P024-এর deprecated API ধারণা), NIST blacklist আপডেট — temporal benchmark versioning।
- **বাস্তব, multi-language, dynamic-সমর্থিত benchmark** (Python/Go/JS crypto, OAuth flow)।
- **Repair:** LLM দিয়ে customized fix + verification।

## O. Relationships
- **Complements P030** (generic static API-misuse detector evaluation — MUBench) — এটি security-নির্দিষ্ট।
- **Feeds P031** (LLM API misuse) — P031 ঠিক এই SLR-এর LLM gap-এর সমান্তরাল।
- **Links T3** (OAuth/authorization; P013-এর client-side API key ও validation সমস্যা)।
- **Links T6/P028** — দুর্বল documentation misuse-এর কারণ।
- **Links T5/P024** — API evolution ও misuse detector অভিযোজন।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract (৬৯, ৬ API, ৩০ misuse, ১০ measure, ৯ benchmark) | p.1 L17–27 |
| ৯৫%/৭২% misuse prevalence | p.2 L79–81 |
| RQ1–RQ4, contributions | p.2 L88–99 |
| Misuse-এর কারণ | p.3 L148–157 |
| Search method ও string | p.4 L179–206 |
| Inclusion/exclusion (Table 2) | p.5 L235–245 |
| Funnel ১,৭১৩ → ২৭ → ৬৯ | p.5 L251–262 |
| Data extraction, thematic analysis | p.5–6 L271–295 |
| Venue বণ্টন | p.6 L300–309 |
| RQ1 API category (Table 3) | p.6–10 L314–590 |
| RQ2 ৩০ misuse | p.12–18 L715– |
| RQ3 taxonomy | p.19–27 L1222–1674 |
| RQ4 metrics, benchmark (Table 7) | p.27–29 L1678–1860 |
| ১৪ open issue | p.29–33 L1880–2075 |
| Threats | p.33 L2087–2108 |
| Conclusion | p.33–34 L2111–2147 |

**Document integrity:** Body সম্পূর্ণ; Table 3, 5–7 column-split (study-ID তালিকা পাঠযোগ্য কিন্তু কাঠামো হারিয়েছে); Fig.1–11 অনুপস্থিত; misuse M1–M30-এর পূর্ণ তালিকা এই বিশ্লেষণে আংশিকভাবে পড়া হয়েছে।
