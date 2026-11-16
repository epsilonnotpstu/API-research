# L1 blind labelling প্রতিবেদন

## পদ্ধতি

`YOUR_ID=L1` অনুযায়ী ৮৬টি item-এর চূড়ান্ত সিদ্ধান্ত `labels_L1.csv`-তে লেখা হয়েছে। ক্রম ও item_id নেওয়া হয়েছে `items.csv` থেকে; প্রত্যেক item-এর প্রমাণ কেবল সেই item-এর `contract/` ও `impl/` থেকে নেওয়া হয়েছে। অন্য item-এর ফাইল দিয়ে কোনো সিদ্ধান্ত সমর্থন করা হয়নি। কাজের সীমা ও পাঁচটি অনুমোদিত label অনুসরণ করা হয়েছে। সূত্র: `TASK_M1.md`, “The items”, “Rules”, “Task M1” ও “Output”; `items.csv`, W01–X68 সারি।

প্রথম command ছিল `cat TASK_M1.md`; এরপর অনুমোদিত `../../../09_collab/PROTOCOL.md` পড়েছি। Proposition-কে যাচাইযোগ্য দাবি হিসেবে নিয়েছি, পূর্বনির্ধারিত সত্য হিসেবে নয়। প্রাসঙ্গিক request/response declaration, controller branch, DTO, validation এবং যেখানে দেওয়া আছে serializer/exception mapper অনুসরণ করেছি। Source পড়ার জন্য নিজের standard-library Python helper ব্যবহার করেছি; item source import, build বা execute করিনি। প্রতিটি সিদ্ধান্তের সঙ্গে item-সীমাবদ্ধ file ও line locator আছে। সূত্র: `labels_L1.csv`, সব item_id সারির `evidence_locators`।

Label মূলত intended behavior থেকে বিচ্যুত artifact নির্দেশ করে। কেবল mismatch দেখা গেলেই implementation-কে দায়ী করিনি। Artifact-এর নিজস্ব description, example, explicit transformation, validation অথবা control flow দিয়ে দায় নির্ণয় করেছি। দায়-নির্ণয়ের inference rationale-এ ⚠️ দিয়ে চিহ্নিত। Intent বেছে নেওয়ার যথেষ্ট প্রমাণ না থাকলে UNDECIDABLE দিয়েছি। Confidence 1 কম, 2 মাঝারি এবং 3 বেশি; এটি দায়-নির্ণয়ের আস্থা, runtime পরীক্ষার ফল নয়। উদাহরণ: [labels_L1.csv:2, W01](labels_L1.csv), [labels_L1.csv:4, W03](labels_L1.csv), [labels_L1.csv:71, X46](labels_L1.csv)।

## Label বণ্টন

নিচের হিসাব চূড়ান্ত CSV-এর ৮৬টি item_id সারি থেকে গণনা করা হয়েছে; এটি dataset-এর সাধারণ defect prevalence-এর দাবি নয়। সূত্র: `labels_L1.csv:2–87`, W01–X68 সারি।

| Label | সংখ্যা |
|---|---:|
| SPEC | 36 |
| IMPL | 37 |
| TEST | 0 |
| ENV | 0 |
| UNDECIDABLE | 13 |
| মোট | 86 |

Confidence 1: 13, confidence 2: 25, confidence 3: 48। প্রত্যেক item একবার আছে, `items.csv`-এর ক্রম অক্ষুণ্ণ, confidence অনুমোদিত সীমায় এবং সব rationale সর্বোচ্চ ৪০ whitespace-delimited শব্দ। CSV schema, uniqueness, completeness, locator-এর file existence ও line bounds যাচাই করা হয়েছে। সূত্র: `labels_L1.csv:1–87`; `items.csv`, সংশ্লিষ্ট item_id সারি।

## কঠিন সিদ্ধান্ত

