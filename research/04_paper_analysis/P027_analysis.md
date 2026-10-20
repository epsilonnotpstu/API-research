# P027 — RESTRuler: Towards Automatically Identifying Violations of RESTful Design Rules in Web APIs

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references বাদ) · **উৎস:** arXiv 2402.13710 / ICSA 2024 version, ১২ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Justus Bogner (Vrije Universiteit Amsterdam), Sebastian Kotstein (Reutlingen University), Daniel Abajirov, Timothy Ernst, Manuel Merkel (University of Stuttgart)
- **Venue:** IEEE ICSA 2024, DOI 10.1109/icsa59870.2024.00020
- **Cluster:** T6 (secondary: T4 — OpenAPI static analysis)
- **ধরন:** Open-source tool + benchmark-ভিত্তিক মূল্যায়ন

## B. Motivation
- Design rule-এর গুরুত্ব (Delphi study) ও কার্যকারিতা (P026 experiment) প্রমাণিত, কিন্তু practitioner-এর পক্ষে বড় API-তে violation হাতে খোঁজা কঠিন (p.1 L62–74)।
- বিদ্যমান practitioner linter (Spectral, IBM OpenAPI Validator-এর ৬৭ rule, Zalando-র Zally) মূলত documentation ও naming syntax পরীক্ষা করে, RESTful design semantics নয়; Zally লেখকদের ১৪টি rule-এর মাত্র ৪টি সমর্থন করে (p.2–3 L192–264)।
- গবেষণা-tool (SARA/SOFA, Brabra et al.) আংশিক overlap, কিন্তু Massé-র empirically যাচাইকৃত rule-এর জন্য কোনো public tool নেই (p.2 L125–135)।

## C. Research questions (p.3 L312–315)
- RQ1 robustness (কত শতাংশ real-world OpenAPI সফলভাবে বিশ্লেষিত); RQ2 performance efficiency (সময়, RAM, CPU); RQ3 effectiveness (precision, recall)।

## D. Contributions
- **RESTRuler** — Java CLI (Micronaut, picocli, swagger-parser), modular rule interface (`checkViolation()`), line-number-সহ Markdown report, CI/CD-বান্ধব; GitHub-এ open-source (restful-ma/rest-ruler) (p.3–4 L319–446)।
- ১৪টি Massé rule; পুনঃব্যবহারযোগ্য evaluation design ও Zenodo artifact (p.1 L76–94; p.6 L655)।

## E. Methodology
- **Rule নির্বাচন:** Massé-র ৮২ → Delphi-তে উচ্চ/মাঝারি গুরুত্বের ৪৫ → OpenAPI তথ্য দিয়ে প্রয়োগযোগ্য ও effort-সম্ভব → **১৪টি** (১০টি উচ্চ, ৪টি মাঝারি গুরুত্ব; ৬টি P026-এ significant) (p.3 L275–291)।
- **Category (Table I):** URI Design ১০ (PluralNoun, SingularNoun, VerbController, NoTrailingSlash, ForwardSlash, NoFileExtensions, NoCRUDNames, NoUnderscores, Hyphens, Lowercase), Metadata ১ (ContentType), Request Methods ২ (NoTunnel, GETRetrieve), Status Codes ১ (RC401) (p.4–5 L409–540)।
- **Detection কৌশল:** string comparison; dictionary (৮০০+ file extension, CRUD verb তালিকা + ৮০০+ compound noun ব্যতিক্রম, ১২৬k English word); **Apache OpenNLP** tokenization ও POS tagging (Plural/SingularNoun, VerbController); **NoTunnel-এর জন্য custom Naive Bayes Multinomial** (Weka) — description/summary থেকে প্রত্যাশিত HTTP verb অনুমান; ৩,২২৭টি হাতে-labeled নমুনা, ১০-fold CV-তে **গড় accuracy ৮৯%** (p.5–6 L546–633)।
- **উন্নয়ন প্রক্রিয়া:** rapid prototyping; একজন violation তৈরি, দ্বিতীয়জন implement + test, তৃতীয়জন PR review; GitHub Actions CI (p.3 L293–305)।
- **মূল্যায়ন:** APIs.guru থেকে **২,৩৩১টি OpenAPI** (৬২% very small, ২২% small, ১০% medium, ৪% large, ২% very large); precision — ৯০টি random report × সর্বোচ্চ ৩০ violation = **১,৫৯৬ violation** তিন গবেষক হাতে যাচাই; recall — **৭ জন API expert-এর তৈরি ১১১টি “কঠিন/edge-case” violation** (gold standard); Zally-র সঙ্গে ৪টি সাধারণ rule-এ recall তুলনা; Ryzen 5 laptop, psutil দিয়ে RAM/CPU (p.6–7 L657–875)।

## F. Dataset
- উপরে E।

