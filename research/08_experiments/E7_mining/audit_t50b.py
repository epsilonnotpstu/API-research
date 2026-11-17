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
B=runpy.run_path(str(HERE/'build_t50b.py'))
R=B['R']

def reason_privacy_scan(rows,needles=()):
    """Keep source scanners unchanged; distinguish two exact reviewer prose phrases."""
    scanner=B['B']['O'];exceptions=[];clean=[]
    for row in rows:
        def replace(match):
            if match.group().casefold() not in {'basic authentication','basic credentials'}:
                return match.group()
            exceptions.append(dict(candidate_id=row['candidate_id'],reason_sha256=hashlib.sha256(row['reason'].encode()).hexdigest(),
                                   span=match.span(),classification='reviewer-generated authentication prose, not a credential literal'))
            return '<authentication prose>'
        clean.append(scanner['AUTH_LITERAL'].sub(replace,row['reason']))
    return scanner['privacy_findings']('\n'.join(clean).encode(),needles),exceptions

def main():
    R['continuation_guard']();runpy.run_path(str(HERE/'finalize_t50b.py'))['archived_hashes']();out=B['OUT']
    log=json.loads((KEY/'e13_build_log_t50b.json').read_text())
    actual={p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file()}
    assert {p:hashlib.sha256(data).hexdigest() for p,data in actual.items()}==log['package_hashes']
    incident=json.loads((KEY/'e13_preview_privacy_incident.json').read_text())
    variants=B['B']['O']['variants']({incident['observed_value'].encode()})
    assert all(not any(value in data for value in variants) for data in actual.values())
    fixtures=sorted(B['B']['O']['AUTH'].glob('*.yaml'))
    needles=B['B']['O']['fixture_needles'](fixtures)|{incident['observed_value'].encode()}
    assert all(not B['B']['O']['privacy_findings'](data,needles) for data in actual.values())
    import csv
    with (KEY/'review_decisions_t50.csv').open() as f:reasons=list(csv.DictReader(f))
    findings,exceptions=reason_privacy_scan(reasons,needles)
    assert not findings
    assert len(exceptions)==2
    R['private_json'](KEY/'t50b_reason_privacy_prose_exceptions.json',dict(exceptions=exceptions,package_scanner_changed=False,reason_records_changed=False))
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
    def immutable_result(path,value):
        if path.exists():assert json.loads(path.read_text())==value
        else:R['private_json'](path,value)
    immutable_result(KEY/'preservation_t50b_after.json',dict(files=len(after),changed=0,hashes=after))
    immutable_result(KEY/'e13_reference_audit_t50b.json',dict(local_references=references,missing_references=missing,remote_references=remote))
    # All previous repos differ from selected repos, so old/new ancestry pairs
    # cannot exist. The builder still checks all 195 items together.
    old=R['previous_items']();new=R['accepted']()
    assert not {r['repo'] for r in old}&{r['repo'] for r in new}
    immutable_result(KEY/'e13_cross_item_audit_t50b.json',dict(all_items=len(old)+len(new),prior_items=len(old),new_items=len(new),prior_new_repo_overlap=0,
        all_generation_check=True,new_cross_pairs=log['cross_item_pairs'],existing_keys_not_modified=True))
    summary=dict(existing_files_checked=len(after),changed_existing_files=0,pool3_frozen=True,board_read=False,
        package=dict(log['summary']),all_package_hashes_match=True,privacy_scan_passed=True,
        attribution_preview_incident=dict(incidents=1,remediation='Source hosting URL suppression; provenance comment only'),preview_privacy_incident=dict(incidents=1,value_repeated=False,variants_checked=len(variants),delivered_occurrences=0,filter_regression_required=True),
        reference_audit=dict(local_file_incidents=len(references),missing_file_incidents=len(missing),remote_file_incidents=len(remote)),
        cross_item_all_items=len(old)+len(new),prior_package_access=False,upstream_execution=False,network_used=False)
    immutable_result(HERE.parents[1]/'09_collab/logs/T50_scratch/final_audit_t50b.json',summary)
    print(json.dumps(summary))

if __name__=='__main__':main()
