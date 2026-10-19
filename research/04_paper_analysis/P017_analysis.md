# P017 — OOPS: Automated Generation of REST API Specification via LLMs

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references বাদ; Table 4–7-এর per-API সংখ্যা column-split, সারাংশ text থেকে) · **উৎস:** arXiv 2601.12735v2 (৭ Jun 2026), ১৮ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Hao Chen, Yunchun Li, Chen Chen, Fengxu Lin, Wei Li (Beihang University)
- **Venue:** Journal of Systems and Software, 2026, DOI 10.1016/j.jss.2026.112914
- **Cluster:** T4 (secondary: T8 — LLM agent workflow)
- **ধরন:** LLM-agent-ভিত্তিক static analysis technique + empirical evaluation

## B. Motivation
- Developer-রক্ষিত OAS প্রায়ই পুরোনো/ভুল/অসম্পূর্ণ (Kim 2022; Martin-Lopez 2022) (p.1 L54–57)।
- বিদ্যমান generator-এর সীমা: APICARV — manual deployment ও crawler; Respector (P018) ও ExpressO — technology-specific rule (Java/Express.js); LLM-ভিত্তিক Chaplia — শুধু Node.js; LRASGen — মানুষের লেখা regex (p.1–3 L59–92, L273–391)।
- LLM প্রয়োগে তিন চ্যালেঞ্জ: context length (C1), technology-specific rule নির্ভরতা (C2), hallucination (C3) (p.3 L244–271)।

## C. Research questions (p.8 L1010–1014, L896–987)
- RQ1 effectiveness (বনাম ৩ baseline), RQ2 ablation, RQ3 base LLM-এর প্রভাব, RQ4 context efficiency/cost।

## D. Contributions (p.2)
- প্রথম technology-agnostic, LLM-static-analysis-ভিত্তিক OAS generation (OOPS)।
- API dependency graph দিয়ে file association (context সীমা)।
- Multi-stage generation + self-refine (hallucination প্রশমন)।
- ১২টি API (৫ language, ৮ framework)-এ মূল্যায়ন; code ও public dataset GitHub-এ।

## E. Methodology
- **Step 0 — Technology analyzer:** language/framework শনাক্ত → সব prompt-এ role-play (p.4 L411–433)।
- **Step 1 — Endpoint method extraction (Alg.1):** file-level API entry detector — APIEntry = (Path, Handler, Tag∈{LOCAL, REF}); iterative loop, CoT, tool-calling দিয়ে structured output; path parameter `{param}` normalization; non-binary file-এর path দেখে pre-filter (p.4–6 L420–738)। File dependency analyzer — REF handler কোন file-এ, list/read/search tool; invalid path-এ self-refine। **API dependency graph (DAG):** file = node, handler reference = edge; endpoint method extractor topological ক্রমে subgraph পড়ে পূর্ণ path + HTTP method (ALL বিকল্পসহ) নির্ণয় (p.5 L592–632)।
- **Step 2 — OAS generation (Alg.2):** req ও resp specification generator আলাদা (multi-stage); syntactic hallucination (Table 1: JSON error) rule-ভিত্তিক মেরামত + অমীমাংসিত `$ref`-এ LLM feedback; semantic hallucination (OAS version মিশ্রণ, Fig.5) কমাতে **Swagger 2.0 fragment চাওয়া** তারপর Swagger Codegen দিয়ে OpenAPI 3.0.4-এ রূপান্তর; schema hash দিয়ে `components/schemas`-এ reference পুনর্গঠন (p.6–7 L740–1006)।
- Implementation: Python ~৩,০০০ LoC (Respector >১০,০০০); Instructor, JsonRef, JSON Repair; **GPT-5 mini** (RQ1/2/4), temperature ০ (p.9–10 L1347–1359)।

## F. Dataset ও setup (Table 2)
- **১২টি API:** RealWorld (Go/Gin), Lin-CMS (Py/Flask), Management (Py/FastAPI), CMS (JS/Koa), Accountill ও ProShop (Express.js), Proxy-Print, Ur-Codebin, Education-1 (Spring Boot), Cassandra (Jersey), Education-2 (Go/Gin), Laravel-Blog (PHP) — ৮ open-source + **৪ proprietary (campus network-এর web app)**, ২.২K–৩৭.৪K LoC (p.8–9 L990–1180)।
- **Ground truth:** ২ জন বিশেষজ্ঞ স্বাধীনভাবে source code (ও developer OAS) থেকে OAS তৈরি করে consensus (p.9 L1189–1191)।
- **Baselines:** APICARV (৩০ মিনিট crawling, ১০ মিনিট পরে manual login), ExpressO, Respector — প্রতিটি নিজ প্রযোজ্য API-তে; Education-2 ও Laravel-Blog-এ কোনো baseline নেই; LLM-ভিত্তিক পদ্ধতি runnable না থাকায় তুলনা হয়নি (p.9 L1194–1225)।
- **Correctness সংজ্ঞা:** endpoint = method + normalized path; parameter = name + type + location; response = status + type + MIME (**শুধু 2xx**); constraint = ১৩ type, type ও value উভয়ই মিল (p.9 L1227–1244)।

