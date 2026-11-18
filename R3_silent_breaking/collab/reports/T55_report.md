# T55: স্বাধীন numeric ও claim-consistency review

পর্যালোচনার তারিখ: 2026-11-18। `paper/R3_draft.md` v0.2-এর **162টি statement-group** যাচাই করেছি। একই দাবি abstract, results ও conclusion-এ পুনরাবৃত্ত হলে তার প্রতিটি occurrence ledger-এ আলাদা; একটি fraction, তার rounded share ও সংশ্লিষ্ট CI একই group হতে পারে। Section number, hypothesis ID বা DOI-কে empirical observation হিসেবে গণনা করিনি; bibliographic metadata-ও আলাদাভাবে মিলিয়েছি। পূর্ণ coverage ledger: `collab/logs/T55_scratch/checks.tsv`। নিচের 30টি issue-তে একই মূল সমস্যার পুনরাবৃত্ত occurrence একত্র করেছি: **9 ERROR, 21 MINOR**। ⚠️ চিহ্নিত অংশ inference; সেগুলো সরাসরি পর্যবেক্ষিত ফল নয়।

মূল shares, CIs, κ, kind-counts এবং H-R3-1-এর p-value পুনর্গণনায় মিলে গেছে। সবচেয়ে সরল count error হলো “two repositories had fewer than three”: প্রকৃত সংখ্যা **three**। এই ভুল `R3_RESULTS.md`-তেও আছে; তাই শুধু ওই summary-এর সঙ্গে মিললে ভুলটি ধরা পড়ে না। বড় claim-সমস্যা হলো annotation proxy থেকে generator-এর বাস্তব output সম্পর্কে নিশ্চিত সিদ্ধান্ত এবং corpus-এর document availability-কে sampled parent commits-এর availability হিসেবে উপস্থাপন করা।

## Issue table

