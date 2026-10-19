# Duplicate Resolution — PHASE B1

**প্রস্তুতকারী:** Claude | **তারিখ:** 2026-10-19
**Script:** `00_protocol/scripts/merge_match.py` → `_match_groups.json`; `merge_build.py` → `merged_candidates.csv`

## 1. Input

| উৎস | রেকর্ড | মন্তব্য |
|---|---|---|
| `claude_candidates.csv` | 64 included | PHASE A |
| Claude-এর screened-out (যাচাইকৃত) | 6 | C12, C17, C20, C24, C42, C54 — Codex দুটি (C12=KAT, C17=Volkswagen) অন্তর্ভুক্ত করেছিল, তাই matching-এ রাখা হয়েছে |
| `codex_candidates.csv` | 60 | Codex PHASE A |
| **মোট input** | **130** | |

## 2. Matching নিয়ম (ক্রমানুসারে)

1. **Exact DOI** (case-insensitive) — Crossref-এ DOI case-insensitive।
2. **arXiv ID** (versionless)।
3. **Normalized title** (lowercase, শুধু alphanumeric) similarity ≥ 0.90 → *candidate match* — **DOI ভিন্ন হলে manual যাচাই বাধ্যতামূলক**।
4. Similarity 0.70–0.90 → শুধু manual review তালিকা; কখনো auto-merge নয়।
5. Preprint ও published version একই গবেষণা-অবদান হলে একটি রেকর্ড; version তথ্য `arxiv_id`, `arxiv_note`, `pdf_version_note`-এ সংরক্ষিত।

## 3. ফলাফল

| শ্রেণি | সংখ্যা |
|---|---|
| Automatic candidate match | 27 |
| ❌ False positive (manual-এ বাতিল) | 1 |
| ✅ নিশ্চিত duplicate pair (Both) | **26** (25 exact DOI + 1 title-match with DOI conflict — §4.2) |
| Claude only | 44 (64 + 6 − 26) |
| Codex only | 34 (60 − 26) |
| **Merged unique records** | **104** |

> নোট: 27টি automatic match-এর 25টি exact DOI-তে; বাকি 2টি title-এ — একটি সঠিক (NDSS GPTAid, দুই agent ভিন্ন DOI লিখেছিল, §4.2), একটি false positive (§4.1)।

## 4. Manual সিদ্ধান্ত

### 4.1 ❌ False positive: RESTTESTGEN ≠ RESTest
| | Claude C20 | Codex C003 |
|---|---|---|
| Title | RESTTESTGEN: Automated Black-Box Testing of RESTful APIs | RESTest: automated black-box testing of RESTful web APIs |
| DOI | 10.1109/icst46399.2020.00024 | 10.1145/3460319.3469082 |
| Venue/Year | ICST 2020 | ISSTA 2021 (demo) |
| Authors | Viglianisi, Dallago, Ceccato (Verona) | Martin-Lopez, Segura, Ruiz-Cortés (Seville) |

Title similarity 0.93 হলেও **ভিন্ন গবেষণা দল, ভিন্ন tool, ভিন্ন DOI** — আলাদা রেকর্ড (M067, M071)। এটি prompt-এ সতর্ক করা “similar title ≠ same paper” ঝুঁকির বাস্তব উদাহরণ; matching script-এর `FALSE_MATCHES`-এ নথিভুক্ত।

### 4.2 ✅ একই paper, ভিন্ন DOI: GPTAid (NDSS 2025)
- Claude: `10.14722/ndss.2025.230465` · Codex: `10.14722/NDSS.2025.23465`
- যাচাই (2026-10-19): `230465` → Crossref record আছে, doi.org 302 → official NDSS PDF; `23465` → Crossref-এ নেই, **doi.org 404**।
- সিদ্ধান্ত: একই paper (M014); **নিবন্ধিত DOI `10.14722/ndss.2025.230465`** ব্যবহৃত। Codex-এর DOI সম্ভবত arXiv metadata-য় লেখকের দেওয়া DOI থেকে এসেছে। বিস্তারিত: `07_audit/metadata_verification_log.md`।

