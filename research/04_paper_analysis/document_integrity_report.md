# Document Integrity Report — PHASE C

> **হালনাগাদ 2026-11-13 — P038 সমস্যার সমাধান:** সঠিক paper (Ponce et al. 2025, IST 188:107870, author-hosted copy) এখন `paper/P038.pdf`-এ আছে। এর বিশ্লেষণ `04_paper_analysis/P038_analysis.md`-এ (৭৪টি study, confidence High)। এই নথিতে যেখানে P038-কে “substitute”, “P038*” বা “Ghani 2019” বলা হয়েছে, তা ঐতিহাসিক — সেগুলো এখন আর প্রযোজ্য নয়। T9-এর evidence strength এখন **মাঝারি** (`05_research_clusters/cluster_T9_microservices.md`)।


**তারিখ:** 2026-10-19 · **পরিধি:** `03_papers_markdown/P001–P038.md` (pdftotext, `<!-- page N -->` marker) · **উৎস:** `integrity_scan.csv` (স্বয়ংক্রিয় section/caption scan), প্রতিটি `Pxxx_analysis.md`-এর “Document integrity” নোট, `markdown_fixes_log.csv`, first-author identity check।

## 1. সারসংক্ষেপ

| মাত্রা | সংখ্যা | Paper |
|---|---|---|
| **Critical — identity mismatch** (ফাইলটি নির্বাচিত paper নয়) | ১ | **P038** |
| **Major — reading order মারাত্মকভাবে এলোমেলো বা কিছু সংখ্যাগত তথ্য অপুনরুদ্ধারযোগ্য** | ৯ | P010, P013, P020, P022, P027, P033, P037 (+ P016, P035 heading/abstract আংশিক ক্ষতি) |
| **Minor — table column-split, figure অনুপস্থিত, formula আংশিক** | সব ৩৮ | — |
| Byte-level সংশোধন | ১ | P032 (৮৩২টি NUL/control byte অপসারণ) |

**মূল সিদ্ধান্ত:** body text সব ৩৮টি ফাইলে পাঠযোগ্য। Figure-নির্ভর সংখ্যা ও column-split table-এর ক্ষেত্রে বিশ্লেষণে text/summary box-এর সংখ্যা ব্যবহৃত হয়েছে, এবং অনিশ্চিত পুনর্গঠন analysis ফাইলে চিহ্নিত।

## 2. Critical: P038 identity mismatch

- **নির্বাচিত:** Ponce, Verdecchia, Miranda, Soldani — *Microservices testing: A systematic literature review*, IST 2025, DOI 10.1016/j.infsof.2025.107870।
- **প্রদত্ত PDF (`paper/P038.pdf`, sha256 9a04aa1e…6184):** Ghani, Wan-Kadir, Mustafa, Imran … — *Microservice Testing Approaches: A Systematic Literature Review*, IJIE 11(8) 2019, DOI 10.30880/ijie.2019.11.08.008।
- **শনাক্তকরণ:** title-শব্দ মিলের পরীক্ষা ব্যর্থ হয়েছিল (দুটি শিরোনামের শব্দ প্রায় এক)। তাই first-author surname check চালানো হয় — কেবল P038 ব্যর্থ, বাকি ৩৭টি মিলেছে।
- **ব্যবস্থা:**
  - Markdown অপরিবর্তিত।
  - প্রদত্ত document “SUBSTITUTE” লেবেলসহ বিশ্লেষিত (confidence Low)।
  - Ponce 2025-এর কোনো দাবি ব্যবহার করা হয়নি।
  - Synthesis ও cluster report-এ P038-কে কম ওজন দেওয়া হবে।
- **প্রয়োজন:** সঠিক PDF (publisher বা repository: hdl.handle.net/2158/1438341, hdl.handle.net/11568/1331513 — access যাচাই হয়নি)।

## 3. Version (কোন সংস্করণ পড়া হয়েছে)

| Version | সংখ্যা | Paper |
|---|---|---|
| arXiv preprint | ২৪ | P002–P005, P007, P010–P012, P016, P017, P020, P023, P024, P026–P032, P034–P037 |
| Supervisor-provided copy | ৯ | P001, P006, P008, P009, P013, P014, P015, P018, P038 |
| Author/institution-hosted | ৩ | P019, P021, P025 |
| Published proceedings (ICLR) | ২ | P022, P033 |

