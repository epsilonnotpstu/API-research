import csv
S="contract/"
J="pkg__swagger__swagger.json"
rows=[
("C035","GET /dav/projects/{project}/{uid}.ics; REPORT /dav/projects/{project}","ABSENT","","NA","","NA","",3,"CalDAV routes not in swagger; contract only covers /api/v1 REST."),
("C036","POST /v1beta1/resources; PUT /v1beta1/resources","PRESENT",S+"swagger.json:2815","DECLARED",S+"swagger.json:2817","NO","",2,"Batch create/update endpoint described with BearerAuth; no rule on namespace or project-bound creation."),
("C037","POST /v3/watch","PRESENT",S+"Documentation__dev-guide__apispec__swagger__rpc.swagger.json:1474","DECLARED",S+"Documentation__dev-guide__apispec__swagger__rpc.swagger.json:3114","NO","",3,"Watch described with global ApiKey; no statement that READ is limited to granted key range."),
("C038","GET /api/v1/stable/durable-tasks/{durable-task}","PRESENT",S+"api-contracts__openapi__openapi.yaml:54","DECLARED",S+"api-contracts__openapi__openapi.yaml:8","NO","",3,"Path has no tenant parameter; global bearer/cookie auth only; no tenant-binding statement."),
("C039","GET /exec/namespaces/{namespace}/components/{component}; GET /api/v1/namespaces/{namespace}/environments/{environment}/wirelogs","ABSENT","","NA","","NA","",3,"Contracts are for RCA/finops agents, not openchoreo-api exec or wirelogs."),
("C040","POST /api/v1/restore; POST /api/v1/backup","PRESENT",S+"internal__api__server__openapi.yaml:1848","DECLARED",S+"internal__api__server__openapi.yaml:44","NO","",3,"Restore described with global BearerAuth and 401; no role requirement stated."),
("C041","GET /log","ABSENT","","NA","","NA","",3,"No /log WebSocket path in node swagger."),
("C042","DELETE /api/v1/sources","PRESENT",S+"api__v1alpha1__openapi.yaml:11","NOT_DECLARED","","NO","",3,"deleteSources documented, only 401 response; no security section or owner scoping."),
("C043","PATCH /api/v1/nodes/{name}","PRESENT",S+"api__openapi-spec__swagger.json:29987","DECLARED",S+"api__openapi-spec__swagger.json:82168","NO","",3,"Node patch documented with global BearerToken; no rule about nodes and ownerReferences."),
("C044","HEAD /v2/{name}/blobs/{digest}; POST /v2/{name}/blobs/uploads/","PRESENT",S+"swagger__swagger.yaml:420","NOT_DECLARED","","NO","",2,"Blob and upload paths documented; no security section or per-repository read rule."),
("C045","POST /api/v1/fleet/android_enterprise/pubsub","ABSENT","","NA","","NA","",2,"Only nanodep, nanomdm and terraform teams specs present; no Android pubsub path."),
("C046","POST /v1/workspaces/{workspace_id}/projects/{project_id}/github/connect/complete","PRESENT",S+"docs__openapi-v1.yaml:6167","DECLARED",S+"docs__openapi-v1.yaml:21","NO","",3,"Endpoint documented with installation_id as free input; no ownership or tenant binding of installation stated."),
("C047","GET /api/datasources/proxy/uid/{uid}/{datasource_proxy_route}","PRESENT",S+"public__openapi3.json:16646","DECLARED",S+"public__openapi3.json:25452","NO","",2,"Proxy path documented with global basic/api_key; plugin ReqActions per datasource not mentioned."),
("C048","PUT /api/v1/nodes/{name}","PRESENT",S+"api__openapi-spec__swagger.json:31805","DECLARED",S+"api__openapi-spec__swagger.json:110593","NO","",2,"Node replace documented with global BearerToken; admission webhook validation behaviour not in spec."),
("C049","POST /api/v2/user/file-actions/copy","PRESENT",S+"openapi__openapi.yaml:4265","DECLARED",S+"openapi__openapi.yaml:41","NO","",2,"Copy endpoint documented; denied_patterns described only as list of denied patterns, no source-side rule."),
("C050","GET /attachments/{uuid}","ABSENT","","NA","","NA","",3,"Gogs API spec lacks the non-API /attachments route."),
("C051","PUT /api/v1/provisioning/contact-points/{UID}","PRESENT",S+"public__openapi3.json:26515","DECLARED",S+"public__openapi3.json:27747","NO","",3,"Put documented with global basic/api_key; no mention of protected:write permission."),
]
ids=[r[0] for r in csv.reader(open('items.csv'))][1:]
assert ids==[r[0] for r in rows]
w=csv.writer(open('codes_H3.csv','w',newline=''))
w.writerow("item_id,operation,contract_operation,op_locator,contract_security,sec_locator,policy_in_contract,policy_quote,confidence,rationale".split(','))
w.writerows(rows)
