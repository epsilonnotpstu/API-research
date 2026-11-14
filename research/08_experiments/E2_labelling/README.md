# E2 — Pilot labelling: P001-এর ৭৩টি F_OAS fault

**তারিখ:** 2026-11-13 · **Sheet:** `p001_foas_labelling_sheet.csv` (৭৩ সারি) · **Script:** `build_labelling_sheet.py` · **নিয়ম:** `../R1_triage_codebook.md` v0.2

## Sheet-এ কী আছে
- প্রতিটি fault-এর operation, status, request অবৈধ ছিল কিনা, violation-এর ধরন ও message, `strict_only` চিহ্ন, developer-এর প্রতিক্রিয়া।
- `suggested_*` কলাম: codebook-এর নিয়ম থেকে **স্বয়ংক্রিয় rule-based প্রস্তাব**। এটি ground truth নয় — R1-এর rule-based baseline।
- ফাঁকা কলাম: `label_A_*`, `label_B_*`, `evidence_*`, `final_L1`।

## Labelling-এর নিয়ম
1. দুইজন labeller আলাদাভাবে label দেবেন। **Label দেওয়ার সময় `suggested_*` কলাম লুকিয়ে রাখতে হবে** (anchoring এড়াতে)।
2. প্রতিটি label-এর সাথে প্রমাণ-কোড লিখতে হবে (E-DEV, E-DOC, E-CONSIST, E-AUX, E-CONV)। API-গুলো closed-source, তাই E-CODE-INTENT নেই; মূল উৎস হবে API-র public documentation।
3. শেষে Cohen's κ হিসাব; মতভেদ আলোচনা করে `final_L1`।
4. Response body দেখতে হলে: `../_external/p001/faultClustersConfirmedBugs_<api>.csv`-এ `testCaseId` দিয়ে খুঁজতে হবে।

## Rule-based baseline-এর ফল (প্রাথমিক)

| প্রস্তাবিত label | Fault | আস্থা ৩ / ২ / ১ |
|---|---|---|
| SPEC | ৩৭ | ৫ / ২০ / ১২ |
| UNDECIDABLE | ৩৬ | — |
| IMPL | ০ | — |

- **নিয়ম একা অর্ধেকের বেশি সিদ্ধান্ত দিতে পারে না:** ৭৩টির ৩৬টি (৪৯%) UNDECIDABLE। মূলত FORMAT, COMPOSITION, ENUM, এবং বৈধ input-এ undocumented 400/404/409 (Marvel-এ ১০টি)। ⇒ R1-এর multi-evidence/LLM triage-এর প্রয়োজনের প্রাথমিক সংখ্যা।
- **উচ্চ আস্থার SPEC মাত্র ৫টি** — সবই Amadeus-এর double-escaped pattern।
- Developer-confirmed ১০টি F_OAS fault-এর সবগুলোই rule-এ SPEC পেয়েছে। ⚠️ “confirmed” মানে developer সমস্যা মেনেছেন; ভুলটা spec-এ না code-এ, তা বলে না — তাই এটি baseline-এর নির্ভুলতার প্রমাণ নয়।
- কোনো fault IMPL পায়নি, কারণ F_OAS-এ 5xx নেই এবং code দেখা যায় না। ⚠️ এটি নিয়মের সীমা, বাস্তবে IMPL নেই তার প্রমাণ নয়।

## তিন label-সেটের তুলনা (2026-11-13)
- `codex_labels.csv` — Codex T3: blind LLM labeller, codebook v0.2। মানব labeller নয়; R1-এর LLM baseline।
- `triage_output.csv` — Codex T2: rule + evidence triage।
- `comparison_rule_triage_codex.csv` — তিনটির পাশাপাশি তুলনা।

| | Rule baseline | T2 triage | T3 LLM |
|---|---|---|---|
| SPEC | ৩৭ | ৩৪ | ৪৭ |
| UNDECIDABLE | ৩৬ | ৩১ | ১৬ |
| ENV | ০ | ৮ | ৯ |
| IMPL | ০ | ০ | ১ |

- **Agreement:**
  - LLM বনাম triage: ৬১.৬% (κ ০.৩৫)।
  - LLM বনাম rule: ৪৯.৩% (κ ০.১০)।
- **মতভেদের কারণ ও সমাধান:** codebook v0.3 (`../R1_triage_codebook.md` §9)।
- ⚠️ কোনো সেটই ground truth নয়। দুইজন মানব labeller-এর label এখনো বাকি।

## v0.3 agreement: rule triage (T11) বনাম Codex blind labels (T13) — 2026-11-14, Claude
ফাইল: `comparison_triage_codex_v03.csv` (73 faults)।

| মাপ | মান |
|---|---|
| L1 strict agreement | 80.8% (κ 0.748) |
| L1 coarse (SPEC_PARTIAL→SPEC) | 86.3% (κ 0.803) |
| দুজনেই decide করেছে (n=43) | 97.7% (κ 0.961) |
| L2, একই L1-এ | 41/42 |

- মূল মতভেদ: triage UNDECIDABLE কিন্তু Codex SPEC — 8টি; বাকি 2টি।
- v0.2-ভিত্তিক T3 labels-এর সাথে আগের κ 0.28 মূলত codebook-এর version অমিল ছিল, এটা নিশ্চিত হলো।
- ⚠️ **স্বাধীনতার সীমা:** triage.py-র নিয়ম ও T13 labels দুটোই Codex (একই model family) থেকে, একই codebook v0.3 পড়ে। উচ্চ κ তাই আংশিকভাবে shared bias; এটা inter-rater reliability নয়। মানব labeller (দুজন) এখনো অপরিহার্য।
