import runpy
from pathlib import Path
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t50b.py'))
for method in ['GET','PUT','DELETE']:
 R['accept']('tyk',6,method+' /tyk/org/keys/{keyID}',
  'the organisation key operation is under /tyk/orgs/keys/{keyID}',
  'the router registers the operation under /tyk/org/keys/{keyName}',
  'SPEC','openapi','route.organization_key_prefix',contract=[('swagger.yml',r"/tyk/orgs/keys/\{keyID\}")],
  implementation=[('gateway/server.go',r'HandleFunc\("/org/keys/\{keyName')])
R['accept']('tyk',6,'POST /tyk/org/keys/{keyID}',
 'organisation key creation is documented on /tyk/org/keys without an identifier',
 'the router allows POST on the organisation key path containing keyName',
 'SPEC','openapi','route.organization_key_create_identifier',contract=[('swagger.yml',r'^  /tyk/org/keys:')],
 implementation=[('gateway/server.go',r'HandleFunc\("/org/keys/\{keyName')])
print('Accepted items and exclusions:',R['finish_accept']('The parent organisation-key paths disagree with existing router registrations; four operation discrepancies pass before the byte-order cap.'))
