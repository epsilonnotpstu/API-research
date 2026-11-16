# K4 কোডিং রিপোর্ট (kb2)

## Method
- TASK_CODE.md ও PROTOCOL.md পড়া হয়েছে; প্রতিটি item শুধু নিজের directory (contract/ ও impl/) থেকে বিচার করা হয়েছে, items.csv-এর ১৮টি row, কোনো item-এর source চালানো হয়নি।
- প্রতিটি proposition ফাইলের সাথে যাচাই করা হয়েছে (grep/sed, explicit item path দিয়ে)। সব proposition-এর Y বাস্তবে মিলেছে, তাই কোনো item-কে proposition-mismatch হিসেবে UNCLEAR করা হয়নি।
- divergence_kind: explicit branch/serialization/response construction হলে DELIBERATE; wrong variable, unguarded null, missing mapping বা unused path variable হলে ACCIDENTAL।
- contract_specificity: dedicated prose/explicit flag/status হলে SPECIFIC; shared schema, $ref, generated snapshot বা inherited class-level path হলে GENERIC।

## Difficult items
- U26, U35 (Harbor bare success responder): explicit `_ =` discard ও bare responder দেখে DELIBERATE, তবে oversight হওয়ার সম্ভাবনা আছে (confidence 2)।
- U21, U25: field-এর অনুপস্থিতি (route-এ allowedImportAdditions নেই; domain model-এ description নেই) omission ধরে ACCIDENTAL, confidence 2।
- U29: MapStruct-generated class দেওয়া নেই; explicit mapping না থাকা থেকে অনুমান।
- U22, U32: contract-এর $ref সম্ভবত name collision/copy-paste; GENERIC ধরা হয়েছে।
- U20/U36: contract-এ explicit `type: string` থাকায় SPECIFIC, কিন্তু এটি copy-paste হতে পারে (confidence 2)।
- U34 vs U33: U34-এর path template explicit তাই SPECIFIC; U33-এ project scope class-level path থেকে আসে তাই GENERIC; এই সীমারেখা বিতর্কযোগ্য।

## Limitations
- Runtime data/history নেই; "evidently targets" বিচার শুধু code shape থেকে।
- U27/U31: handler ফাইলের পুরো call-chain সম্পূর্ণ পড়া হয়নি, SendError/Errors.Error() থেকে সিদ্ধান্ত।

## Boundary incidents
- কোনো boundary incident নেই। শুধু items.csv, item directory ও PROTOCOL.md ব্যবহার করা হয়েছে। Source-এর license header redacted ছিল।
