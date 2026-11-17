# F4 — Blind labelling প্রতিবেদন

## পদ্ধতি

প্রথম command ছিল `cat TASK_M1F.md`। এরপর অনুমোদিত `../../../09_collab/PROTOCOL.md` এবং `items.csv` পড়ে প্রতিটি item-এর নিজস্ব `contract/` ও `impl/` থেকে proposition যাচাই করেছি। ভিন্ন item-এর source তুলনা করিনি। Board, coordinator task, codebook, অন্য labeller-এর output বা বাইরের tool source পড়িনি। এই পরিসর task-এর নির্দেশ অনুযায়ী নির্ধারিত (`TASK_M1F.md:3-21`)।

Route registration, input validation, response construction, DTO mapping, authorization callback এবং persistence query ধরে প্রাসঙ্গিক আচরণ অনুসরণ করেছি। যে artifact intended behaviour থেকে বেশি বিচ্যুত বলে মনে হয়েছে, সেটিকে L1 দিয়েছি; mismatch থাকলেই স্বয়ংক্রিয়ভাবে IMPL দিইনি। Intended behaviour-এর সিদ্ধান্ত অনুমাননির্ভর, তাই rationale-এ ⚠️ ব্যবহার করেছি। প্রতিটি সিদ্ধান্তের নিজস্ব source locator আছে (`labels_F4.csv:2-62`)।

## Label distribution ও যাচাই

মোট ৬১টি item-এ একবার করে label দেওয়া হয়েছে: SPEC ৩৮টি এবং IMPL ২৩টি। Confidence ৩ পেয়েছে ৫০টি, confidence ২ পেয়েছে ১১টি; confidence ১ নেই। ভিত্তি: `labels_F4.csv:2-62`।

Standard-library Python দিয়ে output-এর item order `items.csv`-এর সঙ্গে যাচাই করেছি। ৬১টি unique item, নির্ধারিত পাঁচটি column, বৈধ L1/confidence এবং প্রতিটি rationale সর্বোচ্চ ৪০ শব্দ—এসব যাচাই করা হয়েছে। Evidence locator-এর file অস্তিত্ব, line সীমা এবং সংশ্লিষ্ট item-এর ভেতরে অবস্থানও যাচাই করেছি। শুধু সম্পূর্ণ final CSV ও এই প্রতিবেদন লেখা হয়েছে; L2 বা partial-label file তৈরি করিনি (`TASK_M1F.md:24-49`; `labels_F4.csv:1-62`)।

## কঠিন সিদ্ধান্ত

