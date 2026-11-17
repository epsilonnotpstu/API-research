# T54: F1–F3-এর independent review

তারিখ: ২০২৬-১১-১৭। Offline code review ও synthetic পরীক্ষা সম্পন্ন। `t53_*.py` এবং `test_t53.py` অপরিবর্তিত রাখা হয়েছে। নিচের ISSUE-গুলো synthetic counterexample; বাস্তব sample বা package-এ এগুলো ঘটেছে—এমন দাবি করা হচ্ছে না।

## Verdict

| Fix | Verdict | মূল সিদ্ধান্ত |
| --- | --- | --- |
| F1 | **ISSUE** | `submodule → None` protocol handling ঠিক। কিন্তু downstream candidate check gitlink-কে behaviour file হিসেবে নিতে পারে; D1-এর non-behaviour দাবিটি সম্পূর্ণ কার্যকর হয়নি। |
| F2 | **ISSUE** | Threshold হুবহু কার্যকর, কিন্তু ছোট বা দুই-শব্দের distinctive message text redaction ও package scan দুটিই পার হতে পারে। |
| F3 | **ISSUE** | মূল raw fallback, parent provenance, line bound ও content scan সঠিক। তবে unsafe-reference `ContractError`-ও ধরা পড়ে fallback হয়; D1-এর unsafe-path failure দাবির এই ব্যতিক্রম আছে। এছাড়া shared filename scan gap fallback-এও প্রযোজ্য। |

F1-এর ISSUE হলো protocol fix-এর পরে প্রকাশ পাওয়া existing eligibility gap। F3-এর filename gap-ও আগে থেকে থাকা shared সমস্যা। এগুলোকে সংশ্লিষ্ট এক লাইনের পরিবর্তনে নতুন করে তৈরি হওয়া bug বলা হচ্ছে না।

## F1: protocol সঠিক, candidate eligibility অসম্পূর্ণ

`mining/t53_pool.py:111`-এ `missing` ও `submodule` দুটিই `None` হয়। এই উত্তরগুলোর কোনো blob payload নেই; `continue` পরের response সঠিকভাবে পড়তে দেয়। `--batch` ও `--batch-check` দুটির জন্যই synthetic protocol stream-এ পরবর্তী blob অক্ষত ছিল। বাস্তব synthetic bare Git repo-তেও gitlink ও missing path `None`, সাধারণ source path blob হয়েছে। `Git.blob`-ও `None` ফেরায় (`t53_pool.py:153`)। Submodule-এর content পড়া বা fetch করা হয় না।

Document detection-এ non-blob বাদ যায় (`t53_pool.py:142`, `t53_pool.py:185`)। Incremental discovery-তে `None` হলে path সরানো হয় (`t53_pool.py:265`)। Parent contract blob-কে gitlink দিয়ে বদলালে parent document change হিসেবে সেই commit বাদ পড়ে (`t53_pool.py:272`); পরের commit-এর roots-এ পুরোনো contract থাকে না। এই আচরণ পরীক্ষায় সঠিক ছিল।

**Counterexample:** শুধুমাত্র source-সদৃশ `api/handler.go` নামের নতুন gitlink যোগ করা synthetic commit pool-এ ঢুকেছে এবং package preparation-ও পেরিয়েছে। অথচ তার কোনো `before/` বা `after/` source blob নেই। কারণ candidate loop কেবল path predicate, numstat ও whitespace diff পরীক্ষা করে (`t53_pool.py:288`, `t53_pool.py:291`, `t53_pool.py:294`); parent/child blob type চায় না। Builder missing blob skip করে (`t53_build.py:84`)। Reproducer: `mining/test_t54.py:126`।

