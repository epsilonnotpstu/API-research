import runpy,re
from pathlib import Path
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t50.py'))
B=runpy.run_path(str(Path(__file__).resolve().parents[1]/'build.py'))
n=R['next_row']();R['record_preview'](n,'exact parent response-set enumeration')
contract='src/main/config/openapi/v2/openapi-user.yaml'
raw=R['M']['git'](n['repo'],'show',n['parent_commit']+':'+contract).decode()
lines,nodes=B['yaml_nodes'](raw)
manager='api/v2/SearchApiV2Manager.java'
code='api/v2/V2ErrorCode.java';writer='api/v2/V2EnvelopeWriter.java'
ops=[('get',p) for p in ['/health','/suggest-words','/labels','/related-queries','/related-content','/ui/config','/auth/me']]+[('post','/auth/logout')]
for method,path in ops:
 a,z=nodes[('paths',path,method)]
 opid=next(x.strip() for x in lines[a:z] if 'operationId:' in x)
 assert ('paths',path,method,'responses','400') not in nodes
 R['accept']('fess',1,method.upper()+' /api/v2'+path,
  'the listed responses omit 400 for undecodable query parameters',
  'undecodable query parameters produce 400 invalid_request before dispatch',
  'SPEC','openapi','status.undecodable_parameters',contract=[(contract,re.escape(opid))],
  implementation=[(manager,r'request.getParameterNames|malformed request parameters'),(code,r'INVALID_REQUEST\('),(writer,r'res.setStatus\(code.defaultHttpStatus')],confidence=3)
R['accept']('fess',1,'DELETE /api/v2/tags/{tagId}',
 'the listed deletion responses omit 409 Conflict',
 'exhausted concurrent deletion retries return 409 Conflict',
 'SPEC','openapi','status.tag_delete_conflict',contract=[(contract,r'operationId: tagsDeleteV2')],
 implementation=[('api/v2/handlers/TagsHandler.java',r'private Map.*deleteTag|failed|the tag was changed concurrently'),(code,r'CONFLICT\('),(writer,r'res.setStatus\(code.defaultHttpStatus')],
 route=[(manager,r'tagsHandler.handle')])
R['accept']('fess',1,'POST /api/v2/auth/login',
 'the listed login responses omit 403 Forbidden',
 'the baseline cross-site origin check returns 403 before login dispatch',
 'SPEC','openapi','status.login_origin_forbidden',contract=[(contract,r'operationId: authLoginV2')],
 implementation=[(manager,r'cross-site request blocked'),(code,r'FORBIDDEN\('),(writer,r'res.setStatus\(code.defaultHttpStatus')],
 helpers=['src/main/java/org/codelibs/fess/api/v2/handlers/OriginValidator.java','src/main/java/org/codelibs/fess/api/v2/handlers/CsrfRequirement.java'])
R['private_json'](R['KEY']/'t50_fess_scope.json',dict(established_operations=10,other_schema_edits='Not staged: index-backed schema variants and nullable highlighting lack complete bounded parent evidence. Neither can precede the retained operations in byte order.'))
print('Accepted items and exclusions:',R['finish_accept']('Parent handlers emit unlisted error responses; ten operation discrepancies established, followed by the byte-order cap.'))
