**T3 — ৭৩টি P001 F_OAS fault-এর স্বাধীন blind labelling**

৭৩টি fault-এর প্রত্যেকটির Level-1, প্রযোজ্য Level-2, evidence codes, confidence, সর্বোচ্চ ৪০ শব্দের rationale এবং যাচাইযোগ্য source locator লেখা হয়েছে। ফলাফল: **SPEC ৪৭, UNDECIDABLE ১৬, ENV ৯, IMPL ১**। এগুলো এই labeller-এর attribution; adjudicated ground truth নয়। উৎস: [codex_labels.csv](../../08_experiments/E2_labelling/codex_labels.csv), `fault_id=F001`–`F073`।

কাজটি [T3 assignment](../tasks/T3.md:1), [protocol](../PROTOCOL.md:1) এবং [codebook v0.2](../../08_experiments/R1_triage_codebook.md:1) অনুসারে করা হয়েছে। `p001_foas_labelling_sheet.csv`, `build_labelling_sheet.py`, `triage_output.csv` এবং `T2_report.md` খোলা হয়নি। Blind CSV-কে `testCaseId` দিয়ে সংশ্লিষ্ট `faultClustersConfirmedBugs_<api>.csv`-এর request/response ও diagnostic-এর সঙ্গে মেলানো হয়েছে; attribution-এর জন্য অন্য labeller-এর label নেওয়া হয়নি। উৎস: [T3 assignment](../tasks/T3.md:2), output-এর প্রতিটি row-এর `sources`।

**Blinding audit:** CSV-র শেষ পরিবর্তন ২০২৬-১১-১৩ **১৫:১২:৩২ UTC**। CSV সম্পূর্ণ ও initial validation পাস হওয়ার পরে final board check-এ concurrently যোগ হওয়া T2 classification summary ও review দেখা গেছে। এই exposure-এর পরে কোনো label বা CSV content পরিবর্তন করা হয়নি। তাই pre-freeze labelling স্বাধীন ছিল, তবে পুরো session-জুড়ে blind থাকার দাবি করা হচ্ছে না। উৎস: [board-এর T2 completion/review log](../COLLAB_BOARD.md:26), [frozen CSV](../../08_experiments/E2_labelling/codex_labels.csv), filesystem modification time ও সংরক্ষিত SHA-256: `64b860aa89d81de2ba301c953eccc78ce8ec47059b24a84e96f7e9b33aa8b6a6`। নিষিদ্ধ চারটি file খোলা হয়নি।

**Label distribution**

নিচের সব সংখ্যা output-এর ৭৩টি row থেকে গণনা করা; API-নির্দিষ্ট পরীক্ষার বাইরে কোনো defect prevalence নির্দেশ করে না। উৎস: [codex_labels.csv](../../08_experiments/E2_labelling/codex_labels.csv), `F001`–`F073`; sampling scope: [T3 assignment](../tasks/T3.md:1)।

| Level-1 | সংখ্যা |
|---|---:|
| SPEC | 47 |
| IMPL | 1 |
| BOTH | 0 |
| TEST | 0 |
| ENV | 9 |
| UNDECIDABLE | 16 |
| মোট | 73 |

| Level-2 | সংখ্যা |
|---|---:|
| S-RESP-TYPE | 17 |
| S-STATUS | 12 |
| S-RESP-MISSING | 9 |
| S-STRUCT | 7 |
| S-CONFIG | 2 |
| I-RESP-CONTRACT | 1 |
| খালি — ENV/UNDECIDABLE | 25 |

Level-2 খালি রাখা হয়েছে শুধু ENV ও UNDECIDABLE-এর জন্য, কারণ v0.2 এদের subtype সংজ্ঞায়িত করে না। কোনো নতুন subtype বা `NA` label উদ্ভাবন করা হয়নি। উৎস: [codebook, Level-2](../../08_experiments/R1_triage_codebook.md:72); output-এর ENV ও UNDECIDABLE rows।

