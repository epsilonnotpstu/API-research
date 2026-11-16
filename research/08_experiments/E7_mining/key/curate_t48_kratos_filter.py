"""Private identity similarity query parameter evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
R['accept']('kratos',115,'GET /admin/identities',
 'preview_credentials_identifier_similar selects identity credentials by partial identifier similarity',
 'read credentials_identifier_similar instead and leave the documented preview parameter unused',
 'IMPL','spec_file','request_parameter.identity_similarity_preview_name',
 [('spec/api.json',r'"/admin/identities"|"name": "preview_credentials_identifier_similar"')],
 [('identity/handler.go',r'query.Get\("credentials_identifier_similar"\)|params.CredentialsIdentifierSimilar|func .*parseListIdentitiesParameters|func .*list\(')],
 [('identity/handler.go',r'admin.GET\(RouteCollection, h.list\)|RouteCollection .*"/identities"')],confidence=3)
R['decide']('kratos',115,'ACCEPT','Identity listing documents the preview-prefixed similarity filter, but the parent parser reads its unprefixed name; the parser is corrected.')
print('New accepted items:',len(R['accepted']()))
