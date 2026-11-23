#!/usr/bin/python3
"""Pre-registered repository-cap and seeded sampling, with immutable hashes."""
from collections import defaultdict
from pathlib import Path
import random
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from r4_common import (ROOT, PipelineError, cli, read_json, refuse_existing,
                       sha256_file, verify_hashes, write_json)


def select(pool):
    by_id = {item['ghsa_id']: item for item in pool}
    if len(by_id) != len(pool):
        raise PipelineError('DUPLICATE_POOL_ID')
    if len(pool) <= 160:
        return [by_id[i] for i in sorted(by_id)]
    repositories = defaultdict(list)
    for item in pool:
        repositories[item['repo']].append(item['ghsa_id'])
    ids = []
    for repo, members in sorted(repositories.items()):
        ids.extend(random.Random('r4:' + repo).sample(sorted(members), min(4, len(members))))
    if len(ids) > 160:
        ids = random.Random('r4-sample-20261123').sample(sorted(ids), 160)
    return [by_id[i] for i in sorted(ids)]


def main(root=ROOT):
    mining = Path(root) / 'mining'
    refuse_existing(mining / 'sample.json', mining / 'sample_freeze.json',
                    Path(root) / 'packages/r4_blind')
    freeze = read_json(mining / 'pool_freeze.json')
    verify_hashes(mining, freeze['sha256'])
    sample = select(read_json(mining / 'pool.json'))
    write_json(mining / 'sample.json', sample)
    write_json(mining / 'sample_freeze.json', {
        'sha256': {'sample.json': sha256_file(mining / 'sample.json')},
        'pool_freeze_sha256': sha256_file(mining / 'pool_freeze.json')})
    print('sample=' + str(len(sample)))


if __name__ == '__main__':
    cli(main)