- **Q12 — SPEC, confidence ২।** ⚠️ অজানা flag-এর জন্য explicit `BlankResult`, zero ID ও diagnostic context দেখে এটিকে deliberate fallback হিসেবে বিচার করেছি। Positive-only response constraint বেশি সংকীর্ণ মনে হয়েছে। বিকল্প ব্যাখ্যা: failure-কে সফল response হিসেবে ফেরানোই implementation defect। প্রমাণ: `Q12/impl/pkg/handler/eval.go:84-120`; `Q12/contract/docs/api_docs/bundle.yaml:1106-1121`।
- **Q15 — SPEC, confidence ২।** ⚠️ Code comment ও filtering function UI/evaluation catalog-এ শুধু enabled enricher রাখার অভিপ্রায় দেখায়। Contract-এ flag-scoped enricher-এর inclusion যথেষ্ট qualified নয়। Disabled configuration দৃশ্যমান রাখার বিকল্প product intent-ও সম্ভব। প্রমাণ: `Q15/impl/pkg/handler/enricher.go:108-123,189-206`; `Q15/contract/docs/api_docs/bundle.yaml:1349-1357,1454-1457`।
- **Q20 — IMPL, confidence ২।** ⚠️ Issuer failure branch generic text helper ব্যবহার করে, যেখানে পাশের failure branch introspection error writer ব্যবহার করে। Structured error contract মানাই বেশি সম্ভাব্য intent মনে হয়েছে। প্রমাণ: `Q20/impl/internal/handlers/handler_oauth2_introspection.go:23-34`; `Q20/impl/internal/middlewares/authelia_context.go:89-94`; `Q20/contract/api/openapi.yml:2072-2077`।
- **Q25 — SPEC, confidence ২।** ⚠️ Listing ও file retrieval-এর জন্য পৃথক route দেখে slashless listing-কে ইচ্ছাকৃত মনে হয়েছে। Published slash-ই authoritative হওয়ার বিকল্প ব্যাখ্যাটি বাদ দেওয়ার মতো history নেই। প্রমাণ: `Q25/impl/http/server.go:588-596`; `Q25/contract/docs/swagger.json:482-525`।
- **Q33 — SPEC, confidence ২।** ⚠️ POST-এর replacement-style persistence-এ explicit null-parent clearing আছে; একই item-এর PATCH branch কেবল non-null parent পেলে পরিবর্তন করে। POST documentation-এ PATCH-এর semantics চলে এসেছে বলে বিচার করেছি। প্রমাণ: `Q33/impl/apiserver/src/main/java/org/dependencytrack/persistence/ProjectQueryManager.java:251-266,286-304`; `Q33/impl/apiserver/src/main/java/org/dependencytrack/resources/v1/ProjectResource.java:964-981`; `Q33/contract/apiserver/src/main/java/org/dependencytrack/resources/v1/ProjectResource.java:730-738`।
- **Q45 — IMPL, confidence ২।** ⚠️ দৃশ্যমান callback inherited-context permission পরীক্ষা করে না। তবে সরবরাহ না করা lower-layer authorization-এর সম্পূর্ণ আচরণ যাচাই সম্ভব নয়। প্রমাণ: `Q45/impl/nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ParameterContextResource.java:177-187,727-745`; contract-এর একই relative file `Q45/contract/nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ParameterContextResource.java:663-669`।

## সীমাবদ্ধতা ও খোলা প্রশ্ন

Runtime exchange ও VCS history অনুপস্থিত; intended behaviour-এর কোনো স্বাধীন authoritative oracle দেওয়া হয়নি (`TASK_M1F.md:10`)। তাই confidence evidence-এর স্পষ্টতা বোঝায়, পরীক্ষিত runtime নিশ্চয়তা নয়। Framework serialization, router matching ও generated mapper সম্পর্কে সিদ্ধান্ত static reading-এর অনুমান; item code চালানো, compilation, network, Docker, Java বা Maven ব্যবহার করা হয়নি (`TASK_M1F.md:21,36-41`)।

কম-confidence সিদ্ধান্তে fallback, disabled configuration প্রকাশ, update semantics এবং authorization-এর সম্ভাব্য বিকল্প intent খোলা প্রশ্ন হিসেবে রইল। প্রতিটি সিদ্ধান্ত বাধ্যতামূলক দুই-value answer set-এর মধ্যে সম্পূর্ণ দেওয়া হয়েছে (`TASK_M1F.md:30-35`; `labels_F4.csv:2-62`)।

## Boundary incidents ও privacy

অনুমোদিত protocol ছাড়া এই directory-এর বাইরের material access করিনি; board, coordinator task বা অন্য labeller-এর output-এ accidental access ঘটেনি। সব item search explicit item path দিয়ে করা হয়েছে; output লেখা হয়েছে শুধু `labels_F4.csv` ও `report_F4.md`-এ (`TASK_M1F.md:15-23`)।

তবে source মুদ্রণের redaction-এ ত্রুটি হয়েছে: `Q04/contract/api/openapi.yml:175`-এর session example, `Q20/contract/api/openapi.yml:2093`-এর token example এবং `Q59/impl/registry/app/api/controller/metadata/get_artifact_detail.go:129`-এর ব্যক্তিগত attribution tool output-এ অপর্যাপ্ত redaction-সহ এসেছে। মান বা নাম এখানে পুনরুৎপাদন করা হয়নি এবং deliverable-এ রাখা হয়নি। Example-line redaction পরে বাড়ানো হয়েছে; এই ঘটনাগুলি privacy instruction-এর ব্যত্যয় হিসেবে নথিবদ্ধ করছি, scope-বহির্ভূত file access হিসেবে নয় (`TASK_M1F.md:20,23`)।
