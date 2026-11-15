# E7 — Developer-এর repair direction কী দিয়ে বোঝা যায়? (pre-registration, Claude, 2026-11-15)

**অবস্থা: FROZEN, mining শুরুর আগে।** Hash `E7_plan_freeze.sha256`-এ। Miner (T45) আর coder (C1/C2)-দের এই file পড়া নিষেধ, যাতে তারা hypothesis না জানে।

## প্রেক্ষাপট (hypothesis কোথা থেকে এল)
- **E6-এ যৌথ ভুল:** K22 আর K21-এ contract উদার কিছু কথা দিয়েছিল (optional বা default), কিন্তু code ইচ্ছাকৃতভাবে কঠোর ছিল। সব LLM labeller IMPL বলেছে, অথচ developer spec বদলেছে।
- **E6-এর 25টি item-এ Claude-এর post-hoc coding (direction জেনে, তাই biased):**
  - Code-এর বিচ্যুতি ইচ্ছাকৃত (guard, explicit status, naming config) → developer প্রায়ই spec সারিয়েছে।
  - বিচ্যুতি দুর্ঘটনাজনিত (null dereference, crash, header বাদ পড়া) → প্রায় সবসময় code।
- এই 25টি item শুধু hypothesis তৈরির কাজে লেগেছে। **Confirmatory পরীক্ষা হবে নতুন item-এ।**

## Hypothesis (আগে থেকে নির্ধারিত)
- **H-E7-1 (primary, confirmatory):** P(SPEC | DELIBERATE) > P(SPEC | ACCIDENTAL)।
  - Repair direction (SPEC/IMPL) আসবে miner-এর key থেকে।
  - Divergence kind আসবে blind coding থেকে।
- **H-E7-2 (secondary):** P(SPEC | contract GENERIC) > P(SPEC | contract SPECIFIC)।
- **Triage-এর জন্য ব্যবহারিক measure (descriptive):**
  - নিয়ম "ACCIDENTAL → IMPL, DELIBERATE → SPEC"-এর accuracy, macro-F1 (SPEC/IMPL) আর per-class precision।
  - তুলনা করা হবে majority baseline-এর সঙ্গে।

## Coding instrument (definition FROZEN; coder task-এ হুবহু যাবে)
প্রতি item-এ proposition-এর ভাষায় "implementation does Y" — অর্থাৎ parent অবস্থার behaviour Y। প্রশ্ন: **Y কি project code-এর এমন অংশ থেকে আসে, যা স্পষ্টতই Y ঘটানোর জন্য লেখা?**

**`divergence_kind`:**
- **DELIBERATE:** Y তৈরি হয় এমন project code থেকে, যা স্পষ্টতই Y-কে লক্ষ্য করে লেখা। যেমন:
  - explicit guard, validation বা required flag;
  - explicit status বা response তৈরি;
  - explicit serialization, naming বা type নির্বাচন;
  - case-টা handle করার explicit branch;
  - declared route বা handler;
  - data model-এ field-এর type বা নাম বেছে নেওয়া।
- **ACCIDENTAL:** Y কোনো বাদ পড়া বা অসাবধানতার পার্শ্বফল। যেমন:
  - unhandled exception, null dereference বা unboxing;
  - case বা default-এর branch না থাকা;
  - header বা content-type set না করা;
  - framework-এর default, যা code-এ সামলানো হয়নি;
  - ক্রমের ভুল (যেমন guard-এর আগে parse);
  - ভুল variable বা cache-এর পুনর্ব্যবহার।
- **UNCLEAR:** দেওয়া artifact থেকে সিদ্ধান্ত নেওয়া যায় না।

**`contract_specificity`** (proposition-এর "contract says X" অংশ):
- **SPECIFIC:** contract এই behaviour সম্পর্কে স্পষ্ট, আলাদা করে লেখা কথা বলে। যেমন prose description, explicit default, explicit status বা media type, অথবা এই operation-এর জন্য বিশেষ constraint।
- **GENERIC:** X এসেছে boilerplate, generator default, inherited বা shared schema, অথবা নীরবতা থেকে। যেমন operation-টা নেই, required না থাকা, schema-র type default।
- **UNCLEAR।**

