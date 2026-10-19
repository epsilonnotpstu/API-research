# Claude Independent Discovery Report — PHASE A6 Audit

**প্রস্তুতকারী:** Claude | **তারিখ:** 2026-10-19 | **অবস্থা:** PHASE A সম্পন্ন — HUMAN CHECKPOINT 1-এ অপেক্ষমাণ
**স্বাধীনতা ঘোষণা:** PHASE A চলাকালীন `01_discovery/`-এ Codex-এর ফাইল (`codex_*.csv/md`) তৈরি হয়েছে দেখা গেছে, কিন্তু **সেগুলো খোলা বা পড়া হয়নি**। আমার কোনো script সেগুলো স্পর্শ করে না।

---

## 1. সংখ্যায় সারসংক্ষেপ

| পরিমাপ | মান |
|---|---|
| লগ করা search operation | ৬৮ (`search_log.csv`) — OpenAlex ৪৮, Consensus ৫, Crossref ২, WebSearch ৭, arXiv ৪ (ব্যর্থ), Semantic Scholar ১ (ব্যর্থ), DBLP ১ (ব্যর্থ); এর বাইরে trend-count-এর ১৩টি OpenAlex group-by query (`trend_counts_openalex.csv`) |
| ব্যর্থ/অনুপলব্ধ search | ৯ row (arXiv API ×৪, S2 ×১, DBLP ×১, OpenAlex quota ×১, Consensus rate-limit ×২ — শেষের দুটি পরে সফলভাবে পুনরায় চালানো হয়েছে) |
| সংগৃহীত result record (মোট, duplicate সহ) | ≈৭১১ |
| Seed candidate (screening-এর পর) | ৭০ |
| Registrar-যাচাইকৃত (Crossref বা DataCite) | **৭০/৭০** |
| Included candidate | **৬৪** |
| Screened-out (যাচাইকৃত, কারণসহ বাদ) | ৬ (C12, C17, C20, C24, C42, C54) |
| Retraction/correction notice পাওয়া গেছে | ০ (৬২টিতে পরীক্ষিত; C56, C70-এ Not assessed) |
| Direct PDF যাচাইকৃত (`%PDF` signature) | ৪৫/৬৪ (publisher/proceedings/repository ১৪ + বৈধ preprint ৩১) |
| শুধু landing page (full text যাচাই হয়নি) | ১৯/৬৪ |
| Abstract-level evidence | ৬১ পূর্ণ abstract, ২ আংশিক (C51, C65), ১ শুধু metadata (C31) |

## 2. Breadth — taxonomy অনুযায়ী কভারেজ

| Code | Area | Primary | Secondary | মূল্যায়ন |
|---|---|---|---|---|
| T1 | REST/Web API testing & fuzzing | 16 | 9 | **অতিরিক্ত ঘন** — সাহিত্যের বাস্তব ঘনত্বের প্রতিফলন, তবে PHASE B-তে কমাতে হবে |
| T2 | GraphQL, RPC/gRPC & architecture styles | 5 | 1 | পর্যাপ্ত নয়; gRPC-তে একটিই (C25) |
| T3 | API security & authorization | 5 | 4 | মাঝারি; বেশিরভাগ ২০২৩+ |
| T4 | API specification inference/enrichment | 5 | 5 | ভালো; T1 ও T8-এর সংযোগস্থল |
| T5 | API evolution / breaking changes / deprecation | 9 | 1 | ভালো; library ও web দুই দিকই আছে |
| T6 | Documentation, design quality, governance | 5 | 2 | মাঝারি |
| T7 | API misuse detection | 5 | 0 | মাঝারি; LLM-যুগের কাজ সহ |
| T8 | LLM tool use, API calling, MCP | 10 | 7 | ভালো; দ্রুত পরিবর্তনশীল |
| T9 | Microservice APIs | 2 | 2 | দুর্বল (মূলত T1/T5-এ মিশে আছে) |
| T10 | API recommendation | 1 | 0 | ইচ্ছাকৃতভাবে সীমিত (আপেক্ষিক হ্রাস, landscape §1) |
| T11 | API monitoring & anomaly detection | 1 | 0 | **দুর্বল** — উচ্চ-মানের কাজ পাওয়া যায়নি; C67 নিম্ন-আস্থা |

## 3. Recent বনাম Foundational

