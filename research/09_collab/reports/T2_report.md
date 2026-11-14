# T2 — Evidence-based triage classifier prototype

তারিখ: 2026-11-13 · Agent: Codex · Task: `09_collab/tasks/T2.md:4`।

## কী করা হয়েছে

`triage.py` library ও তিন-argument CLI, stdlib `unittest` suite, এবং P001-এর ৭৩-row output তৈরি হয়েছে। CLI মূল sheet-এর columns রেখে `label_L1`, `label_L2`, `confidence`, `evidence_codes`, `rules`, `evidence_refs`, `evidence_details`, `unresolved`, `spec_limitation`, `note`, `codebook_ref` যোগ করে। Raw CSV join হয় `(api, testCaseId)` দিয়ে; status ও operation mismatch হলে execution থামে। Evidence references-এ raw file ও `testCaseId`, sheet-এর `fault_id`, এবং প্রযোজ্য spec pointer থাকে। সূত্র: `08_experiments/tools/triage.py:159`, `:521`, `:603`; output: `08_experiments/E2_labelling/triage_output.csv`, rows F001–F073।

⚠️ SPEC/ENV attribution-গুলো codebook-ভিত্তিক inference; output নতুন ground truth নয়। Baseline-এর `suggested_*` columns সিদ্ধান্তের input নয়: classifier raw evidence ও `strict_only` পড়ে; baseline columns comparison-এর জন্য রাখা হয়েছে। সূত্র: `08_experiments/tools/triage.py:521`, `:603`; `08_experiments/E2_labelling/README.md:5`।

## নিয়ম ও evidence

প্রতিটি feature-এর implementation docstring-এ codebook section আছে; নিচের সব path repository root থেকে। সূত্র: `08_experiments/tools/triage.py:99`, `:106`, `:131`, `:219`, `:271`, `:377`, `:470`, `:490`।

| Feature / rule | সিদ্ধান্তের শর্ত ও confidence | Evidence / implementation | Synthetic tests |
|---|---|---|---|
| `STRICT_ONLY` | Given flag true হলে SPEC / S-RESP-MISSING, 2; default OAS semantics-এর চেয়ে কঠোর validation | §8.1; E-AUX; `08_experiments/tools/triage.py:99` | `08_experiments/tools/test_triage.py:44`, `:253` |
| `DOUBLE_ESCAPE` | Original regex value-কে reject করে এবং double escape সরালে match করে → SPEC / S-RESP-TYPE, 3 | §8.4; E-AUX; `08_experiments/tools/triage.py:106` | `08_experiments/tools/test_triage.py:49`, `:54`, `:58`, `:65` |
| `JAVA_REGEX` | Reported pattern-এ Unicode-property dialect syntax → SPEC / S-STRUCT, 2; arbitrary Python regex error দিয়ে সিদ্ধান্ত নয় | §8.4; E-AUX; `08_experiments/tools/triage.py:106` | `08_experiments/tools/test_triage.py:61` |
| `NULL_MIXED` | একই exact JSON path-এ null ও non-null, অন্তত দুই response representative → SPEC / S-RESP-TYPE, 1 | §8.3; E-CONSIST; API-wide fallback-এ E-CROSS-ও; `08_experiments/tools/triage.py:219` | `08_experiments/tools/test_triage.py:82`, `:89`, `:94`, `:98`, `:103`, `:107` |
| `PROPERTY_STABLE` | Extra property সব applicable parent object-এ উপস্থিত, অন্তত দুই response → SPEC lean / S-RESP-MISSING, 1 | §3/R2; E-CONSIST; code intent নেই বলে confidence কম; `08_experiments/tools/triage.py:219` | `08_experiments/tools/test_triage.py:113` |
| `ALT_DATE_FORMAT` | Calendar-valid ISO/common alternative date বা timestamp → SPEC lean / S-RESP-TYPE, 1 | §4 ও §3/E-CONV; `08_experiments/tools/triage.py:131` | `08_experiments/tools/test_triage.py:68`, `:74` |
| `STATUS_CROSS_DOCUMENTED` | P001 অনুযায়ী valid input; nonempty error object; একই spec-এর অন্য operation-এ একই status documented → SPEC / S-STATUS; matching schema থাকলে 2, শুধু description থাকলে 1 | §3/E-CROSS ও §4; E-AUX-ও; `08_experiments/tools/triage.py:377` | `08_experiments/tools/test_triage.py:154`, `:162`, `:169`, `:176`, `:183` |
| `OUTLIER_REPEATED` | ENUM বা NUMERIC_RANGE-এর reported outlier প্রকৃত response-এ আছে এবং একই value আরেক response-এ আছে → SPEC lean / S-RESP-TYPE, 1 | §3/E-CONSIST ও §4; `08_experiments/tools/triage.py:271` | `08_experiments/tools/test_triage.py:126`, `:134`, `:141`, `:148` |
| `COMPOSITION_UNSAT` | Local spec load করে failure path-এর schema-তে sufficient contradiction proof → SPEC / S-STRUCT, 2 | §8.4–8.5; E-AUX; `08_experiments/tools/triage.py:429`, `:470` | `08_experiments/tools/test_triage.py:192`, `:198`, `:204`, `:210` |
| `NULL_DOCUMENTED_PROSE` | অতিরিক্ত evidence rule: typed, non-nullable schema-র description স্পষ্টভাবে null অনুমোদন করে এবং response null → SPEC / S-RESP-TYPE, 2 | §3 evidence hierarchy ও §8.3; E-AUX, external E-DOC নয়; `08_experiments/tools/triage.py:490` | `08_experiments/tools/test_triage.py:218`, `:224` |

