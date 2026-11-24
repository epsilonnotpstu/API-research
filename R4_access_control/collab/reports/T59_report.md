# T59 — R1, R3 ও R4: double-anonymous readiness ও cross-paper consistency review

তারিখ: 2026-11-24। Reviewer: Codex। Task: `R4_access_control/collab/tasks/T59.md`।

তিনটি Markdown draft ও তাদের generated `main.tex` পরীক্ষা করেছি; bibliography, figure location এবং নির্দিষ্ট local venue/replication নির্দেশনাও মিলিয়েছি। সরাসরি author-identity leak পাইনি। বিদ্যমান companion-result উদ্ধৃতিতে numeric mismatch নেই। তবে চারটি citation direction অনুপস্থিত, R1-এর figure path ভাঙা, এবং কয়েকটি submission-preparation কাজ বাকি আছে। তাই বর্তমান অবস্থাকে submission-ready বলা যায় না।

## পদ্ধতি ও scope

- সব command repository root থেকে চালানো হয়েছে। প্রথম command ছিল হুবহু `cat R4_access_control/collab/tasks/T59.md`। Network, compiler বা external project code ব্যবহার করিনি; git write করিনি।
- `packages/`-এর item contents, `mining/key/` salts এবং `research/09_collab/human_check/` পড়িনি। Human validation-এর অবস্থা শুধু manuscript ও venue নির্দেশনা থেকে নিয়েছি।
- Write কেবল এই report ও `R4_access_control/collab/logs/T59_scratch/`-এ। সংশোধনের প্রস্তাবগুলো প্রয়োগ করিনি।
- Static checker: `R4_access_control/collab/logs/T59_scratch/audit.py`। ফল: একই directory-র `static_audit.json`; reviewed draft/TeX/bibliography-র SHA-256: `input_hashes.json`; companion-number check: `cross_paper_check.json`। পুনরায় checker চালিয়ে input hashes অপরিবর্তিত পাওয়া গেছে।
- Severity: **BLOCKER** = বর্তমান source layout-এ সাধারণ build আটকে যায়; **ERROR** = task-এর স্পষ্ট requirement বা নথিভুক্ত author action অসম্পূর্ণ; **MINOR** = wording/formatting বা পরবর্তী verification-এর ঘাটতি। একই সমস্যার Markdown ও TeX occurrence এক finding হিসেবে গোনা হয়েছে।

## Findings

