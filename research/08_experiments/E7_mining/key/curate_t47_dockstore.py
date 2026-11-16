"""Private parent evidence and reviewed acceptance calls."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t47.py'))
a=R['accept'];d=R['decide'];P='dockstore-webservice/src/main/java/'
for base,cls in [('containers','DockerRepoResource'),('workflows','WorkflowResource')]:
    a('dockstore',89,'GET /'+base+'/published',
      'limit has the allowable range 1 through 100',
      'pass limit=0 to a database query with maximum result count zero without a lower-bound guard',
      'IMPL','annotations','query_constraint.published_limit_lower_bound',
      [(P+'io/dockstore/webservice/resources/'+cls+'.java',r'allowableValues = "range\[1,100\]"')],
      [(P+'io/dockstore/webservice/resources/'+cls+'.java',r'int maxLimit = Math.min|findAllPublished\(offset, maxLimit'),
       (P+'io/dockstore/webservice/jdbi/EntryDAO.java',r'setMaxResults\(limit\)')],confidence=2)
d('dockstore',89,'ACCEPT','Two published-list operations declare a positive limit range but pass zero unchanged to the parent database query.')
a('dockstore',95,'GET /metadata/runner_dependencies',
  'python_version defaults to 2',
  'bind an omitted python_version to 3',
  'SPEC','annotations','query_default.runner_python_version',
  [(P+'io/dockstore/webservice/resources/MetadataResource.java',r'name = "python_version".*defaultValue = "2"')],
  [(P+'io/dockstore/webservice/resources/MetadataResource.java',r'@DefaultValue\("3"\) @QueryParam\("python_version"\)')],
  [(P+'io/dockstore/webservice/resources/MetadataResource.java',r'@Path\("/runner_dependencies"\)|@Path\("/metadata"\)')])
d('dockstore',95,'ACCEPT','Runner Python default is 2 in the parent schema annotation and 3 in the binding annotation.')
a('dockstore',103,'GET /api/ga4gh/v1/tools/{id}/versions/{version-id}/{type}/descriptor/{relative-path}',
  'a non-plain descriptor response is a ToolDescriptor object with descriptor metadata',
  'return the matching SourceFile object directly for an additional descriptor',
  'IMPL','annotations','response_schema.additional_trs_descriptor',
  [(P+'io/swagger/api/ToolsApi.java',r'Get additional tool descriptor|response = ToolDescriptor.class')],
  [(P+'io/swagger/api/impl/ToolsApiServiceImpl.java',r'entity\(unwrap \? entity.getContent\(\) : entity\)'),
   (P+'io/dockstore/webservice/core/SourceFile.java',r'public class SourceFile|class SourceFile|private String content')],
  [(P+'io/swagger/api/ToolsApi.java',r'@Path\("/\{id\}/versions/\{version-id\}/\{type\}/descriptor/\{relative-path\}"\)'),
   (P+'io/dockstore/webservice/DockstoreWebserviceApplication.java',r'GA4GH_API_PATH =')],confidence=2)
d('dockstore',103,'ACCEPT','Additional descriptor contract names ToolDescriptor; the parent branch instead returns SourceFile for the structured response.')
a('dockstore',131,'GET /api/ga4gh/v2/tools/{id}/versions/{version_id}/containerfile',
  'the structured containerfile response is an array of ToolContainerfile objects',
  'return a single ToolContainerfile object for the structured response',
  'IMPL','spec_file','response_shape.trs_containerfile_array',
  [('dockstore-webservice/src/main/resources/openapi.yaml',r"'/api/ga4gh/v2/tools/\{id\}/versions/\{version_id\}/containerfile'|#/components/schemas/ToolContainerfile")],
  [(P+'io/swagger/api/impl/ToolsApiServiceImpl.java',r'ToolContainerfile dockerfile =|entity\(unwrap \? dockerfile.getContainerfile\(\) : dockerfile\)')],confidence=2)
d('dockstore',131,'ACCEPT','The parent containerfile response schema is an array, while the implementation returns one object.')
print('Accepted items from this reviewed repository:',5)
