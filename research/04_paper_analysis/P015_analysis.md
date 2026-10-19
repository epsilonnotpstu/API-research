# P015 — Fuzzing for Detecting Access Policy Violations in REST APIs

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references বাদ) · **উৎস:** ISSRE 2025 IEEE version, ১২ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Andrea Arcuri, Omur Sahin, Man Zhang (Kristiania University of Applied Sciences; ইত্যাদি)
- **Venue:** IEEE ISSRE 2025, DOI 10.1109/ISSRE66568.2025.00025
- **Cluster:** T3 (secondary: T1 — fuzzer oracle সম্প্রসারণ)
- **ধরন:** নতুন automated oracle + fuzzer integration + empirical study

## B. Motivation
- OWASP API 2023-এ BOLA #১, BFLA #৫; বিদ্যমান REST fuzzer মূলত 500 ও schema mismatch খোঁজে; অনেক fuzzer authentication-ই সামলাতে পারে না, আর যারা পারে তারা BOLA/BFLA স্বয়ংক্রিয়ভাবে ধরে না (p.1 L32–38, L76–84)।
- Related work-এর সমালোচনা: RESTler-এর user-namespace নিয়ম অতি-কঠোর (shared access উপেক্ষা); Nautilus-এ manual annotation; LLM-ভিত্তিক BOLA কাজের oracle অস্পষ্ট; **Petri-net পদ্ধতির (P014) OpenAPI links প্রয়োজন** (p.2 L127–169)।

## C. Research questions (p.8 L1057–1061)
- RQ1: injected fault শনাক্ত? RQ2: security-literature-এর example API-তে fault? RQ3: বাস্তব API-তে কী security fault পাওয়া যায়?

## D. Contributions
- তিনটি নতুন automated oracle, fuzzing-পরবর্তী “security testing phase” হিসেবে; শর্ত শুধু OpenAPI + অন্তত দুই user-এর login তথ্য; কোনো access-policy specification বা annotation লাগে না (p.2 L171–179; p.3 L188–196)।
- EvoMaster-এ open-source integration; fault-সহ executable test (comment-সহ) output।

## E. Methodology
- **মূল কৌশল:** fuzzer-এর তৈরি valid test (T) থেকে প্রয়োজনীয় call খুঁজে copy, target-এর পরের call slice করা, নতুন sequence জোড়া — জটিল input data পুনরায় তৈরি না করেই নির্দিষ্ট status code পাওয়া (p.3 L240–270)।
- **Oracle A — Not-Recognized (fault 801):** authenticated user 401 পায় যেখানে 403 হওয়া উচিত; false-positive এড়াতে তিন শর্ত: X-এ A-র 401; অন্য endpoint Y-তে A-র 2xx; Y-তে অন্য কোনো test-এ 401/403 (Y সুরক্ষিত প্রমাণ) — **usability fault, vulnerability নয়** (p.3 L277–315, L344–354)।
- **Oracle B — Leakage (fault 800):** একই endpoint-এ 403 ও 404 উভয় পাওয়া → protected resource-এর অস্তিত্ব ফাঁস (RFC 9110 অনুযায়ী 403 বা 404 সামঞ্জস্যপূর্ণ হওয়া উচিত); ancestor resource-এ GET করে বৈধ 404 বাদ (p.3–5 L330–342, L510–518, L667–678)।
- **Oracle C — Missed-Check (fault 802):** একই user-এর জন্য PUT/PATCH/DELETE-এর একটিতে 403 কিন্তু অন্যটিতে 2xx → সম্ভাব্য বাদ পড়া authorization check; কিছু false positive স্বীকৃত (p.5–6 L659–718)।
- **Fuzzer integration:** EvoMaster ভিন্ন user দিয়ে একই resource-এ call কম তৈরি করে → 403 test তৈরি করতে post-processing-এ user বদলে শেষ call duplicate; overhead endpoint সংখ্যার রৈখিক, সাধারণত <১ মিনিট (p.7 L837–999)।

## F. Dataset ও setup
- **RQ1:** ৩টি ছোট Java/SpringBoot API, প্রতিটিতে প্রতিটি oracle-এর জন্য injected fault; ১ মিনিট × ১০ (p.8 L1138–1147)।
- **RQ2:** ৩টি security example API — capital (Checkmarx), crAPI (OWASP), WebGoat; black-box, ১ ঘণ্টা × ১০; মোট ৩২,২৭৬ LoC, ২৫৯ endpoint (Table I)।
- **RQ3:** EMB-এর authentication-প্রয়োজনীয় সব (১০টি) API — white-box, ১ ঘণ্টা × ১০; ২৯১,৪৯১ LoC, ৭৯২ endpoint (Table II; familie-ba-sak ১৪৩,৫৫৬ LoC — নরওয়ের child benefit system)।
- মোট >১৩০ ঘণ্টা compute (p.8 L1134–1135)।

