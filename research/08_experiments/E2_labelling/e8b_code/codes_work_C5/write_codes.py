import csv
from pathlib import Path

rows=[]
def loc(item,part,refs):
    found=[]
    for name,line in refs:
        matches=list(Path(item,part).rglob(name))
        assert len(matches)==1,(item,part,name,matches)
        found.append(str(matches[0])+(':' if part=='impl' else '#')+str(line))
    return ';'.join(found)
def add(item,kind,specificity,confidence,impl,contract,why):
    assert len(why.split())<=40,(item,len(why.split()))
    rows.append(dict(item_id=item,divergence_kind=kind,contract_specificity=specificity,confidence=confidence,
        impl_locators=loc(item,'impl',impl),contract_locators=loc(item,'contract',contract),rationale=why))

add('W01','DELIBERATE','SPECIFIC',3,
    [('ProductReviewsProvider.java',113),('PaginationConfig.java',19),('application.yaml',447)],
    [('product-review-openapi.yaml',67)],
    'The null-size branch explicitly selects the configured reviews page size of 10; the operation schema explicitly defaults size to 50.')
add('W02','DELIBERATE','SPECIFIC',3,
    [('LevelRefsController.java',139),('LocationLevelRefs.java',42),('LocationLevelRef.java',56),('LocationLevelRef.java',63)],
    [('LevelRefsController.java',113)],
    'The handler explicitly retrieves and formats LocationLevelRefs, whose entries declare level identifiers and effective dates; success annotations explicitly select LocationLevels.')
add('W03','DELIBERATE','SPECIFIC',2,
    [('GroupsResourceImpl.java',1013),('GroupsResourceImpl.java',1095)],
    [('openapi.json',2059)],
    'An explicit trim().isEmpty() guard restricts name assignment to blank supplied names, excluding nonblank names. The header description explicitly specifies the artifact name. Classification concerns guard structure, not historical intent.')
add('W04','ACCIDENTAL','SPECIFIC',3,
    [('WaterUserCreateController.java',85)],
    [('WaterUserCreateController.java',60)],
    'The omitted query value goes directly to Boolean.parseBoolean without a null/default branch, yielding false. The operation description explicitly promises default true.')
add('W05','DELIBERATE','SPECIFIC',3,
    [('handler.go',218)],
    [('api.swagger.json',1610)],
    'GetGroup explicitly constructs an authorization request with action get. The GET operation description explicitly illustrates a policy with action create.')
add('W06','DELIBERATE','SPECIFIC',3,
    [('ToolsApiServiceImpl.java',248),('ToolsApiServiceImpl.java',443)],
    [('openapi.yaml',920)],
    'The DOCKERFILE response explicitly uses the single ToolContainerfile as its JSON entity; the operation response schema explicitly declares an array of those objects.')
add('W07','DELIBERATE','GENERIC',3,
    [('project.go',38),('project.go',74)],
    [('swagger.yaml',108),('swagger.yaml',768)],
    'The request struct explicitly binds ProjectName to project_name. The contract name property is inherited through the shared Project model, rather than specified separately for this request.')
add('W08','DELIBERATE','SPECIFIC',3,
    [('handler.go',60),('handler.go',263),('warden_local.go',68)],
    [('api.swagger.json',1675)],
    'DeleteGroup explicitly passes Scope, defined as hydra.warden.groups, into token introspection. The operation security declaration explicitly requires hydra.groups.')
add('W09','DELIBERATE','SPECIFIC',3,
    [('ToolsApiServiceImpl.java',185),('ToolsApiServiceImpl.java',428),('SourceFile.java',62)],
    [('ToolsApi.java',146),('ToolsApi.java',152)],
    'The relative-path branch explicitly returns a SourceFile JSON entity with content and path fields. The dedicated success annotation specifies ToolDescriptor.')
add('W10','UNCLEAR','SPECIFIC',2,
    [('OfficeController.java',110),('XMLv1.java',67),('XMLv1Office.java',9)],
    [('OfficeController.java',88),('CsvV1Office.java',12)],
    'Wrapper annotations express the proposed structure, but JAXBContext uses dtoList.getClass(), not the wrapper type, and marshalling failures become server errors. Successful XML output matching Y is therefore not established by these artifacts.')
add('W11','ACCIDENTAL','GENERIC',3,
    [('ArtifactsResourceImpl.java',591)],
    [('openapi.json','/paths/~1artifacts~1{artifactId}~1versions~1{version}~1meta/put/requestBody'),('openapi.json',1712)],
    'The version-update DTO copies name and description but omits labels before storage. Labels are exposed through the shared EditableMetaData request schema, without a dedicated version-update statement.')
