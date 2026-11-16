from pathlib import Path
import runpy
R = runpy.run_path(str(Path(__file__).parents[1] / 'review_t49.py'))
R['accept']('service-api', 435, 'DELETE /user',
    'the supplied IDs select launches to delete',
    'resolve the supplied IDs as users and delete those user records',
    'SPEC', 'annotations', 'resource_kind.bulk-delete-users-versus-launches',
    [('ws/controller/UserController.java', r'@ApiOperation\("Delete specified launches by ids"\)')],
    [('ws/controller/UserController.java', r'return deleteUserHandler.deleteUsers\(deleteBulkRQ, user\)'),
     ('core/user/impl/DeleteUserHandlerImpl.java', r'deleteBulkRQ.getIds\(\).forEach\(userId|deleteUser\(userId, currentUser\)|User user = userRepository.findById|userRepository.delete\(user\)')],
    route=[('ws/controller/UserController.java', r'@RequestMapping\("/user"\)|^\s*@DeleteMapping$')])
print('Accepted/capped:', R['finish_accept'](
    'Parent operation description promises deletion of launches; its handler resolves and deletes users; the patch corrects the documented resource kind.'))