Confidence-এর বণ্টন: **১ → ১৬, ২ → ৩০, ৩ → ২৭**। এই কাজে ১ = attribution অপর্যাপ্ত, ২ = যুক্তিসমর্থিত inference বা historical uncertainty, ৩ = স্পষ্ট diagnostic/prose অথবা সরাসরি প্রযোজ্য codebook rule। এটি operational interpretation; calibrated probability নয়। v0.2 সংখ্যার range দেয়, কিন্তু পূর্ণ rubric দেয় না। উৎস: [codebook, record format](../../08_experiments/R1_triage_codebook.md:120); output-এর `confidence` column।

`STRICT_ONLY=true` নয়টি fault-এর rationale-এ রাখা হয়েছে: **F010, F011, F015–F018, F065, F072, F073**। প্রত্যেকটি v0.2-এর নির্ধারিত default অনুযায়ী SPEC/S-RESP-MISSING; ফলে ৪৭টি SPEC-এর মধ্যে ৯টি strict-only এবং ৩৮টি অন্য ধরনের। TEST=০ হওয়া strict oracle-এর correctness প্রমাণ করে না—এখানে codebook-এর attribution convention অনুসরণ করা হয়েছে। উৎস: [blind CSV](../../08_experiments/E2_labelling/p001_foas_blind.csv), উল্লিখিত `fault_id`-গুলোর `strict_only`; [strictness rule](../../08_experiments/R1_triage_codebook.md:130)।

ENV-এর মধ্যে আটটি 429/quota/throttling response—F013, F037–F042, F071—এবং একটি Cloudflare block—F048। F048-এর body-তে HTML block page পাওয়া যায়; স্রেফ undocumented 403 দেখে ENV দেওয়া হয়নি। উৎস: output-এর উল্লিখিত rows এবং তাদের `sources`-এ নির্দিষ্ট raw `testCaseId`; [R4](../../08_experiments/R1_triage_codebook.md:69)।

UNDECIDABLE: **F004, F005, F006, F007, F019, F022, F023, F024, F032, F033, F034, F044, F045, F046, F061, F070**। এসব ক্ষেত্রে পরস্পরবিরোধী contract ও observed response ছাড়িয়ে পুরো cluster-এর intended behaviour স্থির করা যায়নি। উৎস: output-এর সংশ্লিষ্ট rows; [R5](../../08_experiments/R1_triage_codebook.md:70)।

**Evidence ব্যবহারের ব্যাখ্যা**

CSV-তে `sources`-এর `#fault_id=...` ও `#testCaseId=...` হলো logical CSV row locator; multiline response-এর physical line number নয়। Schema-র ক্ষেত্রে `:line` দেওয়া হয়েছে। একাধিক code/source semicolon দিয়ে পৃথক করা। উৎস: output-এর header ও `F001`–`F073` rows।

| Evidence code | ব্যবহার করা row | এই কাজে ব্যাখ্যা |
|---|---:|---|
| E-AUX | 34 | Local prose/example/header default এবং বহিরাগত schema semantics-এর সহায়ক constraint evidence |
| E-CONSIST | 20 | একই operation-এর একাধিক captured request/response-এর তুলনা; repeat experiment নয় |
| E-CONV | 23 | HTTP rejection, quota/block diagnostic অথবা JSON serialization convention |
| E-DEV | 13 | সরবরাহকৃত confirmation/fix flag; পরিবর্তিত artifact-এর প্রমাণ হিসেবে ব্যবহার করা হয়নি |
| E-DOC | 6 | Official Spotify/Stripe documentation-এর নির্দিষ্ট field semantics |

এক row-তে একাধিক code থাকতে পারে; তাই যোগফল ৭৩ নয়। F022, F023, F032, F044 এবং F070-তে যথেষ্ট স্বতন্ত্র intent evidence না থাকায় `evidence_codes` খালি, কিন্তু raw response ও schema source দেওয়া আছে। E-CODE-INTENT ব্যবহার করা হয়নি; task-এর অনুমোদিত code তালিকায় না থাকায় E-CROSS-ও ব্যবহার করা হয়নি। উৎস: [T3 assignment](../tasks/T3.md:8); output-এর `evidence_codes` ও `sources` columns।