| paper | location | issue | severity (BLOCKER/ERROR/MINOR) | fix |
|---|---|---|---|---|
| R1 | `research/10_paper/latex/main.tex:362`; actual asset `research/10_paper/figures/fig_kind_direction.pdf`; bibliography base `main.tex:641` | **B01 — Figure আছে, কিন্তু reference resolve হয় না।** `latex/` থেকে build করলে `figures/fig_kind_direction.pdf` চায় `latex/figures/`-এ; ওই file/directory নেই, এবং `graphicspath` নেই। `../references` bibliography-ও `latex/` build base নির্দেশ করে। | BLOCKER | Generator-এ figure argument `../figures/fig_kind_direction.pdf` করুন, অথবা উপযুক্ত `graphicspath` ও filename ব্যবহার করে regenerate করুন। Figure ও bibliography একই build base থেকে resolve হচ্ছে নিশ্চিত করুন। |
| R1 | `research/10_paper/R1_draft.md:51`–83, পুরো draft:1–433; `research/10_paper/latex/main.tex:68`–110, পুরো source:1–642 | **E01 — R3 ও R4-এর companion reference নেই।** Task-এর “each paper cites the others” requirement-এ R1→R3 এবং R1→R4 দুই direction-ই অনুপস্থিত। | ERROR | Related Work-এ দুটির পৃথক topic ও contribution পরিচয় দিয়ে প্রতিটিকে “a companion study, under review; omitted for anonymity” বলুন; identifiable title/author/repository link দেবেন না। তারপর regenerate করুন। |
| R3 | `R3_silent_breaking/paper/R3_draft.md:33`–51, পুরো draft:1–273; `R3_silent_breaking/paper/latex/main.tex:49`–73, পুরো source:1–384 | **E02 — R4 companion reference নেই।** বর্তমান anonymous reference শুধু repair-direction study, অর্থাৎ R1-এর দিকে। | ERROR | Access-control/security-fix study-কে anonymous companion study হিসেবে পৃথকভাবে উল্লেখ করুন; নতুন কোনো সংখ্যা দিলে R4-এর own Results-এর সঙ্গে মিলিয়ে নিন। |
| R4 | `R4_access_control/paper/R4_draft.md:30`–46, পুরো draft:1–265; `R4_access_control/paper/latex/main.tex:46`–66, পুরো source:1–362 | **E03 — R1 companion reference নেই।** বর্তমান companion paragraph R3-এর silent-change study নিয়ে। | ERROR | Repair-direction/divergence study-কে anonymous companion study হিসেবে পৃথকভাবে উল্লেখ করুন। |
| R1 | `research/10_paper/R1_draft.md:423`–433; `research/10_paper/latex/main.tex:626`–638; `research/10_paper/REPLICATION_PACKAGE_PLAN.md:45` | **E04 — Data availability section আছে, anonymous-link placeholder নেই।** শুধু ভবিষ্যতে anonymous archive ছাড়ার প্রতিশ্রুতি আছে। | ERROR | Data availability-তে `[anonymous link to be added]`-জাতীয় স্পষ্ট placeholder দিন; submission-এর আগে anonymised review archive-এর কার্যকর link বসান। |
| R3 | `R3_silent_breaking/paper/R3_draft.md:260`–266; `R3_silent_breaking/paper/latex/main.tex:370`–379; `R3_silent_breaking/paper/VENUE.md:23` | **E05 — AI-use disclosure আছে, কিন্তু affected sections নির্দিষ্ট নয়।** Claude/Codex ও কাজের ধরন বলা আছে; “draft and edit text” কোন manuscript sections-এ প্রযোজ্য তা বলা নেই। Instrument-method-এর §3.4 উল্লেখ assistant-generated prose-এর scope নির্ধারণ করে না। | ERROR | Authors প্রকৃত ব্যবহার মিলিয়ে affected section numbers/names ও assistant-এর ভূমিকা স্পষ্ট করুন; VENUE.md অনুযায়ী disclosure review ও complete করুন। |
| R4 | `R4_access_control/paper/R4_draft.md:259`–265; `R4_access_control/paper/latex/main.tex:348`–357; `R4_access_control/paper/VENUE.md:17`–20; `R3_silent_breaking/paper/VENUE.md:23` | **E06 — AI-use disclosure-তে affected sections নির্দিষ্ট নয়।** “draft text” এবং pipeline/number-check সহায়তার কথা আছে; কোন sections affected বলা নেই। R4 venue note R3-এর author actions গ্রহণ করেছে। | ERROR | বাস্তব ব্যবহার অনুসারে section-level scope লিখুন এবং disclosure authors দ্বারা যাচাই করুন; নতুন scope অনুমান করে বসাবেন না। |
| R1 | `research/10_paper/R1_draft.md:384`; `research/10_paper/latex/main.tex:573`; `research/10_paper/REPLICATION_PACKAGE_PLAN.md:8` | **E07 — Human spot-check ফলের বদলে submission source-এ সরাসরি `[TODO]` আছে।** Archive plan-ও human check যোগ হওয়ার পরে rebuild চায়। এটি manuscript-completeness finding; human-check file-এর content সম্পর্কে সিদ্ধান্ত নয়। | ERROR | অনুমোদিত মানবীয় coding/agreement সম্পন্ন হলে ফল §6-এ বসান, TODO সরিয়ে regenerate করুন এবং plan অনুযায়ী archive rebuild করুন। |
| R3 | `R3_silent_breaking/paper/R3_draft.md:230`; `R3_silent_breaking/paper/latex/main.tex:328`; `R3_silent_breaking/paper/VENUE.md:29` | **E08 — নথিভুক্ত human spot-check author action manuscript-এ অসম্পূর্ণ।** Draft এখনো “prepared and will be reported separately” বলছে; VENUE.md agreement §6-এ দিতে বলেছে। | ERROR | 20-item check-এর agreement/result §6-এ রিপোর্ট করুন; কাজের বর্তমান status-এর সঙ্গে manuscript মিলিয়ে regenerate করুন। |
| R4 | `R4_access_control/paper/R4_draft.md:230`; `R4_access_control/paper/latex/main.tex:309`; `R4_access_control/paper/VENUE.md:21` | **E09 — নথিভুক্ত human spot-check author action manuscript-এ অসম্পূর্ণ।** এখানেও শুধু ভবিষ্যৎ report-এর কথা আছে। | ERROR | 20-item check শেষ করে manuscript-এ validation result ও scope যোগ করুন, তারপর regenerate করুন। |
| R3 | `R3_silent_breaking/paper/R3_draft.md:51`; `R3_silent_breaking/paper/latex/main.tex:73` | **M01 — Anonymous wording নিরাপদ, কিন্তু task-এর requested companion wording থেকে আলাদা।** “A separate study of the same corpus (under review; omitted for anonymity)” ব্যবহার হয়েছে। এটি identity leak নয়। | MINOR | “A companion study (under review; omitted for anonymity)” হিসেবে wording এক করুন; corpus সম্পর্ক আলাদা বাক্যে ব্যাখ্যা করা যায়। |
| R1 | `research/10_paper/`-এ `VENUE.md` পাওয়া যায়নি; `research/10_paper/REPLICATION_PACKAGE_PLAN.md:62`–64; `research/10_paper/latex/main.tex:2` | **M02 — Local venue specification অসম্পূর্ণ/পুরোনো।** Task ও source ISSTA 2027/acmsmall ঠিক করেছে; replication plan এখনো venue ও double-blind-কে open decision বলছে। R1-এর local page cap নেই। | MINOR | Venue decision, official format ও length limit স্থানীয় নথিতে হালনাগাদ করুন। নিচের page estimate থেকে over-limit verdict দেবেন না, যতক্ষণ cap যাচাই না হয়। |
| R3 | `R3_silent_breaking/paper/VENUE.md:16`–24,27; `R3_silent_breaking/paper/R3_draft.md:1`; `R3_silent_breaking/paper/latex/main.tex:13` | **M03 — Venue compliance এখনো provisional।** Local rules ICSME 2026 CFP থেকে; 2027 re-check এবং public/preprint title থেকে পার্থক্য নিশ্চিত করার কাজ বাকি। শুধু local files দিয়ে publication history যাচাই করা যায়নি। | MINOR | Submission-এর আগে official 2027 CFP ও public/preprint title মিলিয়ে দেখুন; PDF compile করে actual page count পরীক্ষা করুন। এই task-এ network/compile করা হয়নি। |
| R4 | `R4_access_control/paper/VENUE.md:4`–5,18; `R4_access_control/paper/latex/main.tex:2` | **M04 — ASE 2027 template/length ও dates স্থানীয় সিদ্ধান্তেই অনিশ্চিত।** IEEEtran বর্তমান local assumption-এর সঙ্গে মেলে; official 2027 compliance প্রমাণিত নয়। | MINOR | Official CFP থেকে template ও cap নিশ্চিত করুন, প্রয়োজন হলে generator/template বদলান, তারপর PDF page count মাপুন। |
| R1 | `research/10_paper/latex/main.tex:25,68,112,270,531,563,601` | **M05 — Generated section titles-এ manual numeric prefix আছে।** যেমন `section{1. Introduction}`; class-এর automatic numbering-এর সঙ্গে duplicate numbering হবে বলে source থেকে বোঝা যায়। | MINOR | Generator দিয়ে heading-এর `1.`–`7.` prefix সরিয়ে automatic section numbering ব্যবহার করুন। |

