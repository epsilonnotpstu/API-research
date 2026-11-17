# C14 blind coding প্রতিবেদন

`items.csv`-এর ক্রমে ৬১টি item-এর coding লেখা হয়েছে `codes_C14.csv`-এ। প্রতিটি row-তে দুইটি label, confidence, implementation ও contract-এর line locator এবং সর্বোচ্চ ৪০ শব্দের rationale আছে। যাচাইয়ের ফল `codes_work_C14/validation.json`-এ সংরক্ষিত।

## পদ্ধতি

প্রথম command ছিল `cat TASK_CODE.md`; এরপর অনুমোদিত `../../../09_collab/PROTOCOL.md` ও `items.csv` পড়েছি। `TASK_CODE.md`-এর supervisor override অনুযায়ী board ও coordinator task পড়িনি। প্রত্যেক item-এর proposition কেবল সেই item-এর `contract/` ও `impl/` দিয়ে যাচাই করেছি; item-গুলির source-এর মধ্যে comparison করিনি। Source পড়া ও locator তৈরির জন্য নিজের Python helper ব্যবহার করেছি; item source execute, compile বা import করিনি। পদ্ধতির নির্দেশনাগত ভিত্তি: `TASK_CODE.md`, “What you code”, “Output” ও “Rules”; `../../../09_collab/PROTOCOL.md`, rules 1, 3–6।

⚠️ Label হলো দৃশ্যমান code structure-এর ব্যাখ্যা, developer-এর ঐতিহাসিক উদ্দেশ্য সম্পর্কে দাবি নয়। Explicit route, guard, status, type ও branch-কে `DELIBERATE`; অনুপস্থিত mapping, status assignment, binding, membership check বা initialization-কে `ACCIDENTAL` ধরেছি। Contract-এর dedicated prose ও operation declaration-কে `SPECIFIC`; silence, shared field constraint ও reusable pagination annotation-কে `GENERIC` ধরেছি। উদাহরণ ও evidence: `codes_C14.csv`, rows Q01–Q07, Q40, Q43, Q48, Q52।

## কঠিন সিদ্ধান্ত

- **Q06 ও Q51:** renamed field-এর mapping শুধু `fromModel`-এ আছে; `toModel`-এ reverse mapping নেই। ⚠️ Generated MapStruct implementation অনুপস্থিত বলে non-transfer সিদ্ধান্তে confidence 2 রেখেছি। Evidence: সংশ্লিষ্ট row-এর `MapStructClientModelMapper.java:20`, `:33`, `DefaultClientService.java` ও `ClientRepresentation.java` locators; `codes_C14.csv`, rows Q06, Q51।
- **Q14:** body-তে suppression filter এবং count-এ `includeSuppressed=true`—দুইটিই explicit। তাই structural rule অনুযায়ী `DELIBERATE`, confidence 2; count ও body-র অসামঞ্জস্যকে আলাদা করে অনুমিত historical oversight বলিনি। Evidence: Q14-এর `FindingResource.java:71`, `QueryManager.java:1630`, `:1901`; `codes_C14.csv`, row Q14।
- **Q17:** multipart path সরাসরি `ScanUploadEvent` তৈরি করে; task `DependencyCheckParser` ব্যবহার করে। এই explicit dispatch-কে `DELIBERATE` করেছি, confidence 2। Copy-paste বা ভুল variable ব্যবহারের ইতিহাস দেওয়া নেই। Evidence: Q17-এর `BomResource.java:168`, `ScanUploadProcessingTask.java:68`, `:74`; `codes_C14.csv`, row Q17।
- **Q19 ও Q41:** output conversion-এ `PurgeOnDelete` বাদ পড়া সরাসরি দৃশ্যমান। তবে “provided by Add or Update” prose `/process/{id}/config` operation-এ আছে। ⚠️ একই configuration model-এর list/detail response-এ সেই প্রতিশ্রুতির প্রয়োগ inference; তাই `SPECIFIC` হলেও confidence 2। Evidence: নিজ নিজ item-এর `process.go:176`, `swagger.yaml#704`, `#2489`; `codes_C14.csv`, rows Q19, Q41।
- **Q31:** service call-এর আগে body binding নেই। Required-body enforcement-এর omission হিসেবে `ACCIDENTAL`, confidence 2 রেখেছি। Evidence: Q31-এর `siteinfo_controller.go:43`, `swagger.yaml#1720`; `codes_C14.csv`, row Q31।
- **Q37:** prose বলে শুধু namespace required, কিন্তু object ও relation-এর parameter declaration-এ `required:true` আছে। এই internal contract conflict বজায় রেখেই explicit parameter constraint-কে `SPECIFIC`, confidence 2 করেছি। Evidence: Q37-এর `api.json#507`, `#534`, `#541`; `codes_C14.csv`, row Q37।
- **Q38 ও Q56:** empty filter result-এর slice nil থাকে এবং writer-এ যায়। ⚠️ JSON `null` সিদ্ধান্ত সাধারণ nil-slice serialization থেকে inferred; writer internals দেওয়া নেই। তাই confidence 2। Evidence: নিজ নিজ item-এর `storage/handler.go:85`, `:126`; `codes_C14.csv`, rows Q38, Q56।
- **Q45 ও Q49:** প্রথমটির visible callback-এ inherited-context authorization নেই; downstream implementation সম্পূর্ণ দেওয়া নেই। দ্বিতীয়টিতে view resolver explicit HTML content type সেট করে, কিন্তু rendering চালানো হয়নি। উভয়ের confidence 2। Evidence: Q45-এর `ParameterContextResource.java:731`; Q49-এর `WebMvcAutoConfiguration.java:149`; `codes_C14.csv`, rows Q45, Q49।