add('W12','DELIBERATE','SPECIFIC',2,
    [('GroupsResourceImpl.java',232),('GroupsResourceImpl.java',239),('GroupsResourceImpl.java',1370),('GroupsResourceImpl.java',1381)],
    [('openapi.json',1764)],
    'The update path explicitly guards name assignment with trim().isEmpty(), excluding nonblank headers from version metadata. The header description explicitly specifies the new version name. Historical intent is unavailable.')
add('W13','DELIBERATE','SPECIFIC',3,
    [('MetadataResource.java',345),('MetadataResource.java',354),('PipHelper.java',52)],
    [('MetadataResource.java',328)],
    'output=json explicitly selects a dependency map as the JSON response entity. The operation response annotation explicitly declares application/json with String schema.')
add('W14','DELIBERATE','SPECIFIC',3,
    [('handler.go',60),('handler.go',106),('warden_local.go',68)],
    [('api.swagger.json',1527)],
    'The listing handler explicitly passes hydra.warden.groups to token introspection. The GET operation security declaration explicitly requires hydra.groups.')
add('W15','DELIBERATE','SPECIFIC',3,
    [('ProductsEndpoint.java',62)],
    [('product-openapi.yaml',125)],
    'The endpoint explicitly names the bound query parameter sort_attribute; the operation explicitly names it sortAttribute.')
add('W16','DELIBERATE','SPECIFIC',3,
    [('ProductReviewsProvider.java',64),('NotFoundException.java',6),('GlobalExceptionHandler.java',257)],
    [('product-review-openapi.yaml',256)],
    'The absent-review branch explicitly throws NotFoundException, whose 404 annotation is resolved by the handler. The dedicated 200 description explicitly promises all-null fields when the user has no review.')
add('W17','ACCIDENTAL','SPECIFIC',3,
    [('WorkflowResource.java',829),('EntryDAO.java',319)],
    [('WorkflowResource.java',822)],
    'Only the upper bound is clamped; no lower-bound validation prevents zero reaching setMaxResults. The operation parameter explicitly restricts limit to range[1,100].')
add('W18','ACCIDENTAL','SPECIFIC',2,
    [('immutable.go',83),('immutable.go',90),('immutable.go',100),('immutable.go',104)],
    [('swagger.yaml',2463),('swagger.yaml',2473),('swagger.yaml',6057)],
    'The update copies body metadata and uses its ID for access and update, without reading the path rule ID. This is a wrong-source-ID omission; the contract explicitly identifies the rule through that path parameter.')
add('W19','DELIBERATE','SPECIFIC',3,
    [('LoanDisbursementDetailsAssembler.java',39),('FromJsonHelper.java',244),('JsonParserHelper.java',523)],
    [('LoansApiResourceSwagger.java',1806)],
    'The selected date parser explicitly accepts only JSON primitives and converts strings using dateFormat and locale; arrays bypass it. The dedicated disbursement request field explicitly illustrates an array date.')
add('W20','DELIBERATE','SPECIFIC',3,
    [('handler.go',256)],
    [('api.json',1082)],
    'GetLoginRequest explicitly coalesces login_challenge with challenge before lookup. The operation explicitly marks login_challenge required.')
add('W21','ACCIDENTAL','SPECIFIC',3,
    [('DockerRepoResource.java',791),('EntryDAO.java',319)],
    [('DockerRepoResource.java',786)],
    'The upper-bound-only clamp leaves zero unchanged and forwards it to setMaxResults; lower-bound handling is absent. The operation explicitly declares range[1,100].')
add('W22','DELIBERATE','GENERIC',3,
    [('repository.go',45),('repository.go',128),('repository.go',145)],
    [('swagger.yaml',780),('swagger.yaml',2659)],
    'The response model explicitly declares id as int64 without string encoding and returns it as JSON. The contract string type is inherited from the shared Repository schema.')
add('W23','DELIBERATE','SPECIFIC',2,
    [('GroupsResourceImpl.java',975),('GroupsResourceImpl.java',1257),('GroupsResourceImpl.java',1325)],
    [('openapi.json',1431)],
    'The CREATE_VERSION fallback reaches a storage call with dryRun explicitly hardcoded false. The contract explicitly promises no changes for dryRun=true. This coding reflects the literal flag choice, not a claim about intent.')
add('W24','DELIBERATE','SPECIFIC',3,
    [('ProductsEndpoint.java',56)],
    [('product-openapi.yaml',116),('product-openapi.yaml',123)],
    'The query binding explicitly supplies desc as its default; the operation parameter schema explicitly supplies asc.')
add('W25','DELIBERATE','GENERIC',2,
    [('BusinessDateApiResource.java',85),('BusinessDateData.java',33),('GoogleGsonSerializerHelper.java',112),('LocalDateAdapter.java',38)],
    [('BusinessDateApiResourceSwagger.java',39)],
    'The registered LocalDateAdapter explicitly constructs a year/month/day array for the returned LocalDate. The string date type comes from the shared BusinessDateResponse model rather than dedicated operation prose.')
