# T11 — codebook v0.3 অনুযায়ী message-level triage

তারিখ: 2026-11-13 · Agent: Codex। T10 DONE হওয়ার পরে T11-এর অনুমোদিত paths-এ কাজ করা হয়েছে। Scope ও execution boundary: `09_collab/tasks/T11.md:1`, `09_collab/PROTOCOL.md:6`–`:13`; পূর্ববর্তী কাজ: `09_collab/reports/T2_report.md`, `09_collab/reports/T10_report.md`।

**ফল।** ৭৩টি fault-এর জন্য cluster CSV এবং ৫৭৪টি violation message-এর জন্য পৃথক message CSV তৈরি হয়েছে; ৬১টি test pass, skip ০। Strict agreement **৩৫/৭৩ = ৪৭.৯৫%, κ = ০.২৭৯৩**; lenient agreement **৩২/৭৩ = ৪৩.৮৪%, κ = ০.১৬১৬**। Comparator হলো অপরিবর্তিত v0.2 `codex_labels.csv`; সেটি মানব-adjudicated gold নয়। Evidence: `08_experiments/E2_labelling/triage_output_v03.csv`, rows F001–F073; `triage_messages_v03.csv`, keys `(fault_id,msg_idx)`; `codex_labels.csv`, rows F001–F073; গণনা `08_experiments/tools/triage.py:773`, `:784`; test execution record নিচে। এই paragraph-এর সংক্ষিপ্ত CSV নামগুলোর পূর্ণ prefix `08_experiments/E2_labelling/`।

**কী পরিবর্তন হয়েছে।** নিচের সব attribution ⚠️ codebook-ভিত্তিক inference; output নতুন ground truth নয়। Classifier frozen Codex labels পড়ে না; comparison-এর সময় শুধু report তৈরির গণনায় সেই file পড়া হয়েছে। Implementation: `08_experiments/tools/triage.py:690`, `:739`, `:826`।

