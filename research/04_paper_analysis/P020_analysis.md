# P020 — Microservice API Evolution in Practice: A Study on Strategies and Challenges

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references বাদ; related work skim) · **উৎস:** arXiv 2311.08175v1 (১৪ Nov 2023), ২০ পৃষ্ঠা — JSS চূড়ান্ত সংস্করণের preprint · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Alexander Lercher, Johann Glock, Christian Macho, Martin Pinzger (University of Klagenfurt)
- **Venue:** Journal of Systems and Software, 2024, DOI 10.1016/j.jss.2024.112110
- **Cluster:** T5 (secondary: T9 — microservices; T6 — documentation/governance)
- **ধরন:** Qualitative interview study (grounded theory open coding)

## B. Motivation
- Microservice-এর loose coupling compile-time-এ API change ধরা পড়তে দেয় না — breaking change runtime-এ প্রথম call-এ প্রকাশ পায় (p.1 L40–47)।
- পূর্ববর্তী গবেষণা communication ও integration-কে প্রধান চ্যালেঞ্জ বলেছে কিন্তু **অন্তর্নিহিত কারণ ও সমাধান-দিক দেয়নি** (p.1 L49–59)।

## C. Research questions (p.2 L112–116)
- RQ1: service-এর মধ্যে message exchange ও তার documentation কী দিয়ে হয়?
- RQ2: API change প্রবর্তন ও যোগাযোগে কোন strategy?
- RQ3: কোন challenge?

## D. Contributions (p.2 L119–130)
- Microservice API evolution-এর প্রথম practice-ভিত্তিক study: ৬টি strategy (best practice) ও ৬টি challenge (pitfall); দুটি মূল সমস্যা — **tight organizational coupling** ও **consumer lock-in**; দুটি গবেষণা-দিক; replication package (interview guide, codebook)।

## E. Methodology
- **Semi-structured interview:** ৫ বিভাগের guide (background, communication, provider-side evolution, consumer-side evolution, additional thoughts); দুবার পরিমার্জিত (p.2 L71–104)।
- ২০টি interview, ৩টি বাদ (দুই-জনের দল; breaking change নেই; intermediate ফল জেনে ফেলা) → **n=১৭, ১১টি কোম্পানি** (৮টি আন্তর্জাতিক); গড় ১০.২ বছর অভিজ্ঞতা, loosely-coupled-এ ৪.৬ বছর; গড় ৭০.৯ মিনিট; ১১টি online, ৬টি সামনাসামনি (p.2–3 L105–181)।
- **Sampling:** প্রাক্তন সহকর্মী + snowball; প্রতি কোম্পানি সর্বোচ্চ ৩ জন (p.3 L158–164)।
- **Analysis:** verbatim transcript → প্রথম লেখকের open coding; দ্বিতীয়/তৃতীয় লেখক ২টি random transcript স্বাধীনভাবে code (investigator triangulation); ১২টির পরে codebook স্থিতিশীল, শেষ ৩টিতে নতুন category নেই (saturation); **member checking** — ১৭-এর ১৩ জন সাড়া, ২ জনের ছোট মন্তব্য (p.3 L183–215)।
- রিপোর্টিং নিয়ম: শুধু ≥৫ participant ও ≥৩ কোম্পানির উল্লেখিত finding (p.16 threats)।

## F. Dataset
- ১৭ জন practitioner (developer, architect, tech lead, department head, product manager); Table 1-এ কোম্পানি ও ভূমিকা।

## G. Evaluation
- গুণগত; প্রতিটি finding (i/17) সমর্থন-সংখ্যা সহ; সংশ্লিষ্ট সাহিত্যের সঙ্গে grounding।

