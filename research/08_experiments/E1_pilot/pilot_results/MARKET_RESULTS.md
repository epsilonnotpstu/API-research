# Market pilot batch — ফলাফল ও তিন SUT-এর তুলনা (2026-11-14, Claude)

**Batch:** `runs/market/batches/20261114T023303Z_batch_1724645/runs.tsv`।
**Harness:** `harness_v2`। Settings অন্য দুই SUT-এর মতো: `SCHEMA_CHECKS=response_headers_conformance`, 300 s, max examples 100, severity 30%, seeds 1–3।
**Auth:** EMB fixture, role `user`।
**Summary CSV:** `market_attribution_summary.csv`।

## 1. Run-এর অবস্থা
- 15/15 run complete, 15টি analysis সম্পন্ন।
- Exchange সংখ্যা: বেশিরভাগ run-এ 1,202; REQUEST_STRICT s1-এ 1,002 ও s3-এ 1,102।
- Smoke run (s1): 13/13 operation। Schemathesis একটি run প্রায় 32 s-এ শেষ করে, অর্থাৎ budget যথেষ্ট।
- Spec: Swagger 2.0, 13টি operation। প্রতিটিতে status স্পষ্টভাবে ঘোষিত (200/201/204/401/403/404)।

## 2. Baseline
- Distinct fingerprint: s1/s2/s3 = 13/15/15; union 15; তিন seed-এই উপস্থিত 13।
- s1-এর ভাগ:

| Kind | Status | n | পর্যবেক্ষণ |
|---|---|---|---|
| UNDOCUMENTED_STATUS | 406 | 4 | validation ব্যর্থ হলে body `"Argument validation error"` (`PUT /customer/cart`, `POST /customer/cart/pay`, `PUT /customer/contacts`, `POST /register`) |
| SERVER_ERROR (+ একই exchange-এর UNDOCUMENTED_STATUS রূপ) | 500 | 4 + 4 | ভুল JSON-এ `"JSON parse error"`; সীমার বাইরের int; `orderId` string → long রূপান্তর ব্যর্থ |
| UNDOCUMENTED_OPERATION | 400 | 1 | Schemathesis probe |

⚠️ [H] **406 প্রথম দৃষ্টিতে IMPL।** HTTP-তে 406 মানে Accept/content negotiation ব্যর্থ, input validation নয় (তখন 400/422 প্রত্যাশিত)। কিন্তু সেটা নিশ্চিত হবে code-এর exception handler দেখার পর। এটা BOTH-এর প্রার্থীও: spec-এ 400 নেই, আর code ভুল status দেয়।

## 3. Fault injection
| Fault | Ops mutated | Replay NEW | Replay label match | Fresh NEW | Fresh VANISHED | Unexplained |
|---|---|---|---|---|---|---|
| REQUEST_LOOSE | 3/1/2 | 0/0/0 | — | 0/0/2 | 0/0/0 | 0 |
| REQUEST_STRICT | 3/4/4 | 0/2/10 | 12/12 | 2/0/0 | 4/1/3 | 0 |
| RESPONSE_ORACLE | 4/4/4 | 8/5/10 | 23/23 | 8/5/10 | 0 | 0 |
| METHOD_SEM | 3/4/4 | 3/7/6 (VANISHED 0/7/3) | 16/16 | 3/4/4 | 0/7/3 | 0 |

- Fresh mode-এ label দেওয়া হয় না (NEEDS_MANUAL)।
- REQUEST_STRICT fresh-এ নতুন violation প্রায় নেই, বরং পুরোনো violation **হারিয়ে যায়** (VANISHED 4/1/3)। ⚠️ [H] কঠোর spec থেকে generator কম "খারাপ" input পাঠায়, তাই যে implementation-ত্রুটি আগে ধরা পড়ত সেগুলো আর দেখা যায় না। অর্থাৎ spec-ত্রুটি IMPL-ত্রুটিকেও আড়াল করে।

## 4. তিন SUT-এর তুলনা (seed 1/2/3)
| | scout-api (Batch 2) | swagger-petstore | market |
|---|---|---|---|
| Operation | 49 | 19 | 13 |
| Baseline fingerprint (s1) | 99 | 43 | 13 |
| REQUEST_STRICT replay NEW | 28/20/61 | 11/6/30 | 0/2/10 |
| REQUEST_STRICT fresh NEW | 0/2/0 | 6/0/23 | 2/0/0 |
| RESPONSE_ORACLE replay NEW | 90/0/0 | 4/12/5 | 8/5/10 |
| REQUEST_LOOSE replay NEW | 0/0/0 | 0/0/0 | 0/0/0 |
| Replay label match | সব | 92/92 | 51/51 |
| Fresh unexplained (মোট) | 0 | 8 | 0 |

### যা তিন SUT-এই টিকে আছে
1. **Replay mode-এ injected fault-এর label 100% সঠিক** — তবে এটা নকশাগত: manifest-এর operation-এ নতুন violation-কে manifest-এর label দেওয়া হয়। Attribution-এর আসল পরীক্ষা হলো fresh mode ও বাস্তব (non-injected) violation।
2. **REQUEST_STRICT: replay ≫ fresh** (একটি ব্যতিক্রম: petstore s3)। কঠোর spec-এর ত্রুটি fuzzing traffic-এ প্রায়ই অদৃশ্য — R1-এর জন্য মূল empirical দাবির প্রার্থী।
3. **REQUEST_LOOSE replay-এ সর্বদা 0।** কারণটা কাঠামোগত: spec শিথিল হলে পুরোনো traffic-এ নতুন violation হতে পারে না। এই fault class মূল্যায়নের metric হওয়া উচিত VANISHED (baseline-এর violation লুকানো), NEW নয়। ⚠️ পরের batch-এর আগে metric সংশোধন প্রস্তাব।
4. **RESPONSE_ORACLE scout-এ seed-নির্ভর, অন্য দুটিতে স্থিতিশীল।** কারণ scout-এর 2xx-body operation কম। `ORACLE_POOL=baseline` দিয়ে scout পুনরায় চালানো পরের ধাপ।

### সীমা
- একটি fuzzer (Schemathesis 3.39.16), budget 300 s, seed 3টি, severity একটিই।
- তিনটিই Java SUT।
- Petstore একটি demo application।
