"""Private reference-target URL parent evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
for operation,source,method in [
 ('GET /ids/globalIds/{globalId}','rest/v3/impl/IdsResourceImpl.java','getContentByGlobalId'),
 ('GET /groups/{groupId}/artifacts/{artifactId}/versions/{versionExpression}/content','rest/v3/impl/GroupsResourceImpl.java','getArtifactVersionContent')]:
 R['accept']('apicurio-registry',155,operation,
  'references=REWRITE rewrites external references to valid registry content references',
  'rewrite each reference to a version metadata URL without the content suffix, so following it returns metadata instead of the referenced artifact content',
  'IMPL','spec_file','response_reference.rewrite_targets_metadata',
  [('api-specifications/registry/v3/openapi.json',r'"'+operation.split(' ',1)[1].replace('{',r'\{').replace('}',r'\}')+r'"|How to handle references when retrieving content|registry \(`REWRITE`\)|The artifact version.s metadata')],
  [('rest/v3/impl/AbstractResourceImpl.java',r'HandleReferencesType.REWRITE|rewriteReferences|String path = String.format|resolveReferenceUrls'),
   (source,r'public Response '+method+r'|handleContentReferences')],confidence=3)
R['decide']('apicurio-registry',155,'ACCEPT','Two content endpoints promise usable rewritten references, but parent URLs resolve to version metadata; adding the content suffix restores content reference targets.')
print('New accepted items:',len(R['accepted']()))
assert R['next_row']() is None
