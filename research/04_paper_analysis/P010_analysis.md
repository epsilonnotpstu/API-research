# P010 — A Principled Approach to GraphQL Query Cost Analysis

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references বাদ) · **উৎস:** arXiv 2009.05632v1 (১১ Sep 2020), ১২ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Alan Cha, Erik Wittern, Guillaume Baudart, James C. Davis, Louis Mandel, Jim A. Laredo (IBM Research; IBM Germany; Purdue)
- **Venue:** ESEC/FSE 2020, DOI 10.1145/3368089.3409670
- **Cluster:** T2 (secondary: T3 — denial-of-service/rate limiting)
- **ধরন:** Formal static analysis + empirical evaluation + industrial transfer

## B. Motivation
- GraphQL-এর expressiveness provider-এর জন্য ঝুঁকিপূর্ণ: worst-case query exponential কাজ চাপায় (Hartig & Pérez) — DoS, pricing, execution cost (p.1 L90–96)।
- Wittern et al.-এর corpus-এ বাণিজ্যিক/বড় open-source schema-র **>৮০%** exponential worst-case; **<৪০%** linear গ্যারান্টি দেয় (p.2 L166–170)।
- APIs.guru-র ৩০টি public GraphQL API-র **২৫টি (৮৩%)** কোনো query analysis বর্ণনা করে না; ২২টি (৭৩%) rate-limit বা জটিল query প্রতিরোধের উল্লেখই করে না; ৩টি শুধু request-frequency rate limiting (p.2 L172–180)।
- Dynamic analysis সঠিক কিন্তু ব্যয়বহুল/backend-নির্ভর; বিদ্যমান static analysis GraphQL convention (pagination) সমর্থন করে না (p.1 L97–99)।

## C. Research questions (p.6 L734–741)
- RQ1 configuration-সহ বাস্তব API-তে প্রয়োগযোগ্য? RQ2 upper bound দেয়? RQ3 bound যথেষ্ট tight? RQ4 যথেষ্ট সস্তা? RQ5 অন্য পদ্ধতির তুলনায়?

## D. Contributions (p.1 L114–123)
- GraphQL semantics-এর নতুন compact formalization (context object সহ)।
- দুটি complexity metric — **resolve complexity** (server execution cost) ও **type complexity** (response size) — এবং linear-time static upper-bound analysis, correctness প্রমাণ (Theorem 1–2)।
- GitHub ও Yelp-এ মূল্যায়ন; বিদ্যমান analysis-এর over/under-estimation কারণ শনাক্ত।
- প্রথম GraphQL query-response corpus (১০,০০০ জোড়া)।

## E. Methodology
- **Formal semantics (Fig.3):** basic query, inline fragment, concatenation, nesting; resolver function দিয়ে storage-agnostic (p.3 L293–334)।
- **Pagination convention:** slicing (`first`, `limit`) ও connections pattern (Edge/Connection); GraphQL spec-এ নেই বলে **configuration** দিয়ে ধরা: `limitArguments`, `limitedFields`, `defaultLimit`, `resolverWeight`, `typeWeight`; regex/wildcard সমর্থন (p.4–5 L461–568)।
- **Assumption 1–2:** resolver limit argument বা default limit মেনে চলে — না মানলে backend bug (p.5 L494–503, L549–552)।
- **Analysis (Fig.4):** query structure-এর উপর inductive weighted recursive sum; list-এ `l × child`; O(n) সময় ও স্থান (p.5–6 L585–709)।
- Mutation-এ resolve complexity প্রযোজ্য; type complexity পরিবর্তিত data ধরে না — future work; subscription-এর জন্য rate-limit নীতি প্রস্তাব (p.6 L713–727)।

## F. Dataset ও setup
- **Corpus:** নিজস্ব grammar-based random query generator (depth/breadth probability ০.৫; numeric argument normal distribution); GitHub ও Yelp প্রতিটিতে ৫,০০০ unique query-response, এপ্রিল ২০১৯–মার্চ ২০২০ (p.7 L797–825)।
- **নৈতিক সীমা:** complexity ≤১,০০০, depth ≤১০, শুধু query (mutation/subscription নয়) (L821–825)।
- “Typical” query: GitHub-এর ১৪টি documentation example-এর একটি ছাড়া সবার type complexity ≤৩০২ → ≤৩০০ সংজ্ঞা (L826–836)।
- Schema: GitHub ২৪৫ object type/১,৫৬৯ field/২২,০৭১ LoC; Yelp ২৫/১২১/৭৬০; configuration GitHub ৫০ LoC (০.২%), Yelp ৩৯ (৫.১%) (Table 1, p.7 L754–786)।
- Weight: W1,0 (object=১, বাকি=০)।

