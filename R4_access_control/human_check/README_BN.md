# R4 human spot-check (আপনার জন্য, ২০টি item)

**কী করবেন:**
- ফাইল: `r4_spotcheck.csv`।
- প্রতিটি item-এর folder খুলুন: `packages/r4_blind/Annn/`। ভেতরে আছে `item.md` (advisory), `diff.patch` (fix), `before/` আর `after/`, আর `contract/`।
- প্রতিটি ঘরের সংজ্ঞা `plan/TASK_R4.md`-এ আছে। Model coder-রাও ঠিক একই সংজ্ঞা দেখেছে।

**পূরণ করার ঘর:**
- `human_ac_relevant`: YES, NO বা UNCLEAR।
- নিচের ঘরগুলো শুধু YES হলে পূরণ করবেন:
  - `human_ac_kind`;
  - `human_principals_needed`;
  - `human_observable_via_http`;
  - `human_contract_operation`;
  - `human_contract_security`;
  - `human_policy_in_contract`;
  - `human_fix_location`।
- `notes` ঘরে নিজের ভাষায় এক লাইন লিখুন।
- সময় কম থাকলে অন্তত এই তিনটি ঘর পূরণ করুন: `human_ac_relevant`, `human_ac_kind`, `human_principals_needed`।

**সতর্কতা:**
- `plan/r4_spotcheck_model_codes.csv` খুলবেন না।
- এই sheet পূরণে কোনো LLM ব্যবহার করবেন না।

**বাছাই কীভাবে হয়েছে:**
- GPT যেগুলোকে access-control vulnerability বলেছে, সেগুলো থেকে ২০টি নেওয়া হয়েছে।
- প্রতিটি kind থেকে তার আনুপাতিক সংখ্যক item, seed দিয়ে বাছা হয়েছে।
- ক্রম এলোমেলো করা আছে।

**শেষ হলে:** আমাকে "R4 spot-check done" বলুন।