| location (section / line) | paper says | source says (file:line) | severity | suggested fix |
|---|---|---|---|---|
| 01 — §3.2 / L82 | “two had fewer than three” | `mining/pool4_inventory.json:34`: allure-server 2; `:97`: bibliothek 1; `:349`: open-banking-gateway 1। অর্থাৎ তিনটি repository। `plan/R3_RESULTS.md:6` একই ভুল পুনরাবৃত্ত করেছে। | ERROR | “three had fewer than three” লিখুন। হিসাব দিন: 44×3 + 2 + 1 + 1 = 136; 44+3 = 47, এবং আরও 7টি zero-candidate repository। |
| 02 — §3.2 / L78 | Commit-এ “at most 400 changed lines in at most 8 files” | `plan/R3_PLAN.md:29`, `collab/tasks/T53.md:31`: সীমা retained **behaviour-path files**-এর added+deleted lines ও file count-এর জন্য; পুরো commit-এর জন্য নয়। `mining/t53_pool.py:287`–`:300`-ও সেটিই করে। | ERROR | “at most 400 added/deleted lines across at most 8 retained behaviour-path files” লিখুন; অন্য ধরনের touched files এই cap-এর denominator নয়। |
| 03 — §3.2 / L75; §6 / L157 | “non-merge commit since 2023-01-01”; “window starts in 2023” | `plan/R3_PLAN.md:24`; `mining/freeze4.json:13`, `:16`; `collab/tasks/T53.md:26`: recorded HEAD-এর default-branch **first-parent** history; **UTC committer date** cutoff inclusive; upper bound recorded HEAD। | MINOR | পূর্ণ window ও branch restriction একবার স্পষ্ট করুন। “Since 2023” বাক্যটি রাখতে পারেন, তবে সেটিই সম্পূর্ণ eligibility definition নয়। |
| 04 — §3.2 / L79 | “not formatting-only” | `collab/tasks/T53.md:32`–`:34`; `mining/t53_pool.py:287`–`:297`: whitespace-only বা content-unchanged rename file আগে বাদ যায়; retained behaviour file না থাকলে commit বাদ। Mixed commit সম্পূর্ণ বাদ দেওয়ার rule নয়। | MINOR | Per-file filtering এবং rename-only exclusion লিখুন; retained files-এর উপর size cap প্রযোজ্য বলুন। |
| 05 — §3.2 / L80 | “not authored by a bot” | `plan/R3_PLAN.md:30`: নির্দিষ্ট bot-pattern rule। `collab/tasks/T53.md:35`-এ author-field heuristic-এ `github-actions`-ও আছে। এটি সব bot শনাক্ত করার প্রমাণ নয়। | MINOR | “does not match the predefined bot-author patterns” লিখে ব্যবহৃত patterns ও author-field check উল্লেখ করুন; plan-এর সংক্ষিপ্ত তালিকা ও frozen T53 rule-এর পার্থক্য disclose করুন। |
| 06 — §3.2 / L82 | “hash-frozen before any commit was read” | `plan/R3_PLAN.md:33`, `:37`-এর intended protection হলো pre-freeze sampled-commit inspection/judgement না করা। `collab/tasks/T53.md:43` metadata, document detection ও whitespace checks অনুমোদন করে; `mining/t53_pool.py:137`–`:148`, `:247`, `:260`-এ classification-এর জন্য blob bytes mechanically পড়া হয়। | MINOR | “frozen before candidate patches were inspected for behavioural judgement; mechanical discovery reads were permitted” লিখুন। Pool freeze-এর পরে sample freeze, তারপর packaging—এই order-ও বলুন। |
| 07 — Contributions / L41; conclusion / L164 | Sample/result-কে “from 54 … services” / “In 54 REST services” বলা হয়েছে | `plan/R3_PLAN.md:22`: corpus 54। `plan/r3_score_output.txt:1`, `plan/R3_RESULTS.md:6`: sampled commits আছে 47 repository-তে। Abstract L12 সঠিক 47 বলেছে। | MINOR | সর্বত্র “136 commits from 47 of a 54-service corpus” ব্যবহার করুন; corpus size ও represented sample size আলাদা রাখুন। |
| 08 — §3.1 / L72; §6 / L156; abstract-এর untouched-contract interpretation / L11, L19 | “each with a checked-in OpenAPI/Swagger document”; coverage-কে বিদ্যমান prior contract-এর নীরবতা হিসেবে পড়া যায় | `plan/R3_PLAN.md:22` corpus-level criterion। কিন্তু `plan/R3_DEVIATIONS.md:127`, `mining/key/r3_build_log.json:6780`, `plan/R3_RESULTS.md:70`: **29/136 parent commits-এ checked-in document নেই**। | ERROR | Corpus snapshot-এ document থাকা এবং sampled parent-এ থাকা আলাদা করে বলুন। No-document items অন্তর্ভুক্ত থাকার কথা method ও threats-এ লিখুন; “unchanged contract” এখানে “no detected contract-file modification”, document অবশ্যই উপস্থিত ছিল এমন নয়। |
| 09 — §3.3 / L88; abstract / L19; discussion / L144; conclusion / L164; §6-এ omission | সব package-এ “parent contract, projected to the affected operations”; “only 1 of 60” থেকে contract-এর প্রকৃত coverage সম্পর্কে দৃঢ় সিদ্ধান্ত | `plan/R3_DEVIATIONS.md:55`–`:63`, `:125`–`:130`; `mining/key/r3_build_log.json:6777`–`:6782`: mapped_operations 3, raw_fallback 93, no_checked_in_document 29, bounded_document_prefix 6, whole_document 5। `plan/R3_RESULTS.md:70` contract_specified judgements-কে approximate বলেছে। | ERROR | Actual mapping-mode counts দিন। Raw fallback হলো redacted first-2,000-line root text, affected-operation projection-এর নিশ্চয়তা নয়। Coverage ফলকে “coded as SPECIFIED in the delivered parent-contract context” বলুন; truncated/missing context-এ “never described” সিদ্ধান্ত সমর্থিত নয়। §6-এ এই সীমাবদ্ধতা অবশ্যই যোগ করুন। |
| 10 — abstract / L18; introduction / L24; Contributions / L43; §3.5 / L102; discussion / L143; conclusion / L164 | No annotation edit হলে AutoGuard বা অন্য code-generated contract-ও বদলাবে না / কিছুই reveal করবে না | `plan/R3_PLAN.md:55`, `:89` annotation-based operational proxy নির্ধারণ করে, actual generator চালানোর ফল নয়। Paper-এর নিজের `paper/R3_draft.md:159` বলে generator types থেকেও infer করতে পারে। `plan/R3_RESULTS.md:62` একই categorical overclaim করেছে; summary মিললেও inference প্রমাণ হয় না। | ERROR | 29/32, 91%, p-value রাখুন; দাবি করুন “edit no detected contract-annotation line; by our annotation proxy these are candidates for being missed”। ⚠️ Actual generated output বা tool recall এখানে পরীক্ষা হয়নি। Checked-in document diff-এর invisibility এবং generated document-এর invisibility এক দাবি নয়। |
| 11 — RQ4 / L38; §3.6 / L109; §4.4 / L139 | RQ4 documentation lag জিজ্ঞেস করে; result-এ শুধু H-R3-2 INSUFFICIENT এবং contract coverage বলা হয়েছে | `plan/R3_PLAN.md:19`: affected-operation update descriptive RQ4। `:56`–`:59`: hypothesis-এ repository-level proxy, operation refinement descriptive only। `:93`–`:95`: BREAKING+SPECIFIED subset, n≥8 দরকার। `plan/r3_scores.csv:5`, `plan/r3_score_output.txt:10`: **0/1 no-update**, অর্থাৎ একমাত্র eligible case-এ update ঘটেছে। | ERROR | পরিষ্কার করুন যে §3.6-এর H-R3-2 definition plan-এর সমতুল্য—এখানে hypothesis বদলায়নি। কিন্তু broad/operation-level RQ4-এর descriptive result দেওয়া হয়নি। “0/1 had no repository-level contract update; insufficient because n=1<8” লিখুন। Operation-level lag অনির্ণীত বলুন; broader repository-level descriptives দিলে নতুন descriptive result হিসেবে label দিন। |
| 12 — abstract / L19; §4.4 / L139 | 60-এর মধ্যে 1 SPECIFIED, 56 UNSPECIFIED; বাকি তিনটির ব্যাখ্যা নেই | `plan/R3_RESULTS.md:42`; `plan/r3_score_output.txt:14`: **3 UNCLEAR**। Breaking subset-এ SPECIFIED 1, UNSPECIFIED 28, UNCLEAR 3। | MINOR | “1 specified, 56 unspecified, 3 unclear” লিখুন। সব অবশিষ্ট case-কে implicit UNSPECIFIED ধরে নেবেন না। |
| 13 — §4.2 / L133 | “added response fields (response shape, 8/8)” | `plan/R3_RESULTS.md:39`: response shape 8/8 compatible, **mainly** added fields। Taxonomy-তে shape আরও বিস্তৃত (`plan/TASK_R3.md:34`)। Coder metadata-তেও B117-এ count-population ও optional flag-এর আচরণ আছে (`packages/r3_blind/codes_G1.csv:118`, `codes_G2.csv:118`)। | MINOR | “All eight sampled RESPONSE_SHAPE cases were coded COMPATIBLE, mainly involving added fields” লিখুন; added-fields subtype-এর 8/8 measurement দাবি করবেন না। |
| 14 — introduction / L29 | Quote শুরু “the main remaining gap …” | `notes/NOVELTY_VERIFIED.md:22`: **“The main remaining gap …”**। Initial capital বদলেছে। | MINOR | Quote-এর শুরুতে “The” ফিরিয়ে দিন; verbatim রাখুন। |
| 15 — §2 / L59 | Quote শুরু “detection of syntactic breaks …” | `notes/NOVELTY_VERIFIED.md:21`: **“Detection of syntactic breaks …”**। | MINOR | “Detection” লিখুন; quotation-এর case অক্ষুণ্ণ রাখুন। |
| 16 — §2 / L62 | “often shift the problem, i.e., create semantic breaking changes instead” | `notes/NOVELTY_VERIFIED.md:19`: **“often shifts the problem, i.e., creates semantic breaking changes instead.”** | ERROR | Quote-এ “shifts” ও “creates” ফিরিয়ে দিন এবং surrounding sentence ব্যাকরণমাফিক পুনর্গঠন করুন; অথবা quote বাদ দিয়ে paraphrase করুন। |
| 17 — §2 / L53–L54; References / L170; verification claim / L169 | AutoGuard claim ও “do not capture semantic changes” একই verified-reference তালিকার অংশ বলে উপস্থাপিত | `notes/NOVELTY_VERIFIED.md:6`–`:24`-এ AutoGuard-এর নিজস্ব verified entry নেই; review-এর AutoGuard description আছে `:23`-এ। তবে quote-টি **সমর্থিত**: `notes/NOVELTY.md:12`; local text `lit/autoguard/Lercher2025-AutoGuard.txt:342`, `:344`। Title মেলে local text `:1`–`:2`-এ। | MINOR | AutoGuard-এর verification addendum entry ও local full-text locator যোগ করুন, অথবা original frozen NOVELTY entry-টি স্পষ্টভাবে cite করুন। এটিকে fabricated quote বলা হচ্ছে না; requested addendum-এ provenance অসম্পূর্ণ। |
| 18 — §3.1 / L72 | “20 of them were chosen by metadata criteria alone” | `plan/R3_PLAN.md:22` শুধু 34 earlier repositories এবং 20 T50 repositories বলে। R3 workspace-এর reviewed source-এ “metadata criteria alone” selection basis পাওয়া যায়নি। | MINOR | T50 selection report/criteria-এর নির্দিষ্ট citation দিন, অথবা শুধু “20 came from the T50 expansion” লিখুন। **20 সংখ্যাটি মেলে; selection claim trace করা যায়নি।** |
| 19 — discussion / L142 | “Silent change is the norm, not the exception.” | `plan/r3_scores.csv:2`: 60/136 = 44.12%; `plan/R3_RESULTS.md:54`: Claude 55/136 = 40.44%। দুই estimate-ই অর্ধেকের নিচে। | ERROR | “Silent observable change is common” লিখুন। “Norm” যদি majority বোঝায়, এই ফল তা সমর্থন করে না। |
| 20 — discussion / L142 বনাম abstract, §4.1, conclusion | “Roughly two in five” বনাম primary 44% | `plan/r3_scores.csv:2`: primary 44.12%; `plan/R3_RESULTS.md:56`: model-family range 40–44%। “Two in five” coarse approximation; exact contradiction নয়। | MINOR | Primary result বোঝালে “about 44%, or a little over two in five” লিখুন; cross-family range বোঝালে “40–44%” দিন। |
| 21 — conclusion / L164 | “44% of behaviour-changing commits … alter observable behaviour” | `plan/R3_PLAN.md:16`, `:27`; `plan/r3_scores.csv:2`: denominator **136 behaviour-path-touching candidates**, যার মধ্যে YES 60, NO 50, UNCLEAR 26 (`plan/r3_score_output.txt:6`)। Denominator আগে থেকেই actual behaviour-changing commits নয়। | ERROR | “44% of sampled commits touching production behaviour-path code, without modifying a detected contract file, were coded as changing observable API behaviour” লিখুন। |
| 22 — §4.1; §6 / L148–L153 | Shares ও CIs আছে, কিন্তু observable UNCLEAR count নেই | `plan/r3_score_output.txt:6`: GPT YES/NO/UNCLEAR = **60/50/26**; `plan/R3_PLAN.md:80` disagreement-কে UNCLEAR করে। ফলে 26/136 = 19.12% candidate unresolved। | MINOR | তিনটি label-count দিন এবং বলুন 44% হলো সব sampled candidates-এর মধ্যে confirmed-YES coding share; UNCLEAR-ও denominator-এ আছে। κ 0.94 শুধু 102 both-decided item-এর জন্য—abstract-এর agreement wording-এও এই restriction সংক্ষেপে বলুন। |
| 23 — §3.3 / L90; §6-এ omission | Coders “do not see the commit message …”; residual blinding risk উল্লেখ নেই | `plan/R3_DEVIATIONS.md:71`–`:73`: short বা two-word distinctive message fragment source/contract-এ থাকলে unredacted থাকতে পারে। `plan/R3_AUDIT.md:17`: out-of-package read পাওয়া যায়নি। অর্থাৎ actual leakage প্রমাণিত নয়, কিন্তু guarantee-ও নয়। | MINOR | “Metadata were withheld/redacted; no external-history reads were found” বলুন। §6-এ residual in-source linkage/evaluative-hint risk লিখুন; coder সত্যিই message দেখেছে—এমন দাবি করবেন না। |
| 24 — §6 / L152–L153 | LLM threat-এ শুধু দুই model family ও planned spot-check | `plan/R3_AUDIT.md:11`–`:12`; `plan/R3_RESULTS.md:69`: Claude batches 31–67 s, 7–18 tool calls; ⚠️ mostly bulk diff reading-এর আশঙ্কা recorded threat। | MINOR | Timing ও inspection-depth concern যোগ করুন; “mostly read diffs” অংশটিকে audit-এর inference হিসেবে রাখুন, প্রতিষ্ঠিত observation হিসেবে নয়। |
| 25 — §3; §6-এ process omission | Design frozen plan-এর summary; mining handover/deviations অনুল্লেখিত | `plan/R3_DEVIATIONS.md:4`–`:23`, `:29` onward; `plan/R3_RESULTS.md:72`: usage-limit-এর পরে hypotheses-জানা supervisor mining শেষ করেছেন; F1–F6d mechanical fixes coding-এর আগে; judgement step ছিল না। | MINOR | একটি process-deviation paragraph ও `R3_DEVIATIONS.md` citation দিন। Frozen scoring/coding safeguards বজায় ছিল এবং sample resample হয়নি—এটিও বলুন। অযাচিত selection bias ঘটেছে বলে দাবি করার ভিত্তি নেই। |
| 26 — §6 / contract-context threat omission | Redaction-এর কারণে evidence loss উল্লেখ নেই | `plan/R3_DEVIATIONS.md:100`, `:111`, `:116`–`:119`: fixpoint redaction, কখনও whole-line `[REDACTED]`, এবং truncated JSON-এর পুনরায় redaction। Privacy বজায় রাখলেও delivered context মূল text-এর সম্পূর্ণ বিকল্প নয়। | MINOR | ⚠️ Redaction ও truncation semantic/coverage judgement দুর্বল করতে পারে—এমন সম্ভাব্য construct threat যোগ করুন। Item contents না দেখে actual label error-এর সংখ্যা দাবি করবেন না। |
| 27 — §6 / sampling threat omission | Candidate pool eligibility gap উল্লেখ নেই | `plan/R3_DEVIATIONS.md:68`–`:70`: behaviour-looking pure gitlink pool-এ ঢোকার সম্ভাব্য gap; **কোনো sampled commit-এ gitlink নেই**, সব sampled commit-এ source blob আছে; frozen pool রাখা হয়েছে। | MINOR | সংক্ষিপ্ত process note দিন: pool-level gap known, sampled items-এ mechanical check-এ affected case শূন্য। এটিকে observed sample contamination বলা যাবে না। |
| 28 — §6 / L155 | “Three commits per repository weight repositories equally” | `plan/R3_PLAN.md:34`; inventory `mining/pool4_inventory.json:34`, `:97`, `:349`: 44 repository-তে 3, একটিতে 2, দুটিতে 1। Pooled commit estimator-এ সবার exact weight সমান নয়। | MINOR | “We targeted up to three commits per repository, reducing commit-volume dominance; three repositories contributed fewer” লিখুন। |
| 29 — §3.5 / L103; §6 / L161 | “within 90 days” field-কে full follow-up হিসেবে পড়া যায়; শুধু over-counting/conservativeness caveat আছে | `collab/tasks/T53.md:88`: history কেবল recorded HEAD পর্যন্ত। `mining/sample4.json:1`-এর date fields এবং key metadata থেকে independent check: review date 2026-11-18-এর 90 দিনের মধ্যে **12 item**, যার **3টিতে field false**। | MINOR | ⚠️ নতুন audit inference: right-censoring সম্ভব; false মানেই completed 90-day no-update নয়। Observation end ও censoring rule লিখুন। বর্তমান H-R3-2-তে একমাত্র eligible item updated, তাই n=1/INSUFFICIENT verdict বদলায় না। |
| 30 — §2 / L48; References / L171 | Tools-এর removed-operation/new-required-parameter/type-change rules; practice-study full subtitle | `notes/NOVELTY.md:18` tools-এর broad spec-diff scope বলে, নির্দিষ্ট rule-list নয়। `notes/NOVELTY_VERIFIED.md:15` title-এর মূল অংশ, year, venue ও DOI দেয়; full subtitle নয়। | MINOR | Tool rule examples-এর versioned official documentation ও পূর্ণ bibliographic record-এর local evidence যোগ করুন, অথবা unsupported specificity কমান। Offline review-এ এই দুটি detail trace করা যায়নি; এগুলো মিথ্যা প্রমাণিত হয়নি। |

