# K1 কোডিং রিপোর্ট (batch b5)

## পদ্ধতি
- প্রতিটি item (V/W/X) শুধু তার নিজের `contract/` ও `impl/` থেকে পড়া হয়েছে; item-এর মধ্যে ফাইল তুলনা করা হয়নি (শুধু V27/V33-এর একই handler আলাদাভাবে যাচাই)।
- Proposition-এর Y আসলেই impl-এ আছে কিনা আগে যাচাই করা হয়েছে; সব ২১টি item-এ Y নিশ্চিত হয়েছে, তাই কোনো item UNCLEAR হয়নি।
- `divergence_kind`: explicit branch/status/type/serializer/exception mapping হলে DELIBERATE; missing return বা missing check হলে ACCIDENTAL।
- `contract_specificity`: operation-specific response/security/prose হলে SPECIFIC; shared component/schema হলে GENERIC।
- কোনো item-এর source execute করা হয়নি; শুধু read-only grep/python ব্যবহার।

## কঠিন item
- W35, W30: 410 লেখার পর `return` নেই (ACCIDENTAL, confidence 3)।
- W40: `validateProjectReq` metadata.public যাচাই করে না; তবে downstream `projectCtl.Create` দেওয়া নেই, তাই ACCIDENTAL confidence 2।
- V08: 409 guard শুধু body-র দুই field দেখে; existing assignment check-এর branch অনুপস্থিত (ACCIDENTAL, 2)।
- W24: SQL-এ `minPrice IS NULL OR maxPrice IS NULL` explicit, কিন্তু intent oversight-ও হতে পারে; rubric অনুযায়ী DELIBERATE, confidence 2।
- X35, X39: explicit `HttpStatus.OK` তাই DELIBERATE, যদিও সম্ভবত generator-stub ভুল।
- X30: contract-এর `annualInterestRate` Integer একটি nested swagger class-এ; top-level response-এর সাথে সম্পর্ক পুরো যাচাই করা যায়নি।
- V11: contract-এ 404 অনুপস্থিত; contract_specificity SPECIFIC ধরা হয়েছে কারণ 200 BankSearchResult স্পষ্ট।
- V27/V33: autocomplete enum shared schema (generated) তাই GENERIC।

## সীমাবদ্ধতা
- কিছু item-এ downstream/framework আচরণ (যেমন Gson, Spring handler mapping) দেওয়া ফাইল থেকে অনুমান করা।
- SPECIFIC/GENERIC সীমারেখা annotated-source contract-এ (X30, W25, X42) অস্পষ্ট; confidence 2।

## Boundary incident
- নেই।