- বছর অনুযায়ী: 2019: 3, 2020: 5, 2021: 3, 2022: 3, **2023: 16, 2024: 12, 2025: 15, 2026: 7**।
- ৫০/৬৪ (৭৮%) ২০২৩–২০২৬-এর — prompt-এর “সাম্প্রতিক ৩–৪ বছর” অগ্রাধিকার পূরণ হয়েছে।
- ১২টি Foundational হিসেবে চিহ্নিত (RESTler, EvoMaster, IDL, GraphQL cost analysis, REST vs GraphQL experiment, security property checkers, public REST API analysis, API evolution SLR, differential regression testing, REST deprecation, docs smells, MUBench evaluation)।
- **সতর্কতা:** ২০২৬-এর ৭টি paper খুব নতুন — citation বা replication প্রমাণ নেই; গুরুত্ব নির্ধারণ বিষয়বস্তু-ভিত্তিক, প্রভাব-ভিত্তিক নয়।

## 4. Duplicate ও version সম্পর্ক

- DOI, normalized title ও temp ID — সব unique (script-চেক)।
- **একই কাজের ভিন্ন version (একটি record হিসেবে রাখা):**
  - C34 ↔ arXiv 2507.05316 (“OASBuilder: …” — শিরোনামে tool-নাম যোগ)।
  - C41 (EMSE 2022) ↔ arXiv 2110.07889; CWI/DANS repository copy-ও OpenAlex-এ আলাদা record হিসেবে আছে।
  - C64 arXiv 2507.16044 — ৪টি version, v1–v4-এর মধ্যে শিরোনাম ও সংখ্যা বদলেছে; catalog-এ বর্তমান (v4) abstract।
- **সম্ভাব্য extended version (আলাদা DOI, এখনো যাচাই হয়নি — PHASE B-তে):**
  - C13 AGORA (ISSTA 2023) ↔ “Test Oracle Generation for REST APIs” (TOSEM 2025, 10.1145/3726524)।
  - C30 (ISSRE 2025) ↔ “Enhancing REST API fuzzing with access policy violation checks and injection attacks” (JSS 2026, 10.1016/j.jss.2026.113060)।
  - C20 RESTTESTGEN (excluded) ↔ STVR 2022 ও ICSME 2022 version।
- **নাম-সংঘাত (ভিন্ন কাজ, একই নাম):** “APIBench” — Gorilla (C55) এবং API recommendation benchmark (C68)।

## 5. Survey বনাম Original; Preprint বনাম Peer-reviewed

- Paper kind: Original ৫১ (technique/empirical), Survey/SLR/mapping ৮ (C04, C21, C31, C37, C50, C61, C62, C65), Benchmark ৪ (C14, C19, C57, C58), Industrial action research ১ (C48)।
- Peer-reviewed ৬০, **Preprint ৪** (C18, C19, C59, C64) — সবগুলো স্পষ্টভাবে চিহ্নিত।
- বিশেষ track: NIER (C09), SEIP (C48, C60), ACL Industry (C34), Workshop (C67) — review-গভীরতা main track-এর চেয়ে কম হতে পারে; `review_status` কলামে উল্লেখিত।

## 6. অনুপস্থিত বা দুর্বল metadata

| ID | সমস্যা | করণীয় |
|---|---|---|
| C31 | কোনো abstract পাওয়া যায়নি; Crossref issue বছর 2027 (article in press) | PHASE B-তে publisher page/full text থেকে বিষয়বস্তু যাচাই; না পেলে বাদ |
| C65 | শুধু আংশিক abstract (institutional repository snippet) | full abstract যাচাই |
| C51 | OpenAlex abstract-এর শেষাংশ কাটা (ফলাফল অনুপস্থিত) | NDSS OA PDF থেকে যাচাই |
| C08 | OpenAlex abstract কাটা; Consensus থেকে পূর্ণ abstract নেওয়া | PHASE B-তে publisher abstract-এর সঙ্গে মিলিয়ে দেখা |
| C56 | **OpenAlex arXiv DOI → ভুল শিরোনাম** (similarity 0.26) | DataCite + ICLR page ব্যবহৃত; OpenAlex data বাদ |
| C15, C21, C22, C36, C49, C68 | Online-first বনাম issue বছরের পার্থক্য | `year_note`-এ দুটোই রেকর্ড |
| C56, C70 | Retraction status Not assessed (Crossref record নেই) | ICLR-এর জন্য retraction database নেই — ঝুঁকি কম কিন্তু অযাচাইকৃত |

## 7. Broken বা inaccessible link

