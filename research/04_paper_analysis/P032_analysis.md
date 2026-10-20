# P032 — From REST to MCP: An Empirical Study of API Wrapping and Automated Server Generation for LLM Agents

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (related work বাদ, references বাদ; AutoMCP implementation অংশ skim) · **উৎস:** arXiv 2507.16044**v4** (৬ Apr 2026), ৫৬ পৃষ্ঠা — TOSEM-format preprint (DOI placeholder) · **বিশ্লেষক:** Claude · 2026-10-19
**⚠️ Peer-review অবস্থা:** final set-এর preprint (selection-এ preprint cap-এর অন্তর্ভুক্ত); ACM TOSEM template-এ কিন্তু প্রকাশনা-নিশ্চিতকরণ নেই।

---

## A. Bibliographic identity
- **Authors:** Meriem Mastouri (Grand Valley State), Emna Ksontini (UNC Wilmington), Amine Barrak (Oakland), Wael Kessentini (DePaul)
- **Venue:** arXiv preprint (2025, v4 2026); DOI প্রযোজ্য নয়
- **Cluster:** T8 (secondary: T4 — OpenAPI-driven generation ও spec repair; T6 — tool/API design)
- **ধরন:** Empirical study (mining + manual coding) + tool (AutoMCP, SpecFix)

## B. Motivation
- MCP LLM agent-এর tool interface-এর প্রধান standard; অধিকাংশ MCP server এমন vendor-কে লক্ষ্য করে যাদের ইতিমধ্যে REST API আছে — কিন্তু MCP tool ও REST API-র সম্পর্ক অনধ্যয়িত (p.1 L14–17)।
- আকারের বৈপরীত্য: GitHub REST ৬০০+ operation বনাম MCP ৫১ tool; Slack ২০০+ বনাম ৮ (p.2 L175–177)।
- Tool সংখ্যা বাড়লে LLM tool-selection accuracy সর্বোচ্চ ৮৫% পর্যন্ত কমে (p.3 L200–201) — coverage বনাম usability টানাপোড়েন।
- Swagger Codegen-ধাঁচের spec → code রূপান্তর MCP-তে প্রযোজ্য কিনা এবং spec quality সমস্যা তা টিকে থাকে কিনা অজানা (p.3 L204–208)।

## C. Research questions (p.5 L376–382)
- RQ1: MCP server vendor REST API-র উপর কতটা নির্ভর; integration strategy ও configuration?
- RQ2: REST operation কীভাবে MCP tool-এ রূপান্তরিত — exposure, omission, mapping pattern?
- RQ3: OpenAPI থেকে স্বয়ংক্রিয় generation কতটা সম্ভব; কোন factor বাধা দেয়?
- RQ4: স্বয়ংক্রিয় spec repair ও tool-set transformation কতটা কার্যকর?

## D. Contributions
- MCP server construction-এর প্রথম বৃহৎ empirical study; omission/grouping pattern catalog; specification defect taxonomy; **AutoMCP** (baseline generator + **SpecFix** + filtering/grouping) ও replication package [43] (p.3 L215–227)।

