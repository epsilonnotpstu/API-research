# K1 কোডিং রিপোর্ট (batch e11_b6)

## পদ্ধতি
- TASK_CODE.md ও PROTOCOL.md পড়ে প্রতিটি item-এর proposition, contract ও impl ফাইল শুধু সেই item-এর ডিরেক্টরির ভিতরে পড়েছি (grep/sed, read-only Python JSON parse)।
- divergence_kind: Y কি স্পষ্ট লক্ষ্যযুক্ত কোড (explicit branch, declared return type, explicit config) থেকে এসেছে, নাকি omission/framework default থেকে।
- contract_specificity: X কি operation-specific স্পষ্ট বক্তব্য, নাকি shared component/generator-reflected schema।
- কোনো item cross-compare করা হয়নি; কোনো item source চালানো হয়নি।

## কঠিন item
- V10: controller-এ paymentProduct ব্যবহৃত হয় না (omission), কিন্তু constant sepa-credit-transfers দেওয়া ফাইলে নেই, তাই UNCLEAR।
- X59, X68: contract-এর enum/nested map Java class থেকে reflected মনে হয়, তাই GENERIC (confidence 2)।
- X13: required=false generated codegen output, তাই GENERIC (confidence 2)।
- X67, V24: shared global parameter/response component, তাই GENERIC।
- V05, X62, X05: contract-এর operation-specific schema reference স্পষ্ট (সম্ভবত copy-paste), তাই SPECIFIC; কোন artifact ঠিক তা বিচার করিনি।
- V35: base64 বক্তব্য shared RecordKey schema-তে, 422 operation-specific; মিশ্র, SPECIFIC (confidence 2)।
- X47: deserializer ফাইল দেওয়া নেই; Boolean map type service থেকে অনুমান।

## সীমাবদ্ধতা
শুধু দেওয়া ফাইল দেখেছি; runtime path (যেমন X26/X43 এ view/table commit থেকে mapper পর্যন্ত call) অনুমিত।

## Boundary incident
নেই।
