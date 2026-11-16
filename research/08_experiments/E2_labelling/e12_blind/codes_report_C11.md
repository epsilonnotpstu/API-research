# Blind coding report — C11

## পদ্ধতি

প্রথম command ছিল `cat TASK_CODE.md`। এরপর অনুমোদিত `../../../09_collab/PROTOCOL.md` ও `items.csv` পড়েছি। প্রতিটি item-এর proposition কেবল তার নিজস্ব `contract/` ও `impl/` artifacts দিয়ে পরীক্ষা করেছি; এক item-এর সিদ্ধান্তের evidence হিসেবে অন্য item-এর ফাইল ব্যবহার করিনি।

`divergence_kind` নির্ধারণে Y তৈরির নিকটবর্তী code mechanism দেখেছি। Explicit serialization, enum, list return, route, validation branch ও error envelope-কে DELIBERATE বলেছি। Missing mapping, missing membership check, wrong variable, null handling এবং payload assignment-এর অনুপস্থিতিকে ACCIDENTAL বলেছি। এটি developer-এর মানসিক উদ্দেশ্য বা কোন artifact সঠিক, সেই বিচার নয় (`TASK_CODE.md`, “What you code”)।

`contract_specificity` স্বাধীনভাবে নির্ধারণ করেছি। Operation-specific prose, explicit route name, parameter annotation ও dedicated success-response declaration-কে SPECIFIC; shared schema থেকে পাওয়া type/enum, inherited route থেকে অনুমিত isolation এবং response-list-এর নীরবতাকে GENERIC বলেছি। Shared schema-তেও আচরণটি নিয়ে dedicated prose থাকলে সেটিকে SPECIFIC ধরা হয়েছে, যেমন widget description ও allowedImportAdditions। Operation-এ explicit required parameter reference থাকলেও SPECIFIC ধরা হয়েছে। এই সীমারেখার প্রয়োগ নিচে ব্যাখ্যা করা আছে।

Confidence 3 সরাসরি code/declaration evidence; confidence 2-তে framework binding, generated mapping বা scope interpretation-এর inference আছে। ⚠️ চিহ্নিত inference-গুলো runtime observation নয়। CSV rationale সর্বোচ্চ 40 words এবং প্রতিটি row-তে একই item-এর implementation ও contract locators রয়েছে।

## ফলাফল

`codes_C11.csv`-এ `items.csv`-এর ক্রমে 36টি item রয়েছে: DELIBERATE 17, ACCIDENTAL 19; SPECIFIC 19, GENERIC 17। কোনো proposition-কে artifacts-এর সঙ্গে বিরোধপূর্ণ পাইনি, তাই UNCLEAR ব্যবহার করিনি। এগুলো static coding judgment, runtime pass/fail নয় (evidence: `codes_C11.csv`, rows U01–U36)।

## কঠিন সিদ্ধান্ত

- **U02:** ⚠️ Domain ও persistence widget-এ description নেই এবং mapper domain model-এ যাচ্ছে। Missing field propagation-কে ACCIDENTAL বলেছি; fields-এর তালিকা থাকাই description বাদ দেওয়ার dedicated নির্দেশের evidence নয়। Contract-এর optional description prose-এর কারণে SPECIFIC। Generated mapper অনুপস্থিত হওয়ায় confidence 2।

  Evidence: `U02/impl/gravitee-apim-rest-api/gravitee-apim-rest-api-management-v2/gravitee-apim-rest-api-management-v2-rest/src/main/java/io/gravitee/rest/api/management/v2/rest/resource/analytics/dashboards/DashboardsResource.java:87;U02/impl/gravitee-apim-rest-api/gravitee-apim-rest-api-management-v2/gravitee-apim-rest-api-management-v2-rest/src/main/java/io/gravitee/rest/api/management/v2/rest/mapper/DashboardMapper.java:54;U02/impl/gravitee-apim-rest-api/gravitee-apim-rest-api-service/src/main/java/io/gravitee/apim/core/dashboard/model/DashboardWidget.java:35;U02/impl/gravitee-apim-repository/gravitee-apim-repository-api/src/main/java/io/gravitee/repository/management/model/CustomDashboardWidget.java:34`; `U02/contract/gravitee-apim-rest-api/gravitee-apim-rest-api-management-v2/gravitee-apim-rest-api-management-v2-rest/src/main/resources/openapi/openapi-analytics.yaml#1720;U02/contract/gravitee-apim-rest-api/gravitee-apim-rest-api-management-v2/gravitee-apim-rest-api-management-v2-rest/src/main/resources/openapi/openapi-analytics.yaml#1770`

