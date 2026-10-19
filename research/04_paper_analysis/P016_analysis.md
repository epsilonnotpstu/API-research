# P016 — Specification and Automated Analysis of Inter-Parameter Dependencies in Web APIs (IDL)

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (related work §8 বাদ, references বাদ) · **উৎস:** arXiv 2005.03320v1 (৭ May 2020), ১৪ পৃষ্ঠা — চূড়ান্ত IEEE TSC সংস্করণের পূর্ববর্তী preprint · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Alberto Martin-Lopez, Sergio Segura, Carlos Müller, Antonio Ruiz-Cortés (ISA group, Universidad de Sevilla)
- **Venue:** IEEE Transactions on Services Computing, 2022 (online 2021), DOI 10.1109/tsc.2021.3050610
- **Cluster:** T4 (secondary: T1 — valid test input generation; T6 — spec language design)
- **ধরন:** DSL + formal semantics (CSP mapping) + tool suite

## B. Motivation
- Web API প্রায়ই **inter-parameter dependency** আরোপ করে (Twilio: `body` বা `media_url` কিন্তু উভয় নয়; QuickBooks: `region` বা `postalCode` অন্তত একটি) (p.1 L68–80)।
- OAS ও RAML এ ধরনের dependency বর্ণনা করতে পারে না — Swagger নিজেই বলে “OpenAPI 3.0 does not support parameter dependencies”; OAS GitHub issue #256 (২০১৫) >২৬০ vote, ৫৫ comment (p.1–2 L82–119)।
- লেখকদের পূর্ববর্তী গবেষণা [26]: ৪০টি API-র ২,৫৫৭ operation পর্যালোচনা — **৮৫% API-তে (৩৪/৪০) dependency**, ৬৩৩টি dependency, **৯.৭% operation-এ (২৪৮/২,৫৫৭)** (p.2 L191–197)।

## C. Research questions (p.11 L1325–1337)
- RQ1 Expressiveness: IDL কি বাস্তব API-র dependency মডেল করতে যথেষ্ট? RQ2 Validation: IDLReasoner-এর analysis operation কি প্রত্যাশিতভাবে কাজ করে?

## D. Contributions (p.2)
- **IDL** — inter-parameter dependency-র জন্য textual DSL (PICT-অনুপ্রাণিত)।
- **IDL → CSP mapping** (formal semantics) ও **৯টি analysis operation** catalogue।
- Tool suite: Xtext editor (LSP-সমর্থিত), parser, **IDL4OAS** (`x-dependencies` extension), **IDLReasoner** (MiniZinc-ভিত্তিক Java library; Chuffed, Gecode), ১৭৮টি test case।

## E. Methodology
- **৭টি dependency type (Fig.1):** Requires (৩৫% dependency; ৪৭.৫% API), Or (৩%; ২৭.৫%), OnlyOne (১৭%; ৪৭.৫%), AllOrNone (৬%; ৩০%), ZeroOrOne (১৮%; ৪৭.৫%), Arithmetic/Relational (১৭%; ৫০% — সবচেয়ে বিস্তৃত), Complex (৪%; ৭.৫%) (p.3–4 L234–358)।
- **IDL syntax:** `IF p THEN q`, `Or(...)`, `OnlyOne(...)`, `AllOrNone(...)`, `ZeroOrOne(...)`, relational/arithmetic (`p1 + p2 < 100`), `LIKE` wildcard; predicate-এ NOT/AND/OR; Requires predicate-এর ভিতরে নিষিদ্ধ; Or/OnlyOne ইত্যাদি syntactic sugar (p.4–6 L363–598)।
- **CSP mapping (Table 1):** প্রতিটি parameter-এর জন্য দুটি variable (`p` ও `pSet`); relational/arithmetic শুধু সব parameter উপস্থিত থাকলে মূল্যায়িত (p.6–7 L717–848)।
- **৯ operation:** consistent specification, dead parameter, false optional, valid specification, valid request, valid partial request, all requests, number of requests, random request (p.8–9 L961–1163)।

