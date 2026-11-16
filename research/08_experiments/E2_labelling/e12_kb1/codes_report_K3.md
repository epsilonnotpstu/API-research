# K3 কোডিং রিপোর্ট (kb1)

## Method
- প্রতিটি item (U01-U18) এর proposition আগে `contract/` ও `impl/` ফাইলের বিপরীতে যাচাই করা হয়েছে (grep/sed, explicit item path দিয়ে)।
- divergence_kind: Y কি explicit guard/enum/route/return type দ্বারা তৈরি (DELIBERATE) নাকি omission/wrong variable/missing mapping (ACCIDENTAL)।
- contract_specificity: dedicated statement (SPECIFIC) নাকি shared schema/class-level path/silence (GENERIC)।

## Difficult items
- U05/U16: service layer এ env check নেই; id দিয়ে global lookup আসলে design হতে পারে, তবে omission ধরে ACCIDENTAL (confidence 2)।
- U10/U18: return type List<Token> explicit, তাই DELIBERATE; annotation এ responseContainer বাদ পড়েছে। U18 এ dockstore endpoint আসলে findQuayByUserId ডাকে (আলাদা quirk, Y প্রভাবিত হয় না)।
- U01: contract এ ConnectionStatus object ref shared schema থেকে এসেছে, তাই GENERIC।
- U08: contract text "launches" স্পষ্ট বক্তব্য হলেও impl users মুছে; SPECIFIC ধরা হয়েছে।
- U11: contract এ 400 এর অনুপস্থিতি explicit response list এর অংশ ধরে SPECIFIC (confidence 2)।

## Limitations
- কোনো item এর source execute বা compile করা হয়নি; runtime আচরণ অনুমান নয়, শুধু static reading।
- U17 mapper এর generated implementation নেই; MapStruct default name-matching ধরে নেওয়া হয়েছে।

## Boundary incidents
- নেই। শুধু item directory ও PROTOCOL.md (শুরুর কয়েক লাইন) পড়া হয়েছে।
