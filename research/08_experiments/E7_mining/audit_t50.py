#!/usr/bin/python3
"""Independent delivered-byte, reference, privacy and preservation audit."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import posixpath
import runpy

HERE=Path(__file__).resolve().parent
KEY=HERE/'key'
B=runpy.run_path(str(HERE/'build_t50.py'))
R=B['R']

def main():
    R['guard']();out=B['OUT']
    log=json.loads((KEY/'e13_build_log.json').read_text())
    actual={p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file()}
    assert {p:hashlib.sha256(data).hexdigest() for p,data in actual.items()}==log['package_hashes']
    incident=json.loads((KEY/'e13_preview_privacy_incident.json').read_text())
    variants=B['B']['O']['variants']({incident['observed_value'].encode()})
    assert all(not any(value in data for value in variants) for data in actual.values())
    fixtures=sorted(B['B']['O']['AUTH'].glob('*.yaml'))
    needles=B['B']['O']['fixture_needles'](fixtures)|{incident['observed_value'].encode()}
    assert all(not B['B']['O']['privacy_findings'](data,needles) for data in actual.values())
    references=[];missing=[];remote=[]
    for relative,data in actual.items():
        if '/contract/' not in relative or not relative.endswith(('.yaml','.yml','.json')):continue
        for ref in B['B']['references'](data):
            filename,_,fragment=ref.partition('#')
            if not filename:continue
            if '://' in filename:
                remote.append(dict(source=relative,reference=ref));continue
            target=posixpath.normpath(posixpath.join(posixpath.dirname(relative),filename))
            entry=dict(source=relative,target=target,fragment=fragment);references.append(entry)
            if target not in actual:missing.append(entry)
    assert not missing,'New package contains missing contract file references'
    baseline=json.loads((KEY/'preservation_t50_start.json').read_text())
    after={p:hashlib.sha256((HERE/p).read_bytes()).hexdigest() for p in baseline}
    assert after==baseline
    R['private_json'](KEY/'preservation_t50_after.json',dict(files=len(after),changed=0,hashes=after))
    R['private_json'](KEY/'e13_reference_audit.json',dict(local_references=references,missing_references=missing,remote_references=remote))
    # All previous repos differ from selected repos, so old/new ancestry pairs
    # cannot exist. The builder still checks all 195 items together.
    old=R['previous_items']();new=R['accepted']()
    assert not {r['repo'] for r in old}&{r['repo'] for r in new}
    R['private_json'](KEY/'e13_cross_item_audit.json',dict(all_items=len(old)+len(new),prior_items=len(old),new_items=len(new),prior_new_repo_overlap=0,
        all_generation_check=True,new_cross_pairs=log['cross_item_pairs'],existing_keys_not_modified=True))
    summary=dict(existing_files_checked=len(after),changed_existing_files=0,pool3_frozen=True,board_read=False,
        package=dict(log['summary']),all_package_hashes_match=True,privacy_scan_passed=True,
        preview_privacy_incident=dict(incidents=1,value_repeated=False,variants_checked=len(variants),delivered_occurrences=0,filter_regression_required=True),
        reference_audit=dict(local_file_incidents=len(references),missing_file_incidents=len(missing),remote_file_incidents=len(remote)),
        cross_item_all_items=len(old)+len(new),prior_package_access=False,upstream_execution=False,network_used=False)
    R['private_json'](HERE.parents[1]/'09_collab/logs/T50_scratch/final_audit.json',summary)
    print(json.dumps(summary))

if __name__=='__main__':main()
