# Blind labeller L2 — Task M1

ল্যাবেলার পরিচয়: `YOUR_ID=L2`। `items.csv`-এর ক্রমে ৮৬টি item-এর প্রত্যেকটির জন্য একটি করে L1 label, confidence, evidence locator এবং সর্বোচ্চ ৪০ শব্দের rationale দেওয়া হয়েছে। ফলাফল: [labels_L2.csv](labels_L2.csv), data rows 1–86; ইনপুট: [items.csv](items.csv), data rows 1–86।

পদ্ধতি: প্রথম command ছিল `cat TASK_M1.md`। এরপর অনুমোদিত `../../../09_collab/PROTOCOL.md` এবং item তালিকা পড়েছি। প্রতিটি proposition-কে যাচাইয়ের লক্ষ্য হিসেবে নিয়ে শুধু সংশ্লিষ্ট item-এর `contract/` ও `impl/` থেকে annotation, parameter binding, control flow, DTO, serializer এবং exception mapping অনুসরণ করেছি। কোনো item-এর বিচার অন্য item-এর ফাইলের ওপর নির্ভর করেনি। প্রযোজ্য কাজের সীমা: [TASK_M1.md](TASK_M1.md), “Rules” ও “Task M1”; প্রতিটি সিদ্ধান্তের সূত্র: [labels_L2.csv](labels_L2.csv), `evidence_locators` column।

শুধু contract–implementation অমিলকে implementation-এর ভুল ধরে নেওয়া হয়নি। একই item-এর বর্ণনা, example, typed interface, dedicated DTO বা control flow থেকে intended behaviour-এর সমর্থন থাকলে সেই অনুযায়ী SPEC অথবা IMPL বেছে নিয়েছি। পর্যাপ্ত দিকনির্দেশ না থাকলে UNDECIDABLE দিয়েছি। অনুমাননির্ভর সিদ্ধান্তে ⚠️ চিহ্ন ব্যবহার করেছি। Confidence: 1 = কম, 2 = মাঝারি, 3 = বেশি; এটি artifact-এর দায় নির্ধারণের নিশ্চয়তা, runtime পরীক্ষার ফল নয়। উদাহরণ: [labels_L2.csv](labels_L2.csv), item_id=W01, X03, X46, X54।

Label distribution:

| L1 | সংখ্যা |
| --- | ---: |
| SPEC | 35 |
| IMPL | 38 |
| TEST | 0 |
| ENV | 0 |
| UNDECIDABLE | 13 |
| মোট | 86 |

উৎস: [labels_L2.csv](labels_L2.csv), data rows 1–86। Confidence distribution: 1-এর ১২টি, 2-এর ২৩টি, 3-এর ৫১টি। সব rationale ৪০ শব্দের সীমার মধ্যে; সর্বোচ্চ ৩১ শব্দ। একই CSV-র `confidence` ও `rationale` columns থেকে গণনা করা হয়েছে।

কঠিন ক্ষেত্রে W01-এর documented default ও configured default-এর মধ্যে কোনটি intended, তা স্থানীয় evidence মীমাংসা করে না; W05-এর দুই OAuth scope নামের ক্ষেত্রেও স্বাধীন policy নেই। দুটিই UNDECIDABLE। X22-তে duplicate error response writer পর্যন্ত অনুসরণ করা গেলেও writer ও underlying mapping অনুপস্থিত; তাই proposition-এর চূড়ান্ত 500 নিশ্চিত করা যায়নি। X45-এর OffsetRecordSent schema-তে partition/offset required নয় এবং অতিরিক্ত property নিষিদ্ধ নয়; ফলে error entry থাকলেই schema violation প্রমাণিত হয় না। সূত্র: [labels_L2.csv](labels_L2.csv), item_id=W01, W05, X22, X45 এবং সংশ্লিষ্ট `evidence_locators`।

⚠️ X07-তে existing policy entry-এর subjects পরিবর্তনের strategy ও 204 response দেখে অতিরিক্ত 201 creation response-কে SPEC, confidence 2 দিয়েছি; creation semantics-এর স্বাধীন প্রমাণ সীমিত। W23-তে unprocessable schema ও rule violation-এর পৃথক status mapping দেখে অনুল্লিখিত 422-কে documentation ঘাটতি হিসেবে SPEC, confidence 2 দিয়েছি। এ সিদ্ধান্তগুলো inference হিসেবে চিহ্নিত। সূত্র: [labels_L2.csv](labels_L2.csv), item_id=X07, W23।

সীমাবদ্ধতা: এটি static review। কোনো runtime exchange বা VCS history সরবরাহ করা হয়নি; network, Docker, Java, Maven, compilation কিংবা item source execution ব্যবহার করা হয়নি। কেবল standard-library Python দিয়ে package data পড়া ও output structure যাচাই করা হয়েছে। অনুপস্থিত framework configuration, generated bean validation, response writer বা storage implementation-এর আচরণ নিশ্চিত বলে দাবি করিনি; প্রযোজ্য rationale-তে সীমাবদ্ধতা রেখেছি। TEST বা ENV বেছে নেওয়ার মতো স্বতন্ত্র artifact evidence পাওয়া যায়নি। পরিধির ভিত্তি: [TASK_M1.md](TASK_M1.md), “The items”, “No execution” ও “Tools”; অনিশ্চয়তার উদাহরণ: [labels_L2.csv](labels_L2.csv), item_id=W40, X17, X22, X31।

Boundary incidents: কোনো অনিচ্ছাকৃত boundary access ঘটেনি। COLLAB_BOARD.md, coordinator task, codebook, অন্য labeller-এর label/report কিংবা অনুমোদিত directory-এর বাইরের অন্য project material খোলা, তালিকাভুক্ত বা search করা হয়নি। একমাত্র বাইরের পাঠ ছিল অনুমোদিত protocol। Search-এ নির্দিষ্ট item path ব্যবহার করেছি; source উদ্ধৃতির আগে attribution ও credential-looking line redact করেছি। কেবল `labels_L2.csv` এবং `report_L2.md` লিখেছি; কোনো item source পরিবর্তন বা partial label file তৈরি করিনি। সীমা: [TASK_M1.md](TASK_M1.md), “Boundary”, “Privacy”, “Search paths” ও “Writing”।

কাজ সম্পন্ন: CSV-তে ৮৬টি unique item, input order, অনুমোদিত L1 values, confidence range, rationale word limit এবং প্রতিটি evidence path/line-এর অস্তিত্ব যাচাই করা হয়েছে। পাঠকের জন্য খোলা প্রশ্ন হলো UNDECIDABLE item-গুলোর intended policy বা অনুপস্থিত mapping; বর্তমান evidence সীমার মধ্যে কোনো deliverable বাকি নেই। ফলাফলের সূত্র: [labels_L2.csv](labels_L2.csv), data rows 1–86।
