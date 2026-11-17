import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('keto',39,'GET /relation-tuples',
 'the namespace query parameter is required',
 'query parsing accepts an omitted namespace and persistence applies no namespace restriction when it is empty',
 'SPEC','openapi','request.namespace_optionality',
 contract=[('spec/api.json',r'Only the namespace field is required')],
 implementation=[('internal/relationtuple/read_server.go',r'func \(h \*handler\) getRelations|GetRelationTuples\(r.Context\(\), query'),('internal/relationtuple/definitions.go',r'q.Namespace = query.Get\("namespace"\)'),('internal/persistence/sql/relationtuples.go',r'if query.Namespace != ""')])
R['accept']('keto',39,'GET /expand',
 'the max-depth query parameter is required',
 'the query parser accepts an omitted max-depth and the expansion engine uses its configured global depth limit',
 'SPEC','openapi','request.max_depth_optionality',
 contract=[('spec/api.json',r'"name": "max-depth"')],
 implementation=[('internal/expand/handler.go',r'func \(h \*handler\) getExpand|x.GetMaxDepthFromQuery'),('internal/x/max_depth.go',r'if !q.Has\("max-depth"\)|return 0, nil'),('internal/expand/engine.go',r'if globalMaxDepth :=')])
print('Accepted items and exclusions:',R['finish_accept']('Namespace and expansion depth are marked required in generated contracts although existing parsers accept omission; the patch removes both required flags.'))