Embedded spec prose-কে **E-AUX** বলা হয়েছে, spec-এর বাইরের independent **E-DOC** নয়। এই response-side ব্যবহারটি v0.2-এর prose-সংক্রান্ত E-AUX সংজ্ঞার interpretation; এর request-side উদাহরণ response-side ranking স্পষ্ট করে না। যেমন `followers.href`-এর prose-তে সর্বদা null বলা হলেও formal type string। উৎস: [E-AUX সংজ্ঞা](../../08_experiments/R1_triage_codebook.md:135), [FollowersObject](../../08_experiments/_external/p001/specs/Spotify_Playlists__openapi.yaml:5430), output `F053`, `F057`, `F061`।

E-CONSIST-এর জন্য F021-তে একই অনুমোদিত raw file-এর অতিরিক্ত response `test_1h822k3yh58hh_getCreatorCollection` দেখা হয়েছে; সেটি নতুন labelling unit নয়। তাতে ২০টি character এবং timestamp-রূপের `modified` আছে, যা F021-এর অন্য character-list response-এর সঙ্গে তুলনা করা হয়েছে। অন্য operation-এর timestamp দেখে একক individual-character response F022-এর intent স্থির করা হয়নি। উৎস: [raw Marvel CSV](../../08_experiments/_external/p001/faultClustersConfirmedBugs_marvel.csv), উল্লিখিত `testCaseId`; output `F021`, `F022`।

**কঠিন সিদ্ধান্ত ও তার সীমা**

| Fault | সিদ্ধান্ত ও কারণ | নির্দিষ্ট evidence |
|---|---|---|
| F001/F003 বনাম F004–F006 | ⚠️ Double-escaped decimal pattern স্পষ্ট spec সমস্যা; কিন্তু একই cluster-এ missing fax, phone এবং tax type থাকলে সেগুলোর intent আলাদাভাবে অজানা। তাই শেষ তিনটি UNDECIDABLE। | [decimal pattern](../../08_experiments/_external/p001/specs/Amadeus__openapi.json:1218), [নিজস্ব numeric example](../../08_experiments/_external/p001/specs/Amadeus__openapi.json:1573), [required fax](../../08_experiments/_external/p001/specs/Amadeus__openapi.json:753), output `F001`, `F003`–`F006` |
| F007 | ⚠️ Saved schema-তে countryCode string, diagnostic-এ object-only; dayOfWeek-এর example URL অথচ enum bare নাম। একটি নির্ভরযোগ্য artifact-level attribution দেওয়া যায়নি। | [countryCode](../../08_experiments/_external/p001/specs/DHL_LocationFindByAddress__openapi.yaml:662), [dayOfWeek enum](../../08_experiments/_external/p001/specs/DHL_LocationFindByAddress__openapi.yaml:747), output `F007` |
| F008/F009 | ⚠️ application/problem+json response তার নিজস্ব header default-এর সঙ্গে মেলে; operation-এর produces শুধু application/json। বর্তমান Level-2-তে header/configuration-এর নিকটতম S-CONFIG ব্যবহার। | [produces](../../08_experiments/_external/p001/specs/DHL_LocationFindByAddress__openapi.yaml:54), [400 default](../../08_experiments/_external/p001/specs/DHL_LocationFindByAddress__openapi.yaml:78), [401 default](../../08_experiments/_external/p001/specs/DHL_LocationFindByAddress__openapi.yaml:92), output `F008`, `F009` |
| F019/F023/F032 | ⚠️ sentence অনুপস্থিত থাকা বা সবসময়-null thumbnail/series links-কে অনুমান করে optional/nullable বলা হয়নি। Contract mismatch ও intended representation এক বিষয় নয়। | [required sentence](../../08_experiments/_external/p001/specs/LanguageTool__openapi.json:203), [Story.thumbnail](../../08_experiments/_external/p001/specs/Marvel__openapi.yaml:4970), [Series](../../08_experiments/_external/p001/specs/Marvel__openapi.yaml:4663), output `F019`, `F023`, `F032` |
| F024 | ⚠️ characterId=0-এর 409 বনাম documented missing-character 404: zero-কে invalid ID, absent resource, নাকি conflict ধরতে হবে, তার independent evidence নেই। | [individual-character responses](../../08_experiments/_external/p001/specs/Marvel__openapi.yaml:133), output `F024` |
| F033/F034/F045 | ⚠️ Timestamp format ও nullable description-এর জন্য কিছু SPEC evidence আছে; কিন্তু `-0001-11-30T00:00:00-0500` এবং F045-এর `diamondCode=0`-এর intended sentinel semantics প্রতিষ্ঠিত নয়। পুরো cluster UNDECIDABLE। | [ComicDate](../../08_experiments/_external/p001/specs/Marvel__openapi.yaml:4270), [Comic properties](../../08_experiments/_external/p001/specs/Marvel__openapi.yaml:4826), output `F033`, `F034`, `F045` |
| F044 | ⚠️ Request ও response দুটোতেই offset=4294967296; দুটো schema-তেই int32। Missing validation বনাম ভুল declared range পৃথক করার evidence নেই। | [request offset](../../08_experiments/_external/p001/specs/Marvel__openapi.yaml:105), [response container](../../08_experiments/_external/p001/specs/Marvel__openapi.yaml:4279), output `F044` |
| F046/F061 | ⚠️ fixed=true থেকে code fix নাকি schema fix বোঝা যায় না। যথাক্রমে totalResults="6" এবং followers.total=null-এর representation অমীমাংসিত। | [OMDb totalResults](../../08_experiments/_external/p001/specs/OMDb__openapi.yaml:133), [FollowersObject](../../08_experiments/_external/p001/specs/Spotify_Playlists__openapi.yaml:5430), [blind CSV](../../08_experiments/E2_labelling/p001_foas_blind.csv), `F046`, `F061` |
| F047 | ⚠️ Error string-এর ভেতরে unescaped double quotes থাকার কারণে captured 200 body JSON হিসেবে decode হয় না। IMPL/I-RESP-CONTRACT; 5xx না থাকলেও serialization defect দৃশ্যমান। | [OMDb 200 object response](../../08_experiments/_external/p001/specs/OMDb__openapi.yaml:87), [raw OMDb CSV](../../08_experiments/_external/p001/faultClustersConfirmedBugs_omdb.csv), `testCaseId=test_1iv3rat0bqo1d_search` |
| F066/F067/F069 | ⚠️ Milan/Paris-এর euro এবং Tokyo-এর yen একই operation-এ location-এর সঙ্গে সামঞ্জস্যপূর্ণ; dollar-only enum-এর SPEC attribution confidence ২। এটি সব enum mismatch-কে SPEC বলার নিয়ম নয়। | [price enum](../../08_experiments/_external/p001/specs/Yelp_Businesses__openapi.yaml:248), output `F066`, `F067`, `F069` |
| F070 | rating=0.0 ও review_count=0 একসঙ্গে আছে। [H] এটি unrated sentinel হতে পারে; কিন্তু প্রমাণিত নয়, তাই UNDECIDABLE। | [rating minimum](../../08_experiments/_external/p001/specs/Yelp_Businesses__openapi.yaml:255), output `F070` |