- **W01 — UNDECIDABLE, confidence 1।** 50/asc প্রতিশ্রুতি এবং 10/desc configuration দুটোই স্পষ্ট। কোনটি intended default, তার স্বাধীন প্রমাণ নেই। সূত্র: [labels_L1.csv:2, W01](labels_L1.csv)।
- **W05 — UNDECIDABLE, confidence 1।** hydra.groups declaration এবং hydra.warden.groups guard-এর বিরোধ নিশ্চিত; শুধু guard চালু আছে বলেই সেটিকে intended scope বলা যায় না। সূত্র: [labels_L1.csv:6, W05](labels_L1.csv)।
- **W16 — UNDECIDABLE, confidence 1।** review না থাকলে null-filled 200 এবং deliberate 404 exception—দুটি নীতির মধ্যে কোনটি চাওয়া হয়েছে তা স্থানীয় প্রমাণে স্থির হয় না। সূত্র: [labels_L1.csv:17, W16](labels_L1.csv)।
- **W23 — SPEC, confidence 2।** ⚠️ Invalid schema-র 422 এবং incompatibility-র 409 আলাদা exception mapping হওয়ায় 422 omission-কে documentation gap হিসেবে নিয়েছি। এটি ইতিহাসভিত্তিক সিদ্ধান্ত নয়। সূত্র: [labels_L1.csv:24, W23](labels_L1.csv)।
- **X07 — SPEC, confidence 3।** ⚠️ Subjects পরিবর্তনের জন্য existing entry আবশ্যক; valid entry তৈরির সময় subjects-ও আবশ্যক। তাই documented 204 update-কে code সমর্থন করে, অতিরিক্ত 201 creation description সমস্যাযুক্ত। সূত্র: [labels_L1.csv:48, X07](labels_L1.csv)।
- **X30 — SPEC, confidence 2।** ⚠️ Decimal rate model schema-র integer restriction-কে প্রশ্নবিদ্ধ করে। তবে বাস্তব fractional response দেওয়া নেই; BigDecimal declaration নিজে কোনো নির্দিষ্ট response-এ fraction প্রমাণ করে না। সূত্র: [labels_L1.csv:60, X30](labels_L1.csv)।
- **X31 — IMPL, confidence 2।** ⚠️ _links annotation-এ intent দেখা যায়, কিন্তু local getter-এ runtime rename নেই। Supplied model-এর বাইরে inherited annotation বা serializer configuration যাচাই করা যায়নি; এ কারণে confidence সীমিত। সূত্র: [labels_L1.csv:61, X31](labels_L1.csv)।
- **X42 — UNDECIDABLE, confidence 1।** Singular schema এবং deliberate singleton-list formatting-এর কোনটি পরিবর্তন করা উচিত, তা স্থির করার প্রমাণ নেই। সূত্র: [labels_L1.csv:67, X42](labels_L1.csv)।
- **X45 — SPEC, confidence 2।** ⚠️ Per-record error shape নথিভুক্ত নয়, কিন্তু OffsetRecordSent-এ required field বা অতিরিক্ত property নিষেধ নেই। তাই error object অবশ্যই schema-invalid—এমন দাবি করিনি; documentation অসম্পূর্ণ বলেছি। সূত্র: [labels_L1.csv:70, X45](labels_L1.csv)।
- **X59 — SPEC, confidence 3।** ⚠️ Contract-এর ISO-code description ও en example parser-এর en/cy আচরণের সঙ্গে মেলে; ENGLISH/WELSH enum তার নিজের বর্ণনার সঙ্গেই অসংগত। সূত্র: [labels_L1.csv:79, X59](labels_L1.csv)।

## সীমাবদ্ধতা ও খোলা প্রশ্ন

Runtime exchange ও VCS history অনুপস্থিত—এই সীমা task-এ নির্দিষ্ট। কোনো network, Docker, Java, Maven, compilation বা item execution করা হয়নি। ফলে ফলাফল static review; নির্দিষ্ট deployment-এ response পর্যবেক্ষণের দাবি নেই। সূত্র: `TASK_M1.md`, “The items”, “No execution” ও “Tools”।

দেওয়া excerpt-এর বাইরে framework, generated interface, storage implementation বা global exception handling-এর আচরণ অনুমানসাপেক্ষ হতে পারে। যেমন W31-এ unknown sort field downstream-এ শেষ পর্যন্ত গৃহীত হয় কি না, W40-এ storage-এর আরও validation আছে কি না, X22-এ writer-এর চূড়ান্ত runtime response—এসব সম্পূর্ণভাবে যাচাইয়ের উপকরণ নেই। সংশ্লিষ্ট সিদ্ধান্তে confidence 2 রাখা হয়েছে এবং rationale-এ স্থানীয় প্রমাণের সীমা বজায় রাখা হয়েছে। সূত্র: [labels_L1.csv:32, W31](labels_L1.csv), [labels_L1.csv:41, W40](labels_L1.csv), [labels_L1.csv:55, X22](labels_L1.csv)।

UNDECIDABLE item-গুলোর খোলা প্রশ্ন হলো intended default, parameter spelling, route অথবা absence behavior-এর authoritative সিদ্ধান্ত কোনটি। এগুলো মেটাতে এই task-এ অনুপস্থিত intent বা runtime evidence লাগবে; এই review-তে সেগুলো সংগ্রহ করা হয়নি। সূত্র: `labels_L1.csv`, L1=UNDECIDABLE সারি; `TASK_M1.md`, “The items” ও “Boundary”।

## Boundary incidents

কোনো accidental boundary access ঘটেনি। `COLLAB_BOARD.md`, coordinator task, অন্য labeller-এর label/report, codebook, অন্য project copy বা বাইরের source পড়িনি। একমাত্র directory-বহির্ভূত গবেষণা নথি ছিল স্পষ্টভাবে অনুমোদিত `../../../09_collab/PROTOCOL.md`। Search/read সবসময় named item subtree-তে সীমিত ছিল; source excerpt ছাপানোর আগে credential-looking line ও personal attribution filter করেছি। এটি এই কাজের tool-use প্রক্রিয়ার বিবৃতি; অনুমোদনের ভিত্তি `TASK_M1.md`, “Supervisor authorization”, “Boundary”, “Privacy” ও “Tools”।

চূড়ান্ত deliverable: `labels_L1.csv` এবং এই `report_L1.md`। L2 বা আংশিক label file তৈরি করা হয়নি। সূত্র: `TASK_M1.md`, “Output”; `labels_L1.csv:1–87`।
