**L6 — অন্ধ contract review**

**পদ্ধতি।** `items.csv`-এর ক্রমে Q01–Q61 স্বাধীনভাবে পর্যালোচনা করেছি। প্রথম shell command ছিল `cat TASK_M1.md`; এরপর অনুমোদিত `../../../09_collab/PROTOCOL.md` পড়েছি। প্রতিটি proposition-কে যাচাইয়ের প্রশ্ন হিসেবে ধরে সেই item-এর contract, route, handler, mapper ও প্রাসঙ্গিক persistence/helper code অনুসরণ করেছি। অন্য item-এর ফাইলের সঙ্গে তুলনা করে সিদ্ধান্ত নিইনি। নির্দেশনা: `TASK_M1.md:6–28`।

কোন artifact intended behaviour থেকে বিচ্যুত, তা নির্ধারণে operation-এর উদ্দেশ্য, একই item-এর ব্যাখ্যামূলক মন্তব্য, control flow ও schema-র অভ্যন্তরীণ সামঞ্জস্য বিবেচনা করেছি। সিদ্ধান্তের inferential অংশ rationale-এ ⚠️ দিয়ে চিহ্নিত। প্রত্যেক CSV row-তে নিজ item-এর evidence locator আছে; confidence 1–3 এবং rationale সর্বোচ্চ 40 শব্দ। উৎস: `TASK_M1.md:24–44`; ফল: `labels_L6.csv:2–62`।

**Label distribution।** মোট 61টি item-এর প্রতিটির জন্য একটি L1 label দেওয়া হয়েছে; CSV header ছাড়া 61টি row আছে। উৎস: `items.csv:2–62`, `labels_L6.csv:2–62`।

| L1 | সংখ্যা |
| --- | ---: |
| SPEC | 36 |
| IMPL | 25 |
| TEST | 0 |
| ENV | 0 |
| UNDECIDABLE | 0 |
| মোট | 61 |

Confidence 3 হয়েছে 51টি এবং confidence 2 হয়েছে 10টি; confidence 1 নেই। সংখ্যাগুলি সম্পূর্ণ CSV থেকে গণনা করা। উৎস: `labels_L6.csv:2–62`।

**কঠিন সিদ্ধান্ত।**

- Q07: ⚠️ configurable message limit-কে ইচ্ছাকৃত input constraint ধরে SPEC, confidence 2 দিয়েছি; সীমাটি schema-তে নেই। প্রমাণ: `Q07/contract/src/main/config/openapi/v2/openapi-user.yaml:1558–1563`; `Q07/impl/src/main/java/org/codelibs/fess/helper/ChatApiHelper.java:238–250`।
- Q12: ⚠️ অজানা flag-এর জন্য শূন্য flagID ও diagnostic-সহ blank result-কে deliberate fallback ধরে SPEC, confidence 2 দিয়েছি। Runtime বা history না থাকায় ইতিবাচক ID বজায় রাখাই আসল intent ছিল কি না নিশ্চিত নয়। প্রমাণ: `Q12/impl/pkg/handler/eval.go:84–119`; `Q12/contract/docs/api_docs/bundle.yaml:1106–1121`।
- Q15: ⚠️ implementation-এর UI ও evaluation catalog সম্পর্কে স্পষ্ট মন্তব্যের ভিত্তিতে enabled namespace-গুলিই effective catalog ধরে SPEC, confidence 2 দিয়েছি। বিকল্প ব্যাখ্যায় সংরক্ষিত disabled configuration-ও দেখানো কাম্য হতে পারে। প্রমাণ: `Q15/impl/pkg/handler/enricher.go:108–123,189–206`; `Q15/contract/docs/api_docs/bundle.yaml:1349–1357`।
- Q27: ⚠️ endpoint prose ও parameter annotation দুটিতেই namespace আবশ্যিক, কিন্তু handler ও DAO omission মেনে নেয়; তাই IMPL, confidence 2। Generic DAO-র optional filter একা endpoint-এর intent প্রমাণ করে না। প্রমাণ: `Q27/impl/internal/relationtuple/read_server.go:50–57,97–117`; `Q27/impl/internal/persistence/sql/relationtuples.go:230–235`।
- Q45: ⚠️ প্রদত্ত authorization callback-এ inherited-context read check পাইনি; IMPL, confidence 2। অনুপস্থিত service implementation-এর ভিতরে অতিরিক্ত authorization আছে কি না এখানে যাচাই করা যায়নি। প্রমাণ: `Q45/impl/nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ParameterContextResource.java:177–187,726–745`; contract requirement একই item-এর `contract/nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/api/ParameterContextResource.java:663–669`।
- Q54: ⚠️ concrete route ও handler উভয়ই path-এর এক member ব্যবহার করে; তাই collection path ও plural body-কে stale documentation ধরে SPEC, confidence 2। History ছাড়া উল্টো ব্যাখ্যা পুরোপুরি বাদ দেওয়া যায় না। প্রমাণ: `Q54/impl/engine/ladon/handler.go:285,380–393`; `Q54/contract/docs/api.swagger.json:506–540,1032–1039`।

