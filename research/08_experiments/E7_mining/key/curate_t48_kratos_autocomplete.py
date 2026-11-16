"""Private existing login-flow autocomplete enum evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
for endpoint in ['api','browser','flows']:
 R['accept']('kratos',81,'GET /self-service/login/'+endpoint,
  'input autocomplete is restricted to email, tel, url, current-password, new-password and one-time-code',
  'include username webauthn in identifier-first login input nodes when that strategy is enabled',
  'SPEC','spec_file','response_enum.login_autocomplete_username_webauthn',
  [('spec/api.json',r'"/self-service/login/'+endpoint+r'"|"autocomplete"|"one-time-code"|"loginFlow"')],
  [('idfirst/strategy_login.go',r'func .*PopulateLoginMethodIdentifierFirstIdentification|Autocomplete = "username webauthn"'),
   ('flow/login/handler.go',r'func .*NewLoginFlow|PopulateLoginMethodIdentifierFirstIdentification|func .*getLoginFlow|Write.*f\)'),
   ('ui/node/attributes.go',r'Autocomplete .*json:')],
  [('flow/login/handler.go',r'RouteInitBrowserFlow|RouteInitAPIFlow|RouteGetFlow')],confidence=2)
R['decide']('kratos',81,'ACCEPT','Three login flow responses use an autocomplete value absent from the parent input enum; documentation adds the already emitted value without changing it.')
print('New accepted items:',len(R['accepted']()))
