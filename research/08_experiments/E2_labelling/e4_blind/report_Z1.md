# Z1 — Blind M1 labelling প্রতিবেদন

## পদ্ধতি

`TASK_M1.md` অনুসারে `items.csv`-এর I001–I050 প্রতিটি item একবার করে, item_id ক্রমে মূল্যায়ন করেছি। চূড়ান্ত ফল `labels_Z1.csv`-এ আছে। সিদ্ধান্তের ভিত্তি ছিল সংশ্লিষ্ট K01–K04 package-এর source, specification এবং নির্দিষ্ট observed request/response; প্রয়োজনমতো একই package-এর compose log মিলিয়েছি। প্রতিটি CSV row-তে source file:line, JSON Pointer-সহ spec locator এবং exchange-এর physical line আছে। সিদ্ধান্তমূলক inference-গুলো `⚠️` দিয়ে চিহ্নিত। পদ্ধতির নির্দেশ: `TASK_M1.md`; পূর্ণ evidence: `labels_Z1.csv`, I001–I050।

Exchange locator গণনায় `example_exchange + 1` ব্যবহার করেছি। প্রথম পাঠে Python `splitlines()` JSON string-এর Unicode separator-ও line break হিসেবে ধরেছিল, ফলে সাময়িক ভুল mismatch দেখা যায়। newline (`\n`) অনুযায়ী পুনরায় পড়ে তা সংশোধন করেছি। চূড়ান্ত যাচাইয়ে সব ৫০টি referenced exchange-এর method, path template এবং status নিজ নিজ item-এর সঙ্গে মিলেছে; কোনো label সেই প্রাথমিক mismatch ধারণার ওপর দাঁড়ায়নি। উদাহরণ: `items.csv:2` ↔ `K01/r1/exchanges.jsonl:1013`; `items.csv:24` ↔ `K04/r1/exchanges.jsonl:621`।

SPEC বেছে নিয়েছি যখন source-এর সুস্পষ্ট mapping, optional model field, serialization policy বা ইচ্ছাকৃত validation response-এর সঙ্গে specification অসংগত। IMPL বেছে নিয়েছি যখন observed failure-এর জন্য null dereference, input-error-কে 500 করা, অথবা প্রয়োজনীয় validation অনুপস্থিত থাকার প্রমাণ আছে। TEST বেছে নিয়েছি checker-এর নিজস্ব অক্ষমতা বা পরীক্ষার অপূর্ণ semantic precondition-এর ক্ষেত্রে। দুই পক্ষের অসংগতি থাকলেও প্রত্যাশিত আচরণ নির্ধারণের প্রমাণ না থাকলে UNDECIDABLE রেখেছি। এগুলো এই blind review-এর নিজস্ব বিচারনীতি; কোনো codebook থেকে নেওয়া নয়। সংশ্লিষ্ট উদাহরণ: `labels_Z1.csv`, I017, I025, I034, I037, I006।

## বণ্টন

নিচের গণনা `labels_Z1.csv`-এর I001–I050 থেকে করা হয়েছে। একই exchange-এর ভিন্ন finding আলাদা item হিসেবেই গণিত হয়েছে; এগুলো স্বতন্ত্র root cause-এর সংখ্যা নয়। যেমন I005/I013 একই exchange নির্দেশ করে: `K01/r1/exchanges.jsonl:4404`।

| Package | SPEC | IMPL | TEST | ENV | UNDECIDABLE | মোট |
|---|---:|---:|---:|---:|---:|---:|
| K01 | 10 | 4 | 0 | 0 | 1 | 15 |
| K02 | 11 | 4 | 0 | 0 | 0 | 15 |
| K03 | 3 | 0 | 2 | 0 | 0 | 5 |
| K04 | 8 | 4 | 1 | 0 | 2 | 15 |
| মোট | 32 | 12 | 3 | 0 | 3 | 50 |

Confidence 3: ৪০টি; confidence 2: ১০টি; confidence 1: ০টি। প্রতিটি rationale সর্বোচ্চ ৩৩ whitespace-separated শব্দ; অনুমোদিত সীমা ৪০। উৎস: `labels_Z1.csv`, confidence ও rationale columns। ENV-এর জন্য স্বতন্ত্র causal evidence না পাওয়ায় কোনো item-এ সেই label দিইনি; এটি deployment-গুলো সম্পূর্ণ নির্ভুল হওয়ার দাবি নয়।

## কঠিন সিদ্ধান্ত ও তাদের প্রমাণ

