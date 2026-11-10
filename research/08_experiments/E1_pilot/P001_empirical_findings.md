# P001-এর ১৪৭টি confirmed fault — R1-এর জন্য empirical বিশ্লেষণ

**তারিখ:** 2026-11-09 · **Script:** `p001_oas_analysis.py` · **ফলাফল:** `p001_results/` (`summary.json`, `oas_violation_types.csv`, `developer_response.csv`, `replay_agreement.csv`)

**Data:** P001 (Martin-Lopez, Segura, Ruiz-Cortés, ESEC/FSE 2022) supplementary material, Zenodo 10.5281/zenodo.6941292, CC-BY 4.0। ২.৭ GB zip থেকে range request দিয়ে নির্দিষ্ট ফাইল নামানো হয়েছে।
- `results-all/faultClustersConfirmedBugs_<api>.csv` — প্রতিটি confirmed fault-এর একটি প্রতিনিধি test, পূর্ণ response body ও failure message সহ।
- `additional/bugs_reported.csv` — developer-দের প্রতিক্রিয়া।
- `results-replication/resources/taas_eval/<API>/openapi.*` — ১৩টি spec।

**সংখ্যার যাচাই:** ১৪৭টি fault, যার ৭৩টি (৫০%) F_OAS — P001 paper-এর রিপোর্টের সাথে হুবহু মেলে (`P001_analysis.md` §H)।

⚠️ = বিশ্লেষকের অনুমান। [H] = hypothesis।

---

## 1. Oracle অনুযায়ী fault ও developer প্রতিক্রিয়া

| P001 oracle | Fault | Report করা | Developer উত্তর | Confirmed | Fixed | Confirmed / reported |
|---|---|---|---|---|---|---|
| F_OAS (spec অমিল) | ৭৩ | ৬৯ | ২৩ | ১০ | ৪ | **১৪.৫%** |
| F_2XXP (অবৈধ parameter গৃহীত) | ৪৪ | ৪২ | ২৮ | ২৪ | ১৪ | **৫৭.১%** |
| F_400 (বৈধ-মনে-হওয়া input-এ 400) | ১৬ | ১৬ | ১২ | ৬ | ০ | ৩৭.৫% |
| F_2XXD (dependency লঙ্ঘন গৃহীত) | ৮ | ৮ | ৬ | ৫ | ১ | ৬২.৫% |
| F_5XXI / F_5XXV | ৫ / ১ | ৩ / ০ | ১ / ০ | ০ / ০ | ১ / ০ | — |

**পর্যবেক্ষণ:**
- Spec-অমিল (F_OAS) সংখ্যায় সবচেয়ে বেশি।
- কিন্তু developer-রা এগুলো **সবচেয়ে কম confirm করেছেন**: ১৪.৫%, যেখানে F_2XXP-তে ৫৭.১%।

⚠️ **ব্যাখ্যা (অনুমান):**
- অনেক F_OAS developer-দের চোখে “bug” নয়। হতে পারে spec-এর ঘাটতি, নয়তো কম গুরুত্বপূর্ণ।
- এটি R1-এর triage-প্রয়োজনের পরোক্ষ প্রমাণ (Class B)।
- বিকল্প ব্যাখ্যাও সম্ভব: report-এর ভাষা, প্রতিষ্ঠানের response নীতি ইত্যাদি। তাই এটি কার্যকারণ প্রমাণ নয়।

## 2. F_OAS-এর ধরন (৭৩টি fault; multi-label — ২৬টিতে একাধিক ধরন)

| ধরন (P001 validator-এর message) | Fault | Developer উত্তর | Confirmed | Fixed | Codebook-এ সম্ভাব্য দিক [H] |
|---|---|---|---|---|---|
| ADDITIONAL_PROPERTIES (undeclared field) | ২৭ | ১৪ | ৪ | ০ | S-RESP-MISSING (spec অসম্পূর্ণ) |
| STATUS_UNDEFINED (undocumented status) | ২২ | ৪ | ৩ | ১ | S-STATUS বা IMPL (ভুল status) |
| TYPE_NULL (null, কিন্তু spec-এ nullable নেই) | ১৯ | **০** | **০** | ১ | S-RESP-TYPE (nullable অনুপস্থিত) |
| FORMAT (date ইত্যাদি) | ১১ | ১ | ১ | ০ | উভয় দিকই সম্ভব |
| COMPOSITION (oneOf/allOf/anyOf ব্যর্থ) | ৮ | — | — | — | Spec-এর composition জটিলতা |
| TYPE_MISMATCH | ৭ | ৪ | ৩ | ১ | উভয় দিকই সম্ভব |
| PATTERN | ৫ | ৩ | ৩ | ০ | **SPEC (নিশ্চিত উদাহরণ — নিচে দেখুন)** |
| MISSING_REQUIRED | ৪ | ৩ | ২ | ০ | IMPL বা অতিরিক্ত-কঠোর `required` |
| ENUM / CONTENT_TYPE / অন্যান্য | ৩ / ২ / ৫ | | | | |

