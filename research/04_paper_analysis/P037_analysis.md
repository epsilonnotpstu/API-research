# P037 — LO2: Microservice API Anomaly Dataset of Logs and Metrics

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (references বাদ) · **উৎস:** PROMISE 2025 (CC-BY), ১০ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Alexander Bakhtin, Jesse Nyyssölä, Yuqing Wang, Noman Ahmad, Ke Ping, Matteo Esposito, Mika Mäntylä, Davide Taibi (University of Oulu ও সহযোগী)
- **Venue:** PROMISE 2025, DOI 10.1145/3727582.3728682
- **Cluster:** T9 (secondary: T1 — API negative testing দিয়ে data generation; T3 — OAuth2 security protocol)
- **ধরন:** Dataset paper + preliminary analysis

## B. Motivation
- Microservice-এর anomaly detection ও root cause analysis-এ logs, metrics, traces (multi-modal) প্রয়োজন; বিদ্যমান dataset হয় **benchmark demo system** (TrainTicket, DeathStarBench, OnlineBoutique) নয়তো **proprietary**; অনেকগুলো তিনটি modality দেয় না (p.1–2 L131–151; Table 1)।
- বিদ্যমান dataset মূলত **performance fault** (CPU, network delay) inject করে — **API misuse/erroneous call থেকে উদ্ভূত anomaly** কম অধ্যয়িত (p.1 L125–129; p.4 L553–555)।

## C. Research questions
- ⚠️ RQ নেই (dataset paper); লক্ষ্য: production-ধাঁচের OSS microservice-এর multi-modal labeled dataset ও প্রাথমিক বিশ্লেষণ।

## D. Contributions (p.2 L155–183)
- **Light-OAuth2** (networknt, ৭ microservice + MySQL; production-grade OSS, পরে archived)-এর logs ও metrics dataset — FAIR, Zenodo, CC-BY 4.0।
- End-to-end replication scripts (deploy, test, collect)।
- প্রাথমিক log anomaly detection ও metric PCA বিশ্লেষণ; trace সংগ্রহের চ্যালেঞ্জ।
- Community contribution mechanism (GitHub issue)।

## E. Methodology
- **Test suite (Locust):** standard OAuth2.0 flow — Authorization Code (PKCE সহ/ছাড়া), Client Credentials, Refresh Token — এবং Client/User/Service registration-এর CRUD; insecure Resource Owner Password flow ও Light-OAuth2-নির্দিষ্ট feature বাদ; API security অভিজ্ঞ দুই লেখক documentation ও OAuth2.0 spec থেকে test লিখে পরস্পর review (p.3 L469–500)।
- **Correct বনাম error (negative) task:** documentation-এ বর্ণিত প্রতিটি error-এর জন্য আলাদা task (যেমন `GET /oauth2/service` → 404 SERVICE_NOT_FOUND, `POST` → 400 SERVICE_ID_EXISTS) — **৫৩টি error label** (p.3 L501–514)।
- **Run:** Docker Compose deploy → সব service প্রস্তুত → ৬০ s correct test → প্রতিটি error-এর জন্য correct + সেই error ১০ s; প্রতি রান ৫৪টি test; প্রতি ঘণ্টায় cronjob, Jul–Aug 2024, **১,৭৪০ রান**, ~৫৪০ GB; **hardware/network fault inject করা হয়নি** (p.3–4 L520–559)।
- **Collection:** `docker logs` (DEBUG level), Prometheus node exporter (host metrics, প্রতি ৫ s), Jaeger agent (traces) (p.4 L565–572)।
- **Preliminary analysis:** LogLead দিয়ে log anomaly detection (DT, LR, IsolationForest, KMeans, RarityModel, OOVD; word/অন্যান্য representation); stage ১ — সব service-এর log একত্রে (১০০ রান × ১ error + correct, ৭০০ sequence, ৫০-৫০ split, ১০ পুনরাবৃত্তি); stage ২ — প্রতিটি (error, service) জোড়া আলাদা (৫৩×৭ matrix, DT, একবার); metrics-এ PCA (p.4–6 L641–909)।

