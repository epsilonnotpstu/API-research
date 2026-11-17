# K5 কোড রিপোর্ট (kb3, 19 items)

## Method
- প্রতিটি item শুধু নিজের `contract/` ও `impl/` থেকে পড়া হয়েছে; items-এর মধ্যে তুলনা করা হয়নি।
- Y (implementation behaviour) প্রথমে files-এ যাচাই করা হয়েছে, তারপর DELIBERATE/ACCIDENTAL বিচার (explicit guard, route, serializer, type choice বনাম omission, framework default, missing branch)।
- X (contract statement) dedicated prose/status/schema হলে SPECIFIC, boilerplate বা silence হলে GENERIC।
- কোনো item-এর source চালানো হয়নি; শুধু grep/sed এবং read-only python ব্যবহার।

## কঠিন items
- Q43: contract-এ শুধু shared `@PaginatedApi` annotation, তাই GENERIC; implementation-এ pagination বাদ পড়েছে (ACCIDENTAL)।
- Q45: callback-এ inherited-context read check নেই; কিন্তু `authorizeReadWriteParameterContext` এর ভেতরের অংশ দেখা যায়নি, তাই confidence 2।
- Q49: resolver-এর text/html explicit (DELIBERATE), কিন্তু handler-এর `produces=text/plain` copy-paste মনে হয়; দুই ব্যাখ্যাই সম্ভব।
- Q52/Q57: contract-এ `network` শুধু bare `type: string`, তাই SPECIFIC কিন্তু confidence 1।
- Q58, Q61: contract annotation নিজের summary/code-এর সাথে অসঙ্গত (copy-paste সম্ভাব্য), তবু code explicit তাই DELIBERATE।
- Q59: contract-এর 404 একই standard response ref, তাই GENERIC।
- Q47: contract-এর trailing slash হাতে লেখা `@Router` annotation থেকে; typo হতে পারে।

## Limitations
- Proposition-এর সব claim সরাসরি files-এ মিলেছে; কোনো item UNCLEAR করা হয়নি।
- সীমিত file সেট, তাই callee (যেমন Q45-এর helper) সব সময় দেখা যায়নি।

## Boundary incidents
- নেই।
