# P022 — Learning Evolving Tools for Large Language Models (ToolEVO)

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ + appendix (error analysis, API modification prompt) skim; references বাদ · **উৎস:** ICLR 2025 camera-ready (arXiv 2410.06617), ৩০ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Guoxin Chen, Zhong Zhang, Xin Cong, Fangda Guo, Yesai Wu, Yankai Lin, Wenzheng Feng, Yasheng Wang (ICT CAS; Tsinghua; Renmin; Huawei Noah's Ark)
- **Venue:** ICLR 2025 (DOI প্রযোজ্য নয়; arXiv 2410.06617)
- **Cluster:** T5 (secondary: T8 — LLM tool learning)
- **ধরন:** নতুন training framework + benchmark

## B. Motivation
- Tool learning-এ API (name, parameter, response format) সময়ের সঙ্গে বদলায়; LLM-এর শেখা/prompt-এ দেওয়া API আর server-এর API-র অমিলে performance ভেঙে পড়ে (Fig.1–2) (p.1–2 L113–146)।
- বিদ্যমান tool learning static environment ধরে নেয়; real-time API সংগ্রহ ব্যয়বহুল (p.2 L137–146)।

## C. Research questions
- ⚠️ স্পষ্ট RQ নেই; তিনটি পরীক্ষামূলক setting (static, in-domain dynamic, OOD dynamic) + API change-ধরন বিশ্লেষণ + ablation।

## D. Contributions (p.2 L163–170)
- Tool variability-র প্রভাবের প্রথম অনুসন্ধান (দাবি)।
- **ToolEVO:** MCTS-ভিত্তিক active exploration + self-reflection + tool-update; trial-and-error trajectory দিয়ে SFT।
- **ToolQA-D:** tool variability-র প্রথম benchmark (দাবি)।
- বিভিন্ন API change-এর প্রভাব বিশ্লেষণ।

## E. Methodology
- **Formulation:** collected API Pc বনাম deployed API Ps; environment feedback — task completion (reward ±১), API response, error message (invocation error বনাম **deprecation error**) (p.2–3 L180–233)।
- **MCTS:** state = task + Pc + action history; action = ReAct-ধাঁচের API invocation; PUCT selection, LLM দিয়ে k-node expansion, **cached rollout**, backpropagation (p.3–4 L199–300)।
- **Self-reflection:** error state থেকে একই LLM verbal reflection তৈরি করে (GPT-4-এর মতো শক্তিশালী model নয়) (p.4 L310–323)।
- **Tool-update:** নতুন tool সফলভাবে call করার পর `UpdateTool[newtool desc]` system tool দিয়ে prompt-এর Pc হালনাগাদ (memory-ধাঁচ) (p.5 L386–400)।
- **Training:** সফল trajectory দিয়ে SFT (~৩০k trajectory); failed trajectory/preference learning ব্যবহার হয়নি (p.5 L405–418; p.6 L499–500)।
- **ToolQA-D:** ToolQA (৭ dataset: Agenda, Airbnb, Coffee, DBLP, Flights, SciREX, Yelp)-এর API **GPT-4 দিয়ে random পরিবর্তন** (synonym, camelCase, special character insertion) → Psin (training) ও PsOOD (test-only); Easy/Hard; train ৬,২৩৪/৫,৮৮৪, dev ৭০০/৭০০, test ৭০০/৭৩০ (p.5–6 L424–453; Appendix D.1)।
- Base model: Llama3-8B, Qwen2-7B; greedy decoding, ৩-shot ReAct; prompt-এ শুধু Pc (p.6 L497–506)।

## F. Dataset ও setup
- উপরে E; baselines: GPT-3.5, GPT-4, GPT-4o, GPT-4o-mini, Claude-3.5-Sonnet; Llama3/Qwen2 series (৭০B/৭২B সহ); **Static-SFT** (Pc-তে ToolEVO দিয়েই সংগৃহীত trajectory — strong baseline) (p.6 L493–504)।

## G. Evaluation
- Task success rate (ToolQA evaluation toolkit), dataset ও difficulty অনুযায়ী; API change type বিশ্লেষণ (Llama3); ablation (OOD setting)।

## H. Results (author-reported)
- **Static (Pc→Pc):** Pc-তে fine-tune না করেও ToolEVO Static-SFT-এর সমান বা বেশি (p.7 L1312–1316)।
- **In-domain dynamic (Pc prompt, Psin server):** outdated prompt সব model-এর performance কমায়, Static-SFT সবচেয়ে বেশি; ToolEVO (৭B) Static-SFT ও ৭২B model-কে ছাড়িয়ে যায় (p.8 L1325–1335)।
- **OOD dynamic (Pc→PsOOD):** ToolEVO baseline-গুলোর চেয়ে “significant margin”-এ ভালো; proprietary model-এর গড় Easy/Hard — GPT-3.5 ৩১.৪/১৯.২, GPT-4 ৪০.৩/২৩.২, GPT-4o ৫৬.০/২৪.৪, GPT-4o-mini ৪৭.৪/২১.৭, Claude-3.5-Sonnet ৬০.২/৩২.১ (Table 4); উদাহরণ: Agenda-Easy-এ Static-SFT ৫৮ বনাম ToolEVO ৭১, Agenda-Hard ৯ বনাম ৪৯ (p.7–8; Table 4 L1076–1205)।
- **Static-SFT “stereotype”:** prompt-এর API-তে অতি-আস্থা → deprecated API বারবার call (error analysis C.3) (p.8 L1342–1345; Appendix)।
- **API change type:** parameter পরিবর্তন name পরিবর্তনের চেয়ে বেশি ক্ষতিকর; special character insertion-ও বড় সমস্যা; response format পরিবর্তনের প্রভাব ন্যূনতম; Hard task-এ পতন বেশি (p.8–9 L1367–1512)।
- **Ablation:** tool-update বাদ দিলে কমে; **self-reflection বাদ দিলে আরও বেশি** কমে (p.9–10 L1518–1592)।

## I. Strengths
- **গুরুত্বপূর্ণ ও কম-অধ্যয়িত সমস্যা** — API evolution (T5) ও LLM tool use (T8)-এর সংযোগস্থল; ICLR-এ গৃহীত।
- In-domain ও OOD পৃথক — কেবল memorization নয়, adaptation পরীক্ষা।
- ছোট (৭–৮B) model দিয়ে proprietary/৭০B-কে ছাড়ানো — ব্যবহারিক।
- API change-ধরন অনুযায়ী বিশ্লেষণ ও বিস্তারিত error taxonomy (appendix)।
- Code উন্মুক্ত (GitHub Chen-GX/ToolEVO)।

## J. Explicit limitations (appendix C error analysis; p.5)
- ToolEVO-ও নতুন tool-এ invocation error ও API response থেকে তথ্য ভুল মূল্যায়ন করে; “preliminary exploration” (Appendix C)।
- শুধু SFT (fair comparison-এর জন্য); failed trajectory/preference learning ব্যবহার হয়নি (p.5 L416–418)।
- ⚠️ পৃথক limitations/threats section নেই।

## K. Inferred limitations (⚠️ অনুমান)
- **Synthetic tool variability:** GPT-4-এর তৈরি **semantic-preserving rename/special-character insertion** — বাস্তব API evolution (endpoint সরানো, parameter বিভাজন, behavioral change, auth পরিবর্তন, pagination বদল; P020/P023-এর breaking change ধরন) প্রতিনিধিত্ব করে না।
- **অতি-সহায়ক environment:** deprecation error message নতুন API ও তার ব্যবহারবিধি **স্পষ্টভাবে বলে দেয়** (“…is deprecated… use X instead”, Appendix) — বাস্তবে REST API সাধারণত 404/410/400 দেয়, বিকল্প জানায় না (P020: consumer অজানা ও informal communication)। ফল তাই উপরের সীমা (upper bound)।
- **Benchmark বৈচিত্র্য সীমিত:** ToolQA-র ৭টি ছোট synthetic domain-এর local tool (LoadDB, PythonInterpreter ইত্যাদি) — বাস্তব web API নয় (P033 ToolBench-এর ১৬k RapidAPI-র তুলনায়)।
- **Static-SFT baseline-এ ToolEVO pipeline ব্যবহৃত** — fair, কিন্তু অন্য dynamic-adaptation পদ্ধতি (retrieval of fresh docs — P035-এর documentation augmentation; ToolLLM-এর API retriever) baseline হিসেবে নেই; “সর্বশেষ documentation retrieve করা” সহজতম বিকল্পের সঙ্গে তুলনা নেই।
- কোনো statistical test/variance নেই (greedy decoding, একক রান)।
- “প্রথম benchmark” দাবি — সমসাময়িক কাজ (যেমন P024-এর deprecated API usage, CodeUpdateArena-ধাঁচ) সাপেক্ষে সংকীর্ণ অর্থে সত্য।

## L. Threats to validity
- ⚠️ আনুষ্ঠানিক section নেই; inferable: construct (synthetic variability), external (ToolQA domain), conclusion (single run)।

## M. Reproducibility
- Code ও (দাবিকৃত) benchmark GitHub-এ; GPT-4-generated modification-এর random seed/version নির্ভরতা; training ২টি open model — **মাঝারি-উচ্চ**।

## N. Opportunities (hypothesis)
- **Real-world API evolution-ভিত্তিক tool-variability benchmark:** OpenAPI version history (P021-এর UC-1, P023-এর Maven breaking change taxonomy) থেকে বাস্তব change mining — structural ও **behavioral** change, ambiguous error message সহ।
- **Spec-diff-aware agent:** OpenAPI changelog/diff (P018/P017-এর generated spec) agent-এর memory-তে inject — MCTS trial-and-error-এর সস্তা বিকল্প; তুলনামূলক গবেষণা।
- **MCP server evolution** (P036): MCP tool schema পরিবর্তনে agent-এর robustness — T8-এর নতুন evaluation axis।
- Breaking-change communication-কে machine-readable করা (deprecation header, `Sunset`, OpenAPI `deprecated`) — agent-বান্ধব API evolution governance (P020-এর consumer lock-in-এর agent সংস্করণ)।
- Preference learning (failed trajectory) ও online continual adaptation।

## O. Relationships
- **Bridges T5 ↔ T8:** API evolution সমস্যা LLM agent consumer-এ প্রয়োগ।
- **Complements P024** (LLM code generation-এ deprecated library API) — একটি tool-call স্তরে, অন্যটি code স্তরে।
- **Builds on ToolQA** এবং ToolLLM/ToolBench (P033)-এর static tool learning-এর সমালোচনা।
- **Relates to P035** (documentation দিয়ে hallucination প্রশমন) — বিকল্প পদ্ধতি।
- **Echoes P020** (consumer ও provider-এর অসমন্বয়) — agent-consumer সংস্করণে।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract | p.1 L19–28 |
| Tool variability সমস্যা (Fig.1–2) | p.1–2 L103–146 |
| Contributions | p.2 L163–170 |
| Task formulation, feedback ধরন | p.2–3 L180–233 |
| MCTS অপারেশন | p.3–4 L199–300 |
| Self-reflection | p.4 L310–323 |
| Tool-update | p.5 L386–400 |
| SFT, failed trajectory বাদ | p.5 L405–418 |
| ToolQA-D নির্মাণ (GPT-4 modification) | p.5–6 L424–453; Appendix D.1 L2816– |
| Baselines, implementation | p.6 L493–506 |
| Static ফল (Table 2) | p.7 L1312–1316 |
| Dynamic ফল (Table 3) | p.8 L1325–1335 |
| OOD ফল (Table 4) | p.7–8 L1076–1205, L1336–1345 |
| API change-type বিশ্লেষণ | p.8–9 L1367–1512 |
| Ablation (Table 5) | p.9–10 L1518–1592 |
| Deprecation message উদাহরণ | Appendix L2684–2688 |
| Error analysis | Appendix L2734–2806 |

**Document integrity:** Body সম্পূর্ণ; MCTS সূত্র (PUCT, backpropagation) আংশিক হারিয়েছে; **Table 2–5 column-split** — ToolEVO-র dataset-স্তরের সব সংখ্যা ও average পুনর্গঠন অনিশ্চিত (proprietary average পাঠযোগ্য); Fig.2, 4–6 অনুপস্থিত।