## Identity/anonymity ফল

ছয়টি target file-এ known local username এবং read-only git remote থেকে পাওয়া study owner/repository identifier মিলিয়ে scan করেছি। Study author/user name, e-mail, absolute local path, university/affiliation, acknowledgements/funding, “our previous/prior/earlier work”, কিংবা study-র non-anonymous repository URL পাইনি। Target source-গুলিতে সরাসরি HTTP(S)/GitHub repository URL-ও নেই। Evidence: `static_audit.json`-এর প্রতিটি paper-এর দুই file-সংক্রান্ত `identity_scans`; সম্পূর্ণ reviewed file ranges findings table-এ আছে। এটি source audit-এর ফল, deposited archive বা rendered PDF metadata-এর certification নয়।

তিনটি author block নিরাপদ: R1 `research/10_paper/latex/main.tex:2,11`-এ `anonymous` option ও `Anonymous Author(s)`; R3/R4 নিজ নিজ `paper/latex/main.tex:14`-এ `Anonymous Author(s)` এবং `Under double-anonymous review`। R1-এর author affiliation/email/thanks declaration নেই; IEEE source-গুলিতেও বাস্তব affiliation নেই।

Claude, Codex, GPT ও Sonnet নামগুলো method/instrument disclosure, গবেষকের নাম নয়। Related-work author names এবং ReportPortal, Microcks, Traccar, Mattermost ইত্যাদি upstream service names-কে leak হিসেবে ধরা হয়নি। Bibliography-তে R3-এর AutoGuard upstream GitHub URL-ও অনুমোদিত upstream reference; study repository link নয় (`R3_silent_breaking/paper/latex/references.bib:5`)। Paper-relative artifact paths যেমন `plan/R3_PLAN.md` ও `09_collab/tasks/T42.md` user-identity-যুক্ত machine path নয়।