অন্য confidence-2 সিদ্ধান্তগুলির নিজস্ব প্রমাণ ও সংক্ষিপ্ত যুক্তি সংশ্লিষ্ট CSV row-তে রয়েছে: Q23, Q32, Q53 ও Q55। উৎস: `labels_L6.csv:24,33,54,56`।

**সীমাবদ্ধতা।** প্যাকেজে runtime exchange ও VCS history নেই; তাই এগুলি static attribution, পরীক্ষায় পুনরুৎপাদিত ফল নয়। Network, Docker, Java, Maven, compilation অথবা item source execution করিনি। কেবল নিজের standard-library Python দিয়ে data পড়া, source excerpt redaction, output লেখা ও structural validation করেছি; repository module import করিনি। প্যাকেজের সীমা ও execution বিধি: `TASK_M1.md:10,20–22,40–44`।

Generated mapper implementation, framework serializer এবং কিছু service dependency সরবরাহ করা হয়নি। ⚠️ ওই অংশের ফল দৃশ্যমান declaration ও call flow থেকে অনুমিত; যেমন Q06-এর reverse mapping এবং Q38-এর nil slice serialization। প্রমাণ: `Q06/impl/rest/admin-v2/api/src/main/java/org/keycloak/models/mapper/MapStructClientModelMapper.java:18–33`; `Q38/impl/storage/handler.go:96–104,125–126`। Intent নির্ধারণের জন্য পুরোনো সংস্করণ, বাইরের documentation বা অন্য labeller-এর সিদ্ধান্ত ব্যবহার করিনি।

**সীমানা ও privacy ঘটনা।** অননুমোদিত boundary access ঘটেনি। এই directory-র বাইরের একমাত্র পড়া ফাইল ছিল অনুমোদিত `../../../09_collab/PROTOCOL.md`। Board, coordinator task, codebook, অন্য labeller-এর output বা অন্য project copy খোলা বা search করা হয়নি; নতুন ফাইল কেবল `labels_L6.csv` এবং `report_L6.md`। অনুমোদিত সীমানা: `TASK_M1.md:3,15–23,41–44`।

তবে source excerpt ছাপার সময় redaction filter দুটি credential-looking example বাদ দিতে পারেনি: `Q20/contract/api/openapi.yml:2093`-এর access-token example এবং `Q44/contract/swagger.yml:1064–1065`-এর OAuth-code example। মানগুলি এই report বা labels-এ পুনরায় দিইনি। এগুলি বাস্তব credential কি না যাচাই করিনি। প্রথম ঘটনার পরে token-prefix শনাক্তকরণ বাড়িয়েছি, কিন্তু দ্বিতীয় example-ও filter এড়িয়েছে; তাই privacy বিধির পূর্ণ অনুসরণ হয়েছে দাবি করছি না। প্রযোজ্য বিধি: `TASK_M1.md:20`।
