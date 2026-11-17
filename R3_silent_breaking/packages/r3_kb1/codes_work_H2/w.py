import csv
H="item_id,observable_change,change_kind,client_impact,contract_specified,confidence,locators,rationale".split(",")
R=[
("B001","YES","INPUT_STRICTER","BREAKING","UNSPECIFIED",2,"diff.patch:6-7","Multipart upload parsing now throws via Ensure.requireNonNull when the file or fileName part is missing; before, the map was returned with null entries."),
("B002","YES","AUTHZ_OR_AUTH","COMPATIBLE","UNSPECIFIED",1,"diff.patch:8,31","getPermissions/resetPermissions are synchronized so a race can no longer leave parent-group permissions missing for the session; results differ only under concurrency."),
("B003","YES","HEADER_OR_MEDIA_TYPE","COMPATIBLE","UNSPECIFIED",1,"diff.patch:18-22,33","Default Content-Type header value changes from the bare type 'application' to 'application/json', and an Accept header defaulting to */* is added to the forwarded headers."),
("B004","NO","NA","NA","NA",3,"diff.patch:6-14","Only two unused string constants are added; no behaviour changes."),
("B005","YES","RESPONSE_CONTENT","UNCLEAR","UNSPECIFIED",1,"diff.patch:15-35,85-95","Namespace normalisation now also re-applies the app-instance tracking label for namespaced objects whose namespace was defaulted, and error message text changes; resulting target manifests/tracking metadata differ."),
("B006","NO","NA","NA","NA",2,"diff.patch:6-30","Batch-size config lookup is passed realm context instead of call context in an internal cleanup task; no client-visible effect shown."),
("B007","UNCLEAR","NA","NA","NA",1,"diff.patch:20-27","Config validation now sets an empty server path to '/'; effect on served routes depends on code not provided."),
("B008","YES","RESPONSE_CONTENT","UNCLEAR","UNSPECIFIED",1,"diff.patch:60-120","Endpoint descriptors (interface name, href, subprotocol fields) are built differently, with callback address and hostname/prefix ordering changed; served descriptor values change."),
("B009","YES","HEADER_OR_MEDIA_TYPE","COMPATIBLE","UNSPECIFIED",3,"diff.patch:8","Requests with Origin starting http://127.0.0.1 now receive CORS headers like http://localhost; before they went through the normal origin checks."),
("B010","UNCLEAR","NA","NA","NA",1,"diff.patch:15-45","Cancelling a reusable caller job now reloads intermediate caller jobs instead of cancelling them; returned cancelled-job list and final states may differ."),
("B011","YES","RESPONSE_SHAPE","COMPATIBLE","UNSPECIFIED",1,"diff.patch:25-45","Password policy failures now return structured text validation errors (with message ids/context) instead of plain errors, and ErrTooManyBreaches is removed."),
("B012","YES","STATUS_OR_ERROR_MAPPING","COMPATIBLE","UNSPECIFIED",1,"diff.patch:6","After sending 405 for an unknown method, the request is now marked handled so no further handler processes it."),
("B013","UNCLEAR","NA","NA","NA",1,"diff.patch:6-25","The empty display-name check moved from the controller into CheckPermissionForUpdateUser, whose code is not provided; ordering of errors may differ."),
("B014","YES","RESPONSE_CONTENT","COMPATIBLE","UNSPECIFIED",3,"after/pkg/handler/eval.go:235-238","Eval result segmentID is now set only when a segment yields a variant; before, it held the last evaluated segment's ID even with no match (now 0)."),
]
w=csv.writer(open("codes_H2.csv","w",newline=""));w.writerow(H);w.writerows(R)
open("codes_report_H2.md","w").write("# H2 report kb1\n\n14 items coded. No item failed to open. B001 contract folder was empty. Hard cases: B005, B007, B008, B010, B013 (relevant code outside provided files); B003 only affects outbound headers. Several confidences are 1.\n")