## G. Evaluation
- প্রতি API-তে গড় fault (১০ রান) — বিদ্যমান oracle (H500, Schema) ও তিন নতুন oracle (Table III)।

## H. Results (author-reported)
- **RQ1:** প্রতিটি পরীক্ষায় সব injected fault শনাক্ত (p.8 L1168–1177)।
- **RQ2:** capital — Leakage ১.০, Missed-Check ০.৭ (১০-এর ৭ রানে); crAPI — Not-Recognized ১.০; WebGoat — Not-Recognized ৫.০ (Table III)।
- **RQ3:** familie-ba-sak Not-Recognized ১১.৯; proxyprint Not-Recognized ৪.২ + Leakage ২.০; scout-api ০.১ (১০-এর ১ রানে); **বাস্তব API-তে কোনো Missed-Check নেই** (p.9 L1366–1376; Table III)।
- **মোট ২৭টি distinct fault** (সব রানে নয়); তুলনায় বিদ্যমান oracle: **H500 ৮১২.৪, Schema ১২,৪১৩.২** (গড় যোগফল) — “a drop in a bucket” (p.9 L1353–1360)।
- Discussion: 500 আসলে crash নয় — প্রায়ই input validation ত্রুটি; schema fault-এর বড় অংশ অসম্পূর্ণ documentation (404 অঘোষিত, nullable না দেওয়া) — **severity এক নয়**; Missed-Check সম্ভবত অনেক গুরুত্বপূর্ণ (p.11 L1520–1578)।

## I. Strengths
- **Specification-মুক্ত oracle:** access-policy formal spec (XACML ইত্যাদি) বাস্তবে নেই বলে HTTP status-code সামঞ্জস্যের heuristic — ব্যবহারিক ও fuzzer-agnostic।
- False-positive প্রতিরোধে চিন্তাশীল শর্ত (Not-Recognized-এর তিন ধাপ, Leakage-এর ancestor check)।
- বিদ্যমান test pool পুনঃব্যবহার — জটিল input তৈরির সমস্যা এড়ায়।
- বাস্তব, বড় সরকারি system (familie-ba-sak) সহ ১৬টি API; open-source; ১০ রান।
- 500/schema fault-এর severity নিয়ে সৎ, সমালোচনামূলক আলোচনা — T1 cluster-এর “500 count” মেট্রিকের সীমাবদ্ধতা স্পষ্ট করে।

## J. Explicit limitations (p.11 §VI; text)
- ১৬টি API — industrial API-তে সাধারণীকরণে বড় study প্রয়োজন।
- অন্য fuzzer-এ integration-এর সহজতা অপরীক্ষিত।
- Oracle fuzzer-এর generated test-এর উপর নির্ভরশীল — coverage কম হলে oracle অকার্যকর (scout-api ০.১)।
- Missed-Check-এ কিছু false positive সম্ভব।
- Security example API-তে অন্য কোনো fault ছিল কিনা হাতে যাচাই করা হয়নি (recall অজানা) (p.9 L1320–1325)।
- Fault severity — practitioner study ছাড়া নিশ্চিত বলা যায় না।

## K. Inferred limitations (⚠️ অনুমান)
- **Precision কখনো মাপা হয়নি:** ২৭টি “fault”-এর কতগুলো developer-স্বীকৃত বা সত্যিকারের — কোনো manual validation বা developer confirmation রিপোর্ট নেই (familie-ba-sak-এর একটি উদাহরণের Norwegian error message ছাড়া)। P011-এর মতো industrial triage এখানে অনুপস্থিত।
- **সবচেয়ে গুরুত্বপূর্ণ oracle (Missed-Check) বাস্তব API-তে শূন্য** — প্রকৃত BOLA/BFLA vulnerability-র প্রমাণ কেবল একটি ইচ্ছাকৃত-vulnerable app-এ (capital); বেশিরভাগ fault Not-Recognized (লেখকদের ভাষায় “usability fault, not a security vulnerability”) — শিরোনামের “access policy violations” দাবির তুলনায় ফল দুর্বল।
- **প্রকৃত BOLA (user A অন্য user B-র resource-এ 2xx পায়) সরাসরি ধরা হয় না** — কারণ policy অজানা; Missed-Check একটি পরোক্ষ proxy (verb-অসামঞ্জস্য)। শুধু read-access BOLA (GET) এই oracle-এর বাইরে।
- **Count-এর অসামঞ্জস্য:** abstract-এ “13 real-world REST APIs”, conclusion-এ “13 real-world APIs” — কিন্তু §V অনুযায়ী ১০টি real-world + ৩টি security example (ইচ্ছাকৃত vulnerable)।
- Self-evaluation: EvoMaster লেখকগোষ্ঠী (P002/P003/P011-এর সঙ্গে একই) নিজের tool-এ নিজের oracle মূল্যায়ন; অন্য fuzzer (RESTler-এর namespace checker, P012-এর RestTestGen) বা P014-এর সঙ্গে head-to-head তুলনা নেই।
- Status code-ভিত্তিক heuristic — API যদি 200 + error body দেয় (সাধারণ প্র্যাকটিস; familie-ba-sak-এর “FEILET” status উদাহরণ), oracle বিভ্রান্ত হতে পারে।

