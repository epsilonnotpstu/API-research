# Cluster T3 — API Security & Authorization Testing

**Primary:** P012, P013, P014, P015 · **Secondary:** P010, P029, P036, P037
⚠️ = অনুমান। [H] = hypothesis।

## 1. ID ও নাম
T3 — Web/REST API-র নিরাপত্তা ত্রুটি (mass assignment, BOLA, access policy, web-to-mobile inconsistency) শনাক্তকরণ।

## 2. Problem ও motivation
- OWASP API Top 10-এর authorization-জনিত ত্রুটি (BOLA, BFLA, mass assignment) সাধারণ fuzzer-এর 5xx oracle-এ ধরা পড়ে না।
- Security-specific oracle দরকার (P012, P014, P015)।
- Mobile client ও server validation-এর অসামঞ্জস্য বাস্তব exploit তৈরি করে (P013)।

## 3. Core RQ
- Spec ও black-box পর্যবেক্ষণ থেকে কি mass assignment শনাক্ত করা যায় (P012)?
- Log ও OpenAPI link দিয়ে কি BOLA attack ধরা যায় (P014)?
- Fuzzing-এর সময় access-policy oracle কি নতুন fault পায় (P015)?
- Mobile app থেকে কি API reconnaissance করা যায় (P013)?

## 4. Paper
| ID | পদ্ধতি |
|---|---|
| P013 (S&P 2018) | App static/dynamic analysis → request template → invalid request probing |
| P012 (ICSE 2023) | RestTestGen-এ CRUD inference, field clustering, read-only candidate → attack |
| P014 (IJIS 2025) | OpenAPI → Colored Petri Net, log replay → BOLA detection |
| P015 (ISSRE 2025) | EvoMaster extension: Not-Recognized, Leakage, Missed-Check oracle |
| Secondary | P010 (GraphQL DoS), P029 (security API misuse SLR), P036 (MCP security), P037 (OAuth2 microservice log) |

## 5. ঐতিহাসিক অবদান
- **P013:** প্রথম বৃহৎ পরিসরের mobile-to-web API inconsistency অধ্যয়ন — ১০,০০০ app।

## 6. সাম্প্রতিক উন্নয়ন
- P014 ও P015 (২০২৫)।
- **Corpus-এর বাইরে (GV05):**
  - REST security testing survey (২০২৫–২০২৬)।
  - XBOW benchmark।
  - MCP security benchmark (GV01): MCPSecBench, MCPTox ইত্যাদি।

## 7. Methodology
- Black-box inference (P012)।
- Formal model ও runtime log (P014)।
- Search-based fuzzing + oracle (P015)।
- Program analysis + probing (P013)।

## 8. Tool
- RestTestGen extension (P012)।
- Links2CPN (P014)।
- EvoMaster security oracle (P015)।

## 9. Dataset ও benchmark
- **P012:** ৫টি open-source API (VAmPI, OWASP, Toggle, Bookstore, CRUD; ৪৭ operation) — existing + seeded vulnerability; scalability-র জন্য ১০টি Google spec।
- **P014:** OWASP Juice Shop (২টি BOLA), ১৫ ছাত্রের CTF (~২,০০০ request), Memos (BOLA fix revert করা)।
- **P015:** ৩টি artificial API (injected fault); capital, crAPI, WebGoat; ১০টি authenticated EMB API (৭৯২ endpoint)।
- **P013:** ১০,০০০ Google Play app (AndroZoo) — app তালিকা অপ্রকাশিত।

## 10. মূল্যায়ন
- **Precision/recall/F1:** P012, P014।
- **Distinct fault গণনা:** P015।
- **Verified exploit:** P013।
- কোনো paper-এ বৃহৎ real-world ground truth নেই ⚠️।

## 11. প্রতিষ্ঠিত ফলাফল
- **P012:**
  - CRUD inference ৯৮%।
  - Zero false positive।
