#!/usr/bin/python3
"""Offline, read-only Git mining. Never imports or executes upstream content."""
import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OVERFLOW = Path('/run/media/afridi/Shared Data/api_research_upstream')
EARLIER = ROOT.parent / '_external/upstream'
REPOS = {p.stem: str(p) for p in sorted(OVERFLOW.glob('*.git'))}
REPOS.update({p.name: str(p / '.git') for p in sorted(EARLIER.iterdir()) if (p / '.git').is_dir()})
CUE = re.compile(r'\b(swagger|openapi|api[ -]?doc|spec|contract|documentation|required|status[ -]?code|response[ -]?code|nullable|match|align|fix|correct)\w*', re.I)
STRONG = re.compile(r'swagger|openapi|api[ -]?doc|contract|status[ -]?code|response[ -]?code|nullable|documentation', re.I)
ANNOT = re.compile(r'@(Operation|Api(?:Operation|Response|Responses|Param|Model|ModelProperty|ImplicitParam|ImplicitParams)?|Schema|Parameter|Parameters|Content|RequestBody)\b')
BEHAV = re.compile(r'@(\w*Mapping|Path|GET|POST|PUT|DELETE|PATCH|Json\w+|NotNull|NotBlank|Size|Valid|ExceptionHandler|ControllerAdvice)\b')
PATH_SURFACE = re.compile(r'(controller|resource|endpoint|dto|model|exception|handler|response|request|swagger|openapi|api-doc|/api/)', re.I)
SECRET = re.compile(r'(?i)(password|passwd|client.?secret|private.?key|access.?token|refresh.?token|authorization\s*[:=]|bearer\s+[a-z0-9]|BEGIN .+PRIVATE KEY|jdbc:.*(?:password|user)=)')

def redact(text):
    out = []
    contact_remaining = 0
    for line in text.splitlines():
        line = re.sub(r'"contact"\s*:\s*\{[^}]*\}', '"contact": "[REDACTED contact]"', line)
        if re.search(r'^[-+ ]*\s*contact\s*:', line):
            contact_remaining = 8
        elif contact_remaining:
            contact_remaining -= 1
            if re.search(r'\bname\s*:', line): line = '[REDACTED contact name]'
        if re.search(r'(?i)\bCreated by\b|@author\b', line):
            line = '[REDACTED personal attribution]'
        line = re.sub(r'(?i)(?:Signed-off-by|Co-authored-by|Author|Committer):.*', '[REDACTED personal attribution]', line)
        if SECRET.search(line) and re.search(r'["\x27:=]', line):
            # Keep line positions, but never persist credential-like assignments.
            line = '[REDACTED credential-related line]'
        line = re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[REDACTED email]', line)
        line = re.sub(r'(?i)([?&][^\s=&"<>]*(?:token|secret|password|api.?key)[^\s=&"<>]*=)[^&\s"<>]+', r'\1[REDACTED]', line)
        line = re.sub(r"\b[A-Z][a-z]+'s (?:changes|specification)", '[REDACTED personal reference]', line)
        line = re.sub(r'https?://[^\s/:]+:[^\s/@]+@', 'https://[REDACTED]@', line)
        line = re.sub(r'\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]+|AKIA[A-Z0-9]{16})\b', '[REDACTED token]', line)
        if re.match(r'\s*(?:Signed-off-by|Co-authored-by|Author|Committer):', line, re.I):
            line = '[REDACTED personal attribution]'
        out.append(line)
    return '\n'.join(out)

