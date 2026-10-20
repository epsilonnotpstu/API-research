# Cluster T6 — API Documentation, Design Rules & Governance

**Primary:** P026, P027, P028 · **Secondary:** P001, P008, P009, P016, P018, P019, P020, P025, P030, P032, P035
⚠️ = অনুমান। [H] = hypothesis।

## 1. ID ও নাম
T6 — API design rule, documentation-এর মান এবং তাদের consumer-প্রভাব।
- Consumer-এর মধ্যে মানুষ ও (secondary প্রমাণে) LLM দুটোই আছে।

## 2. Problem ও motivation
- খারাপ design ও documentation বোঝাপড়া কমায় (P026) এবং productivity কমায় (P028)।
- বড় পরিসরে এমন ত্রুটি স্বয়ংক্রিয়ভাবে শনাক্ত করা দরকার (P027, P028)।

## 3. Core RQ
- Design rule-এর লঙ্ঘন কি বোঝাপড়া কমায় (P026)?
- লঙ্ঘন কি নির্ভুলভাবে শনাক্ত করা যায় (P027)?
- Documentation smell কি শনাক্তযোগ্য, এবং developer-রা কি সেগুলোকে গুরুত্ব দেন (P028)?

## 4. Paper
| ID | ধরন |
|---|---|
| P026 (EMSE 2023) | Controlled experiment, ১০৫ জন অংশগ্রহণকারী |
| P027 (ICSA 2024) | RESTRuler tool, ২,৩৩১টি APIs.guru spec |
| P028 (SANER 2021) | ৫টি documentation smell, BERT classifier, survey |

## 5. ঐতিহাসিক অবদান
- **P028:** API documentation smell-এর catalog।

## 6. সাম্প্রতিক উন্নয়ন
- **P027:** বড় পরিসরে design-rule linting।
- **Secondary প্রমাণ:**
  - P032 ও P035 দেখায় spec/documentation-এর মান LLM agent ও code-LLM-কে প্রভাবিত করে।
  - Corpus-এর বাইরে (GV03): agent-ready OpenAPI documentation (2605.14312) ও SilentProbe।

## 7. Methodology
- Controlled experiment (P026)।
- Rule-based static analysis (P027)।
- ML classification + survey (P028)।

## 8. Tool
- RESTRuler (P027), Zally (baseline)।
- BERT smell detector (P028)।

## 9. Dataset
- **P027:** ২,৩৩১টি spec; ১,৫৯৬টি manual violation check; ১১১টি expert-crafted violation।
- **P028:** ১,০০০টি Java SE documentation unit।
- **P026:** ১০৫ জন অংশগ্রহণকারীর data (Zenodo)।

## 10. মূল্যায়ন
- **P026:** correctness, সময়, perceived difficulty, effect size।
- **P027:** precision/recall।
- **P028:** classifier F1।

## 11. প্রতিষ্ঠিত ফলাফল
- **P026:**
  - ১২টির মধ্যে ১১টি rule-এর লঙ্ঘন বোঝাপড়া কমায় (d ০.২৪–২.১৭)।
  - Perceived difficulty প্রকৃত ভুলের সাথে প্রায়ই মেলে না।
  - অভিজ্ঞতা লঙ্ঘনের প্রভাব থেকে রক্ষা করে না।
- **P027:**
  - ১,৬৯,০৬১টি violation।
  - Precision ৯১.২%, recall ৬৭.৬%।
- **P028:**
  - ৭৮% unit-এ smell।
  - BERT-এর F1 ০.৭৫–০.৯৭।
  - ৯৫.২% developer productivity হ্রাসের কথা জানিয়েছেন।

## 12. বিরোধ
- **P026:** perceived ও actual difficulty-র অমিল।
  - ⇒ P028-এর survey-ভিত্তিক severity-র সীমা ⚠️।
- **PathHierarchy3 লঙ্ঘন** বরং ভালো ফল দিয়েছে (P026) — অর্থাৎ সব rule সমান গুরুত্বপূর্ণ নয়।

## 13. লেখক-স্বীকৃত সীমাবদ্ধতা
- **P026:** প্রতি rule-এ একটি stimulus।
- **P027:** syntactic rule; বড় ফাইলে RAM সমস্যা।
- **P028:** কেবল Java SE; ৫টি smell।

## 14. বিশ্লেষণী সীমাবদ্ধতা ⚠️
- **LLM consumer-এর উপর** design বা documentation লঙ্ঘনের প্রভাব সরাসরি পরীক্ষিত নয়।
- **REST/OpenAPI documentation smell catalog নেই** — P028 Java-কেন্দ্রিক।

## 15. অপর্যাপ্ত প্রমাণ
- Design বা documentation-এর মান → testing, security বা agent ফলাফলের কার্যকারণ সম্পর্ক।

## 16. Gap
- **G4:** spec/documentation-এর মান → agent reliability (Class B/C, Partially weakened)।
- REST documentation smell (Class C) — লক্ষ্যভিত্তিক search হয়নি।

## 17. Technical উন্নতি
- P026-এর effect size দিয়ে rule severity weighting।
- LLM-assisted semantic rule check।

## 18. নতুন approach [H]
- **P026-এর experiment-এর পুনরাবৃত্তি LLM-as-consumer দিয়ে:**
  - একই rule-লঙ্ঘিত বনাম অনুগত spec।
  - LLM-এর tool-call সঠিকতা পরিমাপ।
- এটি মানুষ ও LLM-এর তুলনা (G4-এর সাশ্রয়ী সংস্করণ)।

## 19. দক্ষতা ও resource
- APIs.guru, RESTRuler।
- LLM API।
- Experiment design ও statistics।

## 20. ঝুঁকি
- Synthetic stimulus-এর বাস্তবতা।
- LLM-এর memorization (জনপ্রিয় API)।

## 21. Baseline ও metric
- **Baseline:** অনুগত spec।
- **Metric:** tool-call validity, task success, effect size।

## 22. নতুন গবেষকের সুযোগ
- উপরের LLM-replication — কম খরচ, স্পষ্ট নকশা।

## 23. প্রমাণের মান
**মাঝারি-উচ্চ।**
- তিনটি শক্তিশালী paper।
- LLM-সংযোগের প্রমাণ কেবল secondary (P032 preprint, P035)।
