# P023 — Breaking Bad? Semantic Versioning and Impact of Breaking Changes in Maven Central

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (related work §6 skim, references বাদ) · **উৎস:** arXiv 2110.07889 / EMSE author version, ৪৮ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Lina Ochoa, Thomas Degueule, Jean-Rémy Falleri, Jurgen Vinju (TU Eindhoven; Univ. Bordeaux/LaBRI; CWI)
- **Venue:** Empirical Software Engineering 27, 2022, DOI 10.1007/s10664-021-10052-y
- **Cluster:** T5 (secondary: none — library-level, তবে T7/T6-এর সঙ্গে ধারণাগত সংযোগ)
- **ধরন:** External, differentiated **replication study** + নতুন static analysis tool (Maracas)

## B. Motivation
- Library evolution breaking change (BC) আনে → client upgrade এড়ায় → নিরাপত্তা ঝুঁকি ও technical lag (p.1–2 L18–23, L75–83)।
- Raemaekers et al. (JSS 2017)-এর মূল study দাবি করেছিল BC semver উপেক্ষা করে ব্যাপক এবং client-এ উল্লেখযোগ্য প্রভাব ফেলে; কিন্তু তা **clirr** (২০০৫-এ বন্ধ, ৯টি tool-এর মধ্যে সবচেয়ে কম sound) ও ২০১১-র snapshot-নির্ভর (p.3 L123–133; p.9 L455–465)।

## C. Research questions (p.4 L166–169)
- Q1: Maven Central-এ semver নীতি কীভাবে প্রয়োগ হয়? Q2: সময়ের সঙ্গে আনুগত্য কতটা বেড়েছে? Q3: BC-এর client-এর উপর প্রভাব কী? — মূল study-র H1–H3 পরীক্ষাযোগ্য hypothesis হিসেবে (p.9 L446–453)।

## D. Contributions
- উন্নত protocol (নতুন filter ও sanity check — শুধু external client-যুক্ত ১২% artefact); **Maracas** (japicmp-ভিত্তিক) — দুই version-এর মধ্যে সব BC ও client code-এর প্রভাবিত location; মূল corpus (MDD, ২০১১) পুনর্বিশ্লেষণ + MDG (২০১৮, ১৪৪K → ২.৪M artefact) সম্প্রসারণ; Zenodo replication package (p.3–4 L140–161)।

## E. Methodology
- **Corpus:** MDD (৩০ Jul 2011, ১৪৮,২৫৩ JAR); MDG (৬ Sep 2018, ২.৪M library, ৯.৭M dependency, ২.১M upgrade relation) (p.11 L568–583)।
- **Upgrade filter:** semver-রূপ X.Y[.Z]; qualifier (-rc1, -M1 ইত্যাদি) ও তারিখ-version বাদ; adjacent version; v1-এর ≥১ external client (MDG-তে ৫৬% artefact-এর কোনো client নেই, মাত্র ১২%-এর external client); শুধু Java (Scala/Kotlin/Groovy বাদ); Java ≤৮ bytecode (p.12–13 L598–677)।
- **BC সংজ্ঞা:** শুধু **binary compatibility** (মূল study-র সঙ্গে সামঞ্জস্য); ৩১ ধরনের BC; IoC-ধাঁচের (client library type extend করে — যেমন interface-এ নতুন abstract method) BC সহ (p.6–8 L277–378)।
- **Unstable API:** @Beta, @Internal, internal/experimental package — top-১০০০ library থেকে semi-automatic তালিকা (p.8 L380–426; threats)।
- **Maracas:** ∆-model (BC তালিকা) ও detection model (client location); Jezek & Dietrich benchmark (সম্প্রসারিত)-এ **precision ৯৬.৩%, recall ৯৮.৫%**, Java linker ground truth; pessimistic (over-approximate) (p.21–22 L1134; threats)।

## F. Dataset
- **১১৯,৮৭৯ library upgrade, ২৯৩,৮১৭ client** (abstract) (p.2 L61–62)।

## G. Evaluation
- Semver level (major/minor/patch/initial-development) অনুযায়ী breaking upgrade ও broken client-এর অনুপাত; সময়-প্রবণতা; মূল study-র সঙ্গে তুলনা; statistical test (Q2-এ “significantly”)।

