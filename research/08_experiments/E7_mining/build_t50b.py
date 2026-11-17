#!/usr/bin/python3
"""Rebuild the unused Q package with the existing salt and unchanged build rules."""
import json
from pathlib import Path
import runpy
import sys

HERE=Path(__file__).resolve().parent
OLD=runpy.run_path(str(HERE/'build_t50.py'))
for name,value in OLD.items():
    if not name.startswith('__'):globals()[name]=value
R=runpy.run_path(str(HERE/'review_t50b.py'))
# Shared functions retain their original globals; retarget only the new outputs.
OLD['reconstruct'].__globals__['R']=R
import inspect
pub_source=inspect.getsource(OLD['publish']).replace('e13_build_log.json','e13_build_log_t50b.json').replace('e13_shuffle_mapping.csv','e13_shuffle_mapping_t50b.csv')
exec(compile(pub_source,str(HERE/'build_t50b.py')+':publish','exec'),globals())

def main():
    R['continuation_guard']()
    assert R['next_row']() is None
    salt_path=KEY/'e13_shuffle_salt.txt';assert salt_path.is_file()
    salt=salt_path.read_text().strip()
    verify='--verify' in sys.argv
    if not verify:B['absent']([OUT,KEY/'e13_key.csv',KEY/'accepted_full_t50.csv',KEY/'e13_build_log_t50b.json',KEY/'e13_shuffle_mapping_t50b.csv'])
    result=reconstruct(salt)
    if verify:
        files,key,log,full,mapping=result
        actual={p.relative_to(OUT).as_posix():p.read_bytes() for p in OUT.rglob('*') if p.is_file()}
        assert actual==files
        assert (KEY/'e13_key.csv').read_bytes()==key
        assert (KEY/'accepted_full_t50.csv').read_bytes()==full_bytes(full)
        assert json.loads((KEY/'e13_build_log_t50b.json').read_text())==log
        assert (KEY/'e13_shuffle_mapping_t50b.csv').read_bytes()==B['cb'](['item_id','source_item'],mapping)
        verification=dict(summary=log['summary'],checks=dict(log['assertions'],existing_private_files_preserved=True,frozen_pool_preserved=True,
            separate_Q_only_package=True,exact_disk_reconstruction=True,same_shuffle_salt=True),auth_fixtures=log['auth_fixtures'],auth_value_variants=log['auth_value_variants'])
        path=HERE/'verification_t50b.json'
        if path.exists():assert json.loads(path.read_text())==verification
        else:R['private_json'](path,verification)
    else:publish(result)
    R['continuation_guard']()
    print(json.dumps(dict(verified=verify,**result[2]['summary'])))

if __name__=='__main__':main()
