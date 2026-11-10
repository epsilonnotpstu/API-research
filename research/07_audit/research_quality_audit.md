# Research Quality Audit (চলমান লগ)

এই ফাইল প্রতিটি phase-এর শেষে QA checklist, পাওয়া ত্রুটি, সংশোধন ও অমীমাংসিত বিষয় রেকর্ড করে।

---

## PHASE A — Claude independent discovery (2026-10-19)

### A. QA checklist (prompt-এর ১০টি পয়েন্ট)

| # | চেক | ফল | প্রমাণ/মন্তব্য |
|---|---|---|---|
| 1 | প্রতিটি paper reference বাস্তব | ✅ | ৭০/৭০ seed Crossref বা DataCite-এ resolve হয়েছে; raw: `01_discovery/raw/verify/C??.json` |
| 2 | Title ও identifier সামঞ্জস্যপূর্ণ | ✅ (১টি ব্যতিক্রম ধরা পড়েছে ও সংশোধিত) | ৬৭টিতে registrar বনাম OpenAlex title similarity = 1.0; C56-এ 0.26 (OpenAlex ত্রুটি) — OpenAlex data বাদ |
| 3 | Link label সঠিক | ✅ | `canonical_url`, `doi_url`, `direct_pdf_url_verified`, `alt_oa_url` আলাদা; PDF শুধুমাত্র `%PDF` signature-এ verified |
| 4 | Duplicate নেই | ✅ | DOI/title/ID uniqueness script-চেক; version-সম্পর্ক discovery report §4-এ |
| 5 | সিদ্ধান্ত প্রমাণ-সমর্থিত | ✅ (abstract-স্তরে) | কোনো full-text দাবি নেই; সব finding “author claim/author-reported” হিসেবে চিহ্নিত |
| 6 | বিপরীত প্রমাণ বিবেচিত | ⚠️ আংশিক | C41 (replication, বিপরীত ফল) অন্তর্ভুক্ত; সক্রিয় contradiction-search PHASE D-র কাজ |
| 7 | অসমর্থিত দাবি চিহ্নিত | ✅ | Landscape ও report-এ “hypothesis” লেবেল; কোনো gap “প্রতিষ্ঠিত” বলা হয়নি |
| 8 | Gap অতিরঞ্জিত নয় | ✅ | PHASE A-তে কোনো gap claim নেই; H1–H5 hypothesis |
| 9 | CSV ও Markdown সামঞ্জস্য | ✅ | Markdown CSV থেকে script দিয়ে তৈরি (`build_catalog_md.py`) |
| 10 | পুনরুৎপাদনযোগ্যতা | ✅ | সব script `00_protocol/scripts/`; raw response সংরক্ষিত; search_log-এ request URL |

### B. পাওয়া ত্রুটি ও সংশোধন

| # | ত্রুটি | কীভাবে ধরা পড়ল | সংশোধন |
|---|---|---|---|
| E1 | OpenAlex full-text search + citation sort-এ অপ্রাসঙ্গিক ফল (NumPy, SciPy…) | OP003/OP004 ফল পর্যালোচনা | `--ta --cs` mode যোগ; noisy query লগে রাখা হয়েছে |
| E2 | OpenAlex arXiv DOI → ভুল শিরোনাম (ToolLLM ↔ “Counterfactually Auditable…”) | DataCite cross-check | সব arXiv record DataCite/arxiv.org দিয়ে যাচাই; C56-এ OpenAlex data বাদ |
| E3 | Crossref `issued` = journal issue বছর (যেমন C31 = 2027, C36 = 2021) | OpenAlex বছরের সঙ্গে অমিল | `published-online/print` আলাদাভাবে আনা; year rule ও `year_note` |
| E4 | API-evolution trend-এ ২০২২ spike (336) | Normalization-এর সময় অস্বাভাবিকতা | Source group-by: ৩০১টি একক Zenodo deposit — artifact হিসেবে চিহ্নিত |
| E5 | DataCite author format “Family, Given” | Catalog পর্যালোচনা | Normalize করা হয়েছে |
| E6 | arXiv abs-page version parser সর্বশেষ (non-link) version ধরে না | C64 আগে v4 দেখা গেলেও parser v3 দেখায় | Version count সরাসরি page-read থেকে hard-code ও উৎস উল্লেখ |
| E7 | C08 ও C51-এর OpenAlex abstract কাটা | Abstract dump পড়ার সময় | C08: Consensus পূর্ণ abstract; C51: “Partial abstract” চিহ্নিত |
| E8 | প্রথম PDF-probe run-এ arxiv.org-এ ১৫ s crawl-delay মানা হয়নি (<৩০ request) | robots.txt পরে পড়া হয়েছে | পরবর্তী সব arxiv.org request ≥১৫ s; ঘটনাটি স্বচ্ছতার জন্য রেকর্ড |
| E9 | Landscape-এ research group-এর নাম স্মৃতি থেকে লেখা | Self-review | Author count Crossref থেকে যাচাই করে report-এ লেখা; landscape-এ “PHASE B-তে নিশ্চিত করতে হবে” যোগ |

