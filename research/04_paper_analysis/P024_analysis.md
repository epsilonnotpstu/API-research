# P024 — LLMs Meet Library Evolution: Evaluating Deprecated API Usage in LLM-based Code Completion

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references বাদ) · **উৎস:** ICSE 2025 version (arXiv 2406.09834), ১৩ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Chong Wang, Kaifeng Huang, Jian Zhang, Yebo Feng, Lyuye Zhang, Yang Liu, Xin Peng (NTU Singapore; Tongji; Fudan)
- **Venue:** ICSE 2025, DOI 10.1109/icse55347.2025.00245
- **Cluster:** T5 (secondary: T8 — LLM ও API জ্ঞান; T7 — outdated/incorrect API usage)
- **ধরন:** Empirical evaluation study + দুটি lightweight mitigation baseline

## B. Motivation
- Library দ্রুত বিবর্তিত হয় (যেমন `torch.gels` → `torch.lstsq` → `torch.linalg.lstsq`); LLM code completion পুরোনো API সুপারিশ করতে পারে (p.1 L60–73)।
- পূর্ববর্তী কাজ ভুল function name (Izadi: token error-এর ২৩%) ও hallucination দেখিয়েছে, কিন্তু **deprecated API usage** গভীরভাবে অধ্যয়িত নয় (p.1 L74–90)।

## C. Research questions (p.2 L99–125; RQ4 p.10)
- মূল প্রশ্ন: LLM code completion-এ deprecated ও replacing API usage-এর অবস্থা (AUP, DUR) ও মূল কারণ কী?
- RQ1 model perspective; RQ2 prompt perspective; RQ3 library perspective; RQ4 প্রস্তাবিত fix কতটা কার্যকর?

## D. Contributions (p.2 L110–117)
- LLM code completion-এ deprecated API usage-এর প্রথম study (model, prompt, library দৃষ্টিকোণ)।
- দুটি lightweight fix — **REPLACEAPI** ও **INSERTPROMPT** — ভবিষ্যৎ গবেষণার baseline।
- Library evolution × LLM-driven development-এর ভবিষ্যৎ দিক।

## E. Methodology
- **API mapping:** ৮টি Python library (NumPy, Pandas, scikit-learn, SciPy, seaborn + TensorFlow, PyTorch, Transformers), Jan 2019-পরবর্তী version-এর documentation/changelog থেকে হাতে; দুই লেখক স্বাধীনভাবে, তৃতীয়জন মীমাংসা, **Jaccard ৯১.৮%**; ২৪৭টি প্রাথমিক mapping → instance থাকা **১৪৫টি** (p.3 L336–358; p.4 L421–425)।
- **Prompt construction:** Sourcegraph থেকে ১১৩,৬৬০ Python file; AST + lightweight type/alias resolution দিয়ে function খুঁজে **৯,০২২ outdated (O) ও ১৯,১০৩ up-to-date (U) function**; API invocation line-এর আগের লাইনগুলো = line-level completion prompt (মোট ২৮,১২৫) (p.3–4 L362–452)।
- **Models:** CodeGen-350M/2B/6B-mono, DeepSeek-Coder-1.3B-instruct, StarCoder2-3B, CodeLlama-7B-Python, GPT-3.5-turbo (Jan 2024); greedy decoding, max ৫০ token (p.4–5 L455–556)।
- **Annotation:** completion-এর FQN → DepC / RepC / Others; **AUP** = plausible (DepC বা RepC) অনুপাত; **DUR** = plausible-এর মধ্যে DepC অনুপাত; RUR (reference usage rate) সহায়ক (p.5 L527–599; p.7 L799–807)।
- **Root cause probing:** open model-এ dep বনাম rep-এর generative log-likelihood, paired t-test (p.6–7 L742–762); prompt context-similarity (Jaccard of variable/call names) (p.7 L827–846)।
- **Fix (Alg.1–3):** REPLACEAPI — decoding-এ deprecated token কেটে replacement বসিয়ে বাকিটা regenerate (white-box LLM-এ); INSERTPROMPT — `# {dep} is deprecated, use {rep} instead…` comment যোগ করে regenerate (p.9 L1035–1071)।

## F. Dataset ও setup
- উপরে E; RQ4 মূল্যায়ন: U-থেকে যে prompt-এ model DepC দিয়েছে (ground-truth আছে) — Fixed Rate, Edit Similarity, Exact Match (p.10 L1133–1175)।

