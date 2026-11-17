# K5 কোডিং রিপোর্ট (kb1, Q01-Q21)

## Method
প্রতিটি item আলাদাভাবে পড়া হয়েছে: proposition যাচাই করে impl-এর নির্দিষ্ট handler/mapper/router অংশ এবং contract-এর সংশ্লিষ্ট অংশ দেখা হয়েছে (targeted grep/sed, শুধু item path-এ)। কোনো source code execute বা compile করা হয়নি। কোনো item-এ proposition-এর Y মিথ্যা পাওয়া যায়নি, তাই UNCLEAR কোড করা হয়নি।

Rule: contract-এ X যদি absence/silence হয় (যেমন 409 নেই, maxLength নেই, security নেই, query param নেই) তাহলে GENERIC; generator default (Q13 required) এবং shared generated schema (Q19) ও GENERIC।

## Difficult items
- Q17: impl স্পষ্টভাবে ScanUploadEvent dispatch করে, কিন্তু contract-এর notes PUT BOM operation থেকে copy করা মনে হয়; তাই GENERIC, confidence 1।
- Q21: ClusteSummaryEntity একটি dedicated class (DELIBERATE), contract-এর response=ControllerStatusEntity স্পষ্ট হলেও copy-paste সন্দেহ আছে; SPECIFIC, confidence 2।
- Q10 ও Q04: error-to-status mapping-এ missing branch/missing status বলে ACCIDENTAL; তবে 500 typed response স্পষ্ট construction, তাই বিতর্কের জায়গা আছে (confidence 2)।
- Q12, Q14: দুটোই explicit branch/filter, তাই DELIBERATE; তবে ফলাফল (flagID 0, count mismatch) হয়তো অনভিপ্রেত। Confidence 2।
- Q03, Q07: contract-এ শুধু absence বলে GENERIC।

## Limitations
শুধু প্রদত্ত ফাইলের ভিত্তিতে বিচার; runtime ও history নেই। Developer-এর intent অনুমানভিত্তিক। Q09-এর swagger:parameters typo থেকে contract gap অনুমান করা।

## Boundary incidents
কোনো boundary incident নেই। শুধু items.csv, TASK_CODE.md, PROTOCOL.md (প্রথম ~50 লাইন) এবং item directory পড়া হয়েছে।
