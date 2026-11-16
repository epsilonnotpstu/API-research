# K2 b3 রিপোর্ট (blind code-structure reading)

## Method
প্রতিটি item-এর শুধু নিজস্ব contract/ ও impl/ directory পড়া হয়েছে; items.csv-এর proposition-কে review target ধরে impl code-এ Y যাচাই করা হয়েছে। targeted grep/sed ও read-only python (-I -B) ব্যবহার হয়েছে। কোনো item code execute করা হয়নি, item-এর মধ্যে cross-item তুলনা করা হয়নি।

## Difficult items
- V03: query param নাম (credentials_identifier_similar) vs struct tag (preview_...) — stale naming না intentional, বোঝা যায়নি (confidence 1, DELIBERATE)।
- X32: contract-এর roles List<RoleEntity> শুধু shared MemberEntity model থেকে আসে; specificity borderline (GENERIC, confidence 1)।
- V40, W19, X64: explicit code/declaration আছে, কিন্তু simplification বা copy-paste typo-র সম্ভাবনা; confidence 2।
- V20: Vert.x RouterBuilder default BodyHandler যোগ করে কিনা artifacts থেকে যাচাই করা যায় না; code-এ শুধু CORS rootHandler আছে।
- X57, V12: hardcoded false / ParseDuration side effect — oversight হিসেবে ACCIDENTAL।
- X01/X53/X51: একই pattern; interface-এ explicit @NotNull, contract-এ required marker-এর অনুপস্থিতি (GENERIC)।

## Limitations
- ACCIDENTAL/DELIBERATE intent শুধু code structure থেকে অনুমান; commit history নেই।
- X24 ও W02-এ contract ও impl file identical।

## Boundary incidents
কোনো নেই। শুধু items.csv, TASK_CODE.md, PROTOCOL.md ও item directory পড়া হয়েছে (PROTOCOL.md-র প্রথম ৫০ লাইন)।
