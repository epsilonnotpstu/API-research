# E4 — Triage মূল্যায়ন (RQ2): SPEC-দিকের held-out blind set ও পদ্ধতি-তুলনা — pre-registration খসড়া (Claude, 2026-11-15)

**অবস্থা:** খসড়া। এটা চূড়ান্ত (FROZEN) হবে package তৈরির পরে, কিন্তু **labelling শুরুর আগে**। Freeze-এর পরে measure বা মানদণ্ড বদলানো যাবে না; বদলালে সেটা আলাদা "post-hoc" অংশে যাবে।

## কেন (সৎ review থেকে)
1. **SPEC recall কখনো মাপা হয়নি।** E5-এর ground truth শুধু IMPL। তাই "সব IMPL বা UNDECIDABLE" বলা একটা procedure-ও সেখানে পাস করে।
2. Roadmap-এর RQ2 (triage-এর নির্ভুলতা বনাম baseline) এখনো খোলা।
3. আগের metric একাধিকবার বদলেছে। তাই এখানে আগে থেকে নির্ধারিত plan লাগবে।

## Item set (builder: T40)
- **SUT ও traffic:** চার SUT-এর **labelled seed-1 baseline** (positive-only Schemathesis):
  - scout `20261113T202103Z_baseline_NONE_p0_s1_1642810`
  - petstore `20261114T021748Z_batch_1701236_baseline_NONE_p0_s1`
  - market `20261114T023303Z_batch_1724645_baseline_NONE_p0_s1`
  - cwa `20261114T084828Z_batch_118863_baseline_NONE_p0_s1`
- **প্রতি SUT-এ একটা composite mutated spec:**
  - চারটি fault class (LOOSE, STRICT, ORACLE, METHOD_SEM) **আলাদা আলাদা operation-এ** প্রয়োগ, নির্দিষ্ট seed-এ, `specmut` দিয়ে।
  - Package-এ এই একটা spec-ই থাকবে। Original spec থাকবে না, তাই diff করে mutation ধরা যাবে না।
- **Injected item (truth = SPEC):**
  - Baseline traffic-কে composite spec দিয়ে **replay**। Mutated op-এ NEW fingerprint, যার kind fault-এর canonical expected kind।
  - SPEC L2 আসে fault থেকে (specmut `EXPECTED`)। প্রতিটি fault × SUT থেকে সর্বোচ্চ 3টি, deterministic ভাবে বাছা।
- **Decoy (truth = adjudicated final label, secondary):**
  - একই replay-এ PERSISTENT baseline fingerprint (original spec-এও ছিল)। এদের label `final_labels_baseline_s1.csv`-এ আছে: SPEC/IMPL/BOTH/TEST/UNDECIDABLE।
  - প্রতি SUT-এ সর্বোচ্চ 6টি, label stratum অনুযায়ী deterministic।
  - ⚠️ Decoy-র truth adjudicated। Injected item-এর মতো construction-গত সত্য নয়।
- **Package:** `E2_labelling/e4_blind/K??/`:
  - `source/`: original SUT source;
  - `spec.json`: composite;
  - `r1/exchanges.jsonl` আর `compose.log`;
  - `items.csv`।
  - Key থাকবে `E4_triage/e4_key.csv`-এ, labeller-দের জন্য নিষিদ্ধ।

## পদ্ধতি (মূল্যায়নের বিষয়)
- **M0 naive:** সব IMPL। এটা tool-গুলোর ডিফল্ট ধারণা।
- **M1 zero-shot LLM:** নতুন Codex session। Codebook আর intent tool ছাড়া, শুধু item, spec, exchange আর source। প্রশ্ন: "spec defect নাকি implementation fault নাকি অন্য?"। Effort high।
- **M2 codebook v0.6 LLM (evidence-based):** নতুন Codex session দুটি (F1, F2)। Labeller copy `CODEBOOK_v0.6.md` আর `intent_evidence.py`। Task E5 v3-এর মতো। Effort xhigh।
- **M3 rule-based triage (ঐচ্ছিক, সময় থাকলে):** E1 data-র জন্য triage.py-র নিয়মের port।
- **IMPL-দিকের তুলনা:** M2-এর IMPL-দিক E5 v3 (D1/D2) থেকে নেওয়া। M1-কেও E5 v3 package-এ চালানো হবে (নতুন session), যাতে দুই দিকেই M1 বনাম M2 তুলনা করা যায়।

## Measure (আগে থেকে নির্ধারিত)
- **Primary, injected SPEC item-এ প্রতি পদ্ধতি/labeller:**
  - (a) **SPEC recall** = SPEC/SPEC_PARTIAL-এর ভাগ;
  - (b) **ভুল দিক** = IMPL/IMPL_PARTIAL;
  - (c) UNDECIDABLE বা DEFERRED;
  - (d) TEST বা ENV।
- **দুই দিক একসঙ্গে** (E4 SPEC item + E5 v3 primary IMPL item):
  - per-class precision/recall, macro-F1 (SPEC, IMPL, abstain আলাদা class);
  - abstain বাদ দিয়ে decided accuracy আর coverage।
- **Secondary, decoy-তে:** adjudicated final label-এর সঙ্গে agreement। Exact আর compatible (BOTH ↔ primary + flag)।

## সাফল্যের মানদণ্ড (আগে থেকে নির্ধারিত)
- **P1:** M2-এর injected SPEC item-এ ভুল-দিক (IMPL) ≤ 10%, দুই labeller-এরই।
- **P2:** M2-এর two-direction macro-F1 > M0 আর > M1।
- **P3, তথ্যমূলক:** M2-এর SPEC recall জানানো হবে। কোনো threshold নেই। ⚠️ ধারণা হলো recall কম হবে, কারণ v0.6 স্বাধীন প্রমাণ চায়, আর spec defect-এর পক্ষে স্বাধীন প্রমাণ (code-এর আচরণ intended) প্রায়ই test বা doc-এ থাকে।

## পূর্বজ্ঞাত সীমা
- **Positive-only traffic:** REQUEST_LOOSE-এর injected item কম বা শূন্য হতে পারে, কারণ VALID_REJECTED-এর জন্য invalid request লাগে।
- **কৃত্রিম spec edit:** `maxLength:1`, `maximum:0` বা সব property required-এর মতো edit চোখে পড়ার মতো অস্বাভাবিক, ফলে SPEC বলা সহজ হতে পারে। বাস্তব spec defect এত স্পষ্ট নয়। এটা external validity-র threat।
- **Model family:** সব labeller একই model family-র।
- **Decoy-র উৎস:** decoy-র label এই একই LLM বা adjudication pipeline থেকে এসেছে।
- **n:** ছোট (আনুমানিক 20–40টি SPEC item)।
