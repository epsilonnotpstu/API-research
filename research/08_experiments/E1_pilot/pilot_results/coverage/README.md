# Baseline JaCoCo coverage (2026-11-14, Claude)

- **Tool:** `jacococli.jar report` (0.8.12), প্রতিটি run-এর `jacoco.exec`-এর ওপর।
- **Class-এর সীমা:** শুধু application-এর নিজের class (SUT jar থেকে বের করা):
  - scout-api: `se/devscout`, 102টি class।
  - swagger-petstore: `io/swagger/petstore`, 20টি class।
  - market: `market/` (`market-rest`) + `market-core-0.1.2.jar`, 89টি class।
  - cwa-verification: `BOOT-INF/classes/app/`, 63টি class।
  - Library বাদ।
- **ফাইল:** `baseline_coverage.csv` (সারাংশ); `<sut>_s<seed>_*.csv` (class-ভিত্তিক JaCoCo CSV)।

| SUT | Line coverage (s1/s2/s3) | Branch coverage (s1/s2/s3) | মোট line |
|---|---|---|---|
| scout-api (Batch 2) | 31.6 / 29.4 / 31.5% | 16.2 / 17.9 / 18.5% | 2,673 |
| swagger-petstore | 72.9 / 72.4 / 72.9% | 61.3 / 59.5 / 61.3% | 580 |
| market | 36.2 / 35.2 / 35.4% | 4.1 / 2.6 / 2.6% | 1,583 |
| cwa-verification | 43.0 / 43.0 / 43.0% | 8.7 / 8.7 / 8.7% | 711 |

## পড়ার নিয়ম
- Seed-ভেদে পার্থক্য ছোট (≤2.2 percentage point)। মানে seed variability-র চেয়ে SUT-এর পার্থক্য অনেক বড়।
- ⚠️ **Market-এর branch coverage খুব কম।** `market-core`-এ web module-এর জন্য থাকা service-ও আছে, যা REST দিয়ে পৌঁছানো যায় না। সংখ্যাটা তাই প্রকৃত REST coverage-এর চেয়ে কম দেখায়। REST-reachable denominator আলাদা করা বাকি।
- ⚠️ **scout-api-র denominator-এ admin, import আর auth class আছে**, যেগুলো fuzzing-এ পৌঁছায় না।
- **R1-এর জন্য তাৎপর্য:** baseline violation-গুলো code-এর মাত্র এক-তৃতীয়াংশ (petstore-এ প্রায় তিন-চতুর্থাংশ) exercise করে পাওয়া। Coverage বাড়লে violation-এর বণ্টন বদলাতে পারে। এটা external validity-র একটা সীমা।
- ⚠️ **cwa-র branch denominator বেশি** (619 branch, 711 line)। [H] সম্ভবত Lombok-এর তৈরি `equals`/`hashCode`-এর কারণে; class-ভিত্তিক CSV দেখে যাচাই করা হয়নি। Branch coverage তাই কম দেখাতে পারে।