## স্বাধীন পুনর্গণনা

সব Python computation `/usr/bin/python3 -I -B` দিয়ে হয়েছে। Frozen scorer execute/import করিনি, তার output file-ও পরিবর্তন করিনি। Reproduction command:

```text
/usr/bin/python3 -I -B collab/logs/T55_scratch/recompute.py
```

**Input limitation:** `plan/r3_scores.csv:1`–`:6` কেবল `measure,k,n,result` schema-তে পাঁচটি aggregate row। এটি per-item score table নয়। তাই ওই CSV থেকে shares, Wilson intervals এবং H-R3-1 p নিজে হিসাব করেছি; **kind, annotation, contract coverage, language বা coder-family counts শুধু ওই CSV থেকে পুনর্গণনা করা অসম্ভব**। সেগুলোর জন্য permitted coder-output metadata (`packages/r3_blind/codes_G1.csv`, `codes_G2.csv`, `packages/r3_kb*/codes_H1.csv`, `codes_H2.csv`) ও `mining/key/r3_key.csv` join করে agreement→final-code rule নিজে reimplement করেছি। কোনো item diff/source/contract content খোলা হয়নি। Metadata থেকে পাওয়া aggregates পরে `R3_RESULTS.md` ও `r3_score_output.txt`-এর সঙ্গে মিলিয়েছি। Machine-readable ফল: `collab/logs/T55_scratch/recomputed.json`; অতিরিক্ত mapping/date aggregates: `collab/logs/T55_scratch/independent_numbers.json` ও নিচের বিবরণ।

