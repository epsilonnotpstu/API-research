"""G1 review utilities: read data, redact console excerpts, preserve raw searches."""
import csv
import datetime
import json
from pathlib import Path
import re
import subprocess

BASE = Path(__file__).resolve().parent.parent
SENSITIVE = re.compile(r'@author|copyright|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|authorization|\bBasic\s+\S+|\bBearer\s+\S+|(?:password|passwd|api[_-]?key|client[_-]?secret|access[_-]?token)\s*[:=]|[\"\x27](?:password|token|secret)[\"\x27]\s*:|[\"\x27][0-9a-f]{32,}[\"\x27]|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|static final String \w*(?:TOKEN|TOK|TAN|API_KEY)\w*\s*=', re.I)

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def safe(line):
    return '[REDACTED credential-looking or attribution line]' if SENSITIVE.search(line) else line

def show(file, start=1, end=None):
    p = BASE / file
    print(f'FILE {file}')
    for i, line in enumerate(p.read_text().splitlines(), 1):
        if i >= start and (end is None or i <= end):
            print(f'{i}: {safe(line)}')

def search(root, pattern, glob=None):
    """Explicit subtree only; no symlinks followed."""
    p = BASE / root
    rx = re.compile(pattern, re.I)
    files = [p] if p.is_file() else sorted(p.rglob(glob or '*'))
    for f in files:
        if not f.is_file() or f.is_symlink():
            continue
        try:
            lines = f.read_text().splitlines()
        except UnicodeError:
            continue
        for i, line in enumerate(lines, 1):
            if rx.search(line):
                cleaned = safe(line)
                print(f'{f.relative_to(BASE)}:{i}: {cleaned[:450]}' + (' [long line truncated]' if len(cleaned)>450 else ''))

def begin(item, target, mandatory, reason):
    row = next(r for r in csv.DictReader((BASE / 'items.csv').open()) if r['item_id'] == item)
    record = dict(item_id=item, proposition=row['proposition'], target=target,
                  mandatory_search=dict(required=mandatory, reason=reason),
                  start_time=now(), end_time=None, hits=[], manual_additions=[],
                  decision=None, history_scope='unavailable')
    (BASE / 'review_G1' / f'{item}.json').write_text(json.dumps(record, indent=2) + '\n')

def run(item, contract, method, path, status=None, field=None):
    cmd = ['/usr/bin/python3', '-I', '-B', '../../tools/intent_evidence.py',
           f'{item}/source', contract, '--method', method, '--path', path, '--json']
    if status is not None:
        cmd += ['--status', str(status)]
    if field is not None:
        cmd += ['--field', field]
    p = subprocess.run(cmd, cwd=BASE, capture_output=True)
    dest = BASE / 'search_G1' / item
    dest.with_suffix('.json').write_bytes(p.stdout)
    dest.with_suffix('.stderr').write_bytes(p.stderr)
    dest.with_suffix('.exitcode').write_text(str(p.returncode) + '\n')
    print(item, 'exit', p.returncode)
    if p.returncode:
        print(safe(p.stderr.decode(errors='replace')))

def result(item):
    d = json.loads((BASE / 'search_G1' / f'{item}.json').read_text())
    for k, v in d.items():
        if k != 'hits':
            print(k, safe(json.dumps(v)))
    for i, hit in enumerate(d.get('hits', [])):
        print('HIT', i, safe(json.dumps(hit)))

def compact(item):
    d = json.loads((BASE / 'search_G1' / f'{item}.json').read_text())
    print({k:d[k] for k in ['independent_evidence','history','scan','warnings']})
    for i,x in enumerate(d['hits']):
        print(i, x['category'], x['location'], safe(x['snippet']))

def finish(item, label, dispositions=None, additions=None, details=None):
    p = BASE / 'review_G1' / f'{item}.json'
    d = json.loads(p.read_text())
    rawpath = BASE / 'search_G1' / f'{item}.json'
    raw = json.loads(rawpath.read_text()) if rawpath.exists() and rawpath.read_text().strip() else {}
    hit_reviews = []
    for i, h in enumerate(raw.get('hits', [])):
        info = (dispositions or {}).get(i)
        if info is None:
            raise ValueError(f'Missing review for hit {i}')
        disposition, reason, checks = info
        hit_reviews.append(dict(index=i, category=h['category'], file=h['file'], line=h['line'],
                                disposition=disposition, reason=reason,
                                checklist=dict(zip(['a_explicit_behavior','b_target_linkage','c_independent_basis','d_applicable_revision','e_counterevidence_reviewed'], checks))))
    d.update(hits=hit_reviews, manual_additions=additions or [], decision=dict(label, details=details), end_time=now())
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')

def label(item, l1, l2, confidence, evidence_types, locators, rationale,
          both=False, reviewed='not_applicable', proposed='', flag='none',
          dispositions=None, additions=None, details=None, search_status=None):
    rawpath = BASE / 'search_G1' / f'{item}.json'
    raw = json.loads(rawpath.read_text()) if rawpath.exists() and rawpath.read_text().strip() else None
    values = dict(item_id=item, L1=l1, L2=l2, proposed_L2=proposed, confidence=confidence,
                  evidence_types=evidence_types, evidence_locators=locators,
                  both_candidate=both, intent_search_status=search_status or ('complete' if raw else 'not_run'),
                  intent_search_verdict=raw['independent_evidence'] if raw else 'NA',
                  intent_review_verdict=reviewed, adjudication_flag=flag,
                  history_scope='unavailable', rationale=rationale)
    finish(item, values, dispositions, additions, details)