**Concrete patch suggestion:** `discover`-এ tree update-এর আগে changed paths-এর parent kind সংরক্ষণ করুন। `:288`-এর path selection-এ `behaviour(p)`-এর সঙ্গে parent **অথবা** child-এ `kind == 'blob'` শর্ত দিন। Child record `updated[sha + ':' + p]` থেকে পাওয়া যায়। Pure gitlink add/update বাদ যাবে; সত্যিকারের source deletion বা blob→gitlink replacement-এ parent source-এর deletion বাদ পড়বে না। শুধু child blob চাওয়া ঠিক হবে না। F1-এর protocol line রাখুন।

**প্রভাব:**

- **Pool:** আগে error হওয়া traversal এখন শেষ হয়; সংশ্লিষ্ট gitlink source-সদৃশ হলে অতিরিক্ত ineligible candidate ঢুকতে পারে। আগে সফল হওয়া সাধারণ blob/missing response-এর semantics বদলায়নি।
- **Sample:** একই pool দিলে sampler অপরিবর্তিত (`t53_sample.py:13`)। কিন্তু candidate set বদলালে seeded draw-ও বদলাতে পারে; পুরোনো aborted run-এর সঙ্গে সম্পূর্ণ pool equality দাবি করা যায় না। Code hash checkpoint invalidation রয়েছে (`t53_pool.py:329`, `t53_pool.py:349`); বাস্তবে সব repo rediscover হয়েছে কি না এখানে পরীক্ষা করা হয়নি।
- **Leakage:** F1 submodule content package-এ আনে না। মূল ঝুঁকি eligibility ও source-শূন্য item; shared privacy সীমাবদ্ধতা আলাদা।
- **Determinism:** fixed Git objects ও code-এ response handling deterministic। পুনরায় discovery এবং sampling একই ফল দিয়েছে (`test_t54.py:106`)।

⚠️ এই eligibility patch গ্রহণ করলে pool/sample বদলাতে পারে; existing freeze রেখে নিঃশব্দে প্রয়োগ করা উচিত নয়। এই review কোনো freeze বা sample বদলায়নি।

## F2: length ও word count distinctiveness-এর নিশ্চয়তা নয়

`mining/t53_privacy.py:29` stripped line-এর অন্তত ২০ character এবং whitespace split-এ অন্তত ৩ word চায়; sorting/deduplication deterministic। Ticket/issue/PR extraction আলাদা রয়েছে (`:30`, `:31`); SHA context তৈরি হয় `t53_build.py:75`-এ। Threshold ও independent ID redaction-এর synthetic পরীক্ষা পাস করেছে।

কিন্তু D1-এর “Distinctive message text … is still redacted” দাবিটি সার্বিকভাবে সত্য নয় (`plan/R3_DEVIATIONS.md:47`)। একটি ছোট স্বতন্ত্র subject, দীর্ঘ দুই-শব্দের subject, অথবা একটি স্বতন্ত্র identifier এই threshold-এ বাদ পড়তে পারে। Source comment, API description বা string literal-এ সেটি থাকলে আলাদা secret/email/date/SHA rule নাও মিলতে পারে। **Concrete residual risk: message-to-source/contract exact-text linkage দিয়ে blind item-এর commit শনাক্ত করা বা message-এর evaluative hint পড়ে ফেলা।** এটি credential leak না হলেও metadata leakage ও blinding failure।

`context_for_repo` কেবল filtered needles জমায় (`t53_build.py:73`)। `redact_text` সেই তালিকাই ব্যবহার করে (`t53_privacy.py:47`); `findings` আবার একই redactor চালায় (`:137`); package scan-ও একই context ব্যবহার করে (`t53_build.py:142`)। ফলে scan-এর clean ফল বাদ-পড়া message text অনুপস্থিত থাকার স্বাধীন প্রমাণ নয়।