## E. Methodology
- **RQ1 corpus:** Anthropic-এর official MCP catalogue (৩১ Jul 2025) ৩৪৫ → বাস্তব repo ২৭৯ → public REST API-যুক্ত vendor ১৬৫ → ≥১০ star → **১১৬** (p.6 L591–599)।
- **RQ1 পদ্ধতি:** দুই লেখক প্রতি tool handler থেকে প্রথম external call পর্যন্ত trace (REST-backed/partial/non-REST; **κ = ০.৮৭**); REST-backed-এ configuration (auth, transport, tool filtering; Krippendorff α ০.৯০–০.৯৬) ও integration (bare বনাম custom client, α ০.৮৫; invocation subtype α ০.৮৩; augmentation taxonomy α ০.৮১) (p.7–8 L644–718)।
- **RQ2:** official OpenAPI-যুক্ত **৪২টি server**; ১০-server gold standard (২৯৮ tool, ৮৫৭ operation; cardinality α ০.৮২, SetSim ০.৮৯) → **GPT-4.1** semantic labeler (gold-এ macro-F1 ০.৮৭, exact-match ০.৭৮) দিয়ে বাকিগুলো; structural feature (read-only, mutating, destructive, pagination, auth, deprecated, deep path) ও semantic category (OpenAPI tag-এর BERTopic bootstrap consensus clustering) অনুযায়ী coverage, omission, lift; mapping pattern (α ০.৯১/০.৯৪) (p.9–13 L732–996)।
- **RQ3–RQ4 corpus:** ৪২ + APIs.guru/Konfig-এর ৩,৭৮৪ spec থেকে auth × size stratified ৫০ → “৮০” (abstract) / **৭৭** (results) API; **AutoMCP-Baseline:** প্রতি operation → এক tool (OpenAPI 2.0/3.0 parse, `$ref` inline, auth `.env` template, OAuth2 flow); প্রতি tool invocation লাইভ চালিয়ে সফলতা; ব্যর্থতার root-cause (তিন লেখক) (p.6–7 L603–624; p.13–15 L1004–1098; §5.1)।
- **SpecFix:** তিন defect শ্রেণি — (A) authentication misconfiguration, (B) malformed base URL, (C) undocumented runtime header/token prefix — rule-ভিত্তিক detection (৬ rule) + **LLM-ভিত্তিক validation ও minimal patch** (documentation-কে প্রমাণ হিসেবে) (p.15–16; Table 3)।
- **Transformations:** category-based filtering (RQ2-এর omission pattern) + Collection/Item Merge grouping (`GET /items` + `GET /items/{id}` → এক tool) (§5.3)।

## F. Dataset
- উপরে E; ৮,৮৯০ candidate tool (৭৭ API); ২,১৯০টি sampled invocation।

## G. Evaluation
- Descriptive শতাংশ; agreement statistic; coverage/lift; execution success rate; SpecFix precision/recall ও repair correctness; tool-count reduction; behavioural equivalence of merged tools।

## H. Results (author-reported)
- **RQ1:** REST-backed ৮৭ (৭৬.৩%), partial ১৪ (১২.৩%), non-REST ১৩ (১১.৪%) → **৮৮.৬% REST-নির্ভর**; auth: API key ৪৮.৩%, bearer ১৭.২%, OAuth 2.0 ১০.৩%; transport: STDIO-only ৫০.৬%, multi ৪০.২%; **৭৩.৬% সব tool নিঃশর্তভাবে expose** করে (filtering নেই); **৯২% server শুধু bare API wrapper**; bare tool-এর ৬৪.৮% direct HTTP, ২৮.৯% SDK, **মাত্র ৪.৬% OpenAPI-generated client** (p.18–24 L1671–2246)।
- **RQ2:** **median coverage ১৯%** (mean ৩২.৪%); ছোট API-তে median ৬৮%, খুব বড় API-তে ৬%; read/retrieval বেশি exposed, destructive/high-impact এবং **authentication/authorization/configuration** operation বেশি omitted; observability, orchestration, analytics semantic category preferentially exposed; **৮৯.৮% tool এক-এক mapping**, ১০.২% aggregation (পাঁচটি recurring pattern, retrieval-কেন্দ্রিক); reused operation-এর ৬৮% GET (p.25–33 L2260–2989)।
- **RQ3:** ৫৯/৭৭ API (৭৬.৬%) সম্পূর্ণ সফল; tool স্তরে **১,৬৬৬/২,১৯০ (৭৬%)** সফল; ব্যর্থতা মূলত endpoint নয়, **specification-স্তরের defect** (auth metadata অসম্পূর্ণ, base URL, undocumented header) — একটি API-wide defect সব tool ভাঙে (p.34–45 L2997–3721)।
- **RQ4:** SpecFix — ১৮টি ব্যর্থ API-র ১৬টিতে লক্ষ্যভুক্ত defect (২০ instance); repair correctness **১৬/১৯ (৮৪.২%)** — ভুলগুলো: LLM placeholder base URL (`https://api.example.com`) বসিয়েছে, custom identity header-কে bearer দিয়ে প্রতিস্থাপন; ১১/১৬ API পূর্ণ recovery; corpus স্তরে API ৭৬.৬% → **৮৭.০%**, tool **৭৬% → ৯৪.২%** (+১৮.২ pp); ৩টি আগে-সফল API-তে regression (১০ invocation, ০.৪৫%) — over-constrained auth (p.46–50 L3731–3784)।
- **Transformations:** filtering ১,৬৩৬/৮,৮৯০ (−১৮.৪%) বাদ; merge ৪৮৬ tool কমায় (২৩২ endpoint-এ behavioural equivalence পাস); মোট ৮,৮৯০ → ৬,৭৬৮ (−২৩.৯%), **median per-API ৭৩ → ৪৯ (−৩২.৯%)** — তবু বাস্তব MCP server-এর বিমূর্ততা স্তরের চেয়ে অনেক বেশি tool (p.51–52 L3875–3993)।

