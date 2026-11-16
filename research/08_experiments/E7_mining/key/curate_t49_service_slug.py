from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
for op,controller,entity in [('GET /organizations','OrganizationController','organizations'),('GET /organizations/{org_id}/projects','OrganizationProjectController','projects')]:
 R['accept']('service-api',285,op,
  'the slug query parameter filters '+entity+' by slug',
  'build the slug equality condition from the name parameter instead of the supplied slug',
  'IMPL','annotations','query_mapping.slug-uses-name-value',
  [('ws/controller/'+controller+'.java',r'Filter '+entity+r' by slug')],
  [('ws/controller/'+controller+'.java',r'if \(StringUtils.isNotEmpty\(slug\)\)|new FilterCondition\(Condition.EQUALS, false, name, "slug"\)')])
print('Accepted/capped:',R['finish_accept']('Parent query documentation says slug filters by slug; both controllers instead compare the name value; patch uses slug.'))
