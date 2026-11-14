**T13 — codebook v0.3 অনুযায়ী P001 F_OAS-এর message-level re-labelling**

৭৩টি fault-এর **৫৭৪টি raw violation message** label করা হয়েছে। Message-স্তরে SPEC ৪৭০, TEST ৬৬, UNDECIDABLE ২৮, ENV ৯ এবং IMPL ১; cluster-স্তরে SPEC ২৫, SPEC_PARTIAL ৭, UNDECIDABLE ২২, TEST ৯, ENV ৯ এবং IMPL ১। এগুলো এই labeller-এর attribution; adjudicated ground truth নয়। উৎস: [message CSV](../../08_experiments/E2_labelling/codex_labels_v03_messages.csv), `(fault_id,msg_idx)=F001:1`–`F073:2`; [cluster CSV](../../08_experiments/E2_labelling/codex_labels_v03.csv), `fault_id=F001`–`F073`; [ground-truth সীমা](../../08_experiments/R1_triage_codebook.md:212)।

**কাজের পদ্ধতি ও blinding audit**

[T13 assignment](../tasks/T13.md:1), [protocol](../PROTOCOL.md:1) এবং [codebook §9](../../08_experiments/R1_triage_codebook.md:154) অনুসরণ করে blind input-এর প্রতিটি `testCaseId` সংশ্লিষ্ট raw CSV-তে unique join করা হয়েছে। প্রতিটি raw `failReason` ঠিক ` --- ` দিয়ে split করা; `msg_idx` **১ থেকে শুরু**, raw ordering, প্রথম message-এর `OAS disconformity:` prefix এবং F047-এর newline অপরিবর্তিত রাখা হয়েছে। `sources`-এর `#fault_id=` / `#testCaseId=` logical CSV row locator; schema ও report-এর `:number` physical line locator। উৎস: দুই output CSV-র header ও সব row; [raw Amadeus](../../08_experiments/_external/p001/faultClustersConfirmedBugs_amadeus.csv), `testCaseId=test_rl8drizqvygo_getMultiHotelOffers`; [raw OMDb](../../08_experiments/_external/p001/faultClustersConfirmedBugs_omdb.csv), `testCaseId=test_1iv3rat0bqo1d_search`।

Blind CSV-র `messages` **১৯টি fault-এ ৬০০ character-এ truncated**: F001, F003–F007, F017–F019, F021, F023, F032–F034, F043, F045, F052, F053, F055। প্রতিটি truncated string পূর্ণ normalized raw message sequence-এর prefix; তাই labelling-এ সম্পূর্ণ raw message নেওয়া হয়েছে। উৎস: [blind input](../../08_experiments/E2_labelling/p001_foas_blind.csv), উল্লিখিত `fault_id`; [message output](../../08_experiments/E2_labelling/codex_labels_v03_messages.csv), একই fault-গুলোর সব `msg_idx`; প্রতিটি output row-এর raw source locator।

নিষিদ্ধ `triage_output*.csv`, `triage_messages*.csv`, `comparison_rule_triage_codex.csv`, `p001_foas_labelling_sheet.csv`, `build_labelling_sheet.py`, `T2_report.md`, `T11_report.md` খোলা হয়নি। অনুমোদিত নিজের [v0.2 CSV](../../08_experiments/E2_labelling/codex_labels.csv), `F001`–`F073`, এবং [T3 report](T3_report.md:1) evidence note হিসেবে পুনর্ব্যবহার করা হয়েছে। **পূর্ণ blinding দাবি করা হচ্ছে না**: বাধ্যতামূলক initial board read-এ T11-এর summary distribution ও review প্রকাশিত ছিল; exposure কাজ শুরুর log-এ লেখা হয়েছে। সেগুলো message attribution-এর evidence হিসেবে ব্যবহার করা হয়নি। প্রক্রিয়ার উৎস: [T13-এর নিষেধাজ্ঞা](../tasks/T13.md:2), [বাধ্যতামূলক board নির্দেশ](../../AGENTS.md:2), [board](../COLLAB_BOARD.md), `T13` row ও `2026-11-14 02:02 +06 | Codex | T13` log।