- **কোনো “plausible-looking” PDF URL তালিকায় নেই** — শুধুমাত্র `%PDF` signature-সহ ৪৫টি URL `direct_pdf_url_verified`-এ।
- ১৯টি paper-এ verified PDF নেই: C01, C02, C07, C13, C14, C16, C21, C22, C27, C30, C31, C32, C36, C37, C39, C40, C48, C65, C67 — বেশিরভাগ ACM/IEEE/Elsevier paywall। এগুলোর জন্য শুধু DOI landing page দেওয়া হয়েছে। অনেকের লেখক-হোস্টেড বা institutional copy থাকতে পারে, কিন্তু **যাচাই করা হয়নি** — অনুমান করে link বসানো হয়নি।
- ৩১টি ক্ষেত্রে বৈধ arXiv preprint PDF আছে, কিন্তু published version-এর সঙ্গে বিষয়বস্তু হুবহু এক কিনা যাচাই হয়নি — PHASE C-তে বিশ্লেষণের আগে version সতর্কতা প্রয়োজন।
- Publisher landing page (doi.org) আলাদাভাবে HTTP-check করা হয়নি — DOI resolution Crossref record দিয়ে নিশ্চিত।

## 8. কম মনোযোগ পাওয়া area (search coverage gap)

1. **API monitoring/observability ও anomaly detection (T11)** — উচ্চ-মানের প্রতিনিধি পাওয়া যায়নি।
2. **API performance (REST/gRPC/GraphQL)** — শুধুমাত্র কম-মানের venue-এর micro-benchmark; কোনো candidate রাখা হয়নি।
3. **API privacy** — API-specific কাজ প্রায় অনুপস্থিত (একটি LNCS 2022 পাওয়া গেছে, রাখা হয়নি)।
4. **API usability / developer experience** — C46 ছাড়া প্রায় নেই; usability-specific search (OP034) দুর্বল ফল দিয়েছে।
5. **Event-driven/asynchronous API (AsyncAPI, webhooks, WebSocket, message broker)** — **search করা হয়নি** (আমার search strategy-র ঘাটতি; C38 এ বিষয় স্পর্শ করে)।
6. **Android/platform API compatibility** — forward-citation-এ দেখা গেছে (TSE 2023, MSR 2022), কিন্তু scope সীমিত রাখতে অন্তর্ভুক্ত হয়নি।
7. **API economics/pricing, rate limiting** — একটি (Pricing4APIs, CSI 2024) দেখা গেছে, রাখা হয়নি।
8. **Non-English literature** — অনুসন্ধান শুধু ইংরেজিতে।

## 9. Search limitation ও bias

1. **Tool availability:** DBLP (anti-bot), Semantic Scholar (429), arXiv export API (429) ব্যবহার করা যায়নি; OpenAlex-এর দৈনিক free quota শেষ হয়ে যায় (≈৭০% কাজের পর)। ফলে venue-ভিত্তিক exhaustive sweep (যেমন ICSE/FSE/ISSTA/ASE ২০২৪–২৬-এর সব API paper) হয়নি।
2. **OpenAlex metadata ত্রুটি:** অন্তত ৩টি arXiv DOI ভুল শিরোনামে map করা দেখা গেছে (ToolLLM; GPT-4 report; InstructGPT)। তাই সব arXiv record DataCite/arxiv.org দিয়ে পুনর্যাচাই করা হয়েছে।
3. **Research-group concentration:** ৬৪টির মধ্যে ১৮টি (২৮%) দুটি group থেকে — Arcuri/Zhang (C02, C04, C05, C14, C18, C19, C22, C25, C30) ও Orso/Sinha (C03, C06, C07, C09, C10, C11, C32, C33, C66)। কারণ: (ক) এরা সত্যিই ক্ষেত্রের প্রধান অবদানকারী; (খ) **forward-citation-এর anchor (C03, C04) এদেরই paper — এতে আমার পদ্ধতিই concentration বাড়িয়েছে**। PHASE B-তে অন্য group-এর কাজ (যেমন RESTest/Seville, RestTestGen/Verona, MoRest, Schemathesis, WuppieFuzz) সক্রিয়ভাবে খোঁজা উচিত।
4. **Citation-sort bias:** `--sort cited` পুরোনো paper-কে সুবিধা দেয়; recency-র জন্য আলাদা date filter দিয়ে ভারসাম্য রাখা হয়েছে।
5. **Relevance-ranking opacity:** OpenAlex/Consensus-এর ranking algorithm অস্বচ্ছ; শীর্ষ ১৫–২৫টি ফলই দেখা হয়েছে।
6. **একক screener:** সব screening একজন agent-এর — inter-rater reliability নেই। Codex merge আংশিকভাবে এটি পূরণ করবে।
7. **Abstract-level judgement:** গুরুত্ব ও প্রাসঙ্গিকতা abstract দেখে; লেখকের দাবিগুলো স্বাধীনভাবে যাচাই হয়নি।
8. **Keyword bias:** “API” শব্দ বহু অর্থে ব্যবহৃত; noisy query (OP003, OP004) লগে রাখা হয়েছে স্বচ্ছতার জন্য।
9. **arXiv crawl-delay:** robots.txt-এ ১৫ সেকেন্ড crawl-delay আছে; প্রথম verification run-এ arXiv PDF probe এর চেয়ে কম ব্যবধানে (≈১.৫–১০ সেকেন্ড, ৩০টির কম request) হয়েছিল — পরবর্তী সব arxiv.org request ≥১৫ সেকেন্ড ব্যবধানে।

