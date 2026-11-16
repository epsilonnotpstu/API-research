from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
R['accept']('service-api',206,'GET /v1/project/{projectName}/preference/',
  'the trailing-slash preference route returns HTTP 200 for a logged-in user',
  'require a projectKey path variable although that route binds only projectName',
  'IMPL','annotations','path_binding.preference-project-key',
  [('base/ws/controller/ProjectController.java',r'@GetMapping\(\{"/\{projectKey\}/preference", "/\{projectName\}/preference/"\}\)|@ResponseStatus\(HttpStatus.OK\)')],
  [('base/ws/controller/ProjectController.java',r'getUserPreference\(@PathVariable String projectKey')],confidence=2)
print('Accepted/capped:',R['finish_accept']('Trailing-slash route exposes projectName but handler requires projectKey; patch names the captured variable consistently.'))