| নিয়ম | বাস্তবায়ন ও প্রমাণ |
|---|---|
| §9.1 message → cluster | প্রতিটি raw `failReason` message source order-এ পৃথক row; `msg_idx` ১ থেকে শুরু। পুনরাবৃত্ত message থাকলেও বাদ যায় না; repeated array item স্বাধীন response নয়। `classify_messages` ও `aggregate_labels`: `08_experiments/tools/triage.py:93`, `:739`, `:753`; regression `08_experiments/tools/test_triage.py:550`। |
| কোনো decisive override নেই | F001 SPEC; F003–F006 SPEC_PARTIAL। Double-escape message-এর confidence ৩ থাকে, কিন্তু অন্য message-এর অমীমাংসিত intent চাপা পড়ে না। `triage_output_v03.csv`, উল্লিখিত fault rows; `triage_messages_v03.csv`, F003/msg_idx=13; test `08_experiments/tools/test_triage.py:491`। |
| §9.2 strict property oracle | ২৭টি affected fault-এর সব ৬৬টি additional-property message TEST / T-ORACLE-STRICT। ৯টি সম্পূর্ণ strict-only fault TEST; বাকি ১৮টির mixed aggregation নিচে ব্যাখ্যা করা হয়েছে। `08_experiments/tools/triage.py:583`; test `08_experiments/tools/test_triage.py:536`; message CSV-তে `rule=STRICT_ONLY`। |
| `doc_gap` আলাদা attribute | Public field documentation-এর URL ও ISO retrieval date, এবং schema-তে field অনুপস্থিত থাকার evidence থাকলে `doc_gap=true`; label TEST-ই থাকে, confidence ≤২। Library-তে `Context.documentation` input আছে। এই offline CLI run-এ এমন input দেওয়া হয়নি: সব `doc_gap=False` অর্থ **gap প্রতিষ্ঠিত হয়নি**, completeness প্রমাণিত নয়। `08_experiments/tools/triage.py:169`, `:583`; test `08_experiments/tools/test_triage.py:384`; message CSV, সব rows। |
| §9.3 ENV আগে | 429/502/503/504 এবং error body-র gateway/timeout diagnostic → ENV; অন্য 5xx → IMPL/I-CRASH। `08_experiments/tools/triage.py:641`, `:690`; tests `08_experiments/tools/test_triage.py:235`, `:402`। |
| Malformed JSON | Failed JSON decoding এবং documented JSON response থাকলে parse message → IMPL/I-RESP-CONTRACT। Swagger-এ `produces` না থাকলে response schema-এর সঙ্গে captured expected `outputContentType_x` দরকার। F047 এখন IMPL, confidence ২। `08_experiments/tools/triage.py:658`; `triage_messages_v03.csv`, F047/msg_idx=1; tests `08_experiments/tools/test_triage.py:414`, `:430`। |
| Closed-source R3 / developer flags | Code অনুপস্থিত থেকে constraint অনুপস্থিত অনুমান করা হয় না; `confirmed`/`fixed` থেকে fix direction নির্ধারণ করা হয় না। `08_experiments/tools/triage.py:690`; test `08_experiments/tools/test_triage.py:440`। |
| §9.4 L2 | Media mismatch → S-MEDIA; repeated enum/range outlier → S-RESP-VALUE। `08_experiments/tools/triage.py:232`, `:690`; message CSV F008/F009, F066/msg_idx=1, F069/msg_idx=3; test `08_experiments/tools/test_triage.py:448`। |
| §9.5 composition | Global UNSAT proof, representative branch matches ও nullable parent without type আলাদা checks। Instance witness-এ response path, observation index ও SHA-256 আছে; external reference fetch হয় না। Global proof ছাড়া overlap/nullable diagnostic একা attribution দেয় না। `08_experiments/tools/triage.py:492`, `:543`; test `08_experiments/tools/test_triage.py:361`; message CSV F051/msg_idx=2, F062/msg_idx=2–3। |

উপরের table-এ `triage_output_v03.csv` ও `triage_messages_v03.csv`-এর পূর্ণ prefix `08_experiments/E2_labelling/`। Fault CSV-তে আগের sheet columns রয়ে গেছে; আগের tool-এর মতো `note`-এ triage explanation লেখা হয়, অন্য input values অপরিবর্তিত। `evidence_details`-এ সব message decisions, `unresolved`-এ শুধু unresolved messages, `aggregation_gap`-এ unspecified mixture, এবং `n_labelled_messages`-এ row count আছে। UNDECIDABLE cluster-এরও supported L2 subfindings থাকে; সেগুলো cluster-এর পূর্ণ attribution নয়। Evidence: `08_experiments/tools/triage.py:797`, `:826`; fault CSV, F049 (`unresolved=[]`, কিন্তু TEST+SPEC mixture), F007 (`unresolved` nonempty)।

**Aggregation-এর অনির্দিষ্ট অংশ।** §9.1-এ TEST+SPEC, TEST+UNDECIDABLE, ENV+অন্য L1-এর ফল নির্দিষ্ট নেই। ⚠️ Implementation এগুলো conservative UNDECIDABLE রাখে এবং `AGGREGATION_RULE_GAP` লেখে; নতুন TEST_PARTIAL বা ENV_PARTIAL উদ্ভাবন করে না। SPEC ও IMPL আলাদা message-এ প্রতিষ্ঠিত হলে BOTH হয়; UNKNOWN message-ও evidence-এ থাকে। সূত্র: `08_experiments/R1_triage_codebook.md`, §9.1; `08_experiments/tools/triage.py:753`; tests `08_experiments/tools/test_triage.py:287`, `:301`।