## G. Evaluation
- Precision/Recall/F1, চার মাত্রায়; ablation (Variant 1: ReAct agent; Variant 2: single-pass); ৫টি LLM; LLM call, token, file association, খরচ।

## H. Results (author-reported)
- **RQ1:** endpoint P/R ৯৯.২/৯৮.৫%; request parameter ৯৭.২/৯৭.৪%; response ৯৭.৩/৯৬.৮%; constraint ৯২.৩/৯২.৮%; baseline-এর তুলনায় গড় F1 উন্নতি **৪১.৫%, ৬০.২%, ৭০.৪%, ৪৩.৬%** (p.10–12 L1297–1926)।
- **ব্যর্থতার ধরন:** non-standard endpoint registration (Spring Security filter-এ login; Laravel `authenticate`); static resource/HTML endpoint false positive; nested request body flatten করা; query param-কে body ধরা; RESTful best-practice থেকে **201/204 “অনুমান”** যেখানে framework 200 দেয়; `limit ≥ 0`-এর মতো অ-প্রয়োগকৃত constraint যোগ; ১৫০+ অক্ষরের regex-এ bracket ভুল (p.10–12)।
- **শক্তির উদাহরণ:** class inheritance থেকে field; Mongoose `timestamps`-এর implicit `createdAt/updatedAt` (p.11 L1844–1857)।
- **RQ2:** Variant 1 (ReAct) — precision −৯.০%, **recall −৪৩.৮%** (agent অসম্পূর্ণ অন্বেষণে থেমে যায়); endpoint step-এর অবদান গড় F1 +৩৬.৯%; generation step-এর অবদান +১৯.২/+২৪.৮/+২৩.০% (p.12 L1927–1947)।
- **RQ3:** Gemini 3 Flash endpoint/parameter/response-এ শ্রেষ্ঠ; GPT-5 mini constraint-এ; Qwen3-Coder-Plus মাঝারি (Laravel-Blog response F1 ১৩.৩%); GPT-5 nano ও Gemini 2.0 Flash-Lite দুর্বল — Flash-Lite দুটি API-তে dependency graph-ই তৈরি করতে পারেনি (p.12–13)।
- **RQ4:** endpoint step গড় ৩৭৫.২৫ LLM call, গড় input ≤১.৯২K token; generation step ৩১৭.৭৫ call, ≤৫.৫৯K (সর্বোচ্চ ১৬.১৩K); file association depth ≤৩; **গড় খরচ $০.৪১/API** (p.13–14 L2627–2703)।

## I. Strengths
- **Technology-agnostic** — ৫ language, ৮ framework; rule-based tool-এর (Respector ~১৬০ rule) প্রধান দুর্বলতা দূর।
- Data-leakage প্রশমনে ৪টি proprietary API — LLM paper-এ বিরল ও প্রশংসনীয়।
- Correctness criteria স্পষ্ট ও কঠোর (type, location, constraint value exact)।
- Ablation, multi-LLM ও খরচ বিশ্লেষণ — ব্যবহারিক সিদ্ধান্তে সহায়ক।
- Failure case-এর সৎ ও বিস্তারিত বিশ্লেষণ; code ও public data উন্মুক্ত।

## J. Explicit limitations (p.14 §6; conclusion)
- Data leakage — open-source API training data-তে থাকতে পারে (developer OAS-এর হুবহু output দেখা যায়নি; proprietary API দিয়ে প্রশমন)।
- Prompt ও hyperparameter প্রভাব (temperature ০)।
- সব language/framework কভার নয়; proprietary framework বা বিরল language-এ অজানা।
- **শুধু 2xx response** — 4xx/5xx ও middleware-স্তরের error future work।
- Business-logic ভুল বোঝা (semantic hallucination) — future: ExecutionAgent-ধাঁচে API deploy করে dynamic validation।

