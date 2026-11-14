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
    require(isinstance(hashes, dict) and hashes, f'Empty hash inventory: {directory}')
    for name, digest in hashes.items():
        require(re.fullmatch('[a-f0-9]{64}', str(digest)), f'Invalid digest for {name}')
        require(sha(Path(directory) / safe_relative(name)) == digest, f'Changed evidence: {directory}/{name}')
    return hashes


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


def ledger(path):
    with Path(path).open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        require(reader.fieldnames == LEDGER_FIELDS, 'Unexpected runs.tsv header')
        rows = list(reader)
    seen = set()
    for row in rows:
        require(None not in row and all(v is not None for v in row.values()), 'Malformed runs.tsv row')
        require(re.fullmatch(r'0|[1-9][0-9]*', row['seed']), 'Invalid ledger seed')
        require(row['role'] in ('control', 'mutant'), 'Invalid ledger role')
        key = (int(row['seed']), row['role'])
        require(key not in seen, 'Duplicate ledger seed/role'); seen.add(key)
        require(Path(row['run_dir']).is_absolute(), 'Ledger paths must be absolute')
    return rows


def paired_rows(path, allow_incomplete=False):
    rows = ledger(path); groups = {}
    require(len({r['run_dir'] for r in rows}) == len(rows), 'Reused run directory')
    for row in rows:
        groups.setdefault(int(row['seed']), []).append(row)
    pairs = {}
    for seed, group in groups.items():
        ready = {r['role'] for r in group} == {'control','mutant'} and all(r['harness_exit'] == '0' and r['status'] == 'COMPLETE' for r in group)
        if not ready:
            require(allow_incomplete, 'Failed/pending/incomplete run pair')
            continue
        pairs[seed] = {r['role']:Path(r['run_dir']).resolve() for r in group}
    require(pairs, 'No complete control/mutant pair in ledger')
    return pairs
