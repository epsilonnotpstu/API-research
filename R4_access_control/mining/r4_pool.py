#!/usr/bin/python3
"""Mechanical eligibility, commit deduplication and pool hash freeze."""
from collections import Counter, defaultdict
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from r4_common import (ROOT, QUERY, ECOSYSTEMS, CommandError, PipelineError,
                       annotation_lines, cli, diff, git, guard_upstream,
                       is_contract_path, is_source_path, is_test_path, read_json,
                       repo_cache, sha256_file, write_json)


def numstat(text):
    """Parse git's NUL format, including spaces, tabs and rename pairs."""
    fields = iter(text.split('\0'))
    result = []
    for field in fields:
        if not field:
            continue
        added, deleted, path = field.split('\t', 2)
        old, new = (path, path) if path else (next(fields), next(fields))
        result.append({'old_path': old, 'new_path': new, 'added': added, 'deleted': deleted})
    return result


def eligible(resolution, root=ROOT):
    if 'reason' in resolution:
        return dict(resolution)
    cache = repo_cache(root, resolution['repo'])
    parent, fix = resolution['parent_sha'], resolution['fix_sha']
    try:
        tree = git(cache, 'ls-tree', '-r', '--name-only', '-z', parent).split('\0')
        contracts = sorted(p for p in tree if p and is_contract_path(p))
        if not contracts:
            return {'reason': 'NO_CONTRACT_AT_PARENT'}
        changes = numstat(git(cache, 'diff', '--no-ext-diff', '--no-textconv',
                              '--numstat', '-z', parent, fix))
        source = [c for c in changes if is_source_path(c['old_path']) or
                  is_source_path(c['new_path'])]
        if not source:
            return {'reason': 'NO_SOURCE_CHANGE'}
        if any(c['added'] == '-' or c['deleted'] == '-' for c in source):
            # The plan defines a line threshold, but binary numstat supplies no
            # line count. Stop before freezing rather than invent an exclusion.
            raise PipelineError('BINARY_SOURCE_NUMSTAT')
        for c in source:
            c['added'], c['deleted'] = int(c['added']), int(c['deleted'])
        lines = sum(c['added'] + c['deleted'] for c in source)
        if lines > 2000:
            return {'reason': 'TOO_LARGE'}
        test_paths = git(cache, 'diff', '--no-ext-diff', '--no-textconv', '--name-only',
                         '--diff-filter=AMRT', '-z', parent, fix).split('\0')
        touches_contract = any(is_contract_path(c[p]) for c in changes
                               for p in ('old_path', 'new_path'))
        annotation = annotation_lines(diff(cache, parent, fix)) > 0
    except CommandError:
        return {'reason': 'FETCH_ERROR'}
    paths = sorted({c[p] for c in source for p in ('old_path', 'new_path')
                    if is_source_path(c[p])})
    return {**resolution, 'source_files': paths, 'source_changes': source,
            'contract_paths': contracts, 'n_contract_docs': len(contracts),
            'fix_lines': lines, 'fix_touches_contract': touches_contract,
            'fix_touches_annotation': annotation,
            'fix_silent': not touches_contract and not annotation,
            'test_in_fix': any(is_test_path(p) for p in test_paths if p)}


def make_pool(advisories, resolutions, root=ROOT):
    counts, ecosystems, repositories = Counter(), defaultdict(Counter), defaultdict(Counter)
    measured, groups = {}, defaultdict(list)

    def count(reason, advisory, repo):
        counts[reason] += 1
        ecosystems[advisory['ecosystem']][reason] += 1
        repositories[repo][reason] += 1

    # Each distinct advisory is accounted for once; lowest id supplies scalar
    # advisory metadata, while ghsa_ids and cwes retain all merged advisories.
    unique = {}
    for advisory in sorted(advisories, key=lambda a: (a['ghsa_id'], a['ecosystem'])):
        unique.setdefault(advisory['ghsa_id'], advisory)
    for identifier, advisory in sorted(unique.items()):
        resolution = resolutions[identifier]
        repo = resolution.get('repo', '__unresolved__')
        if 'reason' in resolution:
            count(resolution['reason'], advisory, repo)
            continue
        key = (repo, resolution['fix_sha'])
        if key not in measured:
            measured[key] = eligible(resolution, root)
        fields = measured[key]
        if 'reason' in fields:
            count(fields['reason'], advisory, repo)
        else:
            groups[key].append(advisory)
    pool = []
    for key, group in sorted(groups.items()):
        group.sort(key=lambda a: a['ghsa_id'])
        primary = group[0]
        count('ELIGIBLE', primary, key[0])
        for duplicate in group[1:]:
            count('DEDUP', duplicate, key[0])
        pool.append({**measured[key], 'ghsa_id': primary['ghsa_id'],
                     'ghsa_ids': [a['ghsa_id'] for a in group],
                     'ecosystem': primary['ecosystem'],
                     'cwes': sorted({c for a in group for c in a['cwes']}),
                     'severity': primary.get('severity'),
                     'published_at': primary.get('published_at')})
    pool.sort(key=lambda a: a['ghsa_id'])
    inventory = {'unit': 'distinct advisories; ELIGIBLE counts deduplicated items',
                 'n_advisories': len(unique), 'n_items': len(pool),
                 'counts': dict(counts),
                 'per_ecosystem': {e: dict(c) for e, c in ecosystems.items()},
                 'per_repository': {r: dict(c) for r, c in repositories.items()}}
    return pool, inventory


def main(root=ROOT):
    mining = Path(root) / 'mining'
    guard_upstream(root, 'pool.json', 'pool_inventory.json')
    pool, inventory = make_pool(read_json(mining / 'advisories.json'),
                                read_json(mining / 'resolved.json'), root)
    write_json(mining / 'pool.json', pool)
    write_json(mining / 'pool_inventory.json', inventory)
    names = ['advisories.json', 'resolved.json', 'pool.json', 'pool_inventory.json']
    names.extend('cache/advisories_' + e + '.json' for e in ECOSYSTEMS)
    freeze = {'sha256': {n: sha256_file(mining / n) for n in names}, 'query': QUERY}
    write_json(mining / 'pool_freeze.json', freeze)
    print('eligible=' + str(len(pool)) + ' excluded=' +
          str(inventory['n_advisories'] - len(pool)))


if __name__ == '__main__':
    cli(main)
