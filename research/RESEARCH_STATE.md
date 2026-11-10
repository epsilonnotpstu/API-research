# RESEARCH_STATE

**শেষ হালনাগাদ:** 2026-10-19 (Claude)
**বর্তমান phase:** ✅ **PHASE C, D, E সম্পন্ন** — supervisor-এর সিদ্ধান্তের অপেক্ষা (`06_final_recommendations/research_execution_roadmap.md` §14)

---

## 1. Phase অবস্থা

| Phase | অবস্থা | মন্তব্য |
|---|---|---|
| A — Independent discovery | ✅ | Claude ৬৪ (+৬ screened-out) |
| Checkpoint 1 | ✅ | Supervisor merge নির্দেশ দিয়েছেন |
| B — Merge & screening | ✅ | ১০৪ merged → ৩৮ নির্বাচিত (P001–P038) |
| Checkpoint 2 | ✅ | ৩৮/৩৮ PDF `paper/`-এ; Markdown pdftotext দিয়ে পুনর্নির্মিত (supervisor-এর ‘markdown ঠিক করো’ নির্দেশ) |
| C — Deep reading | ✅ | ৩৮/৩৮ (`Pxxx_analysis.md` + `matrix/`); `evidence_matrix.csv`, `comparative_matrix.md`, `document_integrity_report.md`, `cross_paper_synthesis.md`; ⚠️ P038 identity mismatch |
| D — Clusters & gaps | ✅ | ৯টি cluster report, `final_paper_cluster_table.md/.csv` (final table), `cluster_comparison.md`, `research_gap_register.csv` (G1–G14), `gap_validation.md` (GV01–GV17), `cluster_relationships.md`, `research_landscape_report.md` |
| E — Recommendations | ✅ | `ranked_research_topics.md` (R1–R7), `best_research_direction.md` (A: R2, **B: R1 ⭐**, C: R3), `research_execution_roadmap.md`, `final_research_report.md` |

## 2. সংখ্যা

| পরিমাপ | মান |
|---|---|
| Claude candidates (PHASE A) | 70 যাচাইকৃত (64 included) |
| Codex candidates | 60 |
| Merged unique records | 104 (Both 26 · Claude only 44 · Codex only 34) |
| Registrar-verified | 104/104 |
| Eligible after Stage 1 | 97 |
| **Papers selected** | **38** (P001–P038) |
| Verified PDF (selected) | 32/38 (OA 11 · preprint 21); **6 not verified** |
| Papers deeply analyzed | **38** (P038 = substitute document) |

## 3. PHASE B deliverables

- `02_screening/merged_candidates.csv` — ১০৪ রেকর্ড, provenance, verified/unverified link, conflict, স্কোর, সিদ্ধান্ত
- `02_screening/duplicate_resolution.md`
- `07_audit/metadata_verification_log.md`
- `02_screening/selection_methodology.md` (+ `screening_scores.json`, `_selection.json`, `_sensitivity.json`)
- `02_screening/final_papers.csv`, `final_papers.md`
- `02_screening/excluded_papers.md`
- `02_screening/download_checklist.md`, `paper_manifest.csv`
- `07_audit/research_quality_audit.md` (PHASE B section)

## 4. Missing documents / metadata

- Full text যাচাই হয়নি: **P008** AGORA, **P015** Access-policy fuzzing, **P018** Respector, **P019** RestPi, **P025** Differential regression, **P038** Microservices SLR (candidate route: `download_checklist.md`)
- P038-এর abstract আংশিক
- P032 preprint, arXiv v1–v4-এ পরিবর্তন

## 5. Assumptions ও অমীমাংসিত প্রশ্ন

- Year rule: Crossref version-of-record; অন্য বছর `year_note`-এ।
- T10 (API recommendation) চূড়ান্ত তালিকা থেকে ইচ্ছাকৃতভাবে বাদ — supervisor চাইলে M064 (TSE 2023) যোগ করা যায়।
- **প্রশ্ন:** ৬টি “Not verified” paper institutional access-এ পাওয়া যাবে কি? না গেলে প্রতিটির জন্য বিকল্প (`excluded_papers.md`-এর priority alternate) প্রস্তাব করতে পারি।
- **প্রশ্ন:** Event-driven/async API নিয়ে লক্ষ্যভিত্তিক অতিরিক্ত search এখনো হয়নি — PHASE D-র gap validation-এর সময় করা হবে কি?

## 5b. Download ও conversion অবস্থা (2026-10-19)

