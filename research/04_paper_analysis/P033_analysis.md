# P033 — ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (appendix-এর filtering অংশ দেখা; related work বাদ; references বাদ) · **উৎস:** ICLR 2024 camera-ready (arXiv 2307.16789), ২৩ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Yujia Qin, Shihao Liang, Yining Ye, … Yankai Lin, Zhiyuan Liu, Maosong Sun (Tsinghua; ModelBest; Renmin; Yale; Tencent WeChat AI; Zhihu)
- **Venue:** ICLR 2024 (DOI প্রযোজ্য নয়; arXiv 2307.16789 — OpenAlex arXiv DOI mislabel পূর্বে নথিভুক্ত)
- **Cluster:** T8 (secondary: T1 — বাস্তব REST API-র বৃহৎ ব্যবহার/execution)
- **ধরন:** Dataset (ToolBench) + reasoning algorithm (DFSDT) + model (ToolLLaMA) + evaluator (ToolEval) + retriever

## B. Motivation
- Open-source LLM (LLaMA) tool-use-এ দুর্বল কারণ instruction tuning মূলত ভাষা-কাজে; closed model (ChatGPT) শক্তিশালী কিন্তু অস্বচ্ছ (p.1–2 L45–141)।
- পূর্ববর্তী tool-learning data-এর সীমা: (১) কম API ও কম বৈচিত্র্য, (২) সীমাবদ্ধ scenario — একক tool, আগে থেকে নির্দিষ্ট API set, (৩) দুর্বল planning (CoT/ReAct), এবং কিছু কাজ API আসলে execute করে না (p.2 L172–291)।

## C. Research questions
- ⚠️ আনুষ্ঠানিক RQ নেই; পরীক্ষিত দাবি: retriever কার্যকারিতা, DFSDT বনাম ReAct, ToolLLaMA-র সাধারণীকরণ (unseen instruction/tool/category), OOD (APIBench) সাধারণীকরণ।

## D. Contributions (p.2–3 L303–437)
- **ToolBench:** RapidAPI-র **১৬,৪৬৪টি বাস্তব REST API** (৩,৪৫১ tool, ৪৯ category); single-tool (I1), intra-category multi-tool (I2), intra-collection multi-tool (I3) instruction; ১২৬,৪৮৬ (instruction, solution path) জোড়া।
- **DFSDT** — depth-first search decision tree reasoning।
- **ToolEval** — ChatGPT-ভিত্তিক automatic evaluator (pass rate, win rate)।
- **ToolLLaMA** (LLaMA-2 7B fine-tuned) + **neural API retriever** (Sentence-BERT)।
- Code, model, demo উন্মুক্ত।

## E. Methodology
- **API collection:** RapidAPI-র ১০,৮৫৩ tool (৫৩,১৯০ API) crawl — নাম, বর্ণনা, HTTP method, required/optional parameter, request body, code snippet, example response; **৪০৪/internal error, দীর্ঘ response time, নিম্নমানের response বাদ দিয়ে** ৩,৪৫১ tool (১৬,৪৬৪ API) রাখা — অর্থাৎ ~৬৯% API বাদ (p.4 L582–600; Appendix A.1)।
- **Instruction generation:** API sample করে ChatGPT (gpt-3.5-turbo-16k) দিয়ে instruction + relevant API; ১২/৩৬ human-written seed; multi-tool-এ একই category/collection থেকে ২–৫ tool, প্রতি tool ≤৩ API; hallucinated API-যুক্ত instruction বাদ; ~২০০k জোড়া (I1 ৮৭,৪১৩; I2 ৮৪,৮১৫; I3 ২৫,২৫১) (p.4–5 L605–801)।
- **Solution path annotation:** ChatGPT function-calling দিয়ে বাস্তব API call; “Finish with Final Answer”/“Finish by Giving Up”; **DFSDT** — error propagation ও সীমিত exploration সমস্যা এড়াতে node বাদ দিয়ে নতুন শাখা; শুধু pass করা path রাখা → ১২৬,৪৮৬ (p.5–6 L806–843)।
- **ToolEval:** ground-truth path অসম্ভব (API-র temporal variability, অসীম সমাধান) → ChatGPT judge; **human agreement — pass rate ৮৭.১%, win rate ৮০.৩%** (p.6 L856–869)।
- **ToolLLaMA:** LLaMA-2 7B, positional interpolation-এ context ৪০৯৬ → ৮১৯২ (p.7 L979–980)।
- **Generalization levels:** unseen instruction (Inst.), unseen tool same category (Tool), unseen category (Cat.); oracle API বনাম retriever top-৫ (p.7 L981–997)।

