# Blind coder K2 — b1 report

## Method
- প্রতিটি item শুধু নিজের `contract/` ও `impl/` directory থেকে পড়া হয়েছে; items এর মধ্যে কোনো তুলনা করা হয়নি।
- Proposition-এর Y (implementation behaviour) আসল code-এ যাচাই করা হয়েছে (grep ও sed দিয়ে নির্দিষ্ট item path-এ)। সব 21টি item-এ Y পাওয়া গেছে, তাই কোনোটিকে "Y মেলেনি" বলে UNCLEAR করা হয়নি।
- `divergence_kind`: explicit guard/mapping/route/serialization থাকলে DELIBERATE; omission, unchecked exception, framework default, inverted/ভুল condition হলে ACCIDENTAL।
- `contract_specificity`: operation-specific prose/default/status/schema থাকলে SPECIFIC; shared schema/parameter, বা silence হলে GENERIC।

## কঠিন items
- V19: impl-এ শুধু CorsHandler rootHandler আছে, কোনো body handler নেই (ACCIDENTAL/omission)। কিন্তু Vert.x RouterBuilder নিজে default body handler যোগ করে কি না এই artifacts থেকে নিশ্চিত হওয়া যায় না; confidence 2।
- W03/W12: `trim().isEmpty()` explicit branch, কিন্তু logic উল্টো (override শুধু empty হলে); oversight ধরে ACCIDENTAL, confidence 2।
- X55: একই ConsumerRecord schema binary ও JSON দুই format-এ ব্যবহৃত, JSON example-এ object আছে; SPECIFIC বনাম GENERIC অনিশ্চিত, confidence 1।
- W06/X12/W10: contract annotation সম্ভবত copy-paste ভুল; Y সবই explicit code, তাই DELIBERATE।
- W18/W11: contract shared parameter/schema, তাই GENERIC।
- V17: shared `ErrorResponse` component, তাই GENERIC।

## Limitations
- কোনো code execute/compile করা হয়নি; framework default আচরণ (Vert.x, Javalin) অনুমানভিত্তিক হতে পারে।
- সঠিক/ভুল artifact বিচার করা হয়নি।

## Boundary incidents
- নেই। শুধু TASK_CODE.md, ../../../09_collab/PROTOCOL.md (প্রথম 50 লাইন) ও item directories পড়া হয়েছে। প্রথম `find` listing-এ item ফাইলের নাম (codes_K1* বাদ দিয়ে) দেখা হয়েছে, বিষয়বস্তু নয়।