## F. Dataset
- ~**৬৫৭,০০০ log file** (১,৭৪০ × ৫৪ × ৭), **>২ বিলিয়ন log line**; **৪৮৫টি metric**, >৪৫.৫ মিলিয়ন metric file; trace CSV (কিন্তু প্রতি trace-এ মাত্র একটি span); Locust response log metadata (ground-truth timestamp) (p.1 L72–75; p.4 L579–628)।

## G. Evaluation
- F1 (supervised), AUC-ROC (unsupervised), mean ± SD; PCA explained variance।

## H. Results (author-reported)
- **Stage ১:** সব optimized score ≈০.৬৬৭ — অর্থাৎ model কাজ করে না, সবকিছু error বলে; unsupervised AUC-ROC ≈০.৫ (random); কেবল DecisionTree F1 >০.৭; representation-এর প্রভাব নগণ্য → **সব service-এর log একত্র করা ভালো পদ্ধতি নয়** (p.5 L804–829)।
- **Stage ২:** Client ও **Token service** log সবচেয়ে তথ্যবহুল (OAuth flow-এর শেষ ধাপ); Key service সবচেয়ে দুর্বল (এর জন্য Locust task নেই); Key ছাড়া সব service কোনো না কোনো error type-এ perfect detection — কিন্তু এর জন্য error আগে থেকে জানা দরকার (বাস্তবে অব্যবহারযোগ্য) (p.5–6 L831–890)।
- **PCA:** শীর্ষ ৩ component থেকে ১০টি স্বতন্ত্র feature — বেশিরভাগ **memory ও disk** (Docker-এর disk written bytes, filesystem available, memory AnonPages ইত্যাদি) (p.6 L897–909)।
- **Traces:** Light-OAuth2 sub-operation instrument করে না — কেবল MySQL call-এর single-span trace; OpenTelemetry দিয়ে instrument করা resource-সীমার কারণে অসম্ভব → **কার্যত দুই modality (logs, metrics)** (p.4 L601–615)।
- **চ্যালেঞ্জ:** error অজানা হলে কোন service-এর model বাছবেন, service-জুড়ে threshold normalize, একক error একাধিক service-এ ছড়ালে root cause (p.6 L915–920)।

## I. Strengths
- **API-misuse-চালিত anomaly** — performance-fault-কেন্দ্রিক dataset-এর পরিপূরক; T1 (negative testing) ও T9 (observability)-র সেতু।
- Production-grade OSS + source code উপলব্ধ (benchmark demo বা proprietary-র মাঝামাঝি)।
- বিশাল আকার, fine-grained label (৫৩ error), FAIR, CC-BY, replication script।
- নেতিবাচক ফলাফল (stage ১ ব্যর্থতা, trace সমস্যা) সৎভাবে রিপোর্ট।

## J. Explicit limitations (p.7–8 Threats)
- Construct: Light-OAuth2-এর **অসম্পূর্ণ API documentation** — Locust task ভুল বোঝার ঝুঁকি (পারস্পরিক review ও OAuth2.0 spec দিয়ে প্রশমন); trace modality অনুপস্থিত।
- Internal: hardware anomaly নেই (ইচ্ছাকৃত, কারণ পৃথক করতে); database প্রতি রানে reset।
- External: configuration, MySQL, বিশ্ববিদ্যালয়ের server production cloud নয়; **সব Locust task সমান probability** — অবাস্তব correct/error বণ্টন (sampling দিয়ে সমন্বয়যোগ্য)।
- Future: proper tracing, task weight/spike, per-service metric, hardware anomaly, অন্য MSS।