- **P014:**
  - Attempt-স্তরে সব attack ধরা পড়ে।
  - Successful-attack স্তরে V2 precision ০.২২।
  - OpenAPI links ১,৯৫৫টির মধ্যে মাত্র ৯টি spec-এ।
- **P015:**
  - ২৭টি নতুন fault।
  - Existing oracle ৮১২টি 500 ও ১২,৪১৩টি schema fault রিপোর্ট করে, যার severity প্রশ্নসাপেক্ষ।
  - Real API-তে Missed-Check fault নেই।
- **P013:**
  - ৮৮.৪% invalid request গৃহীত।
  - বাস্তব exploit (zero-dollar checkout, SQLi)।

## 12. বিরোধ
- কোনো paper সরাসরি অন্যটির বিরোধিতা করে না।
- কিন্তু **P015-এর real-world ফল** (Missed-Check নেই) seeded benchmark-ভিত্তিক সাফল্যের সাধারণীকরণ প্রশ্নবিদ্ধ করে ⚠️।

## 13. লেখক-স্বীকৃত সীমাবদ্ধতা
- **P012:** spec দরকার; heuristic clustering।
- **P014:** OpenAPI link দরকার; successful-attack স্তরে precision কম।
- **P015:** ownership অনুমান।
- **P013:** obfuscation ও WebView।

## 14. বিশ্লেষণী সীমাবদ্ধতা ⚠️
- Benchmark seeded বা vulnerable-by-design।
- P015 self-evaluation।
- P013 পুনরুৎপাদন অসম্ভব (data অপ্রকাশিত)।
- Multi-role বা multi-tenant authorization modelling দুর্বল।

## 15. অপর্যাপ্ত প্রমাণ
- Real CVE-ভিত্তিক REST benchmark।
- Production false-positive হার।
- MCP বা agent-mediated API authorization।

## 16. Gap
- **G5:** real REST security benchmark (Class A+B, Supported)।
- **G3:** MCP/REST-wrapper authorization testing।
  - Broad MCP security: Partially weakened।
  - Narrowed version: Class C।
- **G13:** log-ভিত্তিক security anomaly dataset (Class C)।

## 17. Technical উন্নতি
- Ownership tracking।
- OpenAPI link/dependency inference (T4) দিয়ে P014-এর পূর্বশর্ত পূরণ।
- Role-aware unified oracle (BOLA + BFLA + mass assignment)।

## 18. নতুন approach [H]
- **P015-এর access-policy oracle-কে MCP tool layer-এ প্রয়োগ** — agent-এর মাধ্যমে wrapped REST endpoint-এ privilege violation (P032 × P036 × P015)।

## 19. দক্ষতা ও resource
- OWASP API Top 10-এর জ্ঞান।
- Docker-এ vulnerable SUT (VAmPI, crAPI, Juice Shop)।
- EvoMaster বা RestTestGen।
- নৈতিক disclosure প্রক্রিয়া।

## 20. ঝুঁকি
- Real vulnerability-র জন্য নৈতিক ও আইনি সীমা।
- Ground truth তৈরি ব্যয়বহুল।
- MCP security এলাকা দ্রুত ভিড় জমাচ্ছে।

## 21. Baseline ও metric
- **Baseline:** P012/P015 tool, Schemathesis-এর security check, mcp-scan।
- **Metric:** precision, recall, distinct verified vulnerability, FP per hour।

## 22. নতুন গবেষকের সুযোগ
- Narrowed G3 (মাঝারি)।
- G5-এর ছোট সংস্করণ — একটি নির্দিষ্ট vulnerability class-এর curated CVE set।

## 23. প্রমাণের মান
**মাঝারি-উচ্চ।**
- চারটি peer-reviewed paper।
- কিন্তু সবই seeded বা ক্ষুদ্র benchmark।
- P013 আংশিক পাঠ (Medium confidence, scrambled layout)।
