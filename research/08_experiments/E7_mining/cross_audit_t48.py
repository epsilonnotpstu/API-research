#!/usr/bin/python3
"""Audit actual manifests across all generations without opening old packages."""
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
KEY = HERE / 'key'
B = runpy.run_path(str(HERE / 'build_t48.py'))


def main():
    B['R']['guard']()
    prior = B['B']['inputs']()
    middle = [json.loads(p.read_text()) for p in sorted((KEY / 't47_items').glob('*.json'))]
    new = B['R']['accepted']()
    rows = prior + middle + new
    logs = [(json.loads((KEY / name).read_text()), task) for name, task in
            [('build_log.json', 'prior'), ('e8b_build_log.json', 'T47'), ('e10_build_log.json', 'T48')]]
    details = {d['source_item']: dict(d, source_task=task) for log, task in logs for d in log['items']}
    assert set(details) == {r['item_id'] for r in rows}
    readers = {repo: B['B']['Git'](B['B']['M']['REPOS'][repo]) for repo in {r['repo'] for r in rows}}
    changes = {r['item_id']: set(readers[r['repo']].changed(r['parent_commit'], r['fix_commit'])) for r in rows}
    pairs = []
    for earlier in rows:
        for later in rows:
            if earlier is later or earlier['repo'] != later['repo']:
                continue
            a, b = details[earlier['item_id']], details[later['item_id']]
            paths = {p.split('/', 1)[1] for p in b['files']}
            overlap = changes[earlier['item_id']] & paths
            if not overlap or not readers[earlier['repo']].ancestor(earlier['fix_commit'], later['parent_commit']):
                continue
            retained = overlap & set(b['protected'])
            if b['source_task'] == 'T48':
                assert overlap == retained
            pairs.append(dict(earlier=a['item_id'], later=b['item_id'], earlier_set=a['source_task'],
                              later_set=b['source_task'], paths=sorted(overlap), retained_own_locators=sorted(retained)))
    flagged = {p['later'] for p in pairs}
    current = logs[-1][0]
    # An item can remain flagged after its optional overlap was removed.
    removed = {p['later'] for p in current['cross_item_pairs'] if p['excluded']}
    for d in current['items']:
        assert d['cross_item_flag'] == (d['item_id'] in flagged | removed)
    affected = {p['later'] for p in pairs if p['earlier_set'] == 'T48' and p['later_set'] != 'T48'}
    previously_flagged = {d['item_id'] for log, task in logs[:-1] for d in log['items'] if d['cross_item_flag']}
    result = dict(all_items=len(rows), all_pairs=pairs, newly_affected_prior_items=sorted(affected),
                  additional_prior_flags=sorted(affected - previously_flagged), V_flags_match=True,
                  existing_keys_not_modified=True,
                  summary=dict(pair_incidents=len(pairs), flagged_items=len(flagged | removed),
                               incoming_to_V=sum(p['later_set'] == 'T48' for p in pairs),
                               V_to_prior=sum(p['earlier_set'] == 'T48' and p['later_set'] != 'T48' for p in pairs),
                               affected_prior_items=len(affected), additional_prior_flagged_items=len(affected - previously_flagged)))
    B['R']['private_json'](KEY / 'e10_cross_item_all.json', result)
    B['R']['guard']()
    print(json.dumps(result['summary']))


if __name__ == '__main__':
    main()
