import csv
R=[
("B071","YES","DEFAULT_OR_OPTIONALITY","BREAKING","UNSPECIFIED",2,"diff.patch:20,40","Absent channel query parameter on live.m3u8 and segment endpoints defaulted to 0 before and now defaults to 1, so requests omitting channel address a different stream channel."),
("B072","NO","NA","NA","NA",3,"diff.patch","Only logger framework swap (slf4j to log4j2) and log statement changes; no request handling altered."),
("B073","YES","AUTHZ_OR_AUTH","COMPATIBLE","UNSPECIFIED",2,"after/EntraIdCredential.java refresh(); diff.patch:@@ -197","Expired Entra ID access token previously returned false immediately; now a silent renewal is attempted (throttled after failure) so idle sessions can recover and groups refresh; failure still returns false when expired."),
("B074","YES","STATUS_OR_ERROR_MAPPING","COMPATIBLE","UNSPECIFIED",2,"after/CreateChargeExceptionMapper.java:55-59","Connector error NON_HTTPS_RETURN_URL_NOT_ALLOWED previously fell to default giving 500 connector error; now returns 422 with code P0920 on return_url. Contract documents 422 only generically."),
("B075","YES","RESPONSE_CONTENT","COMPATIBLE","UNSPECIFIED",2,"diff.patch:171-183","Validation error messages in form error fields now get a trailing period appended and first letter uppercased; message text differs from before."),
("B076","YES","SIDE_EFFECT_OR_STATE","COMPATIBLE","UNSPECIFIED",2,"diff.patch AbstractResource.java:111,136; GroupsResourceImpl.java:1101,1145","Artifacts and versions created through these endpoints now record the caller principal as owner passed to storage; update path also gains an Authorized write annotation. Owner not in contract."),
("B077","YES","RESPONSE_CONTENT","COMPATIBLE","UNSPECIFIED",2,"after/LoanScheduleModelDisbursementPeriod.java:108","addLoanCharges on a disbursement period was a no-op; now adds fee charge to chargesDueAtTimeOfDisbursement, changing charge values in calculated loan schedule."),
("B078","UNCLEAR","NA","NA","NA",1,"diff.patch:@@ -2595","Inline check (canWrite or admin or curator, else 403) replaced by checkCanWrite whose definition is not provided; equivalence to old check cannot be determined."),
("B079","YES","RESPONSE_SHAPE","COMPATIBLE","UNSPECIFIED",2,"after/AggregateSourceInfo.java:9,32","AggregateSourceInfo gains annotationSourcesInfo list property (never populated here, so serialized as null or absent); no contract provided."),
("B080","NO","NA","NA","NA",3,"diff.patch","Change is in a contract-test wiremock stub helper; no production HTTP operation affected."),
("B081","YES","STATUS_OR_ERROR_MAPPING","BREAKING","UNSPECIFIED",3,"diff.patch:@@ -50 ImportController.java","POST /import always returned 201 before. Now empty file gives 400, non-JSON content type 415, import exception 500; 201 only on success. Contract has no /import."),
("B082","NO","NA","NA","NA",3,"diff.patch:612","Log message now uses throwable.toString() instead of getMessage(); logging only."),
("B083","NO","NA","NA","NA",2,"diff.patch header.go","YAML omitempty tags and new model structs in a client-side models package; no HTTP operation behaviour visible."),
("B084","YES","SIDE_EFFECT_OR_STATE","COMPATIBLE","UNSPECIFIED",2,"diff.patch:333-340","On delete event removing a git reference, a published workflow left with no versions is now unpublished; before it stayed published. Index update also now triggered otherwise."),
]
with open("codes_H1.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow("item_id,observable_change,change_kind,client_impact,contract_specified,confidence,locators,rationale".split(","))
    w.writerows(R)
