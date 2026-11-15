# E6 ফল: আসল contract-alignment fix-এ triage পদ্ধতির তুলনা (2026-11-15, Claude)

**Truth:** developer নিজে কোন দিক সারিয়েছে। Contract বদলালে SPEC, behaviour বদলালে IMPL।

**Pre-registration:**
- `E6_PLAN.md`, labelling শুরুর আগে FROZEN।
- Scorer `score_e6.py` labelling-এর আগে লেখা আর dry-run করা। Output `e6_scores.csv`।
- Scoring-এর সময় freeze hash (`e6_package_freeze.sha256`) আবার হিসাব করে মেলানো হয়েছে: items, codebook, দুই TASK, K-tree, scorer, key, stars, `score_e4.py` — সব OK।

## Labeller
| ID | পদ্ধতি | Effort |
|---|---|---|
| Y1, Y2 | M1: zero-shot, codebook বা tool নেই | high |
| G1, G2 | M2: codebook v0.6 + intent tool (history scope `unavailable`) | xhigh |

- সবাই নতুন Codex session।
- Usage limit-এ মাঝপথে থেমেছিল, পরে একই session resume করা হয়েছে। Package বা task বদলানো হয়নি।
- Item: 18টি (truth IMPL 10, SPEC 8), 11টি repo থেকে।

## Pre-registered ফল (n=18)

| পদ্ধতি | macro-F1 | SPEC P/R | IMPL P/R | Decided-accuracy | Coverage |
|---|---|---|---|---|---|
| M0 সব IMPL (majority) | 0.36 | 0/0 | 0.56/1.00 | 0.56 | 1.00 |
| M0 সব SPEC | 0.31 | 0.44/1.00 | 0/0 | 0.44 | 1.00 |
| **M1 Y1** | **0.86** | 1.00/0.75 | 0.82/0.90 | 0.88 | 0.94 |
| **M1 Y2** | **0.88** | 1.00/0.75 | 0.90/0.90 | 0.94 | 0.89 |
| M2 G1 | 0.72 | 1.00/0.50 | 0.88/0.70 | 0.92 | 0.67 |
| M2 G2 | 0.70 | 1.00/0.50 | 0.78/0.70 | 0.85 | 0.72 |

**Labeller-এর মধ্যে মিল:** Y1–Y2 17/18, G1–G2 15/18।

**মানদণ্ড:**
- **Q1 PASS:** দুই M1 labeller-ই M0-কে ছাড়িয়েছে (0.86 ও 0.88, বনাম 0.36)।
- **Q2 (দিক আগে থেকে ধরা হয়নি): M1 > M2, দুই জোড়াতেই।** Macro-F1 0.86–0.88 বনাম 0.70–0.72।
  - ⇒ **E4-এর ফল আসল fix-এও টিকেছে।** তবে ব্যবধান ছোট: E4-এ ছিল প্রায় 0.26, এখানে প্রায় 0.15।
- **Q3 FAIL:** মানদণ্ড ছিল প্রতিটি M2 labeller-এর decided-accuracy ≥ M1-এর গড় (0.91)।
  - G1 0.92 পেরিয়েছে, G2 0.85 পেরোয়নি।
  - ⇒ "Codebook ভুল কম করে, তাই বেশি নিরাপদ" দাবি এখানে সমর্থিত নয়। Decided-accuracy মোটামুটি সমান (0.85–0.94)।
- **Popularity ভাগ:** ≥500 star-এর item মাত্র 2টি (K02 microcks, K25 Iced-Latte)। ভাগটা অর্থহীন, তাই কোনো সিদ্ধান্ত টানা হয়নি। এটা আগেই সীমা হিসেবে লেখা ছিল।

## Item ধরে বিশ্লেষণ (post-hoc; pre-registered নয়)

**জোড়া ধরে তুলনা:** M1 সঠিক কিন্তু M2 নয় — প্রতি জোড়ায় 4টি item (K02, K12, K14, আর K15 বা K23)। উল্টো ঘটনা একবারও নেই।
- Exact sign test p=0.125, প্রতিটি জোড়ায় আলাদাভাবে। n ছোট, তাই এটা একা significant নয়।
- E4-এর সঙ্গে দিক একই।

**M2-এর বাড়তি abstention পুরোটাই coverage-এর খরচ:**
- K02, K12, K14-এ দুই G-ই UNDECIDABLE দিয়েছে। কারণ ছিল independent test বা doc-এর অভাব, অর্থাৎ §11.4-এর evidence gate।
- তিনটিতেই দুই M1 সঠিক।
- M2 abstain করে M1-এর একটিমাত্র ভুল এড়িয়েছে: K21-এ G1।

**সব পদ্ধতির যৌথ ভুল:**
- **K22 (cwms-data-api, truth SPEC):**
  - Contract-এ লেখা ছিল office না দিলে user session-এর office ধরা হবে। Code-এ office বাধ্যতামূলক।
  - চারজনই IMPL দিয়েছে। Developer contract বদলে office required করেছে।
- **K21 (swagger-petstore, truth SPEC):**
  - Contract-এ `status` optional, default available। Code null পেলে 400 দেয়।
  - Developer contract-এ required করেছে। Y1 আর G2 IMPL দিয়েছে, Y2 আর G1 abstain করেছে।

