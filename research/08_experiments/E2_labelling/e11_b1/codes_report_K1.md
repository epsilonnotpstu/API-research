# K1 blind coding report (b1)

## Method
- TASK_CODE.md এবং PROTOCOL.md পড়া হয়েছে; শুধু প্রতিটি item-এর নিজস্ব contract/ ও impl/ directory পড়া হয়েছে, items-এর মধ্যে কোনো তুলনা করা হয়নি।
- প্রতিটি proposition আগে impl source-এ verify করা হয়েছে (grep/sed, শুধু explicit item path-এ), তারপর divergence_kind ও contract_specificity code করা হয়েছে। কোনো source execute করা হয়নি।
- সব 21টি proposition-এর Y impl-এ নিশ্চিত হয়েছে; কোনোটিতে UNCLEAR দেওয়ার মতো mismatch পাওয়া যায়নি।

## Difficult items
- V19: CORS rootHandler আছে কিন্তু body handler নেই; Vert.x framework-এর আচরণ ফাইল থেকে যাচাই করা যায় না, তাই ACCIDENTAL, confidence 2।
- W03/W12: inverted condition (trim().isEmpty()) comment-এর intent-এর বিপরীত, তাই ACCIDENTAL।
- W11: labels/properties বাদ পড়া omission হিসেবে ধরা হয়েছে (intent-এর প্রমাণ নেই); contract shared schema, তাই GENERIC।
- W23: contract-এ 409 explicit, 422 অনুপস্থিত; SPECIFIC কিন্তু confidence 2।
- W10, X12: contract-এর explicit annotation সম্ভবত copy-paste ভুল, তবু dedicated statement হিসেবে SPECIFIC।
- X55, V17: contract-এর statement bare type / shared response component থেকে এসেছে, তাই GENERIC (confidence 2)।

## Limitations
- Framework default আচরণ (Vert.x, JAX-RS) ফাইল থেকে যাচাই করা যায়নি।
- SPECIFIC/GENERIC সীমারেখা (shared schema বনাম dedicated annotation) কয়েকটিতে judgment-নির্ভর।

## Boundary incidents
- কোনো boundary incident নেই। (একটি command harness-এর safety check-এ block হয়েছিল, কিছু চলেনি।)
