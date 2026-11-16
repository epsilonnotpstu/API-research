# P4: proposition-only coding

`TASK_CODE.md`-এর নির্দেশ অনুযায়ী `items.csv`-এর W01–W41 proposition থেকে `codes_P4.csv` তৈরি করা হয়েছে। Evidence হিসেবে প্রতিটি rationale-এ সংশ্লিষ্ট row ID দেওয়া হয়েছে। Labels এবং ব্যাখ্যাগুলো proposition থেকে করা inference; তাই rationale-এ ⚠️ ব্যবহার করা হয়েছে। কোনো artifact সঠিক বা ভুল—এমন সিদ্ধান্ত দেওয়া হয়নি। নির্দেশের ভিত্তি: `TASK_CODE.md`, “What you code”, “Output” ও “Rules” অংশ।

## পদ্ধতি

⚠️ Explicit guard, configured default, parameter binding, response construction, field type ও parsing choice যে আচরণ সরাসরি তৈরি করে, সেটিকে DELIBERATE ধরা হয়েছে। এটি developer-এর মানসিক উদ্দেশ্যের দাবি নয়। Missing validation, missing termination, উপেক্ষিত identifier ও default handling-এর omission-কে ACCIDENTAL ধরা হয়েছে। যেমন W03/W12-এর empty-value guard সরাসরি Y নির্বাচন করে; W20/W30/W35-এ response লেখার পরে execution চলতে থাকা missing termination নির্দেশ করে। Evidence: `TASK_CODE.md`, “divergence_kind”; `items.csv`, W03, W12, W20, W30, W35।

⚠️ Explicit default, required scope, allowed range, status এবং operation-এর নির্দিষ্ট response declaration-কে SPECIFIC ধরা হয়েছে। Named model-এর field type, schema example এবং route nesting থেকে অনুমিত containment-কে GENERIC ধরা হয়েছে যখন আলাদা operation-specific বক্তব্যের প্রমাণ নেই। Proposition schema-র provenance নিশ্চিত করে না; এই পার্থক্য judgment হিসেবে প্রয়োগ করা হয়েছে। Evidence: `TASK_CODE.md`, “contract_specificity”; `items.csv`, W01, W02, W05, W17, W19, W22, W25, W26।

## কঠিন item ও সিদ্ধান্ত

- ⚠️ W03/W12: empty-value condition আপাতভাবে অপ্রত্যাশিত হলেও explicit branch Y তৈরি করে; তাই DELIBERATE। Evidence: `items.csv`, W03, W12।
- ⚠️ W11: কেবল name ও description copy করার মধ্যে field selection এবং অন্য field বাদ পড়া—দুই পাঠ সম্ভব। এখানে labels/properties update বাদ পড়াকে omission ধরে ACCIDENTAL; EditableMetaData-ভিত্তিক contract-কে GENERIC ধরা হয়েছে। Confidence 2। Evidence: `items.csv`, W11।
- ⚠️ W18: body identifier দিয়ে update করা explicit হলেও path identifier উপেক্ষা করা wrong-variable ধরনের oversight হিসেবে ACCIDENTAL। Intent সম্পর্কে অতিরিক্ত প্রমাণ নেই; confidence 2। Evidence: `items.csv`, W18।
- ⚠️ W24 বনাম W31/W40: W24-এ absent bound অনুযায়ী predicate বন্ধ করার শর্ত Y সরাসরি নির্বাচন করে। W31/W40-এ বর্ণিত সমস্যা allowed-set check-এর অনুপস্থিতি। তাই যথাক্রমে DELIBERATE এবং ACCIDENTAL। Evidence: `items.csv`, W24, W31, W40।
- ⚠️ W25/W37: LocalDate-এর array output framework serializer default-এর ফল হতে পারে। Explicit serializer configuration-এর তথ্য না থাকায় ACCIDENTAL, confidence 1। এটি সবচেয়ে অনিশ্চিত mechanism inference। Evidence: `items.csv`, W25, W37।
- ⚠️ W07/W19/W22/W28/W29: property naming বা type/example-এর contract evidence schema-ভিত্তিক হিসেবে GENERIC ধরা হয়েছে; shared বা inherited হওয়ার সরাসরি প্রমাণ নেই। Confidence 2। Evidence: `items.csv`, W07, W19, W22, W28, W29।
- ⚠️ W02/W06/W09/W10/W27: proposition operation-এর response representation নির্দিষ্টভাবে বর্ণনা করায় SPECIFIC ধরা হয়েছে। শুধু shared schema reference হলে classification বদলাতে পারে। Evidence: `items.csv`, W02, W06, W09, W10, W27।
- ⚠️ W26/W38/W39: route nesting-কে dedicated ownership constraint-এর প্রমাণ ধরা হয়নি; তাই GENERIC। Selected parent matching বাদ যাওয়াকে ACCIDENTAL ধরা হয়েছে। Confidence 2। Evidence: `items.csv`, W26, W38, W39।
- ⚠️ W23/W41: 409-এর explicit failure declaration SPECIFIC-এর ভিত্তি; শুধু 422 অনুল্লিখিত থাকা নয়। Mapping সরাসরি 422 নির্বাচন করে বলে DELIBERATE। Confidence 2। Evidence: `items.csv`, W23, W41।

## ফলাফল ও যাচাই

মোট ৪১টি row: DELIBERATE ২৬টি, ACCIDENTAL ১৫টি; SPECIFIC ৩০টি, GENERIC ১১টি। Confidence 3 পেয়েছে ২২টি, 2 পেয়েছে ১৭টি এবং 1 পেয়েছে ২টি। Evidence: `codes_P4.csv`, W01–W41।

স্থানীয় Python standard library দিয়ে CSV header, input-এর সঙ্গে row order, label ও confidence-এর অনুমোদিত মান, প্রতিটি rationale-এর সর্বোচ্চ ৩০ শব্দ, row citation এবং report-এর উপস্থিতি যাচাই করা হয়েছে; সব check পাস করেছে। Evidence: `items.csv`, W01–W41; `codes_P4.csv`, header ও W01–W41; `codes_report_P4.md`। এই check classification-এর substantive সত্যতা যাচাই করে না।

## সীমাবদ্ধতা ও খোলা প্রশ্ন

এই reading-এর evidence কেবল `items.csv`-এর proposition; source implementation, মূল contract, serializer configuration ও schema provenance যাচাই করা হয়নি। এটি task-এর নির্ধারিত সীমা। Evidence: `TASK_CODE.md`, “What you are given” ও “Rules”।

⚠️ একই confidence দুই axis-এর সামগ্রিক নিশ্চয়তা প্রকাশ করে; তুলনামূলক দুর্বল axis-কে গুরুত্ব দেওয়া হয়েছে। সব row-এ সিদ্ধান্তের কিছু basis থাকায় UNCLEAR ব্যবহার করা হয়নি। Evidence: `TASK_CODE.md`, “Use UNCLEAR only…”; `codes_P4.csv`, W01–W41।

⚠️ খোলা প্রশ্ন হলো schema-ভিত্তিক বক্তব্যগুলো shared definition থেকে এসেছে কি না এবং W25/W37-এর array output explicit configuration দ্বারা নির্বাচিত কি না। Proposition-only সীমার মধ্যে এগুলো নিষ্পত্তি করা যায় না। Evidence: `items.csv`, W07, W11, W19, W22, W25, W28, W29, W37।