## F. Dataset ও setup
- RQ1: **২২টি জনপ্রিয় API-র ৩০টি operation** (Amazon PA, Box, GitHub, Groupon, PayPal, Shopify, Vimeo, YouTube…); ১০টি পূর্ববর্তী study থেকে, ২০টি নতুন; **১৪৯টি dependency** IDL-এ লেখা (p.11 L1343–1358)।
- RQ2: equivalence partitioning, boundary-value, PICT দিয়ে pairwise combinatorial — **১৭৮টি test case** (JUnit 5) (p.11 L1379–1394)।

## G. Evaluation
- RQ1: গুণগত (লেখকরা নিজেরা মডেল করেছেন — expressiveness সমস্যা পাওয়া গেছে কিনা)।
- RQ2: test suite পাস/ফেল; execution time।

## H. Results (author-reported)
- **RQ1:** ১৪৯টি dependency-র সবকটি সংক্ষিপ্তভাবে প্রকাশযোগ্য — **কোনো expressiveness সমস্যা নেই** (p.11 L1351–1354)।
- **RQ2:** test suite parsing, MiniZinc translation ও boundary case (parameter-হীন operation)-এ fault প্রকাশ করেছে — সব fix; শেষে সব test পাস; পুরো suite ৬০–৭০ s; বেশিরভাগ operation কয়েক ms, শুধু all-requests ব্যয়বহুল (p.12 L1429–1445)।

## I. Strengths
- **Empirical ভিত্তি:** language নকশা ২,৫৫৭ operation-এর study থেকে উদ্ভূত — অনুমান-নির্ভর নয়।
- Formal semantics (CSP) → স্বয়ংক্রিয় reasoning (dead/false-optional parameter, valid request) — API gateway, test generation, client code generation-এ প্রয়োগ সম্ভাবনা।
- OAS-এর সঙ্গে সামঞ্জস্যপূর্ণ extension (IDL4OAS) — গ্রহণযোগ্যতা সহজ।
- সব artifact (IDL spec, dataset, test suite, demo video) উন্মুক্ত।
- পরবর্তীতে RESTest-এ ব্যবহৃত — বাস্তব প্রভাব (P002 survey-তে inter-parameter dependency একটি স্বীকৃত চ্যালেঞ্জ)।

## J. Explicit limitations (p.12 §7; conclusion)
- Dependency শনাক্তকরণ manual documentation review — misclassification/overlook সম্ভব।
- Tool-এ bug থাকতে পারে (test suite দিয়ে প্রশমিত)।
- ৪০টি API-র বাইরে সাধারণীকরণ অনিশ্চিত।
- **Developer/practitioner দিয়ে usability মূল্যায়ন নেই** — IDL বোঝা কঠিন হতে পারে।
- Future work: inconsistency-র কারণ ব্যাখ্যা (CSP explanation), RAML integration।

## K. Inferred limitations (⚠️ অনুমান)
- **IDL লেখার ভার মানুষের:** dependency স্বয়ংক্রিয়ভাবে **অনুমান** করা হয় না — documentation-এর natural language থেকে IDL-এ রূপান্তর হাতে; ৮৫% API-তে dependency থাকা সত্ত্বেও কতজন provider IDL লিখবেন? (OAS-এ links-এর ৯/১,৯৫৫ ব্যবহার — P014 — একই ধরনের adoption-ঝুঁকির ইঙ্গিত দেয়)।
- **RQ1 আত্ম-মূল্যায়িত ও circular-প্রবণ:** একই লেখকরা language নকশা ও মূল্যায়ন উভয়ই করেছেন; ১৪৯টি dependency তাদেরই বাছাই করা; কোনো স্বাধীন annotator বা inter-rater agreement নেই; “কোনো সমস্যা নেই” একটি দুর্বল (non-falsifying) প্রমাণ।
- **RQ2 শুধু software correctness** — বাস্তব API testing-এ IDL-এর উপযোগিতা (যেমন invalid request হ্রাস, coverage বৃদ্ধি) এখানে পরিমাপ করা হয়নি (পরবর্তী RESTest কাজে আংশিক)।
- **Scope সীমাবদ্ধ:** শুধু একই operation-এর input parameter-এর মধ্যে dependency; **inter-operation (stateful) dependency, response-নির্ভর constraint, header/body nested field-এর গভীর constraint** IDL-এ নেই।
- Dependency study-র ডেটা ২০১৯-এর; documentation ভুল/পুরোনো হতে পারে — documentation-এ লেখা dependency আর server-এর প্রকৃত আচরণের পার্থক্য যাচাই হয়নি।
- পাঠিত সংস্করণ arXiv preprint (২০২০) — চূড়ান্ত TSC সংস্করণে পরিবর্তন সম্ভব।

