# Blind labeller L4 — M1 প্রতিবেদন

## পদ্ধতি

প্রথম shell command ছিল `cat TASK_M1.md`। এরপর অনুমোদিত `../../../09_collab/PROTOCOL.md` এবং `items.csv` পড়েছি। এই task-এর বিশেষ অনুমোদন অনুযায়ী COLLAB_BOARD বা coordinator task পড়িনি। পর্যালোচনার ভিত্তি ছিল প্রতিটি row-এর proposition ও সেই item-এর নিজস্ব contract/implementation; proposition-কে প্রমাণ হিসেবে ধরা হয়নি। সূত্র: `TASK_M1.md`, “Supervisor authorization”, “The items”, “Rules”।

প্রতিটি item স্বাধীনভাবে বিচার করেছি; অন্য item-এর source দিয়ে কোনো সিদ্ধান্ত সমর্থন করিনি। Schema reference, handler, serializer annotation, parameter lookup এবং exception mapping অনুসরণ করেছি। যেখানে intended behavior সম্পর্কে সিদ্ধান্ত সরাসরি লেখা নেই, rationale-এ ⚠️ দিয়ে inference চিহ্নিত করেছি। শুধু mismatch পাওয়া মানেই implementation ভুল—এমন নিয়ম ব্যবহার করিনি। প্রতিটি label-এর সূত্র `labels_L4.csv`-এর সংশ্লিষ্ট `item_id` row-তে রয়েছে।

## Label distribution

`labels_L4.csv`-এর ৪০টি data row গণনা:

| L1 | সংখ্যা |
|---|---:|
| SPEC | 10 |
| IMPL | 24 |
| TEST | 0 |
| ENV | 0 |
| UNDECIDABLE | 6 |
| মোট | 40 |

Confidence 1 হলো কম, 2 মাঝারি এবং 3 বেশি। UNDECIDABLE-এর confidence সিদ্ধান্তটির নিশ্চয়তা বোঝায়; কোনো অনুপস্থিত defect-এর নিশ্চয়তা নয়। সব label `items.csv`-এর ক্রমে একবার করে দেওয়া হয়েছে; rationale-এর সর্বোচ্চ দৈর্ঘ্য ৩৬ শব্দ। সূত্র: `labels_L4.csv`, row V01–V40।

## কঠিন সিদ্ধান্ত

- **V02:** proposition action-এর ছয়টি অনুমোদিত মান দাবি করলেও contract-এ action শুধু string; enum আসলে responseCode-এর। তাই দাবি করা mismatch প্রতিষ্ঠিত হয়নি এবং UNDECIDABLE দিয়েছি। সূত্র: `V02/contract/rest-api/resources/src/main/resources/openapi/deviceEvent/deviceEvent.yaml:44`; `labels_L4.csv`, row V02। V07 ও V22-এর পৃথক পর্যালোচনার ব্যাখ্যা তাদের নিজস্ব CSV row-তে আছে।
- **V04 ও V12:** ⚠️ positive duration গ্রহণকারী parser এবং expiration interval-এর বর্ণনা দেখে regex-কে অতিরিক্ত সংকীর্ণ মনে হয়েছে। Integer-only syntax-এর স্বাধীন business justification নেই। তাই SPEC, confidence 2; parser-ই ভুল—এ সম্ভাবনা পুরোপুরি বাদ দেওয়া যায় না। পৃথক প্রমাণ: `labels_L4.csv`, row V04 ও V12।
- **V05:** ⚠️ singular endpoint description ও একটিমাত্র JsonDatastoreMessage তৈরির স্পষ্ট code collection schema reference-কে specification error হিসেবে চিহ্নিত করার পক্ষে শক্তিশালী প্রমাণ। সূত্র: `V05/contract/rest-api/resources/src/main/resources/openapi/dataMessage/dataMessage-scopeId-datastoreMessageId.yaml:26`; `V05/impl/rest-api/resources/src/main/java/org/eclipse/kapua/app/api/resources/v1/resources/DataMessagesJson.java:202`।
- **V13:** ⚠️ required errors array-কে intended response structure ধরে bare Error entity-কে implementation defect বলেছি। Runtime failure trace না থাকায় confidence 2। নির্দিষ্ট operation service exception ধরে response detail-ও ফেরায়; তাই প্রতিটি failure একই mapper দিয়ে যায়—এ দাবি করিনি। সূত্র: `V13/contract/swatch-contracts/src/main/resources/META-INF/openapi.yaml:1251`; `V13/impl/swatch-contracts/src/main/java/com/redhat/swatch/contract/resource/SubscriptionsExceptionMapper.java:42`; `V13/impl/swatch-contracts/src/main/java/com/redhat/swatch/contract/resource/ContractsResource.java:323`।
- **V16:** ⚠️ identifier-first strategy ইচ্ছাকৃতভাবে username webauthn বসায়; enum-কে অসম্পূর্ণ specification বলেছি। Feature value সরিয়ে implementation বদলানোকে intended সমাধান ধরে নিইনি। সূত্র: `V16/contract/spec/api.json:718`; `V16/impl/selfservice/strategy/idfirst/strategy_login.go:188`।
- **V19:** CORS root handler দেখা যায়, কিন্তু RouterBuilder-এর নিজস্ব body-processing implementation package-এ নেই। তাই CORS body parsing বন্ধ করে—এই causal assertion যাচাই করা যায়নি; UNDECIDABLE, confidence 1। সূত্র: `V19/impl/src/main/java/io/strimzi/kafka/bridge/http/HttpBridge.java:143`, একই file-এর line 168 ও 286। V20 ও V31-এর সিদ্ধান্তও তাদের নিজস্ব package পরীক্ষা করে নেওয়া হয়েছে; পৃথক সূত্র CSV-তে।
- **V21 ও V37:** ⚠️ authentication header extraction এবং POST route/form-এর স্পষ্ট design যথাক্রমে parameter-location ও HTTP-method documentation error নির্ধারণে সহায়ক হয়েছে। পৃথক প্রমাণ: `labels_L4.csv`, row V21 ও V37।
- **V40:** ⚠️ monthly totals map-এর key-তে month ও unit থাকলেও response builder প্রথম value বেছে নেয় এবং অন্য unit-এ zero দেয়। এটি যথাযথ total নির্বাচন না করার implementation defect হিসেবে বিচার করেছি। সূত্র: `V40/impl/src/main/java/org/candlepin/subscriptions/resource/InstancesResource.java:215`; `V40/impl/swatch-core/src/main/java/org/candlepin/subscriptions/db/model/InstanceMonthlyTotalKey.java:45`।

