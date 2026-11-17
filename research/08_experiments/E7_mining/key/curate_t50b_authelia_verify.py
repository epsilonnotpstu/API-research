import runpy,json
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
for method in ['GET','HEAD']:
 R['accept']('authelia',12,method+' /api/verify',
  'HTTP 200 denotes successful permission verification and HTTP 401 denotes unauthorized access',
  'a malformed original URL invokes an error reply without setting a non-success HTTP status',
  'IMPL','openapi','verify.parse_error_status',confidence=2,
  contract=[('api/openapi.yml',r'/api/verify:')],
  implementation=[('internal/handlers/handler_verify.go',r'Unable to parse target URL'),('internal/middlewares/authelia_context.go',r'func \(c \*AutheliaCtx\) Error\(')],
  route=[('internal/server/server.go',r'r\.'+method+r'\("/api/verify"')])
print('Accepted items and exclusions:',R['finish_accept']('Verification parse failure invokes a JSON error helper without changing status, contradicting the contract describing HTTP 200 as successful verification.'))
