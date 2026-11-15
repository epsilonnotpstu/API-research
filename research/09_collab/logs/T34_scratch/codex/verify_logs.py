"""Compare independent recount with Claude stdout, without reading exchanges."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
s = json.loads((HERE / 'recount.json').read_text())
cc = (HERE.parent / 'claude_run_cc.log').read_text().splitlines()
ss = (HERE.parent / 'claude_run_ss.log').read_text().splitlines()
checks = 0
ctl = None
for line in cc:
    if line.startswith('== controlled'):
        ctl = 'True'
    elif line.startswith('== manifest'):
        ctl = 'False'
    m = re.match(r'\s+(\S+)\s+(\S+)\s+\| EvoMaster (\d+)/(\d+) \| Schemathesis (\d+)/(\d+)', line)
    if m:
        sut, fault, e, n, sch, n2 = m.groups()
        row = next(x for x in s['controlled_by_sut_fault'] if (x['controlled'], x['sut'], x['fault']) == (ctl, sut, fault))
        assert [int(e), int(sch), int(n), int(n2)] == [row['evo_beyond'], row['sch_beyond'], row['pairs'], row['pairs']]
        checks += 1
    m = re.match(r'\s+TOTAL \| EvoMaster (\d+)/(\d+) \| Schemathesis (\d+)/(\d+)', line)
    if m:
        e, n, sch, n2 = map(int, m.groups())
        row = s['controlled_totals'][ctl]
        assert [e, sch, n, n2] == [row['evo_beyond'], row['sch_beyond'], row['pairs'], row['pairs']]
        checks += 1
for line in ss:
    m = re.match(r'\s+(\S+)\s+(\S+)\s+\| (\d+) \| (\d+)/(\d+) \| (\d+)$', line)
    if m:
        sut, fault, n, b, n2, maxref = m.groups()
        row = next(x for x in s['same_seed_by_sut_fault'] if (x['sut'], x['fault']) == (sut, fault))
        assert list(map(int, [n, b, n2, maxref])) == [row['runs'], row['beyond'], row['runs'], row['max_ref']]
        checks += 1
assert checks == 35
hashes = json.loads((HERE / 'reviewed_hashes.json').read_text())
root = HERE.parents[3]
import hashlib
unchanged = all(hashlib.sha256((root / p).read_bytes()).hexdigest() == h for p, h in hashes.items())
assert unchanged
for name, h in s['input_sha256'].items():
    assert hashlib.sha256((root / '08_experiments/E1_pilot/pilot_results' / name).read_bytes()).hexdigest() == h
result = {'stdout_group_and_total_checks': checks, 'csv_assertions': s['checks']['assertions'],
          'protected_files': len(hashes), 'protected_hashes_unchanged': unchanged,
          'spot_check_rows': 3, 'spot_check_assertions': json.loads((HERE / 'spot_check.json').read_text())['assertions'],
          'raw_exchange_files_read_in_spot_check': len(json.loads((HERE / 'spot_check.json').read_text())['raw_inputs'])}
(HERE / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
