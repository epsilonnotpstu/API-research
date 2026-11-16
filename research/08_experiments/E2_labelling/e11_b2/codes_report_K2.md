# K2 blind coding report (batch e11_b2)

## Method
- প্রথমে TASK_CODE.md পড়েছি, তারপর শুধু PROTOCOL.md এবং প্রতিটি item-এর নিজস্ব `contract/` ও `impl/` directory পড়েছি।
- প্রতিটি item আলাদাভাবে judge করেছি; item-এর মধ্যে file compare করিনি।
- প্রথমে proposition-এর Y (implementation behaviour) আসলেই impl-এ আছে কি না যাচাই করেছি; সব item-এ Y পাওয়া গেছে, তাই কোনোটিতে `UNCLEAR` দিইনি।
- divergence_kind: explicit guard/status/type/route/naming = DELIBERATE; omission, wrong variable, missing branch = ACCIDENTAL।
- contract_specificity: operation-specific prose/status/schema/route = SPECIFIC; shared component, generated boilerplate = GENERIC।
- কোনো source execute বা compile করা হয়নি। Helper: `codes_work_K2/mk.py` (CSV তৈরি, `/usr/bin/python3 -I -B`)।

## Difficult items
- V34: `/content` suffix না থাকা omission নাকি intent তা artifacts থেকে স্পষ্ট নয়। `?references=REWRITE` শুধু content endpoint-এ অর্থবহ, তাই ACCIDENTAL দিয়েছি, confidence 1।
- X17: `requireNotNull` explicit guard, কিন্তু sibling handler `catch()` ব্যবহার করে; 400 mapping না থাকা omission ধরেছি (confidence 2)।
- X25: 409 contract-এ আছে, কিন্তু text generated boilerplate (ShortId wording) হওয়ায় GENERIC দিয়েছি; এটি debatable।
- V06: impl-এ constant explicit (DELIBERATE), কিন্তু এটি placeholder হতে পারে। Contract enum shared parameter-এ, তাই GENERIC (confidence 2 ও 1 সীমারেখা)।
- V22: contract-এর `action` enum শুধু device.yaml-এ; deviceEvent-এ `action` plain string। তাই X event-specific নয় (GENERIC)।
- V39: `accountService.find` null return করে কি না দেওয়া files-এ দেখা যায় না; inference হিসেবে ACCIDENTAL।
- X44 ও X46: contract-এর বক্তব্য (204+RoleEntity; nested map) সম্ভবত copy-paste/ভুল, কিন্তু task অনুযায়ী কোন artifact ঠিক তা judge করিনি; explicit declaration হিসেবে SPECIFIC।
- V23/V32/V38: impl ও contract file তিনটিতে byte-identical; তাই একই code দিয়েছি।
- W08/W36 একই impl/contract; একই code।

## Limitations
- শুধু given files; runtime বা version history নেই। Confidence কম যেখানে intent inference লাগে (V34, V06, X25)।

## Boundary incidents
- কোনো দুর্ঘটনাজনিত boundary access হয়নি। `items.csv` প্রথম listing-এ `find .` দিয়ে এই directory-র ভেতরের file name দেখা হয়েছে (codes_K1* বাদ দিয়ে filter করা হয়েছিল, কোনো codes_K1 file খোলা হয়নি)।
