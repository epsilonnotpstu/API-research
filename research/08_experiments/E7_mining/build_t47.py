#!/usr/bin/python3
"""Publish only new W items; preserve every pre-existing private file."""
import argparse
import csv
import hashlib
import hmac
import io
import json
from pathlib import Path
import re
import runpy
import secrets
import tempfile

HERE=Path(__file__).resolve().parent
KEY=HERE/'key'
OUT=HERE.parent/'E2_labelling/e8b_blind'
B=runpy.run_path(str(HERE/'build.py'))
R=runpy.run_path(str(HERE/'review_t47.py'))
FORBIDDEN=re.compile(r'\b(?:fix|fixed|commit|later|changed|mined|repair|direction|E6|E7|E8|T42|T43|T45|T46|T47)\b',re.I)


def w_order(rows,salt):
    return sorted(rows,key=lambda row:(hmac.new(salt.encode(),row['item_id'].encode(),hashlib.sha256).digest(),row['item_id']))


def prepare(new,prior,repos,salt,needles=()):
    assert new and all(r.get('source_task')=='T47' and r['set']=='new' for r in new)
    # Prepare together so the original cross-item test sees all previous items.
    all_files,_,all_log,all_full=B['prepare'](prior+new,repos,salt,needles)
    old_ids={r['item_id'] for r in prior}
    assert not old_ids & {r['item_id'] for r in new}
    target={r['item_id']:f'W{i:02}' for i,r in enumerate(w_order(new,salt),1)}
    convert={d['item_id']:target[d['source_item']] for d in all_log['items'] if d['source_item'] in target}
    files={convert[p.split('/',1)[0]]+'/'+p.split('/',1)[1]:data
           for p,data in all_files.items() if '/' in p and p.split('/',1)[0] in convert}
    full=[dict(r,item_id=convert[r['item_id']]) for r in all_full if r['item_id'] in convert]
    full.sort(key=lambda r:r['item_id'])
    items=[{column:r[column] for column in B['ITEM_COLUMNS']} for r in full]
    files['items.csv']=B['cb'](B['ITEM_COLUMNS'],items)
    assert not FORBIDDEN.search(files['items.csv'].decode())
    files['README.md']=all_files['README.md']
    details=[]
    for d in all_log['items']:
        if d['item_id'] in convert:
            details.append(dict(d,item_id=convert[d['item_id']]))
    stable={d['item_id']:d['source_item'] for d in all_log['items']}
    pairs=[dict(p,earlier=convert.get(p['earlier'],stable[p['earlier']]),later=convert.get(p['later'],stable[p['later']]))
           for p in all_log['cross_item_pairs'] if p['later'] in convert]
    log=dict(items=details,cross_item_pairs=pairs,assertions=all_log['assertions'],
             package_hashes={p:B['sha'](data) for p,data in sorted(files.items())},
             summary=dict(items=len(full),files=len(files),bytes=sum(map(len,files.values())),
                 contract_files=sum('/contract/' in p for p in files),implementation_files=sum('/impl/' in p for p in files),
                 cross_item_flagged=sum(r['cross_item_flag']=='true' for r in full),
                 excluded_cross_files=sum(len(p['excluded']) for p in pairs),
                 retained_cross_locators=sum(len(p['retained_own_locators']) for p in pairs),
                 projected_files=sum(f['projection'] for d in details for f in d['files'].values()),
                 redacted_files=sum(f['redacted'] for d in details for f in d['files'].values()),
                 all_items_cross_checked=len(prior)+len(new)))
    mapping=[dict(item_id=iid,source_item=source) for source,iid in sorted(target.items(),key=lambda v:v[1])]
    assert {p.split('/')[0] for p in files if '/' in p}==set(target.values())
    assert len(full)==len(new)
    for data in files.values():
        B['require'](not B['O']['privacy_findings'](data,needles),'Private value detected (suppressed)')
    return files,B['cb'](B['KEY_COLUMNS'],full),log,full,mapping


