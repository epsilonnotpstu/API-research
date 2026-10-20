# Cluster T8 — LLM Tool Use, API Calling & MCP

**Primary:** P032, P033, P034, P035, P036 · **Secondary:** P005, P007, P017, P022, P024, P031
⚠️ = অনুমান। [H] = hypothesis।

## 1. ID ও নাম
T8 — LLM ও agent-এর API/tool ব্যবহার: API selection, call generation, hallucination ও MCP ecosystem।

## 2. Problem ও motivation
- LLM agent এখন API-র প্রধান নতুন consumer।
- Agent-এর সঠিক API নির্বাচন ও call করা কঠিন (P033, P034)।
- Code-LLM hallucinate করে (P035)।
- MCP দ্রুত মানক হয়ে উঠছে, কিন্তু server-গুলোর মান ও নিরাপত্তা অজানা (P032, P036)।

## 3. Core RQ
- Real API-তে tool use কীভাবে শেখানো যায় (P033)?
- Retrieval-aware training কি hallucination কমায় (P034)?
- Documentation কখন সাহায্য করে (P035)?
- MCP server কীভাবে REST wrap করে, এবং generation কতটা নির্ভরযোগ্য (P032)?
- MCP server-এর health ও security কেমন (P036)?

## 4. Paper
| ID | ধরন |
|---|---|
| P033 ToolLLM (ICLR 2024) | Dataset (ToolBench) + DFSDT + ToolLLaMA |
| P034 Gorilla (NeurIPS 2024) | APIBench + retrieval-aware fine-tuning |
| P035 (ICSE-SEIP 2025) | CloudAPIBench + DAG/DAG++ |
| P032 (arXiv 2025, preprint) | REST→MCP empirical + AutoMCP/SpecFix |
| P036 (TOSEM 2026) | MCP ecosystem mining + security scan |

## 5. ঐতিহাসিক অবদান
- **P033, P034:** বৃহৎ পরিসরের API-calling benchmark ও প্রশিক্ষণ পদ্ধতি।

## 6. সাম্প্রতিক উন্নয়ন
- **MCP (২০২৫–২০২৬):** P032, P036।
- **Corpus-এর বাইরে (GV01, GV03, GV09, GV12):**
  - MCP security benchmark: MCPSecBench, MCPTox।
  - MCP privilege measurement।
  - WAPIIBench।
  - SilentProbe।
  - Constrained decoding।

## 7. Methodology
- Instruction-data synthesis (P033)।
- Fine-tuning (P033, P034)।
- RAG ও confidence gating (P035)।
- Repository mining ও static/dynamic scan (P036)।
- Generation + repair (P032)।

## 8. Tool
- ToolLLaMA, DFSDT, ToolEval (P033)।
- Gorilla (P034)।
- DAG++ (P035)।
- AutoMCP, SpecFix (P032)।
- mcp-scan, SonarQube (P036)।

## 9. Dataset
- **P033:** ToolBench (১৬,০০০+ RapidAPI API)।
- **P034:** APIBench (১,৬৪৫টি ML API)।
- **P035:** CloudAPIBench (৬২২টি task)।
- **P036:** ১,৮৯৯টি MCP server।
- **P032:** ১১৬টি MCP server; ৪২টি server–OpenAPI জোড়া; ৭৭টি OpenAPI API (৮,৮৯০ tool; ২,১৯০টি sampled invocation)।

## 10. মূল্যায়ন
- Pass/win rate, LLM judge (P033)।
- AST accuracy (P034)।
- Valid invocation (P035)।
- Tool success rate (P032) — success = error-free invocation, semantic correctness নয় ⚠️।
- Prevalence (P036)।
- **Execution-validated, version-pinned মূল্যায়ন বিরল** ⚠️।

## 11. প্রতিষ্ঠিত ফলাফল
- **P033:**
  - DFSDT ReAct-এর চেয়ে ভালো।
  - Retrieved API oracle API-এর চেয়েও ভালো।
- **P034:**
  - Gorilla GPT-4-এর চেয়ে +২০.৪৩%।
  - Imperfect retriever accuracy ৪৭–৫২% পর্যন্ত কমায়।
