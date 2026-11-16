from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
for method,path,resource in [('POST','/analytics/dashboards','DashboardsResource'),('PUT','/analytics/dashboards/{dashboardId}','DashboardResource')]:
 R['accept']('gravitee-api-management',200,method+' '+path,
  'the submitted dashboard widgets support an optional description string',
  'map each widget into a domain and persistence model with no description field, losing the submitted description',
  'IMPL','openapi','request_body.dashboard-widget-description-persistence',
  [('openapi/openapi-analytics.yaml',r'Optional description of the widget|CreateUpdateDashboard:|^    /analytics/dashboards')],
  [('management/v2/rest/mapper/DashboardMapper.java',r'DashboardWidget mapWidget\(Widget widget\)|Dashboard map\(CreateUpdateDashboard dashboard\)'),('core/dashboard/model/DashboardWidget.java',r'private String title;|private String type;'),('repository/management/model/CustomDashboardWidget.java',r'private String title;|private String type;')],
  route=[('resource/analytics/dashboards/'+resource+'.java',r'DashboardMapper.INSTANCE.map\(|[a-zA-Z]+DashboardUseCase.execute')],confidence=2)
print('Accepted/capped:',R['finish_accept']('Parent widget schema exposes description; domain and repository models lack the field; patch adds persistence support without changing the accepted description facet.'))
