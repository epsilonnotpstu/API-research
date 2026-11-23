import csv
Y="YES"
def r(i,rel,k,p,o,co,cs,pol,fx,c,loc,why): return [i,rel,k,p,o,co,cs,pol,fx,str(c),loc,why]
N=lambda i,loc,why,c=2: r(i,"NO",*["NA"]*7,c,loc,why)
rows=[
r("A097",Y,"OTHER","NONE",Y,"ABSENT","NA","NO","MIDDLEWARE_FILTER",2,"A097/diff.patch:11-30","Anonymous client sets X-Forwarded-Proto though forwarded headers are untrusted, switching which proxy access rule (http vs https) is matched, bypassing the stricter rule."),
r("A098",Y,"PROPERTY_LEVEL","ONE",Y,"UNCLEAR","NA","UNCLEAR","SERVICE_LOGIC",2,"A098/diff.patch:15,245-260","Editor-role user lacking protected:write could change protected webhook URL fields of contact points via the provisioning API."),
N("A099","A099/diff.patch:8-20","Flaw is in the legacy WebRTC data-channel input path, not an HTTP operation; modern HTTP/WebSocket control path is stated unaffected."),
r("A100",Y,"FUNCTION_LEVEL","ONE",Y,"ABSENT","NA","NO","MIDDLEWARE_FILTER",2,"A100/diff.patch:1-60","JSON web service registered as plain class bypassed Service Access Policy checks, so callers could invoke comment operations the policy should restrict."),
r("A101",Y,"FUNCTION_LEVEL","ONE",Y,"UNCLEAR","NA","NO","MIDDLEWARE_FILTER",2,"A101/diff.patch:30-60","Request with oversized body was forwarded to the AuthZ plugin without body, so a user the plugin would deny by body content could be allowed."),
r("A102",Y,"FUNCTION_LEVEL","ONE",Y,"PRESENT","NOT_DECLARED","NO","SERVICE_LOGIC",3,"A102/diff.patch:18-60; contract api/v1/sync/{namespace} l.2321","Any authenticated user, even with fake token, could create, read, update, delete sync-limit ConfigMaps without Kubernetes permission check."),
r("A103",Y,"FUNCTION_LEVEL","ONE",Y,"ABSENT","NA","NO","OTHER",1,"A103/diff.patch (test util only)","Authenticated user could delete objects via S3-gateway delete-objects without delete permission. Diff only shows test helper; fix location unseen."),
r("A104",Y,"FUNCTION_LEVEL","ONE",Y,"ABSENT","NA","NO","SERVICE_LOGIC",3,"A104/diff.patch:30-70","Token cached after introspection for one scope was accepted for rules requiring other scopes, so a token lacking scope bar passed bar-protected endpoints."),
r("A105",Y,"FUNCTION_LEVEL","ONE",Y,"PRESENT","DECLARED","NO","HANDLER",3,"A105/diff.patch:8-12; contract /apis/v2beta1/pipelines/upload l.937","Any user (even unauthorized) uploading pipelines or versions without namespace skipped authorization, creating or altering shared pipelines run by others."),
r("A106",Y,"MISSING_AUTHENTICATION","NONE",Y,"ABSENT","NA","NO","MIDDLEWARE_FILTER",2,"A106/diff.patch:64-175,545","Local configserver GraphQL API had no-op authorization and open CORS, letting any caller read and write secrets without credentials."),
N("A107","A107/diff.patch:23-60","Application controller created delete hooks without AppProject check; triggered by Git content and reconciliation, not a request-level HTTP decision."),
r("A108",Y,"OBJECT_LEVEL","TWO_SAME_ROLE",Y,"PRESENT","DECLARED","NO","HANDLER",3,"A108/diff.patch:5-30; contract PATCH blocks","Board member could patch comment blocks created by another user without permission to modify others' comments."),
r("A109",Y,"TENANT_ISOLATION","ONE",Y,"ABSENT","NA","NO","SERVICE_LOGIC",3,"A109/diff.patch:70-135; contract l.672 only in x- list","Authenticated tenant supplied another organization's installation_id at connect-complete and bound it to own workspace, reading victim's private repositories."),
N("A110","A110/diff.patch:9","Container runtime supplementary-group setup for processes inside containers; not an HTTP API access decision.",3),
N("A111","A111/diff.patch:1-40","Header-name constants in a Camel JIRA component library let HTTP headers override route parameters; library/integration flaw, not service REST API."),
r("A112",Y,"MISSING_AUTHENTICATION","NONE",Y,"UNCLEAR","NA","NO","MIDDLEWARE_FILTER",2,"A112/diff.patch:9-30","Backend API endpoints such as secret and service listings did not enforce authentication; unauthenticated callers could read cluster data. Diff shows only auth middleware tweak."),
]
w=csv.writer(open("codes_H2.csv","w",newline=""))
w.writerow("item_id,ac_relevant,ac_kind,principals_needed,observable_via_http,contract_operation,contract_security,policy_in_contract,fix_location,confidence,locators,rationale".split(","))
w.writerows(rows); print(len(rows))