⚠️ **অনুমান (n=2, তাই anecdotal):** দুটোই এক ধরনের অমিল — contract উদার কিছু কথা দিয়েছে (optional বা default), কিন্তু code কঠোর।
- LLM দুই পদ্ধতিতেই contract-কে intent ধরে IMPL বলেছে।
- Developer সস্তা পথ নিয়েছে: contract কঠোর করেছে।
- **Fuzzer-এর দিক থেকে এগুলো VALID_REJECTED।** Fuzzer এ ধরনের ঘটনাকে "server bug" হিসেবে দেখায়। কিন্তু developer-এর repair direction এখানে SPEC।
- ⇒ "Repair direction ≠ fault location" সীমাটা এখানে বাস্তবে দেখা গেল। REQUEST_LOOSE-ধাঁচের অমিলে triage-এর একটা প্রথাগত prior দরকার হতে পারে। এটা পরীক্ষাযোগ্য hypothesis, এখনো প্রমাণিত নয়।

**K08 (rhsm, truth IMPL):**
- চারজনই UNDECIDABLE দিয়েছে।
- Proposition-এ শুধু লেখা "IllegalArgumentException throw হয়"। আসল HTTP status কী হয়, তা লেখা নেই, আর package থেকে framework-এর wrapping বোঝা যায় না।
- ⇒ এটা item-এর মানের সমস্যা, proposition অসম্পূর্ণ। Abstain এখানে যুক্তিসঙ্গত।
- Post-hoc হিসেবে K08 বাদ দিলেও Q1–Q3-এর ফল বদলায় না। M1-এর macro-F1 বাড়ে, M2-রও বাড়ে, ক্রম একই থাকে।
  - n=17-এ macro-F1: Y1 0.88, Y2 0.90, G1 0.75, G2 0.72; M0 0.35।
  - Q3: G1 পেরোয়, G2 পেরোয় না।

## E4-এর সঙ্গে তুলনা
| | E4 (কৃত্রিম fault + decoy) | E6 (আসল fix) |
|---|---|---|
| M1 macro-F1 | 0.94 | 0.86–0.88 |
| M2 macro-F1 | 0.66–0.70 | 0.70–0.72 |
| M2 SPEC recall | 0.39–0.46 | 0.50 |
| M2 coverage | 0.54–0.59 | 0.67–0.72 |
| M2 > M1? | না | না |

**উপসংহার:**
- Zero-shot (source access সহ) codebook procedure-এর চেয়ে ভালো — কৃত্রিম আর আসল দুই benchmark-এই।
- Codebook-এর evidence gate দুটোতেই coverage কমায়। কিন্তু ভুল উল্লেখযোগ্যভাবে কমায় না।
- ⇒ **R1-এর জন্য:** codebook v0.6-এর §11.4 gate (independent intent evidence ছাড়া attribution নয়) বর্তমান আকারে খুব কঠোর।
  - সম্ভাব্য পরিবর্তন: gate-কে abstain-এর বদলে confidence-এ নামিয়ে আনা।
  - এটা নতুন pre-registered মূল্যায়ন ছাড়া দাবি করা যাবে না।

## সীমা
- **n=18, আর একটি item-এর মান দুর্বল (K08)।** CI চওড়া। Sign test একা significant নয়।
- **Truth = repair direction।** K21/K22 দেখায়, এটা fault location থেকে আলাদা হতে পারে।
- **একই model family।** সব labeller Codex `gpt-6.1-sol`, আর proposition-ও Codex লিখেছে। Model-এর মধ্যে প্রথাগত bias ভাগ হতে পারে।
- **Memorisation যাচাই করা যায়নি।** ≥500 star-এর item মাত্র 2টি। Swagger-petstore বহুল পরিচিত, যদিও এই repo-র star 336।
- **Static-only:** package-এ runtime exchange নেই। K08-এর মতো item-এ framework-এর আচরণ অনুমানের ওপর নির্ভর করে।

## Boundary incident (labeller-দের নিজেদের report থেকে, Claude যাচাই করেছেন)
- **Path ছাড়া `rg --files`:** চারজনই session-এর শুরুতে explicit path ছাড়া একটি `rg --files` চালিয়েছে। শুধু task-এর filename ফিরেছে।
  - G2-এর search 09_collab-এ গিয়ে protocol, নিজের log আর একটি task draft-এর pathname পেয়েছে। Content খোলেনি।
  - E4-এও একই ঘটনা ঘটেছিল। ⇒ TASK template-এ প্রথম command স্পষ্টভাবে বলে দিতে হবে।
- **Protocol-এর ভুল path-এ existence probe:** Y1 আর G1 করেছে। Content পড়েনি।
- **cwa test-fixture-এর TAN/hash literal transcript-এ ছাপা হয়েছে:** Y1, G1, G2।
  - Deliverable-এ এগুলো নেই। Claude scan করেছেন: demo credential, key, token, email কিছু পাওয়া যায়নি। "Email"-এর মতো যা মিলেছে, সব `line@Annotation` ধরনের reference।
  - ⇒ `09_collab/logs/E6_*.log` gitignore করা হয়েছে।
- **Intent tool:** ancestor `.git` পেলে history দেওয়া বন্ধ করেছে (`enclosing repository outside source_dir`; G1/G2-এর 9টি search output)। T38-এর fix কাজ করছে।