এই dataset-এ ১৮টি mixed gap: F007, F019, F023, F032, F049, F050, F051, F052, F053, F055, F056, F057, F058, F059, F060, F062, F063, F064। TEST ও SPEC message-এর সবগুলো decided হলেও cluster abstain করতে পারে, যেমন F049। Evidence: `08_experiments/E2_labelling/triage_output_v03.csv`, উল্লিখিত rows-এর `aggregation_gap`, `rules`, `evidence_details`।

**v0.2 বনাম v0.3 label distribution।** v0.2 এখানে T2 triage artifact, rule-baseline-এর `suggested_L1` নয়। প্রতি column-এর unit একটি fault। নিচের সব count-এর evidence: `08_experiments/E2_labelling/triage_output.csv` এবং `triage_output_v03.csv`, F001–F073; scoring mapping `08_experiments/tools/triage.py:773`।

| L1 | T2 v0.2 | v0.3 raw | v0.3 strict | v0.3 lenient |
|---|---:|---:|---:|---:|
| SPEC | 34 | 17 | 17 | 26 |
| SPEC_PARTIAL | 0 | 9 | 0 | 0 |
| IMPL | 0 | 1 | 1 | 1 |
| IMPL_PARTIAL | 0 | 0 | 0 | 0 |
| ENV | 8 | 8 | 8 | 8 |
| TEST | 0 | 9 | 9 | 9 |
| BOTH | 0 | 0 | 0 | 0 |
| UNDECIDABLE | 31 | 29 | 38 | 29 |
| মোট | 73 | 73 | 73 | 73 |

Raw UNDECIDABLE ৩১→২৯ দেখে উন্নতির দাবি করা যাবে না: strict scoring-এ নতুন count ৩৮। v0.2 SPEC-এর ১৭টি SPEC, ৯টি TEST, ৪টি SPEC_PARTIAL, ৪টি UNDECIDABLE হয়েছে। পুরোনো UNDECIDABLE-এর ২৫টি অপরিবর্তিত, ৫টি SPEC_PARTIAL, ১টি IMPL; ENV-এর ৮টি অপরিবর্তিত। Evidence: একই দুই CSV-র `fault_id` join, rows F001–F073। ⚠️ Label policy ও unit বদলেছে; এই count precision-এর প্রমাণ নয়।

Message distribution: SPEC ৪৪৮, IMPL ১, ENV ৮, TEST ৬৬, UNDECIDABLE ৫১; মোট ৫৭৪। একাধিক message একই fault থেকে আসে, তাই message count-কে স্বাধীন failure sample বলা যাবে না। Evidence: `08_experiments/E2_labelling/triage_messages_v03.csv`, `L1` column; `08_experiments/tools/triage.py:93`, `:232`।

**Frozen Codex labels-এর সঙ্গে agreement।** `fault_id` দিয়ে পূর্ণ ৭৩-row one-to-one join; comparator-এর labels অপরিবর্তিত SPEC ৪৭, UNDECIDABLE ১৬, ENV ৯, IMPL ১। Partial mapping শুধু scoring-এর সময়; CSV-র raw label পরিবর্তন করা হয়নি। সূত্র: `08_experiments/E2_labelling/codex_labels.csv`, F001–F073; `08_experiments/tools/triage.py:773`, `:784`।

| Triage version / scoring | মিল | Raw agreement | Cohen's κ |
|---|---:|---:|---:|
| T2 v0.2 (context) | 45/73 | 61.6438% | 0.353778 |
| v0.3 strict: *_PARTIAL → UNDECIDABLE | 35/73 | 47.9452% | 0.279293 |
| v0.3 lenient: *_PARTIAL → base L1 | 32/73 | 43.8356% | 0.161625 |

গণনা: `p_o=matched/n`, `p_e=Σ count_triage(label)×count_codex(label)/n²`, `κ=(p_o−p_e)/(1−p_e)`; TEST-সহ দুই পাশে উপস্থিত সব label-এর union ব্যবহৃত। সূত্র: `08_experiments/tools/triage.py:784`; hand-calculated κ fixture: `08_experiments/tools/test_triage.py:465`। নিচের crosstab সরাসরি পুনর্গণনার evidence; source একই তিন CSV, F001–F073।

