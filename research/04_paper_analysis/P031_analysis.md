# P031 — Identifying and Mitigating API Misuse in Large Language Models

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (related work বাদ, references বাদ; per-model table column-split) · **উৎস:** IEEE TSE author version (arXiv 2503.22821), ১৯ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Terry Yue Zhuo, Junda He, Jiamou Sun, Zhenchang Xing, David Lo, John Grundy, Xiaoning Du (Monash; CSIRO Data61; SMU; ANU)
- **Venue:** IEEE Transactions on Software Engineering, 2026, DOI 10.1109/tse.2026.3651566
- **Cluster:** T7 (secondary: T8 — LLM code generation; T5 — outdated API)
- **ধরন:** Empirical study (LLM code completion/infilling) + taxonomy refinement + LLM-based repair (Dr.Fix)

## B. Motivation
- LLM code generation-এ library API ভুলভাবে ব্যবহৃত হয়; ৫৯০,০০০+ Python library; library evolution LLM-কে বিভ্রান্ত করে (p.1 L34–46)।
- পূর্ববর্তী গবেষণা synthetic/StackOverflow-ধাঁচের প্রশ্নে (GPT-4-এর ৬২% কোডে misuse, ১৮টি Java API-তে) — বাস্তব **IDE completion/infilling** context-এ সাধারণীকরণ অনিশ্চিত (p.1 L49–81)।
- Rule/program-analysis-ভিত্তিক APR শব্দার্থ বোঝে না; LLM-ভিত্তিক repair বেশি উপযোগী হতে পারে (p.2 L94–101)।

## C. Research questions (p.4 L336–356; §5)
- RQ1: code generation-এ LLM কতটা ভালোভাবে API invocation করে (method infilling ও parameter completion)?
- RQ2: বাস্তবে LLM কীভাবে API misuse করে (মানব-দৃষ্টিকোণ থেকে)?
- (RQ3) taxonomy-guided LLM repair (Dr.Fix) কতটা কার্যকর?

## D. Contributions (p.2 L178–184)
- Python ও Java-তে তিনটি LLM-এর API misuse-এর empirical study।
- বিদ্যমান taxonomy (Schlichtig; Wei; He) LLM-প্রেক্ষাপটে অভিযোজিত — **Intent** ও **Hallucination** উপ-শ্রেণি যোগ; Replacement/Outdated বাদ (snippet থেকে নির্ধারণযোগ্য নয়) (p.2 L124–138; p.3 L251–279)।
- **Dr.Fix** (Detect-reason-Fix) — taxonomy-guided, backbone-agnostic LLM APR।
- Public dataset/replication package (প্রকাশের পরিকল্পনা) (p.2 L200–201)।

## E. Methodology
- **Dataset:** The Stack থেকে Python ও Java-তে প্রতিটিতে **৩,০০০ unique fully-qualified API** (একটি API-র একটি নমুনা; ৬৩১ Python ও ৪৮৬ Java repository; ৪,৬৪১ ও ৬,২৫৮ package) (p.5 L507–549)।
- **Tasks:** (১) **API method infilling** — method নাম mask; (২) **API parameter completion** — method নাম দেওয়া, argument mask; context-এর আগের code দেওয়া (p.4 L363–409)।
- **Models:** StarCoder-7B, Qwen2.5-Coder-7B (open, VSCode default hyperparameter), **GitHub Copilot** (GPT-4-distilled, হাতে paste) — ২০২৪-এর শুরুতে (p.4–5 L420–498)।
- **Metrics:** BLEU, CodeBERTScore, **masked element-স্তরে Exact Match**, precision/recall; EM-কে lower bound স্বীকার (p.5–6 L570–666)।
- **Annotation:** EM-ব্যর্থ নমুনা থেকে প্রতি model × element × language-এ ৩০০ random; দুই annotator (৫+ বছর অভিজ্ঞতা), closed coding + axial coding, **Cohen's κ = ০.৯৭**, ~৩০০ ঘণ্টা (p.6 L670–731)।
- **Misuse type:** Intent (বৈধ কিন্তু উদ্দেশ্য-বহির্ভূত API), Hallucination (অস্তিত্বহীন method/parameter), Missing, Redundancy (+ Position) (p.2 L131–138)।
- **Dr.Fix (Fig.9):** detect (misuse চিহ্নিত) → reason (taxonomy দিয়ে কারণ) → fix; backbone: GPT-4o, Qwen2.5-Coder-Instruct, Llama-3.1; তুলনা: সরল prompting, Dr.Fix (w/o taxonomy), Zhang et al.-এর fine-tuned CodeBERT/CodeT5 (Java, DL API); annotated dataset-এর **১০%** নমুনায় মূল্যায়ন (p.11–14 L1499–2141)।