**প্রস্তাবিত test বাস্তব message ছাড়াই যোগ করা হয়েছে:** সম্পূর্ণ invented ছোট তিন-শব্দের marker, দীর্ঘ দুই-শব্দের marker এবং এক-শব্দের marker message ও source comment-এ বসানো। বর্তমান code-এ তিনটিই অক্ষত থাকে এবং দুই scan clean হয় (`test_t54.py:160`)। Synthetic commit থেকে সম্পূর্ণ `prepare()` চালিয়েও ছোট invented subject package-এর in-memory bytes-এ পাওয়া গেছে (`test_t54.py:175`)। কোনো real message পড়া বা ছাপা হয়নি।

**Concrete patch suggestion:** `:29`-এ threshold-এর বদলে সব non-empty stripped message line রাখুন (`if s.strip()`); বিদ্যমান boundary-aware replacement ও deterministic ordering রাখুন। অন্তত final leakage check-এর জন্য এই unfiltered তালিকা অবশ্যই চাই। Generic-word collision ফিরতে পারে; strict no-message rule ও byte-identical task copy-এর conflict হলে mechanical failure হিসেবে ধরতে হবে। Generic text exempt করার নীতি আলাদা অনুমোদিত deviation ছাড়া length heuristic দিয়ে ধরে নেওয়া যাবে না। নতুন privacy regression-এ invented markers **অনুপস্থিত** থাকা, অথবা package build fail হওয়া চাই; বর্তমান characterization tests সফল হওয়া মানে gap পুনরুৎপাদিত হয়েছে।

**প্রভাব:** pool/sample selection-এ F2 ব্যবহৃত হয় না। Frozen draw বদলায় না; redacted bytes এবং কোন build scan পার হয় তা বদলায়। Distinctive text leak সম্ভব। Fixed inputs-এ threshold, sorting ও replacement deterministic; পরীক্ষায় needle order input order-এর ওপর নির্ভর করেনি (`test_t54.py:141`)।

## F3: fallback ও তার সীমা

**D1 অনুযায়ী যা সঠিক:** `t53_build.py:112` projection-এর `ContractError` ও post-redaction `JSONDecodeError` ধরে। আগে জমা হওয়া সব projected contract মুছে (`:115`), parent roots আবার নেয় (`:116`), path-এর UTF-8 byte order-এ সাজায় (`:117`), parent blob পড়ে (`:119`), সম্পূর্ণ raw file redact করার পরে অবশিষ্ট global ২,০০০-line budget কাটে (`:121`)। এটি প্রতিটি file-এর জন্য আলাদা ২,০০০ নয়। Mapping mode `raw_fallback` (`:123`)। Redacted local filename অনুপস্থিত হলে `ContractError` হয় (`:110`); missing fragment-ও `C['at']` থেকে একই exception দেয় (`t53_contracts.py:52`)।

**Content scan বজায় আছে:** fallback branch-এর পরেও সব delivered bytes-এ `V['findings'](..., **context)` চলে (`t53_build.py:126`)। `prepare` সমস্ত package bytes-এ `scan_package` চালিয়ে finding থাকলে fail করে (`:191`, `:192`)। তাই fallback scan bypass করে না। Positive fixture-এ redacted raw contract দুই scan-ই পেরিয়েছে (`test_t54.py:187`); forced privacy finding item fail করেছে (`test_t54.py:334`); এমন VCS-header fixture-ও আছে যা item-level privacy check পার হলেও final package scan ও `prepare` প্রত্যাখ্যান করেছে (`test_t54.py:340`)। **সব fallback অবশ্যই build হবে—এমন নিশ্চয়তা নেই; scan finding হলে ব্যর্থ হওয়া প্রত্যাশিত।** F2-এর বাদ-পড়া needle তবুও একই scan-এর blind spot।

