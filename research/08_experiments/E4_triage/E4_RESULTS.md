# E4 ফল — SPEC-দিকের held-out blind set আর triage পদ্ধতির তুলনা (2026-11-15, Claude)

**Pre-registration:** `E4_PLAN.md`, FROZEN আর labelling-এর আগে লেখা।
- Scorer: `score_e4.py`, labelling-এর আগে লেখা আর self-test করা। Output `e4_scores.csv`।
- Freeze hash scoring-এর সময় যাচাই করা হয়েছে: package, task, scorer আর key সব OK।

## Labeller
| ID | পদ্ধতি | Package |
|---|---|---|
| F1, F2 | M2: codebook v0.6 + intent tool, xhigh | E4 |
| Z1 | M1: zero-shot, codebook বা tool ছাড়া, high | E4 |
| Z2 | M1: zero-shot, high | E5 v3 |
| D1, D2 | M2 (IMPL দিক) | E5 v3, আগে করা |

সবাই নতুন Codex session।

## Pre-registered ফল
**Primary (E4 injected, n=28, truth SPEC):**

| | SPEC recall | ভুল দিক (IMPL) | Abstain | Other |
|---|---|---|---|---|
| M2 F1 | 11 (39%) | 2 (7%) | 15 | 0 |
| M2 F2 | 13 (46%) | 2 (7%) | 13 | 0 |
| M1 Z1 | **27 (96%)** | 1 (4%) | 0 | 0 |

**দুই দিক একসঙ্গে** (E4 SPEC 28 + E5 v3 primary IMPL 11):

| পদ্ধতি | macro-F1 | SPEC P/R | IMPL P/R | Decided-accuracy | Coverage |
|---|---|---|---|---|---|
| M0 সব IMPL | 0.22 | 0/0 | 0.28/1.00 | 0.28 | 1.00 |
| **M1 Z1+Z2** | **0.94** | 0.96/0.96 | 0.91/0.91 | 0.95 | 1.00 |
| M2 F1+D1 | 0.66 | 1.00/0.39 | 0.80/0.73 | 0.90 | 0.54 |
| M2 F2+D2 | 0.70 | 1.00/0.46 | 0.80/0.73 | 0.91 | 0.59 |

Swapped pairing-এও (F1+D2, F2+D1) একই।

**মানদণ্ড:**
- **P1 পূরণ:** M2-এর ভুল দিক 7% ≤ 10%, দুজনেরই।
- **P2 ব্যর্থ:** M2-এর macro-F1 M0-এর চেয়ে বেশি, কিন্তু **M1-এর চেয়ে অনেক কম** (0.66–0.70 বনাম 0.94)।
- **P3:** M2-এর SPEC recall 39–46%। Plan-এ প্রত্যাশা ছিল কম হবে, আর সেটাই হয়েছে।

**Secondary (decoy, n=22; truth = adjudicated final label):**
- Partial label মিলিয়ে ধরলে মিল: Z1 **15/22**, F1/F2 12/22।
- Final SPEC (n=5): Z1 4, F1/F2 2। Final IMPL (n=5): Z1 5, F1/F2 4।
- Final BOTH (n=6): সবাই 0। কেউ BOTH লেখে না, আর Z1-এর flag নেই।
- ⚠️ Decoy-র final label একই LLM-codebook pipeline আর supervisor adjudication থেকে এসেছে। ফলে তুলনাটা M2-এর পক্ষে ঝুঁকে থাকার কথা, তবু Z1 এগিয়ে।

## ব্যাখ্যা (post-hoc; ⚠️ চিহ্নিত অংশ inference)
1. **Evidence-conservative procedure (M2) নির্ভুল, কিন্তু কম কাজের।**
   - SPEC precision 1.00, decided-accuracy 0.90–0.91।
   - তবে SPEC item-এর অর্ধেকের বেশিতে বিরত থাকে। কারণ v0.6 স্বাধীন intent-প্রমাণ চায় (test/doc), যা এই source-গুলোতে প্রায়ই নেই।
   - F1/F2-এর বিরতির উদাহরণ: "handler Principal থেকে customer নেয়… retrieved test web module-এর" → none_found → UNDECIDABLE।
2. **Zero-shot (M1) "কোন দিকটা অস্বাভাবিক বা স্পষ্টভাবে ভুল দেখায়" দিয়ে বিচার করে।**
   - E4-এ code-এর স্পষ্ট নকশাকে (explicit GET route, nullable field) intent ধরে spec-কে ভুল বলেছে।
   - E5-এ explicit 418 বা WRITE_ONLY-কে ত্রুটি বলেছে।
   - ⚠️ কৃত্রিম fault দুই দিকেই "অস্বাভাবিক" দেখায়: `maxLength:1`, `maximum:0`, method swap, 418। তাই এই heuristic এখানে প্রায় নিখুঁত।
   - Z1-এর 28টি rationale-এর মধ্যে 7টি সরাসরি অস্বাভাবিক constraint-এর কথা বলে, যেমন "one-character ceiling"।
3. **M2 যেখানে সত্যিকারের ভুল আটকেছে:**
   - E016 (guard-only REJECT_VALID): Z2 বলেছে SPEC, যা ভুল। D1/D2 বিরত ছিল।
   - E4-এ Z1-এর একমাত্র ভুল-দিক I042 (STRICT)। F1/F2 সেখানে IMPL দেয়নি।
   - কিন্তু M2 নিজেও 2টি METHOD_SEM item-এ (I011, I016) IMPL দিয়েছে। সেখানে একই exchange-এ আলাদা একটা 500 ছিল, আর labeller সেটাকেই primary ধরেছে।
