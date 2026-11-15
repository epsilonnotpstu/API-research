# G1 blind review প্রতিবেদন

## পদ্ধতি

`TASK_M2.md` ও `CODEBOOK_v0.6.md` অনুসারে `items.csv`-এর ১৮টি item একই ক্রমে, স্বতন্ত্র package হিসেবে পর্যালোচনা করেছি। প্রত্যেকটির proposition যাচাইয়ের লক্ষ্য হিসেবে নিয়েছি; কোনো package-এর প্রমাণ অন্য package-এর সিদ্ধান্তে ব্যবহার করিনি। সিদ্ধান্ত, source file:line, contract pointer, confidence ও intent verdict রয়েছে `labels_G1.csv:2–19` এবং সংশ্লিষ্ট `review_G1/Kxx.json`-এ।

Intent-নির্ভর ক্ষেত্রে প্রথমে target scenario লিখে HANDLER → E-TEST → E-DOC → E-CONSIST → E-HISTORY ক্রম অনুসরণ করেছি। Handler/annotation-কে স্বয়ংক্রিয় স্বাধীন প্রমাণ ধরিনি; fixture, helper prefix, operation ও branch মিলিয়েছি। প্রতিটি raw hit-এর শূন্য থেকে শুরু হওয়া index, disposition এবং (a)–(e) checklist সংরক্ষিত। Raw verdict ও reviewed verdict আলাদা রেখেছি। নিয়মের ভিত্তি: `CODEBOOK_v0.6.md` §§11.1–11.4; পূর্ণ audit: `review_G1/K09.json`, `review_G1/K15.json`, `review_G1/K23.json`।

শুধু অনুমোদিত `/usr/bin/python3 -I -B ../../tools/intent_evidence.py` এবং নিজস্ব read/redaction/output utilities চালিয়েছি। Package source, Java, Maven, Docker বা compilation চালাইনি; network ব্যবহার করিনি। Runtime response পর্যবেক্ষণের বদলে source থেকে ফল অনুমান করলে তা review-তে static inference হিসেবে লিখেছি। প্রতিটি item-এর `history_scope=unavailable`; কোনো `--history-root` ব্যবহার করিনি। Invocation ও সীমার নথি: `review_G1/Kxx.json`-এর `tool_run`, `decision.details` ও `history_review`; ব্যতিক্রমসমূহ নিচে ও `review_G1/boundary_incidents.json`-এ।

## ফলের বণ্টন

| L1 | সংখ্যা | Item |
|---|---:|---|
| IMPL | ৮ | K01, K04, K06, K11, K13, K20, K22, K25 |
| SPEC | ৪ | K07, K09, K19, K23 |
| UNDECIDABLE | ৬ | K02, K08, K12, K14, K15, K21 |

উৎস: `labels_G1.csv:2–19`। প্রত্যেক item-এর একটি row আছে; rationale সর্বোচ্চ ৪০ শব্দ। ছয়টি UNDECIDABLE item-এ `both_candidate=true`; চূড়ান্ত BOTH label দিইনি। `adjudication_flag=none` সর্বত্র; একই class-এর বিভিন্ন method-কে অনিশ্চিত স্বাধীন corroboration হিসেবে গ্রহণ করিনি। যাচাইয়ের ফল: `review_G1/validation.json`।

K01, K04, K06, K11 ও K25-এ নির্দিষ্ট null/exception path এবং codebook §9.3 R1/§11.4.1-এর deterministic crash নিয়ম প্রয়োগ করেছি; intent tool চালানো দরকার হয়নি। উদাহরণ: K25-তে endpoint নিজেই null দেয়, helper সেটি dereference করে, এবং generic exception handler 500 দেয় (`K25/source/src/main/java/com/zufar/icedlatte/payment/endpoint/PaymentEndpoint.java:31`, `K25/source/src/main/java/com/zufar/icedlatte/payment/api/StripeSessionCreator.java:58`, `K25/source/src/main/java/com/zufar/icedlatte/common/exception/handler/GlobalExceptionHandler.java:75–83`)। এটি public create-body অনুপস্থিতির ঘটনা নয়; `review_G1/K25.json`।

## কঠিন সিদ্ধান্ত

