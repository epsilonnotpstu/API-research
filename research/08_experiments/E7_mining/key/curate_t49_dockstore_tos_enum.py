from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
for op in ['GET /users/user','GET /users/{userId}']:
 R['accept']('dockstore',223,op,
  'the returned User tosversion enum permits only NONE and TOS_VERSION_1',
  'return the stored TOSVersion enum which also permits TOS_VERSION_2 through the JSON getter',
  'SPEC','openapi','response_enum.user-tos-version2',
  [('src/main/resources/openapi3/openapi.yaml',r'^        tosversion:|TOS_VERSION_1')],
  [('core/TOSVersion.java',r'TOS_VERSION_2'),('core/User.java',r'TOSVersion getTOSVersion|return this.tosVersion')],
  route=[('resources/UserResource.java',r'Get user by id|Get the logged-in user|return foundUser;|public User getUser')])
print('Accepted/capped:',R['finish_accept']('Parent User schema omits TOS_VERSION_2; parent enum and JSON getter expose it; patch adds the missing enum member.'))
