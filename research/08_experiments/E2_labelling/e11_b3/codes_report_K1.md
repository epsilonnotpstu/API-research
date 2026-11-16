# K1 blind coding report (batch b3)

## Method
- TASK_CODE.md এবং PROTOCOL.md পড়া হয়েছে; শুধু প্রতিটি item-এর নিজস্ব contract/ ও impl/ directory-তে নির্দিষ্ট path দিয়ে grep/sed ব্যবহার করা হয়েছে।
- প্রতিটি proposition-কে review target হিসেবে ফাইলের সাথে মিলিয়ে দেখা হয়েছে; কোনো item-এর সোর্স execute করা হয়নি, item-এর মধ্যে তুলনা করা হয়নি।
- divergence_kind: explicit guard/branch/DTO/type choice থাকলে DELIBERATE; dropped parameter, missing validation, wrong constant, framework default হলে ACCIDENTAL।
- contract_specificity: operation-specific prose/enum/default/status থাকলে SPECIFIC; shared component বা silence হলে GENERIC।

## Difficult items
- V20: CORS rootHandler-এর সাথে body handling-এর সম্পর্ক ফাইলে দেখা যায় না (framework default); তাই Y নিশ্চিত করা যায়নি, UNCLEAR।
- V03, X20: ভুল query key/constant; ইচ্ছাকৃত নাকি copy-paste ভুল তা অনুমান-নির্ভর (V03 confidence 1)।
- V40: explicit if/else আছে কিন্তু findFirst key উপেক্ষা করে; DELIBERATE ধরা হয়েছে, সীমারেখা অস্পষ্ট।
- V12: ParseDuration ব্যবহার explicit, কিন্তু compound গ্রহণ library default; ACCIDENTAL।
- X24, W02, W14, X32: contract annotation আর impl DTO/scope আলাদা; impl-এর পছন্দ explicit বলে DELIBERATE।
- V01: contract-এ 422 explicit কিন্তু base64 বর্ণনা shared schema-তে; SPECIFIC (confidence 2)।

## Limitations
- X57-এ dryRun parameter পাস না হওয়া oversight ধরা হয়েছে; কোড-মন্তব্য নেই।
- শুধু প্রদত্ত ফাইল দেখা হয়েছে; অন্য কোড (যেমন Vert.x defaults) যাচাই করা যায়নি।

## Boundary incidents
কোনো নেই। অন্য coder-এর ফাইল বা directory-র বাইরের কিছু পড়া হয়নি।
