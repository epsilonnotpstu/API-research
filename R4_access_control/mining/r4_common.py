#!/usr/bin/python3
"""R4's independent, standard-library-only mining primitives.

Importing this module never reads mining data. Diagnostics deliberately omit
subprocess output, which may contain advisory text, credentials or identities.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parent.parent
CWES = (284, 285, 639, 862, 863, 915, 269, 266, 425, 566, 708, 306)
ECOSYSTEMS = ('maven', 'go')
EXCLUDED = frozenset(('test tests testdata example examples sample samples '
                      'fixture fixtures vendor node_modules third_party e2e mock mocks').split())
QUERY = {'type': 'reviewed', 'ecosystems': list(ECOSYSTEMS),
         'cwes': ['CWE-' + str(n) for n in CWES], 'per_page': 100}


class PipelineError(RuntimeError):
    """An error safe to print: messages contain kinds, never input contents."""


class CommandError(PipelineError):
    def __init__(self, returncode, stderr=''):
        super().__init__('SUBPROCESS_FAILED')
        self.returncode = returncode
        self.not_found = bool(re.search(r'HTTP (?:404|422)\b', stderr))


def run(cmd):
    """Return stdout; retry network operations up to three attempts (1, 2s)."""
    cmd = [str(s) for s in cmd]
    network = (Path(cmd[0]).name == 'gh' or
               Path(cmd[0]).name == 'git' and
               any(s in {'fetch', 'clone', 'ls-remote', 'push', 'pull',
                         'diff', 'show', 'cat-file', 'ls-tree'} for s in cmd[1:]))
    attempts = 3 if network else 1
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GIT_CONFIG_NOSYSTEM='1',
               GIT_CONFIG_GLOBAL=os.devnull, LC_ALL='C', GH_PROMPT_DISABLED='1')
    for attempt in range(attempts):
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    encoding='utf-8', errors='replace', env=env,
                                    timeout=300, check=False)
        except (OSError, subprocess.TimeoutExpired):
            error = CommandError(-1)
        else:
            if result.returncode == 0:
                return result.stdout
            error = CommandError(result.returncode, result.stderr)
        if attempt + 1 < attempts:
            time.sleep(2 ** attempt)
    raise error


def parts(path):
    return PurePosixPath(path).parts


def is_contract_path(path):
    p = PurePosixPath(path)
    return (p.suffix.lower() in {'.yaml', '.yml', '.json'} and
            any(s in p.name.lower() for s in ('openapi', 'swagger')) and
            not any(s.lower() in EXCLUDED for s in p.parts))


def is_test_path(path):
    p = PurePosixPath(path)
    return (any(s.lower() in {'test', 'tests'} for s in p.parts[:-1]) or
            p.name.endswith(('_test.go', 'Test.java', 'Tests.java', 'Test.kt', 'IT.java')))


def is_source_path(path):
    p = PurePosixPath(path)
    return (p.suffix in {'.java', '.kt', '.go'} and not is_test_path(path) and
            not any(s.lower() in EXCLUDED for s in p.parts))


def annotation_patterns():
    path = ROOT.parent / 'R3_silent_breaking/mining/annotation_patterns.json'
    data = read_json(path)
    names = set(data['jvm_names']) | {'SecurityRequirement', 'SecurityRequirements', 'SecurityScheme'}
    jvm = re.compile(r'@(?:[A-Za-z_$][\w$]*\.)*(?:' +
                     '|'.join(re.escape(n) for n in sorted(names)) + r')\b')
    flags = 0
    for name in data.get('go_flags', []):
        flags |= getattr(re, name)
    return jvm, re.compile(data['go_pattern'], flags)


def annotation_lines(diff_text):
    jvm, go = annotation_patterns()
    count = 0
    in_hunk = False
    for line in diff_text.splitlines():
        if line.startswith('diff --git '):
            in_hunk = False
        elif line.startswith('@@ '):
            in_hunk = True
        elif in_hunk and line[:1] in {'+', '-'}:
            count += bool(jvm.search(line[1:]) or go.search(line[1:]))
    return count


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_json(path):
    with Path(path).open(encoding='utf-8') as stream:
        return json.load(stream)


def write_json(path, data):
    """Exclusive creation, sorted keys, UTF-8 and LF, including final LF."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(data, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')


def refuse_existing(*paths):
    if any(Path(p).exists() for p in paths):
        raise PipelineError('OUTPUT_EXISTS')


def guard_upstream(root, *outputs):
    mining = Path(root) / 'mining'
    refuse_existing(mining / 'pool_freeze.json', mining / 'sample_freeze.json',
                    Path(root) / 'packages/r4_blind', *(mining / p for p in outputs))


def verify_hashes(base, hashes):
    for name, expected in hashes.items():
        if sha256_file(Path(base) / name) != expected:
            raise PipelineError('FREEZE_HASH_MISMATCH')


def git(repo, *args):
    return run(['git', '--literal-pathspecs', '--git-dir', str(repo), *args])


def repo_cache(root, repo):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
        raise PipelineError('INVALID_REPOSITORY')
    owner, name = repo.split('/')
    if owner in {'.', '..'} or name in {'.', '..'}:
        raise PipelineError('INVALID_REPOSITORY')
    return Path(root) / 'mining/cache/git' / (owner + '__' + name + '.git')


def diff(repo, parent, fix, paths=None):
    command = ['diff', '--no-ext-diff', '--no-textconv', '--no-color', parent, fix]
    if paths is not None:
        command.extend(['--', *paths])
    return git(repo, *command)


def cli(main):
    try:
        main()
    except (PipelineError, OSError, ValueError, KeyError, TypeError):
        # Never echo exception text: JSON, filenames and subprocess data are private.
        print('ERROR: pipeline stopped; inspect input validity or existing outputs.')
        raise SystemExit(1)
