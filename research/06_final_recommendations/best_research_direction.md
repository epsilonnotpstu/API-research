# Best Research Direction — PHASE E3

**তারিখ:** 2026-10-19 · **ভিত্তি:** `ranked_research_topics.md` (R1–R7), `05_research_clusters/gap_validation.md`
**ভূমিকা:** Research Supervisor হিসেবে নতুন গবেষকের জন্য পরামর্শ। ⚠️ = অনুমান।
- কোনো সুপারিশ publication-এর নিশ্চয়তা দেয় না।
- Global novelty দাবি করা হচ্ছে না: search ছিল snippet-স্তরের এবং corpus ৩৮টি paper।

---

## Option A — Feasible ও কম ঝুঁকি: **R2 — Inferred spec-এর downstream মূল্য**

- **কেন:**
  - Feasibility সর্বোচ্চ (৫)।
  - সব artifact প্রকাশিত: P018 Respector ও ১৫টি API, P019 RestPi, EvoMaster, Schemathesis।
  - GPU লাগে না।
  - মূল্যায়ন প্রতিষ্ঠিত: coverage ও A12 (P003, P004-এর ধারা)।
- **প্রশ্ন:**
  - Code-inferred বা merged spec কি developer spec-এর চেয়ে fuzzer-এর coverage ও fault বাড়ায়?
  - কোন element (constraint, non-200 response) সবচেয়ে কার্যকর?
- **সীমা:**
  - Novelty মাঝারি (৩); ফল “প্রত্যাশিত” মনে হতে পারে।
  - Significance সীমিত।
- **উপযুক্ত:** সীমিত infrastructure ও সময়ে (প্রায় ৩–৪ মাস ⚠️) প্রথম গবেষণা-অভিজ্ঞতা।

## Option B — Balanced: **R1 — Spec or Bug? Runtime triage ও evidence-driven OpenAPI repair** ⭐ (সর্বোচ্চ সুপারিশ)

- **কেন:**
  - Base weighting-এ ১ম (৪.০০)।
  - পাঁচটির মধ্যে চারটি weighting-এ শীর্ষে বা যুগ্ম-শীর্ষে; কোনোটিতে ৩য়-এর নিচে নয়।
- **সমস্যাটি corpus-এর সবচেয়ে বহুল-প্রমাণিত পর্যবেক্ষণের উপর দাঁড়িয়ে:**
  - P001: ৬৩% failure spec disconformity।
  - P004: প্রায় ৯৯% spec-এ mismatch।
  - P018: developer-confirmed inconsistency।
  - P015: schema-fault severity প্রশ্নসাপেক্ষ।
  - P032: spec defect → tool failure।
- **আগের কাজ আংশিক:**
  - P001-এর triage manual।
  - P032 SpecFix static-only, এবং লেখকরা নিজেরাই runtime defect বাদ দিয়েছেন।
- **তিনটি cluster-এর সংযোগস্থলে (T1 × T4 × T6):**
  - ফল testing (false failure হ্রাস), spec quality ও agent (T8)-এর জন্য প্রাসঙ্গিক।
  - এতে significance বাড়ে, অথচ T8-এর দ্রুত-পরিবর্তনশীল প্রতিযোগিতায় সরাসরি নামতে হয় না।
- **Option A-র সমন্বয়:** R1-এর RQ3 (repaired spec → downstream fuzzing) মূলত R2-এর নকশা। তাই R2 R1-এর প্রথম experiment হিসেবে অন্তর্ভুক্ত করা যায়।
  - এতে ঝুঁকি কমে: R1-এর novelty দুর্বল হলেও R2-ধাঁচের অবদান থেকে যায়।
- **প্রধান ঝুঁকি:**
  - Novelty-অনুমান সংবেদনশীল। Novelty ৩ হলে R1 পাঁচ নম্বরে নামে।
  - তাই **প্রথম কাজ: 2607.12101 (spec fault injection) ও P032-এর সর্বশেষ version-এর পূর্ণ পাঠ।**

## Option C — Ambitious / উচ্চ ঝুঁকি: **R3 — REST API-র behavioural breaking change: benchmark + detector**

- **কেন:**
  - Significance সর্বোচ্চ (৫); importance-heavy weighting-এ ১ম।
  - Gap-টি **তিনটি ভিন্ন লেখক-গোষ্ঠী স্পষ্টভাবে উল্লেখ করেছে** (P021, P023, P025)।
  - P020-এর practitioner প্রমাণ এটিকে সমর্থন করে।
  - Search-এ behavioural label-সহ REST benchmark পাওয়া যায়নি।
- **ঝুঁকি:**
  - পুরোনো version build।
  - Behavioural label-এর subjectivity।
  - পর্যাপ্ত breaking change না পাওয়া।
  - Labelling-এর বড় খরচ।
- **বিকল্প C′:** R5 (spec-quality × LLM agents)।
  - প্রাসঙ্গিকতা উচ্চ, কিন্তু novelty-ঝুঁকিও উচ্চ (SilentProbe 2609.00035, 2605.14312)।
  - Novelty ৪ হলে base weighting-এ ১ম হয় — sensitivity-র কারণে নজরে রাখার মতো।

---

## চূড়ান্ত সুপারিশ

**R1 (Option B)** — সঙ্গে R2-কে প্রথম experiment হিসেবে অন্তর্ভুক্ত করা।

**যুক্তি:**
1. **প্রমাণ:** সমস্যাটি ৯টি corpus paper-এ প্রত্যক্ষ বা পরোক্ষভাবে প্রমাণিত।
2. **Gap যাচাই:** GV16-এ runtime triage বা repair পাওয়া যায়নি। বিরোধী প্রমাণও নেই।
3. **Feasibility:** open data (P001 Zenodo 10.5281/zenodo.6941292 — বিষয়বস্তু যাচাই বাকি), open SUT ও tool আছে, GPU লাগে না।
4. **মূল্যায়নযোগ্যতা:** triage F1, patch correctness এবং downstream coverage বা false-failure — তিনটিই পরিমাপযোগ্য, baseline সহ।
5. **ঝুঁকি-ব্যবস্থাপনা:** R2-এর অন্তর্ভুক্তি একটি নিশ্চিত empirical অবদান দেয়।

**যে শর্তে সুপারিশ বদলাবে:**
- পূর্ণ পাঠে runtime spec repair বা triage-এর পূর্ববর্তী কাজ পাওয়া গেলে → **R2 (Option A)** বা **R3 (Option C)**।
- Supervisor-এর লক্ষ্য দীর্ঘমেয়াদি ও উচ্চ-প্রভাব হলে → **R3**।
- Supervisor LLM agent-কেন্দ্রিক দিক চাইলে → **R5**, তবে সতর্কতাসহ।