## I. Strengths
- **নতুন ও সময়োপযোগী:** MCP ecosystem-এর REST সম্পর্কের প্রথম পদ্ধতিগত পরিমাপ — T4 (spec) ও T8 (agent tool)-এর সরাসরি সেতু।
- **কঠোর manual coding:** প্রতিটি ধাপে pre-consensus κ/α রিপোর্ট; LLM labeler gold standard-এ যাচাই করে তবে scale।
- বাস্তব invocation-ভিত্তিক মূল্যায়ন (শুধু code generation নয়); defect taxonomy actionable।
- Pattern (omission, grouping) থেকে transformation — empirical finding থেকে tool নকশা।
- Regression ও ভুল repair সৎভাবে রিপোর্ট।

## J. Explicit limitations (p.52–53 Threats)
- Internal: manual coding subjectivity (κ ০.৮৭–১.০, α ০.৮১–১.০); GPT-4.1 alignment-এর residual error coverage পরিসংখ্যানে প্রভাব ফেলতে পারে; live API-র transient অবস্থা (rate limit, downtime) — পুনরায় চালানো ও ১০% স্বাধীন পুনর্মূল্যায়ন (κ ০.৯৭); SpecFix পাঁচটির মধ্যে তিনটি defect শ্রেণি লক্ষ্য করে।
- External: official catalogue (Jul 2025) + ≥১০ star — private/enterprise/community server-এ সাধারণীকরণ নাও হতে পারে।
- Transformation রক্ষণশীল — user intent/task-oriented abstraction future work।

## K. Inferred limitations (⚠️ অনুমান)
- **“সফলতা” = invocation error ছাড়া সম্পন্ন** — response-এর semantic সঠিকতা, বা **LLM agent আসলে generated tool দিয়ে task সম্পন্ন করতে পারে কিনা** মাপা হয়নি; tool description-এর মান (P028/P036-এর smell), tool-selection accuracy বা agent success rate-এ AutoMCP-এর প্রভাব অপরীক্ষিত — মূল motivation (৮৫% selection loss) সত্ত্বেও।
- **Sampled invocation:** ৮,৮৯০ tool-এর মধ্যে ২,১৯০টি; destructive/mutating operation লাইভ API-তে চালানোর নৈতিকতা ও নমুনা পক্ষপাত (read-heavy?) স্পষ্ট নয়।
- **Corpus সংখ্যার অসামঞ্জস্য:** abstract “৮০” বনাম results “৭৭” API; conclusion-এও ৭৭।
- **SpecFix মূল্যায়ন ছোট ও tuning-সংলগ্ন:** ১৬ API, ২০ defect — যে ব্যর্থতা দেখে defect taxonomy তৈরি, একই নমুনায় repair মূল্যায়ন (held-out নেই)।
- **Security মাত্রা অল্প:** MCP server-এর ৭৩.৬% সব tool expose করে, auth token `.env`-এ — generated server-এর least-privilege, destructive operation exposure-এর নিরাপত্তা বিশ্লেষণ নেই (P036 ও T3-এর সঙ্গে gap)।
- GPT-4.1 labeler ও LLM repair — closed model নির্ভরতা।
- Preprint; একাধিক version (v1–v4) — সংখ্যা version-ভেদে বদলেছে কিনা যাচাই প্রয়োজন।