## L. Threats to validity
- উপরে J; inferable: construct (expressiveness-এর মানদণ্ড অস্পষ্ট), evaluator bias।

## M. Reproducibility
- IDL, IDLReasoner, IDL4OAS GitHub-এ; dataset, test suite, demo video supplementary [43]-এ — **উচ্চ**।

## N. Opportunities (hypothesis)
- **স্বয়ংক্রিয় IDL inference:** NL documentation থেকে **LLM দিয়ে IDL তৈরি** (NLP2REST, P017-এর মতো LLM spec generation-এর সঙ্গে); source code থেকে static analysis দিয়ে (P018/P019 — validation logic থেকে dependency); traffic থেকে mining — T4-এর কেন্দ্রীয় gap।
- **Documentation-implementation dependency drift:** documented IDL বনাম server-এর প্রকৃত আচরণ — differential testing দিয়ে অসঙ্গতি (P001/P004-এর spec mismatch-এর dependency-মাত্রা)।
- **Inter-operation/stateful constraint language** — IDL-কে sequence-level-এ সম্প্রসারণ (P008 AGORA-র sequence invariant future work-এর সঙ্গে মিল)।
- IDL-aware LLM agent tool calling — invalid tool-call হ্রাস (T8 সংযোগ: P033/P034-এর API call ত্রুটি)।
- Developer usability study (লেখকদের স্বীকৃত gap)।

## O. Relationships
- **Builds on** লেখকদের ICSOC 2019 dependency catalogue [26]।
- **Used by** RESTest (একই গোষ্ঠী; P002/P004 সাহিত্যে উদ্ধৃত)।
- **Complements P017–P019** (spec inference) — তারা spec তৈরি করে, IDL spec-এ যা প্রকাশ করা যায় না তা প্রকাশ করে।
- **Shares group with P009** (SCORE/ISA Lab, Sevilla) — Ruiz-Cortés উভয়ে।
- **Links P012** — উভয়ই OpenAPI-তে `x-` extension দিয়ে অতিরিক্ত semantics যোগ করে।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Twilio/QuickBooks উদাহরণ | p.1 L68–80 |
| OAS অসমর্থন, issue #256 | p.1–2 L82–119 |
| ৮৫% API, ৬৩৩ dependency, ৯.৭% | p.2 L191–197 |
| ৭টি dependency type ও শতাংশ | p.3–4 L234–358 |
| IDL grammar (Listing 1) | p.5 L386–467 |
| IDL syntax উদাহরণ | p.5–6 L469–598 |
| Google Maps Places IDL (Listing 2) | p.6 L621–708 |
| CSP mapping (Table 1) | p.6–7 L717–848 |
| ৯ analysis operation | p.8–9 L961–1163 |
| Tool suite, IDL4OAS, IDLReasoner | p.9–10 L1169–1305 |
| RQ1–RQ2 | p.11 L1325–1337 |
| RQ1 (৩০ ops, ২২ API, ১৪৯ dep) | p.11 L1343–1358 |
| RQ2 (১৭৮ test) | p.11–12 L1379–1449 |
| Threats | p.12 L1454–1517 |
| Conclusions, future work | p.13 L1681–1719 |

**Document integrity:** Body সম্পূর্ণ; section heading-এর অনেকগুলো (২–৯) auto-detect হয়নি; Table 1 (CSP mapping) সূত্র আংশিক ভাঙা (∀, ⇒ চিহ্ন বিকৃত); grammar listing আংশিক; Fig.1 (dependency distribution) অনুপস্থিত — শতাংশ text থেকে। Conclusions references-এর পরে অবস্থিত (pdftotext ক্রম)।
