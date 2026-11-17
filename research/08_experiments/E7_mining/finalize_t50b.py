#!/usr/bin/python3
"""Audit the authorized continuation without rewriting its append-only journal."""
import csv
import hashlib
import inspect
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
KEY=HERE/'key'
R=runpy.run_path(str(HERE/'review_t50b.py'))
F=runpy.run_path(str(HERE/'finalize_t50.py'))
validate_previews=F['validate_previews']
source=inspect.getsource(F['audit'])
source=source.replace("stop=json.loads((KEY/'t50_stop.json').read_text()) if (KEY/'t50_stop.json').exists() else None",'stop=None')
scope=dict(F,R=R)
exec(compile(source,str(HERE/'finalize_t50b.py')+':shared-audit','exec'),scope)
_audit=scope['audit']

def archived_hashes():
    manifest=json.loads((R['ARCHIVE']/'manifest.json').read_text())
    for name,value in manifest['hashes'].items():
        if isinstance(value,dict):
            folder=R['ARCHIVE']/name
            actual={p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.rglob('*') if p.is_file()}
            assert actual==value,'Superseded directory changed'
        else:assert hashlib.sha256((R['ARCHIVE']/name).read_bytes()).hexdigest()==value,'Superseded file changed'
    return manifest

def audit():
    R['continuation_guard']();manifest=archived_hashes()
    ordered,yields,summary,exported=_audit()
    assert summary['accepted_items']>=60 or all(r['capped'] or r['last_reviewed_rank']>=r['pool3'] for r in yields)
    assert ordered[40]['rank']==3
    assert [(d['repo'],d['rank']) for d in ordered[:40]]==[(m['clone_name'],rank) for rank in [1,2] for m in R['P3']['selected']()]
    # The historical marker remains evidence of round 2, not a current stop.
    assert json.loads((KEY/'t50_stop.json').read_text())['completed_round']==2
    with (KEY/'review_decisions_t50.csv').open() as f:actual=list(csv.DictReader(f))
    expected=[{k:str(v) for k,v in row.items()} for row in exported]
    signature=lambda row:(row['candidate_id'],row['operation'],row['review_status'])
    assert {signature(r):r for r in actual}=={signature(r):r for r in expected}
    assert len(actual)==len(exported)
    # A target stop may occur before the current round is complete.
    last=ordered[-1]['rank'];pairs={(d['repo'],d['rank']) for d in ordered}
    size={r['repo']:r['pool3'] for r in yields}
    round_complete=all((repo,last) in pairs or size[repo]<last or r['capped'] for r in yields for repo in [r['repo']])
    summary.update(completed_round=last if round_complete else last-1,
                   current_round=last,current_round_complete=round_complete,
                   continuation_start_rank=3,continuation_reviewed=len(ordered)-40,
                   continuation_items=len(R['accepted']())-8,
                   original_round2_items=8,append_only_verified=True,
                   superseded_outputs_verified=True,same_shuffle_salt=True,
                   stopping_reason='T50 acceptance threshold reached after the complete final candidate.' if len(R['accepted']())>=60 else 'Every repo capped or exhausted')
    return ordered,yields,summary,exported

def main():
    R['append_csv_records']();R['checkpoint'](force=True)
    _,_,summary,_=audit()
    path=HERE/'summary_t50b.json'
    if path.exists():assert json.loads(path.read_text())==summary
    else:R['private_json'](path,summary)
    print(json.dumps(summary))

if __name__=='__main__':main()