- `paper/`-এ: **৩৩/৩৮** PDF — P001–P009 supervisor-এর `research/Paper/` থেকে কপি (মূল ফাইল অপরিবর্তিত), P010–P038-এর ২৪টি স্বয়ংক্রিয় (`paper/download_log.csv` — উৎস, version, sha256, first-page title match)।
- অনুপস্থিত (৫): P013, P014 (local DNS/VPN route সমস্যা), P015, P018, P038 (publisher-only) — supervisor-এর manual download।
- markitdown 0.1.8 দিয়ে ৩৩টি Markdown: `03_papers_markdown/` + `conversion_report.csv`। **২৮/৩৩ ফাইলে শব্দের মাঝে space হারিয়েছে** (merged-token rate ০.০১–০.৩২); একই PDF-এ pdftotext-এর rate ≈০ ও page break সংরক্ষিত। Converter পরিবর্তনের সিদ্ধান্ত supervisor-এর।

## 5c. PHASE C অগ্রগতি

- Markdown: `03_papers_markdown/Pxxx.md` (pdftotext, `<!-- page N -->` marker); পুরোনো markitdown কপি `_markitdown/`-এ।
- পাঠ-ক্রম: P001 → P038। **সম্পন্ন: P001–P038** (প্রতিটির `04_paper_analysis/Pxxx_analysis.md` + `matrix/Pxxx.json`, cluster সহ)। পরবর্তী: synthesis (evidence matrix, integrity report, cross-paper synthesis) → PHASE D।
- ⚠️ **P038 IDENTITY MISMATCH:** supervisor-প্রদত্ত PDF = Ghani et al. 2019, IJIE (10.30880/ijie.2019.11.08.008), নির্বাচিত Ponce et al. 2025, IST (10.1016/j.infsof.2025.107870) নয়। প্রদত্ত document labelled substitute হিসেবে বিশ্লেষিত (confidence Low); Ponce 2025-এর কোনো দাবি ব্যবহার হয়নি। সঠিক PDF পেলে পুনর্বিশ্লেষণ। বাকি ৩৭টি first-author check-এ মিলেছে।
- Supervisor নির্দেশ (2026-10-19): পাঠের সঙ্গে সঙ্গে cluster-এ ভাগ করা এবং শেষে একটি final table।
- Evidence location রীতি: `p.N` = PDF page marker, `L` = Markdown line number।

## 6. পরবর্তী নিরাপদ ধাপ

1. Supervisor সিদ্ধান্ত (roadmap §14): Option (R1/R2/R3), LLM ব্যবহারের নীতি, scope।
2. P038-এর সঠিক PDF (Ponce et al. 2025) পেলে `P038_analysis.md` পুনর্লিখন → `build_evidence_matrix.py` ও `build_final_table.py` পুনরায় চালানো → T9 cluster report হালনাগাদ।
3. ✅ R1 E0 সম্পন্ন (2026-11-09): **GO** — `06_final_recommendations/R1_novelty_check_E0.md`। বাকি: 2504.08113 ও TOSEM 10.1145/3491038 পূর্ণ পাঠ; `restest.us.es` archive-এর প্রাপ্যতা (TLS সমস্যা) supervisor-এর browser থেকে যাচাই; ACM DL বা IEEE-তে search।
4. ▶️ Roadmap E1 আংশিক (2026-11-09) — `08_experiments/README.md`:
   - নিজস্ব `specmut` tool (Swagger 2 + OAS3, ground-truth manifest); ১৪৪/১৪৪ check পাস।
   - Triage codebook v0.1।
   - ৩৬টি EMB spec-এর mutability তালিকা।
   - Pilot SUT প্রস্তাব: market, swagger-petstore, scout-api, cwa-verification।
   - ⛔ SUT build বা run (external code) auto-mode-এ বাতিল — supervisor-এর অনুমতি বা নিজে চালানো প্রয়োজন।
   - ✅ (পরবর্তী অংশ) Analysis pipeline সম্পন্ন: `conformance.py`, `attribute.py`, `mitm_fulllog.py`; replay test pass।
   - ✅ P001-এর ১৪৭টি confirmed fault বিশ্লেষণ (`08_experiments/E1_pilot/P001_empirical_findings.md`):
     - F_OAS confirm-হার ১৪.৫% বনাম F_2XXP ৫৭.১%।
     - F_OAS-এর ১২% কেবল strict validator-এ violation।
     - Amadeus spec-এ double-escaped pattern (নিশ্চিত SPEC ত্রুটি)।
     - আমাদের checker P001-এর verdict ৮৫–৯৭% পুনরুৎপাদন করে।
   - ✅ Codebook v0.2।

## 7. Context reset হলে

এই ফাইল → `02_screening/final_papers.md` → `02_screening/selection_methodology.md` → `07_audit/research_quality_audit.md` পড়ুন। Scripts: `00_protocol/scripts/`।
