# Z2 — Blind M1 পর্যালোচনা

## পদ্ধতি

`TASK_M1.md` অনুযায়ী `items.csv`-এর E001–E038 প্রতিটি item একবার, item_id ক্রমে বিচার করেছি। প্রতিটির নিজস্ব package-এর source, `spec.json`, নির্ধারিত run-এর request/response এবং প্রাসঙ্গিক ক্ষেত্রে `compose.log` মিলিয়েছি। CSV-তে source file:line, আসল specification JSON Pointer এবং exchange-এর physical line দিয়েছি। আগের request থেকে state তৈরির প্রমাণ দরকার হলে একই run-এর অতিরিক্ত exchange যুক্ত করেছি। পদ্ধতির নির্দেশনা: `TASK_M1.md`; item নির্বাচন ও run: `items.csv`, E001–E038।

`example_exchange + 1` দিয়ে exchange locator নির্ধারণ করেছি। একটি মধ্যবর্তী inspection-এ Python `splitlines()` Unicode line separator-কে অতিরিক্ত বিভাজক ধরেছিল; সেই ফল চূড়ান্ত সিদ্ধান্তে ব্যবহার করার আগে newline-ভিত্তিক file iteration দিয়ে সংশোধন করেছি। চূড়ান্ত CSV-র সব exchange locator এই physical-line পদ্ধতিতে যাচাই করা হয়েছে।

L1-তে discrepancy-টির প্রধান ব্যাখ্যা বেছে নিয়েছি। প্রত্যক্ষ source/stack-trace মিল থাকলে confidence 3; binding, পূর্ববর্তী malformed state, অথবা product intent সম্পর্কে অনুমান লাগলে সাধারণত 2। অনুমানভিত্তিক rationale-এ ⚠️ ব্যবহার করেছি। প্রমাণ ও প্রতিটি সিদ্ধান্ত: `labels_Z2.csv`, E001–E038।

## বণ্টন

| L1 | সংখ্যা |
| --- | ---: |
| IMPL | 30 |
| SPEC | 3 |
| TEST | 5 |
| ENV | 0 |
| UNDECIDABLE | 0 |
| মোট | 38 |

Confidence 3 হয়েছে 24টি, confidence 2 হয়েছে 14টি; confidence 1 নেই। এগুলো `labels_Z2.csv`-এর E001–E038 গণনা। শূন্য ENV বা UNDECIDABLE এই 38টি নির্বাচিত বিচারের ফল; deployment-গুলোতে অন্য ত্রুটি অনুপস্থিত থাকার দাবি নয়।

## কঠিন সিদ্ধান্ত