- **U03:** ⚠️ Parameter-এর @Parameter documentation-এ query লেখা থাকলেও runtime @QueryParam নেই। JSON-consuming operation-এর unannotated long parameter থেকে body binding infer করেছি; ACCIDENTAL/SPECIFIC, confidence 2। Framework execution করিনি।

  Evidence: `U03/impl/dockstore-webservice/src/main/java/io/dockstore/webservice/resources/WorkflowResource.java:2372;U03/impl/dockstore-webservice/src/main/java/io/dockstore/webservice/resources/WorkflowResource.java:2377`; `U03/contract/dockstore-webservice/src/main/resources/openapi3/openapi.yaml#48`

- **U05:** ⚠️ Global ID lookup সফল হলে environment মিলানো হয় না; environmentId ব্যবহৃত হয় fallback key lookup-এ। Missing check-কে ACCIDENTAL বলেছি। Contract-এর envId description environment শনাক্ত করে; category isolation-এর dedicated promise না থাকায় scope expectation-কে GENERIC বলেছি।

  Evidence: `U05/impl/gravitee-apim-rest-api/gravitee-apim-rest-api-service/src/main/java/io/gravitee/rest/api/service/impl/CategoryServiceImpl.java:107;U05/impl/gravitee-apim-rest-api/gravitee-apim-rest-api-service/src/main/java/io/gravitee/rest/api/service/impl/CategoryServiceImpl.java:110;U05/impl/gravitee-apim-rest-api/gravitee-apim-rest-api-service/src/main/java/io/gravitee/rest/api/service/impl/CategoryServiceImpl.java:115`; `U05/contract/gravitee-apim-rest-api/gravitee-apim-rest-api-management/gravitee-apim-rest-api-management-rest/src/main/java/io/gravitee/rest/api/management/rest/resource/EnvironmentsResource.java#59;U05/contract/gravitee-apim-rest-api/gravitee-apim-rest-api-management/gravitee-apim-rest-api-management-rest/src/main/java/io/gravitee/rest/api/management/rest/resource/CategoryResource.java#79`

- **U10:** List<Token> return ও DAO list query সরাসরি explicit। তাই DELIBERATE। Response annotation operation-এ Token নাম দিয়েছে বলে SPECIFIC ধরেছি; responseContainer অনুপস্থিতি এই annotation-কে mere shared-schema default হিসেবে গণনা করিনি।

  Evidence: `U10/impl/dockstore-webservice/src/main/java/io/dockstore/webservice/resources/UserResource.java:201;U10/impl/dockstore-webservice/src/main/java/io/dockstore/webservice/resources/UserResource.java:206;U10/impl/dockstore-webservice/src/main/java/io/dockstore/webservice/jdbi/TokenDAO.java:66`; `U10/contract/dockstore-webservice/src/main/java/io/dockstore/webservice/resources/UserResource.java#200`

- **U11:** Invalid UUID-এর জন্য explicit BadRequestError এবং HTTP 400 mapping রয়েছে: DELIBERATE। Contract-এ 400 অনুল্লিখিত—এই silence-এর ভিত্তিতে GENERIC। এটি handler-এর unhandled exception হিসেবে code করিনি।

  Evidence: `U11/impl/src/server/v2.0/handler/scan.go:103;U11/impl/src/controller/scan/base_controller.go:1095;U11/impl/src/pkg/task/dao/task.go:112;U11/impl/src/lib/http/error.go:31`; `U11/contract/api/v2.0/swagger.yaml#1224`