**পর্যবেক্ষণ:** TYPE_NULL ধরনের ১৯টি fault-এ **একটিও developer উত্তর আসেনি।**
- ⚠️ এগুলো সম্ভবত spec-এ `nullable` বাদ পড়ার ফল, অর্থাৎ SPEC দিকের।
- তবে উত্তর না আসা মানেই “spec ভুল” নয়।
- [H] Codebook pilot-এ এই ধরন অগ্রাধিকার পাবে।

### উদাহরণ: Amadeus-এর double-escaped pattern — একটি স্পষ্ট SPEC ত্রুটি

**ত্রুটির উৎস:**
- P001-এর Amadeus spec-এ (`taas_eval/Amadeus/openapi.json`) ৯টি জায়গায় pattern লেখা আছে `"^\\\\d+(\\\\.\\\\d+)?$"`।
- JSON-decode করার পর regex-টি হয় `^\\d+…`। এটি অঙ্ক (`\d`) নয়, **আক্ষরিক backslash + `d`** খোঁজে।
- ফলে “399.00”-এর মতো সঠিক মূল্য-string কখনোই মেলে না। Python `re` দিয়ে যাচাই করা হয়েছে।

**প্রভাব:**
- PATTERN ধরনের **৫টি fault-ই** এই pattern থেকে এসেছে।
- এর ৩টি developer “confirmed” করেছেন, কিন্তু একটিও fixed নয়।
- Implementation সঠিক; ত্রুটি spec-এর escape-এ।
- ⇒ Codebook অনুযায়ী **SPEC / S-RESP-TYPE**।

⚠️ **অনিশ্চয়তা:** Double-escape-টি Amadeus-এর প্রকাশিত spec-এ ছিল, নাকি P001-এর format রূপান্তরের সময় ঢুকেছে — অজানা।
- দুই ক্ষেত্রেই এটি “spec নিজেই ত্রুটির উৎস”-এর বাস্তব উদাহরণ।
- এবং দেখায় যে developer-এর “confirmed” label-ও attribution বলে দেয় না।

## 3. আমাদের `conformance.py` দিয়ে replay — instrument যাচাই

প্রতিটি fault-এর প্রতিনিধি request/response (P001-এর CSV থেকে পুনর্গঠিত) P001-এর নিজের spec-এর বিপরীতে চালানো হয়েছে।

| P001 oracle | Default (OpenAPI semantics) | Strict (undeclared property = violation) |
|---|---|---|
| F_OAS | ৬২/৭৩ (৮৫%) | **৭১/৭৩ (৯৭%)** |
| F_400 | ১৫/১৬ | ১৫/১৬ |
| F_5XXI + F_5XXV | ৬/৬ | ৬/৬ |
| F_2XXP | ৩০/৪৪ | ৩০/৪৪ |
| F_2XXD | **০/৮** | ০/৮ |

**মূল ফলাফল:**

1. **Instrument নির্ভরযোগ্য:**
   - Spec-ভিত্তিক verdict-এ (F_OAS, F_400, 5xx) আমাদের checker P001-এর validator-এর রায় ৮৫–১০০% পুনরুৎপাদন করে।
   - ⇒ R1-এর experiment-এ ব্যবহারযোগ্য।
2. **Strictness-এর প্রশ্ন:**
   - ADDITIONAL_PROPERTIES-এর ২৭টি fault-এর মধ্যে default mode-এ ১৮টি পুনরুৎপাদিত হয়েছে, strict mode-এ ২৭টিই।
   - বাকি **৯টি (F_OAS-এর ১২%) কেবল OpenAPI-র ডিফল্টের চেয়ে কঠোর ব্যাখ্যায় violation।**
   - তিনটি spec-এ (LanguageTool, Foursquare, YouTube Search) `additionalProperties: false` একবারও নেই।
   - ⚠️ অনুমান: P001-এর validator undeclared property-কে ত্রুটি ধরত। RESTest-এর configuration পড়ে নিশ্চিত করতে হবে।
   - **R1-এর জন্য তাৎপর্য:**
     - “Violation”-এর সংজ্ঞা validator-এর strictness-এর উপর নির্ভরশীল।
     - Experiment-এ strictness স্পষ্টভাবে ঘোষণা করে দুটোই রিপোর্ট করতে হবে।
     - Codebook-এ এদের আলাদা চিহ্ন দরকার।