## G. Evaluation
- Heat map (predicted vs actual); over-estimation শতাংশ (<২৫%, <৫০%); runtime (2017 MacBook Pro)।
- Baselines: তিনটি open-source library (libA, libB, libC — GitHub-এ ≥১০ star) পরীক্ষামূলকভাবে; GitHub ও Yelp-এর closed-source analysis গুণগতভাবে।

## H. Results (author-reported)
- **RQ1:** উভয় API সহজে configure করা গেছে; default limit — GitHub ২১, Yelp ১৩ field (p.7 L845–866)।
- **RQ2:** সব query-র prediction actual-এর সমান বা বেশি — **কোনো under-estimation নেই** (p.7 L877–879)।
- **RQ3:** অনেক query diagonal-এর কাছাকাছি; বড় query-তে looser — কারণ data sparsity; “typical” query-তে over-estimation কম (Table 2, p.8 L1087–1094)। GitHub type complexity-তে **৮৪%** prediction <৫০% over-estimate; **median error ১৯%** বনাম libA **৬৩৪%**; 90th percentile ৬৬.০% বনাম ১৪,৫৬৮.২% (p.9 L1291–1297)।
- **RQ4:** median ৩.০ ms (query), ১.১ ms (response); 95% < ৭.৩ ms ও < ৪ ms (p.8 L1102–1105)।
- **RQ5:** libA argument-কে limit হিসেবে নিতে পারে না → ৮১.২% prediction actual-এর দ্বিগুণের বেশি; **libB/libC-র ~৬৪% prediction under-estimation** — নিরাপত্তা-সংকটপূর্ণ প্রেক্ষাপটে অগ্রহণযোগ্য (p.9 L1284–1309); কোনো library BQ2 (resolver সংখ্যা) উত্তর দিতে পারে না (L1310–1317)।
- **বাস্তব প্রভাব:** GitHub-এর analysis unpaginated list ভুলভাবে ধরত — exponential query গৃহীত হয়ে timeout; রিপোর্ট করার পর **GitHub patch করেছে** (p.2 L131–138; p.10 L1337–1342)। Yelp-এর `reviews` resolver limit argument উপেক্ষা করে — **Yelp bug নিশ্চিত করেছে** (p.10 L1405–1410)। Yelp-এর dynamic rate limit অল্প quota-তে জটিল query দিয়ে অতিক্রম করা যায় (L1343–1352)।
- **Industrial transfer:** IBM API Connect ও DataPower v10.0.0-এ GraphQL gateway; schema introspection + GUI + স্বয়ংক্রিয় configuration সুপারিশ (p.10–11 L1423–1447)।

## I. Strengths
- **Soundness প্রমাণ** (upper bound guarantee) — নিরাপত্তা প্রেক্ষাপটে under-estimation-এর অনুপস্থিতি মূল সুবিধা।
- Formal ও data-driven (pagination convention) মিশ্রণ — তত্ত্ব ও অনুশীলনের সংযোগ।
- বাস্তব vulnerability disclosure (GitHub) ও bug (Yelp) — বহিঃস্থ বৈধতা।
- প্রথম query-response corpus প্রকাশিত (Zenodo); product-এ অন্তর্ভুক্ত।
- নৈতিক বিবেচনা (public API-তে ক্ষতিকর query এড়ানো) স্পষ্ট।

## J. Explicit limitations (p.10–11 L1451–1481; L1437)
- **Internal:** configuration ত্রুটি over-estimation ঘটাতে পারে; random query-র realism — জনপ্রিয় project-এ data বেশি, অন্যগুলো “unnatural”; ক্ষতি এড়াতে complexity সীমিত করায় query বাস্তবের চেয়ে ছোট হতে পারে।
- **External:** slicing argument, resolver-এ limit enforcement ও সঠিক configuration-এর উপর নির্ভরতা — সব provider-এ সত্য নাও হতে পারে।
- **Configuration-এর প্রয়োজন** দুর্বলতা (L1437)।
- Mutation-এর type complexity future work; hybrid static/dynamic নকশা future work (L1379–1381)।
- **Analysis prototype শেয়ার করা যায়নি** (institutional policy) (L1504)।

