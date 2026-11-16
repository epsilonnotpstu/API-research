**C6-এর কাজ ও পদ্ধতি**

`items.csv`-এর ক্রমে ৩৭টি item-এর coding `codes_C6.csv`-তে দিয়েছি। প্রতিটি row-এর implementation ও contract locator শুধু সেই item-এর directory-তে সীমাবদ্ধ। প্রথম command ছিল `cat TASK_CODE.md`; এরপর অনুমোদিত `../../../09_collab/PROTOCOL.md` পড়েছি। Coding-এর সংজ্ঞা ও output format-এর ভিত্তি `TASK_CODE.md`।

প্রতিটি proposition-এর Y সংশ্লিষ্ট handler, guard, DTO, parser অথবা serializer দিয়ে যাচাই করেছি; X-এর জন্য operation annotation, parameter description, response declaration এবং প্রযোজ্য schema দেখেছি। Explicit guard/type/response choice-কে DELIBERATE এবং missing handling বা wrong-variable use-কে ACCIDENTAL করেছি। এই label থেকে কোন artifact সঠিক বা developer কী চেয়েছিলেন, সে সিদ্ধান্ত নিইনি। সব row-তে Y-এর পক্ষে static evidence পাওয়ায় UNCLEAR ব্যবহার করিনি; পৃথক evidence প্রতিটি row-এর locator-এ আছে (`codes_C6.csv`, item_id=W01 থেকে W41; সংজ্ঞা: `TASK_CODE.md`)।

ফল: DELIBERATE ৩২টি, ACCIDENTAL ৫টি; SPECIFIC ৩২টি, GENERIC ৫টি। ACCIDENTAL item হলো W04, W11, W17, W18 ও W21। GENERIC item হলো W07, W11, W22, W25 ও W37; এগুলিতে X এসেছে reused model/schema থেকে। Confidence=2 দিয়েছি W03, W12 ও W23-তে; বাকি ৩৪টিতে confidence=3 (`codes_C6.csv`, সংশ্লিষ্ট item_id; `codes_work_C6/validation.txt`)।

**কঠিন সিদ্ধান্ত**

- W03-তে nonblank name বাদ পড়ে explicit `trim().isEmpty()` guard-এর কারণে। ⚠️ Guard-এর polarity ভুল হওয়ার ব্যাখ্যাও সম্ভব; task-এর explicit-guard মানদণ্ডে DELIBERATE, confidence=2 রেখেছি। Evidence: `W03/impl/app/src/main/java/io/apicurio/registry/rest/v2/GroupsResourceImpl.java:1097`; contract: সংশ্লিষ্ট `codes_C6.csv` row।
- W12-তে update path-এর name override-এ explicit empty-only guard আছে। ⚠️ এখানে developer intent নির্ধারণ করা যায় না; coded guard অনুসারে DELIBERATE, confidence=2। Evidence: `W12/impl/app/src/main/java/io/apicurio/registry/rest/v2/GroupsResourceImpl.java:1372`; `codes_C6.csv`, item_id=W12।
- W23-তে CREATE_VERSION fallback-এর storage call-এ `dryRun=false` literal আছে। ⚠️ Caller-এর flag propagate না হওয়া omission হিসেবেও ব্যাখ্যাযোগ্য; explicit false argument-কে প্রধান evidence ধরে DELIBERATE, confidence=2। Evidence: `W23/impl/app/src/main/java/io/apicurio/registry/rest/v3/GroupsResourceImpl.java:1325`; `codes_C6.csv`, item_id=W23।
- W17-তে zero-এর জন্য lower-bound handling নেই; upper-bound clamp-এর উপস্থিতি zero handling-এর dedicated choice প্রমাণ করে না। Evidence: `W17/impl/dockstore-webservice/src/main/java/io/dockstore/webservice/resources/WorkflowResource.java:829`। W18-তে path ID ব্যবহারের বদলে body থেকে পাওয়া ID ব্যবহৃত হয়েছে; task-এর wrong-variable উদাহরণ অনুসারে ACCIDENTAL। Evidence: `W18/impl/src/server/v2.0/handler/immutable.go:90`, `:100`, `:104`।
- W19, W28 এবং W29-এর নিজস্ব parser path-এ primitive-only guard আছে; সেই explicit type choice-এর জন্য DELIBERATE দিয়েছি। Array-এর পরে চূড়ান্ত HTTP response সম্পর্কে অতিরিক্ত দাবি করিনি (`codes_C6.csv`, item_id=W19, W28, W29)।
- W41-তে documented status ও failure prose operation-এ explicit বলে SPECIFIC করেছি। তবে 422 তালিকায় না থাকা থেকে সব undocumented status নিষিদ্ধ, এমন দাবি করিনি। Exception wrapping ও 422 mapping আলাদাভাবে explicit (`codes_C6.csv`, item_id=W41; `W41/contract/common/src/main/resources/META-INF/openapi.json#2019`)।

**সীমাবদ্ধতা ও যাচাই**

এটি সরবরাহকৃত source-এর static reading। Runtime data ও version history ছিল না; network, Docker, Java, Maven, compilation বা item source execution ব্যবহার করিনি। Confidence=3 অর্থ সরবরাহকৃত static evidence স্পষ্ট; runtime verification বোঝায় না। Confidence=2-তে classification boundary-এর ব্যাখ্যাগত অনিশ্চয়তা রেখেছি (`TASK_CODE.md`; `codes_C6.csv`, confidence column)।

নিজস্ব read-only Python validation দিয়ে সাতটি column, ৩৭টি item-এর সম্পূর্ণতা ও ক্রম, category/confidence values, item-local locator-এর file ও line bounds এবং rationale-এর ৪০-word সীমা পরীক্ষা করেছি। সব check passed; সর্বোচ্চ rationale ৩৫ word। এই check locator-এর অস্তিত্ব যাচাই করে, semantic judgment-এর স্বয়ংক্রিয় প্রমাণ নয় (`codes_work_C6/validation.txt`)।

**Boundary ও redaction incident**

অনুমোদিত protocol ছাড়া এই directory-এর বাইরে কোনো file খোলা, list বা search করিনি। COLLAB_BOARD, coordinator task বা অন্য coder-এর output পড়িনি। লিখেছি কেবল C6-এর নির্ধারিত output ও `codes_work_C6/`-তে।

একটি source excerpt-এর TODO comment-এ personal attribution প্রথম redaction filter এড়িয়ে tool output-এ এসেছিল। সংশ্লিষ্ট স্থান: `W19/impl/fineract-core/src/main/java/org/apache/fineract/infrastructure/core/serialization/JsonParserHelper.java:757`। পরে TODO/created-by/written-by comment redaction বাড়িয়েছি (`codes_work_C6/read_evidence.py`, `safe` function)। Attribution-এর মান CSV বা report-এ পুনরুৎপাদন করিনি। এটি redaction incident; অননুমোদিত path access ঘটেনি।
