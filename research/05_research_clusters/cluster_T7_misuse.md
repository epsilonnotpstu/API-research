# Cluster T7 — API Misuse Detection (human- and LLM-written code)

**Primary:** P029, P030, P031 · **Secondary:** P021, P024, P028, P034, P035
⚠️ = অনুমান। [H] = hypothesis।

## 1. ID ও নাম
T7 — Client code-এ API-র ভুল ব্যবহার (misuse) শনাক্তকরণ ও সংশোধন, security API সহ।

## 2. Problem ও motivation
- API misuse crash, bug ও নিরাপত্তা ত্রুটি তৈরি করে।
- Static detector-এর precision খুব কম (P030)।
- Security API misuse ব্যাপক (P029)।
- LLM-generated code-এ নতুন ধরনের misuse দেখা দেয়, যেমন hallucination (P031)।

## 3. Core RQ
- Static detector কতটা কার্যকর, এবং কেন ব্যর্থ হয় (P030)?
- Security API misuse detection-এর অবস্থা কী (P029)?
- LLM কোন ধরনের misuse করে, এবং কীভাবে ঠিক করা যায় (P031)?

## 4. Paper
| ID | ধরন |
|---|---|
| P030 (TSE 2019) | MUBench-ভিত্তিক মূল্যায়ন — ৪টি detector |
| P029 (CSUR 2025) | ৬৯টি study-র SLR |
| P031 (TSE 2026) | LLM misuse taxonomy + Dr.Fix |

## 5. ঐতিহাসিক অবদান
- **P030:** “frequency = correctness” ধারণাকে প্রধান false-positive উৎস হিসেবে চিহ্নিত করে।

## 6. সাম্প্রতিক উন্নয়ন
- **P031:** LLM misuse।
- **Corpus-এর বাইরে (GV17):**
  - Java security API-র LLM misuse (2404.03823)।
  - AI assistant-এর security API usage (2607.11348)।
  - ⇒ এলাকাটি দ্রুত পূর্ণ হচ্ছে।

## 7. Methodology
- Pattern mining (JADET, GROUMINER, TIKANGA, DMMC)।
- Static, dynamic ও hybrid analysis (P029)।
- LLM taxonomy + prompting repair (P031)।

## 8. Tool
- MUBenchPipe (P030)।
- Dr.Fix (P031)।

## 9. Dataset
- **P030:** MUBench (১০০টি misuse)।
- **P031:** ৩,০০০ API/ভাষা, ৩৬,০০০ generation।
- **P029:** ৯টি public benchmark; এর মধ্যে মাত্র ৫টি misuse-specific (Java crypto/SSL)।

## 10. মূল্যায়ন
- Precision ও recall (empirical, conceptual, realistic) — P030।
- EM ও BLEU — P031।

## 11. প্রতিষ্ঠিত ফলাফল
- **P030:**
  - সব detector-এর precision ১২%-এর নিচে।
  - False positive-এর প্রধান কারণ valid-but-uncommon usage (৩৪.৩%)।
- **P031:**
  - Hallucination সবচেয়ে সাধারণ misuse।
  - Dr.Fix EM সর্বোচ্চ ৪০ পয়েন্ট বাড়ায়।
- **P029:**
  - Detection মূলত heuristic।
  - ML-ভিত্তিক study মাত্র ৩টি।
  - Developer-রা non-sensitive প্রসঙ্গে misuse প্রত্যাখ্যান করেন।

## 12. বিরোধ
- **P030:** frequency ভুলের প্রধান কারণ।
- **P035:** low-frequency API-তে LLM বেশি hallucinate করে।
- ⇒ “Frequency” দুই দিক থেকেই বিভ্রান্তিকর ⚠️।

## 13. লেখক-স্বীকৃত সীমাবদ্ধতা
- **P030:** Java; correct usage example-এর অভাব।
- **P031:** BLEU/EM-ভিত্তিক মূল্যায়ন।
- **P029:** Android ও Java পক্ষপাত।

## 14. বিশ্লেষণী সীমাবদ্ধতা ⚠️
- **Web/REST API client-এর misuse প্রায় অনুপস্থিত** — সবই library API।
- **P031-এ execution-validated repair নেই।**

## 15. অপর্যাপ্ত প্রমাণ
- OpenAPI-ভিত্তিক client-code misuse।
- REST client-এর misuse benchmark।

## 16. Gap
- **G8:** LLM-era security API misuse — **Weakened** (GV17)।
- REST client misuse with spec-as-oracle — Class C, লক্ষ্যভিত্তিক search হয়নি।

## 17. Technical উন্নতি
- Spec বা IDL থেকে constraint নিয়ে client code-এর static check (P016 × P030)।

## 18. নতুন approach [H]
- **OpenAPI-constrained client-code checker:** LLM-generated HTTP client-এর endpoint, parameter ও dependency-কে spec ও IDL-এর বিপরীতে যাচাই করা।
- এটি G7-এর residual-এর সাথে সম্পর্কিত। WAPIIBench ও constrained decoding-এর সাথে তুলনা আবশ্যক।

## 19. দক্ষতা ও resource
- Static analysis (Python/JS AST)।
- OpenAPI tooling।
- LLM।

## 20. ঝুঁকি
- WAPIIBench (2509.20172) ও constrained decoding (2607.05936)-এর সাথে overlap।

## 21. Baseline ও metric
- **Baseline:** WAPIIBench pipeline, P031 Dr.Fix।
- **Metric:** violation precision/recall, execution success।

## 22. নতুন গবেষকের সুযোগ
- সীমিত। আগে overlap যাচাই প্রয়োজন।

## 23. প্রমাণের মান
**উচ্চ** (corpus-এর ভেতরে)।
- কিন্তু corpus-এর বাইরের ২০২৫–২০২৬ কাজ novelty দাবি দুর্বল করে।
