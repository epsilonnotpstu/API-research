import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
for suffix,methodname in [('', 'PostEvaluation'),('/batch','PostEvaluationBatch')]:
 R['accept']('flagr',20,'POST /api/v1/evaluation'+suffix,
  'evaluation result flagID is an integer with minimum 1',
  'an unknown positive flagID produces a successful evaluation response with result flagID set to 0',
  'IMPL','openapi','evaluation.missing_flag_identity',
  contract=[('docs/api_docs/bundle.yaml',r'^  evalResult:')],
  implementation=[('pkg/handler/eval.go',r'func \(e \*eval\) '+methodname+r'\(|func BlankResult|return BlankResult\(nil')])
print('Accepted items and exclusions:',R['finish_accept']('Unknown positive flag identifiers become zero in evaluation results, violating the parent minimum; the patch retains the requested identifier.'))