## H. Results (author-reported)
- **Q1:** MDD-তে নতুন protocol-এ breaking upgrade ৩২.২% (মূল ৩০.০%), কিন্তু major-এ ৭২.৭% (মূল ৩৫.৯%), minor ৫০.১% (মূল ৩৫.৭%), patch ২৪.২% (মূল ২৩.৮%), initial dev ৩৯.৩% (p.25–26 L1329–1477)। **MDG-তে:** সামগ্রিক ২২.০%; major ৬১.৮%, minor ৩৭.৯%, patch ১৪.৬%, initial ২৬.৭% → **৮৩.৪% upgrade semver-সম্মত**; তবু **২০.১% non-major upgrade breaking** — H1 আংশিক নিশ্চিত (p.26–29 L1480–1648)।
- **Q2:** non-major breaking upgrade ২০০৫-এ **৬৭.৭% → ২০১৮-এ ১৬.০%**; minor breaking ৮৪.৪% → ৩০.১%, patch ৫৯.৭% → ৯.৬% — H2 নিশ্চিত (p.37 L2045–2050)।
- **Q3:** মাত্র **৭.৯% client (MDG)** ও ৯.৫% (MDD) ভাঙে; initial dev upgrade-এ সর্বোচ্চ (১৬.৮%), major ১১.৭%, minor ৭.৮%, patch ৫.০%; অধিকাংশ BC এমন declaration-এ যা client ব্যবহার করে না — **কিন্তু ব্যবহার করলে ভাঙার সম্ভাবনা উচ্চ** → **H3 প্রত্যাখ্যাত** (p.38–34 L2205–2534)।
- উপসংহার: Maven ecosystem “breaking bad” নয় (p.42 L2922–2950)।

## I. Strengths
- **বৃহৎ-মাপের, পুনরুৎপাদনযোগ্য replication** — বিরল ও মূল্যবান (মূল লেখক script ও data দিয়েছেন)।
- একই protocol দুই corpus-এ চালিয়ে protocol প্রভাব ও সময় প্রভাব আলাদা করা।
- Tool নির্ভুলতা benchmark-এ মাপা (৯৬.৩/৯৮.৫%); threats-এ প্রতিটি পক্ষপাতের দিক (overestimate) স্পষ্ট।
- “BC ঘটে” বনাম “client ভাঙে” — গুরুত্বপূর্ণ ধারণাগত পার্থক্য প্রমাণিত।
- Zenodo package (code, notebook, dataset নির্দেশনা)।

## J. Explicit limitations (p.34–35 §5.4; conclusion)
- Internal: Maracas অসম্পূর্ণ (strictfp/native মিস; pessimistic); unstable-API তালিকা অসম্পূর্ণ → BC overestimate; “library” = ≥১ external client heuristic; qualifier-যুক্ত version বাদ (Guava ২০১৭-পরবর্তী সব বাদ); version range তথ্য নেই।
- External: শুধু Java/MCR — অন্য ecosystem-এ সাধারণীকরণ নয়।
- **Behavioural compatibility বিবেচনা করা হয়নি** (শুধু binary); future work-এ behavioural incompatibility, qualitative interview, Java language evolution-এর প্রভাব, client reaction।

## K. Inferred limitations (⚠️ অনুমান)
- **“৭.৯% client ভাঙে” — binary-only lower bound:** behavioural BC (Mostafa et al.: ৭৬.৫% release-এ behavioural incompatible change, related work L2671) বাদ — তাই প্রকৃত client impact কম দেখানো হতে পারে; “not breaking bad” উপসংহার binary স্তরে সীমিত।
- Client impact = **static reachability** (client ব্যবহৃত declaration-এ BC) — আসল compile/test ব্যর্থতা চালিয়ে যাচাই নয়; dynamic/reflection usage মিস।
- Adjacent upgrade-ভিত্তিক — client সাধারণত একাধিক version লাফিয়ে upgrade করে; cumulative impact অপরিমাপিত।
- MDG ২০১৮ পর্যন্ত — Java ৯+ module system, record ইত্যাদি বাদ (Java ≤৮)।
- **Web/REST API-তে সরাসরি প্রযোজ্য নয়** — REST-এ compile-time চেক নেই (P020: runtime-এ প্রথম call-এ ভাঙে), binary compatibility ধারণা নেই; তবু পদ্ধতিগত analog (OpenAPI diff + consumer usage) প্রস্তাবযোগ্য।
- Q2-এর “significantly” — কোন test ও effect size তা markdown-এ সম্পূর্ণ দৃশ্যমান নয় (PDF-এ যাচাই প্রয়োজন)।