পরিচিত version পার্থক্য:
- **P003:** arXiv v2-এ ১৯টি API, TOSEM version-এ ২০টি।
- **P001:** idUS “submitted version”।
- **P021:** preprint-এ DOI placeholder।
- **P032:** arXiv v1–v4-এর মধ্যে পরিবর্তন আছে। এছাড়া paper-এর ভেতরেই সংখ্যার অসঙ্গতি আছে (৮০ বনাম ৭৭ API)।

Preprint-এর সংখ্যা version of record-এর সাথে মিলিয়ে দেখা হয়নি। এটি একটি সীমাবদ্ধতা।

## 4. Major সমস্যা (প্রতি paper)

| Paper | সমস্যা | বিশ্লেষণে প্রভাব |
|---|---|---|
| P010 | Formula আংশিক garbled; Table 2-এর column PDF ছাড়া অপুনরুদ্ধারযোগ্য | Table 2-ভিত্তিক তুলনা ব্যবহার করা হয়নি |
| P013 | Two-column order ব্যাপকভাবে এলোমেলো; Table I–III ও Algorithm 1 আংশিক হারিয়েছে | Confidence Medium |
| P016 | অনেক heading শনাক্ত হয়নি; conclusion references-এর পরে | পাঠ হাতে পুনর্বিন্যাস করা হয়েছে |
| P020 | Section order ব্যাপকভাবে এলোমেলো | Section হাতে মিলিয়ে দেখা হয়েছে |
| P022 | Result table column-split — ToolEVO average পুরো পুনরুদ্ধারযোগ্য নয় | কেবল text-এ উল্লিখিত সংখ্যা ব্যবহৃত |
| P027 | Reading order এলোমেলো; figure থেকে ভুয়া heading | প্রতি rule-এর সংখ্যা text থেকে নেওয়া |
| P033 | Table 2–5 column-split; Table 4-এর average অস্থায়ী পুনর্গঠন | PDF-এ যাচাই প্রয়োজন হিসেবে চিহ্নিত |
| P035 | Column interleaving-এ abstract ও heading-এর কিছু অংশ হারিয়েছে | Body থেকে পূরণ করা হয়েছে |
| P037 | Table 4-এর ৫৩×৭ matrix অপুনরুদ্ধারযোগ্য | কেবল text-এর সারাংশ ব্যবহৃত |

## 5. Minor সমস্যা (সাধারণ)

- **Table column-split:** pdftotext-এর ডিফল্ট reading order-এ cell-গুলো আলাদা line-এ ভেঙে যায়। বেশিরভাগ ক্ষেত্রে Sum/Total সারি বা text-এর সংখ্যা দিয়ে মিলিয়ে দেখা হয়েছে (যেমন P008, P015, P018)।
- **Figure অনুপস্থিত:** কেবল caption আছে। Plot-নির্ভর মান (coverage curve, box plot, trend chart) ব্যবহার করা হয়নি।
- **Formula বা symbol garbled:** P007, P012, P014, P018, P019, P025, P026, P032, P036।
- **Appendix পড়া হয়নি:** P026, P035, P036।

## 6. সংশোধন লগ (`markdown_fixes_log.csv`)

| Paper | ধরন | বিবরণ |
|---|---|---|
| P032 | control_char_cleanup | Figure-glyph থেকে আসা NUL ও control byte অপসারণ (`[\x00-\x08\x0b\x0c\x0e-\x1f]`)। এই byte-এর কারণে `grep` binary হিসেবে ব্যর্থ হচ্ছিল। Body text অপরিবর্তিত। |
| P038 | identity_mismatch_flag | উপরের §2 দেখুন। ফাইল অপরিবর্তিত। |

অন্য কোনো ফাইলে NUL byte পাওয়া যায়নি।

## 7. সুপারিশ

1. **P038:** সঠিক PDF সংগ্রহ করে পুনর্বিশ্লেষণ (অগ্রাধিকার: উচ্চ)।
2. **PDF-এ যাচাই করা দরকার এমন সংখ্যা:** P033 Table 4, P022 ToolEVO, P010 Table 2, P037 Table 4। এগুলো চূড়ান্ত প্রতিবেদনে সরাসরি উদ্ধৃত হলে আগে যাচাই করতে হবে।
3. **Preprint বনাম version of record:** P003-এর মতো যেসব paper-এর সংখ্যা প্রধান সুপারিশে ব্যবহৃত হবে, সেগুলোর published version মিলিয়ে দেখা।
4. **Table-heavy পুনঃপাঠের জন্য:** `pdftotext -layout` বিকল্প হিসেবে বিবেচ্য। এটি supervisor-এর সিদ্ধান্ত। Default converter অপরিবর্তিত রাখা হয়েছে।
