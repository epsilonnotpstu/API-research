# P034 — Gorilla: Large Language Model Connected with Massive APIs

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (related work বাদ, appendix বাদ, references বাদ) · **উৎস:** NeurIPS 2024 version (arXiv 2305.15334), ১৮ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Shishir G. Patil, Tianjun Zhang, Xin Wang, Joseph E. Gonzalez (UC Berkeley; Microsoft Research)
- **Venue:** NeurIPS 2024, DOI 10.52202/079017-4020
- **Cluster:** T8 (secondary: T5 — API documentation পরিবর্তনে অভিযোজন; T7 — API hallucination/misuse)
- **ধরন:** Dataset (APIBench) + retriever-aware fine-tuned model + evaluation metric (AST sub-tree matching)

## B. Motivation
- GPT-4-ও API call-এ সঠিক argument দিতে ব্যর্থ ও API usage hallucinate করে (p.1 L18–20)।
- পূর্ববর্তী tool-integration ছোট, সুনথিভুক্ত API set ধরে — web-scale, ওভারল্যাপিং, পরিবর্তনশীল লক্ষ লক্ষ API এক context-এ রাখা অসম্ভব; নতুন benchmark দরকার (p.1–2 L49–54, L120–123)।

## C. Research questions
- ⚠️ আনুষ্ঠানিক RQ নেই; পরীক্ষিত: zero-shot ও retrieval setting-এ AST accuracy ও hallucination; retriever-aware training-এর প্রভাব; test-time documentation পরিবর্তনে অভিযোজন; constraint-aware API selection।

## D. Contributions
- **APIBench:** TorchHub, TensorFlow Hub ও HuggingFace-এর ML model API (মোট **১,৬৪৫ API call**), প্রতি API-তে ১০টি self-instruct instruction (~১১,০০০+ instruction–API জোড়া) (p.2 L125–135; p.4 L218–220; p.9 L1199–1200)।
- **Gorilla:** retriever-aware fine-tuned **LLaMA-7B**।
- **AST sub-tree matching** — functional correctness ও hallucination-এর সংজ্ঞা ও পরিমাপ (p.5 L325–348)।

## E. Methodology
- **Dataset curation:** HuggingFace-এ ~২০৩,৬৮১ model — দুর্বল documentation বাদ দিয়ে প্রতি domain-এ top-২০ (৩৬ domain) → ৯২৫; TF Hub v2-এর ৮০১ থেকে ৬২৬; TorchHub ৯৪/৯৫; প্রতি model card → JSON (domain, framework, functionality, api_name, api_call, api_arguments, environment requirements, example code, performance, description) — RESTful API-তেও সাধারণীকরণযোগ্য বলে দাবি (p.3–4 L197–267)।
- **Instruction generation:** GPT-4 self-instruct, প্রতি hub-এ ৬টি হাতে-লেখা উদাহরণ (মোট ১৮ — একমাত্র হাতে তৈরি data), API নাম/hint ছাড়া instruction (p.4 L268–276)।
- **Training:** instruction → chat-style; with/without retriever; retriever-aware: prompt-এ “Use this API documentation for reference: <doc>” — test-time documentation পরিবর্তনে অভিযোজনের জন্য (p.4–5 L281–307)।
- **Constraints:** parameter size, accuracy lower bound ইত্যাদি (p.4–5 L286–302; p.9 L979–989)।
- **Evaluation:** AST-এ candidate call reference-এর sub-tree কিনা; **hallucination = database-এর কোনো API-র sub-tree নয় (কাল্পনিক tool)**; ভুল API = error (আলাদা) (p.5 L325–348)।
- **Baselines:** GPT-4 (0314), GPT-3.5-turbo (0301), Claude-v1, LLaMA-7B; retriever: zero-shot, BM25 (top-১), GPT-Index (text-davinci-003), Oracle; self-instruct pair থেকে holdout test (p.6 L412–431)।

## F. Dataset
- উপরে E।

## G. Evaluation
- AST accuracy, hallucination rate, wrong-API error; constraint subset (TorchHub-এর ৬৫.২৬%)।