3. **“Spec” শুধু OpenAPI document নয়:**
   - F_2XXD-এর ৮টিই আমাদের checker ধরেনি। Inter-parameter dependency OpenAPI-তে প্রকাশযোগ্য নয়; P001 RESTest-এর IDL ব্যবহার করেছে (P016)।
   - F_2XXP-এর ১৪টিও ধরা পড়েনি। অন্তত কয়েকটি ক্ষেত্রে constraint কেবল RESTest-এর test configuration-এ আছে। উদাহরণ: Restcountries-এ `capital=Milan`, `currency=NAR` “অবৈধ”, অথচ spec-এ শুধু `type: string`।
   - ⇒ R1-এর triage-এ “spec defect” নির্ণয়ে **সহায়ক constraint-উৎস** (IDL, test config, documentation)-কে আলাদা প্রমাণ-স্তর হিসেবে ধরতে হবে।
   - Codebook-এর E-DOC স্তর এর সাথে সম্পর্কিত।
4. **অবশিষ্ট miss (F_OAS ২টি, strict-এ):**
   - Marvel-এ path parameter-এর random মানে `/` থাকায় path মেলেনি → UNDOCUMENTED_OPERATION।
   - একটিতে composition-এর ভিন্ন ব্যাখ্যা।

## 4. Instrument-এর উন্নতি (এই বিশ্লেষণের সময় ধরা পড়ে সংশোধিত)

| Bug বা অভাব | কীভাবে ধরা পড়ল | সংশোধন |
|---|---|---|
| `$ref` parameter resolve-এর আগে (name, in) key — Amadeus-এর ২৭টি parameter এক হয়ে যাচ্ছিল | F_2XXP miss debug | আগে resolve, তারপর key |
| Array query parameter (csv বা form) deserialize হচ্ছিল না → ভুয়া INVALID_ACCEPTED, F_400 miss | F_400 অসঙ্গতি | `collectionFormat` ও `style` অনুযায়ী split ও coerce |
| Content-Type যাচাই নেই | DHL miss | `RESPONSE_CONTENT_TYPE` |
| `date`/`date-time` format যাচাই নেই (jsonschema-র Draft4 checker-এ নেই) | Marvel miss | নিজস্ব format checker |
| অ-JSON body | OMDb miss | `RESPONSE_PARSE` |
| Java regex (`\p{L}`) Python-এ compile হয় না | market spec | Pattern বাদ দিয়ে `x-unchecked-pattern` চিহ্ন |

সব সংশোধনের পর regression পাস:
- `test_specmut` ১৪৪/১৪৪।
- `test_pipeline` — unexplained ০।

## 5. সীমাবদ্ধতা

- প্রতিটি fault-এর **একটি প্রতিনিধি** test। Cluster-এর বাকি failure-এর body এই ফাইলে নেই — পূর্ণ data `restest.us.es`-এ, যার TLS সমস্যা আছে।
- Developer প্রতিক্রিয়ার অনেক ঘর ফাঁকা। “Fixed” spec-এ নাকি code-এ হয়েছে, তা অজানা।
- P001-এর API-গুলো closed-source, তাই codebook-এর E-CODE-INTENT প্রমাণ নেই। এখানে attribution label দেওয়া হয়নি — কেবল ধরন ও সম্ভাব্য দিক [H]।
- ADDITIONAL_PROPERTIES-এর strictness-অনুমান পরোক্ষ।

## 6. R1-এর জন্য পরবর্তী পদক্ষেপ

1. **Codebook v0.2:**
   - (ক) Strictness চিহ্ন: STRICT_ONLY।
   - (খ) সহায়ক constraint-উৎস (IDL বা test config) প্রমাণ-স্তর হিসেবে।
   - (গ) TYPE_NULL ও COMPOSITION-এর জন্য নির্দিষ্ট নিয়ম।
2. **P001-এর ৭৩টি F_OAS-এর ছোট pilot labelling:** দুইজন labeller। Public documentation (E-DOC) ও response consistency (E-CONSIST) দিয়ে, code ছাড়া।
3. **RESTest source থেকে strictness নিশ্চিতকরণ:** validator configuration দেখা।
