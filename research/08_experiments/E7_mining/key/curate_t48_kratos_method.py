"""Private password-login HTTP method evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
R['accept']('kratos',100,'GET /self-service/login/methods/password',
 'password login is available through GET at this path',
 'register the password login handler only for POST and generate a POST form',
 'SPEC','spec_file','http_method.password_login_get_post',
 [('.schema/api.swagger.json',r'"/self-service/login/methods/password"|"get"')],
 [('password/login.go',r'RouteLogin =|r.POST\(RouteLogin|Method: "POST"|func .*handleLogin')],confidence=3)
R['decide']('kratos',100,'ACCEPT','Password login is documented under GET, while parent routing and generated forms use POST; documentation changes the method to match routing.')
print('New accepted items:',len(R['accepted']()))
