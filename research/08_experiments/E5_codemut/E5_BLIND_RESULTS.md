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
