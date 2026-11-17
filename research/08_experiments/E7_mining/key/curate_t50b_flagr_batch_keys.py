import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('flagr',17,'POST /api/v1/evaluation/batch',
 'batch evaluation accepts flagKeys as an array of nonempty strings',
 'the batch handler evaluates only flagIDs and never reads the supplied flagKeys',
 'IMPL','openapi','evaluation.batch_flag_keys',confidence=2,
 contract=[('docs/api_docs/bundle.yaml',r'flagKeys:|operationId: postEvaluationBatch')],
 implementation=[('pkg/handler/eval.go',r'func \(e \*eval\) PostEvaluationBatch|flagIDs := params.Body.FlagIds')])
print('Accepted items and exclusions:',R['finish_accept']('The batch request schema exposes flagKeys, but the parent handler loops only over flagIDs; the patch adds the missing key evaluation loop.'))
