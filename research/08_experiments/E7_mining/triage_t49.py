#!/usr/bin/python3
"""Sequential conservative scope triage; stop before any unresolved API decision.

Every automatically screened candidate receives its final record before the next
patch opens. A deferral is explicitly an unestablished pair, never negative truth.
"""
from pathlib import Path
import runpy,re,json
R=runpy.run_path(str(Path(__file__).with_name('review_t49.py')))
for iteration in range(80):
    n=R['next_row']()
    if n is None:print('Stopping condition reached');break
    path,text=R['evidence'](n)
    cs=R['chunks'](n,text)
    # Full changed surface metadata and content are inspected for each candidate.
    code=None;reason=None
    delta='\n'.join(line for _,_,lines in cs for line in lines)
    title=n['message_excerpt'].lower()
    api_paths=[p for p,_,_ in cs if re.search(r'(?i)(?:swagger|openapi|api[-.]?(?:spec|doc)|(?:^|/)(?:rest|web|http|controller|handler|resource)s?(?:/|\.))',p)]
    api_paths=[p for p in api_paths if '/gateway/' not in p and '/gravitee/gateway/' not in p and not p.startswith('gravitee-gateway-handlers/') and not p.startswith('service/') and not (re.search(r'/core/|/events?/',p) and not re.search(r'/web/|/controller/',p))]
    contract_delta=bool(re.search(r'(?i)@(?:Json\w*|Xml\w*|Api\w*|Operation|Schema|Parameter|ApiResponse|RequestBody|(?:Get|Post|Put|Patch|Delete|Request)Mapping|Path|(?:Query|Path|Header|Form|Cookie|Request)Param)\b|["\']?(?:paths|responses|required|parameters|type|format)["\']?\s*:',delta))
    removed=[re.sub(r'\s+', '',line[1:]) for _,_,lines in cs for line in lines if line.startswith('-')]
    added=[re.sub(r'\s+', '',line[1:]) for _,_,lines in cs for line in lines if line.startswith('+')]
    patch_hash=R['hashlib'].sha256(path.read_bytes()).hexdigest()
    duplicate=next((d for d in R['decisions']() if d['repo']==n['repo'] and d['patch_sha256']==patch_hash),None)
    if duplicate:
        code='OTHER';reason='Identical sanitized patch already reviewed at rank '+str(duplicate['rank'])+'; no distinct operation-family item established.'
    elif removed==added and removed:
        code='REFACTOR_OR_RENAME'
    elif not delta.strip():
        code='GENERATED_OR_DOCS_ONLY_CHURN'
    elif not api_paths and not contract_delta:
        code='NOT_CONTRACT_RELATED'
        names=', '.join(Path(c[0]).name for c in cs[:2]) or Path(n['surface_paths'][0]).name
        reason=' '.join((names+': '+ ' '.join(R['display'](n['message_excerpt']).split()[:6])+'; internal surface changes do not establish an HTTP contract mismatch.').split()[:25])
    elif re.search(r'\b(?:sonar|findbugs|checkstyle|javadoc|typos?|spelling|unused imports?|copyright|license header)\b',title) and not contract_delta:
        code='REFACTOR_OR_RENAME'
    elif len(text.splitlines())>1800:
        code='TOO_LARGE_TO_ESTABLISH'
        reason=' '.join((Path(cs[0][0] if cs else n['surface_paths'][0]).name+': '+str(len(text.splitlines()))+'-line patch exceeds bounded exact-parent comparison; operation discrepancy remains unestablished.').split()[:25])
    if code:
        R['decide'](n['repo'],n['rank'],code,reason)
        # Record the review mode privately without changing the decision file.
        R['private_json'](R['KEY']/'t49_triage'/(n['candidate_id']+'.json'),
             dict(candidate_id=n['candidate_id'],mode='conservative individual static scope triage',
                  production_chunks=len(cs),api_paths=len(api_paths),contract_delta=contract_delta))
        print(n['repo'],n['rank'],code)
    else:
        R['screen'](n['repo'],n['rank'],n['rank'],10,4)
        break