## H. Results (author-reported)
- **RQ1:** REST গড়ে ৬৬.৮% (median ৮৫%), event-driven ২২.৬% (median ১০%), SOAP শুধু legacy; **১৭/১৭ OpenAPI/Swagger** ব্যবহার করে; ৯/১৭ wiki/UML দিয়ে semantics সম্পূরক; ৯/১৭ API gateway; ১৩/১৭ event-driven (RabbitMQ ৬, Kafka ৩) কিন্তু **মাত্র ৩/১৭ তা নথিভুক্ত করে**, AsyncAPI মাত্র ১ জন; ৬/১৭ internal REST API নথিভুক্ত করে না — source code পড়ে; GraphQL/gRPC ≤২ জন (p.3–6 L224–654)।
- **RQ2 — ৬ strategy (Table 2):** (১) প্রয়োজনীয় breaking change মেনে নেওয়া — কারণ নতুন feature ১২/১৭, উন্নয়ন ৯/১৭, API design ৬/১৭; ত্রৈমাসিক–অর্ধবার্ষিক; **structural change ১৭/১৭ breaking মনে করেন, behavioral মাত্র ৫/১৭** (২) compatible থাকা — workaround ১৭/১৭, extension/duplication ১১/১৭, regression/contract test ১০/১৭, dynamic API ৬/১৭ (৩) versioning ১৭/১৭ (semver ৫/১৭, integer ১২/১৭); **একাধিক version একসঙ্গে ১৩/১৭** (২–৮টি) (৪) অন্য দলের সঙ্গে সহযোগিতা, API-first ১১/১৭ (৫) internal-এ “just break and fix” (৬) বাহ্যিক system-এর API abstract করা (p.6–10)।
- **RQ3 — ৬ challenge (Table 3):** change impact analysis হাতে-কলমে ও শ্রমসাধ্য (৯/১৭); **consumer পুরোনো version-এ আটকে থাকে (১২/১৭)** — কেউ কেউ নিজেরাই “never change a running system” মানেন (৫/১৭); communication অস্পষ্ট (৯/১৭) — consumer অজানা (৭/১৭), informal channel, hierarchy (৬/১৭); **API maintainability/usability ক্ষয় (১৪/১৭)**, backward compatibility technical debt বাড়ায় (৯/১৭); সরকারি service provider অসহযোগী (৬/১৭); event-driven evolution উপেক্ষিত (p.10–14)।
- **Discussion:** strategy-গুলো challenge কমায় কিন্তু নতুন তৈরি করে → **tight organizational coupling** (প্রযুক্তিগত loose coupling সত্ত্বেও সাংগঠনিক মিটিং-নির্ভরতা) ও **consumer lock-in**; গবেষণা-দিক: (i) **automated change impact analysis** (service dependency graph, breaking change detection), (ii) **effective change communication** (consumer-নির্দিষ্ট changelog) (p.14–16)।

## I. Strengths
- কঠোর qualitative পদ্ধতি: saturation, investigator triangulation, member checking, ≥৫/১৭ রিপোর্টিং threshold, replication package।
- Provider ও consumer উভয় দৃষ্টিকোণ পৃথকভাবে।
- প্রতিটি finding সাহিত্যের সঙ্গে grounded — শুধু মতামত নয়।
- **Behavioral breaking change উপেক্ষিত** — একটি গুরুত্বপূর্ণ, পরীক্ষাযোগ্য অনুসন্ধান; T5-এর tool-গবেষণার জন্য সরাসরি প্রাসঙ্গিক।
- দুটি ধারণাগত সমস্যা (organizational coupling, consumer lock-in) — তত্ত্ব-গঠন।

## J. Explicit limitations (p.16 §6.3)
- External: ১১ কোম্পানি, ১৭ জন — সাধারণীকরণ সীমিত (বৈচিত্র্য ও saturation দিয়ে প্রশমন); <৫ participant-এর finding বাদ (যেমন বাহ্যিক API-র নিম্নমানের documentation ৪/১৭)।
- Internal: ভুল ব্যাখ্যা — guideline, open প্রশ্ন, triangulation, member checking দিয়ে প্রশমন।

## K. Inferred limitations (⚠️ অনুমান)
- **Sampling bias:** প্রাক্তন সহকর্মী + snowball — সম্ভবত অস্ট্রিয়া/DACH অঞ্চল-কেন্দ্রিক ও লেখকদের নেটওয়ার্কে সমজাতীয়; কোম্পানি-ভিত্তিক বণ্টন ও দেশ স্পষ্ট নয় (Table 1 markdown-এ পাঠযোগ্য নয়)।
- **Triangulation সীমিত:** ১৭-এর মধ্যে মাত্র ২টি transcript দ্বিতীয় coder দেখেছেন; coder agreement সংখ্যাগতভাবে (κ) রিপোর্ট নেই।
- Self-report — প্রকৃত change frequency, breaking change হার বা incident data দিয়ে যাচাই নেই (mining study-র সঙ্গে triangulation অনুপস্থিত)।
- “Six challenges” abstract-এ, কিন্তু section-কাঠামোয় ৫.২–৫.৭ উপবিভাগ সংখ্যা ও Table 3 markdown-এ সম্পূর্ণ মেলানো যায়নি; একটি জায়গায় “(4/19)” (p.5 L489) — n=১৭-এর সঙ্গে অসঙ্গত (সম্ভবত typo)।
- GraphQL/gRPC প্রায় অনুপস্থিত — ফলাফল REST/event-driven-কেন্দ্রিক; P009/P011-এর paradigm-এ প্রযোজ্যতা অজানা।
- Interview ২০২১–২০২৩; LLM-যুগের consumer (AI agent, MCP — T8) এর বাইরে।

