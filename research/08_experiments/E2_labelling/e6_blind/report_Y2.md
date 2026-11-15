**Y2 — Task M1 blind labelling প্রতিবেদন**

**পদ্ধতি।** `items.csv`-এর ১৮টি proposition সংশ্লিষ্ট package-এর নিজস্ব contract, handler, DTO, validator, exception mapper এবং প্রাসঙ্গিক test-এর সাহায্যে আলাদাভাবে বিচার করেছি। এক package-এর সিদ্ধান্তে অন্য package-এর উপাদান ব্যবহার করিনি। Proposition-এর বক্তব্যও যাচাইয়ের বিষয় হিসেবে ধরেছি। সিদ্ধান্তের inference-গুলো CSV rationale-এ ⚠️ দিয়ে চিহ্নিত। প্রতিটি row-তে source file:line এবং contract path/pointer আছে; Java annotation contract-এর ক্ষেত্রে method/annotation-ভিত্তিক pointer বর্ণনামূলক। নির্দেশনার ভিত্তি: `TASK_M1.md:5`, `TASK_M1.md:13`, `TASK_M1.md:24`; ফলের ভিত্তি: `labels_Y2.csv`, item_id K01–K25।

পর্যালোচনায় shell-এর read/search command এবং `/usr/bin/python3 -I -B` দিয়ে standard-library data reading ব্যবহার করেছি। Package source import, execution বা compilation করিনি। Test-এর assertion-কে package-এর evidence হিসেবে পড়েছি; test চালিয়ে ফল পাওয়ার দাবি করছি না। এই কাজের execution record হলো এই সেশনের tool log; execution সীমা নির্ধারিত আছে `TASK_M1.md:21` ও `TASK_M1.md:42`-এ।

**বণ্টন।** নিচের সংখ্যা `labels_Y2.csv`-এর item_id-ভিত্তিক গণনা।

| L1 | সংখ্যা | item_id |
| --- | ---: | --- |
| SPEC | 6 | K02, K07, K09, K15, K19, K23 |
| IMPL | 10 | K01, K04, K06, K11, K12, K13, K14, K20, K22, K25 |
| TEST | 0 | — |
| ENV | 0 | — |
| UNDECIDABLE | 2 | K08, K21 |

Confidence 3 পেয়েছে ১৩টি item; confidence 2 পেয়েছে K04, K08, K14, K21 ও K22। Confidence 1 নেই। এগুলো adjudication-এর নিশ্চয়তা নির্দেশ করে; runtime ফলের পরিমাপ নয়। ভিত্তি: `labels_Y2.csv`, সব item_id; confidence scale: `TASK_M1.md:25`।

**কঠিন সিদ্ধান্ত।**

- **K08 — UNDECIDABLE, confidence 2।** Converter-এর `IllegalArgumentException` দেখা যায়, আবার local mapper-এ 400 এবং fallback 500 উভয় পথ আছে। Parameter binding exception-টিকে কীভাবে wrap করে, supplied artifacts থেকে নিশ্চিত হয়নি। শুধু exception ছোড়া দেখে HTTP contract ভঙ্গ হয়েছে বলা যায় না। ভিত্তি: `K08/source/swatch-common-resteasy/src/main/java/com/redhat/swatch/common/resteasy/EnumParamConverterProvider.java:82`; `K08/source/swatch-core/src/main/java/org/candlepin/subscriptions/exception/mapper/BadRequestExceptionMapper.java:43`; একই mapper directory-র `DefaultExceptionMapper.java:42`; contract `K08/source/api/rhsm-subscriptions-api-v1-spec.yaml:233`।
- **K21 — UNDECIDABLE, confidence 2।** Contract-এ optional status-এর পাশাপাশি `default: available` আছে। Controller bound null পেলে 400 দেয়; কিন্তু query বাদ দিলে external Swagger Inflector সেই null পাঠায় কি না, package-এর code দিয়ে নির্ধারিত হয়নি। ভিত্তি: `K21/source/src/main/resources/openapi.yaml:131`, `K21/source/src/main/resources/openapi.yaml:135`; `K21/source/src/main/java/io/swagger/petstore/controller/PetController.java:51`; `K21/source/src/main/webapp/WEB-INF/web.xml:8`।
- **K14 — ⚠️ IMPL, confidence 2।** Proposition-এর trigger সংশোধন করা প্রয়োজন: 204 আসে requested workflow version/tag না থাকলে। Descriptor-type filtering আলাদাভাবে empty list তৈরি করে, যা 200 হিসেবে ফেরে। Documented unavailable-type 404 enforce না হওয়ার পক্ষে implementation evidence আছে; proposition-এর 204 ব্যাখ্যা হুবহু গ্রহণ করিনি। ভিত্তি: `K14/source/dockstore-webservice/src/main/java/io/openapi/api/impl/ToolsApiServiceImpl.java:913`, একই file-এর `:924`, `:938`, `:941`, `:990`; contract `K14/source/dockstore-webservice/src/main/resources/openapi3/openapi.yaml:4104`।
- **K04 — ⚠️ IMPL, confidence 2।** Nullable persist-এর value primitive builder-এ সরাসরি যায়; builder-এ true default থাকলেও সেটি রক্ষা করার null guard নেই। Generated DTO-র বিস্তারিত নিশ্চিত করার সীমাবদ্ধতায় confidence কমিয়েছি। ভিত্তি: `K04/source/hivemq-edge/src/main/java/com/hivemq/api/resources/impl/BridgeResourceImpl.java:394`; `K04/source/hivemq-edge/src/main/java/com/hivemq/bridge/config/MqttBridge.java:158`, একই file-এর `:235`; contract `K04/source/ext/hivemq-edge-openapi-2025.1-SNAPSHOT.yaml:4554`।
- **K22 — ⚠️ IMPL, confidence 2।** Annotation session-office default প্রতিশ্রুতি দেয়; handler তা প্রয়োগের আগেই office বাধ্যতামূলক করে। Default-টির intended semantics-এর অতিরিক্ত প্রত্যক্ষ প্রমাণ সীমিত হওয়ায় confidence 2 রেখেছি। ভিত্তি: `K22/source/cwms-data-api/src/main/java/cwms/cda/api/location/kind/OutletController.java:104`, একই file-এর `:120`; `K22/source/cwms-data-api/src/main/java/cwms/cda/api/Controllers.java:339`।

