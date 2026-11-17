import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('answer',40,'GET /answer/admin/api/users/activation',
 'user activation is retrieved at the plural users/activation route',
 'the router binds this handler to singular user/activation under the admin API prefix',
 'SPEC','openapi','request.activation_route',
 contract=[('docs/swagger.yaml',r'/answer/admin/api/users/activation:')],
 implementation=[('internal/router/answer_api_router.go',r'r.GET\("/user/activation", a.adminUserController.GetUserActivation\)')],
 route=[('internal/server/http.go',r'"/answer/admin/api"|RegisterAuthAdmin')])
print('Accepted items and exclusions:',R['finish_accept']('Activation documentation uses plural users while the existing admin router uses singular user; the patch corrects the annotation and generated documents.'))
