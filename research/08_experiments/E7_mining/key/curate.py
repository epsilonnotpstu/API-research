#!/usr/bin/python3
"""Explicit manual acceptance decisions and exact-parent evidence selectors."""
import json
from pathlib import Path
import re
import runpy
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/'mine.py'))
git=m['git'];safe=m['safe'];rows=m['load_sources']();accepted=[]

def accept(repo,rank,operation,x,y,direction,kind,family,contract,implementation,route=(),helpers=(),confidence=3):
    r=dict(next(r for r in rows if r['repo']==repo and r['rank']==rank))
    tree=git(repo,'ls-tree','-r','--name-only',r['parent_commit']).decode().splitlines()
    checks={};evidence={}
    for role,selectors in [('contract',contract),('implementation',implementation),('route',route)]:
        checks[role]=[]
        for suffix,pattern in selectors:
            paths=[p for p in tree if p.endswith(suffix)]
            assert len(paths)==1,(repo,rank,suffix,len(paths))
            p=paths[0];text=safe(git(repo,'show',r['parent_commit']+':'+p).decode('utf-8'))
            hits=[i for i,l in enumerate(text.splitlines(),1) if re.search(pattern,l)]
            assert hits,(repo,rank,suffix,'missing evidence selector')
            checks[role].extend(r['parent_commit']+':'+p+':'+str(i) for i in hits)
            evidence[p]={'parent_lines':hits,'parent_numbered_excerpt':'\n'.join(str(i)+': '+l for i,l in enumerate(text.splitlines(),1) if any(abs(i-h)<=4 for h in hits))}
    helper_paths=[]
    for suffix in helpers:
        paths=[p for p in tree if p.endswith(suffix)];assert len(paths)==1,(repo,suffix)
        helper_paths.extend(paths)
    r.update(item_id='N'+str(len(accepted)+1).zfill(3),set='new',operation=operation,proposition=operation+': contract says '+x+'; implementation does '+y,
        truth_direction=direction,confidence=confidence,contract_kind=kind,mismatch_type=family.split('.')[0],fix_family=family,
        proposition_check=json.dumps(checks,separators=(',',':')),evidence=json.dumps({'parent':evidence,'patch':'key/review_evidence/'+r['candidate_id']+'.diff','gate':'Manual static parent contract and implementation comparison; corresponding patch resolves this proposition; no runtime execution.'},ensure_ascii=False),helper_paths=helper_paths,
        inference_notes='⚠️ Static framework/library semantics inferred; no upstream code or runtime traffic executed.')
    accepted.append(r)

B='basyx.submodelrepository/basyx.submodelrepository-http/src/main/java/org/eclipse/digitaltwin/basyx/submodelrepository/http/'
A='basyx.aasrepository/basyx.aasrepository-http/src/main/java/org/eclipse/digitaltwin/basyx/aasrepository/http/'
L='basyx.aasdiscoveryservice/basyx.aasdiscoveryservice-http/src/main/java/org/eclipse/digitaltwin/basyx/aasdiscoveryservice/http/'
accept('basyx-java-server-sdk',5,'PUT /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/attachment','a successful file upload returns 204','return 200 after storing the file','IMPL','annotations','response_status.file_upload',[(B+'SubmodelRepositoryHTTPApi.java',r'responseCode = "204".*Submodel element updated|attachment.*RequestMethod.PUT')],[(B+'SubmodelRepositoryApiHTTPController.java',r'HttpStatus.OK|repository.setFileValue')])
accept('basyx-java-server-sdk',7,'PUT /shells/{aasIdentifier}/asset-information','a successful Asset Information update returns 204','return 200 after setting the Asset Information','IMPL','annotations','response_status.asset_information',[(A+'AasRepositoryHTTPApi.java',r'responseCode = "204".*Asset Information|asset-information.*RequestMethod.PUT')],[(A+'AasRepositoryApiHTTPController.java',r'putAssetInformationAasRepository|aasRepository.setAssetInformation|HttpStatus.OK')])
accept('basyx-java-server-sdk',15,'GET /lookup/shells','assetIds is optional','call stream on the nullable assetIds argument','IMPL','annotations','optional_query_parameter.asset_ids',[(L+'LookupApi.java',r'RequestParam\(value = "assetIds", required = false')],[(L+'LookupApiController.java',r'assetIds.stream\(')])
C='cwms-data-api/src/main/java/cwms/cda/api/'
accept('cwms-data-api',9,'GET /blobs/{blob-id}','the blob-id query parameter overrides the path identifier','read clob-id to choose the overriding identifier','IMPL','annotations','query_parameter_name.blob_id',[(C+'BlobController.java',r'OpenApiParam\(name = BLOB_ID, description = "If this _query_')],[(C+'BlobController.java',r'idQueryParam = ctx.queryParam\(CLOB_ID\)')],[(C+'Controllers.java',r'final String (?:BLOB_ID|CLOB_ID) =')])
G='gravitee-apim-rest-api/gravitee-apim-rest-api-management/gravitee-apim-rest-api-management-rest/src/main/java/io/gravitee/rest/api/management/rest/resource/organization/RoleResource.java'
accept('gravitee-api-management',20,'DELETE /organizations/{organizationId}/configuration/rolescopes/{scope}/roles/{role}','204 carries an application/json RoleEntity','complete the role deletion through a void method','SPEC','annotations','response_body.role_deletion',[(G,r'content = @Content.*RoleEntity.class|responseCode = "204"')],[(G,r'public void deleteRole|roleService.delete')],confidence=2)