## G. Evaluation
- AUP, DUR, RUR; t-test; contextual similarity; FR/ES/EM।

## H. Results (author-reported)
- **RQ1:** AUP মাত্র ৯–২৩% (CodeLlama-7B সর্বোচ্চ ২৩.৪%, StarCoder2 সর্বনিম্ন ৯.৩%; GPT-3.5 ১৩.২%); **DUR ২৫–৩৮%**, বড় model-এ বেশি (GPT-3.5 ৩৭.৪%) (p.5–6 L591–714)। কারণ: training data-য় deprecated usage (৯,০২২ বনাম ১৯,১০৩ — উল্লেখযোগ্য অংশ) ও inference-এ deprecation জ্ঞানের অভাব; O prompt-এ dep-এর likelihood rep-এর চেয়ে significantly বেশি, U-তে উল্টো (p.6–7 L716–766)।
- **RQ2:** O prompt-এ DUR **৭০–৯০%**, U-তে ৯–১৮%; RUR উভয়ে ৭০–৯০% — অর্থাৎ model মূলত **context-এ যা ছিল তাই অনুসরণ করে**; O–U context similarity মাত্র ০.২৬৬ (p.7 L789–850)।
- **RQ3:** library-ভেদে DUR ~০–১০০%; NumPy, scikit-learn, TensorFlow-এ কম (≤২০%), SciPy (৩০–৫০%) ও **PyTorch (৫০–৭০%)**-এ বেশি; শুধু package সরানো (torch → torch.linalg)-ধরনের ছোট পরিবর্তনে বিভ্রান্তি বেশি — O/U context similarity বেশি হলে DUR বেশি (Table IV) (p.8–9 L904–991)।
- **RQ4:** REPLACEAPI — সব open model-এ **FR >৮৫%**, ES >৮০%; বড় model-এ FR কিছুটা কমে (decoding intervention-এ সংবেদনশীল); ভুল মূলত return value/argument; INSERTPROMPT — FR ২৫.৭–৯৭.২% (DeepSeek-instruct ৯৩.৫%), কিন্তু ES/EM কম; REPLACEAPI black-box model (GPT-3.5)-এ প্রয়োগ অসম্ভব (p.10 L1100–1192)।
- **Implications:** deprecated usage alert/validation, model editing, **RAG দিয়ে up-to-date documentation**, multi-agent library-upgrade pipeline (p.11 L1247–1317)।

## I. Strengths
- বাস্তব GitHub code থেকে prompt — synthetic নয়; বড় নমুনা (২৮k prompt, ৭ model, ৮ library)।
- Mapping সংগ্রহে দুই annotator + Jaccard agreement।
- **Root cause-এর পরিমাণগত প্রমাণ** (likelihood t-test, context similarity) — শুধু বর্ণনামূলক নয়।
- প্রস্তাবিত fix সরল ও স্পষ্টভাবে “baseline” হিসেবে অবস্থানকৃত; code ও data উন্মুক্ত।

