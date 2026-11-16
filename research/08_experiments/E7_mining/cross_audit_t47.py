#!/usr/bin/python3
"""Read-only, all-pairs audit of actual manifests, including old destinations."""
from collections import Counter
import csv
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
KEY=HERE/'key'
B=runpy.run_path(str(HERE/'build_t47.py'))


def main():
    B['R']['guard']()
    prior=B['B']['inputs']();new=B['R']['accepted']();rows=prior+new
    old_log=json.loads((KEY/'build_log.json').read_text())
    new_log=json.loads((KEY/'e8b_build_log.json').read_text())
    details={d['source_item']:dict(d,source_task='prior') for d in old_log['items']}
    details.update({d['source_item']:dict(d,source_task='T47') for d in new_log['items']})
    assert set(details)=={r['item_id'] for r in rows}
    readers={repo:B['B']['Git'](B['B']['M']['REPOS'][repo]) for repo in {r['repo'] for r in rows}}
    changes={r['item_id']:set(readers[r['repo']].changed(r['parent_commit'],r['fix_commit'])) for r in rows}
    pairs=[]
    for earlier in rows:
        for later in rows:
            if earlier is later or earlier['repo']!=later['repo']:continue
            a=details[earlier['item_id']];b=details[later['item_id']]
            paths={p.split('/',1)[1] for p in b['files']}
            overlap=changes[earlier['item_id']]&paths
            if not overlap or not readers[earlier['repo']].ancestor(earlier['fix_commit'],later['parent_commit']):continue
            retained=overlap&set(b['protected'])
            # All optional overlaps were already removed from the new package.
            if b['source_task']=='T47':assert overlap==retained
            pairs.append(dict(earlier=a['item_id'],later=b['item_id'],earlier_set=a['source_task'],
                              later_set=b['source_task'],paths=sorted(overlap),retained_own_locators=sorted(retained)))
    flagged={p['later'] for p in pairs}
    for d in new_log['items']:assert d['cross_item_flag']==(d['item_id'] in flagged)
    result=dict(all_items=len(rows),all_pairs=pairs,
                newly_affected_prior_items=sorted({p['later'] for p in pairs if p['earlier_set']=='T47' and p['later_set']=='prior'}),
                W_flags_match=True,existing_keys_not_modified=True,
                summary=dict(pair_incidents=len(pairs),flagged_items=len(flagged),
                    incoming_to_W=sum(p['later_set']=='T47' for p in pairs),
                    W_to_prior=sum(p['earlier_set']=='T47' and p['later_set']=='prior' for p in pairs)))
    B['R']['private_json'](KEY/'e8b_cross_item_all.json',result)
    B['R']['guard']()
    print(json.dumps(result['summary']))


if __name__=='__main__':main()
