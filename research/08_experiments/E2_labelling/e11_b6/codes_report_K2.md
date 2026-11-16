# K2 blind code-structure report (batch e11_b6)

## Method
- TASK_CODE.md এবং PROTOCOL.md পড়া হয়েছে; শুধু প্রতিটি item-এর নিজস্ব contract/ ও impl/ directory-তে explicit path দিয়ে grep/sed/python (read-only, `-I -B`) ব্যবহার করা হয়েছে।
- প্রতিটি proposition আগে impl-এর বিপরীতে যাচাই করা হয়েছে (Y সত্যিই ঘটে কি না), তারপর divergence_kind ও contract_specificity কোড করা হয়েছে।
- Item-এর মধ্যে কোনো cross-item diff/hash করা হয়নি। কোনো source code execute বা compile করা হয়নি।
- Output: codes_K2.csv (21 rows, items.csv order)।

## Difficult items
- V10: controller paymentProduct forward করে না (omission-এর মতো), কিন্তু entrypoint named constant PAYMENT_PRODUCT_SEPA ব্যবহার করে; DELIBERATE (confidence 2) কোড করা হয়েছে।
- X59: contract-এর enum ENGLISH/WELSH generator-derived মনে হয়, অথচ description ও example ISO code বলে; তাই GENERIC, confidence 1।
- V05, X62: contract-এর response schema সম্ভবত copy-paste, তবু operation-specific ও explicit, তাই SPECIFIC (confidence 2)।
- X67, V10: shared parameter component (sortParam/sortDir, PaymentProduct) আছে, কিন্তু operation সেগুলো explicit ref করে ও prose আছে; SPECIFIC (confidence 2)।
- X31: parent type দেওয়া নেই, তাই getLinks()-এ @JsonProperty না থাকাকে omission ধরা হয়েছে (confidence 2)।
- V35: schema RecordValue object/array-ও অনুমোদন করে; 422 ও base64 prose আছে বলে SPECIFIC (confidence 2)।
- X05, V24: contract shared/inherited schema (list wrapper, ErrorResponse default) ব্যবহার করে, তাই GENERIC।

## Limitations
- Runtime data বা history নেই; ACCIDENTAL/DELIBERATE সিদ্ধান্ত শুধু code structure থেকে অনুমান।
- SPECIFIC বনাম GENERIC সীমানা shared component ও generator-annotation ক্ষেত্রে বিষয়ভিত্তিক।

## Boundary incidents
- কোনো ইচ্ছাকৃত বা আকস্মিক boundary access হয়নি। প্রথম find কমান্ড items.csv-এর item directory ও TASK-এর ভিতরেই ছিল (পুরো e11_b6 directory-তে `find .`, যেখানে codes_K1* ফাইল বাদ দেওয়ার filter ছিল; কোনো codes_K1 ফাইল খোলা হয়নি)।
