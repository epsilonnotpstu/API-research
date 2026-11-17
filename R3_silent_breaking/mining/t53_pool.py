#!/usr/bin/python3
"""Hypothesis-blind pool4 discovery. Git bytes are data and are never executed.

Only numstat, metadata, whitespace-diff exit status, and document detection are
used. No patch or message is requested here. All first-parent dates are filtered
in Python, so non-monotonic dates cannot truncate the history walk.
"""
from collections import Counter
from datetime import datetime, timezone
import csv
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
import sys
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
UPSTREAM = Path('/run/media/afridi/Shared Data/api_research_upstream')
BOT = BASE / 'collab/logs/T53_scratch/bot_scan.py'
START = 1672531200
EMPTY = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
EXCLUDE = re.compile(r'(?:^|/)(?:\.github|\.circleci|ci|helm|charts?|k8s|kubernetes|docker|compose|deploy(?:ment)?s?|terraform|tests?|testing|testfixtures|fixtures?|generated|target|vendor|node_modules|examples?|samples?|benchmarks?|sdks?|clients?|client-go|httpclient(?:-next)?|[^/]*-sdk|[^/]*-examples)(?:/|$)|src/(?:test|it)/|_test\.go$|\.test\.|\.spec\.', re.I)
DOCS = re.compile(r'(?:^|/)(?:docs?|documentation|website|site)(?:/|$)', re.I)
BEHAVIOUR = re.compile(r'controller|resource|handler|endpoint|route|validator|serializ|exception|dto|model|mapper|(?:^|/)(?:api|rest|web|http)(?:/|$)', re.I)
EXTRA_EXCLUDE = re.compile(r'(?:^|/)(?:migrations?|dbmigration|build|buildSrc|dist|out|\.gradle|\.idea|\.git|integration|instrumentation|operator|cli|console|serdes|serde|fosite)(?:/|$)|utils/maven-plugin/', re.I)
LANG = {'.java': 'Java', '.kt': 'Kotlin', '.go': 'Go'}

