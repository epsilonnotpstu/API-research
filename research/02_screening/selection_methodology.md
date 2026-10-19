# Selection Methodology — PHASE B3

**প্রস্তুতকারী:** Claude | **তারিখ:** 2026-10-19
**পুনরুৎপাদন:** `00_protocol/scripts/merge_match.py → merge_build.py → select_papers.py → final_build.py`; ইনপুট `screening_scores.json` (সব স্কোর ও override), আউটপুট `_selection.json`, `_sensitivity.json`

---

## 1. লক্ষ্য

১০৪টি যাচাইকৃত merged রেকর্ড থেকে ৩০–৪০টি (লক্ষ্য ≈৩৫) paper নির্বাচন, যাতে:
- প্রতিটি রক্ষিত research area-য় **cross-paper তুলনার মতো যথেষ্ট (≥২, পছন্দনীয় ≥৩) paper** থাকে;
- বেশিরভাগ সাম্প্রতিক (২০২৩–২০২৬), তবে অপরিহার্য foundational কাজ থাকে;
- পদ্ধতিগত বৈচিত্র্য (technique, empirical, controlled experiment, survey, benchmark/dataset) থাকে;
- একটি জনপ্রিয় ক্ষেত্র বা একটি research group প্রাধান্য না পায়;
- Full-text প্রাপ্যতা বিবেচিত হয় (PHASE C-তে বিশ্লেষণযোগ্যতা), কিন্তু একমাত্র নির্ধারক না হয়।

## 2. Cluster taxonomy (দুই agent-এর taxonomy মিলিয়ে)

| Code | Cluster | Claude PHASE A | Codex area |
|---|---|---|---|
| T1 | REST/Web API testing & fuzzing | T1 | API testing, automated testing, and fuzzing |
| T2 | GraphQL, RPC/gRPC & architecture styles | T2 | GraphQL and alternative API architectures |
| T3 | API security & authorization | T3 | API security and authorization |
| T4 | API specification inference & enrichment | T4 | API specification inference, generation, validation |
| T5 | API evolution, breaking changes & deprecation | T5 | API evolution and breaking changes |
| T6 | API documentation, design quality & governance | T6 | API documentation and usability |
| T7 | API misuse detection | T7 | (Codex-এ security-এর অধীনে) |
| T8 | LLM tool use, API calling & MCP | T8 | LLM- and AI-assisted API engineering |
| T9 | Microservice APIs, reliability & observability | T9 + T11 | Microservice reliability, testing, observability |
| T10 | API recommendation & composition | T10 | API discovery, recommendation, composition |

Codex-এর কিছু রেকর্ড বিষয়বস্তু অনুযায়ী পুনঃশ্রেণিবদ্ধ (যেমন GPTAid → T7, OOPS/RestPi/SpeCrawler → T4, LO2 → T9) — `merge_build.py`-এ `CODEX_T_OVERRIDE`।

## 3. Stage 1 — Eligibility (inclusion/exclusion criteria)

**Inclusion (সবগুলো পূরণ করতে হবে):**
1. Registrar-যাচাইকৃত পরিচয় (Crossref/DataCite; ICLR-এর ক্ষেত্রে official proceedings page)।
2. Software API-কেন্দ্রিক গবেষণা প্রশ্ন।
3. স্পষ্ট research contribution (technique + evaluation, empirical study, controlled experiment, systematic review, benchmark/dataset)।
4. অন্তত abstract-স্তরের প্রমাণ, যাতে contribution মূল্যায়ন করা যায়।

**Exclusion:**
- E1: শুধু metadata (abstract নেই) → contribution মূল্যায়ন অসম্ভব (M038, M090, M091, M097, M098, M100)।
- E2: Research contribution নয় (magazine column/essay) (M093)।
- E3: Retracted (পাওয়া যায়নি)।

ফল: ১০৪ → **৯৭ eligible**, ৭ ineligible (`excluded_papers.md` §ক)।

## 4. Stage 2 — Weighted scoring

| মানদণ্ড | ওজন | স্কেল ও সংজ্ঞা |
|---|---|---|
| **R** Relevance / API-কেন্দ্রিকতা | 0.25 | 5 = API engineering-এর কেন্দ্রীয় প্রশ্ন; 2 = API প্রান্তিক |
| **E** Evidence/rigor signal | 0.25 | abstract-এ মূল্যায়নের পরিধি (বাস্তব subject সংখ্যা, industrial data, controlled design), peer review, main-track বনাম workshop/demo/NIER/preprint |
| **V** Analytical value | 0.20 | open problem/limitation নথিভুক্ত, benchmark/dataset, tool comparison, survey, contradicting evidence — gap analysis-এ কতটা কাজে লাগবে |
| **T** Temporal role (auto) | 0.15 | ≥২০২৩ → 5; ২০২১–২২ → 3; ≤২০২০ → 2; foundational flag → 4 |
| **A** Full-text access (auto) | 0.15 | publisher/proceedings/repository/author PDF বা arXiv-only paper যাচাইকৃত → 5; বৈধ arXiv preprint (published paper-এর) → 4; যাচাই হয়নি → 2 |