| v0.3 scored L1 | Strict: Codex SPEC | IMPL | ENV | UNDECIDABLE | Lenient: Codex SPEC | IMPL | ENV | UNDECIDABLE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SPEC | 13 | 0 | 1 | 3 | 16 | 0 | 1 | 9 |
| IMPL | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 |
| ENV | 0 | 0 | 8 | 0 | 0 | 0 | 8 | 0 |
| TEST | 9 | 0 | 0 | 0 | 9 | 0 | 0 | 0 |
| UNDECIDABLE | 25 | 0 | 0 | 13 | 22 | 0 | 0 | 7 |

⚠️ Agreement কমার মধ্যে policy mismatch আছে: Codex labels v0.2 strict-only default ব্যবহার করেছে, তাই ৯টি TEST এখন তার SPEC-এর সঙ্গে মেলে না। Lenient-এ F003/F066/F069 মেলে, কিন্তু F004/F005/F006/F033/F034/F045 strict-এ মিলে lenient-এ মেলে না; তাই lenient agreement এখানে বেশি নয়। Evidence: `codex_labels.csv`, উল্লিখিত rows-এর `rationale`; `triage_output_v03.csv`, একই rows; পূর্ণ prefix `08_experiments/E2_labelling/`।

**অবশিষ্ট disagreement-এর পূর্ণ তালিকা।** Strict-এ ৩৮টি, lenient-এ ৪১টি; অন্তত এক mode-এ disagreement আছে এমন union ৪৪টি। S = শুধু strict, L = শুধু lenient, S+L = উভয়। SP = SPEC_PARTIAL, U = UNDECIDABLE। নিচের প্রতিটি row-এর primary evidence হলো `08_experiments/E2_labelling/triage_output_v03.csv#fault_id=<ID>` ও `08_experiments/E2_labelling/codex_labels.csv#fault_id=<ID>`; message detail হলো `08_experiments/E2_labelling/triage_messages_v03.csv`-এর একই `fault_id` rows। Reason class-গুলো ⚠️ এই comparison-এর ব্যাখ্যা, adjudication নয়।

