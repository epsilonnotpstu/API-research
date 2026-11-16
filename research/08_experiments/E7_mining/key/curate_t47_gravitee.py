"""Private ranked decisions; scoped-route behaviour is a static inference."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t47.py'))
a=R['accept'];d=R['decide']
BASE='gravitee-apim-rest-api/'
V2=BASE+'gravitee-apim-rest-api-management-v2/gravitee-apim-rest-api-management-v2-rest/src/main/'
M=BASE+'gravitee-apim-rest-api-management/gravitee-apim-rest-api-management-rest/src/main/java/io/gravitee/rest/api/management/rest/resource/'
S=BASE+'gravitee-apim-rest-api-service/src/main/java/'
a('gravitee-api-management',63,'GET /environments/{envId}/clusters',
  'sortBy is limited to name, createdAt and updatedAt with optional descending prefixes',
  'construct a sorting field directly from any nonblank sortBy value without checking that field set',
  'IMPL','spec_file','query_constraint.cluster_sort_fields',
  [(V2+'resources/openapi/openapi-environments.yaml',r'clusterSortByParam:|Possibility to sort Cluster results by field|operationId: searchClusters')],
  [(V2+'java/io/gravitee/rest/api/management/v2/rest/resource/cluster/ClustersResource.java',r'@QueryParam\("sortBy"\) String sortBy|searchClusterUseCase.execute'),
   (S+'io/gravitee/apim/core/cluster/use_case/SearchClusterUseCase.java',r'String field = isAscending|new SortableImpl\(field, isAscending\)')],confidence=2)
d('gravitee-api-management',63,'ACCEPT','Cluster sorting documents a closed field enum; the parent converts arbitrary nonblank strings directly into sort fields.')
for base,root,child,method in [('apis','ApiResource','ApiLogsResource','findApiLog'),('applications','ApplicationResource','ApplicationLogsResource','findApplicationLog')]:
    variable='api' if base=='apis' else 'application'
    a('gravitee-api-management',120,'GET /'+base+'/{'+variable+'}/logs/{log}',
      'the log resource is nested under the selected '+variable+' identifier',
      'look up the log globally by identifier and timestamp without comparing its '+variable+' to the selected route resource',
      'IMPL','annotations','resource_scope.'+variable+'_log_lookup',
      [(M+child+'.java',r'@Operation\(summary = "Get a specific log"\)|@PathParam\("'+variable+r'"\)'),
       (M+root+'.java',r'public '+child+r' get')],
      [(M+child+'.java',r'return logsService.'+method+r'\(GraviteeContext.getExecutionContext\(\), logId, timestamp\)'),
       (S+'io/gravitee/rest/api/service/impl/LogsServiceImpl.java',r'public .*'+method+r'\(|logRepository.findById\(id, timestamp\)')],
      [(M+base.capitalize()+'Resource.java',r'@Path\("\{'+variable+r'\}"\)')],confidence=2)
d('gravitee-api-management',120,'ACCEPT','Two nested log routes ignore their selected resource identifiers; the parent service performs global identifier lookups.')
a('gravitee-api-management',126,'GET /apis/{api}/alerts/{alert}/events',
  'alert events are retrieved under the selected API alert resource',
  'query events only by alert identifier and time bounds without checking the selected API reference',
  'IMPL','annotations','resource_scope.api_alert_events',
  [(M+'ApiAlertsResource.java',r'Retrieve the list of events for an alert|@PathParam\("api"\)'),
   (M+'ApiResource.java',r'public ApiAlertsResource getApiAlertsResource')],
  [(M+'ApiAlertsResource.java',r'public AlertEventPage getApiAlertEvents|alertService.findEvents\('),
   (S+'io/gravitee/rest/api/service/impl/AlertServiceImpl.java',r'public Page<AlertEventEntity> findEvents\(final String alertId|new AlertEventCriteria.Builder\(\).alert\(alertId\)')],
  [(M+'ApisResource.java',r'@Path\("\{api\}"\)')],confidence=2)
d('gravitee-api-management',126,'ACCEPT','The API-nested alert event contract reaches a parent service overload that never checks the API reference.')
print('Accepted items from this reviewed repository:',4)