**বণ্টন ও aggregation**

নিচের সংখ্যা দুই output CSV-র সব row থেকে গণনা করা। Strict ও lenient column শুধু §9.1-এর partial-label mapping; অন্য labeller-এর সঙ্গে agreement বা accuracy গণনা করা হয়নি। উৎস: [message CSV](../../08_experiments/E2_labelling/codex_labels_v03_messages.csv), `F001:1`–`F073:2`; [cluster CSV](../../08_experiments/E2_labelling/codex_labels_v03.csv), `F001`–`F073`; [mapping rule](../../08_experiments/R1_triage_codebook.md:171)।

| L1 | Message | Cluster, native | Cluster, strict | Cluster, lenient |
|---|---:|---:|---:|---:|
| SPEC | 470 | 25 | 25 | 32 |
| IMPL | 1 | 1 | 1 | 1 |
| ENV | 9 | 9 | 9 | 9 |
| TEST | 66 | 9 | 9 | 9 |
| BOTH | 0 | 0 | 0 | 0 |
| SPEC_PARTIAL | প্রযোজ্য নয় | 7 | 0 | 0 |
| IMPL_PARTIAL | প্রযোজ্য নয় | 0 | 0 | 0 |
| UNDECIDABLE | 28 | 22 | 29 | 22 |
| মোট | 574 | 73 | 73 | 73 |

| Message L2 | সংখ্যা |
|---|---:|
| S-RESP-TYPE | 439 |
| T-ORACLE-STRICT | 66 |
| S-STATUS | 12 |
| S-STRUCT | 9 |
| S-RESP-VALUE | 8 |
| S-MEDIA | 2 |
| I-RESP-CONTRACT | 1 |
| খালি: ENV / UNDECIDABLE | 37 |

**৫৪৬টি message decided**, বাকি ২৮টি UNDECIDABLE। `n_decided`-এ TEST-ও decided; cluster L1 অনির্ধারিত হলেও message-level সিদ্ধান্ত বাদ দেওয়া হয়নি। `label_L2` হলো message-order অনুযায়ী decided L2-গুলোর unique semicolon-separated union; তাই mixed UNDECIDABLE cluster-এও পরিচিত locus আছে। এটি output convention, codebook-এর অতিরিক্ত attribution rule নয়। উৎস: [cluster CSV](../../08_experiments/E2_labelling/codex_labels_v03.csv), সব row, বিশেষত `F007`, `F049`, `F061`; [message CSV](../../08_experiments/E2_labelling/codex_labels_v03_messages.csv), সংশ্লিষ্ট fault-গুলোর rows।

⚠️ **Aggregation table-এর gap:** §9.1-এ TEST+SPEC, TEST+UNDECIDABLE এবং TEST+SPEC+UNDECIDABLE-এর cell নেই। এই **১৮টি cluster-এ provisional UNDECIDABLE** ব্যবহার করেছি; message label ও `n_decided` অক্ষত। TEST-কে বাদ দিয়ে SPEC_PARTIAL বা SPEC বানানো হয়নি। এটি conservative operational interpretation; codebook-এ এমন mixed combination-এর নির্ধারিত verdict আছে বলে দাবি নয়। উৎস: [aggregation table](../../08_experiments/R1_triage_codebook.md:163); নিচের IDs দুই output CSV-তেই আছে।

| অনুল্লিখিত message combination | সংখ্যা | Fault IDs |
|---|---:|---|
| SPEC + TEST; সব message decided | 14 | F049–F053, F055–F060, F062–F064 |
| TEST + UNDECIDABLE | 1 | F019 |
| SPEC + TEST + UNDECIDABLE | 3 | F007, F023, F032 |

অন্য চারটি native UNDECIDABLE cluster-এ কোনো message decided নয়: **F024, F044, F046, F070**। সাতটি SPEC_PARTIAL হলো **F004–F006, F033, F034, F045, F061**; প্রতিটিতে কেবল SPEC ও UNDECIDABLE message আছে। উৎস: [cluster CSV](../../08_experiments/E2_labelling/codex_labels_v03.csv), উল্লিখিত IDs; [message aggregation rule](../../08_experiments/R1_triage_codebook.md:165)।