- **P035:**
  - Spec যোগে valid invocation ৪১.৮০%→৮৬.৮২%।
  - High-frequency API-তে DAG ক্ষতিকর।
- **P032:**
  - ৯২% bare wrapper।
  - Median operation coverage ১৯%।
  - Tool success ৭৬%, SpecFix-এর পর ৯৪.২%।
- **P036:**
  - ৭.২% server-এ vulnerability, ৫.৫%-এ tool poisoning।
  - mcp-scan excessive permission মিস করে।

## 12. বিরোধ
- **Retrieval-এর মূল্য:** P033 বনাম P034/P035।
- **বড় model:** P034 অনুযায়ী GPT-4 বেশি hallucinate করে; P024 (secondary)।

## 13. লেখক-স্বীকৃত সীমাবদ্ধতা
- **P033:** live API ও ChatGPT judge।
- **P034:** ML API domain।
- **P035:** AWS/Azure; benchmark availability।
- **P032:** live API drift; GPT-4.1।
- **P036:** sample-ভিত্তিক scan; শুধু open-source।

## 14. বিশ্লেষণী সীমাবদ্ধতা ⚠️
- **সংখ্যার অসঙ্গতি:** P032 (৮০ বনাম ৭৭ API), P034 (৬৯৬ বনাম ৬২৬), P036 (১,৮৯৯/৫৮৩/৭৩)।
- **Agent-centric (end-to-end task) মূল্যায়ন নেই:** P032 ও P036।
- **Security:** P036-এ API-level authorization বিশ্লেষণ নেই।

## 15. অপর্যাপ্ত প্রমাণ
- Spec-এর মান → agent reliability কার্যকারণ।
- MCP server-এর functional ও authorization testing।
- MCP–REST co-evolution।

## 16. Gap
- **G3:** MCP/REST-wrapper authorization testing (narrowed, Class C)।
- **G4:** spec-quality কার্যকারণ (Class B/C, Partially weakened)।
- **G7:** hallucination benchmark — **Weakened**।
- **T5×T8 evolution** — Partially weakened।

## 17. Technical উন্নতি
- Task-oriented tool abstraction (P032)।
- Least-privilege generation।
- Confidence-gated OpenAPI operation retrieval (P035 → agent)।

## 18. নতুন approach [H]
1. **Spec-mutation testbed:**
   - Real OpenAPI spec-এ নিয়ন্ত্রিত ত্রুটি inject করা: description মুছে ফেলা, type ভুল করা, constraint বাদ দেওয়া, P027 rule লঙ্ঘন।
   - তারপর AutoMCP-ধাঁচের MCP server বা সরাসরি function-calling দিয়ে agent task success মাপা।
   - এটি G4।
2. **MCP authorization fuzzing:** P015-এর oracle MCP tool layer-এ প্রয়োগ (G3)।

## 19. দক্ষতা ও resource
- LLM API বা open model (GPU ঐচ্ছিক)।
- MCP SDK।
- OpenAPI tooling।
- Docker SUT।

## 20. ঝুঁকি
- **খুব দ্রুত চলমান এলাকা** — novelty সময়ের সাথে দ্রুত ক্ষয় হয়।
- Proprietary model drift।
- খরচ।

## 21. Baseline ও metric
- **Baseline:** অপরিবর্তিত spec, SpecFix-repaired spec, BFCL/WAPIIBench-ধাঁচের pipeline।
- **Metric:** task success, invalid-call হার, silent failure।

## 22. নতুন গবেষকের সুযোগ
- **G4 spec-mutation testbed** — মাঝারি খরচ, উচ্চ প্রাসঙ্গিকতা।
- তবে SilentProbe ও 2605.14312 পূর্ণ পাঠে overlap যাচাই আবশ্যক।

## 23. প্রমাণের মান
**মাঝারি।**
- P032 preprint (Medium confidence)।
- কয়েকটি paper-এ সংখ্যার অসঙ্গতি।
- Corpus-এর বাইরের কাজ বিপুল ও দ্রুত বাড়ছে।
