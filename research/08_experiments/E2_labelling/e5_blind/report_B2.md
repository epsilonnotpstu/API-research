B2 হিসেবে `items.csv`-এর E001–E029 ক্রমে সব ২৯টি item পর্যালোচনা করেছি। `../../R1_triage_codebook.md`-এর §৯–১০, বিশেষত v0.4 সংযোজন, অনুসরণ করেছি; file-এর শিরোনাম পুরোনো v0.3 হলেও §১০-এ চাওয়া নিয়ম রয়েছে। প্রতিটি item-এর নির্দিষ্ট violation message-এর জন্য deployed source, spec ও প্রতিনিধি traffic মিলিয়েছি; প্রয়োজনে আগের write এবং পরের read, integration test ও compose.log দেখেছি। CSV-র `evidence_locators`-এ প্রমাণ রয়েছে। Exchange locator ১-ভিত্তিক physical line; `items.csv`-এর `example_exchange` ০-ভিত্তিক।

প্রাথমিক L1-এর বণ্টন (`labels_B2.csv`, E001–E029):

| L1 | সংখ্যা |
|---|---:|
| IMPL | 18 |
| SPEC | 7 |
| TEST | 3 |
| UNDECIDABLE | 1 |
| SPEC_PARTIAL / IMPL_PARTIAL / ENV | 0 |

শুধু E019-এ `both_candidate=true`: `{}` থেকে null keyType switch crash করে, আর key/keyType-এ `@NotNull` থাকা সত্ত্বেও schema-তে required নেই। প্রাথমিক label IMPL রেখেছি; BOTH লিখিনি (§10.1, §10.6; `K06/source/src/main/java/app/coronawarn/verification/controller/ExternalTokenController.java:80`, `:91`; `K06/source/src/main/java/app/coronawarn/verification/model/RegistrationTokenRequest.java:47`, `:59`; `K06/spec.json#/components/schemas/RegistrationTokenRequest`; `K06/r1/compose.log:10355`)।

কঠিন attribution: ⚠️ E008/E011/E027-এ K09-এর explicit WRITE_ONLY annotation এবং নাম সরবরাহের পরেও ধারাবাহিক omission-কে code intent ধরে SPEC/S-RESP-MISSING দিয়েছি, confidence ২। Annotation-টি নিজেই ভুল mapping হওয়ার বিকল্প developer confirmation ছাড়া পুরোপুরি বাদ দেওয়া যায় না (`K09/source/src/main/java/io/swagger/petstore/model/Pet.java:55`; `K09/r1/exchanges.jsonl:4`, `:107`; `K09/spec.json#/components/schemas/Pet/required`)। বিপরীতে E007-এর নামহীন pet আগে XML দিয়ে তৈরি হয়েছিল; এখানে ইচ্ছাকৃত optionality ও validation-এর ত্রুটি আলাদা করার যথেষ্ট স্বাধীন প্রমাণ নেই, তাই UNDECIDABLE/১ (`K05/r1/exchanges.jsonl:171`, `:421`; `K05/source/src/main/java/io/swagger/petstore/model/Pet.java:31`)।

E002/E009/E013/E024/E025/E028-এ typed binding-কে intent-এর প্রমাণ ধরে IMPL/২ দিয়েছি। ⚠️ এটি attribution inference; framework-এর coercion implementation চালিয়ে যাচাই করিনি। সংশ্লিষ্ট Boolean/int/long declaration ও traffic প্রতিটি CSV row-তে উল্লেখ করেছি। E014/E021-এর explicit 418-কে §10.7 অনুযায়ী SPEC/S-STATUS দিয়েছি; success data-র জন্য HTTP semantics অনুপযুক্ত হওয়াকে আলাদা implementation fault ধরিনি (`K02/source/api/src/main/java/se/devscout/scoutapi/resource/SystemResource.java:32`; `K04/source/market-rest/src/main/java/market/rest/ProductsRestController.java:38`)।

E005-এর U+0012 header HTTP parser-এ প্রত্যাখ্যাত; E010/E026-এর সংখ্যা int64 সীমার বাইরে হলেও checker-এর Python int conversion সেটি গ্রহণ করে। §10.5 অনুযায়ী অস্থায়ী নাম `T-GEN-INVALID-HTTP` ও `T-ORACLE-FORMAT` শুধু `proposed_L2`-তে রেখেছি, L2 ফাঁকা (`K05/r2/exchanges.jsonl:410`; `K05/r1/exchanges.jsonl:962`, `:1062`; `../../tools/conformance.py:246`, `:441`)।

সীমাবদ্ধতা: ফল supplied snapshot ও traffic-নির্ভর; developer fix/confirmation বা live reproduction নেই। E004-এর 500 source guard ও proxy record দিয়ে সমর্থিত, নির্দিষ্ট exception stack frame নিশ্চিত করিনি (`K05/source/src/main/java/io/swagger/petstore/controller/PetController.java:72`; `K05/r1/compose.log:2023`, `:2024`)। Docker, Java, Maven, network বা external code চালাইনি; শুধু নিজস্ব Python দিয়ে data পড়া, output লেখা ও যাচাই করেছি। COLLAB_BOARD, অন্য labeller-এর output বা অন্য নিষিদ্ধ file খুলিনি। TASK-এর অনুমোদিত তিনটি বাইরের file ছাড়া বাইরের source দেখিনি।

যাচাই: ২৯টি row-এর item order, অনুমোদিত L1, confidence, rationale-এর সর্বোচ্চ ৩০ শব্দ, evidence file/physical line এবং JSON pointer পরীক্ষা পাস করেছে (`labels_B2.csv`, E001–E029)।
