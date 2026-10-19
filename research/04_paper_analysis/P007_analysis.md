# P007 — A Multi-Agent Approach for REST API Testing with Semantic Graphs and LLM-Driven Inputs (AutoRestTest)

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references বাদ) · **উৎস:** arXiv 2411.07098v2 (২২ Jan 2025), ১৩ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Myeongsoo Kim, Tyler Stennett, Saurabh Sinha, Alessandro Orso (Georgia Tech; IBM Research)
- **Venue:** ICSE 2025, DOI 10.1109/icse55347.2025.00179
- **Cluster:** T1 (secondary: T8 — LLM-generated inputs)
- **ধরন:** Original technique (MARL + semantic graph + LLM)

## B. Motivation
- বিদ্যমান tool operation নির্বাচন, dependency, parameter, value — প্রতিটি ধাপ **আলাদাভাবে** optimize করে; সমন্বিত কৌশল নেই → invalid request বেশি, বড় service-এ coverage কম (p.1 L50–74)।

## C. Research questions (p.7 L763–771)
- RQ1: coverage (code ও operation) — SOTA-র তুলনায়। RQ2: 500-error detection। RQ3: ablation (MARL, SPDG, LLM)।

## D. Contributions (p.2 L142–243)
- Similarity-ভিত্তিক graph দিয়ে dependency search space কমানো, MARL দিয়ে ধাপগুলোর যৌথ optimization, LLM দিয়ে realistic input; empirical ফল; artifact [34]।
- দাবি: “first black-box tool to adopt a dependency-embedded multi-agent approach” (p.1 L21–23)।

## E. Methodology
- **SPDG (p.5–6):** node = operation; edge = input parameter name ও output field name-এর **GloVe cosine similarity > ০.৭**; কোনো edge না থাকলে top-৫ সদৃশ operation-এ সংযোগ; runtime-এ 2xx হলে edge weight বাড়ে, ব্যর্থ হলে কমে; random dependency query নতুন edge আবিষ্কার করে (undocumented response field সহ)।
- **চারটি agent (p.6–7):** Operation (reward: 5xx +২, 4xx +১, 2xx −১, 401 −৩, 405 −১০ — সমস্যাযুক্ত operation-এ বারবার ফেরে); Parameter (combination, ≤১০; 2xx +২, 4xx −২, 5xx −১); Value (উৎস নির্বাচন: dependency value / **GPT-3.5-Turbo few-shot (temp 0.8)** / type-based random); Dependency (SPDG edge-এর Q-table)।
- **Learning:** ε-greedy (১.০ → ০.১ linear decay), Q-learning α=০.১, γ=০.৯; **value decomposition** (joint Q = Σ Qᵢ) — কেন্দ্রীভূত update (p.4–5 L414–529)।
- **Mutator:** ২০% request invalid করা (ARAT-RL অনুসারে) (p.7 L730–739)।

## F. Dataset ও setup
- **১২টি service (Table I):** P005-এর মতোই — ৯ open-source + FDIC, Spotify, OhSome (online)। SCS/NCS (EvoMaster লেখকদের) বাদ, OCVN (auth) ও OMDB বাদ (p.8 L841–853)।
- দুটি cloud VM (48-core Xeon, 128GB); ১ ঘণ্টা × ১০ রান; database restore প্রতি session (p.7 L773–780)।
- **Baselines:** RESTler v9.2.4, EvoMaster v3.0.0, ARAT-RL v0.1, MoRest — **RESTGPT-enhanced spec** দিয়ে (p.8 L835–858)।
- Metrics: JaCoCo coverage, processed operation (NLP2REST script), unique 500 (ARAT-RL script, response message দিয়ে dedup)।

## G. Evaluation
- গড় (১০ রান); ⚠️ **কোনো statistical test নেই**; ablation-এর রান-সংখ্যা উল্লেখ নেই।

