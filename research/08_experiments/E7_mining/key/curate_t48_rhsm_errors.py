"""Private shared error-envelope evidence; operation order follows parent spec."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
operations=[
 ('DELETE /api/swatch-contracts/internal/contracts/{uuid}','deleteContractByUUID'),
 ('GET /api/swatch-contracts/internal/contracts','getContract'),
 ('POST /api/swatch-contracts/internal/contracts','createContract'),
 ('POST /api/swatch-contracts/internal/rpc/contracts/sync','syncAllContracts'),
 ('POST /api/swatch-contracts/internal/rpc/partner/contracts','createPartnerEntitlementContract'),
 ('POST /api/swatch-contracts/internal/subscriptions','saveSubscriptions'),
 ('GET /api/swatch-contracts/internal/subscriptions','getSubscriptions'),
 ('POST /api/swatch-contracts/internal/subscriptions/umb','syncUmbSubscription'),
 ('POST /api/swatch-contracts/internal/rpc/subscriptions/sync','syncAllSubscriptions')]
for operation,method in operations:
 R['accept']('rhsm-subscriptions',104,operation,
  'the default JSON error response is an Errors envelope with a required errors array',
  'serialize a single Error object with code, status, title and optional detail directly from exception mappers',
  'SPEC','spec_file','response_body.contract_service_error_envelope',
  [('swatch-contracts/src/main/resources/META-INF/openapi.yaml',r'operationId: '+method+r'|    Errors:|        - errors|    ErrorResponse:|schemas/Errors')],
  [('contract/resource/DefaultExceptionMapper.java',r'class DefaultExceptionMapper|public Response toResponse|new Error\(\)|\.entity\('),
   ('contract/resource/ContractsExceptionMapper.java',r'class ContractsExceptionMapper|new Error\(\)|\.entity\('),
   ('contract/resource/SubscriptionsExceptionMapper.java',r'class SubscriptionsExceptionMapper|new Error\(\)|\.entity\(')],
  [('contract/resource/ContractsResource.java',r'public .* '+method+r'\(')],confidence=2)
R['decide']('rhsm-subscriptions',104,'ACCEPT','Nine existing operations require an errors-array envelope, while parent exception mappers emit one Error directly; schema correction matches the mappers and fills the cap.')
print('New accepted items:',len(R['accepted']()))