- **U12:** ⚠️ Export call-এ membership পৌঁছায় না এবং handler launchId দিয়ে global lookup করে: missing isolation check হিসেবে ACCIDENTAL। Class-level project prefix থেকে isolation infer হওয়ায় GENERIC এবং confidence 2।

  Evidence: `U12/impl/src/main/java/com/epam/ta/reportportal/ws/controller/LaunchController.java:499;U12/impl/src/main/java/com/epam/ta/reportportal/core/launch/impl/GetLaunchHandlerImpl.java:340;U12/impl/src/main/java/com/epam/ta/reportportal/core/launch/impl/GetLaunchHandlerImpl.java:343`; `U12/contract/src/main/java/com/epam/ta/reportportal/ws/controller/LaunchController.java#107;U12/contract/src/main/java/com/epam/ta/reportportal/ws/controller/LaunchController.java#479`

- **U17:** ⚠️ Domain property city, contract property townName এবং mapper-এ rename নেই। Missing translation হিসেবে ACCIDENTAL; townName shared address schema থেকে আসায় GENERIC। Generated mapper implementation ছাড়া inference হওয়ায় confidence 2।

  Evidence: `U17/impl/opba-banking-rest-impl/src/main/java/de/adorsys/opba/tppbankingapi/controller/TppBankingApiPisController.java:62;U17/impl/opba-banking-rest-impl/src/main/java/de/adorsys/opba/tppbankingapi/controller/TppBankingApiPisController.java:67;U17/impl/opba-facade-protocol-api-shared/src/main/java/de/adorsys/opba/protocol/api/dto/result/body/Address.java:9`; `U17/contract/opba-banking-rest-api/src/main/resources/static/tpp_banking_api_pis.yml#183;U17/contract/opba-banking-rest-api/src/main/resources/static/tpp_banking_api_commons.yml#344`

- **U18:** List return proposition-এর Y নিশ্চিত করে; handler বাস্তবে findQuayByUserId ডাকে। ভিন্ন token source এখানে নতুন review target বানাইনি। Y-এর collection shape explicit হওয়ায় DELIBERATE; operation response annotation-এর জন্য SPECIFIC।

  Evidence: `U18/impl/dockstore-webservice/src/main/java/io/dockstore/webservice/resources/UserResource.java:227;U18/impl/dockstore-webservice/src/main/java/io/dockstore/webservice/resources/UserResource.java:232;U18/impl/dockstore-webservice/src/main/java/io/dockstore/webservice/jdbi/TokenDAO.java:70`; `U18/contract/dockstore-webservice/src/main/java/io/dockstore/webservice/resources/UserResource.java#226`

- **U19:** Partial-root permission-এর জন্য আলাদা branch leaf permissions যাচাই করে। এই explicit authorization path-এর কারণে DELIBERATE। PATCH-specific permission prose-এর জন্য SPECIFIC।

  Evidence: `U19/impl/services/concierge/enforcement/src/main/java/org/eclipse/ditto/services/concierge/enforcement/ThingCommandEnforcement.java:895;U19/impl/services/concierge/enforcement/src/main/java/org/eclipse/ditto/services/concierge/enforcement/ThingCommandEnforcement.java:898;U19/impl/services/concierge/enforcement/src/main/java/org/eclipse/ditto/services/concierge/enforcement/ThingCommandEnforcement.java:902`; `U19/contract/documentation/src/main/resources/openapi/ditto-api-2.yml#599;U19/contract/documentation/src/main/resources/openapi/ditto-api-2.yml#642`

