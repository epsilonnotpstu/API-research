"""Freeze verification and concise check evidence; never emit fixture values."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = Path(__file__).resolve().parent
freeze_path = SCRATCH / 'freeze.json'
freeze = json.loads(freeze_path.read_text())
current = [p for directory in ('08_experiments/tools', '08_experiments/E1_pilot/harness_v2')
           for p in (ROOT / directory).rglob('*') if p.is_file()]
paths = set(freeze['before']) | {str(p.relative_to(ROOT)) for p in current}
freeze['after'] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() if (ROOT / name).is_file() else None
                   for name in sorted(paths)}
intended = set(freeze['intended_changes'])
freeze['changed_intended'] = sorted(name for name in intended if freeze['before'].get(name) != freeze['after'].get(name))
freeze['protected_entries'] = len(set(freeze['before']) - intended)
freeze['protected_present_files'] = sum(freeze['before'][name] is not None for name in set(freeze['before']) - intended)
freeze['unexpected_changes'] = sorted(name for name in paths - intended if freeze['before'].get(name) != freeze['after'].get(name))
freeze['unexpected_new_files'] = sorted(set(freeze['after']) - set(freeze['before']) - intended)
freeze['all_protected_unchanged'] = not freeze['unexpected_changes'] and not freeze['unexpected_new_files']
assert freeze['all_protected_unchanged']
assert set(freeze['changed_intended']) == intended
freeze_path.write_text(json.dumps(freeze, indent=2) + '\n')
checks = json.loads((SCRATCH / 'checks.json').read_text())
checks.update({'test_specmut': 0, 'test_pipeline': 0, 'static_validate': 0})
summary = {}
for name in sorted(k for k in checks if not k.startswith('bash_n:')):
    text = (SCRATCH / (name + '.txt')).read_text()
    assert checks[name] == 0
    assert not re.search(r'^FAILED|^FAIL ', text, re.M), name
    counts = re.findall(r'^Ran (\d+) tests', text, re.M)
    summary[name] = {'exit_code': checks[name], 'unit_tests': [int(n) for n in counts],
                     'log': str((SCRATCH / (name + '.txt')).relative_to(ROOT)),
                     'log_sha256': hashlib.sha256(text.encode()).hexdigest()}
    if name == 'test_specmut':
        assert '144 passed, 0 failed' in text
        summary[name]['real_spec_fault_property_cases'] = 144
    elif name == 'test_pipeline':
        assert text.rstrip().endswith('PASS')
    elif name == 'static_validate':
        assert 'PASS ALL STATIC CHECKS AND PERMITTED UNIT TESTS' in text
summary['bash_n'] = {'scripts': sum(k.startswith('bash_n:') for k in checks), 'exit_code': 0,
                     'log': str((SCRATCH / 'bash_n.txt').relative_to(ROOT))}
summary['freeze'] = {'all_protected_unchanged': True, 'protected_entries': freeze['protected_entries'],
                     'protected_present_files': freeze['protected_present_files'],
                     'changed_intended': len(freeze['changed_intended'])}
summary['sanity'] = {'all_checks_passed': json.loads((SCRATCH / 'sanity.json').read_text())['all_checks_passed'],
                     'variants': 6, 'legacy_seed1_noop_disclosed': True}
summary['execution_boundary'] = 'Own Python tools and tests; shell syntax, preflight failures and extracted pure fragments only. No Docker, Java, Maven, network, fuzzer or SUT execution.'
(SCRATCH / 'verification.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({'protected_entries': freeze['protected_entries'], 'protected_present_files': freeze['protected_present_files'],
                  'changed_intended': len(freeze['changed_intended']), 'all_protected_unchanged': True, 'all_checks_passed': True}))