## H. Results (author-reported)
- **RQ1:** method **৫৮.৩%** (ARAT-RL ৪২.১, EvoMaster ৪৩.১, MoRest ৩১.৫, RESTler ৩৪.৭); line ৫৮.৩%; branch ৩২.১% (অন্যরা ১১.৪–২০.৫) (p.8 L925–934)। Online processed operation **২৫** বনাম ৯–১১ (Table II; OhSome-এ ১২ বনাম ০) (L935–942)।
- সুবিধা বড়/বহু-parameter service-এ (Genome Nexus, Person Controller, User Management, Market, YouTube, OhSome, Spotify); ১–২ parameter-যুক্ত service-এ (Features, REST Countries, Project Tracking) পার্থক্য সামান্য (p.8 L943–952)।
- **RQ2 (Table III):** **৪২টি** 500 (error-যুক্ত operation-ভিত্তিক গণনা — p.2 L125) বনাম ARAT-RL ৩৩, EvoMaster ২০, MoRest ২০, RESTler ১৪; OhSome ২০ (ARAT-RL ১২), Spotify-তে একমাত্র ১টি; OhSome error developer-স্বীকৃত ও fixed (p.9 L1068–1087; p.2 L127–132)।
- **RQ3 (Table IV):** Q-learning বাদে সবচেয়ে বড় পতন (method ৪৫.৬%, −১২.৭), SPDG বাদে method ৪৬.৭%, LLM বাদে ৪৭.৪%; প্রতিটি উপাদান বাদে ১০.৭–১৩.৯ বিন্দু কমে (p.10 L1162–1205)।

## I. Strengths
- সমস্যাকে পৃথক কিন্তু সমন্বিত decision-এ ভাগ করা — নকশাগতভাবে স্পষ্ট ও ব্যাখ্যাযোগ্য (DeepREST-এর black-box deep RL-এর বিপরীতে)।
- Runtime-এ dependency graph পরিমার্জন — undocumented response field আবিষ্কার।
- বাস্তব bug developer-স্বীকৃত (OhSome); baselines-কে enhanced spec দেওয়া।
- Artifact প্রকাশিত।

## J. Explicit limitations (p.10 L1206–1228)
- **Construct:** GPT-3.5 প্রশিক্ষণে API সংক্রান্ত তথ্য থাকতে পারে → **data leakage**; ২০% mutation rate ও default parameter-এর প্রভাব।
- **Internal:** REST API-র flaky আচরণ (network) — বহু রান দিয়ে প্রশমন।
- **Spec quality:** OpenAPI-র অসম মান — spec completeness-এর প্রভাব future work।
- **External:** benchmark নির্বাচন।
- Concurrent DeepREST ও LlamaRestTest-এর সঙ্গে তুলনা নেই (p.11 L1278–1280)।

## K. Inferred limitations (⚠️ অনুমান)
- **একই group-এর দুই paper-এ baseline-ফলের অসামঞ্জস্য:** P005 ও P007 একই ১২টি service, একই tool version, একই ১ঘণ্টা×১০ ব্যবহার করেছে, অথচ ARAT-RL-এর 500-error P005-এ ১৬০, P007-এ ৩৩ (গণনার একক ভিন্ন — P005 ১০ রানের যোগফল, P007 error-যুক্ত operation); method coverage-ও ভিন্ন (ARAT-RL ৪১.৭ বনাম ৪২.১; EvoMaster ৪৫.৮ বনাম ৪৩.১)। ফলে **cross-paper তুলনা অসম্ভব** এবং মূল্যায়ন-পদ্ধতির মানকীকরণের অভাব প্রকট (P019/C19 WFD-এর উদ্বেগের প্রমাণ)।
- **AutoRestTest বনাম LlamaRestTest কখনো সরাসরি তুলনা হয়নি**, যদিও উভয়ই একই group, একই benchmark — কোনটি ভালো তা অজানা।
- **Statistical test নেই**; ablation-এর রান-সংখ্যা অনুল্লিখিত।
- **Table IV-এর কলাম-লেবেল অসামঞ্জস্যপূর্ণ:** header “Method, Line, Branch”-এর অধীনে ৫৮.৩/৩২.১/৫৮.৩ — অথচ RQ1-এ line ৫৮.৩, branch ৩২.১; ablation text-এ “45.6%, 18.2%, 45.9% for method, line, branch” — line ও branch অদলবদল সম্ভব (p.10 L1113–1140 বনাম L1172–1175)।
- Fault oracle শুধু 500; 500-গুলোর কতটি প্রকৃত bug তা যাচাই হয়নি (OhSome ছাড়া)।
- **GloVe word similarity** — domain-specific নামকরণে (abbreviation, ভিন্ন ভাষা) দুর্বল হতে পারে; threshold ০.৭ পূর্ববর্তী কাজ থেকে নেওয়া, sensitivity বিশ্লেষণ নেই।
- GPT-3.5 closed model — খরচ ও reproducibility (model deprecation) ঝুঁকি।