### C. Tool/source সীমাবদ্ধতা (রেকর্ড)

- arXiv export API: HTTP 429 (৪টি query চালানো যায়নি)
- Semantic Scholar Graph API: HTTP 429 (API key নেই)
- DBLP: anti-bot challenge page — circumvent করা হয়নি
- OpenAlex: দৈনিক free credit শেষ (2026-10-19 ~02:48 UTC; retry-after ≈ ২১ ঘণ্টা) → পরবর্তী কাজ Crossref/DataCite/WebSearch দিয়ে
- Consensus: কঠোর rate-limit; ৩টি সফল query

### D. অমীমাংসিত বিষয় (PHASE B-তে বহন)

1. C31: abstract নেই — বিষয়বস্তু যাচাই করা যায়নি।
2. C65: শুধু আংশিক abstract।
3. C13 ↔ TOSEM 2025 এবং C30 ↔ JSS 2026 — extended version কিনা।
4. C56, C70: retraction status Not assessed।
5. ১৯টি paper-এর OA full text যাচাই হয়নি।
6. Research-group concentration (২৮%) — selection-এ ভারসাম্য দরকার।
7. Event-driven/async API ও API usability/privacy search-এর ঘাটতি।
8. arXiv preprint version বনাম published version-এর বিষয়বস্তু-পার্থক্য যাচাই হয়নি।

---

## PHASE B — Merge, verification & screening (2026-10-19)

### A. QA checklist

| # | চেক | ফল | প্রমাণ/মন্তব্য |
|---|---|---|---|
| 1 | প্রতিটি paper reference বাস্তব | ✅ | ১০৪/১০৪ merged record registrar-যাচাইকৃত; Codex-only ৩৪টি স্বাধীনভাবে পুনর্যাচাই (`02_screening/raw/verify_codex/`) |
| 2 | Title ও identifier সামঞ্জস্যপূর্ণ | ✅ (২টি সংশোধন) | NDSS DOI (Codex ভুল, doi.org 404) ও Morest শিরোনাম (Codex truncated) — `metadata_verification_log.md` K1, K2 |
| 3 | Link label সঠিক | ✅ | Verified PDF শুধু `%PDF` probe বা first-page text মিলিয়ে; 403/HTML/timeout → “unverified candidate”; Codex-এর ২১টি PDF দাবি স্বাধীনভাবে নিশ্চিত, ২টি “PDF candidate” আসলে HTML |
| 4 | Duplicate নেই | ✅ | DOI/title/ID uniqueness script-চেক পাস; ১টি false-positive match ধরা ও বাতিল (RESTTESTGEN ≠ RESTest) |
| 5 | সিদ্ধান্ত প্রমাণ-সমর্থিত | ✅ (abstract-স্তরে) | Codex-এর templated `findings` ব্যবহার করা হয়নি; Codex-only নির্বাচিতদের abstract নিজে আনা হয়েছে |
| 6 | বিপরীত প্রমাণ বিবেচিত | ⚠️ আংশিক | P023 (semver replication, পূর্ববর্তী study-র বিপরীত) নির্বাচিত; P023 বনাম ২.৩০%/১১.৫৮% BC-হারের আপাত-বিরোধ PHASE C-র জন্য নোট |
| 7 | অসমর্থিত দাবি চিহ্নিত | ✅ | “author claim/abstract-level” লেবেল; preprint চিহ্নিত |
| 8 | Gap অতিরঞ্জিত নয় | ✅ | PHASE B-তে কোনো gap claim নেই |
| 9 | CSV ও Markdown সামঞ্জস্য | ✅ | সব Markdown CSV থেকে script-generated; integrity script “ALL CHECKS PASSED” (৩৮ ID, title, PDF link, manifest–checklist সারিবদ্ধতা) |
| 10 | পুনরুৎপাদনযোগ্যতা | ✅ | `merge_match.py → merge_build.py → select_papers.py → final_build.py`; সব স্কোর ও override `screening_scores.json`-এ; sensitivity `_sensitivity.json` |

