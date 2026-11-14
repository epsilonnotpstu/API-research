# E5 blind labelling — attribution কি code fault-কে IMPL বলে? (2026-11-14, Claude)

## নকশা
- **Package:** `../E2_labelling/e5_blind/` (`build_e5_blind.py`)।
  - 29টি item: 14টি target (mutated op-এ NEW বা INCREASED), 15টি decoy (অন্য op-এ NEW)।
  - 9টি নিরপেক্ষ package K01–K09। প্রতিটিতে শুধু deploy করা build-এর source, spec, exchange আর log; control-এর source নেই।
- **Labeller:** দুটি নতুন Codex session (B1, B2), আগের কোনো context ছাড়া, high effort।
  - Board, E5, `_external`, run-এর ফোল্ডার আর একে অপরের label পড়া নিষিদ্ধ।
- **Audit:**
  - B2-এর কোনো নিষিদ্ধ অ্যাক্সেস নেই।
  - B1 একবার `09_collab`-এ ফাইলের নামের তালিকা দেখেছে (filter: `*B1*`/PROTOCOL/AGENTS; ভেতরের লেখা খোলেনি)। নিজে report-এ স্বীকার করেছে।
- **চাবি:** `blind_key.csv`। মূল্যায়ন: `evaluate_e5_blind.py` → `e5_blind_scores.csv`।

## ফল
| মাপ | B1 | B2 |
|---|---|---|
| সব target → IMPL* | 9/14 | 7/14 |
| প্রত্যাশিত kind-এর target (n=10) → IMPL* | **7/10** | **5/10** |
| Decoy-এর বণ্টন | IMPL 9, SPEC 4, TEST 2 | IMPL 11, SPEC 2, TEST 2 |
| B1–B2 L1 agreement | 23/29 (target-এ 12/14) | |

### Operator অনুযায়ী (প্রত্যাশিত-kind target)
| Operator | Item | B1 | B2 |
|---|---|---|---|
| DROP_NULL_CHECK (scout, market, cwa) | E012, E016, E018 | IMPL ×3 | IMPL ×3 |
| DROP_VALIDATION (cwa) | E019 | IMPL (BOTH-প্রার্থী) | IMPL |
| REJECT_VALID (scout) | E015 | IMPL | IMPL |
| REJECT_VALID (petstore) | E005 | TEST | TEST |
| RESP_FIELD (petstore, `@JsonProperty(WRITE_ONLY)`) | E011, E027 | IMPL ×2 | **SPEC ×2** |
| WRONG_STATUS (scout, market; 418) | E014, E021 | **SPEC ×2** | **SPEC ×2** |

## ব্যাখ্যা
1. **"ভুল-দেখতে" code fault ঠিকঠাক IMPL হয়।** Crash, guard, validation সরানো: 5/5, দুই labeller-ই।
2. **"ইচ্ছাকৃত-দেখতে" code fault SPEC-এ চলে যায়।**
   - দুই labeller-ই WRONG_STATUS-এ codebook **§10.7** উল্লেখ করেছে: code স্পষ্টভাবে একটা status দেয় যা spec-এ নেই, তাই SPEC।
   - B2 RESP_FIELD-এর explicit annotation-কেও একই যুক্তিতে SPEC বলেছে।
   - ⚠️ এটা labeller-এর ভুল নয়; নিয়ম মেনেই হয়েছে। §10.7 এসেছিল market-এর ইচ্ছাকৃত 406 থেকে।
   - **[H8] শুধু code দেখে intent ধরার পদ্ধতি (E-CODE-INTENT) ইচ্ছাকৃত নকশা আর ইচ্ছাকৃত-দেখতে ভুলকে আলাদা করতে পারে না।** এর জন্য code-এর বাইরের intent-প্রমাণ লাগবে: test assertion, documentation, commit history বা spec-এর ইতিহাস।
   - এটা R1-এর attribution-পদ্ধতির একটা মৌলিক সীমা, আর একই সাথে codebook সংশোধনের প্রস্তাব (নিচে)।
