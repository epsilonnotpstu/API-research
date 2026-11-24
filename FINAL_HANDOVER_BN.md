# চূড়ান্ত হস্তান্তর: তিনটি paper (R1, R3, R4)

তৈরি করেছে Claude, ২০২৬-১১-২৪-এ। Claude আর Codex-এর access আজ শেষ। এর পরের সব কাজ আপনার, আর এই নথিতেই সব লেখা আছে।

**মূল নীতি:** প্রতিটি paper-এর plan আগে hash দিয়ে freeze করা হয়েছে, coding blind, আর scoring হয়েছে মাত্র একবার। Archive-এর `reproduce` script চালালেই প্রতিটি সংখ্যা হুবহু আবার পাওয়া যায়।

---

## ১. এক নজরে

| Paper | বিষয় | Venue (লক্ষ্য) | Deadline | অবস্থা |
|---|---|---|---|---|
| **R1**: Spec or Bug? | Contract আর implementation অমিল হলে developer কোন দিক ঠিক করে | ISSTA 2027 (ACM acmsmall) | ~৮–১১ জানুয়ারি ২০২৭ ⚠️ যাচাই করুন | v0.4 তৈরি। শুধু আপনার spot-check বাকি (§6-এর একটি TODO)। |
| **R3**: Silent behavioural changes | Contract না বদলে service-এর আচরণ কতটা বদলায় | ICSME 2027 (IEEE) | ~মার্চ ২০২৭ ⚠️ অনুমান | v0.3 তৈরি। Codex যাচাই (T55) সম্পন্ন। |
| **R4**: Access-control vulnerabilities | বাস্তব access-control দুর্বলতা ধরতে black-box tester-এর কী লাগে, contract-এ তার তথ্য থাকে কিনা | ASE 2027 (IEEE) | ~১০ মার্চ ২০২৭ ⚠️ নিশ্চিত নয় | v0.3 তৈরি। Codex যাচাই (T58) সম্পন্ন। Follow-up R4b চলছে (নিচে দেখুন)। |

## ২. আপনার করণীয় (ক্রমানুসারে)

### ক. PDF compile করা (তিনটি paper-ই)
এই machine-এ পূর্ণ LaTeX নেই। Tectonic নামানোর অনুমতিও পাওয়া যায়নি। তাই সবচেয়ে সহজ পথ Overleaf:

1. **R1:** `research/10_paper/latex/main.tex`, `research/10_paper/references.bib` আর `research/10_paper/figures/` upload করুন। Class: acmart, যা Overleaf-এ আগে থেকেই আছে।
2. **R3:** `R3_silent_breaking/paper/latex/` (ভেতরে `IEEEtran.cls` আছে) আর `R3_silent_breaking/paper/figures/` upload করুন।
3. **R4:** `R4_access_control/paper/latex/` আর `R4_access_control/paper/figures/` upload করুন।
4. Compile-এর ক্রম: `pdflatex → bibtex → pdflatex → pdflatex`।
5. পৃষ্ঠার সীমা মিলিয়ে দেখুন:
   - ISSTA (acmsmall): সাধারণত প্রায় ১৮ পৃষ্ঠা;
   - ICSME আর ASE (IEEE): ১০ + ২ পৃষ্ঠা।

বিকল্প হিসেবে নিজের machine-এ ইনস্টল করতে পারেন: `sudo pacman -S texlive-latex texlive-latexrecommended texlive-latexextra texlive-fontsrecommended texlive-publishers`।

### খ. Human spot-check (তিনটি; এটাই paper-এর সবচেয়ে বড় দুর্বলতা দূর করবে)

| Paper | ফাইল | কয়টি item | নির্দেশনা |
|---|---|---|---|
| R1 | `research/09_collab/human_check/kind_spotcheck.csv` | ২০ | আপনি নিজে আবার করছিলেন। আগের প্রথম পূরণ report করা হবে না। |
| R3 | `R3_silent_breaking/human_check/r3_spotcheck.csv` | ২০ | `R3_silent_breaking/human_check/README_BN.md` |
| R4 | `R4_access_control/human_check/r4_spotcheck.csv` | ২০ | `R4_access_control/human_check/README_BN.md` |

