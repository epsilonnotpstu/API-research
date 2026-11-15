#!/usr/bin/python3
"""Explicit evidence-gated decisions; history and directions stay in key/."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import runpy

HERE=Path(__file__).resolve().parents[1]
M=runpy.run_path(str(HERE/'mine2.py'));git=M['git'];safe=M['safe']
rows=json.loads((HERE/'key/pool2_sources.json').read_text());accepted=[]
assert hashlib.sha256((HERE/'pool2.json').read_bytes()).hexdigest()==json.loads((HERE/'freeze2.json').read_text())['pool_sha256']

def accept(repo,rank,operation,x,y,direction,kind,family,contract,implementation,route=(),helpers=(),confidence=3):
    r=dict(next(r for r in rows if r['repo']==repo and r['rank']==rank))
    tree=git(repo,'ls-tree','-r','--name-only',r['parent_commit']).decode().splitlines();checks={};evidence={}
    for role,selectors in [('contract',contract),('implementation',implementation),('route',route)]:
        checks[role]=[]
        for suffix,pattern in selectors:
            paths=[p for p in tree if p.endswith(suffix)];assert len(paths)==1,(repo,rank,'ambiguous selector',suffix)
            path=paths[0];text=safe(git(repo,'show',r['parent_commit']+':'+path).decode('utf-8','replace'));lines=text.splitlines()
            hits=[i for i,line in enumerate(lines,1) if re.search(pattern,line)];assert hits,(repo,rank,'selector not found',suffix)
            checks[role].extend(r['parent_commit']+':'+path+':'+str(i) for i in hits)
            evidence[path]=dict(parent_lines=hits,parent_numbered_excerpt='\n'.join(str(i)+': '+line for i,line in enumerate(lines,1) if any(abs(i-h)<=5 for h in hits)))
    helper_paths=[]
    for suffix in helpers:
        paths=[p for p in tree if p.endswith(suffix)];assert len(paths)==1;helper_paths.extend(paths)
    patch=HERE/'key/review2_evidence'/(r['candidate_id']+'.diff');assert patch.exists()
    r.update(item_id='N46_'+str(len(accepted)+1).zfill(3),set='new',source_task='T46',operation=operation,proposition=operation+': contract says '+x+'; implementation does '+y,truth_direction=direction,confidence=confidence,contract_kind=kind,mismatch_type=family.split('.')[0],fix_family=family,proposition_check=json.dumps(checks,separators=(',',':')),evidence=json.dumps(dict(parent=evidence,patch=str(patch.relative_to(HERE)),patch_sha256=hashlib.sha256(patch.read_bytes()).hexdigest(),gate='Explicit static parent comparison and resolving patch; no runtime execution.'),ensure_ascii=False),helper_paths=helper_paths,inference_notes='⚠️ Framework dispatch, validation and serialization inferred statically; no upstream code executed.')
    accepted.append(r)

P='src/main/java/com/zufar/icedlatte/'
S='src/main/resources/api-specs/'
accept('Iced-Latte',36,'GET /api/v1/products','sort_attribute accepts averageRating and reviewsCount','lowercase those values before checking a case-sensitive allowed set and reject them','IMPL','spec_file','query_parameter_enum.product_sort_case',[(S+'product-openapi.yaml',r'Possible allowed values:.*averageRating')],[(P+'product/api/GetProductsRequestValidator.java',r'ALLOWED_SORT_ATTRIBUTES_VALUES|sortAttribute.toLowerCase|throw new GetProductsBadRequestException')],[(P+'product/endpoint/ProductsEndpoint.java',r'PRODUCTS_URL =|getProductsRequestValidator.validate|name = "sort_attribute"')])
accept('Iced-Latte',58,'POST /api/v1/products/rating','rating creation is routed under /api/v1/products/rating','route rating creation under /api/v1/rating/product','SPEC','spec_file','operation_path.rating_create',[(S+'rating-openapi.yaml',r'^  /api/v1/products/rating:')],[(P+'review/endpoint/RatingEndpoint.java',r'RATING_URL =|@PostMapping|addNewMarkToProduct')])
accept('Iced-Latte',58,'GET /api/v1/products/rating/{productId}','rating lookup is routed under /api/v1/products/rating/{productId}','route rating lookup under /api/v1/rating/product/{productId}','SPEC','spec_file','operation_path.rating_lookup',[(S+'rating-openapi.yaml',r'^  /api/v1/products/rating/\{productId\}:')],[(P+'review/endpoint/RatingEndpoint.java',r'RATING_URL =|@GetMapping|public ResponseEntity<List<RatingMark>>')])

AP='app/src/main/java/io/apicurio/registry/'
AS='common/src/main/resources/META-INF/openapi.json'
accept('apicurio-registry',1,'POST /groups/{groupId}/artifacts/{artifactId}/contract/status','status is a required non-null lifecycle string and invalid requests receive 400','dereference a null status before parameter validation and map the resulting exception to 500','IMPL','spec_file','required_body_property.contract_status',[(AS,r'"ContractStatusTransition": \{|"status"|"transitionContractStatus"')],[(AP+'rest/v3/impl/GroupsResourceImpl.java',r'public ContractMetadata transitionContractStatus|ContractStatus targetStatus = ContractStatus.valueOf'),(AP+'services/http/HttpStatusCodeMap.java',r'return HTTP_INTERNAL_ERROR')],confidence=2)
accept('apicurio-registry',6,'POST /groups/{groupId}/artifacts','X-Registry-Name and X-Registry-Description specify the submitted artifact metadata','omit those header values when an existing artifact takes the UPDATE or RETURN_OR_UPDATE branch','IMPL','spec_file','request_header.artifact_metadata_on_existing', [('app/src/main/resources-unfiltered/META-INF/resources/api-specifications/registry/v2/openapi.json',r'"name": "X-Registry-Name"|"name": "X-Registry-Description"|"operationId": "createArtifact"')],[(AP+'rest/v2/GroupsResourceImpl.java',r'return handleIfExists\(groupId|private ArtifactMetaData handleIfExists|return updateArtifactInternal\(groupId, artifactId, version, content')],confidence=2)
accept('apicurio-registry',36,'POST /groups/{groupId}/artifacts','dryRun=true produces no persistent changes','pass false to version creation when an existing artifact takes FIND_OR_CREATE_VERSION','IMPL','spec_file','dry_run.existing_artifact_version',[(AS,r'When set to `true`, the operation will not result in any changes|"operationId": "createArtifact"')],[(AP+'rest/v3/GroupsResourceImpl.java',r'case FIND_OR_CREATE_VERSION|return handleIfExistsReturnOrUpdate|artifactType, contentDto, metaData, branches, isDraftVersion, false, owner')],confidence=2)

C='cwms-data-api/src/main/java/cwms/cda/'
accept('cwms-data-api',26,'GET /timeseries/profile-instance/{location-id}/{parameter-id}/{version}/','start and end are optional with default years 1800 and 3000','require both query parameters before retrieving the profile instance','SPEC','annotations','required_query_parameter.profile_instance_window',[(C+'api/timeseriesprofile/TimeSeriesProfileInstanceController.java',r'Default is the year 1800|Default is the year 3000')],[(C+'api/timeseriesprofile/TimeSeriesProfileInstanceController.java',r'Instant startTime = requiredInstant|Instant endTime = requiredInstant'),(C+'api/Controllers.java',r'public static Instant requiredInstant|throw new RequiredQueryParameterException')],[(C+'ApiServlet.java',r'String timeSeriesProfileInstancePath|new TimeSeriesProfileInstanceController')])
accept('cwms-data-api',28,'GET /timeseries/recent','a successful JSON response is an array of Tsv objects','serialize an array of RecentValue objects','SPEC','annotations','response_schema.recent_timeseries',[(C+'api/TimeSeriesRecentController.java',r'@OpenApiContent\(isArray = true, from = Tsv.class')],[(C+'api/TimeSeriesRecentController.java',r'List<RecentValue> latestValues|Formats.format\(contentType, latestValues, RecentValue.class\)'),(C+'data/dto/RecentValue.java',r'public class RecentValue|JsonProperty'),(C+'data/dto/Tsv.java',r'public class Tsv|JsonProperty')],helpers=[C+'formatters/json/JsonV2.java'],confidence=2)
accept('cwms-data-api',36,'GET /forecast-spec','designator-mask filters forecast specification designators','read designator instead of designator-mask for the filter','IMPL','annotations','query_parameter_name.forecast_designator_mask',[(C+'api/ForecastSpecController.java',r'@OpenApiParam\(name = DESIGNATOR_MASK')],[(C+'api/ForecastSpecController.java',r'String designator = ctx.queryParam\(DESIGNATOR\)'),(C+'api/Controllers.java',r'String DESIGNATOR =|String DESIGNATOR_MASK =')],[(C+'ApiServlet.java',r'cdaCrudCache\("/forecast-spec/')])
accept('cwms-data-api',50,'GET /basins/{basin-id}','the application/json response is a single basin object','serialize the selected basin through a singleton list','IMPL','annotations','response_shape.basin_singleton_array',[(C+'api/BasinController.java',r'@OpenApiContent\(from = cwms.cda.data.dto.basin.Basin.class, type = Formats.JSON\)')],[(C+'api/BasinController.java',r'Formats.format\(contentType, Collections.singletonList\(basin\)'),(C+'formatters/json/JsonV2.java',r'format\(List<\? extends CwmsDTOBase>|writeValueAsString\(dtoList\)')],[(C+'ApiServlet.java',r'cdaCrudCache\("/basins/')],helpers=[C+'formatters/Formats.java'],confidence=2)

F='fineract-provider/src/main/java/org/apache/fineract/'
accept('fineract',4,'PUT /roles/{roleId}/permissions','permission-map values have string type','process the permission-map values as Boolean values','SPEC','annotations','request_value_type.role_permission_booleans',[(F+'useradministration/api/RolesApiResourceSwagger.java',r'public String ALL_FUNCTIONS_READ|class PutRolesRoleIdPermissionsRequest')],[(F+'useradministration/service/RoleWritePlatformServiceJpaRepositoryImpl.java',r'Map<String, Boolean> commandPermissions|commandPermissions.get\(permissionCode\).booleanValue')],[(F+'useradministration/api/RolesApiResource.java',r'updateRolePermissions|PutRolesRoleIdPermissionsRequest')],confidence=2)
accept('fineract',36,'PUT /configurations/{configId}','the numeric configuration-update field is named description','read and update the numeric field named value','SPEC','annotations','request_property_name.global_configuration_value',[(F+'infrastructure/configuration/api/GlobalConfigurationApiResourceSwagger.java',r'public Long description')],[(F+'infrastructure/configuration/domain/GlobalConfigurationProperty.java',r'String valueParamName = "value"|command.longValueOfParameterNamed\(valueParamName\)')],[(F+'infrastructure/configuration/api/GlobalConfigurationApiResource.java',r'@Path\("/configurations"\)|public String updateConfiguration|updateConfiguration\(configId\)')],confidence=2)
accept('fineract',36,'PUT /externalevents/configuration','externalEventConfigurations maps each event name to another map of booleans','deserialize each event name directly to a Boolean value','SPEC','annotations','request_shape.external_event_configuration_map',[(F+'infrastructure/event/external/api/ExternalEventConfigurationApiResourceSwagger.java',r'Map<String, Map<String, Boolean>> externalEventConfigurations')],[(F+'infrastructure/event/external/command/ExternalEventConfigurationCommand.java',r'Map<String, Boolean> externalEventConfigurations'),(F+'infrastructure/event/external/serialization/ExternalEventConfigurationCommandFromApiJsonDeserializer.java',r'fromApiJsonHelper.fromJson\(json, ExternalEventConfigurationCommand.class\)')],[(F+'infrastructure/event/external/api/ExternalEventConfigurationApiResource.java',r'@Path\("/externalevents/configuration"\)|@PUT')])
accept('fineract',44,'GET /v1/configurations/{configId}','the response wraps a list under globalConfiguration','serialize a single GlobalConfigurationPropertyData object directly','SPEC','annotations','response_shape.single_global_configuration',[(F+'infrastructure/configuration/api/GlobalConfigurationApiResourceSwagger.java',r'List<GlobalConfigurationPropertyData> globalConfiguration'),(F+'infrastructure/configuration/api/GlobalConfigurationApiResource.java',r'public String retrieveOne|implementation = GlobalConfigurationApiResourceSwagger.GetGlobalConfigurationsResponse.class')],[(F+'infrastructure/configuration/api/GlobalConfigurationApiResource.java',r'configurationData = this.readPlatformService.retrieveGlobalConfiguration\(configId\)|propertyDataJsonSerializer.serialize\(settings, configurationData'),('fineract-core/src/main/java/org/apache/fineract/infrastructure/configuration/data/GlobalConfigurationPropertyData.java',r'private String name|private boolean enabled|private Long value')],confidence=2)

G='gravitee-rest-api-management/gravitee-rest-api-management-rest/src/main/java/io/gravitee/rest/api/management/rest/resource/'
GM='gravitee-rest-api-model/src/main/java/io/gravitee/rest/api/model/'
accept('gravitee-api-management',18,'GET /configuration/groups/{group}/members','each member has roles represented as a list of RoleEntity objects','return GroupMemberEntity objects whose roles are a map of strings','SPEC','annotations','response_property_type.group_member_roles',[(G+'GroupMembersResource.java',r'response = MemberEntity.class'),(GM+'MemberEntity.java',r'List<RoleEntity> roles')],[(G+'GroupMembersResource.java',r'public List<GroupMemberEntity> getGroupMembers'),(GM+'GroupMemberEntity.java',r'Map<String, String> roles')],[(G+'GroupResource.java',r'@Path|GroupMembersResource')],confidence=2)

accept('kratos',20,'POST /admin/identities','a conflicting identity can receive a 409 response','forward duplicate-credential creation errors without a conflict mapping and produce 500','IMPL','spec_file','response_status.duplicate_identity', [('spec/api.json',r'"/admin/identities"|"409"')],[('identity/handler.go',r'IdentityManager\(\).Create|Writer\(\).WriteError\(w, r, err\)'),('identity/manager.go',r'type ErrDuplicateCredentials struct')],confidence=2)
accept('kratos',51,'GET /admin/identities','a successful identity listing is an array','write a single identity object when the identifier query parameter matches','IMPL','spec_file','response_shape.identity_identifier_lookup', [('spec/api.json',r'"/admin/identities"|"listIdentities"|"type": "array"')],[('identity/handler.go',r'identifier := r.URL.Query\(\).Get\("identifier"\)|Writer\(\).Write\(w, r, i\)')])

K='rest-api/resources/src/main/'
accept('kapua',20,'GET /{scopeId}/devices/{deviceId}/events','sortParam and sortDir select the result ordering','construct and execute the event query without applying either sorting parameter','IMPL','spec_file','query_parameter.device_event_sorting',[(K+'resources/openapi/deviceEvent/deviceEvent-scopeId-deviceId.yaml',r'parameters/sortParam|parameters/sortDir'),(K+'resources/openapi/openapi.yaml',r'^    sortParam:|^    sortDir:')],[(K+'java/org/eclipse/kapua/app/api/resources/v1/resources/DeviceEvents.java',r'@QueryParam\("sortParam"\)|query.setPredicate\(andPredicate\)|query.setOffset\(offset\)|return query\(scopeId, deviceId, query\)')],confidence=2)

accept('microcks',17,'GET /api/keycloak/config','public-client has string type','serialize public-client as the boolean true','SPEC','spec_file','response_value_type.keycloak_public_client', [('api/microcks-openapi-v1.7.yaml',r'^        public-client:|^          type: string')],[('webapp/src/main/java/io/github/microcks/web/KeycloakConfigController.java',r'@JsonProperty\("public-client"\)|private final boolean publicClient = true|@RequestMapping\("/api/keycloak"\)')])

N='model/src/main/java/org/projectnessie/'
for operation,method in [
    ('PUT /v1/trees/{referenceType}/{referenceName}','assignReference'),
    ('DELETE /v1/trees/{referenceType}/{referenceName}','deleteReference'),
    ('POST /v1/trees/branch/{branchName}/transplant','transplantCommitsIntoBranch'),
    ('POST /v1/trees/branch/{branchName}/merge','mergeRefIntoBranch')]:
    accept('nessie',16,operation,'the OpenAPI expectedHash query parameter is not marked required','require a non-null expectedHash through the inherited validation declaration','SPEC','annotations','required_query_parameter.expected_hash_'+method,[(N+'api/v1/http/HttpTreeApi.java',r'@QueryParam\("expectedHash"\)|'+method)],[(N+'api/v1/TreeApi.java',r'@Valid @NotNull @Pattern\(regexp = Validation.HASH_REGEX|'+method)],confidence=2)

PAY='src/main/java/uk/gov/pay/api/'
accept('pay-publicapi',15,'POST /v1/payments','language is one of ENGLISH or WELSH','validate language as the ISO codes en or cy','SPEC','spec_file','request_enum.payment_language_codes', [('swagger/swagger.json',r'"enum" : \[ "ENGLISH", "WELSH" \]')],[(PAY+'json/RequestJsonParser.java',r'Must be.*en.*cy|SupportedLanguage.fromIso639AlphaTwoCode')],[(PAY+'resources/PaymentsResource.java',r'@Path\("/v1/payments"\)|createPayment')])
accept('pay-publicapi',15,'POST /v1/payments','metadata is described as an ExternalMetadata object with a nested metadata map','convert the submitted metadata entries directly into the external metadata map','SPEC','spec_file','request_schema.payment_metadata_wrapper', [('swagger/swagger.json',r'"ExternalMetadata" : \{|"\$ref" : "#/definitions/ExternalMetadata"')],[(PAY+'json/RequestJsonParser.java',r'objectMapper.convertValue\(paymentRequest.get\("metadata"\), Map.class\)|new ExternalMetadata\(metadataMap\)'),(PAY+'model/CreateCardPaymentRequest.java',r'request.add\("metadata", metadata.getMetadata\(\)\)')],[(PAY+'resources/PaymentsResource.java',r'@Path\("/v1/payments"\)|createPayment')],confidence=2)

PO='runtime/service/src/main/java/org/apache/polaris/service/'
for operation,method,family in [
    ('POST /v1/{prefix}/namespaces/{namespace}/tables/{table}','updateTable','table'),
    ('POST /v1/{prefix}/namespaces/{namespace}/views/{view}','replaceView','view')]:
    accept('polaris',14,operation,'a server-side CommitStateUnknownException receives 500','map CommitStateUnknownException to 400','IMPL','spec_file','response_status.unknown_state_'+family,[('spec/iceberg-rest-catalog-open-api.yaml',r'An unknown server-side problem occurred; the commit state is unknown\.|"type": "CommitStateUnknownException"')],[(PO+'exception/IcebergExceptionMapper.java',r'case CommitStateUnknownException e -> Status.BAD_REQUEST|@Provider'),(PO+'catalog/iceberg/IcebergCatalogHandler.java',r'public LoadTableResponse updateTable\(|public LoadViewResponse replaceView\(|\.updateView\(viewCatalog')],confidence=2)

BR='src/main/java/io/strimzi/kafka/bridge/'
accept('strimzi-kafka-bridge',32,'GET /consumers/{groupid}/instances/{name}/records','ConsumerRecord.value has string type','emit a structured JSON object for an object-valued record in JSON format','SPEC','spec_file','response_value_type.consumer_record_json_object', [('src/main/resources/openapi.json',r'"ConsumerRecord": \{|"value": \{|"type": "string"')],[(BR+'http/converter/HttpJsonMessageConverter.java',r'jsonObject.put\("value"|JsonUtils.bytesToJson\(record.value\(\)\)'),(BR+'http/HttpSinkBridgeEndpoint.java',r'private void pollHandler|toMessage\(records\)|fromKafkaRecords')],confidence=2)
accept('strimzi-kafka-bridge',32,'GET /consumers/{groupid}/instances/{name}/records','ConsumerRecord.value has a non-null string schema','emit an explicit null value for a record with null Kafka value','SPEC','spec_file','response_nullability.consumer_record_tombstone', [('src/main/resources/openapi.json',r'"ConsumerRecord": \{|"value": \{|"type": "string"')],[(BR+'http/converter/HttpJsonMessageConverter.java',r'jsonObject.put\("value"|JsonUtils.bytesToJson\(record.value\(\)\)')],[(BR+'http/HttpSinkBridgeEndpoint.java',r'private void pollHandler|toMessage\(records\)|fromKafkaRecords')],confidence=2)

def finish():
    prior=json.loads((HERE/'key/new_accepted.json').read_text())
    exploratory=list(csv.DictReader((HERE.parent/'E6_realfix/combined_accepted.csv').open()))
    dedup=set()
    for r in exploratory+prior+accepted:
        key=r['repo'],r['operation'],r['fix_family'];assert key not in dedup;dedup.add(key)
    assert max(Counter(r['repo'] for r in prior+accepted).values())<=6
    (HERE/'key/new_accepted2.json').write_text(json.dumps(accepted,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(accepted_T46=len(accepted),combined_new=len(prior)+len(accepted),per_repo=dict(Counter(r['repo'] for r in accepted)))))

if __name__=='__main__':finish()