- **K02:** PUT contract-এ requestBody নেই; server binding mandatory। Client body পাঠায়, কিন্তু omitted-body policy-র স্বাধীন প্রমাণ হয় না। তাই UNDECIDABLE (`K02/source/api/microcks-openapi-v1.10.yaml:394–405`, `K02/source/webapp/src/main/java/io/github/microcks/web/SecretController.java:85`, `review_G1/K02.json`)।
- **K08:** enum converter-এর IllegalArgumentException থেকে HTTP 500 ধরে নিইনি। HTTP wrapper ও raw Throwable mapper আলাদা; target query-binding branch-এর স্বাধীন test নেই। তাই UNDECIDABLE (`K08/source/swatch-common-resteasy/src/main/java/com/redhat/swatch/common/resteasy/EnumParamConverterProvider.java:68–84`, `K08/source/swatch-core/src/main/java/org/candlepin/subscriptions/exception/mapper/WebApplicationExceptionMapper.java:38–50`, `review_G1/K08.json`)।
- **K12:** target test-এর fixture-এ দশটি tag; empty-tag body omission সেটি যাচাই করে না। All-tags endpoint-এর empty-list response আলাদা operation; সেই উদাহরণ দিয়ে target intent স্থির করিনি (`K12/source/hivemq-edge/src/test/java/com/hivemq/api/resources/impl/ProtocolAdaptersResourceImplTest.java:69–89`, `review_G1/K12.json`)।
- **K14:** 204 branches আসলে missing version-এর পরে আসে, descriptor-type filtering-এর পরে নয়। Proposition-এর scenario equivalence প্রতিষ্ঠিত নয়; একই method-এর দুটি branch স্বাধীন intent নয় (`K14/source/dockstore-webservice/src/main/java/io/openapi/api/impl/ToolsApiServiceImpl.java:909–941`, contract `K14/source/dockstore-webservice/src/main/resources/openapi3/openapi.yaml:4104–4112`, `review_G1/K14.json`)।
- **K15:** Tan body ও DeferredResult schema আলাদা, কিন্তু schema-টি open এবং কোনো required property নেই। Target tests শুধু status assert করে; prose-এর “Return TAN string” নির্দিষ্ট JSON structure স্থির করে না। তাই shape difference থেকে নিশ্চিত defect বলিনি (`K15/source/api-docs.json#/components/schemas/DeferredResultResponseEntityTan`, `K15/source/src/test/java/app/coronawarn/verification/VerificationApplicationExternalTest.java:131–146`, `review_G1/K15.json`)।
- **K21/K22:** K21-তে optional status-এর default `available`; omission সত্যিই null bind করে কি না সরবরাহকৃত test দেখায় না। K22-তে helper সরাসরি missing query প্রত্যাখ্যান করে এবং 400 mapper আছে; documented session default-এর লঙ্ঘনে §10.7 প্রযোজ্য (`review_G1/K21.json`, `K22/source/cwms-data-api/src/main/java/cwms/cda/api/Controllers.java:339–344`, `K22/source/cwms-data-api/src/main/java/cwms/cda/ApiServlet.java:296–299`, `review_G1/K22.json`)।

## Tool failure ও tool-miss

১৩টি intent invocation-এর মধ্যে K09, K15 ও K23 সফল; মোট ১৮৬টি raw hit আলাদাভাবে review করেছি। বাকি দশটি invocation-এ exit 2: Java annotation contract অথবা tool-এর unsupported YAML flow syntax। তাদের raw stdout শূন্য-byte `.json` হিসেবেই অপরিবর্তিত রেখেছি; `.stderr` ও `.exitcode` কারণ সংরক্ষণ করে। ভুয়া JSON verdict বানাইনি; `intent_search_verdict=NA`। নথি: `search_G1/Kxx.{json,stderr,exitcode}`, সংশ্লিষ্ট `review_G1/Kxx.json.tool_run`।