## H. Results (author-reported)
- **Zero-shot fine-tuned Gorilla:** state-of-the-art — **GPT-4-এর চেয়ে ২০.৪৩%, ChatGPT-এর চেয়ে ১০.৭৫% ভালো**; LLaMA-র চেয়ে সর্বোচ্চ ৮৩% (p.7 L523–524)।
- Retriever ছাড়া train করা model-এ test-time oracle doc সামান্য প্রভাব (TensorHub −০.৮৮%, HF +০.৯৭%); BM25/GPT-Index দিলে **উল্লেখযোগ্য পতন** (TorchHub −২১.৫০%, HF −৪৭.৫৭%) — অ-অনুকূল retriever বিভ্রান্ত করে (p.7 L526–531)।
- **Retriever-aware training (oracle doc সহ):** TorchHub +১২.৩৭%, HF +২৩.৪৬%; কিন্তু test-time GPT-Index দিলে −২৯.২০%, BM25 −৫২.২৭% — ভালো retriever থাকলে retriever-aware training, না থাকলে zero-shot fine-tuning (p.7–8 L793–845)।
- **Hallucination:** GPT-4/GPT-3.5 zero-shot-এ ব্যাপক hallucination (যেমন যেকোনো GitHub repo নাম দিয়ে `AutoModel.from_pretrained`); **GPT-3.5 GPT-4-এর চেয়ে কম hallucinate** করে — সব setting-এ (p.8 L939–945)।
- **Test-time doc changes:** ResNet-50 → ResNet-101 backbone পরিবর্তন ও registry পরিবর্তন (pytorch/vision → NVIDIA) — retriever-aware Gorilla অভিযোজিত (গুণগত উদাহরণ, Fig.6) (p.8–9 L950–974)।
- **Constraints:** সব model-এ accuracy কমে; Gorilla zero-shot-এ সর্বোচ্চ, retrieval-এ GPT-3.5-এর সমান (Table 3) (p.9 L1173–1176)।

## I. Strengths
- **API hallucination-এর স্পষ্ট, পরিমাপযোগ্য সংজ্ঞা** (AST sub-tree) — পরবর্তী গবেষণায় (P033 APIBench OOD, P035) ব্যবহৃত।
- Retrieval ও fine-tuning-এর মিথস্ক্রিয়া নিয়ে অ-স্বজ্ঞাত ও গুরুত্বপূর্ণ ফল — খারাপ retriever ক্ষতি করে।
- Documentation পরিবর্তনে অভিযোজন — T5 (evolution)-এর সঙ্গে প্রাথমিক সেতু।
- Code, model, data, demo উন্মুক্ত; ছোট open model দিয়ে closed model-কে ছাড়ানো।

## J. Explicit limitations
- ⚠️ পৃথক limitations section নেই; স্বীকৃত: ML domain বেছে নেওয়া হয়েছে চ্যালেঞ্জিং হওয়ায়; ML API skewed data-তে biased prediction দিতে পারে (broader impact) (p.9 L1196–1202); execution “এই paper-এর focus নয়” (p.5 L320)।

## K. Inferred limitations (⚠️ অনুমান)
- **Train–test leakage-প্রবণ split:** holdout একই self-instruct pool থেকে instruction-স্তরে ভাগ — একই API train ও test-এ; Gorilla মূলত **memorized API catalogue**-এর উপর মূল্যায়িত, সত্যিকারের unseen API নয় (P033-এর tool/category-স্তরের OOD-এর তুলনায় দুর্বল)।
- **অসম তুলনা:** HuggingFace-এ Gorilla ছাড়া অন্য model-এর শুধু domain নাম যাচাই (multiple-choice-তে রূপান্তর) (p.7 L521–522) — model-জুড়ে metric অভিন্ন নয়।
- **REST API নয়:** ML model hub call (`torch.hub.load`) — single function call, HTTP semantics, authentication, multi-step, state নেই; শিরোনামের “Massive APIs” দাবি ML-hub-এ সীমিত।
- **Execution নেই** — AST match = syntactic/argument সাদৃশ্য; call আসলে কাজ করে কিনা পরীক্ষিত নয়।
- **GPT-4 instruction তৈরি করেছে এবং GPT-4 baseline** — distribution GPT-4-এর ভাষা; বাস্তব ব্যবহারকারীর প্রশ্ন নয়।
- **সংখ্যার অসামঞ্জস্য:** TF Hub “৬৯৬ API call” (intro) বনাম “৬২৬” (method); TorchHub ৯৪ বনাম ৯৫।
- Documentation-change অভিযোজন কেবল গুণগত দুটি উদাহরণ — পরিমাণগত মূল্যায়ন নেই (P022 পরে এটি করে)।
- পুরোনো baseline checkpoint (২০২৩) — NeurIPS 2024 সংস্করণেও বর্তমান model অনুপস্থিত।

