# P035 — On Mitigating Code LLM Hallucinations with API Documentation (CloudAPIBench)

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (related work বাদ; appendix-এর construction বিবরণ দেখা হয়নি; references বাদ) · **উৎস:** arXiv 2407.09726 / ICSE-SEIP 2025 version, ১৮ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Nihal Jain, Robert Kwiatkowski, Baishakhi Ray, Murali Krishna Ramanathan, Varun Kumar (Amazon Web Services)
- **Venue:** ICSE-SEIP 2025, DOI 10.1109/icse-seip66354.2025.00027
- **Cluster:** T8 (secondary: T6 — documentation-এর কোন অংশ উপকারী; T7 — API hallucination/misuse; T5 — নতুন/আপডেট API)
- **ধরন:** Benchmark + RAG (documentation-augmented generation) ablation + selective retrieval পদ্ধতি

## B. Motivation
- Code LLM **low-frequency API** (প্রশিক্ষণে কম দেখা — নতুন, আপডেট, বিরল) hallucinate করে; API-র ধ্রুবক evolution সমস্যা বাড়ায় (p.1 L25–29)।
- StarCoder2-15B-এর perplexity high-frequency API-তে কম, low-frequency-তে বেশি (Fig.1) (p.1–2 L51–56, L125–138)।
- API hallucination state-of-the-art Code LLM-এর সব hallucination-এর সর্বোচ্চ ১৫%; hallucinated call snowball করে ও security vulnerability আনতে পারে (p.2 L158–173)।

## C. Research questions
- ⚠️ আনুষ্ঠানিক RQ নেই; পরীক্ষিত: (১) Code LLM API frequency অনুযায়ী কতটা hallucinate করে; (২) DAG-এর কোন উপাদান (augmentation design, retriever precision, retrieval সংখ্যা) প্রভাব ফেলে; (৩) selective retrieval (index lookup, confidence) DAG-এর ক্ষতি কমায় কিনা।

## D. Contributions (p.2 L175–184)
- **CloudAPIBench** — AWS ও Azure SDK API invocation-এর benchmark, The Stack v2-ভিত্তিক API frequency annotation সহ।
- **DAG (Documentation Augmented Generation)**-এর পূর্ণাঙ্গ ablation।
- DAG কোথায় ক্ষতি করে তার বৈশিষ্ট্যায়ন ও **selective retrieval (DAG++)**।

## E. Methodology
- **CloudAPIBench:** **৬২২টি synthetic Python task** (data leakage এড়াতে), প্রতিটিতে একটি নির্দিষ্ট cloud API invocation; prompt = import + variable declaration + developer-style comment, invocation-এর ঠিক আগে থামে; comment **Claude 3 Sonnet** দিয়ে API description থেকে তৈরি (p.3 L239–277)।
- **Frequency:** The Stack v2-এ একই নামের function definition/call গণনা — Low (০–১০), Medium (১১–১০০), High (≥১০১) (p.3 L250–265)।
- **Metric — Valid API invocation:** official documentation থেকে API stub (signature, required/optional argument) তৈরি; candidate call stub-এ **bind** হলে valid — static analysis বা string matching-এর চেয়ে robust বলে দাবি (p.3 L278–287)।
- **Models:** StarCoder2-{৩,৭,১৫}B, CodeGemma-{২,৭}B, Granite-Code-{৩,৮,২০}B, **GPT-4o**; greedy, ২৫৬ token, প্রথম function call পর্যন্ত (p.4 L415–424)।
- **DAG pipeline:** model প্রথমে hypothetical invocation দেয় → সেটিকে query করে BM25 দিয়ে documentation retrieve → prompt-এর আগে docstring হিসেবে যোগ → পুনরায় generate; **configurable-precision retriever** (x% ক্ষেত্রে target doc অন্তর্ভুক্ত) (p.4–5 L456–499)।
- **Augmentation design:** name only, description, specification, description+specification, full documentation (p.5 L492–499)।
- **Selective retrieval:** (১) **Index lookup** — প্রথম invocation-এর API নাম index-এ না থাকলে DAG; (২) **API invocation confidence** — API নাম token-এর সর্বনিম্ন probability threshold-এর নিচে হলে DAG; **DAG++** = দুটির OR (threshold ০.৮) (p.6–8 L703–1081)।

## F. Dataset
- উপরে E।

