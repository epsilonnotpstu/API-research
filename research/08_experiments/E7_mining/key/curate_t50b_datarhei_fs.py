import runpy
from pathlib import Path
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t50b.py'))
for fs,handler in [('disk','DiskFSHandler'),('mem','MemFSHandler')]:
 R['accept']('datarhei-core',3,'GET /api/v3/fs/'+fs,
  'the listing operation path ends in a trailing slash',
  'the listing handler is registered without that slash, with slash-suffixed paths routed to GetFile',
  'SPEC','openapi','route.filesystem_listing_slash',
  contract=[('docs/swagger.json',r'"/api/v3/fs/'+fs+r'/":')],
  implementation=[('http/server.go',r'v3.GET\("/fs/'+fs+r'(?:"|/\*)')],
  helpers=['http/handler/api/'+fs+'fs.go'])
print('Accepted items and exclusions:',R['finish_accept']('Parent documents place filesystem listings on trailing-slash paths; existing routing distinguishes listing paths from file paths.'))
