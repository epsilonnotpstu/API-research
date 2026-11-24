import csv
P="contract/"
R=[
("C052","GET /v2/_catalog; GET /v2/{name}/tags/list","PRESENT",P+"swagger__swagger.json:34","NOT_DECLARED","","NO","",1,"Group-revocation flaw affects all group-authorised registry reads; operation inferred. Contract has no security or group rule."),
("C053","POST /api/serviceaccounts/{serviceAccountId}/tokens","PRESENT",P+"public__openapi3.json:23696","DECLARED",P+"public__openapi3.json:27760","YES","action: `serviceaccounts:write` scope: `serviceaccounts:id:1` (single service account)",2,"Token creation needs serviceaccounts:write on the account; revoked permission still honoured briefly. Global security basic/api_key declared."),
("C054","GET /api/v1/applications/{name}/resource; DELETE /api/v1/applications/{name}/resource; POST /api/v1/applications/{name}/resource/actions","PRESENT",P+"assets__swagger.json:972","NOT_DECLARED","","NO","",2,"Resource endpoints described but no security or RBAC/destination-scoping rule in contract."),
("C055","GET /api/v1/repository/provider/{provider}/name/{name}; DELETE /api/v1/repository/provider/{provider}/name/{name}; GET /api/v1/artifact/name/{name}","PRESENT",P+"pkg__api__openapi__minder__v1__minder.swagger.json:1585","NOT_DECLARED","","NO","",3,"Paths described; no security block and no statement binding repository to caller's project."),
("C056","DELETE /api/latest/fleet/spec/certificates","ABSENT","","NA","","NA","",2,"Contracts cover nanomdm, nanodep and teams only; no certificate template route. Path inferred from handler struct."),
("C057","DELETE /api/v1/applications/{name}","PRESENT",P+"assets__swagger.json:609","NOT_DECLARED","","NO","",2,"Flaw is internal hook creation on app deletion; delete operation described without security or AppProject restriction rule."),
("C058","DELETE /v2/{name}/manifests/{reference}; DELETE /v2/{name}/blobs/{digest}","PRESENT",P+"swagger__swagger.json:691","NOT_DECLARED","","NO","",3,"Delete operations described; no security scheme and no scope-to-action rule."),
("C059","DELETE /realms/{realm}/account/credentials/{credentialId}","ABSENT","","NA","","NA","",2,"Only the admin client openapi exists; Account REST API credential endpoint not described. Path inferred from Keycloak account API."),
("C060","PUT /api/v1/sources/{id}/status; PUT /api/v1/agents/{id}/status","PRESENT",P+"api__v1alpha1__agent__openapi.yaml:11","NOT_DECLARED","","NO","",3,"Agent API paths described without security; token source_id binding not stated."),
("C061","GET /answer/admin/api/dashboard; GET /answer/admin/api/users/page","PRESENT",P+"docs__swagger.json:126","DECLARED",P+"docs__swagger.json:128","NO","",2,"Admin auth middleware passed on nil user; contract declares ApiKeyAuth and admin tag only, no stated admin-only rule. Operation representative of admin routes."),
("C062","ANY /api/proxy/; ANY /api/exec/; ANY /api/wirelogs/","ABSENT","","NA","","NA","",3,"Only finops-agent and rca-agent specs exist; gateway internal routes not described."),
("C063","PUT /nifi-api/controller-services/{id}","NO_CONTRACT","","NA","","NA","",2,"Contract file is a config fragment with no paths; not a usable API description. Route inferred from NiFi API."),
("C064","PUT /api/users/{username}","PRESENT",P+"swagger.yaml:1604","NOT_DECLARED","","NO","",3,"Update-user operation described with no security or owner-only rule."),
("C065","GET /api/v1/projects/{projectID}/sources/{sourceID}","PRESENT",P+"docs__swagger.json:6967","DECLARED",P+"docs__swagger.json:6969","NO","",3,"Operation has ApiKeyAuth; contract does not state that the source must belong to the project in the path."),
("C066","DELETE /api/v1/projects/{project}/background","PRESENT",P+"pkg__swagger__swagger.json:1924","DECLARED",P+"pkg__swagger__swagger.json:1976","NO","",3,"JWTKeyAuth declared; contract does not mention token scopes such as projects.background_delete."),
("C067","GET /api/v1/clusters/kubeconfig/{name}","ABSENT","","NA","","NA","",3,"Contract lacks the kubeconfig download route; fix moved it from whitelist to authenticated scope."),
("C068","GET /api/v1/jobs; POST /api/v1/jobs; GET /api/v1/jobs/{id}; PATCH /api/v1/jobs/{id}; DELETE /api/v1/jobs/{id}","PRESENT",P+"api__manager__swagger.json:735","NOT_DECLARED","","NO","",3,"Job paths described with no security declaration; contract states no authentication requirement."),
]
H="item_id,operation,contract_operation,op_locator,contract_security,sec_locator,policy_in_contract,policy_quote,confidence,rationale".split(",")
ids=[l.split(",")[0] for l in open("items.csv").read().split("\n")[1:] if l]
d={r[0]:r for r in R}
assert ids==[r[0] for r in R],ids
w=csv.writer(open("codes_H3.csv","w",newline=""))
w.writerow(H)
for i in ids: w.writerow(d[i])
