# K4 কোডিং রিপোর্ট (e12_kb1)

## Method
- TASK_CODE.md এবং PROTOCOL.md পড়া হয়েছে; শুধু প্রতিটি item-এর নিজস্ব `contract/` ও `impl/` ডিরেক্টরি explicit path দিয়ে grep/sed করা হয়েছে। কোনো কোড execute করা হয়নি; item-এর মধ্যে তুলনা করা হয়নি।
- প্রতিটি proposition-এর Y (implementation behaviour) ফাইলে যাচাই করা হয়েছে, তারপর `divergence_kind` ও `contract_specificity` কোড করা হয়েছে। মোট 18 row (U01-U18)।

## Difficult items
- U01: contract-এ NewConnection.connectionStatus explicit `$ref` ConnectionStatus (object), যদিও সম্ভবত ConnectivityStatus উদ্দেশ্য ছিল। specificity SPECIFIC ধরা হয়েছে (explicit $ref), confidence 2।
- U09/U13/U15: enum-সংক্রান্ত। U09/U13-এ "excludes mqtt-5" আসলে silence, তাই GENERIC; U15-এ explicit দুই-মানের enum আছে (সম্ভবত stale generated output), তাই SPECIFIC কিন্তু confidence কম।
- U06/U07/U05/U16/U12: contract-এর scoping/path variable class-level বা sub-resource path structure থেকে আসে, operation-specific statement নেই, তাই GENERIC।
- U08: contract prose ("launches") explicit কিন্তু copy-paste-এর মতো; impl স্পষ্টভাবে users delete করে, তাই DELIBERATE।
- U18: impl-এ আলাদা একটি সম্ভাব্য slip (dockstore token-এর জন্য quay DAO call) আছে, কিন্তু proposition-এর Y শুধু List<Token> return; সেটাই কোড করা হয়েছে।
- U10/U18: contract ও impl একই ফাইল; `response = Token.class` explicit annotation ধরা হয়েছে।

## Limitations
- ACCIDENTAL বনাম DELIBERATE সিদ্ধান্ত কোডের ধরন (omission, wrong variable, silent mapper drop) থেকে অনুমান; কোনো history/runtime data নেই।
- GENERIC/SPECIFIC-এর সীমারেখা enum ও path-prefix ক্ষেত্রে বিষয়ভিত্তিক।

## Boundary incidents
- কোনো ঘটনা নেই। directory-র বাইরে শুধু `../../../09_collab/PROTOCOL.md` পড়া হয়েছে। (credential-সদৃশ মান কোথাও পুনর্মুদ্রণ করা হয়নি।)