- **I006, I028, I032 — UNDECIDABLE, confidence 2।** প্রথমটিতে optional name-এর অনুপস্থিতি handler প্রত্যাখ্যান করে; দ্বিতীয়টিতে open object schema মেনে unknown-key body পাঠিয়েও 400 হয়; তৃতীয়টিতে schema-সম্মত empty list handler প্রত্যাখ্যান করে। source-এর বর্তমান আচরণ দেখা যায়, কিন্তু সেটিই অভিপ্রেত contract কি না নির্ধারণের অতিরিক্ত প্রমাণ নেই। প্রমাণ: `K04/source/src/main/java/io/swagger/petstore/controller/PetController.java:99`, `K04/spec.json#/paths/~1pet~1{petId}/post/parameters/1`, `K04/r1/exchanges.jsonl:351`; `K01/source/api/src/main/java/se/devscout/scoutapi/resource/TagResource.java:81`, `K01/spec.json#/paths/~1v2~1tags~1{id}/put/parameters/1/schema`, `K01/r1/exchanges.jsonl:2117`; `K04/source/src/main/java/io/swagger/petstore/controller/UserController.java:87`, `K04/spec.json#/paths/~1user~1createWithList/post/requestBody/content/application~1json/schema`, `K04/r1/exchanges.jsonl:1053`।

- **I011 ও I016 — operation finding-এর জন্য SPEC; পাশাপাশি server failure আছে।** যথাক্রমে PUT/PATCH এবং GET/POST mapping mismatch সরাসরি source ও spec-এ দেখা যায়। অন্যদিকে I016-এর 500 log-এ missing media-র dereference দেখায়। একমাত্র L1 field-এ item-এর নির্দিষ্ট operation discrepancy-র কারণ দিয়েছি; অন্য failure-কে অস্বীকার করিনি। প্রমাণ: `K02/source/market-rest/src/main/java/market/rest/CartRestController.java:74`, `K02/spec.json#/paths/~1customer~1cart`, `K02/r1/exchanges.jsonl:211`; `K01/source/api/src/main/java/se/devscout/scoutapi/resource/MediaFileResource.java:245`, `K01/spec.json#/paths/~1v1~1media_files~1{id}~1file`, `K01/r1/exchanges.jsonl:1402`, `K01/r1/compose.log:84371`।

- **I034 ও I050 — TEST।** এই item-গুলোর finding হলো checker-এর unsupported encoding/serialization; এটি নিজে API implementation failure-এর প্রমাণ নয়। I034-এ form encoding spec-এ ঘোষিত এবং source-এ form overload আছে, যদিও একই exchange-এ 500-ও আছে। I050-এর Authorization-bearing request 201 পেয়েছে। I050-এর header schema উন্নত করা দরকার কি না, বা I034-এর 500-এর সুনির্দিষ্ট stack কী, এই label দিয়ে নিষ্পত্তি করিনি। প্রমাণ: `items.csv:35`, `K04/source/src/main/java/io/swagger/petstore/controller/OrderController.java:71`, `K04/spec.json#/paths/~1store~1order/post/requestBody/content/application~1x-www-form-urlencoded`, `K04/r1/exchanges.jsonl:646`; `items.csv:51`, `K03/source/src/main/java/app/coronawarn/verification/controller/InternalTanController.java:142`, `K03/spec.json#/paths/~1version~1v1~1tan~1teletan/post/parameters/0`, `K03/r1/exchanges.jsonl:231`।

- **I037 — TEST।** UUID-এর আকৃতি ঠিক হলেই registration session আছে এমন নয়। supplied placeholder token-এর session না থাকলে source স্পষ্টভাবে 400 দেয়; log-এ token না থাকার ঘটনাও আছে। প্রমাণ: `K03/source/src/main/java/app/coronawarn/verification/controller/ExternalTestStateController.java:102`, `K03/spec.json#/paths/~1version~1v1~1testresult/post/responses/400`, `K03/r1/exchanges.jsonl:82`, `K03/r1/compose.log:531`।

- **I035 ও I041 — IMPL; আগের write-এর প্রভাব বিবেচিত।** ⚠️ I035-এর listing-এ photoUrls-বিহীন যে pet id আছে, আগের form write-তেও সেটি আছে; helper default list-কে null দিয়ে overwrite করতে পারে। ⚠️ I041-এর আগে username-বিহীন user গৃহীত হয়েছে; lookup stored username-এ সরাসরি equals চালায়। এই source path-গুলো state-নির্ভর failure ব্যাখ্যা করে। প্রমাণ: `K04/source/src/main/java/io/swagger/petstore/data/PetData.java:121`, `K04/spec.json#/components/schemas/Pet/required`, `K04/r1/exchanges.jsonl:146`, `K04/r1/exchanges.jsonl:211`; `K04/source/src/main/java/io/swagger/petstore/data/UserData.java:55`, `K04/spec.json#/paths/~1user~1{username}/get/responses/404`, `K04/r1/exchanges.jsonl:952`, `K04/r1/exchanges.jsonl:1156`।

