# R1 "Spec or Bug?": findings-এর সমন্বিত সারাংশ (2026-11-16)

**উদ্দেশ্য:** এ পর্যন্ত যত দাবি এসেছে, সেগুলো এক জায়গায় রাখা। প্রতিটি দাবির পাশে আছে তার প্রমাণ, প্রমাণের শক্তি, আর কোথায় খুঁটিনাটি পাওয়া যাবে। Paper লেখার কাঠামো হিসেবেও এটা কাজে লাগবে। বিস্তারিত সংখ্যা আছে `E1_pilot/pilot_results/PILOT_SUMMARY.md`-এর H1–H12-এ।

**প্রমাণের শক্তির চিহ্ন:**
- **C** = pre-registered confirmatory।
- **P** = pilot বা descriptive (pre-registered নয়, অথবা ছোট n)।
- **X** = post-hoc বা exploratory।

## RQ1: অমিল কতটা ধরা পড়ে, আর কোন পক্ষের দোষ বলা যায় কি?
| দাবি | শক্তি | মূল সংখ্যা | উৎস |
|---|---|---|---|
| Positive-only fuzzing-এ spec-ত্রুটি প্রায়ই অদৃশ্য থাকে; replay বা negative data দিলে দেখা যায়, তবে noise-সহ | P | Fresh-এ mutated-op-এর সংকেত noise ছাড়ায় 34/61 run-এ (কোন kind আশা করা হচ্ছে, সেই filter দিয়ে); REQUEST_LOOSE-এ মাত্র 6/25 | H1, `NOISE_FLOOR_SPEC.md` |
| একক পক্ষকে দোষ দেওয়া যথেষ্ট নয় | P | Baseline অমিলের 27%-এ spec আর code দুটোই বদলাতে হয় (BOTH, 30/112) | H2 |
| Oracle নিজেই উল্লেখযোগ্য ত্রুটির উৎস | P | Baseline-এর 16% TEST (26/161) | H6 |
| Code fault fresh fuzzing-এ ধরা পড়ে | P | Mutant-এর জোড়া seed-এ noise ছাড়ায় 25/31 | H7 |
| দুই fuzzer-এ fault class-এর pattern একই | P | Controlled ঘরে EvoMaster 20/26, Schemathesis 19/26 | H9 |

## RQ2: Triage, অর্থাৎ কোন পক্ষ সারাতে হবে?
| দাবি | শক্তি | মূল সংখ্যা | উৎস |
|---|---|---|---|
| Intent-evidence codebook নিরাপদ, কিন্তু coverage কম | C | E5 v3-এ misattribution 0/0; স্বাধীন প্রমাণ না থাকলে UNDECIDABLE | H8 |
| Zero-shot LLM codebook-এর চেয়ে ভালো (কৃত্রিম fault) | C | macro-F1: M1 0.94, M2 0.66–0.70 | H10, `E4_RESULTS.md` |
| একই ফল আসল developer fix-এও | C | macro-F1: M1 0.86–0.88, M2 0.70–0.72; codebook-এর "বেশি নিরাপদ" দাবি FAIL | H11, `E6_RESULTS.md` |
| **Divergence-এর ধরন repair direction আগাম বলে** | **C** | E7: deliberate → SPEC 26/33, accidental → 0/11 (p < 1e-4)। E8b pooled, direction-blind proposition: 39/48 বনাম 0/10 (p = 1.8e-6) | H12, `E7_RESULTS.md`, `E8_RESULTS.md` |
| Generic contract-এ SPEC repair বেশি | C (secondary) | Generic 15/18, specific 11/26 (p = 0.007) | `E7_RESULTS.md` |
| Blind reader accidental অমিল বেশি miss করে | X → **টেকেনি** | E8-এ post-hoc দাবি; pre-registered E8b-তে p = 0.31 | `E8_RESULTS.md` |
| Kind rule (accidental → IMPL override) zero-shot LLM-কে উন্নত করে না | C (INSUFFICIENT) | E9 Part B: ৮৫টি item-এ discordant ১; M1 accidental 24/24, 23/24 ঠিক; override precision 24/24 | `E9_hybrid/E9_RESULTS.md` |
| Zero-shot LLM-এর ভুল deliberate item-এ কেন্দ্রীভূত, মূলত SPEC-truth item-এ abstention | P (pre-registered descriptive) | E6: deliberate 7/10; E9 Part B: deliberate 47/61, যার ১২টি UNDECIDABLE-SPEC | `E9_hybrid/E9_RESULTS.md` |
| M1 abstain করলে R ব্যবহার → macro-F1 0.976 | ✗ (replicate হয়নি) | E9 Part B post-hoc; দুই labeller-এ একই; E10-এ pre-registered FB 0.65–0.70, forced choice-এর কাছে হেরেছে | `E9_hybrid/E9_RESULTS.md` |
| Kind × direction সম্পর্ক সম্পূর্ণ নতুন, আলাদা sample-এ replicate করে | P | E10 H-E10-3: 19/24 বনাম 2/13, p = 2.7e-4; cluster ধরে 7/11 বনাম 1/9, p = 0.025। প্রথমবার accidental → SPEC (২টি, একই fix থেকে) | `E10_fallback/E10_RESULTS.md` |
| Kind coding coder-এর model family-র ওপর নির্ভর করে না | P | E11: Claude coder 67/81 বনাম 1/39 (cluster ধরে 38/51 বনাম 1/30); GPT আর Claude-এর মধ্যে κ 0.96। ⚠️ দুই পরিবারই একই miner-এর লেখা পড়েছে | `E11_crossfamily/E11_RESULTS.md` |
| Zero-shot LLM triage-এর accuracy sample-ভেদে স্থিতিশীল নয় | X (descriptive) | M1 macro-F1: E9-এ 0.90, E10-এ 0.58–0.64; এর মূল কারণ এক repo-র ২টি fix থেকে আসা ১০টি item | `E10_fallback/E10_RESULTS.md` |

