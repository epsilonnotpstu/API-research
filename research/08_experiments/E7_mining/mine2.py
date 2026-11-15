#!/usr/bin/python3
"""Content-verified offline discovery. No upstream code is executed."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import posixpath
import re
import runpy

HERE = Path(__file__).resolve().parent
M = runpy.run_path(str(HERE / 'mine.py'))
git = M['git']
safe = M['safe']
KEY = HERE / 'key'
DATA = re.compile(r'\.(?:ya?ml|json)$', re.I)
JVM = re.compile(r'\.(?:java|kt)$', re.I)
CODE = re.compile(r'\.(?:java|kt|go)$', re.I)
EXCLUDE = re.compile(r'(?:^|/)(?:\.github|\.circleci|ci|helm|charts?|k8s|kubernetes|docker|compose|deploy(?:ment)?s?|terraform|tests?|testing|testfixtures|fixtures?|generated|target|vendor|node_modules|examples?|samples?|benchmarks?|sdks?|clients?|client-go|httpclient(?:-next)?|[^/]*-sdk|[^/]*-examples)(?:/|$)|src/(?:test|it)/|_test\.go$|\.test\.|\.spec\.', re.I)
DOCS = re.compile(r'(?:^|/)(?:docs?|documentation|website|site)(?:/|$)', re.I)
BEHAVIOUR = re.compile(r'controller|resource|handler|endpoint|route|validator|serializ|exception|dto|model|mapper|(?:^|/)(?:api|rest|web|http)(?:/|$)', re.I)
JVM_IMPORT = re.compile(r'(?m)^\s*import\s+(?:static\s+)?(?:io\.swagger\.|springfox\.|org\.springdoc\.|io\.javalin\.openapi\.)')
ANNOTATION_USE = re.compile(r'@(?:OpenApi|Operation|Api|ApiOperation|ApiResponse|ApiResponses|Schema|ApiModel|ApiParam|Parameter|RequestBody|RouterOperation|RouterOperations)\b')
SKIP_MESSAGE = re.compile(r'^(?:revert|release|bump|merge|chore\(deps\)|build\(deps\))\b|dependabot|renovate|\b(?:reformat|formatting|spotless)\b', re.I)


def excluded(path):
    return bool(EXCLUDE.search(path))


def openapi(raw):
    """Only a top-level version key is a root; extensions alone mean nothing."""
    try:
        value = json.loads(raw)
        return isinstance(value, dict) and any(isinstance(value.get(k),str) and re.fullmatch(r'(?:2\.0|3\.\d+(?:\.\d+)?(?:[-+][\w.-]+)?)',value[k]) for k in ('openapi','swagger'))
    except (ValueError, UnicodeDecodeError):
        return bool(re.search(rb'(?m)^(?:openapi|swagger|[\"\'](?:openapi|swagger)[\"\'])\s*:\s*[\"\']?(?:2\.0|3\.\d+(?:\.\d+)?(?:[-+][\w.-]+)?)[\"\']?\s*(?:#.*)?$', raw))


def refs(raw):
    return [x.decode('utf-8', 'replace') for x in re.findall(rb'\$ref[\"\']?\s*:\s*[\"\']?([^\s\"\',}]+)', raw)]


def production(path):
    if excluded(path) or DOCS.search(path) or not CODE.search(path):
        return False
    # Spark lineage agents are instrumentation libraries, not server modules.
    if re.search(r'(?:^|/)(?:integration|instrumentation|operator|cli|console|serdes|serde|fosite)(?:/|$)|utils/maven-plugin/',path,re.I):
        return False
    if JVM.search(path):
        return '/src/main/' in '/' + path or bool(re.search(r'(?:^|/)(?:server|services?|rest-api|backend|webapp|model|api)(?:/|-)', path, re.I))
    return not re.search(r'(?:^|/)(?:cmd|tools?|hack|scripts?|testdata)(?:/|$)', path, re.I)


def annotated(raw):
    text=raw.decode('utf-8','replace')
    return bool(JVM_IMPORT.search(text) and ANNOTATION_USE.search(text) or re.search(r'@(?:io\.swagger|org\.springdoc|io\.javalin\.openapi)\.',text))


def classify(path, versions):
    if excluded(path):
        return []
    roles = []
    if DATA.search(path) and any(openapi(raw) for raw in versions):
        roles.append('openapi_root')
    if JVM.search(path) and not DOCS.search(path) and any(annotated(raw) for raw in versions):
        roles.append('contract_annotations')
    if production(path):
        if BEHAVIOUR.search(path):
            roles.append('production_behaviour')
    return roles


def objects(repo, names):
    """Batch-read literal Git objects; a missing historical path is normal."""
    names = list(dict.fromkeys(names))
    if not names:
        return {}
    # mine.git intentionally has no stdin argument; use its reviewed Git wrapper.
    reader = M['OLD']['Git'](M['REPOS'][repo])
    raw = reader.run('cat-file', '--batch', stdin=('\n'.join(names) + '\n').encode())
    result = {}; offset = 0
    for name in names:
        end = raw.index(b'\n', offset); header = raw[offset:end].split(); offset = end + 1
        if header[-1] == b'missing':
            result[name] = None
            continue
        size = int(header[-1]); result[name] = raw[offset:offset + size]
        assert raw[offset + size:offset + size + 1] == b'\n'
        offset += size + 1
    assert offset == len(raw)
    return result


def reachable(repo, revision, roots, targets):
    reached = set(); pending = sorted(roots); graph = {}; verified_roots = []
    while pending:
        names = [revision + ':' + p for p in pending]
        blobs = objects(repo, names); next_paths = set()
        for p, name in zip(pending, names):
            raw = blobs[name]
            if raw is None or excluded(p):
                continue
            if not reached and p in roots and not openapi(raw):
                continue
            # Every initial root is checked individually, independent of order.
            if p in roots and not openapi(raw):
                continue
            reached.add(p)
            if p in roots: verified_roots.append(p)
            children = []
            for ref in refs(raw):
                filename = ref.split('#', 1)[0]
                if not filename or re.match(r'^[\w+.-]+:', filename):
                    continue
                child = posixpath.normpath(posixpath.join(posixpath.dirname(p), filename))
                if child.startswith('../') or child.startswith('/') or excluded(child):
                    continue
                children.append(child)
                if child not in reached: next_paths.add(child)
            graph[p] = children
        if targets <= reached: break
        pending = sorted(next_paths - reached)
    return reached & targets, dict(roots=sorted(verified_roots), graph=graph)


def reviewed():
    old = set()
    for name in ('candidates.csv', 't43/candidates.csv'):
        for r in csv.DictReader((M['BASE'] / name).open()):
            if r['review_status'] in {'accepted', 'rejected', 'deferred'}:
                old.add((r['repo'], r['fix_commit']))
    sources = {r['candidate_id']: r for r in M['load_sources']()}
    for r in csv.DictReader((KEY / 'review_decisions.csv').open()):
        if r['review_status'] in {'accepted', 'rejected', 'deferred'}:
            s = sources[r['candidate_id']]; old.add((s['repo'], s['fix_commit']))
    return old


def main():
    for p in (HERE / 'pool2.json', HERE / 'freeze2.json', KEY / 'pool2_sources.json'):
        assert not p.exists(), 'Refusing to replace a frozen pool'
    prior = reviewed(); sources = []; inventory = []
    for metadata in json.loads((HERE / 'inventory.json').read_text()):
        repo = metadata['repo']; records = []; root_paths = set(); blob_ids = set()
        raw = git(repo, 'log', '--all', '--no-merges', '--no-renames', '--raw', '--no-abbrev', '--date=short', '--format=%x00%H%x09%P%x09%cs%x09%s').decode('utf-8', 'replace')
        for block in raw.split('\0')[1:]:
            ls = block.splitlines(); sha, parents, date, message = ls[0].split('\t', 3)
            if not parents or (repo, sha) in prior or not M['CUE'].search(message) or SKIP_MESSAGE.search(message):
                continue
            changes = []; needed = {}
            for line in ls[1:]:
                if not line.startswith(':') or '\t' not in line: continue
                header, path = line.split('\t', 1); fields = header.split()
                old_oid, new_oid, status = fields[2:5]
                changes.append([status, path])
                if excluded(path) or not (DATA.search(path) or JVM.search(path) and not DOCS.search(path) or production(path)): continue
                needed[path] = [oid for oid in (old_oid, new_oid) if set(oid) != {'0'}]
                blob_ids.update(needed[path])
            if needed:
                records.append(dict(repo=repo,fix_commit=sha,parent_commit=parents.split()[0],date=date,message_excerpt=safe(message).strip()[:160],cue_score=M['rank_candidate'](message,[]),stars=metadata['stars'],changes=changes,needed=needed))
        # Store classifications, never a repository's full source in memory.
        classification = {}; root_oids = set(); ids = sorted(blob_ids)
        for start in range(0, len(ids), 150):
            for oid, data in objects(repo, ids[start:start+150]).items():
                text = data.decode('utf-8', 'replace')
                is_root = openapi(data); annotation = annotated(data)
                classification[oid] = (is_root, annotation)
        for r in records:
            for path, oids in r['needed'].items():
                if DATA.search(path) and any(classification[o][0] for o in oids): root_paths.add(path)
        # Roots that never changed in a cue commit are discoverable at current tips.
        tips = git(repo, 'rev-list', '--all', '--max-count=1').decode().strip()
        if tips:
            paths = [p for p in git(repo, 'ls-tree', '-r', '--name-only', tips).decode().splitlines() if DATA.search(p) and not excluded(p)]
            for start in range(0, len(paths), 100):
                batch = paths[start:start+100]
                for name, data in objects(repo, [tips+':'+p for p in batch]).items():
                    if data and openapi(data): root_paths.add(name.split(':',1)[1])
        for r in records:
            roles = {}; fragments = set()
            for path, oids in r.pop('needed').items():
                kind = []
                if DATA.search(path):
                    if any(classification[o][0] for o in oids): kind.append('openapi_root')
                    else: fragments.add(path)
                else:
                    if JVM.search(path) and not DOCS.search(path) and any(classification[o][1] for o in oids): kind.append('contract_annotations')
                    if production(path) and BEHAVIOUR.search(path): kind.append('production_behaviour')
                if kind: roles[path] = kind
            ref_evidence = {}
            if fragments and root_paths:
                # Exact parent/child closure, rather than a same-directory proxy.
                for revision in (r['parent_commit'], r['fix_commit']):
                    reached, evidence = reachable(repo, revision, root_paths, fragments)
                    if reached:
                        ref_evidence[revision] = evidence
                        for p in reached: roles.setdefault(p, []).append('openapi_ref')
            if not roles: continue
            r.update(surface_paths=sorted(roles),path_roles=roles,ref_evidence=ref_evidence,score=r.pop('cue_score')+int(any(M['OP'].search(p) for p in roles)))
            sources.append(r)
        inventory.append(dict(repo=repo,pool2=sum(r['repo']==repo for r in sources),prior_review_excluded=sum(r==repo for r,_ in prior),known_root_paths=len(root_paths)))
        print(json.dumps(inventory[-1]),flush=True)
    sources.sort(key=lambda r:(r['repo'],-r['score'],r['fix_commit']))
    ranks=Counter()
    for i,r in enumerate(sources,1):
        ranks[r['repo']]+=1;r.update(candidate_id=f'P2C{i:05}',rank=ranks[r['repo']])
    pool=[{k:r[k] for k in ('candidate_id','repo','rank','score','surface_paths','path_roles')} for r in sources]
    M['dump'](KEY/'pool2_sources.json',sources);M['dump'](HERE/'pool2.json',pool);M['dump'](HERE/'pool2_inventory.json',inventory)
    M['dump'](HERE/'freeze2.json',dict(pool_sha256=hashlib.sha256((HERE/'pool2.json').read_bytes()).hexdigest(),source_sha256=hashlib.sha256((KEY/'pool2_sources.json').read_bytes()).hexdigest(),code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),prior_review_exclusions=len(prior),rule='Correction cue AND content-verified OpenAPI/ref/JVM annotations OR production JVM/Go behaviour path; score unchanged; repo, descending score, ascending SHA',before_review=True))


if __name__=='__main__':main()
