# P012 — Automated Black-box Testing of Mass Assignment Vulnerabilities in RESTful APIs

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references বাদ) · **উৎস:** arXiv 2301.01261v1 (৩ Jan 2023; “preliminary version prior to peer-review”), ১১ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Davide Corradini, Michele Pasqua, Mariano Ceccato (University of Verona)
- **Venue:** ICSE 2023, DOI 10.1109/icse48619.2023.00213
- **Cluster:** T3 (secondary: T1 — black-box REST test generation; T4 — spec থেকে semantics অনুমান)
- **ধরন:** নতুন security testing technique + empirical validation

## B. Motivation
- Mass assignment OWASP API Security-এর শীর্ষ vulnerability-গুলোর একটি; framework-এর auto-binding (input field → DB column) ভুল configuration-এ attacker read-only field (যেমন `admin`) লিখতে পারে (p.1 L12–22; p.3 L153–232)।
- OWASP guideline হাতে-প্রয়োগের জন্য; **কোনো automated black-box পদ্ধতি নেই** (p.2 L82; p.3 L175–184)।

## C. Research questions (p.6 L463–473)
- RQ1: CRUD semantics, resource type, resource-id স্বয়ংক্রিয় শনাক্তকরণের নির্ভুলতা; RQ2: mass assignment শনাক্তকরণের নির্ভুলতা; RQ3: বড় API-তে scalability।

## D. Contributions
- OpenAPI থেকে read-only attribute শনাক্তকরণ (clustering + heuristic), abstract test template, security oracle — প্রথম automated black-box mass-assignment testing; RestTestGen-এ `MassAssignmentSecurityTestingStrategy` হিসেবে open-source (p.7 L564–571)।

## E. Methodology
- **CRUD semantics:** HTTP method থেকে (POST=C, GET single=R, GET array=RM, PUT/PATCH=U, DELETE=D) (p.4 L253–266)।
- **Resource grouping:** সব parameter নাম Porter stemming → global boolean vector (Table I) → **EM clustering** (cluster সংখ্যা স্বয়ংক্রিয়) (p.4 L278–294)।
- **Resource-id:** `id`/`name` suffix, সবচেয়ে কম nested, `id` অগ্রাধিকার (p.4 L302–312)।
- **OpenAPI annotation:** `x-crudOperationSemantics`, `x-crudResourceType`, `x-crudResourceIdentifier` — developer হাতে দিতে পারেন (p.4 L313–326)।
- **Read-only:** একই group-এ R/RM-এর output-এ আছে কিন্তু C/U-এর input-এ কখনো নেই (p.4–5 L327–342)।
- **Templates:** Update-injection `<Cτ, Rτ, Uτ+f, Rτ, (Dτ, Rτ)?>`; Create-injection `<Cτ+f, Rτ, (Dτ, Rτ)?>`; resource-id output-এ না থাকলে RM দিয়ে before/after diff (Template 1′, 2′) (p.5 L357–426)।
- **Input:** spec-এর example/default/enum, নইলে format-সঙ্গত random; নাম থেকে ২০+ string format অনুমান (p.5 L376–390)।
- **Oracle:** একই resource-id; injected মান পরবর্তী read-এ দেখা গেলে vulnerability; **default-value false positive এড়াতে দ্বিতীয় ভিন্ন মান দিয়ে পুনরাবৃত্তি** (p.6 L474–506)। পার্শ্ব-oracle: undocumented field-যুক্ত request-এ 2xx = spec লঙ্ঘন; 5xx = crash (p.6 L442–456)।
- Parameter: MAX_OPERATION_ATTEMPTS = ১২, MAX_TEMPLATE_ATTEMPTS = ৩ (dry run থেকে) (p.7 L572–576)।

