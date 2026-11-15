# R1 pilot — চার SUT-এর সমন্বিত ফল (2026-11-14, Claude)

এই নথি E1 (fault injection) আর E2 (baseline labelling) মিলিয়ে বর্তমান প্রমাণের সারাংশ। প্রতিটি সংখ্যার উৎস-ফাইল নিচে দেওয়া আছে।
- ⚠️ চিহ্ন = অনুমান।
- [H] = paper-এ দাবি করার আগে আরও যাচাই দরকার।

## 1. Setup
| | scout-api | swagger-petstore | market | cwa-verification |
|---|---|---|---|---|
| Spec | Swagger 2.0 | OpenAPI 3.0.4 | Swagger 2.0 | OpenAPI 3.0.1 |
| Operation | 49 | 19 | 13 | 5 (সব POST) |
| Request constraint (spec-এ) | 18 | 6 | 51 | 10 |
| Auth | EMB admin header | নেই | EMB user header | নেই |
| Line / branch coverage (baseline) | 29–32% / 16–19% | 72–73% / 60–61% | 35–36% / 3–4% | 43% / 9% |

**সাধারণ setup:**
- EMB commit 915859080da0…; Schemathesis 3.39.16 (Docker); mitmproxy 10.2.4 (পুরো exchange log); JaCoCo 0.8.12।
- Budget 300 s, max examples 100, seed 1–3।
- Fault মাপা হয়েছে `specmut` দিয়ে, চারটি class-এ।
- **Main protocol:** positive data, এলোমেলো 30% operation, default oracle।
- Harness: `E1_pilot/harness` (v1, scout Batch 2) এবং `E1_pilot/harness_v2` (বাকি সব)।
- Coverage: `coverage/README.md`।

## 2. Fault detection — replay mode
উৎস: `all_runs_occurrence_metrics.csv` (`recount_all.py`)। Diagnostic batch বাদ: `20261114T025044Z_batch_1756007`, `…025723Z_batch_1771572`, `…081502Z_batch_102982`, `…093050Z_batch_195691`।

মান = seed 1/2/3। **N** = NEW fingerprint, **V** = VANISHED, **I** = INCREASED, **D** = DECREASED (দুটোই occurrence স্তরে, mutated op-এ)।

| Fault | Protocol | scout-api | petstore | market | cwa |
|---|---|---|---|---|---|
| REQUEST_STRICT | main | N 28/20/61 | N 11/6/30 | N 0/2/10 | V 0/2/1 |
| RESPONSE_ORACLE | main | N 90/0/0 | N 4/12/5 | N 8/5/10 | 0/0/0 |
| RESPONSE_ORACLE | baseline-2xx pool | N 4/86/43 | — | — | — |
| METHOD_SEM | main | N 5/11/15, V 5/10/14 | N 10/7/7, V 12/8/10 | N 3/7/6, V 0/7/3 | N 2/2/2, V 2/2/2 |
| REQUEST_LOOSE | main | 0 | 0 | 0 | 0 |
| REQUEST_LOOSE | constraint pool + negative data + 100% | N 1/1/1, V 1/1/1 | I 1/1/1, V 0/0/1 | I 2/1/2 (SUT oracle); 0 (default) | N 2/2/2, I 2/3/2 |

**প্রতিটি replay সারিতে দুটো জিনিস সবসময় 0:**
- unexplained (NEW/VANISHED অপরিবর্তিত op-এ)।
- অপরিবর্তিত op-এ occurrence-এর পরিবর্তন।

আর NEW-এর manifest label match 100%। ⚠️ এটা নকশাগত, কারণ replay-তে mutated op-এর নতুন violation manifest-এর label পায়।

## 3. Fresh mode (নতুন fuzzing run) — সতর্কতার সাথে পড়তে হবে
| Fault (main) | scout | petstore | market | cwa |
|---|---|---|---|---|
| REQUEST_STRICT: fresh NEW (replay NEW-এর তুলনায়) | 0/2/0 (28/20/61) | 6/0/23 (11/6/30) | 2/0/0 (0/2/10) | 0 (0) |
| REQUEST_STRICT: fresh VANISHED / DECREASED | V 0/2/1, D 12/11/13 | V 2/0/2 | V 4/1/3, D 0/4/0 | V 1/2/1 |

- Main protocol-এ fresh unexplained প্রায় 0: মোট 8, সবগুলো petstore-এ (METHOD_SEM 1, LOOSE 1, STRICT 6)।
- Negative data-য় fresh-এর noise অনেক বেড়ে যায়। scout LOOSE-এ অপরিবর্তিত op-এ পরিবর্তন 45–62। তাই fresh-এর occurrence metric ব্যাখ্যার জন্য একই seed-এ একাধিক baseline দিয়ে noise floor মাপা দরকার। এটা এখনো করা হয়নি।

