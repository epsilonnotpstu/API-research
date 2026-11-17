#!/usr/bin/python3
"""Conservative individual scope triage; never inspect beyond a pending final."""
import json,re,runpy
from pathlib import Path
R=runpy.run_path(str(Path(__file__).with_name('review_t50b.py')))
for iteration in range(100):
    n=R['next_row']()
    if n is None:print('Supervisor stopping condition reached');break
    path,text=R['evidence'](n);cs=R['chunks'](n,text)
    delta='\n'.join(line for _,_,lines in cs for line in lines)
    api=[p for p,_,_ in cs if re.search(r'(?i)swagger|openapi|api[-.]?(?:spec|doc)|(?:^|/)(?:rest|web|http|controllers?|handlers?|resources?|routers?|endpoints?)(?:/|\.)',p)]
    api=[p for p in api if not re.search(r'(?i)^routers/web/|/app/web/admin/|^controller/|/handler/file/|/org/apache/nifi/controller/',p)]
    data_delta='\n'.join(line for p,_,lines in cs if p.endswith(('.json','.yaml','.yml')) for line in lines)
    semantic=bool(re.search(r'(?i)@(?:Json\w*|Xml\w*|Api\w*|Operation|Schema|Parameter|ApiResponse|RequestBody|(?:Get|Post|Put|Patch|Delete|Request)Mapping|Path|(?:Query|Path|Header|Form|Cookie|Request)Param)\b|json:"|form:"|binding:"',delta) or re.search(r'(?i)["\x27]?(?:paths|responses|required|parameters|type|format)["\x27]?\s*:',data_delta))
    annotations=bool(re.search(r'(?m)^[+-].*(?:@Router|@Success|@Failure|swagger:route)',text))
    title=n['message_excerpt'].lower();code=None;reason=None
    patch_hash=R['hashlib'].sha256(path.read_bytes()).hexdigest()
    duplicate=next((d for d in R['decisions']() if d['repo']==n['repo'] and d['patch_sha256']==patch_hash),None)
    if duplicate:
        code='OTHER';reason='Identical sanitized patch already reviewed at rank '+str(duplicate['rank'])+'; no distinct operation-family item established.'
    elif not delta.strip() and not annotations:
        code='GENERATED_OR_DOCS_ONLY_CHURN'
    elif not api and not semantic and not annotations:
        code='NOT_CONTRACT_RELATED'
    elif re.search(r'(?i)\b(?:typos?|spelling|unused imports?|license header|file headers)\b',title) and not semantic and not annotations:
        code='REFACTOR_OR_RENAME'
    elif len(text.splitlines())>2200:
        code='TOO_LARGE_TO_ESTABLISH'
        reason=' '.join((Path(cs[0][0] if cs else n['surface_paths'][0]).name+': '+str(len(text.splitlines()))+'-line patch exceeds bounded exact-parent comparison; operation discrepancy remains unestablished.').split()[:25])
    if code:
        R['decide'](n['repo'],n['rank'],code,reason)
        R['private_json'](R['KEY']/'t50b_triage'/(n['candidate_id']+'.json'),dict(candidate_id=n['candidate_id'],mode='conservative individual static scope triage',chunks=len(cs),api_paths=len(api),semantic_delta=semantic,annotation_delta=annotations))
        print(n['repo'],n['rank'],code,flush=True)
    else:
        R['screen'](n['repo'],n['rank'],n['rank'],12,5)
        break