- **U21:** PUT reconstruction allowedImportAdditions পড়ে না এবং empty additions-যুক্ত constructor ব্যবহার করে। Missing propagation হিসেবে ACCIDENTAL; permitted additions ও default নিয়ে dedicated contract prose থাকায় SPECIFIC।

  Evidence: `U21/impl/gateway/service/src/main/java/org/eclipse/ditto/gateway/service/endpoints/routes/policies/PolicyEntriesRoute.java:179;U21/impl/gateway/service/src/main/java/org/eclipse/ditto/gateway/service/endpoints/routes/policies/PolicyEntriesRoute.java:188;U21/impl/policies/model/src/main/java/org/eclipse/ditto/policies/model/ImmutablePolicyEntry.java:93`; `U21/contract/documentation/src/main/resources/openapi/ditto-api-2.yml#311;U21/contract/documentation/src/main/resources/openapi/sources/schemas/policies/policyEntry.yml#20`

- **U26:** Success responder বাছাই explicit হলেও proposition-এর payload না-পাওয়ার কারণ missing payload assignment। তাই ACCIDENTAL; operation-এর InstanceCreatedResp declaration-এর কারণে SPECIFIC।

  Evidence: `U26/impl/src/server/v2.0/handler/preheat.go:67;U26/impl/src/server/v2.0/handler/preheat.go:71`; `U26/contract/api/v2.0/swagger.yaml#959;U26/contract/api/v2.0/swagger.yaml#2030`

- **U28:** ⚠️ Optional attributes কোনো null default ছাড়া Lists.newArrayList-এ যায়, তবে শুধু content-loading branch-এ। Null binding static inference; unconditional crash দাবি করিনি। ACCIDENTAL/SPECIFIC, confidence 2।

  Evidence: `U28/impl/src/main/java/com/epam/ta/reportportal/ws/controller/WidgetController.java:93;U28/impl/src/main/java/com/epam/ta/reportportal/ws/controller/WidgetController.java:94;U28/impl/src/main/java/com/epam/ta/reportportal/core/widget/impl/GetWidgetHandlerImpl.java:159;U28/impl/src/main/java/com/epam/ta/reportportal/core/widget/impl/GetWidgetHandlerImpl.java:160`; `U28/contract/src/main/java/com/epam/ta/reportportal/ws/controller/WidgetController.java#93`

- **U29:** ⚠️ Response mapper-এ city থেকে townName rename নেই। Missing translation-কে ACCIDENTAL বলেছি; shared address schema থেকে townName আসায় GENERIC। Generated mapping code নেই, তাই confidence 2।

  Evidence: `U29/impl/opba-banking-rest-impl/src/main/java/de/adorsys/opba/tppbankingapi/controller/TppBankingApiPisInfoController.java:62;U29/impl/opba-banking-rest-impl/src/main/java/de/adorsys/opba/tppbankingapi/controller/TppBankingApiPisInfoController.java:92;U29/impl/opba-facade-protocol-api-shared/src/main/java/de/adorsys/opba/protocol/api/dto/result/body/Address.java:9;U29/impl/opba-facade-protocol-api-shared/src/main/java/de/adorsys/opba/protocol/api/dto/request/payments/PaymentInfoBody.java:20`; `U29/contract/opba-banking-rest-api/src/main/resources/static/tpp_banking_api_pis.yml#231;U29/contract/opba-banking-rest-api/src/main/resources/static/tpp_banking_api_commons.yml#344`

- **U32:** Collection PATCH explicit path-end route ও MergeThing.withFeatures ব্যবহার করে: DELIBERATE। Contract operation নিজে required featureId reference অন্তর্ভুক্ত করেছে বলে SPECIFIC, যদিও parameter definition shared।

  Evidence: `U32/impl/gateway/service/src/main/java/org/eclipse/ditto/gateway/service/endpoints/routes/things/FeaturesRoute.java:105;U32/impl/gateway/service/src/main/java/org/eclipse/ditto/gateway/service/endpoints/routes/things/FeaturesRoute.java:123;U32/impl/gateway/service/src/main/java/org/eclipse/ditto/gateway/service/endpoints/routes/things/FeaturesRoute.java:125`; `U32/contract/documentation/src/main/resources/openapi/ditto-api-2.yml#69;U32/contract/documentation/src/main/resources/openapi/sources/parameters/featureIdPathPathParam.yml#11;U32/contract/documentation/src/main/resources/openapi/sources/parameters/featureIdPathPathParam.yml#14`

