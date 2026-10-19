# P026 — Do RESTful API Design Rules Have an Impact on the Understandability of Web APIs?

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (related work §2.3 skim, appendix table বাদ, references বাদ) · **উৎস:** arXiv 2305.07346 / EMSE author version, ৪০ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Justus Bogner (University of Stuttgart), Sebastian Kotstein (Reutlingen University), Timo Pfaff (University of Stuttgart)
- **Venue:** Empirical Software Engineering 28, 2023, DOI 10.1007/s10664-023-10367-y
- **Cluster:** T6 (secondary: none)
- **ধরন:** Controlled online experiment (hybrid crossover/between-subjects)

## B. Motivation
- Web API-ই প্রায়ই developer-এর একমাত্র যোগাযোগবিন্দু — understandability গুরুত্বপূর্ণ quality attribute (p.1 L61–68)।
- বহু RESTful design rule (Massé ২০১১, Richardson & Ruby ২০০৭) আছে, কিন্তু **অধিকাংশের কার্যকারিতার empirical প্রমাণ নেই**; বাস্তব API-র ক্ষুদ্র অংশই RESTful (p.2–3 L79–106)।
- লেখকদের পূর্ববর্তী Delphi study: Massé-র ৮২টি নিয়মের মাত্র ৪৫টি উচ্চ/মাঝারি গুরুত্বপূর্ণ, maintainability ও usability-র সঙ্গে যুক্ত (p.3 L102–106)।

## C. Research questions (p.6–7 L251–284)
- RQ1 (confirmatory): কোন design rule understandability-তে significant প্রভাব রাখে?
- RQ2 (confirmatory + exploratory): কোন rule perceived difficulty-তে প্রভাব রাখে; actual ও perceived-এর সম্পর্ক?
- RQ3 (exploratory): demographic (experience, ভূমিকা, Richardson maturity model জ্ঞান) কি প্রভাব ফেলে?

## D. Contributions
- ১২টি RESTful design rule-এর understandability প্রভাবের প্রথম controlled experimental প্রমাণ; উন্মুক্ত উপকরণ (Zenodo 7381500)।

## E. Methodology
- **১২ rule, ৪ category (Table 2):** URI Design — PluralNoun, VerbController, CRUDNames; Hierarchy — PathHierarchy1 (path বনাম query param), PathHierarchy2 (top-down বনাম bottom-up), PathHierarchy3 (দীর্ঘ hierarchical বনাম ছোট path); Request Methods — NoTunnel, GETRetrieve, POSTCreate; Status Codes — NoRC200Error, RC401, RC415 (p.8–12 L341–651)।
- প্রতিটি rule-এর জন্য rule ও violation সংস্করণের OpenAPI snippet (Swagger editor screenshot), APIs.guru-র বাস্তব উদাহরণ থেকে সরলীকৃত; pilot-এ বিশেষজ্ঞ দিয়ে “অতিরঞ্জিত নয়” যাচাই, একটি task বাদ (p.8 L353–359; p.12 L652–667)।
- **Task:** প্রতি snippet-এ ৫-বিকল্পের single-choice প্রশ্ন (return value / endpoint purpose / response code reason) + ৫-বিন্দু perceived difficulty (p.14–15 L700–736)।
- **Measure:** **TAU (Timed Actual Understandability)** — ভুল = ০, সঠিক = ১ − (সময়/সর্বোচ্চ সময়) (Scalabrino et al.) (p.15 L739–773)।
- **Design:** দুটি counterbalanced sequence, প্রতিজন ৬টি rule + ৬টি violation; প্রতিটি task-এর প্রতিটি সংস্করণ অর্ধেক অংশগ্রহণকারী দেখে (p.16–17 L822–934)।
- **Execution:** LimeSurvey, ~৩ সপ্তাহ, ১০–১৫ মিনিট; convenience + referral sampling, social media (p.7–8 L320–338; p.17–19 L937–999)।
- **Cleaning:** ৪৮টি অসম্পূর্ণ বাদ; <৫ s বা >৩ min (status-code প্রশ্নে ১০ s/৪ min) উত্তর বাদ; ২টি পূর্ণ response ও ১২টি উত্তর বাদ (p.19–20 L1004–1034)।
- **Analysis:** Shapiro-Wilk → non-normal → **Wilcoxon-Mann-Whitney + Holm-Bonferroni**, Cohen's d; RQ3-এ Kendall's τ ও linear regression (p.20–21 L1096–1136)।

