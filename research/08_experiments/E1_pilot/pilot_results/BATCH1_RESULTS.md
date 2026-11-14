# Pilot Batch 1 — scout-api (2026-11-14)

**Setup:**
- SUT: scout-api (EMB, Swagger 2.0, ৪৯টি operation), administrator auth।
- Generator: Schemathesis 3.39.16, `--checks all`, প্রতি operation-এ সর্বোচ্চ ১০০টি example, shrinking বন্ধ।
- Generator input-এ recursive `$ref` কাটা (`harness/derecurse.py`)। Conformance যাচাই আসল বা mutated spec দিয়ে।
- ৩টি seed × (baseline + ৪টি fault class @ ৩০%) = **১৫টি run**। সব সম্পূর্ণ (harness exit 0)। প্রতি run প্রায় ৪০ সেকেন্ড, প্রায় ১,৪৯০টি exchange। সব run-এ ৪৯/৪৯ operation-এ পৌঁছেছে।
- কাঁচা data: `../runs/_batch1/` · সারাংশ: `batch1_attribution_summary.csv` · আগের অসম্পূর্ণ run: `../runs/_diagnostic_batch0/` (ফলাফল হিসেবে ব্যবহার করা যাবে না)।

⚠️ = অনুমান। একটি SUT ও ছোট budget — এগুলো pilot-এর পর্যবেক্ষণ, সাধারণ সিদ্ধান্ত নয়।

## 1. Baseline (মূল spec, seed 1)
- ৩০৪টি violation occurrence, **৫৩টি অনন্য fingerprint**:
  - SERVER_ERROR ৩৩
  - UNDOCUMENTED_STATUS ১৬
  - INVALID_ACCEPTED ২
  - VALID_REJECTED ১
  - UNDOCUMENTED_OPERATION ১
- তিন seed-এ fingerprint সংখ্যা ৫৩, ৫৩, ৫৪ — স্থিতিশীল।
- ⇒ Injection ছাড়াই ~৫৩টি বাস্তব অমিল আছে। এগুলোই R1-এর manual বা triage labelling-এর কাঁচামাল (সব `NEEDS_MANUAL`)।

## 2. Injected spec fault: replay বনাম fresh

| Fault | Seed | Mutated ops | Replay NEW / VANISHED | Fresh NEW / VANISHED |
|---|---|---|---|---|
| REQUEST_LOOSE | ১ / ২ / ৩ | ১২ / ১৩ / ১৪ | ০/০ · ০/০ · ০/০ | ০/০ · ০/০ · ০/০ |
| REQUEST_STRICT | ১ / ২ / ৩ | ১৪ / ১৪ / ১৪ | ২৮/০ · ২০/০ · ৪৬/০ | ২/২ · ৯/১০ · ৭/৮ |
| RESPONSE_ORACLE | ১ / ২ / ৩ | ৮ / ৭ / ৫ | ৮৬/০ · ০/০ · ০/০ | ৮৬/৪ · ০/০ · ০/০ |
| METHOD_SEM | ১ / ২ / ৩ | ৩ / ৫ / ৭ | ৩/২ · ৭/৫ · ১০/৬ | ২/২ · ২/৫ · ৪/৬ |

- **Pipeline-এর সঠিকতা:** সব NEW violation mutated operation-এই পড়েছে (১২টি analysis-এ unexplained ০)। Replay mode-এ এগুলো manifest অনুযায়ী SPEC label পেয়েছে।

## 3. পর্যবেক্ষণ
1. **REQUEST_STRICT fresh mode-এ প্রায় অদৃশ্য।**
   - Replay-এ ২০–৪৬টি নতুন violation (INVALID_ACCEPTED), fresh-এ মাত্র ২–৯টি।
   - ⚠️ কারণ: generator কঠোর spec মেনেই request বানায়, তাই spec-লঙ্ঘনকারী request আর পাঠায়ই না।
   - ⇒ Spec-নির্ভর fuzzer নিজের spec-এর অতিরিক্ত-কঠোরতা ধরতে পারে না; baseline traffic-এর replay দরকার।
2. **REQUEST_LOOSE-এর কোনো প্রভাব নেই — কিন্তু এখানে mutation দুর্বল।**
   - তিন seed-এই পাঠানো request baseline-এর সাথে হুবহু এক।
   - Edit-গুলো মূলত `format` মুছে ফেলা; scout-api-র spec-এ request constraint প্রায় নেই।
   - ⇒ এটি 2607.12101-এর “hidden degradation”-এর প্রমাণ নয়; বরং এই SUT-এ LOOSE পরীক্ষা করার মতো constraint নেই। Constraint-সমৃদ্ধ SUT দরকার।
3. **RESPONSE_ORACLE seed-নির্ভর:** seed ১-এ ৮৬টি NEW, seed ২ ও ৩-এ ০।
   - ⚠️ সম্ভাব্য কারণ: বাছাই করা operation-গুলোর response-এ body নেই বা schema মেলে। এখনো যাচাই হয়নি — পরের ধাপে manifest ও response মিলিয়ে দেখতে হবে।
4. **METHOD_SEM:** fresh run-এ 4xx বেড়েছে (seed ২: ৩৭ → ২৩৩, seed ৩: ৪৩ → ৩৩৯) — ভুল method-এ request যাওয়ার প্রত্যাশিত ফল। VANISHED ২–৬টি: মূল operation-এর বিদ্যমান অমিল ঢাকা পড়ে।

## 4. Harness-এ যা ঠিক করতে হয়েছে (threats-এ লিখতে হবে)
- mitmproxy entrypoint (`usermod` ব্যর্থ)।
- Auth: EMB-এর administrator header; spec-এ auth অনুল্লিখিত।
- Recursive schema-তে generator stall → generator input de-recurse। Mutated run-এ `specmut(derecurse(original))`, operation-set সমতা যাচাইসহ।
- SUT image একবার build (`r1-scout-sut:pilot`)।
- ⚠️ Generator input ≠ test spec — এটি একটি validity threat। Conformance সবসময় আসল বা mutated spec দিয়ে।

## 5. পরের ধাপ
1. RESPONSE_ORACLE seed ২ ও ৩-এর শূন্য ফল ব্যাখ্যা করা।
2. Baseline-এর ৫৩টি fingerprint-এ `triage.py` চালানো + source code দেখে label (scout-api open-source, তাই E-CODE-INTENT পাওয়া যাবে)।
3. Constraint-সমৃদ্ধ SUT যোগ: market, swagger-petstore, cwa-verification।
4. Code-mutation দিক (IMPL ground truth)।
5. JaCoCo coverage report (`.exec` সংগ্রহ হয়েছে, report এখনো বানানো হয়নি)।
