import runpy
from pathlib import Path
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t50.py'))
R['accept']('answer',2,'GET /answer/admin/api/siteinfo/interface',
 'a data request body matching AddCommentReq is required',
 'GetInterface reads site configuration without binding or requiring a request body',
 'SPEC','openapi','request.spurious_body',
 contract=[('docs/swagger.yaml',r'^  /answer/admin/api/siteinfo/interface:')],
 implementation=[('internal/controller_backyard/siteinfo_controller.go',r'func .* GetInterface|GetSiteInterface\(ctx\)')],
 route=[('internal/router/answer_api_router.go',r'siteinfo/interface')])
print('Accepted items and exclusions:',R['finish_accept']('Parent GET interface documentation requires an unrelated comment body; the handler reads configuration without binding a body.'))
