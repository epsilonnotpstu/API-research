# K1 blind coding report (e11_b2)

## Method
- প্রতিটি item (21টি) আলাদাভাবে পড়া হয়েছে: proposition, তারপর impl এ সংশ্লিষ্ট handler/mapper/constant এবং contract এ সংশ্লিষ্ট operation/schema। শুধু item-এর নিজস্ব `contract/` ও `impl/` দেখা হয়েছে; targeted `grep`/`sed` ব্যবহার করা হয়েছে (explicit item path সহ)।
- `divergence_kind`: Y কি এমন project code থেকে আসে যা evidently Y-কে target করে (explicit constant, explicit status, declared route, data-model type)? নাকি omission/oversight (null dereference, missing guard, swapped variable, case-normalization ordering, missing path suffix)?
- `contract_specificity`: contract-এ dedicated, operation-specific statement আছে কি, নাকি shared component / boilerplate / silence।

## Difficult items
- X17: `requireNotNull` একটি explicit guard, কিন্তু `effect{}`-এর ভেতরে exception raise হয়, 400 recover branch এ পৌঁছায় না; তাই ACCIDENTAL (confidence 2)।
- X44: void method দ্বারা 204 deliberate ধরা হয়েছে (annotation-এ 204 documented); contract annotation-এ RoleEntity সম্ভবত copy-paste।
- V06: controller `paymentProduct` উপেক্ষা করে, কিন্তু protocol entrypoint এ named constant explicit; DELIBERATE (confidence 2)।
- V22: contract-এর `action` enum shared schema (device.yaml), deviceEvent-এ ব্যবহৃত হয় না (plain string); তাই contract GENERIC। SUBMIT enum constant documented, `normalizeAction` default branch দিয়ে pass করে।
- V34: URL explicit তৈরি, কিন্তু `/content` বাদ পড়া oversight বলে ACCIDENTAL (confidence 2)।
- V37: contract-এর `get` সম্ভবত annotation slip; impl explicit POST।
- V39: contract-এর 404 explicit status কিন্তু shared response ref; SPECIFIC (confidence 3 নয়, শুধু impl অংশে 3)।
- V38/V23/V32/W39/X25: contract-এর shared/generated boilerplate বনাম per-operation statement এর সীমারেখা বিচারসাপেক্ষ।

## Limitations
- কোনো code execute/compile করা হয়নি; runtime আচরণ static reading থেকে অনুমান।
- DELIBERATE/ACCIDENTAL নির্ধারণে developer intent অনুমান করতে হয়েছে (বিশেষত V06, V34, X44)।
- Line number গুলো অধিকাংশ spot-check করা, কিছু range আনুমানিক।

## Boundary incidents
- কোনো বাইরের ফাইল পড়া হয়নি (শুধু TASK_CODE.md ও PROTOCOL.md-এর প্রথম অংশ)।
- ছোট deviation: W08/W36 এবং V38/V23/V32 এর মধ্যে `md5sum` দিয়ে file identical কিনা দেখা হয়েছে (cross-item হ্যাশ তুলনা, কোনো content তুলনা বা সিদ্ধান্তে ব্যবহার নয়, প্রতিটি item আলাদাভাবে বিচার করা হয়েছে)। এছাড়া একটি ভুল `ls` কমান্ড W36 ডিরেক্টরি লিস্ট করেছে (নিজস্ব item-এর মধ্যেই)।
- Helper script: codes_work_K1/w.py।
