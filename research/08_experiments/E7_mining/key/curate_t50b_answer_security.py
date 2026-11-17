import runpy,json,re
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py');n=R['next_row']()
a=json.loads(R['M']['git'](n['repo'],'show',n['parent_commit']+':docs/swagger.json'))
b=json.loads(R['M']['git'](n['repo'],'show',n['fix_commit']+':docs/swagger.json'))
for path,ops in a['paths'].items():
 for method,op in ops.items():
  if method not in b['paths'].get(path,{}):continue
  av=bool(op.get('security',a.get('security',[])));bv=bool(b['paths'][path][method].get('security',b.get('security',[])))
  if av==bv:continue
  suffix=path.removeprefix('/answer/admin/api').removeprefix('/answer/api/v1')
  x='API key authentication is required' if av else 'no authentication security requirement is declared'
  y='the router exposes this operation through a group permitting anonymous requests on public sites' if av else 'the router requires authenticated user or administrator middleware before the handler'
  R['accept']('answer',27,method.upper()+' '+path,x,y,
   'SPEC','openapi','security.authentication_requirement',confidence=2,
   contract=[('docs/swagger.json',re.escape('"'+path+'"'))],
   implementation=[('internal/router/answer_api_router.go',r'\.'+method.upper()+r'\("'+re.escape(suffix)+r'"'),('internal/base/server/http.go',r'RegisterAnswerAPIRouter\(authV1\)|RegisterAnswerAdminAPIRouter|RegisterUnAuthAnswerAPIRouter|RegisterMustUnAuthAnswerAPIRouter')],
   helpers=['internal/base/middleware/auth.go'])
print('Accepted items and exclusions:',R['finish_accept']('Twenty-two parent operation security declarations disagree with authenticated or public router groups; the patch aligns the documented authentication requirements.'))
