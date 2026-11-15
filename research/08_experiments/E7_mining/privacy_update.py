#!/usr/bin/python3
"""Apply only deterministic, line-preserving privacy redactions to this output.

The ordinary publisher still refuses all existing destinations. This narrowly
scoped remediation requires the prior disk manifest, unchanged item/key bytes,
and equality between parent reconstruction and sanitization of existing bytes.
"""
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
B=runpy.run_path(str(HERE/'build.py'))

def main():
    kd=B['KEY'];out=B['OUT'];audit=kd/'privacy_update.json';B['absent']([audit])
    old_bytes=(kd/'build_log.json').read_bytes();old=json.loads(old_bytes)
    actual={p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file()}
    assert {p:B['sha'](d) for p,d in actual.items()}==old['package_hashes']
    fixtures=sorted(B['O']['AUTH'].glob('*.yaml'));needles=B['O']['fixture_needles'](fixtures)
    expected,key,log,_=B['prepare'](B['inputs'](),B['M']['REPOS'],(kd/'shuffle_salt.txt').read_text().strip(),needles)
    assert set(actual)==set(expected)
    assert key==(kd/'e7_key.csv').read_bytes()
    assert actual['items.csv']==expected['items.csv']
    changes=[]
    for relative,data in expected.items():
        before=actual[relative]
        if data==before:continue
        assert '/contract/' in relative or '/impl/' in relative
        path=relative.split('/',2)[2]
        assert B['sanitize'](before,path,needles)==data
        assert len(before.splitlines())==len(data.splitlines())
        changes.append(dict(path=relative,before_sha256=B['sha'](before),after_sha256=B['sha'](data)))
    assert changes,'No privacy remediation needed'
    for change in changes:(out/change['path']).write_bytes(expected[change['path']])
    log.update(auth_fixtures=len(fixtures),auth_value_variants=len(B['O']['variants'](needles)),
        input_hashes={**old['input_hashes'],str(HERE/'build.py'):B['sha']((HERE/'build.py').read_bytes())},
        privacy_update_prior_log_sha256=B['sha'](old_bytes))
    (kd/'build_log.json').write_bytes(B['jb'](log))
    # Preserve the earlier aggregate audit as private provenance before rerunning.
    earlier=HERE/'verification.json'
    if earlier.exists():earlier.rename(kd/'verification_before_privacy_update.json')
    with audit.open('xb') as f:f.write(B['jb'](dict(rule='Comment credit headers and continuations only; unchanged line counts, item table and key',modified_files=len(changes),changes=changes,prior_log_sha256=B['sha'](old_bytes),final_summary=log['summary'])))
    print(json.dumps(dict(modified_files=len(changes),**log['summary'])))

if __name__=='__main__':main()
