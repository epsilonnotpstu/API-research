from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
R['accept']('service-api',255,'PUT /v1/{projectKey}/item/info',
  'the bulk item-update operation is scoped to the projectKey path',
  'load requested item IDs globally and update their descriptions after checking only that the path project exists',
  'IMPL','annotations','resource_scope.bulk-item-project-membership',
  [('ws/controller/TestItemController.java',r'@RequestMapping\("/v1/\{projectKey\}/item"\)|@PutMapping\(value = "/info"\)|Bulk update attributes and description')],
  [('core/item/impl/UpdateTestItemHandlerImpl.java',r'bulkInfoUpdate\(|projectRepository.existsById|testItemRepository.findAllById\(bulkUpdateRq.getIds\(\)\)|ItemInfoUtils.updateDescription')],
  route=[('ws/controller/TestItemController.java',r'updateTestItemHandler.bulkInfoUpdate|extractMembershipDetails\(user, projectKey\)')],confidence=2)
print('Accepted/capped:',R['finish_accept']('Project-scoped bulk update loads item IDs globally without checking their projects; patch validates each item against membership before updating.'))
