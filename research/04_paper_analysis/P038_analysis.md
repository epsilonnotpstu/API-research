# P038 — Microservices testing: A systematic literature review

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references বাদ)
**উৎস:** author-hosted IST version (`paper/P038.pdf`, sha256 323af80f…c532, ১৬ পৃষ্ঠা; robertoverdecchia.github.io/papers/IST_2025.pdf)
**বিশ্লেষক:** Claude · 2026-11-13

**আগের ভুল:** আগে এখানে যে substitute (Ghani et al. 2019) বিশ্লেষিত হয়েছিল, সেটি আলাদা ফাইলে সংরক্ষিত — `P038_substitute_Ghani2019_analysis.md`। এই paper নিজেই Ghani et al.-কে পুরোনো ও সীমিত SLR হিসেবে উল্লেখ করে (p.3 L248–253)।

---

## A. Bibliographic identity
- **Authors:** Francisco Ponce (University of Pisa), Roberto Verdecchia (University of Florence), Breno Miranda (Federal University of Pernambuco), Jacopo Soldani (University of Pisa)।
- **Venue:** Information and Software Technology 188 (2025) 107870; DOI 10.1016/j.infsof.2025.107870।
  - Received 7 May 2025; online 23 Aug 2025 (p.1 L88–90)।
- **Replication package:** Zenodo 10.5281/zenodo.16941552।
- **Cluster:** T9 (secondary: T1 — API/conformance testing; T3 — security gap)।
- **ধরন:** SLR (৭৪টি primary study)।

## B. Motivation
- **Microservice architecture (MSA) test করা কঠিন:** distributed ও heterogeneous। বিশেষত system ও integration level-এ (p.1 L64–73)।
- **জ্ঞান খণ্ডিত:** বিদ্যমান secondary study-গুলোর সীমা (p.3 L222–260):
  - Hui et al. (SMS, ২০২৪ পর্যন্ত) level, objective বা strategy-র গভীরে যায় না।
  - Waseem et al.: ৩৩টি study, ২০১৫–২০১৯।
  - Ghani et al.: ১৫টি study, ২০১০–২০১৮।
  - Fischer et al.: শুধু SUT।
  - Simosa & Siqueira: শুধু contract testing।

## C. Research questions
- GQM-ভিত্তিক লক্ষ্য: microservice-based system-এর testing approach-এর জ্ঞান সংগ্রহ ও শ্রেণিবিন্যাস (p.3 L313–319)।
- বিশ্লেষণ কাঠামো **4W1H** (what, when, where, why, how)।
- ⚠️ সংখ্যাযুক্ত RQ নেই।

## D. Contributions
- ৭৪টি primary study-কে **SWEBOK** অনুযায়ী শ্রেণিবদ্ধ করা: testing level, objective, strategy, type।
- Non-functional দিক **ISO/IEC 25010** অনুযায়ী।
- Study type (Stol & Fitzgerald) ও **TRL** মূল্যায়ন।
- SUT বিশ্লেষণ: আকার ও domain।
- Practical implications এবং ভবিষ্যৎ গবেষণার দিক।

## E. Methodology (p.3–5)
- **Search:**
  - Google Scholar `ALLINTITLE: ("microservice*" AND "test*")` → ১৮৬টি।
  - Scopus-এ একই query → ২৭৮টি।
  - উভয় query 16 Dec 2024-এ চালানো (L281–302)।
- **Duplicate:** ৯২টি বাদ। লেখকদের মতে Scopus-এর ফল Google Scholar-এর subset; চূড়ান্ত ১৮৬টি (L303–311)।
- **Manual selection:**
  - ৪ জন লেখক।
  - ২৫টি study-তে Fleiss’ κ = ০.৭৮।
  - Criteria I1–I3, E1–E6।
  - ফল: ৫৬টি (L337–364)।
- **Snowballing:** bidirectional, theoretical saturation পর্যন্ত। +২১ → **মোট ৭৪** (L366–384)।
- **Extraction:** deductive, open ও axial coding। ১৫টি attribute, প্রায় ১.১k মান (L443–479)।

