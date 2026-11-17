import runpy
from pathlib import Path
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t50b.py'))
R['accept']('datarhei-core',8,'POST /api/v3/events',
 'the request consumes text/event-stream or application/x-json-stream',
 'request binding requires an application/json Content-Type and JSON event filters',
 'SPEC','openapi','content_type.event_filter_request',contract=[('docs/swagger.yaml',r'^  /api/v3/events:')],
 implementation=[('http/handler/api/events.go',r'ShouldBindJSON\(c, &filters\)'),('http/handler/util/util.go',r'!strings.HasPrefix\(ctype, echo.MIMEApplicationJSON\)|func ShouldBindJSON')])
print('Accepted items and exclusions:',R['finish_accept']('The parent event endpoint documents streaming request media types, but its existing JSON binder requires application/json; the patch corrects consumes.'))
