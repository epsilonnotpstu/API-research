# P021 — A Systematic Review of API Evolution Literature

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (state-of-the-art বর্ণনা §5 skim, references বাদ) · **উৎস:** author preprint (ACM template “Vol. 1, No. 1, June 2020”, ৩৫ পৃষ্ঠা; ডেটা ৩১ Dec 2020 পর্যন্ত) — চূড়ান্ত ACM CSUR ২০২১ সংস্করণের পূর্ববর্তী · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Maxime Lamothe (Polytechnique Montréal), Yann-Gaël Guéhéneuc, Weiyi Shang (Concordia University)
- **Venue:** ACM Computing Surveys 54(8), 2021, DOI 10.1145/3470133
- **Cluster:** T5 (secondary: T7 — API misuse; T10 — recommendation, final set-এ বাদ দেওয়া cluster)
- **ধরন:** Systematic literature review (Kitchenham guideline)

## B. Motivation
- API evolution ব্যবহারকারী ও developer উভয়ের জন্য সমস্যা সৃষ্টি করে; গবেষণা ১৯৯৪-এর ১টি থেকে ২০২০-এ ৩৬টি — বিস্তৃত সাহিত্য অগ্রগতি ও অবশিষ্ট চ্যালেঞ্জ ঢেকে দেয় (p.2 L69–102)।

## C. Research questions (p.4 L196–205)
- RQ1: API evolution গবেষণা ক্ষেত্র কীভাবে বিকশিত হয়েছে (goal, evaluation, subject)? RQ2: state-of-the-art কী? RQ3: বর্তমান ও ভবিষ্যৎ চ্যালেঞ্জ কী?

## D. Contributions
- ৩৬৯টি primary study-র শ্রেণিবিন্যাস (topic, contribution type, evaluation, subject language); state-of-the-art সারাংশ (Table 6); **১৭টি existing challenge (EC) ও ১৫টি unsolved challenge (UC)** (Table 7); classification ও evaluation data GitHub-এ।

## E. Methodology
- Search phrase: শুধু **“API Evolution”** (exact), ছয়টি library + Google Scholar; forward/backward snowballing (p.4 L211–226)।
- **Funnel:** ৮২৮ (duplicate-মুক্ত) → filter ১৭৯ → snowballing +১৯০ → **৩৬৯** (p.5 L274–287)।
- বর্জনের কারণ: API evolution-সম্পর্কিত নয় ৪৬%, অপ্রাপ্য ২৫%, thesis ১৭%, non-English ৯%, SE নয় ৩% (p.6 L363–364)।
- **একজন লেখক filtering ও extraction** করেছেন; test-retest reliability ০.৯৪ (filtering) ও ০.৯৭ (১৮৯টি নমুনায় extraction) (p.5 L287–289; p.6 L369–377)।
- Topic: তিন লেখক closed card sorting — API Maintenance ১৭৮, API Usability ১৬১, Other ১৯; contribution type open card sorting (৫ ধরন) (p.7–9 L589–901)।

## F. Dataset
- ৩৬৯টি publication, ১৯৯৪–৩১ Dec 2020; repository: senseconcordia/APIEvolutionSurveyPapers।

## G. Evaluation
- Descriptive trend, frequency; challenge তালিকা গুণগতভাবে সংকলিত।