## L. Threats to validity
- ⚠️ আনুষ্ঠানিক section নেই; inferable: construct (AST ≠ execution), internal (split leakage), external (ML hub ≠ web API)।

## M. Reproducibility
- Code, model, APIBench উন্মুক্ত (gorilla.cs.berkeley.edu) — **উচ্চ**; closed baseline checkpoint অবসরপ্রাপ্ত।

## N. Opportunities (hypothesis)
- **REST/OpenAPI APIBench:** OpenAPI-ভিত্তিক hallucination benchmark — endpoint/parameter hallucination AST-এর বদলে **spec-validation + execution** দিয়ে (P031, P035-এর সঙ্গে T7↔T8)।
- **API-level unseen split** ও time-based split (documentation version) — memorization বনাম generalization পৃথক করা।
- **Retriever-robust training:** noisy/incorrect retrieved doc-এ robustness (খারাপ retriever ক্ষতিকর ফলাফলের সমাধান) — hard-negative doc training।
- **Constraint-aware selection for web APIs:** cost, latency, rate-limit, SLA (P009/P010-এর pricing/cost ধারণা) — agent API selection।
- Documentation-change robustness-এর পরিমাণগত benchmark (P022/P024-এর সঙ্গে)।

## O. Relationships
- **Compared in P033** (ToolLLaMA OOD on APIBench); Gorilla single-call বনাম ToolLLM multi-step।
- **Foundation for P035** (API hallucination ও documentation augmentation; low-frequency API)।
- **Relates to P022** (tool variability — documentation change-এর পরবর্তী গবেষণা) ও **P024** (deprecated API)।
- **Relates to P031** (LLM API misuse — hallucination শ্রেণি)।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract | p.1 L17–31 |
| Web-scale API চ্যালেঞ্জ | p.1–2 L49–54, L120–123 |
| APIBench overview (৯৪/৬৯৬/৯২৫) | p.2 L125–135 |
| Dataset curation (৬২৬, ১,৬৪৫) | p.3–4 L197–267 |
| Instruction generation | p.4 L268–276 |
| Gorilla training, retriever-aware | p.4–5 L281–319 |
| Constraint-এর উদাহরণ | p.4–5 L286–302 |
| AST sub-tree, hallucination সংজ্ঞা | p.5 L325–348 |
| Baselines, retrievers, holdout | p.6 L412–431 |
| HF-এ অসম মূল্যায়ন | p.7 L521–522 |
| Zero-shot ফল (+২০.৪৩%/+১০.৭৫%) | p.7 L523–531 |
| Retriever-aware ফল (Table 2) | p.7–8 L793–845 |
| Hallucination পর্যবেক্ষণ | p.8 L939–945 |
| Documentation change (Fig.6) | p.8–9 L950–974 |
| Constraint ফল (Table 3) | p.9 L979–1176 |
| Conclusion, broader impact | p.9 L1180–1202 |

**Document integrity:** Body সম্পূর্ণ; Table 1–3 column-split (per-model per-hub সংখ্যা পুনর্গঠন করা হয়নি — শতাংশগত পার্থক্য text থেকে); Fig.1–6 অনুপস্থিত; ছোট টাইপো (“his suggests”) মূলেই।
