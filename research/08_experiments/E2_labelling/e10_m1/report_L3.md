L3-এর blind review সম্পন্ন হয়েছে। `items.csv`-এর ক্রমে ৪০টি item-এর প্রতিটির জন্য একটি L1 label, confidence, evidence locator এবং সর্বোচ্চ ৪০ শব্দের rationale দেওয়া হয়েছে। ফলাফলের উৎস: `labels_L3.csv`, item_id V01–V40।

প্রতিটি proposition-কে যাচাইযোগ্য দাবি হিসেবে ধরে সংশ্লিষ্ট item-এর নিজস্ব contract ও implementation পড়েছি। Schema reference, parameter parsing, route registration, serialization annotation, exception mapping ও প্রাসঙ্গিক call path অনুসরণ করেছি। অন্য item-এর ফাইলের সঙ্গে তুলনা করে সিদ্ধান্ত নেওয়া হয়নি। Contract-কে স্বয়ংক্রিয়ভাবে সঠিক ধরা হয়নি; তার নিজের description, example ও সংশ্লিষ্ট implementation-এর অর্থও বিবেচনা করেছি। Intended behaviour সম্পর্কে অনুমানকে rationale-এ ⚠️ দিয়ে চিহ্নিত করেছি। Confidence ১ কম, ২ মাঝারি এবং ৩ বেশি; UNDECIDABLE-এর confidence সিদ্ধান্ত নেওয়ার প্রমাণসীমা সম্পর্কে আস্থা বোঝায়।

Label বণ্টন নিচে দেওয়া হলো। গণনার ভিত্তি: `labels_L3.csv`, item_id V01–V40।

| L1 | সংখ্যা | শতাংশ |
|---|---:|---:|
| SPEC | ৮ | ২০% |
| IMPL | ২৬ | ৬৫% |
| TEST | ০ | ০% |
| ENV | ০ | ০% |
| UNDECIDABLE | ৬ | ১৫% |
| মোট | ৪০ | ১০০% |

কঠিন সিদ্ধান্তের একটি ধরন ছিল proposition-এর ভিত্তি অনুপস্থিত থাকা। V02-তে `action` কেবল string; পরবর্তী enum-টি `responseCode`-এর। তাই SUBMIT থাকলেই উল্লিখিত contract violation প্রতিষ্ঠিত হয় না। V07 ও V22-ও নিজেদের artifact পড়েই UNDECIDABLE পেয়েছে। এই সিদ্ধান্তে confidence ৩ মানে অভিযুক্ত artifact শনাক্ত করার ভিত্তি অনুপস্থিত থাকার বিষয়ে উচ্চ আস্থা। আলাদা ভুল test/request artifact না থাকায় এগুলোকে TEST বলা হয়নি। প্রমাণ: `V02/contract/rest-api/resources/src/main/resources/openapi/deviceEvent/deviceEvent.yaml:44-52`; `labels_L3.csv`, item_id V02, V07, V22।

CORS-সংক্রান্ত V19, V20 ও V31-এ confidence ১ রেখেছি। উদাহরণস্বরূপ, V19-এ CORS root handler নিবন্ধনের পর RouterBuilder router তৈরি করে; endpoint আবার parsed body পড়ছে। সরবরাহকৃত ফাইলে RouterBuilder-এর অভ্যন্তরীণ body processing নেই। শুধু explicit BodyHandler অনুপস্থিত দেখে body হারিয়ে যাওয়ার causal দাবি নিশ্চিত করা যায় না। প্রমাণ: `V19/impl/src/main/java/io/strimzi/kafka/bridge/http/HttpBridge.java:168-172`; `V19/impl/src/main/java/io/strimzi/kafka/bridge/http/HttpSinkBridgeEndpoint.java:497-518`; `labels_L3.csv`, item_id V19, V20, V31।