## K. Inferred limitations (⚠️ অনুমান)
- **Construct validity দাবি অতিরিক্ত আশাবাদী:** লেখকরা বলেন “কোনো উল্লেখযোগ্য threat নেই”, কিন্তু W1,0 weight প্রকৃত server cost (CPU/DB time) প্রতিফলিত করে না — resolve complexity ও প্রকৃত latency-র সম্পর্ক কখনো পরিমাপ করা হয়নি।
- মাত্র দুটি API (দুটিই বড় বাণিজ্যিক); ছোট/self-hosted GraphQL server-এ, যেখানে resolver limit মানা হয় না (Yelp-ই ভঙ্গ করেছে), Assumption 1 ভঙ্গ হলে soundness হারায়।
- **Corpus synthetic** (random generator) — বাস্তব client traffic বা attacker query নয়।
- **Prototype বন্ধ** → মূল ফল স্বাধীনভাবে পুনরুৎপাদন অসম্ভব; শুধু corpus ও library configuration উন্মুক্ত।
- Table 2-এর কলাম-বিন্যাস markdown-এ ভেঙেছে — কোন শতাংশ কোন (API, metric)-এর তা PDF-এ যাচাই প্রয়োজন (text-এর ৮৪% দাবি নিশ্চিত)।
- Persisted queries, batching, aliases-ভিত্তিক amplification ইত্যাদি আধুনিক GraphQL attack vector আলোচিত নয়।

## L. Threats to validity
- উপরে J; inferable: construct (weight বনাম প্রকৃত cost), external (দুটি API)।

## M. Reproducibility
- Zenodo artifact: query generator, corpus, library configuration, measurement [L1503–1504]। **Analysis prototype নেই** — পুনরুৎপাদন আংশিক। Public API পরিবর্তিত হওয়ায় (GitHub patch) একই ফল পাওয়া যাবে না।

## N. Opportunities (hypothesis)
- **Learned/hybrid cost model:** static upper bound + runtime data statistics (লেখকদের future work) — ML দিয়ে tighter bound, soundness বজায় রেখে।
- **Automatic configuration inference:** schema naming + introspection + LLM দিয়ে limit argument/default limit অনুমান (IBM GUI-র সুপারিশ এর প্রাথমিক রূপ) — T4 (spec inference)-এর সঙ্গে মিল।
- **Resolver limit enforcement testing:** Assumption 1 ভঙ্গ (Yelp bug) স্বয়ংক্রিয়ভাবে খুঁজতে fuzzing — T1/T2 সংযোগ; একটি নতুন oracle শ্রেণি।
- Mutation/subscription cost; persisted-query ও batching attack।
- Cost-aware GraphQL test generation (P011/EvoMaster GraphQL-এ ব্যয়বহুল query নিয়ন্ত্রণ)।
- REST-এর জন্যও অনুরূপ “response size/cost bound” (pagination parameter-ভিত্তিক) — rate-limit ও LLM agent tool-call খরচ (T8)-এর সঙ্গে সংযোগ।

## O. Relationships
- **Builds on:** Hartig & Pérez (GraphQL semantics), Wittern et al. (schema corpus — P009-এর S10)।
- **Addresses P009-এর** “security/DoS” limitation ও roadmap (ii) ও (iv) (pricing)।
- **Contrasts with** libA/B/C ও GitHub/Yelp-এর ad hoc পদ্ধতি।
- **Links T3** (DoS), **T6** (API management/governance)।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Exponential query ঝুঁকি | p.1 L90–96 |
| APIs.guru ৩০ API সমীক্ষা (৮৩%, ৭৩%) | p.2 L172–186 |
| >৮০% exponential schema | p.2 L166–170 |
| Formal semantics | p.3–4 L293–422 |
| Pagination config, Assumption 1–2 | p.4–5 L461–568 |
| Resolve/type complexity, Theorem 1–2 | p.5–6 L585–694 |
| O(n) | p.6 L696–709 |
| Mutation/subscription | p.6 L713–727 |
| RQ1–RQ5 | p.6 L734–741 |
| Corpus | p.7 L797–836 |
| Table 1 | p.7 L754–786 |
| RQ2–RQ4 | p.7–8 L870–1105 |
| Table 2 | p.8 L1017–1085 |
| RQ5 library তুলনা | p.9 L1243–1317 |
| GitHub/Yelp disclosure | p.2 L131–138; p.10 L1326–1352, L1405–1410 |
| IBM gateway | p.10–11 L1423–1447 |
| Threats | p.11 L1451–1481 |
| Prototype শেয়ার নয় | p.11 L1504 |

**Document integrity:** Body সম্পূর্ণ; formal rule (Fig.3, Fig.4) ও semantics bracket (⟦⟧ → “J…K”) আংশিক ভাঙা কিন্তু অর্থবোধ্য; Fig.5–6 heat map-এর axis সংখ্যা বিচ্ছিন্ন; **Table 2 কলাম-বিন্যাস হারিয়েছে** — নির্দিষ্ট শতাংশ PDF-এ যাচাই করতে হবে।
