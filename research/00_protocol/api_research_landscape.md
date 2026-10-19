# API Research Landscape — প্রাথমিক মানচিত্র (PHASE A1)

**প্রস্তুতকারী:** Claude | **তারিখ:** 2026-10-19
**ভিত্তি:** ৪৭টি OpenAlex query, ২টি Consensus query, ৩টি WebSearch, ১৩-area trend count (`trend_counts_openalex.csv`), এবং ৬৮টি seed candidate-এর metadata ও abstract।

> ⚠️ **সতর্কতা:** এই দলিল PHASE A-র *প্রাথমিক পর্যবেক্ষণ*, যা metadata আর abstract-এর ওপর দাঁড়িয়ে। কোনো full paper পড়া হয়নি। এখানে কোনো research gap-কে **প্রতিষ্ঠিত** বলা হচ্ছে না। "সম্ভাব্য দিক" লেখা অংশগুলো hypothesis মাত্র। সেগুলো PHASE C/D-তে যাচাই হবে।

---

## 1. Quantitative ইঙ্গিত: কোন ক্ষেত্র কত দ্রুত বাড়ছে

পদ্ধতি: OpenAlex-এ title+abstract keyword match, Computer Science field (id 17)। প্রতি বছরের মোট CS publication দিয়ে normalize করে "প্রতি ১ লক্ষ CS paper-এ কতটি" হিসাব করা হয়েছে, কারণ ২০১৮→২০২৬-এ OpenAlex-এর মোট CS volume প্রায় দ্বিগুণ হয়েছে।

| Area | প্রতি লক্ষে 2021 | 2023 | 2025 | 2026 (আংশিক বছর) | Normalized growth 2021→2025 |
|---|---|---|---|---|---|
| LLM tool use / function calling | 0.7 | 12.6 | 84.9 | 242.6 | ×118 (বিস্ফোরক) |
| Model Context Protocol (MCP) | 0.2* | 0.3* | 40.9 | 140.2 | MCP ২০২৪-এর শেষে ঘোষিত; ২০২১–২৩-এর count keyword noise |
| API anomaly / monitoring | 9.6 | 13.6 | 34.7 | 43.9 | ×3.6 (তবে মান নিয়ে প্রশ্ন আছে, §3 দেখুন) |
| Microservice APIs | 19.6 | 29.9 | 56.3 | 55.5 | ×2.9 |
| gRPC / RPC APIs | 6.7 | 6.1 | 15.5 | 19.9 | ×2.3 |
| API security & authorization | 4.7 | 3.9 | 10.1 | 17.4 | ×2.2 |
| API documentation | 5.0 | 8.1 | 8.5 | 12.0 | ×1.7 |
| OpenAPI / API specification | 11.7 | 14.2 | 18.7 | 34.8 | ×1.6 |
| REST/Web API testing & fuzzing | 22.2 | 22.1 | 34.3 | 51.0 | ×1.5 |
| GraphQL | 12.4 | 9.7 | 15.7 | 18.6 | ×1.3 |
| API evolution / breaking changes | 6.7 | 5.2 | 7.1 | 18.2 | ×1.1 |
| API misuse | 4.3 | 3.9 | 4.1 | 6.6 | ×0.9 (স্থিতিশীল) |
| API recommendation | 7.8 | 7.9 | 4.7 | 4.7 | ×0.6 (আপেক্ষিক হ্রাস) |

**Data artifact সতর্কতা:**
- "API evolution"-এ ২০২২ সালের raw count ৩৩৬। এর মধ্যে ৩০১টি একটিমাত্র Zenodo bulk deposit থেকে আসা, তাই এটি প্রকৃত trend নয়।
- ২০২৫–২০২৬-এর বৃদ্ধির একটি অংশ Zenodo/SSRN/preprint indexing বাড়ার ফল হতে পারে। তাই এই সংখ্যা শুধু দিক নির্দেশ করে, মান (quality) নির্দেশ করে না।
- Keyword match পুরোপুরি নির্ভুল নয়। যেমন "tool use" অন্য প্রসঙ্গেও আসে, আর "API" pharmaceutical অর্থেও ব্যবহৃত হয়।

---