## 3b. Negative + positive data (`DATA_GEN=all`) — STRICT, ORACLE (baseline-2xx pool), METHOD_SEM
প্রতিটি SUT-এর batch `runs/<sut>/batches/`-এ, `neg_all_<sut>.console.log` অনুযায়ী: 12 run আর 9 analysis করে, সব complete। মান = seed 1/2/3।

| Fault | Mode | scout | petstore | market | cwa |
|---|---|---|---|---|---|
| REQUEST_STRICT | replay N | 31/20/53 | 11/4/31 | 0/2/6 | 0/0/0 (V 0/2/1) |
| REQUEST_STRICT | **fresh N** | **26/23/55** | **11/7/21** | **1/4/6** | 0 (V 3/2/1) |
| RESPONSE_ORACLE (pool) | replay N | 0/86/44 | 5/7/13 | 8/5/6 | 1/0/0 |
| METHOD_SEM | replay N / V | 5/12/16 / 5/11/15 | 10/7/8 / 12/8/11 | 3/8/6 / 0/12/7 | 2/3/4 / 2/2/2 |
| সব | replay unexplained, অপরিবর্তিত op-এ পরিবর্তন | 0, 0 | 0, 0 | 0, 0 | 0, 0 |
| সব | fresh: অপরিবর্তিত op-এ পরিবর্তন | 49–84 | 12–22 | 2–21 | 2–4 |

**সংশোধন (2026-11-14):** negative data দিলে REQUEST_STRICT-এর fresh NEW প্রায় replay-এর সমান। তাই §5-এর H1 শর্তসাপেক্ষ: এটা positive-only generation-এর (Schemathesis default) ফল। তবে fresh-এর noise অনেক বেশি; replay নিখুঁত থাকে।

## 4. Baseline violation-এর চূড়ান্ত label (E2)
উৎস: `../../E2_labelling/FINAL_LABELS.md`, `final_labels_baseline_s1.csv`।

| | n | SPEC (+PARTIAL) | IMPL | BOTH | TEST | UNDECIDABLE |
|---|---|---|---|---|---|---|
| scout-api | 99 | 31 | 32 | 17 | 1 | 18 |
| swagger-petstore | 43 | 7 | 7 | 7 | 20 | 2 |
| market | 13 | 4 | 2 | 6 | 1 | 0 |
| cwa-verification | 6 | 2 | 0 | 0 | 4 | 0 |
| **মোট** | **161** | **44** | **41** | **30** | **26** | **20** |

- **Labeller:** A = Claude, B = Codex (blind), adjudication supervisor-এর।
- **Pooled A–B agreement:** L1 80.7% (κ 0.73)। Codebook §10.1-এর BOTH-রীতি মেলালে 84.5% (κ 0.77)।

## 5. দাবির প্রার্থী (paper-এর জন্য)
1. **[H1, সংশোধিত] Positive-only fuzzing-এ spec-ত্রুটি প্রায়ই অদৃশ্য; replay সেগুলো দেখায়। Negative data দিলে fresh-ও দেখায়, তবে অনেক বেশি noise-সহ (§3b)।**
   - **Noise floor (2026-11-14):** baseline replicate দিয়ে মাপলে fresh-এর mutated-op সংকেত 51/61 run-এ noise ছাড়ায়। অপরিবর্তিত op-এর পরিবর্তন প্রায় পুরোটাই noise। ব্যতিক্রম: cwa STRICT/ORACLE, আর market LOOSE (সেখানে শুধু occurrence-স্তরে)। `NOISE_FLOOR_SPEC.md`।
   - REQUEST_STRICT, তিন seed-এর মোট NEW:

     | SUT | Replay | Fresh |
     |---|---|---|
     | scout | 109 | 2 |
     | petstore | 47 | 29 |
     | market | 12 | 2 |
     | cwa | 0 | 0 |

   - Petstore-এ fresh-এর সংকেত তুলনামূলক বেশি। ⚠️ সম্ভবত এর spec-এ header constraint আছে, যা generator সরাসরি ব্যবহার করে।
   - Fresh-এ বরং violation **হারায়** (market V 4/1/3, scout D 12/11/13)। ⚠️ মানে কঠোর spec থেকে generator "কম খারাপ" input পাঠায়, তাই IMPL-ত্রুটি আড়াল হয়।
