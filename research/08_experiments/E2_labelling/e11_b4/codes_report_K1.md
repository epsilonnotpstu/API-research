# K1 blind coding report (e11_b4)

## Method
- প্রতিটি item-এর proposition পড়ে শুধু সেই item-এর `contract/` ও `impl/` ফাইল দেখেছি; অন্য item-এর সাথে তুলনা করিনি।
- `divergence_kind`: implementation-এর Y কি এমন project code থেকে আসে যা evidently Y-কে target করে (explicit guard/serialization/status/type choice = DELIBERATE; missing return/branch/mapping/check = ACCIDENTAL)।
- `contract_specificity`: contract-এ X নিয়ে dedicated statement (prose, explicit status, per-operation constraint) থাকলে SPECIFIC; shared component/generator artefact/নীরবতা হলে GENERIC।
- শুধু read-only grep/sed/python ব্যবহার করেছি, প্রতিটি search-এ explicit item path দিয়েছি; কোনো code execute করিনি।

## Difficult items
- V16: impl-এ শুধু ছয়টি autocomplete constant আছে, "username webauthn" যোগ করার code দেওয়া ফাইলে নেই, তাই Y যাচাই করা গেল না, UNCLEAR।
- V02/V07: contract-এ deviceEvent.action শুধু `type: string`; restricted enum শুধু shared `action` schema (device.yaml), event থেকে referenced নয়। তাই GENERIC।
- V31: CORS rootHandler explicit, কিন্তু body unprocessed হওয়া framework behaviour; ACCIDENTAL (confidence 2) ধরেছি।
- V09: URL format string-এ content suffix নেই; javadoc বলছে content URL, তাই ACCIDENTAL (confidence 2)।
- X19: explicit `ResponseEntity(CREATED)` তাই DELIBERATE, তবে return type SubmodelElement হওয়ায় borderline।
- V21: contract-এর query placement garbled annotation ("in: authorization") থেকে, তাই GENERIC।
- W26/W38: nesting শুধু sub-resource locator path থেকে implied, তাই GENERIC।

## Limitations
- Framework runtime behaviour (Vert.x, Spring, Jersey) যাচাই করা যায়নি; V31, V14 ও X22-এর বিচার code পড়ে।
- Contract-specificity-র GENERIC/SPECIFIC সীমারেখা generated spec-এর ক্ষেত্রে বিষয়ভিত্তিক।

## Boundary incidents
কোনো নেই। শুধু items.csv, TASK_CODE.md, ../../../09_collab/PROTOCOL.md এবং item directory পড়া হয়েছে; অন্য coder-এর output পড়া হয়নি।
