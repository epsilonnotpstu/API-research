# T38 — Git history-এর repository boundary

`intent_evidence.py`-তে default history search এখন source tree-এর নিজস্ব repository-তে সীমাবদ্ধ। বাইরের enclosing repository পেলে `availability=unavailable`, `scope=unavailable`, reason `enclosing repository outside source_dir`; কোনো `git log` চলে না। `history.toplevel_inside_source` boolean-ও সব result-এ থাকে। বাস্তব temporary enclosing repository ও subprocess spy দিয়ে এই আচরণ যাচাই করা হয়েছে। প্রমাণ: `08_experiments/tools/intent_evidence.py:819-877`; `08_experiments/tools/test_intent_evidence.py:280-290,342-349`।

আগের `root` selection source-এর resolved path-ই ছিল; repository root-এ normalize করা হতো না। বর্তমান implementation-এও source scan-এর root অপরিবর্তিত। EMB layout-এর metadata check-এ Scout source directory পাওয়া গেছে, কিন্তু git toplevel হলো `08_experiments/_external/emb`; source-এর parent ceiling দিলে source থেকে probe exit 128, explicit EMB directory থেকে probe exit 0। এখানে source code/history content scan করা হয়নি। প্রমাণ: `08_experiments/tools/intent_evidence.py:540-550`; `09_collab/logs/T38_scratch/layout.json:1`।

`--history-root DIR` নতুন opt-in: resolved directory-টি source-এর ancestor অথবা source নিজে হতে হবে; নয়তো CLI exit 2, git subprocess চালানোর আগেই। বাইরের history অনুমোদনের জন্য probed git toplevel-কে ঠিক ওই directory-র সমান হতে হয়। বাইরের অনুমোদিত repository-তে `scope=explicit_root`, source-এর ভেতরের repository-তে `scope=own_repo`। Explicit root থেকে `git log` চালানোর সময় source file-এর repository-relative prefix রাখা হয়। প্রমাণ: `08_experiments/tools/intent_evidence.py:540-550,835-854,904-905,918-921`; `08_experiments/tools/test_intent_evidence.py:301-333`।

প্রতিটি git subprocess-এর `GIT_CEILING_DIRECTORIES` source-এর parent-এ set করা হয়েছে। Explicit opt-in-এ git-এর working directory সেই অনুমোদিত root; ceiling একই থাকে। Inherited `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR`, `GIT_INDEX_FILE` বাদ দেওয়া হয়। Ceiling-এর কারণে discovery বন্ধ হলে শুধু ancestor `.git` metadata-র existence দেখে enclosing-repository reason দেওয়া হয়; parent repository-তে fallback git query করা হয় না। প্রমাণ: `08_experiments/tools/intent_evidence.py:822-838,867-873`; `08_experiments/tools/test_intent_evidence.py:280-290,301-315`।

T33/T36 invocation migration: আগের source/spec/method/path/status/field arguments রেখে **`--history-root 08_experiments/_external/emb`** যোগ করতে হবে, research directory থেকে চালালে। অন্য working directory হলে EMB-এর absolute path দিতে হবে। T33-এর `command` list-এ এটি `['--history-root', str(EMB)]`; T36-এর `argv`-তে একই repository path যোগ হবে। এই task-এ পুরোনো reports, scripts বা saved results বদলানো হয়নি। আগের invocation-এর প্রমাণ: `09_collab/logs/T33_scratch/verify_examples.py:10-16,41-45`; `09_collab/logs/T36_scratch/run_searches.py:42-45`। উদাহরণ, ভবিষ্যতে EMB history রাখতে:

```sh
/usr/bin/python3 -I -B 08_experiments/tools/intent_evidence.py \
  08_experiments/_external/emb/jdk_8_maven/cs/rest/original/scout-api \
  08_experiments/_external/emb/openapi-swagger/scout-api.json \
  --method GET --path /v1/system/roles --status 418 \
  --history-root 08_experiments/_external/emb --json
```

Verification: `/usr/bin/python3 -I -B 08_experiments/tools/test_intent_evidence.py` — **59 tests PASS**, zero failures/skips। Existing tests-সহ নতুন coverage: enclosing repo/no-log, own repo/history hit, explicit ancestor CLI/history hit ও সঠিক pathspec, invalid ancestor/exit 2, exact-root mismatch/no-log, missing git executable, এবং outside-toplevel mock/no-log। Git-শূন্য source-এর পুরোনো test-ও pass। প্রমাণ: `09_collab/logs/T38_scratch/tests.txt:1-8`; `08_experiments/tools/test_intent_evidence.py:115-117,263-349`।

সীমা: nested repositories খুঁজতে আলাদা recursive git discovery যোগ হয়নি; probe নির্ধারিত source বা explicit directory থেকেই হয়। Git pickaxe আগের মতোই candidate evidence, intent-এর নিশ্চয়তা নয়। প্রমাণ: `08_experiments/tools/intent_evidence.py:822-835,861-864`। Actual EMB history search পুনরায় চালানো হয়নি; metadata probe এবং committed synthetic fixtures দিয়ে boundary/pathspec যাচাই করা হয়েছে (`09_collab/logs/T38_scratch/layout.json:1`; `08_experiments/tools/test_intent_evidence.py:263-315`)। Open question নেই; পুরোনো EMB invocations ভবিষ্যতে পুনরায় চালালে উপরের opt-in প্রয়োজন।

Execution: নিজস্ব Python tests ও local git fixture/metadata commands ছাড়া কোনো external project code, Docker/Java/Maven বা network চালানো হয়নি। Blind package/labels, E5, harness, runs এবং অন্য tools edit করা হয়নি; write scope হলো `09_collab/tasks/T38.md:46-56`।
