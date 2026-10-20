# P036 — Model Context Protocol (MCP) at First Glance: Studying the Security and Maintainability of MCP Servers

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (background ও related work skim; per-pattern table ও appendix বাদ; references বাদ) · **উৎস:** TOSEM author version (arXiv 2506.13538), ৫৩ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Mohammed Mehedi Hasan, Hao Li, Emad Fallahzadeh, Gopi Krishnan Rajbahadur, Bram Adams, Ahmed E. Hassan (Queen's University)
- **Venue:** ACM Transactions on Software Engineering and Methodology, 2026, DOI 10.1145/3814959
- **Cluster:** T8 (secondary: T3 — tool poisoning, credential exposure; T9 — ecosystem health)
- **ধরন:** Large-scale mining + hybrid static/dynamic analysis empirical study

## B. Motivation
- MCP (Anthropic, Nov 2024) tool-calling interface standardize করে; SDK সাপ্তাহিক ২৫ মিলিয়ন+ download, ~৮৬% enterprise MCP-সক্ষম model ব্যবহার করে (p.1 L18–20; p.2 L94–96)।
- FM-এর অ-নির্ধারিত (non-deterministic) control flow নতুন ঝুঁকি আনে — **tool poisoning** (credential চুরি, `.bashrc`-এ backdoor), বাস্তব ঘটনা: malicious Postmark-MCP server (hidden BCC দিয়ে email exfiltration), MCP Inspector-এ RCE (CVE-2025-49596) (p.3 L113–134)।
- MCP server-এর health, security, maintainability অনধ্যয়িত (p.3 L136–146)।

## C. Research questions (p.4 L172–214)
- RQ-0: MCP server কতটা healthy ও sustainable?
- RQ-1: কতটা security vulnerability আছে?
- RQ-2: কতটা maintainability issue (code smell, bug) আছে?

## D. Contributions (p.5 L228–254)
- **Dataset:** ১,৮৯৯ open-source MCP server (৮৮ official, ২৫৫ community, ১,৫৫৬ GitHub-mined)।
- **Cross-ecosystem baseline:** PyPI, NPM, IaC, ML ecosystem-এর সঙ্গে health/security/smell তুলনা।
- **Hybrid analysis framework:** SonarQube (static) + **mcp-scan** (MCP-specific, dynamic)।
- Empirical finding।

## E. Methodology
- **Data collection:** Anthropic official list (১ Jun 2025: ৩৪৩) + GitHub Code Search-এ `@modelcontextprotocol/sdk` / `from mcp.server` import → ১,৭১৫ repo, overlap বাদে ১,৫৫৬ mined → মোট ১,৮৯৯; **≥১০ star filter → ৫৮৩** (প্রকৃত বিশ্লেষণের নমুনা) (p.3 L155; p.14–15 L879–956)।
- **RQ-0:** CHAOSS-এর ৭ + সাহিত্যের ৭ = ১৪ metric (development ৮, community ৬); GitHub REST API; age-normalized; Elasticsearch (p.15–17 L961–1147)।
- **RQ-1/RQ-2:** **SonarQube** (Docker CLI, ৫৮৩ repo) — vulnerability, code smell, bug; severity Blocker–Minor; SonarQube rule → CWE ম্যাপিং; **mcp-scan** (live server চালু করে tool description reflection দিয়ে tool poisoning ইত্যাদি) — Cochran's formula (৯৫% confidence, **±১০% margin**) অনুযায়ী **৮৩টি** random নমুনা; প্রথমে ৬০টি সফল, tool bug রিপোর্টের পর patched version-এ মোট **৭৩টি** (p.17–18 L1164–1239)।
- **Issue clustering:** **LLM-Jury** (worker LLM + judge) দিয়ে SonarQube issue-কে pattern-এ cluster; দুই মানব reviewer-এর সঙ্গে agreement **κ = ০.৯**; positional bias/order-effect consistency পরীক্ষা (p.18–19 L1277–1329)।

## F. Dataset
- উপরে E; ভাষা: Python, JavaScript, TypeScript, “Others” (polyglot)।

## G. Evaluation
- Descriptive প্রাধান্য, অন্য ecosystem-এর সঙ্গে তুলনা; κ।

## H. Results (author-reported)
- **RQ-0:** শক্তিশালী health — **৫.৫ commit/সপ্তাহ** (traditional ২.৫), CI adoption ৪২.২% (৪০.৩%), median contributor ২.০ (সমান), contributor follower median ১২৯.৬ (৩৭.৩), issue resolution কিছুটা ধীর ৫.৬ দিন (৪.০) (p.4 L180–185)।
- **RQ-1:** SonarQube — **৭.২% server-এ ৮টি vulnerability pattern**; সর্বাধিক **credential exposure (৩.৬%)** (যেমন plaintext `OPENAI_API_KEY`); মাত্র ৩টি (abstract)/২টি (PyPI-এর সঙ্গে: authentication issue, improper input validation) traditional ecosystem-এর top vulnerability-র সঙ্গে overlap; NPM-এর সঙ্গে কোনোটিই নয় (p.4 L195–199; p.26 L1781–1785)। mcp-scan — **৫.৫% server-এ tool poisoning** (credential exposure-এর চেয়ে বেশি) — SonarQube এটি ধরতে পারে না (p.4 L199–202; p.31 L1985–1988)।
- **mcp-scan-এর অন্ধবিন্দু (হাতে পাওয়া):** অতিরিক্ত permission (apple-notes-mcp-এর full disk access), insecure default (godot-mcp-এ sensitive operation-এ auto-approval) — reflection-ভিত্তিক বলে source code দেখে না (p.31 L1989–1997)।
- “Pure” MCP server (অন্য application থেকে উদ্ভূত নয়) credential exposure ও transport security-তে বেশি প্রবণ (p.31 L1998–1999)।
- **RQ-2:** **৬৬% server-এ critical/blocker code smell** (সর্বাধিক high cognitive complexity); **১৪.৪%-এ bug pattern**; ১০টি smell ও ৯টি bug-এর taxonomy — traditional SE-র সঙ্গে overlap (p.4–5 L211–226)।
- **Implications:** MCP-specific vulnerability CWE/vulnerability database-এ অন্তর্ভুক্তি; registry-তে স্বয়ংক্রিয় security scanning; SAST CI-তে; responsible development (p.1 L30–32; §7)।

## I. Strengths
- **MCP ecosystem-এর প্রথম বৃহৎ নিরাপত্তা/maintainability পরিমাপ** — সময়োপযোগী, শিল্প-প্রাসঙ্গিক।
- Traditional ও MCP-specific scanner একত্রে — দেখায় traditional tool অর্ধেক চিত্রই ধরে।
- Cross-ecosystem baseline — প্রসঙ্গসহ তুলনা।
- Dynamic scan-এর বাস্তব প্রয়োগ (credential সংগ্রহ, live server) — শ্রমসাধ্য; tool bug রিপোর্ট করে উন্নয়নে অবদান।
- LLM-Jury-কে মানব agreement দিয়ে যাচাই; সৎ threats।

## J. Explicit limitations (p.39–41 Threats)
- Open-source server — সমগ্র population প্রতিনিধিত্ব নাও করতে পারে।
- SonarQube vulnerability exhaustive নয় (যদিও CWE Top 25, OWASP Top 10 কভার করে); SonarQube “bug” সবসময় প্রকৃত fault নয়।
- SDK import-ভিত্তিক mining — অন্য SDK ব্যবহারকারী server বাদ পড়তে পারে।
- mcp-scan শুধু ৮৩-এর নমুনায় (৯৫% CI, ১০% margin); reflection-ভিত্তিক — source code, fuzzing, runtime monitoring নেই।
- Star filter (≥১০) গুণমানের দুর্বল proxy; sustainability metric exhaustive নয়, কিছু domain-এ তুলনামূলক median অনুপলব্ধ।

## K. Inferred limitations (⚠️ অনুমান)
- **“১,৮৯৯ server মূল্যায়ন” দাবি বিভ্রান্তিকর:** abstract-এ ১,৮৯৯, কিন্তু SonarQube বিশ্লেষণ **৫৮৩**-এ এবং mcp-scan **৭৩**-এ; শতাংশগুলোর denominator ভিন্ন ও abstract-এ স্পষ্ট নয়।
- **Tool poisoning ৫.৫% ≈ ৭৩-এর ৪টি server** — অত্যন্ত ছোট absolute সংখ্যা; ±১০% margin-এ প্রকৃত হার ০–১৫%-এর মধ্যে যেকোনো কিছু; “credential exposure-এর চেয়ে বেশি প্রচলিত” তুলনা (৫৮৩-এ ৩.৬%) ভিন্ন নমুনা ও ভিন্ন tool-এর — পরিসংখ্যানগতভাবে দুর্বল।
- **False positive যাচাই অনুপস্থিত:** SonarQube vulnerability/mcp-scan finding-এর precision হাতে যাচাই নয় (LLM-Jury কেবল pattern clustering-এর জন্য); “tool poisoning” flag প্রকৃত ক্ষতিকর উদ্দেশ্য নাকি অস্বাভাবিক description তা অস্পষ্ট; responsible disclosure উল্লেখ নেই।
- **API-স্তরের নিরাপত্তা অনুপস্থিত:** MCP server যে REST API wrap করে (P032-এর ৮৮.৬%) তার **authorization scope, destructive operation exposure, least privilege** — BOLA/BFLA-ধাঁচের ঝুঁকি (T3) — বিশ্লেষিত নয়; শুধু code-level ও description-level।
- **Health ≠ quality:** commit/সপ্তাহ বেশি নতুন hype-চালিত project-এর বৈশিষ্ট্য; পুরোনো ecosystem-এর সঙ্গে তুলনা বয়স-পক্ষপাতদুষ্ট (age-normalization সত্ত্বেও)।
- ২০২৫-এর মাঝামাঝি snapshot — দ্রুত পরিবর্তনশীল ecosystem; MCP spec নিজেও (OAuth 2.1 auth, remote transport) পরিবর্তিত।

## L. Threats to validity
- উপরে J; inferable: denominator ambiguity, ছোট dynamic নমুনা, finding precision অযাচাইকৃত।

## M. Reproducibility
- Dataset প্রকাশিত (দাবি); SonarQube open; mcp-scan proprietary guardrail API নির্ভর ও সংস্করণ-সংবেদনশীল; credential-নির্ভর dynamic setup — **মাঝারি**।

## N. Opportunities (hypothesis)
- **MCP security testing beyond descriptions:** REST fuzzing (P006/P007) ও access-policy oracle (P015)-কে MCP tool interface-এ প্রয়োগ — authorization, destructive tool, cross-tenant leak (BOLA-in-MCP); লেখকদের স্বীকৃত “no fuzzing/runtime tool” gap।
- **Least-privilege MCP generation ও audit:** P032-এর omission pattern (auth/config/destructive omit) + এই paper-এর excessive permission finding → policy-as-code checker।
- **Tool-poisoning detection-এর precision/recall benchmark** — labeled ক্ষতিকর ও নিরীহ description; LLM-ভিত্তিক detector তুলনা।
- **MCP–REST spec consistency:** MCP tool schema বনাম underlying OpenAPI-র mismatch (P001/P004/P018-এর ধারণা) — নিরাপত্তা ও সঠিকতা উভয়ের জন্য।
- **MCP server evolution ও breaking change** (T5): tool schema পরিবর্তনে agent ভাঙা (P022, P025-এর differential testing MCP-তে)।
- Longitudinal ecosystem health (T9 সংযোগ)।

## O. Relationships
- **Complements P032** (MCP-REST mapping ও generation) — P032 functional, P036 security/maintainability।
- **Extends T3 concerns** (P012–P015) নতুন agent-tool surface-এ; P029-এর credential/security API misuse-এর সঙ্গে সাদৃশ্য (credential exposure)।
- **Relates to P033/P034** (tool-using LLM) — tool supply chain-এর ঝুঁকি।
- **Relates to P028** (description quality) — tool description নিজেই attack surface।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract (১,৮৯৯; ৭.২%; ৫.৫%; ৬৬%; ১৪.৪%) | p.1 L15–32 |
| MCP adoption | p.2 L86–97 |
| Tool poisoning, বাস্তব ঘটনা | p.3 L113–134 |
| RQ-0–RQ-2 ও finding সারাংশ | p.4–5 L172–226 |
| Contributions | p.5 L228–254 |
| GitHub mining (১,৭১৫ → ১,৫৫৬) | p.14 L879–893 |
| Star filter → ৫৮৩ | p.15 L948–956 |
| Health metrics (Table 2) | p.15–16 L961–1065 |
| SonarQube workflow | p.17 L1164–1176 |
| mcp-scan sampling (৮৩ → ৭৩) | p.17–18 L1178–1239 |
| LLM-Jury, κ ০.৯ | p.18–19 L1277–1329 |
| Vulnerability pattern (Table 6) | p.26 L1781–1800 |
| Tool poisoning ও mcp-scan অন্ধবিন্দু | p.31 L1985–1999 |
| Threats | p.39–41 L2979–3049 |

**Document integrity:** Body সম্পূর্ণ; Table 1–6 ও smell/bug taxonomy table column-split — নির্দিষ্ট per-pattern সংখ্যা পুনর্গঠন করা হয়নি; Fig.1–২ (motivating example) আংশিক; Cochran-সূত্র হারিয়েছে; appendix (LLM-Jury prompt, clustering model) পড়া হয়নি।
