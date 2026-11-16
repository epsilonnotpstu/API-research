from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
R['accept']('service-api',263,'GET /v1/{projectKey}/launch/{launchId}/report',
  'the launch export operation is scoped to the projectKey path',
  'load and export launchId globally without passing the path project membership to the export handler',
  'IMPL','annotations','resource_scope.launch-export-project',
  [('ws/controller/LaunchController.java',r'@RequestMapping\("/v1/\{projectKey\}/launch"\)|@GetMapping\(value = "/\{launchId\}/report"\)|Export specified launch')],
  [('ws/controller/LaunchController.java',r'exportLaunch\(launchId, format, outputStream, user\)'),('core/launch/impl/GetLaunchHandlerImpl.java',r'void exportLaunch|Launch launch = launchRepository.findById\(launchId\)')],confidence=2)
print('Accepted/capped:',R['finish_accept']('Project-scoped export passes launchId without project membership; handler looks it up globally; patch validates launch ownership against the path project.'))