### B. Codex তালিকার গুণগত মূল্যায়ন (স্বাধীন cross-check)

**শক্তি:** ৬০/৬০ পরিচয় সঠিক; ২১/২১ “verified PDF” দাবি সত্য; ৩৪টি নতুন রেকর্ড যোগ করেছে যার ৪টি চূড়ান্ত তালিকায় গুরুত্বপূর্ণ ফাঁক পূরণ করেছে (industrial-scale online testing, WARDroid, RestPi, LO2 dataset); documentation ও recommendation-এ Claude-এর চেয়ে বেশি কভারেজ।
**দুর্বলতা:** (১) `findings` কলাম templated — paper-নির্দিষ্ট প্রমাণ নেই; (২) NDSS DOI ভুল ও quality report-এ উল্টো দাবি; (৩) একটি magazine column-কে “empirical evidence” বলা; (৪) ১১টি বৈধ arXiv route অনুপস্থিত; (৫) ২টি HTML URL “PDF candidate” হিসেবে; (৬) ৮টি metadata-only রেকর্ড; (৭) LLM/MCP ও API misuse-এ কম কভারেজ।

### C. Claude-এর নিজস্ব PHASE A ত্রুটি যা PHASE B-তে ধরা পড়েছে

| # | ত্রুটি | সংশোধন |
|---|---|---|
| CB1 | RESTler, API-evolution SLR, Online testing, GraphQL SMS-এর বৈধ OA কপি PHASE A-তে খুঁজে পাইনি | PHASE B-তে যাচাই করে যোগ (first-page text মিলিয়ে) |
| CB2 | Industrial-scale testing (FSE 2022), mobile-client API security (S&P 2018), PL-ভিত্তিক spec inference, API anomaly dataset — PHASE A-তে অনুপস্থিত | Codex merge-এ পূরণ |
| CB3 | Title-similarity matching-এ false positive-এর ঝুঁকি (০.৯৩) | DOI-ভিন্ন হলে manual যাচাই বাধ্যতামূলক করা হয়েছে |
| CB4 | Final annotation-এ merged ID রেফারেন্স পাঠকের কাছে অস্পষ্ট | Builder P-ID-তে map করে |

### D. অমীমাংসিত (PHASE C-তে বহন)

1. ৬টি নির্বাচিত paper-এর full text যাচাই হয়নি — P008, P015, P018, P019, P025, P038।
2. ২৩টি নির্বাচিত paper preprint/submitted version-এ নির্ভরশীল (পাঠ্য-পার্থক্য সম্ভব)।
3. P032 preprint ও version-অস্থির।
4. Scoring একক screener-এর; inter-rater reliability নেই।
5. Event-driven/async API, API privacy, performance — চূড়ান্ত তালিকায় অনুপস্থিত (সাহিত্য ও search উভয় সীমাবদ্ধতা)।
6. Retraction যাচাই সীমিত (Retraction Watch database ব্যবহৃত হয়নি)।

---

## PHASE C — Deep reading (2026-10-19)

### A. QA checklist

| # | চেক | ফল | প্রমাণ/মন্তব্য |
|---|---|---|---|
| 1 | প্রতিটি নির্বাচিত paper-এর Markdown পাঠ | ✅ ৩৮/৩৮ (P038 substitute) | `04_paper_analysis/Pxxx_analysis.md` (A–P section) |
| 2 | ফাইল ↔ paper identity | ⚠️ ১টি ব্যর্থ | First-author check: P038 = Ghani et al. 2019, নির্বাচিত Ponce et al. 2025 নয়; title-word check এটি ধরতে পারেনি |
| 3 | প্রতিটি দাবির page/line প্রমাণ | ✅ | §P evidence table (p.N = PDF page marker, L = Markdown line) |
| 4 | Author-reported বনাম inferred limitation আলাদা | ✅ | §J বনাম §K (⚠️); JSON `author_limitations` বনাম `analyst_limitations` |
| 5 | Opportunity-কে hypothesis হিসেবে লেবেল করা | ✅ | §N “(hypothesis)” |
| 6 | Conversion ত্রুটির প্রভাব রেকর্ড | ✅ | `document_integrity_report.md`; অনিশ্চিত সংখ্যা চিহ্নিত (P010, P022, P033, P037) |
| 7 | Matrix ↔ analysis সামঞ্জস্য | ✅ | `evidence_matrix.csv` script দিয়ে JSON থেকে (`00_protocol/scripts/build_evidence_matrix.py`); ৩৮টি JSON-এর key-set অভিন্ন |
| 8 | Paper-এর ভেতরের অসঙ্গতি রিপোর্ট | ✅ | P009, P021, P029, P031, P032, P034, P036, P038 (`cross_paper_synthesis.md` থিম ৭) |
| 9 | Retrieved content-কে নির্দেশ হিসেবে গণ্য না করা | ✅ | Paper text-এর ভেতরের কোনো নির্দেশ অনুসরণ করা হয়নি |
| 10 | Cross-paper synthesis-এ বিরোধ বিবেচনা | ✅ | `cross_paper_synthesis.md` §4 |