| fault_id | v0.3 raw / Codex | Mode | Reason class | নির্দিষ্ট পার্থক্য |
|---|---|---|---|---|
| F003 | SP / SPEC | S | aggregation | Double-escape প্রমাণিত; roomQuantity string→integer mismatch-এর intent classifier-এ অমীমাংসিত। Codex repeated string representation গ্রহণ করেছে। |
| F004 | SP / U | L | aggregation | Decimal pattern SPEC; missing fax ও roomQuantity unresolved। |
| F005 | SP / U | L | aggregation | Pattern/alternate date SPEC; fax ও roomQuantity unresolved। |
| F006 | SP / U | L | aggregation | Pattern/alternate date SPEC; phone pattern, fax ও tax amount-এর কিছু intent unresolved। |
| F010 | TEST / SPEC | S+L | rule gap | v0.3 open-object extra property oracle policy বনাম Codex v0.2 SPEC default। |
| F011 | TEST / SPEC | S+L | rule gap | একই strict-only policy পরিবর্তন; neighborhood-সহ allowed additions। |
| F014 | U / SPEC | S+L | evidence source | Raw language-code rejection দেখে Codex invalidity চিনেছে; classifier supplied faulty flag/cross-status evidence-এ নির্ভর করে। |
| F015 | TEST / SPEC | S+L | rule gap | warnings/confidence/premiumHint: v0.2→v0.3 strict-only policy। |
| F016 | TEST / SPEC | S+L | rule gap | Match-এর extra fields: একই policy পরিবর্তন। |
| F017 | TEST / SPEC | S+L | rule gap | ignoreRanges/spellCheckOnly: একই policy পরিবর্তন। |
| F018 | TEST / SPEC | S+L | rule gap | Replacement/rule extras: একই policy পরিবর্তন। |
| F022 | SPEC / U | S+L | evidence source | Classifier calendar-valid compact-offset date-কে weak E-CONV বলে; Codex same-operation recurrence/intent চেয়েছে। |
| F024 | SPEC / U | S+L | evidence source | Classifier অন্য operation-এর 409 documentation গ্রহণ করেছে; Codex id=0-এর intended error semantics অনির্ধারিত রেখেছে। |
| F025 | U / SPEC | S+L | evidence source | Codex malformed characterId দেখে 400 rejection মেনেছে; classifier supplied validity flag ও empty error object থেকে abstain করে। |
| F028 | U / SPEC | S+L | evidence source | Raw nonnumeric characterId/offset interpretation বনাম supplied validity flag ও empty body। |
| F030 | U / SPEC | S+L | evidence source | Raw nonnumeric characterId interpretation বনাম একই classifier সীমা। |
| F031 | U / SPEC | S+L | evidence source | Raw nonnumeric ID/comics=null interpretation বনাম একই classifier সীমা। |
| F033 | SP / U | L | aggregation | কিছু nullable/date evidence আছে; negative-year timestamp unresolved। |
| F034 | SP / U | L | aggregation | Valid alternative timestamps SPEC; negative-year sentinel intent unresolved। |
| F035 | U / SPEC | S+L | evidence source | Raw malformed ID/offset/limit দেখে Codex coherent 400 বলেছে; classifier flag/empty body-তে abstain করে। |
| F045 | SP / U | L | aggregation | Nullable/date subfinding SPEC; diamondCode numeric sentinel ও invalid date unresolved। |
| F048 | SPEC / ENV | S+L | rule gap | Classifier generic undocumented 403→SPEC lean রাখে; Codex Cloudflare blocking body থেকে intermediary ENV বলে। Gateway/timeout matcher এই security-block case ধরে না। |
| F049 | U / SPEC | S+L | aggregation | TEST extra property + SPEC paging null; §9.1 mixed rule অনির্দিষ্ট। |
| F050 | U / SPEC | S+L | aggregation | TEST extra property + SPEC paging/image null evidence। |
| F051 | U / SPEC | S+L | aggregation | TEST extras + unresolved composition intent। Both oneOf branches match করার witness আছে, global UNSAT নেই। |
| F052 | U / SPEC | S+L | aggregation | TEST extras, SPEC paging null, composition overlap diagnostic; Codex overlap-কে SPEC বলে। |
| F053 | U / SPEC | S+L | aggregation | TEST extras, SPEC nullable fields ও composition diagnostic এক cluster-এ। |
| F054 | U / SPEC | S+L | evidence source | Codex current Spotify E-DOC থেকে null image dimensions অনুমোদন পেয়েছে; offline classifier-এ সেই independent docs input নেই। |
| F055 | U / SPEC | S+L | aggregation | TEST extras + nullable SPEC + composition unknown; Codex অতিরিক্ত E-DOC ব্যবহার করেছে। |
| F056 | U / SPEC | S+L | aggregation | TEST extras + unresolved image/public null; Codex E-DOC ব্যবহার করেছে, classifier docs input পায়নি। |
| F057 | U / SPEC | S+L | aggregation | TEST primary_color + SPEC prose/consistency nullable fields। |
| F058 | U / SPEC | S+L | aggregation | TEST primary_color + SPEC paging null। |
| F059 | U / SPEC | S+L | aggregation | TEST total_episodes + SPEC previous=null। |
| F060 | U / SPEC | S+L | aggregation | TEST restriction + SPEC previous=null। |
| F061 | SPEC / U | S+L | evidence source | Classifier API-wide exact-path recurrence দিয়ে followers.total nullable বলে; Codex independent nullable evidence অপর্যাপ্ত বলেছে। Fix flag কোনো direction দেয় না। |
| F062 | U / SPEC | S+L | aggregation | TEST extras + nullable-parent composition diagnostic; Codex Stripe E-DOC থেকে intent নিয়েছে। |
| F063 | U / SPEC | S+L | aggregation | TEST extras + null package_dimensions/tax_code composition diagnostic; Codex E-DOC যোগ করেছে। |
| F064 | U / SPEC | S+L | aggregation | TEST extras + nullable-parent diagnostic; Codex E-DOC যোগ করেছে। |
| F065 | TEST / SPEC | S+L | rule gap | Strict-only policy বদলেছে; dimensions ইতিমধ্যেই schema-তে declared থাকার snapshot/oracle caveat রয়ে গেছে। |
| F066 | SP / SPEC | S | aggregation | € একই value অন্য response-এ আছে; €€-এর exact recurrence নেই। Codex locale-aware currency interpretation করেছে। |
| F067 | U / SPEC | S+L | evidence source | Classifier exact-value cross-response yen recurrence পায়নি; Codex Tokyo/Europe-এর locale-coherent currency evidence গ্রহণ করেছে। |
| F069 | SP / SPEC | S | aggregation | Nullable coordinates ও repeated € SPEC; €€€€-এর exact recurrence নেই। |
| F072 | TEST / SPEC | S+L | rule gap | YouTube open-object extras: v0.3 oracle-policy default বনাম v0.2 SPEC। |
| F073 | TEST / SPEC | S+L | rule gap | একই YouTube strict-only policy পরিবর্তন। |

