#!/usr/bin/python3
"""Supervisor continuation: append-only decisions, fsync, complete-round yields."""
import os
import io
import runpy
from pathlib import Path
from collections import Counter
import csv
import json
import hashlib

HERE=Path(__file__).resolve().parent
L=runpy.run_path(str(HERE/'review_t50.py'))
for _name,_value in L.items():
    if not _name.startswith('__'):globals()[_name]=_value
G=L['accept'].__globals__
ARCHIVE=KEY/'t50_superseded_round2'
_decide=L['decide']
_display=L['display']

def display(text):
    text='\n'.join('<redacted source attribution URL>' if re.search(r'https?://(?:www\.)?(?:github|gitlab|gitee|bitbucket)\.',line) else '<redacted encoded literal>' if re.search(r'(?:0x[0-9a-fA-F]{2}[,\s]*){8,}|\bh1:[A-Za-z0-9+/=]+',line) else line for line in text.splitlines())
    return _display(text)

def private_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())

def next_row():
    done=decisions();decided={d['candidate_id'] for d in done}
    items=[r for r in accepted() if r['candidate_id'] in decided]
    if len(items)>=60:return None
    seen={(d['repo'],d['rank']) for d in done};counts=Counter(r['repo'] for r in items)
    by_pair={(r['repo'],r['rank']):r for r in sources()}
    for phase,repo,rank in plan():
        if counts[repo]>=10 or (repo,rank) in seen:continue
        return dict(by_pair[repo,rank],review_phase=phase)
    return None

def append_csv_records():
    path=KEY/'review_decisions_t50.csv'
    with path.open() as f:old=list(csv.DictReader(f));fields=list(old[0])
    seen={(r['candidate_id'],r['operation'],r['review_status']) for r in old}
    new=[]
    # JSON records are final, exclusive and durable before this journal append.
    for d in sorted(decisions(),key=lambda d:(d['rank'],[r['clone_name'] for r in P3['selected']()].index(d['repo']))):
        row=dict(d,operation='',source_item='')
        if (d['candidate_id'],'',d['review_status']) not in seen:new.append(row)
        for p in sorted((KEY/'t50_capped').glob('*.json')):
            cap=json.loads(p.read_text())
            if cap['candidate_id']!=d['candidate_id']:continue
            row=dict(d,review_status='accepted_capped',reason_code=cap['reason_code'],reason=cap['reason'],operation=cap['operation'],source_item=cap['item_id'])
            if (d['candidate_id'],cap['operation'],'accepted_capped') not in seen:new.append(row)
    if new:
        with path.open('a',newline='') as f:
            csv.DictWriter(f,fields,lineterminator='\n').writerows(new);f.flush();os.fsync(f.fileno())

def yield_rows():
    ds=decisions();items=accepted();counts=Counter(r['repo'] for r in items);sizes=Counter(r['repo'] for r in sources())
    result=[]
    for meta in P3['selected']():
        repo=meta['clone_name'];reviewed=[d for d in ds if d['repo']==repo];last=max((d['rank'] for d in reviewed),default=0)
        reason='repo cap' if counts[repo]>=10 else 'pool exhausted' if last>=sizes[repo] else 'T50 target reached' if len(items)>=60 else 'continuing'
        result.append(dict(repo=repo,pool3=sizes[repo],reviewed=len(reviewed),accepted_candidates=sum(d['reason_code']=='ACCEPT' for d in reviewed),items=counts[repo],capped=counts[repo]>=10,last_reviewed_rank=last,stop_reason=reason))
    return result

def checkpoint(force=False):
    rows=yield_rows();ds=decisions();current=next_row();last=max((d['rank'] for d in ds),default=0)
    complete=current is None or current['rank']>last
    if force or complete:
        buffer=io.StringIO(newline='');w=csv.DictWriter(buffer,list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
        temporary=HERE/'yield_t50.csv.next'
        with temporary.open('w') as f:f.write(buffer.getvalue());f.flush();os.fsync(f.fileno())
        temporary.replace(HERE/'yield_t50.csv')
        path=KEY/'t50b_round_checkpoints'/f'{last:04}_{len(ds):06}.json'
        if not path.exists():private_json(path,dict(round=last,complete_round=complete,reviewed=len(ds),accepted_items=len(accepted()),stopped=current is None))

def decide(repo,rank,code,reason=None):
    _decide(repo,rank,code,reason)
    append_csv_records();checkpoint()

def continuation_guard():
    guard()
    manifest=json.loads((ARCHIVE/'manifest.json').read_text())
    for name,digest in manifest['existing_record_hashes'].items():
        if name=='review_decisions_t50.csv':continue
        assert hashlib.sha256((KEY/name).read_bytes()).hexdigest()==digest,'Prior record changed'
    original=(ARCHIVE/'review_decisions_t50.csv').read_bytes()
    assert (KEY/'review_decisions_t50.csv').read_bytes().startswith(original),'Journal is not append-only'
    assert hashlib.sha256((HERE/'pool3.json').read_bytes()).hexdigest()==manifest['pool3_sha256']

G.update(next_row=next_row,private_json=private_json,decide=decide,display=display)
# Prefer an explicitly supplied full path over suffix matches (for example a
# real document and a nested symlink with the same suffix). Evidence is still
# read by git show at the exact parent and all locators remain auditable.
import inspect
_accept_source=inspect.getsource(G['_accept']).replace('def accept(', 'def accept_exact_path(')
_accept_source=_accept_source.replace("[p for p in tree if p.endswith(suffix)]", "([suffix] if suffix in tree else [p for p in tree if p.endswith(suffix)])")
exec(compile(_accept_source,str(HERE/'review_t50b.py')+':exact-path','exec'),G)
G['_accept']=G['accept_exact_path']
# The historical budget marker remains byte-identical; only this continuation
# ignores it, under the supervisor's explicit amendment.
if __name__=='__main__':
    continuation_guard();append_csv_records();checkpoint(force=True)
    n=next_row()
    print(json.dumps(dict(reviewed=len(decisions()),items=len(accepted()),next_repo=n['repo'] if n else None,next_rank=n['rank'] if n else None)))