## F. Dataset
- **১০৫ জন** (৫৯ industry ৫৬%, ১৮ academia ১৭%, ২৮ student ২৭%); REST experience ১–১৫ বছর (median ৪); ৬৭% জার্মানি; মাত্র ২৮ জন (২৭%) Richardson maturity model জানে — তাদের ৭৯% Level 2-কেই RESTful-এর ন্যূনতম মনে করে (p.21–22 L1141–1233)।

## G. Evaluation
- Correctness, duration, TAU, perceived difficulty; hypothesis test per rule।

## H. Results (author-reported)
- **RQ1:** **১২-এর ১১টি rule-এ violation significantly খারাপ** (PathHierarchy3 ব্যতিক্রম — violation `POST /servers` ভালো করেছে: ৯৬% বনাম ৮৩% সঠিক); Cohen's d ০.২৪–২.১৭; ৬টি rule-এ d > ১.০ — **CRUDNames d = ২.১৭** (৯৬% বনাম ৩৮% সঠিক), GETRetrieve (১০০% বনাম ৬০%), NoRC200Error (৯৮% বনাম ৫৮%, d = ১.২৫), POSTCreate, PathHierarchy2, PathHierarchy1; ছোট effect: NoTunnel, RC401, RC415; কিছু ক্ষেত্রে correctness সমান কিন্তু সময় বেশি (PluralNoun ২০.৮২ s বনাম ৩২.২৩ s) (p.24–26 L1500–1737)।
- **RQ2:** ৯/১২ rule-এ violation significantly বেশি কঠিন অনুভূত (ব্যতিক্রম PathHierarchy3, RC415, **VerbController**); d ০.৭৯–২.০৬ (PathHierarchy2 সর্বোচ্চ); **৯টি task-এ TAU ও perceived difficulty-র মধ্যে কোনো significant negative correlation নেই** — CRUDNames, PathHierarchy2, POSTCreate-এর মতো ক্ষতিকর violation অংশগ্রহণকারীরা ভুল বোঝে অথচ টের পায় না → “বিশেষভাবে বিপজ্জনক” (p.27–30 L1749–2164)।
- **RQ3:** কোনো শক্তিশালী সম্পর্ক নেই; REST experience rule-এ সামান্য ভালো performance-এর সঙ্গে যুক্ত (τ = ০.১৯৬) কিন্তু violation-এ নয় — **অভিজ্ঞতা violation-এর ক্ষতি পূরণ করে না**; RMM-জ্ঞান violation-কে বেশি কঠিন রেট করার সঙ্গে যুক্ত (τ = ০.৩০৪) (p.30–31 L2166–2215)।

## I. Strengths
- **Rigorous experimental design:** pre-registered-ধাঁচের hypothesis, counterbalancing, pilot, multiple-comparison correction, effect size — SE experiment-এ বড় নমুনা (১০৫ বনাম median ৩৪)।
- Actual বনাম perceived understandability পার্থক্য — “অদৃশ্য ক্ষতিকর violation”-এর গুরুত্বপূর্ণ ধারণা।
- উপকরণ ও R script উন্মুক্ত — replication সম্ভব।
- Threats-এ সৎ আলোচনা (mono-operation bias, learning effect)।

## J. Explicit limitations (p.31–33 §5)
- Construct: TAU-এর binary correctness-time trade-off আদর্শ নয়; **mono-operation bias** — প্রতিটি rule-এর একটি মাত্র উদাহরণ, rule সমন্বয় পরীক্ষিত নয়।
- Internal: learning effect সম্ভব (task কাঠামো একই); online setting-এ নিয়ন্ত্রণ কম; একাধিকবার অংশগ্রহণ প্রতিরোধ নেই।
- External: প্রতিটি সংস্করণ অর্ধেক নমুনা; ৬৭% জার্মানি; **কৃত্রিম setting** — documentation বা চলমান API ছাড়া শুধু snippet।
- Future work: replication, অন্য violation/rule, **স্বয়ংক্রিয় violation শনাক্তকারী tool** (→ P027 RESTRuler)।

