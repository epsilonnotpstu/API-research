import csv
NA=["NA"]*7
R=[
("A017","NO",*NA,2,"A017/diff.patch; server/sso/validate.go","SAML response validation flaw lets attacker forge assertions; authentication/signature validation, not an operation-level access rule."),
("A018","YES","FUNCTION_LEVEL","TWO_ROLES","YES","ABSENT","NA","NO","SERVICE_LOGIC",3,"A018/diff.patch:session.go UpdateSessionsIsGuest; contract boards swagger lacks it","User demoted to guest kept stale session roles and could still change group names until sessions were refreshed."),
("A019","YES","TENANT_ISOLATION","TWO_SAME_ROLE","YES","ABSENT","NA","NO","DATA_QUERY",3,"A019/diff.patch:9-30 server.go","Holder of one tenant's token could update labels of or unsubscribe a worker of another tenant by worker UUID; no tenant ownership check."),
("A020","YES","OTHER","ONE","YES","UNCLEAR","NA","NO","SERVICE_LOGIC",2,"A020/diff.patch:9-14 connection.go; contract truncated at 3000 lines","User with copy permission could copy a file denied by source-side pattern filters to a permitted name and read it; only destination was checked."),
("A021","YES","PROPERTY_LEVEL","ONE","YES","UNCLEAR","NA","NO","SERVICE_LOGIC",2,"A021/diff.patch workflow/util/merge.go, operator.go; contract truncated","User creating a Workflow could set restricted spec fields (hostNetwork, serviceAccountName, securityContext) despite strict template-reference mode; only podSpecPatch was blocked."),
("A022","YES","PROPERTY_LEVEL","ONE","YES","ABSENT","NA","NO","SERVICE_LOGIC",3,"A022/diff.patch:9-32 team.go","Team admin lacking the invite-user permission still received the team invite ID in the teams response, enabling invitations."),
("A023","NO",*NA,2,"A023/diff.patch","Over-broad service-account RBAC of a node CSI plugin on a compromised node; not an HTTP operation of this service."),
("A024","YES","OBJECT_LEVEL","TWO_SAME_ROLE","YES","ABSENT","NA","NO","HANDLER",3,"A024/diff.patch run_log_server.go; v1beta1 swagger has no run log path","Caller could read logs of another user's run (or an unrelated pod via node ID) without authorization against the run."),
("A025","NO",*NA,2,"A025/diff.patch operator/pkg/model/ingestion/gateway.go","Gateway API controller ignored ReferenceGrant for mirror backends; Kubernetes CRD/controller authorization, not an HTTP operation of the service."),
("A026","YES","FUNCTION_LEVEL","TWO_ROLES","YES","ABSENT","NA","NO","MIDDLEWARE_FILTER",3,"A026/diff.patch:11 debug_handler.go","Any authenticated user, including lowest-privilege observer, could access debug/pprof endpoints; fix requires global admin role."),
("A027","YES","OBJECT_LEVEL","TWO_ROLES","YES","ABSENT","NA","NO","HANDLER",3,"A027/diff.patch endpoint_yjs.go authorizeYjsRoom","Any authenticated user could open /yjs/<typename.id.column> and read or write file-column content of rows, including admin-only tables, without row permission checks."),
("A028","NO",*NA,2,"A028/diff.patch auth/store.go","Client certificate CN was accepted as RBAC user identity via gateway; authentication/credential validation flaw."),
("A029","YES","OTHER","ONE","YES","UNCLEAR","NA","NO","SERVICE_LOGIC",1,"A029/diff.patch pkg/apis/core/validation/validation.go","Node update validation overwrote old-object values before admission, letting updates evade validating webhooks that rely on old state."),
("A030","NO",*NA,2,"A030/diff.patch ElasticSearchRestClientConstant.java","Unprefixed header names bypass Camel inbound header filter in a library component; header injection, no service-defined access rule or operation."),
("A031","YES","FUNCTION_LEVEL","TWO_ROLES","YES","PRESENT","DECLARED","YES","MIDDLEWARE_FILTER",2,"A031/diff.patch:8-22 SecurityConfiguration.java; contract /import (admin scope) line 759","Non-admin users could call import/export operations reserved for admin role; fix restructures the request matcher rules."),
("A032","YES","FUNCTION_LEVEL","ONE","YES","ABSENT","NA","NO","HANDLER",3,"A032/diff.patch AttributesRestHandlder.go","Any authenticated low-privilege user could read the apiTokenSecret attribute via the attributes API because RBAC check was disabled."),
]
with open("codes_H1.csv","w",newline="") as f:
    w=csv.writer(f);w.writerow("item_id,ac_relevant,ac_kind,principals_needed,observable_via_http,contract_operation,contract_security,policy_in_contract,fix_location,confidence,locators,rationale".split(","))
    for r in R:
        if r[1]=="NO": r=(r[0],"NO","NA","NA","NA","NA","NA","NA","NA")+r[9:]
        w.writerow(r)
print(len(R))