def git(repo, *args):
    assert args[0] in {'log', 'show', 'diff', 'ls-tree', 'cat-file', 'rev-list'}
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_PAGER='cat', GIT_TERMINAL_PROMPT='0')
    return subprocess.run(['git', '--git-dir=' + REPOS[repo], *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env).stdout

def blob(repo, rev, path):
    return git(repo, 'show', rev + ':' + path).decode('utf-8', 'replace')

def numbered(text):
    return '\n'.join(f'{i}: {line}' for i, line in enumerate(redact(text).splitlines(), 1))

def dump(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def main():
    inventories, pool = [], []
    for repo in REPOS:
        head = git(repo, 'rev-list', '-1', 'HEAD').decode().strip()
        paths = git(repo, 'ls-tree', '-r', '--name-only', head).decode().splitlines()
        specs, annotations, behaviours, generators, popularity, behaviour_paths, python_surfaces = [], [], [], [], [], [], []
        for path in paths:
            suffix = Path(path).suffix.lower()
            if suffix not in {'.java', '.kt', '.py', '.yaml', '.yml', '.json', '.xml', '.md', '.gradle', '.properties'}:
                continue
            # Avoid bulk fixtures, vendored schemas, credentials and unrelated prose.
            if any(s in path.lower() for s in ['node_modules/', '/target/', '.lock', 'package-lock']):
                continue
            content = blob(repo, head, path)
            if suffix in {'.yaml', '.yml', '.json'} and re.search(r'^(?:openapi|swagger)\s*:|^\s{0,2}"(?:openapi|swagger)"\s*:', content, re.M):
                role = 'service_contract'
                if repo == 'microcks' and not path.startswith('api/microcks-openapi-'): role='fixture_or_imported_example'
                specs.append({'path': path, 'line': next(i for i,l in enumerate(content.splitlines(),1) if re.search(r'(openapi|swagger)\W*:',l)), 'sha256': hashlib.sha256(content.encode()).hexdigest(), 'role':role})
            if suffix in {'.java', '.kt'}:
                a = [i for i,l in enumerate(content.splitlines(),1) if ANNOT.search(l)]
                b = [i for i,l in enumerate(content.splitlines(),1) if BEHAV.search(l)]
                if a and re.search(r'import\s+(?:io\.swagger|com\.wordnik\.swagger)',content): annotations.append({'path':path, 'lines':a})
                if b: behaviours.append({'path':path, 'lines':b})
                if PATH_SURFACE.search(path) and not re.search(r'/tests?/',path,re.I): behaviour_paths.append(path)
            if suffix == '.py':
                hits=[i for i,l in enumerate(content.splitlines(),1) if re.search(r'FastAPI|APIRouter|BaseModel|@\w+\.(?:get|post|put|delete|patch)\(',l)]
                if hits: python_surfaces.append({'path':path,'lines':hits})
            if suffix in {'.xml', '.gradle', '.properties', '.yaml', '.yml'}:
                hits = [i for i,l in enumerate(content.splitlines(),1) if re.search(r'springdoc|springfox|swagger|openapi',l,re.I)]
                if hits: generators.append({'path':path,'lines':hits})
            if Path(path).name.lower().startswith('readme'):
                for i,l in enumerate(content.splitlines(),1):
                    if re.search(r'stars|stargazer',l,re.I): popularity.append({'path':path,'line':i,'text':redact(l)[:350]})
        history = git(repo,'log','--all','--no-merges','--date=short','--format=@@%H\t%P\t%cs\t%s','--name-status').decode('utf-8','replace')
        commits = []
        for block in history.split('@@')[1:]:
            lines = block.splitlines()
            sha, parents, date, message = lines[0].split('\t',3)
            changes = [l.split('\t') for l in lines[1:] if '\t' in l]
            commits.append((sha,parents,date,message,changes))
            cue = CUE.findall(message)
            surface = [c[-1] for c in changes if PATH_SURFACE.search(c[-1]) or c[-1].endswith(('.java','.kt')) or c[-1] in [s['path'] for s in specs]]
            if not parents or not cue or not surface: continue
            # Broad recall pool; additions, churn and ambiguous features are excluded in review.
            excluded = bool(re.search(r'^(?:bump|merge|release|chore\(deps\)|build\(deps\))\b|dependabot|renovate',message,re.I))
            if excluded: continue
            score = 10 * bool(STRONG.search(message)) + 4 * bool(re.search(r'fix|correct|align|match|required',message,re.I)) + min(len(surface),4)
            pool.append(dict(repo=repo,fix_commit=sha,parent_commit=parents.split()[0],date=date,message_excerpt=redact(message)[:160],score=score,changed_files=len(changes),surface_paths=' | '.join(surface),changes=changes))
        inventories.append(dict(repo=repo,git_dir=REPOS[repo],head=head,commit_count=len(commits),all_reachable_commit_count=int(git(repo,'rev-list','--all','--count')),spec_files=specs,annotation_files=annotations,behaviour_files=behaviours,behaviour_path_files=behaviour_paths,python_generated_surfaces=python_surfaces,generator_references=generators,popularity_evidence=popularity,stars='unavailable_offline'))
        print(json.dumps({'repo':repo,'commits':len(commits),'spec_files':len(specs),'annotation_files':len(annotations),'behaviour_files':len(behaviours),'candidates':sum(r['repo']==repo for r in pool)}),flush=True)
    pool.sort(key=lambda r:(r['repo'],-r['score'],r['fix_commit']))
    for i,row in enumerate(pool,1): row['candidate_id']=f'C{i:04}'
    dump('inventory.json',inventories)
    dump('candidate_pool.json',pool)
    dump('mining_manifest.json',dict(started_utc=STARTED,finished_utc=dt.datetime.now(dt.timezone.utc).isoformat(),repos=REPOS,heuristic='cue + changed surface path; rank strong cues, correction cues, surface count; SHA tie break',no_network=True))

STARTED=dt.datetime.now(dt.timezone.utc).isoformat()
if __name__ == '__main__': main()
