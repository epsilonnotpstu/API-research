from pathlib import Path
import runpy
R = runpy.run_path(str(Path(__file__).parents[1] / 'review_t49.py'))
controller = 'ws/controller/BugTrackingSystemController.java'
for method, name in [('DELETE', 'deleteExternalSystem'), ('GET', 'getExternalSystem')]:
    R['accept']('service-api', 382,
        method + ' /{projectName}/external-system/{systemId}',
        'the project path variable is named projectName',
        'request a required projectId path variable that is absent from the route',
        'IMPL', 'annotations', 'path_binding.external-system-project-name',
        [(controller, r'@RequestMapping\("/\{projectName\}/external-system"\)')],
        [(controller, r'public .* ' + name + r'\(@PathVariable Long projectId')],
        route=[(controller, r'@(?:Get|Delete)Mapping\(value = "/\{systemId\}"\)')],
        confidence=2)
print('Accepted/capped:', R['finish_accept'](
    'Parent routes expose projectName but GET and DELETE bind nonexistent projectId; the patch changes both bindings to projectName.'))
