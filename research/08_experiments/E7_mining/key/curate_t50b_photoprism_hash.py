import runpy
from pathlib import Path
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t50b.py'))
R['accept']('photoprism',5,'GET /api/v1/videos/{hash}/{token}/{format}',
 'the required hash path segment is declared as a parameter named thumb',
 'the route and handler use a path parameter named hash',
 'SPEC','openapi','parameter.video_hash_name',
 contract=[('internal/api/swagger.json',r'"operationId": "GetVideo"')],
 implementation=[('internal/api/video.go',r'c.Param\("hash"\)|router.GET')])
print('Accepted items and exclusions:',R['finish_accept']('The parent video path uses hash but declares the corresponding required parameter as thumb; the handler reads hash.'))
