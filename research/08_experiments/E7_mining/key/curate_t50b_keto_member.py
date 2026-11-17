import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('keto',15,'DELETE /engines/acp/ory/{flavor}/roles/{id}/members/{member}',
 'member removal uses the role members collection path with members supplied in a request body',
 'the router requires an additional member path segment and the handler reads that path parameter',
 'SPEC','openapi','route.member_path',
 contract=[('docs/api.swagger.json',r'removeOryAccessControlPolicyRoleMembersBody'),('engine/ladon/handler.go',r'swagger:route DELETE .*roles/\{id\}/members engines')],
 implementation=[('engine/ladon/handler.go',r'r.DELETE\(BasePath\+"/roles/:id/members/:member"|s == ps.ByName\("member"\)')])
print('Accepted items and exclusions:',R['finish_accept']('The parent removal contract uses a collection path and body, while runtime routing and handler require the member path parameter.'))