| measure | স্বাধীন ফল | source cross-check |
|---|---|---|
| GPT observable | 60/136 = 0.4411764706; Wilson 95% [0.3604814617, 0.5251032559] | `plan/r3_scores.csv:2`; rounded 44%, [36%,53%] সঠিক |
| GPT breaking | 32/136 = 0.2352941176; Wilson 95% [0.1718861157, 0.3132451136] | `plan/r3_scores.csv:3`; rounded 24%, [17%,31%] সঠিক |
| Claude observable / breaking | 55/136 = 0.4044117647; 12/136 = 0.0882352941 | `plan/r3_score_output.txt:67`; 40%, 9% সঠিক |
| H-R3-1 | 29/32 = 0.90625; P[Binomial(32,0.5)≥29] = 1.2780074030×10⁻⁶ | `plan/r3_scores.csv:4`; 91%, 1.3×10⁻⁶, PASS সঠিক |
| Observable annotation_touched | true 8, false 52; মোট 60 | `plan/r3_score_output.txt:15` |
| Breaking annotation_touched | true 3, false 29; মোট 32 | `plan/r3_score_output.txt:9` |
| সব item annotation_touched | true 16, false 120; মোট 136 | `mining/key/r3_build_log.json:6772` |
| Observable contract_specified | SPECIFIED 1, UNSPECIFIED 56, UNCLEAR 3 | `plan/r3_score_output.txt:14` |
| Breaking contract_specified | SPECIFIED 1, UNSPECIFIED 28, UNCLEAR 3 | `plan/r3_score_output.txt:14` |
| H-R3-2 | BREAKING+SPECIFIED n=1; no-update 0, update 1; minimum n=8 পূরণ হয়নি | `plan/r3_scores.csv:5`; `plan/R3_PLAN.md:95`; INSUFFICIENT সঠিক |
| Within-family observable κ | GPT 0.9044272663; Claude 0.8243941200 | `plan/r3_score_output.txt:2`; rounded 0.90, 0.82 সঠিক |
| Cross-family observable κ | 99 agreement / 102 both-decided; κ=0.9412216673 | `plan/r3_scores.csv:6`; H-R3-3 threshold 0.6, minimum n=30 পূরণ; PASS সঠিক |
| Cluster bootstrap, 2,000 resamples / seed 1 | observable [0.3529411765, 0.5251798561]; breaking [0.1631205674, 0.3120567376] | `plan/R3_PLAN.md:86`; `plan/r3_score_output.txt:7`–`:8`; Wilson-এর কাছাকাছি বলাটি সমর্থিত |
| Leave-one-repository-out breaking share | min 0.2255639098; max 0.2406015038; full estimate থেকে max absolute difference 0.0097302079 | `plan/r3_score_output.txt:66`; “less than 0.01” সঠিক |
| Breaking family-count ratio | 32/12 = 2.6666666667 → 2.7 | `plan/R3_RESULTS.md:53`–`:54` |