## F. Dataset ও setup
- **নৈতিকতা:** public API (APIs.guru) আক্রমণ এড়িয়ে স্থানীয় open-source API (p.6 L507–516)।
- GitHub search → **৫টি API (Table II):** VAmPI (Python/Flask, ১২ ops), OWASP (Java/Spring, ১০), Toggle (ASP.NET, ১৬), Bookstore (Java/Spring, ৫), CRUD (Node.js/Express, ৪) — মোট ২৬ endpoint, ৪৭ operation (p.7 L526–539)।
- **Vulnerability:** VAmPI ১ ও OWASP ৪ বিদ্যমান; **বাকিগুলোতে হাতে seed করা** (নতুন field + auto-mapping + spec-এ read-এ যোগ); প্রতিটির safe version (p.7 L540–556)।
- **Spec সংশোধন:** লেখক + দুই বহিরাগত বিশেষজ্ঞ source code-এর সঙ্গে মিলিয়ে OpenAPI ঠিক করেছেন; একই দল ground truth তৈরি করেছে (p.7 L557–563)।
- ১০ বার পুনরাবৃত্তি; প্রতিবার state restore (p.7 L582–586)।
- Scalability: ১০টি Google API (Gmail, Drive, YouTube…; ৪৫৪ operation) — **শুধু static অংশ**, dynamic test নৈতিক কারণে চালানো হয়নি (p.9 L720–727)।

## G. Evaluation
- RQ1: correctness ratio vs manual gold standard; RQ2: TP/FP/FN, precision, recall; RQ3: সময় ও read-only field সংখ্যা।

## H. Results (author-reported)
- **RQ1 (Table III):** CRUD গড় **৯৮%** (Toggle ৮৮% — RM অস্বাভাবিক return type-এ R হিসেবে লেবেল); clustering **৯৪%** (ভুলগুলো শুধু delete operation — কম parameter-এর কারণে পৃথক cluster); resource-id **৯৩%** (VAmPI-তে `book_title`) (p.8 L627–653)।
- **RQ2 (Table IV):** সব case-এ FP = ০, precision ১০০%; একমাত্র OWASP-এ গড় TP ৩.৬/৪ (FN ০.৪) — এক রানে ৮টির মধ্যে ২টি sequence instantiate হয়েছিল (p.9 L704–712)। পার্শ্বফল: ২৪টি HTTP 500, **৫টি স্বতন্ত্র bug** (Toggle ছাড়া সব case-এ) (L713–718)।
- **RQ3:** ১০টি Google API-র static analysis গড় **৩৭.২ s**, **৯৮১টি read-only field** candidate (p.9 L728–744)।

## I. Strengths
- স্পষ্ট, সরল, ব্যাখ্যাযোগ্য pipeline; শুধু OpenAPI + HTTP access দরকার — language/framework-নিরপেক্ষ (৪টি language, ৫টি framework)।
- Default-value false positive প্রতিরোধে দ্বৈত-মান যাচাই — চিন্তাশীল oracle নকশা।
- Safe version-এ মূল্যায়ন — false positive সত্যিই পরীক্ষিত।
- Annotation দিয়ে মানুষের হস্তক্ষেপের পথ; RestTestGen-এ open-source।
- নৈতিক বিবেচনা স্পষ্ট।

## J. Explicit limitations (p.8 L654–677; conclusion)
- **Internal:** gold standard-এর subjectivity — source code পরিদর্শনে প্রশমন।
- **Construct:** seed করা vulnerability OWASP সংজ্ঞা মেনে।
- **External:** শুধু open-source; closed-source industrial-এ সাধারণীকরণ অনিশ্চিত।
- CRUD/resource/resource-id শনাক্তকরণ অসম্পূর্ণ হতে পারে — annotation বিকল্প (p.4 L323–326)।
- Future work: আরও project, industrial, BOLA ও access control, developer user study (conclusion)।

## K. Inferred limitations (⚠️ অনুমান)
- **খুব ছোট ও কৃত্রিম মূল্যায়ন:** ৫টি API, ৪৭ operation, মোট **~১০টি vulnerability**, যার অর্ধেকের বেশি **লেখকদের নিজেদের seed করা** — seeding procedure ঠিক যে প্যাটার্ন (spec-এর read-এ field যোগ, write-এ নয়) approach খোঁজে সেটাই তৈরি করে → precision/recall ১০০% প্রত্যাশিত, circularity ঝুঁকি (P008-এর mutation-invariant mirroring-এর অনুরূপ)।
- **Spec হাতে সংশোধিত:** বাস্তবে spec অসম্পূর্ণ/ভুল (P001: ৬৩%, P004: ~৯৯%) — read-only field যদি read response schema-তে না থাকে, পদ্ধতি অন্ধ। লুকানো field (spec-এ নেই কিন্তু DB-তে আছে — বাস্তব mass assignment-এর মূল রূপ) ধরা যায় না।
- **RQ3 কোনো scalability প্রমাণ নয়:** শুধু static অংশ; ৯৮১ candidate-এর কতটি সত্যিই read-only বা vulnerable তা অজানা — precision বড় API-তে অজ্ঞাত; dynamic অংশের খরচ “অনুমান” (লেখকরাও “speculate” বলেন, L733)।
- Authentication/authorization প্রেক্ষাপট (কোন user role কোন field লিখতে পারে) উপেক্ষিত — admin user-এর জন্য `admin` লেখা বৈধ হতে পারে।
- কোনো baseline নেই (যুক্তিসঙ্গত — প্রথম পদ্ধতি — কিন্তু OWASP ZAP/Burp-এর param-mining বা সরল “সব response field inject” baseline তুলনা সম্ভব ছিল)।
- পাঠিত সংস্করণ preprint (peer-review-পূর্ব) — চূড়ান্ত ICSE সংস্করণে সংখ্যা ভিন্ন হতে পারে।

