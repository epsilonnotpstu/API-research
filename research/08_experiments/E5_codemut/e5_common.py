"""Shared stdlib evidence I/O. No Docker, shell, SUT or build execution."""
import csv
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
HARNESS = EXP / 'E1_pilot/harness_v2'
TOOLS = EXP / 'tools'
EMB = EXP / '_external/emb'
SUTS = {'scout-api', 'swagger-petstore', 'market', 'cwa-verification'}
JARS = {'scout-api': 'api/target/scout-api-sut.jar', 'swagger-petstore': 'target/swagger-petstore-sut.jar',
        'market': 'market-rest/target/market-sut.jar', 'cwa-verification': 'target/cwa-verification-sut.jar'}
LEDGER_FIELDS = ['seed', 'role', 'run_dir', 'harness_exit', 'status']


def layout(kind='pair'):
    require(kind in ('pair', 'noise'), 'Unknown E5 comparison kind')
    prefix = 'noise-' if kind == 'noise' else ''
    return prefix, ('control_repeat' if kind == 'noise' else 'mutant')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), f'Missing/nonregular evidence: {path}')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load(path):
    path = Path(path)
    require(not path.is_symlink(), f'Symlink evidence: {path}')
    with path.open(encoding='utf-8') as stream:
        return json.load(stream)


def safe_relative(name):
    require(isinstance(name, str) and name and '\\' not in name, 'Invalid relative evidence path')
    name = name.removeprefix('./')
    p = PurePosixPath(name)
    require(not p.is_absolute() and all(x not in ('', '.', '..') for x in name.split('/')), 'Unsafe evidence path')
    return name


def snapshot(directory, hashes):
    hash_inventory(hashes)
    for name, digest in hashes.items():
        require(sha(Path(directory) / safe_relative(name)) == digest, f'Changed evidence: {directory}/{name}')
    return hashes


def hash_inventory(hashes, required=()):
    """Validate a recorded identity without requiring historical bytes locally."""
    require(isinstance(hashes, dict) and hashes, 'Missing/empty hash inventory')
    require(set(required) <= set(hashes), 'Missing core snapshot entries')
    for name, digest in hashes.items():
        require(safe_relative(name) == name, 'Noncanonical snapshot path')
        require(isinstance(digest, str) and re.fullmatch('[a-f0-9]{64}', digest), f'Invalid digest for {name}')
    return hashes


def runtime_snapshots(meta):
    return {'tools': hash_inventory(meta['tool_sha256'], ('conformance.py','attribute.py','specmut.py')),
            'harness': hash_inventory(meta['harness_sha256'], ('run_pilot.sh','run_metadata.py'))}


def tool_inventory():
    return hash_inventory({p.name:sha(p) for p in sorted(TOOLS.glob('*.py'))},
                          ('conformance.py','attribute.py','specmut.py'))


def harness_inventory():
    return hash_inventory({p.relative_to(HARNESS).as_posix():sha(p) for p in sorted(HARNESS.rglob('*'))
                           if p.is_file() and not any(x.startswith('.') for x in p.relative_to(HARNESS).parts)})


def inspection(path):
    value = load(path)
    require(isinstance(value, list) and len(value) == 1 and isinstance(value[0], dict), f'Expected single inspect record: {path}')
    return value[0]


def image_id(value):
    return isinstance(value, str) and re.fullmatch(r'sha256:[a-f0-9]{64}', value) is not None


def atomic_json(path, value, staging_dir=None):
    """Replace a report atomically; a fresh FAIL replaces any stale PASS."""
    path = Path(path)
    require(not path.is_symlink(), 'Refusing symlink output')
    tmp = (Path(staging_dir) if staging_dir is not None else path.parent) / (path.name + '.tmp')
    with tmp.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    tmp.replace(path)


def ledger(path, kind='pair'):
    _, treatment = layout(kind)
    with Path(path).open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        require(reader.fieldnames == LEDGER_FIELDS, 'Unexpected runs.tsv header')
        rows = list(reader)
    seen = set()
    for row in rows:
        require(None not in row and all(v is not None for v in row.values()), 'Malformed runs.tsv row')
        require(re.fullmatch(r'0|[1-9][0-9]*', row['seed']), 'Invalid ledger seed')
        require(row['role'] in ('control', treatment), 'Invalid ledger role')
        key = (int(row['seed']), row['role'])
        require(key not in seen, 'Duplicate ledger seed/role'); seen.add(key)
        require(Path(row['run_dir']).is_absolute(), 'Ledger paths must be absolute')
    return rows


def paired_rows(path, allow_incomplete=False, kind='pair'):
    _, treatment = layout(kind)
    rows = ledger(path, kind); groups = {}
    require(len({r['run_dir'] for r in rows}) == len(rows), 'Reused run directory')
    for row in rows:
        groups.setdefault(int(row['seed']), []).append(row)
    pairs = {}
    for seed, group in groups.items():
        ready = {r['role'] for r in group} == {'control',treatment} and all(r['harness_exit'] == '0' and r['status'] == 'COMPLETE' for r in group)
        if not ready:
            require(allow_incomplete, 'Failed/pending/incomplete run pair')
            continue
        pairs[seed] = {r['role']:Path(r['run_dir']).resolve() for r in group}
    require(pairs, 'No complete comparison in ledger')
    return pairs


def excluded_operations(report):
    """Return validated operation identities; never silently accept malformed exclusions."""
    entries = report.get('excluded_ops', [])
    require(isinstance(entries,list), 'Invalid excluded operations')
    result = set()
    for op in entries:
        require(op['method'] in ('GET','POST','PUT','PATCH','DELETE','HEAD','OPTIONS','TRACE') and
                isinstance(op['path'],str) and op['path'].startswith('/') and op.get('reason'), 'Invalid excluded operation')
        result.add((op['method'],op['path']))
    require(len(result)==len(entries), 'Duplicate excluded operation')
    require(not entries or report['status']=='PASS_WITH_EXCLUSION', 'Exclusions require PASS_WITH_EXCLUSION')
    return result
