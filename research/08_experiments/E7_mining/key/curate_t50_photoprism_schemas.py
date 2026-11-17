import runpy
from pathlib import Path
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t50.py'))
base='internal/api/'
ops=[
 ('GET /api/v1/albums/{uid}/links','GetAlbumLinks','a single entity.Link object','a JSON array of share links',
  [('internal/api/links.go',r'c.JSON\(http.StatusOK, m.Links\(\)\)'),('internal/entity/album.go',r'func .* Links\(\) Links'),('internal/entity/link.go',r'type Links \[\]Link')]),
 ('GET /api/v1/labels','SearchLabels','a single search.Label object','a JSON array of label objects',
  [('internal/api/labels_search.go',r'c.JSON\(http.StatusOK, result\)'),('internal/entity/search/labels.go',r'func Labels.*results \[\]Label')]),
 ('GET /api/v1/moments/time','GetMomentsTime','a single entity.Album object','a JSON array of monthly query.Moment results',
  [('internal/api/moments_time.go',r'c.JSON\(http.StatusOK, result\)'),('internal/entity/query/moments.go',r'type Moments \[\]Moment|func MomentsTime')]),
 ('GET /api/v1/photos/view','SearchPhotosView','an array described as search.Photo objects','an array of viewer.Result objects containing resolved viewer fields',
  [('internal/api/photos_search.go',r'UserPhotosViewerResults|c.JSON\(http.StatusOK, result\)'),('internal/entity/search/photos_viewer.go',r'func UserPhotosViewerResults'),('internal/entity/search/viewer/result.go',r'type Results \[\]Result|type Result struct')])]
for operation,opid,x,y,implementation in ops:
 R['accept']('photoprism',2,operation,x,y,'SPEC','openapi','schema.response_shape',
  contract=[(base+'swagger.json',r'"operationId": "'+opid+'"')],implementation=implementation)
print('Accepted items and exclusions:',R['finish_accept']('Four parent response schemas disagree with existing JSON result types; annotations and the checked-in document are corrected.'))