## L. Threats to validity
- উপরে J; inferable: construct (seeded vulnerability-র প্রতিনিধিত্বশীলতা), external (ছোট toy API)।

## M. Reproducibility
- RestTestGen-এ strategy open-source; replication package উল্লেখিত (p.8 L681); case study GitHub-এ; সংশোধিত spec ও ground truth package-এ থাকার কথা (যাচাই প্রয়োজন)।

## N. Opportunities (hypothesis)
- **Spec-independent read-only/sensitive field আবিষ্কার:** response observation, framework convention বা **LLM দিয়ে sensitive field (role, balance, isVerified) অনুমান** — undocumented field-এর জন্য।
- **Role-aware mass assignment ও BOLA/BFLA একীভূত oracle** — P014/P015-এর সঙ্গে সমন্বয়ে OWASP API Top-10-এর authorization শ্রেণির একটি সমন্বিত black-box framework।
- **বাস্তব (non-seeded) vulnerability benchmark** — CVE/bug bounty থেকে REST API security benchmark (T3-এ একটি সাধারণ gap)।
- RQ3 সম্প্রসারণ: বড় API-তে candidate precision পরিমাপ (sandbox/local deployment)।
- White-box hybrid: ORM model/DTO পড়ে read-only field নির্ণয় (P018 static analysis-এর সঙ্গে)।

## O. Relationships
- **Built on** RestTestGen (একই গবেষণা-গোষ্ঠী)।
- **Contrasts with** RESTler-এর security checker (P006-এর পরবর্তী কাজ: use-after-free, resource-leak, hierarchy, namespace) — mass assignment সেখানে নেই।
- **Precursor to** P014 (BOLA), P015 (access policy) — লেখকদের future work-এ BOLA উল্লেখ।
- **Depends on spec quality** — T4 (P016–P019) cluster-এর সঙ্গে নির্ভরতা; P001/P004-এর spec-mismatch ফলাফল এর প্রয়োগযোগ্যতা সীমিত করে।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Mass assignment সংজ্ঞা, VAmPI উদাহরণ | p.2–3 L144–232 |
| কোনো automated black-box পদ্ধতি নেই | p.2 L82 |
| CRUD inference | p.4 L253–269 |
| EM clustering | p.4 L278–294 |
| Resource-id heuristic | p.4 L302–312 |
| Annotation | p.4 L313–326 |
| Templates | p.5 L357–426 |
| Oracle, দ্বৈত-মান যাচাই | p.6 L474–506 |
| RQs | p.6 L463–473 |
| Case studies (Table II), seeding | p.7 L526–563 |
| Configuration, ১০ রান | p.7 L572–586 |
| RQ1 (৯৮/৯৪/৯৩%) | p.8 L627–653 |
| Threats | p.8 L654–677 |
| RQ2 (Table IV) | p.9 L692–718 |
| RQ3 (৩৭.২ s, ৯৮১) | p.9 L720–744 |
| Conclusion, future work | p.11 |

**Document integrity:** দুই-কলামের reading order কিছু জায়গায় এলোমেলো (abstract intro-র মাঝে; RQ1 উপসংহার threats-এর আগে); Table II–V column-split — Table IV-এর TP/FP/FN/Pr পুনর্গঠনযোগ্য (Recall কলাম markdown-এ দৃশ্যমান নয়), CRUD-এর #Vuln মান হারিয়েছে (TP ২.০ থেকে ২ অনুমিত); Template 2 সূত্র আংশিক হারানো, text থেকে পুনর্গঠিত।
