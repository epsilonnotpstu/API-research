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
