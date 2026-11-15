# Blind labeller Y1 — প্রতিবেদন

১৮টি item-এর জন্য একবার করে L1 label, confidence, evidence locator এবং সর্বোচ্চ ৪০ শব্দের rationale তৈরি করেছি। ফলাফল `labels_Y1.csv`-এ item_id ক্রমে আছে; input হলো `items.csv`-এর K01–K25-এর নির্বাচিত ১৮টি row। L2 বা partial label file তৈরি করিনি।

## পদ্ধতি

`TASK_M1.md`-এর নির্দেশ অনুযায়ী প্রতিটি package আলাদাভাবে পর্যালোচনা করেছি। একই repository-র মতো দেখালেও অন্য package-এর evidence ব্যবহার বা package-গুলোর মধ্যে তুলনা করিনি। Proposition-কে যাচাইযোগ্য দাবি হিসেবে ধরে সংশ্লিষ্ট contract operation/schema, handler, DTO, validator, response/exception mapping এবং প্রাসঙ্গিক local test বা documentation পড়েছি। Contract-এর pointer এবং source-এর file:line প্রতিটি CSV row-তে দিয়েছি।

শুধু mismatch দেখেই contract-কে সঠিক ধরে নিইনি। যেখানে request-এর উদ্দেশ্য, dedicated response model, local test বা documentation contract-এর বিপরীতে একমত হয়েছে, সেখানে SPEC দিয়েছি; যেমন K09-এর `Payment.java:18`, `CreatePaymentITest.java:61` এবং `docs/api_specification.md:74` একই `payment_id` সমর্থন করে। যেখানে optional input বা empty collection handling-এর control flow সরাসরি ব্যর্থ হয়, সেখানে IMPL দিয়েছি; যেমন K06-এর `DirectDebitEventsResource.java:71`, `DateValidator.java:10` এবং `ConnectorUriGenerator.java:84`। পূর্ণ path সংশ্লিষ্ট CSV row-তে আছে। Intent বা framework আচরণ সম্পর্কে inference হলে ⚠️ চিহ্ন ব্যবহার করেছি।

শুধু shell-এর read-only operation এবং `/usr/bin/python3 -I -B` দিয়ে standard-library data reading ও deliverable validation করেছি। Package source, repository module, Java, Maven, Docker, network বা intent tool চালাইনি। Local test পড়া হয়েছে, চালানো হয়নি। History scope = unavailable (`TASK_M1.md`)।

## ফলাফলের distribution

| L1 | সংখ্যা | item_id |
| --- | ---: | --- |
| SPEC | 6 | K02, K07, K09, K15, K19, K23 |
| IMPL | 11 | K01, K04, K06, K11, K12, K13, K14, K20, K21, K22, K25 |
| TEST | 0 | — |
| ENV | 0 | — |
| UNDECIDABLE | 1 | K08 |

Confidence 3 দিয়েছি ১৩টি item-এ এবং confidence 2 দিয়েছি ৫টি item-এ: K08, K13, K14, K21, K22। এই হিসাবের evidence হলো `labels_Y1.csv`-এর সংশ্লিষ্ট item_id row। TEST বা ENV-এর জন্য নির্দিষ্ট deviating artifact-এর যথেষ্ট প্রমাণ পাইনি; এটি এই review-এর সিদ্ধান্ত, runtime ফলাফল নয়।

Deliverable validation-এ exact CSV header, ১৮টি unique row, input-এর সঙ্গে item_id order, অনুমোদিত L1/confidence, এবং rationale word limit পরীক্ষা করেছি। সর্বোচ্চ rationale ৩৫ শব্দ। সব cited source file ও line বিদ্যমান; JSON pointer resolve হয়েছে। YAML pointer-এর প্রতিটি named key থাকার পরীক্ষা করেছি, পূর্ণ YAML parser দিয়ে pointer traversal করিনি। Bengali report-এর পাঁচটি required বিষয়ও পরীক্ষা করেছি। Evidence: এই session-এর standard-library validation command-এর PASS output এবং `labels_Y1.csv`-এর ১৮টি row।

