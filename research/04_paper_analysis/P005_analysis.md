# P005 — LlamaRestTest: Effective REST API Testing with Small Language Models

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references বাদ) · **উৎস:** arXiv 2501.08598v2 (৩ Apr 2025) — PACMSE/FSE 2025 camera-ready header সহ (Article FSE022), ২৩ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Myeongsoo Kim, Saurabh Sinha, Alessandro Orso (Georgia Tech; IBM Research)
- **Venue:** Proc. ACM Softw. Eng. 2 (FSE 2025), DOI 10.1145/3715737; CC-BY 4.0
- **Cluster:** T1 (secondary: T4 — spec enrichment; T8 — LLM for API)
- **ধরন:** Original technique (fine-tuned small LM + RL)

## B. Motivation
- Black-box tool-গুলো complex input constraint ও inter-parameter dependency (IPD)-তে ব্যর্থ (p.2 L74–76)।
- NLP2REST, ARTE, RESTGPT spec-এর NL অংশ থেকে তথ্য তোলে, কিন্তু **runtime-এ server feedback দিয়ে refine করতে পারে না** (p.2 L84–87)।
- RESTGPT (GPT-3.5) খরচ ~$১০/spec; গোপনীয়তার কারণে local open-source model কাম্য (p.7 L373–380)।

## C. Research questions (p.11 L744–756)
- RQ1: LlamaREST-EX/IPD বনাম RESTGPT (IPD শনাক্তকরণ ও valid input)।
- RQ2: fine-tuning ও quantization-এর প্রভাব (code/operation coverage)।
- RQ3: SOTA tool-এর সঙ্গে coverage তুলনা। RQ4: 500-error detection। RQ5: ablation।

## D. Contributions (p.3 L146–152)
- “প্রথম” LM-ভিত্তিক REST testing যা server feedback + fine-tuning + quantization ব্যবহার করে।
- Empirical ফল; artifact (tool, benchmark, fine-tuning data, model) [35]।

## E. Methodology
- **দুটি model** (Llama3-8B থেকে): LlamaREST-IPD (IPD শনাক্তকরণ) ও LlamaREST-EX (valid value)। একক model-এ catastrophic forgetting দেখে দুটি আলাদা (p.8 L452–456)।
- **Training data (p.7–8 L395–449):** IPD — Martin-Lopez IPD database থেকে benchmark-বহির্ভূত **৫৫১টি parameter**; rule RESTGPT দিয়ে তৈরি, তারপর একজন লেখক manually যাচাই (২৫টি = ৪.৫% সংশোধন, ~৫ ঘণ্টা)। EX — APIs.guru-র **৪,১৩৩টি spec** (১.৮M+ parameter set) থেকে **enum-যুক্ত parameter** (name, description → enum values)।
- **Fine-tuning:** QLoRA (PEFT), Google Colab A100 40GB, batch ৮, early stopping (EX ৩৫ epoch, IPD ৫১ epoch) (p.9 L493–521)।
- **Quantization:** llama.cpp — 2-bit (২.৯৬GB), 4-bit (৪.৫৮GB), 8-bit (৭.৯৫GB) (p.10 L533–541)।
- **Testing loop:** ARAT-RL (Q-learning: 2xx → Q কমে, 4xx/500 → Q বাড়ে; ε-greedy); **বারবার 4xx হলে** দুটি LM সক্রিয় হয় — parameter description + **server response message** prompt-এ দিয়ে (p.10 L546–580)।

## F. Dataset ও setup
- **১২টি service (Table 1, p.11):** ৯টি open-source (Features-Service, Genome-Nexus, Language-Tool, Market, Person-Controller, Project-Tracking-System, REST-Countries, User-Management, YouTube-mock) + ৩টি online (FDIC, Ohsome, Spotify)।
- বাদ: SCS ও NCS (“EvoMaster-এর লেখকদের লেখা, bias এড়াতে”), OCVN (authentication সমস্যা), OMDB (খুব ছোট) (p.11–12 L775–779, L1027)।
- M1 MacBook Pro 64GB; প্রতি tool ১ ঘণ্টা × ১০ রান (ablation ৩ রান) (p.11 L761–779)।
- **Baselines:** RESTler v9.2.4, EvoMaster v3.0.0, ARAT-RL v0.1, MoRest (লেখকদের কাছ থেকে); এগুলো **RESTGPT-enhanced spec** পেয়েছে (p.16 L1322–1325)।
- RQ1 ground truth: RESTGPT dataset — value-এর জন্য ৭টি, IPD-র জন্য ৩টি service; semantic validity দুজন বাইরের developer স্বাধীনভাবে বিচার করেছেন (p.13 L1062–1076)।