### B. ত্রুটি ও সংশোধন

| # | ত্রুটি | ধরা পড়ল | সংশোধন |
|---|---|---|---|
| C1 | P032-এ ৮৩২টি NUL/control byte — `grep` নীরবে ব্যর্থ | grep output শূন্য; `grep -a` ও Python count | Control byte অপসারণ; `markdown_fixes_log.csv` |
| C2 | P038 PDF ভুল paper (supervisor manual download) | First-author surname check | Substitute হিসেবে বিশ্লেষণ, confidence Low; সঠিক PDF প্রয়োজন |
| C3 | Read tool size limit (>২৫K token ফাইল) | Tool error | Section-ভিত্তিক compressed পাঠ ও offset/limit read; কোনো section বাদ পড়েনি (references ছাড়া) |
| C4 | Table column-split | পাঠের সময় | Text বা summary box-এর সংখ্যা অগ্রাধিকার পেয়েছে; অনিশ্চিত পুনর্গঠন চিহ্নিত |

### C. অমীমাংসিত

1. P038-এর সঠিক PDF (Ponce et al. 2025)।
2. ২৪টি preprint-এর সংখ্যা version of record-এর সাথে মিলিয়ে দেখা হয়নি।
3. P026, P035, P036-এর appendix পড়া হয়নি।

---

## PHASE D — Clusters & gap analysis (2026-10-19)

### A. QA checklist

| # | চেক | ফল | প্রমাণ/মন্তব্য |
|---|---|---|---|
| 1 | Paper reference বাস্তব | ✅ | সব P-ID P001–P038-এর মধ্যে (script check); বাইরের কাজ কেবল search log-এ নথিভুক্ত শিরোনাম বা ID হিসেবে, “snippet-স্তর” লেবেলসহ |
| 2 | Title/identifier সামঞ্জস্য | ✅ | `final_paper_cluster_table.csv` সরাসরি `evidence_matrix.csv` + `final_papers.csv` থেকে (script); P038 substitute-এর আলাদা metadata |
| 3 | Link label | ✅ | নতুন link যোগ হয়নি; DOI কেবল যাচাইকৃত রেকর্ড থেকে |
| 4 | Duplicate নেই | ✅ | ৩৮টি সারি, অনন্য ID |
| 5 | সিদ্ধান্ত প্রমাণ-সমর্থিত | ✅ | Cluster report-এ paper ID; gap-এ supporting paper + search ID |
| 6 | বিরোধী প্রমাণ বিবেচিত | ✅ | ১৭টি gap-validation search; ৪টি gap weakened (G6, G7, G8, G11), ৪টি partially weakened |
| 7 | অসমর্থিত দাবি চিহ্নিত | ✅ | ⚠️/[H] লেবেল; Class C আলাদা |
| 8 | Gap অতিরঞ্জিত নয় | ✅ | G1 “no dataset” → “no behavioural labels”-এ সংকুচিত; G3 broad → narrowed |
| 9 | CSV ↔ Markdown সামঞ্জস্য | ✅ | Gap ID ও GV ID cross-check script: অমিল নেই; cluster link matrix script দিয়ে যাচাই |
| 10 | পুনরুৎপাদনযোগ্যতা | ✅ | `build_evidence_matrix.py`, `build_final_table.py`, search log GV01–GV17 |

### B. ত্রুটি ও সংশোধন
| # | ত্রুটি | সংশোধন |
|---|---|---|
| D1 | Cluster report-এর প্রথম খসড়ায় dataset বিবরণ স্মৃতি থেকে (P012 SUT, P016/P018/P019 সংখ্যা, P032 “৫০টি API”) | `evidence_matrix.csv`-এর সাথে মিলিয়ে সংশোধন |
| D2 | P025 tool-এর বিবরণ অস্পষ্ট | P025 analysis থেকে “RESTler-generated suite + log diff” |
| D3 | Title-word identity check P038 ধরতে পারেনি | First-author check যোগ (PHASE C) |