2. **[H2] একক-পক্ষের attribution অপর্যাপ্ত।** নির্ণয়যোগ্য baseline অমিলের 26% (30/115) BOTH: spec আর code দুটোই বদলাতে হয়।
3. **[H3] Detectability fault class আর spec-এর গঠনের ওপর নির্ভর করে।**
   - RESPONSE_ORACLE ধরা পড়ে কেবল 2xx body আর editable response schema থাকলে। scout-এর 30টি op schema-হীন `default` ঘোষণা করে।
   - REQUEST_LOOSE ধরা পড়ে তিন শর্তে: negative traffic, checker-এর মূল্যায়িত constraint, প্রচলিত rejection status।
4. **[H4] Fingerprint-স্তরের attribution metric সংকেত লুকায়।** শিথিলতার প্রভাব নতুন fingerprint হিসেবে নয়, পুরোনো fingerprint-এর বাড়তি occurrence হিসেবে আসে (`LOOSE_RESULTS.md` §6)।
5. **[H5] Stateful fault per-operation attribution ভাঙে।** Petstore-এ `POST /user {}` (#952) থেকে পাঁচটি অন্য operation-এ 500।
6. **[H6] Oracle নিজেই উল্লেখযোগ্য ত্রুটির উৎস।** Baseline-এর 16% (26/161) TEST:
   - checker coverage (XML/form body),
   - int64 format enforce না করা,
   - server state না বোঝা (cwa token),
   - fuzzer-এর probe।
   - আর default oracle SUT-এর rejection convention (market 406) বোঝে না।

7. **[H7] Code fault (E5) fresh fuzzing-এ নির্ভরযোগ্যভাবে ধরা পড়ে, কিন্তু মোট গণনায় নয়।**
   - 9টি mutant, 22টি বৈধ জোড়া-seed।
   - Mutated op-এ সংকেত 22/22; প্রত্যাশিত kind 20/22।
   - অপরিবর্তিত op-এর noise বড়, কিন্তু control বনাম control-এর সমান মাপের। অর্থাৎ ওটা fuzzing-এর অনির্দেশ্যতা।
   - **Noise floor (44টি control-repeat run):** সংকেত noise ছাড়ায় 18/22 জোড়া-seed-এ, 7/9 mutant-এ।
     - ব্যতিক্রম market-drop-null: শুধু INCREASED, আর noise-ও একই মাপের।
     - ব্যতিক্রম petstore-reject-valid: fingerprint noise-এও আছে।
   - Mapped op-এ কাকতালীয় "প্রত্যাশিত kind" 3/22 noise run-এ।
   - Attribution label-এর মূল্যায়ন: H8 দেখুন।
   - উৎস: `../../E5_codemut/E5_RESULTS.md` §3b।
   - **হালনাগাদ (2026-11-15):** বিকল্প site (v2, v3) আর নতুন checker (int format) যোগ করে এখন হিসাব 12 mutant, 31 জোড়া-seed।
     - সংকেত 31/31, প্রত্যাশিত kind 26/31, noise ছাড়ায় **25/31**।
     - Site-প্রতি একটা গুনলে (v2 বাদ): 26/28 আর 25/28।
     - উৎস: `E5_RESULTS.md` §3c। Validator-এ provenance আর drift আলাদা করা হয়েছে (T30)।

8. **[H8] শুধু code-এর ভিত্তিতে intent-বিচার ইচ্ছাকৃত-দেখতে code fault-কে SPEC বলে।** Blind E5 labelling (দুটি নতুন Codex session):
   - Crash, guard আর validation fault: IMPL 5/5।
   - WRONG_STATUS: 0/2। দুই labeller-ই codebook §10.7 উল্লেখ করেছে।
   - RESP_FIELD annotation: B2 0/2।
   - প্রত্যাশিত-kind target-এ মোট: B1 7/10, B2 5/10।
   - **Codebook v0.5 (§11, স্বাধীন intent-প্রমাণ বাধ্যতামূলক) দিয়ে আবার করা হয়েছে:** নতুন labeller C1/C2, pre-registered, primary n=9।
     - ভুল দিকের (SPEC/TEST) attribution: B1 2, B2 4 → **C1 0, C2 0**।
     - IMPL* 7/6। বাকিগুলো UNDECIDABLE+both।
     - WRONG_STATUS-এ labeller-রা test আর documentation-এ intent-প্রমাণ খুঁজে পেয়ে IMPL দিয়েছে।
     - খরচ: annotation fault-এ বিরত থাকা।
   - উৎস: `../../E5_codemut/E5_BLIND_RESULTS.md` (v1 + v2)।

9. **[H9] দ্বিতীয় fuzzer (EvoMaster v6.2.0 black-box) — fault class-স্তরের প্যাটার্ন একই রকম, ঘর-স্তরে generator-নির্ভরতা আছে।** উৎস: `FUZZER_COMPARE.md`।
   - **Controlled ঘর** (একই mutation set, p30): EvoMaster **20/26**, Schemathesis **19/26**।
   - পার্থক্য আসে নির্দিষ্ট ঘরে:
     - market STRICT 0/3 বনাম 3/3: EvoMaster-এর ভাঙা request 500 পায়, 2xx নয় (T32)।
     - petstore METHOD_SEM 3/3 বনাম 0/3: Schemathesis-এর সংকেত শুধু UNCHECKABLE।
   - RESPONSE_ORACLE দুই fuzzer-এই শক্তিশালী, REQUEST_LOOSE দুটোতেই দুর্বল।
   - **একই seed-এ EvoMaster প্রায় একই request sequence পুনরাবৃত্তি করে** (প্রতিটি seed-এ 1টি replicate; cwa হুবহু এক, scout s2 ব্যতিক্রম)।
     - Observed same-seed reference 45/48 row-এ 0।
     - Mutated run-এর traffic: request-side mutation-এ baseline থেকে প্রায় পুরো আলাদা (positional median ~0.01), ORACLE-এ প্রায় একই (median 0.966)।
     - ⚠️ Hypothesis (T34 F1): fresh-mode noise reference fault class অনুযায়ী বাছা উচিত হতে পারে। এখন দুটো reference-ই পাশাপাশি দেওয়া হচ্ছে।
     - Schemathesis-এর same-seed replicate একে অপরের থেকে অনেক সরে যায় (median 0.26–0.72)।
   - Scout-এ EvoMaster-এর জন্য derecursed input লেগেছে (recursive schema inline হওয়ায় stall; T31)।

## 6. সীমা (threats to validity)
- **External validity:**
  - চারটিই Java/Spring/Dropwizard SUT; budget 300 s; seed 3টি।
  - দুটি fuzzer: Schemathesis (মূল) আর EvoMaster (তুলনা, H9)। EvoMaster-এর তুলনা শুধু fresh mapped-fingerprint স্তরে।
  - Coverage মাঝারি থেকে কম (branch 3–61%)।
- **Construct validity:**
  - fault তৈরি করা কৃত্রিম (`specmut`)।
  - Replay-এর label match নকশাগত।
  - একক হলো fingerprint, root cause নয়।
- **Labelling:**
  - দুটি LLM labeller আর একজন মানব adjudicator।
  - 11টি label rule থেকে প্রয়োগ করা, item ধরে দেখা হয়নি।
  - মানব inter-rater reliability নেই।
- **Protocol:** negative data এখন চারটি fault class-এই প্রয়োগ হয়েছে (§3b)। Pool/severity এখনো fault-ভেদে আলাদা: LOOSE constraint pool 100%, ORACLE 2xx pool 30%, STRICT/METHOD_SEM এলোমেলো 30%।

## 7. পরের ধাপ
2. ~~Fresh-এর noise floor (spec mutation)~~ — হয়েছে, বিদ্যমান replicate থেকে: 51/61 run-এ সংকেত noise ছাড়ায় (`NOISE_FLOOR_SPEC.md`)।
3. ~~Checker-এ int32/int64 format enforcement~~ — হয়েছে: scout/petstore-এর হাজার হাজার ভুয়া VALID_REJECTED occurrence বাদ গেছে; label বদল নেই (`CHECKER_INT_FORMATS.md`)।
4. ~~E5 blind labelling আর E5 noise floor~~ — হয়েছে (H7, H8)। বাকি:
   - ~~codebook v0.5 মেনে blind labelling আবার করা; E005-এর সংশোধন~~ — হয়েছে (H8, v2)।
   - Attribution-পদ্ধতিতে নিয়মবদ্ধ intent-প্রমাণ খোঁজার ধাপ (test → docs → history)।
     - Tool আছে (`tools/intent_evidence.py`)।
     - Codebook §11.4 proposal (T33) supervisor-এর সিদ্ধান্তের অপেক্ষায়; 7টি প্রশ্ন খোলা।
   - ~~market-এর বিকল্প RESP_FIELD site~~ — হয়েছে (v2, 3/3; `E5_RESULTS.md` §3c)।
5. ~~দ্বিতীয় fuzzer (EvoMaster)~~ — হয়েছে (H9)। বাকি:
   - ~~Schemathesis-এর same-seed replicate দিয়ে একই trajectory বিশ্লেষণ~~ — হয়েছে। Schemathesis-এর replicate নিজেরাই অনেক সরে যায় (positional median 0.26–0.72)।
   - কোন reference উপযুক্ত, তা নির্ধারণে আরও replicate দরকার (T34 F1)।
   - market STRICT-এ 500-পথের code-level কারণ।
