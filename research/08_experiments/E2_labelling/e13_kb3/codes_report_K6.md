# K6 কোডিং রিপোর্ট (kb3, Q43-Q61)

## পদ্ধতি
- শুধু TASK_CODE.md, PROTOCOL.md এবং প্রতিটি item-এর নিজস্ব contract/ ও impl/ ডিরেক্টরি পড়া হয়েছে; items-এর মধ্যে তুলনা করা হয়নি।
- প্রতিটি item-এ proposition-এর Y (implementation behaviour) সোর্স কোডে যাচাই করা হয়েছে, তারপর divergence_kind ও contract_specificity ঠিক করা হয়েছে।
- কোনো item source execute বা compile করা হয়নি। সব সার্চ explicit item path দিয়ে চালানো হয়েছে।

## কঠিন item
- Q47: contract-এর trailing slash আসে @Router annotation থেকে (generated swagger); SPECIFIC ধরেছি, confidence 2।
- Q49: handler-এ produces=text/plain আছে, কিন্তু view resolver স্পষ্টভাবে text/html সেট করে; DELIBERATE (confidence 2), কারণ mismatch oversight-ও হতে পারে।
- Q58, Q61: contract (swagger schema / @ApiOperation response) হয়তো copy-paste slip, কিন্তু impl-এর Y স্পষ্ট response construction; DELIBERATE।
- Q59: handler সব error-এ explicit 500 তৈরি করে, কিন্তু not-found branch নেই; ACCIDENTAL (confidence 2)।
- Q45: facade-এর verifyUpdateParameterContext ভেতরে inherited-context check থাকতে পারে, যা দেওয়া artifact-এ নেই; confidence 2।
- Q46: ctx.Error স্পষ্টভাবে ডাকা হয়, কিন্তু status সেট হয় না (default 200); ACCIDENTAL।
- Q52/Q57: Position schema shared, তাই GENERIC; impl-এর Network field type একটি data-model choice, DELIBERATE।
- Q43, Q53: contract-এর শর্ত shared annotation বা নীরবতা থেকে আসে, তাই GENERIC।

## সীমাবদ্ধতা
- যেসব item-এ impl ফাইল আংশিক (যেমন Q45, Q59), অনুপস্থিত ফাইলের আচরণ ধরে নিইনি।
- Rationale সর্বোচ্চ 40 শব্দে সীমিত।

## Boundary incident
- কোনো incident নেই।