- **Optional parameter ও উদ্দেশ্য:** E013-এ tags এবং E016-এ username অনুপস্থিত থাকলে source সরাসরি 400 ফেরায়। ⚠️ সংশ্লিষ্ট operation-এর অর্থ এবং নিয়ন্ত্রিত rejection দেখে missing required declaration-কে SPEC, confidence 2 দিয়েছি; স্বাধীন product intent নেই। প্রমাণ: `K10/source/src/main/java/io/swagger/petstore/controller/PetController.java:234`, `K10/spec.json#/paths/~1pet~1findByTags/get/parameters/0/required`, `K10/r2/exchanges.jsonl:403`; `K04/source/src/main/java/io/swagger/petstore/controller/UserController.java:104`, `K04/spec.json#/paths/~1user~1login/get/parameters/0/required`, `K04/r1/exchanges.jsonl:1279`।
- **অযৌক্তিক filter বাধ্যবাধকতা:** E022/E025-এ optional group না থাকায় explicit guard request প্রত্যাখ্যান করছে; IMPL দিয়েছি। E017-এ username নিয়ে একই উদ্দেশ্যগত অনিশ্চয়তা থাকলেও observed 500 সরাসরি unsafe exception handling-এর প্রমাণ। প্রমাণ: `K09/source/api/src/main/java/se/devscout/scoutapi/resource/TagResource.java:44`, `K09/r1/exchanges.jsonl:2304`, `K09/r1/exchanges.jsonl:4304`, সংশ্লিষ্ট `K09/spec.json` operation-এর group.required=false; `K08/source/src/main/java/io/swagger/petstore/controller/UserController.java:104`, `K08/r1/exchanges.jsonl:1278`।
- **Malformed header ও বড় integer:** E003-এর HTML response HTTP parser-এ api_key header rejection দেখায়। E023/E026/E037-এর ID ঘোষিত int64-এর সীমা ছাড়িয়েছে; valid-request দাবি TEST। প্রমাণ: `K08/r2/exchanges.jsonl:410`, `K08/spec.json#/paths/~1pet~1{petId}/get/parameters/0/schema`; `K03/r1/exchanges.jsonl:962`, `K03/r2/exchanges.jsonl:411`, `K03/r1/exchanges.jsonl:1062` এবং সংশ্লিষ্ট `K03/spec.json` path parameter schema।
- **Binary capture:** E007-এর আট byte-এর base64 সম্পূর্ণ decode করা যায়; reported size-ও আট এবং truncated=false। text decode_error binary body-কে uncheckable করে না; এই flag TEST। upload response-এর অন্য সম্ভাব্য schema সমস্যা এই item-এর নির্দিষ্ট capture flag থেকে আলাদা। প্রমাণ: `K08/r2/exchanges.jsonl:660`, `K08/spec.json#/paths/~1pet~1{petId}~1uploadImage/post/requestBody/content/application~1octet-stream/schema`, `K08/source/src/main/java/io/swagger/petstore/controller/PetController.java:157`।
- **আগের invalid state ও response:** E005/E020-এর আগে name-বিহীন XML pet accepted হয়েছিল; E030-এর আগে form থেকে string-valued tags stored হয়েছিল। ⚠️ malformed test serialization অবদান রাখলেও accepted state ও সফল response-এর contract রক্ষা না হওয়াকে প্রধান IMPL ব্যাখ্যা দিয়েছি, confidence 2। E034-তেও একই বিবেচনা। প্রমাণ: `K03/r1/exchanges.jsonl:171`, `K03/r1/exchanges.jsonl:421`, `K08/r1/exchanges.jsonl:171`, `K08/r1/exchanges.jsonl:421`, `K03/r3/exchanges.jsonl:181`, `K03/r3/exchanges.jsonl:213`, `K04/r3/exchanges.jsonl:157`; source ও schema locator সংশ্লিষ্ট CSV row-তে আছে।
- **Serialization ও পুরোনো state আলাদা করা:** K10-এ name getter WRITE_ONLY; তাই E009/E011/E014-এর required-name omission-এর প্রত্যক্ষ source ব্যাখ্যা আছে। K12-তে price mixin একইভাবে response থেকে required price সরায়। প্রমাণ: `K10/source/src/main/java/io/swagger/petstore/model/Pet.java:55`, `K10/spec.json#/components/schemas/Pet/required`, `K10/r1/exchanges.jsonl:210`, `K10/r1/exchanges.jsonl:2`, `K10/r1/exchanges.jsonl:421`; `K12/source/market-rest/src/main/java/market/RestConfig.java:21`, `K12/spec.json#/definitions/ProductDTO/required`, `K12/r1/exchanges.jsonl:1002`।
- **নির্দিষ্ট 500-এর কারণ:** E018-এ empty Optional.get এবং E021-এ null keyType-এর switch stack trace-সহ মিলে যায়। E021-এর schema-তেও required declaration অনুপস্থিত; তবে crash-এর প্রধান কারণ unsafe handling ধরে IMPL দিয়েছি। প্রমাণ: `K05/source/src/main/java/app/coronawarn/verification/controller/InternalTanController.java:120`, `K05/r1/compose.log:12954`, `K05/r1/exchanges.jsonl:236`; `K11/source/src/main/java/app/coronawarn/verification/controller/ExternalTokenController.java:80`, `K11/source/src/main/java/app/coronawarn/verification/controller/ExternalTokenController.java:91`, `K11/r1/compose.log:10355`, `K11/r1/exchanges.jsonl:132`, `K11/spec.json#/components/schemas/RegistrationTokenRequest`।
- **অসম্ভব path requirement:** E031-এ route-এ {id} নেই, source-এর PathParam-ও ব্যবহৃত হয় না; body-র ID list দিয়ে কাজ হয়। তাই SPEC, confidence 3। প্রমাণ: `K01/source/api/src/main/java/se/devscout/scoutapi/resource/v1/FavouritesResourceV1.java:30`, একই file-এর line 55, `K01/spec.json#/paths/~1v1~1favourites/post/parameters/0`, `K01/r1/exchanges.jsonl:4662`।