## L. Threats to validity
- উপরে J (Wohlin কাঠামো); inferable: construct (binary-only BC; static impact), external (Java ≤৮, ২০১৮)।

## M. Reproducibility
- **উচ্চ:** Zenodo (5221840) — code, Jupyter notebook, corpus access নির্দেশনা; Maracas open-source; MDD/MDG public।

## N. Opportunities (hypothesis)
- **REST/OpenAPI-স্তরের “Breaking Bad” study:** OpenAPI version history (APIs.guru, GitHub) + oasdiff-ধাঁচের BC detector + consumer usage (gateway log/SDK) — “BC ঘটে বনাম consumer ভাঙে” প্রশ্ন web API-তে; P020-এর qualitative দাবি (consumer lock-in) quantitative-ভাবে যাচাই; P021-এর UC-1 benchmark।
- **Behavioural BC detection** (লেখকদের future work; P020-এ ৫/১৭) — differential testing (P025) দিয়ে library ও REST উভয়ে।
- **LLM-জ্ঞান × BC:** কোন library BC LLM-generated code-কে ভাঙে (P024-এর deprecated API-র সঙ্গে সংযোগ) — Maracas-ধাঁচের analyzer দিয়ে LLM output যাচাই।
- Unstable-API marker standardization (@Beta/@Internal বনাম semver) — REST-এ `x-stability`/`deprecated` ব্যবহার mining।
- Client reaction pattern mining → automated migration (P021 UC-12/UC-15)।

## O. Relationships
- **Replicates** Raemaekers et al. (JSS 2017)।
- **Cited in P021** context (Java-কেন্দ্রিক API evolution সাহিত্যের প্রতিনিধি) এবং **P020** (Xavier et al., Brito et al.-এর মতো library BC গবেষণার সঙ্গে microservice-এর তুলনা)।
- **Complements P024** (LLM ও deprecated API) ও **P022** (tool evolution)।
- **Contrasts with P025** (behavioural/semantic regression in REST)।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract (১১৯,৮৭৯ upgrade; ২৯৩,৮১৭ client; ৮৩.৪%; ৭.৯%) | p.1–2 L18–70 |
| মূল study ও clirr সমস্যা | p.3 L123–133; p.9 L433–465 |
| Protocol পার্থক্য | p.3–4 L134–161 |
| Q1–Q3 | p.4 L166–169 |
| Binary/source/behavioural compatibility | p.6 L277–296 |
| IoC BC উদাহরণ (Fig.2.1) | p.7 L337–367 |
| Corpus MDD/MDG | p.11 L561–583 |
| Upgrade filter (১২% external client) | p.12–13 L598–677 |
| Maracas accuracy | p.21–22 L1134; p.34 L2544 |
| Q1 ফল (MDD, MDG) | p.25–29 L1329–1648 |
| Q2 প্রবণতা (৬৭.৭→১৬.০%) | p.37 L2045–2057 |
| Q3 ফল (৭.৯%) | p.38–34 L2205–2534 |
| Threats | p.34–35 L2536–2598 |
| Implications | p.40–41 L2811–2921 |
| Conclusion, future work | p.42–43 L2922–2996 |

**Document integrity:** Body সম্পূর্ণ; বেশ কিছু table (semver level × BC) column-split — মূল শতাংশ text থেকে; figure (time trend) অনুপস্থিত; page marker ও text-এর page ক্রম কিছু জায়গায় অস্বাভাবিক (p.38 → p.34) — pdftotext page index অনুযায়ী রেখেছি, PDF-এ যাচাই প্রয়োজন।