## 2. Research Taxonomy (প্রমাণের ভিত্তিতে পরিমার্জিত)

প্রাথমিক taxonomy (prompt-এ দেওয়া) থেকে নিচের পরিবর্তন করা হয়েছে:
- **Merge:** "Microservice APIs"-এর গবেষণার বড় অংশ testing ও evolution-এর সঙ্গে মিশে আছে। তাই আলাদা cluster না করে cross-cutting context হিসেবে রাখা হলো।
- **যোগ:** "Model Context Protocol / agent-facing APIs" একটি নতুন ও দ্রুত উদীয়মান ক্ষেত্র। এটি LLM tool use থেকে আলাদা, কারণ এর মূল প্রশ্ন software-engineering ধরনের: security, maintainability, REST→MCP রূপান্তর।
- **যোগ:** "API misuse in LLM-generated code"। এটি পুরোনো API misuse গবেষণা আর LLM code generation-এর সংযোগস্থল।
- **দুর্বল হিসেবে চিহ্নিত:** "API performance comparison" এবং "API privacy"। কারণ §3-এ দেখুন।

### T1. REST/Web API Testing & Fuzzing *(সবচেয়ে ঘন ও পরিণত ক্ষেত্র)*
- **সমস্যা:** OpenAPI spec বা source code থেকে স্বয়ংক্রিয়ভাবে HTTP request sequence তৈরি করা, যাতে code coverage আর fault detection সর্বোচ্চ হয়।
- **পরিভাষা:** stateful fuzzing, producer–consumer dependency, inter-parameter dependency, black-box/white-box, search-based (MIO), test oracle, 5xx failure, operation coverage।
- **প্রধান পদ্ধতির ধারা:** grammar/dependency-based (RESTler), search-based (EvoMaster), constraint/combinatorial (RESTest, RestCT), NLP-enriched spec (NLP2REST), reinforcement learning (ARAT-RL, DeepREST), LLM/SLM-চালিত (RESTGPT, LlamaRestTest, AutoRestTest, KAT)।
- **Dataset/benchmark:** EMB corpus (ICST 2023), WFC/WFD (preprint 2025), এবং Kim et al. (ISSTA 2022)-এর ২০টি service-এর benchmark।
- **প্রাথমিক পর্যবেক্ষণ:** ক্ষেত্রটিতে tool comparison study আছে (Kim et al. 2022; Zhang & Arcuri TOSEM 2023), যারা "open problems" তালিকা দেয়। এটি gap খোঁজার জন্য মূল্যবান primary evidence, যা PHASE C-তে full text থেকে নিতে হবে।
- **সম্ভাব্য প্রশ্ন (hypothesis):** flakiness, test oracle-এর দুর্বলতা (বেশিরভাগ tool শুধু 5xx ধরে), এবং LLM-based tool-গুলোর তুলনা ও reproducibility।

### T2. GraphQL ও RPC/gRPC API
- **সমস্যা:** GraphQL schema থেকে query generation, query cost বা DoS, এবং RPC API-র white-box fuzzing।
- **পরিভাষা:** schema introspection, query depth/complexity, resolver, protobuf।
- **পর্যবেক্ষণ:** REST-এর তুলনায় top-venue কাজ অনেক কম (GraphQL SMS CSUR 2022; Belhadi et al. TWEB 2023; Cha et al. FSE 2020)। gRPC-র raw count বাড়ছে, কিন্তু বেশিরভাগই performance comparison, যার মান কম।

### T3. API Security, Authorization ও Vulnerability Detection
- **সমস্যা:** BOLA/IDOR, mass assignment, access-policy violation, injection; OWASP API Security Top 10-এর স্বয়ংক্রিয় শনাক্তকরণ।
- **পদ্ধতি:** security-property checker যুক্ত fuzzing (Atlidakis et al. ICST 2020), black-box mass-assignment testing (ICSE 2023), formal model (Colored Petri Net থেকে BOLA), multi-identity testing।
- **পর্যবেক্ষণ:** normalized growth ×2.2। কিন্তু peer-reviewed technique paper তুলনামূলক কম, আর অনেক নতুন কাজ preprint বা Zenodo-তে। Authorization logic-এর বাস্তবসম্মত ground truth benchmark-এর অভাব থাকতে পারে (**hypothesis**)।