4. **R1-এর জন্য তাৎপর্য:**
   - Roadmap-এর H2 ("multi-evidence triage single-signal-এর চেয়ে ভালো") **এই benchmark-এ সমর্থিত নয়।**
   - তবে benchmark-এর কৃত্রিমতা zero-shot-এর পক্ষে কাজ করে। আসল defect-এ (decoy) zero-shot-ও এগিয়ে, কিন্তু n=22 আর truth-এর উৎস দুর্বল।
   - সৎ অবস্থান: **শক্তিশালী LLM-কে source-access দিলে zero-shot-ই শক্ত baseline।** Codebook-এর মূল্য এখন যা দেখা যাচ্ছে:
     - (a) ভুল দিক কমানো, যা সামান্য;
     - (b) প্রতিটি সিদ্ধান্তের audit trail;
     - (c) অনিশ্চয়তায় বিরত থাকা।
   - Accuracy-তে এর লাভ নেই।
   - পরের মূল্যায়ন হতে হবে **আসল, developer-confirmed defect-এ।** কৃত্রিম injection-এ নয়।

## সীমা
- কৃত্রিম spec edit চোখে পড়ার মতো। এটা external validity-র threat, আর M1-এর পক্ষে bias।
- LOOSE item 0; cwa থেকে মাত্র 1টি injected item।
- সব labeller একই model family, একটি session করে। Zero-shot labeller মাত্র একজন করে (Z1, Z2)।
- n ছোট: 28 + 11 + 22। কোনো statistical test নেই।
- Boundary incident হয়েছে চারজনেরই:
  - শুরুতে explicit path ছাড়া `rg --files` চালানো হয়েছিল। শুধু filename discovery, current directory-র মধ্যে।
  - Protocol খুঁজতে কয়েকটা অননুমোদিত path-এর অস্তিত্ব পরীক্ষা হয়েছিল, content পড়া হয়নি।
  - F2 আর Z1-এর transcript-এ market-এর upstream demo credential দেখা গেছে। তাই সেই log commit হয়নি, gitignore করা।
  - কেউ নিষিদ্ধ file-এর content পড়েছে বলে জানায়নি।

## সংযোজন: future-version oracle (T41; আসল developer-এর fix-এর দিক)
**পদ্ধতি:** EMB snapshot-কে upstream commit-এর সঙ্গে মেলানো হয়েছে (anchor, blob-hash দিয়ে):
- petstore 24/27;
- cwa 67/71;
- market 135/139।

তারপর anchor-এর পরের history-তে খোঁজা হয়েছে, mismatch-টা spec বদলে মিটেছে নাকি code বদলে। Scout-এর upstream পাওয়া যায়নি, তাই বাদ। Item 62টি।
- **ফলন খুব কম:** 3/62-এ fix-এর দিক পাওয়া গেছে, তিনটিই spec_changed_to_match_code।
  - বাকি 31টি HEAD পর্যন্ত অপরিবর্তিত, 27টি অস্পষ্ট, 1টি অসম্পর্কিত পরিবর্তন।
  - Code_changed বা both কোনোটাই পাওয়া যায়নি।
  - অর্থাৎ বেশিরভাগ spec–code অমিল developer কখনো সারায়নি। ⚠️ Survivorship আর right censoring-এর কারণে "অপরিবর্তিত" থেকে কোনো label অনুমান করা যায় না।
- **Final label-এর সঙ্গে মিল 2/3:** P015 SPEC আর C002 SPEC_PARTIAL মিলেছে। C002-এ evidence partial, regenerated spec।
  - **অমিল: P014।** Final IMPL, কিন্তু developer commit `9fb97b1` (2025-08-04, "Change status/tag to required param for findbystatus/findbytag endpoints") spec-এ `required:false→true` করেছে। Handler-এর guard অপরিবর্তিত। Confidence 3।
- **Guard-only প্যাটার্নের তাৎপর্য:**
  - P014/P015-এর guard (optional parameter অনুপস্থিত হলে 400) developer-এর কাছে **ইচ্ছাকৃত** ছিল, তাই তারা spec সারিয়েছে।
  - E5-এর injected guard (reject-valid) ছিল **bug**।
  - সুতরাং guard একা ambiguous, এক প্রেক্ষাপটে intended, অন্য প্রেক্ষাপটে bug। এতে codebook v0.6-এর "guard-only → UNDECIDABLE" নিয়ম সমর্থিত হয়।
  - কিন্তু developer-এর পরের commit একটা শক্তিশালী স্বাধীন প্রমাণ (E-HISTORY/E-DEV), যা blind package-এ ছিল না।
  - P019/P021/P043 (একই প্যাটার্ন) upstream-এ অপরিবর্তিত, তাই UNDECIDABLE বহাল।
- **E6-এর জন্য:** এই oracle একা মূল্যায়নের ভিত্তি হতে পারবে না, কারণ ফলন কম আর শুধু একটা দিকই এসেছে। তবে আসল intent-প্রমাণ হিসেবে পরিপূরক কাজে লাগে।
- উৎস: `future_oracle/future_oracle.csv`, `anchors.json`, `agreement.csv`; `09_collab/reports/T41_report.md`।