## G. Evaluation
- Valid API invocation % (frequency group অনুযায়ী), retrieval trigger rate, token খরচ; ablation-এ StarCoder2-3B, retriever precision ৫০%।

## H. Results (author-reported)
- **সব model hallucinate করে;** ধরন — অস্তিত্বহীন API, target API-র ভুল ব্যবহার, ভুল বিদ্যমান API; frequency-র সঙ্গে শক্তিশালী সম্পর্ক; **GPT-4o low-frequency-তে মাত্র ৩৮.৫৮% valid** (p.1 L62–63; p.4 L429–438)।
- **Augmentation:** name/description প্রায় অকার্যকর; **API Specification যোগে ৪১.৮০% → ৮৬.৮২%** (গড়); full documentation সেরা কিন্তু ৬৮৫.২৪ token/augmentation; description + specification সর্বোত্তম ভারসাম্য (p.5 L511–524)।
- **Retriever precision:** low-frequency API কম precision-এও উপকৃত; **high-frequency API-তে base model-এর সমান হতে >৮০% precision লাগে**; ৫০% precision-এ high-frequency ৮৪.৩৯% → ৬৭.৩২% (p.6 L693–697)।
- **Retrieval সংখ্যা:** high-frequency-তে একটি retrieval-এ তীব্র পতন, দুই বা ততোধিকে আংশিক পুনরুদ্ধার (p.6 L717–724)।
- **Index lookup:** high-frequency regression কমায় (base-এর সামান্য ওপরে), কিন্তু low-frequency-তে সামান্য regression (বিদ্যমান-কিন্তু-ভুল API চেনে না) (p.7 L712–769)।
- **Confidence:** API invocation confidence বিভিন্ন model-এ well-calibrated; StarCoder2-3B-এ সর্বোত্তম threshold ~০.৭–০.৮ (p.7 L778–829)।
- **DAG++ (Table 3):** GPT-4o-তে DAG high-frequency-তে **−৩৯.০২%** পতন ঘটায়; DAG++ তা প্রশমিত করে low-frequency লাভ রাখে; GPT-4o-তে DAG++ high-frequency-তে মাত্র **৩.৪১%** ক্ষেত্রে, low-frequency-তে **৫০.৫৬%** ক্ষেত্রে retrieve করে; CloudAPIBench-এ **+৮.২০% absolute** (GPT-4o); বড় model কম retrieval চায় (p.8 L1062–1106; p.1 L72)।

## I. Strengths
- **Frequency-stratified মূল্যায়ন** — “long tail” API সমস্যার পরিমাণগত প্রমাণ; pre-training corpus-স্তরের বিশ্লেষণ।
- **Documentation-এর কোন অংশ** কাজের তা পৃথক করা — T6 (documentation design)-এর জন্য সরাসরি শিক্ষা: **specification (signature) ছাড়া NL description প্রায় অর্থহীন LLM-এর জন্য**।
- RAG-এর ক্ষতিকর দিক (irrelevant context) প্রদর্শন ও সরল, ব্যবহারিক প্রতিকার।
- Industrial (AWS) প্রেক্ষাপট; multi-family model।

## J. Explicit limitations (p.9 Limitations)
- Python-only, ছোট synthetic prompt — সব বাস্তব cloud API invocation প্রতিনিধিত্ব নাও করতে পারে।
- Construction heuristic-নির্ভর (frequency estimation-এর customized logic)।
- Iterative generate-retrieve-regenerate — latency-sensitive setting-এ অনুপযুক্ত।
- Generated code মানব review ও sandbox প্রয়োজন।

## K. Inferred limitations (⚠️ অনুমান)
- **“Valid invocation” = stub binding** — শুধু argument নাম/সংখ্যা/required-ness; **argument মানের সঠিকতা, সঠিক API নির্বাচন (task semantics), বা execution সাফল্য** মাপা হয় না। একটি ভুল-কিন্তু-বিদ্যমান API যার signature মেলে — তা প্রশ্নের target API নয় বলে invalid ধরা হয় কিনা নির্ভর করে stub-এর উপর (target stub-এ binding)।
- **Configurable-precision retriever কৃত্রিম** — বাস্তব retriever-এর error distribution (semantically কাছের ভুল doc) মডেল করে না; BM25-ভিত্তিক distractor।
- **Synthetic prompt (Claude 3 Sonnet-generated comment)** — বাস্তব developer context, multi-call workflow, error handling নেই; leakage এড়ানো যুক্তিসঙ্গত কিন্তু realism কমায়।
- Frequency গণনা নাম-ভিত্তিক (একই নামের অন্য library function গণিত হতে পারে)।
- Statistical test/variance নেই; ablation একটি ছোট model (StarCoder2-3B)-এ।
- Benchmark ও dataset প্রকাশের তথ্য markdown-এ স্পষ্ট নয় (AWS-এর ভেতরের কাজ — যাচাই প্রয়োজন)।
- Cloud **SDK** (boto3/Azure SDK) API — REST API-র উপর wrapper; সরাসরি HTTP/OpenAPI নয়, তবু T8-এর REST-backed tool-এর সমতুল্য।

