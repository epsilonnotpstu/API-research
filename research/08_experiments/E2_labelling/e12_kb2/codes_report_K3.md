# K3 কোডিং রিপোর্ট (kb2)

## Method
- TASK_CODE.md ও PROTOCOL.md পড়া হয়েছে; প্রতিটি item শুধু নিজের directory থেকে (contract/ ও impl/) বিচার করা হয়েছে। Item-এর মধ্যে তুলনা করা হয়নি।
- explicit item path দিয়ে grep/sed ব্যবহার করে সংশ্লিষ্ট লাইন পড়া হয়েছে; কোনো source execute করা হয়নি।
- Proposition-এর Y প্রতিটি ক্ষেত্রে ফাইলের সাথে মিলিয়ে দেখা হয়েছে; সবগুলোতে Y নিশ্চিত হয়েছে (কোনো UNCLEAR নেই)।
- Output: codes_K3.csv (18 row, items.csv order)।

## Difficult items
- U21, U25, U26/U35: implementation-এ field/payload নেই। এটি "explicit omission" নাকি oversight, তা বোঝা কঠিন; field পড়ার/ payload set করার কোনো branch না থাকায় ACCIDENTAL (confidence 2)।
- U22: contract-এ `connectionStatus` একটি shared schema ref (ConnectionStatus object), সম্ভবত ভুল reuse; specificity SPECIFIC ধরা হয়েছে কিন্তু অনিশ্চিত। U32-এর shared parameter $ref-কে boilerplate হিসেবে GENERIC ধরা হয়েছে; দুটির মধ্যে সীমারেখা বিষয়ভিত্তিক।
- U23: contract enum generated/inline বলে GENERIC (confidence 2)।
- U27/U31: contract-এ shared `Errors` definition, impl-এ explicit `json:"errors"` envelope: DELIBERATE + GENERIC।
- U30: দুটি path-এর variable নামের অমিল (projectKey/projectName) copy-paste oversight বলে ACCIDENTAL।

## Limitations
- U23, U29-এর contract ফাইলে generator উৎপত্তি অনুমান; কোনো version history নেই।
- U25-এ domain model-এ field-এর অনুপস্থিতিকে "data-model choice" না ধরে omission ধরা হয়েছে।

## Boundary incidents
কোনো নেই।