def jb(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def exclusive(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw)

def safe_path(path):
    return bool(path and not path.startswith('/') and '\\' not in path and
                all(x not in {'', '.', '..'} for x in path.split('/')) and
                not any(x in path for x in ['\0', '\r', '\n', '\t']))

def behaviour(path):
    suffix = PurePosixPath(path).suffix.lower()
    if not safe_path(path) or suffix not in LANG or EXCLUDE.search(path) or DOCS.search(path) or EXTRA_EXCLUDE.search(path):
        return False
    if suffix in {'.java', '.kt'}:
        if not ('/src/main/' in '/' + path or re.search(r'(?:^|/)(?:server|services?|rest-api|backend|webapp|model|api)(?:/|-)', path, re.I)):
            return False
    elif re.search(r'(?:^|/)(?:cmd|tools?|hack|scripts?|testdata)(?:/|$)', path, re.I):
        return False
    return bool(BEHAVIOUR.search(path))

def git_env():
    env = dict(os.environ)
    for name in list(env):
        if name.startswith('GIT_'):
            del env[name]
    env.update(GIT_OPTIONAL_LOCKS='0', GIT_PAGER='cat', GIT_TERMINAL_PROMPT='0',
               GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null',
               GIT_NO_REPLACE_OBJECTS='1', GIT_NO_LAZY_FETCH='1')
    return env

class Git:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.prefix = ['git', '--no-pager', '--no-optional-locks', '-c', 'core.hooksPath=/dev/null',
                       '-c', 'core.fsmonitor=false', '-c', 'diff.external=', '--git-dir=' + str(directory)]
        self.env = git_env()
        self.checker = None
        self.reader = None
        self.info = {}

    def run(self, *args, stdin=None):
        result = subprocess.run(self.prefix + list(args), input=stdin, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, env=self.env)
        if result.returncode:
            raise RuntimeError('Read-only Git failed: ' + args[0] + '; diagnostics suppressed')
        return result.stdout

    def close(self):
        for process in (self.checker, self.reader):
            if process:
                process.stdin.close()
                process.stdout.close()
                process.wait()

    def batch(self, names, content=False):
        attr = 'reader' if content else 'checker'
        process = getattr(self, attr)
        if process is None:
            process = subprocess.Popen(self.prefix + ['cat-file', '--batch' if content else '--batch-check'],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.DEVNULL, env=self.env)
            setattr(self, attr, process)
        result = {}
        for name in names:
            if '\n' in name or '\r' in name or '\0' in name:
                raise RuntimeError('Unsafe object path; contents suppressed')
            process.stdin.write(name.encode() + b'\n')
            process.stdin.flush()
            fields = process.stdout.readline().rstrip(b'\n').split()
            if fields[-1:] in ([b'missing'], [b'submodule']):  # D1 fix: a path inside a submodule is not a blob of this repository
                result[name] = None
                continue
            if len(fields) != 3:
                raise RuntimeError('Invalid object response (' + str(len(fields)) + ' fields); contents suppressed')
            oid, kind, size = fields[0].decode(), fields[1].decode(), int(fields[2])
            data = process.stdout.read(size) if content else None
            if content and process.stdout.read(1) != b'\n':
                raise RuntimeError('Truncated object response')
            result[name] = (oid, kind, data)
        return result

    def tree(self, revision):
        if revision is None:
            return {}
        result = {}
        for entry in self.run('ls-tree', '-r', '-z', revision).split(b'\0'):
            if not entry:
                continue
            metadata, path = entry.split(b'\t', 1)
            mode, kind, oid = metadata.decode().split()
            path = path.decode('utf-8', 'strict')
            if safe_path(path):
                result[path] = (oid, kind, mode)
        return result

    def classify(self, ids):
        pending = sorted(set(ids) - self.info.keys())
        # Bound memory: never retain a complete repository's source blob bytes.
        for start in range(0, len(pending), 24):
            for oid, record in self.batch(pending[start:start + 24], content=True).items():
                if record is None or record[1] != 'blob':
                    self.info[oid] = (False, ())
                    continue
                raw = record[2]
                # Only top-level keys count; source annotations are not documents.
                root = is_openapi(raw)
                self.info[oid] = (root, tuple(refs(raw)))

    def blob(self, revision, path):
        if revision is None:
            return None
        value = self.batch([revision + ':' + path], content=True)[revision + ':' + path]
        if value is None:
            return None
        if value[1] != 'blob':
            raise RuntimeError('Non-blob source; contents suppressed')
        return value[2]

    def nonwhite(self, parent, child, paths):
        args = ['diff', '--no-ext-diff', '--no-textconv', '-w', '--ignore-blank-lines',
                '--quiet', parent or EMPTY, child, '--'] + sorted(paths)
        result = subprocess.run(self.prefix + args, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, env=self.env)
        if result.returncode not in {0, 1}:
            raise RuntimeError('Whitespace check failed; diagnostics suppressed')
        return result.returncode == 1

def is_openapi(raw):
    if b'\0' in raw or not (b'openapi' in raw or b'swagger' in raw):
        return False
    try:
        obj = json.loads(raw)
        return isinstance(obj, dict) and any(k in obj for k in ('openapi', 'swagger'))
    except (ValueError, UnicodeError, RecursionError):
        return bool(re.search(rb'(?m)^(?:openapi|swagger|[\"\x27](?:openapi|swagger)[\"\x27])\s*:', raw))

def refs(raw):
    if b'\0' in raw or b'$ref' not in raw:
        return []
    return [m.decode('utf-8', 'replace') for m in re.findall(rb'\$ref[\"\x27]?\s*:\s*[\"\x27]?([^\s\"\x27,}\]]+)', raw)]

def roots_and_closure(tree, info, roots=None):
    if roots is None:
        roots = {p for p, (oid, kind, *_) in tree.items() if kind == 'blob' and info[oid][0]}
    pending = list(roots)
    reached = set()
    while pending:
        path = pending.pop()
        if path in reached or path not in tree or tree[path][1] != 'blob':
            continue
        reached.add(path)
        for ref in info[tree[path][0]][1]:
            filename = unquote(ref.split('#', 1)[0])
            if not filename or re.match(r'^[\w+.-]+:', filename):
                continue
            target = posixpath.normpath(posixpath.join(posixpath.dirname(path), filename))
            if safe_path(target):
                pending.append(target)
    return roots, reached

def history(git, head):
    raw = git.run('log', '--first-parent', '--reverse', '--diff-merges=first-parent',
                  '--format=%x00T53%x09%H%x09%P%x09%cI%x09%ct%x00', '--numstat', '-z',
                  '--find-renames=50%', '--no-ext-diff', '--no-textconv', head)
    result = []
    for block in raw.split(b'\0T53\t')[1:]:
        metadata, rest = block.split(b'\0', 1)
        oid, parents, date, stamp = metadata.decode().split('\t')
        entries = rest.split(b'\0')
        changes = []
        i = 0
        while i < len(entries):
            record = entries[i].lstrip(b'\n')
            i += 1
            if not record:
                continue
            added, deleted, path = record.split(b'\t', 2)
            if path:
                old = new = path.decode('utf-8', 'strict')
            else:
                old, new = (x.decode('utf-8', 'strict') for x in entries[i:i + 2])
                i += 2
            changes.append(dict(old=old, new=new,
                                added=int(added) if added != b'-' else None,
                                deleted=int(deleted) if deleted != b'-' else None))
        result.append(dict(sha=oid, parents=parents.split(), date=date, timestamp=int(stamp), changes=changes))
    return result

def discover(directory, head, bot_shas=None):
    git = Git(directory)
    try:
        commits = history(git, head)
        relevant = [i for i, c in enumerate(commits) if c['timestamp'] >= START]
        counts = Counter(nonmerge_window=0, bot_exclusions=0, contract_exclusions=0,
                         size_exclusions=0, empty_behaviour_exclusions=0, pool=0)
        if not relevant:
            return [], dict(counts), dict(roots={}, document_updates=[])
        if bot_shas is None:
            process = subprocess.run(['/usr/bin/python3', '-I', '-B', str(BOT), str(directory), head],
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            if process.returncode:
                raise RuntimeError('Scratch bot process failed; diagnostics suppressed')
            bot_shas = set(json.loads(process.stdout))
        initial = commits[min(relevant)]
        tree = git.tree(initial['parents'][0] if initial['parents'] else None)
        git.classify(v[0] for v in tree.values() if v[1] == 'blob')
        parent_roots, parent_docs = roots_and_closure(tree, git.info)
        candidates = []
        doc_history = []
        candidate_roots = {}
        for index in range(min(relevant), len(commits)):
            c = commits[index]
            parent = c['parents'][0] if c['parents'] else None
            changed = {p for x in c['changes'] for p in (x['old'], x['new'])}
            prior_roots = sorted(parent_roots)
            names = [c['sha'] + ':' + p for p in sorted(changed) if safe_path(p)]
            updated = git.batch(names)
            new_ids = [v[0] for v in updated.values() if v is not None and v[1] == 'blob']
            git.classify(new_ids)
            next_roots = set(parent_roots)
            for name, value in updated.items():
                path = name.split(':', 1)[1]
                next_roots.discard(path)
                if value is None:
                    tree.pop(path, None)
                else:
                    tree[path] = (value[0], value[1], '100644')
                    if value[1] == 'blob' and git.info[value[0]][0]:
                        next_roots.add(path)
            child_roots, child_docs = roots_and_closure(tree, git.info, next_roots)
            contract_changed = bool(changed & (parent_docs | child_roots))
            if contract_changed:
                doc_history.append(dict(sha=c['sha'], date=c['date'], timestamp=c['timestamp'], position=index))
            parent_roots, parent_docs = child_roots, child_docs
            if len(c['parents']) > 1 or c['timestamp'] < START:
                continue
            counts['nonmerge_window'] += 1
            if c['sha'] in bot_shas:
                counts['bot_exclusions'] += 1
                continue
            if contract_changed:
                counts['contract_exclusions'] += 1
                continue
            kept = set()
            lines = 0
            for change in c['changes']:
                paths = {p for p in (change['old'], change['new']) if behaviour(p)}
                if not paths or change['added'] is None or change['deleted'] is None:
                    continue
                amount = change['added'] + change['deleted']
                if amount == 0 or not git.nonwhite(parent, c['sha'], paths):
                    continue
                kept.update(paths)
                lines += amount
            if not kept:
                counts['empty_behaviour_exclusions'] += 1
                continue
            if lines > 400 or len(kept) > 8:
                counts['size_exclusions'] += 1
                continue
            candidates.append(dict(repo=Path(directory).name.removesuffix('.git'), sha=c['sha'],
                                   parent=parent, date=c['date'], files=sorted(kept, key=lambda p:p.encode()),
                                   changed_lines=lines, language=';'.join(sorted({LANG[PurePosixPath(p).suffix.lower()] for p in kept}))))
            candidate_roots[parent or 'ROOT'] = prior_roots
        counts['pool'] = len(candidates)
        return sorted(candidates, key=lambda c:c['sha']), dict(counts), dict(roots=candidate_roots, document_updates=doc_history,
            positions={c['sha']:i for i,c in enumerate(commits)})
    finally:
        git.close()

def heads(repositories):
    rows = []
    for path in sorted(repositories, key=lambda p:p.name.encode()):
        git = Git(path)
        try:
            rows.append(dict(repo=path.name.removesuffix('.git'), head=git.run('rev-parse', '--verify', 'HEAD').decode().strip()))
        finally:
            git.close()
    return rows

def heads_bytes(rows):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, ['repo', 'head'], delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()

def code_hashes():
    return {p.name:sha(p.read_bytes()) for p in [Path(__file__), BOT]}

def main():
    destinations = ['pool4.json', 'pool4_inventory.json', 'freeze4.json', 'key/document_history.json']
    if any((HERE / p).exists() for p in destinations):
        raise RuntimeError('Refusing to overwrite frozen discovery outputs')
    repositories = sorted(UPSTREAM.glob('*.git'), key=lambda p:p.name.encode())
    if len(repositories) != 54:
        raise RuntimeError('Expected exactly 54 bare clones')
    pinned = heads(repositories)
    if (HERE / 'heads.tsv').exists():
        assert (HERE / 'heads.tsv').read_bytes() == heads_bytes(pinned), 'Pinned heads changed'
    else:
        exclusive(HERE / 'heads.tsv', heads_bytes(pinned))
    pool = []
    inventory = []
    documents = {}
    for row in pinned:
        checkpoint = BASE / 'collab/logs/T53_scratch' / (row['repo'] + '_checkpoint.json')
        signature = dict(head=row['head'], code=code_hashes())
        saved = json.loads(checkpoint.read_text()) if checkpoint.exists() else None
        if saved and saved['signature'] == signature:
            candidates, counts, docs = saved['candidates'], saved['counts'], saved['documents']
        else:
            candidates, counts, docs = discover(UPSTREAM / (row['repo'] + '.git'), row['head'])
            checkpoint.write_bytes(jb(dict(signature=signature,candidates=candidates,counts=counts,documents=docs)))
        pool.extend(candidates)
        inventory.append(dict(repo=row['repo'], **counts))
        documents[row['repo']] = docs
        print(json.dumps(dict(repo=row['repo'], **counts)), flush=True)
    if heads(repositories) != pinned:
        raise RuntimeError('Heads changed during discovery')
    exclusive(HERE / 'pool4.json', jb(pool))
    exclusive(HERE / 'pool4_inventory.json', jb(inventory))
    exclusive(HERE / 'key/document_history.json', jb(documents))
    code = code_hashes()
    exclusive(HERE / 'freeze4.json', jb(dict(pool_sha256=sha(jb(pool)), code_sha256=sha(jb(code)),
        code_files=code, heads_sha256=sha(heads_bytes(pinned)), before_sampling=True,
        document_history_sha256=sha(jb(documents)), inventory_sha256=sha(jb(inventory)),
        rules=dict(history='HEAD first-parent; exclude merge candidates; UTC committer cutoff inclusive',
                   cutoff='2023-01-01T00:00:00Z', max_changed_lines=400, max_files=8,
                   document='top-level openapi/swagger at parent or child; local reference closure at parent',
                   formatting='per-file -w --ignore-blank-lines quiet exit status; pure rename zero numstat',
                   renamed_paths='both production paths count toward the eight-path limit'))))
    print(json.dumps(dict(frozen=True, pool=len(pool), repositories=len(pinned))), flush=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        sys.exit('Pool build failed: ' + type(error).__name__ + '; diagnostics suppressed')
