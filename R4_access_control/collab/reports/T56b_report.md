# T56b: independent R4 mining pipeline

সাতটি deliverable লেখা হয়েছে: `mining/r4_common.py`, `r4_collect.py`, `r4_resolve.py`, `r4_pool.py`, `r4_sample.py`, `r4_build.py` এবং `test_r4.py`। Implementation Python 3 standard library ব্যবহার করে; privacy-র জন্য অনুমোদিত R3 module read-only import করা হয়েছে। বাস্তব advisory, repository cache বা package নিয়ে pipeline চালানো হয়নি। Network ব্যবহার করা হয়নি। Workspace repository-তে commit করা হয়নি; tests-এর git commits কেবল temporary synthetic repository-তে তৈরি হয়েছে।

## Design choices

- `run(cmd)` network command এবং lazy-fetch করতে পারে এমন git read command-এ সর্বোচ্চ তিনবার attempt করে; backoff ১ ও ২ সেকেন্ড। Subprocess stdout/stderr exception বা diagnostic-এ প্রকাশ করা হয় না। Collector কেবল count print করে।
- T50 contract rule, excluded directory segments, Java/Kotlin/Go source filter এবং test-path/name filter আলাদা helper। R3-এর annotation names-এর সঙ্গে নির্ধারিত security annotations union করা হয়েছে। শুধু added/removed hunk line গণনা করা হয়; diff header বা unchanged context নয়।
- Collector paginated JSON stream-এর প্রতিটি response page অক্ষত structured data হিসেবে cache করে। Normalized advisories GHSA id অনুযায়ী sorted; references-এর মূল order থাকে। Withdrawn advisory `WITHDRAWN` count-সহ `collect_inventory.json`-এ নথিভুক্ত হয় এবং normalized population থেকে বাদ যায়।
- Resolver source repository-র candidates আগে নেয়, বাকি reference order অক্ষুণ্ণ রাখে। API resolution-এর পরে bare partial repository-তে depth-two fetch হয়। First-parent lookup ব্যর্থ হলে refetch এবং raw commit header দিয়ে shallow-boundary ও প্রকৃত root commit আলাদা করা হয়। Commit header-এর message/author package-এ যায় না। Exhausted API/fetch failure `FETCH_ERROR`; এই failure লুকিয়ে পরের candidate নির্বাচন করা হয় না।
- Eligibility parent tree এবং NUL-delimited numstat ব্যবহার করে; rename, tab-সহ filename এবং deleted source সমর্থিত। Annotation measure-এর জন্য diff লাগে। Test file কেবল delete হলে `test_in_fix` true হয় না। Dedup key `(repo, fix_sha)`; lowest GHSA primary, সব GHSA ও CWE retained।
- Inventory-র unit স্পষ্ট করা আছে: প্রতিটি distinct advisory একবার counted হয়; `ELIGIBLE` deduplicated item বোঝায়, অতিরিক্ত merged advisory `DEDUP` হয়। Per-ecosystem এবং per-repository একই count breakdown থাকে; unresolved repository আলাদা bucket-এ থাকে।
- Pool freeze-এ নির্ধারিত চারটি JSON-এর পাশাপাশি দুই ecosystem-এর cached response pages-এর SHA-256 ও query parameters থাকে। Sampling freeze pool freeze-এর hash বহন করে। Downstream script hash যাচাই করে; existing output/freeze overwrite করে না। Canonical JSON sorted-key, UTF-8, LF।
- Pool size সর্বোচ্চ ১৬০ হলে সবাই selected হয়, repository cap তখন প্রয়োগ হয় না। বড় pool-এ নির্ধারিত repository seed দিয়ে সর্বোচ্চ চারটি, প্রয়োজন হলে নির্ধারিত global seed দিয়ে ১৬০টি selected হয়।
- Fresh 32-byte salt দিয়ে HMAC-SHA256 order থেকে `A001` ইত্যাদি id হয়। Salt এবং key আলাদা restricted-permission directory-তে থাকে। Source snapshots largest-change order-এ সর্বোচ্চ ২০টি; contract parent version-এর largest তিনটি, প্রত্যেকটি সর্বোচ্চ ৩,০০০ line। Contract index সব document ও original byte size দেখায়। Claude batches item-id order-এ ১৬টি করে, শেষ batch-এ অবশিষ্টগুলো।
- `TASK_R4.md` opaque bytes হিসেবে copy করা হয়; তার content পড়া বা বিশ্লেষণ করা হয়নি। Item, diff, snapshots এবং contracts-এ R3 privacy redaction চলে; পরিচিত credential prefixes ও raw PEM block-এর অতিরিক্ত protection আছে। Log-এ কেবল finding kind ও count থাকে, secret value থাকে না। Flattened filename collision হলে build বন্ধ হয়।

## Plan ও task-এর পার্থক্য; অনির্দিষ্ট ক্ষেত্রে সিদ্ধান্ত