- **U33:** ⚠️ Project existence check-এর পরে global item IDs নিয়ে description বদলানো হয়; item membership যাচাই অনুপস্থিত। ACCIDENTAL। Shared project route prefix থেকে isolation infer হওয়ায় GENERIC, confidence 2।

  Evidence: `U33/impl/src/main/java/com/epam/ta/reportportal/core/item/impl/UpdateTestItemHandlerImpl.java:372;U33/impl/src/main/java/com/epam/ta/reportportal/core/item/impl/UpdateTestItemHandlerImpl.java:375;U33/impl/src/main/java/com/epam/ta/reportportal/core/item/impl/UpdateTestItemHandlerImpl.java:377`; `U33/contract/src/main/java/com/epam/ta/reportportal/ws/controller/TestItemController.java#104;U33/contract/src/main/java/com/epam/ta/reportportal/ws/controller/TestItemController.java#481`

- **U34:** Controller userId গ্রহণ করেও handler-এ পাঠায় না; keyId-ভিত্তিক existence check ও delete হয়। Missing user propagation-কে ACCIDENTAL বলেছি। Proposition-এর X শুধু route-এ দুই identifier থাকার কথা, যা explicit—তাই SPECIFIC।

  Evidence: `U34/impl/src/main/java/com/epam/ta/reportportal/ws/controller/UserController.java:320;U34/impl/src/main/java/com/epam/ta/reportportal/ws/controller/UserController.java:321;U34/impl/src/main/java/com/epam/ta/reportportal/core/user/impl/ApiKeyHandlerImpl.java:93;U34/impl/src/main/java/com/epam/ta/reportportal/core/user/impl/ApiKeyHandlerImpl.java:96`; `U34/contract/src/main/java/com/epam/ta/reportportal/ws/controller/UserController.java#317`

- **U35:** Instance delete-এর পরে success responder-এ payload assignment নেই। ACCIDENTAL/SPECIFIC: এখানে বিচারটি missing payload নিয়ে, success status বেছে নেওয়া নিয়ে নয়।

  Evidence: `U35/impl/src/server/v2.0/handler/preheat.go:84;U35/impl/src/server/v2.0/handler/preheat.go:89`; `U35/contract/api/v2.0/swagger.yaml#1010;U35/contract/api/v2.0/swagger.yaml#2024`

## সীমাবদ্ধতা

Runtime data ও version history দেওয়া হয়নি (`TASK_CODE.md`, “What you are given”)। Network, Docker, Java, Maven, compilation বা item source execution করিনি। নিজের Python helper দিয়ে text reading, CSV লেখা এবং output-format validation করেছি। Framework binding, serializer ও MapStruct behavior-এর inference confidence 2 rows-এ স্পষ্ট করেছি; artifacts-এর বাইরে dependencies বা generated classes খুঁজিনি। CSV-তে ACCIDENTAL label oversight-এর structural mechanism বোঝায়, বাস্তব developer intent প্রমাণ করে না।

## Boundary incidents ও যাচাই

কোনো accidental boundary access ঘটেনি। COLLAB_BOARD.md, coordinator task files বা অন্য coder-এর output পড়িনি। Directory-এর বাইরে কেবল অনুমোদিত PROTOCOL.md পড়েছি। Search roots প্রতিবার explicit item path ছিল; source excerpts ছাপার আগে attribution ও credential-looking lines redact করা হয়েছে। Write paths কেবল `codes_C11.csv`, `codes_report_C11.md`, এবং `codes_work_C11/`।

Output verification-এ row count/order, column names, label values, confidence range, rationale length এবং প্রতিটি locator-এর file ও line existence পরীক্ষা করেছি। Source behavior যাচাই করতে কোনো third-party code চালানো হয়নি। নিজের output writer-এর প্রথম run-এ U11-এর task.go filename দুই ফাইলে মেলায় assertion থেমেছিল; dao/task.go নির্দিষ্ট করে সংশোধনের পরে output লেখা সম্পন্ন হয়েছে। এটি boundary incident নয়।
