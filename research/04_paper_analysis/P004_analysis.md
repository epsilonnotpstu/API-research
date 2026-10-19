# P004 — Automated Test Generation for REST APIs: No Time to Rest Yet

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references গণনা: ৮৭) · **উৎস:** arXiv 2204.08348v3 (৬ Jul 2022), ১৩ পৃষ্ঠা — ISSTA 2022 camera-ready-এর সমতুল্য ফরম্যাট · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Myeongsoo Kim, Qi Xin, Saurabh Sinha, Alessandro Orso (Georgia Tech; Wuhan University; IBM Research)
- **Venue:** ISSTA 2022, DOI 10.1145/3533767.3534401
- **Cluster:** T1 (secondary: T4 spec mismatch)
- **ধরন:** Empirical tool comparison (independent — লেখকরা কোনো tool-এর নির্মাতা নন)

## B. Motivation
- Tool-গুলো ভিন্ন benchmark, setup, metric-এ মূল্যায়িত; benchmark ছোট বা closed-source; তুলনা বিচ্ছিন্ন (p.1 L68–75)।
- নিজেদের দাবি “first” (L76–82): academic + practitioner tool পদ্ধতিগতভাবে বাছাই; benchmark-এর code-বৈশিষ্ট্য বিশ্লেষণ; failure-এর গভীর বিশ্লেষণ; নির্দিষ্ট ভবিষ্যৎ দিক।

## C. Research questions (p.4 L545–549)
- **RQ1:** কত code coverage? **RQ2:** কত error response (500)? **RQ3:** ফলাফলের implication কী?

## D. Contributions (p.2 L152–160)
- ১০টি tool × ২০টি service-এর বিস্তৃত তুলনা; strengths/weaknesses ও future research implication; replication artifact (Zenodo [45])।
- **Proof-of-concept:** (১) parameter description থেকে suggested value (OCVN ও Languagetool-এ ২,৯২৩টি parameter-এর ৯৩৪টি = ৩২%); (২) NLP dependency parsing দিয়ে ১২টি inter-parameter dependency-এর ৮টি শনাক্ত; (৩) NLTK name-similarity দিয়ে producer–consumer dependency-এর ~৮০% top-3-এ (p.8–9 L1089–1153)।

## E. Methodology
- **Tool নির্বাচন (p.3 L391–410):** ২০১১ থেকে top venue (ASE, CCS, FSE, ICSE, ISSTA, NDSS, S&P, TOSEM, TSE, USENIX, WWW, WSDM) keyword search + citation (শেষ search Dec 2021) → ১৯টি public tool (৮ research + ১১ practitioner) → কাজ করে এমন ১০টি: EvoMasterWB, EvoMasterBB, RESTler, RestTestGen, RESTest, Schemathesis, Dredd, Tcases, bBOXRT, APIFuzzer (Table 1 — technique, stateful কিনা, oracle, parameter generation, version)।
- **Benchmark নির্বাচন (p.5 L687–705):** পূর্ববর্তী benchmark (bBOXRT, EvoMaster, RESTest) থেকে ৩০ + GitHub top-120 থেকে ৪৯ = ৭৯ → OpenAPI নেই/compile হয় না/বেশিরভাগ external service-নির্ভর বাদ → **২০টি Java/Kotlin service** (Table 2: মোট ৯৭৭K LOC, Java/Kotlin ২০৭K, ৬৭৫ operation; OCVN ১৯২ op, ProxyPrint ১১৭)।
- **Setup (p.5 L782–809):** Google Cloud e2-standard-4 (৪ vCPU, 16GB); প্রতি tool ১ ঘণ্টা × ১০ trial + একবার ২৪ ঘণ্টা; ১০ মিনিট অন্তর data; JaCoCo coverage।
- **Fault metric (p.4 L553–573):** unique 500 error (stack trace দিয়ে group), unique failure point (stack-এর শীর্ষ method-line), unique library failure point।
- RESTest-এর জন্য লেখকরা নিজে inter-parameter dependency annotation লিখেছেন; EvoMasterWB-এর ১০টি driver নিজেরা লিখেছেন (p.10 L1330–1350)।

