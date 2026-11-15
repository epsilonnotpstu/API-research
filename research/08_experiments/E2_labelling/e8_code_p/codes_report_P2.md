# P2: proposition-only coding প্রতিবেদন

## পদ্ধতি

`TASK_CODE.md`-এর “What you code”, “Output” ও “Rules” অনুসারে শুধু `items.csv`-এর proposition থেকে coding করা হয়েছে। অনুমোদিত `../../../09_collab/PROTOCOL.md` পড়া হয়েছে; source, coordinator task, `COLLAB_BOARD.md` বা network ব্যবহার করা হয়নি। প্রতিটি সিদ্ধান্তের evidence হিসেবে CSV rationale-এ `items.csv:<item_id>` এবং inference বোঝাতে ⚠️ দেওয়া হয়েছে। নির্দেশনার এই সীমার ভিত্তিতেই ফল পড়তে হবে।

⚠️ `DELIBERATE` বলতে আচরণটি লক্ষ্য করে লেখা code-এর textual ইঙ্গিত বোঝানো হয়েছে; developer-এর মানসিক উদ্দেশ্য বোঝানো হয়নি। Explicit mapping, validation, response construction, model/type বা conditional handling-কে সেই ইঙ্গিত হিসেবে ধরা হয়েছে। Null failure, অনুপস্থিত check, উপেক্ষিত parameter ও অনুপস্থিত header-কে `ACCIDENTAL` ধরা হয়েছে। উদাহরণ: `items.csv:X07,X10,X25,X34,X67,X69`।

⚠️ Explicit status, default, route বা operation constraint-কে `SPECIFIC` ধরা হয়েছে। Optionality-কে absent `required` flag-এর সম্ভাব্য প্রকাশ এবং character restriction-এর অনুপস্থিতিকে silence হিসেবে `GENERIC` ধরা হয়েছে। Optionality-এর উৎপত্তি proposition-এ নেই বলে সেই সিদ্ধান্তগুলির confidence 2; এগুলি নিশ্চিত schema provenance-এর দাবি নয়। Evidence: `items.csv:X01,X13,X21,X23,X40,X51,X53,X65`।

⚠️ শুধু named response model বা field type দেওয়া থাকলে সেটিকে explicit contract declaration হিসেবে `SPECIFIC` ধরা হয়েছে, সাধারণত confidence 1-সহ। এগুলি shared schema বা generator থেকে এসেছে—এমন evidence দেওয়া হয়নি। তাই সেগুলির dedicated হওয়ার অনিশ্চয়তা confidence-এ রাখা হয়েছে। Evidence: `items.csv:X03,X05,X08,X12,X24,X27,X30,X32,X36,X46,X47,X50,X62`।

## ফল ও যাচাই

`codes_P2.csv`-এ `items.csv`-এর একই ক্রমে 67টি item আছে। Coding-এর বিতরণ: `DELIBERATE` 52, `ACCIDENTAL` 15; `SPECIFIC` 58, `GENERIC` 9। Confidence 1/2/3 যথাক্রমে 20/26/21টি। এগুলি coding-এর সংখ্যা, source সম্পর্কে স্বাধীনভাবে যাচাইকৃত ফল নয়। Evidence: `items.csv` ও `codes_P2.csv`, সব item row।

CSV header, item completeness/order, allowed label, confidence range এবং সর্বোচ্চ 30-word rationale সীমা স্থানীয় validation-এ পরীক্ষা করা হয়েছে; দীর্ঘতম rationale 23 words। পুনরাবৃত্ত proposition জোড়াগুলির code, confidence ও rationale এক রাখা হয়েছে: `X26/X43`, `X28/X56`, `X38/X45`, `X50/X55`, `X59/X68`। Evidence: `codes_P2.csv`, সংশ্লিষ্ট item row।

## কঠিন item

- ⚠️ `X02`: supplied read-only value forward করা omitted protection-এর ইঙ্গিত; deliberate passthrough-ও সম্ভব। তাই `ACCIDENTAL`, confidence 2। Evidence: `items.csv:X02`; `codes_P2.csv:X02`।
- ⚠️ `X06`: current status-এ transition গ্রহণ করার পেছনে explicit branch নাকি missing rejection, তা বলা নেই। অনুমোদিত transition handling-এর সম্ভাবনা ধরে `DELIBERATE`, confidence 1। Evidence: `items.csv:X06`; `codes_P2.csv:X06`।
- ⚠️ `X09`: `/search`-এর implementation route explicit; contract statement অন্য identifier route নিয়ে। Undeclared operation-এর generic expectation হিসেবে confidence 1 দেওয়া হয়েছে। Evidence: `items.csv:X09`; `codes_P2.csv:X09`।
- ⚠️ `X35,X37,X39`: return status দেওয়া আছে, কিন্তু explicit construction নাকি framework default জানা নেই। নির্বাচিত status-এর ইঙ্গিত ধরে `DELIBERATE`, confidence 2। Evidence: উল্লিখিত `items.csv` ও `codes_P2.csv` row।
- ⚠️ `X44`: empty lookup-এ completion missing-case omission নাকি deliberate idempotence, নির্ধারণ করা যায় না। প্রথম ব্যাখ্যাটি ধরে `ACCIDENTAL`, confidence 2। Evidence: `items.csv:X44`; `codes_P2.csv:X44`।
- ⚠️ `X20,X60`-এ ভিন্ন query name পড়া wrong-parameter oversight হিসেবে ধরা হয়েছে। `X64`-এ numeric input-এর `value` নামটি model/naming choice-এর ইঙ্গিত হিসেবে `DELIBERATE`, confidence 1; wrong-name oversight-ও সম্ভব। Evidence: `items.csv:X20,X60,X64`; সংশ্লিষ্ট `codes_P2.csv` row।

## সীমাবদ্ধতা ও খোলা প্রশ্ন

এই কাজের evidence শুধু proposition; source, annotation, schema inheritance, framework configuration বা runtime response দেওয়া হয়নি (`TASK_CODE.md`, “What you are given”)। ফলে ⚠️ `DELIBERATE/ACCIDENTAL`-এর বহু সিদ্ধান্ত code mechanism-এর অনুমান, এবং `SPECIFIC/GENERIC`-এর কিছু সিদ্ধান্ত contract provenance-এর অনুমান। একটিমাত্র confidence field-এ দুই label-এর মিলিত অনিশ্চয়তা রাখা হয়েছে; দুর্বল সিদ্ধান্ত থাকলে confidence কমানো হয়েছে। Evidence: `codes_P2.csv:X03,X06,X09,X35,X44,X64`।

খোলা প্রশ্ন হলো explicit statement-এর উৎস এবং ambiguous acceptance/return behaviour-এর mechanism; blind task-এর সীমার মধ্যে এগুলি অনুসন্ধান করা হয়নি। কোনো artifact-কে সঠিক বা ভুল বলা হয়নি। সব item-এ কিছু textual basis থাকায় best judgement দেওয়া হয়েছে; `UNCLEAR` ব্যবহার করা হয়নি। Evidence: `TASK_CODE.md`, “What you code” ও “Rules”; `codes_P2.csv`, সব item row।
