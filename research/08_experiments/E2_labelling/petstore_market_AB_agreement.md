# Petstore ও market baseline (s1): labeller A বনাম B (2026-11-14)

- **A** = Claude: `../E1_pilot/pilot_results/{swagger-petstore,market}_baseline_s1_labels_A_claude.csv`। নিয়ম: `../E1_pilot/label_petstore_baseline.py`, `label_market_baseline.py`।
- **B** = Codex T16 (T15-এর session resume করে চালানো): `*_labels_codex.csv`, `*_root_causes_codex.csv`, `../../09_collab/reports/T16_report.md`।
- **Adjudication sheet:** `swagger-petstore_adjudication.csv`, `market_adjudication.csv`। তৈরি হয়েছে `compare_AB.py` দিয়ে।
- **Protocol:** দুটি LLM labeller + মানব (supervisor) adjudication।

## Agreement
| SUT | n | L1 agreement | κ | L2 (একই L1-এ) | Adjudication দরকার |
|---|---|---|---|---|---|
| swagger-petstore | 43 | 83.7% | 0.748 | 35/36 | 10 |
| market | 13 | 53.8% | 0.426 | 6/7 | 10 |

Market-এর 6টি মতভেদের সবগুলোই **লেখার নিয়মের পার্থক্য**, বিচারের নয়:
- A লিখেছে L1 = BOTH।
- B লিখেছে L1 = IMPL + `both_candidate=true` ("candidate flag আলাদা; চূড়ান্ত BOTH নয়")।
- দুজনেরই মূল কারণ একই: RC-M1, `_links` array।
- B-র নিয়ম মানলে market-এ L1 মিল হয় **13/13**।
- ⚠️ A নিজেও অসংগত ছিল: scout-এ "IMPL + note", market-এ BOTH।

## মতভেদ — সিদ্ধান্তের প্রশ্ন
| # | প্রশ্ন | Item | A | B |
|---|---|---|---|---|
| Q1 | BOTH কি labeller-এর চূড়ান্ত L1, নাকি প্রাথমিক L1 + flag (চূড়ান্ত হবে adjudication-এ)? | M002, M004, M006, M008, M011, M013 | L1 BOTH | IMPL + flag |
| Q2 | একই fingerprint-এর occurrence-এ SPEC আর TEST মিশে থাকলে কী হবে? Codebook §9.1-এ শুধু SPEC + UNDECIDABLE আছে। | P019 (63 SPEC / 3 TEST), P021 (60/2), P043 (34/2) | majority → SPEC | UNDECIDABLE (abstain) |
| Q3 | Encoded backslash (`%5C`) username-এ Tomcat-এর 400 | P037, P039 | UNDECIDABLE (container policy) | TEST (transport-invalid input) |
| — | Item-ভিত্তিক বিচার | P014: documented default বনাম explicit required check — A IMPL, B SPEC। P018: fix-এর জায়গা request enum নাকি response contract — A SPEC, B IMPL। | | |
| — | BOTH flag-এর পার্থক্য | P035, P036, P038 (কেবল A), M003, M005, M007, M012 (406, কেবল A) | | |

⚠️ Q3 নিয়ে A-র মন্তব্য: RFC 3986 অনুযায়ী `%5C` বৈধ percent-encoding। Tomcat নিরাপত্তার কারণে default-এ এটা প্রত্যাখ্যান করে। তাই input-টা "transport-invalid" নয়, এটা container-এর policy। তবে P022 (header-এ control character) সত্যিই অবৈধ HTTP, আর সেখানে দুজনেই TEST দিয়েছে।

## যেখানে দুজন একমত (উল্লেখযোগ্য)
- **Petstore-এর stateful user fault:** `POST /user {}` (#952) থেকে পরের সব `/user*` 500। দুজনেই আলাদাভাবে খুঁজে পেয়েছে।
- **Pet id unboxing crash:** IMPL, BOTH প্রার্থী।
- **Market:** `_links` array (BOTH প্রার্থী), আর 406 ইচ্ছাকৃত (SPEC / S-STATUS)।
- **REQUEST_UNCHECKABLE (16):** দুজনেই TEST + checker coverage দিয়েছে। A-র প্রস্তাবিত code `T-ORACLE-COVERAGE` আর B-র প্রস্তাব একই।
- **নতুন TEST code-এর প্রস্তাব (দুজনেরই):** checker int64/int32 format enforce করে না। A: `T-ORACLE-FORMAT`; B: `T-ORACLE-NUMERIC-FORMAT`।

## Supervisor adjudication (2026-11-14)
- **Q1:** labeller-রা প্রাথমিক L1 + flag দেবে; চূড়ান্ত BOTH কেবল supervisor ঠিক করবেন (codebook §10.1)।
  - এই রীতিতে market-এ L1 মিল 13/13।
  - M002, M004, M006, M008, M011, M013 → প্রাথমিক IMPL; চূড়ান্ত BOTH বাকি।
- **Q2:** SPEC + TEST মিশ্রণ → SPEC_PARTIAL (§10.4)। প্রযোজ্য: P019, P021, P043।
- **Q3:** `%5C` container policy → UNDECIDABLE (§10.3)। প্রযোজ্য: P037, P039।
- **এখনো supervisor-এর CSV-তে বাকি:**
  - P014, P018 (item-ভিত্তিক বিচার)।
  - BOTH-এর চূড়ান্ত সিদ্ধান্ত: market-এর 6টি `_links` item; 406-এর M003, M005, M007, M012; petstore-এর P006, P012, P018, P031, P033, P035, P036, P038, P042।
  - scout-এর 12টি BOTH item (`batch2_adjudication.csv`)।
