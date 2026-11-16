"""Private, exact-parent acceptance records after ranked patch screening."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t47.py'))
a=R['accept']; d=R['decide']
P='app/src/main/java/io/apicurio/registry/'
a('apicurio-registry',69,'PUT /artifacts/{artifactId}/versions/{version}/meta',
  'EditableMetaData accepts labels and properties when updating version metadata',
  'copy only name and description from the request into the storage update',
  'IMPL','spec_file','request_property.version_metadata_labels_properties',
  [('common/src/main/resources/META-INF/openapi.json',r'"EditableMetaData": \{|"operationId": "updateArtifactVersionMetaData"|"labels": \{')],
  [(P+'rest/ArtifactsResourceImpl.java',r'public void updateArtifactVersionMetaData|dto.setDescription\(data.getDescription\(\)\)|storage.updateArtifactVersionMetaData\(artifactId, version.longValue\(\), dto\)')])
d('apicurio-registry',69,'ACCEPT','The version metadata request schema includes labels and properties, but the parent resource drops both fields before storage.')
for operation,method in [('POST /groups/{groupId}/artifacts','createArtifact'),('PUT /groups/{groupId}/artifacts/{artifactId}','updateArtifact')]:
    a('apicurio-registry',87,operation,
      'nonempty X-Registry-Name and X-Registry-Description override metadata extracted from artifact content',
      'apply header overrides only when their trimmed values are empty',
      'IMPL','spec_file','request_header.artifact_nonempty_metadata_override',
      [('app/src/main/resources-unfiltered/META-INF/resources/api-specifications/registry/v2/openapi.json',r'"operationId": "'+method+r'"|Specifies the (?:artifact )?(?:name|description) of (?:artifact being added|this new version)')],
      [(P+'rest/v2/GroupsResourceImpl.java',r'public ArtifactMetaData '+method+r'\(|if \(artifactName != null && artifactName.trim\(\).isEmpty\(\)\)|if \(name != null && name.trim\(\).isEmpty\(\)\)|if \(description != null && description.trim\(\).isEmpty\(\)\)|if \(artifactDescription != null && artifactDescription.trim\(\).isEmpty\(\)\)')])
d('apicurio-registry',87,'ACCEPT','Creation and update document nonempty metadata headers; both parent override guards instead require empty strings.')
for operation,method in [('POST /groups/{groupId}/artifacts','createArtifact'),('POST /groups/{groupId}/artifacts/{artifactId}/versions','createArtifactVersion')]:
    a('apicurio-registry',91,operation,
      'rule-processing failures list 409 and no 422 response',
      'map an unprocessable Avro schema during compatibility checking to 422',
      'SPEC','spec_file','response_status.unprocessable_avro_rule',
      [('common/src/main/resources/META-INF/openapi.json',r'"operationId": "'+method+r'"|"RuleViolationConflict": \{')],
      [(P+'rest/v3/GroupsResourceImpl.java',r'public .*'+method+r'\(|rulesService.applyRules'),
       (P+'rules/RulesServiceImpl.java',r'public void applyRules|executor.execute\(context\)'),
       (P+'rules/compatibility/CompatibilityRuleExecutor.java',r'checker.testCompatibility'),
       ('schema-util/avro/src/main/java/io/apicurio/registry/rules/compatibility/AvroCompatibilityChecker.java',r'throw new UnprocessableSchemaException'),
       (P+'services/http/HttpStatusCodeMap.java',r'HTTP_UNPROCESSABLE_ENTITY = 422|map.put\(UnprocessableSchemaException.class'),
       (P+'services/http/CoreRegistryExceptionMapperService.java',r'getStatusCode|Response.status')],confidence=2)
d('apicurio-registry',91,'ACCEPT','Two parent registration operations omit 422 while their Avro compatibility checker throws an exception explicitly mapped to 422.')
print('Accepted items from this reviewed repository:',5)