accept('basyx-java-server-sdk',10,'POST /submodels/{submodelIdentifier}/submodel-elements','201 contains a JSON SubmodelElement','return a bodyless 201 after creating the element','IMPL','annotations','response_body.created_submodel_element',[(B+'SubmodelRepositoryHTTPApi.java',r'responseCode = "201".*Submodel element created')],[(B+'SubmodelRepositoryApiHTTPController.java',r'new ResponseEntity<SubmodelElement>\(HttpStatus.CREATED\)|postSubmodelElementSubmodelRepo')])
accept('basyx-java-server-sdk',27,'POST /shells/{aasIdentifier}/submodel-refs','creating an already existing resource receives 409','append a duplicate submodel reference and return 201','IMPL','annotations','response_status.duplicate_submodel_reference',[(A+'AasRepositoryHTTPApi.java',r'responseCode = "409"')],[(A+'AasRepositoryApiHTTPController.java',r'addSubmodelReference|new ResponseEntity<Reference>\(body, HttpStatus.CREATED\)'),('basyx.aasservice/basyx.aasservice-backend-inmemory/src/main/java/org/eclipse/digitaltwin/basyx/aasservice/backend/InMemoryAasService.java',r'aas.getSubmodels\(\).add\(submodelReference\)')],confidence=2)
accept('cwms-data-api',8,'GET /projects/{office}/{project-id}/water-user/{water-user}/contracts/{contract-name}','the resource path contains water-users','register the controller under a path containing water-user','SPEC','annotations','operation_path.water_contract',[(C+'watersupply/WaterContractController.java',r'path = "/projects/.*water-users/')],[('cwms-data-api/src/main/java/cwms/cda/ApiServletRouteConfiguration.java',r'addWaterContractHandlers\(format|new WaterContractController')],helpers=(C+'watersupply/WaterSupplyControllerBase.java',))
F='fineract-provider/src/main/java/org/apache/fineract/portfolio/loanaccount/'
accept('fineract',24,'GET /loans/{loanId}','annualInterestRate is an integer','represent annualInterestRate with a BigDecimal in the serialized loan data','SPEC','annotations','response_type.annual_interest_rate',[(F+'api/LoansApiResourceSwagger.java',r'public Integer annualInterestRate;')],[(F+'data/LoanAccountData.java',r'private BigDecimal annualInterestRate;'),(F+'api/LoansApiResource.java',r'return.*serialize|GetLoansLoanIdResponse.class')],confidence=2)
N='model/src/main/java/org/projectnessie/'
accept('nessie',4,'GET /v2/trees/{ref}','200 contains a Reference object','return a SingleReferenceResponse wrapping the reference property','SPEC','annotations','response_body.reference_wrapper',[(N+'api/v2/http/HttpTreeApi.java',r'schema = @Schema\(implementation = Reference.class\)')],[('servers/rest-services/src/main/java/org/projectnessie/services/rest/RestV2TreeResource.java',r'public SingleReferenceResponse getReferenceByName|\.reference\(tree\(\).getReferenceByName'),(N+'model/SingleReferenceResponse.java',r'Reference getReference\(\)')])