- **I026 — IMPL, confidence 2।** ⚠️ একই null-username lookup path update-এর 500-ও ব্যাখ্যা করতে পারে, কিন্তু সুনির্দিষ্ট exception stack নেই। K04-এ NOP logger ব্যবহারের বার্তা আছে। তাই সম্ভাব্য source path-কে নিশ্চিত observed stack হিসেবে উপস্থাপন করিনি। প্রমাণ: `K04/source/src/main/java/io/swagger/petstore/controller/UserController.java:152`, `K04/source/src/main/java/io/swagger/petstore/data/UserData.java:55`, `K04/spec.json#/paths/~1user~1{username}/put/requestBody/content/application~1x-www-form-urlencoded`, `K04/r1/exchanges.jsonl:1256`, `K04/r1/compose.log:8`।

## সীমাবদ্ধতা ও খোলা প্রশ্ন

Source-এর VCS history নেই বলে task জানায়। বাইরের intent evidence, coordinator material বা অন্য labeller-এর সিদ্ধান্ত ব্যবহার করিনি। ফলে code বনাম contract-এর বিরোধে ownership নির্ধারণে কিছু বিচারমূলক অনিশ্চয়তা রয়ে গেছে; বিশেষত I006, I028, I032। নির্দেশ ও অনিশ্চিত ফল: `TASK_M1.md`; `labels_Z1.csv`, সংশ্লিষ্ট item_id।

K04-এর config একটি `webapp/openapi.yaml` routing document নির্দেশ করে; এই পর্যালোচনায় সেই embedded routing document-এর বিষয়বস্তু পাওয়া যায়নি। Controller-এ সরাসরি HTTP annotation-ও নেই। তাই I023, I033, I039-এ observed operation, controller behavior এবং HTTP semantics থেকে SPEC অনুমান করেছি, confidence 2 রেখেছি। প্রমাণ: `K04/source/inflector.yaml:3`; `labels_Z1.csv`, I023, I033, I039। এগুলোর definitive intent যাচাইয়ের জন্য সংশ্লিষ্ট runtime routing document উপযোগী হবে; এই task-এর সীমার মধ্যে সেটি বাইরে খোঁজা হয়নি।

কোনো network request, Docker, Java, Maven, build বা package-source execution করিনি। কেবল standard-library Python দিয়ে package data পড়া, evidence যাচাই এবং নির্ধারিত দুই output লেখা হয়েছে। validation-এ ৫০টি unique ordered item_id, পাঁচটি অনুমোদিত L1 value, confidence range, rationale length, সব source/log line-এর অস্তিত্ব, সব JSON Pointer-এর resolution এবং exchange identity পরীক্ষা করেছি। সব পরীক্ষা পাস করেছে। এটি static evidence ও ইতিমধ্যে রেকর্ড হওয়া run-এর মূল্যায়ন; নতুন runtime reproduction নয়। ফলের উৎস: `labels_Z1.csv` এবং এই session-এর validation tool output।

## Boundary ও handling incident

এই অংশ session-এর সরাসরি tool-use নথি; নতুন কোনো boundary inspection করা হয়নি।

1. Task file পড়ার আগে filename discovery-তে `rg --files` চালিয়েছিলাম, যার explicit path argument ছিল না। সেটি বর্তমান directory-তেই সীমিত ছিল এবং শুধু `TASK_M1.md` filename ফিরিয়েছিল; তবু task-এর পরবর্তী explicit-path নিয়মের সঙ্গে command form মেলেনি। পরে সব search-এ নির্দিষ্ট permitted file/directory path ব্যবহার করেছি।
2. Protocol খুঁজতে একটি loop-এ অনুমোদিত ব্যতিক্রমের বাইরের `../../../../09_collab/PROTOCOL.md`-এর অস্তিত্ব পরীক্ষা হয়েছিল। সেটি পাওয়া যায়নি এবং তার content পড়া হয়নি। প্রকৃত protocol পড়েছি কেবল অনুমোদিত `../../../09_collab/PROTOCOL.md` থেকে। অন্য project copy-এর কোনো content খোলা বা তুলনা করা হয়নি।
3. প্রথম source-redaction pattern assignment ধরলেও একটি setter-call-এর masked password placeholder line ধরেনি (`K04/source/src/main/java/io/swagger/petstore/data/UserData.java:85`)। পরে redaction pattern বিস্তৃত করেছি। এই প্রতিবেদনে সেই value পুনর্মুদ্রণ করিনি।
4. উপরের ঘটনা ছাড়া নিষিদ্ধ `CODEBOOK_v0.6.md`, অন্য codebook, `TASK_M2.md`, `COLLAB_BOARD.md`, coordinator task, অন্য labeller-এর output বা intent-search output পড়া হয়নি। Task-এর নির্দিষ্ট override অনুসারে board পড়া বা update করা হয়নি। Output কেবল `labels_Z1.csv` ও `report_Z1.md`।
