# RESEARCH_STATE

**শেষ হালনাগাদ:** 2026-11-16 (Claude)
**বর্তমান phase:** Literature phase A–E সম্পন্ন। এখন R1-এর execution চলছে (§9)।
- E0, E1, E2 সম্পন্ন, আর code-mutation ground truth (E5_codemut)-ও।
- **Roadmap E4 (triage মূল্যায়ন, RQ2):** কৃত্রিম fault-এ (E4) আর আসল developer fix-এ (E6) মূল্যায়ন সম্পন্ন। দুটোতেই zero-shot > codebook v0.6 (`08_experiments/E6_realfix/E6_RESULTS.md`)।
- **E7 (repair direction, ৪৫টি নতুন fix):** H-E7-1 আর H-E7-2 দুটোই PASS। তবে proposition-only control দেখিয়েছে, divergence_kind-এর সংকেত proposition-এর ভাষাতেই আছে (`08_experiments/E7_repairdir/E7_RESULTS.md`)।
- **E8 + E8b (direction-blind proposition):** pooled primary PASS (deliberate → SPEC 39/48, accidental → SPEC 0/10, p = 1.8e-6)। Miss-rate দাবি টেকেনি।
- **পরের ধাপ:** সিদ্ধান্ত বাকি (DAY_2026-11-16 §৬ দেখুন)।

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
2. ✅ (2026-11-13) P038 সমাধান: সঠিক PDF `paper/P038.pdf`, analysis ও matrix নতুন করে, final table পুনর্নির্মিত, T9 report হালনাগাদ। পূর্বের নির্দেশ ছিল: P038-এর সঠিক PDF (Ponce et al. 2025) পেলে `P038_analysis.md` পুনর্লিখন → `build_evidence_matrix.py` ও `build_final_table.py` পুনরায় চালানো → T9 cluster report হালনাগাদ।
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
     - আমাদের checker P001-এর oracle category ৮৫–৯৭% re-detect করে। (সংশোধন 2026-11-13: এটি category-level; constraint-level agreement ও negative control বাকি — T4 R01।) Undeclared-property message: default ০/২৭, strict ২৭/২৭।
   - ✅ Codebook v0.2।
5. ▶️ Roadmap E2 প্রস্তুতি (2026-11-13) — `08_experiments/E2_labelling/`: P001-এর ৭৩টি F_OAS-এর labelling sheet + rule-based baseline (SPEC ৩৭, UNDECIDABLE ৩৬)। বাকি: দুইজন labeller-এর manual label ও κ।
   - নোট: repo-তে নতুন `.venv` সক্রিয়, তাতে pandas নেই — script চালাতে `/usr/bin/python3` ব্যবহার করতে হবে।

## 7. Context reset হলে

এই ফাইল → `02_screening/final_papers.md` → `02_screening/selection_methodology.md` → `07_audit/research_quality_audit.md` পড়ুন। Scripts: `00_protocol/scripts/`।

## 8. Claude + Codex সহযোগিতা (2026-11-13 থেকে)
- সমন্বয়: `09_collab/COLLAB_BOARD.md` (task, owner, status, log), নিয়ম `09_collab/PROTOCOL.md`, Codex-এর জন্য `research/AGENTS.md`।
- Codex model: gpt-6.1-sol। T2 (high), T3 (xhigh), T4 (xhigh), T9 (medium + web) চালু হয়েছে। T9 সম্পন্ন ও Claude-এর review শেষ।
- Supervisor docker allow rule যোগ করেছেন → T7 (scout-api pilot) T5 harness-এর পরে।
- **2026-11-14:** প্রথম বাস্তব pilot (Batch 1, scout-api) সম্পন্ন — `08_experiments/E1_pilot/pilot_results/BATCH1_RESULTS.md`। T11 (triage v0.3) গৃহীত; T13 (Codex, v0.3 re-labelling) চলমান। পরবর্তী: RESPONSE_ORACLE-এর seed-নির্ভরতা ব্যাখ্যা, baseline-এর ৫৩টি violation-এর triage, আরও SUT।
- **2026-11-14 (পরবর্তী অংশ):**
  - **Batch 2 (scout-api):** 15/15 run, প্রতিটিতে 4,703টি exchange। Baseline-এ 99টি fingerprint। ফল: `08_experiments/E1_pilot/pilot_results/BATCH2_RESULTS.md`।
  - **Labeller A (Claude, source-ভিত্তিক):** 99টি fingerprint label করা শেষ। ফল sealed রাখা হয়েছে, যতক্ষণ না T15 শেষ হয়।
  - **Labelling protocol (supervisor-এর সিদ্ধান্ত):** labeller A = Claude, labeller B = Codex (blind); মতভেদের adjudication করবেন supervisor। Report-এ লিখতে হবে "LLM×2 + human adjudication"।
  - **T13 গৃহীত:** v0.3 triage বনাম Codex labels — κ 0.75; দুজনেই decide করেছে এমন item-এ 42/43 মিল। দুটোই Codex-এর, তাই স্বাধীন নয়।
  - **T14 গৃহীত:** harness_v2। Petstore batch সম্পন্ন — `PETSTORE_RESULTS.md`: RESPONSE_ORACLE তিন seed-এই কাজ করে; REQUEST_STRICT-এ replay fresh-এর চেয়ে বেশি ধরে।
  - **Tools:** specmut-এ `--only-ops`, নতুন `tools/eligible_ops.py`; harness_v2-তে `ORACLE_POOL=baseline`।
  - **Market:** smoke run সফল; batch চলমান।
  - **চলমান Codex task:** T15 (blind labeller B)।
  - **পরবর্তী:**
    - Market-এর ফল।
    - A–B agreement ও adjudication তালিকা।
    - Pool-সহ RESPONSE_ORACLE পুনরায় চালানো।
    - Petstore ও market baseline-এর labelling।
    - cwa-verification build।
