import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('keto',40,'DELETE /relation-tuples',
 'the delete operation declares no query parameters',
 'the handler reads namespace, object, relation and subject filters from the query and uses them for deletion',
 'SPEC','openapi','request.delete_filter_documentation',confidence=2,
 contract=[('spec/api.json',r'"operationId": "deleteRelationTuples"')],
 implementation=[('internal/relationtuple/transact_server.go',r'func \(h \*handler\) deleteRelations|DeleteAllRelationTuples\(r.Context\(\), query\)'),('internal/relationtuple/definitions.go',r'func \(q \*RelationQuery\) FromURLQuery|q.Namespace = query.Get\("namespace"\)')])
print('Accepted items and exclusions:',R['finish_accept']('Delete operation has no generated query parameters because its annotation names the wrong operation; the patch restores documentation of existing deletion filters.'))