প্রতিটি সিদ্ধান্তে parent-এর file:line locator আর ≤40 শব্দের rationale থাকবে।

## Data
- **Mining (T45, Codex, hypothesis জানে না):**
  - T42/T43-এর acceptance protocol অপরিবর্তিত। Direction নিয়ে কোনো targeting বা quota নেই।
  - Repo: নতুন 15টি bare clone, আর পুরোনো 22টির পরের ranked candidate।
  - এক repo থেকে সর্বোচ্চ 6টি item। লক্ষ্য ≥40টি নতুন item।
- **Coder package (`E2_labelling/e7_blind/`):**
  - শুধু parent অবস্থা: proposition, contract excerpt, implementation file।
  - Fix, message, date বা SHA থাকবে না।
  - E6-এর 25টি exploratory item এতে মেশানো থাকবে। Coder জানবে না কোনগুলো।
- **Coder:** নতুন Codex session দুটি, C1 আর C2 (high)। তারা hypothesis বা repair direction কোনোটাই জানবে না।
- **Adjudication:** C1 আর C2 একমত হলে সেটাই চূড়ান্ত। না হলে Claude adjudicate করবেন **key খোলার আগে**।
  - Claude নতুন item-এর key এই ধাপের আগে খুলবেন না। Mining report-এ শুধু aggregate সংখ্যা থাকবে।
  - E6-এর 25টি item-এর direction Claude আগে থেকেই জানেন, তাই সেগুলোর adjudication blind নয়। এগুলো শুধু exploratory।

## বিশ্লেষণ (আগে থেকে নির্ধারিত)
- **Primary set:** নতুন item, যাদের adjudicated `divergence_kind` DELIBERATE বা ACCIDENTAL, আর key-তে truth SPEC বা IMPL।
  - UNCLEAR আর BOTH বাদ যাবে, তবে তাদের সংখ্যা রিপোর্ট হবে।
- **Test:** 2×2 table-এ one-sided Fisher exact, α = 0.05।
  - প্রতিটি arm-এর P(SPEC), Wilson 95% CI সহ।
  - Odds ratio, Haldane-corrected Woolf 95% CI সহ।
- **Minimum sample:** প্রতিটি arm-এ ≥8 item। না হলে শুধু descriptive, confirmatory দাবি নয়।
- **Reliability:** `divergence_kind`-এ C1–C2-এর Cohen's κ (3-class)।
  - κ < 0.40 হলে primary ফলকে "unreliable coding" বলে চিহ্নিত করা হবে। Test তবুও চলবে।
- **Sensitivity:**
  - (a) Miner-এর confidence = 3 শুধু;
  - (b) cross-item leakage-flag থাকা item বাদ দিয়ে;
  - (c) adjudication ছাড়া, শুধু C1-C2 একমত হওয়া item।
- **Exploratory:** E6-এর 25টি item-এ একই table। আলাদা রিপোর্ট হবে, confirmatory-তে যোগ হবে না।
- **H-E7-2:** একই রকম 2×2 Fisher, `contract_specificity` দিয়ে।
- **Scorer:** `score_e7.py`, coding শেষ হওয়ার আগে লেখা হবে আর synthetic data দিয়ে test করা হবে। এর hash coding শুরুর আগে freeze হবে।

## পূর্বজ্ঞাত সীমা
- **Truth = repair direction।** এটা fault location নয়; প্রশ্নটাই repair direction নিয়ে।
- **Kind আর direction সত্যিই আলাদা কিনা নিশ্চিত নয়।** Coder (LLM) নিজের মনে direction অনুমান করে সেই অনুযায়ী kind দিতে পারে। এটা কমানোর উপায়: শুধু code-এর গঠন নিয়ে প্রশ্ন, আর locator বাধ্যতামূলক।
- **Repo বাছাই spec-first দিকে ঝুঁকে আছে।** জনপ্রিয় repo (airflow, mattermost, harbor …) থাকায় memorisation-এর ঝুঁকি আছে। তাই stars নথিভুক্ত হবে, আর popularity অনুযায়ী ভাগ descriptive হিসেবে দেখানো হবে।
- **একই model family।** Miner আর coder দুজনেই Codex।
