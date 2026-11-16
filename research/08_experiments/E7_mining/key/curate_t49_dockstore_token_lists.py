from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
for endpoint,name in [('github.com','Github'),('quay.io','Quay'),('dockstore','Dockstore')]:
 R['accept']('dockstore',152,'GET /users/{userId}/tokens/'+endpoint,
  'the response annotation declares a single Token',
  'return a List<Token> from the token DAO',
  'SPEC','annotations','response_shape.user-token-list',
  [('resources/UserResource.java',r'Get '+name+' tokens with user id.*response = Token.class\)')],
  [('resources/UserResource.java',r'List<Token> get'+name+'UserTokens|return tokenDAO.find')],
  helpers=['jdbi/TokenDAO.java'])
print('Accepted/capped:',R['finish_accept']('Three token endpoints declare scalar Token responses but return lists; patch adds responseContainer List to their annotations.'))