## L. Threats to validity
- উপরে J; inferable: construct (binding-ভিত্তিক validity), external (synthetic, Python, দুই provider), retriever simulation।

## M. Reproducibility
- Open model ব্যবহৃত; benchmark প্রকাশের অবস্থা অনিশ্চিত; GPT-4o snapshot নির্দিষ্ট (2024-05-13) — **মাঝারি**।

## N. Opportunities (hypothesis)
- **OpenAPI/MCP-স্তরের selective documentation retrieval:** agent tool-call-এ OpenAPI operation spec retrieve (P032-এর tool explosion ও P033-এর retriever) — confidence-gated; “specification > description” ফলাফল MCP tool description design-এ প্রয়োগ।
- **Execution-validated hallucination benchmark** — stub binding-এর বদলে sandbox/mock server execution (P025-এর differential ধারণা, P001 online testing)।
- **Low-frequency/নতুন API × API evolution:** নতুন version release-এর পরে hallucination হার সময়ের সঙ্গে (P024, P022-এর সঙ্গে longitudinal)।
- **Documentation quality → DAG কার্যকারিতা:** documentation smell (P028) বা অসম্পূর্ণ spec থাকলে DAG-এর লাভ কতটা কমে — T6→T8 causal পরীক্ষা।
- **Security-relevant API hallucination** (IAM/permission API) — T3/T7 সংযোগ (P029)।

## O. Relationships
- **Builds on P034 (Gorilla)** — retrieval-aware ধারণা; Gorilla-র “খারাপ retriever ক্ষতিকর” পর্যবেক্ষণের পদ্ধতিগত বিস্তার ও প্রতিকার।
- **Complements P024** (deprecated API — evolution) ও **P031** (LLM API misuse taxonomy; hallucination শ্রেণি)।
- **Relates to P022** (tool variability) ও **P033** (API retriever)।
- **Informs T6 (P026–P028):** LLM-এর জন্য documentation-এর কোন উপাদান সবচেয়ে মূল্যবান।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract (৩৮.৫৮%, ৪৭.৯৪%, −৩৯.০২%, +৮.২০%) | p.1 L25–72 |
| Perplexity বনাম frequency | p.1–2 L51–56, L125–138 |
| API hallucination-এর প্রভাব (১৫%) | p.2 L158–173 |
| Contributions | p.2 L175–184 |
| CloudAPIBench composition (৬২২) | p.3 L239–248 |
| Frequency সংজ্ঞা | p.3 L250–265 |
| Construction (Claude 3 Sonnet) | p.3 L266–277 |
| Valid invocation metric | p.3 L278–287 |
| Models, inference | p.4 L415–424 |
| Results (Table 1) | p.4 L391–438 |
| DAG pipeline, retriever | p.4–5 L456–499 |
| Augmentation design (৪১.৮০→৮৬.৮২%) | p.5 L511–524 |
| Precision, retrieval সংখ্যা | p.5–6 L525–724 |
| Index lookup (Table 2) | p.6–7 L703–769 |
| Confidence (Fig.9) | p.7 L773–857 |
| DAG++ (Table 3) | p.8 L1056–1106 |
| Limitations | p.9 L1162–1192 |

**Document integrity:** দুই-কলামের reading order কয়েক জায়গায় অনুচ্ছেদ ভেঙেছে (abstract-এর প্রথম অংশ ও কিছু section heading হারিয়েছে); Table 1–3 column-split — per-model সংখ্যা পুনর্গঠন করা হয়নি; Fig.1–9 অনুপস্থিত; appendix (A.1–A.4, B.1) পড়া হয়নি।
