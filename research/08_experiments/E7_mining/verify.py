#!/usr/bin/python3
"""Verify published bytes, reconstruct parent excerpts, and emit aggregates only."""
from collections import Counter
import csv
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys

HERE=Path(__file__).resolve().parent
B=runpy.run_path(str(HERE/'build.py'))

def main():
    rows=B['inputs']();fixtures=sorted(B['O']['AUTH'].glob('*.yaml'))
    expected,key,log,full=B['prepare'](rows,B['M']['REPOS'],(B['KEY']/'shuffle_salt.txt').read_text().strip(),B['O']['fixture_needles'](fixtures))
    output=B['OUT'];actual={p.relative_to(output).as_posix():p.read_bytes() for p in output.rglob('*') if p.is_file()}
    assert actual==expected,'Published bytes differ from deterministic parent reconstruction'
    assert (B['KEY']/'e7_key.csv').read_bytes()==key
    published=json.loads((B['KEY']/'build_log.json').read_text())
    assert log['package_hashes']==published['package_hashes']
    assert log['assertions']==published['assertions']
    keys=list(csv.DictReader(io.StringIO(key.decode())))
    assert list(keys[0])==B['KEY_COLUMNS']
    full_rows=list(csv.DictReader((B['KEY']/'accepted_full.csv').open()))
    assert len(full_rows)==len(keys)==len(rows)
    items=list(csv.DictReader(io.StringIO(actual['items.csv'].decode())))
    assert list(items[0])==B['ITEM_COLUMNS']
    assert [r['item_id'] for r in items]==[f'X{i:02}' for i in range(1,len(items)+1)]
    assert not B['FORBIDDEN'].search(actual['items.csv'].decode())
    by_id={r['item_id']:r for r in full_rows}
    for r,k in zip(items,keys):
        assert r['proposition']==by_id[r['item_id']]['proposition']
        assert r['repo']==k['repo'] and r['operation']==k['operation']
    test_outputs=[]
    for script in ['test_build.py','test_pool2.py','test_review2.py']:
        test=subprocess.run([sys.executable,'-I','-B',str(HERE/script)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        test_outputs.append(test.stdout)
        assert test.returncode==0,'Synthetic or corpus audit tests failed'
    (HERE.parents[1]/'09_collab/logs/T46_scratch/test_results.txt').write_bytes(b'\n'.join(test_outputs))
    report=dict(summary=log['summary'],sets=dict(Counter(r['set'] for r in keys)),new_direction_counts=dict(Counter(r['truth_direction'] for r in keys if r['set']=='new')),
        source_tasks=dict(Counter(r['source_task'] for r in keys)),actual_disk_hashes=True,production_reconstruction_deterministic=True,key_schema=True,verbatim_propositions=True,forbidden_words=True,
        auth_fixtures=published['auth_fixtures'],auth_value_variants=published['auth_value_variants'],assertions=log['assertions'])
    with (HERE/'verification2.json').open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(report))

if __name__=='__main__':main()