3. **E005 আমার package-এর ত্রুটি।**
   - INCREASED item-এর উদাহরণ হিসেবে fingerprint-এর প্রথম exchange দেওয়া হয়েছিল। সেটা transport-অবৈধ request (header-এ control byte), যা mutation-এর তৈরি নয়। Labeller-দের TEST label ওই exchange-এর জন্য সঠিক।
   - পরের সংস্করণে INCREASED item-এর উদাহরণ হিসেবে এমন exchange দিতে হবে, যার ঘটনা control-এ নেই।
4. **"অন্যান্য" target (E004, E007, E022, E029)** প্রত্যাশিত kind-এর নয়। যেমন E022, petstore `findByTags`-এর VALID_REJECTED, যেটা baseline-এই ছিল। এদের ground truth অস্পষ্ট, তাই মূল মাপ থেকে বাদ।

## Codebook-এর জন্য প্রস্তাব (supervisor-এর সিদ্ধান্ত দরকার)
**§10.7-এর সংশোধন:**
- "Code ইচ্ছাকৃতভাবে undocumented status দেয় → SPEC" — এই নিয়ম প্রযোজ্য হবে কেবল যখন code-এর বাইরে **স্বাধীন intent-প্রমাণ** থাকে। যেমন:
  - status assert করে এমন test,
  - documentation,
  - commit বা issue,
  - একাধিক জায়গায় একই নীতি (market-এর 406 দুটো handler-এ)।
- একমাত্র প্রমাণ যদি code-এর ওই একটা লাইন হয় → **UNDECIDABLE + BOTH-প্রার্থী**।

## সীমা
- 10টি মূল target; 2টি LLM labeller (একই model family); একটিই package-নকশা।
- Labeller-রা জানত item-গুলো "fuzzing violation", আর প্রতিটি package-এ ত্রুটি থাকতে পারে।
- Decoy-এর ground truth জানা নেই; তাই decoy শুধু blinding-এর জন্য, মূল্যায়নে নয়।

---

# v2 — codebook v0.5 আর সংশোধিত package (2026-11-14, Claude)
**Pre-registration:** `E5_BLIND_V2_PLAN.md` (labelling-এর আগে লেখা)।
- **Package:** `../E2_labelling/e5_blind_v2/`।
  - Item ID আর package নাম নতুন করে এলোমেলো। Item set v1-এর সমান।
  - উদাহরণ exchange বদলেছে শুধু 2/29 item-এ (E005→E014, E022→E028)।
- **Codebook:** labeller-দের দেওয়া হয়েছে `CODEBOOK_v0.5.md`। এতে §11-এর উৎস-লাইন নেই, তাই "fault ইঞ্জেক্ট করা হয়েছে" তথ্যটা labeller পায় না।
- **Labeller:** দুটি নতুন Codex session, C1 ও C2 (high)।
- **Audit:** দুজনেই শুধু package, `tools/conformance.py` আর PROTOCOL পড়েছে। কোনো নিষিদ্ধ অ্যাক্সেস নেই (log পরীক্ষা করা হয়েছে, আর report-এও বলা আছে)।
- **তুলনা:** `compare_blind_v1_v2.py` → `e5_blind_v1_v2.csv`। Score: `e5_blind_v2_scores.csv`।

## ফল (primary set, n=9: ground truth শক্ত এমন target)
| Labeller | Codebook | IMPL* | **ভুল দিকে (SPEC/TEST)** | UNDECIDABLE (+both) |
|---|---|---|---|---|
| B1 | v0.4 | 7 | **2** | 0 |
| B2 | v0.4 | 5 | **4** | 0 |
| C1 | v0.5 | 7 | **0** | 2 (2) |
| C2 | v0.5 | 6 | **0** | 3 (3) |

- **C1–C2 L1 agreement:** 28/29, target-এ 13/14। v1-এ ছিল 23/29।
- **Decoy-এ SPEC:** v1-এ B1 4টি, B2 2টি। v2-এ C1, C2 দুজনেরই 1টি করে।