## K. Inferred limitations (⚠️ অনুমান)
- **“Anomaly” = documented API error response (4xx), প্রকৃত fault নয়:** documentation-অনুযায়ী প্রত্যাশিত error (404 NOT_FOUND, 400 EXISTS) — সিস্টেম সঠিকভাবেই আচরণ করছে; এটি “anomaly detection” নয়, বরং **request-type classification**। বাস্তব production anomaly (bug, degradation, security attack) প্রতিনিধিত্ব করে না।
- **একটি system, archived:** সাধারণীকরণ সীমিত; system আর রক্ষণাবেক্ষণে নেই — বাস্তব “production” দাবি দুর্বল।
- **Host-level metrics** — per-service নয়; ১০ s error window-এ metric পরিবর্তন ক্ষুদ্র (লেখকরাও প্রভাব “light” আশা করেন) — metrics modality-র anomaly-সংকেত সন্দেহজনক।
- **Preliminary analysis দুর্বল:** stage ২ একবার রান, label-নির্ভর; F1 ০.৬৬৭-এর “degenerate” baseline দেখায় task design-এর সমস্যা; কোনো multi-modal fusion পরীক্ষা নেই — dataset-এর মূল প্রতিশ্রুতি অপরীক্ষিত।
- **Security মাত্রা:** OAuth2 system হলেও attack traffic (token replay, BOLA, PKCE downgrade) নেই — নিরাপত্তা-anomaly gap।

## L. Threats to validity
- উপরে J; inferable: construct (anomaly-র সংজ্ঞা), external (এক system), ecological (equal-probability load)।

## M. Reproducibility
- Zenodo-তে পূর্ণ dataset ও replication package; Docker Compose — **উচ্চ** (archived system-এর dependency ঝুঁকি)।

## N. Opportunities (hypothesis)
- **Security-anomaly microservice dataset:** OAuth2/API-তে BOLA, token misuse, mass assignment attack traffic (P012/P014/P015-এর attack scenario) + log/metric — P014-এর log-ভিত্তিক BOLA detection-এর জন্য বাস্তব benchmark; T3↔T9।
- **Fuzzer-generated anomaly:** REST fuzzer (P006/P007/EvoMaster) দিয়ে অপ্রত্যাশিত (undocumented) 5xx ও crash — প্রকৃত fault-সমৃদ্ধ observability dataset; test oracle হিসেবে log/metric anomaly ব্যবহার (T1-এর oracle problem — P003/P008)।
- **Spec-aware log anomaly detection:** OpenAPI-এর documented response বনাম observed log — অসঙ্গতি = anomaly (P001/P004 spec mismatch-এর runtime সংস্করণ)।
- Multi-service threshold/normalization ও root-cause localization পদ্ধতি (লেখকদের চ্যালেঞ্জ)।
- Proper trace instrumentation (OpenTelemetry) সহ multi-modal fusion benchmark।

## O. Relationships
- **Complements P038** (microservices testing SLR) — testing ও observability-র সংযোগ।
- **Relates to P014** (log-ভিত্তিক BOLA detection) — অনুরূপ log-চালিত বিশ্লেষণ; LO2-এ security attack নেই।
- **Relates to P011/P020** (microservice API, industrial context)।
- **Uses T1 practice** (negative testing) data generation-এ।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract (৬৫৭K file, ২B line, ৪৫M metric file, ৪৮৫ metric) | p.1 L57–79 |
| বিদ্যমান dataset-এর সীমা | p.1–2 L131–151 |
| Contributions | p.2 L155–183 |
| Related dataset (Table 1) | p.2–3 L195–355 |
| Light-OAuth2 system | p.2–3 L251–463 |
| Test suite, OAuth2 flow | p.3 L469–500 |
| Correct/error task | p.3 L501–514 |
| Run procedure, ১,৭৪০ রান | p.3–4 L520–559 |
| Collection (Docker, Prometheus, Jaeger) | p.4 L565–572 |
| Data description, trace সমস্যা | p.4 L579–628 |
| Log analysis setup | p.4–5 L641–802 |
| Stage ১ ফল (Table 3) | p.5–6 L804–829 |
| Stage ২ ফল (Table 4) | p.5–6 L831–890 |
| PCA | p.6 L897–909 |
| চ্যালেঞ্জ, future use | p.6 L913–960 |
| Contribution পথ | p.6–7 L974–1008 |
| Threats | p.7–8 L1038–1121 |

**Document integrity:** Body সম্পূর্ণ; Table 1–4 column-split (Table 4-এর ৫৩×৭ matrix পুনর্গঠন অসম্ভব); Fig.1–2 অনুপস্থিত; F1 সূত্র হারিয়েছে।