## K. Inferred limitations (⚠️ অনুমান)
- **প্রতি rule একটি উদাহরণ = rule নয়, উদাহরণের প্রভাব:** PathHierarchy3-এর ফল দেখায় উদাহরণ-নির্বাচন (path দৈর্ঘ্য, বিকল্পের শব্দচয়ন) ফলাফল নির্ধারণ করতে পারে — অন্য rule-এর বড় effect-ও আংশিক উদাহরণ-artifact হতে পারে (যেমন CRUDNames violation-এ `GET …/delete-queue/…` — দুটি rule একসঙ্গে ভাঙা)।
- **Answer option ডিজাইন সংস্করণ-নিরপেক্ষ কিনা:** একই ৫টি বিকল্প দুই সংস্করণে — violation-এ কিছু বিকল্প শব্দগতভাবে অপ্রাসঙ্গিক হয়ে সহজ হতে পারে (PathHierarchy3-এ লেখকরা নিজেই উল্লেখ করেন)।
- **Understandability-র সংকীর্ণ সংজ্ঞা:** first-contact snippet comprehension; প্রকৃত integration task (code লেখা, error handling) বা দীর্ঘমেয়াদি ব্যবহার নয়।
- Sampling: convenience/referral, লেখকদের নেটওয়ার্ক — REST-সচেতন নমুনা; ৪৮টি অসম্পূর্ণ response বাদ — attrition bias সম্ভব।
- **LLM consumer অনুপস্থিত:** ২০২৩-এ LLM agent/code generator API-র বড় “পাঠক” — একই rule LLM-এর বোঝায় প্রভাব ফেলে কিনা পরীক্ষিত নয় (গবেষণা-সুযোগ)।

## L. Threats to validity
- উপরে J (Wohlin কাঠামো, বিস্তারিত); inferable: stimulus sampling bias।

## M. Reproducibility
- Zenodo-তে উপকরণ, data, R analysis script — **উচ্চ**।

## N. Opportunities (hypothesis)
- **LLM-as-API-consumer understandability experiment:** একই ১২ rule-এর rule/violation snippet LLM-কে দিয়ে comprehension ও tool-call সঠিকতা — P033/P034/P035-এর tool-use ব্যর্থতার একটি design-স্তরের ব্যাখ্যা; MCP tool description design (P032, P036) নির্দেশিকা।
- **Stimulus-variation replication:** প্রতি rule-এ একাধিক উদাহরণ (multi-item) — rule-effect বনাম item-effect পৃথক করা।
- **Rule violation prevalence × understandability-weighted linting:** P027-এর detector-কে এই effect size দিয়ে অগ্রাধিকার দেওয়া (CRUDNames, GETRetrieve, NoRC200Error সর্বোচ্চ)।
- “অদৃশ্য violation” (low TAU, low perceived difficulty) — API review tool-এ বিশেষ সতর্কতা।
- Documentation-এর প্রশমন ক্ষমতা পরিমাপ (লেখকদের দাবি “partly mitigate” — পরীক্ষাযোগ্য; P028-এর documentation smell-এর সঙ্গে)।

## O. Relationships
- **Motivates P027 (RESTRuler)** — একই লেখকগোষ্ঠী, স্বয়ংক্রিয় violation শনাক্তকরণ।
- **Complements P028** (documentation smell) — design বনাম documentation-স্তরের understandability।
- **Relates to P020** — API usability/design degradation (১৪/১৭) practitioner সমস্যা; এখানে design rule-এর মূল্য প্রমাণিত।
- **Relates to P015** — status code-এর সঠিক ব্যবহার (401/403/404) নিরাপত্তা ও বোধগম্যতা উভয় ক্ষেত্রে গুরুত্বপূর্ণ।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract (১০৫ জন, ১১/১২, ৯/১২) | p.1–2 L18–51 |
| Delphi study (৪৫/৮২) | p.3 L102–106 |
| Richardson maturity model | p.4 L149–161 |
| RQ1–RQ3 | p.6–7 L251–284 |
| Table 1 overview | p.7 L287–317 |
| Sampling | p.7–8 L320–338 |
| ১২ rule ও উদাহরণ | p.8–12 L341–651 |
| Task ও প্রশ্নের ধরন | p.14–15 L700–736 |
| TAU সংজ্ঞা | p.15 L739–773 |
| Hypotheses (Table 3) | p.16 L783–818 |
| Experiment design (Table 4) | p.16–17 L822–934 |
| Data cleaning | p.19–20 L1001–1034 |
| Statistical analysis | p.20–21 L1096–1136 |
| Demographics | p.21–22 L1141–1233 |
| RQ1 ফল, effect size | p.24–26 L1500–1737 |
| RQ2 ফল, correlation | p.27–30 L1749–2164 |
| RQ3 ফল | p.30–31 L2166–2215 |
| Threats | p.31–33 L2217–2306 |
| Conclusion | p.33–34 L2309–2343 |

**Document integrity:** Body সম্পূর্ণ; TAU সূত্র হারিয়েছে (text-বর্ণনা আছে); Table 2, 4–7 column-split; Fig.1–14 অনুপস্থিত; appendix-এর বিস্তারিত statistical table (Table 8–13) পড়া হয়নি — মূল সংখ্যা text থেকে।
