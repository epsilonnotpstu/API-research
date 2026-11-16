# K2 blind code reading, batch b4 (21 items)

## Method
- প্রতিটি item শুধু তার নিজের `contract/` ও `impl/` থেকে পড়া হয়েছে; item-এর মধ্যে তুলনা করা হয়নি। কোনো source code execute করা হয়নি।
- Proposition-এর Y (implementation behaviour) প্রথমে impl ফাইলে যাচাই করা হয়েছে, তারপর `divergence_kind` ঠিক করা হয়েছে (explicit guard/status/serialization/branch = DELIBERATE; missing return, wrong exception, ignored parameter, unset default = ACCIDENTAL)।
- `contract_specificity`: operation-specific prose/status/constraint = SPECIFIC; shared component, generator output, বা নীরবতা = GENERIC।
- Output: `codes_K2.csv` (items.csv ক্রমে, 21 row)।

## কঠিন item
- V31: CORS rootHandler বসানো হয়েছে কিন্তু BodyHandler নেই; body হারানো Vert.x default-এর উপর নির্ভর করে, এখানে যাচাইযোগ্য নয় (confidence 1)।
- V09: URL-এ `/content` নেই, কিন্তু `?references=REWRITE` থেকে বোঝা যায় content উদ্দেশ্য ছিল; তাই ACCIDENTAL (confidence 2), DELIBERATE-ও যুক্তিসঙ্গত।
- V02/V07: দুটি item-এর impl ও contract সম্পূর্ণ অভিন্ন (diff দিয়ে যাচাই), তাই একই code। SUBMIT একটি explicit enum constant, normalizeAction শুধু alias map করে; contract-এর `action` enum shared schema বলে GENERIC (confidence 1)।
- V15/V25: impl ও contract অভিন্ন; mapper explicit ভাবে একক Error তৈরি করে (DELIBERATE); contract-এর Errors envelope shared default response থেকে আসে (GENERIC)।
- X19: bodyless 201 explicit `new ResponseEntity(HttpStatus.CREATED)`; oversight হতে পারে, কিন্তু rubric অনুযায়ী explicit response construction হিসেবে DELIBERATE (confidence 2)।
- X22: 500 সরাসরি যাচাই করা যায়নি; conflict mapping-এর অনুপস্থিতি দেখা গেছে।
- V21 ও V16: contract-এর বিবৃতি generator/annotation artifact (ভুল `in: authorization` annotation; Go enum), তাই GENERIC।

## Limitations
- Framework runtime আচরণ (Vert.x, Go herodot status) execute না করে অনুমান করা হয়েছে।
- DELIBERATE/ACCIDENTAL সীমারেখা কয়েকটি item-এ (V09, X19, V04) বিচারসাপেক্ষ।

## Boundary incidents
- কোনো ঘটনা নেই। শুধু নির্ধারিত directory ও PROTOCOL.md-এর অনুমোদিত অংশ (প্রথম ৩০ লাইন) পড়া হয়েছে; অন্য coder-এর output পড়া হয়নি।