### C. সীমাবদ্ধতা
- Gap-validation WebSearch snippet-স্তরের; scholarly API (OpenAlex/S2) ব্যবহৃত হয়নি (আগের quota বা 429 সমস্যা)।
- বাইরের ২০২৫–২০২৬ কাজের দাবি যাচাই হয়নি।

---

## PHASE E — Recommendations (2026-10-19)

| # | চেক | ফল | মন্তব্য |
|---|---|---|---|
| 1 | প্রতিটি প্রস্তাব কংক্রিট unresolved প্রশ্নসহ | ✅ | R1–R7 প্রতিটিতে RQ, baseline, metric |
| 2 | Weakened gap থেকে প্রস্তাব নয় | ✅ | G6/G7/G8/G11 বাদ |
| 3 | Scoring স্বচ্ছ | ✅ | `score_topics.py` + `_scoring.json`; প্রতিটি score-এর যুক্তি |
| 4 | Importance বনাম convenience আলাদা | ✅ | Significance কলাম আলাদাভাবে আলোচিত |
| 5 | Sensitivity analysis | ✅ | ৫টি weighting + ৩টি perturbation; R1 novelty-সংবেদনশীল তা স্পষ্ট |
| 6 | Novelty বা publication-এর অতিরঞ্জন নেই | ✅ | “global novelty দাবি নয়” স্পষ্ট লেখা |
| 7 | Option A/B/C | ✅ | R2 / R1 / R3 (+C′ R5) |
| 8 | Roadmap-এর ১৪টি উপাদান | ✅ | `research_execution_roadmap.md` |
| 9 | Supervisor সিদ্ধান্ত চিহ্নিত | ✅ | Roadmap §14 |

---

## R1 E0/E1 (2026-11-09)

| # | বিষয় | ফল |
|---|---|---|
| 1 | E0 novelty check | 2607.12101 ও RESTifAI পূর্ণ পাঠ; P032 v4 সর্বশেষ নিশ্চিত; P001 Zenodo পরিদর্শন; GV18–GV20 লগ করা |
| 2 | TOSEM 10.1145/3491038 (Marculescu et al.) | Open full text পাওয়া যায়নি। Repository handle (11250/2991533) ভিন্ন paper-এ resolve হয় — **শুধু abstract-স্তর** ব্যবহৃত |
| 3 | `restest.us.es` archive | TLS chain যাচাই ব্যর্থ; bypass করা হয়নি |
| 4 | `specmut` যাচাই | ১৪৪/১৪৪ property check পাস। প্রথম run-এ locality bug (no-op mutation-এর `$ref` inlining থেকে যাচ্ছিল) ধরা পড়ে সংশোধিত |
| 5 | External code execution | EMB build auto-mode classifier বাতিল করেছে; workaround করা হয়নি। Supervisor-এর সিদ্ধান্তের জন্য `08_experiments/README.md` |
| 6 | ভুল git ক্রম | Sparse-checkout-এর আগে checkout-এ পুরো EMB নামতে শুরু করেছিল; থামানো ও মুছে ফেলা হয়েছে (১৩০ MB), তারপর সঠিক sparse clone |

### R1 E1 — pipeline ও P001 বিশ্লেষণ (2026-11-09, পরবর্তী অংশ)

| # | বিষয় | ফল |
|---|---|---|
| 1 | P001 data-র সংখ্যা যাচাই | ১৪৭টি fault ও ৭৩টি F_OAS — paper-এর সংখ্যার সাথে হুবহু মেলে |
| 2 | Instrument-এর bug (replay-তে ধরা) | `$ref` parameter-এর key-ভুল, array query deserialize, content-type, date format, non-JSON body — সব সংশোধিত; regression pass |
| 3 | অনুমান চিহ্নিত | ADDITIONAL_PROPERTIES strictness, TYPE_NULL-এর SPEC-ঝোঁক, developer confirm-হারের ব্যাখ্যা — সব ⚠️/[H] |
| 4 | Double-escape উদাহরণ | Python `re` দিয়ে যাচাই; উৎস (Amadeus বনাম P001-এর রূপান্তর) অনিশ্চিত হিসেবে উল্লেখিত |
| 5 | Data licence | P001 package CC-BY 4.0; raw ফাইল git-বহির্ভূত (`_external/`) |
