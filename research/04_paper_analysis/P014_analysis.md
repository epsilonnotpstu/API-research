# P014 — Automated Broken Object-Level Authorization Attack Detection in REST APIs through OpenAPI to Colored Petri Nets Transformation (Links2CPN)

**পাঠের অবস্থা:** সম্পূর্ণ body পাঠ (related work §6 skim, references বাদ) · **উৎস:** Int. J. Inf. Security (Springer, CC-BY), ১৯ পৃষ্ঠা · **বিশ্লেষক:** Claude · 2026-10-19

---

## A. Bibliographic identity
- **Authors:** Ailton Santos Filho, Ricardo J. Rodríguez, Eduardo L. Feitosa (Federal University of Amazonas; Universidad de Zaragoza)
- **Venue:** International Journal of Information Security, 2025, DOI 10.1007/s10207-024-00970-5
- **Cluster:** T3 (secondary: T9 — log-ভিত্তিক runtime detection; T4 — OpenAPI links থেকে আচরণ মডেল)
- **ধরন:** Formal model transformation + log-ভিত্তিক attack detection + ছোট user study

## B. Motivation
- BOLA OWASP API Security Top 10-এর #১; attacker অন্য user-এর object id দিয়ে data পড়ে/বদলায় (p.1 L29–31; p.5 L433–438)।
- OpenAPI-র textual spec formal method-এ সরাসরি ব্যবহারযোগ্য নয়; Petri net-এ রূপান্তর করলে বিদ্যমান analysis কৌশল ব্যবহার করা যায় (p.2 L110–119)।

## C. Research questions
- ⚠️ স্পষ্ট RQ নেই; তিন-স্তর মূল্যায়ন: running example, user-based (CTF), real-world software (Memos)।

## D. Contributions (p.2 L121–174)
- OpenAPI 3.1.0 → Colored Petri Net (CPN) রূপান্তর (Algorithm 1–3)।
- Links2CPN tool (Python, Snakes library) — রূপান্তর + **conformance checking (token replay)** দিয়ে web server log থেকে BOLA attack শনাক্ত; GitHub-এ উন্মুক্ত।

## E. Methodology
- **Transformation:** প্রতিটি (operation, response status) → transition `METHOD-path-STATUS`; preset place-এর arc parameter নাম দিয়ে লেবেল; **OpenAPI `links`** দিয়ে response থেকে পরবর্তী operation-এ arc (যেমন login response-এর `bid` → `GET /basket/{bid}`); বিচ্ছিন্ন transition বাদ (p.6–7 Alg. 1–3)।
- **Coloring:** user role, resource id, state টোকেনের data হিসেবে (p.6 L505–508)।
- **Event log:** CLF + Authorization header + request/response body → JSON (URL, parameter, method, status, client IP, timestamp) (p.8 L718–729)।
- **Conformance checking (replay):** transition fire করা না গেলে — (i) input place-এ token নেই = control-flow violation; (ii) token-এর মান ভিন্ন = **data-flow violation → BOLA ধরা হয়** (p.8 L769–782)।
- Logging overhead “ন্যূনতম” — async logging/API gateway দিয়ে প্রশমনযোগ্য বলে যুক্তি (p.8 L784–792)।

## F. Dataset ও setup
- **Running example:** OWASP Juice Shop (AWS EC2-তে instrumented), দুটি BOLA: V1 অন্যের cart দেখা, V2 অন্যের cart-এ product যোগ; log ৩০ ও ২৩ লাইন (p.9–10)।
- **User-based:** UFAM-এর Computer Network Security কোর্সের ২০ জনের মধ্যে ১৫ শিক্ষার্থী CTF-এ (২৫ Jan–৮ Feb 2023); **১২টি attack report**, ~৪,০০০ log line, ~২,০০০ request; V1-এ ৫১৪, V2-এ ১৯২ request; ground truth হাতে লেবেল (p.10–11 L953–981)।
- **Real-world:** Memos (open-source note app) — ২০২২-এ fixed BOLA **revert করে** পুনরায় vulnerable; ১১-লাইনের log (p.12 L1167–1210)।
- Ethics approval ও informed consent উল্লেখিত।

## G. Evaluation
- Accuracy, precision, recall, F1 — দুটি confusion matrix: (a) attack attempt বনাম detection; (b) successful attack বনাম detection (p.11)।

