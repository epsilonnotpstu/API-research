# E5 blind labelling v2 — pre-registration (Claude, 2026-11-14; লেবেলিং শুরুর আগে লেখা)

## পরিবর্তন (v1-এর তুলনায়)
1. **উদাহরণ exchange** (`build_e5_blind.py --example-rule discriminating`):
   - প্রতিটি item-এর উদাহরণ transport-এর দিক থেকে পরিষ্কার (path, query বা header-এ control byte নেই)।
   - INCREASED item-এর উদাহরণ এমন request, যেটা control-এ ওই fingerprint ছাড়া উত্তর পেয়েছে (`SAME_REQ_DIFF_OUTCOME`), অথবা control-এ ছিলই না (`NOVEL_REQ`)।
   - যে request control-এও একই violation দিয়েছে, তা কখনো বাছা হয় না (E005-এর সংশোধন)।
   - `--example-rule first` দিলে v1 package হুবহু তৈরি হয় (যাচাই করা হয়েছে: items.csv আর key byte-সমান)।
2. **Codebook v0.5:** labeller-রা পায় `CODEBOOK_v0.5.md`। এতে §11.1–11.2 আছে, কিন্তু §11-এর উৎস-লাইন, H8 আর 11.3 বাদ (blinding)। §§1–10 অপরিবর্তিত।
3. **নতুন labeller C1, C2:** নতুন Codex session, v1 package আর label পড়া নিষিদ্ধ। নতুন salt দিয়ে item ID আর package নাম আবার এলোমেলো করা হয়েছে।
4. **চাবি:** `blind_key_v2.csv`। Item set v1-এর সমান (একই fingerprint নির্বাচন)।

## মূল্যায়ন (আগে থেকে নির্ধারিত)
- **Primary set (n=9)**, `stratum=primary`: এমন target যার kind manifest-এর প্রত্যাশিত signal-এর মধ্যে পড়ে, এবং যেকোনো একটি:
  - (NEW fingerprint আর `signal_exceeds_noise=True`), অথবা
  - `SAME_REQ_DIFF_OUTCOME` উদাহরণ।
  - Item: E009, E013, E015, E016, E019, E021, E023, E024, E025।
- **v1-তুলনীয় set (n=10):** primary + E014 (v1-এর E005-এর উত্তরসূরি; noise ছাড়ায় না, উদাহরণ `NOVEL_REQ`)।
- **মাপ:**
  - (a) IMPL* (IMPL/IMPL_PARTIAL)-এর হার;
  - (b) **ভুল দিকে attribution** (SPEC/SPEC_PARTIAL/TEST)-এর হার;
  - (c) UNDECIDABLE-এর হার (বিরত থাকা), আর তার মধ্যে `both_candidate=true`।
  - v0.5-এ intent-দেখতে fault-এর (WRONG_STATUS E019/E021, RESP_FIELD E023/E024) "সঠিক" ফল IMPL অথবা UNDECIDABLE+both। **সাফল্য = (b) কমে যাওয়া।**
- **Operator অনুযায়ী v1 বনাম v2:** v1 B1/B2 বনাম v2 C1/C2, একই fingerprint-এ মিলিয়ে (`fingerprint` + `pair` + `seed`)।
- Decoy শুধু blinding-এর জন্য; ground truth নেই, মূল্যায়নে নয়।

## সীমা
- একই model family; একটি package নকশা; n ছোট।
- **উদাহরণ বদলেছে মাত্র 2/29 item-এ:** E005→E014 আর E022→E028, দুটোই `NOVEL_REQ`। বাকি 27টির উদাহরণ v1-এর সাথে হুবহু এক (যাচাই করা)। তাই primary set-এ v1 বনাম v2-এর পার্থক্য আসবে শুধু codebook আর labeller session থেকে।
- E014-এর উদাহরণ হলো int64-এর সীমা ছাড়ানো `petId`-এ 400। Checker int64 format যাচাই করে না, তাই এটা VALID_REJECTED হিসেবে এসেছে। Mutation-এর প্রভাব নয় [H]। এ কারণেই E014 primary-তে নেই।
