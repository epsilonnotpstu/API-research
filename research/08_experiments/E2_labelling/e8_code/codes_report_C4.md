# C4: Blind code-structure coding

## পদ্ধতি ও ফল

`TASK_CODE.md` প্রথম command-এ পড়েছি; এরপর অনুমোদিত `../../../09_collab/PROTOCOL.md` পড়েছি। `TASK_CODE.md`-এর supervisor override অনুযায়ী board বা coordinator task পড়িনি। `items.csv`-এর প্রতিটি item নিজস্ব contract ও implementation দিয়ে স্বাধীনভাবে বিচার করেছি; item-এর মধ্যে source comparison করিনি।

⚠️ প্রতিটি classification হলো static structure থেকে inference; লেখকের মানসিক অভিপ্রায় বা কোন artifact সঠিক, তা বিচার করা হয়নি। `DELIBERATE` দিয়েছি যেখানে guard, branch, response construction, serialization বা model type সরাসরি Y তৈরি করে। `ACCIDENTAL` দিয়েছি missing handling, wrong parameter, parsing order ও header omission-এর ক্ষেত্রে। Contract-এর dedicated prose/default/status/constraint-কে `SPECIFIC`, shared schema, generated field type ও অনুল্লিখিত required flag-কে `GENERIC` ধরেছি। সংজ্ঞার ভিত্তি: `TASK_CODE.md`, “What you code” ও “Rules”।

`codes_C4.csv`-তে 67টি row `items.csv`-এর একই ক্রমে আছে। গণনা ওই CSV থেকেই:

| ক্ষেত্র | ফল | সংখ্যা |
|---|---|---:|
| divergence_kind | DELIBERATE | 53 |
| divergence_kind | ACCIDENTAL | 14 |
| divergence_kind | UNCLEAR | 0 |
| contract_specificity | SPECIFIC | 44 |
| contract_specificity | GENERIC | 23 |
| contract_specificity | UNCLEAR | 0 |
| confidence | 3 | 60 |
| confidence | 2 | 7 |
| confidence | 1 | 0 |

প্রতি row-তে implementation ও contract locator এবং সর্বোচ্চ 40 শব্দের rationale আছে। Inference বোঝাতে rationale-এ ⚠️ ব্যবহার করেছি।

## কঠিন সিদ্ধান্ত

- ⚠️ X05: একক property serialization সরাসরি নির্বাচিত, কিন্তু list expectation collection operation-এর সঙ্গে shared response schema থেকে এসেছে। তাই `DELIBERATE/GENERIC`, confidence 2। Evidence: `codes_C4.csv`, item_id=X05।
- ⚠️ X25: backend-এর list append-এ duplicate check নেই; contract-এর 409 wording repeated generic resource-conflict boilerplate। তাই `ACCIDENTAL/GENERIC`, confidence 2; supplied backend-এর বাইরের layer নিয়ে সিদ্ধান্ত দিইনি। Evidence: `codes_C4.csv`, item_id=X25।
- ⚠️ X28: archive streaming explicit; application/zip schema array বললেও একই contract-এর prose ZIP file বলেছে। লক্ষ্য করা schema statement-কে `SPECIFIC` রেখেছি, confidence 2। Evidence: `codes_C4.csv`, item_id=X28; `X28/contract/dockstore-webservice/src/main/resources/openapi3/openapi.yaml#39`।
- ⚠️ X31: documentation-এর `_links` annotation serializer rename নয়; getter-এর পাশে JSON override নেই। তাই omission হিসেবে `ACCIDENTAL`, confidence 2; global serializer configuration supplied নয়। Evidence: `codes_C4.csv`, item_id=X31।
- ⚠️ X36: asynchronous DeferredResult wrapper-এর generated properties-কে generic schema evidence ধরেছি; actual response construction Tan body নির্বাচন করেছে। Evidence: `codes_C4.csv`, item_id=X36।
- ⚠️ X44: `ifPresent` present-role deletion করে, empty lookup-এর error branch নেই। এটিকে omission হিসেবে `ACCIDENTAL`, confidence 2 দিয়েছি; structure থেকে idempotent-delete উদ্দেশ্য নিশ্চিত করা যায় না। Evidence: `codes_C4.csv`, item_id=X44।
- ⚠️ X56: ZIP streaming explicit হলেও schema ও prose পরস্পর আলাদা payload নির্দেশ করে; confidence 2। Evidence: `codes_C4.csv`, item_id=X56; `X56/contract/dockstore-webservice/src/main/resources/openapi3/openapi.yaml#39`।
- ⚠️ X59: parser ISO-code conversion বেছে নেয়; request schema-এর enum names-এর পাশেই ISO-code prose ও `en` example আছে। Generated enum representation ধরে `GENERIC`, confidence 2। Evidence: `codes_C4.csv`, item_id=X59।
- ⚠️ X67: sorting parameters গ্রহণ করলেও query তৈরিতে প্রয়োগ নেই; contract semantics shared parameter definition থেকে এসেছে। তাই `ACCIDENTAL/GENERIC`। Evidence: `codes_C4.csv`, item_id=X67।

## সীমাবদ্ধতা ও যাচাই

Runtime data, history, framework execution বা বাইরের dependency inspection ব্যবহার করিনি। Bean validation, JSON serialization ও response behavior সম্পর্কে সিদ্ধান্ত supplied source structure-এর মধ্যে সীমিত। `UNCLEAR` ব্যবহারের নিয়ম প্রয়োগ করে পর্যালোচনার পরে কোনো item-এ Y অপ্রমাণিত বলে স্থির করিনি; এটি runtime verification-এর দাবি নয়। Evidence: প্রতিটি সিদ্ধান্তের locator, `codes_C4.csv`।

নিজস্ব Python helper দিয়ে row count/order, enum values, confidence range, rationale word limit, locator file existence এবং line bounds যাচাই করেছি। Helper source: `codes_work_C4/write_outputs.py`; evidence validation: `codes_work_C4/validate_outputs.py`। কোনো item source compile বা execute করিনি; network, Docker, Java বা Maven ব্যবহার করিনি।

## Boundary incidents

কোনো accidental boundary access ঘটেনি। বর্তমান directory-এর বাইরে কেবল অনুমোদিত protocol পড়েছি। অন্য coder-এর output, COLLAB_BOARD বা coordinator task খুলি, list বা search করিনি। Source snippet ছাপার আগে attribution/credential-looking line redact করেছি; final output-এ এমন value নেই। Search প্রতিবার নির্দিষ্ট item path-এ সীমাবদ্ধ ছিল। Writes কেবল `codes_C4.csv`, `codes_report_C4.md` ও `codes_work_C4/`-এ করেছি। Audit-এর নিয়ম ও অনুমোদন: `TASK_CODE.md`, “Supervisor authorization” ও “Rules”; ব্যবহৃত redaction helper: `codes_work_C4/read.py`।