## H. Results (author-reported)
- Running example ও Memos: attack request-এ “transition not enabled” error — শনাক্ত (p.9–10; p.12)।
- **Attempt-স্তরে (Table 2a):** V1 ও V2 উভয়ে Accuracy = Precision = Recall = F1 = **১** (p.11 L1060–1062)।
- **Successful attack-স্তরে (Table 2b):** V1 — Acc ০.৯৯, Prec ০.৯৭, Rec ১, F1 ০.৯৮; **V2 — Acc ০.৬৪, Prec ০.২২, Rec ১, F1 ০.৩৭** — ব্যর্থ attempt-কেও attack হিসেবে চিহ্নিত করে; status code-ভিত্তিক heuristic প্রয়োজন (p.11 L1067–1076)।
- V1-এ ১০১ attempt-এর ৯৮টি সফল (৯৭.০২%); V2-এ ৮৮-এর ২০টি (২২.৭২%); ১২-র মধ্যে ৩ জন V2 exploit করতে পারেননি (p.11–12 L1077–1165)।
- Abstract: “accuracy greater than 95% in the proposed scenarios” (p.1 L36–37)।
- **APIs.guru-র ১,৯৫৫টি spec-এর মাত্র ৯টি `links` ব্যবহার করে** (p.3 L257–264)।

## I. Strengths
- Formal, ব্যাখ্যাযোগ্য detection — কোন transition কেন fire হলো না তা স্পষ্ট।
- কোনো training data লাগে না; spec + log দিয়েই কাজ — runtime monitoring/forensics-এ প্রয়োগযোগ্য।
- Tool, log, vulnerable fork সব GitHub-এ; Open Access।
- মানব-উৎপন্ন attack traffic (CTF) — নিছক scripted attack-এর চেয়ে বাস্তবসম্মত বৈচিত্র্য।

## J. Explicit limitations (p.12–13 §5.4; p.3; conclusion)
- **OpenAPI `links` প্রয়োজন** — বাস্তবে প্রায় অনুপস্থিত (৯/১,৯৫৫); developer spec আপডেট করবেন বা code annotation/AI tool সাহায্য করবে বলে অনুমান।
- Spec-কে error case সহ সঠিক হতে হবে।
- নির্দিষ্ট OpenAPI version-এ বাঁধা; **centralized log** প্রয়োজন (network segmentation নীতির বিপরীতে); JSON log format-এ রূপান্তর লাগে।
- শুধু known pattern — অজানা attack-এর জন্য ML/anomaly detection-এর সঙ্গে hybrid প্রস্তাব।
- User study-র sample প্রতিনিধিত্বশীল নয়।
- শুধু offline; ভবিষ্যতে eBPF দিয়ে real-time, fuzzing দিয়ে pentest tool, বেশি legitimate traffic-সহ মূল্যায়ন।

## K. Inferred limitations (⚠️ অনুমান)
- **৯/১,৯৫৫ (০.৪৬%) — প্রয়োগযোগ্যতার মৌলিক বাধা:** পদ্ধতিটি কার্যত এমন spec-এর উপর নির্ভরশীল যা প্রায় কোথাও নেই; মূল্যায়নের তিনটি case-এর spec-ই লেখকরা নিজেরা `links` দিয়ে লিখেছেন/সাজিয়েছেন।
- **BOLA-র সংজ্ঞা সংকীর্ণ:** “একই session-এ পূর্বে server-প্রদত্ত id ছাড়া অন্য id” = attack। বৈধ ক্ষেত্রে (shared resource, admin access, bookmark/URL থেকে সরাসরি access, অন্য client/session-এ পাওয়া id) এটি false positive দেবে — evaluation traffic attack-কেন্দ্রিক বলে এটি পরীক্ষিত হয়নি (লেখকরাও বেশি legitimate traffic দিয়ে মূল্যায়ন future work বলেন)।
- **Detection বনাম authorization-এর পার্থক্য:** server আসলে access দিলেও না দিলেও attempt-কে attack বলে — তাই V2-এ precision ০.২২; এটি vulnerability detector নয়, বরং **suspicious access-attempt detector**।
- **Metric সংজ্ঞা উল্টো:** TP = “benign correctly benign”, TN = “attack correctly attack” (p.11 L1053–1058) — প্রচলিত নিরাপত্তা-রীতির বিপরীত; precision/recall-এর ব্যাখ্যা বিভ্রান্তিকর হতে পারে। Abstract-এর “>৯৫% accuracy” V2-এর ০.৬৪ (successful-attack স্তর) বাদ দিয়ে।
- **Threats section দুর্বল:** “no problem should arise”, “free from threats to internal validity” — অতি-আত্মবিশ্বাসী; ground truth একই গবেষকদের হাতে লেবেল।
- Scale: সব log ১১–৪,০০০ লাইন, দুটি অ্যাপ; বড় traffic-এ token-replay-এর খরচ/latency মাপা হয়নি।
- Real-world case-এ vulnerability ইচ্ছাকৃতভাবে revert করা — “real-world” দাবি আংশিক।
- Background-এ CRUD → “UPDATE” HTTP method (p.3 L208–209) — HTTP-তে নেই; ছোট কিন্তু মনোযোগহীনতার লক্ষণ।

