# Search Strategy — PHASE A (Claude-এর স্বাধীন অনুসন্ধান)

**প্রস্তুতকারী:** Claude (Lead Researcher agent)
**তারিখ:** 2026-10-19 (সব retrieval timestamp UTC-তে `search_log.csv`-এ সংরক্ষিত)
**অবস্থা:** PHASE A সম্পন্ন; Codex-এর কোনো ফলাফল দেখা হয়নি।

---

## 1. লক্ষ্য

Software API research-এর বিস্তৃত landscape থেকে ৪৫–৬০টি যাচাইকৃত (verified) candidate paper খুঁজে বের করা। অগ্রাধিকার পাবে সাম্প্রতিক কাজ (২০২৩–২০২৬)। পাশাপাশি থাকবে কিছু foundational paper (২০১৮–২০২১), যেগুলো ছাড়া কোনো ক্ষেত্র বোঝা যায় না।

## 2. Tool ও source-এর বাস্তব প্রাপ্যতা (যাচাই করা হয়েছে, অনুমান নয়)

| Source | যেভাবে ব্যবহার | অবস্থা (2026-10-19) | মন্তব্য |
|---|---|---|---|
| **OpenAlex** REST API | `search.py openalex` | ✅ কাজ করেছে | প্রধান discovery source; arXiv preprint-ও index করে। `search=` (relevance) এবং `title_and_abstract.search` filter দুটোই ব্যবহৃত |
| **Crossref** REST API | `verify.py`, DOI lookup | ✅ কাজ করেছে | DOI registrar হিসেবে primary bibliographic verification |
| **DataCite** REST API | `verify.py` | ✅ কাজ করেছে | arXiv DOI (`10.48550/arXiv.*`)-এর registrar; arXiv record যাচাইয়ে ব্যবহৃত |
| **arxiv.org/abs** পেজ | `curl` | ✅ কাজ করেছে | version history, বর্তমান title, comments যাচাই |
| **arXiv export API** | `search.py arxiv` | ❌ HTTP 429 | বারবার rate-limited; query চালানো যায়নি (log-এ রেকর্ড করা আছে) |
| **Semantic Scholar** Graph API | `search.py s2` | ❌ HTTP 429 | API key ছাড়া rate-limited; forward/backward citation-এর জন্য OpenAlex `cites:` filter বিকল্প হিসেবে ব্যবহৃত |
| **DBLP** search API | curl | ❌ anti-bot challenge page | robots/access policy মেনে circumvent করা হয়নি |
| **Consensus** (MCP) | semantic search | ⚠️ আংশিক | rate limit বেশ কড়া; ২টি সফল query। এগুলো cross-check এবং abstract সংগ্রহে ব্যবহৃত |
| **WebSearch** | publication-status যাচাই | ✅ | শুধু venue বা version নিশ্চিত করতে; discovery-র প্রধান source নয় |
| ACM DL / IEEE Xplore / SpringerLink / ScienceDirect | সরাসরি নয় | ⚠️ পরোক্ষ | এদের metadata Crossref ও OpenAlex-এর মাধ্যমে যাচাই করা হয়েছে। Publisher site সরাসরি crawl করা হয়নি (ToS/paywall) |

**সীমাবদ্ধতা:** DBLP ও Semantic Scholar ব্যবহার করা যায়নি। ফলে venue-ভিত্তিক exhaustive sweep (যেমন ICSE/FSE/ISSTA-র সব API paper) সম্ভব হয়নি। এই ঘাটতি আংশিক পূরণ করা হয়েছে OpenAlex forward-citation chasing দিয়ে।

## 3. Search pass-এর নকশা

### Pass 1 — Broad discovery (landscape mapping)
- প্রতিটি taxonomy area-র জন্য অন্তত একটি relevance-sorted query। প্রায়ই সঙ্গে থাকে একটি citation-sorted query (influential paper খুঁজতে)।
- Area: REST testing/fuzzing, GraphQL, API security/authorization, OpenAPI/specification, API evolution/breaking changes, deprecation, documentation, misuse, recommendation, LLM tool use, API hallucination, microservices, REST design quality, monitoring/anomaly, performance (REST/gRPC/GraphQL), usability, test oracles, LLM agents over REST।
- Survey-শনাক্তকরণ: OpenAlex `type:review` filter এবং "survey"/"systematic" keyword।
- Landmark lookup: RESTler, ToolLLM, Toolformer।

### Pass 2 — Focused expansion
- নির্দিষ্ট ফাঁক পূরণ: mass-assignment, BOLA/access-policy, code থেকে spec generation, benchmark corpus, LLM-generated code-এ API misuse, MCP, REST deprecation, API privacy, GraphQL cost analysis, LLM-based documentation।
- **Forward citation searching** (OpenAlex `cites:` filter):
  - `W4224306538` (Kim et al., ISSTA 2022): 2023+ citing works, citation-sorted
  - `W3204578495` (API evolution SLR, CSUR 2021): 2022+
  - `W4386027284` (Golmohammadi et al. survey, TOSEM 2023): 2025+
  - `W4389518608` (API-Bank, EMNLP 2023): 2024+