## J. Explicit limitations (p.11 Threats)
- Internal: Python dynamic — lightweight type/alias resolution কিছু call মিস করতে পারে (bias দেয় না বলে দাবি); শুধু function-level deprecation, **parameter-level deprecation নয়**।
- External: library ও LLM নির্বাচন; শুধু Python (Java/C# নয়)।
- INSERTPROMPT zero-shot, per-model tuning নয়; Others completion-এর functional correctness মূল্যায়ন ভবিষ্যৎ কাজ (p.5 L559–569)।

## K. Inferred limitations (⚠️ অনুমান)
- **DUR-এর অর্থ context-নির্ভর:** O dataset-এ prompt আগে থেকেই পুরোনো-version code-এর context — সেখানে deprecated API predict করা “ভুল” নয়, বরং context-সঙ্গত (environment পুরোনো library ব্যবহার করতে পারে)। Overall DUR (২৫–৩৮%) O ও U-র মিশ্রণের অনুপাতের উপর নির্ভরশীল (৯k:১৯k), model-এর অন্তর্নিহিত প্রবণতা নয়।
- **Model নির্বাচন পুরোনো/ছোট:** ≤৭B open model ও GPT-3.5; GPT-4-class, Claude, DeepSeek-V2/Qwen2.5-Coder নেই — ২০২৫-এর frontier আচরণ অজানা।
- **Data contamination:** prompt-গুলো public GitHub থেকে, model-এর training-এ থাকতে পারে — DUR আংশিক memorization প্রতিফলিত করে (লেখকরা root cause হিসেবে উল্লেখ করেন কিন্তু threat হিসেবে নয়)।
- **Fix-এর বাস্তবতা:** উভয় fix-এর জন্য **dep→rep mapping আগে থেকে জানা** দরকার — বাস্তবে এটি নিজেই কঠিন সমস্যা (P021 EC: migration mapping); RAG baseline পরীক্ষা হয়নি (শুধু প্রস্তাব)।
- AUP ৯–২৩% — “Others” বেশিরভাগ; তাই DUR একটি ছোট উপসেটে (plausible) গণিত — statistical confidence interval রিপোর্ট নেই।
- Line-level completion — chat/agentic code generation (বর্তমান প্রধান ব্যবহার) মূল্যায়িত নয়।

## L. Threats to validity
- উপরে J; inferable: construct (DUR-এর context-dependence), contamination, external (ছোট model)।

## M. Reproducibility
- Code ও data উন্মুক্ত [91]; open model Hugging Face থেকে; GPT-3.5 version deprecation ঝুঁকি — **উচ্চ** (open অংশে)।

## N. Opportunities (hypothesis)
- **Web/REST API deprecation × LLM:** LLM-generated client code বা agent tool call-এ deprecated REST endpoint/OpenAPI `deprecated: true` operation ব্যবহারের হার — P022 (tool variability) ও P035 (API documentation দিয়ে hallucination প্রশমন)-এর সঙ্গে একীভূত benchmark।
- **Deprecation-aware RAG বনাম model editing বনাম decoding constraint** — নিয়ন্ত্রিত তুলনা (লেখকদের প্রস্তাবিত দিকগুলোর empirical মূল্যায়ন)।
- **Automatic dep→rep mapping mining** (changelog, OpenAPI diff, P018/P017-generated spec diff) — fix-এর পূর্বশর্ত স্বয়ংক্রিয় করা।
- **Parameter-level ও behavioural deprecation** (P023-এর BC taxonomy) — LLM কি argument পরিবর্তন জানে?
- Frontier/agentic model-এ পুনরাবৃত্তি (replication) — model আকার বাড়লে DUR বাড়ে কিনা।

## O. Relationships
- **Complements P022** (LLM tool variability — invocation স্তর) ও **P035** (CloudAPIBench — low-frequency API hallucination, documentation augmentation)।
- **Builds on** Python API deprecation গবেষণা (Wang et al. [25]) ও P021-এর API evolution সাহিত্য।
- **Links P031** (LLM API misuse, T7) — deprecated usage একটি misuse শ্রেণি।
- **Links P023** (BC ও client impact) — LLM একটি নতুন ধরনের “client”।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract (৭ LLM, ১৪৫ mapping, ২৮,১২৫ prompt) | p.1 L20–41 |
| Motivation (PyTorch উদাহরণ) | p.1 L60–73 |
| RQ১–৩, contributions | p.2 L99–125 |
| API mapping সংগ্রহ (Jaccard ৯১.৮%) | p.3 L336–358 |
| Prompt construction, type/alias resolution | p.3–4 L362–452 |
| ৯,০২২/১৯,১০৩ function | p.4 L421–425 |
| Models | p.4–5 L455–556 |
| AUP/DUR সংজ্ঞা | p.5 L527–599 |
| RQ1 ফল (AUP ৯–২৩%, DUR ২৫–৩৮%) | p.5–6 L591–714 |
| Root cause (t-test) | p.6–7 L716–766 |
| RQ2 (O ৭০–৯০%, U ৯–১৮%; similarity ০.২৬৬) | p.7 L769–850 |
| RQ3 (library-ভেদ, Table IV) | p.8–9 L852–991 |
| Fix algorithm | p.9 L993–1084 |
| RQ4 (FR >৮৫%; ২৫.৭–৯৭.২%) | p.10 L1098–1192 |
| Implications, threats | p.11 L1247–1317 |

**Document integrity:** দুই-কলামের reading order ব্যাপকভাবে মিশ্রিত (দুটি কলামের লাইন একই লাইনে জোড়া লেগেছে, বিশেষত p.2–5, p.10–11); Table I–V column-split; Fig.3–5 অনুপস্থিত; algorithm আংশিক। সংখ্যা চলমান text ও summary box থেকে যাচাইকৃত।