উপরের primary reason class অনুযায়ী aggregation ২৩টি, rule gap ১০টি, evidence source ১১টি; একাধিক কারণ থাকলে table-এর explanation-এ দ্বিতীয় কারণটিও বলা হয়েছে। Evidence: উপরের ৪৪-row table ও তার ঘোষিত CSV row references।

**Verification ও পুনরুৎপাদন।** নিচের command repository root থেকে চালানো হয়েছে। Final test run-এ ৬১টি test OK, failure/error/skip ০; পুরো message CSV-এর প্রত্যেক column ও raw message coverage-ও recomputed result-এর সঙ্গে মেলে। Absolute বনাম relative file locator comparison-এ refs normalize/sort করা হয়, যাতে local workspace prefix ও ordering-কে semantic disagreement ধরা না হয়। Evidence: `08_experiments/tools/test_triage.py:550`; runner `:575`।

```text
/usr/bin/python3 -I -B 08_experiments/tools/triage.py 08_experiments/E2_labelling/p001_foas_labelling_sheet.csv 08_experiments/_external/p001 08_experiments/E2_labelling/triage_output_v03.csv --messages 08_experiments/E2_labelling/triage_messages_v03.csv
/usr/bin/python3 -I -B 08_experiments/tools/test_triage.py
Ran 61 tests
OK
```

Agreement ও distribution পুনর্গণনার read-only command; এটি শুধু নিজের project module চালায়:

```python
# Run with /usr/bin/python3 -I -B from the repository root.
import sys
from collections import Counter
sys.path.insert(0, '08_experiments/tools')
import triage as T
p = '08_experiments/E2_labelling/'
v03 = T.read_csv(p + 'triage_output_v03.csv')
codex = {r['fault_id']: r for r in T.read_csv(p + 'codex_labels.csv')}
assert len(v03) == len(codex) == len({r['fault_id'] for r in v03}) == 73
assert {r['fault_id'] for r in v03} == set(codex)
for filename in ('triage_output.csv', 'triage_output_v03.csv'):
    print(filename, Counter(r['label_L1'] for r in T.read_csv(p + filename)))
for mode in ('strict', 'lenient'):
    print(mode, T.agreement([r['label_L1'] for r in v03],
                            [codex[r['fault_id']]['label_L1'] for r in v03], mode))
```

