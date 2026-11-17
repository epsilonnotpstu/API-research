import csv
I="Q%d/impl/"; C="Q%d/contract/"
rows=[
(22,"DELIBERATE","SPECIFIC",3,"CommandTypeResource.java:30","swagger.json#/paths/~1commandtypes/post","@GET method on @Path(commandtypes) is an explicit declared handler; contract declares only POST for this path."),
(23,"DELIBERATE","SPECIFIC",2,"pkg/handler/eval.go:85-100,118-119","docs/api_docs/bundle.yaml#/definitions/evalResult/properties/flagID (line 1118-1121)","BlankResult is an explicit constructor for not-found flags with message; flagID defaults to 0. Contract states minimum 1 on evalResult.flagID."),
(24,"DELIBERATE","SPECIFIC",3,"gateway/server.go:579","swagger.yml:1009","Router explicitly registers /org/keys/{keyName}; contract explicitly names /tyk/orgs/keys/{keyID}."),
(25,"DELIBERATE","SPECIFIC",2,"http/server.go:590-591;http/handler/api/memfs.go:128","docs/swagger.json#/paths/~1api~1v3~1fs~1mem~1","Explicit v3.GET fs/mem to ListFiles and wildcard fs/mem/* to GetFile. Contract path with trailing slash is explicit (from @Router annotation)."),
(26,"DELIBERATE","GENERIC",3,"internal/router/answer_api_router.go:247;internal/base/server/http.go:83-86","docs/swagger.json#/paths/~1answer~1api~1v1~1tag/delete","DELETE tag is registered in router group with explicit MustAuthAndAccountAvailable middleware; contract operation just has no security entry (silence)."),
(27,"DELIBERATE","SPECIFIC",2,"internal/relationtuple/definitions.go:458-490;internal/persistence/sql/relationtuples.go:218-232","spec/api.json:507,538-540","FromURLQuery uses Get without a required check; persistence has explicit if-nonempty filter branches for namespace like object/relation. Contract has required:true plus prose."),
(28,"DELIBERATE","SPECIFIC",2,"internal/api/video.go:38-39","internal/api/swagger.json#/paths/~1api~1v1~1videos~1{hash}~1{token}~1{format}/get/parameters/0","Route declares :hash and handler reads c.Param(hash). Contract parameter entry explicitly named thumb (annotation Param thumb)."),
(29,"ACCIDENTAL",  "SPECIFIC",2,"http/handler/api/restream.go:189-191;restream/restream.go:842-845","docs/swagger.yaml:2178-2181","UpdateProcess error (unknown ID, plain fmt.Errorf) is mapped by blanket catch-all to 400; no discrimination of not-found despite @Failure 404 annotation. Contract lists 404 explicitly."),
(30,"DELIBERATE","GENERIC",3,"SearchApiV2Manager.java:240-256","openapi-user.yaml:625-642","Explicit try/catch with comment around getParameterNames writes INVALID_REQUEST 400 before dispatch. /auth/me responses just omit 400 (silence)."),
(31,"DELIBERATE","SPECIFIC",2,"controller_backyard/siteinfo_controller.go:43-46;router/answer_api_router.go:224","docs/swagger.yaml:1717-1726","GetInterface is a plain read handler calling service without any bind; contract has an explicit required body param with AddCommentReq (copy-paste annotation, but explicit)."),
(32,"DELIBERATE","SPECIFIC",3,"pkg/handler/enricher.go:110-122,191-193;pkg/handler/enricher.go:45-47","docs/api_docs/bundle.yaml:1349-1357","effectiveEnricherModels calls enabledEnrichers over globals plus flag enrichers; comments state disabled enrichers are not listed. Contract prose describes enabled built-ins only."),
(33,"DELIBERATE","SPECIFIC",2,"apiserver/.../persistence/ProjectQueryManager.java:285-304","apiserver/.../resources/v1/ProjectResource.java:735-738","Explicit else branch sets parent to null when transient parent absent/null; resource layer has no preservation. Contract prose explicitly says omitted/null leaves parent unchanged."),
(34,"DELIBERATE","SPECIFIC",2,"nifi-web-api/.../ControllerServiceResource.java:402-421","nifi-web-api/.../ControllerServiceResource.java:385-388","Method explicitly fetches getControllerServiceReferencingComponents and returns that entity; annotation response=ControllerServiceEntity (copy of getControllerService) is explicit."),
(35,"DELIBERATE","SPECIFIC",2,"internal/api/labels_search.go:57-69","internal/api/swagger.json#/paths/~1api~1v1~1labels/get/responses/200","Handler explicitly returns search.Labels result via c.JSON; slice/array output. Contract declares explicit schema search.Label."),
(36,"ACCIDENTAL","SPECIFIC",2,"SessionResource.java:103-113 vs 65,89","swagger.json:961-962","POST add() logs login and returns user but never calls setAttribute(USER_ID_KEY), unlike GET paths; looks like an omission. Contract summary says Create a new Session."),
(37,"DELIBERATE","SPECIFIC",2,"internal/relationtuple/definitions.go:487-489;internal/persistence/sql/relationtuples.go:218-223","spec/api.json:531-544,507","Query uses Get without required checks and persistence adds object/relation filters only if nonempty (explicit branches). Contract has required:true, contradicting its prose."),
(38,"ACCIDENTAL","SPECIFIC",2,"storage/handler.go:85-102,126",".schema/api.swagger.json#/paths/~1engines~1acp~1ory~1{flavor}~1policies/get/responses/200","ListByQuery declares var res Policies (nil) and appends only matches; no empty-slice initialisation, so JSON null. Contract: Policies is an array."),
(39,"DELIBERATE","SPECIFIC",3,"UserResource.java:42-43","swagger.json:754-769","Method explicitly typed Collection<User>. Contract 200 schema explicitly an array of Position."),
(40,"ACCIDENTAL","SPECIFIC",2,"pkg/handler/crud.go:664-674","docs/api_docs/bundle.yaml:528-540","DeleteConstraint deletes by constraintID only; flagID is parsed but used just for commit/notification, no membership check. Contract nests path under required flagID."),
(41,"ACCIDENTAL","GENERIC",2,"http/api/process.go:85-100 (Unmarshal omits PurgeOnDelete; Marshal at 98 copies it)","docs/swagger.yaml:704-705","Unmarshal cleanup conversion lacks PurgeOnDelete while Marshal copies it, an asymmetric omission. Contract only has shared schema field purge_on_delete; reflection claim is inferred."),
(42,"ACCIDENTAL","SPECIFIC",2,"pkg/handler/crud.go:573-583","docs/api_docs/bundle.yaml:402-415","DeleteSegment deletes by segmentID only; flagID used only for commit/notification, no membership constraint. Contract nests under required flagID."),
]
items=[r['item_id'] for r in csv.DictReader(open('items.csv'))]
d={ "Q%d"%r[0]:r for r in rows}
with open('codes_K5.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow("item_id,divergence_kind,contract_specificity,confidence,impl_locators,contract_locators,rationale".split(','))
    for i in items:
        r=d[i]; n=r[0]
        il=";".join("Q%d/impl/%s"%(n,p.strip()) for p in r[4].split(';'))
        cl="Q%d/contract/%s"%(n,r[5]) if True else ""
        w.writerow([i,r[1],r[2],r[3],il,cl,r[6]])
print(len(items))