## H. Results (author-reported)
- **RQ1 — trends:** ২০১৭→২০১৮-এ প্রকাশনা দ্বিগুণের বেশি; ICSE-তে ৪২টি, TSE-তে ৮, EMSE-তে ৬, WAPI workshop ১২ (p.7 L496–516)। ২০১১ থেকে usability paper বেশি, কিন্তু ২০২০-এ maintenance (২৪ বনাম ৭) (p.7 L600–602); API usage, migration (২০২০-এ ১৪), misuse ও recommendation উদীয়মান (p.8 L645–656)।
- **Contribution:** অধিকাংশ new tools & techniques; empirical (data-mining, case study, user study — মাত্র ৮টি); ৫টি survey; ৩টি dataset (p.9–12)।
- **Evaluation:** ৩১টি metric → ৯ ধরন; precision/recall/F1/AUC বাড়ছে কিন্তু **অ-মানকীকৃত absolute metric** প্রচুর; **বহু tool-এর কোনো formal evaluation নেই**; **৭৪% empirical study কোনো statistical test ব্যবহার করে না** (p.12–14 L1158–1381; p.30 L1949)।
- **Java-কেন্দ্রিকতা:** **২৩৬/৩৬৯ (৬৩.৯%) শুধু Java** API দিয়ে মূল্যায়িত; JavaScript ১৫টি; অন্য ভাষা ≤৫% (p.15 L1455–1467; L1945–1948)।
- **RQ2 — state-of-the-art তথ্য:** ১৪.৭৮% API change compatibility ভাঙে, ২.৫৪% client-কে প্রভাবিত করে; deprecated element-এর মাত্র ৬৪%-এর replacement আছে; Android reference-এর ২৮% পুরোনো, ২২% outdated usage ~১৪ মাসে আপগ্রেড; backward-incompatibility-সংক্রান্ত client bug-এর ৬৭% সহজ client change-এ ঠিক হয় (p.24–25 L1657–1687)।
- **RQ3 — Table 7:** EC-10 “Web API-র জন্য আরও tool”, EC-11 “library API গবেষণা Web API-তে কাজে লাগানো”, EC-15 change-চালক factor স্বয়ংক্রিয় শনাক্ত, EC-16 API semantics ও dependency; **UC-1 uniform benchmark**, UC-8/UC-13 Java-র বাইরে সাধারণীকরণ, UC-14 বিভিন্ন API-র evolution তুলনা, UC-15 বড় migration/recommendation dataset (p.28–29 L1821–1870)।
- **উপসংহার — তিন প্রধান চ্যালেঞ্জ:** (১) API change-চালক factor স্বয়ংক্রিয় শনাক্ত ও ব্যবহার, (২) uniform benchmark, (৩) বিভিন্ন ভাষায় developer/user-এর উপর evolution-এর প্রভাব বোঝা; machine learning পদ্ধতি অন্বেষণের সুপারিশ (p.1 L21–23; p.32 L2083–2113)।

## I. Strengths
- বৃহৎ (৩৬৯) ও দীর্ঘ (২৭ বছর) কভারেজ; snowballing দিয়ে nomenclature ফাঁক পূরণ (+১৯০)।
- Test-retest reliability রিপোর্ট; classification data প্রকাশিত।
- EC/UC বিভাজন — কোন চ্যালেঞ্জে কাজ শুরু হয়েছে আর কোনটি একেবারে খোলা তা স্পষ্ট।
- **Java-skew ও benchmark অভাবের পরিমাণগত প্রমাণ** — গবেষণা-অগ্রাধিকার নির্ধারণে সরাসরি ব্যবহারযোগ্য।

## J. Explicit limitations (p.31 §7)
- Construct: “API Evolution” একমাত্র search phrase নিখুঁত নয়; taxonomy মূলত ad hoc — subjectivity bias।
- External: সব paper খুঁজে পাওয়া অসম্ভব; ছয় search engine + snowballing দিয়ে প্রশমন।
- Internal: selection ও classification-এ লেখক bias; **অধিকাংশ selection/classification একজন লেখকের** — test-retest দিয়ে যাচাই।

## K. Inferred limitations (⚠️ অনুমান)
- **Test-retest ≠ inter-rater:** একই ব্যক্তির পুনরায় coding কেবল consistency দেখায়, validity বা অন্য researcher-এর সঙ্গে agreement নয় — single-reviewer SLR-এর প্রচলিত দুর্বলতা।
- **সংখ্যার অসামঞ্জস্য:** Java-এর অংশ একবার “৬৩.৯% (২৩৬/৩৬৯) — সব paper”, একবার “৬৬% empirical study”, conclusion-এ “**৭০.৪%** analysed paper” — ভিন্ন denominator অস্পষ্ট (p.15 L1458; p.30 L1945; p.32 L2097)।
- **Web/REST API প্রায় অনুপস্থিত:** “API Evolution” phrase মূলত library-কেন্দ্রিক সাহিত্য ধরে; Web API মাত্র EC-10/EC-11-এ — **REST/microservice evolution-এর মূল্যায়ন এই SLR-এ কার্যত নেই** (P020 ঠিক এই gap পূরণ করে)।
- Quality assessment নেই — দুর্বল ও শক্তিশালী study সমান ওজনে গণিত; state-of-the-art সংখ্যাগুলো (১৪.৭৮%, ৬৪%) একক study থেকে, synthesis নয়।
- Cut-off ২০২০ — LLM-যুগের API evolution (P022 ToolEVO, P024 deprecated API in LLM) অন্তর্ভুক্ত নয়।
- পাঠিত সংস্করণ preprint template (DOI placeholder `1122445.1122456`) — চূড়ান্ত CSUR সংস্করণের সংখ্যা ভিন্ন হতে পারে।