Wilson গণনায় z=1.959963984540054; H-R3-1-এ exact upper-tail sum ব্যবহার করেছি। অতিরিক্ত diagnostic interval গণনা করা থাকলেও H-R3-2-তে testযোগ্য p বা substantive hypothesis verdict তৈরি করিনি। κ agreement fraction নয়; raw coder labels থেকে marginals-সহ নিজে হিসাব করেছি।

| GPT final kind | observable n | BREAKING | COMPATIBLE | UNCLEAR impact |
|---|---:|---:|---:|---:|
| RESPONSE_CONTENT | 9 | 7 | 2 | 0 |
| STATUS_OR_ERROR_MAPPING | 9 | 7 | 1 | 1 |
| RESPONSE_SHAPE | 8 | 0 | 8 | 0 |
| SIDE_EFFECT_OR_STATE | 7 | 2 | 3 | 2 |
| INPUT_STRICTER | 6 | 6 | 0 | 0 |
| INPUT_LOOSER | 5 | 0 | 5 | 0 |
| AUTHZ_OR_AUTH | 4 | 2 | 1 | 1 |
| HEADER_OR_MEDIA_TYPE | 2 | 1 | 1 | 0 |
| DEFAULT_OR_OPTIONALITY | 2 | 2 | 0 | 0 |
| ORDERING_PAGINATION_LIMITS | 2 | 2 | 0 | 0 |
| OTHER | 1 | 0 | 1 | 0 |
| UNCLEAR kind | 5 | 3 | 0 | 2 |
| **মোট** | **60** | **32** | **22** | **6** |

