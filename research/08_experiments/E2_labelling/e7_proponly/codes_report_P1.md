# P1 blind coding প্রতিবেদন

## পদ্ধতি

`TASK_CODE.md`-এর “What you code” ও “Output” নির্দেশনা অনুসারে শুধু `items.csv`-এর proposition থেকে `divergence_kind` ও `contract_specificity` নির্ধারণ করেছি। `../../../09_collab/PROTOCOL.md` পড়েছি; এই task-এর supervisor override অনুযায়ী board বা coordinator task পড়িনি। কোনো source অনুসন্ধান বা network ব্যবহার করিনি। প্রতিটি CSV rationale-এ সংশ্লিষ্ট `items.csv` row ID এবং inference চিহ্ন ⚠️ আছে।

⚠️ স্পষ্ট validation declaration, route, response construction ও data-model choice-কে DE­LIBERATE ধরেছি; omission, null handling failure, ordering এবং ভুল parameter lookup-কে ACCIDENTAL ধরেছি। উদাহরণ: `items.csv` X01, X07, X34, X14 বনাম X06, X20, X54, X67। DE­LIBERATE বলতে developer-এর সচেতন contract-বিরোধী অভিপ্রায় বোঝানো হয়নি; proposition-এ আচরণটি স্পষ্ট code choice থেকে এসেছে কি না সেটিই বিচার্য (`TASK_CODE.md`, “1. divergence_kind”)।

⚠️ Contract-এর স্পষ্ট status, media type, default, route, field name/type বা operation-specific শর্তকে SPECIFIC ধরেছি। কোনো named schema ব্যবহৃত হলেই সেটি shared বা generator-produced ধরে নিইনি; proposition-এ তার উৎস প্রায়ই নেই। অনুপস্থিত operation/required declaration-কে GENERIC ধরেছি (`items.csv` X09, X33, X01, X51, X53, X65)। শুধু “optional” বলা ক্ষেত্রে declaration-এর উৎস অনির্দিষ্ট হওয়ায় provisional GENERIC ও confidence 1 দিয়েছি (`items.csv` X13, X40, X58)।

## কঠিন item

- ⚠️ X15: `java.util.Date` একটি স্পষ্ট model choice হলেও epoch milliseconds-এর জন্য আলাদা serialization configuration বলা নেই। Framework default-এর সম্ভাবনায় ACCIDENTAL; confidence 1 (`items.csv` X15)।
- ⚠️ X25: duplicate append ও 201 থেকে dedicated duplicate-success branch প্রমাণিত নয়। অনুপস্থিত existence handling-এর সম্ভাবনায় ACCIDENTAL; confidence 2 (`items.csv` X25)।
- ⚠️ X29: enum conversion-এর `IllegalArgumentException` বলা আছে; exception mapping বা শেষ HTTP status নেই। সেই সীমার মধ্যে ACCIDENTAL; confidence 1 (`items.csv` X29)।
- ⚠️ X36: `DeferredResultResponseEntityTan` নামটি framework wrapper-এর generated schema হওয়ার ইঙ্গিত দেয়; provenance নিশ্চিত নয়। GENERIC; confidence 1 (`items.csv` X36)।
- ⚠️ X49: `payment_id` naming choice ধরে DE­LIBERATE করেছি; annotation নাকি serialization default, তা proposition বলে না। Confidence 2 (`items.csv` X49)।
- ⚠️ X50: explicit null emission থেকে DE­LIBERATE; contract-এর non-nullability schema default হওয়ার সম্ভাবনায় GENERIC। উৎস অনির্দিষ্ট হওয়ায় confidence 1 (`items.csv` X50)।
- ⚠️ X52: line feed গ্রহণের পেছনে dedicated rule বলা নেই। Validation oversight ধরে ACCIDENTAL; নির্দিষ্ট regex বা mechanism অনুমান করিনি। Confidence 1 (`items.csv` X52)।
- ⚠️ X57: literal false একটি স্পষ্ট argument হলেও dryRun propagation বাদ পড়ার সম্ভাবনায় ACCIDENTAL করেছি। Persistence সচেতনভাবে লক্ষ্য ছিল কি না অনির্দিষ্ট; confidence 2 (`items.csv` X57)।

## সীমাবদ্ধতা ও খোলা প্রশ্ন

⚠️ এই codes proposition-ভিত্তিক inference; implementation execution, source inspection বা contract provenance verification নয়। বিশেষত schema generation, optionality-এর declaration এবং serialization configuration অনির্দিষ্ট থাকলে একই বর্ণনার বিকল্প ব্যাখ্যা সম্ভব (`items.csv` X13, X15, X36, X49, X50)। কোনো artifact-কে সঠিক বা ভুল বলে রায় দিইনি।

⚠️ Confidence 3 স্পষ্ট textual basis; 2 কিছু interpretation; 1 দুর্বল provenance বা intent evidence বোঝায়। এটি দুই field-এর সম্মিলিত confidence; probability বা inter-rater agreement নয়। UNCLEAR ব্যবহার করিনি, কারণ প্রতিটি proposition-এ অন্তত একটি বিচারযোগ্য ইঙ্গিত আছে (`TASK_CODE.md`, “Use UNCLEAR only…”; `items.csv` X01–X70)।

আউটপুট: `codes_P1.csv` ও এই `codes_report_P1.md`। পুনর্বিচারের প্রধান খোলা প্রশ্ন হলো X15-এর serialization configuration, X36/X50-এর schema provenance, X25-এর duplicate handling এবং X57-এর flag propagation—এই blind task-এর সীমার মধ্যে সেগুলোর উত্তর অনুসন্ধান করা হয়নি (`items.csv` X15, X25, X36, X50, X57)।