## 10. শক্তি ও দুর্বলতা

**শক্তি**
- ৭০/৭০ seed registrar-যাচাইকৃত; একটিও কাল্পনিক DOI বা অযাচাইকৃত PDF নেই।
- প্রতিটি search, verification ও build ধাপ script-চালিত ও raw response-সহ সংরক্ষিত — পুনরুৎপাদনযোগ্য।
- Quantitative trend evidence (normalized) দিয়ে landscape সমর্থিত, data artifact (Zenodo spike) চিহ্নিত।
- Contradicting evidence-এর উদাহরণ সচেতনভাবে অন্তর্ভুক্ত (C41 replication মূল study-র বিপরীত ফল দেয়)।

**দুর্বলতা**
- T1-এ অতিরিক্ত ঘনত্ব ও group concentration।
- T9–T11 দুর্বল; কয়েকটি area search-ই হয়নি (event-driven API)।
- ১৯টি paper-এর full text access অনিশ্চিত — human download-এ সমস্যা হতে পারে।
- DBLP/S2 না থাকায় recall-এর নিশ্চয়তা কম।

## 11. প্রাথমিক cross-area পর্যবেক্ষণ (⚠️ HYPOTHESIS — gap হিসেবে দাবি নয়)

এগুলো শুধুমাত্র PHASE B/C-তে কী যাচাই করতে হবে তার নির্দেশিকা:
- **H1 — Specification quality একটি “hub” সমস্যা:** spec-এর মান testing (C07, C09, C10), security (C28, C29), এবং agent tool-calling (C34, C64)—তিনটিকেই প্রভাবিত করে বলে abstract-গুলো ইঙ্গিত দেয়। Spec-quality-র প্রভাবের তুলনামূলক empirical প্রমাণ কতটা আছে তা অজানা।
- **H2 — API evolution × LLM:** C69 (deprecated API in completion), C70 (ToolEVO), C58 (API instability in benchmarks), C55 (doc-change adaptation) একই মৌলিক সমস্যার ভিন্ন রূপ নির্দেশ করে — web/REST API evolution-এর ক্ষেত্রে agent-এর আচরণ নিয়ে কাজ কম দেখা গেছে (search-ভিত্তিক, যাচাই দরকার)।
- **H3 — Oracle problem:** C13, C30, C08, C18 ইঙ্গিত দেয় যে testing tool-গুলো এখনো মূলত 5xx-এর ওপর নির্ভরশীল; semantic/business-logic ও authorization oracle খোলা প্রশ্ন হতে পারে।
- **H4 — Evaluation methodology:** C03, C05, C19, C58, C37, C50 সবাই benchmark/তুলনার সমস্যা উল্লেখ করে — এটি একাধিক cluster-এ পুনরাবৃত্ত author-stated challenge।
- **H5 — MCP:** C62–C64 দেখায় MCP server-এর বেশিরভাগ REST wrapper; REST-যুগের জ্ঞান (testing, security, evolution) MCP-তে স্থানান্তরযোগ্য কিনা — খোলা প্রশ্ন হতে পারে।

## 12. PHASE B (merge)-এর জন্য সুপারিশ

1. Codex তালিকার সঙ্গে DOI → arXiv ID → normalized title ক্রমে duplicate মেলানো; C13/C30-এর extended version সম্পর্ক মীমাংসা।
2. T1-কে ~৮–১০টিতে নামিয়ে আনা; group-diversity নিশ্চিত করা।
3. T9, T11, T2 (gRPC), event-driven API — Codex এগুলো কভার করলে অগ্রাধিকার; না করলে লক্ষ্যভিত্তিক অতিরিক্ত search।
4. OpenAlex quota reset (≈২১ ঘণ্টা পর) হলে অবশিষ্ট OpenAlex-নির্ভর যাচাই (C69, C70-এর OA locations) সম্পন্ন করা।
5. ১৯টি paywalled paper-এর জন্য legal OA copy (author page, institutional repository) খোঁজা — download checklist-এর আগে।
