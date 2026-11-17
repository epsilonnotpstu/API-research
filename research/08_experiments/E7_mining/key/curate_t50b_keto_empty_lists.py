import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
for suffix,typ in [('policies','Policies'),('roles','Roles')]:
 R['accept']('keto',21,'GET /engines/acp/ory/{flavor}/'+suffix,
  'the successful response is a JSON array',
  'empty filtered results remain nil slices passed to the JSON response writer, yielding null instead of an empty array',
  'IMPL','openapi','response.empty_list_null',confidence=2,
  contract=[('.schema/api.swagger.json',r'"description": "'+typ+r' is an array of')],
  implementation=[('storage/handler.go',r'var res '+typ+r'|h.h.Write\(w, r, l.Filter\(m\).Value\)'),('engine/ladon/handler.go',r'var p kstorage.'+typ)])
print('Accepted items and exclusions:',R['finish_accept']('List schemas require arrays, but empty filtering leaves nil slices for JSON serialization; the patch initializes both list kinds as empty arrays.'))