- Plan §3 প্রাধান্য পেয়েছে: task-এর “first candidate that fetches” নয়, **first candidate that resolves through the API** fix হয়। Full SHA-ও API দিয়ে resolve হয়। Short SHA-র ক্ষেত্রে `--jq .sha` দিয়ে field আলাদা করার বদলে একই endpoint-এর JSON response থেকে `.sha` নেওয়া হয়। নির্বাচিত commit fetch না হলে অন্য fix বেছে না নিয়ে `FETCH_ERROR` লেখা হয়।
- Plan §6-এর annotation measure হিসাব করতে diff পড়তে হয়। তাই task-এর eligibility-তে “trees and numstat” কথাটির পাশাপাশি measure-এর জন্য diff command আছে। Parent contract/source/size eligibility advisory text বা diff-এর semantic judgement ব্যবহার করে না।
- ⚠️ Plan language tie-break নির্ধারণ করেনি। সমান extension count হলে lexical extension order ব্যবহার করা হয়েছে; যেমন Java/Kotlin tie-তে Java।
- ⚠️ একই GHSA দুই ecosystem query-তে এলে distinct advisory হিসেবে একবার গণনা হয়; lexical ecosystem order-এর প্রথম record scalar metadata দেয়। আলাদা GHSA একই fix-এ merge হলে lowest GHSA scalar metadata দেয় এবং CWE union থাকে। Plan এসব scalar merge detail নির্ধারণ করেনি।
- ⚠️ Binary source-এর numstat `-` হলে ২,০০০-line threshold নির্ণয় করা যায় না। নতুন exclusion reason বা শূন্য line অনুমান না করে pipeline freeze-এর আগে `BINARY_SOURCE_NUMSTAT` error-এ বন্ধ হয়। বাস্তবে এমন case এলে supervisor-এর documented সিদ্ধান্ত প্রয়োজন।

## Test results

চালানো command:

```text
/usr/bin/python3 -I -B mining/test_r4.py
```

শেষ verification-এ stdout/stderr `collab/logs/T56b_scratch/test_output.txt`-এ capture করা হয়েছে। Output tail:

```text
test_reject_duplicate_id (__main__.Sampling.test_reject_duplicate_id) ... ok
test_repository_cap_and_registered_seed (__main__.Sampling.test_repository_cap_and_registered_seed) ... ok
test_small_pool_keeps_all_without_cap (__main__.Sampling.test_small_pool_keeps_all_without_cap) ... ok

----------------------------------------------------------------------
Ran 56 tests in 1.732s

OK
```

Tests local `file://` origin ব্যবহার করে। `GIT_ALLOW_PROTOCOL=file` দিয়ে HTTP/SSH git transport বন্ধ থাকে; প্রতিটি `gh` call mocked। Synthetic artifacts নির্ধারিত scratch directory-র temporary subtree-তে তৈরি ও cleanup হয়। Coverage-এ সব eligibility reason, dedup, exact seeds ও cap, shallow-parent repair, API/fetch failure, malformed API response, parent-version contract, ২০-source limit, ১৬-item batches, secret scan, metadata omission, hash tampering ও প্রতিটি pipeline script-এর frozen-output refusal আছে।

প্রথম run-এ ৫০টির মধ্যে একটি test raw PEM redaction-এর ত্রুটি শনাক্ত করে: reused R3 helper raw PEM header-এর প্রথম `-`-কে diff prefix ধরে block চিনতে পারেনি। অতিরিক্ত block-redaction pass দিয়ে সংশোধন এবং পরবর্তী tests যোগ করার পরে শেষ run-এর ৫৬টিই pass করেছে।

## Risks

- ⚠️ বাস্তব GitHub API, rate limit, remote partial-clone/lazy-fetch behaviour এবং বড় repository performance এই offline task-এ যাচাই করা হয়নি। Supervisor-এর network-enabled run এবং independent implementation comparison এখনও প্রয়োজন।
- ⚠️ R3 privacy rules ইচ্ছাকৃতভাবে conservative; encoded value, hexadecimal text, date ও attribution মুছে যাওয়ায় কিছু বৈধ source/contract context-ও কমতে পারে। Finding counts overlapping pattern match ধারণ করতে পারে; এগুলো distinct secret count নয়।
- ⚠️ Known-prefix/credential-pattern scanner অজানা format-এর সব secret শনাক্ত করার নিশ্চয়তা দেয় না। কোনো detected token log-এ রাখা হয় না।
- ⚠️ Interrupted collection/build আংশিক output রেখে যেতে পারে। Exclusive-create guard তার উপর rerun করতে দেয় না; supervisor-কে partial output আলাদা করে পুনরায় চালাতে হবে। Frozen artifacts স্বয়ংক্রিয়ভাবে মুছে বা rewrite করা হয় না।
- বাস্তব pool/sample/package তৈরি করা হয়নি। নিষিদ্ধ implementation, scorer, real package, real cache ও coder-task content পড়া হয়নি।

T56b DONE 56 tests pass
