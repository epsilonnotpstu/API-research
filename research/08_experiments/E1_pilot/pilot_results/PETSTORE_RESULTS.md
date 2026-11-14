# Swagger-petstore pilot batch — ফলাফল (2026-11-14, Claude)

**Harness:** `harness_v2` (Codex T14) — এই SUT-এ প্রথম runtime ব্যবহার।
**Batch:** `runs/swagger-petstore/batches/20261114T021748Z_batch_1701236/runs.tsv`।
**Settings:** Batch 2-এর মতো — `SCHEMA_CHECKS=response_headers_conformance`, budget 300 s, max examples 100, severity 30%, seeds 1–3, auth নেই।
**Summary CSV:** `petstore_attribution_summary.csv`।

## 1. Run-এর অবস্থা
- 15/15 run complete: harness exit 0, Schemathesis exit 1 (test failure = স্বাভাবিক), JaCoCo dump OK, 15টি analysis।
- Smoke run (s1, আলাদা): 19/19 operation, 1,458 exchange। Status: 500 → 613, 200 → 338, 400 → 302, 404 → 205।
- Spec: OpenAPI 3.0.4, 19টি operation, base `/api/v3`। T14-এর খোলা প্রশ্ন (`/api/v3` routing) runtime-এ নিষ্পত্তি হয়েছে — সঠিক।

## 2. Baseline
| মাপ | মান |
|---|---|
| Distinct fingerprint (s1/s2/s3) | 43 / 46 / 45 |
| Union / তিন seed-এই উপস্থিত | 49 / 40 → seed-নির্দিষ্ট 9 (≈18%) |

s1-এর kind ভাগ: VALID_REJECTED 400 ×13, SERVER_ERROR ×8, REQUEST_UNCHECKABLE ×16, RESPONSE_SCHEMA ×4 (যেমন `PUT /pet` 200-এ required `photoUrls` অনুপস্থিত), RESPONSE_PARSE ×1, UNDOCUMENTED_OPERATION ×1 (Schemathesis probe)।

⚠️ **REQUEST_UNCHECKABLE (16):** spec `application/xml` ও `application/x-www-form-urlencoded` body গ্রহণ করে; `conformance.py` শুধু JSON validate করে। এগুলো checker-এর coverage সীমা (TEST শ্রেণি)। VALID_REJECTED এসব exchange বাদ দেয়, তাই false VALID_REJECTED তৈরি হয় না।

## 3. Fault injection
| Fault | Ops mutated | Replay NEW (s1/s2/s3) | Replay label match | Fresh NEW | Fresh unexplained (NEW+VANISHED) |
|---|---|---|---|---|---|
| REQUEST_LOOSE | 4/5/4 | 0/0/0 | — | 2/3/2 | 0/1/0 |
| REQUEST_STRICT | 4/5/5 | 11/6/30 | 47/47 | 6/0/23 | 0/0/6 |
| RESPONSE_ORACLE | 2/5/4 | 4/12/5 | 21/21 | 4/12/5 | 0/0/0 |
| METHOD_SEM | 4/3/3 | 10/7/7 (VANISHED 12/8/10) | 24/24 | 4/1/3 | 1/0/0 |

- Fresh mode-এ label দেওয়া হয় না (NEEDS_MANUAL), তাই সেখানে label match প্রযোজ্য নয়।

## 4. scout-api (Batch 2)-এর সাথে তুলনা
1. **RESPONSE_ORACLE এখন তিন seed-এই দেখা যায়** (scout: 90/0/0)। Petstore-এ বেশি operation body-সহ 2xx দেয় (baseline-এ ১৯-এর ১৩টি; scout-এ ৪৯-এর ২২টি, যার প্রায় সব GET)। এতে আগের ব্যাখ্যা সমর্থিত: oracle mutation কেবল 2xx body-তে কাজ করে। প্রতিকার: specmut-এ eligible-operation pool (নিচে §5)।
2. **REQUEST_STRICT fresh mode-এ আংশিক দেখা যায়** (6/0/23; scout-এ 0/2/0)। ⚠️ [H] Petstore spec-এ constraint বেশি (যেমন header `api_key` `maxLength`), তাই কঠোর করা spec থেকে generator সত্যিই ভিন্ন traffic তৈরি করে। তবু replay > fresh, আর seed 2-তে fresh ০ — "replay ছাড়া spec-কঠোরতা প্রায়ই অদৃশ্য" পর্যবেক্ষণ দুই SUT-এই টিকে আছে।
3. **REQUEST_LOOSE replay-এ ০ (দুই SUT-এই)।** Spec শিথিল করলে পুরোনো traffic-এ নতুন violation হয় না — এটা প্রত্যাশিত, কারণ শিথিলতা কেবল আগের violation সরাতে পারে। এখানে baseline-এ সংশ্লিষ্ট violation ছিল না। Fresh-এ 2–3টি নতুন RESPONSE_SCHEMA দেখা গেছে। ⚠️ [H] শিথিল spec-এ generator নতুন input পাঠায়, যা 2xx পায় কিন্তু response schema ভাঙে।
4. **Fresh mode-এ unexplained এই প্রথম > 0** (মোট 8; scout-এ 0)। Baseline-এর seed-নির্দিষ্টতা (~18%) দেখায় fresh-এর পার্থক্যের একটা অংশ শুধু nondeterminism। Fresh ফল তাই repeated baseline-এর সাথে তুলনা করে পড়তে হবে।

## 5. পরের ধাপ
- specmut `--only-ops`: RESPONSE_ORACLE-এর জন্য baseline-এ body-সহ 2xx পাওয়া operation-এর pool (helper `tools/eligible_ops.py`)।
- Petstore baseline-এর code-ভিত্তিক labelling (labeller A/B), scout-এর মতো।
- Market batch।
- সীমা: একটি fuzzer, budget 300 s, seed 3টি; petstore একটি demo SUT (সম্ভবত ইচ্ছাকৃত ত্রুটিসহ)।
