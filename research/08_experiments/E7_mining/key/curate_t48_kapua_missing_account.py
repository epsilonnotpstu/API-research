"""Private missing-account status evidence; first resource method fills cap."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
R['accept']('kapua',114,'PUT /{scopeId}/serviceConfigurations',
 'a missing target entity is reported as a 404 entityNotFound response',
 'dereference a missing scope account while updating its configuration, producing a generic server error',
 'IMPL','spec_file','status_code.service_configuration_missing_account',
 [('serviceConfiguration-scopeId.yaml',r'put:|404:|entityNotFound'),
  ('rest-api/resources/src/main/resources/openapi/openapi.yaml',r'entityNotFound:|entityNotFoundExceptionInfo:|httpErrorCode: 404')],
 [('resources/ServiceConfigurations.java',r'public Response update\(|Account account = accountService.find|account.getScopeId'),
  ('errors/ThrowableMapper.java',r'public Response toResponse|serverError|INTERNAL_SERVER_ERROR'),
  ('errors/KapuaEntityNotFoundExceptionMapper.java',r'public Response toResponse|Status.NOT_FOUND')],
 [('resources/ServiceConfigurations.java',r'@Path\("\{scopeId\}/serviceConfigurations"\)|@PUT')],confidence=2)
R['decide']('kapua',114,'ACCEPT','Bulk configuration update promises entity-not-found handling, but a null account is dereferenced; the patch throws the exception mapped to 404.')
print('New accepted items:',len(R['accepted']()))