## Paper-এর সম্ভাব্য মূল বক্তব্য (এখনকার অবস্থা)
1. **ক্লাসিক অনুমান উল্টে দেখা যায়।** স্বাভাবিক ধারণা হলো, spec আর code মিলছে না মানেই code-এ bug। কিন্তু developer-রা প্রায়ই spec সারায়। E6-এ সেটা ৮/১৮, E7-এর নতুন set-এ ২৬/৪৫।
2. **কোন পক্ষ সারাতে হবে, তা অনেকটাই আগাম বলা যায়।**
   - অমিলের আচরণটা যদি কোনো ভুল বা বাদ পড়ার পার্শ্বপ্রতিক্রিয়া হয় (accidental), তাহলে code সারানো হয়।
   - Code যদি ইচ্ছাকৃত সিদ্ধান্তে আলাদা আচরণ করে (deliberate), তাহলে বেশিরভাগ ক্ষেত্রে spec সারানো হয়।
   - এটা দুটো স্বাধীন sample-এ, direction না জানা লেখকের proposition দিয়েও টিকেছে।
3. **Zero-shot LLM ইতিমধ্যে এই সংকেত ভালো ধরে।** একটা explicit codebook procedure যোগ করলে উন্নতি হয় না, বরং coverage কমে।
4. **Kind rule LLM-এর সাফল্য ব্যাখ্যা করে, কিন্তু override হিসেবে উন্নতি আনে না** (E9 INSUFFICIENT)।
   - LLM accidental item আগেই ঠিক বলে।
   - তার দুর্বলতা deliberate item-এ abstention। ঠিক সেখানে rule "SPEC" বলে, আর প্রায় ৫ বারে ৪ বার ঠিক হয়।
   - **খোলা প্রশ্ন (E10):** "LLM, আর LLM abstain করলে rule" pipeline কি নতুন item-এও টেকে?

## সব দাবির ক্ষেত্রে প্রযোজ্য সীমাবদ্ধতা
- **কোনো মানুষ coder নেই।** সব coder, labeller আর judge একই LLM family-র। κ উঁচু, তবে এটা একই model-এর ভেতরের সামঞ্জস্য।
  - **Paper-এর আগে একটা human spot-check দরকার।** আমাদের protocol-এ inspector হলেন user। যেমন E7/E8b থেকে ১৫–২০টি item-এর kind code (deliberate/accidental) আপনি যাচাই করবেন, item-এর direction না দেখে।
- **Corpus সীমিত।** শুধু Java/Kotlin/Go OSS REST project। নেওয়া হয়েছে কেবল যেসব commit message-এ correction-এর ইঙ্গিত আছে।
- **Accidental arm ছোট (n = ১০–১১)।** তাই odds ratio-র CI খুব চওড়া। Effect-এর দিক নিশ্চিত, আকার নয়।
- **Forking path:** একাধিক amendment আছে (E7 A1–A3, E8 B1)। সবগুলো আগে থেকে hash করে commit করা, আর পরে নেওয়া সিদ্ধান্তগুলো খোলাখুলি লেখা।

## পরের কাজ
1. E9 Part B: সম্পন্ন (INSUFFICIENT)। E10: সম্পন্ন। Fallback-এর সুবিধা দেখা যায়নি, তবে kind-এর ফল আবার replicate হয়েছে। পরের ধাপ: মানুষের validation আর অন্য পরিবারের মডেল।
2. Human spot-check sheet: আমি তৈরি করব, আপনি সময়মতো যাচাই করবেন।
3. Paper-এর খসড়া v0.1: `10_paper/R1_draft.md`।