Spotify-র composition পরীক্ষা শুধু diagnostic-এর “matched 0 out of 2” পুনরাবৃত্তি করে করা হয়নি। Saved schemas-এ `TrackObject` ও `EpisodeObject`-এর property-গুলো optional এবং `type`-এ আলাদা enum নেই। আমাদের সীমিত checker-এ প্রতিটি response-এর প্রথম track-এর reachable `$ref`, primitive type, object property, array item এবং int32 constraint পরীক্ষা করা হয়েছে; চারটি witness-ই উভয় branch-এ মেলে। এটি পূর্ণ OpenAPI validator নয়। উৎস: [PlaylistTrackObject.oneOf](../../08_experiments/_external/p001/specs/Spotify_Playlists__openapi.yaml:5770), [EpisodeObject](../../08_experiments/_external/p001/specs/Spotify_Playlists__openapi.yaml:5244), [TrackObject](../../08_experiments/_external/p001/specs/Spotify_Playlists__openapi.yaml:6683); নিচের raw row locators।

| Fault | Representative track.id | TrackObject | EpisodeObject | Raw CSV testCaseId |
|---|---|---|---|---|
| F051 | 295X5cd7nBzFNrgn77FyGK | মেলে | মেলে | test_1iextu6ha8n6u_endpointgetplayliststracks |
| F052 | 3JbzCex8HkQSkgwXq0i6NC | মেলে | মেলে | test_1iv6kpnuu90th_endpointgetplaylist |
| F053 | 1X4l4i472kW5ofFP8Xo0x0 | মেলে | মেলে | test_1iyhprxoyjeb8_endpointgetplaylist |
| F055 | 0A8rvkDkZRTH3UgYGWxFnp | মেলে | মেলে | test_1jia0oo7begjb_endpointgetplaylist |