**নিয়ম:**
- কোনো LLM দিয়ে পূরণ করবেন না।
- `plan/*_spotcheck_model_codes.csv` ফাইলগুলো খুলবেন না।

**শেষ হলে যা করবেন (Claude ছাড়াই):**
1. দুই কলামের মিলের হার আর Cohen's κ হিসাব করুন: আপনার উত্তর বনাম `*_spotcheck_model_codes.csv`-এর GPT-এর উত্তর।
2. Paper-এর §6 (Threats)-এ এক লাইন যোগ করুন, যেমন: "A human spot-check of 20 items agreed with the GPT final codes in k/20 cases (κ = …)."

### গ. Replication archive upload (anonymous)
সবগুলো Shared Data drive-এ আছে:

| Paper | ফাইল | আকার |
|---|---|---|
| R1 | `R1_replication/R1_anon_23ef64d.tar.gz` | ৫৯ MB (পুরোনো `R1_anon_49f92e2` বাতিল) |
| R3 (R3b-সহ) | `R3_replication/R3_anon_a857c05.tar.gz` | ১১ MB (পুরোনো `R3_anon_acda551` বাতিল) |
| R4 (R4b-সহ) | `R4_replication/R4_anon_525e970.tar.gz` | ৩৮ MB (পুরোনো `R4_anon_93c6a5f` বাতিল) |

**কীভাবে:**
1. Zenodo-তে upload করুন। Review-এর সময় "restricted" রাখুন, অথবা anonymous view link দেওয়া যায় এমন কোথাও রাখুন (যেমন OSF-এর anonymous view-only link)।
2. Link পেলে প্রতিটি paper-এর "Data availability" অংশে `[anonymous link to be added]` জায়গায় বসিয়ে দিন।
3. LaTeX আবার তৈরি করুন: R3/R4-এ `python3 -I -B paper/latex/md2ieee.py`, R1-এ `python3 -I -B research/10_paper/latex/md2acm.py`।

### ঘ. AI-use disclosure
- IEEE (R3, R4) এটা বাধ্যতামূলক করেছে। প্রতিটি paper-এ "Disclosure of AI use" অংশ লেখা আছে, পড়ে নিশ্চিত করুন।
- ISSTA-র (ACM) নীতি দেখে R1-এ একই রকম অংশ যোগ করুন।

### ঙ. Venue-এর তারিখ যাচাই
- ICSME 2027-এর CFP দেখুন: conf.researchr.org/home/icsme-2027।
- ASE 2027-এর CFP দেখুন: conf.researchr.org/home/ase-2027। এখানে template (IEEE বা ACM) কোনটা চায়, সেটাও দেখে নিন।
- ISSTA 2027-এর তারিখ আর page limit মিলিয়ে নিন।

## ৩. গুরুত্বপূর্ণ নীতি ও সতর্কতা
- **Double-anonymous review:**
  - Title বা preprint এখন প্রকাশ্যে দেবেন না।
  - GitHub repo (`API-research`) review চলাকালে private রাখাই নিরাপদ।
- **Commit history:** সব commit থেকে Claude-এর co-author লাইন সরানো হয়েছে, এখন author শুধু আপনি।
  - পুরোনো নথিতে লেখা commit hash মেলাতে চাইলে `COMMIT_HASH_MAP.txt` দেখুন।
  - Rewrite-এর আগের backup আছে Shared Data-তে: `git_backup_before_coauthor_rewrite_20261123.bundle`।
- **খোলা সিদ্ধান্ত:** পুরোনো commit `930ba0a`-তে (নতুন hash `2dffc7f`) একটি পাবলিক demo credential-এর ১৫ অক্ষরের prefix এখনো history-তে আছে। চাইলে আরেকবার history rewrite করে মুছতে পারেন, তবে তাতে force push লাগবে।
- **Licence:** তিনটি repo-র licence বিধিনিষেধমূলক (convoy: proprietary, netmaker: SSPL, evmos: non-commercial)। R4 archive-এ ওদের code রাখা হয়নি, শুধু hash রাখা আছে।