## Cross-paper consistency: দুই দিকই পরীক্ষা

| direction | draft location | generated TeX location | ফল |
|---|---|---|---|
| R1 → R3 | পুরো `research/10_paper/R1_draft.md:1`–433 | পুরো `research/10_paper/latex/main.tex:1`–642 | অনুপস্থিত; E01 |
| R1 → R4 | একই complete source coverage | একই complete source coverage | অনুপস্থিত; E01 |
| R3 → R1 | `R3_silent_breaking/paper/R3_draft.md:51` | `R3_silent_breaking/paper/latex/main.tex:73` | Anonymous prose আছে; companion-result সংখ্যা উদ্ধৃত নেই; M01 wording adjustment |
| R3 → R4 | পুরো `R3_silent_breaking/paper/R3_draft.md:1`–273 | পুরো `R3_silent_breaking/paper/latex/main.tex:1`–384 | অনুপস্থিত; E02 |
| R4 → R1 | পুরো `R4_access_control/paper/R4_draft.md:1`–265 | পুরো `R4_access_control/paper/latex/main.tex:1`–362 | অনুপস্থিত; E03 |
| R4 → R3 | `R4_access_control/paper/R4_draft.md:46,213` | `R4_access_control/paper/latex/main.tex:66,282` | Anonymous prose আছে; সব quoted result সংখ্যা মিলে গেছে |

| R4-এ উদ্ধৃত R3 result | R3 own draft evidence | R3 own TeX evidence | recomputation/verdict |
|---|---|---|---|
| 136 commits | `R3_silent_breaking/paper/R3_draft.md:88,247` | `R3_silent_breaking/paper/latex/main.tex:119,355` | মিলে গেছে |
| 47 REST services | একই draft:88,247 | একই TeX:119,355 | মিলে গেছে; এটি sampled repositories, full corpus 54 নয় |
| 44% observable behaviour change | একই draft:150 | একই TeX:205 | `60/136 × 100 = 44.1176%`, rounded 44% |
| 91% client-breaking changes annotation-এ silent | একই draft:169,212 | একই TeX:240,303 | `29/32 × 100 = 90.625%`, rounded 91%; R4 discussion-এর দ্বিতীয় occurrence-ও মেলে |

R4-এর নিজের 91% হলো `93/102` security fixes-এ contract document **ও** annotation অপরিবর্তিত থাকার হার (`R4_access_control/paper/R4_draft.md:173`; `paper/latex/main.tex:226`)। R3-এর 91% হলো `29/32` breaking commits-এ annotation না বদলানোর হার; contract-file silence তার sampling condition। দুই 91%-এর denominator ও population আলাদা, এবং paper-এর comparison-এ তা পৃথক study হিসেবে বলা হয়েছে। একই population বা একক estimate ধরে নিইনি।

