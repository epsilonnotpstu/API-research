# RESEARCH_STATE

**শেষ হালনাগাদ:** 2026-10-19 (Claude)
**বর্তমান phase:** ▶️ **PHASE C চলছে** (supervisor 2026-10-19-এ সব ৩৮টি PDF দিয়ে ‘next stage’ শুরুর নির্দেশ দিয়েছেন)

---

## 1. Phase অবস্থা

| Phase | অবস্থা | মন্তব্য |
|---|---|---|
| A — Independent discovery | ✅ | Claude ৬৪ (+৬ screened-out) |
| Checkpoint 1 | ✅ | Supervisor merge নির্দেশ দিয়েছেন |
| B — Merge & screening | ✅ | ১০৪ merged → ৩৮ নির্বাচিত (P001–P038) |
| Checkpoint 2 | ✅ | ৩৮/৩৮ PDF `paper/`-এ; Markdown pdftotext দিয়ে পুনর্নির্মিত (supervisor-এর ‘markdown ঠিক করো’ নির্দেশ) |
| C — Deep reading | ▶️ চলছে | C1 automated scan সম্পন্ন (`04_paper_analysis/integrity_scan.csv`); C2 প্রতি paper: `Pxxx_analysis.md` + `matrix/Pxxx.json` |
| D — Clusters & gaps | ⬜ | |
| E — Recommendations | ⬜ | |

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
| Papers deeply analyzed | 0 |

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
- পাঠ-ক্রম: P001 → P038। **সম্পন্ন: P001–P025** (প্রতিটির `04_paper_analysis/Pxxx_analysis.md` + `matrix/Pxxx.json`, cluster সহ)। পরবর্তী: P026।
- Supervisor নির্দেশ (2026-10-19): পাঠের সঙ্গে সঙ্গে cluster-এ ভাগ করা এবং শেষে একটি final table।
- Evidence location রীতি: `p.N` = PDF page marker, `L` = Markdown line number।

## 6. পরবর্তী নিরাপদ ধাপ

Supervisor-এর নিশ্চিতকরণের অপেক্ষা: “Markdown files ready”। তারপর PHASE C1: `03_papers_markdown/` scan → P-ID mapping → `04_paper_analysis/document_integrity_report.md`।

## 7. Context reset হলে

এই ফাইল → `02_screening/final_papers.md` → `02_screening/selection_methodology.md` → `07_audit/research_quality_audit.md` পড়ুন। Scripts: `00_protocol/scripts/`।