**Parent/root provenance:** production history producer কেবল blob এবং top-level `openapi`/`swagger` detection থেকে roots বানায় (`t53_pool.py:169`, `:185`, `:269`)। Candidate-এর parent roots সংরক্ষিত হয় `:256`, `:305`-এ। Normal build এবং fallback উভয়েই সেই parent-keyed roots ও `row['parent']` ব্যবহার করে (`t53_build.py:95`, `:96`, `:116`, `:119`)। Fallback `$ref` targets enumerate করে না। ফলে producer-এর সঠিক, frozen history ধরে unrelated config, non-root reference file বা child-only contract fallback-এ আসে না। Synthetic producer-derived history দিয়ে unrelated config বাদ থাকা পরীক্ষা হয়েছে (`test_t54.py:264`); আলাদা child content ও child-only root দিয়েও parent bytes-ই এসেছে (`test_t54.py:275`)। Child থেকে source পড়া `after/`-এর স্বাভাবিক কাজ; contract provenance বদলায় না।

এই নিশ্চয়তা task-এর mechanical document definition অনুযায়ী; semantic OpenAPI validity-এর নিশ্চয়তা নয়। `build_item` arbitrary caller-supplied roots পুনরায় classify করে না। Production caller history hash পরীক্ষা করে (`t53_build.py:158`), কিন্তু ক্ষতিগ্রস্ত বা ইচ্ছাকৃত forged history-এর বিরুদ্ধে hash-কে semantic validation বলা যাবে না। অনুমোদিত সীমার কারণে বাস্তব history/key পড়িনি।

**ISSUE ১—unsafe-reference error-ও recover হচ্ছে:** `t53_contracts.py:201` repo tree ছেড়ে যাওয়া reference ধরে `ContractError` ছোড়ে (`:202`); F3-এর broad catch (`t53_build.py:112`) সেটিকেও raw fallback বানায়। Synthetic root-এর escaping `$ref`-এ item fail হয়নি (`test_t54.py:304`)। বাইরের file read হয়নি এবং কেবল parent root গেছে—সুতরাং এটি arbitrary-file disclosure-এর প্রমাণ নয়। তবে D1-এর “Unsafe-path … still fail the item” (`R3_DEVIATIONS.md:62`) যদি reference-path safety error-ও বোঝায়, এই দাবিটি পূরণ হয় না। Unsafe **output** path-এর `ValueError` ঠিকই escape করে (`t53_build.py:98`, `:118`; tests `test_t54.py:295`, `test_t54.py:328`)।

**Concrete patch suggestion:** escaping-reference safety error-কে `ContractError` থেকে আলাদা করুন—যেমন `ValueError`-derived `ContractSafetyError`। `t53_contracts.py:202`-এ সেটি তুলুন, এবং `build_item`-এর projection fallback দিয়ে সেটি ধরবেন না। Missing reference/syntax/line-bound-এর মতো recoverable projection error-এ fallback বহাল থাকবে। যদি D1 শুধু output path বোঝায়, deviation-এ সেই সংকীর্ণ অর্থ স্পষ্ট করা দরকার।

**ISSUE ২—shared filename leakage:** `files['contract/' + path]` original path অপরিবর্তিত রাখে (`t53_build.py:122`); item finding loop values-only (`:126`), final scan-ও `path`-কে privacy check-এ পাঠায় না (`:139`)। Synthetic fallback root-এর filename-এ context-known ticket ID রেখে contents clean হলেও scan clean হয়েছে (`test_t54.py:317`)। এটি fallback-সৃষ্ট নতুন scanner bug নয়, কিন্তু নতুনভাবে retained raw-root items-এও metadata প্রকাশ করতে পারে।

**Concrete patch suggestion:** final scan-এ প্রত্যেক relative path-এর UTF-8 bytes-ও generic findings এবং সব metadata context দিয়ে scan করুন। Path-এ নিষিদ্ধ metadata থাকলে fail করুন; filename নিঃশব্দে rename করলে references ও locators ভাঙতে পারে। একই guard projected/source paths-এর জন্যও প্রযোজ্য হওয়া উচিত।

