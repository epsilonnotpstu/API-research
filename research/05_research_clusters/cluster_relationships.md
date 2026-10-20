# Cluster Relationships — PHASE D

**ভিত্তি:**
- Primary/secondary সদস্যপদ (`final_paper_cluster_table.md`-এর membership matrix)।
- প্রতিটি analysis-এর §O (Relationships)।
⚠️ = অনুমান। [H] = hypothesis।

## 1. Secondary-membership থেকে সংযোগের ঘনত্ব

**গণনার নিয়ম:** একটি paper-এর primary X ও secondary Y হলে X→Y একটি সংযোগ ধরা হয়েছে।

| থেকে \ প্রতি | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 |
|---|---|---|---|---|---|---|---|---|---|
| **T1** (P001–P008) | — | | | 4 | | 2 | | 2 | |
| **T2** (P009–P011) | 1 | — | 1 | | | 1 | | | 1 |
| **T3** (P012–P015) | 2 | | — | 3 | | | | | 1 |
| **T4** (P016–P019) | 2 | | | — | | 3 | | 1 | |
| **T5** (P020–P025) | 1 | | | | — | 2 | 2 | 2 | 1 |
| **T6** (P026–P028) | | | | 1 | | — | 1 | | |
| **T7** (P029–P031) | | | 1 | | 2 | 1 | — | 1 | |
| **T8** (P032–P036) | 1 | | 1 | 1 | 2 | 2 | 2 | — | 1 |
| **T9** (P037–P038) | 2 | | 1 | | | | | | — |

**পাঠ:**
- **T1↔T4** সবচেয়ে ঘন সংযোগ (৪+২)।
- **T6** সবচেয়ে বেশি paper-এর secondary (১১)। অর্থাৎ documentation ও spec-এর মান একটি **cross-cutting concern**।
- **T8** সবচেয়ে বেশি cluster-এর সাথে যুক্ত (৭টি)। LLM consumer হিসেবে T8 integration hub।
- **T2** প্রায় বিচ্ছিন্ন — অন্য কোনো cluster-এর paper T2-কে secondary নেয় না।

## 2. প্রধান সম্পর্ক (প্রমাণসহ)

| সম্পর্ক | ধরন | প্রমাণ |
|---|---|---|
| T4 → T1 | **Enabler:** spec/dependency inference fuzzing-এর input উন্নত করে | P003, P004 (underspecified spec coverage আটকায়); P016 (IDL → RESTest); P005 (IPD); P018/P019 (missed element) |
| T1 → T3 | **Infrastructure reuse:** fuzzing framework-এ security oracle | P012 (RestTestGen), P015 (EvoMaster) |
| T4/T6 → T8 | **Quality propagation:** spec/doc ত্রুটি agent ব্যর্থতা ঘটায় | P032 (spec defect → tool failure), P035 (spec key element) ⚠️ কার্যকারণ নিয়ন্ত্রিতভাবে প্রমাণিত নয় |
| T5 → T8 | **Consumer breakage:** API পরিবর্তন LLM-কে ভাঙে | P022, P024, P034 (documentation change) |
| T7 ↔ T8 | **Shared phenomenon:** hallucination একই সাথে misuse ও tool error | P031, P034, P035 |
| T1 ↔ T5 | **Technique reuse:** differential testing ও invariant | P025 (RESTler → regression), P008 (invariant → cross-version oracle) [H] |
| T6 → T5 | **Documentation of change:** deprecation বা changelog-এর মান | P020 (event-driven documented নয়), P024 (context-নির্ভর) |
| T3 ↔ T8 | **New attack surface:** MCP | P036, P032 (auth বাদ) |
| T9 ↔ T1/T3 | **Observability as oracle** [H] | P037, P014 |
| T2 ↔ T1 | **Paradigm transfer** | P011 (EvoMaster RPC); P009 |

## 3. সম্পর্ক-চিত্র (text)

```
                 T6 Docs/design ─────────────┐ (cross-cutting quality)
                   │                         │
   T4 Spec inference ──enables──▶ T1 REST testing ──reuse──▶ T3 Security
         │                          │   │                      │
         │ quality                  │   └──differential──▶ T5 Evolution
         ▼                          │                          │ breaks
   T8 LLM tools/MCP ◀── consumer ───┘                          ▼
         │  ▲                                              (LLM consumers)
         │  └──── hallucination ──── T7 Misuse
         └──── new surface ──── T3
   T9 Microservices ── observability oracle [H] ── T1/T3
   T2 GraphQL/RPC ── paradigm transfer ── T1  (দুর্বল সংযোগ)
```

## 4. আন্তঃ-cluster gap (সেতু-সুযোগ)

| সেতু | Gap | মন্তব্য |
|---|---|---|
| T4 × T1 | G9 | Inferred spec → fuzzing; সবচেয়ে feasible |
| T1 × T4 × T6 | G14 | Runtime triage + spec repair |
| T5 × T1 | G1/G2 | Behavioural breaking change |
| T4/T6 × T8 | G4 | Spec-quality → agent |
| T3 × T8 | G3 (narrowed) | MCP authorization |
| T9 × T1 | G13 | Log oracle |

**পর্যবেক্ষণ:** শক্তিশালী gap-গুলো প্রায় সবই **cluster-সীমানায়** অবস্থিত। এটি সেতুবন্ধনমূলক গবেষণার সুযোগ নির্দেশ করে।
- ⚠️ এটি একটি পর্যবেক্ষণ, প্রমাণ নয়।
- Corpus নির্বাচনই এই চিত্র প্রভাবিত করতে পারে।
