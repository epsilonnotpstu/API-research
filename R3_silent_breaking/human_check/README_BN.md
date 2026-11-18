# R3 human spot-check (আপনার জন্য, ২০টি item)

**কী করবেন:**
1. ফাইল: `r3_spotcheck.csv`। প্রতি সারিতে একটি item আছে।
2. প্রতিটি item-এর folder (`packages/r3_blind/Bnnn/`) খুলুন। ভেতরে আছে `item.md`, `diff.patch`, before/after file আর contract।
3. কোন প্রশ্নের কী মানে, তার সংজ্ঞা `plan/TASK_R3.md`-এ আছে। Model coder-রাও ঠিক এই সংজ্ঞাই দেখেছে।
4. প্রতিটি item-এ তিনটি ঘর পূরণ করুন:
   - `human_observable_change`: `YES`, `NO` বা `UNCLEAR`। প্রশ্ন: HTTP client কি কোনো পার্থক্য দেখতে পাবে?
   - `human_client_impact`: `BREAKING`, `COMPATIBLE` বা `UNCLEAR`। প্রশ্ন: আগে ঠিকভাবে চলা কোনো client কি এখন ভাঙবে? আগের ঘরে `NO` লিখলে এটি ফাঁকা রাখুন।
   - `human_change_kind`: ঐচ্ছিক। `TASK_R3.md`-এর ১১টি category-র একটি লিখুন।
5. `notes` ঘরে নিজের ভাষায় এক লাইন লিখুন।

**সতর্কতা:**
- `plan/r3_spotcheck_model_codes.csv` খুলবেন না। সেখানে model-দের উত্তর আছে, শেষ করার পর আমি নিজে তুলনা করব।
- কোনো LLM দিয়ে এই sheet পূরণ করবেন না। এটা মানুষের যাচাই হিসেবেই paper-এ যাবে।

**বাছাই কীভাবে হয়েছে:** যে ৬০টি item-এ GPT coder "আচরণ বদলেছে" বলেছে, সেখান থেকে seed দিয়ে ২০টি বাছা হয়েছে, দুই ভাগে:
- ১০টি এমন item, যাকে GPT "breaking" বলেছে;
- ১০টি বাকি item থেকে।

ক্রম এলোমেলো করা আছে।

**শেষ হলে:** আমাকে "R3 spot-check done" বলুন।
