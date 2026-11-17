import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('authelia',14,'POST /api/oidc/introspection',
 'HTTP 500 responses have application/json content with the generic OpenID error schema',
 'issuer resolution failure returns a text/plain HTTP 500 status message',
 'IMPL','openapi','error.introspection_media_type',
 contract=[('api/openapi.yml',r'/api/oidc/introspection:')],
 implementation=[('internal/handlers/handler_oauth2_introspection.go',r'ctx.ReplyStatusCode\(fasthttp.StatusInternalServerError\)'),('internal/middlewares/authelia_context.go',r'func \(ctx \*AutheliaCtx\) ReplyStatusCode')],
 route=[('internal/server/handlers.go',r'r.POST\(oidc.EndpointPathIntrospection')])
print('Accepted items and exclusions:',R['finish_accept']('The introspection contract declares JSON errors for HTTP 500, but issuer-resolution failure invokes a helper emitting plain text.'))