add('W27','DELIBERATE','SPECIFIC',3,
    [('LocationKindController.java',112),('CwmsIdLocationKind.java',41),('CwmsIdLocationKind.java',51)],
    [('LocationKindController.java',85)],
    'The handler explicitly formats a CwmsIdLocationKind list, with kebab-case location-id and location-kind-id accessors. The operation success annotation explicitly specifies a Location array.')
add('W28','DELIBERATE','SPECIFIC',3,
    [('LoanApplicationCommandFromApiJsonHelper.java',368),('JsonParserHelper.java',368),('JsonParserHelper.java',440)],
    [('LoansApiResourceSwagger.java',663)],
    'The selected date parser explicitly requires a primitive and parses its string using format/locale. Arrays bypass the guard and return null for required-field validation. The dedicated request example explicitly shows an array.')
add('W29','DELIBERATE','SPECIFIC',3,
    [('LoanScheduleAssembler.java',271),('FromJsonHelper.java',214),('JsonParserHelper.java',390),('JsonParserHelper.java',523)],
    [('LoansApiResourceSwagger.java',1421)],
    'The selected parser explicitly gates date extraction on isJsonPrimitive; an array leaves the parsed date null. The dedicated PostLoansRequest field explicitly illustrates an array date.')
add('W30','DELIBERATE','SPECIFIC',3,
    [('handler.go',757)],
    [('api.json',1273)],
    'GetLogoutRequest explicitly coalesces logout_challenge with challenge and forwards the result to lookup. The operation explicitly marks logout_challenge required.')
add('W32','DELIBERATE','SPECIFIC',3,
    [('ProductReviewsProvider.java',54),('ProductReviewValidator.java',43),('NotFoundException.java',6),('GlobalExceptionHandler.java',257)],
    [('product-review-openapi.yaml',132)],
    'Product existence validation explicitly throws NotFoundException and its annotation resolves to 404. The operation 400 description explicitly includes product not found.')
add('W33','DELIBERATE','SPECIFIC',3,
    [('handler.go',60),('handler.go',319),('warden_local.go',68)],
    [('api.swagger.json',1726)],
    'AddGroupMembers explicitly passes hydra.warden.groups to token introspection. The operation security declaration explicitly requires hydra.groups.')
add('W34','DELIBERATE','SPECIFIC',3,
    [('handler.go',60),('handler.go',375),('warden_local.go',68)],
    [('api.swagger.json',1782)],
    'The member-removal handler explicitly passes hydra.warden.groups to token introspection. The operation security declaration explicitly requires hydra.groups.')
add('W35','DELIBERATE','SPECIFIC',3,
    [('handler.go',481)],
    [('api.json',918)],
    'GetConsentRequest explicitly coalesces consent_challenge with challenge before lookup. The operation explicitly marks consent_challenge required.')
add('W36','DELIBERATE','SPECIFIC',3,
    [('handler.go',60),('handler.go',162),('warden_local.go',68)],
    [('api.swagger.json',1576)],
    'CreateGroup explicitly passes hydra.warden.groups to token introspection. The operation security declaration explicitly requires hydra.groups.')
add('W37','DELIBERATE','GENERIC',2,
    [('BusinessDateApiResource.java',71),('BusinessDateData.java',33),('GoogleGsonSerializerHelper.java',112),('LocalDateAdapter.java',38)],
    [('BusinessDateApiResourceSwagger.java',39)],
    'The returned dates use a registered adapter explicitly constructing year/month/day arrays. The contract string type comes from the shared BusinessDateResponse model rather than a dedicated list-operation statement.')
add('W39','DELIBERATE','SPECIFIC',3,
    [('ApiAlertsResource.java',176),('ApiAlertsResource.java',189)],
    [('ApiAlertsResource.java',177),('ApiAlertsResource.java',180)],
    'The events method explicitly checks API_ALERT with READ in its permission annotation; its operation description explicitly requires MANAGEMENT_ALERT[READ].')
add('W41','DELIBERATE','SPECIFIC',3,
    [('GroupsResourceImpl.java',1044),('AvroCompatibilityChecker.java',19),('AvroCompatibilityChecker.java',46),('HttpStatusCodeMap.java',124),('CoreRegistryExceptionMapperService.java',55)],
    [('openapi.json','/paths/~1groups~1{groupId}~1artifacts~1{artifactId}~1versions/post/responses'),('openapi.json','/paths/~1groups~1{groupId}~1artifacts~1{artifactId}~1versions/post/description')],
    'Avro parsing failures are explicitly wrapped as UnprocessableSchemaException and mapped to 422. The operation explicitly documents 400, 404, 409, and 500 as error statuses.')

expected=[r['item_id'] for r in csv.DictReader(open('items.csv',newline=''))]
assert [r['item_id'] for r in rows]==expected
with open('codes_C5.csv','w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print('Wrote',len(rows),'ordered rows to codes_C5.csv')
