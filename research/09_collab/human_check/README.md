# Human spot-check: deliberate/accidental code (for the user)

**কেন:** R1-এর সব coder একই LLM family-র। Paper লেখার আগে মানুষের চোখে দেখা দরকার, model-এর kind code ঠিক কিনা।

**কী করবেন:**
1. `kind_spotcheck.csv`-এ ২০টি item আছে।
2. প্রতিটির `where_to_look` কলামের file:line খুলে proposition-এর "implementation does …" অংশটা মিলিয়ে দেখুন।
3. `your_kind` কলামে নিচের তিনটির একটি লিখুন:
   - **DELIBERATE:** আচরণটা project-এর code ইচ্ছা করেই তৈরি করে। যেমন:
     - স্পষ্ট guard বা validation;
     - স্পষ্ট status তৈরি করা;
     - নাম বা type বেছে নেওয়া;
     - আলাদা branch;
     - route ঘোষণা করা।
   - **ACCIDENTAL:** আচরণটা কোনো বাদ পড়া বা অসতর্কতার ফল। যেমন:
     - unhandled exception বা null;
     - হারিয়ে যাওয়া branch বা default;
     - header সেট না করা;
     - framework default;
     - ভুল ক্রম।
   - **UNCLEAR:** দেওয়া file দেখে বলা যায় না।
4. কোন পক্ষ "ঠিক", সেটা বিচার করবেন না। শুধু আচরণটা ইচ্ছাকৃত code থেকে এসেছে, না অসতর্কতা থেকে, সেটা দেখুন।
5. প্রতি item-এ ২–৪ মিনিট লাগার কথা।

**Blinding:**
- `08_experiments/E9_hybrid/spotcheck_model_codes.csv` ফাইলটি খুলবেন না। ওতে model-এর code আছে।
- Item কোন দিকে সারানো হয়েছে, সেটা এই sheet-এ নেই।

**পরে আমি যা করব:** আপনার code আর model-এর code-এর মধ্যে Cohen's κ বের করব। κ ≥ 0.6 হলে model-এর coding মানুষের সাথে সামঞ্জস্যপূর্ণ বলে report করব। কম হলে সেটাও সীমাবদ্ধতা হিসেবে লিখব।

Sheet freeze: `spotcheck_freeze.sha256`। Sampling: seed 20261116, ১০টি accidental + ১০টি deliberate (C1 = C2), ক্রম এলোমেলো করা।