**ইচ্ছাকৃতভাবে বাদ:** citation count (prompt-এর নির্দেশ: citation ≠ quality) — শুধু তথ্য হিসেবে `cited_by_openalex` কলামে।

**সতর্কতা:** R, E, V Claude-এর abstract-ভিত্তিক বিচার; এগুলো বৈজ্ঞানিক মানের প্রমাণ নয়। প্রতিটি স্কোর `screening_scores.json`-এ প্রকাশ্য, তাই supervisor চ্যালেঞ্জ করতে পারেন।

## 5. Stage 3 — Coverage-constrained selection

| Constraint | মান | যুক্তি |
|---|---|---|
| Cluster quota | T1 8, T2 3, T3 4, T4 4, **T5 6**, T6 3, T7 3, T8 5, **T9 2**, **T10 0** | T1 সাহিত্যে সবচেয়ে ঘন, তাই সর্বোচ্চ — কিন্তু মোটের ~২১%; প্রতিটি রক্ষিত cluster-এ তুলনাযোগ্য সংখ্যা |
| Research-group cap | প্রতি group ≤ 4 | PHASE A-তে দেখা ২৮% concentration (Arcuri/Zhang; Orso/Sinha) কমাতে |
| Preprint cap | ≤ 3 | Peer-reviewed প্রমাণকে অগ্রাধিকার |
| Greedy | স্কোর অনুযায়ী; tie-break E, তারপর V | স্বচ্ছতা |

**T10 (recommendation) বাদ কেন:** (ক) normalized publication volume আপেক্ষিকভাবে কমছে (`00_protocol/api_research_landscape.md` §1); (খ) Codex-এর ৫টির ৩টি ProgrammableWeb-ধরনের offline registry dataset, ২টি metadata-only; (গ) LLM-যুগে API নির্বাচন T8-এর tool retrieval-এ স্থানান্তরিত (M053, M025)। M064 (TSE benchmark) সর্বোচ্চ-স্কোরের বাদপড়া — PHASE D-তে প্রয়োজনে পুনর্বিবেচনা।

**T9-এ ২টি কেন:** তৃতীয় স্থানে আসত M102 (R=3; স্কোর 3.10 — সব নির্বাচিতের মধ্যে সর্বনিম্ন); সেই স্থান T5-এ M043-কে দেওয়া হয়েছে (নিচে)।

## 6. Documented manual overrides

| # | বাদ | যোগ | কারণ |
|---|---|---|---|
| O1 | M073 ARTE | **M003 AGORA** | Oracle problem (5xx-এর বাইরে semantic oracle) gap analysis-এর কেন্দ্রীয় (H3); input generation M009/M028-এ প্রতিনিধিত্ব পেয়েছে; AGORA দুই agent-ই বেছেছে; কম স্কোর মূলত access (A=2) থেকে |
| O2 | M041 Public REST APIs | **M017 Doc smells** | স্কোরিং-এর পর T6-এ কোনো documentation paper ছিল না; documentation prompt-এ নির্দিষ্ট area; M017 দুই agent-ই বেছেছে |
| O3 | (T9 quota 3→2) | **M043 Differential regression** (T5 quota 5→6) | Web/REST breaking-change *detection* technique একটিও ছিল না; M043 একমাত্র প্রধান কাজ |

Override ছাড়া selection-এর সঙ্গে overlap: ৩৬/৩৮ (§৮)।

## 7. ফলাফলের প্রোফাইল (৩৮টি)