### 4.3 Manual review (0.70–0.90) — সবগুলো **ভিন্ন paper**
| Codex | Claude | Sim | সিদ্ধান্ত |
|---|---|---|---|
| C005 ARTE (TSE) | C13 AGORA (ISSTA 2023) | 0.74 | ভিন্ন — input generation বনাম oracle |
| C015 Online testing (FSE 2022) | C31 Security testing survey (CSR 2026) | 0.76 | ভিন্ন |
| C028 SpeCrawler (arXiv 2402.11625) | C34 OASBuilder (ACL 2025; arXiv 2507.05316) | 0.87 | **সম্পর্কিত কিন্তু আলাদা রেকর্ড** — একই IBM group (Lazar, Vetzler, Boaz, Goldbraich, Amid, Anaby-Tavor); SpeCrawler পূর্বসূরি preprint, OASBuilder পরবর্তী peer-reviewed কাজ বলে প্রতীয়মান। ভিন্ন arXiv ID ও শিরোনাম বলে merge করা হয়নি; সম্পর্কটি নোট করা হলো |

### 4.4 একই কাজের version-সম্পর্ক (একটি রেকর্ডে রাখা)
| Merged | Published | Preprint/অন্য version | মন্তব্য |
|---|---|---|---|
| M012 RESTler | ICSE 2019 (10.1109/icse.2019.00083) | arXiv 1806.09739 “REST-ler: Automatic Intelligent REST API Fuzzing”; MSR-hosted PDF | arXiv শিরোনাম ভিন্ন — বিষয়বস্তু ভিন্ন হতে পারে; MSR কপির প্রথম পৃষ্ঠার শিরোনাম ICSE version-এর সঙ্গে মেলে |
| M040 OASBuilder | ACL Industry 2025 | arXiv 2507.05316 (“OASBuilder: …”) | শিরোনামে tool-নাম যোগ |
| M020 Breaking bad? | EMSE 2022 | arXiv 2110.07889; HAL copy; CWI/DANS repository record | OpenAlex-এ একাধিক work-record (index duplicate) |
| M061 From REST to MCP | — (preprint) | arXiv 2507.16044 v1–v4 | Version-এর মধ্যে শিরোনাম ও সংখ্যা বদলেছে |
| M053 ToolLLM | ICLR 2024 | arXiv 2307.16789 (v1–v2) | OpenAlex-এ arXiv DOI ভুল শিরোনামে map |

### 4.5 সম্ভাব্য extended version (আলাদা paper হিসেবে গণ্য, merge নয়)
| নির্বাচিত | Extended/সম্পর্কিত | সিদ্ধান্ত |
|---|---|---|
| P008 AGORA (ISSTA 2023) | “Test oracle generation for REST APIs” (TOSEM 2025, 10.1145/3726524; AGORA+) | ভিন্ন DOI ও বিস্তৃত মূল্যায়ন — আলাদা কাজ; PHASE C-তে AGORA+-এর ফল তুলনার জন্য নোট |
| P015 Access policy (ISSRE 2025) | JSS 2026 (10.1016/j.jss.2026.113060; arXiv 2604.00702) | আলাদা কাজ (injection attack যোগ) |
| M067 RESTTESTGEN (ICST 2020) | STVR 2022, ICSME 2022 version | excluded |

### 4.6 Claude-এর screened-out কিন্তু Codex-এর included
- **KAT** (Claude C12 = Codex C009 → M006) ও **Volkswagen industrial** (Claude C17 = Codex C012 → M008): provenance = *Both*; PHASE B-তে নতুন করে score করা হয়েছে (উভয়ই চূড়ান্ত তালিকার বাইরে — `excluded_papers.md`)।

## 5. Provenance সারসংক্ষেপ

| Provenance | Merged pool (104) | চূড়ান্ত নির্বাচিত (38) |
|---|---|---|
| Both | 26 | 15 |
| Claude only | 44 | 19 |
| Codex only | 34 | 4 |

**ব্যাখ্যা:** দুই agent-এর ঐকমত্য (26) discovery-coverage নিয়ে আস্থা বাড়ায়, কিন্তু paper-এর গুণমান প্রমাণ করে না। চূড়ান্ত নির্বাচনে Codex-only অবদান (P001, P013, P019, P037) এমন ফাঁক পূরণ করেছে যা Claude-এর PHASE A-তে ছিল (industrial-scale testing, mobile-client security, PL-ভিত্তিক spec inference, API anomaly dataset)।