## F. Dataset
- ৭৪টি peer-reviewed primary study (২০১৫–২০২৪)।
- Publisher: IEEE ৩৫, ACM ১৬, Springer ১১, Elsevier ৭, Wiley ৩, MDPI ২ (L999–1003)।

## G. Evaluation
- বর্ণনামূলক গণনা, শতাংশ ও heatmap।
- Inter-rater agreement (Fleiss’ κ)।

## H. Results (author-reported)
- **Trend:** ২০১৫-এ প্রথম; ২০১৮ থেকে বৃদ্ধি; ২০২৪-এ সর্বোচ্চ ১৪টি (L985–990)।
- **Level:** system ৪৭, integration ২১, unit ১৫, acceptance ৫ (L941–950)।
- **Functional বনাম non-functional:** ৪৪ বনাম ৩৬ (L951–954)।
  - Functional objective: conformance ২৩, regression ১৪, **API ৮** (L957–963)।
  - Non-functional: performance efficiency ২১, reliability ১৪, flexibility ২ (L972–977)।
- **Strategy:** specification-based সবচেয়ে বেশি, মূলত conformance ও regression-এ (L1078–1090; Table 1)।
  - Fault-based কেবল reliability-তে।
  - Usage-based ছড়ানো।
- **Study type:**
  - Laboratory experiment ৫০ (“63%”), formal theory ১২, simulation ৭; field study বিরল।
  - **TRL ৩–৪** (L1049–1061)।
  - Black-box প্রধান; gray-box বা white-box মাত্র ৩টি (L1056–1058)।
- **SUT:** small ২১, medium ১৪, large ২২ (L1144–1146)।
  - **TrainTicket ১৬টি study-তে** — de-facto large benchmark।
  - Sock Shop ৬টিতে, কিন্তু এখন deprecated।
  - Standard small ও medium MSA-র অভাব (L1098–1120)।
- **API testing-এর উদাহরণ:**
  - Microusity: OpenAPI থেকে input, status-code-ভিত্তিক error।
  - RAML-ভিত্তিক mock।
  - MicroRank/MicroRCA: root cause।
  - Endpoint coverage metric (L715–747)।

## I. Strengths
- কঠোর ও স্বচ্ছ protocol: দুটি উৎস, κ, saturation-পর্যন্ত snowballing, প্রকাশিত replication package।
- SWEBOK + ISO 25010 + TRL + SUT — বহুমাত্রিক শ্রেণিবিন্যাস। Corpus-এর T9 cluster-এর জন্য এটি প্রথম শক্তিশালী primary প্রমাণ।
- স্পষ্ট gap: security testing, empirical validation, standard SUT।

## J. Explicit limitations (p.12 §8)
- Google Scholar-এর reproducibility-ঝুঁকি। Scopus ও snowballing দিয়ে প্রশমন।
- শুধু peer-reviewed literature; white ও grey literature বাদ। State of practice ভবিষ্যৎ কাজ।
- Observer bias। κ ও যৌথ আলোচনা দিয়ে প্রশমন।

## K. Inferred limitations (⚠️ অনুমান)
- **Title-only query** (`ALLINTITLE`): শিরোনামে “microservice” নেই এমন REST/API testing কাজ বাদ পড়ে।
  - উদাহরণ: EvoMaster বা RESTler-এর microservice benchmark-এ মূল্যায়িত কাজ।
  - P003 ও P011-এর মতো কাজ microservice SUT ব্যবহার করে, কিন্তু title-এ নেই।
  - ফলে **API testing মাত্র ৮টি** — এটি সম্ভবত কম-গণনা।
