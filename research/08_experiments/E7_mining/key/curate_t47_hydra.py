"""Private evidence for scope declarations and already-handled JSON responses."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t47.py'))
a=R['accept'];d=R['decide']
for operation,method in [
    ('GET /warden/groups','FindGroupNames'),
    ('POST /warden/groups','CreateGroup'),
    ('GET /warden/groups/{id}','GetGroup'),
    ('DELETE /warden/groups/{id}','DeleteGroup'),
    ('POST /warden/groups/{id}/members','AddGroupMembers'),
    ('DELETE /warden/groups/{id}/members','RemoveGroupMembers')]:
    a('hydra',101,operation,
      'the required OAuth scope is hydra.groups',
      'require hydra.warden.groups through the token scope guard',
      'SPEC','spec_file','security_scope.warden_group_management',
      [('docs/api.swagger.json',r'"hydra.groups"')],
      [('warden/group/handler.go',r'func \(h \*Handler\) '+method+r'\(|Scope\s+= "hydra.warden.groups"|\}, Scope\); err != nil'),
       ('warden/warden_local.go',r'func \(w \*LocalWarden\) TokenAllowed|IntrospectToken\(ctx, token, fosite.AccessToken'),
       ('warden/warden_strategy.go',r'func matchScopes|if !ss\(granted, scope\)|matchScopes\(c.ScopeStrategy')],
      [('warden/group/handler.go',r'r\.(?:GET|POST|DELETE)\(GroupsHandlerPath')],confidence=2)
d('hydra',101,'ACCEPT','Six group operations document hydra.groups, while every parent handler passes hydra.warden.groups to the scope guard.')
for resource,method in [('login','GetLoginRequest'),('consent','GetConsentRequest'),('logout','GetLogoutRequest')]:
    a('hydra',103,'GET /oauth2/auth/requests/'+resource,
      'an already handled request returns one 410 JSON requestWasHandledResponse object',
      'write that 410 object and then continue to serialize the ordinary request into the same response',
      'IMPL','spec_file','response_body.already_handled_json_fallthrough',
      [('spec/api.json',r'"/oauth2/auth/requests/'+resource+r'"|"requestWasHandledResponse": \{|"410": \{')],
      [('consent/handler.go',r'func \(h \*Handler\) '+method+r'\(|if request.WasHandled|WriteCode\(w, r, http.StatusGone|h.r.Writer\(\).Write\(w, r, request\)')],
      [('consent/handler.go',r'admin.GET\((?:Login|Consent|Logout)Path')],confidence=2)
d('hydra',103,'ACCEPT','Three already-handled request handlers write their documented 410 object but fall through to a second JSON write; the patch returns immediately.')
print('Accepted items from this reviewed repository:',9)
