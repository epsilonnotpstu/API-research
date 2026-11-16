"""Private parent-state permissions serialization evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
R['accept']('kapua',71,'GET /authentication/info',
 'the JSON loginInfo response has rolePermissions, groupPermissions and groupRolePermissions array properties',
 'map those collections to the singular rolePermission, groupPermission and groupRolePermission element names',
 'IMPL','spec_file','response_body.login_info_permission_collection_names',
 [('authentication-info.yaml',r'/authentication/info:|application/json|loginInfo'),
  ('authentication/authentication.yaml',r'rolePermissions:|groupPermissions:|groupRolePermissions:')],
 [('token/LoginInfo.java',r'XmlAccessorType|XmlElement\(name = "(?:rolePermission|groupPermission|groupRolePermission)"'),
  ('token/shiro/LoginInfoImpl.java',r'getRolePermission|getGroupPermission|getGroupRolePermission'),
  ('core/MoxyJsonConfigContextResolver.java',r'JSON_WRAPPER_AS_ARRAY_NAME')],
 [('resources/Authentication.java',r'@Path\("/authentication"\)|@Path\("info"\)|public LoginInfo loginInfo|return authenticationService.getLoginInfo')],confidence=2)
R['decide']('kapua',71,'ACCEPT','LoginInfo schema uses plural permission arrays; parent JAXB properties use singular names, and the patch introduces the corresponding plural wrappers.')
print('New accepted items:',len(R['accepted']()))