- **Backward citation**: survey paper-গুলো (C04, C37) থেকে foundational কাজ শনাক্ত করা হয়েছে, যেমন RESTler, EvoMaster, RESTTESTGEN। Full reference list পড়া হয়নি, কারণ PHASE A-তে full text নেই।

### Trend quantification
`trend_counts.py`: ১৩টি area-র ২০১৮–২০২৬ সালের বার্ষিক count (title+abstract match, CS field)। এটি শুধুই মোটা দাগের volume indicator। ফলাফল `trend_counts_openalex.csv`-এ, বিশ্লেষণ `api_research_landscape.md`-এ।

## 4. Query syntax নোট (provider-specific)

- **OpenAlex:** `search=<text>` (stemmed relevance search) অথবা `filter=title_and_abstract.search:<boolean expr>`। Boolean-এ `AND`/`OR` বড় হাতের অক্ষরে লিখতে হয়। `primary_topic.field.id:17` = Computer Science। তারিখের filter: `from_publication_date:YYYY-MM-DD`।
- **Crossref:** `query.bibliographic=` (Boolean সমর্থন নেই) এবং `filter=from-pub-date:`।
- **arXiv:** `search_query=cat:cs.SE AND ti:"..."` (field prefix ti/abs/cat)। Rate limit-এর কারণে চলেনি।
- **শিক্ষা (lesson learned):** OpenAlex-এ full-text `search` আর citation sort একসঙ্গে দিলে অত্যন্ত noisy ফল আসে। উদাহরণ: OP003/OP004-এ NumPy আর SciPy উঠে এসেছে। তাই পরে `--ta --cs` mode ব্যবহার করা হয়েছে (OP005 থেকে)।

## 5. Inclusion criteria (PHASE A screening)

1. বিষয়বস্তু software API (web/REST/GraphQL/RPC API, library API, অথবা LLM-এর API/tool calling)-এর engineering, quality, security, evolution বা ব্যবহার নিয়ে।
2. স্পষ্ট research contribution থাকতে হবে: technique, empirical study, benchmark বা systematic survey।
3. Bibliographic identity অন্তত একটি registrar (Crossref বা DataCite) থেকে যাচাইযোগ্য হতে হবে।
4. সাম্প্রতিক (২০২৩–২০২৬) কাজ অগ্রাধিকার পাবে। পুরোনো কাজ শুধু foundational হলে।
5. Peer-reviewed venue অগ্রাধিকার পাবে। তবে গুরুত্বপূর্ণ preprint রাখা হয়েছে, স্পষ্টভাবে `preprint` চিহ্নিত করে।

## 6. Exclusion criteria

- "API" শব্দটি শুধু implementation detail হিসেবে এসেছে (যেমন কোনো app "REST API ব্যবহার করে তৈরি")।
- Predatory বা খুব কম review-মানের venue-এর তুলনামূলক কাজ, যদি একই প্রশ্নে উন্নত মানের বিকল্প থাকে। উদাহরণ: অনেক REST/gRPC performance comparison paper (OP026)।
- Zenodo/SSRN-এর unreviewed concept paper, যদি সেগুলো landscape-এর জন্য অপরিহার্য না হয়।
- Thesis/dissertation (PHASE A-তে বাদ; তবে প্রয়োজনে PHASE D-তে gap যাচাইয়ে ব্যবহার করা যাবে)।
- Pharmaceutical "API" (Active Pharmaceutical Ingredient) বা সম্পূর্ণ অপ্রাসঙ্গিক ফল।

## 7. Verification protocol

`verify.py` প্রতিটি candidate-এর জন্য যা করে:
1. DOI থাকলে Crossref record আনে (title, author, year, venue, type, `updated-by` / `update-to` দিয়ে retraction বা correction শনাক্ত করে)।
2. arXiv-only হলে DataCite record আনে, এবং arxiv.org/abs পেজ থেকে version ও title যাচাই করে।
3. OpenAlex record আনে (OA status, alternate location, `is_retracted`, abstract)।
4. Registrar title বনাম OpenAlex title-এর similarity হিসাব করে (<0.9 হলে manual check)।
5. প্রতিটি সম্ভাব্য PDF URL-এ ranged GET পাঠায়। **শুধু response body `%PDF` দিয়ে শুরু হলেই** URL-টিকে "verified direct PDF" ধরা হয়। Landing page বা 403-কে কখনোই PDF বলা হয় না।

Raw verification output: `research/01_discovery/raw/verify/*.json`

## 8. Reproducibility

- সব script: `research/00_protocol/scripts/`
- সব raw search response: `research/01_discovery/raw/<source>/<query_id>.json`
- পুনরায় চালাতে: `python3 search.py openalex "<query>" --ta --cs --from 2022-01-01` ইত্যাদি। তবে OpenAlex index সময়ের সঙ্গে বদলায়, তাই count হুবহু মিলবে না।