পুরোনো T2 output ও frozen comparator অপরিবর্তিত রাখা হয়েছে। নিচে SHA-256; CSV paths-এর পূর্ণ prefix `08_experiments/E2_labelling/`। Comparator hash T3-এর freeze report-এর সঙ্গে মেলে (`09_collab/reports/T3_report.md`, “Blinding audit”); T2 file-এ কোনো write command চালানো হয়নি।

| অপরিবর্তিত input | SHA-256 |
|---|---|
| `triage_output.csv` | `c6c1e92b21ddd2faa61251154592dc7bb8fde8e1837c12577e4f04d8b32f51e3` |
| `codex_labels.csv` | `64b860aa89d81de2ba301c953eccc78ce8ec47059b24a84e96f7e9b33aa8b6a6` |
| `p001_foas_labelling_sheet.csv` | `bfe0f92a2e0ac3a258f19f85f7188cac15664f8cbad5494d2b93e8b7c1555a4b` |

Execution কেবল নিজের Python tool/tests ও তাদের আগে থেকে installed dependencies-এ সীমিত ছিল; Docker, SUT, Schemathesis, EvoMaster, PIT, package installation বা downloaded code execution করা হয়নি। Bytecode writing বন্ধ। Evidence: উপরের exact execution commands; `08_experiments/tools/triage.py:1`, `:23`, `:314`; boundary `09_collab/PROTOCOL.md:12`।

**সীমাবদ্ধতা ও খোলা প্রশ্ন।**

- §9.1-এর TEST/ENV mixed aggregation supervisor/coordinator-কে নির্দিষ্ট করতে হবে। এই run conservative fallback ব্যবহার করেছে; ১৮টি gap audit করা সম্ভব। Source: `08_experiments/R1_triage_codebook.md`, §9.1; fault CSV-র `aggregation_gap=True` rows।
- Frozen comparator v0.2; একই semantics-এ agreement পেতে মানব adjudication বা স্বাধীন v0.3 relabelling দরকার। শুধু Codex labels-কে TEST-এ remap করে এই report-এর score বাড়ানো হয়নি। Source: `08_experiments/E2_labelling/codex_labels.csv`, F010/F011/F015–F018/F065/F072/F073; codebook §9.2।
- Public docs এই run-এ সংগ্রহ করা হয়নি। Optional `Context.documentation` শুধু independently collected field evidence-এর input interface; এটি web retrieval বা historical snapshot validation করে না। তাই সব `doc_gap=False`-কে missing-documentation rate বলা যাবে না। Source: `08_experiments/tools/triage.py:169`, `:583`, `:826`।
- Composition-এর first representative witness ও nullable-parent diagnostic intent প্রমাণ করে না; full satisfiability solver বা converter root-cause analysis করা হয়নি। Spotify F051/F052/F053/F055-এ branch matches `[0,1]`; Stripe F062–F064-এ null witness কোনো branch-এ মেলে না। Source: message CSV-র সংশ্লিষ্ট rows-এর `note`; `08_experiments/tools/triage.py:543`।
- F014 এবং Marvel empty 400 cases-এ raw request-এর independent validity পুনর্নির্ণয় করা হয়নি; F048-এর Cloudflare security block-এর dedicated ENV rule নেই। API-wide nullable consistency ও exact-outlier recurrence-এর পুরোনো conservative limitations-ও রয়ে গেছে। Source: disagreement table-এর ওই rows; `08_experiments/tools/triage.py:232`, `:399`, `:641`, `:690`।
- P001 কেবল confirmed-fault representatives; message সংখ্যা successful-response population বা independent repeated experiments নয়। এই ফল থেকে classifier accuracy, false-positive rate বা API correctness দাবি করা যাচ্ছে না। Source: `08_experiments/E1_pilot/P001_empirical_findings.md:123`; `08_experiments/tools/triage.py:232`; codebook §9.6।