## ফল ও সীমাবদ্ধতা

Coding-এ `DELIBERATE` ৪৩টি, `ACCIDENTAL` ১৮টি; `SPECIFIC` ৪৯টি, `GENERIC` ১২টি। Confidence 3 রয়েছে ৪৯টি row-তে এবং confidence 2 রয়েছে ১২টিতে। কোনো row-তে `UNCLEAR` ব্যবহার করিনি। এগুলি এই coding-এর গণনা; runtime-এ divergence পুনরুৎপাদনের দাবি নয়। Evidence: `codes_work_C14/validation.json`; individual evidence: `codes_C14.csv`।

Runtime data, version history ও সব dependency implementation অনুপস্থিত; external source ব্যবহার করিনি। তাই historical intent, framework configuration-এর অদৃশ্য অংশ এবং production behavior সম্পর্কে অতিরিক্ত সিদ্ধান্ত দিইনি। এই সীমার উৎস `TASK_CODE.md`, “What you are given” ও “Rules”; item-specific সীমা CSV-র confidence-2 rationale-এ লেখা আছে।

## Boundary ও redaction incidents

অনুমোদিত protocol file ছাড়া directory-এর বাইরে কোনো file open, list বা search করিনি; অন্য coder-এর output পড়িনি। Network, Docker, Java, Maven বা item source execution ব্যবহার করিনি। নিজের helper ও intermediate decision file শুধু `codes_work_C14/`-এ এবং চূড়ান্ত output নির্ধারিত দুইটি path-এ লিখেছি। Audit basis: এই session-এর tool-call record; অনুমোদিত path-এর উৎস `TASK_CODE.md`, “Output” ও “Rules”।

দুইটি output-redaction incident হয়েছে। Q20-এর `contract/api/openapi.yml#2093` ও `#2122`-এর credential-looking documentation example broad excerpt-এ ছাপা হয়েছিল; Q59-এর `impl/registry/app/api/controller/metadata/get_artifact_detail.go:129`-এর comment-এ personal attribution-ও ছাপা হয়েছিল। কোনো value বা attribution এখানে পুনরুৎপাদন করিনি। প্রত্যেকটি শনাক্ত হওয়ার পরে নিজের `codes_work_C14/read.py`-এর filter সংশোধন করেছি। এগুলি redaction-rule incident; অনুমোদিত filesystem boundary অতিক্রমের ঘটনা নয়। Audit basis: এই session-এর সংশ্লিষ্ট excerpt ও filter-edit tool calls।

CSV integrity check-এ row count/order, header, allowed label/confidence, rationale length এবং প্রতিটি locator-এর নিজ item-এ file ও line existence যাচাই করেছি। Source behavior-এর runtime test চালাইনি। Evidence: `codes_work_C14/validate.py`, `codes_work_C14/validation.json`।
