from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
R['accept']('service-api',163,'DELETE /users/{userId}/api-keys/{keyId}',
 'the API-key deletion route identifies both userId and keyId',
 'ignore userId and check existence and delete using keyId alone',
 'IMPL','annotations','resource_scope.user-api-key-owner',
 [('ws/controller/UserController.java',r'@RequestMapping\("/users"\)|@DeleteMapping\(value = "/\{userId\}/api-keys/\{keyId\}"\)')],
 [('ws/controller/UserController.java',r'return apiKeyHandler.deleteApiKey\(keyId\)'),('core/user/impl/ApiKeyHandlerImpl.java',r'apiKeyRepository.existsById\(id\)|apiKeyRepository.deleteById\(id\)')],confidence=2)
print('Accepted/capped:',R['finish_accept']('Nested API-key route binds userId but handler ignores it and deletes by keyId alone; patch constrains lookup by both identifiers.'))
