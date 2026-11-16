from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
R['accept']('harbor',164,'GET /repositories/manifest',
 'the manifest retrieval operation uses the singular /repositories/manifest path under the API base path',
 'register the manifest handler only at the plural /api/repositories/manifests path',
 'SPEC','openapi','request_path.repository-manifests-plural',
 [('docs/swagger.yaml',r'^  /repositories/manifest:')],
 [('ui/router.go',r'beego.Router\("/api/repositories/manifests"')],
 helpers=['api/repository.go'])
print('Accepted/capped:',R['finish_accept']('Parent Swagger uses singular manifest; parent router registers plural manifests; patch corrects the documented path.'))
