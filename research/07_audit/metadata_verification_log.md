# Metadata Verification & Correction Log — PHASE B2

**প্রস্তুতকারী:** Claude | **তারিখ:** 2026-10-19
**নীতি:** কোনো agent-এর metadata অন্ধভাবে গ্রহণ করা হয়নি। Merged record-এর canonical title, author, year, venue ও DOI **registrar (Crossref/DataCite) ও official proceedings page** থেকে নতুন করে আনা হয়েছে; agent-এর CSV শুধু matching ও provenance-এর জন্য।

---

## 1. যাচাই পদ্ধতি

| ধাপ | Claude-এর ৭০ রেকর্ড | Codex-only ৩৪ রেকর্ড |
|---|---|---|
| Registrar lookup | PHASE A-তে সম্পন্ন (`01_discovery/raw/verify/`) | PHASE B-তে নতুন (`02_screening/raw/verify_codex/`) — Crossref, DataCite |
| OpenAlex consistency | PHASE A | PHASE B (single-record DOI lookup — credit লাগে না) |
| Date detail (online/print/issue) | `enrich.py` | `enrich.py` |
| arXiv version খোঁজা | DataCite search | DataCite search |
| PDF যাচাই | ranged GET + `%PDF` signature | **Codex-এর তালিকাভুক্ত সব PDF URL পুনরায় probe** (`_codex_pdf_reprobe.json`) |
| অতিরিক্ত OA খোঁজা (নির্বাচিত paper) | WebSearch + author/repository page + first-page text (`pdftotext`) মিলিয়ে | একই |

**ফল:** ১০৪/১০৪ merged record registrar-যাচাইকৃত; retraction/correction notice পাওয়া যায়নি (OpenAlex `is_retracted` ও Crossref `updated-by` অনুযায়ী — এটি পূর্ণাঙ্গ retraction audit নয়, কারণ Retraction Watch database ব্যবহার করা হয়নি)।

## 2. সংশোধন (Corrections)

| # | রেকর্ড | সমস্যা | প্রমাণ | সংশোধন |
|---|---|---|---|---|
| K1 | M014 GPTAid (NDSS 2025) | Codex DOI `10.14722/NDSS.2025.23465` | doi.org → **404**; Crossref-এ নেই। `10.14722/ndss.2025.230465` → Crossref record + doi.org 302 → `ndss-symposium.org/.../2025-465-paper.pdf` | নিবন্ধিত DOI `…230465` গৃহীত। Codex-এর quality report-এ উল্টো দাবি (“…230465 inconsistent”) — **প্রমাণ সেই দাবিকে সমর্থন করে না** |
| K2 | M072 Morest (ICSE 2022) | Codex title শুধু “Morest” | Crossref: `title=["Morest"]`, `subtitle=["model-based RESTful API testing with execution feedback"]` | পূর্ণ শিরোনাম: “Morest: Model-based RESTful API Testing with Execution Feedback” |
| K3 | M093 “APIs With GraphQL” | Codex: “abstract reports empirical evidence” | Abstract নেই; IEEE Software column (একক লেখক, practitioner essay) | Research contribution নয় → ineligible |
| K4 | Codex `findings` কলাম (৬০টিই) | বাক্যগুলো templated (যেমন “The abstract reports an evaluated technical approach with useful results…”) — paper-নির্দিষ্ট তথ্য নেই | CSV পরিদর্শন | Codex-only নির্বাচিত paper-গুলোর problem/contribution/findings Claude নিজে registrar/OpenAlex/DataCite abstract থেকে লিখেছে (`final_annotations.json`) |
| K5 | Year convention | Codex OpenAlex-বছর (প্রায়ই online-first) ব্যবহার করেছে; Claude PHASE A Crossref বছর | ৯টি রেকর্ডে ১ বছরের পার্থক্য (M015, M021, M022, M073, M086, M087, M088, M094, M096) | **একক নিয়ম:** Crossref version-of-record (published-online/print/issued-এর প্রথমটি); ভবিষ্যৎ issue-বছর হলে OpenAlex; অন্য বছর `year_note`-এ |
| K6 | M053 ToolLLM | OpenAlex arXiv DOI → ভুল শিরোনাম (sim 0.26) | DataCite + ICLR proceedings page | OpenAlex data বাদ (PHASE A-তে ধরা পড়েছিল) |
| K7 | Venue string | “Computer Standards &amp; Interfaces”, “Web-to-Mobile … &amp; …” | HTML entity | `html.unescape` |