## F. Dataset
- ২০টি open-source Java/Kotlin RESTful service; spec GitHub repo থেকে; MySQL, MongoDB, private Ethereum network সেটআপ।

## G. Evaluation
- Line/branch/method coverage; 500 error/UFP/ULFP; Pearson correlation (coverage বনাম error)। ⚠️ Tool-জোড়া তুলনায় statistical significance test রিপোর্ট নেই (শুধু গড় ও box plot)।

## H. Results (author-reported; Table 3, p.5)
| Tool | Line | Branch | Method | 500 E/UFP/ULFP |
|---|---|---|---|---|
| EvoMasterWB | **52.76%** | **36.08%** | **52.86%** | **33.3**/6.4/3.2 |
| EvoMasterBB | 45.41 | 28.21 | 47.17 | 16.4/3.3/1.8 |
| Schemathesis | 43.01 | 25.29 | 43.65 | 14.2/2.8/2.0 |
| RestTestGen | 40.86 | 21.15 | 42.31 | 7.7/2/1 |
| bBOXRT | 40.23 | 22.20 | 42.48 | 9.5/2.1/1.3 |
| Tcases | 37.16 | 16.29 | 41.47 | 18.5/3.5/2.1 |
| Dredd | 36.04 | 13.80 | 40.59 | 6.9/1.5/0.9 |
| RESTler | 35.44 | 12.52 | 40.03 | 15.1/2.1/1.3 |
| RESTest | 33.86 | 18.26 | 33.99 | 7.2/1.9/1.1 |
| APIFuzzer | 32.19 | 18.63 | 33.77 | 6.9/2.2/1.3 |

- **কম coverage-এর তিন কারণ (p.6 L847–882):** (১) domain-specific/format-constrained parameter value তৈরি করতে না পারা (যেমন email-এ ‘@’); (২) producer–consumer dependency শনাক্ত না করা বা দুর্বল heuristic; (৩) **API ও spec-এর mismatch**।
- সহজ parameter-এর service-এ coverage সময়ের সঙ্গে বাড়ে; constrained parameter-এ দ্রুত “coverage wall” (p.7 L890–908)।
- Unique failure point error-এর চেয়ে ৩–৭ গুণ কম; প্রায় অর্ধেক failure point library-তে — library failure বেশি গুরুতর (যেমন ERC-20 service-এ Ethereum gas হারানো) (p.7 L931–972)।
- **Coverage–error correlation ~০.৭৮৮১ (Pearson)** (p.7 L973–981)।
- Parameter-combination বৈচিত্র্য (Tcases, Schemathesis) বেশি fault ধরে (p.7 L982–1022)।
- EvoMasterWB সর্বোচ্চ, কিন্তু producer–consumer dependency চিনতে না পারার উদাহরণে Schemathesis সফল (Figure 6) (p.9 L1217–1234)।
- **APIs.guru-র ১,০০০+ spec-এর ~৯৯%-এ mismatch** (Schemathesis দিয়ে যাচাই) (p.10 L1320–1329)।

## I. Strengths
- **স্বাধীন মূল্যায়ক** (tool-নির্মাতা নন) — P003-এর author-bias-এর বিপরীতে গুরুত্বপূর্ণ।
- Practitioner tool অন্তর্ভুক্ত; তিন স্তরের fault metric; ২৪ ঘণ্টার রান।
- Implication-গুলো proof-of-concept দিয়ে সমর্থিত — পরবর্তী NLP2REST, RESTGPT, LlamaRestTest (একই group)-এর ভিত্তি।