## কঠিন case ও খোলা প্রশ্ন

- **K08 — UNDECIDABLE, confidence 2:** `K08/source/swatch-common-resteasy/src/main/java/com/redhat/swatch/common/resteasy/EnumParamConverterProvider.java:82` invalid enum-এ exception ছোড়ে। `K08/source/swatch-core/src/main/java/org/candlepin/subscriptions/exception/mapper/WebApplicationExceptionMapper.java:45` wrapped HTTP exception-এর status বহাল রাখে; `DefaultExceptionMapper.java:42` unhandled exception-এর জন্য 500 নির্ধারণ করে। Query conversion-এ framework কোন wrapper দেয়, তা package evidence থেকে স্থির করতে পারিনি। তাই contract-এর 400 এবং converter exception থাকা মাত্রই IMPL বলিনি। Contract pointer CSV-তে আছে।
- **K13 — IMPL, confidence 2:** `K13/source/cwms_radar_api/src/main/java/cwms/radar/api/OfficeController.java:94` representation নির্বাচন করে, কিন্তু `:98`-এ শুধু string result লেখে। `K13/source/cwms_radar_api/src/main/java/cwms/radar/formatters/csv/CsvV1Office.java:30` formatter-এর media type দেয়। ⚠️ Handler-এ content type প্রয়োগের অভাব implementation সমস্যা বলে বিচার করেছি; deployment middleware দিয়ে final response header যাচাই করা যায়নি।
- **K14 — IMPL, confidence 2:** Proposition-এর descriptor-type ব্যাখ্যা পুরোপুরি সঠিক নয়। `K14/source/dockstore-webservice/src/main/java/io/openapi/api/impl/ToolsApiServiceImpl.java:911` ও `:928` version খোঁজে; version না পেলে `:924` ও `:941` থেকে 204 দেয়। ⚠️ Requested resource অনুপস্থিত থাকায় documented 404-কে উপযুক্ত বলে বিচার করেছি। Contract-এর 404 description বিশেষভাবে specified type উল্লেখ করে; missing-version behavior-এর intent তাই সম্পূর্ণ নিশ্চিত নয়।
- **K19 — SPEC, confidence 3:** `K19/source/src/main/java/uk/gov/pay/api/model/CreatePaymentRefundRequest.java:21`-এর READ_ONLY annotation-এর বিপরীতে `:37`-এর comment ভবিষ্যতে input বাধ্যতামূলক করার কথা বলে। `K19/source/src/main/java/uk/gov/pay/api/service/CreateRefundService.java:49` input ব্যবহার করে এবং না থাকলে fallback নেয়। ⚠️ এটি supported input-এর documentation annotation ভুল বলে বিচার করেছি।
- **K20 — IMPL, confidence 3:** `K20/source/src/main/java/app/coronawarn/verification/service/HashingService.java:37`-এর dollar-anchored regex এবং `:70`-এর `find()` একত্রে বিচার করেছি। ⚠️ Final line terminator-এর আগে match হওয়ার কারণে extra line feed গ্রহণের সিদ্ধান্ত static reasoning; Java বা package code চালিয়ে যাচাই করিনি। Contract হলো `K20/source/src/main/java/app/coronawarn/verification/controller/VerificationController.java:120`-এর operation description।
- **K21 — IMPL, confidence 2:** `K21/source/src/main/resources/openapi.yaml:131` status optional এবং `:135` default available বলে। `K21/source/src/main/java/io/swagger/petstore/controller/PetController.java:51` null পেলে 400 branch নেয়। ⚠️ Contract অনুযায়ী default handling প্রয়োজন; external binding আগে default বসালে HTTP request-এ ওই branch অপ্রাপ্য হতে পারে। সেটি প্রমাণিত নয়।
- **K22 — IMPL, confidence 2:** `K22/source/cwms-data-api/src/main/java/cwms/cda/api/location/kind/OutletController.java:105` session default প্রতিশ্রুতি দেয়, কিন্তু `:120` requiredParam ডাকে। `K22/source/cwms-data-api/src/main/java/cwms/cda/api/Controllers.java:341` missing/empty office প্রত্যাখ্যান করে। ⚠️ Promised fallback অনুযায়ী implementation-কে দায়ী করেছি; আলাদা intent evidence ছাড়া description পুরোনো বা ভুল হওয়ার সম্ভাবনা বাদ দেওয়া যায়নি।