## K. Inferred limitations (⚠️ অনুমান)
- **Ground truth-এর নির্ভরযোগ্যতা:** দুই বিশেষজ্ঞ — কিন্তু inter-rater agreement সংখ্যা নেই; তাঁরা লেখকগোষ্ঠীর অংশ কিনা অস্পষ্ট; ground truth নিজেও source-code reading — **runtime আচরণের সঙ্গে যাচাই হয়নি**।
- **“F1 উন্নতি ৪১.৫–৭০.৪%”** — আপেক্ষিক না absolute percentage point তা অস্পষ্ট; এবং প্রতিটি API-তে ভিন্ন baseline (কিছু ক্ষেত্রে দুর্বল APICARV) — সমজাতীয় তুলনা নয়। Respector-এর ক্ষেত্রে প্রকৃত head-to-head কেবল ৪টি Java API-তে।
- **একবার রান (temperature ০)** — LLM non-determinism (API-side) ও variance রিপোর্ট নেই; কোনো statistical test নেই।
- **Downstream উপযোগিতা অপরীক্ষিত:** তৈরি OAS দিয়ে testing (RESTler/EvoMaster coverage/fault) বা documentation drift শনাক্ত করে কি না — মূল motivation হলেও পরিমাপ হয়নি (P018 Respector এটা করেছিল)।
- **Spec নিজেই “best practice” দিয়ে কলুষিত হতে পারে** — LLM implementation-এর বদলে convention অনুযায়ী 201/limit≥0 লেখে; এটি P001/P004-এর spec-implementation mismatch সমস্যাকে নতুন করে তৈরি করতে পারে।
- Constraint শুধু ১৩টি JSON-Schema type; **inter-parameter dependency (P016 IDL) উপেক্ষিত**; security scheme/auth তথ্যও মূল্যায়ন-বহির্ভূত।
- ৬৯৩টি গড় LLM call/API — বড় monorepo/microservice (শত শত service)-এ খরচ ও latency স্কেলিং অপরীক্ষিত।
- Closed model (GPT-5 mini, Gemini) — model deprecation হলে পুনরুৎপাদন কঠিন; open model (Qwen) দুর্বল।

## L. Threats to validity
- উপরে J; inferable: construct (2xx-only response, ground truth পদ্ধতি), conclusion (single run)।

## M. Reproducibility
- Code ও open-source dataset GitHub-এ (jsi-cst/OOPS); proprietary ৪টি API অপ্রাপ্য; closed LLM নির্ভরতা — **মাঝারি**।

## N. Opportunities (hypothesis)
- **Static (LLM) + dynamic validation hybrid:** generated OAS-কে চলন্ত API-তে probe করে সংশোধন (লেখকদের future work; P001 online testing-এর সঙ্গে সমন্বয়) — LLM-এর “best-practice hallucination” ধরার উপায়।
- **Error response (4xx/5xx) ও security scheme inference** — testing oracle-এর জন্য জরুরি (P015-এর schema fault আলোচনা)।
- **IDL/inter-parameter dependency inference** LLM দিয়ে source থেকে — P016-এর gap পূরণ।
- **Spec drift detection:** OOPS-generated বনাম developer OAS diff — documentation smell (P028) ও breaking change (T5) শনাক্তকরণ।
- **Downstream benchmark:** generated spec দিয়ে fuzzing coverage/fault বনাম human spec — T4→T1 প্রভাব পরিমাপ।
- LLM tool/MCP description generation (P032 REST→MCP)-এ প্রয়োগ।

## O. Relationships
- **Direct competitor/successor of P018 (Respector)** — Respector baseline; rule বনাম LLM।
- **Complements P019 (RestPi)** — type inference-এর formal দিক বনাম LLM।
- **Related to P016** — constraint inference আছে কিন্তু inter-parameter dependency নেই।
- **Feeds T1** (spec দরকার: P006 RESTler, P007 AutoRestTest — লেখকরা LlamaRestTest/LogiAgent integration পরিকল্পনা করেন)।
- **Links T8** (LLM agent workflow; P032-এর REST→MCP wrapping-এ OAS ব্যবহৃত)।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract (F1 >৯৮/৯৭/৯২%) | p.1 L15–30 |
| বিদ্যমান পদ্ধতির সীমা | p.1–3 L54–92, L273–391 |
| তিন চ্যালেঞ্জ | p.3 L244–271 |
| Overview (Fig.3) | p.4 L331–386 |
| API entry, dependency graph (Alg.1) | p.4–5 L420–632 |
| Agents, self-refine, normalization | p.5–6 L641–738 |
| OAS generation (Alg.2), Swagger 2.0 কৌশল | p.6–8 L740–1006 |
| RQ1–RQ4 | p.8 L896–1014 |
| Dataset (Table 2), proprietary | p.8–9 L990–1180 |
| Ground truth (২ বিশেষজ্ঞ) | p.9 L1189–1191 |
| Baselines | p.9 L1194–1225 |
| Correctness criteria | p.9 L1227–1244 |
| Implementation, GPT-5 mini | p.9–10 L1347–1359 |
| RQ1 ফল ও ব্যর্থতা | p.10–12 L1297–1926 |
| RQ2 ablation | p.12 L1886–1947 |
| RQ3 LLM তুলনা | p.12–13 L1950–2623 |
| RQ4 cost $০.৪১ | p.13–14 L2627–2703 |
| Threats | p.14 L2666–2698 |
| Conclusion, future work | p.15–16 L2773–2816 |

**Document integrity:** Body সম্পূর্ণ; দুই-কলামের reading order কয়েক জায়গায় এলোমেলো (contribution bullet ও RQ তালিকা খণ্ডিত, Threats-এর আগে Related work); Algorithm 1–2 line-number সহ পাঠযোগ্য; **Table 4–7 per-API সংখ্যা column-split** (একটি spurious heading “## 94.4 N/A”); সারাংশ সংখ্যা text থেকে যাচাইকৃত।
