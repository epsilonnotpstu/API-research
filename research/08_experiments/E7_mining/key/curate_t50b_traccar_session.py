import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('traccar',17,'POST /api/session',
 'a successful request creates a new session',
 'successful login returns the user without storing the user identifier in the HTTP session',
 'IMPL','openapi','session.login_state',confidence=2,
 contract=[('swagger.json',r'Create a new Session')],
 implementation=[('SessionResource.java',r'public User add\(|LogAction.login\(user.getId\(\)|request.getSession\(\).removeAttribute\(USER_ID_KEY\)')])
print('Accepted items and exclusions:',R['finish_accept']('The contract promises session creation, but successful login returns the user without setting session identity; the patch adds that state.'))