## G. Evaluation
- Metrics: valid-value precision, সঠিক IPD rule সংখ্যা; JaCoCo method/branch/line coverage; online service-এর জন্য processed operation; unique 500 error (ARAT-RL script, response message দিয়ে dedup)।
- ⚠️ **কোনো statistical significance test বা effect size নেই**; ফল ১০ রানের গড়।

## H. Results (author-reported)
- **RQ1 values (Table 3):** LlamaREST-EX FT **৭২.৪৪%**, RESTGPT ৬৮.৮২%, base Llama3-8B ২২.৯৪% (text-এ ২৪.৯৪% — ⚠️ অসামঞ্জস্য, p.13 L1077 বনাম Table 3 L872); 8-bit ৬৬.১২%, 4-bit ৬০.২১%, 2-bit ২৯.১২%। Language-Tool ও FDIC-তে RESTGPT ভালো (domain/format জ্ঞান) (p.13 L1087–1100)।
- **RQ1 IPD (Table 4):** মোট **১৮টি rule** (Table total) — FT ১২টি, RESTGPT ৯, Llama3 ২, 8-bit ৭, 4-bit ৬, 2-bit ১। ⚠️ abstract/intro-তে “১৭টি dependency” (p.3 L127) বনাম Table-এ ১৮ — অসামঞ্জস্য।
- **RQ2:** FT একা সামান্য উন্নতি (method ৫০.১% বনাম base ৪৯.২%); **8-bit quantized FT সর্বোচ্চ** (method ৫৫.৮%, branch ২৮.৩%, line ৫৫.৩%; ৩৭.৫ operation বনাম base ২৩) (p.15 L1253–1275)। লেখকদের ব্যাখ্যা: দ্রুত inference (FT ৪৮.৯s → 8-bit ৩৬.৯s প্রতি IPD) ও quantization-এর “regularization effect” (p.15 L1276–1286)।
- **RQ3:** method coverage ৫৫.৮% বনাম EvoMaster ৪৫.৮, ARAT-RL ৪১.৭, MoRest ৩৩.৩, RESTler ৩৩.১; online operation ৩৭.৫ বনাম ৯.৯–১১.৬ (p.16–17 L1326–1348)।
- **RQ4 (Table 2):** **২০৪টি 500 error** বনাম ARAT-RL ১৬০, MoRest ১৪০, RESTler/EvoMaster ১৩০; Ohsome-এ (৩৬) ও Spotify-তে (৮) একমাত্র tool যা error পেয়েছে (p.17 L1378–1391)।
- **RQ5 (Table 7, ৩ রান):** IPD বাদ দিলে সবচেয়ে বড় পতন (method −৯.২), তারপর server response (−৬.১), parameter description (−৫.৯), EX (−৩.৭) (p.18 L1454–1475)।
- লেখকদের স্বীকারোক্তি: দুর্বল server message-যুক্ত API-তে অন্য tool-এর মতোই (p.17 L1354–1367)।

## I. Strengths
- **কম খরচে কার্যকর:** 8B model, consumer hardware (MacBook), local — গোপনীয়তা ও খরচ সুবিধা; সীমিত infrastructure-এর গবেষকের জন্য অনুসরণযোগ্য।
- Server response message ব্যবহার — নতুন signal; ablation দ্বারা সমর্থিত।
- Bias এড়াতে EvoMaster-লেখকদের service বাদ দেওয়া; baselines-কে enhanced spec দেওয়া — ন্যায্যতার প্রচেষ্টা।
- Model ও data প্রকাশিত।

## J. Explicit limitations (p.19 L1489–1512)
- ১২টি service প্রতিনিধিত্বশীল না-ও হতে পারে; fine-tuning dataset-নির্ভরতা।
- সীমিত tool তুলনা; settings optimal না-ও হতে পারে; script bug সম্ভাবনা; ARAT-RL-নির্ভরতা।
- Concurrent কাজ (DeepREST, AutoRestTest) তুলনায় অন্তর্ভুক্ত নয় (p.20 L1546–1547)।
- 2-bit model domain-heavy service-এ খারাপ; বড় model কিছু constraint-এ ভালো।