## L. Threats to validity
- উপরে J; inferable: sampling/selection bias, self-report bias, researcher bias (প্রথম লেখক একাই সব coding)।

## M. Reproducibility
- Replication package: interview guide, codebook (Lercher et al. 2023) — qualitative study হিসেবে ভালো; transcript গোপনীয়।

## N. Opportunities (hypothesis)
- **Behavioral breaking change detection for REST/microservices** — ১২/১৭ structural-কেন্দ্রিক; behavioral change (timezone, value semantics) শনাক্তে differential regression testing (P025) + invariant (P008) একীভূত; লেখকদের পরবর্তী কাজ (Lercher 2025, P017-এ উদ্ধৃত) static breaking-change detection-এ গেছে।
- **Automated change impact analysis:** service dependency graph (static + tracing, T9 P037) থেকে প্রভাবিত consumer চিহ্নিত — লেখকদের প্রস্তাবিত দিক (i)।
- **Consumer-নির্দিষ্ট changelog/notification** — API gateway log (৬/১৭ ইতিমধ্যে consumer log রাখে) + OpenAPI diff + LLM সারাংশ — দিক (ii)।
- **Event-driven API (AsyncAPI) evolution ও documentation** — ১৩/১৭ ব্যবহার করে কিন্তু ৩/১৭ নথিভুক্ত করে: স্পষ্ট gap (AsyncAPI spec inference — T4-এর সম্প্রসারণ)।
- **LLM agent-কে consumer হিসেবে** — tool/API version change-এ agent-এর অভিযোজন (P022 ToolEVO-র সঙ্গে সংযোগ): consumer lock-in-এর নতুন রূপ।
- Quantitative follow-up survey — এই qualitative তত্ত্বকে বৃহত্তর নমুনায় যাচাই।

## O. Relationships
- **Grounded in P021** (Lamothe et al. API evolution SLR — Java-কেন্দ্রিকতা ৬৩.৯%) — web/microservice API evolution গবেষণার আহ্বানের সাড়া।
- **Cites P025** (Godefroid et al. differential regression testing) — regression testing strategy-র tool সমাধান।
- **Cites P009** (Quiña-Mera GraphQL SMS) ও Wittern et al. (P010-এর পূর্বসূরি)।
- **Links T9** (P038 microservices testing SLR; P037 LO2) ও T6 (documentation)।
- **Links P023** (Maven semver/breaking change) — library ecosystem-এর অনুরূপ সমস্যা microservice-এ।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract (১৭ interview, ১১ কোম্পানি) | p.1 L13–22 |
| Motivation (runtime breaking) | p.1 L40–59 |
| RQ1–RQ3 | p.2 L112–116 |
| Interview guide, সময়কাল | p.2 L71–110 |
| Participant selection, n=১৭ | p.3 L158–181 |
| Open coding, triangulation, member checking | p.3 L183–215 |
| RQ1 (REST ৬৬.৮%, OpenAPI ১৭/১৭) | p.3–5 L224–535 |
| Event-driven documentation ৩/১৭ | p.6 L637–654 |
| Strategy তালিকা (Table 2), RQ2 উত্তর | p.6 L564–635 |
| Breaking change কারণ | p.6–7 L668–696 |
| Structural vs behavioral (৫/১৭) | p.7 L720–738 |
| Regression testing (১০/১৭) | p.7–8 L740–783 |
| Versioning, multiple versions (১৩/১৭) | p.8–9 L789–886 |
| Challenges (RQ3) | p.10–14 L1052–1417 |
| Organizational coupling, consumer lock-in | p.14–15 L1418–1525 |
| Research directions | p.15–16 L1526– |
| Threats | p.16 L1577– |

**Document integrity:** দুই-কলামের reading order ব্যাপকভাবে এলোমেলো — section ক্রম ভাঙা (যেমন “2.3” “3”-এর পরে, “4.2” “4”-এর আগে); Table 1–3 column-split (Table 2–3-এর participant/company count পুনর্গঠন সম্ভব নয়); Fig.1–2 অনুপস্থিত। সব (i/17) সংখ্যা চলমান text থেকে।
