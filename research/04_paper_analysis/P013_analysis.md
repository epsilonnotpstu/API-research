# P013 — Mobile Application Web API Reconnaissance: Web-to-Mobile Inconsistencies & Vulnerabilities (WARDroid)

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references বাদ) · **উৎস:** IEEE S&P 2018 author version, ১৪ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Abner Mendoza, Guofei Gu (Texas A&M University)
- **Venue:** IEEE Symposium on Security and Privacy 2018, DOI 10.1109/sp.2018.00039
- **Cluster:** T3 (secondary: T4 — client code থেকে API template/constraint অনুমান)
- **ধরন:** Static analysis + black-box server testing + বৃহৎ পরিমাপ গবেষণা

## B. Motivation
- Mobile app input validation client-এ করে; server সেই validation পুনরাবৃত্তি না করলে **“Web API Hijacking”** — parameter tampering-এর mobile রূপ (p.1–2 L7–40, L72–77)।
- OWASP Mobile Top-10-এ “Weak Server Controls” শীর্ষে (p.1); পূর্ববর্তী গবেষণা device-local নিরাপত্তায় কেন্দ্রীভূত, server-side web API কম মনোযোগ পেয়েছে (p.2)।

## C. Research questions
- ⚠️ স্পষ্ট RQ নেই; অন্তর্নিহিত প্রশ্ন: app validation logic থেকে server validation-এর অসঙ্গতি স্বয়ংক্রিয়ভাবে বের করা যায় কি, এবং ecosystem-এ তা কত ব্যাপক?

## D. Contributions (p.2)
- Mobile-to-web validation অসঙ্গতি শনাক্তের প্রথম পদ্ধতিগত approach; “Web API Hijacking” শ্রেণি সংজ্ঞায়ন।
- WARDroid: network-aware app-to-web static analysis framework।
- Misuse pattern ও বাস্তব case study।

## E. Methodology
- **Formal নিয়ম:** Cs(S)=true ⇒ Ca(S)=true; Ca(S)=false ⇒ Cs(S)=false; লক্ষ্য **Cs(S)=true ∧ Ca(S)=false** — app প্রত্যাখ্যান করে কিন্তু server গ্রহণ করে (p.3 L230–255)। App white-box, server black-box।
- **Threat model:** network attacker যে app reverse-engineer করতে ও নিজের HTTPS traffic দেখতে পারে (p.3–4)।
- **Program slicing:** HTTP library (HttpURLConnection, Apache, Volley, javax.net.ssl, URL) ও socket API-কে Point of Interest (POI) ধরে **FlowDroid-এর inverted taint rule দিয়ে backward slicing**; SuSi NETWORK category; ad/analytics library বাদ (p.5–6 L582–)।
- **Augmented PDG:** UI XML constraint (max length, input type, spinner) + EdgeMiner-এর ১৯,৬৪৭ implicit callback (FlowDroid-এর ১৮১-এর বিপরীতে); asynchronous event backward analysis-এ স্বাভাবিকভাবে ক্রমায়িত (p.6–7)।
- **Path constraints → Z3/Z3-Str**; constants (hard-coded API key) inter-procedural constant propagation দিয়ে; request template = <Method, Scheme, Domain, Path, Parameters, Headers, Body> (p.6–8 L599–)।
- **Input generation:** NoTamper-ধাঁচে constraint-এর DNF-এর প্রতিটি disjunct আলাদাভাবে negate (p.9)।
- **Response evaluation:** দুটি valid request-এর response diff দিয়ে noise অপসারণ → invalid response-এর সঙ্গে **edit distance**; negative keyword (“Error”, “Unauthorized”) ও ন্যূনতম আকার filter (p.9 L1011; p.10 L1166)।
- Server fingerprinting heuristic (PHP/ASP.NET, MySQL) দিয়ে SQLi-ধাঁচের input প্রস্তাব (p.8)।

## F. Dataset ও setup
- AndroZoo থেকে Google Play-র শীর্ষ ১০ category-র **১০,০০০ app** (p.9 L1035)।
- নৈতিকতা: test/demo account, private data সংরক্ষণ নয়, কিছু ক্ষেত্রে developer-এর অনুমতি; IRB প্রয়োজন হয়নি বলে দাবি (p.8 L935)।

## G. Evaluation
- Flagged vs verified app সংখ্যা; download-ভিত্তিক victim population; একটি app-এ manual MITM trace বনাম WARDroid template সংখ্যা; case study।