## F. Dataset
- ৬,০০০ API (৩,০০০ × ২ ভাষা); মোট ৩৬,০০০ generation (p.9 L1045–1056); annotated misuse: abstract-এ ৩,২০৯ method + ৩,৪৯২ parameter (৬,৭০১), অন্যত্র “৬,৪৫২” (p.2 L182)।

## G. Evaluation
- RQ1: automatic metric; RQ2: misuse type বণ্টন (Table 2–4); Dr.Fix: BLEU, CodeBERTScore, EM, refusal rate।

## H. Results (author-reported)
- **RQ1:** Python method infilling-এ EM — Qwen2.5-Coder **৮৫.৪%**, StarCoder ৭৫.৬%; Java-তে Qwen২.৫ ৬১.২%, Copilot ৫৩.১%, StarCoder ৪৪.৩% — **Finding 1:** Qwen2.5-Coder সামগ্রিকভাবে সেরা; parameter completion method-এর চেয়ে কঠিন (p.9 L1058–1193)।
- **RQ2:** **Finding 2: Hallucination সবচেয়ে সাধারণ** (StarCoder-এ Java parameter misuse-এর সর্বোচ্চ ৪৩.৩%); Python parameter-এ required parameter বাদ ২৯.০% (StarCoder); method-এ intent error StarCoder ৩০.৪%, Copilot ২৫.০%, Qwen ২৩.৬%; Python-এর dynamic typing ও overlapping library interface প্রধান চ্যালেঞ্জ; model-জুড়ে একই ধরনের error — সাধারণ সমস্যা (p.10–11 L1310–1402)।
- **Dr.Fix:** baseline prompting ও পূর্ববর্তী APR-এর চেয়ে ভালো — **BLEU সর্বোচ্চ +৩৮.৪, EM সর্বোচ্চ +৪০ percentage point**; Java method-এ GPT-4o EM ৩১ → ৭১ (full taxonomy), একটি setting-এ EM ৯২ → ৯৬; CodeBERT/CodeT5 BLEU ১২.৪/২০.১ বনাম GPT-4o+Dr.Fix ৭৯.৪/৮২.৫ (p.13–14 L1813–2141)।

## I. Strengths
- **বাস্তব IDE-ধাঁচের context** (The Stack-এর real code) — synthetic প্রশ্নের চেয়ে প্রাসঙ্গিক; open ও closed model।
- বড় annotation প্রচেষ্টা (৩০০ ঘণ্টা) ও উচ্চ agreement (κ ০.৯৭)।
- Taxonomy-কে নতুন করে না বানিয়ে বিদ্যমান কাঠামো অভিযোজন — তুলনাযোগ্যতা।
- Detection থেকে repair পর্যন্ত — P029/P030-এর “repair সমর্থনের অভাব” gap-এর উত্তর।
- Threats-এ সৎ আলোচনা (single run, closed coding subjectivity)।

## J. Explicit limitations (p.14–15 §6)
- Internal: মানব annotation-এর subjectivity (κ দিয়ে প্রশমন); LLM output-এর stochasticity — **একবার রান**; closed coding-এ ভিন্ন সিদ্ধান্তে ভিন্ন শ্রেণিবিন্যাস; API domain coverage নির্ধারণ কঠিন।
- External: শুধু Python ও Java; Dr.Fix-এর backbone সীমিত; APR baseline তুলনা Java ও DL API-তে সীমিত; **ঘনঘন-ব্যবহৃত API-কেন্দ্রিক — বিরল বা deprecated API-তে সাধারণীকরণ নয়**; annotation ব্যয়বহুল।