- **Security gap-এর দাবি সংকীর্ণ পরিধির ফল:** “none … directly address security testing on MSAs” (L1306–1310)। অথচ REST API security testing আছে — P012, P014, P015। P014 microservice log-ও বিবেচনা করে। Title-query-র কারণে এগুলো ধরা পড়েনি।
- **সংখ্যার ছোট অসঙ্গতি:**
  - ৫৬ + ২১ = ৭৭, অথচ মোট ৭৪ বলা হয়েছে।
  - Duplicate হিসাব: ১৮৬ + ২৭৮ − ৯২ ≠ ১৮৬।
  - Laboratory experiment ৫০/৭৪ = ৬৮%, অথচ লেখা “63%” (সম্ভবত ভিন্ন denominator)।
- **Spec-quality-র প্রশ্ন অনুপস্থিত:** specification-based strategy প্রধান হলেও, spec ভুল বা অসম্পূর্ণ হলে কী হয়, তা আলোচিত নয়। এটি R1-এর প্রেক্ষাপট।
- **Conversion integrity:** দুই-কলাম layout-এ section-এর ক্রম এলোমেলো (৮.৩ আগে, ৯-এর মাঝে ৮.২)। Table ও figure-এর মান হারিয়েছে; সংখ্যা text থেকে নেওয়া।

## L. Threats to validity
- উপরে J।
- অনুমানযোগ্য threat:
  - Construct — title-query-র সংজ্ঞা।
  - Conclusion — category একাধিকবার গণ্য।

## M. Reproducibility
- **উচ্চ:** Zenodo replication package (selection, extraction, code)।
- Google Scholar-নির্ভরতা আংশিক ঝুঁকি।

## N. Opportunities (hypothesis)
- [H] **Microservice API security testing:** লেখকদের ঘোষিত gap। REST security oracle (P012, P015) এবং BOLA log detection (P014)-কে multi-service setting-এ প্রয়োগ। LO2 (P037)-এ attack traffic যোগ।
- [H] **Spec-quality-সচেতন microservice conformance testing:** specification-based approach প্রধান। তাই spec defect-এর প্রভাব ও attribution (R1; 2607.12101 TrainTicket ব্যবহার করে) microservice পরিসরে প্রাসঙ্গিক।
- [H] **Standard small বা medium MSA benchmark:** EMB-এর microservice SUT বা নতুন suite।
- [H] **Title-query-র বাইরে updated mapping:** REST fuzzing literature (P001–P008)-কে microservice testing-এর সাথে সংযুক্ত করা।

## O. Relationships
- **Supersedes** Ghani et al. 2019 (substitute document)।
- **Complements** P037 (LO2 observability dataset), P011 (industrial microservice RPC fuzzing), P020 (microservice API evolution)।
- **Security gap** P012, P014, P015 ও P036-এর সাথে সংযোগ ঘটায়।
- **TrainTicket** benchmark 2607.12101-এর সাথে ভাগ করা।

## P. Evidence locations

| দাবি | অবস্থান |
|---|---|
| Identity, dates, Zenodo | p.1 L5–35, L84–91 |
| Abstract (৭৪, SWEBOK, ফল) | p.1 L37–57 |
| Related secondary studies, Ghani | p.3 L222–269 |
| Search (GS ১৮৬, Scopus ২৭৮) | p.3 L271–311 |
| Selection (κ ০.৭৮, ৫৬) | p.4 L337–364 |
| Snowballing (+২১ → ৭৪) | p.4 L366–384 |
| Extraction | p.5 L443–479 |
| API testing studies | p.7 L715–747 |
| Levels, objectives | p.9 L941–977 |
| Trends, publishers | p.9 L980–1003 |
| Study type, TRL, black-box | p.10 L1049–1061 |
| SUTs, TrainTicket | p.11 L1133–1154 |
| Threats | p.12 L1172–1252 |
| Future directions (security, empirical, SUT) | p.13 L1292–1330 |

**Document integrity:**
- Body সম্পূর্ণ।
- Section-এর ক্রম আংশিক এলোমেলো।
- Table 1–2-এর ঘর column-split; Fig. 2–12 অনুপস্থিত।
- সংখ্যা text থেকে নেওয়া।
