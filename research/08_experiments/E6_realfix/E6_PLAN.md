# E6 — আসল defect-এ triage মূল্যায়ন (truth = developer-এর fix-এর দিক): pre-registration খসড়া (Claude, 2026-11-15)

**অবস্থা:** খসড়া। Package তৈরির পরে, labelling-এর আগে FROZEN হবে (hash সহ)।

## প্রশ্ন
E4-এ কৃত্রিম fault-এ zero-shot LLM (M1) codebook-v0.6 procedure-কে (M2) ছাড়িয়েছে। macro-F1 ছিল 0.94 বনাম 0.66–0.70। **আসল spec↔code অমিলেও কি তাই হয়?**
- এখানে truth হলো developer নিজে কোন দিক সারিয়েছে:
  - spec বা contract বদলালে → SPEC;
  - behaviour বদলালে → IMPL।

## Item set
- **উৎস:** `combined_accepted.csv` (T42 ∪ T43), deduplicated।
- **ছাঁকনি:**
  - confidence ≥2;
  - একটি repo থেকে সর্বোচ্চ 8টি item, যাতে কোনো একটা project আধিপত্য না পায়;
  - fix-family ধরে একটির বেশি নয়।
- **লক্ষ্য:** ≥40টি item, minority দিক ≥40%। এটা না হলে যা পাওয়া যায় তা নিয়েই এগোনো হবে, আর ভারসাম্যের অভাব সীমা হিসেবে লেখা হবে। মাপকাঠি হবে per-class।

## Package (প্রতি item, blind)
- **Parent commit-এর source snapshot।** `git archive`-এর মতো, কিন্তু শুধু প্রাসঙ্গিক module, যাতে আকার ছোট থাকে।
  - CHANGELOG বা release note-এ ভবিষ্যৎ fix-এর উল্লেখ আছে কিনা পরীক্ষা করা হবে। থাকলে সেই অংশ বাদ যাবে।
- **Contract:** parent-এর spec file, অথবা annotation-ভিত্তিক হলে source-এর ভেতরেই।
- **Proposition:** নিরপেক্ষ template, শুধু parent অবস্থা থেকে লেখা: `"<METHOD> <path>: contract says <X>; implementation does <Y>"`।
  - কোন দিকে পরে বদল হয়েছে, তার কোনো ইঙ্গিত থাকবে না। Claude নমুনা নিয়ে যাচাই করবেন।
- **Runtime exchange থাকবে না।** T42 অনুযায়ী এই item-গুলো static-ভাবে বিচারযোগ্য।
- **VCS history থাকবে না।** Repo আর project-এর নাম লুকানো সম্ভব নয়, তাই popularity (stars) নথিভুক্ত হবে।

## পদ্ধতি
- **M0:** সব SPEC (majority-class baseline) আর সব IMPL, দুটোই।
- **M1 zero-shot:** নতুন Codex session দুটি (Y1, Y2), high। E4-এ zero-shot ছিল একজন, এবার দুজন।
- **M2 codebook v0.6 + intent tool:** নতুন session দুটি (G1, G2), xhigh। Tool-এর history scope `unavailable`।

## Measure (আগে থেকে নির্ধারিত)
- **Per-class recall** (SPEC, IMPL) আর **macro-F1** (SPEC/IMPL)। ABSTAIN আর OTHER = miss।
- **Decided-accuracy** আর coverage।
- Popularity অনুযায়ী ভাগ: stars <500 বনাম ≥500 (memorisation-এর ঝুঁকি)।
- Labeller-এর মধ্যে মিল।

## মানদণ্ড (আগে থেকে নির্ধারিত)
- **Q1:** M1 macro-F1 > M0 (majority)।
- **Q2:** M2 বনাম M1-এর macro-F1। কোনো দিক অনুমান করা নেই, দুটোই রিপোর্ট হবে। E4-এর ফল এখানে টেকে কিনা, এটাই মূল প্রশ্ন।
- **Q3:** M2-এর decided-accuracy ≥ M1-এর decided-accuracy। এটা "নিরাপত্তা"-র দাবি পরীক্ষা করে।

## পূর্বজ্ঞাত সীমা
- **Developer-এর fix-এর দিক মানেই আসল "দোষ" নয়।** Developer হয়তো সহজ দিকটা সারিয়েছে, যেমন spec বদলানো কম খরচের। আমরা "repair direction" মাপছি।
- **Item কম, আর SPEC-এর দিকে ঝোঁক থাকতে পারে।**
- **Memorisation:** LLM হয়তো জনপ্রিয় repo-র history জানে।
- **Proposition লিখেছে Codex, যে fix দেখেছিল।** তাই শব্দচয়নে bias থাকতে পারে। Claude নমুনা যাচাই করবেন।
