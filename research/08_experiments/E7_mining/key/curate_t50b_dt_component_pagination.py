import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
root='apiserver/src/main/java/org/dependencytrack/'
R['accept']('dependency-track',43,'GET /v1/vulnerability/component/{uuid}',
 'pagination parameters select the page and number of component vulnerabilities returned',
 'the DAO query selects all matching vulnerabilities without offset or limit and the handler returns the entire result',
 'IMPL','jvm_annotation','response.component_vulnerability_pagination',
 contract=[(root+'resources/v1/VulnerabilityResource.java',r'@PaginatedApi|@Path\("/component/\{uuid\}"\)'),(root+'resources/v1/openapi/PaginatedApi.java',r'Number of elements to return per page|The page to return')],
 implementation=[(root+'resources/v1/VulnerabilityResource.java',r'qm.getVulnerabilities\(component, suppressed\)|Response.ok\(result.getObjects\(\)\)'),(root+'persistence/VulnerabilityQueryManager.java',r'public PaginatedResult getVulnerabilities\(Component|dao.getVulnerabilitiesByComponent|objects\(componentVulnerabilities\)'),(root+'persistence/jdbi/VulnerabilityDao.java',r'List<Vulnerability> getVulnerabilitiesByComponent')])
print('Accepted items and exclusions:',R['finish_accept']('Component vulnerability listing declares pagination but its DAO omits limit and offset; the patch applies request pagination and returns the selected page.'))