**নিজের v0.2 label থেকে পরিবর্তন**

Native L1-এ **৩১টি বদলেছে, ৪২টি অপরিবর্তিত**। নিচের transition-গুলো [নিজের v0.2 CSV](../../08_experiments/E2_labelling/codex_labels.csv), `F001`–`F073`, এবং [v0.3 cluster CSV](../../08_experiments/E2_labelling/codex_labels_v03.csv), একই IDs, সরাসরি join করে গণনা করা। Labelling rule ও evidence scope বদলের কারণে এই পরিবর্তনকে attribution accuracy-র উন্নতি বলা যাচ্ছে না।

| v0.2 → v0.3 | সংখ্যা | Fault IDs |
|---|---:|---|
| SPEC → SPEC | 24 | F001–F003, F008, F009, F012, F014, F020, F021, F025–F031, F035, F036, F043, F054, F066–F069 |
| SPEC → TEST | 9 | F010, F011, F015–F018, F065, F072, F073 |
| SPEC → UNDECIDABLE | 14 | F049–F053, F055–F060, F062–F064 |
| UNDECIDABLE → SPEC_PARTIAL | 7 | F004–F006, F033, F034, F045, F061 |
| UNDECIDABLE → SPEC | 1 | F022 |
| UNDECIDABLE → UNDECIDABLE | 8 | F007, F019, F023, F024, F032, F044, F046, F070 |
| ENV → ENV | 9 | F013, F037–F042, F048, F071 |
| IMPL → IMPL | 1 | F047 |

- **Strict-only rule বদল:** আগের নয়টি strict-only SPEC এখন TEST/T-ORACLE-STRICT। আরও ১৮টি mixed fault-সহ মোট **২৭টি fault-এর ৬৬টি property diagnostic** TEST। এটি §9.2-এর oracle-policy attribution। উৎস: [নতুন rule](../../08_experiments/R1_triage_codebook.md:177), [পুরোনো অবস্থান](T3_report.md:37), [message CSV](../../08_experiments/E2_labelling/codex_labels_v03_messages.csv), `L2=T-ORACLE-STRICT` rows।
- **Partial সিদ্ধান্ত আলাদা করা:** F004–F006-এ broken decimal pattern প্রমাণিত, fax-এর optionality অজানা; F033/F034/F045-এ স্বাভাবিক timestamp-এর schema mismatch আছে, negative-year sentinel-এর intent অজানা; F061-এ href-এর nullable prose আছে, total-এর নেই। তাই SPEC_PARTIAL। উৎস: message CSV `F004:1`–`F006:82`, `F033:1`–`F034:62`, `F045:1`–`F045:65`, `F061:1`–`F061:2`; [fax](../../08_experiments/_external/p001/specs/Amadeus__openapi.json:753), [ComicDate](../../08_experiments/_external/p001/specs/Marvel__openapi.yaml:4270), [FollowersObject](../../08_experiments/_external/p001/specs/Spotify_Playlists__openapi.yaml:5430)।
- **Mixed oracle/spec ফল:** উপরের ১৪টি পুরোনো SPEC fault-এ substantive SPEC message এখনো আছে; TEST message-সহ aggregation অনির্দিষ্ট হওয়ায় cluster UNDECIDABLE। উৎস: message ও cluster CSV-র transition table-এ উল্লিখিত ১৪টি ID; [§9.1](../../08_experiments/R1_triage_codebook.md:163)।
- ⚠️ **F022 নতুন SPEC:** individual-character `modified` timestamp-এর সঙ্গে F021-এর একই `Character` schema-র character-list serialization মিলিয়েছি; **E-CROSS, confidence 2**। T3-তে E-CROSS ব্যবহার করা হয়নি; বর্তমান task-এ §3-এর code প্রযোজ্য। F023/F032-এর `modified` message-এও E-CROSS ব্যবহার হয়েছে, তবে অন্য unresolved/TEST message-এর কারণে cluster UNDECIDABLE আছে। উৎস: message CSV `F022:1`, `F023:2`–`F023:9`, `F032:3`–`F032:4`; [shared Character.modified](../../08_experiments/_external/p001/specs/Marvel__openapi.yaml:4580), [cross-operation evidence](../../08_experiments/R1_triage_codebook.md:57), [T3 restriction note](T3_report.md:55)।
- **নতুন L2:** F008/F009-এর S-CONFIG → **S-MEDIA**; F066/F067-এর S-RESP-TYPE → **S-RESP-VALUE**। F069-এ nullable coordinates-এর S-RESP-TYPE ও price enum-এর S-RESP-VALUE দুটোই সংরক্ষিত। F007-এর weekday-URL message-ও S-RESP-VALUE। উৎস: দুই label CSV-র সংশ্লিষ্ট IDs; message CSV `F007:6`, `F008:1`, `F009:1`, `F066:1`–`F067:3`, `F069:1`–`F069:4`; [নতুন L2](../../08_experiments/R1_triage_codebook.md:194)।

