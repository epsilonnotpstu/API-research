#!/usr/bin/python3
"""Freeze the specified per-repository sample before any package is built."""
import csv
import hashlib
import json
from pathlib import Path
import random
import runpy

HERE = Path(__file__).resolve().parent
P = runpy.run_path(str(HERE / 't53_pool.py'))

def select(pool, repositories):
    lookup = {(r['repo'], r['sha']):r for r in pool}
    result = []
    for repo in sorted(repositories, key=lambda p:p.encode()):
        shas = sorted(r['sha'] for r in pool if r['repo'] == repo)
        for sha in random.Random('20261117:' + repo).sample(shas, min(3, len(shas))):
            result.append(lookup[repo, sha])
    return result

def guard():
    freeze = json.loads((HERE / 'freeze4.json').read_text())
    assert freeze['before_sampling'] is True
    assert P['sha']((HERE / 'pool4.json').read_bytes()) == freeze['pool_sha256']
    assert P['sha']((HERE / 'heads.tsv').read_bytes()) == freeze['heads_sha256']
    assert P['code_hashes']() == freeze['code_files']
    return freeze

def main():
    freeze = guard()
    assert not (HERE / 'sample4.json').exists() and not (HERE / 'freeze4_sample.json').exists()
    assert not (HERE.parent / 'packages/r3_blind').exists()
    pool = json.loads((HERE / 'pool4.json').read_text())
    with (HERE / 'heads.tsv').open() as stream:
        repositories = [r['repo'] for r in csv.DictReader(stream, delimiter='\t')]
    sample = select(pool, repositories)
    P['exclusive'](HERE / 'sample4.json', P['jb'](sample))
    P['exclusive'](HERE / 'freeze4_sample.json', P['jb'](dict(sample_sha256=P['sha'](P['jb'](sample)),
        pool_sha256=freeze['pool_sha256'], sampler_sha256=P['sha'](Path(__file__).read_bytes()),
        before_packaging=True, rule='random.Random("20261117:" + repo).sample(sorted(shas), min(3, len(shas)))',
        repositories=sorted(repositories, key=lambda p:p.encode()), sample_size=len(sample))))
    print(json.dumps(dict(sample_frozen=True, sample_size=len(sample))))

if __name__ == '__main__':
    main()
