# K2 কোডিং রিপোর্ট (batch e11_b5)

## পদ্ধতি
প্রতিটি item আলাদাভাবে পড়া হয়েছে (TASK_CODE.md অনুযায়ী); item-এর মধ্যে কোনো তুলনা করা হয়নি। প্রতিটি proposition-এর Y impl ফাইলে যাচাই করা হয়েছে, তারপর divergence_kind ও contract_specificity কোড করা হয়েছে। কোনো source execute করা হয়নি।

## কঠিন item
- W24: JPQL-এ explicit `IS NULL OR` clause আছে; one-sided case oversight হতে পারে, তাই confidence 2।
- W40: handler-এ validation নেই, কিন্তু downstream layer artifact-এ নেই; ACCIDENTAL, confidence 2।
- V08: assignment check-এর অনুপস্থিতি omission হিসেবে ধরা হয়েছে।
- W25/X30/X27: contract-এ hand-written swagger class-এর field type; SPECIFIC ধরা হয়েছে (confidence 2)।
- V13/W41/W07/V27/V33/X50: shared schema বা silence-এর কারণে GENERIC।

## সীমাবদ্ধতা
শুধু দেওয়া artifact দেখা হয়েছে; অনুপস্থিত base class বা downstream validation অজানা।

## Boundary incident
কোনো নেই।
