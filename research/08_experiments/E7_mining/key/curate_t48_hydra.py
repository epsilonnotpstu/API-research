"""Private exact-parent discovery evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
R['accept']('hydra',107,'GET /.well-known/openid-configuration',
 'claims_supported contains claim names and scopes_supported contains supported OAuth scope values',
 'populate claims_supported from the scope provider and scopes_supported from the claim provider',
 'IMPL','spec_file','response_body.discovery_claim_scope_swap',
 [('docs/api.swagger.json',r'"/.well-known/openid-configuration"|"claims_supported"|"scopes_supported"|"wellKnown":')],
 [('oauth2/handler.go',r'func .*WellKnownHandler|ClaimsSupported:|ScopesSupported:'),
  ('oauth2/doc.go',r'ClaimsSupported .*json|ScopesSupported .*json'),
  ('driver/configuration/provider_viper.go',r'func .*OIDCDiscoverySupportedClaims|func .*OIDCDiscoverySupportedScope|OIDC_DISCOVERY_CLAIMS_SUPPORTED|OIDC_DISCOVERY_SCOPES_SUPPORTED')],confidence=3)
R['decide']('hydra',107,'ACCEPT','Discovery contract distinguishes claim names from scopes; parent handler assigns the two providers in reverse, and the patch restores their respective fields.')
print('New accepted items:',len(R['accepted']()))
n=R['next_row']();R['screen'](n['repo'],n['rank'],n['rank'],12,4)
