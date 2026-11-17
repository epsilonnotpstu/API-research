import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
ops=[('GET /api/v1/flags','crud.go',r'payload, err := e2rMapFlags\(fs\)'),('GET /api/v1/flags/{flagID}','crud.go',r'func \(c \*crud\) GetFlag\('),('PUT /api/v1/flags/{flagID}','crud.go',r'func \(c \*crud\) PutFlag\('),('PUT /api/v1/flags/{flagID}/enabled','crud.go',r'func \(c \*crud\) SetFlagEnabledState\('),('PUT /api/v1/flags/{flagID}/restore','crud.go',r'func \(c \*crud\) RestoreFlag\('),('POST /api/v1/flags/{flagID}/duplicate','crud_duplicate.go',r'payload, err := e2rMapFlag\(created\)')]
for op,file,pat in ops:
 R['accept']('flagr',26,op,
  'the returned effective enricher catalog includes the flag-scoped enrichers plus enabled server built-ins',
  'the response mapper filters out disabled flag-scoped enrichers along with disabled built-ins',
  'IMPL','openapi','response.flag_enricher_visibility',confidence=2,
  contract=[('docs/api_docs/bundle.yaml',r'Effective context enrichers for this flag')],
  implementation=[('pkg/handler/enricher.go',r'entries := enabledEnrichers\(effectiveEnrichers\(flag\)\)|if entries\[i\].enabled'),('pkg/handler/'+file,pat)],
  helpers=['pkg/entity/enricher.go'])
print('Accepted items and exclusions:',R['finish_accept']('Flag response documentation includes flag-scoped enrichers, but the mapper removes disabled ones; the patch separates visibility from evaluation enablement.'))