## L. Threats to validity
- উপরে J (conclusion: ১০ রান; external: ১৬ API, এক fuzzer); inferable: construct (Not-Recognized = security fault?), precision অজানা।

## M. Reproducibility
- EvoMaster extension open-source; EMB ও ৩টি artificial API উন্মুক্ত; security example API-গুলো public GitHub-এ — **উচ্চ** reproducibility।

## N. Opportunities (hypothesis)
- **Policy inference + ownership oracle:** traffic/test থেকে “কে কোন resource তৈরি করেছে” track করে A-র resource-এ B-র 2xx = BOLA candidate; LLM দিয়ে endpoint semantics (admin-only, owner-only) অনুমান — P012/P014/P015 একীভূত করার সুস্পষ্ট gap।
- **Developer-validated precision study** — তিন oracle-এর FP হার ও severity practitioner দিয়ে মূল্যায়ন (লেখকরাই প্রয়োজনীয় বলেন)।
- **Cross-tool security oracle benchmark:** RESTler security checkers, RestTestGen mass-assignment, Links2CPN, EvoMaster oracles একই API সেটে (T3-এ বাস্তব vulnerability benchmark-এর অভাব)।
- Fault severity/triage: ১২,০০০+ schema fault ও ৮০০+ 500 থেকে গুরুত্বপূর্ণগুলো আলাদা করা (LLM-সহায়ক classification) — T1 ও T6 সংযোগ।
- 200-with-error-body API-র জন্য response-semantic oracle।

## O. Relationships
- **Explicitly contrasts** P014 (links দরকার), RESTler security rules (P006 লেখকদের পরবর্তী কাজ), P012 (mass assignment — RestTestGen extension)।
- **Extends** EvoMaster (P002/P003/P011 গোষ্ঠী)।
- **Supports P003/P008-এর oracle-problem থিম** — 500-এর বাইরে semantic oracle প্রয়োজন।
- **Schema-fault আলোচনা** P001/P004-এর spec-implementation mismatch-এর সঙ্গে সামঞ্জস্যপূর্ণ।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| BOLA/BFLA motivation | p.1 L32–38, L76–84 |
| Related work সমালোচনা (RESTler, P014) | p.2 L127–169 |
| শর্ত: OpenAPI + ২ user | p.2 L171–177; p.3 L188–196 |
| Test copy/slice কৌশল | p.3 L240–270 |
| Not-Recognized oracle | p.3 L277–315, L344–354 |
| Leakage oracle | p.3–5 L330–342, L510–518, L667–678 |
| Missed-Check oracle | p.5–6 L659–800 |
| Fuzzer integration, overhead | p.6–7 L802–999 |
| RQs | p.8 L1057–1061 |
| Setup (১ ঘণ্টা × ১০, >১৩০ ঘণ্টা) | p.8 L1121–1135 |
| Table I–II | p.8 L1013–1056 |
| RQ1 | p.8 L1168–1177 |
| Table III | p.9 L1203–1316 |
| ২৭ fault বনাম ৮১২/১২,৪১৩ | p.9 L1353–1360 |
| RQ3, familie-ba-sak উদাহরণ | p.9–10 L1366–1512 |
| 500/schema severity আলোচনা | p.11 L1520–1578 |
| Threats | p.11 L1581–1593 |

**Document integrity:** Body সম্পূর্ণ; দুই-কলামের reading order আংশিক মিশ্রিত (Not-Recognized ও Leakage অনুচ্ছেদ পরস্পরে ঢুকে গেছে); generated test listing (Kotlin/Java) পাঠযোগ্য; Table I–III column-split কিন্তু Sum সারি দিয়ে পুনর্গঠন যাচাই করা হয়েছে (NR ২২.২, Leakage ৩.০, Missed ০.৭)।