## 3. Link যাচাই: agent-দাবি বনাম স্বাধীন probe

### 3.1 Codex-এর PDF দাবি
| Codex label | সংখ্যা | আমাদের probe |
|---|---|---|
| “Direct PDF verified (HTTP 200, PDF content type)” | 21 | **21/21 নিশ্চিত** (`%PDF`) |
| “PDF candidate identified; HTTP 200 during check” | 3 | C030 HAL ✅ PDF; **C032 handle URL → HTML (PDF নয়)**; **C053 Springer → HTML (PDF নয়)** |
| “PDF candidate… reachability check timed out” | 2 | C031, C049 — আবারও timeout; unverified |
| “Publisher PDF endpoint identified; HTTP 403” | 12 | সবগুলো 403 (ACM/ScienceDirect) — **verified হিসেবে গণ্য নয়** |

### 3.2 Codex-এ অনুপস্থিত বৈধ OA route (Claude যোগ করেছে)
- Both-pair-এ arXiv version শুধু Claude-এর রেকর্ডে: C03/2204.08348, C04/2212.14604, C05/2205.05325, C09/2312.00894, C10/2501.08598, C38/2311.08175, C41/2110.07889, C51/2409.09288 (৮টি)।
- Codex-only রেকর্ডে PHASE B-তে পাওয়া: X011/2309.08360, X020/2405.01111, X054/2504.12067।

### 3.3 Claude PHASE A-তে অনুপস্থিত, PHASE B-তে যোগ (first-page text মিলিয়ে)
| Paper | URL | মন্তব্য |
|---|---|---|
| RESTler (P006) | microsoft.com/…/2021/03/RESTler.pdf | প্রথম পৃষ্ঠা: “RESTler: Stateful REST API Fuzzing … Atlidakis, Godefroid” |
| API evolution SLR (P021) | ece.uwaterloo.ca/~wshang/pubs/mlamothe_csur_2021.pdf | author-hosted |
| Online testing (P001) | idus.us.es bitstream | OpenAlex: submittedVersion |
| GraphQL SMS (P009) | idus.us.es bitstream | OpenAlex: submittedVersion |

### 3.4 যাচাই হয়নি (unverified candidate হিসেবে চিহ্নিত)
- NSF PAR (Respector) — 120 s timeout।
- ACM `/doi/pdf/` — OpenAlex OA বললেও script-এ 403; browser-এ চেষ্টার পরামর্শ।
- MSR technical report (Differential regression) — PDF URL পাওয়া যায়নি।
- Florence/Pisa repository record (Microservices SLR) — OpenAlex: not OA।

## 4. অবশিষ্ট অনিশ্চয়তা

1. ৬টি নির্বাচিত paper-এর full text যাচাই হয়নি (P008, P015, P018, P019, P025, P038)।
2. ২১টি নির্বাচিত paper-এর জন্য শুধু arXiv preprint যাচাইকৃত, আরও ২টির (P001, P009) repository-তে submitted version — published version-এর সঙ্গে পাঠ্য-পার্থক্য PHASE C-তে মিলিয়ে দেখতে হবে।
3. Retraction-যাচাই সীমিত (Retraction Watch নয়)।
4. ICLR paper (P022, P033)-এর retraction status Not assessed (Crossref record নেই)।
5. Author list Crossref-নির্ভর; কিছু publisher author ক্রম/নাম-বানান ভিন্ন রাখতে পারে।