## L. Threats to validity
- উপরে J; inferable: conclusion validity (no statistics), construct (500-গণনার একক)।

## M. Reproducibility
- Tool, benchmark, ফল artifact-এ [34]; কিন্তু GPT-3.5-Turbo-নির্ভরতা — model বন্ধ হলে হুবহু পুনরুৎপাদন কঠিন। Hardware বড় (48-core, 128GB) কিন্তু tool হালকা হতে পারে।

## N. Opportunities (hypothesis)
- **AutoRestTest বনাম LlamaRestTest বনাম DeepREST** — একই protocol, একই fault-counting, statistical test সহ স্বাধীন তুলনা (একটি সুস্পষ্ট, কম-infrastructure গবেষণা সুযোগ)।
- SPDG-তে GloVe-এর বদলে code/LLM embedding বা spec-aware similarity।
- Spec completeness-এর প্রভাব নিয়ন্ত্রিত পরীক্ষা (লেখকদের future work) — T4-এর সঙ্গে সংযোগ।
- Fault classification (লেখকদের future work) — P001-এর Challenge #1-এর সঙ্গে মিল।

## O. Relationships
- **Sibling of P005** (একই group, concurrent) — একে অপরের তুলনা নেই; baseline সংখ্যায় অমিল।
- **Builds on:** ARAT-RL, RESTGPT, NLP2REST, P004।
- **Alternative to:** DeepREST (single-agent deep RL), MoRest (static property graph)।
- **Confirms P004/P003:** dependency শনাক্তকরণ ও constrained value — মূল বাধা।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Motivation | p.1 L50–74 |
| Contributions | p.2 L142–243 |
| Workflow | p.4 L357–413 |
| Q-learning, value decomposition | p.4–5 L414–529 |
| SPDG (০.৭ threshold, top-৫) | p.5–6 L531–601 |
| Agents ও reward | p.6–7 L602–723 |
| GPT-3.5, temp 0.8 | p.7 footnote L733–734 |
| Mutator ২০% | p.7 L730–739 |
| RQs | p.7 L763–771 |
| Setup, benchmark, baselines | p.7–8 L773–870 |
| RQ1 coverage | p.8 L921–957; Figure 4 |
| Operation coverage | p.8 Table II L875–919 |
| RQ2 | p.9 Table III L964–1161 |
| RQ3 ablation | p.10 Table IV L1113–1205 |
| Threats | p.10 L1206–1228 |

**Document integrity:** YAML figure letter-spaced; সমীকরণ (value decomposition) আংশিক ভাঙা কিন্তু অর্থবোধ্য; Figure 2–4 অনুপস্থিত (per-service coverage PDF-এ দেখতে হবে); Table I–IV পুনর্গঠনযোগ্য; Table IV-এর কলাম-লেবেল মূল paper-এই অসামঞ্জস্যপূর্ণ মনে হয় — PDF-এ যাচাই প্রয়োজন।