## K. Inferred limitations (⚠️ অনুমান)
- **“EM-ব্যর্থতা = misuse” construct সমস্যা:** ground truth developer-এর লেখা code; ভিন্ন কিন্তু বৈধ API (যেমন `requests.get` বনাম `session.get`) “Intent misuse” হিসেবে গণ্য হতে পারে — লেখকরা EM-কে lower bound বলেন, কিন্তু annotation EM-fail নমুনা থেকে, তাই misuse হার নির্ভরশীল।
- **সংখ্যার অসামঞ্জস্য:** annotated নমুনা ৬,৭০১ (abstract) বনাম ৬,৪৫২ (contributions) বনাম “১,২০০ failure samples” (method section) — denominator অস্পষ্ট।
- **Dr.Fix মূল্যায়ন দুর্বল:** annotated dataset-এর ১০% (ছোট নমুনা), যেখানে misuse **আগে থেকে জানা** — বাস্তবে detection ধাপের false positive/negative-এর প্রভাব আলাদাভাবে মাপা হয়নি; repair-এর সঠিকতা BLEU/EM দিয়ে, **execution/test দিয়ে নয়**।
- **Model নির্বাচন পুরোনো:** ২০২৪-এর শুরুর ৭B model ও Copilot (GPT-4-distilled) — ২০২৬-এ প্রকাশিত TSE paper-এর জন্য বর্তমান agentic/frontier coding model অনুপস্থিত।
- **Web/REST API নয়:** library function call; HTTP client-এর endpoint/parameter misuse (OpenAPI-নির্ভর) — T8-এর tool-call সমস্যার সঙ্গে সাদৃশ্য থাকলেও পরীক্ষিত নয়।
- Copilot হাতে paste — পুনরুৎপাদনযোগ্যতা কম; dataset “পরিকল্পিত” প্রকাশ।

## L. Threats to validity
- উপরে J; inferable: construct (EM-fail-ভিত্তিক misuse), measurement (BLEU-ভিত্তিক repair), recency।

## M. Reproducibility
- Replication package [20] উল্লেখিত, code/dataset GitHub-এ প্রকাশের পরিকল্পনা; Copilot ও closed model নির্ভরতা — **মাঝারি**।

## N. Opportunities (hypothesis)
- **LLM REST/OpenAPI client-code misuse study:** LLM-generated HTTP client code-এ endpoint hallucination, required parameter বাদ, auth/pagination misuse — OpenAPI spec দিয়ে স্বয়ংক্রিয় যাচাই (spec-as-oracle); P035 (CloudAPIBench) ও P034 (Gorilla)-এর সঙ্গে T7↔T8 সংযোগ।
- **Execution-validated repair benchmark:** Dr.Fix-ধাঁচের repair test/runtime দিয়ে যাচাই; detection-error-সহ end-to-end।
- **Spec/documentation-grounded generation:** IDL (P016)/OpenAPI constraint-কে constrained decoding-এ ব্যবহার করে hallucination ও missing parameter প্রতিরোধ।
- **Deprecated/rare API ও security API misuse** (P024, P029) — লেখকদের স্বীকৃত gap।
- Agentic coding tool (Claude Code, Cursor agent)-এ misuse হার ও self-repair ক্ষমতা।

## O. Relationships
- **Builds on P030/MUBench lineage** ও DL-library misuse taxonomy (Wei, He)।
- **Answers P029's** LLM ও repair gap (generic API-তে)।
- **Complements P024** (deprecated API — evolution-কেন্দ্রিক) ও **P035** (low-frequency API hallucination, documentation augmentation)।
- **Parallel to P033/P034** (tool/API call hallucination in LLM agents)।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract (৩,২০৯/৩,৪৯২; +৩৮.৪ BLEU, +৪০% EM) | p.1 L15–25 |
| পূর্ববর্তী synthetic study (৬২%) | p.1 L49–53 |
| IDE context gap | p.1 L69–81 |
| Taxonomy অভিযোজন (Intent, Hallucination) | p.2 L124–138; p.3 L251–279 |
| Contributions | p.2 L178–184 |
| RQs | p.4 L336–356 |
| Tasks (infilling, parameter completion) | p.4 L363–409 |
| Model নির্বাচন, hyperparameter | p.4–5 L420–498 |
| Dataset (The Stack, ৩,০০০ API × ২) | p.5 L507–549 |
| Metrics | p.5–6 L570–666 |
| Annotation, κ ০.৯৭ | p.6 L670–731 |
| RQ1 ফল (Finding 1) | p.9 L1045–1193 |
| RQ2 ফল (Finding 2) | p.10–11 L1310–1402 |
| Dr.Fix workflow | p.11–12 L1499–1576 |
| Dr.Fix মূল্যায়ন | p.12–14 L1678–2141 |
| Threats | p.14–15 L2222–2323 |

**Document integrity:** দুই-কলামের reading order কয়েক জায়গায় মিশ্রিত; BLEU সূত্র আংশিক; Table 2–6 (misuse distribution, metric) column-split — নির্বাচিত সংখ্যা text থেকে; Fig.1–9 অনুপস্থিত।
