# K5 কোডিং রিপোর্ট (kb2)

## Method
- TASK_CODE.md ও PROTOCOL.md পড়েছি; প্রতিটি item (Q22-Q42, মোট 21) শুধু নিজের contract/ ও impl/ ডিরেক্টরি থেকে বিচার করেছি, item-এর মধ্যে তুলনা করিনি।
- targeted grep/sed দিয়ে প্রতিটি proposition-এর Y (implementation behaviour) ফাইলের সঙ্গে মিলিয়ে দেখেছি; কোনো source execute করিনি।
- DELIBERATE: explicit route/guard/branch/type/constructor আছে। ACCIDENTAL: omission (unused flagID, nil slice, missing setAttribute, asymmetric field copy, blanket error mapping)।

## Difficult items
- Q27/Q37 (keto): query parsing-এ required check নেই, কিন্তু persistence-এ explicit if-nonempty branch আছে; তাই DELIBERATE (confidence 2)। Q37 contract-এ required:true আছে কিন্তু prose বলে শুধু namespace required, অর্থাৎ internal contradiction।
- Q29: unknown ID-র 400 আসে blanket error mapping থেকে, 404 annotation থাকা সত্ত্বেও; ACCIDENTAL (2)।
- Q31, Q33, Q36: দুই দিকেই যুক্তি আছে; Q31 GET handler-এ body bind না থাকা স্বাভাবিক ডিজাইন ধরেছি, Q33-এ explicit else branch, Q36-এ setAttribute অনুপস্থিতি omission ধরেছি।
- Q31/Q28/Q34/Q35: contract annotation copy-paste ধরনের হলেও explicit, তাই SPECIFIC (confidence 2)।
- Q41: contract-এ শুধু shared schema field, তাই GENERIC।

## Limitations
- Item-এ runtime বা history নেই; intent অনুমান করা হয়েছে code structure থেকে।
- Q40/Q42-এ contract specificity (path nesting) সীমারেখার কাছাকাছি।

## Boundary incidents
কোনো নেই।