উপরের প্রতিটি row-এর raw source: [faultClustersConfirmedBugs_spotify_Playlists.csv](../../08_experiments/_external/p001/faultClustersConfirmedBugs_spotify_Playlists.csv), সংশ্লিষ্ট `testCaseId`। ⚠️ এখানে instance-level branch overlap প্রতিষ্ঠিত; পুরো schema globally unsatisfiable বলা হয়নি। Exactly-one semantics-এর সঙ্গে overlap-এর অমিল SPEC/S-STRUCT-এর পক্ষে evidence; saved schema বনাম historical diagnostic-এর পার্থক্য confidence ২ রাখার একটি সীমা। [OpenAPI 3.0.3 composition semantics](https://spec.openapis.org/oas/v3.0.3.html#discriminator-object)।

Stripe F062–F064-এ `nullable:true` composed parent-এ আছে, কিন্তু একই level-এ `type` নেই; branch-গুলো null গ্রহণ করে না। ⚠️ Nullable product fields-এর documented অর্থ বজায় রাখতে composition বদলানো দরকার—সেজন্য SPEC/S-STRUCT। শুধু keyword উপস্থিত দেখে validator-কে ভুল বলা হয়নি। উৎস: [product schema](../../08_experiments/_external/p001/specs/Stripe_Products__openapi.yaml:88), [OpenAPI nullable rule](https://spec.openapis.org/oas/v3.0.3.html#schema-object), [Stripe product attributes](https://docs.stripe.com/api/products/object), output `F062`–`F064`।

F065-এর `package_dimensions.height/length/weight/width` saved schema-তে ইতিমধ্যে declared, যদিও diagnostic এগুলোকে অতিরিক্ত বলেছে। [H] `$ref` conversion অথবা schema snapshot mismatch এর কারণ হতে পারে; যাচাই ছাড়া কারণটি স্থির করা হয়নি। Task-এর strict-only flag এবং বর্তমান codebook default বজায় রাখা হয়েছে। উৎস: [declared dimensions](../../08_experiments/_external/p001/specs/Stripe_Products__openapi.yaml:150), output `F065`; [strict-only rule](../../08_experiments/R1_triage_codebook.md:130)।

**v0.3-এর জন্য প্রস্তাব ও খোলা প্রশ্ন**

নিচেরগুলো প্রস্তাব; v0.2 পরিবর্তন করা হয়নি।

1. **Strict oracle বনাম spec coverage আলাদা attribute:** বর্তমান strict-only rule SPEC দেয়, অথচ একই codebook-এর TEST সংজ্ঞায় ভুল oracle আছে। `STRICT_ONLY` বজায় রেখে semantic conformance এবং documentation completeness আলাদা করে রেকর্ড করার নীতি দরকার। উদাহরণ F065-এর declared dimensions ও F010-এর allowed extra fields। উৎস: [TEST সংজ্ঞা](../../08_experiments/R1_triage_codebook.md:34), [strict-only rule](../../08_experiments/R1_triage_codebook.md:130), output `F010`, `F065`।
2. **Mixed cluster-এর aggregation rule:** F004–F006 ও F033/F045-এর মতো response-এ একটি schema defect দৃশ্যমান হলেও অন্য violation-এর intent অজানা। এই labeller পুরো cluster-কে UNDECIDABLE রেখেছে। প্রস্তাব: violation-level সিদ্ধান্ত এবং cluster-level aggregation লিখিতভাবে সংজ্ঞায়িত করা; BOTH পেতে উভয় artifact-এর deviation আলাদাভাবে প্রমাণ করতে হবে। উৎস: [unit definition](../../08_experiments/R1_triage_codebook.md:115), [BOTH](../../08_experiments/R1_triage_codebook.md:33), output-এর উল্লিখিত rows।
3. **Directional developer evidence:** `confirmed`/`fixed`-এর সঙ্গে fix target, issue/commit URL ও সময় সংরক্ষণ করা দরকার। `dev_replied=false` অথচ `dev_fixed=true`-ও input-এ আছে; F046/F061-তে এই metadata-কে definitive attribution ধরা যায়নি। উৎস: [developer-evidence rule](../../08_experiments/R1_triage_codebook.md:42), [blind CSV](../../08_experiments/E2_labelling/p001_foas_blind.csv), `F046`, `F061`।
4. **Null rule ও consistency-এর scope:** একই response-এর array-তে mixed values, একাধিক request-এর mixed values এবং অন্য operation-এর shared schema আলাদা শক্তির evidence। Always-null হলেও explicit documentation সেটি অনুমোদন করতে পারে, যেমন F054-এর image dimensions। প্রস্তাব: scope ও documentation exception স্পষ্ট করা এবং confidence rubric যোগ করা। উৎস: [E-CONSIST](../../08_experiments/R1_triage_codebook.md:54), [TYPE_NULL rule](../../08_experiments/R1_triage_codebook.md:141), output `F022`, `F043`, `F054`, `F056`।
5. **Composition-এর তিনটি পরীক্ষা:** Global unsatisfiability, representative instance-এর একাধিক branch-এ match, এবং converter/validator-এর সমস্যা আলাদা করতে হবে। DHL-এর Date/DateTime definitions দুটোই string; `allOf` নাম দেখেই অসম্ভব বলা যায় না। Stripe-এর parent nullable এবং Spotify-র overlap-এর জন্য আলাদা witness রেকর্ড উপযোগী। উৎস: [composition rule](../../08_experiments/R1_triage_codebook.md:150), [DHL timestamp definitions](../../08_experiments/_external/p001/specs/DHL_LocationFindByAddress__openapi.yaml:756), output `F007`, `F051`, `F062`।
6. **Level-2-তে media/value locus:** Content-Type-এর জন্য S-MEDIA এবং enum/range-এর জন্য S-RESP-VALUE-এর মতো পৃথক subtype বিবেচনা করা যেতে পারে। বর্তমানে F008/F009-তে S-CONFIG এবং F066/F067-তে নিকটতম S-RESP-TYPE ব্যবহৃত হয়েছে। উৎস: [বর্তমান subtype তালিকা](../../08_experiments/R1_triage_codebook.md:74), output-এর উল্লিখিত rows।
7. **E-AUX provenance ও rule priority:** Embedded prose, formal metadata এবং external developer prose-এর ranking ও historical version লিখতে হবে। R1 সব 5xx-এ IMPL চায়, অথচ R4 503-এ ENV দেয়—priority স্পষ্ট করা দরকার। Closed-source code দেখা যায় না বলে constraint অনুপস্থিত ধরে R3 প্রয়োগও করা উচিত নয়। এই ৭৩-row input-এ 503 নেই; এটি codebook পড়ে পাওয়া ambiguity। উৎস: [R1–R5](../../08_experiments/R1_triage_codebook.md:63), [E-AUX](../../08_experiments/R1_triage_codebook.md:135), [blind CSV](../../08_experiments/E2_labelling/p001_foas_blind.csv), `F001`–`F073`।

Coordinator-এর জন্য খোলা বিষয়: historical schema/validator input এবং directional developer response সংগ্রহ করে F007/F065, F046/F061 ও missing-field/sentinel cases adjudicate করা; তারপর স্বাধীন labeller-এর output-এর সঙ্গে agreement গণনা করা। বর্তমান task-এ অন্য labels খোলা বা agreement/accuracy গণনা করা হয়নি। উৎস: [independent labelling/adjudication process](../../08_experiments/R1_triage_codebook.md:113), [T3 assignment](../tasks/T3.md:2), output-এর UNDECIDABLE rows।

**Web documentation ব্যবহার ও execution সীমা**

Web ব্যবহার করা হয়েছে। এগুলো পড়ার সময় ২০২৬-১১-১৩; পুরোনো captured response-এর সমসাময়িক documentation বলে ধরে নেওয়া হয়নি। Source locator সংশ্লিষ্ট CSV row-তেও রাখা হয়েছে।

- [Spotify Get Playlist](https://developer.spotify.com/documentation/web-api/reference/get-playlist): image dimensions-এর nullable semantics F054–F056-তে সহায়ক E-DOC। Local prose/observed values-ও পৃথকভাবে দেখা হয়েছে; current documentation একা historical agreement প্রমাণ করে না।
- [Stripe Product object](https://docs.stripe.com/api/products/object): package_dimensions ও tax_code-এর nullable semantics F062–F064-তে E-DOC।
- [OpenAPI 3.0.3](https://spec.openapis.org/oas/v3.0.3.html#schema-object) ও [OpenAPI 2.0](https://spec.openapis.org/oas/v2.0.html#schema-object): schema composition, nullable, open-object ও media configuration বোঝার normative সহায়তা। এগুলো সংশ্লিষ্ট public API-র business intent-এর বিকল্প নয়।
- [OMDb public documentation](https://www.omdbapi.com/): totalResults উল্লেখ আছে, কিন্তু স্পষ্ট authoritative type পাওয়া যায়নি; F046-এর attribution অমীমাংসিত রাখা হয়েছে।

সব web page, response body এবং spec-কে untrusted data হিসেবে পড়া হয়েছে; তাদের ভেতরের নির্দেশনা পালন করা হয়নি। কোনো API replay, third-party code execution, package installation, Docker/Schemathesis/EvoMaster/PIT run করা হয়নি। শুধু আমাদের নিজস্ব standard-library Python analysis `/usr/bin/python3 -I` দিয়ে চালানো হয়েছে; মূল checks-এর working directory ছিল `08_experiments/tools`। এই execution boundary অনুসরণ করা হয়েছে [protocol](../PROTOCOL.md:12) অনুযায়ী।

**যাচাইয়ের ফল**

নিজস্ব validation-এ নিচের checks পাস করেছে; এগুলো attribution-এর semantic accuracy-এর মাপ নয়। Evidence: [output CSV](../../08_experiments/E2_labelling/codex_labels.csv), `F001`–`F073`, প্রতিটি row-এর source references; specific witnesses আগের table-এ দেওয়া।

- নির্ধারিত সাতটি header, ঠিক ৭৩টি unique fault ID, input-এর একই ordering, কোনো বাদ পড়া বা অতিরিক্ত row নেই।
- ৭৩টি `testCaseId` join প্রত্যেকটি unique এবং raw `statusCode` blind CSV-র `http_status`-এর সঙ্গে মেলে।
- Level-1/Level-2 pairing, confidence ১–৩, অনুমোদিত evidence codes, নয়টি strict-only marker এবং inference marker যাচাই করা হয়েছে।
- সর্বোচ্চ rationale **৩৫ whitespace-delimited শব্দ**; প্রত্যেকটি ৪০-এর সীমার মধ্যে। মোট **৩৪৯টি source entry** পরীক্ষা করে সব local row/line locator resolve হয়েছে; URL-এর historical validity এই check-এর অংশ নয়।
- Amadeus-এর saved escaped pattern `399.00` এবং নিজস্ব example `114.99` দুটোই প্রত্যাখ্যান করে; এক level unescape করলে দুটোই মেলে। এটি সীমিত regex diagnostic, ECMA-262 engine run নয়। উৎস: [saved pattern](../../08_experiments/_external/p001/specs/Amadeus__openapi.json:1218), [example](../../08_experiments/_external/p001/specs/Amadeus__openapi.json:1573)।
- F047-এর raw body standard-library JSON parser-এ decode হয় না। Spotify-র চারটি representative object-এর আটটি branch check মেলে; checker-এর scope ও raw IDs আগের table-এ আছে।

অবশিষ্ট সীমা হলো developer fix direction, কিছু field/sentinel-এর intended semantics, historical artifact equivalence এবং live reproducibility। এগুলো অনুমান দিয়ে পূরণ করা হয়নি; সংশ্লিষ্ট uncertainty rationale ও confidence-এ রাখা হয়েছে। উৎস: output `F004`–`F007`, `F019`, `F022`–`F024`, `F032`–`F034`, `F044`–`F046`, `F061`, `F070`; historical documentation-সংক্রান্ত সীমা `F054`–`F056`, `F062`–`F064`।
