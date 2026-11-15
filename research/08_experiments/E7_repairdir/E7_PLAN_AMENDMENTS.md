# E7 pre-registration amendment (mining শুরুর আগে)

`E7_PLAN.md` বদলানো হয়নি, তার freeze hash অপরিবর্তিত। এই file-এ mining শুরুর আগের পরিবর্তনগুলো লেখা।

## A1 (2026-11-15 21:30, Claude): repo set
- **কী বদলেছে:** তিনটি সবচেয়ে বড় repo বাদ — airflow, mattermost, openproject।
- **কেন:**
  - প্রথমে একটি একটি করে clone-এ গতি ছিল প্রায় 100 KB/s, আর মোট আকার প্রায় 6.6 GB।
  - সংশোধনী (21:29): পরে parallel clone-এ মোট গতি প্রায় 2.5 MB/s হয়েছে।
  - তবুও তিনটি বাদই থাকছে। কারণ এতে নতুন ভাষা আসত (Python, Ruby, TS), আর mining-এর পরিসর সীমিত রাখা দরকার।
- **নতুন set:** 12টি repo — sldt-digital-twin-registry, basyx-java-server-sdk, FAAAST-Service, kapua, apicurio-registry, nessie, polaris, ditto, kratos, hydra, harbor, gravitee-api-management।
- **প্রভাব:** popularity-র ভাগ এখনো সম্ভব, কারণ ≥500 star-এর repo আছে: nessie, polaris, apicurio, ditto, kratos, hydra, harbor।
- **Bias:** Hypothesis বা ফল দেখে এই সিদ্ধান্ত নেওয়া হয়নি। এর কারণ শুধু আকার।

## A2 (2026-11-15 22:50, Claude): mining বাড়ানো (coding শুরুর আগে)
- **অবস্থা:** T45-এ নতুন item মাত্র 16টি। Aggregate direction SPEC 8 / IMPL 7 / BOTH 1; Claude শুধু এই মোট সংখ্যা দেখেছেন। Primary-র প্রতি arm-এ ≥8 পাওয়ার সম্ভাবনা কম।
- **T45-এ retrieval-এর মান খারাপ ছিল:**
  - Pool-এ 20,199 candidate, কারণ path filter CI আর config YAML-ও ধরেছে।
  - 674টি rejection-এর সবগুলোর কারণ একই, generic।
- **পরিবর্তন (T46):**
  - Contract path হিসেবে ধরা হবে শুধু আসল OpenAPI/Swagger file বা contract annotation-যুক্ত source। CI, deploy আর config path বাদ।
  - Rank হবে একই neutral score দিয়ে।
  - প্রতিটি candidate-এর জন্য আলাদা reason code।
  - থামার নিয়ম: মোট নতুন item ≥45 হলে, অথবা প্রতি repo-তে নতুন pool-এর top 60 review হলে। Repo-প্রতি cap 6, T45-এর item সহ।
- **কোনো bias ঢোকেনি:**
  - Divergence kind-এর তথ্য এখনো কারও কাছে নেই, কারণ coding শুরু হয়নি।
  - Per-item direction Claude দেখেননি।
  - Miner hypothesis জানে না।
- **Analysis অপরিবর্তিত।** T45 আর T46-এর item দুটোই set=`new`।