উপরের kind ও impact cross-tab `plan/r3_score_output.txt:12`–`:14`-এর সঙ্গে মেলে। Taxonomy-তে 11 category; disagreement-এর UNCLEAR আলাদা label, দ্বাদশ substantive category নয়।

| language | sampled n | observable YES | BREAKING |
|---|---:|---:|---:|
| Java | 85 | 37 | 19 |
| Go | 48 | 21 | 13 |
| Kotlin | 3 | 2 | 0 |
| **মোট** | **136** | **60** | **32** |

এটি `plan/r3_score_output.txt:16`–`:18`, sample metadata ও key metadata-র সঙ্গে মেলে। Inventory থেকে 54 repository ও 18,590 candidate নিজে sum করেছি; zero pool 7, positive pool<3 repository **3**। Sample metadata থেকে 136 item, 47 unique repository এবং ভাষার একই counts পেয়েছি। Build summary (`mining/key/r3_build_log.json:6771`–`:6785`) delivered 136, failures 0 নিশ্চিত করে।

## Freeze, blinding ও single-run দাবির সীমা

`plan/r3_plan_freeze.sha256`-এর 7/7 regular-file hash, `r3_packages_freeze.sha256`-এর 28/28 regular-file hash এবং `r3_outputs_freeze.sha256`-এর 45/45 regular-file hash মিলে গেছে। Plan manifest-এ scorer এবং self-test দুটোই আছে, এবং package manifest-এ তাদের একই hash আছে। Inventory ও sample-এর SHA-256 যথাক্রমে `mining/freeze4.json:10` ও `mining/freeze4_sample.json:61`-এর সঙ্গে মেলে। Package freeze-এর **11টি TREE entry recompute করিনি**, কারণ তাতে নিষিদ্ধ item contents খুলতে হতো; package-content integrity-এর পূর্ণ verification দাবি করছি না। Salt খোলা হয়নি।