R3-এর “same corpus” বক্তব্যকে R1-এর **40 sampled repositories** বনাম R3-এর **54-service sampling corpus** দেখে numeric contradiction ঘোষণা করিনি: sampling frame ও observed sample আলাদা। R1 draft:10,39 এবং R3 draft:57–66-এ নিজ নিজ scope আছে। R1/R3 থেকে R4-এর ফল কিংবা R1 থেকে R3-এর ফল উদ্ধৃতই নেই; তাই reverse-direction result-number check সেখানে **not applicable due to missing reference**, “সমস্ত direction passed” নয়।

## Local venue checklist

| paper | template ও author block | AI-use section | Data availability | local compliance-এর সীমা |
|---|---|---|---|---|
| R1 | acmart `acmsmall,screen,review,anonymous`; anonymous author; source:2,11 | Local replication plan-এ IEEE-জাতীয় AI section requirement নেই; অনুপস্থিতিকে violation ধরিনি | Draft:423 ও TeX:626-এ section আছে; explicit anonymous-link placeholder নেই, E04 | `VENUE.md` নেই; replication plan-এর anonymity requirement মানা হয়েছে, archive link অসম্পূর্ণ; M02 |
| R3 | `documentclass[conference]{IEEEtran}` ও anonymous block; source:2,14 | Draft:260 / TeX:370-এ আছে; affected-section scope অসম্পূর্ণ, E05 | Draft:249–250 / TeX:357–358-এ section ও `[anonymous link to be added]` আছে | Current local 10+2 ও template assumption অনুযায়ী; official 2027 confirmation বাকি, M03 |
| R4 | `documentclass[conference]{IEEEtran}` ও anonymous block; source:2,14 | Draft:259 / TeX:348-এ আছে; affected-section scope অসম্পূর্ণ, E06 | Draft:250–251 / TeX:337–338-এ section ও `[anonymous link to be added]` আছে | Local IEEE assumption অনুযায়ী; official ASE 2027 template/cap confirmation বাকি, M04 |

R3/R4-এর placeholder task-এর draft-stage criterion পূরণ করে; placeholder-কে কার্যকর deposited archive link বলছি না। Real submission-এর আগে তিনটিরই archive upload/link verification প্রয়োজন (`R3_silent_breaking/paper/VENUE.md:28`; `R4_access_control/paper/VENUE.md:19`; R1 replication plan:8,45)। Task যেহেতু placeholder চেয়েছে, R3/R4-এর placeholder থাকার জন্য আলাদা ERROR গণনা করিনি।

## LaTeX source sanity

| paper | bibliography resolve | unique cited keys / undefined | figure resolve | environment / brace / dollar-math check |
|---|---|---|---|---|
| R1 | `research/10_paper/references.bib`, source:641-এর `../references` | 12 / **0** | source:362-এর path unresolved; B01 | 1 document, 1 abstract, 59 itemize, 3 enumerate, 10 table, 10 tabularx, 1 figure; nesting balanced; braces/math balanced |
| R3 | `R3_silent_breaking/paper/latex/references.bib`, source:383 | 5 / **0** | source:228; `graphicspath` source:5 ধরে `R3_silent_breaking/paper/figures/fig_kind_impact.pdf` পাওয়া যায় | 1 document, 1 abstract, 38 itemize, 1 enumerate, 3 table, 3 tabularx, 1 figure; nesting balanced; braces/math balanced |
| R4 | `R4_access_control/paper/latex/references.bib`, source:361 | 7 / **0** | source:194; `graphicspath` source:5 ধরে `R4_access_control/paper/figures/fig_r4_setup.pdf` পাওয়া যায় | 1 document, 1 abstract, 38 itemize, 1 enumerate, 1 figure; nesting balanced; braces/math balanced |

প্রতিটি `cite` key তার সংশ্লিষ্ট bibliography-র entry-এর সঙ্গে মেলে; duplicate bibliography key নেই। Unescaped `%`, text-mode `_`/`^`, misplaced `#` বা table-এর বাইরে raw `&` পাইনি। `%`-এর একমাত্র unescaped usage প্রথম লাইনের generated-file comment; `&` table alignment-এ; macro definition-এর `#1`, bibliography key/image filename-এর underscore বৈধ। কোনো `input`/`include` subdocument নেই যার আড়ালে আলাদা source বাদ গেছে। এই ফল static review; missing packages, font metrics, overfull boxes, float placement বা compiler warning পরীক্ষা হয়নি।

