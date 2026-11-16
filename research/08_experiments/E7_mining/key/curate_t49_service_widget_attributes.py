from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
R['accept']('service-api',174,'GET /v1/{projectName}/widget/multilevel/{widgetId}',
  'the attributes query parameter is optional',
  'pass omitted attributes as a null array into Lists.newArrayList in widget content loading',
  'IMPL','annotations','query_optional.widget-attributes-null-array',
  [('ws/controller/WidgetController.java',r'@RequestMapping\("/v1/\{projectName\}/widget"\)|name = "attributes"')],
  [('ws/controller/WidgetController.java',r'getWidgetHandler.getWidget\(widgetId, attributes'),('core/widget/impl/GetWidgetHandlerImpl.java',r'params.put\(ATTRIBUTES, Lists.newArrayList\(attributes\)\)')],confidence=2)
print('Accepted/capped:',R['finish_accept']('Parent annotation makes attributes optional; controller forwards null into collection construction; patch normalizes omitted attributes to an empty array.'))