### Item অনুযায়ী (intent-দেখতে fault)
| Item (v2/v1) | Mutant | B1 | B2 | C1 | C2 | v2-এর প্রমাণ |
|---|---|---|---|---|---|---|
| E019/E014 | scout WRONG_STATUS 418 | SPEC | SPEC | **IMPL** | **IMPL** | Integration test `SystemIntegrationTest.java:24` 200 আশা করে |
| E021/E021 | market WRONG_STATUS 418 | SPEC | SPEC | **IMPL** | UNDECIDABLE+b | C1 পেয়েছে REST documentation (`market-web/.../rest.html:96-98`), যেখানে 200 লেখা। C2 এটা পায়নি। |
| E023, E024 / E011, E027 | petstore RESP_FIELD (`WRITE_ONLY`) | IMPL | SPEC | UNDECIDABLE+b | UNDECIDABLE+b | একটিই annotation, স্বাধীন প্রমাণ নেই |

বাকি primary item-গুলো (crash, guard, validation): চারজনেরই IMPL।

## ব্যাখ্যা
1. **Pre-registered সাফল্যের মানদণ্ড পূরণ হয়েছে।**
   - Primary set-এ ভুল দিকের attribution 2 আর 4 থেকে **0 ও 0**-তে নেমেছে।
   - নতুন নিয়ম যা চেয়েছিল, labeller-রা ঠিক তাই করেছে: code-এর বাইরে intent-প্রমাণ খুঁজেছে (test, documentation)। পেলে IMPL দিয়েছে, না পেলে বিরত থেকেছে।
2. **এর খরচ: বিরত থাকা।**
   - RESP_FIELD-এ B1 আগে সঠিক IMPL দিয়েছিল। v2-এ ওটা UNDECIDABLE+b।
   - অর্থাৎ v0.5 নির্ভুলতা (precision) কেনে কিছু coverage-এর বিনিময়ে। সব UNDECIDABLE-এ `both_candidate=true` আছে, তাই এগুলো adjudication-এর জন্য চিহ্নিত থাকে, হারিয়ে যায় না।
3. **প্রমাণ খোঁজার গভীরতা এখন ফলের নির্ধারক।**
   - E021-এ C1 আর C2-এর পার্থক্য এসেছে শুধু এখান থেকে: documentation ফাইলটা খুঁজে পাওয়া গেছে কিনা।
   - [H] Attribution-পদ্ধতিতে intent-প্রমাণ খোঁজার একটা নিয়মবদ্ধ ধাপ (test → docs → history) রাখলে এই অনির্দেশ্যতা কমবে।
4. **E014 (পুরোনো E005) এখনো TEST, চারজনেরই, আর সেটা যুক্তিসঙ্গত।**
   - নতুন উদাহরণটা int64-এর সীমা ছাড়ানো ID।
   - Labeller-রা নিজেরাই ধরেছে যে checker numeric format যাচাই করে না, তাই violation-টা checker-এর ফাঁক (TEST)।
   - এটা আমাদের নিজেদের পর্যবেক্ষণের সাথে মেলে: checker-এ int32/int64 format enforcement দরকার (PILOT_SUMMARY §7)।
   - এই জোড়ার mutation-এর সংকেত noise ছাড়ায় না, তাই ground truth অস্পষ্ট। Pre-registration অনুযায়ী মূল মাপের বাইরে।

## সীমা
- n=9। Labeller সব একই model family-র। একই package নকশা।
- C1/C2 আর B1/B2 আলাদা session। তাই পার্থক্যের কিছু অংশ session-এর এলোমেলোতা হতে পারে। তবে v0.4-এ দুজনেই একই নিয়ম (§10.7) উল্লেখ করেছিল, আর v0.5-এ দুজনেই §11 উল্লেখ করেছে। কাজেই নিয়মের প্রভাবই প্রধান কারণ বলে মনে হয়।
- Labeller-রা জানত item-গুলো fuzzing violation, আর package-এ ত্রুটি থাকতে পারে।
