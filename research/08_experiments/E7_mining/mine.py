#!/usr/bin/python3
"""Direction-neutral offline discovery; upstream bytes are data, never code."""
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'E6_realfix'
OLD = runpy.run_path(str(BASE / 'build_e6_blind.py'))
REPOS = OLD['discover_repos']()
NEW = dict(zip('sldt-digital-twin-registry basyx-java-server-sdk FAAAST-Service kapua apicurio-registry nessie polaris ditto kratos hydra harbor gravitee-api-management'.split(),
               [19,84,94,247,957,1531,2119,952,13960,17667,29733,470]))
CUE = re.compile(r'\b(?:fix(?:es|ed|ing)?|correct\w*|align\w*|match\w*|mismatch\w*|wrong|missing|incorrect\w*|inconsisten\w*|conform\w*|according to (?:the )?(?:spec|docs)|bug\w*)\b', re.I)
STRONG = re.compile(r'\b(?:mismatch\w*|incorrect\w*|inconsisten\w*|wrong|align\w*|conform\w*|according to (?:the )?(?:spec|docs))\b', re.I)
MEDIUM = re.compile(r'\b(?:fix(?:es|ed|ing)?|correct\w*|bug\w*)\b', re.I)
OP = re.compile(r'controller|resource|handler|endpoint|route|validator|serializ|exception|dto|model|openapi|swagger|api.?spec|api.?doc|(?:^|/)api/', re.I)
CODE = re.compile(r'\.(?:java|kt|go|py|js|ts|rb|cs|php)$', re.I)
DATA = re.compile(r'\.(?:yaml|yml|json)$', re.I)
SKIP = re.compile(r'(?:^|/)(?:tests?|generated|target|vendor|node_modules|fixtures?)/|src/test|_test\.go$|\.test\.|\.spec\.', re.I)

def rank_candidate(message,surfaces):
    strength=3 if STRONG.search(message) else 2 if MEDIUM.search(message) else 1
    return 10*strength+int(any(OP.search(p) for p in surfaces))

def safe(text):
    # T44 scans, extended to cover attribution in diff-prefixed source lines.
    lines = text.splitlines(keepends=True)
    cleaned = []
    for line in lines:
        line = re.sub(r'(?i)\b(?:signed-off|co-authored|reviewed|acked|tested|reported|suggested|approved|contributed)-by\s*:.*', '[REDACTED attribution]', line)
        prefix = line[:1] if line[:1] in {'+', '-', ' '} else ''
        value = line[len(prefix):]
        if re.search(r'(?i)@author|\bcopyright\b|\blicensed to\b|\b(?:signed-off|co-authored|reviewed|acked|tested|reported|suggested|approved|contributed)-by\s*:|\b(?:author|committer)\s*:|\bcreated by\b|\bthanks to\b', value):
            cleaned.append(prefix + '[REDACTED attribution]\n')
        else:
            cleaned.append(line)
    return OLD['redact'](''.join(cleaned).encode()).decode()

def git(repo, *args):
    assert args[0] in {'log','show','diff','ls-tree','cat-file','rev-list','merge-base'}
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_PAGER='cat', GIT_TERMINAL_PROMPT='0', GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_NO_REPLACE_OBJECTS='1', GIT_NO_LAZY_FETCH='1')
    for k in list(env):
        if k in {'GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_COMMON_DIR','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'} or k.startswith('GIT_CONFIG_') and k not in {'GIT_CONFIG_NOSYSTEM','GIT_CONFIG_GLOBAL'}:
            del env[k]
    r = subprocess.run(['git','--no-pager','--no-optional-locks','-c','core.hooksPath=/dev/null','-c','core.fsmonitor=false','--git-dir='+str(REPOS[repo]),*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
    if r.returncode: raise RuntimeError('Read-only git failed: '+args[0])
    return r.stdout

def dump(path, data):
    with path.open('x') as f: json.dump(data,f,indent=2,ensure_ascii=False); f.write('\n')

def load_sources(): return json.loads((HERE/'key/candidate_sources.json').read_text())

def main():
    assert not (HERE/'candidate_pool.json').exists(), 'Refusing to overwrite frozen pool'
    reviewed=set(); earlier=set(); stars=dict(NEW)
    for name in ['candidates.csv','t43/candidates.csv']:
        for r in csv.DictReader((BASE/name).open()):
            earlier.add(r['repo'])
            if r['review_status'] in {'accepted','rejected','deferred'}: reviewed.add((r['repo'],r['fix_commit']))
    for name in ['e6_repo_stars.csv','t43_repo_meta.csv']:
        for r in csv.DictReader((BASE/name).open()): stars[r['repo']]=r['stars']
    # Task's 22 earlier bare clones; the three working clones are only used for exploratory excerpts.
    requested=sorted(set(NEW) | {r for r in earlier if REPOS.get(r,Path()).suffix=='.git'})
    sources=[]; inventory=[]
    for repo in requested:
        if repo not in REPOS:
            inventory.append(dict(repo=repo,missing=True)); continue
        raw=git(repo,'log','--all','--no-merges','--date=short','--format=%x00%H%x09%P%x09%cs%x09%s','--name-status').decode('utf-8','replace')
        count=0
        for block in raw.split('\0')[1:]:
            ls=block.splitlines(); sha,parents,date,msg=ls[0].split('\t',3); count+=1
            if not parents or (repo,sha) in reviewed or not CUE.search(msg): continue
            if re.search(r'^(?:revert|release|bump|merge|chore\(deps\)|build\(deps\))\b|dependabot|renovate|\b(?:reformat|formatting|spotless)\b',msg,re.I): continue
            changes=[l.split('\t') for l in ls[1:] if '\t' in l]
            paths=[c[-1] for c in changes]
            surfaces=[p for p in paths if not SKIP.search(p) and (CODE.search(p) and OP.search(p) or DATA.search(p))]
            if not surfaces:continue
            # DATA paths are recall candidates; parent inspection must establish a service contract or local $ref.
            score=rank_candidate(msg,surfaces)
            sources.append(dict(repo=repo,fix_commit=sha,parent_commit=parents.split()[0],date=date,message_excerpt=safe(msg).strip()[:160],score=score,stars=stars.get(repo,'unavailable_offline'),surface_paths=surfaces,changes=changes))
        inventory.append(dict(repo=repo,missing=False,nonmerge_commits=count,candidates=sum(x['repo']==repo for x in sources),stars=stars.get(repo,'unavailable_offline')))
        print(json.dumps(inventory[-1]),flush=True)
    sources.sort(key=lambda r:(r['repo'],-r['score'],r['fix_commit']))
    ranks={}
    for i,r in enumerate(sources,1):
        ranks[r['repo']]=ranks.get(r['repo'],0)+1;r['rank']=ranks[r['repo']];r['candidate_id']=f'C{i:05}'
    pool=[{k:r[k] for k in ['candidate_id','repo','rank','score','surface_paths']} for r in sources]
    dump(HERE/'key/candidate_sources.json',sources)
    dump(HERE/'candidate_pool.json',pool)
    dump(HERE/'inventory.json',inventory)
    dump(HERE/'freeze.json',dict(pool_sha256=hashlib.sha256((HERE/'candidate_pool.json').read_bytes()).hexdigest(),source_sha256=hashlib.sha256((HERE/'key/candidate_sources.json').read_bytes()).hexdigest(),prior_review_exclusions=len(reviewed),rule='repo, descending correction-cue strength (3 strong alignment/error, 2 correction, 1 missing/match), operation-specific path bit, ascending SHA; no direction terms',code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))

if __name__=='__main__':main()