### T4. API Specification (OpenAPI) Generation, Inference ও Validation
- **সমস্যা:** spec নেই বা ভুল আছে। তাই source code (Respector, ICSE 2024), UI test (ICSE 2023), online docs (ACL 2025) বা LLM (OOPS, JSS 2026) থেকে spec তৈরি করা।
- **পর্যবেক্ষণ:** spec-এর মান downstream testing ও agent tool-calling দুটোর জন্যই গুরুত্বপূর্ণ। এটি T1, T7 ও T8-কে যুক্ত করে।

### T5. API Evolution, Breaking Changes ও Deprecation
- **দুটি উপধারা:** (ক) library API, যেমন Java/Maven ecosystem, behavioral breaking change; (খ) web/REST API, যেমন OpenAPI diff, microservice API evolution, REST deprecation।
- **পর্যবেক্ষণ:** library-API দিক পরিণত (SLR CSUR 2021, Maven Central study EMSE 2022)। Web/microservice API-র দিকে বাস্তব শিল্প-চ্যালেঞ্জ নথিভুক্ত হয়েছে (Lercher et al. JSS 2024), কিন্তু automated technique তুলনামূলক কম (**hypothesis, যাচাই দরকার**)।

### T6. API Documentation ও Design Quality
- **সমস্যা:** documentation smell, REST design rule লঙ্ঘন, understandability, governance।
- **পর্যবেক্ষণ:** controlled experiment আছে (EMSE 2023), rule-violation detector আছে (RESTRuler ICSA 2024), industrial governance-এর অভিজ্ঞতাও আছে (ICSE-SEIP 2024)। LLM agent-এর জন্য "agent-ready" documentation একটি নতুন প্রশ্ন হিসেবে উঠে আসছে (২০২৬ preprint)।

### T7. API Misuse Detection (library/security API)
- **সমস্যা:** API-এর ভুল ব্যবহার শনাক্ত করা, যেমন crypto API বা resource-management API।
- **পর্যবেক্ষণ:** volume স্থিতিশীল। নতুন গতি এসেছে LLM থেকে, দুই দিক থেকে: (ক) LLM দিয়ে misuse rule তৈরি (NDSS 2025); (খ) LLM-generated code-এ misuse (AsiaCCS 2024, TSE 2026)।

### T8. LLM Tool Use, API Calling ও Agent-facing APIs (MCP সহ)
- **সমস্যা:** LLM-কে বাস্তব API (RapidAPI, REST) সঠিকভাবে নির্বাচন ও কল করতে শেখানো, benchmark তৈরি, hallucinated API কমানো, এবং MCP server-এর security ও maintainability।
- **পর্যবেক্ষণ:** সবচেয়ে দ্রুত বর্ধনশীল ক্ষেত্র। মূল কাজগুলো (Toolformer, Gorilla, ToolLLM, API-Bank) মূলত NLP/ML venue-তে। SE দৃষ্টিকোণ থেকে কাজ (API spec মান, REST→MCP রূপান্তর, MCP server maintainability) সাম্প্রতিক ও কম। এটি একটি সম্ভাব্য সংযোগস্থল (**hypothesis**)।
- **ঝুঁকি:** খুব দ্রুত saturation হচ্ছে, তাই novelty claim করা কঠিন। Benchmark-এর অস্থিরতা নিজেই একটি নথিভুক্ত সমস্যা (StableToolBench)।

### T9. Microservice API testing ও dependency
- Microservices testing SLR (IST 2025), SAINT (ICSE 2026), industrial EvoMaster study। T1 ও T5-এর সঙ্গে অনেকটা মিলে যায়।

### T10. API Recommendation ও Discovery
- আপেক্ষিকভাবে কমছে। Benchmark-ভিত্তিক পুনর্মূল্যায়ন আছে (TSE 2022)। LLM আসার পর এর বড় অংশ T8-এ (tool retrieval) সরে গেছে বলে মনে হয় (**hypothesis**)।