Duration grammar-এর ক্ষেত্রে ⚠️ ঘোষিত restriction-কে উদ্দেশ্যের পক্ষে প্রমাণ ধরে IMPL, confidence ২ দিয়েছি। V04-এর schema ও source annotation integer segment চায়, কিন্তু runtime path ParseDuration ও positivity check ব্যবহার করে। কোন grammar ভবিষ্যতে কাম্য, তা নির্ধারণের স্বাধীন নকশা-নথি নেই। V12-এর সিদ্ধান্তও কেবল তার নিজস্ব evidence-ভিত্তিক। প্রমাণ: `V04/contract/spec/api.json:7-10`; `V04/impl/selfservice/strategy/code/strategy_recovery_admin.go:74-79,143-166`; `labels_L3.csv`, item_id V04, V12।

Error-envelope attribution-এ ⚠️ required `errors` array-কে কার্যকর contract ধরে IMPL, confidence ২ দিয়েছি। V13-তে endpoint-এর default response Errors schema-তে যায়, কিন্তু mapper সরাসরি Error তৈরি করে। Mismatch স্পষ্ট হলেও কোন দিক বদলানো মূল নকশার সঙ্গে মিলবে, তার অতিরিক্ত ইতিহাস নেই। প্রমাণ: `V13/contract/swatch-contracts/src/main/resources/META-INF/openapi.yaml:316-317,1251-1258,1904-1909`; `V13/impl/swatch-contracts/src/main/java/com/redhat/swatch/contract/resource/SubscriptionsExceptionMapper.java:42-49`।

V26-এ specification-এর ভিতরেই অতিরিক্ত প্রমাণ আছে: schema-তে plural property, example-এ singular property; serialization annotation-ও singular। তাই ⚠️ SPEC attribution-এ confidence ৩ দিয়েছি। প্রমাণ: `V26/contract/rest-api/resources/src/main/resources/openapi/authentication/authentication.yaml:54-68,95-96,115-126`; `V26/impl/service/security/authentication/api/src/main/java/org/eclipse/kapua/service/authentication/token/LoginInfo.java:38-56`। V40-এ loop-এর order ঠিক রাখার বিষয়টি wrong-value selection থেকে পৃথক করেছি: implementation প্রথম total নেয় এবং অন্য unit-এ zero বসায়। প্রমাণ: `V40/contract/api/rhsm-subscriptions-api-spec.yaml:1703-1711`; `V40/impl/src/main/java/org/candlepin/subscriptions/resource/InstancesResource.java:215-225`।

সীমাবদ্ধতা হলো runtime exchange ও VCS history অনুপস্থিত; সরবরাহকৃত snapshot থেকেই attribution করা হয়েছে। Framework বা dependency-এর অদৃশ্য আচরণ, সম্ভাব্য অতিরিক্ত middleware এবং বাস্তব response পুনরুৎপাদন যাচাই করা হয়নি। V28-এর exact exception wrapping তাই অনিশ্চিত রাখা হয়েছে (`labels_L3.csv`, item_id V28)। কোনো item source compile বা execute করা হয়নি; network, Docker, Java, Maven, external tool source, codebook বা intent tool ব্যবহার করা হয়নি। নিজস্ব standard-library Python দিয়ে package data পড়া এবং output-এর গঠন যাচাই করা হয়েছে।

Boundary incident ঘটেনি। প্রথম shell command ছিল `cat TASK_M1.md`। অনুমোদিত ব্যতিক্রম `../../../09_collab/PROTOCOL.md` ছাড়া এই directory-এর বাইরের কোনো উপকরণ খোলা, তালিকাভুক্ত বা অনুসন্ধান করা হয়নি। COLLAB_BOARD.md, coordinator task file এবং অন্য labeller-এর label/report পড়া হয়নি। Source excerpt ছাপার আগে credential-looking line ও personal attribution redact করা হয়েছে। লেখা হয়েছে শুধু `labels_L3.csv` ও `report_L3.md`; L2 বা partial-label file তৈরি করা হয়নি।