## G. Evaluation
- Success rate; সময়/RAM/CPU size category অনুযায়ী; per-rule precision ও recall।

## H. Results (author-reported)
- **RQ1:** ২,৩৩১-এর ২,৩০০টি সফল — **৯৮.৭%** (abstract-এ “৯৯%”); ৩১টি ব্যর্থ: ১টি ত্রুটিপূর্ণ definition, ৩০টি very large file-এ RAM (৫–৭ GB) — dictionary/NLP rule-এর কারণে (p.7 L928–933, L878–885)।
- **মোট ১৬৯,০৬১ violation** (গড় ৭৩.৫, median ২০/file); ContentType ৩৮,০৫৯ (২২.৫%) ও RC401 ৩৪,২৭৬ (২০.৩%) — মিলে >৪০%; VerbController (০.০৮%), NoTunnel (০.২৬%) বিরল (p.7 L886–904)।
- **RQ2:** median সময় very small ~৭ s, small ২৪ s, medium ৫৫ s, large ~২ min, very large ~৫ min; **৮৪% file <২৩ s**; RAM median ৪৯৭ MB (very small) থেকে ~১.১ GB; CPU median ৮.৪% (p.7–8 L908–1004)।
- **RQ3:** সামগ্রিক **precision ৯১.২%** (rule-ভেদে ৬০–১০০%), **recall ৬৭.৬%** (৪৬.২–১০০%); benchmark-পরবর্তী সহজ সংশোধনে recall ~৭৫% (p.8 L1137–1146, L942–946)।
- **Per-rule:** NoUnderscores, Lowercase ১০০/১০০; RC401 P ১০০% (৩৫৮) / R ৮৩.৩%; GETRetrieve P ৬৬.৭% / R ১০০%; NoCRUDNames P ৯৫.২% / R ৬১.৫% (synonym “purge”, “fetch” মিস); ForwardSlash P ৯৫.১% / **R ৪৪.৪%** (hierarchy semantic অংশ অসমর্থিত); NoFileExtensions **P ৬০%** (`Microsoft.Sql`) / R ৬২.৫%; Hyphens P ৮২.১% / R ৮৮.৯% (Zally ২২.২%); ContentType P ৯৪.১% / R ৬৬.৭%; SingularNoun P ৭০% / R ৬৬.৭%, PluralNoun P ৯০.৯% / R ৫০% (Zally ১০০% recall কিন্তু বহু FP); **NoTunnel P ৬৭.৪% / R ৪৬.২%** (সর্বনিম্ন); VerbController — precision নমুনা অপর্যাপ্ত, R ৫০% (“present”, “permit” noun/verb দ্ব্যর্থতা) (p.8–10 L1340–1480)।

## I. Strengths
- **Evidence-to-tool pipeline:** Delphi (গুরুত্ব) → P026 (কার্যকারিতা) → RESTRuler (শনাক্তকরণ) — একই গবেষণাগোষ্ঠীর সুসংগত প্রোগ্রাম।
- Syntax-এর বাইরে semantic rule (NLP, ML) — industrial linter-এর gap পূরণ।
- বৃহৎ real-world benchmark (২,৩৩১) + expert-তৈরি adversarial gold standard — precision ও recall আলাদা উৎস থেকে সৎভাবে মাপা।
- Per-rule ব্যর্থতার বিস্তারিত কারণ; open-source ও Zenodo artifact।

## J. Explicit limitations (p.10 §VII; discussion)
- Precision labeling একজন ব্যক্তি প্রতি violation — subjective bias; expert violation OpenAPI-তে অনুবাদ করতে হয়েছে।
- External: APIs.guru-তে বড় কোম্পানির আধিক্য (AWS ৫.৭%, Google ১.৫%, Microsoft ০.৩%); মোট violation-এর মাত্র ০.৯৪% যাচাই; কিছু rule-এর recall খুব ছোট নমুনায়; expert edge case industrial প্রতিনিধিত্বশীল নাও হতে পারে; private API-তে সাধারণীকরণ সতর্ক।
- শুধু static analysis — runtime আচরণ নয় (সচেতন সিদ্ধান্ত)।
- বড় file-এ RAM সমস্যা; একই path-এ বহু violation (usability)।

