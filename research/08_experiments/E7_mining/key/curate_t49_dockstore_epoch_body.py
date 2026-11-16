from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
R['accept']('dockstore',188,'POST /workflows/{workflowId}/maxWeeklyExecutionCountForAnyVersion',
 'onOrAfterEpochSecond is a required query parameter',
 'bind the unannotated long entity parameter from the JSON request body because it has no QueryParam annotation',
 'SPEC','openapi','request_location.execution-count-epoch-body',
 [('src/main/resources/openapi3/openapi.yaml',r'name: onOrAfterEpochSecond|in: query')],
 [('resources/WorkflowResource.java',r'@Path\("/\{workflowId\}/maxWeeklyExecutionCountForAnyVersion"\)|in = ParameterIn.QUERY\) long onOrAfterEpochSecond|@Consumes\(MediaType.APPLICATION_JSON\)')],confidence=2)
print('Accepted/capped:',R['finish_accept']('OpenAPI places epoch in query; parent JAX-RS parameter lacks QueryParam and binds the entity; patch corrects the contract location.'))