Consistency-তে operation-local evidence অগ্রাধিকার পায়; যথেষ্ট evidence না পেলে একই API-র একই exact path দেখা হয়। ভিন্ন API, ভিন্ন response status class, missing field, empty array, একই body-র বহু item, বা `totalFailures`-কে নতুন response হিসেবে গণনা করা হয় না। Numeric array index সাধারণীকৃত হয়; JSON pointer escaping সমর্থিত। সূত্র: `08_experiments/tools/triage.py:67`, `:159`, `:219`; tests: `08_experiments/tools/test_triage.py:94`, `:103`, `:107`, `:121`।

Pattern/structural proof ছাড়া cluster-এর সব distinct message supported হতে হয়। Unknown message থাকলে supported subfinding evidence-এ থাকে, কিন্তু cluster UNDECIDABLE। Proven pattern/structural defect থাকলে SPEC decision রাখা হয়; residual message-গুলো `unresolved`-এ থাকে এবং `note` বলে confidence শুধু proven defect-এর। সূত্র: `08_experiments/tools/triage.py:521`; tests: `08_experiments/tools/test_triage.py:246`, `:291`।

Baseline-এর auth/invalid-input undocumented status এবং media-type SPEC lean রাখা হয়েছে। 429 ও 503-এ R4/ENV আগে প্রয়োগ হয়; অন্য 5xx-এ R1/I-CRASH। Response mismatch থেকে IMPL অনুমান করা হয় না। R1 ও R4-এর 503 overlap-এ এটি explicit policy choice। সূত্র: `08_experiments/tools/triage.py:521`; `08_experiments/R1_triage_codebook.md:63`; tests: `08_experiments/tools/test_triage.py:234`, `:240`।

## ফল: baseline বনাম triage

নিচের crosstab একই output-এর `suggested_L1 × suggested_confidence` এবং `label_L1 × confidence` থেকে গণনা। Baseline-এর UNDECIDABLE confidence sheet-এ 1; README-র summary-তে dash ছিল। Evidence: `08_experiments/E2_labelling/triage_output.csv`, rows F001–F073; baseline context: `08_experiments/E2_labelling/README.md:16`।

| L1 | Baseline c1 | Baseline c2 | Baseline c3 | Baseline total | Triage c1 | Triage c2 | Triage c3 | Triage total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SPEC | 12 | 20 | 5 | 37 | 17 | 12 | 5 | 34 |
| IMPL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| BOTH | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TEST | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ENV | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 8 |
| UNDECIDABLE | 36 | 0 | 0 | 36 | 31 | 0 | 0 | 31 |
| Total | 48 | 20 | 5 | 73 | 48 | 20 | 5 | 73 |

UNDECIDABLE 36/73 → 31/73: net 5 কমেছে, অর্থাৎ undecided count-এর 13.9% হ্রাস। Transition: UNDECIDABLE→SPEC 9, SPEC→UNDECIDABLE 4, SPEC→ENV 8, SPEC→SPEC 25, UNDECIDABLE→UNDECIDABLE 27। Evidence: `08_experiments/E2_labelling/triage_output.csv`, rows F001–F073, বিশেষ করে নিচের change tables।

### প্রত্যেক UNDECIDABLE → decided পরিবর্তন