## L. Threats to validity
- উপরে J; inferable: single-reviewer bias, search-term bias (library-কেন্দ্রিক), quality appraisal-এর অভাব।

## M. Reproducibility
- Primary study তালিকা ও classification GitHub-এ (senseconcordia) — **উচ্চ** (repository স্থায়িত্ব যাচাই প্রয়োজন)।

## N. Opportunities (hypothesis)
- **Web/REST API evolution benchmark (UC-1 + EC-10):** OpenAPI version history-র dataset + breaking change ground truth — Java-library benchmark-এর REST সমতুল্য; T5-এর সবচেয়ে স্পষ্ট infrastructure gap।
- **Cross-language/cross-paradigm evolution তুলনা (UC-11, UC-14):** REST বনাম GraphQL বনাম gRPC evolution pattern।
- **LLM-যুগের API evolution:** LLM-এর stale API জ্ঞান (P024), tool evolution (P022) — এই SLR-এর পরবর্তী একটি rapid review।
- **Change-চালক factor-এর ML প্রেডিকশন** (EC-15) — OpenAPI diff + issue tracker থেকে।
- **Statistical rigor audit:** API evolution/REST testing গবেষণায় statistical test ব্যবহার (৭৪% নেই) — T1-এর P005/P007 পর্যবেক্ষণের সঙ্গে সামঞ্জস্যপূর্ণ meta-research।

## O. Relationships
- **Cited by P020** (Java-কেন্দ্রিকতা ৬৩.৯% উদ্ধৃত; microservice API evolution গবেষণার প্রয়োজন)।
- **Context for P023** (Maven breaking change — Java library ecosystem), **P025** (REST regression), **P022/P024** (LLM-যুগ)।
- **Overlaps T7** (misuse; MUBench — P030 Table 6-এ উল্লিখিত benchmark) ও T10 (recommendation)।
- **Parallel to P009** (একই সময়ের SMS, মানকীকৃত evaluation-এর অভাবের অনুরূপ উপসংহার)।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract, তিন প্রধান চ্যালেঞ্জ | p.1 L11–23 |
| Motivation, ১৯৯৪→২০২০ | p.2 L79–102 |
| RQ1–RQ3 | p.4 L196–205 |
| Search, snowballing | p.4 L211–226 |
| Funnel ৮২৮→৩৬৯ | p.5 L274–287 |
| Test-retest ০.৯৪/০.৯৭ | p.5 L287–289; p.6 L369–377 |
| Venue, trends | p.7 L496–516 |
| Topic card sorting | p.7–8 L589–656 |
| Evaluation metric অ-মানকীকরণ | p.12–14 L1158–1381 |
| Java ৬৩.৯% | p.15 L1455–1467 |
| State-of-the-art পরিসংখ্যান | p.24–25 L1657–1687 |
| Table 7 (EC/UC) | p.28–29 L1821–1870 |
| ৭৪% statistical test নেই | p.30 L1949 |
| Threats | p.31 L2043–2066 |
| Conclusion (৭০.৪%) | p.32 L2083–2113 |

**Document integrity:** Body সম্পূর্ণ; Table 1–5 column-split; Fig.1–7 (trend chart) অনুপস্থিত — শতাংশ text থেকে; দুটি spurious “## Case study” heading (table থেকে); preprint template DOI placeholder।
