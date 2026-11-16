"""Private whoami authorization parameter-location evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
R['accept']('kratos',121,'GET /sessions/whoami',
 'the Authorization parameter is supplied in the query string',
 'extract the bearer session token from the Authorization request header',
 'SPEC','spec_file','request_location.whoami_authorization_header',
 [('spec/swagger.json',r'"/sessions/whoami"|"name": "Authorization"|"in": "query"')],
 [('session/handler.go',r'func .*whoami|SessionManager\(\).FetchFromRequest'),
  ('session/manager_http.go',r'func .*FetchFromRequest|func .*extractToken|bearerTokenFromRequest|token := s.extractToken'),
  ('session/helper.go',r'func bearerTokenFromRequest|r.Header.Get\("Authorization"\)')],
 [('session/handler.go',r'RouteWhoami =|public.GET\(RouteWhoami')],confidence=3)
R['decide']('kratos',121,'ACCEPT','Whoami lists Authorization as a query parameter, while its parent session extractor reads the header; the specification corrects the location.')
print('New accepted items:',len(R['accepted']()))