## সীমাবদ্ধতা

এই package-এ runtime exchange ও VCS history অনুপস্থিত; কাজের নির্ধারিত scope-ও তাই। কোনো network access, external tool source, codebook বা intent tool ব্যবহার করিনি; item source চালানো, compile/build, Docker, Java বা Maven ব্যবহার করিনি। শুধু নিজস্ব standard-library Python দিয়ে file reading, CSV writing ও output validation করেছি। সূত্র: `TASK_M1.md`, “The items”, “No execution”, “Tools”।

⚠️ Static analysis থেকে HTTP outcome ও intended behavior-এর attribution সব ক্ষেত্রে সমানভাবে নিশ্চিত নয়। Framework defaults, deployment configuration বা সংরক্ষিত data-এর পূর্ণ অবস্থা ছাড়া কিছু causal assertion যাচাই করা সম্ভব হয়নি। Confidence ও rationale-এ সেই সীমা রাখা হয়েছে; বিশেষত row V19, V20, V31 এবং মাঝারি-confidence সিদ্ধান্তগুলি দেখুন (`labels_L4.csv`)। TEST বা ENV-কে দায়ী করার মতো স্বতন্ত্র প্রমাণ পাওয়া যায়নি; count শূন্য হওয়া সেই artifact-গুলির সামগ্রিক শুদ্ধতার দাবি নয়।

CSV validation-এ header, ৪০টি unique item, মূল order, বৈধ L1 ও confidence, rationale-এর ৪০-শব্দসীমা এবং প্রতিটি evidence locator-এর নিজস্ব item-এর বিদ্যমান file/line পরীক্ষা করা হয়েছে। এই validation item source execution নয়। চূড়ান্ত outputs: `labels_L4.csv` এবং `report_L4.md`।

## Boundary incidents

কোনো accidental boundary access ঘটেনি। অনুমোদিত protocol ছাড়া এই directory-এর বাইরে কোনো project material খোলা, list বা search করা হয়নি। অন্য labeller-এর label/report, COLLAB_BOARD, coordinator task এবং অন্য project copy পড়িনি। Search-এ explicit item paths ব্যবহার করেছি; source snippet ছাপার আগে credential-looking ও attribution line redaction প্রয়োগ করেছি। Write সীমা ছিল এই directory-এর দুই নির্ধারিত output file। সূত্র: `TASK_M1.md`, “Boundary”, “Privacy”, “Writing”; এই পর্যালোচনার tool-use নথি।