প্রতিটি row-এর নতুন attribution ⚠️ inference। সব নতুন decision confidence 1; raw evidence-এর পূর্ণ references output-এর `evidence_refs`-এ আছে। Table-এর CSV evidence বলতে `08_experiments/E2_labelling/triage_output.csv`-এর উল্লেখিত `fault_id` row বোঝায়।

| fault_id | নতুন L1 / L2 / confidence | Rule | নির্দিষ্ট evidence |
|---|---|---|---|
| F020 | ⚠️ SPEC / S-RESP-TYPE / 1 | `ALT_DATE_FORMAT` | CSV row F020; `08_experiments/_external/p001/faultClustersConfirmedBugs_marvel.csv`, testCaseId=`test_1hbg0bpw4ur1g_getCharacterEventsCollection`; valid space-separated ও compact-offset timestamps |
| F021 | ⚠️ SPEC / S-RESP-TYPE / 1 | `ALT_DATE_FORMAT` | CSV row F021; একই raw file, testCaseId=`test_1hbgh0kewz67s_getCreatorCollection`; compact-offset timestamps |
| F022 | ⚠️ SPEC / S-RESP-TYPE / 1 | `ALT_DATE_FORMAT` | CSV row F022; একই raw file, testCaseId=`test_1hbiqjl7j58ir_getCharacterIndividual`; `2017-08-24T16:53:55-0400` |
| F024 | ⚠️ SPEC / S-STATUS / 1 | `STATUS_CROSS_DOCUMENTED` | CSV row F024; একই raw file, testCaseId=`test_1jicuevt3wqch_getCharacterIndividual`; error object-এ code=409; অন্য operation-এর 409 description: `08_experiments/_external/p001/specs/Marvel__openapi.yaml:117` |
| F026 | ⚠️ SPEC / S-STATUS / 1 | `STATUS_CROSS_DOCUMENTED` | CSV row F026; একই raw file, testCaseId=`test_1ib99qn5h0sog_getCharacterStoryCollection`; ResourceNotFound error object; অন্য operation-এর 404 description: `08_experiments/_external/p001/specs/Marvel__openapi.yaml:139` |
| F027 | ⚠️ SPEC / S-STATUS / 1 | `STATUS_CROSS_DOCUMENTED` | CSV row F027; একই raw file, testCaseId=`test_qhhqolkun0ol_getCharacterEventsCollection`; ResourceNotFound; একই spec line 139 |
| F029 | ⚠️ SPEC / S-STATUS / 1 | `STATUS_CROSS_DOCUMENTED` | CSV row F029; একই raw file, testCaseId=`test_s15ksbqdasl5_getComicsCharacterCollection`; ResourceNotFound; একই spec line 139 |
| F036 | ⚠️ SPEC / S-STATUS / 1 | `STATUS_CROSS_DOCUMENTED` | CSV row F036; একই raw file, testCaseId=`test_1jy7qc14lfzuf_getCharacterSeriesCollection`; ResourceNotFound; একই spec line 139 |
| F043 | ⚠️ SPEC / S-RESP-TYPE / 1 | `ALT_DATE_FORMAT;NULL_MIXED` | CSV row F043; একই raw file, testCaseId=`test_1iuys0knl7ayg_getCharacterEventsCollection`; `/data/results/[item]/end` ও `/start`-এ mixed null/non-null, অন্য response-এর references `evidence_details`-এ |

Marvel-এর cross-status entries-তে description আছে, error-body schema নেই। তাই F024-তে অন্য operation-এর business cause-ও একই—এমন দাবি করা হয়নি; 409 status documentation-ই সীমিত evidence। Empty `{}` 400 bodies F025/F028/F030/F031/F035-এ সিদ্ধান্ত হয়নি। সূত্র: `08_experiments/E2_labelling/triage_output.csv`, rows F024–F031, F035; `08_experiments/_external/p001/specs/Marvel__openapi.yaml:117`, `:139`; `08_experiments/tools/triage.py:377`।

### অন্য L1 পরিবর্তন