⚠️ SPEC সিদ্ধান্তগুলোতে শুধু contract/implementation অমিলের উপর নির্ভর করিনি। যেমন K07-এর pagination test, K09-এর explicit JSON নাম ও creation test, K19-এর supplied refund field ব্যবহার ও test, এবং K23-এর numeric score calculation intended behaviour-এর পক্ষে অতিরিক্ত evidence দিয়েছে। K15-তে async completion wrapper-এর বদলে Tan body ফেরানোর উদ্দেশ্য controller documentation ও completion code-এ পাওয়া যায়। বিস্তারিত locator: `labels_Y2.csv`, item_id K07, K09, K15, K19, K23।

**সীমাবদ্ধতা ও খোলা প্রশ্ন।** History scope unavailable এবং runtime exchanges নেই—এটি task-এর শর্ত (`TASK_M1.md:7`, `TASK_M1.md:12`)। তাই observed response, historical intent বা dependency implementation সম্পর্কে নতুন দাবি করিনি। K08-এর binding/wrapping এবং K21-এর omitted-parameter default application অনির্ধারিত রয়ে গেছে। বাইরের framework source বা runtime পরীক্ষা এই task-এর অনুমোদিত scope-এ ছিল না (`TASK_M1.md:21`, `TASK_M1.md:41`); সেগুলো ব্যবহার করিনি।

**Boundary incidents।** সেশনের প্রথম discovery command-এ `rg --files`-এর সঙ্গে explicit search path দেওয়া হয়নি; glob দিয়ে `AGENTS.md`, `PROTOCOL.md`, `TASK_M1.md`, Y2 নাম এবং task-directory path খোঁজা হয়েছিল। Search কার্যত বর্তমান directory-তে হয়েছিল এবং output-এ কেবল `TASK_M1.md` এসেছিল। এটি `TASK_M1.md:14`-এর explicit-path নিয়মের বিচ্যুতি; নিষিদ্ধ file content পড়ার ঘটনা নয়।

Protocol খোঁজার প্রাথমিক shell loop-এ `.`, `..`, `../..`, `../../..`, `../../../..`, `../../../../..`-এর অধীনে `09_collab/PROTOCOL.md`-এর অস্তিত্ব পরীক্ষা করা হয়েছিল। একমাত্র পাওয়া ও পড়া external file ছিল অনুমোদিত `../../../09_collab/PROTOCOL.md`; অন্য ancestor path-এ existence probe করার কাজটি নির্ধারিত external exception-এর অতিরিক্ত ছিল। এই দুই ঘটনার ভিত্তি সেশনের প্রথম দুই tool call; প্রযোজ্য সীমা `TASK_M1.md:14` ও `TASK_M1.md:18`। এরপর package অনুসন্ধান explicit সংশ্লিষ্ট source path-এ সীমাবদ্ধ রেখেছি।

`COLLAB_BOARD.md`, coordinator task file, কোনো codebook, `TASK_M2.md`, intent-search output বা অন্য labeller-এর task/label/review/search/report পড়িনি। Board/coordinator না পড়ার override আছে `TASK_M1.md:3`-এ; অন্য নিষেধগুলো `TASK_M1.md:19` ও `TASK_M1.md:40`-এ। Network, Docker, Java, Maven বা external-code execution ব্যবহার করিনি। Source excerpt মুদ্রণের সময় credential-looking line ও attribution redact করেছি। এই কার্যক্রমের audit record সেশনের tool log। কেবল `labels_Y2.csv` ও `report_Y2.md` লিখেছি।

**Deliverable যাচাই।** Standard-library validation-এ ১৮টি unique item, `items.csv`-এর সঠিক ক্রম, নির্ধারিত পাঁচটি column, বৈধ L1/confidence এবং সর্বোচ্চ ৩৬ শব্দের rationale পাওয়া গেছে। ৮৫টি evidence locator-এর file existence ও উল্লিখিত line-এর সীমা পরীক্ষা করেছি; JSON contract-এর ৫টি pointer resolve হয়েছে। YAML ও annotation pointer মানবিকভাবে সংশ্লিষ্ট excerpt মিলিয়ে বিচার করেছি; automated YAML parser ব্যবহার করিনি। CSV serialize/parse round trip মিলেছে। এই যাচাই package source চালায়নি; যাচাইয়ের পরিসর output structure ও locator validity। ভিত্তি: `labels_Y2.csv`, সব item_id; এই সেশনের output-validation tool result। L2 বা partial-label file তৈরি করিনি (`TASK_M1.md:48`)।