**প্রভাব:** F3 discovery/sampler চালায় না, frozen draw বা ID allocation বদলায় না (`t53_build.py:163`, `:175`)। আগের projection failures এখন delivered set-এ ঢুকতে পারে; contract context-ও বদলায়। Raw fallback কাটা syntax, unresolved `$ref`, description/extension/comment রাখতে পারে; coder interpretability projected contract-এর সমান ধরে নেওয়া যাবে না। Fallback-এর `remote_references=0` (`:123`) “কোনো remote reference নেই” প্রমাণ করে না। Fixed roots, blobs, context ও salt-এ byte order, global budget ও output পুনরায় সমান ছিল (`test_t54.py:238`, `test_t54.py:351`)। নির্ধারিতভাবে ভুল তথ্য প্রকাশ হওয়াও deterministic হতে পারে; determinism privacy-এর বিকল্প নয়।

## Test results ও পুনরুৎপাদন

| Suite | Tests | Failures | Errors | Final exit |
| --- | ---: | ---: | ---: | ---: |
| নতুন `mining/test_t54.py` | 24 | 0 | 0 | 0 |
| অপরিবর্তিত `mining/test_t53.py --synthetic-only` | 29 | 0 | 0 | 0 |

মোট ৫৩টি test পাস। `test_risk_*` tests বিদ্যমান risk **থাকা** assert করে; এগুলো পাস হওয়া ISSUE সমাধানের দাবি নয়। JSONDecodeError, partial projection cleanup, forced privacy failure ও unsafe-root branch-এর ক্ষেত্রে controlled synthetic injection ব্যবহৃত হয়েছে। Missing reference, redacted reference, line budget, root provenance, escaping reference, filename leakage ও message linkage বাস্তব synthetic Git objects/production helpers দিয়ে পরীক্ষা হয়েছে। কোনো upstream content execute হয়নি।

চালানো commands, workspace root থেকে:

```sh
/usr/bin/python3 -I -B R3_silent_breaking/mining/test_t54.py
/usr/bin/python3 -I -B R3_silent_breaking/collab/logs/T54_scratch/run_t53_synthetic.py --synthetic-only
```

দ্বিতীয় command-এর wrapper `runpy` দিয়ে মূল `test_t53.py` load করে তার অপরিবর্তিত `main()` চালায়; `sys.argv`-এ `--synthetic-only` দেয়। মূল main ও fixture setup-এর `SCRATCH` শুধু memory-তে T54 scratch-এ redirect করা হয়েছে। সরাসরি মূল script চালালে `test_t53.py:390`, `:403` T53 scratch-এ লিখত, যা T54 write scope-এর বাইরে। Wrapper actual package/key/upstream path-এর Python open-ও block করে; actual-artifact tests চালায় না। নতুন T54 bare repos `/tmp`-এ তৈরি ও cleanup হয়; T53 fixtures T54 scratch-এর অস্থায়ী directory-তে cleanup হয়।

প্রথম T54 run-এ unsafe-root test-এর প্রত্যাশিত exception-এর বদলে আগের Git lookup-এ error হয়েছিল। Test-টি controlled projection failure দিয়ে fallback guard-এ পৌঁছানোর মতো সংশোধন করা হয়েছে; production code বদলানো হয়নি। উপরের table সর্বশেষ সম্পূর্ণ run-এর ফল।

Machine-readable ফল: `collab/logs/T54_scratch/t54_test_summary.json` এবং `collab/logs/T54_scratch/t53_synthetic/synthetic_test_summary.json`।

নিষিদ্ধ plan/score/notes/paper/research/board, বাস্তব `packages/`, `mining/key/`, sampled commit content এবং অন্য logs পড়া হয়নি। Network ব্যবহৃত হয়নি। নতুন test, এই report এবং T54 scratch ছাড়া workspace-এ কিছু লেখা হয়নি। বাস্তব pool membership, package leak-এর উপস্থিতি বা published artifacts-এর scan এখানে যাচাই করা হয়নি।