K='rest-api/resources/src/main/java/org/eclipse/kapua/app/api/resources/v1/resources/'
accept('kapua',17,'GET /{scopeId}/devices/{deviceId}/packages','the response model is DeviceSnapshots','return DevicePackages from the installed-package service','SPEC','annotations','response_model.device_packages',[(K+'DeviceManagementPackages.java',r'ApiOperation.*response = DeviceSnapshots.class')],[(K+'DeviceManagementPackages.java',r'public DevicePackages get|return packageService.getInstalled')])
accept('kapua',17,'POST /{scopeId}/devices/{deviceId}/requests','the JSON response model is DeviceCommandOutput','return a JsonGenericResponseMessage wrapping the generic device response','SPEC','annotations','response_model.device_request',[(K+'DeviceManagementRequestsJson.java',r'ApiOperation.*response = DeviceCommandOutput.class')],[(K+'DeviceManagementRequestsJson.java',r'public JsonGenericResponseMessage sendRequest|return new JsonGenericResponseMessage')],helpers=(K+'DeviceManagementRequests.java',K+'model/device/management/JsonGenericResponseMessage.java',K+'model/device/management/JsonGenericRequestMessage.java'))
P='src/main/java/uk/gov/pay/api/'
accept('pay-publicapi',7,'GET /v1/refunds','the navigation property is named _links','expose navigation through the unannotated getLinks getter as links','IMPL','annotations','semantic_property_name',[(P+'model/search/card/SearchRefundsResults.java',r'ApiModelProperty\(name = "_links"\)')],[(P+'model/search/card/SearchRefundsResults.java',r'public SearchNavigationLinks getLinks\(')],[(P+'resources/SearchRefundsResource.java',r'@Path\("/v1/refunds"\)')],helpers=(P+'model/links/SearchNavigationLinks.java',))
S='src/main/java/io/strimzi/kafka/bridge/http/'
accept('strimzi-kafka-bridge',13,'POST /topics/{topicname}','offsets entries use the OffsetRecordSent schema','put error_code and message objects into offsets for failed records','SPEC','spec_file','response_schema.producer_error_entry',[('src/main/resources/openapi.json',r'"\$ref": "#/components/schemas/OffsetRecordSent"')],[(S+'HttpSourceBridgeEndpoint.java',r'offset = error.toJson\(\)|results.add\(new HttpBridgeResult<>\(new HttpBridgeError'),(S+'model/HttpBridgeError.java',r'json.put\("error_code"|json.put\("message"')],helpers=(S+'model/HttpBridgeResult.java',S+'HttpUtils.java'))
E='src/main/kotlin/eu/europa/ec/eudi/verifier/endpoint/adapter/input/web/UtilityApi.kt'
accept('eudi-srv-verifier-endpoint',16,'POST /utilities/validations/msoMdoc/deviceResponse','bad requests receive 400 with a JSON validation-failure body','throw an unhandled IllegalArgumentException when device_response is absent','BOTH','spec_file','required_form_field.error_response',[('src/main/resources/public/openapi.json',r'"MsoMdocDeviceResponseValidationFailure"|"#/components/schemas/MsoMdocDeviceResponseValidationFailure"')],[(E,r'requireNotNull\(it\).*device_response|recover = \{ error -> badRequest\(\).json\(\).bodyValueAndAwait\(error\)')],confidence=2)

D='signals/commands/policies/src/main/java/org/eclipse/ditto/signals/commands/policies/modify/'
accept('ditto',22,'PUT /policies/{policyId}/entries/{label}/subjects','creating Subjects receives 201 with a Subjects body','construct a bodyless 204 response for successful Subjects modification','SPEC','spec_file','response_status.subjects_creation',[('documentation/src/main/resources/openapi/ditto-api-2.yml',r'description: The Subjects were successfully created\.')],[(D+'ModifySubjectsResponse.java',r'return new ModifySubjectsResponse\(policyId, label, HttpStatusCode.NO_CONTENT'),('services/policies/persistence/src/main/java/org/eclipse/ditto/services/policies/persistence/actors/policy/PolicyPersistenceActor.java',r'notifySender\(ModifySubjectsResponse.of')],[('services/gateway/endpoints/src/main/java/org/eclipse/ditto/services/gateway/endpoints/routes/policies/PolicyEntriesRoute.java',r'ModifySubjects.of\(policyId')])

if __name__=='__main__':
    m['dump'](m['HERE']/'key/new_accepted.json',accepted)
    print('Explicitly curated new acceptances:',len(accepted))