## ৪. প্রতিটি paper-এর মূল ফল (মনে রাখার জন্য)

**R1:**
- Contract আর code অমিল হলে কোন দিক ঠিক হবে, তা ভালোভাবে অনুমান করা যায় divergence-এর ধরন থেকে। DELIBERATE হলে সাধারণত contract (SPEC) ঠিক করা হয়, ACCIDENTAL হলে code।
- এই ফল আলাদা আলাদা নমুনায় (E8b, E10, E12, E13) pre-registered পরীক্ষায় বারবার মিলেছে। বিস্তারিত `research/10_paper/R1_draft.md`-এ।

**R3:**
- Contract-এ হাত না দিয়ে আচরণ বদলায় এমন commit: ৪৪%।
- এর মধ্যে breaking: ৯–২৪%, model-এর উপর নির্ভর করে।
- যে breaking পরিবর্তনগুলো contract-এ ধরা পড়ে না, তার ৯১% কোনো annotation-ও ছোঁয় না।

**R4:**
- ১৩৮টি advisory-র মধ্যে ১০২টি সত্যিকারের access-control দুর্বলতা।
- এর প্রায় অর্ধেক ধরতে ২ জন user লাগে: যে ৮৯টিতে সিদ্ধান্ত হয়েছে, তার মধ্যে ৪৯টি।
- Fix করার সময় contract বদলায় না: ৯১%।
- যে নিয়মটা ভাঙা হয়েছে, তা contract-এ লেখা থাকে না: ৮৭%।
- **R4b (follow-up, pre-registered, সম্পন্ন):** পূর্ণ contract দিয়ে আবার যাচাই করা হয়েছে, আর প্রতিটি উত্তরের সাথে contract-এর লাইন উল্লেখ বাধ্যতামূলক ছিল। এতে মূল দাবি আরও শক্ত হয়েছে:
  - vulnerable operation contract-এ আছে: ৫৬/১০২;
  - ভাঙা নিয়ম contract-এ লেখা নেই: ৮১% (৪৪/৫৪);
  - **নতুন ফল:** ৩৭.৫% documented vulnerable operation-এ কোনো security requirement-ই ঘোষিত নেই;
  - দুই model family-র মিল: κ = 1.00।
  - Paper v0.4-এর §4.7-এ যোগ করা হয়েছে।

**R3b (follow-up, pre-registered, সম্পন্ন):**
- পূর্ণ contract দিয়ে আবার যাচাই করা হয়েছে, প্রতিটি "লেখা আছে" উত্তরের সাথে contract থেকে হুবহু উদ্ধৃতি বাধ্যতামূলক ছিল।
- পরিবর্তিত আচরণ contract-এ লেখা ছিল: মাত্র **২/৬০**।
- **H-R3-4 PASS:** ৯৭% পরিবর্তন contract-এ লেখা নেই।
- সব উদ্ধৃতি contract-এ হুবহু আছে।
- **সতর্কতা:** Codex-এর limit থাকায় GPT coder-এর জায়গায় Claude Opus ব্যবহার করা হয়েছে, তাই দুই coder pair-ই Claude family-র। এটা paper-এ লেখা আছে।
- R3 paper v0.4-এর §4.7-এ যোগ করা হয়েছে। রাতে কোনো command চালানোর দরকার নেই।

## ৫. কোথায় কী
- Resume-এর বিস্তারিত তথ্য: `RESUME_HERE.md`।
- প্রতিটি study-র নথি:
  - `plan/*_PLAN.md`: plan;
  - `*_DEVIATIONS.md`: plan থেকে বিচ্যুতি;
  - `*_AUDIT.md`: coder-দের audit;
  - `*_RESULTS.md`: ফল।
- Codex-এর review report: `collab/reports/`, আর R1-এর জন্য `research/09_collab/reports/`।