## সীমাবদ্ধতা ও খোলা প্রশ্ন

Source-এর VCS history নেই, এবং উদ্দেশ্য নির্ণয়ের স্বাধীন product record পড়া হয়নি (`TASK_M1.md`)। Empty numeric/boolean বা control-character ID binding-এর exact framework implementation package source-এ খুঁজে পাইনি; তাই E001/E004/E012/E019/E024/E035-তে observed acceptance পর্যন্ত দাবি সীমিত এবং confidence 2 (`labels_Z2.csv`, সংশ্লিষ্ট row)। Petstore-এর নির্দিষ্ট 500-এর stack trace সরবরাহকৃত compose log-এ মেলেনি; E002-এর সুনির্দিষ্ট exception অনুমান হিসেবেই রাখা হয়েছে (`labels_Z2.csv`, E002)।

পর্যালোচনায় network, Docker, Java, Maven, compilation, package-source execution বা external tool source ব্যবহার করা হয়নি। Data parsing ও যাচাইয়ের জন্য শুধু standard-library Python `/usr/bin/python3 -I -B` ব্যবহার করেছি। এটি বর্তমান session-এর কাজের বিবরণ; পুনরায় SUT চালিয়ে নিশ্চিত করার দাবি নয়। CSV যাচাইয়ে 38টি unique ordered item, বৈধ L1/confidence, সর্বোচ্চ 37-word rationale, source/spec/exchange coverage এবং সব locator-এর অস্তিত্ব পরীক্ষা পাস করেছে (`labels_Z2.csv`, E001–E038)।

## Boundary incident

`TASK_M1.md` পড়ার আগে প্রথম filename discovery-তে explicit path ছাড়া `rg --files` চালিয়েছিলাম, glob ছিল PROTOCOL.md, TASK_M1.md, AGENTS.md এবং Z2/z2-সংক্রান্ত filename। এতে বর্তমান directory traverse হয়েছে; output-এ শুধু `TASK_M1.md` এসেছে। এটি task-এর explicit-search-path নিয়মের ব্যত্যয়; session-এর প্রথম discovery tool call-ই এর evidence। নিষিদ্ধ codebook, board, coordinator task বা অন্য labeller-এর file content খোলা হয়নি।

প্রথমে ভুল অবস্থান `09_collab/PROTOCOL.md` পড়ার চেষ্টা ব্যর্থ হয়েছিল, কোনো content পাওয়া যায়নি। পরে task-অনুমোদিত `../../../09_collab/PROTOCOL.md` পড়েছি। অন্য project copy বা বাইরের material খোলা, তালিকা করা বা তুলনা করা হয়নি; অনুমোদিত protocol-ই একমাত্র external read। Source ছাপানোর আগে credential-looking line redact করেছি। এই incident-গুলোর evidence বর্তমান session-এর প্রাথমিক tool transcript; task-এর exception ও সীমা `TASK_M1.md`-তে আছে।

শুধু `labels_Z2.csv` ও `report_Z2.md` লিখেছি; L2 বা partial-label file তৈরি করিনি।