`plan/R3_PLAN.md:4`–`:8`, `plan/R3_DEVIATIONS.md:2`, `plan/R3_AUDIT.md:1`, এবং `plan/R3_RESULTS.md:2` মিলে **internally pre-registered / frozen before mining / frozen before coding / scored once** দাবির documented chain সমর্থন করে। Audit-এ coder-এর out-of-package read পাওয়া যায়নি (`R3_AUDIT.md:17`)। Six denied protocol-path attempts-এ content পড়া হয়নি (`:13`); সেগুলোকে blinding breach বলছি না। Hash matching নিজে independent timestamp বা scorer invocation counter নয়; “একবারই execute হয়েছে” কথাটির ভিত্তি process record, hash alone নয়।

Plan-এর H-R3-2 “fewer than half updated” এবং paper §3.6-এর “most see no update” একই binary hypothesis। §4.4-এর INSUFFICIENT-ও সঠিক। অসামঞ্জস্যটি hypothesis পরিবর্তন নয়; operation-level descriptive RQ4, repository-level hypothesis proxy এবং actual lag count আলাদা করে না বলায় ফলের scope অস্পষ্ট (issue 11)।

## Citation ও quotation audit

চাওয়া সব literature number মিলে গেছে: **17, 5/17** (`notes/NOVELTY_VERIFIED.md:15`–`:16`), **2.30% / 2.3%, 30,548** (`:7`–`:8`), **87.3%, 2,224, 1,368** (`:12`–`:13`), এবং **97** (`:20`)। Venue/year, উল্লিখিত DOI এবং arXiv identifier-ও ledger-এ মিলিয়েছি; subtitle ও AutoGuard provenance-এর সীমা issue 17 ও 30-এ আছে। Addendum-এর unverified **9 of 21** paper-এ ব্যবহার করা হয়নি।

Paper-এর আটটি literature quote-fragment-এর মধ্যে চারটি addendum-এর exact substring: L28, L49, L55 এবং L62-এর প্রথম quote। L29 ও L59-এ initial capital বদলেছে; L62-এর দ্বিতীয় quote-এ দুটি verb বদলেছে। L54-এর AutoGuard fragment addendum-এ নেই, তবে frozen novelty note ও local full text-এ আছে। বড় quote থেকে শেষ full stop-এর আগেই excerpt শেষ হওয়াকে শব্দগত mismatch ধরিনি।

## §6-এ অনুল্লেখিত known limitations

এই তালিকা একই issue-র duplicate count নয়। Recorded threats বা process limitation যেগুলো §6-এ নেই:

- **Contract context:** raw fallback 93/136, missing parent document 29/136; contract_specified approximate (`plan/R3_RESULTS.md:70`; issues 08–09)। Whole-line redaction ও truncation-এর evidence-loss সম্ভাবনাও disclose করা দরকার (`plan/R3_DEVIATIONS.md:111`, `:116`–`:119`; issue 26; ⚠️ effect on labels inference)।
- **Inspection depth:** Claude batches-এর 31–67 s / 7–18 tool calls এবং ⚠️ shallow/bulk diff-reading concern (`plan/R3_AUDIT.md:11`–`:12`, `plan/R3_RESULTS.md:69`; issue 24)।
- **Blinding residual:** short/two-word message-to-source linkage রয়ে যাওয়ার risk (`plan/R3_DEVIATIONS.md:71`–`:73`; issue 23)। Actual leak শনাক্ত হয়েছে এমন evidence নেই।
- **Process deviation:** hypotheses-জানা supervisor-এর mining completion এবং pre-coder mechanical fixes (`plan/R3_RESULTS.md:72`, `plan/R3_DEVIATIONS.md:4` onward; issue 25)।
- **Pool eligibility gap:** possible pure-gitlink candidates; sample-এ zero affected case, pool অপরিবর্তিত (`plan/R3_DEVIATIONS.md:68`–`:70`; issue 27)।
- **Observable uncertainty:** GPT 26/136 unresolved (`plan/r3_score_output.txt:6`; issue 22)। ফলের model-family sensitivity paper-এর discussion-এ আছে; §6-এ planned human check-কে বিশেষত client_impact validation-এর সঙ্গে যুক্ত করলে `plan/R3_RESULTS.md:64` আরও যথাযথভাবে প্রতিফলিত হবে।

সব mechanical repair-কে unresolved limitation ধরিনি। Zero final build failures, completed outputs, denied protocol reads এবং scorer-এর জন্য harmless reordered H2 rows (`plan/R3_AUDIT.md:13`, `:15`, `:17`) আলাদা করে নতুন ERROR নয়। F4/F5 policy change-এর কারণে expected দুই synthetic-test failure-ও বাস্তব sample failure প্রমাণ করে না (`plan/R3_DEVIATIONS.md:92`–`:95`)।

Right-censoring issue 29 উপরোক্ত তিনটি summary-তে explicit known threat হিসেবে লেখা নেই; সেটি এই review-এর **⚠️ নতুন inference**, recorded omission হিসেবে চালানো হয়নি।

## যেসব statement সম্পূর্ণ trace করা যায়নি

1. **L72-এর “20 … metadata criteria alone”:** 20-এর source আছে, selection basis-এর local R3 source নেই।
2. **L48-এর নির্দিষ্ট tool rule examples:** broad spec-diff scope-এর source আছে; প্রতিটি tool-এর ওই rule-list-এর evidence reviewed notes-এ নেই।
3. **L171-এর full title subtitle:** মূল title, year, venue ও DOI মেলে; subtitle addendum-এ নেই।
4. **L133-এর সব আটটি response-shape item-কে added-field subtype বলা:** 8/8 COMPATIBLE trace ও recompute হয়েছে; narrower subtype assertion-এর aggregate evidence নেই। Source বলে “mainly”; এই review item contents খোলেনি।
5. **শুধু `NOVELTY_VERIFIED.md`-এ trace করলে L53–L54 ও AutoGuard-এর নিজস্ব full bibliography মেলে না।** Supplemental frozen note/local text দিয়ে substantive claim ও quote trace হয়েছে; এটি wholly untraceable claim নয়।
6. **শুধু `r3_scores.csv` থেকে** kind/breaking-by-kind, annotation, contract_specified, per-language, Claude counts বা within-family κ recover করা যায় না। Supplemental frozen metadata দিয়ে পুনর্গণনা করেছি; CSV-কে per-item dataset হিসেবে দাবি করছি না।

⚠️ Rare-input reachability (L150), static reachability uncertainty (L151), behavioural testing-এর সম্ভাব্য উপকার (L144), এবং type inference-এর সম্ভাবনা (L159) logical threat/implication; এই review item execution বা content inspection দিয়ে এগুলো যাচাই করেনি। L167-এর archive release ও licence inclusion future commitment, সম্পন্ন release হিসেবে যাচাই করা যায় না।

Paper, plan, frozen outputs বা upstream code পরিবর্তন করা হয়নি; network বা git write ব্যবহার করা হয়নি। Paper SHA-256: `97f03a8b9686d589e7071b4dfa3ed593ae6cf1f9af18d219bdadde4345530242`। Findings ও helper artifacts কেবল অনুমোদিত report/scratch paths-এ লেখা হয়েছে।

T55 DONE 162 checked, 9 ERROR, 21 MINOR
