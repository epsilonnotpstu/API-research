import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('keto',43,'GET /relation-tuples',
 'the object and relation query parameters are required',
 'query parsing accepts omitted object and relation fields, and persistence adds their filters only for nonempty values',
 'SPEC','openapi','request.object_relation_optionality',
 contract=[('spec/api.json',r'"description": "Object of the Relation Tuple"|"description": "Relation of the Relation Tuple"')],
 implementation=[('internal/relationtuple/read_server.go',r'func \(h \*handler\) getRelations|GetRelationTuples\(r.Context\(\), query'),('internal/relationtuple/definitions.go',r'q.Object = query.Get\("object"\)|q.Relation = query.Get\("relation"\)'),('internal/persistence/sql/relationtuples.go',r'if query.Object != ""|if query.Relation != ""')])
print('Accepted items and exclusions:',R['finish_accept']('List object and relation filters are documented as required, but parsing and persistence accept omission; the patch marks these two fields optional.'))