## Word count ও rough page estimate

Counting convention: `## Abstract` থেকে manuscript-এর শেষ পর্যন্ত নিয়েছি, `## References` শুরু হলে তার আগেই থেমেছি। Title ও working-draft/version note বাদ; abstract, headings, Data availability ও AI disclosure অন্তর্ভুক্ত। Body total-এ table cells/captions এবং inline artifact references আছে। Markdown formatting/link destination সরিয়ে whitespace tokens-এ অন্তত একটি letter/digit/underscore থাকলে একটি word ধরেছি; ratio ও hyphenated term ভাঙিনি, standalone math/operator/Markdown punctuation গুনিনি। তুলনার সুবিধায় unnormalised `split()` count-ও দিয়েছি। R1/R4 draft-এ আলাদা References section নেই; bibliography body count-এ যোগ হয়নি।

Page estimate-এ table-row text এবং `Figure N`/`Table N` caption-marker line prose count থেকে বাদ দিয়ে প্রতিটি actual TeX figure/table float-এর জন্য 0.25–0.33 page যোগ করেছি; এতে table text ও float space দ্বিগুণ গোনা হয়নি। Caption-এর বাইরে explanatory discussion prose-তে রেখেছি। সূত্র: **lower = prose words / উচ্চ words-per-page + floats × 0.25; upper = prose words / নিম্ন words-per-page + floats × 0.33**। ACM-এর জন্য 550–600 এবং IEEE-এর জন্য 800–900 words/page, task অনুযায়ী।

| paper / template | draft body words | raw whitespace tokens | page-formula prose words | figures + tables | rough pages, references বাদে |
|---|---:|---:|---:|---:|---:|
| R1 / ACM acmsmall | **5,201** | 5,799 | 4,625 | 1 + 10 = 11 | **10.46–12.04**; প্রায় **11–13** whole pages |
| R3 / IEEE two-column | **3,202** | 3,423 | 3,044 | 1 + 3 = 4 | **4.38–5.12**; প্রায় **5–6** whole pages |
| R4 / IEEE two-column | **2,951** | 3,137 | 2,934 | 1 + 0 = 1 | **3.51–4.00**; model অনুযায়ী প্রায় **4** whole pages |

⚠️ এগুলো task-নির্ধারিত density model-এর inference, compiled page count নয়। Title/author area, প্রচুর bullet/list whitespace, long tables, float constraints এবং references-এর জায়গা আলাদাভাবে typeset হলে দৈর্ঘ্য বাড়তে পারে। R1-এর 10টি table-র কয়েকটি বড়; fixed float allowance বাস্তব height-এর নিশ্চয়তা দেয় না। R3-এর local 10 body + 2 references cap-এর নিচে body estimate; R4-ও স্থানীয় provisional 10+2 assumption-এর নিচে। References-এর exact pages বা final compliance compile ছাড়া নির্ধারণ করিনি। R1-এর verified local page cap পাওয়া যায়নি, তাই length violation ঘোষণা করিনি।

## সীমা ও অবশিষ্ট কাজ

প্রধান confirmed build সমস্যা B01। Source-এ সরাসরি identity leak বা companion-number mismatch পাওয়া যায়নি; কিন্তু missing companion references-কে পাশ করা বলা যাবে না। E01–E09 সংশোধন, M01–M05 নিষ্পত্তি, real anonymous links বসানো এবং final venue/PDF checks শেষে readiness আবার যাচাই করতে হবে। Human-check outcome, deposited archive-এর privacy, public/preprint title collision এবং official 2027 CFP এই read-only/no-network audit থেকে নিশ্চিত করা যায়নি। Findings table-এ মোট 15টি distinct issue: 1 BLOCKER, 9 ERROR, 5 MINOR।

T59 DONE 1 BLOCKER, 9 ERROR, 5 MINOR
