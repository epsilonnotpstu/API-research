# P3: blind proposition-only coding প্রতিবেদন

## পদ্ধতি

`items.csv`-এর ৩৭টি proposition থেকে শুধু X ও Y-এর বর্ণনা ব্যবহার করে coding করেছি; source খোঁজা বা network ব্যবহার করিনি। সব item মূল ক্রমে `codes_P3.csv`-এ আছে। প্রতিটি rationale-তে সংশ্লিষ্ট `items.csv` row id এবং inference চিহ্ন ⚠️ দেওয়া হয়েছে। উৎস: `items.csv`, W01–W41-এর উপস্থিত row-গুলি; `codes_P3.csv`, একই row id-গুলি।

`DELIBERATE` বলতে Y ঘটানোর explicit code choice বোঝানো হয়েছে; contract থেকে বিচ্যুত হওয়ার সচেতন ইচ্ছা ধরে নেওয়া হয়নি। explicit scope, parameter name, fallback, permission annotation ও exception নির্বাচনকে সেইভাবে পড়েছি; omission এবং অনির্দিষ্ট default-এর ফলকে `ACCIDENTAL` হিসেবে বিচার করেছি। সংজ্ঞার উৎস: `TASK_CODE.md:11`; প্রয়োগের উদাহরণ: `items.csv`, W08, W15, W20, W39, W16, W11, W04।

`SPECIFIC` নির্বাচনে explicit default, dedicated example, operation response structure, status বা requirement ব্যবহার করেছি। bare scalar field/response typing-কে ⚠️ schema-ভিত্তিক `GENERIC` হিসেবে অনুমান করেছি; schema কোথা থেকে এসেছে তা proposition-এ নেই বলে confidence কমিয়েছি। সংজ্ঞার উৎস: `TASK_CODE.md:29`; প্রয়োগ: `items.csv`, W01, W19, W06, W32, W13, W22, W25, W37। confidence একটি row-এর দুই coding-এর যৌথ নিশ্চয়তা; যে dimension বেশি অনিশ্চিত, সেটিই confidence কমিয়েছে (`codes_P3.csv`, W13, W25, W37)।

## ফলাফল ও যাচাই

| ক্ষেত্র | coding | সংখ্যা |
|---|---|---:|
| divergence_kind | DELIBERATE | 25 |
| divergence_kind | ACCIDENTAL | 12 |
| divergence_kind | UNCLEAR | 0 |
| contract_specificity | SPECIFIC | 33 |
| contract_specificity | GENERIC | 4 |
| contract_specificity | UNCLEAR | 0 |
| confidence | 1 | 3 |
| confidence | 2 | 18 |
| confidence | 3 | 16 |

সংখ্যার উৎস: `codes_P3.csv`, W01–W41-এর উপস্থিত ৩৭টি row। CSV পুনরায় পড়ে header, মূল item order, unique id, অনুমোদিত label, confidence এবং প্রতিটি rationale-এর সর্বোচ্চ ৩০ শব্দ যাচাই করেছি; সব শর্ত পূরণ হয়েছে। যাচাইযোগ্য artifact: `items.csv` ও `codes_P3.csv`, একই ৩৭টি row id; শর্ত: `TASK_CODE.md:37`।

## কঠিন item

- ⚠️ W23-এ `dryRun=false` literal flag সরাসরি persistence নির্বাচন করছে ধরে `DELIBERATE`, confidence 2 দিয়েছি। caller-এর flag ভুল করে বাদ পড়েছে কি না জানা যায় না; programmer-এর উদ্দেশ্য অনুমান করিনি (`items.csv:W23`; `codes_P3.csv:W23`)।
- ⚠️ W18-এ body id দিয়ে path id উপেক্ষাকে wrong-variable selection হিসেবে `ACCIDENTAL`, confidence 2 দিয়েছি। বিকল্প নকশার প্রমাণ নেই; W11-এর labels বাদ পড়া আরও সরাসরি omission (`items.csv:W18`, W11; `codes_P3.csv`, একই row id)।
- ⚠️ W19, W28, W29-এ string parsing explicit হলেও array উপেক্ষা/missing/null ফলের জন্য dedicated handling বর্ণিত নেই। Y-এর এই array আচরণকে `ACCIDENTAL`, confidence 2 দিয়েছি। field-specific array illustration-কে `SPECIFIC` ধরেছি; illustration generated কি না অজানা (`items.csv`, W19, W28, W29; `codes_P3.csv`, একই row id)।
- ⚠️ W25 ও W37-এ serializer-এর array output project configuration দিয়ে বেছে নেওয়া কি না অজানা। unaddressed default এবং schema-level date type ধরে `ACCIDENTAL/GENERIC`, confidence 1 দিয়েছি (`items.csv`, W25, W37; `codes_P3.csv`, একই row id)।
- ⚠️ W13 ও W22-এর bare string typing-কে `GENERIC` বলা provenance-এর অনুমান। বিপরীতে named operation response এবং explicit array shape-কে `SPECIFIC` ধরেছি; shared/generated হওয়ার প্রমাণ পাওয়া যায়নি (`items.csv`, W13, W22, W02, W06, W09, W27; `codes_P3.csv`, একই row id)।
- ⚠️ W41-এর “maps to status 422” থেকে explicit status mapping অনুমান করেছি। mapping project code-এর নাকি framework-এর, তা বর্ণিত নেই; তাই `DELIBERATE/SPECIFIC`, confidence 2 (`items.csv:W41`; `codes_P3.csv:W41`)।

## সীমাবদ্ধতা ও খোলা প্রশ্ন

proposition-এ source, annotation, serializer configuration, schema provenance বা সম্পূর্ণ control flow নেই। ফলে code-targeting এবং contract specificity-এর কিছু সিদ্ধান্ত inference; বিশেষ করে W13, W18, W23, W25, W37, W41। এই uncertainty coding-এর confidence ও rationale-তে রাখা হয়েছে। কোনো artifact-কে সঠিক/ভুল ঘোষণা করিনি এবং code যাচাইয়ের দাবি করিনি। তথ্যসীমার উৎস: `TASK_CODE.md:6`; সংশ্লিষ্ট evidence: `items.csv` ও `codes_P3.csv`, উল্লিখিত row id-গুলি।

এগুলো unresolved evidence question; blind task-এর সীমা মেনে অতিরিক্ত source সংগ্রহ করিনি (`TASK_CODE.md:45`)। report সম্পূর্ণ; এ task-এর জন্য অতিরিক্ত input প্রয়োজন হয়নি (`codes_P3.csv`, সব ৩৭টি row)।
