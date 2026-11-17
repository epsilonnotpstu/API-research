import csv
H="item_id,observable_change,change_kind,client_impact,contract_specified,confidence,locators,rationale".split(",")
N=lambda i,c,r:[i,"NO","NA","NA","NA",c,"diff.patch",r]
R=[
N("B113",3,"Only adds Swagger @Schema documentation fields to a doc-holder class; no runtime behaviour changes."),
N("B114",3,"Injected service field type changed to async variant; same endpoint signature; outcome not determinable as different from provided code."),
N("B116",2,"Removes @Transactional from a dry-run endpoint that only logs/sends; no client-visible outcome change."),
["B115","YES","STATUS_OR_ERROR_MAPPING","BREAKING","SPECIFIED",3,"after/.../ProductReviewExceptionHandler.java:57-59; contract product-review-openapi.yaml:132 (400 product not found)","Product-not-found-for-review error was 400, now 404. Also type-mismatch and unreadable-body exceptions are rethrown instead of mapped to 500 by generic handler."],
["B117","YES","DEFAULT_OR_OPTIONALITY","COMPATIBLE","UNSPECIFIED",2,"diff.patch GroupResource.java:~186-192; GroupsResource.java:~110-125","New subGroupsCount query param default true. Brief child listing previously omitted subgroup counts, now includes them by default; non-brief unchanged. Counts can be disabled."],
["B118","NO","NA","NA","NA",1,"diff.patch","Importer mapper now sets dispatch criteria on example responses via new parameter; effect depends on callers outside provided diff, likely affects mock matching but undeterminable."],
["B119","YES","RESPONSE_SHAPE","COMPATIBLE","UNSPECIFIED",3,"diff.patch Bridge.java:~142,~414; WebsocketConfiguration.java; BridgeResourceImpl.java:~362","Bridge representation gains optional websocketConfiguration (read and write); bridge created from it uses websocket settings. Existing clients unaffected."],
["B120","NO","NA","NA","NA",2,"diff.patch HttpBridge.java:~198-215,~434,~471","Concurrent maps and stale-consumer cleanup refactor; consumer map removal moved to close handler; same results for clients."],
["B121","YES","RESPONSE_SHAPE","COMPATIBLE","UNSPECIFIED",2,"diff.patch VariantAnnotation.java:~67,~367","Annotation model gains errorMessage property with getter, serialized as a new (null by default) field."],
N("B122",2,"Lombok replaces hand-written accessors in a repository model; new audit enum unused by HTTP. No observable change."),
["B123","NO","NA","NA","NA",2,"diff.patch InMemorySubmodelService.java","Adds synchronization around mutating operations; same single-request outcomes."],
["B124","NO","NA","NA","NA",2,"diff.patch KafkaConfig.java; KafkaLineageStream.java","Kafka config field renamed localServerId to messageKey with deprecated alias; same key used; not reached by an HTTP operation outcome."],
["B125","YES","INPUT_LOOSER","COMPATIBLE","UNSPECIFIED",3,"diff.patch PolicyConditionResource.java:~87-92,~120-123,~158-176; PolicyCondition.java:~63-120","Policy conditions now accept EXPRESSION subject with violationType and CEL validation (400 with celErrors on bad expression), values over 255 chars allowed; violationType added to responses."],
N("B126",2,"Adds new certificate-attribute classes only; no existing HTTP handler is modified or wired in the provided diff."),
]
for r in R:
    r[5]=r[5]
w=csv.writer(open("codes_H2.csv","w",newline=""));w.writerow(H);w.writerows(R)