- 🚩 **RESUME POINT (2026-11-14, বিদ্যুৎ বিভ্রাট):** `09_collab/HANDOFF.md` — কী শেষ, কী থামানো হয়েছে, পুনরায় চালানোর ঠিক command, আর পরের কাজের ক্রম।
- **Codex পর্যবেক্ষণ:** `09_collab/watch_codex.sh`।
  - কোনো argument ছাড়া: কী চলছে আর board-এর অবস্থা।
  - `-f`: live দেখা।
  - `Txx`: কোনো task-এর শেষ পদক্ষেপ।
  - Codex-এর প্রতিটি launch-এর log যাবে `09_collab/logs/Txx.log`-এ।
  - Codex session `~/.codex/sessions/`-এ থাকে, তাই `codex exec resume <id>` দিয়ে আগের session চালিয়ে যাওয়া যায় (T16 এভাবে T15-এর session-এ চালানো হয়েছে)।

## 9. R1 execution stage (2026-11-15)
| Roadmap ধাপ | অবস্থা | মূল artifact |
|---|---|---|
| E0 novelty | ✅ | `06_final_recommendations/R1_novelty_check_E0.md` |
| E1 SUT + fuzzing | ✅ চার SUT, Schemathesis + EvoMaster, specmut-এর চার fault class | `08_experiments/E1_pilot/pilot_results/PILOT_SUMMARY.md`, `FUZZER_COMPARE.md`, `NOISE_FLOOR_SPEC.md`, `STRICT_ABLATION.md` |
| E2 pilot labelling | ✅ 161টি fingerprint, A–B κ 0.73, codebook v0.6.1 | `08_experiments/E2_labelling/FINAL_LABELS.md`, `08_experiments/R1_triage_codebook.md` |
| (অতিরিক্ত) code-mutation GT + blind LLM labelling | ✅ v1–v3; v3 = codebook v0.6-এর held-out মূল্যায়ন | `08_experiments/E5_codemut/E5_RESULTS.md`, `E5_BLIND_RESULTS.md` |
| E3 Respector spec তুলনা | ⏭️ হয়নি | — |
| **E4 triage মূল্যায়ন (RQ2)** | ▶️ প্রথম ধাপ সম্পন্ন: SPEC-দিকের held-out set। macro-F1: M1 zero-shot 0.94 > M2 codebook 0.66–0.70 > M0 0.22; P2 ব্যর্থ। পরের ধাপ: আসল, developer-confirmed defect। | `08_experiments/E4_triage/E4_PLAN.md`, `E4_RESULTS.md` |
| **E6 আসল fix-এ triage (RQ2)** | ✅ n=18 (IMPL 10 / SPEC 8)। macro-F1: M1 0.86–0.88 > M2 0.70–0.72 > M0 0.36। Q1 PASS, Q2 M1 > M2, Q3 FAIL। | `08_experiments/E6_realfix/E6_PLAN.md`, `E6_RESULTS.md` |
| **E7 repair direction** (K21/K22 hypothesis) | ✅ ৪৫টি নতুন + ২৫টি exploratory item; blind C1/C2 coding (κ 0.94)। Deliberate → SPEC 26/33, accidental → SPEC 0/11, p < 0.0001। Generic-contract → SPEC 15/18 বনাম 11/26। ⚠️ Proposition-only control κ = 1.0 (A3)। | `08_experiments/E7_repairdir/E7_PLAN.md`, `E7_RESULTS.md`, `E7_mining/` |
| E8/E8b direction-blind propositions | ✅ E8 একা INSUFFICIENT। E8b pooled PASS: deliberate → SPEC 39/48, accidental → SPEC 0/10, p = 1.8e-6। Miss-rate দাবি টেকেনি (p = 0.31)। | `08_experiments/E8_blindprop/E8_PLAN.md`, `E8_PLAN_AMENDMENTS.md`, `E8_RESULTS.md` |
| E5 (roadmap) LLM triage + patch (RQ3) | ⏳ | — |

- সৎ মূল্যায়ন আর দিনের সারাংশ: `09_collab/reports/DAY_2026-11-15.md`, `DAY_2026-11-16.md`।
- Board: `09_collab/COLLAB_BOARD.md`।