## F. Dataset
- উপরে E।

## G. Evaluation
- Retriever: NDCG@1/@5 বনাম BM25 ও text-embedding-ada-002; reasoning: pass rate; main: pass ও win rate (বনাম ChatGPT-ReAct); OOD: APIBench (TorchHub, TensorHub, HuggingFace) — AST accuracy ও hallucination rate বনাম Gorilla।

## H. Results (author-reported)
- **Retriever:** সব setting-এ BM25 ও ada-002-এর চেয়ে ভালো; single-tool retrieval multi-tool-এর চেয়ে সহজ (Table 2) (p.7 L957–962)।
- **DFSDT:** ReAct ও সমান-budget ReAct@N-এর চেয়ে significantly বেশি pass rate; কঠিন (I2, I3) instruction-এ সুবিধা বেশি (Table 3) (p.7 L963–974)।
- **Main (Table 4):** Vicuna ও Alpaca **শূন্য** pass/win; সব LLM-এ DFSDT > ReAct; ChatGPT+DFSDT GPT-4+ReAct-কে pass rate-এ ছাড়ায়; ToolLLaMA+DFSDT Text-Davinci-003 ও Claude-2-এর চেয়ে ভালো, ChatGPT-এর প্রায় সমান, GPT-4+DFSDT-এর পরে দ্বিতীয়। (Column-split table থেকে পুনর্গঠিত গড়: GPT-4+DFSDT pass ~৭১.১; ToolLLaMA ReAct/DFSDT/DFSDT-Retriever pass ~২৯.০/৬৬.৭/৬৭.৩, win ~৪৭.০/৬০.০/৬৩.১ — ⚠️ PDF-এ যাচাই প্রয়োজন) (p.8 L1199–1217)।
- **Retriever-সহ:** top-৫ retrieved API দিয়ে oracle-এর চেয়েও ভালো — retriever ভালো বিকল্প API খুঁজে পায় (p.8 L1218–1227)।
- **OOD (APIBench):** ToolLLaMA+retriever HuggingFace ও TorchHub-এ Gorilla+BM25 (ZS ও RS)-কে AST accuracy-তে ছাড়ায়; oracle retriever-এ Gorilla-ZS-এর চেয়ে সবসময় ভালো (Table 5) (p.8 L1232–1245)।

## I. Strengths
- **বাস্তব, লাইভ REST API-র বিশাল সংগ্রহ** — synthetic tool-এর পরিবর্তে; multi-tool scenario।
- DFSDT — সাধারণ, model-নিরপেক্ষ reasoning উন্নতি।
- ToolEval-এর human agreement পরিমাপ; open-source সম্পূর্ণ pipeline — পরবর্তী বহু গবেষণার ভিত্তি (StableToolBench ইত্যাদি)।
- Retriever + model একীভূত বাস্তবসম্মত pipeline।

## J. Explicit limitations
- ⚠️ পৃথক limitations/threats section নেই; text-এ স্বীকৃত: API-র temporal variability ও অসীম সমাধান-পথ (ToolEval-এর কারণ) (p.6 L856–858); RapidAPI API-র মান অসম (filtering-এর কারণ)।