| বৈশিষ্ট্য | মান |
|---|---|
| Cluster | T1 8 · T2 3 · T3 4 · T4 4 · T5 6 · T6 3 · T7 3 · T8 5 · T9 2 |
| বছর | 2018: 1 · 2019: 2 · 2020: 2 · 2021: 2 · 2022: 4 · 2023: 7 · 2024: 5 · 2025: 12 · 2026: 3 → **২৭/৩৮ (৭১%) ২০২৩–২০২৬** |
| Foundational | P006 RESTler, P010 GraphQL cost, P016 IDL, P021 API-evolution SLR, P025 Differential regression, P030 MUBench evaluation (+ P013 WARDroid ২০১৮ ও P028 ২০২১ পুরোনো-যুগের) |
| Paper ধরন | Survey/SLR/mapping ৫ (P002, P009, P021, P029, P038) · Tool-comparison empirical ২ (P003, P004) · Dataset ১ (P037) · Controlled experiment ১ (P026) · বাকি ২৯টি technique/empirical |
| Review status | Peer-reviewed ৩৭ · Preprint ১ (P032) |
| Provenance | Both ১৫ · Claude-only ১৯ · Codex-only ৪ |
| Group | Arcuri/Zhang ৪ · Orso/Sinha ৪ (cap) |
| Access | OA verified ১১ (publisher/proceedings/repository/author ৮ + arXiv-only/ICLR ৩) · Preprint OA ২১ · **Not verified ৬** |

## 8. Sensitivity analysis (`_sensitivity.json`)

| Scenario | ওজন (R,E,V,T,A) | Baseline-এর সঙ্গে overlap | পরিবর্তন |
|---|---|---|---|
| S0 baseline | .25,.25,.20,.15,.15 | 38/38 | — |
| S1 সমান ওজন | .2 ×5 | 36/38 | +M040, M044; −M043, M080 |
| S2 access বাদ | .30,.30,.25,.15,0 | 36/38 | +M035, M084; −M036, M047 |
| S3 rigor-ভারী | .20,.40,.20,.10,.10 | 36/38 | +M035; −M036, M047 |
| S4 recency-ভারী | .20,.20,.15,.35,.10 | 31/38 | foundational (M010, M012, M020, M043, M049, M075, M078) বাদ পড়ে, নতুন কাজ ঢোকে |
| S5 override ছাড়া | baseline | 36/38 | +M041, M073; −M003, M017 |

**ব্যাখ্যা:** বেশিরভাগ যুক্তিসঙ্গত ওজনে নির্বাচন স্থিতিশীল (৩৬/৩৮ ≈ ৯৫% overlap; S3-এ একটি স্থান group/preprint cap-এর কারণে খালি থাকে)। অস্থির “প্রান্তিক” paper: M036 (BOLA), M047 (RESTRuler), M080 (RestPi), M043 — এগুলোর বিপরীতে M035 (security checkers, ২০২০), M084 (directive defects, ২০১৭), M040 (OASBuilder) সমতুল্য বিকল্প। Recency-ভারী ওজন foundational কাজ বাদ দেয় — তাই foundational flag (T=4) ইচ্ছাকৃত।

## 9. Prompt-এর ভারসাম্য-চাহিদা কতটা পূরণ হলো

| চাহিদা | অবস্থা |
|---|---|
| Research importance | ✅ R/V স্কোর + দুই agent-এর ঐকমত্য (১৫টি Both) |
| Recent developments | ✅ ৭১% ২০২৩–২০২৬ |
| Foundational contributions | ✅ ৬টি স্পষ্ট foundational |
| Topic coverage | ✅ ৯টি cluster; ⚠️ T10 ইচ্ছাকৃতভাবে বাদ; API privacy/performance/event-driven API অনুপস্থিত (সাহিত্য-সীমাবদ্ধতা + search-সীমাবদ্ধতা) |
| Methodological diversity | ✅ technique, empirical, qualitative interview, controlled experiment, SLR, dataset, formal methods |
| Evaluation quality | ⚠️ abstract-ভিত্তিক অনুমান; PHASE C-তে যাচাই |
| Access to full text | ⚠️ ৩২/৩৮ verified (preprint সহ); ৬টি human/institutional access-নির্ভর |
| Research feasibility | ✅ small-LM (P005), spec inference (P016–P019), dataset (P037) — কম-infrastructure দিক অন্তর্ভুক্ত |
| Cross-paper analysis | ✅ প্রতি cluster ≥২; T1/T5/T8-এ ≥৫ |
| Fashionable area dominance | ✅ T8 (LLM/MCP) ৫টি (১৩%); T1 ৮টি (২১%) |

## 10. সীমাবদ্ধতা

- একক screener (Claude); Codex-এর স্বাধীন তালিকা আংশিক cross-check হিসেবে কাজ করেছে কিন্তু inter-rater scoring হয়নি।
- Abstract-ভিত্তিক E/V স্কোর full text পড়লে বদলাতে পারে।
- Group cap শুধু দুটি প্রভাবশালী group-এ প্রয়োগ; অন্য group-এ concentration (যেমন Seville: P001, P008, P009) সীমিত পর্যায়ে আছে।
- Quota-নির্ধারণ বিচারভিত্তিক; বিকল্প quota-য় ফল বদলাতে পারে।
