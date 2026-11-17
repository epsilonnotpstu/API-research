import csv
R=[
("B057","YES","INPUT_LOOSER","COMPATIBLE","UNSPECIFIED",2,"diff.patch:WalletApi.kt walletResponse(); PostWalletResponse.kt","POST wallet response now also accepts a form 'response' JARM JWT (verified) besides plain fields; malformed form data now yields 400 instead of an unhandled exception."),
("B058","NO","NA","NA","NA",3,"diff.patch:PaymentsResource.java","Whitespace, switch syntax and log message redaction only; responses unchanged."),
("B059","YES","INPUT_LOOSER","COMPATIBLE","UNSPECIFIED",2,"after/internal/controller/comment_controller.go:249","GetCommentWithPage now converts a short comment_id to the full ID before use, so short IDs are resolved instead of being used raw."),
("B060","NO","NA","NA","NA",2,"diff.patch:ContractEntityMapper.java; PartnerApiStubs.java","Mapper skips billing id for entitlements without purchase data and tolerates null contracts (previously NPE) in sync code; stub test helpers added. Not directly an HTTP operation outcome."),
("B061","NO","NA","NA","NA",3,"diff.patch:pkg/visitor/handlers.go","Handler function types gain a context parameter; internal visitor API only."),
("B062","YES","INPUT_STRICTER","BREAKING","UNSPECIFIED",3,"diff.patch:ProjectController.java update()","PATCH project formerly updated from JSON body; now requires name and office query params, ignores body and renames the project (missing params rejected)."),
("B063","NO","NA","NA","NA",2,"diff.patch:WellKnownResourceImpl.java","Bean imports moved to a different package; removed duplicate local variable declarations; same pagination logic. Before state appears non-compiling."),
("B064","NO","NA","NA","NA",3,"diff.patch:JobExecutionRepository.java","Only interface method and empty repository interface added; no behaviour."),
("B065","YES","RESPONSE_SHAPE","COMPATIBLE","UNSPECIFIED",2,"diff.patch:GroupSimpleEntity.java; GroupServiceImpl.java mapToSimple","Simple group listing now includes environmentId and environmentName fields; environment lookup could fail for unknown environment."),
("B066","YES","OTHER","COMPATIBLE","UNSPECIFIED",2,"diff.patch:WalletApi.kt jarmJwksPath, handleGetJarmJwks","New GET /wallet/jarm/{requestId}/jwks.json endpoint added; with jwk embed by reference the client metadata jwks URI now points to it."),
("B067","NO","NA","NA","NA",3,"diff.patch:KafkaConfig.java","Javadoc deprecation comments only."),
("B068","YES","HEADER_OR_MEDIA_TYPE","UNCLEAR","UNSPECIFIED",1,"diff.patch:DittoHeaderDefinition.java:119","Accept header definition no longer flagged as written to external headers, so it is no longer published in outgoing external headers."),
("B069","NO","NA","NA","NA",3,"diff.patch:controllers/user.go; user_util.go","Function moved to another file with a renamed local variable; logic identical."),
("B070","YES","STATUS_OR_ERROR_MAPPING","COMPATIBLE","UNSPECIFIED",3,"diff.patch:commits.go:198","Listing commits with a nonexistent sha now returns 404 instead of 500."),
]
ids=[r['item_id'] for r in csv.DictReader(open('items.csv'))]
assert ids==[r[0] for r in R]
w=csv.writer(open('codes_H2.csv','w',newline=''))
w.writerow("item_id,observable_change,change_kind,client_impact,contract_specified,confidence,locators,rationale".split(','))
for r in R:
    if r[1]=="NO": r=r[:2]+("NA",)*3+r[5:]
    w.writerow(r)
