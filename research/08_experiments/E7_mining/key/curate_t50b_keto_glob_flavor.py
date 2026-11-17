import runpy,json,re
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py');n=R['next_row']()
R['require_current'](n);R['record_preview'](n,'parent flavor operations for capped acceptance')
doc=json.loads(R['M']['git']('keto','show',n['parent_commit']+':docs/api.swagger.json'))
for path,pi in doc['paths'].items():
 for method,op in pi.items():
  if method.lower() not in {'get','post','put','delete','patch','head','options'}:continue
  if method=='delete' and path.endswith('/members'):continue # Documented member route lacks the actual member path segment.
  if not any(p.get('name')=='flavor' and 'regex' in p.get('description','') and 'glob' not in p.get('description','') for p in op.get('parameters',[])+pi.get('parameters',[])):continue
  R['accept']('keto',47,method.upper()+' '+path,
   'the documented policy flavors are regex and exact',
   'the flavor parser also accepts glob through the existing EnabledFlavors list',
   'SPEC','openapi','request.glob_flavor_documentation',
   contract=[('docs/api.swagger.json',r'The ORY Access Control Policy flavor. Can be')],
   implementation=[('engine/ladon/handler.go',r'var EnabledFlavors =|func flavor\(|stringslice.Has\(EnabledFlavors, t\)|r\.'+method.upper()+r'\(BasePath')])
print('Accepted items and exclusions:',R['finish_accept']('Flavor descriptions list regex and exact only, while the existing parser accepts glob; the patch documents the already supported flavor across operations.'))
