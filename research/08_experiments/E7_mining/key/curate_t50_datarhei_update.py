import runpy
from pathlib import Path
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t50.py'))
R['accept']('datarhei-core',1,'PUT /api/v3/process/{id}',
    '404 Not Found is listed for the process update operation',
    'an unknown process ID returns 400 Bad Request',
    'IMPL','openapi','status.process_update_unknown',
    contract=[('docs/swagger.yaml',r'operationId: restream-3-update'),('docs/swagger.yaml',r'"404":')],
    implementation=[('http/handler/api/restream.go',r'Process can.t be updated'),('restream/restream.go',r'unknown process ID \(.*')],
    route=[('http/server.go',r'v3.PUT\("/process/:id"'),('http/errorhandler/error.go',r'api.Error|c.JSON')],helpers=['http/api/error.go'])
print('Accepted items and exclusions:',R['finish_accept']('Unknown-process update returns 400 despite the parent 404 response; the resolving patch distinguishes the missing-process error.'))