এই দশটি ক্ষেত্রে package-local directed manual fallback-এ প্রাসঙ্গিক contract, route, helper/DTO, tests/fixtures ও prose পরীক্ষা করেছি। কোনো পরিচিত অপঠনযোগ্য relevant file বা অমীমাংসিত retrieval gap রেখে complete দিইনি। ফলে CSV-এর `intent_search_status=complete` পুরো reviewed retrieval বোঝায়; CLI সফল বোঝায় না। এটি codebook §11.4.3-এর manual gap-resolution ব্যবহারের সিদ্ধান্ত; প্রতিটি ব্যর্থ invocation-এর বিস্তারিত `decision.details`-এ আছে। পাঁচটি deterministic item-এর status `not_run` (`labels_G1.csv:2–19`)।

- **K09:** lexical tool helper-সংযুক্ত create assertion পায়নি। Manual fallback-এ POST helper, তার prefix এবং `payment_id` assertion মিলেছে; raw conflicting ছিল অন্য operation/status ও annotation মেশার ফল (`K09/source/src/test/java/uk/gov/pay/api/it/CreatePaymentITest.java:57–61,228–235`, `K09/source/src/test/java/uk/gov/pay/api/it/PaymentResourceITestBase.java:26`, `review_G1/K09.json`)।
- **K15:** helper-prefix resolve করে target async test পেয়েছি, কিন্তু সেখানে body assertion নেই। তাই missed test পাওয়াকে SPEC-এর প্রমাণ বানাইনি (`review_G1/K15.json.manual_additions`)।
- **K23:** tool StatisticsApi-কে handler ধরেছিল; actual ProjectsApi class prefix ও integration-test URL manual-এ মিলিয়েছি। Numeric score expectation implementation সমর্থন করে, তবে test raw JSON token type assert করে না; confidence ২ (`K23/source/catwatch-backend/src/main/java/org/zalando/catwatch/backend/web/ProjectsApi.java:27–29,87–91`, `K23/source/catwatch-backend/src/test/java/org/zalando/catwatch/backend/web/ProjectsApiIT.java:85–105`, `review_G1/K23.json`)।

## সীমাবদ্ধতা

এই review source-only; exchange/checker input বা VCS history নেই (`TASK_M2.md`)। Framework binding, serialization ও regex-এর static inference runtime verification নয়। বিশেষত K20-এর ফল validation-level LF acceptance; successful persistence বা observed 201 দাবি করিনি (`review_G1/K20.json.decision.details`)। Independent evidence না পেলে absence থেকে SPEC/IMPL বানাইনি; ছয়টি item তাই UNDECIDABLE (`labels_G1.csv:3,7,10,12,13,16`)।

## Boundary incidents

পূর্ণ বিবরণ ও প্রাথমিক command নথি `review_G1/boundary_incidents.json`-এ:

1. Task পুরো পড়ার আগে একটি `rg --files`-এ explicit path দিইনি; শুধু `TASK_M2.md` filename ফিরেছিল। পরবর্তী search-এ explicit package/file path দিয়েছি।
2. Protocol খোঁজার প্রথম চেষ্টায় ভুল `../../../../09_collab/PROTOCOL.md`-এ existence check হয়েছিল; কোনো content পাওয়া বা পড়া হয়নি। পরে অনুমোদিত `../../../09_collab/PROTOCOL.md` পড়েছি।
3. K15-এর TestUtils excerpt-এ credential-looking test fixture hash/identifier ছাপা হয়েছিল; পরে console redactor শক্ত করেছি। মানগুলো report/CSV-তে পুনরাবৃত্তি করিনি। এগুলো real credential কি না দাবি করছি না।
4. অনুমোদিত intent tool ancestor `.git` existence পরীক্ষা করে এবং successful output-এ enclosing repository জানায়। বাইরে history query হয়নি; এই metadata probing-ও সীমান্তসংক্রান্ত caveat হিসেবে লিখেছি (`../../tools/intent_evidence.py:822–874`, `search_G1/K09.json.history`)।

COLLAB_BOARD.md, TASK_M1.md, coordinator task অথবা অন্য labeller-এর output পড়িনি। Package source বদলাইনি; G1-এর output এই directory-তেই লিখেছি। Boundary ঘটনার বাইরে কোনো অন্য project copy বা বাইরের source material ব্যবহার করিনি; কার্যপরিধির audit `review_G1/boundary_incidents.json` ও প্রতিটি item-এর evidence locators-এ আছে।