## J. Explicit limitations / threats (p.10 L1355–1350)
- ২০টি service সাধারণীকরণে সীমা; local deployment (private Ethereum); incomplete spec; RESTest-এর জন্য নিজেদের লেখা dependency annotation; নিজেদের লেখা EvoMaster driver।
- Future: mutation দিয়ে fault-detection মূল্যায়ন (p.11 L1454–1455)।

## K. Inferred limitations (⚠️ অনুমান)
- **500-error-কেন্দ্রিক fault metric:** spec-violation, semantic বা security fault গণনার বাইরে — P003 এই proxy-র সমালোচনা করে (log না থাকলে, non-crash fault)।
- **Statistical test নেই** tool-ranking-এ; গড়-ভিত্তিক র‍্যাংক ভঙ্গুর হতে পারে।
- **শুধু Java/Kotlin** — EvoMasterWB অন্তর্ভুক্ত করার জন্য; ভাষা-বৈচিত্র্য নেই।
- Proof-of-concept-গুলো ছোট (২টি service, ১২টি dependency) — feasibility, কার্যকারিতার প্রমাণ নয়।
- Tool version ২০২১–২২; পরবর্তী বহু উন্নয়ন।

## L. Threats to validity
- Stated: internal (implementation), external (benchmark), configuration।
- Inferable: construct (unique stack trace ≈ fault — অনুমান)।

## M. Reproducibility
- Zenodo artifact + companion website ✅; cloud machine ছোট (16GB) — পুনরুৎপাদন সহজ।

## N. Opportunities (hypothesis)
- **Spec-এর natural language থেকে value ও dependency extraction** — এই paper সরাসরি প্রস্তাব করে; P005/P007 (LLM) এটি বাস্তবায়ন করেছে।
- Symbolic execution white-box-এ gradient-হীন branch-এর জন্য।
- ML classifier দিয়ে producer–consumer dependency prediction।
- Mutation-ভিত্তিক fault-detection মূল্যায়ন (author-stated future work)।

## O. Relationships
- **Corroborated by P003:** একই black-box ranking (EvoMaster > Schemathesis > RestTestGen/bBOXRT > RESTler/RESTest) — দুটি দলের স্বাধীন মিল (তবে ১০টি service সাধারণ)।
- **Contradicts** Martin-Lopez et al. (ISSRE 2021; এই তালিকায় নেই) যেখানে RESTest > EvoMasterWB — লেখকদের ব্যাখ্যা: ছোট (৪টি) ও RESTest-এর নিজস্ব benchmark (p.11 L1384–1395)।
- **Supports P001:** spec mismatch-এর ব্যাপকতা (৯৯% বনাম ৬৩% F_OAS)।
- **Leads to:** P005 (LlamaRestTest), P007 (AutoRestTest) — একই group।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Motivation | p.1 L68–82 |
| Tool নির্বাচন | p.3 L391–410; Table 1 L272–376 |
| RQs | p.4 L545–549 |
| Fault metric সংজ্ঞা | p.4 L553–573 |
| Benchmark | p.5 Table 2 L574–669; L687–705 |
| Setup | p.5 L782–809 |
| Coverage ফল ও তিন কারণ | p.5 Table 3; p.6 L840–882 |
| Coverage over time | p.7 L890–908 |
| Error ফল, library failure | p.7 L912–972 |
| Correlation 0.7881 | p.7 L973–981 |
| Proof-of-concept (৩২%, ৮/১২, ~৮০%) | p.8–9 L1089–1153 |
| WB বনাম BB বিশ্লেষণ | p.9–10 L1164–1297 |
| ৯৯% spec mismatch | p.10 L1320–1329 |
| Threats | p.10 L1355–1350 |
| Related work বিরোধ | p.11 L1384–1395 |

**Document integrity:** Table 1–3 কলাম-ভাঙা কিন্তু পুনর্গঠনযোগ্য (উপরে Table 3 পুনর্গঠিত); Figure 2 (box plot) ও Figure 4 (dependency graph) অনুপস্থিত; section-ক্রম ঠিক আছে।