## K. Inferred limitations (⚠️ অনুমান)
- **Recall নমুনা অত্যন্ত ছোট:** ১১১টি violation ১৪ rule-এ — NoTrailingSlash ২টি, VerbController ৪টি, RC401 ৬টি; ১০০%/৫০% ধরনের মান পরিসংখ্যানগতভাবে অস্থির; confidence interval নেই।
- **Benchmark-পরবর্তী “উন্নত” সংখ্যা (৭৫%, ১০০%)** একই gold standard-এ tuning — overfitting; স্বাধীন held-out মূল্যায়ন নেই।
- **Developer-স্তরের মূল্য অপরিমাপিত:** violation সত্যিই understandability বা defect কমায় কিনা, বা developer report-কে উপকারী মনে করে কিনা (industry case study future work)।
- **ContentType ও RC401 সর্বাধিক violation** — এগুলো design ত্রুটি না documentation অসম্পূর্ণতা? P015 লেখকদের যুক্তির মতো (schema fault অনেক, severity কম), noise হিসেবে কাজ করতে পারে; P026-এর effect size দিয়ে severity-weighting নেই।
- Precision নমুনায় per-file সর্বোচ্চ ৩০ violation — বড় API-র অতিরিক্ত ওজন সীমিত হলেও rule-ভেদে নমুনা অসম; NoTrailingSlash/VerbController precision নেই।
- NoTunnel ML model-এর ৮৯% accuracy নিজস্ব labeled data-য় — description-এর মানের উপর নির্ভরশীল (বাস্তব OpenAPI-তে description প্রায়ই অনুপস্থিত — P028-এর documentation smell-এর সঙ্গে সম্পর্ক)।
- LLM-ভিত্তিক semantic check (2024-এ সহজলভ্য) baseline হিসেবে পরীক্ষিত নয়।

## L. Threats to validity
- উপরে J; inferable: recall-এর ছোট নমুনা, tuning-on-test, construct (violation = quality সমস্যা?)।

## M. Reproducibility
- Tool (GitHub) ও evaluation artifact (Zenodo 10246326), APIs.guru public — **উচ্চ**।

## N. Opportunities (hypothesis)
- **LLM-assisted semantic design linting:** NoTunnel, ForwardSlash-hierarchy, VerbController, noun/verb দ্ব্যর্থতা — যেখানে dictionary/Naive Bayes দুর্বল; LLM বনাম RESTRuler precision/recall তুলনা (একই gold standard-এ) — সরাসরি, কম-infrastructure গবেষণা।
- **Severity-weighted linting:** P026-এর understandability effect size + violation prevalence দিয়ে অগ্রাধিকার; “অদৃশ্য” violation চিহ্নিত।
- **Design violation × testing/security outcome:** violation-যুক্ত API-তে fuzzing fault (T1) বা authorization ত্রুটি (T3) বেশি কিনা — ecosystem-স্তরের correlation study (APIs.guru)।
- **Design-rule compliance for MCP/tool descriptions** (P032, P036) — agent-বান্ধব API design rule তৈরি ও শনাক্তকরণ।
- **Evolution-aware linting:** version-জুড়ে violation-এর আবির্ভাব (T5 সংযোগ, P020-এর “API design degradation” ১৪/১৭-এর quantitative পরিমাপ)।

## O. Relationships
- **Direct successor of P026** (একই লেখক; P026-এর future work “tool-supported approaches”)।
- **Compares with** Zally, Spectral; **related to** SARA/SOFA (Palma et al.)।
- **Complements P028** (documentation smell — NL text quality) — RESTRuler design-স্তর।
- **Uses OpenAPI** — T4 (P017–P019) generated spec-এ চালানো যায়; spec না থাকলে প্রযোজ্য নয়।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract (১৪ rule, ২,৩০০+, ১১১, P৯১%/R৬৮%) | p.1 L15–42 |
| Motivation | p.1 L62–74 |
| Practitioner tools, Zally ৪/১৪ | p.2–3 L192–264 |
| Rule নির্বাচন প্রক্রিয়া | p.3 L275–291 |
| Development process | p.3 L293–305 |
| RQ1–RQ3 | p.3 L312–315 |
| Architecture, workflow | p.3–4 L319–446 |
| Table I (১৪ rule) | p.5 L454–540 |
| NLP, NoTunnel ML (৮৯%) | p.5–6 L546–633 |
| Dataset size category (Table II) | p.6 L635–649, L686 |
| Metrics, precision/recall পদ্ধতি | p.6–7 L657–875 |
| Expert gold standard | p.6 L724–744 |
| RQ1 robustness ৯৮.৭% | p.7 L928–933 |
| Violation বণ্টন ১৬৯,০৬১ | p.7 L886–904 |
| RQ2 performance (Table III) | p.7–8 L908–1004 |
| RQ3 overall (Table IV–V) | p.8 L1137–1146 |
| Per-rule আলোচনা | p.8–10 L1340–1480 |
| Static-only সিদ্ধান্ত | p.10 L1493–1498 |
| Threats | p.10 L1500–1541 |
| Conclusion | p.10 L1543–1566 |

**Document integrity:** দুই-কলামের reading order মিশ্রিত (RQ1 ফল RQ2-এর পরে, কিছু অনুচ্ছেদ খণ্ডিত); তিনটি spurious heading (“## 14 RESTful API”, “## 7 API experts” — Fig.1 থেকে); Table II–V column-split — per-rule সংখ্যা text আলোচনা থেকে; Fig.1–4 অনুপস্থিত।
