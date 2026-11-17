import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('flagr',34,'GET /api/v1/flags',
 'the enabled query parameter returns flags having the given enabled status',
 'enabled=false is stored in a zero-valued struct field that the vendored query builder omits from SQL predicates',
 'IMPL','openapi','query.enabled_false',
 contract=[('docs/api_docs/bundle.yaml',r'return flags having given enabled status')],
 implementation=[('pkg/handler/crud.go',r'q.Enabled = \*params.Enabled|Where\(q\).Find'),('vendor/github.com/jinzhu/gorm/scope.go',r'if !field.IsIgnored && !field.IsBlank')],
 helpers=['vendor/github.com/jinzhu/gorm/utils.go'])
print('Accepted items and exclusions:',R['finish_accept']('The enabled filter promises the requested boolean status, but struct-based querying omits false; the patch uses an explicit SQL predicate.'))