F047-এর malformed JSON IMPL/I-RESP-CONTRACT এবং নয়টি ENV অপরিবর্তিত। ENV-এর আটটি 429/quota response; F048-এর 403 body-তে Cloudflare block page আছে। Developer `confirmed`/`fixed` flags-কে fix direction ধরা হয়নি; closed-source code-এ constraint অনুপস্থিত অনুমান করেও R3 প্রয়োগ করিনি। উৎস: message CSV `F047:1`, `F048:1`, `F013:1`, `F037:1`–`F042:1`, `F071:1`, এবং `F002:1`, `F046:1`, `F061:2`; [§9.3](../../08_experiments/R1_triage_codebook.md:185)।

**Evidence, confidence ও documentation gap**

| Evidence code | Message-এ ব্যবহার |
|---|---:|
| E-AUX | 270 |
| E-CONSIST | 251 |
| E-CONV | 22 |
| E-DOC | 13 |
| E-CROSS | 11 |
| E-DEV | 6 |
| E-CODE-INTENT | 0 |

এক message-এ একাধিক code থাকতে পারে। E-AUX-এ saved prose/example/header default ব্যবহার হয়েছে; E-DOC কেবল public API documentation। অপর্যাপ্ত independent intent থাকলে evidence code খালি রাখা হয়েছে, raw/schema source বাদ যায়নি। উৎস: [message CSV](../../08_experiments/E2_labelling/codex_labels_v03_messages.csv), সব row-এর `evidence_codes` ও `sources`; evidence সংজ্ঞা: [§3](../../08_experiments/R1_triage_codebook.md:38), [E-AUX](../../08_experiments/R1_triage_codebook.md:135)।

Confidence distribution: message-এ **1=28, 2=285, 3=261**; cluster-এ **1=29, 2=24, 3=20**। Operational rubric: 1=unresolved message/aggregation; 2=consistency/cross-operation inference বা historical uncertainty; 3=স্পষ্ট local contradiction অথবা সরাসরি codebook policy। Uniform cluster-এ সর্বনিম্ন message confidence, partial/unresolved cluster-এ 1। এটি calibrated probability বা codebook-এর সম্পূর্ণ নির্ধারিত rubric নয়। উৎস: দুই output CSV-র `confidence`; codebook-এ range: [record format](../../08_experiments/R1_triage_codebook.md:120), web cap: [§9.3](../../08_experiments/R1_triage_codebook.md:186)।

সব **১৩টি E-DOC message confidence 2**; `sources`-এ URL-এর পাশে `[retrieved=2026-11-14]` আছে। Retrieval date Asia/Dhaka অনুযায়ী; documentation-কে পুরোনো captured response-এর সমসাময়িক snapshot ধরা হয়নি। ব্যবহৃত public evidence:

- Spotify-এর ImageObject-এ nullable dimensions: [Get Playlist](https://developer.spotify.com/documentation/web-api/reference/get-playlist), retrieved 2026-11-14। প্রয়োগ: message CSV `F054:1`–`F054:2`, `F055:3`–`F055:4`, `F056:2`–`F056:3`; saved [ImageObject](../../08_experiments/_external/p001/specs/Spotify_Playlists__openapi.yaml:5482)।
- Stripe-এর nullable `package_dimensions` ও `tax_code`: [Product object](https://docs.stripe.com/api/products/object), retrieved 2026-11-14। প্রয়োগ: `F062:2`–`F062:3`, `F063:2`, `F063:4`, `F064:2`; saved [composition](../../08_experiments/_external/p001/specs/Stripe_Products__openapi.yaml:88)।
- YouTube-এর documented thumbnail key `default`: [Search resource](https://developers.google.com/youtube/data/reference/rest/v3/search#snippet.thumbnails), retrieved 2026-11-14। প্রয়োগ: `F072:2`, `F073:2`; saved [CommentsAndThreads ThumbnailDetails](../../08_experiments/_external/p001/specs/YouTube_CommentsAndThreads__openapi.yaml:8626), [Search ThumbnailDetails](../../08_experiments/_external/p001/specs/YouTube_Search__openapi.yaml:8613)।

Property message-গুলোর `doc_gap`: **true=2, false=2, unknown=62**। `true` হলো YouTube-এর দুই `thumbnails.default` message; `false` হলো Stripe F063:3/F065:2, যেখানে চার dimension ইতিমধ্যে saved schema-তে declared। বাকি property message-এ public coverage প্রতিষ্ঠিত হয়নি; একটি বর্তমান page-এ field খুঁজে না পাওয়াকে false বানাইনি। অন্য ধরনের ৫০৮টি message-এ `unknown` neutral placeholder; documentation completeness সেখানে এই annotation-এর বিষয় নয়। উৎস: message CSV-র `L1=TEST` ও `doc_gap` columns; [gap definition](../../08_experiments/R1_triage_codebook.md:180), [declared dimensions](../../08_experiments/_external/p001/specs/Stripe_Products__openapi.yaml:150)।

**Composition witness ও অবশিষ্ট codebook ambiguity**

Spotify oneOf-এর জন্য অনুমোদিত T3 evidence note পুনর্ব্যবহার করেছি: raw first-track IDs **F051=295X5cd7nBzFNrgn77FyGK, F052=3JbzCex8HkQSkgwXq0i6NC, F053=1X4l4i472kW5ofFP8Xo0x0, F055=0A8rvkDkZRTH3UgYGWxFnp**। এই task-এ raw ID/type পুনরায় মিলিয়েছি; branch matching-এর আগের সীমিত checker নতুন করে চালাইনি। Saved optional-field TrackObject/EpisodeObject-এর instance overlap হলো SPEC/S-STRUCT, confidence 2-এর evidence। পুরো schema globally unsatisfiable বলা হয়নি; historical diagnostic-এর `matched 0` ও saved witness-এর দুই branch match-এর পার্থক্য রয়ে গেছে। উৎস: message CSV `F051:2`, `F052:2`, `F053:4`, `F055:6`; [T3 witness ও checker scope](T3_report.md:77); [oneOf](../../08_experiments/_external/p001/specs/Spotify_Playlists__openapi.yaml:5770), [§9.5](../../08_experiments/R1_triage_codebook.md:199)।

Stripe-এর null witness-এ parent `nullable:true`-এর একই level-এ `type` নেই এবং composition branches null গ্রহণ করে না। Local annotation ও public prose nullable intent সমর্থন করে; schema encoding-এর correction দরকার বলে SPEC/S-STRUCT। Normative সহায়তা: [OpenAPI 3.0.3 Schema Object](https://spec.openapis.org/oas/v3.0.3.html#schema-object), retrieved 2026-11-14; local [package_dimensions](../../08_experiments/_external/p001/specs/Stripe_Products__openapi.yaml:88), [tax_code](../../08_experiments/_external/p001/specs/Stripe_Products__openapi.yaml:107); message CSV `F062:2`–`F062:3`, `F063:2`, `F063:4`, `F064:2`।

চূড়ান্ত adjudication-এর জন্য বাকি বিষয়গুলো:

1. **Mixed TEST aggregation:** উপরের ১৮টি cluster-এর জন্য §9.1-এর নতুন cell দরকার। সব message decided অথচ cluster UNDECIDABLE—এই পার্থক্য downstream scoring-এ দৃশ্যমান রাখা জরুরি। উৎস: aggregation-gap table; cluster CSV-তে `F049`–`F053`, `F055`–`F060`, `F062`–`F064`-এর `n_decided=n_messages`।
2. **Evidence scope ও confidence:** একই response-এর array consistency, একাধিক request এবং E-CROSS কতটা শক্তিশালী—codebook-এ নির্দিষ্ট threshold নেই। এখানে F022-এ E-CROSS গ্রহণ করেছি; সবসময়-null Story.thumbnail/Series links-এ intent অজানা রেখেছি। উৎস: message CSV `F022:1`, `F023:10`, `F032:2`, `F032:5`–`F032:6`; [§3](../../08_experiments/R1_triage_codebook.md:54), [null rule](../../08_experiments/R1_triage_codebook.md:141)।
3. **Declared-property diagnostic-এর subtype:** F063:3/F065:2-এ dimension declared থাকা সত্ত্বেও property rejection। Task-এর নির্দেশ অনুযায়ী TEST/T-ORACLE-STRICT; কিন্তু subtype-টি converter/snapshot সমস্যা ও প্রকৃত undeclared-property strictness আলাদা করে না। [H] Historical converter বা schema snapshot ভিন্ন হতে পারে; বর্তমান evidence-এ কারণ নির্ধারিত নয়। উৎস: সংশ্লিষ্ট message rows ও [schema](../../08_experiments/_external/p001/specs/Stripe_Products__openapi.yaml:150); [§9.2](../../08_experiments/R1_triage_codebook.md:178)।
4. **Multi-property doc_gap:** একটি diagnostic-এ অনেক property থাকতে পারে; কিছু documented/declared এবং কিছু অজানা হলে boolean aggregation rule নেই। Unverified group-এ unknown ব্যবহার করেছি। উৎস: message CSV `F051:3`, `F052:3`–`F052:4`; [attribute definition](../../08_experiments/R1_triage_codebook.md:180)।
5. **Historical validator input:** DHL-এর countryCode diagnostic object চায়, saved schema string; Timestamp/Time-এর allOf-ও saved string schemas দিয়ে zero-match ব্যাখ্যা করা যায় না। Attribution UNDECIDABLE রাখা হয়েছে। উৎস: message CSV `F007:2`–`F007:3`, `F007:5`, `F007:7`, `F007:9`; [countryCode](../../08_experiments/_external/p001/specs/DHL_LocationFindByAddress__openapi.yaml:662), [Time/DataType](../../08_experiments/_external/p001/specs/DHL_LocationFindByAddress__openapi.yaml:705), [Timestamp](../../08_experiments/_external/p001/specs/DHL_LocationFindByAddress__openapi.yaml:756)।
6. **Unresolved value intent:** negative-year timestamp, diamondCode=0, offset overflow, totalResults string, followers.total=null ও rating=0-এর definitive intent/fix direction বাকি। Marvel-এর সাধারণ timestamp-গুলো date-only declaration-এর ঘাটতি সমর্থন করে; সেগুলোকে স্বয়ংক্রিয়ভাবে RFC3339 date-time-compatible বলা হয়নি। উৎস: message CSV `F033:1`, `F034:1`, `F034:47`, `F045:1`, `F045:51`–`F045:52`, `F044:1`, `F046:1`, `F061:2`, `F070:1`; সংশ্লিষ্ট rows-এর raw/schema locators।

**যাচাই ও সংরক্ষিত provenance**

নিজস্ব standard-library Python audit `/usr/bin/python3 -I -` দিয়ে `08_experiments/tools` working directory থেকে চালানো হয়েছে; final result **ALL_VALIDATION_CHECKS_PASS**। নতুন test file বা অন্য task-এর tool পরিবর্তন করা হয়নি। Audit-এর যাচাইযোগ্য data evidence হলো দুই output CSV এবং প্রতিটি row-এর source locators; command-এর assertions output header, logical join ও নিচের constraints পরীক্ষা করেছে। Execution সীমা: [protocol](../PROTOCOL.md:12), allowed outputs: [T13](../tasks/T13.md:12)।

- ঠিক ৭৩টি unique fault, ৫৭৪টি unique `(fault_id,msg_idx)`; প্রতিটি পূর্ণ parsed raw message ও ordering-এর exact string equality, ৭৩টি unique raw join এবং status মিলেছে। Truncated blind text-ও raw normalized prefix-এর সঙ্গে মেলে। উৎস: দুই output CSV-র সব row; blind input-এর সব `fault_id`; output-এর raw `#testCaseId` locators।
- L1/L2 pairing, evidence code vocabulary, tri-state doc_gap, confidence 1–3, সব E-DOC confidence ≤2 ও dated URL, সব rationale ≤30 whitespace-delimited শব্দ; বাস্তব সর্বোচ্চ **২৭ শব্দ**। Local source line/row resolution এবং মোট **২,৬১৩ source entry** পরীক্ষা হয়েছে; URL-এর syntactic presence check historical validity প্রমাণ করে না। উৎস: message CSV-র সব row-এর সংশ্লিষ্ট columns; [§9.3](../../08_experiments/R1_triage_codebook.md:185)।
- Cluster aggregation, `n_messages`, `n_decided`, L2 union ও confidence convention message CSV থেকে পুনরায় গণনা করে cluster CSV-র সঙ্গে মিলেছে; ৬৬টি property diagnostic TEST ও আটটি 429 ENV। উৎস: দুই output CSV-র সব row; [§9.1–§9.3](../../08_experiments/R1_triage_codebook.md:159)।
- Amadeus-এর ছয়টি প্রাসঙ্গিক pattern declaration `114.99` প্রত্যাখ্যান করে; এক level unescape করলে গ্রহণ করে। এটি standard-library regex diagnostic, ECMA-262 engine replay নয়। F047-এর raw body standard-library JSON parser-এ decode হয় না। উৎস: [BaseTotalAmount](../../08_experiments/_external/p001/specs/Amadeus__openapi.json:1218), [PriceVariation](../../08_experiments/_external/p001/specs/Amadeus__openapi.json:1245), [Commission](../../08_experiments/_external/p001/specs/Amadeus__openapi.json:922), [CancellationPolicy](../../08_experiments/_external/p001/specs/Amadeus__openapi.json:1128), message CSV `F047:1`-এর raw source।

Labels final validation-এর পর নিচের SHA-256-এ সংরক্ষিত; নিজের v0.2 CSV-র hash T3 report-এর frozen hash-এর সঙ্গে অপরিবর্তিত মেলে। উৎস: উল্লিখিত files-এর bytes; [পুরোনো frozen hash](T3_report.md:7)।

| Artifact | SHA-256 |
|---|---|
| `08_experiments/E2_labelling/p001_foas_blind.csv` | `9caabc2e42b9dc57f649e844d8829b21628e99f9d3d086e5257b575e9a761d25` |
| `08_experiments/E2_labelling/codex_labels.csv` | `64b860aa89d81de2ba301c953eccc78ce8ec47059b24a84e96f7e9b33aa8b6a6` |
| `08_experiments/E2_labelling/codex_labels_v03_messages.csv` | `eb942f937872c59b235a0bfbbd4bb691175f10edce57e5373554e04665c9aea9` |
| `08_experiments/E2_labelling/codex_labels_v03.csv` | `e81ff35342ef423bcb4f004f0001d66cbf94300e7863ef40b7f4357baeeee4c8` |

External SUT/tool code execution, package installation বা API replay করা হয়নি। Web/spec/response content data হিসেবে পড়া হয়েছে। Historical artifact equivalence, complete composition validation ও human adjudication এই কাজের বাকি সীমা; deliverables সম্পূর্ণ, তবে উপরের ১৮টি mixed aggregation-এর policy decision coordinator-এর জন্য উন্মুক্ত। উৎস: [protocol execution/trust boundary](../PROTOCOL.md:10), [task scope](../tasks/T13.md:5), composition ও aggregation-এর উপরের নির্দিষ্ট evidence locators।