## K. Inferred limitations (⚠️ অনুমান)
- **Evaluation validity:** ChatGPT-ই instruction তৈরি, solution annotate, এবং **judge** — teacher-student-judge একই model পরিবার → ToolLLaMA-র “ChatGPT-এর প্রায় সমান” দাবি self-referential bias-প্রবণ; win rate ChatGPT-ReAct-এর বিপরীতে।
- **Live API drift ও reproducibility:** RapidAPI-র API বদলায়/বন্ধ হয় — একই ফল পুনরুৎপাদন কঠিন (পরবর্তীতে StableToolBench ঠিক এই সমস্যা মোকাবিলা করেছে); ToolEval-এর ChatGPT version-নির্ভরতা।
- **Survivorship bias:** শুধু pass করা path দিয়ে training → ব্যর্থতা থেকে শেখা নেই; filtering-এ ~৬৯% API বাদ — “বাস্তব” API-র ভালো-আচরণকারী উপসেট; ভাঙা/অসম্পূর্ণ documentation (P028, P001/P004-এর spec mismatch)-এর বাস্তবতা কম প্রতিফলিত।
- **Instruction realism:** API sample থেকে instruction তৈরি (reverse) — বাস্তব ব্যবহারকারীর লক্ষ্য-চালিত instruction নয়; I3-এর মান human evaluation-এর বিস্তারিত সংখ্যা ছাড়া।
- **Pass rate-এর সংজ্ঞা দুর্বল:** “budget-এর মধ্যে সম্পন্ন” — উত্তরের তথ্যগত সঠিকতা আলাদাভাবে যাচাই নয়।
- **Safety/side effects:** লাইভ API-তে write/destructive call-এর নিরাপত্তা, rate limit, cost — আলোচিত নয় (T3 সংযোগ)।
- Statistical test/variance নেই।

## L. Threats to validity
- ⚠️ আনুষ্ঠানিক section নেই; inferable: construct (LLM judge), external (RapidAPI উপসেট), reproducibility (API drift)।

## M. Reproducibility
- Code, model, data উন্মুক্ত (GitHub) — কিন্তু লাইভ API ও ChatGPT judge-এর কারণে হুবহু পুনরুৎপাদন **মাঝারি**।

## N. Opportunities (hypothesis)
- **Spec-quality-aware tool learning:** ToolBench-এ documentation smell (P028) ও spec defect (P032-এর A–C) inject করে agent robustness পরিমাপ — T6/T4 → T8।
- **API evolution robustness:** ToolBench API-র সময়ের সঙ্গে পরিবর্তন (P022 ToolEVO-র বাস্তব সংস্করণ) — longitudinal re-run।
- **Execution-grounded evaluation:** LLM judge-এর বদলে response/state-ভিত্তিক verifiable oracle (T1-এর oracle গবেষণা — P008 invariant — agent evaluation-এ)।
- **Security-aware tool use:** destructive/authorization-sensitive API call-এ agent আচরণ (P012/P015 ধারণা agent-এর জন্য)।
- **REST testing ↔ agent tool-use সেতু:** RESTler/EvoMaster-এর dependency inference agent planning-এ (multi-tool sequence = producer-consumer chain)।

## O. Relationships
- **Compared with P034 (Gorilla)** — APIBench-এ OOD; Gorilla single-call, ToolLLM multi-step।
- **Foundation for P022** (ToolEVO tool variability) ও tool-learning benchmark ধারা।
- **Relates to P032** (MCP — tool সংখ্যা বৃদ্ধিতে selection সমস্যা; retriever-ধারণা MCP tool filtering-এর বিকল্প)।
- **Relates to P035** (documentation দিয়ে API hallucination প্রশমন)।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract | p.1 L19–38 |
| পূর্ববর্তী কাজের সীমা | p.2 L172–291 |
| Contributions ও findings | p.2–3 L303–437 |
| RapidAPI hierarchy ও filtering | p.4 L582–600; Appendix A.1 L1539– |
| Instruction generation, sampling | p.4–5 L605–801 |
| Solution path, DFSDT | p.5–6 L806–843 |
| ToolEval, human agreement | p.6 L856–869 |
| Retriever (Table 2) | p.6–7 L870–962 |
| DFSDT vs ReAct (Table 3) | p.7 L963–974 |
| ToolLLaMA training, settings | p.7 L979–1001 |
| Main results (Table 4) | p.8 L1012–1217 |
| Retriever integration | p.8 L1218–1227 |
| OOD APIBench (Table 5) | p.8–9 L1230–1318 |
| Conclusion | p.9 L1354–1365 |

**Document integrity:** দুই-কলাম/wrapfigure-এর কারণে p.2-এর লেখা Figure 2 caption ও Table-এর সঙ্গে মিশে গেছে; সূত্র আংশিক; **Table 4 সম্পূর্ণ column-split** — গড় সংখ্যার কলাম-অনুক্রম অনুমিত (PDF-এ যাচাই করতে হবে); Table 2, 3, 5 সংখ্যাও পুনর্গঠন-অনিশ্চিত, তাই এখানে গুণগত দাবি ব্যবহৃত।