| পরিবর্তন | fault_id | কারণ / evidence |
|---|---|---|
| SPEC → UNDECIDABLE | F054 | Image height/width-এর exact path-এ অন্য response evidence নেই; `08_experiments/E2_labelling/triage_output.csv`, row F054, `unresolved` |
| SPEC → UNDECIDABLE | F056 | Search playlist extra property/null fields-এর জন্য যথেষ্ট cross-response evidence নেই; একই output row F056 |
| SPEC → UNDECIDABLE | F059 | `/shows/previous`-এর null prose সমর্থিত, কিন্তু `total_episodes` extra property unsupported; একই output row F059 |
| SPEC → UNDECIDABLE | F060 | `/episodes/previous`-এর null prose সমর্থিত, কিন্তু `restriction` extra property unsupported; একই output row F060 |
| SPEC → ENV | F013, F037, F038, F039, F040, F041, F042, F071 | সবগুলো 429; codebook §3/R4। একই output-এর উল্লিখিত rows; `08_experiments/R1_triage_codebook.md:69` |

Spotify-র local prose rule F049/F050/F057/F058/F061-এর SPEC decision-কে evidence দেয়, যদিও mixed-value evidence সব null field-এ নেই। Paging-এর description: `08_experiments/_external/p001/specs/Spotify_Playlists__openapi.yaml:5581`, `:5588`; followers null: `:5436`; description null: `:5652`; ফলের individual details: `08_experiments/E2_labelling/triage_output.csv`, rows F049/F050/F057/F058/F061।

### পাঁচটি high-confidence double-escape regression

F001, F003, F004, F005, F006—সবগুলো baseline ও নতুন output-এ SPEC / S-RESP-TYPE / confidence 3; প্রত্যেকটিতে `DOUBLE_ESCAPE` evidence আছে। F001-এ residual unknown নেই; F003/F004/F005/F006-এ যথাক্রমে 1/2/2/3টি deduplicated residual message আছে। সূত্র: `08_experiments/E2_labelling/triage_output.csv`, সংশ্লিষ্ট rows ও `unresolved`; regression: `08_experiments/tools/test_triage.py:291`।

⚠️ এটি ওই পাঁচটি decision এবং সরাসরি regex proof সংরক্ষণের ফল। Independent gold labels ছাড়া সামগ্রিক precision বৃদ্ধি বা পুরো mixed-message cluster-এর প্রতিটি mismatch সঠিকভাবে attributed হয়েছে—এমন দাবি করা হচ্ছে না। Pattern defect-এর confidence-ই 3। সূত্র: `08_experiments/tools/triage.py:106`, `:521`; `08_experiments/E2_labelling/triage_output.csv`, rows F003–F006-এর `note`।

## চালানো ও পরীক্ষা

এই task-এর execution record:

```text
/usr/bin/python3 -I -B 08_experiments/tools/triage.py 08_experiments/E2_labelling/p001_foas_labelling_sheet.csv 08_experiments/_external/p001 08_experiments/E2_labelling/triage_output.csv
{"ENV/confidence=2": 8, "SPEC/confidence=1": 17, "SPEC/confidence=2": 12, "SPEC/confidence=3": 5, "UNDECIDABLE/confidence=1": 31}

/usr/bin/python3 -I -B 08_experiments/tools/test_triage.py
Ran 42 tests
OK
```

৪২টি test pass, skip 0; এর মধ্যে ৫টি P001 regression test-এ পাঁচ pattern case, undecided reduction, empty-error/composition abstention, evidence completeness, এবং saved CSV বনাম recomputed result পরীক্ষা হয়। সূত্র: `08_experiments/tools/test_triage.py:284`, `:291`, `:301`, `:307`, `:311`, `:318`। প্রথম test run-এ fixture root-এর ভুলে regression class skip হয়েছিল; root সংশোধনের পরে উপরোক্ত সম্পূর্ণ run-এ সব test কার্যকর হয়েছে (`08_experiments/tools/test_triage.py:20`)।

নিজস্ব Python চালানো হয়েছে; existing `conformance`/`specmut` import করা হয়েছে, তাদের installed dependency ব্যবহার হয়েছে। New install, Docker/SUT, Schemathesis/EvoMaster/PIT, বা downloaded code execution করা হয়নি। Imports-এর bytecode cache write-ও বন্ধ। সূত্র: `08_experiments/tools/triage.py:1`, `:23`, `:301`; `08_experiments/tools/test_triage.py:1`, `:16`; অনুমোদিত boundary: `09_collab/PROTOCOL.md:12`।

## সীমাবদ্ধতা ও খোলা প্রশ্ন