## L. Threats to validity
- উপরে J; inferable: construct (attempt = attack), conclusion (ছোট n, কোনো পরিসংখ্যান নেই), external (দুটি অ্যাপ, CTF শিক্ষার্থী)।

## M. Reproducibility
- Links2CPN, instrumented Juice Shop, Memos fork, log ফাইল GitHub-এ [44] — উচ্চ; তবে user study-র কাঁচা log-এর গোপনীয়তা/প্রকাশ যাচাই প্রয়োজন।

## N. Opportunities (hypothesis)
- **`links`/dependency স্বয়ংক্রিয় অনুমান:** RESTler-ধাঁচের producer-consumer inference (P006), traffic mining বা LLM দিয়ে OpenAPI-তে links যোগ — পদ্ধতির মূল বাধা দূর করে; T4-এর সঙ্গে সংযোগ।
- **Ownership-aware oracle:** user identity × resource ownership মডেল (token color-এ user id) — session-id-ভিত্তিক heuristic-এর বদলে; P015-এর access-policy fuzzing-এর সঙ্গে সমন্বয়।
- **Active testing:** CPN থেকে BOLA test sequence তৈরি (লেখকদের fuzzing future work) — P012-এর template-ভিত্তিক পদ্ধতির সঙ্গে একীভূত।
- বাস্তব production traffic-এ false-positive হার পরিমাপ; real-time (eBPF/API gateway) deployment-এর latency মূল্যায়ন।
- Microservice distributed log (T9: P037 LO2-এর মতো dataset) জুড়ে BOLA detection।

## O. Relationships
- **Complements P012** (mass assignment; একই OWASP API Top-10 পরিবার; P012-এর লেখকদের future work-এ BOLA)।
- **Contrasts with P015** (active fuzzing দিয়ে access-policy violation) — এটি passive, log-ভিত্তিক।
- **Depends on spec richness** — P001/P004-এর spec-অসম্পূর্ণতা ফলাফল এখানে আরও তীব্র (links প্রায় অনুপস্থিত)।
- **Links T9:** log-ভিত্তিক anomaly detection (P037)।

## P. Evidence locations
| দাবি | অবস্থান |
|---|---|
| Abstract (>৯৫%) | p.1 L23–37 |
| Contributions | p.2 L121–174 |
| ৯/১,৯৫৫ spec-এ links | p.3 L257–278 |
| CPN সংজ্ঞা | p.4–5 L330–413 |
| Running example (Juice Shop BOLA) | p.5 L416–443 |
| Algorithm 1–3 | p.6–7 L511–671 |
| Memos CPN | p.7 L637–651 |
| Event log, replay, BOLA = data-flow violation | p.7–8 L676–782 |
| Logging overhead | p.8 L784–792 |
| Links2CPN | p.8–9 L795–812 |
| Juice Shop V1/V2 | p.9–10 L821–951 |
| User study (১৫ জন, ১২ report) | p.10 L953–981 |
| Metrics, Table 2 (০.৬৪/০.২২) | p.11 L1045–1076 |
| Attempt/success হার | p.11–12 L1077–1165 |
| Memos real-world | p.12 L1167–1210 |
| Threats | p.12–13 L1229–1282 |
| Conclusions, future work | p.15 L1514–1538 |

**Document integrity:** Body সম্পূর্ণ; Algorithm 2–3-এর লাইন আংশিক ভাঙা; CPN definition-এর গ্রিক প্রতীক (Σ ইত্যাদি) হারিয়েছে; Table 1–2 (confusion matrix) column-split — মূল metric text থেকে নেওয়া; JSON listing letter-spaced; Fig.3–7 অনুপস্থিত। §5.2-এ একই অনুচ্ছেদ দুবার (মূল paper-এর editing ত্রুটি)।