def full_bytes(full):
    columns=list(dict.fromkeys(B['KEY_COLUMNS']+[k for r in full for k in r]))
    normalized=[{k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in full]
    return B['cb'](columns,normalized)


def publish(result,output=OUT,key_dir=KEY):
    output=Path(output);key_dir=Path(key_dir)
    files,key,log,full,mapping=result
    destinations=[output]+[key_dir/name for name in ['e8b_key.csv','accepted_full_t47.csv','e8b_build_log.json','e8b_shuffle_mapping.csv']]
    B['absent'](destinations)
    with tempfile.TemporaryDirectory(prefix='.t47-stage-',dir=HERE) as temporary:
        stage=Path(temporary)/'package';stage.mkdir()
        for rel,data in files.items():
            B['O']['safe_path'](rel)
            path=stage/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        assert {p.relative_to(stage).as_posix():B['sha'](p.read_bytes()) for p in stage.rglob('*') if p.is_file()}==log['package_hashes']
        B['absent'](destinations)
        # mkdir is exclusive; no replace, unlink or overwrite operation exists.
        output.mkdir()
        for child in stage.iterdir():child.rename(output/child.name)
        values={'e8b_key.csv':key,'accepted_full_t47.csv':full_bytes(full),
                'e8b_build_log.json':B['jb'](log),
                'e8b_shuffle_mapping.csv':B['cb'](['item_id','source_item'],mapping)}
        for name,data in values.items():
            with (key_dir/name).open('xb') as stream:stream.write(data)


def reconstruct(salt):
    fixtures=sorted(B['O']['AUTH'].glob('*.yaml'))
    needles=B['O']['fixture_needles'](fixtures)
    result=prepare(R['accepted'](),B['inputs'](),B['M']['REPOS'],salt,needles)
    result[2].update(auth_fixtures=len(fixtures),auth_value_variants=len(B['O']['variants'](needles)))
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preflight',action='store_true');parser.add_argument('--verify',action='store_true')
    args=parser.parse_args();R['guard']()
    salt_path=KEY/'e8b_shuffle_salt.txt'
    if not salt_path.exists():
        with salt_path.open('x') as stream:stream.write(secrets.token_hex(32)+'\n')
    salt=salt_path.read_text().strip()
    assert salt!=(KEY/'shuffle_salt.txt').read_text().strip()
    if not args.verify and not args.preflight:
        B['absent']([OUT,KEY/'e8b_key.csv',KEY/'accepted_full_t47.csv',KEY/'e8b_build_log.json'])
    result=reconstruct(salt)
    if args.verify:
        files,key,log,full,mapping=result
        actual={p.relative_to(OUT).as_posix():p.read_bytes() for p in OUT.rglob('*') if p.is_file()}
        assert actual==files
        assert (KEY/'e8b_key.csv').read_bytes()==key
        assert (KEY/'accepted_full_t47.csv').read_bytes()==full_bytes(full)
        assert json.loads((KEY/'e8b_build_log.json').read_text())==log
        assert (KEY/'e8b_shuffle_mapping.csv').read_bytes()==B['cb'](['item_id','source_item'],mapping)
        R['guard']()
        verification=dict(summary=log['summary'],checks=dict(log['assertions'],
                         existing_private_files_preserved=True,frozen_pool_preserved=True,
                         separate_W_only_package=True,exact_disk_reconstruction=True,
                         independent_salt=True),auth_fixtures=log['auth_fixtures'],auth_value_variants=log['auth_value_variants'])
        verification_path=HERE/'verification_t47.json'
        if verification_path.exists():
            assert json.loads(verification_path.read_text())==verification
        else:
            R['private_json'](verification_path,verification)
    elif not args.preflight:
        publish(result);R['guard']()
    print(json.dumps(dict(preflight=args.preflight,verified=args.verify,**result[2]['summary'])))


if __name__=='__main__':main()