## H. Results (author-reported)
- গড় **৮ মিনিট/app**; ১৬,৪৫১ invalid request sample; **৪,৫৬২ app flagged** (p.9 L1035–1040)।
- ১,০০০ flagged app-এর প্রতিটি থেকে ১টি random invalid request → **৮৮৪টি গৃহীত (৮৮.৪%)**; বাকি ১১৬টিতে আরও sample দিয়ে +৪২ → **৯২৬/১,০০০ verified** (p.9 L1040–1052)।
- **১,৭৪৩ app** unencrypted HTTP ব্যবহার করে (p.9 L1053)।
- Verified ৯২৬ app-এর আনুমানিক victim population **>৬.৪৭ মিলিয়ন**; বেশিরভাগ app ১০০–১,০০০ download (p.10 L1200–1215)।
- Efficacy: একটি random app-এ WARDroid ৮টি template বনাম ২ মিনিটের manual MITM-এ ৬টি unique URI/path (p.10 L1070–1078)।
- **Case study (p.11–12):** JSON-based NoSQL/SQL injection login bypass; e-commerce SDK-তে negative quantity দিয়ে **শূন্য-ডলার checkout** (SDK fixed); news app-এ HTML injection → website-এ XSS; ১০M+ fitness app-এ password length অসঙ্গতি → account lockout; email-কে auth token হিসেবে ব্যবহারকারী money-transfer app-এ SQLi দিয়ে সব user data + তহবিল স্থানান্তর (test server-এ); **১০M+ US bank app**-এ সংযুক্ত নয় এমন account-এ transfer।

## I. Strengths
- নতুন, স্পষ্টভাবে সংজ্ঞায়িত attack শ্রেণি ও formal consistency নিয়ম।
- **বিশাল পরিমাপ** (১০,০০০ app) + বাস্তব, উচ্চ-প্রভাব case study (bank, ১০M+ app) + responsible disclosure।
- Client code-কে server spec-এর “proxy” হিসেবে ব্যবহারের ধারণা — spec ছাড়া API-তে প্রযোজ্য; T4-এর spec inference-এর সঙ্গে ধারণাগত সেতু।
- বিদ্যমান tool (FlowDroid, EdgeMiner, Z3-Str, NoTamper) দক্ষতার সঙ্গে সমন্বিত।

## J. Explicit limitations (p.12 L1381–1415; p.10 L1180)
- Obfuscated code (≈১৫% app) ও native/JNI code সমর্থন করে না।
- পূর্ববর্তী response থেকে আসা state/token নিয়ে যুক্তি করতে পারে না।
- WebView/JavaScript-ভিত্তিক hybrid app-এর API access উপেক্ষিত (৯০%+ app-এ WebView আছে)।
- Authentication-প্রয়োজনীয় request — hard-coded credential/মানব হস্তক্ষেপ লাগে।
- **False negative মূল্যায়ন করা হয়নি** (সম্পূর্ণ coverage নিশ্চিত নয়); ফলকে lower bound বলা হয়েছে।
- Response classification-এর edit distance পদ্ধতি “decent accuracy”, আরও robust পদ্ধতি future work (p.9)।
- App-level false positive পরিমাপ কঠিন (p.10)।

## K. Inferred limitations (⚠️ অনুমান)
- **Precision/false positive পরিমাপ দুর্বল:** “৮৮৪ invalid request গৃহীত” = response edit-distance সাদৃশ্য — server আসলে গ্রহণ করেছে নাকি একই ধরনের error page দিয়েছে তা কেবল “random manual inspection” দিয়ে যাচাই; কোনো precision সংখ্যা নেই। “Verified” শব্দটি security-impact-যাচাই নয়, বরং validation অসঙ্গতি — অনেকগুলো নিরীহ হতে পারে (যেমন server-এ দীর্ঘ string গ্রহণ)।
- **Severity বিভাজন নেই:** ৯২৬টির কতগুলো প্রকৃত exploitable — শুধু হাতে-বাছা case study।
- “Server ≥ client strict” অনুমান সবসময় সত্য নয় — client-side constraint UX-এর জন্য (যেমন password length), security-র জন্য নয়; account-lockout উদাহরণ লেখকরাই “may not be useful” বলেন।
- Efficacy মূল্যায়ন একটি মাত্র app ও ২ মিনিটের manual trace — অত্যন্ত দুর্বল।
- Victim population download-সংখ্যা যোগফল — প্রকৃত ঝুঁকিগ্রস্ত user নয়।
- **Artifact/tool প্রকাশের উল্লেখ নেই** → পুনরুৎপাদন অসম্ভব; app পরিচয় গোপন (নৈতিক কারণে বোধগম্য)।
- ২০১৮-র Android ecosystem (cleartext HTTP এখন default-এ নিষিদ্ধ, Android 9+) — কিছু ফলাফল পুরোনো।
- IRB না নেওয়া এবং live production server-এ invalid request পাঠানো — আধুনিক নৈতিক মানদণ্ডে বিতর্কিত হতে পারে।

