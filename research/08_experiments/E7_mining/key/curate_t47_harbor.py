"""Private parent evidence for four existing Harbor operations."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t47.py'))
a=R['accept'];d=R['decide']
a('harbor',76,'PUT /projects/{project_name_or_id}/immutabletagrules/{immutable_rule_id}',
  'immutable_rule_id identifies the immutable rule selected for update',
  'authorize and update the rule identified in the body while ignoring the path rule identifier',
  'IMPL','spec_file','resource_scope.immutable_rule_path_id',
  [('api/v2.0/swagger.yaml',r'description: The ID of the immutable rule|operationId: UpdateImmuRule')],
  [('src/server/v2.0/handler/immutable.go',r'func \(ia \*immutableAPI\) UpdateImmuRule|ia.requireRuleAccess\(ctx, projectID, metadata.ID\)|ia.immuCtl.UpdateImmutableRule\(ctx, projectID, &metadata\)')],confidence=2)
d('harbor',76,'ACCEPT','Immutable-rule update uses the body identifier for authorization and update, although the contract selects the rule through its path identifier.')
a('harbor',120,'GET /repositories',
  'Repository.id has string type',
  'serialize repoResp.ID as an int64 JSON number',
  'SPEC','spec_file','response_value_type.repository_numeric_id',
  [('docs/swagger.yaml',r'description: The ID of repository.|#/definitions/Repository')],
  [('src/ui/api/repository.go',r'ID\s+int64\s+`json:"id"`|ra.Data\["json"\] = repositories|func getRepositories')])
d('harbor',120,'ACCEPT','Repository schema declares a string identifier; the parent response struct serializes an int64 identifier.')
a('harbor',143,'POST /projects',
  'the project request names its project name property name',
  'decode and validate the project name only through the project_name property',
  'SPEC','spec_file','request_property_name.project_create_name',
  [('docs/swagger.yaml',r'Project:|description: The name of the project.|New created project.')],
  [('api/project.go',r'ProjectName string `json:"project_name"`|p.DecodeJSONReq\(&req\)|projectName := req.ProjectName|func validateProjectReq')])
d('harbor',143,'ACCEPT','Project creation references a schema with name, while the parent request decoder and validator require project_name.')
a('harbor',147,'POST /projects',
  'metadata.public accepts only the strings true and false',
  'copy any nonempty metadata.public string into project storage without checking that allowed set',
  'IMPL','spec_file','request_enum.project_metadata_public',
  [('api/v2.0/swagger.yaml',r'The public status of the project. The valid values are')],
  [('src/server/v2.0/handler/project.go',r'func \(a \*projectAPI\) CreateProject|req.Metadata.Public == ""|lib.JSONCopy\(&p.Metadata, req.Metadata\)|a.projectCtl.Create\(ctx, p\)|func \(a \*projectAPI\) validateProjectReq')],confidence=2)
d('harbor',147,'ACCEPT','Project metadata documents two public values; the parent creation handler stores other nonempty strings without validating that set.')
print('Accepted items from this reviewed repository:',4)