## L. Threats to validity
- উপরে J; inferable: construct (execution success ≠ agent usefulness), sampling (invocation নির্বাচন), held-out মূল্যায়নের অভাব।

## M. Reproducibility
- Replication package [43] (AutoMCP, data); live API নির্ভরতা (drift), GPT-4.1 — **মাঝারি**।

## N. Opportunities (hypothesis)
- **Agent-centric evaluation of generated MCP servers:** AutoMCP-generated বনাম hand-crafted MCP server-এ LLM agent-এর task success, tool-selection accuracy, cost — T8-এর কেন্দ্রীয় অনাবিষ্কৃত প্রশ্ন; ToolBench/StableToolBench-ধাঁচের (P033) benchmark-এ।
- **Spec-quality → agent-reliability chain:** OpenAPI defect (P001/P004 mismatch, P028 doc smell, P027 design violation) কীভাবে agent ব্যর্থতায় রূপান্তরিত হয় — T4/T6→T8 causal study।
- **Task-oriented tool abstraction (LLM-assisted grouping)** — রক্ষণশীল structural merge-এর বাইরে, behavioural equivalence যাচাইসহ।
- **Secure-by-default MCP generation:** destructive/auth operation omission policy, scoped credentials, BOLA-aware tool design (P012/P014/P015 + P036)।
- **MCP–REST co-evolution:** REST API version পরিবর্তনে MCP server drift (P022 ToolEVO, P025 differential testing-এর MCP সংস্করণ)।
- **REST testing tool দিয়ে MCP server testing:** fuzzing (P006/P007) MCP tool interface-এ।

## O. Relationships
- **Bridges T4 ↔ T8:** OpenAPI → tool (P017 OOPS-generated spec এখানে input হতে পারে)।
- **Complements P036** (MCP server security/maintainability) ও **P033/P034** (tool-use LLM; tool সংখ্যা ও retrieval সমস্যা)।
- **Echoes P016/P028:** spec/documentation অপূর্ণতা downstream automation ভাঙে।
- **Relates to P020:** API consumer হিসেবে agent; versioning ও change communication-এর নতুন রূপ।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract (১১৬, ৮৮.৬%, ৯২%, ১৯%, ৭৬→৯৪.২%) | p.1 L14–26 |
| GitHub/Slack আকার বৈপরীত্য | p.2 L175–177 |
| Tool-selection ৮৫% loss | p.3 L200–201 |
| RQ1–RQ4 | p.5 L376–382 |
| Dataset construction | p.6–7 L591–624 |
| RQ1 পদ্ধতি, κ/α | p.7–8 L644–718 |
| RQ2 alignment, GPT-4.1 | p.9–10 L757–808 |
| Structural/semantic features | p.10–12 L822–897 |
| RQ3 পদ্ধতি | p.13–15 L1004–1098 |
| RQ4 পদ্ধতি | p.15–16 L1100–1173 |
| AutoMCP, SpecFix নকশা | p.16–22 L1203–1655 |
| RQ1 ফল (Finding RQ1.1–1.2) | p.18–24 L1671–2246 |
| RQ2 ফল (coverage, omission, mapping) | p.25–33 L2260–2989 |
| RQ3 ফল ও defect taxonomy | p.34–45 L2997–3721 |
| RQ4 SpecFix ফল (Table 17–18) | p.46–50 L3731–3784 |
| Filtering/grouping (Table 19) | p.51–52 L3785–3993 |
| Threats | p.52–53 L3996–4027 |
| Conclusion | p.53 L4030–4050 |

**Document integrity:** **Markdown-এ ৮৩২টি NUL/control byte ছিল** (figure-এর ভাঙা font-encoding glyph, p.~24–30) — `grep` binary হিসেবে ধরছিল; মুছে ফেলা হয়েছে, body text অপরিবর্তিত (log: `04_paper_analysis/markdown_fixes_log.csv`)। Fig.2 (study design flow)-এর সংখ্যা spurious “##” heading হিসেবে এসেছে; গাণিতিক সূত্র (Cov, Lift) আংশিক হারিয়েছে; Table 2–19 column-split — মূল সংখ্যা Finding box ও text থেকে।