## L. Threats to validity
- ⚠️ আনুষ্ঠানিক threats section নেই; limitations অংশ মূলত tool-coverage সীমা। Inferable: construct (response similarity = acceptance), external (Android, ২০১৮)।

## M. Reproducibility
- কোনো code/data release উল্লেখ নেই; নির্ভর tool (FlowDroid, EdgeMiner, Z3-Str) open-source। App সেট AndroZoo থেকে পুনরায় নেওয়া সম্ভব কিন্তু তালিকা প্রকাশিত নয়। **Low reproducibility।**

## N. Opportunities (hypothesis)
- **Client-code-derived API spec inference:** WARDroid-এর template extraction-কে OpenAPI তৈরিতে রূপান্তর — T4 (P017–P019)-এর সঙ্গে সংযোগ; mobile backend-এর জন্য “spec-less” REST testing।
- **Client–server–spec তিনমুখী consistency checking:** app constraint, OpenAPI constraint ও server আচরণ — P001/P004-এর spec-mismatch-এর নিরাপত্তা-মাত্রা।
- **LLM দিয়ে obfuscated code/WebView JS থেকে API template ও constraint অনুমান** — static analysis-এর মূল সীমাবদ্ধতা অতিক্রম।
- **Stateful/authenticated** web API hijacking (token flow modelling) — P014 (BOLA)-র সঙ্গে সমন্বয়।
- Response acceptance oracle-এর উন্নতি (learned classifier) ও precision benchmark।
- iOS/cross-platform পুনরাবৃত্তি ও ২০২০-পরবর্তী ecosystem-এ পুনঃপরিমাপ (replication study)।

## O. Relationships
- **Inspired by** NoTamper ও Waptec (web parameter tampering)।
- **Shares technique with** Extractocol, SmartGen (app থেকে server URL/protocol extraction)।
- **Conceptually related to P012** (server-side binding/validation দুর্বলতা) ও **P014/P015** (authorization)।
- **Links T4:** client code থেকে API constraint অনুমান = spec inference-এর বিকল্প উৎস।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract ফল (১০,০০০/৪,০০০+/১,৭৪৩) | p.1 L30–40 |
| Web API Hijacking সংজ্ঞা | p.1–2 L72–77 |
| Consistency নিয়ম Cs/Ca | p.3 L230–255 |
| Threat model | p.3–4 |
| FlowDroid backward slicing | p.5–6 L582– |
| EdgeMiner callbacks | p.7 |
| Z3-Str, templates | p.6–8 L599– |
| Ethics | p.8 L935 |
| Response edit distance | p.9 L1011 |
| ১০,০০০ app, ৮ min, ৪,৫৬২ flagged | p.9 L1035–1040 |
| ৯২৬/১,০০০ verified | p.9 L1050 |
| ১,৭৪৩ unencrypted | p.9 L1053 |
| Efficacy (৮ vs ৬) | p.10 L1070–1078 |
| FP heuristics; FN মূল্যায়ন নয় | p.10 L1166, L1180 |
| ৬.৪৭M victim | p.10 L1209 |
| Case studies | p.11–12 L1237–1360 |
| Limitations | p.12 L1381–1415 |
| Conclusion | p.13 L1536 |

**Document integrity:** দুই-কলামের reading order ব্যাপকভাবে এলোমেলো (Approach, case study ও limitations অংশ খণ্ডিত ও মিশ্রিত); Listing 1 letter-spaced; Table I–III ও Algorithm 1 আংশিক/হারিয়েছে (Table III-এর category-ভিত্তিক বণ্টন পুনর্গঠন অসম্ভব); Fig.2 অনুপস্থিত। মূল সংখ্যা চলমান text থেকে যাচাইকৃত।