### T11. API Monitoring, Anomaly Detection ও Performance
- Raw volume বাড়ছে, কিন্তু top-tier SE/security venue-তে প্রতিনিধিত্বশীল কাজ খুব কম পাওয়া গেছে (OP025, OP026)। বেশিরভাগই অল্প-পরিচিত journal-এ।

---

## 3. গুরুত্বপূর্ণ নেতিবাচক পর্যবেক্ষণ (search থেকে)

1. **Performance comparison (REST vs gRPC vs GraphQL):** OP026-এর ১২টি ফলের সবই কম-প্রভাবশালী venue থেকে। এদের বেশিরভাগ ছোট micro-benchmark বলে মনে হয়। ব্যতিক্রম একটি controlled experiment (Brito & Valente, ICSA 2020, যা understandability নিয়ে, performance নয়)। এই ক্ষেত্রে rigorous গবেষণার সুযোগ থাকতে পারে, আবার এটি "engineering benchmark"-ও হতে পারে, research gap নয়। এটি **অনিশ্চিত**।
2. **API traffic anomaly detection:** বেশিরভাগ ফল general network-traffic anomaly নিয়ে। API-specific কাজ সামান্য (একটি CCGrid workshop paper, একটি MAKE 2026 article)।
3. **API privacy:** API-specific privacy গবেষণায় প্রায় কিছু পাওয়া যায়নি (OP045-এ একটিমাত্র প্রাসঙ্গিক ফল)। কারণ হতে পারে search term-এর সীমাবদ্ধতা। এটিকে এখনই gap বলা যাবে না।
4. **Venue concentration:** T1-এর শক্তিশালী কাজের বড় অংশ কয়েকটি research group থেকে আসে (যেমন EvoMaster group, Georgia Tech-এর Orso group, Verona-র RestTestGen group, Seville-এর RESTest group; author list PHASE B-তে Crossref থেকে নিশ্চিত করতে হবে)। এতে evaluation-এ নিজের benchmark-এ নিজের tool যাচাইয়ের bias থাকতে পারে (**hypothesis**, PHASE C-তে যাচাই করতে হবে)।

## 4. Prompt-এর A1 প্রশ্নগুলোর প্রাথমিক উত্তর

| প্রশ্ন | প্রাথমিক উত্তর (metadata-ভিত্তিক) |
|---|---|
| বেশি scholarly attention | REST API testing/fuzzing; library API evolution; API misuse; LLM tool use |
| দ্রুত পরিবর্তনশীল | LLM tool use, MCP, LLM-ভিত্তিক REST testing, API security |
| পুনরাবৃত্ত technique | search-based testing, RL, LLM prompting/fine-tuning, static analysis, formal model (Petri net), differential testing |
| Measurable research question | testing (coverage, fault count), spec inference (precision/recall), BC detection (F1), tool-calling (pass rate) |
| Open dataset/benchmark | EMB, WFD, APIs.guru-ভিত্তিক OpenAPI corpus, ToolBench/StableToolBench, API-Bank, BC benchmark (ROSEAU-এ উল্লিখিত) |
| প্রযুক্তিগতভাবে কঠিন | business-logic/authorization oracle, stateful dependency, spec–implementation inconsistency, agent-API security |
| ব্যয়বহুল infrastructure ছাড়া সম্ভাব্য | spec inference, BC detection, documentation analysis, small-LM-ভিত্তিক testing (LlamaRestTest দেখিয়েছে যে ছোট model-ও কার্যকর হতে পারে, author-claimed), MCP empirical study |

## 5. পরবর্তী ধাপে যাচাই করার প্রশ্ন

- T1-এ open problem-গুলো কি LLM-based tool আসার পর সমাধান হয়েছে, নাকি এখনো আছে? (দেখতে হবে: C05, C10, C11, C16, C18)
- T3-এ authorization testing-এর evaluation কি বাস্তব API-তে, নাকি synthetic? (C28–C31)
- T4/T8 সংযোগ: spec-এর মান কি agent tool-calling-এর সাফল্যকে প্রভাবিত করে, এবং এর empirical evidence আছে কি? (C34, C35, C59, C64)
- T5: web-API breaking change detection-এর জন্য benchmark আছে কি? (C38, C39, C43)