- Sample কেবল confirmed-fault representative; successful-response population বা cluster-এর সব response নয়। ⚠️ তাই `PROPERTY_STABLE` sample consistency, production-wide intentionality-এর প্রমাণ নয়; confidence 1। সূত্র: `08_experiments/E1_pilot/P001_empirical_findings.md:123`; `08_experiments/tools/triage.py:219`।
- API-wide fallback exact path রাখলেও Marvel-এর `/data/results/[item]` ভিন্ন resource-এর envelope হতে পারে। ⚠️ Schema identity দিয়ে cross-operation alignment ভবিষ্যতে আরও নির্ভরযোগ্য হতে পারে; বর্তমান E-CROSS confidence 1। সূত্র: `08_experiments/tools/triage.py:219`; output row F043-এর `evidence_details`।
- Java Unicode-property rule codebook-এর dialect heuristic; Python `re`-তে reject হলেই সব regex dialect-এ unsatisfiable বলা হয় না। Double escape-ও বিশ্বজনীন unsatisfiability নয়—reported value-এর জন্য defective encoding-এর পরীক্ষা। সূত্র: `08_experiments/tools/triage.py:106`; `08_experiments/R1_triage_codebook.md`, §8.4।
- ENUM/range feature implemented হলেও কোনো P001 ENUM/NUMERIC_RANGE cluster সম্পূর্ণ সিদ্ধান্ত পায়নি: F066/F069-এ repeated `€` subfinding আছে, কিন্তু অন্য currency values-এর cross-response recurrence নেই; F067-এ yen values, F070-এ 0.0 rating অন্য response-এ পুনরাবৃত্ত হয়নি। একই body-র পুনরাবৃত্ত item-কে আলাদা response ধরা হয়নি। সূত্র: `08_experiments/E2_labelling/triage_output.csv`, rows F066/F067/F069/F070; raw `08_experiments/_external/p001/faultClustersConfirmedBugs_yelp_Businesses.csv`, testCaseId=`test_t4hvwvqa3jac_getBusinesses`, `test_trz3n8mdkn5j_getBusinesses`, `test_toa5z97enkv5_getBusinesses`, `test_1ji26wane1g6v_getBusinesses`; implementation `08_experiments/tools/triage.py:271`।
- Composition checker ইচ্ছাকৃতভাবে incomplete: duplicate-only `oneOf`, disjoint allOf types, এবং বাধ্যতামূলক numeric bounds-এর contradiction প্রমাণ করে। Observed instance-এর zero/multiple matches থেকে schema UNSAT ধরে না; reference recursion/external refs/depth limit-এ abstain করে। Local spec দিয়ে চেষ্টা করার পরও P001 composition faults F007/F051/F052/F053/F055/F062/F063/F064 UNDECIDABLE। সূত্র: `08_experiments/tools/triage.py:309`, `:325`, `:429`, `:470`; output-এর উল্লিখিত rows; `08_experiments/tools/test_triage.py:307`।
- Spec prose null rule external prose documentation নয়; E-AUX হিসেবে রাখা হয়েছে। Common alternate date acceptance, cross-operation status description, এবং recurrence—সবই দুর্বল intended-behavior evidence। ⚠️ Developer fix locus বা independent documentation দিয়ে এগুলো adjudicate করা বাকি। সূত্র: `08_experiments/tools/triage.py:131`, `:219`, `:377`, `:490`; evidence hierarchy `08_experiments/R1_triage_codebook.md:38`।
- BOTH/TEST emit করার জন্য এই prototype-এ positive-evidence rule নেই; ENV-এর Level-2 ফাঁকা, কারণ codebook-এ ENV locus সংজ্ঞায়িত নেই। এই P001 F_OAS sheet-এ IMPL-ও নেই; সাধারণ 5xx synthetic case-এ I-CRASH হয়। সূত্র: `08_experiments/tools/triage.py:521`; `08_experiments/R1_triage_codebook.md:72`; `08_experiments/tools/test_triage.py:234`; output rows F001–F073।
- খোলা policy প্রশ্ন: 503-এ R4 নাকি R1 অগ্রাধিকার; proof-সহ SPEC label-এর confidence cluster-জুড়ে নাকি শুধু proven defect-এ; এবং code intent ছাড়া stable-property SPEC lean গ্রহণযোগ্য কি না। বর্তমান choices উপরে প্রকাশ করা হয়েছে; supervisor/coordinator-এর codebook update-এ সিদ্ধান্ত প্রয়োজন। সূত্র: `08_experiments/R1_triage_codebook.md:63`, `:122`; `08_experiments/tools/triage.py:219`, `:521`।
