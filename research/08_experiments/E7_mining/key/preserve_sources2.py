#!/usr/bin/python3
"""Keep the old logical key rows and explicitly map the new package shuffle."""
import csv
import hashlib
import json
from pathlib import Path
import runpy

H=Path(__file__).resolve().parents[1];K=H/'key'
B=runpy.run_path(str(H/'build.py'))
def read(path):
    with path.open() as f:return list(csv.DictReader(f))
identity=lambda r:(r['repo'],r['fix_commit'],r['operation'],r['fix_family'])
old=read(K/'t45_snapshot/e7_key.csv');full=read(K/'accepted_full.csv')
old_by={identity(r):r for r in old};new=json.loads((K/'new_accepted2.json').read_text());new_by={identity(r):r for r in new}
exploratory={identity(r):r for r in read(H.parent/'E6_realfix/combined_accepted.csv')}
stable=[];mapping=[]
for r in old:
    source_task='T45' if r['set']=='new' else exploratory[identity(r)]['source_task']
    stable.append(dict(r,source_task=source_task))
for r in full:
    key=identity(r)
    if key in new_by:
        source=new_by[key]
        row={c:r[c] for c in B['KEY_COLUMNS']};row['item_id']=source['item_id'];stable.append(row)
        stable_id=row['item_id']
    else:stable_id=old_by[key]['item_id']
    mapping.append(dict(corpus_item_id=stable_id,package_item_id=r['item_id'],source_task=r['source_task'],set=r['set'],repo=r['repo']))
assert len(stable)==len(mapping)==70
for old_row,stable_row in zip(old,stable):assert all(stable_row[c]==v for c,v in old_row.items())
assert (K/'new_accepted.json').read_bytes()==(K/'t45_snapshot/new_accepted.json').read_bytes()
assert (K/'shuffle_salt.txt').read_bytes()!=(K/'t45_snapshot/shuffle_salt.txt').read_bytes()
(K/'corpus_key.csv').write_bytes(B['cb'](B['KEY_COLUMNS'],stable))
(K/'shuffle_mapping.csv').write_bytes(B['cb'](list(mapping[0]),mapping))
log=json.loads((K/'build_log.json').read_text());manifest=json.loads((K/'t45_snapshot/package_manifest.json').read_text())
assert log['replacement_history'][-1]['old_package_sha256']==B['package_hash'](manifest)
audit=dict(T45_logical_rows_preserved=41,T45_new_source_rows_preserved=16,T46_appended_rows=29,source_task_added=True,new_salt_verified=True,new_shuffle_verified=any(r['corpus_item_id']!=r['package_item_id'] for r in mapping if r['source_task']=='T45'),old_package_hash_verified=True,stable_key='corpus_key.csv',package_key='e7_key.csv',mapping='shuffle_mapping.csv')
(K/'preservation_audit2.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(audit))