## সীমাবদ্ধতা

এটি parent snapshot-এর static review; কোনো runtime exchange দেওয়া হয়নি এবং source execution নিষিদ্ধ (`TASK_M1.md`)। তাই label-গুলো observed production failure-এর দাবি নয়। VCS history অনুপলব্ধ; বাদ পড়া dependency, generated binding, middleware বা database behavior থেকে intent স্থির করিনি। সরবরাহকৃত package-এর বাইরে কিছু খুঁজে ঘাটতি পূরণ করিনি। Confidence 2 case-গুলোর নির্দিষ্ট অনিশ্চয়তা উপরে এবং CSV rationale-এ আছে।

## Boundary incidents

1. Task file পড়ার আগের প্রথম filename discovery-তে `rg --files`-এর explicit path argument ছিল না; এটি task-এর explicit-path নিয়ম মানেনি। Search বর্তমান directory থেকে চালানো হয়েছিল এবং নামের filter-এ নিষিদ্ধ board/codebook/task বাদ ছিল; output-এ শুধু `TASK_M1.md` এসেছিল। নিষিদ্ধ ফাইলের contents পড়িনি। এই incident-এর evidence হলো session-এর প্রথম `exec_command` invocation ও তার output।
2. Protocol খোঁজার প্রথম command-এ `09_collab/PROTOCOL.md`, `../09_collab/PROTOCOL.md`, `../../09_collab/PROTOCOL.md`-এর existence পরীক্ষা করে অনুমোদিত `../../../09_collab/PROTOCOL.md` পড়েছিলাম। মধ্যবর্তী দুটি candidate বর্তমান directory-এর বাইরে এবং explicit exception-এর বাইরে ছিল। তাদের contents পড়া হয়নি; তবু ওই existence probe scope deviation হিসেবে জানাচ্ছি। Evidence: session-এর প্রথম protocol-read command। এরপর বাইরে কোনো অনুসন্ধান করিনি।
3. প্রথম redaction filter সাধারণ credential assignment ও attribution আড়াল করলেও কিছু credential-সদৃশ test constant আড়াল করেনি: `K15/source/src/test/java/app/coronawarn/verification/service/TanServiceTest.java:61`, `:62`, `:63` এবং `K20/source/src/test/java/app/coronawarn/verification/service/HashingServiceTest.java:36`-সহ তার কয়েকটি hash fixture output-এ এসেছিল। সেগুলোর value এখানে পুনরুৎপাদন করিনি। Filter পরে test constant এবং দীর্ঘ hexadecimal literal আড়াল করার জন্য শক্ত করেছি। এগুলো test fixture-এ ছিল; বাস্তব credential কি না যাচাই করিনি।

`CODEBOOK_v0.6.md`, অন্য codebook, `TASK_M2.md`, `COLLAB_BOARD.md`, coordinator task বা অন্য labeller-এর output পড়িনি। অনুমোদিত protocol এবং নিজস্ব task ছাড়া অন্য task file খুলি নাই। Output লেখা শুধু `labels_Y1.csv` ও এই `report_Y1.md`-এ সীমাবদ্ধ। Board/task-file পড়ার সাধারণ নির্দেশের exception `TASK_M1.md`-এর Supervisor authorization এবং launch instruction অনুসারে প্রয়োগ করেছি।
