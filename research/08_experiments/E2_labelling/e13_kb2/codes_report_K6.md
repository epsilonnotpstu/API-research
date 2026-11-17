# K6 কোডিং রিপোর্ট (kb2, 21 item)

## Method
- শুধু TASK_CODE.md ও PROTOCOL.md পড়েছি; প্রতিটি item আলাদাভাবে শুধু নিজের contract/ ও impl/ থেকে বিচার করেছি, item-এর মধ্যে তুলনা করিনি (একই ফাইল দুই item-এ থাকলেও আলাদা করে দেখেছি)।
- প্রতিটি proposition আগে source-এর সাথে মিলিয়েছি (grep/sed, read-only); কোনো কোড execute করিনি।
- divergence_kind: explicit guard/branch/route/status/type = DELIBERATE; missing guard, nil slice, বাদ পড়া field, বাদ পড়া session set = ACCIDENTAL।
- contract_specificity: নির্দিষ্ট prose/annotation/path entry = SPECIFIC; নীরবতা বা inherited/shared schema = GENERIC।

## Difficult items
- Q27/Q37 (keto): parsing-এ required-guard নেই, কিন্তু persistence-এ explicit `!= ""` branch আছে; DELIBERATE দিয়েছি (confidence 2)। Q37-এ required flag এসেছে inherited queryRelationTuple থেকে (impl-এ সংজ্ঞা নেই), prose বলে শুধু namespace required, তাই GENERIC।
- Q29: সব update error blanket 400 হয়; unknown-ID-র জন্য আলাদা 404 branch নেই। explicit status construction ধরে DELIBERATE (borderline, conf 2)।
- Q33: `else { setParent(null) }` explicit branch ধরে DELIBERATE (conf 2); পাশের duplicate setParent লাইন অগোছালো।
- Q31/Q28/Q34/Q35/Q39/Q22: contract-এর annotation ভুল/copy-paste মনে হলেও explicit বলে SPECIFIC।
- Q40/Q42: path parameter required হওয়া OpenAPI-তে বাধ্যতামূলক boilerplate, তবু প্রতি operation-এ inline declared, তাই SPECIFIC (conf 2 বা কম নিশ্চিত)।

## Limitations
- Locator-এর কিছু line number আনুমানিক (range)। Q37-এর queryRelationTuple সংজ্ঞা দেওয়া artifacts-এ নেই।
- DELIBERATE/ACCIDENTAL সীমারেখা কিছু item-এ ব্যক্তিনির্ভর।

## Boundary incidents
কোনো নেই।