## K. Inferred limitations (⚠️ বিশ্লেষকের অনুমান)
- **লাভ কয়েকটি service-এ কেন্দ্রীভূত:** RQ4-এ ARAT-RL-এর চেয়ে ৪৪টি বেশি error — যা হুবহু Ohsome (৩৬) + Spotify (৮); বাকি ১০টি service-এ সংখ্যা অভিন্ন (Table 2)। Operation coverage-এর পার্থক্যও মূলত Ohsome (২৪.৫ বনাম ০)। ফলে “সামগ্রিক শ্রেষ্ঠত্ব” দাবি মূলত দুটি online service-নির্ভর।
- **Statistical test নেই** — coverage পার্থক্য (বিশেষত RQ2-এর ১–২ শতাংশ বিন্দু) রান-ভেদের মধ্যে থাকতে পারে (P003 দেখিয়েছে রান-ভেদ ৯–১০% পর্যন্ত হয়)।
- **Quantization > full precision (RQ2)** একটি বিপরীতমুখী ফল; RQ1-এ quantized model কম নির্ভুল। “Regularization” ব্যাখ্যা যাচাইহীন; সম্ভবত দ্রুততর inference-এর কারণে ১ ঘণ্টায় বেশি iteration — অর্থাৎ **time-budget confound**। সমান LLM-call সংখ্যায় তুলনা করা হয়নি।
- **IPD মূল্যায়ন ক্ষুদ্র ও সমজাতীয়:** ১৮টি rule-এর ১৩টি YouTube-এর “IF X THEN type=video” ধাঁচের — generalization প্রমাণ দুর্বল।
- **Ground truth RESTGPT-এর** এবং training-এর IPD rule-ও RESTGPT দিয়ে তৈরি → RESTGPT-এর ধাঁচে fit হওয়ার ঝুঁকি (data leakage-সদৃশ circularity, অনুমান)।
- **Oracle শুধু 500** — semantic/spec fault গণনার বাইরে।
- একই research group-এর পূর্ববর্তী tool (ARAT-RL, RESTGPT) baseline ও উপাদান — স্বাধীন replication নেই।
- Text-এ copy-paste ত্রুটি (“we compared AutoRestTest with ARAT-RL…”, p.11 L771) — সম্পাদনাগত, তবে সতর্কতা।

## L. Threats to validity
- Stated: external, setup, script, tool-dependency।
- Inferable: construct (500 = fault), conclusion validity (no stats), internal (time-budget confound)।

## M. Reproducibility
- Tool, model, data, ফল artifact-এ [35] ✅। Fine-tuning-এ A100 লাগে (Colab); inference consumer hardware-এ। Online service (Spotify, Ohsome) সময়ের সঙ্গে বদলায়।

## N. Opportunities (hypothesis)
- **সমান LLM-call/সমান wall-time ও statistical test** সহ পুনর্মূল্যায়ন — quantization-লাভের কারণ আলাদা করা।
- Enum-বহির্ভূত (free-form, regex, domain-specific) value-এর জন্য fine-tuning data সম্প্রসারণ।
- দুর্বল server message-এর API-তে কী হয় — error-message quality-কে স্বাধীন variable হিসেবে অধ্যয়ন (P016-এর T4/T6 সংযোগ)।
- Spec-repair: runtime-এ শেখা IPD ও value spec-এ ফেরত লেখা (T4)।

## O. Relationships
- **Builds on:** P004 (NLP proof-of-concept), ARAT-RL, RESTGPT, NLP2REST — একই group।
- **Competes with:** P007 AutoRestTest (একই group, concurrent; তুলনা নেই), DeepREST।
- **Uses:** P016 (IPD database/ধারণা)।
- **Contrast with P003:** P003-এর “black-box-এ underspecified schema-র viable solution নাও থাকতে পারে” দাবির বিপরীতে server-message + LM আংশিক সমাধান দেখায় (তবে শুধু informative message থাকলে)।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Motivation (runtime feedback নেই) | p.2 L77–87 |
| Contributions | p.3 L146–152 |
| খরচ/গোপনীয়তা যুক্তি | p.7 L372–380 |
| Training data, ৫৫১ IPD, ৪.৫% সংশোধন | p.7–8 L395–449 |
| QLoRA, A100, epochs | p.9 L493–521 |
| Quantization size | p.10 L533–541 |
| Testing loop (ARAT-RL) | p.10 L546–580 |
| Benchmark, বাদ পড়া service | p.11 Table 1; L775–779; p.12 L1027 |
| RQs | p.11 L744–756 |
| RQ1 values | p.12 Table 3; p.13 L1077–1100 |
| RQ1 IPD | p.12 Table 4; p.13 L1101–1105 |
| RQ2 | p.14–15 L1229–1316; Table 5 |
| RQ3 | p.16–17 L1320–1367; Table 6 |
| RQ4 | p.11 Table 2; p.17 L1371–1442 |
| RQ5 ablation | p.18 Table 7 L1404–1475 |
| Threats | p.19 L1489–1512 |

**Document integrity:** YAML/prompt figure letter-spaced কিন্তু পাঠযোগ্য; Table 2–7 কলাম-ভাঙা কিন্তু পুনর্গঠনযোগ্য (Table 4-এর O/− চিহ্ন কলাম-মিলানো অনিশ্চিত — total সারি নির্ভরযোগ্য); Figure 2–4 (coverage chart) অনুপস্থিত — per-service coverage PDF-এ দেখতে হবে।
