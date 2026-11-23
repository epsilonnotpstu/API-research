import csv
NA="NA"
def y(i,kind,pr,obs,co,cs,pol,fl,c,loc,r): return [i,"YES",kind,pr,obs,co,cs,pol,fl,c,loc,r]
def n(i,c,loc,r): return [i,"NO"]+[NA]*8+[c,loc,r]
rows=[
y("A033","OBJECT_LEVEL","TWO_SAME_ROLE","YES","ABSENT",NA,"NO","OTHER",1,"A033/diff.patch:8-14","Advisory: authenticated user views another account's addresses via addressId. Provided diff only adds a POST-method check to an unrelated change-tracking comment command, so advisory and fix do not match."),
n("A034",0,"","") ,
]
rows[1]=y("A034","MISSING_AUTHENTICATION","NONE","YES","ABSENT",NA,"NO","MIDDLEWARE_FILTER",2,"A034/diff.patch (src/mcp/sse_security.go); contract swagger.json has no MCP endpoints","Anyone able to reach the MCP SSE listener, including browser pages via DNS rebinding, could list and call process-control tools without any credential; REST token middleware did not cover it.")
rows+=[
y("A035","MISSING_AUTHENTICATION","NONE","YES","ABSENT",NA,"NO","MIDDLEWARE_FILTER",3,"A035/diff.patch:8-11","GET /clusters/kubeconfig/{name} was registered in the white (unauthenticated) route group; an anonymous caller could download a cluster kubeconfig. Fix moves it under AuthScope."),
y("A036","OBJECT_LEVEL","TWO_SAME_ROLE","YES","PRESENT","DECLARED","NO","OTHER",2,"A036/diff.patch:8-12,41-62; contract answer accept POST (path redacted, docs/swagger.json:1672)","A user with minimal rank could accept an answer, including their own, on another user's question; fix changes the rank.answer.accept threshold via config migration."),
y("A037","PROPERTY_LEVEL","ONE","YES","PRESENT","NOT_DECLARED","NO","SERVICE_LOGIC",3,"A037/diff.patch:5-16,62-100; contract v0_swagger.json:1370 PUT /user/{id}","Any authenticated non-admin could PUT their own profile with IsAdmin true and become admin; protected fields were not pinned."),
y("A038","PROPERTY_LEVEL","ONE","YES","UNCLEAR",NA,"NO","SERVICE_LOGIC",2,"A038/diff.patch:5-20","A user submitting a workflow under Strict/Secure template referencing could set ArtifactGC.podSpecPatch, serviceAccountName or podMetadata, bypassing the field allow-list. Workflow submit path is cut off in truncated contract."),
y("A039","FUNCTION_LEVEL","TWO_ROLES","YES","PRESENT","DECLARED","NO","SERVICE_LOGIC",2,"A039/diff.patch:20-40; contract swagger.json:2321 /projects/{id}","A user explicitly shared read-only on a child project but with higher inherited permission on the parent received the higher permission on the child, so could modify, delete or re-share it."),
y("A040","TENANT_ISOLATION","ONE","YES","PRESENT","NOT_DECLARED","NO","HANDLER",2,"A040/diff.patch:30-108 (getAppEnforceRBAC now returns project); contract assets/swagger.json:559","API server did not enforce the AppProject sourceNamespaces restriction, so a user could act on applications in namespaces outside their project's allowed ones."),
y("A041","MISSING_AUTHENTICATION","NONE","YES","ABSENT",NA,"NO","SERVICE_LOGIC",3,"A041/diff.patch:30-60","Android Pub/Sub status-report handler skipped authentication, so an unauthenticated request carrying a DELETED notification could unenroll a device; fix authenticates first."),
y("A042","TENANT_ISOLATION","TWO_SAME_ROLE","YES","ABSENT",NA,"NO","DATA_QUERY",2,"A042/diff.patch (execution_cache_store.go, mutation.go)","Cache key and lookup ignored namespace, so one tenant's steps could receive or seed another tenant's cached outputs. Cache webhook is not described in the KFP API contracts."),
y("A043","MISSING_AUTHENTICATION","NONE","YES","PRESENT","NOT_DECLARED","NO","HANDLER",3,"A043/diff.patch:8-45; contract server/openapi.yaml:1495 POST /webrtc/source-offer","POST /webrtc/source-offer accepted a WebRTC offer from anyone without the per-mount source password, letting an anonymous caller inject audio into any mount."),
y("A044","FUNCTION_LEVEL","TWO_ROLES","YES","ABSENT",NA,"NO","SERVICE_LOGIC",2,"A044/diff.patch:8-24","A team admin could set the scheme-admin role on a guest team member; the update now rejects guest members and guest-plus-admin combinations. Contract provided covers only boards."),
n("A045",2,"A045/diff.patch:8-75","Flaw is in JWT subject-token validation (issuer certificate, audience binding) of the token-exchange grant; token/signature validation is excluded by the coding rules."),
y("A046","MISSING_AUTHENTICATION","NONE","YES","PRESENT","NOT_DECLARED","NO","MIDDLEWARE_FILTER",2,"A046/diff.patch (router/echo.go); contract swagger.json:805 PUT /echo/like/{id}","PUT /echo/like/:id on the public router let anonymous callers increment fav_count of any echo, including private ones. Fix only adds rate limit and dedup; endpoint stays anonymous."),
y("A047","TENANT_ISOLATION","TWO_SAME_ROLE","UNCLEAR","ABSENT",NA,"NO","DATA_QUERY",2,"A047/diff.patch:20-30 (lt.tenant_id filter)","A tenant could supply another tenant's durable-task UUID to the gRPC WorkerStatus path and receive its event-log entries; lookup lacked a tenant filter. gRPC, not in the REST contract."),
n("A048",2,"","Flaw is cosign keyless signature verification ignoring subject/issuer regexp options, a signature-validation defect in admission policy, not an HTTP access decision."),
]
w=csv.writer(open("codes_H1.csv","w",newline=""))
w.writerow("item_id,ac_relevant,ac_kind,principals_needed,observable_via_http,contract_operation,contract_security,policy_in_contract,fix_location,confidence,locators,rationale".split(","))
w.writerows(rows)
print(len(rows))
